"""Analysis for two_hop_organism stage `qsplit6` (Amendment 6): one scoring pass from raw_qsplit6.npz + raw_qsplit6_zq.npz +
raw_pursuit_qsplit6.npz + meta_qsplit6.json to H3/results/tables/two_hop_qsplit6_tables.json, H3/results/reports/two_hop_qsplit6.md
(sections 1-7 generated, 8 left for the hand-written reading) and H3/results/figures/h3_qsplit6.{png,pdf}.
Usage: two_hop_qsplit6_analysis.py [stage]"""
import os, sys, json
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "..", "common", "scripts"))
import numpy as np
import registry as R, rendering as Rn

STAGE = sys.argv[1] if len(sys.argv) > 1 else "qsplit6"
OUT = R.out_dir("H3", "outputs", "two_hop_organism"); REP = R.out_dir("H3", "results", "reports"); TAB = R.out_dir("H3", "results", "tables"); FIG = R.out_dir("H3", "results", "figures")
RAW = np.load(os.path.join(OUT, f"raw_{STAGE}.npz"), allow_pickle=True); Z = np.load(os.path.join(OUT, f"raw_{STAGE}_zq.npz"))
P = np.load(os.path.join(OUT, f"raw_pursuit_{STAGE}.npz"), allow_pickle=True); META = json.load(open(os.path.join(OUT, f"meta_{STAGE}.json")))
cells = META["cells"]; names = list(dict.fromkeys(b.split("|")[0] for b in cells)); COLS = META["columns"]; ROWS = META["rows"]; KS = META["ks"]; nq = META["n_qpre"]
S0 = META["s_donor0_seq_bf16_quoted"]; LZ0 = META["zq_layers"][0]; RB = slice(51 - LZ0, 60 - LZ0); SWAP_L = list(range(META["swap_layers"][0], META["swap_layers"][1] + 1)); RBL = list(range(51, 60))
ITEMS = {it["name"]: it for it in META["items"]}; NC = len(cells); tok = R.make_tokenizer()
ANS_ALIASES = {"Madrid": ["madrid"], "Ottawa": ["ottawa"], "Paris": ["paris", "parisian"], "Rome": ["rome", "roman"], "Berlin": ["berlin"], "Tokyo": ["tokyo"], "Arabic": ["arabic", "arab"],
               "Russian": ["russian"], "Budapest": ["budapest"], "Warsaw": ["warsaw"], "Athens": ["athens", "athenian"], "cow": ["cow", "cows", "cattle"], "bee": ["bee", "bees"]}
INT_ALIASES = {"Spain": ["spain", "spanish", "spaniard"], "Canada": ["canada", "canadian"], "France": ["france", "french"], "Italy": ["italy", "italian"], "Germany": ["germany", "german"],
               "Japan": ["japan", "japanese"], "Egypt": ["egypt", "egyptian"], "Russia": ["russia", "russian"], "Hungary": ["hungary", "hungarian"], "Poland": ["poland", "polish"],
               "Greece": ["greece", "greek"], "butter": ["butter", "buttery"], "honey": ["honey", "honeyed"]}


def ci(v):
    from scipy import stats as st
    v = np.asarray(v, float); m = float(v.mean()); n = len(v)
    h = float(st.t.ppf(0.975, n - 1) * v.std(ddof=1) / np.sqrt(n)) if n > 1 else float("nan")
    return {"mean": m, "ci": [m - h, m + h], "n_pos": int((v > 0).sum()), "n": int(n)}


byitem = lambda f: [float(np.mean([f(b) for b in cells if b.startswith(nm + "|")])) for nm in names]
mg = lambda b, c: float((RAW[f"{b}|{c}|seq_swap"] - RAW[f"{b}|{c}|seq_answer"]) - (RAW[f"{b}|clean|seq_swap"] - RAW[f"{b}|clean|seq_answer"]))
mgc = lambda b, c: float((RAW[f"{b}|{c}|s_swap"] - RAW[f"{b}|{c}|s_answer"]) - (RAW[f"{b}|clean|s_swap"] - RAW[f"{b}|clean|s_answer"]))
flips = lambda c: int(sum(RAW[f"{b}|{c}|seq_swap"] > RAW[f"{b}|{c}|seq_answer"] for b in cells))


def zsh(b, c, pair, where):
    """J_NP readout shift, L51-59 mean, (second - first) of the pair minus clean; where = 's' (scoring position) or 'q' (q_pre mean)."""
    it = cells[b]; w1, w2 = (it["intermediate"], it["swap_to"]) if pair == "int" else (it["answer"], it["swap_answer"])
    z = Z[f"{b}|{c}|zq"].astype(np.float32)[RB]; zc = Z[f"{b}|clean|zq"].astype(np.float32)[RB]
    d = lambda z_: (z_[:, -1, COLS.index(w2)] - z_[:, -1, COLS.index(w1)]).mean() if where == "s" else (z_[:, :-1, COLS.index(w2)] - z_[:, :-1, COLS.index(w1)]).mean()
    return float(d(z) - d(zc))


def c63(b, c, where):
    if where == "s": d = RAW[f"{b}|{c}|c63s"].astype(np.float32) - RAW[f"{b}|clean|c63s"].astype(np.float32)
    else: d = RAW[f"{b}|{c}|c63"].astype(np.float32).mean(0) - RAW[f"{b}|clean|c63"].astype(np.float32).mean(0)
    return float(d[1] - d[0])


ND_COL = {"q_full_pre": 0, "q_plane_pre": 1, "q_rem_pre": 1, "q_rand_pre": 1, "q_rem_rand_pre": 1, "q_rem_cb_pre": 1, "q_ansplane_pre": 2, "q_ansrem_pre": 2, "q_J25nn_pre": 7, "q_rem25nn_pre": 7}
for i, k in enumerate(KS): ND_COL[f"q_J{k}_pre"] = 3 + i; ND_COL[f"q_J{k}rem_pre"] = 3 + i; ND_COL[f"q_rand{k}rem_pre"] = 3 + i
ND = np.stack([RAW[f"{b}|normdiag"] for b in cells])          # [cells, 27 blocks, 8]
base_of = lambda c: c[:-3] if c.endswith("_cc") else (c[:-4] if c.endswith("_ccr") else c)

