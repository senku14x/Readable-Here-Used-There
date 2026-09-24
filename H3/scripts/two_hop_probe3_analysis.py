"""Analysis for two_hop_organism stage `probe3` (Amendment 8 and its run registration): one scoring pass from raw_probe3.npz +
raw_probe3_zq.npz + meta_probe3.json (+ raw_stage2.npz for the reproduction gate) to H3/results/tables/two_hop_probe3_tables.json,
H3/results/reports/two_hop_probe3.md (generated sections; the hand-written reading is inlined from two_hop_probe3_reading.md)
and H3/results/figures/h3_probe3.{png,pdf}. Usage: two_hop_probe3_analysis.py [probe3|smoke3]"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "..", "common", "scripts"))
import numpy as np
import registry as R

STAGE = sys.argv[1] if len(sys.argv) > 1 else "probe3"
OUT = R.out_dir("H3", "outputs", "two_hop_organism"); REP = R.out_dir("H3", "results", "reports"); TAB = R.out_dir("H3", "results", "tables"); FIG = R.out_dir("H3", "results", "figures")
RAW = dict(np.load(os.path.join(OUT, f"raw_{STAGE}.npz"), allow_pickle=True)); Z = dict(np.load(os.path.join(OUT, f"raw_{STAGE}_zq.npz")))
META = json.load(open(os.path.join(OUT, f"meta_{STAGE}.json"))); R2 = np.load(os.path.join(OUT, "raw_stage2.npz"), allow_pickle=True)
cells = META["cells_ab"]; names = list(dict.fromkeys(b.split("|")[0] for b in cells)); cc_cells = META["cells_c"]; pairs = list(dict.fromkeys(b.split("|")[0] for b in cc_cells))
ROWS_AB, ROWS_C = META["rows_ab"], META["rows_c"]; LZ0 = META["zq_layers"][0]; RB = slice(51 - LZ0, 60 - LZ0); B_BOOT, SEED_BOOT = 2000, 20260907
REF_ROWS = ["q_full_pre", "q_rem_pre", "q_ansrem_pre", "q_J25rem_pre", "q_J25rem_pre_cc"]
CAT = {nm: cells[nm + "|" + META["carriers_ab"][0]].get("category") for nm in names}


def ci(v):
    from scipy import stats as st
    v = np.asarray(v, float); m = float(v.mean()); n = len(v)
    h = float(st.t.ppf(0.975, n - 1) * v.std(ddof=1) / np.sqrt(n)) if n > 1 else float("nan")
    return {"mean": m, "ci": [m - h, m + h], "n_pos": int((v > 0).sum()), "n": int(n)}


def boot(f, arrays, n):
    """Cluster bootstrap over items/pairs: f(*[a[idx] for a in arrays]) -> scalar; percentile 95 % interval."""
    rng = np.random.default_rng(SEED_BOOT); vals = []
    for _ in range(B_BOOT):
        idx = rng.integers(0, n, n); vals.append(f(*[a[idx] for a in arrays]))
    vals = np.asarray(vals, float); vals = vals[np.isfinite(vals)]
    return [float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))] if len(vals) else [float("nan")] * 2


def mg(R_, b, c, clean="clean"): return float((R_[f"{b}|{c}|seq_swap"] - R_[f"{b}|{c}|seq_answer"]) - (R_[f"{b}|{clean}|seq_swap"] - R_[f"{b}|{clean}|seq_answer"]))


byitem = lambda f, nms=None: np.array([np.mean([f(b) for b in cells if b.startswith(nm + "|")]) for nm in (nms or names)])


def zsh(b, c, pair, where="s"):
    """J_NP readout shift at L51-59 minus clean; pair 'int' = swap_to - intermediate, 'ans' = swap_answer - answer (zq columns 0..3)."""
    i1, i2 = (0, 1) if pair == "int" else (2, 3); z = Z[f"{b}|{c}|zq"].astype(np.float32)[RB]; zc = Z[f"{b}|clean|zq"].astype(np.float32)[RB]
    d = (lambda z_: (z_[:, -1, i2] - z_[:, -1, i1]).mean()) if where == "s" else (lambda z_: (z_[:, :-1, i2] - z_[:, :-1, i1]).mean())
    return float(d(z) - d(zc))


def c63(b, c, pair):
    d = RAW[f"{b}|{c}|c63s_{pair}"].astype(np.float32) - RAW[f"{b}|clean|c63s_{pair}"].astype(np.float32); return float(d[1] - d[0])


T = {"stage": STAGE, "run_id": META["run_id"], "n_forwards": META["n_forwards"], "elapsed_s": META["elapsed_s"], "n_items_ab": len(names), "n_cells_ab": len(cells), "n_pairs": len(pairs), "n_cells_c": len(cc_cells),
     "pursuit_agreement_with_stage2": META["pursuit_agreement_with_stage2"], "competence_ab": META["competence_ab"], "competence_c": META["competence_c"]}
M_ = {c: byitem(lambda b: mg(RAW, b, c)) for c in ROWS_AB}; full = M_["q_full_pre"]; fm = float(full.mean())
share = lambda c: float(M_[c].mean() / fm)
rows = {}
for c in ROWS_AB:
    r = {"margin": ci(M_[c]), "share": share(c), "share_ci": boot(lambda a, f_: a.mean() / f_.mean(), [M_[c], full], len(names)), "flips": int(sum(RAW[f"{b}|{c}|seq_swap"] > RAW[f"{b}|{c}|seq_answer"] for b in cells)),
         "rho": float(np.mean([RAW[f"{b}|{c}|rho"] for b in cells])), "kappa": float(np.mean([RAW[f"{b}|{c}|kappa"] for b in cells])), "rberr_max": float(max(RAW[f"{b}|{c}|rberr"] for b in cells)),
         "J_int_s": ci(byitem(lambda b: zsh(b, c, "int"))), "J_ans_s": ci(byitem(lambda b: zsh(b, c, "ans"))), "c63s_int": ci(byitem(lambda b: c63(b, c, "int"))), "c63s_ans": ci(byitem(lambda b: c63(b, c, "ans"))),
         "per_item": dict(zip(names, (M_[c] / full).tolist()))}
    if f"{list(cells)[0]}|{c}|clamp_req" in RAW:
        req = np.stack([RAW[f"{b}|{c}|clamp_req"] for b in cells]); real = np.stack([RAW[f"{b}|{c}|clamp_real"] for b in cells]); kap = np.stack([RAW[f"{b}|{c}|clamp_kappa"] for b in cells]); ok = req > 1e-6
        dims = np.stack([RAW[f"{b}|{c}|clamp_dim"] for b in cells])
        r.update({"clamp_rho_min": float((real[ok] / req[ok]).min()), "clamp_rho_max": float((real[ok] / req[ok]).max()), "clamp_kappa_min": float(kap[ok].min()), "clamp_dim_min": int(dims.min()), "clamp_dim_max": int(dims.max()), "clamp_dim_median": float(np.median(dims))})
    rows[c] = r
T["rows_ab"] = rows
# ---- gates
cl_rows = [c for c in ROWS_AB if "clamp_rho_min" in rows[c]]
realcc = np.stack([RAW[f"{b}|q_J25rem_pre_ccs|clamp_real"] for b in cells]); realr = np.stack([RAW[f"{b}|q_J25rem_pre_ccsr|clamp_real"] for b in cells]); okc = realcc > 1e-6
T["gate3"] = {"fixed_target_ok": bool(all(0.9 <= rows[c]["rho"] <= 1.1 and rows[c]["kappa"] >= 0.99 for c in ROWS_AB)), "clamps_ok": bool(all(0.9 <= rows[c]["clamp_rho_min"] and rows[c]["clamp_rho_max"] <= 1.1 and rows[c]["clamp_kappa_min"] >= 0.99 for c in cl_rows)),
              "ccsr_norm_match_max_rel_dev": float((np.abs(realr[okc] - realcc[okc]) / realcc[okc]).max()),
              "c_rows_ok": bool(all(0.9 <= float(RAW[f"{b}|{c}|rho"]) <= 1.1 and float(RAW[f"{b}|{c}|kappa"]) >= 0.99 for b in cc_cells for c in ROWS_C))}
T["gate3"]["pass"] = bool(T["gate3"]["fixed_target_ok"] and T["gate3"]["clamps_ok"] and T["gate3"]["c_rows_ok"] and T["gate3"]["ccsr_norm_match_max_rel_dev"] <= 0.05)
rep = {c: [abs(mg(RAW, b, c) - mg(R2, b, c)) for b in cells] for c in REF_ROWS}
T["gate4_reproduction"] = {c: {"max_abs_diff": float(max(v)), "fraction_within_0.01": float(np.mean(np.array(v) <= 0.01))} for c, v in rep.items()}
T["gate4_reproduction"]["pass"] = bool(all(T["gate4_reproduction"][c]["fraction_within_0.01"] >= 0.95 for c in REF_ROWS))
T["gate2"] = {"ab": META["competence_ab"], "c": META["competence_c"], "pass": bool(min(META["competence_ab"].values()) >= 0.9 and min(META["competence_c"].values()) >= 0.9)}
ints = byitem(lambda b: zsh(b, "q_J25rem_pre_ccs", "int")); anss = byitem(lambda b: zsh(b, "q_J25rem_pre_ccs", "ans"))
cellok = [abs(zsh(b, "q_J25rem_pre_ccs", "int")) <= 0.3 and abs(zsh(b, "q_J25rem_pre_ccs", "ans")) <= 0.3 for b in cells]
T["gateV"] = {"int_item_mean": float(ints.mean()), "ans_item_mean": float(anss.mean()), "int_item_range": [float(ints.min()), float(ints.max())], "ans_item_range": [float(anss.min()), float(anss.max())],
              "fraction_cells_both_within_0.3": float(np.mean(cellok)), "pass": bool(abs(ints.mean()) <= 0.3 and abs(anss.mean()) <= 0.3)}
T["clamp_sets"] = META["clamp_sets"]; cs_ = list(META["clamp_sets"].values())
T["clamp_set_summary"] = {"F_median": float(np.median([v["F"] for v in cs_])), "X_median": float(np.median([v["X"] for v in cs_])), "X_range": [min(v["X"] for v in cs_), max(v["X"] for v in cs_)],
                          "rank_range": [min(v["rank_min"] for v in cs_), max(v["rank_max"] for v in cs_)], "cos_int_ans_folded_L51_59_mean": float(np.mean([v["cos_int_ans_folded_L51_59"] for v in cs_]))}

# ---- (a) overlap of the intermediate and answer planes
eI, eA, eB = 1 - share("q_rem_pre"), 1 - share("q_ansrem_pre"), 1 - share("q_bothrem_pre")
ovf = lambda f_, r_, a_, b_: ((f_.mean() - r_.mean()) + (f_.mean() - a_.mean()) - (f_.mean() - b_.mean())) / (f_.mean() - r_.mean())
ov = float(ovf(full, M_["q_rem_pre"], M_["q_ansrem_pre"], M_["q_bothrem_pre"])); ov_ci = boot(ovf, [full, M_["q_rem_pre"], M_["q_ansrem_pre"], M_["q_bothrem_pre"]], len(names))
Bs, Bas, Ds = share("q_rem_pre"), share("q_ansrem_pre"), share("q_bothrem_pre")
read_a = "nested" if ov_ci[0] > 0.75 else ("separate" if ov_ci[1] < 0.25 else "partly shared")
T["a"] = {"B": Bs, "B_ans": Bas, "D_both": Ds, "D_additive_expectation": Bs + Bas - 1, "D_nested_expectation": Bas, "e_I": eI, "e_A": eA, "e_both": eB, "overlap_fraction": ov, "overlap_ci": ov_ci,
          "rand4_share": share("q_rand4rem_pre"), "rand4_control_ok": bool(share("q_rand4rem_pre") >= 0.9), "reading": read_a,
          "registered_prediction_scored": {"separate_if_D_le_minB_minus_0.05": bool(Ds <= min(Bs, Bas) - 0.05), "nested_if_D_within_0.05_of_B_ans": bool(abs(Ds - Bas) <= 0.05)},
          "per_relation": {}}
for cat in sorted(set(CAT.values())):
    nm_c = [nm for nm in names if CAT[nm] == cat]; ix = [names.index(nm) for nm in nm_c]
    T["a"]["per_relation"][cat] = {"n": len(nm_c), "overlap_fraction": float(ovf(full[ix], M_["q_rem_pre"][ix], M_["q_ansrem_pre"][ix], M_["q_bothrem_pre"][ix])),
                                   "B": float(M_["q_rem_pre"][ix].mean() / full[ix].mean()), "B_ans": float(M_["q_ansrem_pre"][ix].mean() / full[ix].mean()), "D": float(M_["q_bothrem_pre"][ix].mean() / full[ix].mean())}

# ---- (b) the stronger consumer clamp
C = share("q_J25rem_pre_ccs"); un = rows["q_J25rem_pre"]["margin"]; ccsr_in = bool(un["ci"][0] <= rows["q_J25rem_pre_ccsr"]["margin"]["mean"] <= un["ci"][1])
per_item_C = M_["q_J25rem_pre_ccs"] / full
if not T["gateV"]["pass"]: read_b = "not read: gate V failed (the stronger clamp did not hold the readouts at s)"
elif not ccsr_in: read_b = "not read: the random-rank clamp control left the un-clamped interval"
elif C >= 0.4: read_b = f"a route not J-readable at the answer position through block 62 carries at least {C:.2f} of the question-turn effect (bracket [{C:.2f}, 0.51] with Stage 2)"
elif C <= 0.2: read_b = "Stage 2's surviving half was the partial clamp: the effect reaches the answer through readable content at the answer position"
else: read_b = f"C = {C:.2f} is the result (bracket [{C:.2f}, 0.51] with Stage 2's upper bound)"
T["b"] = {"C": C, "C_ci": rows["q_J25rem_pre_ccs"]["share_ci"], "unclamped": share("q_J25rem_pre"), "partial_clamp_cc": share("q_J25rem_pre_cc"), "control_ccsr": share("q_J25rem_pre_ccsr"),
          "ccsr_within_unclamped_interval": ccsr_in, "gateV": T["gateV"], "reading": read_b, "per_item_C_median": float(np.median(per_item_C)), "items_C_ge_0.4": int((per_item_C >= 0.4).sum()), "items_C_le_0.2": int((per_item_C <= 0.2).sum()),
          "strong_minus_partial_clamp_nats": ci(M_["q_J25rem_pre_cc"] - M_["q_J25rem_pre_ccs"]), "block63_reentry": {c: {"int": rows[c]["c63s_int"]["mean"], "ans": rows[c]["c63s_ans"]["mean"]} for c in ("q_full_pre", "q_J25rem_pre", "q_J25rem_pre_cc", "q_J25rem_pre_ccs", "q_J25rem_pre_ccsr")},
          "per_relation": {cat: float(M_["q_J25rem_pre_ccs"][[names.index(nm) for nm in names if CAT[nm] == cat]].mean() / full[[names.index(nm) for nm in names if CAT[nm] == cat]].mean()) for cat in sorted(set(CAT.values()))}}

# ---- (c) relation transfer
def mc(b, c, tm):
    base = "lang_clean" if c in ("q_xfer", "q_native_lang", "q_xfer_rand") else "cap_clean"
    return float((RAW[f"{b}|{c}|donor_{tm}"] - RAW[f"{b}|{c}|own_{tm}"]) - (RAW[f"{b}|{base}|donor_{tm}"] - RAW[f"{b}|{base}|own_{tm}"]))


bypair = lambda f: np.array([np.mean([f(b) for b in cc_cells if b.startswith(p + "|")]) for p in pairs])
MC = {(c, tm): bypair(lambda b: mc(b, c, tm)) for c in ROWS_C for tm in ("lang", "cap")}
ratio = lambda a, b_: float(a.mean() / b_.mean())
fL, fC = ratio(MC[("q_xfer", "lang")], MC[("q_native_lang", "lang")]), ratio(MC[("q_mirror", "cap")], MC[("q_native_cap", "cap")])
fL_ci = boot(lambda a, b_: a.mean() / b_.mean(), [MC[("q_xfer", "lang")], MC[("q_native_lang", "lang")]], len(pairs)); fC_ci = boot(lambda a, b_: a.mean() / b_.mean(), [MC[("q_mirror", "cap")], MC[("q_native_cap", "cap")]], len(pairs))
gtL = int((MC[("q_xfer", "lang")] > MC[("q_xfer_rand", "lang")]).sum()); gtC = int((MC[("q_mirror", "cap")] > MC[("q_mirror_rand", "cap")]).sum())
randL, randC = ci(MC[("q_xfer_rand", "lang")]), ci(MC[("q_mirror_rand", "cap")]); np_ = len(pairs)
thr = max(1, int(np.ceil(6 * np_ / 7)))
def read_c(f, f_ci, gt, m_main, rnd, m_other, up_word, ans_word):
    if gt >= thr and f >= 0.3: return f"upstream content present: the transplanted state carries something upstream of the answer ({up_word}) that the other question uses"
    if f <= 0.1 and rnd["ci"][0] <= m_main.mean() <= rnd["ci"][1] and m_other.mean() > 0: return f"answer content only: the transplanted state carries the {ans_word}, not the country"
    return f"neither registered pattern: f = {f:.2f}, {gt}/{np_} pairs above the random control"
T["c"] = {"pairs": pairs, "f_L": fL, "f_L_ci": fL_ci, "f_C_mirror": fC, "f_C_ci": fC_ci, "pairs_xfer_above_random": gtL, "pairs_mirror_above_random": gtC,
          "means": {f"{c}|m_{tm}": ci(MC[(c, tm)]) for (c, tm) in MC}, "per_pair": {p: {f"{c}|m_{tm}": float(MC[(c, tm)][i]) for (c, tm) in MC} for i, p in enumerate(pairs)},
          "capital_push_in_language_question_over_native_capital_push": ratio(MC[("q_xfer", "cap")], MC[("q_native_cap", "cap")]),
          "language_push_in_capital_question_over_native_language_push": ratio(MC[("q_mirror", "lang")], MC[("q_native_lang", "lang")]),
          "reading_xfer": read_c(fL, fL_ci, gtL, MC[("q_xfer", "lang")], randL, MC[("q_xfer", "cap")], "the country, or the cue city it came from", "capital"),
          "reading_mirror": read_c(fC, fC_ci, gtC, MC[("q_mirror", "cap")], randC, MC[("q_mirror", "lang")], "the country, or the cue city it came from", "language"),
          "greedy": {b: {c: str(RAW[f"{b}|{c}|greedy"]) for c in ["cap_clean", "cap_donor", "lang_clean", "lang_donor"] + ROWS_C} for b in cc_cells}}
json.dump(T, open(os.path.join(TAB, f"two_hop_{STAGE}_tables.json"), "w"), indent=1, default=str)

# ---- report
f2 = lambda x: f"{x:+.2f}"; f3 = lambda x: f"{x:+.3f}"; NI = len(names)
L = [f"# two_hop_organism · stage `{STAGE}` — joint-plane removal, a verified consumer clamp, and relation transfer (Amendment 8)\n",
     f"Run `{META['run_id']}`, {META['n_forwards']} forwards, {META['elapsed_s']} s; Qwen3.6-27B, thinking off, float32 residual from block {META['fp32_from']} on every forward; sequence-log-prob endpoint. Rows (a) and (b): {len(cells)} cells ({NI} items admitted in Stage 2 × {len(META['carriers_ab'])} carriers), cluster = item. Row (c): {len(cc_cells)} cells ({len(pairs)} city pairs × {len(META['carriers_c'])} carriers), cluster = pair. "
     f"Writes at blocks {META['swap_layers'][0]}–{META['swap_layers'][1]} on `q_pre`; clamps at the scoring position s only. Design: `H3/design_specs/two_hop_organism.md` Amendment 8 and its run registration; battery `H3/scripts/two_hop_probe3.py`; generated by `two_hop_probe3_analysis.py`; the last section is hand-written.\n",
     "## 1. Gates\n",
     f"- Gate 1 (rendering, geometry, question-turn token ids equal across recipient, donor and both templates): asserted per cell in the battery — PASS.",
     f"- Gate 2 (competence, sequence endpoint): rows (a, b) clean {T['competence_ab']['clean']:.2f} / donor {T['competence_ab']['donor']:.2f}; row (c) capital clean {T['competence_c']['cap_clean']:.2f}, capital donor {T['competence_c']['cap_donor']:.2f}, language clean {T['competence_c']['lang_clean']:.2f}, language donor {T['competence_c']['lang_donor']:.2f} — **{'PASS' if T['gate2']['pass'] else 'FAIL'}**.",
     f"- Gate 3 (realized writes): fixed-target rows ρ {min(rows[c]['rho'] for c in ROWS_AB):.4f}–{max(rows[c]['rho'] for c in ROWS_AB):.4f}, κ ≥ {min(rows[c]['kappa'] for c in ROWS_AB):.4f}, read-back ≤ {max(rows[c]['rberr_max'] for c in ROWS_AB):.1e}; clamps ρ {min(rows[c]['clamp_rho_min'] for c in cl_rows):.4f}–{max(rows[c]['clamp_rho_max'] for c in cl_rows):.4f}, κ ≥ {min(rows[c]['clamp_kappa_min'] for c in cl_rows):.4f}; `_ccsr` norm within {100*T['gate3']['ccsr_norm_match_max_rel_dev']:.4f} % of `_ccs`; row (c) writes {'exact' if T['gate3']['c_rows_ok'] else 'NOT within tolerance'} — **{'PASS' if T['gate3']['pass'] else 'FAIL'}**.",
     f"- Gate 4 (reproduction of Stage 2 by the same-run reference rows, ≤ 0.01 nats in ≥ 0.95 of cells): " + "; ".join(f"`{c}` max |Δ| {T['gate4_reproduction'][c]['max_abs_diff']:.1e}" for c in REF_ROWS) + f" — **{'PASS' if T['gate4_reproduction']['pass'] else 'FAIL'}**. Pursuit selections identical to Stage 2's for {100*T['pursuit_agreement_with_stage2']['qpre_vectors_identical_first25']:.1f} % of `q_pre` vectors and {100*T['pursuit_agreement_with_stage2']['s_vectors_identical_first25']:.1f} % of s vectors.",
     f"- Gate V (under `q_J25rem_pre_ccs`, item-mean readout shifts at s within ±0.3): intermediate {f2(T['gateV']['int_item_mean'])} (items {f2(T['gateV']['int_item_range'][0])} to {f2(T['gateV']['int_item_range'][1])}), answer {f2(T['gateV']['ans_item_mean'])} (items {f2(T['gateV']['ans_item_range'][0])} to {f2(T['gateV']['ans_item_range'][1])}); {100*T['gateV']['fraction_cells_both_within_0.3']:.0f} % of cells within ±0.3 on both — **{'PASS' if T['gateV']['pass'] else 'FAIL'}**.",
     f"- Clamp set sizes: every single-token form of the four words and aliases, median {T['clamp_set_summary']['F_median']:.0f}; translation atoms median {T['clamp_set_summary']['X_median']:.0f}, range {T['clamp_set_summary']['X_range'][0]}–{T['clamp_set_summary']['X_range'][1]}; pinned rank {T['clamp_set_summary']['rank_range'][0]}–{T['clamp_set_summary']['rank_range'][1]}. Mean cosine between the intermediate's and the answer's folded directions at L51–59: {T['clamp_set_summary']['cos_int_ans_folded_L51_59_mean']:.2f}.\n",
     "## 2. Main table, rows (a) and (b) (sequence endpoint; margin minus clean; item-clustered intervals; shares are ratios of item means with cluster-bootstrap intervals)\n",
     "| row | margin (nats) | 95 % CI | items > 0 | share of `q_full_pre` | share 95 % CI | flips | J_NP int readout at s | J_NP answer readout at s | block-63 re-entry at s, int / ans | clamp rank |",
     "|---|---|---|---|---|---|---|---|---|---|---|"]
for c in ROWS_AB:
    r = rows[c]; m = r["margin"]
    L.append(f"| `{c}` | {f2(m['mean'])} | [{f2(m['ci'][0])}, {f2(m['ci'][1])}] | {m['n_pos']}/{m['n']} | {f3(r['share'])} | [{r['share_ci'][0]:.3f}, {r['share_ci'][1]:.3f}] | {r['flips']}/{len(cells)} | {f2(r['J_int_s']['mean'])} | {f2(r['J_ans_s']['mean'])} | {f2(r['c63s_int']['mean'])} / {f2(r['c63s_ans']['mean'])} | "
             + (f"{r['clamp_dim_min']}–{r['clamp_dim_max']}" if "clamp_dim_min" in r else "—") + " |")
A = T["a"]; Bb = T["b"]; Cc = T["c"]
L += ["\n## 3. Row (a): are the intermediate's and the answer's readable handles separate or nested?\n",
      f"Same-run shares: intermediate plane removed B = {f3(A['B'])}, answer plane removed B_ans = {f3(A['B_ans'])}, **both removed D = {f3(A['D_both'])}** (random 4-frame control {f3(A['rand4_share'])}). If the two planes carried separate parts, D would be about B + B_ans − 1 = {f3(A['D_additive_expectation'])}; if the intermediate's part were inside the answer's, D would be about B_ans = {f3(A['D_nested_expectation'])}. "
      f"Overlap fraction (the share of the intermediate plane's effect already carried by the answer plane) **{A['overlap_fraction']:.2f}**, cluster-bootstrap [{A['overlap_ci'][0]:.2f}, {A['overlap_ci'][1]:.2f}] → registered reading: **{A['reading']}**. "
      f"Registered prediction scored as written: 'separate' test (D ≤ min(B, B_ans) − 0.05) {A['registered_prediction_scored']['separate_if_D_le_minB_minus_0.05']}; 'nested' test (D within 0.05 of B_ans) {A['registered_prediction_scored']['nested_if_D_within_0.05_of_B_ans']}.\n",
      "| relation (descriptive) | items | B | B_ans | D | overlap fraction |", "|---|---|---|---|---|---|"]
for cat, v in A["per_relation"].items(): L.append(f"| {cat} | {v['n']} | {v['B']:+.2f} | {v['B_ans']:+.2f} | {v['D']:+.2f} | {v['overlap_fraction']:+.2f} |")
L += ["\n## 4. Row (b): the verified consumer clamp\n",
      f"Un-clamped J25 complement {f3(Bb['unclamped'])}; Stage 1/2 partial clamp (25 pursuit atoms at s) {f3(Bb['partial_clamp_cc'])}; **stronger clamp C = {f3(Bb['C'])}** [{Bb['C_ci'][0]:.3f}, {Bb['C_ci'][1]:.3f}]; rank-matched random clamp {f3(Bb['control_ccsr'])} ({'within' if Bb['ccsr_within_unclamped_interval'] else 'outside'} the un-clamped interval). "
      f"The stronger clamp removes {f2(Bb['strong_minus_partial_clamp_nats']['mean'])} nats beyond the partial one [{f2(Bb['strong_minus_partial_clamp_nats']['ci'][0])}, {f2(Bb['strong_minus_partial_clamp_nats']['ci'][1])}], {Bb['strong_minus_partial_clamp_nats']['n_pos']}/{NI} items. Per item, C has median {Bb['per_item_C_median']:.2f}; {Bb['items_C_ge_0.4']}/{NI} items ≥ 0.4 and {Bb['items_C_le_0.2']}/{NI} ≤ 0.2. "
      f"Gate V {'passes' if Bb['gateV']['pass'] else 'FAILS'} → registered reading: **{Bb['reading']}**.\n",
      "Block-63 re-entry at s (Δproj on the raw unit naming directions at the final, unclamped block, swap minus own, minus clean; intermediate pair / answer pair): " + "; ".join(f"`{c}` {f2(v['int'])} / {f2(v['ans'])}" for c, v in Bb["block63_reentry"].items()) + ".\n",
      "Per relation (descriptive): " + ", ".join(f"{cat} {v:.2f}" for cat, v in Bb["per_relation"].items()) + ".\n",
      "## 5. Row (c): does the question-turn state carry the country or the answer?\n",
      "Margins in nats, carriers averaged, minus that rendering's clean value. m_lang = donor's language − own language; m_cap = donor's capital − own capital. Cluster = pair.\n",
      "| row | rendering | written delta | m_lang | 95 % CI | pairs > 0 | m_cap | 95 % CI | pairs > 0 |", "|---|---|---|---|---|---|---|---|---|"]
desc = {"q_xfer": ("language question", "capital question's delta"), "q_native_lang": ("language question", "its own delta"), "q_xfer_rand": ("language question", "random, same norm as the capital delta"),
        "q_mirror": ("capital question", "language question's delta"), "q_native_cap": ("capital question", "its own delta"), "q_mirror_rand": ("capital question", "random, same norm as the language delta")}
for c in ROWS_C:
    a_, b_ = Cc["means"][f"{c}|m_lang"], Cc["means"][f"{c}|m_cap"]
    L.append(f"| `{c}` | {desc[c][0]} | {desc[c][1]} | {f2(a_['mean'])} | [{f2(a_['ci'][0])}, {f2(a_['ci'][1])}] | {a_['n_pos']}/{a_['n']} | {f2(b_['mean'])} | [{f2(b_['ci'][0])}, {f2(b_['ci'][1])}] | {b_['n_pos']}/{b_['n']} |")
L += [f"\nTransfer fraction into the language question f_L = m_lang(`q_xfer`) / m_lang(`q_native_lang`) = **{Cc['f_L']:.2f}** [{Cc['f_L_ci'][0]:.2f}, {Cc['f_L_ci'][1]:.2f}], {Cc['pairs_xfer_above_random']}/{len(pairs)} pairs above the random control → **{Cc['reading_xfer']}**. "
      f"The same transplanted state pushes the language question toward the donor's *capital* by {f2(Cc['means']['q_xfer|m_cap']['mean'])} nats, {Cc['capital_push_in_language_question_over_native_capital_push']:.2f} of the capital question's own push.\n",
      f"Mirror f_C = m_cap(`q_mirror`) / m_cap(`q_native_cap`) = **{Cc['f_C_mirror']:.2f}** [{Cc['f_C_ci'][0]:.2f}, {Cc['f_C_ci'][1]:.2f}], {Cc['pairs_mirror_above_random']}/{len(pairs)} pairs above the random control → **{Cc['reading_mirror']}**. The language question's state pushes the capital question toward the donor's *language* by {f2(Cc['means']['q_mirror|m_lang']['mean'])} nats, {Cc['language_push_in_capital_question_over_native_language_push']:.2f} of the language question's own push.\n",
      "Scope (registered): row (c) separates answer content from content upstream of the answer; it cannot separate the country from the cue city it was derived from.\n",
      "| pair | m_lang xfer / native / random | m_cap xfer | m_cap mirror / native / random | m_lang mirror |", "|---|---|---|---|---|"]
for p in pairs:
    v = Cc["per_pair"][p]
    L.append(f"| {p} | {f2(v['q_xfer|m_lang'])} / {f2(v['q_native_lang|m_lang'])} / {f2(v['q_xfer_rand|m_lang'])} | {f2(v['q_xfer|m_cap'])} | {f2(v['q_mirror|m_cap'])} / {f2(v['q_native_cap|m_cap'])} / {f2(v['q_mirror_rand|m_cap'])} | {f2(v['q_mirror|m_lang'])} |")
L.append("\n## 6. Per-item shares, rows (a) and (b)\n")
L.append("| item | relation | B | B_ans | D (both) | rand4 | J25 rem | + partial clamp | + stronger clamp C | + random clamp |"); L.append("|---|---|---|---|---|---|---|---|---|---|")
for nm in names:
    g = lambda c: rows[c]["per_item"][nm]
    L.append(f"| {nm} | {CAT[nm]} | {g('q_rem_pre'):+.2f} | {g('q_ansrem_pre'):+.2f} | {g('q_bothrem_pre'):+.2f} | {g('q_rand4rem_pre'):+.2f} | {g('q_J25rem_pre'):+.2f} | {g('q_J25rem_pre_cc'):+.2f} | {g('q_J25rem_pre_ccs'):+.2f} | {g('q_J25rem_pre_ccsr'):+.2f} |")
L.append("\n## 7. Interpretation, licensed / not licensed, next decision\n")
_reading = os.path.join(REP, f"two_hop_{STAGE}_reading.md")
L.append(open(_reading).read() if os.path.exists(_reading) else "_(hand-written after reading the tables; kept in `two_hop_" + STAGE + "_reading.md` and inlined here)_\n")
open(os.path.join(REP, f"two_hop_{STAGE}.md"), "w").write("\n".join(L))

# ---- figure from the tables only
try:
    for _p in ("/root/.claude/skills/iclr-plots/scripts", os.path.join(R.PROJECT, ".claude", "skills", "iclr-plots", "scripts"), "/workspace/.claude/skills/iclr-plots/scripts"): sys.path.insert(0, _p)
    import iclrplot as ip; ip.setup()
except Exception as e:
    print("iclrplot not used:", e)
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
fig, axs = plt.subplots(1, 3, figsize=(5.5, 2.0), gridspec_kw={"width_ratios": [1.0, 1.15, 1.25]})
def bars(ax, keys, labels, colors, title):
    vals = [rows[k]["share"] for k in keys]; lo = [rows[k]["share"] - rows[k]["share_ci"][0] for k in keys]; hi = [rows[k]["share_ci"][1] - rows[k]["share"] for k in keys]
    ax.bar(range(len(keys)), vals, yerr=[lo, hi], color=colors, capsize=1.5, width=0.7)
    for i, k in enumerate(keys): ax.scatter(np.full(NI, i) + np.linspace(-0.2, 0.2, NI), [rows[k]["per_item"][nm] for nm in names], s=2, color="k", alpha=0.4, zorder=3)
    ax.set_xticks(range(len(keys))); ax.set_xticklabels(labels, fontsize=4.8, rotation=50, ha="right", rotation_mode="anchor"); ax.set_ylim(-0.05, 1.15); ax.set_title(title, fontsize=6.5); ax.axhline(0, color="k", lw=0.4)
bars(axs[0], ["q_rem_pre", "q_ansrem_pre", "q_bothrem_pre", "q_rand4rem_pre"], ["int plane removed", "answer plane removed", "both removed", "random 4-frame"], ["#d62728", "#fb6a4a", "#67000d", "#bdbdbd"], "(a) joint plane removal")
axs[0].axhline(A["D_additive_expectation"], color="#67000d", lw=0.5, ls=":"); axs[0].set_ylabel("share of q_full_pre")
bars(axs[1], ["q_J25rem_pre", "q_J25rem_pre_cc", "q_J25rem_pre_ccs", "q_J25rem_pre_ccsr"], ["J25 complement", "+ partial clamp", "+ verified clamp", "+ random clamp"], ["#a50f15", "#67000d", "#3f007d", "#fcae91"], "(b) consumer clamp at s")
axs[1].axhline(0.5, color="k", lw=0.4, ls=":"); axs[1].axhline(0.2, color="k", lw=0.4, ls=":")
ax = axs[2]; x = np.arange(len(pairs)); w_ = 0.26
for j, (c, col, lab) in enumerate((("q_native_lang", "#4c4c4c", "language Δ (native)"), ("q_xfer", "#1f77b4", "capital Δ (transfer)"), ("q_xfer_rand", "#bdbdbd", "random Δ"))):
    ax.bar(x + (j - 1) * w_, [Cc["per_pair"][p][f"{c}|m_lang"] for p in pairs], w_, color=col, label=lab)
PL = {q["name"]: f"{q['A']}/{q['B']}" for q in META["pairs"]}; ax.set_xticks(x); ax.set_xticklabels([PL[p] for p in pairs], fontsize=4.8, rotation=50, ha="right", rotation_mode="anchor"); ax.axhline(0, color="k", lw=0.4)
ax.set_ylabel("push toward donor's language (nats)", fontsize=5.5); ax.set_title(f"(c) language question, f_L = {Cc['f_L']:.2f}", fontsize=6.5); ax.legend(fontsize=4.2, frameon=False, loc="upper right")
fig.tight_layout(); fig.savefig(os.path.join(FIG, f"h3_{STAGE}.png"), dpi=200); fig.savefig(os.path.join(FIG, f"h3_{STAGE}.pdf"))
print(json.dumps({k: T[k] for k in ("gate2", "gate3", "gate4_reproduction", "gateV")}, indent=1, default=str))
print(json.dumps({"a": {k: v for k, v in A.items() if k != "per_relation"}, "b": {k: v for k, v in Bb.items() if k not in ("gateV",)}, "c": {k: v for k, v in Cc.items() if k in ("f_L", "f_L_ci", "f_C_mirror", "f_C_ci", "pairs_xfer_above_random", "pairs_mirror_above_random", "reading_xfer", "reading_mirror", "capital_push_in_language_question_over_native_capital_push", "language_push_in_capital_question_over_native_language_push")}}, indent=1, default=str))
