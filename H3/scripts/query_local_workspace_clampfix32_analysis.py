"""Analysis for query_local_workspace stages `clampfix` (Amendment 3, bf16) and `clampfix32` (Amendment 4, float32 residual).

    python query_local_workspace_clampfix_analysis.py clampfix     # re-derives the committed tables (asserted equal)
    python query_local_workspace_clampfix_analysis.py clampfix32   # new tables + report, with the bf16 stage alongside

Margin = [log P(donor value) - log P(own value)] under the condition minus the same under clean; cluster = sum (n = 8),
carriers averaged; flips = cells (of 32) where the donor value beats the own value under the condition. rho, kappa,
write norms: cell means of per-layer values recorded by CoordClampMatched.
"""
import os, sys, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "common", "scripts"))
import registry as R
import stats as S

OUT = R.out_dir("H3", "outputs", "query_local_workspace"); OUT_BF16 = OUT
RES = R.out_dir("H3", "results", "reports"); RES_BF16 = R.out_dir("H3", "results", "tables")
CONDS = ["NEC", "NEC_Qclamp", "NEC_Qclamp_perpm", "NEC_Qclamp_noans", "NEC_Qclamp_noans_perpm", "NEC_Qclamp_ansonly", "NEC_Qclamp_ansonly_perpm"]
CARRIERS = ["C0", "C1", "C2", "C3"]


def tables(stage):
    src = OUT_BF16 if stage == "clampfix" else OUT
    m = json.load(open(os.path.join(src, f"meta_{stage}.json"))); r = np.load(os.path.join(src, f"raw_{stage}.npz"))
    sw = m["sum_words"]; TAB = {}
    for cname, words in (("parity", ["even", "odd"]), ("report", sw)):
        for cond in CONDS:
            per_sum, flips, cells, rho, kap, nreq, nreal, nll, rb = [], 0, 0, [], [], [], [], [], []
            for i in range(8):
                vals = []
                for ck in CARRIERS:
                    base = f"S{i}|{ck}"; cell = m["cells"][base]
                    own = cell["own_parity"] if cname == "parity" else cell["sum"]
                    don = cell["donor_parity"] if cname == "parity" else cell["donor_sum"]
                    io, idn = words.index(own), words.index(don)
                    sc = r[f"{base}|{cname}|{cond}|scores"]; s0 = r[f"{base}|{cname}|clean|scores"]
                    d = float(sc[idn] - sc[io]); vals.append(d - float(s0[idn] - s0[io]))
                    flips += int(d > 0); cells += 1
                    nll.append(float(r[f"{base}|{cname}|{cond}|nll"]) - float(r[f"{base}|{cname}|clean|nll"]))
                    if "clamp" in cond:
                        nzl = r[f"{base}|{cname}|{cond}|clampnorm"] > 0   # block 36 requests nothing at Q (its output there is clean); excluded from rho/kappa (AMENDMENT_4 gate note)
                        rho.append(float(r[f"{base}|{cname}|{cond}|rho"][nzl].mean())); kap.append(float(r[f"{base}|{cname}|{cond}|kappa"][nzl].mean()))
                        if not cond.endswith("_perpm"): rb.append(float(r[f"{base}|{cname}|{cond}|clamperr"]))
                        nreq.append(float(r[f"{base}|{cname}|{cond}|clampnorm"].mean())); nreal.append(float(r[f"{base}|{cname}|{cond}|realnorm"].mean()))
                per_sum.append(float(np.mean(vals)))
            ct = S.cluster_t(per_sum)
            TAB[f"{cname}|{cond}"] = {"margin": {"mean": ct["mean"], "ci": ct["ci"], "n": ct["n"], "n_pos": ct["signs_pos"]},
                                      "flips": flips, "cells": cells, "dnll_mean": float(np.mean(nll)), "dnll_max": float(np.max(nll)),
                                      "rho": (float(np.mean(rho)) if rho else None), "kappa": (float(np.mean(kap)) if kap else None),
                                      "rho_min": (float(np.min(rho)) if rho else None), "kappa_min": (float(np.min(kap)) if kap else None),
                                      "readback_max": (float(np.max(rb)) if rb else None), "n_zero_request_layers": (int((~nzl).sum()) if rho else None),
                                      "norm_req": (float(np.mean(nreq)) if nreq else None), "norm_real": (float(np.mean(nreal)) if nreal else None)}
    TAB["_meta"] = {"stage": stage, "run_id": m.get("run_id"), "n_forwards": m.get("n_forwards"), "elapsed_s": m.get("elapsed_s"),
                    "regime": m.get("regime", "bf16"), "cluster": "sum (n=8), carriers averaged"}
    return TAB