T = {"stage": STAGE, "run_id": META["run_id"], "n_forwards": META["n_forwards"], "elapsed_s": META["elapsed_s"], "n_cells": NC, "n_items": len(names), "n_qpre": nq, "s_donor0_seq_bf16_quoted": S0,
     "restricted_dictionary_size": META["restricted_dictionary_size"], "vocab_size": META["vocab_size"], "ks": KS}
full_items = byitem(lambda b: mg(b, "q_full_pre")); full_mean = float(np.mean(full_items))
rows = {}
for c in ROWS:
    marg = byitem(lambda b: mg(b, c)); row = {"margin_seq": ci(marg), "share_of_q_full_pre": float(np.mean(marg) / full_mean), "share_of_S_donor0_bf16": float(np.mean(marg) / S0), "flips_seq": flips(c),
                                            "margin_candidate": ci(byitem(lambda b: mgc(b, c))), "per_item_margin": dict(zip(names, marg)), "per_cell_margin": {b: mg(b, c) for b in cells},
                                            "J_int_shift_s": ci(byitem(lambda b: zsh(b, c, "int", "s"))), "J_int_shift_qpre": ci(byitem(lambda b: zsh(b, c, "int", "q"))),
                                            "J_ans_shift_s": ci(byitem(lambda b: zsh(b, c, "ans", "s"))), "J_ans_shift_qpre": ci(byitem(lambda b: zsh(b, c, "ans", "q"))),
                                            "block63_reentry_qpre": ci(byitem(lambda b: c63(b, c, "q"))), "block63_reentry_s": ci(byitem(lambda b: c63(b, c, "s"))),
                                            "dNLL_max": float(max(RAW[f"{b}|{c}|nll"] - RAW[f"{b}|clean|nll"] for b in cells)), "dNLL_mean": float(np.mean([RAW[f"{b}|{c}|nll"] - RAW[f"{b}|clean|nll"] for b in cells]))}
    bc = base_of(c); b0 = list(cells)[0]
    if f"{b0}|{c}|rho" in RAW:
        row.update({"rho": float(np.mean([RAW[f"{b}|{c}|rho"] for b in cells])), "kappa": float(np.mean([RAW[f"{b}|{c}|kappa"] for b in cells]))})
    if f"{b0}|{c}|rberr" in RAW:
        row.update({"readback_max": float(max(RAW[f"{b}|{c}|rberr"] for b in cells)), "plane_dev_max": float(max(RAW[f"{b}|{c}|plane_dev"] for b in cells))})
    if bc in ND_COL:
        r_ = ND[:, :, ND_COL[bc]] / ND[:, :, 0]; row.update({"v_over_dh": float(r_.mean()), "v_over_dh_L51_59": float(r_[:, 15:24].mean())})
    if c.endswith("_cc") or c.endswith("_ccr"):
        req = np.stack([RAW[f"{b}|{c}|clamp_req"] for b in cells]); real = np.stack([RAW[f"{b}|{c}|clamp_real"] for b in cells]); kap = np.stack([RAW[f"{b}|{c}|clamp_kappa"] for b in cells]); ok = req > 1e-6
        row.update({"clamp_rho": float((real[ok] / req[ok]).mean()), "clamp_rho_min": float((real[ok] / req[ok]).min()), "clamp_rho_max": float((real[ok] / req[ok]).max()), "clamp_kappa_min": float(kap[ok].min()),
                    "clamp_req_norm_mean": float(req[ok].mean()), "clamp_dim": [int(RAW[f"{b}|{c}|clamp_dim"].min()) for b in cells][:1] + [int(RAW[f"{b}|{c}|clamp_dim"].max()) for b in cells][:1],
                    "clamp_zero_request_blocks": int((~ok).sum())})
        if c.endswith("_ccr"):
            realcc = np.stack([RAW[f"{b}|{bc}_cc|clamp_real"] for b in cells]); okc = realcc > 1e-6
            row["ccr_norm_match_max_rel_dev"] = float((np.abs(real[okc] - realcc[okc]) / realcc[okc]).max())
    rows[c] = row
T["rows"] = rows; sh = lambda c: rows[c]["share_of_q_full_pre"]

# ---- gates
T["gate1"] = {"n_cells": NC, "q_pre_length_equal": True, "single_token_answer_words": True, "pass": True, "note": "rendering, q token-id equality, scoring position excluded and single-token forms asserted per cell in the battery"}
T["competence_clean32_seq"] = float(np.mean([RAW[f"{b}|clean|seq_answer"] > RAW[f"{b}|clean|seq_swap"] for b in cells])); T["competence_donor32_seq"] = float(np.mean([RAW[f"{b}|donor|seq_swap"] > RAW[f"{b}|donor|seq_answer"] for b in cells]))
T["gate2"] = {"pass": bool(T["competence_clean32_seq"] >= 0.9 and T["competence_donor32_seq"] >= 0.9)}
ft_rows = [c for c in ROWS if "rho" in rows[c] and not (c.endswith("_cc") or c.endswith("_ccr"))]
g3 = {"fixed_target_rows_ok": bool(all(0.9 <= rows[c]["rho"] <= 1.1 and rows[c]["kappa"] >= 0.99 for c in ft_rows)),
      "clamp_writes_ok": bool(all(0.9 <= rows[c]["clamp_rho_min"] and rows[c]["clamp_rho_max"] <= 1.1 and rows[c]["clamp_kappa_min"] >= 0.99 for c in ROWS if c.endswith("_cc") or c.endswith("_ccr"))),
      "current_base_ok": bool(0.9 <= rows["q_rem_cb_pre"]["rho"] <= 1.1 and rows["q_rem_cb_pre"]["kappa"] >= 0.99),
      "ccr_norm_match_max_rel_dev": float(max(rows[c]["ccr_norm_match_max_rel_dev"] for c in ROWS if c.endswith("_ccr"))), "readback_max": float(max(rows[c]["readback_max"] for c in ROWS if "readback_max" in rows[c]))}
