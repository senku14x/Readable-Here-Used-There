"""Analysis for two_hop_organism stage `probe4` (Amendment 9): one scoring pass from raw_probe4.npz + raw_probe4_zq.npz + meta_probe4.json
(+ raw_probe3.npz for the reproduction gate) to H3/results/tables/two_hop_probe4_tables.json, H3/results/reports/two_hop_probe4.md (generated
sections; the hand-written reading inlined from two_hop_probe4_reading.md) and H3/results/figures/h3_probe4.{png,pdf}.
Usage: two_hop_probe4_analysis.py [probe4|smoke4]"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "..", "common", "scripts"))
import numpy as np
import registry as R

STAGE = sys.argv[1] if len(sys.argv) > 1 else "probe4"
OUT = R.out_dir("H3", "outputs", "two_hop_organism"); REP = R.out_dir("H3", "results", "reports"); TAB = R.out_dir("H3", "results", "tables"); FIG = R.out_dir("H3", "results", "figures")
RAW = dict(np.load(os.path.join(OUT, f"raw_{STAGE}.npz"), allow_pickle=True)); Z = dict(np.load(os.path.join(OUT, f"raw_{STAGE}_zq.npz")))
META = json.load(open(os.path.join(OUT, f"meta_{STAGE}.json"))); R3 = np.load(os.path.join(OUT, "raw_probe3.npz"), allow_pickle=True)
cells = META["cells_ab"]; names = list(dict.fromkeys(b.split("|")[0] for b in cells)); ccells = META["cells_c"]; pairs = list(dict.fromkeys(b.split("|")[0] for b in ccells))
ROWS_AB, ROWS_C = META["rows_ab"], META["rows_c"]; LZ0 = META["zq_layers"][0]; RB = slice(51 - LZ0, 60 - LZ0); NI = len(names); B_BOOT, SEED_BOOT = 2000, 20260907
CAT = {nm: cells[nm + "|" + META["carriers_ab"][0]].get("category") for nm in names}
MASKED = {r for r in ROWS_AB if r.endswith("m63A")}


def ci(v):
    from scipy import stats as st
    v = np.asarray(v, float); m = float(v.mean()); n = len(v)
    h = float(st.t.ppf(0.975, n - 1) * v.std(ddof=1) / np.sqrt(n)) if n > 1 else float("nan")
    return {"mean": m, "ci": [m - h, m + h], "n_pos": int((v > 0).sum()), "n": int(n)}


def boot(f, arrays, n):
    rng = np.random.default_rng(SEED_BOOT); vals = []
    for _ in range(B_BOOT):
        idx = rng.integers(0, n, n); vals.append(f(*[a[idx] for a in arrays]))
    vals = np.asarray(vals, float); vals = vals[np.isfinite(vals)]
    return [float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))] if len(vals) else [float("nan")] * 2


lse = lambda v: float(np.log(np.sum(np.exp(np.asarray(v, float) - np.max(v)))) + np.max(v))


def mg(R_, b, row, first=False):
    """margin (swap - answer) minus the row's baseline: clean_m63A for the masked rows, clean otherwise; first=True uses first-token log-probs."""
    base = "clean_m63A" if row in MASKED else "clean"
    if first:
        f = lambda r_: lse(R_[f"{b}|{r_}|lpf_swap_all"]) - lse(R_[f"{b}|{r_}|lpf_answer_all"])
        return f(row) - f(base)
    return float((R_[f"{b}|{row}|seq_swap"] - R_[f"{b}|{row}|seq_answer"]) - (R_[f"{b}|{base}|seq_swap"] - R_[f"{b}|{base}|seq_answer"]))


byitem = lambda f: np.array([np.mean([f(b) for b in cells if b.startswith(nm + "|")]) for nm in names])


def zsh(b, row, pair):
    i1, i2 = (0, 1) if pair == "int" else (2, 3); z = Z[f"{b}|{row}|zq"].astype(np.float32)[RB]; zc = Z[f"{b}|clean|zq"].astype(np.float32)[RB]
    return float((z[:, -1, i2] - z[:, -1, i1]).mean() - (zc[:, -1, i2] - zc[:, -1, i1]).mean())


