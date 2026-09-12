"""trying_to_fool — forward-only calibration round (design_spec.md §3). Primary model only (TCSIF_MODEL unset).
Freezes A_k per instrument, A_J^Y, A_b (prompt change), rho_nat, D_max, repeat floors; runs the block-35 carrier transplant
(the attack-shaped positive control), the block-36 source donor, norm-matched random writes, and the naming-direction steer
(unconstrained reachability baseline). Evaluates gates G1-G5 and writes frozen_constants.json + calibration.md."""
import os, sys, json, time, hashlib
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "..", "common", "scripts"))
import numpy as np, torch
import registry as R, materials as M, rendering as Rn, readout as RO, hooks as H
from scipy import stats as st

assert not R.MODEL_KEY, "calibration is registered for the primary model"
OUT = os.path.join(HERE, "outputs"); os.makedirs(OUT, exist_ok=True)
RUN_ID = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()); SEED = 20260909
PAIRS = [("orange", "tiger"), ("guitar", "mountain"), ("diamond", "castle"), ("thunder", "rocket")]
CARRIERS = ["C0", "C1"]; DECOYS = M.DECOYS[:4]; LETTERS = ["B", "D", "F", "H", "K", "M", "Q", "V"]
L_INJ = 35; LGE = list(range(36, 64)); W1, W2 = (48, 50), (51, 59)
QUERY = "Using the code, what is the letter for the word introduced in the first message? Answer with the letter only."


def codebook(X, Y, rng):
    words = [X, Y] + DECOYS; letters = list(LETTERS); rng.shuffle(letters)
    assign = {w: letters[i] for i, w in enumerate(words)}; order = list(words); rng.shuffle(order)
    return "Code: " + ", ".join(f"{w} = {assign[w]}" for w in order) + ".", assign


def forms(tok, w):
    out = []
    for f in (w, " " + w):
        ids = tok(f, add_special_tokens=False).input_ids
        if len(ids) == 1 and ids[0] not in out: out.append(ids[0])
    return out


def ct(v):
    v = np.asarray(v, float); n = len(v); mu = v.mean(); h = st.t.ppf(0.975, n - 1) * v.std(ddof=1) / np.sqrt(n) if n > 1 else float("nan")
    return {"mean": float(mu), "ci": [float(mu - h), float(mu + h)], "n": int(n), "pos": int((v > 0).sum())}