g3["pass"] = bool(g3["fixed_target_rows_ok"] and g3["clamp_writes_ok"] and g3["current_base_ok"] and g3["ccr_norm_match_max_rel_dev"] <= 0.05); T["gate3"] = g3
g4 = rows["q_full_pre"]["margin_seq"]; T["gate4"] = {"mean": g4["mean"], "items_pos": g4["n_pos"], "amendment5_interval": [10.00, 12.38], "amendment5_mean": 11.19, "pass": bool(10.00 <= g4["mean"] <= 12.38 and g4["n_pos"] >= 10)}
T["gate5"] = {"rand_share": sh("q_rand_pre"), "rand_flips": rows["q_rand_pre"]["flips_seq"], "rem_rand_share": sh("q_rem_rand_pre"), "pass": bool(sh("q_rand_pre") <= 0.10 and rows["q_rand_pre"]["flips_seq"] <= 2 and sh("q_rem_rand_pre") >= 0.80)}
# gate 6: pursuit positive control (reported, not gating)
pc = {"L51_59": {"either": [], "both": []}, "all": {"either": [], "both": []}}
for b in cells:
    it = cells[b]; ti, ts = Rn.single_token_id(tok, it["intermediate"]), Rn.single_token_id(tok, it["swap_to"])
    for l in SWAP_L:
        a = RAW[f"{b}|L{l}|atoms_qpre"][:, :2]; e = [(ti in r) or (ts in r) for r in a]; bo = [(ti in r) and (ts in r) for r in a]
        pc["all"]["either"] += e; pc["all"]["both"] += bo
        if l in RBL: pc["L51_59"]["either"] += e; pc["L51_59"]["both"] += bo
T["gate6_positive_control"] = {w: {k: float(np.mean(v)) for k, v in d.items()} for w, d in pc.items()}; T["gate6_positive_control"]["chance_per_pick"] = 2 / META["vocab_size"]
kk = np.concatenate([P[f"L{l}|kkt"] for l in SWAP_L]); T["gate7"] = {"kkt_pass_fraction": float(kk.mean()), "n": int(len(kk)), "pass": bool(kk.mean() >= 0.99)}
T["gates_1_5_pass"] = bool(all(T[f"gate{i}"]["pass"] for i in range(1, 6)))

# ---- share(k) curve, energy, atom types
curve = {}
for k in KS:
    curve[str(k)] = {nm: {"share": sh(c), "margin": rows[c]["margin_seq"]["mean"], "ci": rows[c]["margin_seq"]["ci"], "n_pos": rows[c]["margin_seq"]["n_pos"]}
                     for nm, c in (("J_k", f"q_J{k}_pre"), ("J_k_rem", f"q_J{k}rem_pre"), ("J_k_rem_cc", f"q_J{k}rem_pre_cc"), ("J_k_rem_ccr", f"q_J{k}rem_pre_ccr"), ("rand_k_rem", f"q_rand{k}rem_pre"))}
T["share_k_curve"] = curve
E = META["energy"]; T["energy"] = {str(k): {"e_J_all_blocks": float(np.mean([E[str(l)]["e_J"][str(k)] for l in SWAP_L])), "e_J_L51_59": float(np.mean([E[str(l)]["e_J"][str(k)] for l in RBL])),
                                     "e_rand_sigma_all_blocks": float(np.mean([E[str(l)]["e_rand_sigma"][str(k)] for l in SWAP_L])), "e_rand_sigma_L51_59": float(np.mean([E[str(l)]["e_rand_sigma"][str(k)] for l in RBL])),
                                     "k_over_d": E[str(SWAP_L[0])]["k_over_d"][str(k)], "blocks_e_J_gt_e_rand": int(sum(E[str(l)]["e_J"][str(k)] > E[str(l)]["e_rand_sigma"][str(k)] for l in SWAP_L))} for k in KS}
T["energy"]["n_cov_samples"] = E[str(SWAP_L[0])]["n_cov_samples"]
atoms = {}
for k in KS:
    q_all = np.stack([RAW[f"{b}|L{l}|clsshare{k}"] for b in cells for l in SWAP_L]); q_rb = np.stack([RAW[f"{b}|L{l}|clsshare{k}"] for b in cells for l in RBL])
    s_all = np.stack([RAW[f"{b}|L{l}|clsshare{k}_s"] for b in cells for l in SWAP_L]); s_rb = np.stack([RAW[f"{b}|L{l}|clsshare{k}_s"] for b in cells for l in RBL])
    cnt = {"answer": [], "intermediate": [], "other": []}; wcnt = {"answer": [], "intermediate": [], "other": []}
    for bi, b in enumerate(cells):
        for l in RBL:
            cls = RAW[f"{b}|L{l}|cls_qpre"][:, :k]; co = np.abs(P[f"L{l}|coef{k}"][bi * nq:(bi + 1) * nq]); tot = co.sum(1, keepdims=True).clip(1e-12)
            for w in cnt: cnt[w].append(float((cls == w).mean())); wcnt[w].append(float(((cls == w) * co / tot).sum(1).mean()))
    atoms[str(k)] = {"norm_share_qpre_L51_59": dict(zip(("answer", "intermediate", "other"), q_rb.mean(axis=(0, 1)).round(4).tolist())), "norm_share_qpre_all": dict(zip(("answer", "intermediate", "other"), q_all.mean(axis=(0, 1)).round(4).tolist())),
                     "norm_share_s_L51_59": dict(zip(("answer", "intermediate", "other"), s_rb.mean(0).round(4).tolist())), "norm_share_s_all": dict(zip(("answer", "intermediate", "other"), s_all.mean(0).round(4).tolist())),
                     "count_fraction_qpre_L51_59": {w: float(np.mean(v)) for w, v in cnt.items()}, "coef_weighted_fraction_qpre_L51_59": {w: float(np.mean(v)) for w, v in wcnt.items()}}
nn_rb = np.stack([RAW[f"{b}|L{l}|clsshare_nn"] for b in cells for l in RBL]); atoms["nn25"] = {"norm_share_qpre_L51_59": dict(zip(("answer", "intermediate", "other"), nn_rb.mean(axis=(0, 1)).round(4).tolist()))}
T["atom_types"] = atoms
T["collisions"] = [f"{nm}: answer alias set ∩ intermediate alias set = {sorted(set(ANS_ALIASES.get(it['answer'], [it['answer'].lower()]) + ANS_ALIASES.get(it['swap_answer'], [it['swap_answer'].lower()])) & set(INT_ALIASES.get(it['intermediate'], []) + INT_ALIASES.get(it['swap_to'], []) + [it['intermediate'].lower(), it['swap_to'].lower()]))} (answer class takes priority)"
                   for nm, it in ITEMS.items() if set(ANS_ALIASES.get(it["answer"], [it["answer"].lower()]) + ANS_ALIASES.get(it["swap_answer"], [it["swap_answer"].lower()])) & set(INT_ALIASES.get(it["intermediate"], []) + INT_ALIASES.get(it["swap_to"], []) + [it["intermediate"].lower(), it["swap_to"].lower()])]
