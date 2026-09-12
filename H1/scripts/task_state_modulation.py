"""H1 task-state modulation (Package 2, H1.3–H1.5): does a fitted block-35 task coordinate, moved before the
source counterfactual begins, change the incremental effect of a post-block-36 source replacement?

Stages:
  fit       : G from the 16 fitting words (maintain − mention block-35 interior means, carriers C0/C1); v_c; the
              frozen control panel (4 isotropic, 4 covariance-matched, 2 background PCs, 2 unrelated semantic axes).
  pilot     : calibration pairs on the fitting carriers; the eight-condition factorial, dose rows, control panel.
  evaluate  : Banks 1 and 2 on carriers C2/C3 (same inventory), only after the pilot gates and frozen tolerances.
Writes H1/outputs/task_state_modulation/{G.npz, fit_report.json, raw_<stage>.npz, meta_<stage>.json, manifest_<stage>.json}.
"""
import os, sys, json, time, hashlib, itertools
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "common", "scripts"))
import numpy as np
import torch
import registry as R
import materials as M
import rendering as Rn
import readout as RO
import hooks as H

STAGE = sys.argv[1] if len(sys.argv) > 1 else "fit"
OUT = os.path.join(R.PROJECT, "H1", "outputs", "task_state_modulation")
os.makedirs(OUT, exist_ok=True)
RUN_ID = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
L_STATE, L_X = 35, 36
ARMS = ["maintain", "mention"]
FIT_CARRIERS = M.FIT_CARRIERS
DECOYS = M.DECOYS
SEM_DECOYS = ["dragon", "horse"]
SEED = 20260907
ALL_LAYERS = list(range(R.N_SRC))
DOSES = [0.5, 2.0]


def matched_pairs(tok, words_pairs, carriers):
    ok = []
    for (a, b) in words_pairs:
        good = True
        for arm in ARMS:
            for ck in carriers:
                car = M.CARRIERS[ck]
                ra = Rn.render(tok, Rn.user_text_controlled(arm, a, car), car, sources=[("X", a, True)])
                rb = Rn.render(tok, Rn.user_text_controlled(arm, b, car), car, sources=[("X", b, True)])
                good &= (len(ra) == len(rb) and ra.spans["X"]["full"] == rb.spans["X"]["full"])
        ok.append(((a, b), good))
    return ok