T = {"stage": STAGE, "run_id": META["run_id"], "n_forwards": META["n_forwards"], "elapsed_s": META["elapsed_s"], "n_items": NI, "n_cells_ab": len(cells), "n_pairs": len(pairs), "n_cells_c": len(ccells),
     "competence_ab": META["competence_ab"], "competence_c": META["competence_c"], "clamp_stats": META["clamp_stats"]}
M_ = {r: byitem(lambda b: mg(RAW, b, r)) for r in ROWS_AB if r != "clean_m63A"}; MF = {r: byitem(lambda b: mg(RAW, b, r, first=True)) for r in ROWS_AB if r != "clean_m63A"}
full, fullF = M_["q_full_pre"], MF["q_full_pre"]
share = lambda r: float(M_[r].mean() / full.mean()); shareF = lambda r: float(MF[r].mean() / fullF.mean())
rows = {r: {"margin": ci(M_[r]), "share": share(r), "share_ci": boot(lambda a, f_: a.mean() / f_.mean(), [M_[r], full], NI), "first_token_share": shareF(r),
            "first_token_margin": ci(MF[r]), "flips": int(sum(RAW[f"{b}|{r}|seq_swap"] > RAW[f"{b}|{r}|seq_answer"] for b in cells)),
            "rho": float(np.mean([RAW[f"{b}|{r}|rho"] for b in cells])), "kappa": float(np.mean([RAW[f"{b}|{r}|kappa"] for b in cells])), "rberr_max": float(max(RAW[f"{b}|{r}|rberr"] for b in cells)),
            "J_int_s": ci(byitem(lambda b: zsh(b, r, "int"))), "J_ans_s": ci(byitem(lambda b: zsh(b, r, "ans"))), "per_item": dict(zip(names, (M_[r] / full).tolist()))} for r in M_}
T["rows_ab"] = rows
# ---- gates
rep = {r: [abs(mg(RAW, b, r) - mg(R3, b, r)) for b in cells] for r in ("q_full_pre", "q_J25rem_pre", "q_J25rem_pre_ccs")}
T["gate_reproduction"] = {r: {"max_abs_diff": float(max(v)), "fraction_within_0.01": float(np.mean(np.array(v) <= 0.01))} for r, v in rep.items()}; T["gate_reproduction"]["pass"] = bool(all(T["gate_reproduction"][r]["fraction_within_0.01"] >= 0.95 for r in rep))
cs = META["clamp_stats"]
T["gate_writes"] = {"fixed_target_ok": bool(all(0.9 <= rows[r]["rho"] <= 1.1 and rows[r]["kappa"] >= 0.99 for r in rows)), "clamps_ok": bool(all(0.9 <= v["rho_min"] and v["rho_max"] <= 1.1 and v["kappa_min"] >= 0.99 for v in cs.values())),
                    "ccsrA_norm_match_max_rel_dev": cs.get("q_J25rem_pre_ccsrA", {}).get("normdev_max", float("nan")),
                    "c_rows_ok": bool(all(0.9 <= float(RAW[f"{b}|{c}|rho"]) <= 1.1 and float(RAW[f"{b}|{c}|kappa"]) >= 0.99 for b in ccells for c in ROWS_C))}
T["gate_writes"]["pass"] = bool(T["gate_writes"]["fixed_target_ok"] and T["gate_writes"]["clamps_ok"] and T["gate_writes"]["c_rows_ok"] and T["gate_writes"]["ccsrA_norm_match_max_rel_dev"] <= 0.05)
T["gate_L"] = {"leak_max": float(max(META["leak"].values())), "pass": bool(max(META["leak"].values()) <= 1e-6)}
T["gate_S"] = {"sfullA_m63A_item_mean_margin": float(M_["q_J25rem_pre_sfullA_m63A"].mean()), "max_abs_item": float(np.abs(M_["q_J25rem_pre_sfullA_m63A"]).max()), "pass": bool(abs(M_["q_J25rem_pre_sfullA_m63A"].mean()) <= 0.05)}
vi, va = byitem(lambda b: zsh(b, "q_J25rem_pre_ccsA", "int")), byitem(lambda b: zsh(b, "q_J25rem_pre_ccsA", "ans"))
T["gate_V"] = {"int_item_mean": float(vi.mean()), "ans_item_mean": float(va.mean()), "fraction_cells_within_0.3": float(np.mean([abs(zsh(b, "q_J25rem_pre_ccsA", "int")) <= 0.3 and abs(zsh(b, "q_J25rem_pre_ccsA", "ans")) <= 0.3 for b in cells])),
               "pass": bool(abs(vi.mean()) <= 0.3 and abs(va.mean()) <= 0.3)}
