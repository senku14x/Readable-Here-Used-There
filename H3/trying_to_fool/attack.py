"""trying_to_fool — constrained forge search (design_spec.md Amendment 1 + Amendment 2). Primary model only.
Stages: bank (natural swings A_k, rho_nat, naming-steer baseline on the 16 bank pairs), search (gradient search for an
identity-specific delta at block 35, fitted on C0/C1 with codebook seed A; audit instruments never in the loss),
audit (the found delta on C2/C3 with codebook seed B, beside the naming steer at the same radius)."""
import os, sys, json, time, hashlib
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "..", "common", "scripts"))
import numpy as np, torch
import registry as R, materials as M, rendering as Rn, readout as RO, hooks as H
from hooks import _out, _pack

assert not R.MODEL_KEY, "registered for the primary model"
STAGE = sys.argv[1] if len(sys.argv) > 1 else "bank"
SMOKE = "--smoke" in sys.argv
OUT = os.path.join(HERE, "outputs"); os.makedirs(OUT, exist_ok=True)
RUN_ID = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()); SEED_A, SEED_B = 20260909, 20260910
PAIRS = M.EVAL_BANK_1 + M.EVAL_BANK_2
if SMOKE: PAIRS = PAIRS[:1]
FIT_C, AUD_C = ["C0", "C1"], ["C2", "C3"]; DECOYS = M.DECOYS[:4]; LETTERS = ["B", "D", "F", "H", "K", "M", "Q", "V"]
L_INJ = 35; W = (51, 59); WL = list(range(W[0], W[1] + 1)); SRC = list(range(R.N_SRC))
QUERY = "Using the code, what is the letter for the word introduced in the first message? Answer with the letter only."
STEPS = 3 if SMOKE else 60; LR = 0.15; RADII = [1.0]; BOUND_NLL = 0.02


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