def main():
    tok = R.make_tokenizer()
    from jlens.hf import from_hf
    model = R.load_model(); lm = from_hf(model, tok, compile=False)
    ALL = list(range(R.N_BLOCKS)); SRC = list(range(R.N_SRC)); run = H.make_run(model, lm, ALL)
    lenses = R.load_lenses(("J_NP", "R_CB")); words = sorted({w for p in PAIRS for w in p} | set(DECOYS))
    TID = {w: Rn.single_token_id(tok, w) for w in words}; assert all(v is not None for v in TID.values())
    ro = {k: RO.LensReadout(model, lm, L, [TID[w] for w in words]) for k, L in lenses.items()}
    LID = {L: forms(tok, L) for L in LETTERS}
    RAW, META = {}, {"pairs": PAIRS, "carriers": CARRIERS, "decoys": DECOYS, "words": words, "l_inj": L_INJ, "seed": SEED, "cells": {}}
    t0 = time.time(); n = 0
    # ---- two plain-sentence axes: fit (templates 1-8, in the objective) and audit (9-12, never in the objective)
    MU = {}
    for w in words:
        for split, tpls in (("fit", M.PLAIN_FIT), ("audit", M.PLAIN_VAL)):
            acc = []
            for tpl in tpls:
                s_ = tpl.format(m=w); enc = tok(s_, add_special_tokens=False, return_offsets_mapping=True)
                ce_ = tpl.index("{m}") + len(w) - 1; p_ = next(k for k, (a, b) in enumerate(enc.offset_mapping) if a <= ce_ < b)
                a_, _ = run(enc.input_ids); n += 1; acc.append(torch.stack([a_[l][0, p_, :].float() for l in ALL])); del a_
            MU[(w, split)] = torch.stack(acc).mean(0)
    AX = {}
    for split in ("fit", "audit"):
        dc = torch.stack([MU[(d, split)] for d in DECOYS]).mean(0)
        for w in words:
            v = MU[(w, split)] - dc; AX[(split, "pres", w)] = (v / v.norm(dim=-1, keepdim=True), (v / v.norm(dim=-1, keepdim=True) * dc).sum(-1))
        for X, Y in PAIRS:
            for a, b in ((X, Y), (Y, X)):
                v = MU[(b, split)] - MU[(a, split)]; AX[(split, "pair", a, b)] = v / v.norm(dim=-1, keepdim=True)
    print(f"  axes fitted ({n} forwards, {time.time()-t0:.0f}s)", flush=True)

    def rec(tag, r, logits, acts, X, Y, assign, hook=None, clean_top1=None):
        inter = r.interior
        for k in ro:
            RAW[f"{tag}|z|{k}"] = ro[k].z(acts, inter, SRC).astype(np.float16)
        hs = torch.stack([acts[l][0, inter, :].float() for l in ALL])
        proj = []
        for split in ("fit", "audit"):
            for w in (X, Y):
                u, c = AX[(split, "pres", w)]; proj.append(((hs * u[:, None, :]).sum(-1) - c[:, None]).mean(-1))
            proj.append((hs * AX[(split, "pair", X, Y)][:, None, :]).sum(-1).mean(-1))
        RAW[f"{tag}|resid"] = torch.stack(proj, 1).cpu().numpy().astype(np.float32)            # [64, 6]: fitX fitY fitPair audX audY audPair
        lp = torch.log_softmax(logits[0, inter, :].float(), -1); RAW[f"{tag}|lp"] = lp[:, [TID[X], TID[Y]]].mean(0).cpu().numpy().astype(np.float32)
        lpa = torch.log_softmax(logits[0, -1].float(), -1); RAW[f"{tag}|b"] = np.float32(float(torch.logsumexp(lpa[LID[assign[Y]]], 0) - torch.logsumexp(lpa[LID[assign[X]]], 0)))
        RAW[f"{tag}|rankY"] = ro["J_NP"].full_vocab_ranks(acts, inter, list(range(W1[0], W2[1] + 1)), [TID[Y]])[:, :, 0].min()
        cs, ce = r.meta["carrier_start"], r.meta["carrier_end"]; nll, top1, ret = RO.carrier_damage(logits, r.ids, cs, ce, clean_top1)
        RAW[f"{tag}|nll"] = np.float32(nll); RAW[f"{tag}|ret"] = np.float32(ret)
        if hook is not None and getattr(hook, "realized", None) is not None:
            for kk, vv in H.realized_write_stats(hook).items(): RAW[f"{tag}|w_{kk}"] = np.float32(vv)
        return top1

    rng = np.random.default_rng(SEED)
    for pi, (A, B) in enumerate(PAIRS):
        for X, Y in ((A, B), (B, A)):
            for ck in CARRIERS:
                car = M.CARRIERS[ck]; base = f"{X}->{Y}|{ck}"
                cb, assign = codebook(X, Y, np.random.default_rng(SEED + 100 * pi + CARRIERS.index(ck)))
                rX = Rn.render(tok, Rn.user_text_controlled("maintain", X, car), car, sources=[("X", X, True)], extra_turns=[(cb + "\n" + QUERY, "")])
                rY = Rn.render(tok, Rn.user_text_controlled("maintain", Y, car), car, sources=[("X", Y, True)], extra_turns=[(cb + "\n" + QUERY, "")])
                if not (len(rX) == len(rY) and rX.spans["X"]["full"] == rY.spans["X"]["full"] and rX.meta["carrier_start"] == rY.meta["carrier_start"]):
                    META["cells"][base] = {"excluded": "donor geometry"}; print(f"  excluded {base} (geometry)"); continue
                inter = rX.interior; span = rX.spans["X"]["full"]
                META["cells"][base] = {"X": X, "Y": Y, "F": assign, "span": [span[0], span[-1]], "interior": [inter[0], inter[-1]], "n_tokens": len(rX)}
                aX, lX = run(rX.ids); n += 1; top1 = rec(f"{base}|cleanX", rX, lX, aX, X, Y, assign)
                aY, lY = run(rY.ids); n += 1; rec(f"{base}|cleanY", rY, lY, aY, X, Y, assign, clean_top1=top1)
                h35X = aX[L_INJ][0, inter, :].float(); h35Y = aY[L_INJ][0, inter, :].float()
                rho = float((h35Y - h35X).norm(dim=1).mean()); RAW[f"{base}|rho_nat"] = np.float32(rho)
                # C1b source donor from 36; C1c block-35 carrier transplant (attack-shaped)
                a_, l_ = run(rX.ids, H.SpanWriter(lm.layers, LGE, span, {l: aY[l][0, span, :].clone() for l in LGE})); n += 1; rec(f"{base}|C1b", rX, l_, a_, X, Y, assign, clean_top1=top1); del a_
                a_, l_ = run(rX.ids, H.SpanWriter(lm.layers, [L_INJ], inter, {L_INJ: aY[L_INJ][0, inter, :].clone()})); n += 1; rec(f"{base}|C1c", rX, l_, a_, X, Y, assign, clean_top1=top1); del a_
                # C3 random writes and the naming-direction steer, at {0.5,1,2} rho_nat
                steer = ro["J_NP"].folded_direction(L_INJ, TID[Y]) - ro["J_NP"].folded_direction(L_INJ, TID[X]); steer = steer / steer.norm()
                nseeds = 3 if (pi == 0 and X == A) else 1
                for rad in (0.5, 1.0, 2.0):
                    for sd in range(nseeds):
                        g = torch.Generator(device="cpu").manual_seed(SEED + 17 * sd + int(rad * 10)); v = torch.randn(R.D_MODEL, generator=g); v = v / v.norm() * rad * rho
                        hk = H.AddVector(lm.layers, L_INJ, inter, v.to(aX[L_INJ].device)); a_, l_ = run(rX.ids, hk); n += 1
                        rec(f"{base}|rand{rad}|s{sd}", rX, l_, a_, X, Y, assign, hook=hk, clean_top1=top1); del a_
                    hk = H.AddVector(lm.layers, L_INJ, inter, (steer * rad * rho).to(aX[L_INJ].device)); a_, l_ = run(rX.ids, hk); n += 1
                    rec(f"{base}|steer{rad}", rX, l_, a_, X, Y, assign, hook=hk, clean_top1=top1); del a_
                # C2 repeat floor (first 4 cells): bitwise repeat + one-token-longer question
                if len([c for c in META["cells"] if "excluded" not in META["cells"][c]]) <= 4:
                    a_, l_ = run(rX.ids); n += 1; rec(f"{base}|repeat", rX, l_, a_, X, Y, assign); RAW[f"{base}|repeat_bitwise"] = np.bool_(torch.equal(l_, lX)); del a_
                    rL = Rn.render(tok, Rn.user_text_controlled("maintain", X, car), car, sources=[("X", X, True)], extra_turns=[(cb + "\n" + QUERY + " Thanks.", "")])
                    a_, l_ = run(rL.ids); n += 1; rec(f"{base}|lenvar", rL, l_, a_, X, Y, assign); del a_
                del aX, aY
        print(f"  pair {A}-{B}: {n} forwards ({time.time()-t0:.0f}s)", flush=True)
    META.update({"run_id": RUN_ID, "n_forwards": n, "elapsed_s": round(time.time() - t0, 1)})
    np.savez_compressed(os.path.join(OUT, "raw_calibrate.npz"), **RAW); json.dump(META, open(os.path.join(OUT, "meta_calibrate.json"), "w"), indent=1, default=str)
    man = R.manifest_block(); man.update({"run_id": RUN_ID, "stage": "calibrate", "design": "H3/trying_to_fool/design_spec.md", "raw_sha256": hashlib.sha256(open(os.path.join(OUT, "raw_calibrate.npz"), "rb").read()).hexdigest()})
    json.dump(man, open(os.path.join(OUT, "manifest_calibrate.json"), "w"), indent=1)
    print(f"[done calibrate] {n} forwards, {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