T["gate_competence"] = {"pass": bool(min(META["competence_ab"].values()) >= 0.9 and min(META["competence_c"].values()) >= 0.9)}
T["gates_pass"] = bool(all(T[g]["pass"] for g in ("gate_reproduction", "gate_writes", "gate_L", "gate_S", "gate_V", "gate_competence")))

# ---- part 1a: the repaired clamp
C, CA = share("q_J25rem_pre_ccs"), share("q_J25rem_pre_ccsA"); un = rows["q_J25rem_pre"]["margin"]; ccsr_in = bool(un["ci"][0] <= rows["q_J25rem_pre_ccsrA"]["margin"]["mean"] <= un["ci"][1])
dCA = ci(M_["q_J25rem_pre_ccs"] - M_["q_J25rem_pre_ccsA"])
if not T["gate_V"]["pass"]: read1a = "not read: gate V failed"
elif not ccsr_in: read1a = "not read: the random-rank control left the un-clamped interval"
elif CA >= 0.4: read1a = f"a route bypassing the pinned readable content at every scored answer position carries at least {CA:.2f} of the question-turn effect"
elif CA <= 0.2: read1a = "Amendment 8's surviving share was the partial clamp plus the continuation leak"
else: read1a = f"C_A = {CA:.2f} is the result, with the bracket [{CA:.2f}, 0.51]"
T["part1a"] = {"C_s_only": C, "C_A": CA, "C_A_ci": rows["q_J25rem_pre_ccsA"]["share_ci"], "C_minus_C_A": C - CA, "C_minus_C_A_nats": dCA, "correction_needed": bool(C - CA > 0.05),
               "control_ccsrA": share("q_J25rem_pre_ccsrA"), "ccsrA_within_unclamped_interval": ccsr_in, "unclamped": share("q_J25rem_pre"), "reading": read1a,
               "first_token_shares": {r: rows[r]["first_token_share"] for r in ("q_J25rem_pre", "q_J25rem_pre_ccs", "q_J25rem_pre_ccsA", "q_J25rem_pre_ccsrA")},
               "per_item_C_A_median": float(np.median(M_["q_J25rem_pre_ccsA"] / full)), "items_C_A_ge_0.4": int(((M_["q_J25rem_pre_ccsA"] / full) >= 0.4).sum()), "items_C_A_le_0.2": int(((M_["q_J25rem_pre_ccsA"] / full) <= 0.2).sum())}
# ---- part 1b: route split
Rm, Rd = share("q_J25rem_pre_ccsA_m63A"), share("q_J25rem_pre_sfullA")
if Rm <= 0.1 and Rd >= 0.3: read1b = "direct last-layer read: the bypass is block 63 reading the donor's change straight from the question tokens"
elif Rm >= 0.3 and Rd <= 0.1: read1b = "earlier entry: the change reaches the answer positions before the last block, in directions the clamp does not pin, and the last block converts it"
else: read1b = "both routes carry part of it"
T["part1b"] = {"R_mask": Rm, "R_mask_ci": rows["q_J25rem_pre_ccsA_m63A"]["share_ci"], "R_direct": Rd, "R_direct_ci": rows["q_J25rem_pre_sfullA"]["share_ci"], "interaction": CA - Rm - Rd,
               "full_donor_m63A": share("q_full_pre_m63A"), "full_donor_m63A_ci": rows["q_full_pre_m63A"]["share_ci"], "full_donor_sfullA": share("q_full_pre_sfullA"), "full_donor_sfullA_ci": rows["q_full_pre_sfullA"]["share_ci"],
               "full_donor_interaction": 1 - share("q_full_pre_m63A") - share("q_full_pre_sfullA"), "reading": read1b,
               "per_relation": {cat: {r: float(M_[r][[names.index(nm) for nm in names if CAT[nm] == cat]].mean() / full[[names.index(nm) for nm in names if CAT[nm] == cat]].mean()) for r in ("q_J25rem_pre_ccsA", "q_J25rem_pre_ccsA_m63A", "q_J25rem_pre_sfullA", "q_full_pre_m63A", "q_full_pre_sfullA")} for cat in sorted(set(CAT.values()))}}