def main():
    tok = R.make_tokenizer()
    from jlens.hf import from_hf
    model = R.load_model(); lm = from_hf(model, tok, compile=False)
    for p in model.parameters(): p.requires_grad_(False)
    ALL = list(range(R.N_BLOCKS)); run = H.make_run(model, lm, ALL)
    lenses = R.load_lenses(("J_NP", "R_CB")); words = sorted({w for p in PAIRS for w in p} | set(DECOYS))
    TID = {w: Rn.single_token_id(tok, w) for w in words}; assert all(v is not None for v in TID.values())
    ro = {k: RO.LensReadout(model, lm, L, [TID[w] for w in words]) for k, L in lenses.items()}
    LID = {L: forms(tok, L) for L in LETTERS}
    J = lenses["J_NP"]; gamma = ro["J_NP"].gamma.to("cuda"); Wu = ro["J_NP"].Wu; dev = Wu.device
    t0 = time.time(); n = 0
    # ---- plain-sentence axes (fit: templates 1-8 in the objective; audit: 9-12 never in the objective)
    axp = os.path.join(OUT, "bank_axes.pt")
    if os.path.exists(axp) and not SMOKE:
        AX = torch.load(axp)
    else:
        MU = {}
        for w in words:
            for split, tpls in (("fit", M.PLAIN_FIT), ("audit", M.PLAIN_VAL)):
                acc = []
                for tpl in tpls:
                    s_ = tpl.format(m=w); enc = tok(s_, add_special_tokens=False, return_offsets_mapping=True)
                    ce_ = tpl.index("{m}") + len(w) - 1; p_ = next(k for k, (a, b) in enumerate(enc.offset_mapping) if a <= ce_ < b)
                    a_, _ = run(enc.input_ids); n += 1; acc.append(torch.stack([a_[l][0, p_, :].float() for l in ALL]).cpu()); del a_
                MU[(w, split)] = torch.stack(acc).mean(0)
        AX = {}
        for split in ("fit", "audit"):
            dc = torch.stack([MU[(d, split)] for d in DECOYS]).mean(0)
            for w in words:
                v = MU[(w, split)] - dc; u = v / v.norm(dim=-1, keepdim=True); AX[(split, "pres", w)] = (u, (u * dc).sum(-1))
            for X, Y in PAIRS:
                for a, b in ((X, Y), (Y, X)):
                    v = MU[(b, split)] - MU[(a, split)]; AX[(split, "pair", a, b)] = v / v.norm(dim=-1, keepdim=True)
        if not SMOKE: torch.save(AX, axp)
        print(f"  axes fitted ({n} forwards, {time.time()-t0:.0f}s)", flush=True)

    def readouts(r, logits, acts, X, Y, assign):
        """All audit-side measurements at W, no grad."""
        inter = r.interior; out = {}
        for k in ro:
            z = ro[k].z(acts, inter, WL).astype(np.float32).mean(axis=(0, 1))
            out[f"m_{k}"] = float(z[words.index(Y)] - z[words.index(X)])
            out[f"sY_{k}"] = float(z[words.index(Y)] - z[[words.index(d) for d in DECOYS]].mean())
        hs = torch.stack([acts[l][0, inter, :].float() for l in WL]).cpu()
        for split in ("fit", "audit"):
            out[f"m_RESID_{split}"] = float((hs * AX[(split, "pair", X, Y)][WL][:, None, :]).sum(-1).mean())
            u, c = AX[(split, "pres", Y)]; out[f"sY_RESID_{split}"] = float(((hs * u[WL][:, None, :]).sum(-1) - c[WL][:, None]).mean())
        lp = torch.log_softmax(logits[0, inter, :].float(), -1); out["m_LOGITS"] = float((lp[:, TID[Y]] - lp[:, TID[X]]).mean())
        lpa = torch.log_softmax(logits[0, -1].float(), -1); out["b"] = float(torch.logsumexp(lpa[LID[assign[Y]]], 0) - torch.logsumexp(lpa[LID[assign[X]]], 0))
        out["rankY"] = int(ro["J_NP"].full_vocab_ranks(acts, inter, WL, [TID[Y]])[:, :, 0].min())
        cs, ce = r.meta["carrier_start"], r.meta["carrier_end"]; nll, top1, _ = RO.carrier_damage(logits, r.ids, cs, ce)
        out["nll"] = nll; return out, top1

    # ---------------- differentiable forward with delta at block 35 on interior positions
    def fwd_grad(ids, pos, delta):
        caps = {}
        def add_hook(m, i, o):
            h = _out(o); h2 = h.clone(); h2[0, pos, :] = (h[0, pos, :].float() + delta[None, :]).to(h.dtype); return _pack(o, h2)
        def cap(l):
            def f(m, i, o): caps[l] = _out(o)
            return f
        hs = [lm.layers[L_INJ].register_forward_hook(add_hook)] + [lm.layers[l].register_forward_hook(cap(l)) for l in WL]
        try:
            logits = model(torch.tensor([ids], device=lm.input_device), attention_mask=None).logits
        finally:
            [x.remove() for x in hs]
        return logits, caps

    def loss_terms(r, logits, caps, X, Y, assign, clean):
        inter = r.interior; iX, iY = TID[X], TID[Y]; dec = [TID[d] for d in DECOYS]
        Wsub = Wu[[iX, iY] + dec].float()
        mJ, sY = [], []
        for l in WL:
            h = caps[l][0, inter, :].float(); t = h @ J.jacobians[l].T
            rms = torch.sqrt((t * t).mean(-1, keepdim=True) + ro["J_NP"].eps); z = ((t * gamma) @ Wsub.T) / rms
            mJ.append((z[:, 1] - z[:, 0]).mean()); sY.append((z[:, 1] - z[:, 2:].mean(-1)).mean())
        mJ = torch.stack(mJ).mean(); sY = torch.stack(sY).mean()
        hs = torch.stack([caps[l][0, inter, :].float() for l in WL])
        mP = (hs * AX[("fit", "pair", X, Y)][WL][:, None, :].to(dev)).sum(-1).mean()
        lp = torch.log_softmax(logits[0, inter, :].float(), -1); mL = (lp[:, iY] - lp[:, iX]).mean()
        lpa = torch.log_softmax(logits[0, -1].float(), -1); b = torch.logsumexp(lpa[LID[assign[Y]]], 0) - torch.logsumexp(lpa[LID[assign[X]]], 0)
        cs, ce = r.meta["carrier_start"], r.meta["carrier_end"]
        lpc = torch.log_softmax(logits[0, cs - 1:ce - 1, :].float(), -1); nll = -lpc.gather(1, torch.tensor(r.ids[cs:ce], device=lpc.device)[:, None]).mean()
        return {"mJ": mJ - clean["mJ"], "sY": sY - clean["sY"], "mP": mP - clean["mP"], "mL": mL - clean["mL"], "b": b - clean["b"], "dnll": nll - clean["nll"]}

    RAW, META = {}, {"pairs": PAIRS, "decoys": DECOYS, "words": words, "l_inj": L_INJ, "window": list(W), "seed_A": SEED_A, "seed_B": SEED_B, "cells": {}, "stage": STAGE, "steps": STEPS, "lr": LR, "radii": RADII}
    K = json.load(open(os.path.join(OUT, "bank_constants_smoke.json" if SMOKE else "bank_constants.json"))) if STAGE != "bank" else None

    def cell(X, Y, ck, seed):
        car = M.CARRIERS[ck]; cb, assign = codebook(X, Y, np.random.default_rng(seed + 7 * PAIRS.index(tuple(sorted((X, Y)))) + 3 * ["C0", "C1", "C2", "C3"].index(ck)))
        rX = Rn.render(tok, Rn.user_text_controlled("maintain", X, car), car, sources=[("X", X, True)], extra_turns=[(cb + "\n" + QUERY, "")])
        rY = Rn.render(tok, Rn.user_text_controlled("maintain", Y, car), car, sources=[("X", Y, True)], extra_turns=[(cb + "\n" + QUERY, "")])
        assert len(rX) == len(rY) and rX.spans["X"]["full"] == rY.spans["X"]["full"] and rX.meta["carrier_start"] == rY.meta["carrier_start"]
        return rX, rY, assign

    if STAGE == "bank":
        for pi, (A, B) in enumerate(PAIRS):
            for X, Y in ((A, B), (B, A)):
                for ck in FIT_C + AUD_C:
                    seed = SEED_A if ck in FIT_C else SEED_B
                    rX, rY, assign = cell(X, Y, ck, seed); base = f"{X}->{Y}|{ck}"; inter = rX.interior
                    aX, lX = run(rX.ids); n += 1; oX, top1 = readouts(rX, lX, aX, X, Y, assign)
                    aY, lY = run(rY.ids); n += 1; oY, _ = readouts(rY, lY, aY, X, Y, assign)
                    rho = float((aY[L_INJ][0, inter, :].float() - aX[L_INJ][0, inter, :].float()).norm(dim=1).mean())
                    META["cells"][base] = {"X": X, "Y": Y, "carrier": ck, "F": assign, "interior": [inter[0], inter[-1]], "n_tokens": len(rX), "rho_nat": rho}
                    for k, v in oX.items(): RAW[f"{base}|cleanX|{k}"] = np.float32(v)
                    for k, v in oY.items(): RAW[f"{base}|cleanY|{k}"] = np.float32(v)
                    if ck in AUD_C:   # naming-steer baseline on the audit carriers at the attack radii
                        steer = ro["J_NP"].folded_direction(L_INJ, TID[Y]) - ro["J_NP"].folded_direction(L_INJ, TID[X]); steer = steer / steer.norm()
                        for rad in (0.5, 1.0, 2.0):
                            hk = H.AddVector(lm.layers, L_INJ, inter, (steer * rad * rho).to(aX[L_INJ].device)); a_, l_ = run(rX.ids, hk); n += 1
                            o_, _ = readouts(rX, l_, a_, X, Y, assign); _, _, ret = RO.carrier_damage(l_, rX.ids, rX.meta["carrier_start"], rX.meta["carrier_end"], top1)
                            for k, v in o_.items(): RAW[f"{base}|steer{rad}|{k}"] = np.float32(v)
                            RAW[f"{base}|steer{rad}|ret"] = np.float32(ret)
                            for kk, vv in H.realized_write_stats(hk).items(): RAW[f"{base}|steer{rad}|w_{kk}"] = np.float32(vv)
                            del a_
                    del aX, aY
            print(f"  pair {A}-{B}: {n} forwards ({time.time()-t0:.0f}s)", flush=True)
        # constants: cluster = unordered pair, audit carriers, window W
        INST = ["J_NP", "R_CB", "RESID_fit", "RESID_audit", "LOGITS"]
        def bypair(f):
            by = {}
            for base, c in META["cells"].items(): by.setdefault(tuple(sorted((c["X"], c["Y"]))), []).append(f(base))
            return np.array([np.mean(v) for v in by.values()])
        Kc = {}
        for inst in INST:
            Kc[f"A_{inst}"] = float(bypair(lambda b: RAW[f"{b}|cleanY|m_{inst}"] - RAW[f"{b}|cleanX|m_{inst}"]).mean())
        Kc["A_J_Y"] = float(bypair(lambda b: RAW[f"{b}|cleanY|sY_J_NP"] - RAW[f"{b}|cleanX|sY_J_NP"]).mean())
        Kc["A_b"] = float(bypair(lambda b: RAW[f"{b}|cleanY|b"] - RAW[f"{b}|cleanX|b"]).mean())
        Kc["rho_nat"] = float(bypair(lambda b: META["cells"][b]["rho_nat"]).mean())
        Kc["T_J"] = 0.5 * Kc["A_J_NP"]; Kc["T_Y"] = 0.5 * Kc["A_J_Y"]; Kc["eps"] = {inst: 0.2 * abs(Kc[f"A_{inst}"]) for inst in INST}; Kc["eps_b"] = 0.2 * abs(Kc["A_b"])
        json.dump(Kc, open(os.path.join(OUT, "bank_constants_smoke.json" if SMOKE else "bank_constants.json"), "w"), indent=1)
        print(json.dumps(Kc, indent=1))

    elif STAGE == "search":
        rho_nat = K["rho_nat"]; DELTAS = {}
        for pi, (A, B) in enumerate(PAIRS):
            X, Y = A, B                                   # one direction per pair (Amendment 2)
            cells = [cell(X, Y, ck, SEED_A) for ck in FIT_C]
            cleans = []
            for (rX, rY, assign) in cells:
                with torch.no_grad():
                    lg, caps = fwd_grad(rX.ids, rX.interior, torch.zeros(R.D_MODEL, device=dev))
                    z = loss_terms(rX, lg, caps, X, Y, assign, {"mJ": 0, "sY": 0, "mP": 0, "mL": 0, "b": 0, "nll": 0})
                    cleans.append({k: float(v) for k, v in z.items()}); cleans[-1]["nll"] = cleans[-1].pop("dnll")
            for rad in RADII:
                radius = rad * rho_nat
                g = torch.Generator(device="cpu").manual_seed(SEED_A + pi); delta = (torch.randn(R.D_MODEL, generator=g) * 0.01 * radius / np.sqrt(R.D_MODEL)).to(dev).requires_grad_(True)
                opt = torch.optim.Adam([delta], lr=LR * radius); curve = []
                for step in range(STEPS):
                    opt.zero_grad(); tot = 0.0; terms_acc = {}
                    for (rX, rY, assign), clean in zip(cells, cleans):
                        with torch.enable_grad():
                            lg, caps = fwd_grad(rX.ids, rX.interior, delta); tm = loss_terms(rX, lg, caps, X, Y, assign, clean)
                            obj = tm["mJ"] / abs(K["A_J_NP"]) + tm["sY"] / abs(K["A_J_Y"]) \
                                  - (tm["mP"] / abs(K["A_RESID_fit"])) ** 2 - (tm["b"] / abs(K["A_b"])) ** 2 - (tm["mL"] / abs(K["A_LOGITS"])) ** 2 \
                                  - (torch.relu(tm["dnll"]) / BOUND_NLL) ** 2
                            (-obj / len(cells)).backward(); tot += float(obj) / len(cells)
                            for k, v in tm.items(): terms_acc[k] = terms_acc.get(k, 0.0) + float(v) / len(cells)
                        n += 1
                    opt.step()
                    with torch.no_grad():
                        nr = delta.norm()
                        if nr > radius: delta.mul_(radius / nr)
                    curve.append({"step": step, "obj": tot, "norm": float(delta.norm()), **terms_acc})
                    if step % 10 == 0 or step == STEPS - 1: print(f"  {X}->{Y} r{rad} step {step}: obj {tot:+.3f} mJ/A {terms_acc['mJ']/abs(K['A_J_NP']):+.2f} sY/A {terms_acc['sY']/abs(K['A_J_Y']):+.2f} mP/A {terms_acc['mP']/abs(K['A_RESID_fit']):+.2f} b/A {terms_acc['b']/abs(K['A_b']):+.2f} dnll {terms_acc['dnll']:+.4f} |d| {float(delta.norm()):.2f} ({time.time()-t0:.0f}s)", flush=True)
                DELTAS[f"{X}->{Y}|r{rad}"] = delta.detach().cpu(); RAW[f"{X}->{Y}|r{rad}|curve"] = np.array([[c[k] for k in ("step", "obj", "norm", "mJ", "sY", "mP", "mL", "b", "dnll")] for c in curve], np.float32)
                META["cells"][f"{X}->{Y}|r{rad}"] = {"X": X, "Y": Y, "radius": radius, "final": curve[-1]}
        torch.save(DELTAS, os.path.join(OUT, "search_deltas.pt" if not SMOKE else "smoke_deltas.pt"))

    elif STAGE == "audit":
        DELTAS = torch.load(os.path.join(OUT, "smoke_deltas.pt" if SMOKE else "search_deltas.pt"))
        for key, delta in DELTAS.items():
            XY, rk = key.split("|"); X, Y = XY.split("->"); rad = float(rk[1:])
            for ck in AUD_C + FIT_C:
                rX, rY, assign = cell(X, Y, ck, SEED_B if ck in AUD_C else SEED_A); base = f"{X}->{Y}|{ck}"; inter = rX.interior
                aX, lX = run(rX.ids); n += 1; oX, top1 = readouts(rX, lX, aX, X, Y, assign)
                for k, v in oX.items(): RAW[f"{base}|cleanX|{k}"] = np.float32(v)
                hk = H.AddVector(lm.layers, L_INJ, inter, delta.to(dev)); a_, l_ = run(rX.ids, hk); n += 1
                o_, _ = readouts(rX, l_, a_, X, Y, assign); _, _, ret = RO.carrier_damage(l_, rX.ids, rX.meta["carrier_start"], rX.meta["carrier_end"], top1)
                for k, v in o_.items(): RAW[f"{base}|attack{rad}|{k}"] = np.float32(v)
                RAW[f"{base}|attack{rad}|ret"] = np.float32(ret)
                for kk, vv in H.realized_write_stats(hk).items(): RAW[f"{base}|attack{rad}|w_{kk}"] = np.float32(vv)
                # naming steer at the same realized norm, same cell (the direct comparison)
                steer = ro["J_NP"].folded_direction(L_INJ, TID[Y]) - ro["J_NP"].folded_direction(L_INJ, TID[X]); steer = steer / steer.norm() * float(delta.norm())
                hk2 = H.AddVector(lm.layers, L_INJ, inter, steer.to(dev)); a2, l2 = run(rX.ids, hk2); n += 1
                o2, _ = readouts(rX, l2, a2, X, Y, assign); _, _, ret2 = RO.carrier_damage(l2, rX.ids, rX.meta["carrier_start"], rX.meta["carrier_end"], top1)
                for k, v in o2.items(): RAW[f"{base}|steerm{rad}|{k}"] = np.float32(v)
                RAW[f"{base}|steerm{rad}|ret"] = np.float32(ret2)
                META["cells"][base] = {"X": X, "Y": Y, "carrier": ck, "audit": ck in AUD_C, "F": assign, "delta_norm": float(delta.norm()), "cos_delta_steer": float(torch.dot(delta / delta.norm(), (steer / steer.norm()).cpu()))}
                del aX, a_, a2
            print(f"  {key}: {n} forwards ({time.time()-t0:.0f}s)", flush=True)

    META.update({"run_id": RUN_ID, "n_forwards": n, "elapsed_s": round(time.time() - t0, 1)})
    tag = STAGE + ("_smoke" if SMOKE else "")
    np.savez_compressed(os.path.join(OUT, f"raw_{tag}.npz"), **RAW); json.dump(META, open(os.path.join(OUT, f"meta_{tag}.json"), "w"), indent=1, default=str)
    man = R.manifest_block(); man.update({"run_id": RUN_ID, "stage": tag, "design": "H3/trying_to_fool/design_spec.md (Amendments 1-2)", "raw_sha256": hashlib.sha256(open(os.path.join(OUT, f"raw_{tag}.npz"), "rb").read()).hexdigest()})
    json.dump(man, open(os.path.join(OUT, f"manifest_{tag}.json"), "w"), indent=1)
    print(f"[done {tag}] {n} forwards, {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
