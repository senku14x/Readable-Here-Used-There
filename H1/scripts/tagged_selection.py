"""H1 tagged selection (design: H1/design_specs/tagged_selection.md).

Testing whether the instruction selects which of three tagged sources is carried to the later readout, or
scales whichever word is sourced. Stage A: source replacement of each of the three words under each pointer
and the control. Stage B: the frozen single-word g move crossed with relevance. Stage B2: a native pointer
contrast (pointed B minus pointed A) and a native shared direction, fit from Stage A clean runs only.

Usage: tagged_selection.py pilot
Writes H1/outputs/tagged_selection/{raw_pilot.npz, meta_pilot.json, manifest_pilot.json, fits_pilot.npz}.
"""
import os, sys, json, time, hashlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "common", "scripts"))
import numpy as np
import torch
import registry as R
import materials as M
import rendering as Rn
import readout as RO
import hooks as H

STAGE = sys.argv[1] if len(sys.argv) > 1 else "pilot"
OUT = R.out_dir("H1", "outputs", "tagged_selection")
RUN_ID = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
L_STATE, L_X = 35, 36
TAGS = ["A", "B", "C"]
ARMS = ["A", "B", "C", "ctrl"]
if STAGE == "pilot":
    TRIPLES = [("orange", "tiger", "castle"), ("diamond", "rocket", "dragon"), ("forest", "hammer", "horse"), ("lion", "knife", "fork")]
    CARRIERS = M.FIT_CARRIERS
else:
    _bank = [w for p in M.EVAL_BANK_1 + M.EVAL_BANK_2 for w in p]          # registered rule: consecutive bank words, first 8 triples
    TRIPLES = [tuple(_bank[3 * i:3 * i + 3]) for i in range(8)]
    CARRIERS = M.EVAL_CARRIERS
RESERVE = ["drawer"]
DECOYS = M.FIT_WORDS[:8]
ALL_LAYERS = list(range(R.N_SRC)); RANK_LAYERS = list(range(24, 60))
COPY = "copy the following text exactly, word for word"


def user_text(words, arm, carrier):
    head = f'Here are three words: (A) "{words[0]}", (B) "{words[1]}", (C) "{words[2]}"'
    tail = f". Keep the word tagged {arm} in mind while you {COPY}" if arm in TAGS else f". Those words occur one time. Now {COPY}"
    return head + tail + ":\n\n" + carrier


def rotate(tr, r):
    return tuple(tr[(i + r) % 3] for i in range(3))