# ---- part 2: country or city
def mc(b, c, tm):
    base = "lang_clean" if (c in ("q_xfer", "q_native_lang") or c.startswith("x_")) else "cap_clean"
    return float((RAW[f"{b}|{c}|donor_{tm}"] - RAW[f"{b}|{c}|own_{tm}"]) - (RAW[f"{b}|{base}|donor_{tm}"] - RAW[f"{b}|{base}|own_{tm}"]))


bypair = lambda f: np.array([np.mean([f(b) for b in ccells if b.startswith(p + "|")]) for p in pairs])
MC = {(c, tm): bypair(lambda b: mc(b, c, tm)) for c in ROWS_C for tm in ("lang", "cap")}; npair = len(pairs)


def part2(prefix, ref, tm):
    x = lambda k: MC[(f"{prefix}_{k}", tm)]; r0 = MC[(ref, tm)]
    f_c, f_y = x("ctry").mean() / r0.mean(), x("city").mean() / r0.mean(); c_c, c_y = 1 - x("noctry").mean() / r0.mean(), 1 - x("nocity").mean() / r0.mean()
    d_inst = boot(lambda a, b_, r_: (a.mean() - b_.mean()) / r_.mean(), [x("ctry"), x("city"), r0], npair); d_rem = boot(lambda a, b_, r_: (b_.mean() - a.mean()) / r_.mean(), [x("noctry"), x("nocity"), r0], npair)
    if d_inst[0] > 0 and d_rem[0] > 0: rd = "country dominant: the readable upstream content that transfers is the country's"
    elif d_inst[1] < 0 and d_rem[1] < 0: rd = "city dominant: the readable upstream content that transfers is the cue city's"
    else: rd = "not separated at the level of the readable planes"
    return {"f_ctry": float(f_c), "f_city": float(f_y), "c_ctry": float(c_c), "c_city": float(c_y), "f_rand2": float(x("rand2").mean() / r0.mean()),
            "install_diff_ci": d_inst, "removal_diff_ci": d_rem, "reference_push": ci(r0), "reading": rd,
            "per_pair": {p: {k: float(x(k)[i] / r0[i]) for k in ("ctry", "city", "noctry", "nocity", "rand2")} for i, p in enumerate(pairs)},
            "means_nats": {k: ci(x(k)) for k in ("ctry", "city", "noctry", "nocity", "rand2")}}
T["part2"] = {"language_question": part2("x", "q_xfer", "lang"), "capital_question_mirror": part2("m", "q_mirror", "cap"),
              "cos_country_city_planes_L51_59": float(np.mean([v["max_principal_cos_country_city_planes_L51_59"] for v in ccells.values()])),
              "reference_rows": {f"{c}|m_{tm}": ci(MC[(c, tm)]) for c in ("q_xfer", "q_native_lang", "q_mirror", "q_native_cap") for tm in ("lang", "cap")}}
json.dump(T, open(os.path.join(TAB, f"two_hop_{STAGE}_tables.json"), "w"), indent=1, default=str)