top = {"other": Counter(), "intermediate": Counter(), "answer": Counter()}
for b in cells:
    for l in RBL:
        a = RAW[f"{b}|L{l}|atoms_qpre"][:, :25]; cl = RAW[f"{b}|L{l}|cls_qpre"][:, :25]
        for w in top: top[w].update(int(v) for v in a[cl == w])
T["top_atoms_k25_L51_59"] = {w: [(repr(tok.decode([v])), n_) for v, n_ in top[w].most_common(30)] for w in top}
T["early_stops"] = int(sum(int((RAW[f"{b}|L{l}|stop_qpre"] < META["kmax"]).sum()) for b in cells for l in SWAP_L)); T["nnls_fallbacks_note"] = "scipy fallback count per block is in the battery log"

# ---- current base: re-entry fraction of the plane coordinate inside the band
re_ = {}
for l_i, l in enumerate(SWAP_L):
    fr = []
    for b in cells:
        cf = RAW[f"{b}|L{l}|plane_coord_full"].astype(np.float32); cb = RAW[f"{b}|q_rem_cb_pre|plane_band"][l_i].astype(np.float32)   # [P, 2] each
        fr.append(float(((cb * cf).sum(1) / (cf ** 2).sum(1).clip(1e-8)).mean()))
    re_[str(l)] = float(np.mean(fr))
T["current_base"] = {"share": sh("q_rem_cb_pre"), "rem_share": sh("q_rem_pre"), "reentry_fraction_by_block": re_, "reentry_fraction_L62": re_[str(SWAP_L[-1])], "reentry_fraction_L51_59": float(np.mean([re_[str(l)] for l in RBL])),
                     "P6_share_ok": bool(sh("q_rem_cb_pre") >= sh("q_rem_pre") - 0.10), "plane_rebuilt_ge_0.5_by_L62": bool(re_[str(SWAP_L[-1])] >= 0.5)}

# ---- decision rule and predictions
A, B = sh("q_plane_pre"), sh("q_rem_pre"); Aa, Ba = sh("q_ansplane_pre"), sh("q_ansrem_pre"); RR = sh("q_rem_rand_pre")
cc25, ccr25, un25 = sh("q_J25rem_pre_cc"), sh("q_J25rem_pre_ccr"), sh("q_J25rem_pre"); un25ci = rows["q_J25rem_pre"]["margin_seq"]["ci"]
ccr_within = bool(un25ci[0] <= rows["q_J25rem_pre_ccr"]["margin_seq"]["mean"] <= un25ci[1])
dec = "non-J channel carries most of this consumer's margin" if cc25 >= 0.5 else ("the complement was J-mediated at the consumer" if cc25 <= 0.2 else "report the share(k) curve as the result")
T["decision"] = {"consumer_clamped_complement_share_k25": cc25, "control_ccr_share_k25": ccr25, "unclamped_share_k25": un25, "ccr_within_unclamped_interval": ccr_within, "gates_1_5_pass": T["gates_1_5_pass"],
                 "reading": dec if (T["gates_1_5_pass"] and ccr_within) else f"not taken ({'gate failure' if not T['gates_1_5_pass'] else 'ccr control outside the un-clamped interval'}): would read '{dec}'",
                 "qualifier_answer_atoms_carry_most_of_J25": bool(atoms["25"]["norm_share_qpre_L51_59"]["answer"] > 0.5), "qualifier_answer_plane_removal_kills_most": bool(Ba <= 0.5), "A_plane": A, "B_rem": B, "A_ans": Aa, "B_ans": Ba}
Jrem = [sh(f"q_J{k}rem_pre") for k in KS]; Rrem = [sh(f"q_rand{k}rem_pre") for k in KS]
T["predictions"] = {"P1_gates_1_5": T["gates_1_5_pass"], "P2_k2_majority_L51_59": bool(T["gate6_positive_control"]["L51_59"]["either"] > 0.5), "P2_value": T["gate6_positive_control"]["L51_59"]["either"],
                    "P3_B_ans_le_0.5_and_B_stays": bool(Ba <= 0.5 and B >= 0.68), "P3_values": {"A_ans": Aa, "B_ans": Ba, "B": B},
                    "P4_Jrem_nonincreasing": bool(all(Jrem[i + 1] <= Jrem[i] + 1e-9 for i in range(len(KS) - 1))), "P4_rand_rem_ge_0.8_all_k": bool(all(r >= 0.8 for r in Rrem)), "P4_values": {"J_rem": Jrem, "rand_rem": Rrem},
                    "P5_cc_lower_than_unclamped": {c: bool(rows[c + "_cc"]["margin_seq"]["mean"] < rows[c]["margin_seq"]["mean"]) for c in ROWS if c + "_cc" in rows},
                    "P5_ccr_within_unclamped_interval": {c: bool(rows[c]["margin_seq"]["ci"][0] <= rows[c + "_ccr"]["margin_seq"]["mean"] <= rows[c]["margin_seq"]["ci"][1]) for c in ROWS if c + "_ccr" in rows},
                    "P6_cb_share_ok": T["current_base"]["P6_share_ok"], "P6_plane_rebuilt": T["current_base"]["plane_rebuilt_ge_0.5_by_L62"],
                    "P7_eJ_gt_erand_every_k": bool(all(T["energy"][str(k)]["e_J_all_blocks"] > T["energy"][str(k)]["e_rand_sigma_all_blocks"] for k in KS)), "P7_blocks_holding": {str(k): T["energy"][str(k)]["blocks_e_J_gt_e_rand"] for k in KS}}