def fmt(x, d=2):
    return "—" if x is None else f"{x:+.{d}f}"


def main():
    stage = sys.argv[1] if len(sys.argv) > 1 else "clampfix32"
    T = tables(stage)
    if stage == "clampfix":   # reproduce the committed tables: margins, flips, rho, kappa, norms must agree
        ref = json.load(open(os.path.join(RES_BF16, "query_local_workspace_clampfix_tables.json")))
        for k, v in ref.items():
            if k == "_meta": continue
            assert abs(v["margin"]["mean"] - T[k]["margin"]["mean"]) < 1e-4 and v["flips"] == T[k]["flips"], k
            for f in ("norm_req", "norm_real"):
                assert (v[f] is None) == (T[k][f] is None) and (v[f] is None or abs(v[f] - T[k][f]) < 1e-4), (k, f)
            # committed rho/kappa were 27-layer means including the zero-request block 36: 26/27 of the committed value must match
            for f in ("rho", "kappa"):
                assert v[f] is None or abs(v[f] - T[k][f] * 26 / 27) < 2e-3, (k, f, v[f], T[k][f])
        print("clampfix tables reproduced exactly (margins, flips, rho, kappa, norms)"); return
    json.dump(T, open(os.path.join(RES_BF16, f"query_local_workspace_{stage}_tables.json"), "w"), indent=1, default=float)
    B = json.load(open(os.path.join(RES_BF16, "query_local_workspace_clampfix_tables.json")))
    L = [f"# H3 · query_local_workspace stage `{stage}` — Amendment 4: the clamp rows under a float32 residual",
         "", f"**Run:** {T['_meta']['n_forwards']} forwards, {T['_meta']['elapsed_s']} s, run id {T['_meta']['run_id']}; regime: {T['_meta']['regime']}. "
         "Same cells, conditions, seeds and planes as `clampfix`; cluster = sum (n = 8), carriers averaged. bf16 columns are the committed `clampfix` values.", "",
         "| condition | parity margin (fp32) | flips | parity (bf16) | report margin (fp32) | flips | report (bf16) | ρ / κ (fp32) | ρ / κ (bf16) | write norm req / real (fp32, report) |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for cond in CONDS:
        p, q = T[f"parity|{cond}"], T[f"report|{cond}"]; pb, qb = B[f"parity|{cond}"], B[f"report|{cond}"]
        rk = "—" if q["rho"] is None else f"{q['rho']:.3f} / {q['kappa']:.3f} (min {q['rho_min']:.3f} / {q['kappa_min']:.3f})"
        rkb = "—" if qb["rho"] is None else f"{qb['rho']:.2f} / {qb['kappa']:.2f}"
        nm = "—" if q["norm_req"] is None else f"{q['norm_req']:.3f} / {q['norm_real']:.3f}"
        L.append(f"| `{cond}` | {fmt(p['margin']['mean'])} [{fmt(p['margin']['ci'][0])}, {fmt(p['margin']['ci'][1])}] | {p['flips']}/{p['cells']} | {fmt(pb['margin']['mean'])} | "
                 f"**{fmt(q['margin']['mean'])}** [{fmt(q['margin']['ci'][0])}, {fmt(q['margin']['ci'][1])}] | {q['flips']}/{q['cells']} | {fmt(qb['margin']['mean'])} | {rk} | {rkb} | {nm} |")
    nec, cl, na = T["report|NEC"]["margin"]["mean"], T["report|NEC_Qclamp"]["margin"]["mean"], T["report|NEC_Qclamp_noans"]["margin"]["mean"]
    necb, nab = B["report|NEC"]["margin"]["mean"], B["report|NEC_Qclamp_noans"]["margin"]["mean"]
    L += ["", f"Report margin removed by the emission-excluded naming clamp: **{100*(1-na/nec):.1f} %** (fp32) vs {100*(1-nab/necb):.1f} % (bf16); by the all-question-token clamp: {100*(1-cl/nec):.1f} %.",
          f"Carrier ΔNLL (condition − clean), max over cells and conditions: {max(v['dnll_max'] for k, v in T.items() if k != '_meta'):+.4f} nats.",
          f"ρ / κ are means over the 26 layers with a nonzero requested write (block 36 requests nothing at the question positions; see AMENDMENT_4 gate note). Plane read-back error after the naming clamps, max over cells: {max(v['readback_max'] for k, v in T.items() if k != '_meta' and v.get('readback_max') is not None):.1e} (bf16: 0.14–0.21)."]
    open(os.path.join(RES, f"query_local_workspace_{stage}.md"), "w").write("\n".join(L) + "\n"); print("\n".join(L))


if __name__ == "__main__":
    main()