# ---- report
f2 = lambda x: f"{x:+.2f}"; f3 = lambda x: f"{x:+.3f}"
L = [f"# two_hop_organism · stage `{STAGE}` — the consumer clamp over every scored answer position, where the bypass enters, and country or city (Amendment 9)\n",
     f"Run `{META['run_id']}`, {META['n_forwards']} forwards, {META['elapsed_s']} s; Qwen3.6-27B, thinking off, float32 residual from block 35; sequence-log-prob endpoint (primary). Part 1: {len(cells)} cells ({NI} admitted items × {len(META['carriers_ab'])} carriers), cluster = item. Part 2: {len(ccells)} cells ({npair} city pairs × {len(META['carriers_c'])} carriers), cluster = pair. "
     "Design: `H3/design_specs/two_hop_organism.md` Amendment 9; battery `H3/scripts/two_hop_probe4.py`; generated by `two_hop_probe4_analysis.py`; the last section is hand-written.\n",
     "## 1. Gates\n",
     f"- Competence: part 1 clean {T['competence_ab']['clean']:.2f} / donor {T['competence_ab']['donor']:.2f}; part 2 capital {T['competence_c']['cap_clean']:.2f} / {T['competence_c']['cap_donor']:.2f}, language {T['competence_c']['lang_clean']:.2f} / {T['competence_c']['lang_donor']:.2f} — **{'PASS' if T['gate_competence']['pass'] else 'FAIL'}**.",
     "- Reproduction of `probe3` by the references: " + "; ".join(f"`{r}` max |Δ| {v['max_abs_diff']:.1e}" for r, v in T["gate_reproduction"].items() if r != "pass") + f" — **{'PASS' if T['gate_reproduction']['pass'] else 'FAIL'}**.",
     f"- Writes and clamps: fixed-target ρ {min(r['rho'] for r in rows.values()):.4f}–{max(r['rho'] for r in rows.values()):.4f}, κ ≥ {min(r['kappa'] for r in rows.values()):.4f}; multi-position clamps ρ " + ", ".join(f"`{k}` {v['rho_min']:.4f}–{v['rho_max']:.4f} (κ ≥ {v['kappa_min']:.4f})" for k, v in cs.items()) + f"; `_ccsrA` norms within {100*T['gate_writes']['ccsrA_norm_match_max_rel_dev']:.4f} % — **{'PASS' if T['gate_writes']['pass'] else 'FAIL'}**.",
     f"- Gate L (block-63 attention from the scored answer positions to `q_pre` under every `_m63A` row): maximum post-softmax weight {T['gate_L']['leak_max']:.1e} — **{'PASS' if T['gate_L']['pass'] else 'FAIL'}**.",
     f"- Gate S (both cuts, `q_J25rem_pre_sfullA_m63A`): item-mean margin {T['gate_S']['sfullA_m63A_item_mean_margin']:+.4f} nats, max |item| {T['gate_S']['max_abs_item']:.4f} — **{'PASS' if T['gate_S']['pass'] else 'FAIL'}**.",
     f"- Gate V (readouts at s under `q_J25rem_pre_ccsA`): intermediate {f2(T['gate_V']['int_item_mean'])}, answer {f2(T['gate_V']['ans_item_mean'])}; {100*T['gate_V']['fraction_cells_within_0.3']:.0f} % of cells within ±0.3 — **{'PASS' if T['gate_V']['pass'] else 'FAIL'}**.\n",
     "## 2. Part 1 table (shares of `q_full_pre`; masked rows relative to `clean_m63A`; cluster-bootstrap intervals; first-token share from first-token log-probs, descriptive)\n",
     "| row | margin (nats) | 95 % CI | items > 0 | share | share 95 % CI | first-token share | flips | J_NP int / answer readout at s |", "|---|---|---|---|---|---|---|---|---|"]
for r in rows:
    x = rows[r]; m = x["margin"]
    L.append(f"| `{r}` | {f2(m['mean'])} | [{f2(m['ci'][0])}, {f2(m['ci'][1])}] | {m['n_pos']}/{m['n']} | {f3(x['share'])} | [{x['share_ci'][0]:.3f}, {x['share_ci'][1]:.3f}] | {f3(x['first_token_share'])} | {x['flips']}/{len(cells)} | {f2(x['J_int_s']['mean'])} / {f2(x['J_ans_s']['mean'])} |")