# per-item table and six seeded random cells
KEY = ["q_full_pre", "q_plane_pre", "q_rem_pre", "q_ansplane_pre", "q_ansrem_pre", "q_J25rem_pre", "q_J25rem_pre_cc", "q_J25rem_pre_ccr", "q_rand25rem_pre", "q_rem_cb_pre", "q_rem25nn_pre", "q_rem25nn_pre_cc"]
T["per_item"] = {nm: {c: (rows[c]["per_item_margin"][nm] / rows["q_full_pre"]["per_item_margin"][nm] if c != "q_full_pre" else rows[c]["per_item_margin"][nm]) for c in KEY} for nm in names}
rng = np.random.default_rng(20260924); six = [list(cells)[i] for i in sorted(rng.choice(NC, min(6, NC), replace=False))]
T["six_random_cells"] = {b: {"clean_gap": float(RAW[f"{b}|clean|seq_answer"] - RAW[f"{b}|clean|seq_swap"]), "greedy": {c: str(RAW[f"{b}|{c}|greedy"]) for c in ["clean", "donor"] + KEY},
                             "margins": {c: mg(b, c) for c in KEY}, "J_int_shift_s": {c: zsh(b, c, "int", "s") for c in KEY}, "J_ans_shift_s": {c: zsh(b, c, "ans", "s") for c in KEY},
                             "atoms_s_L59_first8": [tok.decode([int(v)]) for v in RAW[f"{b}|L59|atoms_s"][:8]], "atoms_qpre_last_L59_first8": [tok.decode([int(v)]) for v in RAW[f"{b}|L59|atoms_qpre"][-1, :8]]} for b in six}
json.dump(T, open(os.path.join(TAB, f"two_hop_{STAGE}_tables.json"), "w"), indent=1)

