"""Regime gate for query_local_workspace Amendment 4 (registered before the forward): does the float32-residual regime
(`hooks.Fp32Residual`, block 35 onward, bf16 autocast) reproduce the bf16 forward, and does it realize a small
coordinate clamp exactly? Two sums x C0 x both consumers (mechanical check, no scientific rows).

Prints: top-1 agreement, answer-score differences, carrier NLL difference, residual relative distance at the question
positions per layer band, bitwise determinism of the fp32 clean forward, and rho / kappa / clamp read-back error for the
naming-plane clamp under fp32. Gate G0: top-1 identical on every cell, |dNLL| <= 0.02, |d score| <= 0.25 nats for the own
and donor answers. Gate G1: rho in [0.99, 1.01], kappa >= 0.999, read-back error <= 1e-3.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "common", "scripts"))
import torch
import registry as R, materials as M, rendering as Rn, readout as RO, hooks as H
import hooks_fp32 as H32
sys.argv = [sys.argv[0], "clampfix32"]                # import the stage copy without running it
import importlib.util
spec = importlib.util.spec_from_file_location("qlw", os.path.join(HERE, "query_local_workspace_clampfix32.py")); Q = importlib.util.module_from_spec; spec.loader.exec_module(Q)


def main():
    tok = R.make_tokenizer(); TID = {w: Rn.single_token_id(tok, w) for w in Q.COLS}
    from jlens.hf import from_hf
    model = R.load_model(); lm = from_hf(model, tok, compile=False)
    ALL = list(range(R.N_BLOCKS)); run = H.make_run(model, lm, ALL)
    run32 = lambda ids, ctx=None: run(ids, H.Both(H32.Fp32Residual(lm.layers, Q.LX - 1), ctx))
    LEN = R.load_lenses(("J_NP",))["J_NP"]; ro = RO.LensReadout(model, lm, LEN, [TID[w] for w in Q.COLS])
    CONS = {"parity": ("Is their sum even or odd? Answer even or odd.", Q.PAR_WORDS, Q.answer_ids(tok, Q.PAR_WORDS)),
            "report": ("What is the sum of the pair? Answer with one word.", Q.SUM_WORDS, Q.answer_ids(tok, Q.SUM_WORDS))}
    car = M.CARRIERS["C0"]; g0 = g1 = True
    for i in (0, 1):
        pair, dpair = Q.pair_of(i), Q.donor_pair(i)
        for cname, (q, words, WID) in CONS.items():
            r = Rn.render(tok, Q.utext(pair, car), car, sources=[("P", Q.pstr(pair), True)], extra_turns=[(q, "")])
            cs, ce = r.meta["carrier_start"], r.meta["carrier_end"]; Qp = list(range(ce, len(r)))
            a16, l16 = run(r.ids); a32, l32 = run32(r.ids); b32, m32 = run32(r.ids)
            det = bool(torch.equal(l32, m32) and all(torch.equal(a32[l], b32[l]) for l in ALL))
            s16, t16 = Q.score_words(tok, l16, WID, words); s32, t32 = Q.score_words(tok, l32, WID, words)
            own = Q.parity_of(Q.sum_of(i)) if cname == "parity" else Q.sum_of(i); don = Q.parity_of(Q.donor_sum(i)) if cname == "parity" else Q.donor_sum(i)
            n16 = RO.carrier_damage(l16, r.ids, cs, ce)[0]; n32 = RO.carrier_damage(l32, r.ids, cs, ce)[0]
            rel = {l: float((a32[l][0, Qp, :].float() - a16[l][0, Qp, :].float()).norm() / a16[l][0, Qp, :].float().norm()) for l in (35, 40, 50, 62, 63)}
            print(f"S{i} {cname}: top1 {t16!r}/{t32!r} det={det} dNLL={n32-n16:+.4f} d_own={s32[own]-s16[own]:+.3f} d_donor={s32[don]-s16[don]:+.3f} "
                  f"relQ " + " ".join(f"L{l}:{v:.2e}" for l, v in rel.items()), flush=True)
            g0 &= (t16 == t32) and det and abs(n32 - n16) <= 0.02 and abs(s32[own] - s16[own]) <= 0.25 and abs(s32[don] - s16[don]) <= 0.25
            # naming-plane clamp under fp32 on the NEC construction (donor operands, own carrier), all question tokens
            rd = Rn.render(tok, Q.utext(dpair, car), car, sources=[("P", Q.pstr(dpair), True)], extra_turns=[(q, "")])
            add, _ = run32(rd.ids); span = r.spans["P"]["full"]; carr = list(range(cs, ce)); lge = [l for l in ALL if l >= Q.LX]
            NAM = {w: {l: ro.folded_direction(l, TID[w]) for l in Q.QL} for w in (Q.sum_of(i), Q.donor_sum(i))}
            dirs = {l: (NAM[Q.sum_of(i)][l], NAM[Q.donor_sum(i)][l]) for l in Q.QL}; cref = H.plane_coords(a32, Qp, Q.QL, dirs)
            cl = H32.CoordClampMatched(lm.layers, Q.QL, Qp, dirs, cref)
            ctx = H.Both(H.SpanWriter(lm.layers, lge, span, {l: add[l][0, span, :].clone() for l in lge}),
                         H.SpanWriter(lm.layers, lge, carr, {l: a32[l][0, carr, :].clone() for l in lge}), cl)
            ac, lc = run32(r.ids, ctx)
            pre_ok = all(torch.equal(ac[l][0, :ce, :], a32[l][0, :ce, :]) for l in range(0, Q.LX))
            got = H.plane_coords(ac, Qp, Q.QL, dirs); err = max(float((got[l] - cref[l].to(got[l].device)).abs().max()) for l in Q.QL)
            nz = [l for l in Q.QL if float(cl.post[l]["norms_req"].max()) > 0]   # block 36 requests nothing at Q (its output there is clean): excluded, see AMENDMENT_4 gate note
            rho = min(cl.post[l]["rho"] for l in nz); kap = min(cl.post[l]["kappa"] for l in nz); nrm = sum(cl.realized[l] for l in Q.QL) / len(Q.QL)
            bad = [(l, cl.post[l]["rho"], cl.post[l]["kappa"], float(cl.post[l]["norms_req"].min()), float(cl.post[l]["norms_req"].mean()), float(cl.post[l]["norms_real"].mean())) for l in Q.QL if cl.post[l]["rho"] < 0.99 or cl.post[l]["kappa"] < 0.999]
            print("   per-layer (layer, rho, kappa, req_min, req_mean, real_mean) failing the gate: " + "; ".join(f"L{l}: {a:.3f} {b:.3f} {c:.2e} {d:.3f} {e:.3f}" for l, a, b, c, d, e in bad[:6]) + (f" ... {len(bad)} layers" if len(bad) > 6 else ""), flush=True)
            sc, tc = Q.score_words(tok, lc, WID, words)
            print(f"   clamp fp32: rho_min={rho:.4f} kappa_min={kap:.5f} readback_err={err:.2e} req_norm={nrm:.3f} prefix<36 bitwise={pre_ok} top1={tc!r} donor-own={sc[don]-sc[own]:+.2f}", flush=True)
            g1 &= 0.99 <= rho <= 1.01 and kap >= 0.999 and err <= 1e-3 and pre_ok
            del a16, a32, b32, add, ac
    print(f"G0 (regime reproduces bf16): {'PASS' if g0 else 'FAIL'}; G1 (exact clamp write): {'PASS' if g1 else 'FAIL'}")


if __name__ == "__main__":
    main()