a1, b1 = T["part1a"], T["part1b"]
L += ["\n## 3. Part 1a: the clamp over every scored answer position\n",
      f"s-only verified clamp (Amendment 8, same run) C = {f3(a1['C_s_only'])}; **all scored positions C_A = {f3(a1['C_A'])}** [{a1['C_A_ci'][0]:.3f}, {a1['C_A_ci'][1]:.3f}]; difference C − C_A = {f3(a1['C_minus_C_A'])} ({f2(a1['C_minus_C_A_nats']['mean'])} nats [{f2(a1['C_minus_C_A_nats']['ci'][0])}, {f2(a1['C_minus_C_A_nats']['ci'][1])}], {a1['C_minus_C_A_nats']['n_pos']}/{NI} items > 0) — "
      f"{'**above 0.05: the Amendment 8 (b) reading is corrected (C_A replaces C)**' if a1['correction_needed'] else 'within 0.05: silly mistake 5 did not change the Amendment 8 (b) number materially'}. Random-rank control {f3(a1['control_ccsrA'])} ({'within' if a1['ccsrA_within_unclamped_interval'] else 'outside'} the un-clamped interval). "
      f"Per item C_A median {a1['per_item_C_A_median']:.2f}; {a1['items_C_A_ge_0.4']}/{NI} ≥ 0.4, {a1['items_C_A_le_0.2']}/{NI} ≤ 0.2 → registered reading: **{a1['reading']}**. "
      "First-token shares (descriptive): " + ", ".join(f"`{k}` {v:.3f}" for k, v in a1["first_token_shares"].items()) + ".\n",
      "## 4. Part 1b: where the surviving effect enters\n",
      f"With block 63's read from the scored answer positions to the question tokens cut, the clamped complement keeps **R_mask = {f3(b1['R_mask'])}** [{b1['R_mask_ci'][0]:.3f}, {b1['R_mask_ci'][1]:.3f}]; with the answer positions held entirely at clean through block 62, so that only block 63's read can carry anything, it keeps **R_direct = {f3(b1['R_direct'])}** [{b1['R_direct_ci'][0]:.3f}, {b1['R_direct_ci'][1]:.3f}]; interaction C_A − R_mask − R_direct = {f3(b1['interaction'])} → registered reading: **{b1['reading']}**.\n",
      f"The whole question-turn effect (`q_full_pre`): with block 63's read cut it keeps {f3(b1['full_donor_m63A'])} [{b1['full_donor_m63A_ci'][0]:.3f}, {b1['full_donor_m63A_ci'][1]:.3f}]; through block 63's read alone it keeps {f3(b1['full_donor_sfullA'])} [{b1['full_donor_sfullA_ci'][0]:.3f}, {b1['full_donor_sfullA_ci'][1]:.3f}]; interaction {f3(b1['full_donor_interaction'])}.\n",
      "| relation (descriptive) | C_A | R_mask | R_direct | full, read cut | full, read only |", "|---|---|---|---|---|---|"]
for cat, v in b1["per_relation"].items(): L.append(f"| {cat} | {v['q_J25rem_pre_ccsA']:+.2f} | {v['q_J25rem_pre_ccsA_m63A']:+.2f} | {v['q_J25rem_pre_sfullA']:+.2f} | {v['q_full_pre_m63A']:+.2f} | {v['q_full_pre_sfullA']:+.2f} |")
p2 = T["part2"]
L += ["\n## 5. Part 2: country or city\n", f"Maximum principal cosine between the country plane and the city plane, L51–59: {p2['cos_country_city_planes_L51_59']:.2f}. Fractions are of the full transplanted delta's push (ratios of pair means; cluster bootstrap over pairs).\n",
      "| question (delta) | reference push (nats) | country plane alone | city plane alone | country plane removed (cost) | city plane removed (cost) | random 2-plane alone | install diff (ctry − city) 95 % CI | removal diff (ctry − city) 95 % CI | reading |", "|---|---|---|---|---|---|---|---|---|---|"]
for lab, key in (("language question (capital delta)", "language_question"), ("capital question (language delta)", "capital_question_mirror")):
    v = p2[key]
    L.append(f"| {lab} | {f2(v['reference_push']['mean'])} | {v['f_ctry']:.2f} | {v['f_city']:.2f} | {v['c_ctry']:.2f} | {v['c_city']:.2f} | {v['f_rand2']:.2f} | [{v['install_diff_ci'][0]:+.2f}, {v['install_diff_ci'][1]:+.2f}] | [{v['removal_diff_ci'][0]:+.2f}, {v['removal_diff_ci'][1]:+.2f}] | **{v['reading']}** |")
L += ["\nPer pair (language question; fractions of the full capital-delta push): ", "| pair | country alone | city alone | country removed | city removed | random |", "|---|---|---|---|---|---|"]
for p, v in p2["language_question"]["per_pair"].items(): L.append(f"| {p} | {v['ctry']:+.2f} | {v['city']:+.2f} | {v['noctry']:+.2f} | {v['nocity']:+.2f} | {v['rand2']:+.2f} |")
L.append("\n## 6. Interpretation, licensed / not licensed, next decision\n")
_reading = os.path.join(REP, f"two_hop_{STAGE}_reading.md")
L.append(open(_reading).read() if os.path.exists(_reading) else "_(hand-written after reading the tables; kept in `two_hop_" + STAGE + "_reading.md` and inlined here)_\n")
open(os.path.join(REP, f"two_hop_{STAGE}.md"), "w").write("\n".join(L))