# ---- report
f2 = lambda x: f"{x:+.2f}"; f3 = lambda x: f"{x:+.3f}"
L = [f"# two_hop_organism · stage `{STAGE}` — the question-turn ladder finished: answer plane, k-sweep, consumer clamp, current base (Amendment 6)\n",
     f"Run `{META['run_id']}`, {META['n_forwards']} forwards, {META['elapsed_s']} s; Qwen3.6-27B, thinking off, **float32 residual from block {META['fp32_from']}** on every forward; {NC} cells ({len(names)} items × {len(META['carriers'])} carriers), "
     f"cluster = item (df = {len(names)-1}); writes at blocks {SWAP_L[0]}–{SWAP_L[-1]} on `q_pre` (question turn, scoring position excluded; {nq} positions); consumer clamps at the scoring position only; sequence-log-prob endpoint (logsumexp over spellings). "
     f"Full-vocabulary dictionary {META['vocab_size']} atoms per block; restricted word dictionary {META['restricted_dictionary_size']} atoms. Design: `H3/design_specs/two_hop_organism.md` Amendment 6; battery `H3/scripts/two_hop_qsplit6.py`; this file's §1–7 are generated by `two_hop_qsplit6_analysis.py`, §8 is hand-written.\n",
     "## 1. Gates\n",
     f"- Gate 1 (rendering, `q` token-id equality recipient/donor, scoring position excluded, single-token answer words): asserted per cell in the battery ({NC} cells, `q_pre` length {nq} in every cell) — PASS.",
     f"- Gate 2 (competence, sequence endpoint): clean32 {T['competence_clean32_seq']:.2f}, donor32 {T['competence_donor32_seq']:.2f} — **{'PASS' if T['gate2']['pass'] else 'FAIL'}**.",
     f"- Gate 3 (realized writes): fixed-target rows ρ ∈ [{min(rows[c]['rho'] for c in ft_rows):.4f}, {max(rows[c]['rho'] for c in ft_rows):.4f}], κ ≥ {min(rows[c]['kappa'] for c in ft_rows):.4f}, read-back max {g3['readback_max']:.1e}; consumer clamps ρ ∈ [{min(rows[c]['clamp_rho_min'] for c in ROWS if c.endswith('_cc') or c.endswith('_ccr')):.4f}, {max(rows[c]['clamp_rho_max'] for c in ROWS if c.endswith('_cc') or c.endswith('_ccr')):.4f}] over every block with a nonzero request (block 36's scoring position is still clean under every row, so its request is 0), κ ≥ {min(rows[c]['clamp_kappa_min'] for c in ROWS if c.endswith('_cc') or c.endswith('_ccr')):.4f}; current base ρ {rows['q_rem_cb_pre']['rho']:.4f} κ {rows['q_rem_cb_pre']['kappa']:.4f}; ‖v_R‖ = ‖v_J‖ asserted per position; `_ccr` realized norm within {100*g3['ccr_norm_match_max_rel_dev']:.2f} % of its `_cc` match (bar 5 %) — **{'PASS' if g3['pass'] else 'FAIL'}**.",
     f"- Gate 4 (`q_full_pre` reproduces Amendment 5, +11.19 [+10.00, +12.38], ≥ 10/12 items > 0): {f2(g4['mean'])} nats [{f2(g4['ci'][0])}, {f2(g4['ci'][1])}], {g4['n_pos']}/{g4['n']} items > 0 — **{'PASS' if T['gate4']['pass'] else 'FAIL'}**.",
     f"- Gate 5 (controls): `q_rand_pre` share {f3(T['gate5']['rand_share'])} (≤ 0.10), flips {T['gate5']['rand_flips']}/{NC} (≤ 2); `q_rem_rand_pre` share {f3(RR)} (≥ 0.80) — **{'PASS' if T['gate5']['pass'] else 'FAIL'}**.",
     f"- Gate 6 (pursuit positive control, reported): the k = 2 selection on `q_pre` contains the leading-space `intermediate` or `swap_to` atom in {100*T['gate6_positive_control']['L51_59']['either']:.1f} % of (block, position) cells at L51–59 (both: {100*T['gate6_positive_control']['L51_59']['both']:.1f} %), {100*T['gate6_positive_control']['all']['either']:.1f} % over blocks 36–62 (both {100*T['gate6_positive_control']['all']['both']:.1f} %); chance per pick 2/{META['vocab_size']} = {100*T['gate6_positive_control']['chance_per_pick']:.4f} %. P2 (majority at L51–59): {'held' if T['predictions']['P2_k2_majority_L51_59'] else 'not held'}.",
     f"- Gate 7 (restricted-dictionary NNLS KKT pass fraction ≥ 0.99 after the scipy fallback): {T['gate7']['kkt_pass_fraction']:.4f} of {T['gate7']['n']} (block, vector) fits — **{'PASS' if T['gate7']['pass'] else 'FAIL'}**. Early stops of the full-dictionary pursuit (no positive correlation left before k = {META['kmax']}): {T['early_stops']}.",
     f"- Collisions in the atom classification: {'; '.join(T['collisions']) if T['collisions'] else 'none'}.\n",
     "## 2. Main table (sequence endpoint; margin = log P(swap_answer) − log P(answer) minus clean32; item-clustered 95 % t-intervals; shares are ratios of item means)\n",
     "| row | margin (nats) | 95 % CI | items > 0 | share of `q_full_pre` | share of S_donor0 (bf16, quoted) | flips | ‖v‖/‖Δh‖ (L51–59) | J_NP int shift at s | J_NP int shift on `q_pre` | J_NP answer shift at s | block-63 re-entry (`q_pre`) | ρ / κ (write) | clamp ρ (dim) | ΔNLL max |",
     "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
for c in ROWS:
    r = rows[c]; m = r["margin_seq"]; vr = f"{r['v_over_dh_L51_59']:.3f}" if "v_over_dh_L51_59" in r else "—"
    L.append(f"| `{c}` | {f2(m['mean'])} | [{f2(m['ci'][0])}, {f2(m['ci'][1])}] | {m['n_pos']}/{m['n']} | {f3(r['share_of_q_full_pre'])} | {f3(r['share_of_S_donor0_bf16'])} | {r['flips_seq']}/{NC} | {vr} | "
             f"{f2(r['J_int_shift_s']['mean'])} ({r['J_int_shift_s']['n_pos']}/{m['n']}) | {f2(r['J_int_shift_qpre']['mean'])} | {f2(r['J_ans_shift_s']['mean'])} | {f2(r['block63_reentry_qpre']['mean'])} | "
             + (f"{r['rho']:.3f} / {r['kappa']:.3f}" if "rho" in r else "—") + " | " + (f"{r['clamp_rho']:.3f} ({r['clamp_dim'][0]}–{r['clamp_dim'][1]})" if "clamp_rho" in r else "—") + f" | {r['dNLL_max']:+.4f} |")
L.append(f"\nReference rows: natural donor rendering (`donor32`) J_NP int shift at s {f2(np.mean(byitem(lambda b: zsh(b, 'donor', 'int', 's'))))}, answer shift at s {f2(np.mean(byitem(lambda b: zsh(b, 'donor', 'ans', 's'))))}, margin {f2(np.mean(byitem(lambda b: mg(b, 'donor'))))} nats. "
         f"Candidate-set (single-token) margins are in the tables JSON as a secondary continuity column only. Columns: ‖v‖/‖Δh‖ is the removed/installed component's norm over ‖Δh‖, mean over cells × blocks 51–59 of the per-block position means; J_NP shifts are (swap_to − intermediate) and (swap_answer − answer) readouts at L51–59 minus clean; block-63 re-entry is Δproj(a_swap) − Δproj(a_int) on the raw unit naming directions at the first free block, mean over `q_pre`, minus clean.\n")
L.append("## 3. share(k) curve and energy fractions\n")
L.append("| k | J_k installed | J_k complement | J_k complement + consumer clamp | + random-k clamp (control) | random-k complement (norm- and rank-matched) | ‖v_Jk‖²/‖Δh‖² (all blocks / L51–59) | N(0, Σ) random-k fraction (all / L51–59) | k/d | blocks with e_J > e_rand |")
L.append("|---|---|---|---|---|---|---|---|---|---|")
for k in KS:
    cv = curve[str(k)]; e = T["energy"][str(k)]
    cell = lambda nm: f"{f3(cv[nm]['share'])} ({f2(cv[nm]['margin'])} [{f2(cv[nm]['ci'][0])}, {f2(cv[nm]['ci'][1])}], {cv[nm]['n_pos']}/{len(names)})"
    L.append(f"| {k} | {cell('J_k')} | {cell('J_k_rem')} | {cell('J_k_rem_cc')} | {cell('J_k_rem_ccr')} | {cell('rand_k_rem')} | {e['e_J_all_blocks']:.3f} / {e['e_J_L51_59']:.3f} | {e['e_rand_sigma_all_blocks']:.3f} / {e['e_rand_sigma_L51_59']:.3f} | {e['k_over_d']:.4f} | {e['blocks_e_J_gt_e_rand']}/{len(SWAP_L)} |")
L.append(f"\nPlane rows for comparison: intermediate plane A = {f3(A)}, complement B = {f3(B)} (+ consumer clamp {f3(sh('q_rem_pre_cc'))}, random-plane clamp {f3(sh('q_rem_pre_ccr'))}); answer plane A_ans = {f3(Aa)}, complement B_ans = {f3(Ba)}; restricted-dictionary NNLS k = 25: installed {f3(sh('q_J25nn_pre'))}, complement {f3(sh('q_rem25nn_pre'))} (+ clamp {f3(sh('q_rem25nn_pre_cc'))}, control {f3(sh('q_rem25nn_pre_ccr'))}); "
         f"atom-type ablations at k = 25: answer-related atoms removed {f3(sh('q_rem25ans_pre'))}, intermediate-related atoms removed {f3(sh('q_rem25int_pre'))}. Current base: `q_rem_cb_pre` {f3(sh('q_rem_cb_pre'))} vs `q_rem_pre` {f3(B)}; the free plane coordinate inside the band reaches {100*T['current_base']['reentry_fraction_L62']:.0f} % of the full donor's plane coordinate by block 62 ({100*T['current_base']['reentry_fraction_L51_59']:.0f} % over L51–59; projection ⟨c_cb, c_full⟩/‖c_full‖² per position, mean over `q_pre` and cells). "
         f"Energy reference: Σ_l from {T['energy']['n_cov_samples']} clean block outputs; 5 seeds.\n")
L.append("## 4. Atom-type breakdown (norm shares ‖v_C‖/‖v_Jk‖, mean over cells × blocks × positions; atoms are not orthogonal, so the shares are components, not a partition)\n")
L.append("| k | `q_pre` L51–59: answer / intermediate / other | `q_pre` all blocks | scoring position L51–59 | scoring position all blocks | count fraction (`q_pre`, L51–59) | |coef|-weighted fraction |")
L.append("|---|---|---|---|---|---|---|")
for k in KS:
    a = atoms[str(k)]; g = lambda d: " / ".join(f"{d[w]:.3f}" for w in ("answer", "intermediate", "other"))
    L.append(f"| {k} | {g(a['norm_share_qpre_L51_59'])} | {g(a['norm_share_qpre_all'])} | {g(a['norm_share_s_L51_59'])} | {g(a['norm_share_s_all'])} | {g(a['count_fraction_qpre_L51_59'])} | {g(a['coef_weighted_fraction_qpre_L51_59'])} |")
nnshare = " / ".join(f"{atoms['nn25']['norm_share_qpre_L51_59'][w]:.3f}" for w in ("answer", "intermediate", "other"))
L.append(f"| NNLS 25 | {nnshare} | — | — | — | — | — |")
L.append("\nMost frequent atoms among the first 25 selected on `q_pre` at L51–59 (over all cells), by class:\n")
for w in ("intermediate", "answer", "other"):
    L.append(f"- **{w}**: " + ", ".join(f"{s} ×{n_}" for s, n_ in T["top_atoms_k25_L51_59"][w][:25]))
L.append("\n## 5. Per-item shares of `q_full_pre` (first column: the full margin in nats)\n")
L.append("| item | full | plane A | rem B | ans-plane | ans-rem | J25 rem | J25 rem + cc | + ccr | rand25 rem | current base | NNLS25 rem | NNLS25 rem + cc |")
L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for nm in names:
    p = T["per_item"][nm]; L.append(f"| {nm} | {f2(p['q_full_pre'])} | " + " | ".join(f2(p[c]) for c in KEY[1:]) + " |")
L.append("\n## 6. Six seeded-random cells (seed 20260924; numbers generated, reading hand-written in §8)\n")
for b, d in T["six_random_cells"].items():
    L.append(f"- **{b}** (clean gap {d['clean_gap']:.1f} nats; greedy clean `{d['greedy']['clean']}`, donor `{d['greedy']['donor']}`): margins " + ", ".join(f"{c} {f2(d['margins'][c])}" for c in KEY)
             + f"; greedy under J25 rem `{d['greedy']['q_J25rem_pre']}`, + cc `{d['greedy']['q_J25rem_pre_cc']}`; J_NP int shift at s under J25 rem {f2(d['J_int_shift_s']['q_J25rem_pre'])} → + cc {f2(d['J_int_shift_s']['q_J25rem_pre_cc'])}; answer shift {f2(d['J_ans_shift_s']['q_J25rem_pre'])} → {f2(d['J_ans_shift_s']['q_J25rem_pre_cc'])}; "
             f"pursuit on the donor's Δh at s, L59: {d['atoms_s_L59_first8']}; on the last `q_pre` position: {d['atoms_qpre_last_L59_first8']}.")
D = T["decision"]; Pp = T["predictions"]
L.append(f"\n## 7. Decision rule (Amendment 6 §6) and predictions\n")
L.append(f"Consumer-clamped complement share at k = 25: **{f3(D['consumer_clamped_complement_share_k25'])}** (un-clamped {f3(D['unclamped_share_k25'])}; random-k clamp control {f3(D['control_ccr_share_k25'])}, {'within' if D['ccr_within_unclamped_interval'] else 'outside'} the un-clamped row's interval); gates 1–5 {'pass' if D['gates_1_5_pass'] else 'FAIL'} → **{D['reading']}**. "
         f"Qualifier: answer-related atoms carry {100*atoms['25']['norm_share_qpre_L51_59']['answer']:.0f} % of the J_25 part's norm on `q_pre` at L51–59 ({'most' if D['qualifier_answer_atoms_carry_most_of_J25'] else 'not most'}); answer-plane removal leaves B_ans = {f3(Ba)} ({'kills most of the effect' if D['qualifier_answer_plane_removal_kills_most'] else 'does not kill most of the effect'}).\n")
L.append("| prediction | held? | values |\n|---|---|---|")
L.append(f"| P1 gates 1–5 pass | {Pp['P1_gates_1_5']} | — |")
L.append(f"| P2 k = 2 selection contains intermediate/swap_to on a majority of `q_pre` cells at L51–59 | {Pp['P2_k2_majority_L51_59']} | {100*Pp['P2_value']:.1f} % |")
L.append(f"| P3 answer plane: B_ans ≤ 0.5 while B ≈ 0.78 (qualifier applies) | {Pp['P3_B_ans_le_0.5_and_B_stays']} | A_ans {f3(Aa)}, B_ans {f3(Ba)}, B {f3(B)} |")
L.append(f"| P4 share(J_k rem) non-increasing in k; random-k rem ≥ 0.80 at every k | {Pp['P4_Jrem_nonincreasing']} / {Pp['P4_rand_rem_ge_0.8_all_k']} | J rem {[round(x, 3) for x in Jrem]}; rand rem {[round(x, 3) for x in Rrem]} |")
L.append(f"| P5 `_cc` lowers each complement share; `_ccr` within the un-clamped interval | {sum(Pp['P5_cc_lower_than_unclamped'].values())}/{len(Pp['P5_cc_lower_than_unclamped'])} lower; {sum(Pp['P5_ccr_within_unclamped_interval'].values())}/{len(Pp['P5_ccr_within_unclamped_interval'])} within | " + "; ".join(f"{c}: cc {f3(sh(c + '_cc'))} vs {f3(sh(c))} (ccr {f3(sh(c + '_ccr'))})" for c in Pp['P5_cc_lower_than_unclamped']) + " |")
L.append(f"| P6 current base ≥ B − 0.10; plane rebuilt ≥ 0.5 by block 62? | {Pp['P6_cb_share_ok']} / {Pp['P6_plane_rebuilt']} | cb {f3(sh('q_rem_cb_pre'))}, B {f3(B)}, re-entry fraction at L62 {T['current_base']['reentry_fraction_L62']:.2f} |")
L.append(f"| P7 e_J > N(0, Σ) random-k fraction at every k (block means) | {Pp['P7_eJ_gt_erand_every_k']} | blocks holding per k: {Pp['P7_blocks_holding']} |")
L.append("\nCaveats carried forward from Amendment 5: each row is a fixed state trajectory over blocks 36–62 at `q_pre` (the rows are not a partition of one computation); `q_rem_pre` pins a two-token plane; the J_k rows pin the LS projection onto k greedy atoms of one dictionary (J_NP folded directions), so \"J-readable content\" here means \"content in the span of those atoms\"; the atom classes are string-mechanical (translations and related tokens in other scripts fall in *other*); shares are ratios of item means with n = 12 items.\n")
L.append("## 8. Interpretation, licensed / not licensed, next decision\n\n_(hand-written after reading the tables)_\n")
open(os.path.join(REP, f"two_hop_{STAGE}.md"), "w").write("\n".join(L))

# ---- figure from the tables only
try:
    for _p in ("/root/.claude/skills/iclr-plots/scripts", os.path.join(R.PROJECT, ".claude", "skills", "iclr-plots", "scripts"), "/workspace/.claude/skills/iclr-plots/scripts"): sys.path.insert(0, _p)
    import iclrplot as ip; ip.setup()
except Exception as e:
    print("iclrplot not used:", e)
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
fig, axs = plt.subplots(1, 3, figsize=(5.5, 2.1), gridspec_kw={"width_ratios": [1.5, 1.1, 1.0]})
ax = axs[0]; MAIN = ["q_full_pre", "q_plane_pre", "q_rem_pre", "q_ansplane_pre", "q_ansrem_pre", "q_J25rem_pre", "q_J25rem_pre_cc", "q_J25rem_pre_ccr", "q_rand25rem_pre", "q_rem_cb_pre"]
lab = {"q_full_pre": "full", "q_plane_pre": "plane", "q_rem_pre": "rem", "q_ansplane_pre": "ans\nplane", "q_ansrem_pre": "ans\nrem", "q_J25rem_pre": "J25\nrem", "q_J25rem_pre_cc": "J25 rem\n+clamp", "q_J25rem_pre_ccr": "J25 rem\n+rand", "q_rand25rem_pre": "rand25\nrem", "q_rem_cb_pre": "rem\ncur. base"}
colr = ["#4c4c4c", "#1f77b4", "#d62728", "#6baed6", "#fb6a4a", "#a50f15", "#67000d", "#fcae91", "#bdbdbd", "#e6550d"]
ms = [rows[c]["margin_seq"]["mean"] for c in MAIN]; lo = [rows[c]["margin_seq"]["mean"] - rows[c]["margin_seq"]["ci"][0] for c in MAIN]; hi = [rows[c]["margin_seq"]["ci"][1] - rows[c]["margin_seq"]["mean"] for c in MAIN]
lo = [0 if np.isnan(x) else x for x in lo]; hi = [0 if np.isnan(x) else x for x in hi]
ax.bar(range(len(MAIN)), ms, yerr=[lo, hi], color=colr, capsize=1.5, width=0.7)
for i, c in enumerate(MAIN): ax.scatter(np.full(len(names), i) + np.linspace(-0.2, 0.2, len(names)), [rows[c]["per_item_margin"][nm] for nm in names], s=3, color="k", alpha=0.5, zorder=3)
ax.axhline(0, color="k", lw=0.5); ax.set_xticks(range(len(MAIN))); ax.set_xticklabels([lab[c].replace("\n", " ") for c in MAIN], fontsize=4.5, rotation=60, ha="right", rotation_mode="anchor"); ax.set_ylabel("Δ answer margin (nats)"); ax.set_title("(a) rows, blocks 36–62 on q_pre", fontsize=7)
ax = axs[1]; from matplotlib.ticker import NullFormatter, FixedFormatter
for nm, st_, cl in (("J_k_rem", "-o", "#d62728"), ("J_k_rem_cc", "-s", "#67000d"), ("J_k_rem_ccr", "--^", "#fcae91"), ("rand_k_rem", ":d", "#7f7f7f"), ("J_k", "-x", "#1f77b4")):
    ax.plot(KS, [curve[str(k)][nm]["share"] for k in KS], st_, color=cl, ms=3, lw=1, label={"J_k_rem": "J_k complement", "J_k_rem_cc": "+ consumer clamp", "J_k_rem_ccr": "+ random-k clamp", "rand_k_rem": "random-k complement", "J_k": "J_k installed"}[nm])
ax.set_xscale("log"); ax.set_xticks(KS); ax.xaxis.set_major_formatter(FixedFormatter([str(k) for k in KS])); ax.xaxis.set_minor_formatter(NullFormatter()); ax.set_ylim(-0.1, 1.15); ax.axhline(0.5, color="k", lw=0.4, ls=":"); ax.axhline(0.2, color="k", lw=0.4, ls=":")
ax.set_xlabel("k atoms"); ax.set_ylabel("share of q_full_pre"); ax.set_title("(b) share(k)", fontsize=7); ax.legend(fontsize=4.2, frameon=False, loc="center", bbox_to_anchor=(0.55, 0.42), handlelength=1.6)
ax = axs[2]; w_ = 0.35; x = np.arange(len(KS))
for j, (w, cl) in enumerate((("answer", "#fb6a4a"), ("intermediate", "#1f77b4"), ("other", "#bdbdbd"))):
    ax.bar(x - w_ / 2, [atoms[str(k)]["norm_share_qpre_L51_59"][w] for k in KS], w_, bottom=[sum(atoms[str(k)]["norm_share_qpre_L51_59"][v] for v in ("answer", "intermediate", "other")[:j]) for k in KS], color=cl, label=w)
    ax.bar(x + w_ / 2, [atoms[str(k)]["norm_share_s_L51_59"][w] for k in KS], w_, bottom=[sum(atoms[str(k)]["norm_share_s_L51_59"][v] for v in ("answer", "intermediate", "other")[:j]) for k in KS], color=cl, alpha=0.55)
ax.set_xticks(x); ax.set_xticklabels([f"{k}" for k in KS]); ax.set_ylim(0, 1.75); ax.set_xlabel("k (left q_pre, right scoring pos.)"); ax.set_ylabel("norm share of v_Jk (components)"); ax.set_title("(c) atom types, L51–59", fontsize=7); ax.legend(fontsize=4.2, frameon=False, loc="upper left", ncol=3, columnspacing=0.8, handlelength=1.2)
fig.tight_layout(); fig.savefig(os.path.join(FIG, f"h3_{STAGE}.png"), dpi=200); fig.savefig(os.path.join(FIG, f"h3_{STAGE}.pdf"))
print(json.dumps({k: T[k] for k in ("competence_clean32_seq", "competence_donor32_seq", "gate3", "gate4", "gate5", "gate6_positive_control", "gate7", "decision", "predictions", "current_base")}, indent=1, default=str))
for c in ROWS: print(f"  [{c:20s}] seq margin {rows[c]['margin_seq']['mean']:+6.2f} [{rows[c]['margin_seq']['ci'][0]:+6.2f},{rows[c]['margin_seq']['ci'][1]:+6.2f}] ({rows[c]['margin_seq']['n_pos']}/{rows[c]['margin_seq']['n']}) share {rows[c]['share_of_q_full_pre']:+.3f} flips {rows[c]['flips_seq']:2d} | J int s {rows[c]['J_int_shift_s']['mean']:+.2f} q {rows[c]['J_int_shift_qpre']['mean']:+.2f} ans s {rows[c]['J_ans_shift_s']['mean']:+.2f} | c63 {rows[c]['block63_reentry_qpre']['mean']:+.2f}")