def main():
    t0 = time.time(); tok = R.make_tokenizer()
    from jlens.hf import from_hf
    model = R.load_model(); lm = from_hf(model, tok, compile=False)
    ALL = list(range(R.N_BLOCKS)); run = H.make_run(model, lm, ALL); dev = lm.input_device
    LEN = R.load_lenses(("J_NP",))["J_NP"]
    # donor map: word -> word of the next triple at the same index
    DONOR = {}
    for ti, tr in enumerate(TRIPLES):
        nxt = TRIPLES[(ti + 1) % len(TRIPLES)]
        for i, w in enumerate(tr):
            DONOR[w] = nxt[i]
    SRC = [w for tr in TRIPLES for w in tr]
    TID = {w: Rn.single_token_id(tok, w) for w in SRC + DECOYS}
    assert all(v is not None for v in TID.values()), {k: v for k, v in TID.items() if v is None}
    COLS = SRC + DECOYS
    ro = RO.LensReadout(model, lm, LEN, [TID[w] for w in COLS])
    ra = np.load(os.path.join(R.PROJECT, "H1", "outputs", "natural_modulation", "resid_axis.npz"))
    MU = {w: torch.tensor(ra[f"{w}|fit"].astype(np.float32), device=dev) for w in SRC if f"{w}|fit" in ra}
    assert len(MU) == len(SRC), [w for w in SRC if w not in MU]
    G = np.load(os.path.join(R.PROJECT, "H1", "outputs", "task_state_modulation", "G.npz"))
    ghat = torch.tensor(G["ghat"], device=dev)
    PILOT = None
    if STAGE == "evaluate":
        PF = np.load(os.path.join(OUT, "fits_pilot.npz"))
        PILOT = {k: torch.tensor(PF[k], device=dev) for k in ("d_pointer_AB", "d_shared")}
        PILOT = {k: v / v.norm() for k, v in PILOT.items()}
    def pair_axis(X, Y):
        v = MU[Y] - MU[X]; return v / v.norm(dim=-1, keepdim=True)

    def render(words, arm, ck):
        car = M.CARRIERS[ck]
        return Rn.render(tok, user_text(words, arm, car), car, sources=[(f"X{j+1}", words[j], True) for j in range(3)], name=f"{arm}|{words}|{ck}")

    RAW, META = {}, {"cells": {}, "triples": TRIPLES, "donor": DONOR, "columns": COLS, "carriers": CARRIERS, "arms": ARMS, "rank_layers": RANK_LAYERS,
                     "l_state": L_STATE, "l_x": L_X, "G_sha256": hashlib.sha256(open(os.path.join(R.PROJECT, "H1", "outputs", "task_state_modulation", "G.npz"), "rb").read()).hexdigest()}
    n = 0

    def record(tag, r, acts, logits, words, hook=None):
        inter = r.interior
        RAW[f"{tag}|z"] = ro.z(acts, inter, ALL_LAYERS).astype(np.float16)
        hs = torch.stack([acts[l][0, inter, :].float() for l in ALL_LAYERS])
        lp = torch.log_softmax(logits[0, inter, :].float(), -1)
        for j, X in enumerate(words):
            Y = DONOR[X]
            RAW[f"{tag}|p_pair{j+1}"] = (hs * pair_axis(X, Y)[:, None, :]).sum(-1).cpu().numpy().astype(np.float32)
            RAW[f"{tag}|lp_margin{j+1}"] = (lp[:, TID[Y]] - lp[:, TID[X]]).cpu().numpy().astype(np.float32)
        RAW[f"{tag}|rank"] = ro.full_vocab_ranks(acts, inter, RANK_LAYERS, [TID[w] for w in words]).astype(np.int32)
        zfin = lm.unembed(acts[R.N_BLOCKS - 1][0, inter, :].float()).float()
        RAW[f"{tag}|fin_rank"] = np.array([int(np.median(((zfin > zfin[:, [TID[w]]]).sum(1) + 1).cpu().numpy())) for w in words], np.int32)
        RAW[f"{tag}|g_coord35"] = (acts[L_STATE][0, inter, :].float() @ ghat).cpu().numpy().astype(np.float32)
        cs, ce = r.meta["carrier_start"], r.meta["carrier_end"]
        nll, top1, _ = RO.carrier_damage(logits, r.ids, cs, ce)
        RAW[f"{tag}|nll"] = np.float32(nll); RAW[f"{tag}|top1"] = top1
        if hook is not None:
            for k, v in H.realized_write_stats(hook).items():
                RAW[f"{tag}|w_{k}"] = np.float32(v)

    # ------------------------------------------------------------------ Stage A (+ caches for B/B2)
    H35 = {}      # (ck, ti, rot, arm) -> interior h35 [P, d]
    CACHE = {}    # (ck, ti, rot, arm) -> {"r": rendered, "span": {j: cache}, "donor": {j: cache}, "acts": ..., "logits": ...}
    for ck in CARRIERS:
        for ti, tr in enumerate(TRIPLES):
            for rot in range(3):
                words = rotate(tr, rot)
                for arm in ARMS:
                    key = (ck, ti, rot, arm); tag = f"{ck}|{ti}|rot{rot}|{arm}"
                    r = render(words, arm, ck); acts, lg = run(r.ids); n += 1
                    spans = {j: r.spans[f"X{j+1}"]["full"] for j in range(3)}
                    own = {j: {l: acts[l][0, spans[j], :].clone() for l in ALL} for j in range(3)}
                    H35[key] = acts[L_STATE][0, r.interior, :].float().clone()
                    record(f"{tag}|clean|noswap", r, acts, lg, words)
                    META["cells"][tag] = {"words": list(words), "n_tokens": len(r), "interior_n": len(r.interior), "spans": spans}
                    donor = {}
                    for j in range(3):
                        dw = list(words); dw[j] = DONOR[words[j]]
                        rd = render(tuple(dw), arm, ck)
                        assert len(rd) == len(r) and rd.spans[f"X{j+1}"]["full"] == spans[j], f"donor geometry {tag} j={j}"
                        ad, _ = run(rd.ids); n += 1
                        donor[j] = {l: ad[l][0, spans[j], :].clone() for l in ALL}; del ad
                    CACHE[key] = {"r": r, "spans": spans, "own": own, "donor": donor}
                    # same-source gate (j = 0)
                    acts_s, lg_s = run(r.ids, H.SpanWriter(lm.layers, [l for l in ALL if l >= L_X], spans[0], own[0])); n += 1
                    assert torch.equal(lg_s, lg) and all(torch.equal(acts_s[l], acts[l]) for l in ALL), f"same-source != clean {tag}"
                    del acts_s
                    for j in range(3):
                        a2, l2 = run(r.ids, H.SpanWriter(lm.layers, [l for l in ALL if l >= L_X], spans[j], donor[j])); n += 1
                        for l in range(L_X):
                            assert torch.equal(a2[l][0, r.interior, :], acts[l][0, r.interior, :]), f"layer<{L_X} identity {tag} j={j}"
                        record(f"{tag}|clean|swap{j+1}", r, a2, l2, words); del a2
                    del acts
                print(f"  [A] {ck} T{ti} rot{rot}: {n} forwards ({time.time()-t0:.0f}s)", flush=True)
    # ------------------------------------------------------------------ fits from Stage A clean runs (no swap outcome read)
    mean35 = lambda arm: torch.stack([H35[k].mean(0) for k in H35 if k[3] == arm]).mean(0)
    d_ptr = mean35("B") - mean35("A"); d_ptr_hat = d_ptr / d_ptr.norm()
    d_shared = torch.stack([mean35(a) for a in TAGS]).mean(0) - mean35("ctrl"); d_shared_hat = d_shared / d_shared.norm()
    cos = lambda a, b: float(a @ b / (a.norm() * b.norm()))
    META["fits"] = {"norm_d_pointer_AB": float(d_ptr.norm()), "norm_d_shared": float(d_shared.norm()), "cos_dptr_ghat": cos(d_ptr, ghat), "cos_dshared_ghat": cos(d_shared, ghat),
                    "cos_dptr_dshared": cos(d_ptr, d_shared), "level_gap_ghat_pointed_minus_ctrl": float(torch.stack([mean35(a) for a in TAGS]).mean(0) @ ghat - mean35("ctrl") @ ghat)}
    if PILOT is not None:
        META["fits_transfer"] = {"cos_dshared_native_vs_pilot": cos(d_shared, PILOT["d_shared"]), "cos_dptr_native_vs_pilot": cos(d_ptr, PILOT["d_pointer_AB"])}
    np.savez_compressed(os.path.join(OUT, f"fits_{STAGE}.npz"), d_pointer_AB=d_ptr.cpu().numpy(), d_shared=d_shared.cpu().numpy(), ghat=ghat.cpu().numpy())
    print(f"[fits] |d_ptr| {d_ptr.norm():.2f} |d_shared| {d_shared.norm():.2f} cos(d_shared,g) {META['fits']['cos_dshared_ghat']:.3f} cos(d_ptr,g) {META['fits']['cos_dptr_ghat']:.3f}", flush=True)

    # ------------------------------------------------------------------ Stage B / B2
    def level(key, u):
        return float((H35[key] @ u).mean())

    def moves_for(key):
        ck, ti, rot, arm = key
        out = []
        if arm in TAGS:
            out.append(("g", ghat, level((ck, ti, rot, "ctrl"), ghat)))                     # pointed -> control level along g
            out.append(("dshared", d_shared_hat, level((ck, ti, rot, "ctrl"), d_shared_hat)))  # native gain candidate
            if PILOT is not None:
                out.append(("dshared_pilot", PILOT["d_shared"], level((ck, ti, rot, "ctrl"), PILOT["d_shared"])))   # transferred (identity holdout)
            if arm == "A":
                out.append(("dptr", d_ptr_hat, level((ck, ti, rot, "B"), d_ptr_hat)))       # address candidate: A -> B level
                if PILOT is not None:
                    out.append(("dptr_pilot", PILOT["d_pointer_AB"], level((ck, ti, rot, "B"), PILOT["d_pointer_AB"])))
        else:
            lev = float(np.mean([level((ck, ti, rot, a), ghat) for a in TAGS]))
            out.append(("grev", ghat, lev))                                                    # control -> mean pointed level (one-sided)
        return out

    for key, c in CACHE.items():
        ck, ti, rot, arm = key; tag = f"{ck}|{ti}|rot{rot}|{arm}"; r = c["r"]; words = tuple(META["cells"][tag]["words"])
        for cname, u, lev in moves_for(key):
            alpha = (lev - H35[key] @ u).cpu()
            META["cells"][tag][f"alpha_{cname}"] = float(alpha.mean())
            for ph in range(4):
                sw = None if ph == 0 else H.SpanWriter(lm.layers, [l for l in ALL if l >= L_X], c["spans"][ph - 1], c["donor"][ph - 1])
                mv = H.StateMove(lm.layers, L_STATE, r.interior, u, u, level=None, scale=1.0, alpha_fixed=alpha)
                acts, lg = run(r.ids, H.Both(mv, sw)); n += 1
                record(f"{tag}|{cname}|{'noswap' if ph == 0 else f'swap{ph}'}", r, acts, lg, words, hook=mv); del acts
        if arm == "ctrl":
            print(f"  [B] {ck} T{ti} rot{rot}: {n} forwards ({time.time()-t0:.0f}s)", flush=True)
    META.update({"run_id": RUN_ID, "stage": STAGE, "n_forwards": n, "elapsed_s": round(time.time() - t0, 1), "token_ids": TID})
    np.savez_compressed(os.path.join(OUT, f"raw_{STAGE}.npz"), **RAW)
    json.dump(META, open(os.path.join(OUT, f"meta_{STAGE}.json"), "w"), indent=1)
    man = R.manifest_block(); man.update({"run_id": RUN_ID, "stage": STAGE, "script": os.path.relpath(__file__, R.PROJECT), "design": "H1/design_specs/tagged_selection.md",
                                          "raw_sha256": hashlib.sha256(open(os.path.join(OUT, f"raw_{STAGE}.npz"), "rb").read()).hexdigest()})
    json.dump(man, open(os.path.join(OUT, f"manifest_{STAGE}.json"), "w"), indent=1)
    print(f"[done {STAGE}] {n} forwards, {time.time()-t0:.0f}s -> {OUT}")


if __name__ == "__main__":
    main()