# ---- figure
try:
    for _p in ("/root/.claude/skills/iclr-plots/scripts", os.path.join(R.PROJECT, ".claude", "skills", "iclr-plots", "scripts"), "/workspace/.claude/skills/iclr-plots/scripts"): sys.path.insert(0, _p)
    import iclrplot as ip; ip.setup()
except Exception as e:
    print("iclrplot not used:", e)
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
fig, axs = plt.subplots(1, 3, figsize=(5.5, 2.0), gridspec_kw={"width_ratios": [1.1, 1.3, 1.0]})
def bars(ax, keys, labels, colors, title):
    vals = [rows[k]["share"] for k in keys]; lo = [rows[k]["share"] - rows[k]["share_ci"][0] for k in keys]; hi = [rows[k]["share_ci"][1] - rows[k]["share"] for k in keys]
    ax.bar(range(len(keys)), vals, yerr=[lo, hi], color=colors, capsize=1.5, width=0.7)
    for i, k in enumerate(keys): ax.scatter(np.full(NI, i) + np.linspace(-0.2, 0.2, NI), [rows[k]["per_item"][nm] for nm in names], s=2, color="k", alpha=0.4, zorder=3)
    ax.set_xticks(range(len(keys))); ax.set_xticklabels(labels, fontsize=4.8, rotation=50, ha="right", rotation_mode="anchor"); ax.set_ylim(-0.1, 1.1); ax.set_title(title, fontsize=6.5); ax.axhline(0, color="k", lw=0.4)
bars(axs[0], ["q_J25rem_pre", "q_J25rem_pre_ccs", "q_J25rem_pre_ccsA", "q_J25rem_pre_ccsrA"], ["J25 complement", "+ clamp at s", "+ clamp at all answer pos.", "+ random clamp"], ["#a50f15", "#3f007d", "#6a51a3", "#fcae91"], "(a) clamp over every scored position")
axs[0].set_ylabel("share of q_full_pre")
bars(axs[1], ["q_J25rem_pre_ccsA", "q_J25rem_pre_ccsA_m63A", "q_J25rem_pre_sfullA", "q_full_pre_m63A", "q_full_pre_sfullA"], ["clamped complement", "  block-63 read cut", "  via block-63 read only", "full donor, read cut", "full donor, read only"],
     ["#6a51a3", "#9e9ac8", "#54278f", "#969696", "#252525"], "(b) where it enters")
ax = axs[2]; v = p2["language_question"]; ks = ["ctry", "city", "noctry", "nocity", "rand2"]; labs = ["country\nalone", "city\nalone", "country\nremoved", "city\nremoved", "random"]
vals = [v["f_ctry"], v["f_city"], 1 - v["c_ctry"], 1 - v["c_city"], v["f_rand2"]]
ax.bar(range(5), vals, color=["#1f77b4", "#ff7f0e", "#aec7e8", "#ffbb78", "#bdbdbd"], width=0.7)
for i, k in enumerate(ks): ax.scatter(np.full(npair, i) + np.linspace(-0.15, 0.15, npair), [v["per_pair"][p][k] for p in pairs], s=3, color="k", alpha=0.5, zorder=3)
ax.set_xticks(range(5)); ax.set_xticklabels(labs, fontsize=4.8); ax.axhline(0, color="k", lw=0.4); ax.axhline(1, color="k", lw=0.4, ls=":"); ax.set_ylim(-0.15, 1.2)
ax.set_ylabel("fraction of transfer push", fontsize=5.5); ax.set_title("(c) country or city (language q.)", fontsize=6.5)
fig.tight_layout(); fig.savefig(os.path.join(FIG, f"h3_{STAGE}.png"), dpi=200); fig.savefig(os.path.join(FIG, f"h3_{STAGE}.pdf"))
print(json.dumps({k: T[k] for k in ("gates_pass", "gate_reproduction", "gate_writes", "gate_L", "gate_S", "gate_V")}, indent=1, default=str))
print(json.dumps({"part1a": T["part1a"], "part1b": {k: v for k, v in T["part1b"].items() if k != "per_relation"}, "part2": {k: {kk: vv for kk, vv in v.items() if kk not in ("per_pair",)} if isinstance(v, dict) and "f_ctry" in v else v for k, v in T["part2"].items() if k != "reference_rows"}}, indent=1, default=str))