def main():
    t0 = time.time()
    tok = R.make_tokenizer()
    from jlens.hf import from_hf
    model = R.load_model()
    lm = from_hf(model, tok, compile=False)
    ALL = list(range(R.N_BLOCKS))
    run = H.make_run(model, lm, ALL)
    dev = lm.input_device
    lenses = R.load_lenses(("J_NP",))
    print(f"[setup] {time.time()-t0:.0f}s", flush=True)

    # ------------------------------------------------------------------ FIT
    if STAGE == "fit":
        H35 = {}; POS = []
        for w in M.FIT_WORDS:
            for arm in ARMS:
                for ck in FIT_CARRIERS:
                    car = M.CARRIERS[ck]
                    r = Rn.render(tok, Rn.user_text_controlled(arm, w, car), car, sources=[("X", w, True)])
                    acts, _ = run(r.ids)
                    hi = acts[L_STATE][0, r.interior, :].float()
                    H35[(w, arm, ck)] = hi.mean(0).cpu(); POS.append(hi.cpu()); del acts
        d = {w: torch.stack([H35[(w, "maintain", ck)] for ck in FIT_CARRIERS]).mean(0) - torch.stack([H35[(w, "mention", ck)] for ck in FIT_CARRIERS]).mean(0) for w in M.FIT_WORDS}
        G = torch.stack(list(d.values())).mean(0)
        V = {w: d[w] - G for w in M.FIT_WORDS}
        half1, half2 = M.FIT_WORDS[:8], M.FIT_WORDS[8:]
        G1 = torch.stack([d[w] for w in half1]).mean(0); G2 = torch.stack([d[w] for w in half2]).mean(0)
        cos = lambda a, b: float((a @ b) / (a.norm() * b.norm() + 1e-12))
        ghat = G / G.norm()
        # per-word alignment with G (held-out: leave-one-out G)
        loo = {w: cos(d[w], torch.stack([d[u] for u in M.FIT_WORDS if u != w]).mean(0)) for w in M.FIT_WORDS}
        # covariance of per-position block-35 interior residuals (fit words, both arms), centered
        Xr = torch.cat(POS, 0); Xc = Xr - Xr.mean(0, keepdim=True)
        rng = np.random.default_rng(SEED)
        iso = torch.tensor(rng.standard_normal((4, R.D_MODEL)), dtype=torch.float32); iso = iso / iso.norm(dim=1, keepdim=True)
        cov = []
        for k in range(4):
            e = torch.tensor(rng.standard_normal(Xc.shape[0]), dtype=torch.float32)
            u = Xc.T @ e / np.sqrt(Xc.shape[0]); cov.append(u / u.norm())
        cov = torch.stack(cov)
        U, S_, Vh = torch.linalg.svd(Xc, full_matrices=False)
        pcs = Vh[:2]
        pcs = torch.stack([p if cos(p, G) >= 0 else -p for p in pcs])
        ra = np.load(os.path.join(R.PROJECT, "H1", "outputs", "natural_modulation", "resid_axis.npz"))
        dec_cent = np.stack([ra[f"{w}|fit"].astype(np.float32)[L_STATE] for w in DECOYS]).mean(0)
        sem = []
        for w in SEM_DECOYS:
            v = torch.tensor(ra[f"{w}|fit"].astype(np.float32)[L_STATE] - dec_cent); sem.append(v / v.norm())
        sem = torch.stack(sem)
        panel = {"iso": iso, "cov": cov, "pc": pcs, "sem": sem}
        rep = {"norm_G": float(G.norm()), "norm_d": {w: float(d[w].norm()) for w in M.FIT_WORDS}, "norm_v": {w: float(V[w].norm()) for w in M.FIT_WORDS},
               "split_half_cos": cos(G1, G2), "split_half_shared_energy": float(((G1 @ G2) / (G1.norm() * G2.norm())) ** 2),
               "loo_cos_d_G": loo, "cos_panel_ghat": {k: [cos(v[i], G) for i in range(v.shape[0])] for k, v in panel.items()},
               "cov_positions": int(Xc.shape[0]), "top_singular_values": [float(x) for x in S_[:5]], "seed": SEED,
               "sem_axes": SEM_DECOYS, "fit_words": M.FIT_WORDS, "fit_carriers": FIT_CARRIERS, "layer": L_STATE, "run_id": RUN_ID}
        store = {"G": G.numpy(), "ghat": ghat.numpy(), **{f"d|{w}": d[w].numpy() for w in M.FIT_WORDS}, **{f"v|{w}": V[w].numpy() for w in M.FIT_WORDS},
                 **{f"panel|{k}": v.numpy() for k, v in panel.items()}, "G_half1": G1.numpy(), "G_half2": G2.numpy()}
        np.savez_compressed(os.path.join(OUT, "G.npz"), **store)
        rep["G_sha256"] = hashlib.sha256(open(os.path.join(OUT, "G.npz"), "rb").read()).hexdigest()
        json.dump(rep, open(os.path.join(OUT, "fit_report.json"), "w"), indent=1)
        print(f"[fit] |G| {rep['norm_G']:.2f} split-half cos {rep['split_half_cos']:.3f} | cos(panel, G): " +
              json.dumps({k: [round(x, 3) for x in v] for k, v in rep['cos_panel_ghat'].items()}) + f" | {time.time()-t0:.0f}s", flush=True)
        return

    # ------------------------------------------------------------------ PILOT / EVALUATE
    FIT = np.load(os.path.join(OUT, "G.npz")); FR = json.load(open(os.path.join(OUT, "fit_report.json")))
    ghat = torch.tensor(FIT["ghat"], device=dev)
    PANEL = {f"{k}{i:02d}": torch.tensor(FIT[f"panel|{k}"][i], device=dev) for k in ("iso", "cov", "pc", "sem") for i in range(FIT[f"panel|{k}"].shape[0])}
    NATIVE = {}
    if STAGE in ("orthopanel", "evaluate"):
        # Amendment 1: g-orthogonalized panel + covariance-matched directions in the g-orthogonal complement + native-level rows
        def perp(u):
            v = u - (u @ ghat) * ghat; v = v / v.norm(); assert abs(float(v @ ghat)) < 1e-4, "orthogonalization failed"; return v
        ORTHO = {f"{k}_perp": perp(u) for k, u in PANEL.items()}
        rng = np.random.default_rng(SEED + 2)
        Xc = torch.tensor(FIT["cov_resid_centered"], device=dev) if "cov_resid_centered" in FIT else None
        if Xc is None:
            # regenerate the centered per-position block-35 residual matrix of the fit words (same rendering; cheap)
            POS = []
            for w in M.FIT_WORDS:
                for arm in ARMS:
                    for ck in FIT_CARRIERS:
                        car = M.CARRIERS[ck]
                        rr = Rn.render(tok, Rn.user_text_controlled(arm, w, car), car, sources=[("X", w, True)])
                        acts, _ = run(rr.ids); POS.append(acts[L_STATE][0, rr.interior, :].float().clone()); del acts
            Xr = torch.cat(POS, 0); Xc = Xr - Xr.mean(0, keepdim=True)
        Xperp = Xc - (Xc @ ghat)[:, None] * ghat[None, :]
        for k in range(4):
            e = torch.tensor(rng.standard_normal(Xperp.shape[0]), dtype=torch.float32, device=dev)
            u = Xperp.T @ e / np.sqrt(Xperp.shape[0]); ORTHO[f"covperp{k:02d}"] = perp(u)
        NATIVE = {"pc01": PANEL["pc01"], "cov01": PANEL["cov01"]}
        PANEL = ORTHO
        print(f"[{STAGE}] {len(PANEL)} orthogonalized directions; native rows for {list(NATIVE)}", flush=True)
    if STAGE in ("pilot", "orthopanel"):
        cand = [("orange", "tiger"), ("guitar", "mountain"), ("diamond", "castle")]; carriers = FIT_CARRIERS
    else:
        cand = M.EVAL_BANK_1 + M.EVAL_BANK_2; carriers = M.EVAL_CARRIERS
        frz = json.load(open(os.path.join(OUT, "evaluation_freeze.json"))); assert frz.get("frozen") is True, "evaluation freeze note missing"
    matched = matched_pairs(tok, cand, carriers)
    pairs = [p for p, ok in matched if ok]
    print(f"[pairs] {pairs} | excluded {[p for p, ok in matched if not ok]}", flush=True)
    words = sorted({w for p in pairs for w in p})
    TID = {w: Rn.single_token_id(tok, w) for w in words + DECOYS}
    assert all(v is not None for v in TID.values())
    COLS = words + DECOYS
    # 64 seeded random vocabulary columns for the readout-column floor (excluding the named columns)
    rng_cols = np.random.default_rng(SEED + 1)
    named = set(TID.values()); RAND_IDS = []
    while len(RAND_IDS) < 64:
        t = int(rng_cols.integers(0, model.config.text_config.vocab_size if hasattr(model.config, "text_config") else model.config.vocab_size))
        if t not in named and t not in RAND_IDS: RAND_IDS.append(t)
    ro = RO.LensReadout(model, lm, lenses["J_NP"], [TID[w] for w in COLS] + RAND_IDS)
    RANK_LAYERS = list(range(24, 60))
    ra = np.load(os.path.join(R.PROJECT, "H1", "outputs", "natural_modulation", "resid_axis.npz"))   # RESID_P axis, every non-fit stage
    MU = {}
    for w in words:
        if f"{w}|fit" in ra:
            MU[w] = torch.tensor(ra[f"{w}|fit"].astype(np.float32), device=dev)
    missing = [w for w in words if w not in MU]
    assert not missing or STAGE == "evaluate", f"RESID_P axis missing for {missing}; fit it in natural_modulation first"
    print(f"[resid axis] loaded for {len(MU)}/{len(words)} words" + (f"; missing {missing}" if missing else ""), flush=True)

    def pair_axis(X, Y):
        if X in MU and Y in MU:
            v = MU[Y] - MU[X]; return v / v.norm(dim=-1, keepdim=True)
        return None

    RAW, META = {}, {"cells": {}, "pairs": pairs, "excluded": [p for p, ok in matched if not ok], "columns": COLS, "random_column_ids": RAND_IDS, "rank_layers": RANK_LAYERS, "carriers": carriers,
                     "panel": list(PANEL), "doses": DOSES, "l_state": L_STATE, "l_x": L_X, "G_sha256": FR["G_sha256"]}
    n = 0

    def record(tag, r, acts, logits, X, Y, hook=None, h35_clean=None):
        inter = r.interior
        RAW[f"{tag}|z"] = ro.z(acts, inter, ALL_LAYERS).astype(np.float16)
        pa = pair_axis(X, Y)
        if pa is not None:
            hs = torch.stack([acts[l][0, inter, :].float() for l in ALL_LAYERS])
            RAW[f"{tag}|p_pair"] = (hs * pa[:, None, :]).sum(-1).cpu().numpy().astype(np.float32)
        lp = torch.log_softmax(logits[0, inter, :].float(), -1)
        RAW[f"{tag}|lp_margin"] = (lp[:, TID[Y]] - lp[:, TID[X]]).cpu().numpy().astype(np.float32)
        RAW[f"{tag}|rank_XY"] = ro.full_vocab_ranks(acts, inter, RANK_LAYERS, [TID[X], TID[Y]]).astype(np.int32)
        RAW[f"{tag}|g_coord35"] = (acts[L_STATE][0, inter, :].float() @ ghat).cpu().numpy().astype(np.float32)
        cs, ce = r.meta["carrier_start"], r.meta["carrier_end"]
        nll, top1, _ = RO.carrier_damage(logits, r.ids, cs, ce)
        RAW[f"{tag}|nll"] = np.float32(nll); RAW[f"{tag}|top1"] = top1
        if hook is not None:
            st = H.realized_write_stats(hook)
            for k, v in st.items():
                RAW[f"{tag}|w_{k}"] = np.float32(v)
            RAW[f"{tag}|alpha"] = hook.realized["alpha"].numpy().astype(np.float32)

    for ck in carriers:
        car = M.CARRIERS[ck]
        for (a, b) in pairs:
            rend, cache, clean, LEV, H35 = {}, {}, {}, {}, {}
            for arm in ARMS:
                for w in (a, b):
                    r = Rn.render(tok, Rn.user_text_controlled(arm, w, car), car, sources=[("X", w, True)], name=f"{arm}|{w}|{ck}")
                    acts, logits = run(r.ids); n += 1
                    rend[(arm, w)] = r
                    cache[(arm, w)] = {l: acts[l][0, r.spans["X"]["full"], :].clone() for l in ALL}
                    H35[(arm, w)] = acts[L_STATE][0, r.interior, :].float().clone()
                    LEV[(arm, w)] = float((H35[(arm, w)] @ ghat).mean())
                    for nk, nu in NATIVE.items():
                        LEV[(arm, w, nk)] = float((H35[(arm, w)] @ nu).mean())
                    clean[(arm, w)] = (acts, logits)
            for X, Y in ((a, b), (b, a)):
                for arm in ARMS:
                    other = "mention" if arm == "maintain" else "maintain"
                    r = rend[(arm, X)]; span = r.spans["X"]["full"]; inter = r.interior
                    tag = f"{ck}|{arm}|{X}->{Y}"
                    acts0, lg0 = clean[(arm, X)]
                    record(f"{tag}|clean|noswap", r, acts0, lg0, X, Y)
                    record(f"{tag}|donor_clean", rend[(arm, Y)], clean[(arm, Y)][0], clean[(arm, Y)][1], X, Y)
                    # same-source gate
                    acts_s, lg_s = run(r.ids, H.SpanWriter(lm.layers, [l for l in ALL if l >= L_X], span, cache[(arm, X)])); n += 1
                    assert torch.equal(lg_s, lg0) and all(torch.equal(acts_s[l], acts0[l]) for l in ALL), f"same-source != clean {tag}"
                    del acts_s
                    sw = lambda: H.SpanWriter(lm.layers, [l for l in ALL if l >= L_X], span, cache[(arm, Y)])
                    acts, lg = run(r.ids, sw()); n += 1
                    for l in range(L_X):
                        assert torch.equal(acts[l][0, inter, :], acts0[l][0, inter, :]), f"layer<{L_X} identity {tag} L{l}"
                    record(f"{tag}|clean|swap36", r, acts, lg, X, Y); del acts
                    # clean-derived alpha_t: opposite-arm level of the recipient word, minus the clean coordinate
                    Lstar = LEV[(other, X)]
                    alpha = (Lstar - H35[(arm, X)] @ ghat).cpu()
                    META["cells"][tag] = {"L_star": Lstar, "L_own": LEV[(arm, X)], "alpha_mean": float(alpha.mean()), "n_interior": len(inter), "n_tokens": len(r)}
                    conds = [("g", ghat, 1.0)] + ([] if STAGE == "orthopanel" else [(f"dose{s}", ghat, s) for s in DOSES]) + [(k, u, 1.0) for k, u in PANEL.items()]
                    for cname, u, scale in conds:
                        if cname.startswith("dose") and arm != "maintain":
                            continue
                        for ph, swap in (("noswap", False), ("swap36", True)):
                            mv = H.StateMove(lm.layers, L_STATE, inter, ghat, u, level=None, scale=scale, alpha_fixed=alpha)
                            acts, lg = run(r.ids, H.Both(mv, sw() if swap else None)); n += 1
                            record(f"{tag}|{cname}|{ph}", r, acts, lg, X, Y, hook=mv); del acts
                    for nk, nu in NATIVE.items():
                        # native-level move along u itself: alpha_u = L*_u - u.h (recipient word's opposite-arm level along u)
                        alpha_u = (LEV[(other, X, nk)] - H35[(arm, X)] @ nu).cpu()
                        for ph, swap in (("noswap", False), ("swap36", True)):
                            mv = H.StateMove(lm.layers, L_STATE, inter, nu, nu, level=None, scale=1.0, alpha_fixed=alpha_u)
                            acts, lg = run(r.ids, H.Both(mv, sw() if swap else None)); n += 1
                            record(f"{tag}|native_{nk}|{ph}", r, acts, lg, X, Y, hook=mv); del acts
                        META["cells"][tag][f"native_{nk}"] = {"L_star_u": LEV[(other, X, nk)], "L_own_u": LEV[(arm, X, nk)], "alpha_u_mean": float(alpha_u.mean())}
                print(f"  {ck} {X}->{Y}: {n} forwards ({time.time()-t0:.0f}s)", flush=True)
            del cache, clean, H35; torch.cuda.empty_cache()
    META.update({"run_id": RUN_ID, "stage": STAGE, "n_forwards": n, "elapsed_s": round(time.time() - t0, 1), "token_ids": TID, "arms": ARMS, "native_rows": list(NATIVE),
                 "panel_cos_ghat": {k: float(u @ ghat) for k, u in PANEL.items()}})
    if STAGE == "orthopanel":
        # determinism replication gate: the g rows must reproduce the pilot's g rows bitwise (same rendering, same alpha)
        P = np.load(os.path.join(OUT, "raw_pilot.npz")); bad = []
        for k in RAW:
            if "|g|" in k and k.endswith("|z") and k in P.files and not np.array_equal(RAW[k], P[k]): bad.append(k)
        META["g_rows_bitwise_vs_pilot"] = {"n_checked": sum(1 for k in RAW if "|g|" in k and k.endswith("|z")), "n_mismatch": len(bad), "mismatches": bad[:5]}
        print(f"[gate] g rows bitwise vs pilot: {META['g_rows_bitwise_vs_pilot']}", flush=True)
    np.savez_compressed(os.path.join(OUT, f"raw_{STAGE}.npz"), **RAW)
    json.dump(META, open(os.path.join(OUT, f"meta_{STAGE}.json"), "w"), indent=1)
    man = R.manifest_block(); man.update({"run_id": RUN_ID, "stage": STAGE, "script": os.path.relpath(__file__, R.PROJECT), "G_sha256": FR["G_sha256"],
                                          "raw_sha256": hashlib.sha256(open(os.path.join(OUT, f"raw_{STAGE}.npz"), "rb").read()).hexdigest(),
                                          "package1_decisions": "H1/design_specs/package1_decisions.md"})
    json.dump(man, open(os.path.join(OUT, f"manifest_{STAGE}.json"), "w"), indent=1)
    print(f"[done {STAGE}] {n} forwards, {time.time()-t0:.0f}s -> {OUT}")


if __name__ == "__main__":
    main()
