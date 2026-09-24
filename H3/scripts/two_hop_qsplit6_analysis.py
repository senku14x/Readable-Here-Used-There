"""Analysis for two_hop_organism stages `qsplit6` (Amendment 6) and `stage2` (Amendment 7): one scoring pass from
raw_<stage>.npz + raw_<stage>_zq.npz + raw_pursuit_<stage>.npz + meta_<stage>.json (+ meta_admit.json and screen_stage2.json for
stage2) to H3/results/tables/two_hop_<stage>_tables.json, H3/results/reports/two_hop_<stage>.md (generated sections, the
hand-written reading inlined from two_hop_<stage>_reading.md) and H3/results/figures/h3_<stage>.{png,pdf}.
Usage: two_hop_qsplit6_analysis.py [qsplit6|stage2|smoke1|smoke2]"""
import os, sys, json
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "..", "common", "scripts"))
import numpy as np
import registry as R, rendering as Rn

STAGE = sys.argv[1] if len(sys.argv) > 1 else "qsplit6"; S2 = STAGE in ("stage2", "smoke2"); AMEND = "Amendment 7" if S2 else "Amendment 6"
OUT = R.out_dir("H3", "outputs", "two_hop_organism"); REP = R.out_dir("H3", "results", "reports"); TAB = R.out_dir("H3", "results", "tables"); FIG = R.out_dir("H3", "results", "figures")
# decompress every member once (NpzFile re-reads a member on each access; the 168-cell stage makes ~10^5 accesses)
RAW = dict(np.load(os.path.join(OUT, f"raw_{STAGE}.npz"), allow_pickle=True)); Z = dict(np.load(os.path.join(OUT, f"raw_{STAGE}_zq.npz")))
P = dict(np.load(os.path.join(OUT, f"raw_pursuit_{STAGE}.npz"), allow_pickle=True)); META = json.load(open(os.path.join(OUT, f"meta_{STAGE}.json")))
cells = META["cells"]; names_all = list(dict.fromkeys(b.split("|")[0] for b in cells)); COLS = META["columns"]; ROWS = META["rows"]; KS = META["ks"]; nq = META["n_qpre"]
S0 = META["s_donor0_seq_bf16_quoted"]; LZ0 = META["zq_layers"][0]; RB = slice(51 - LZ0, 60 - LZ0); SWAP_L = list(range(META["swap_layers"][0], META["swap_layers"][1] + 1)); RBL = list(range(51, 60))
ITEMS = {it["name"]: it for it in META["items"]}; NC = len(cells); tok = R.make_tokenizer(); CB_ROW = "q_rem_cbr_pre" if S2 else "q_rem_cb_pre"
CAT = {nm: (cells[nm + "|" + META["carriers"][0]].get("category") or ITEMS[nm].get("category")) for nm in names_all}
CONSTR = {nm: bool(cells[nm + "|" + META["carriers"][0]].get("constructed_donor", ITEMS[nm].get("constructed_donor", False))) for nm in names_all}
ADM = json.load(open(os.path.join(OUT, "meta_admit.json")))["admission"] if (S2 and os.path.exists(os.path.join(OUT, "meta_admit.json"))) else {}
SCREEN = json.load(open(os.path.join(OUT, "screen_stage2.json"))) if (S2 and os.path.exists(os.path.join(OUT, "screen_stage2.json"))) else {}
admitted = [nm for nm in names_all if ADM.get(nm, {}).get("admitted", False)] if ADM else list(names_all)
names = admitted if S2 else names_all            # the primary set: the admitted items (Amendment 7 §2) or all items (Amendment 6)
CLS_CODE = {"other": 0, "intermediate": 1, "answer": 2}
cls_is = lambda arr, w: (arr == CLS_CODE[w]) if arr.dtype.kind in "iu" else (arr == w)
ANS_ALIASES = {"Madrid": ["madrid"], "Ottawa": ["ottawa"], "Paris": ["paris", "parisian"], "Rome": ["rome", "roman"], "Berlin": ["berlin"], "Tokyo": ["tokyo"], "Arabic": ["arabic", "arab"],
               "Russian": ["russian"], "Budapest": ["budapest"], "Warsaw": ["warsaw"], "Athens": ["athens", "athenian"], "cow": ["cow", "cows", "cattle"], "bee": ["bee", "bees"]}
INT_ALIASES = {"Spain": ["spain", "spanish", "spaniard"], "Canada": ["canada", "canadian"], "France": ["france", "french"], "Italy": ["italy", "italian"], "Germany": ["germany", "german"],
               "Japan": ["japan", "japanese"], "Egypt": ["egypt", "egyptian"], "Russia": ["russia", "russian"], "Hungary": ["hungary", "hungarian"], "Poland": ["poland", "polish"],
               "Greece": ["greece", "greek"], "butter": ["butter", "buttery"], "honey": ["honey", "honeyed"]}
if S2:
    sys.argv = [sys.argv[0], "stage2"]; sys.path.insert(0, HERE); import two_hop_qsplit6 as _Q; ANS_ALIASES, INT_ALIASES = _Q.ANS_ALIASES, _Q.INT_ALIASES


def ci(v):
    from scipy import stats as st
    v = np.asarray(v, float); m = float(v.mean()); n = len(v)
    h = float(st.t.ppf(0.975, n - 1) * v.std(ddof=1) / np.sqrt(n)) if n > 1 else float("nan")
    return {"mean": m, "ci": [m - h, m + h], "n_pos": int((v > 0).sum()), "n": int(n)}


mg = lambda b, c: float((RAW[f"{b}|{c}|seq_swap"] - RAW[f"{b}|{c}|seq_answer"]) - (RAW[f"{b}|clean|seq_swap"] - RAW[f"{b}|clean|seq_answer"]))
mgc = lambda b, c: float((RAW[f"{b}|{c}|s_swap"] - RAW[f"{b}|{c}|s_answer"]) - (RAW[f"{b}|clean|s_swap"] - RAW[f"{b}|clean|s_answer"]))
zc = lambda b: cells[b].get("zq_columns", COLS)


def zsh(b, c, pair, where):
    """J_NP readout shift, L51-59 mean, (second - first) of the pair minus clean; where = 's' (scoring position) or 'q' (q_pre mean)."""
    it = cells[b]; w1, w2 = (it["intermediate"], it["swap_to"]) if pair == "int" else (it["answer"], it["swap_answer"]); cols = zc(b); i1, i2 = cols.index(w1), cols.index(w2)
    z = Z[f"{b}|{c}|zq"].astype(np.float32)[RB]; zcl = Z[f"{b}|clean|zq"].astype(np.float32)[RB]
    d = lambda z_: (z_[:, -1, i2] - z_[:, -1, i1]).mean() if where == "s" else (z_[:, :-1, i2] - z_[:, :-1, i1]).mean()
    return float(d(z) - d(zcl))


def c63(b, c, where):
    if where == "s": d = RAW[f"{b}|{c}|c63s"].astype(np.float32) - RAW[f"{b}|clean|c63s"].astype(np.float32)
    else: d = RAW[f"{b}|{c}|c63"].astype(np.float32).mean(0) - RAW[f"{b}|clean|c63"].astype(np.float32).mean(0)
    return float(d[1] - d[0])


ND_COL = {"q_full_pre": 0, "q_plane_pre": 1, "q_rem_pre": 1, "q_rand_pre": 1, "q_rem_rand_pre": 1, "q_rem_cb_pre": 1, "q_rem_cbr_pre": 1, "q_ansplane_pre": 2, "q_ansrem_pre": 2, "q_J25nn_pre": 7, "q_rem25nn_pre": 7}
for i, k in enumerate(KS): ND_COL[f"q_J{k}_pre"] = 3 + i; ND_COL[f"q_J{k}rem_pre"] = 3 + i; ND_COL[f"q_rand{k}rem_pre"] = 3 + i
base_of = lambda c: c[:-3] if c.endswith("_cc") else (c[:-4] if c.endswith("_ccr") else c)


def compute_rows(nms, which=None):
    """Per-row statistics with cluster = item over the item subset `nms`; shares are ratios of item means."""
    byit = lambda f: [float(np.mean([f(b) for b in cells if b.startswith(nm + "|")])) for nm in nms]
    sub = [b for b in cells if b.split("|")[0] in nms]; ND = np.stack([RAW[f"{b}|normdiag"] for b in sub])
    full_mean = float(np.mean(byit(lambda b: mg(b, "q_full_pre")))); rows = {}
    for c in (which or ROWS):
        marg = byit(lambda b: mg(b, c))
        row = {"margin_seq": ci(marg), "share_of_q_full_pre": float(np.mean(marg) / full_mean), "share_of_S_donor0_bf16": float(np.mean(marg) / S0),
               "flips_seq": int(sum(RAW[f"{b}|{c}|seq_swap"] > RAW[f"{b}|{c}|seq_answer"] for b in sub)), "margin_candidate": ci(byit(lambda b: mgc(b, c))),
               "per_item_margin": dict(zip(nms, marg)), "per_cell_margin": {b: mg(b, c) for b in sub},
               "J_int_shift_s": ci(byit(lambda b: zsh(b, c, "int", "s"))), "J_int_shift_qpre": ci(byit(lambda b: zsh(b, c, "int", "q"))),
               "J_ans_shift_s": ci(byit(lambda b: zsh(b, c, "ans", "s"))), "J_ans_shift_qpre": ci(byit(lambda b: zsh(b, c, "ans", "q"))),
               "block63_reentry_qpre": ci(byit(lambda b: c63(b, c, "q"))), "block63_reentry_s": ci(byit(lambda b: c63(b, c, "s"))),
               "dNLL_max": float(max(RAW[f"{b}|{c}|nll"] - RAW[f"{b}|clean|nll"] for b in sub)), "dNLL_mean": float(np.mean([RAW[f"{b}|{c}|nll"] - RAW[f"{b}|clean|nll"] for b in sub]))}
        bc = base_of(c); b0 = sub[0]
        if f"{b0}|{c}|rho" in RAW: row.update({"rho": float(np.mean([RAW[f"{b}|{c}|rho"] for b in sub])), "kappa": float(np.mean([RAW[f"{b}|{c}|kappa"] for b in sub]))})
        if f"{b0}|{c}|rberr" in RAW: row.update({"readback_max": float(max(RAW[f"{b}|{c}|rberr"] for b in sub)), "plane_dev_max": float(max(RAW[f"{b}|{c}|plane_dev"] for b in sub))})
        if bc in ND_COL: r_ = ND[:, :, ND_COL[bc]] / ND[:, :, 0]; row.update({"v_over_dh": float(r_.mean()), "v_over_dh_L51_59": float(r_[:, 15:24].mean())})
        if c.endswith("_cc") or c.endswith("_ccr"):
            req = np.stack([RAW[f"{b}|{c}|clamp_req"] for b in sub]); real = np.stack([RAW[f"{b}|{c}|clamp_real"] for b in sub]); kap = np.stack([RAW[f"{b}|{c}|clamp_kappa"] for b in sub]); ok = req > 1e-6
            row.update({"clamp_rho": float((real[ok] / req[ok]).mean()), "clamp_rho_min": float((real[ok] / req[ok]).min()), "clamp_rho_max": float((real[ok] / req[ok]).max()), "clamp_kappa_min": float(kap[ok].min()),
                        "clamp_req_norm_mean": float(req[ok].mean()), "clamp_dim": [int(min(RAW[f"{b}|{c}|clamp_dim"].min() for b in sub)), int(max(RAW[f"{b}|{c}|clamp_dim"].max() for b in sub))], "clamp_zero_request_blocks": int((~ok).sum())})
            if c.endswith("_ccr"):
                realcc = np.stack([RAW[f"{b}|{bc}_cc|clamp_real"] for b in sub]); okc = realcc > 1e-6; row["ccr_norm_match_max_rel_dev"] = float((np.abs(real[okc] - realcc[okc]) / realcc[okc]).max())
        if c == "q_rem_cbr_pre": row["cons_check_max"] = float(max(RAW[f"{b}|{c}|cons_check"].max() for b in sub)); row["cons_check_mean"] = float(np.mean([RAW[f"{b}|{c}|cons_check"].mean() for b in sub]))
        rows[c] = row
    return rows, full_mean


byitem = lambda f: [float(np.mean([f(b) for b in cells if b.startswith(nm + "|")])) for nm in names]
T = {"stage": STAGE, "amendment": AMEND, "run_id": META["run_id"], "n_forwards": META["n_forwards"], "elapsed_s": META["elapsed_s"], "n_cells": NC, "n_items_all": len(names_all), "n_items_primary": len(names),
     "primary_set": "admitted" if S2 else "all", "admitted": admitted if S2 else None, "categories": CAT, "constructed_donor": CONSTR, "n_qpre": nq, "s_donor0_seq_bf16_quoted": S0,
     "restricted_dictionary_size": META["restricted_dictionary_size"], "vocab_size": META["vocab_size"], "ks": KS}
rows, full_mean = compute_rows(names); T["rows"] = rows; sh = lambda c: rows[c]["share_of_q_full_pre"]
rows_all = rows if names == names_all else compute_rows(names_all)[0]; T["rows_all"] = {c: {k: v for k, v in r.items() if k not in ("per_cell_margin",)} for c, r in rows_all.items()}
KEY = ["q_full_pre", "q_plane_pre", "q_rem_pre", "q_ansplane_pre", "q_ansrem_pre", "q_J25rem_pre", "q_J25rem_pre_cc", "q_J25rem_pre_ccr", "q_rand25rem_pre", CB_ROW, "q_rem25nn_pre", "q_rem25nn_pre_cc"]
if S2:   # per relation type (all items of the type, and its admitted items)
    T["per_relation"] = {}
    for cat in sorted(set(CAT.values())):
        nm_c = [nm for nm in names_all if CAT[nm] == cat]; nm_a = [nm for nm in nm_c if nm in admitted]
        rc, fm = compute_rows(nm_c, KEY); entry = {"n_items": len(nm_c), "n_admitted": len(nm_a), "constructed_donor": sorted({CONSTR[nm] for nm in nm_c}), "screen_flag": SCREEN.get(cat, {}).get("flagged"),
                                                    "screen_loo_residual": SCREEN.get(cat, {}).get("loo_residual_fraction"), "full_margin": rc["q_full_pre"]["margin_seq"], "shares_all": {c: rc[c]["share_of_q_full_pre"] for c in KEY}}
        if len(nm_a) >= 2: ra, _ = compute_rows(nm_a, KEY); entry["shares_admitted"] = {c: ra[c]["share_of_q_full_pre"] for c in KEY}; entry["full_margin_admitted"] = ra["q_full_pre"]["margin_seq"]
        T["per_relation"][cat] = entry

# ---- gates
T["gate1"] = {"n_cells": NC, "pass": True, "note": "rendering, q token-id equality, scoring position excluded and single-token forms asserted per cell in the battery"}
comp_all = {"clean": float(np.mean([RAW[f"{b}|clean|seq_answer"] > RAW[f"{b}|clean|seq_swap"] for b in cells])), "donor": float(np.mean([RAW[f"{b}|donor|seq_swap"] > RAW[f"{b}|donor|seq_answer"] for b in cells]))}
sub_p = [b for b in cells if b.split("|")[0] in names]
comp_p = {"clean": float(np.mean([RAW[f"{b}|clean|seq_answer"] > RAW[f"{b}|clean|seq_swap"] for b in sub_p])), "donor": float(np.mean([RAW[f"{b}|donor|seq_swap"] > RAW[f"{b}|donor|seq_answer"] for b in sub_p]))}
T["competence_clean32_seq"], T["competence_donor32_seq"] = comp_p["clean"], comp_p["donor"]; T["competence_all_items"] = comp_all
T["gate2"] = {"pass": bool(comp_p["clean"] >= 0.9 and comp_p["donor"] >= 0.9), "primary_set": comp_p, "all_items": comp_all}
ft_rows = [c for c in ROWS if "rho" in rows[c] and not (c.endswith("_cc") or c.endswith("_ccr"))]; cc_all = [c for c in ROWS if c.endswith("_cc") or c.endswith("_ccr")]
g3 = {"fixed_target_rows_ok": bool(all(0.9 <= rows[c]["rho"] <= 1.1 and rows[c]["kappa"] >= 0.99 for c in ft_rows)),
      "clamp_writes_ok": bool(all(0.9 <= rows[c]["clamp_rho_min"] and rows[c]["clamp_rho_max"] <= 1.1 and rows[c]["clamp_kappa_min"] >= 0.99 for c in cc_all)),
      "current_base_ok": bool(0.9 <= rows[CB_ROW]["rho"] <= 1.1 and rows[CB_ROW]["kappa"] >= 0.99),
      "ccr_norm_match_max_rel_dev": float(max(rows[c]["ccr_norm_match_max_rel_dev"] for c in ROWS if c.endswith("_ccr"))), "readback_max": float(max(rows[c]["readback_max"] for c in ROWS if "readback_max" in rows[c]))}
g3["pass"] = bool(g3["fixed_target_rows_ok"] and g3["clamp_writes_ok"] and g3["current_base_ok"] and g3["ccr_norm_match_max_rel_dev"] <= 0.05); T["gate3"] = g3
if S2:
    pil = [nm for nm in names_all if not CONSTR[nm]]; g4v = ci([float(np.mean([mg(b, "q_full_pre") for b in cells if b.startswith(nm + "|")])) for nm in pil])
    T["gate4"] = {"pilot_items": pil, "mean": g4v["mean"], "items_pos": g4v["n_pos"], "n": g4v["n"], "stage1_interval": [10.00, 12.38], "pass": bool(10.00 <= g4v["mean"] <= 12.38 and g4v["n_pos"] >= 10), "note": "reproduction gate: the 12 released-donor items under the Stage 2 run"}
else:
    g4 = rows["q_full_pre"]["margin_seq"]; T["gate4"] = {"mean": g4["mean"], "items_pos": g4["n_pos"], "amendment5_interval": [10.00, 12.38], "amendment5_mean": 11.19, "pass": bool(10.00 <= g4["mean"] <= 12.38 and g4["n_pos"] >= 10)}
T["gate5"] = {"rand_share": sh("q_rand_pre"), "rand_flips": rows["q_rand_pre"]["flips_seq"], "rem_rand_share": sh("q_rem_rand_pre"), "pass": bool(sh("q_rand_pre") <= 0.10 and rows["q_rand_pre"]["flips_seq"] <= 2 * max(1, NC // 48) and sh("q_rem_rand_pre") >= 0.80)}
pc = {"L51_59": {"either": [], "both": []}, "all": {"either": [], "both": []}}
for b in cells:
    it = cells[b]; ti, ts = Rn.single_token_id(tok, it["intermediate"]), Rn.single_token_id(tok, it["swap_to"])
    for l in SWAP_L:
        a = RAW[f"{b}|L{l}|atoms_qpre"][:, :2]; e = [(ti in r) or (ts in r) for r in a]; bo = [(ti in r) and (ts in r) for r in a]
        pc["all"]["either"] += e; pc["all"]["both"] += bo
        if l in RBL: pc["L51_59"]["either"] += e; pc["L51_59"]["both"] += bo
T["gate6_positive_control"] = {w: {k: float(np.mean(v)) for k, v in d.items()} for w, d in pc.items()}; T["gate6_positive_control"]["chance_per_pick"] = 2 / META["vocab_size"]
kk = np.concatenate([P[f"L{l}|kkt"] for l in SWAP_L]); T["gate7"] = {"kkt_pass_fraction": float(kk.mean()), "n": int(len(kk)), "pass": bool(kk.mean() >= 0.99)}
if S2: T["gate8"] = {"cons_check_max": rows_all[CB_ROW]["cons_check_max"], "cons_check_mean": rows_all[CB_ROW]["cons_check_mean"], "pass": bool(rows_all[CB_ROW]["cons_check_max"] <= 1.5)}
T["gates_1_5_pass"] = bool(all(T[f"gate{i}"]["pass"] for i in range(1, 6)))
if S2:
    n_cat_adm = len({CAT[nm] for nm in admitted}); T["decision_conditions"] = {"n_admitted": len(admitted), "n_relation_types_admitted": n_cat_adm, "competence_admitted": comp_p, "met": bool(len(admitted) >= 12 and n_cat_adm >= 3 and min(comp_p.values()) >= 0.9)}

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
atoms = {}; sub_p = [b for b in cells if b.split("|")[0] in names]; bidx = {b: i for i, b in enumerate(cells)}
for k in KS:
    q_all = np.stack([RAW[f"{b}|L{l}|clsshare{k}"] for b in sub_p for l in SWAP_L]); q_rb = np.stack([RAW[f"{b}|L{l}|clsshare{k}"] for b in sub_p for l in RBL])
    s_all = np.stack([RAW[f"{b}|L{l}|clsshare{k}_s"] for b in sub_p for l in SWAP_L]); s_rb = np.stack([RAW[f"{b}|L{l}|clsshare{k}_s"] for b in sub_p for l in RBL])
    cnt = {"answer": [], "intermediate": [], "other": []}; wcnt = {"answer": [], "intermediate": [], "other": []}
    for b in sub_p:
        bi = bidx[b]
        for l in RBL:
            cls = RAW[f"{b}|L{l}|cls_qpre"][:, :k]; co = np.abs(P[f"L{l}|coef{k}"][bi * nq:(bi + 1) * nq]); tot = co.sum(1, keepdims=True).clip(1e-12)
            for w in cnt: cnt[w].append(float(cls_is(cls, w).mean())); wcnt[w].append(float((cls_is(cls, w) * co / tot).sum(1).mean()))
    atoms[str(k)] = {"norm_share_qpre_L51_59": dict(zip(("answer", "intermediate", "other"), q_rb.mean(axis=(0, 1)).round(4).tolist())), "norm_share_qpre_all": dict(zip(("answer", "intermediate", "other"), q_all.mean(axis=(0, 1)).round(4).tolist())),
                     "norm_share_s_L51_59": dict(zip(("answer", "intermediate", "other"), s_rb.mean(0).round(4).tolist())), "norm_share_s_all": dict(zip(("answer", "intermediate", "other"), s_all.mean(0).round(4).tolist())),
                     "count_fraction_qpre_L51_59": {w: float(np.mean(v)) for w, v in cnt.items()}, "coef_weighted_fraction_qpre_L51_59": {w: float(np.mean(v)) for w, v in wcnt.items()}}
nn_rb = np.stack([RAW[f"{b}|L{l}|clsshare_nn"] for b in sub_p for l in RBL]); atoms["nn25"] = {"norm_share_qpre_L51_59": dict(zip(("answer", "intermediate", "other"), nn_rb.mean(axis=(0, 1)).round(4).tolist()))}
T["atom_types"] = atoms
alias_set = lambda d, w: set(d.get(w, [])) | {w.lower()}
T["collisions"] = [f"{nm}: {sorted((alias_set(ANS_ALIASES, it['answer']) | alias_set(ANS_ALIASES, it['swap_answer'])) & (alias_set(INT_ALIASES, it['intermediate']) | alias_set(INT_ALIASES, it['swap_to'])))} (answer class takes priority)"
                   for nm, it in ITEMS.items() if (alias_set(ANS_ALIASES, it["answer"]) | alias_set(ANS_ALIASES, it["swap_answer"])) & (alias_set(INT_ALIASES, it["intermediate"]) | alias_set(INT_ALIASES, it["swap_to"]))]
top = {"other": Counter(), "intermediate": Counter(), "answer": Counter()}
for b in sub_p:
    for l in RBL:
        a = RAW[f"{b}|L{l}|atoms_qpre"][:, :25]; cl = RAW[f"{b}|L{l}|cls_qpre"][:, :25]
        for w in top: top[w].update(int(v) for v in a[cls_is(cl, w)])
T["top_atoms_k25_L51_59"] = {w: [(repr(tok.decode([v])), n_) for v, n_ in top[w].most_common(30)] for w in top}
T["early_stops"] = int(sum(int((RAW[f"{b}|L{l}|stop_qpre"] < META["kmax"]).sum()) for b in cells for l in SWAP_L))

# ---- content check at the two informative positions (last q_pre position and s), translations included
# Defined after seeing the six seeded cells of Stage 1 (researcher note, 2026-09-24): the pooled Phase B statistic counts every q_pre position,
# most of which carry no entity content; at the last q_pre position and at s the selected atoms are entity content across scripts.
# "Translation-included" rule (mechanical): an atom is content-related if the frozen classifier says intermediate/answer, OR its decoded string
# has no ASCII letter and its nearest Latin-script unembedding row (cosine, excluding itself) decodes to one of the item's four words or their
# aliases (or the >= 3-letter prefix rule for intermediates). The unembedding rows are read from the checkpoint shard; no forward.
import re as _re, torch as _torch
from huggingface_hub import snapshot_download as _snap
from safetensors import safe_open as _safe
_snapd = _snap(R.MODEL, revision=R.REV, allow_patterns=["*.json"]); _idx = json.load(open(os.path.join(_snapd, "model.safetensors.index.json")))
_key = "lm_head.weight" if "lm_head.weight" in _idx["weight_map"] else "model.embed_tokens.weight"; _shard = _idx["weight_map"][_key]
with _safe(os.path.join(_snap(R.MODEL, revision=R.REV, allow_patterns=[_shard, "*.json"]), _shard), "pt") as _f: _WU = _f.get_tensor(_key).float()
_dev = "cuda" if (_torch.cuda.is_available() and _torch.cuda.mem_get_info()[0] > 8e9) else "cpu"; _WUn = (_WU / _WU.norm(dim=1, keepdim=True).clamp_min(1e-6)).to(_dev)
_toks = tok.convert_ids_to_tokens(list(range(_WU.shape[0]))); _latin = _torch.tensor([bool(_re.search(r"[A-Za-z]", t or "")) for t in _toks], device=_dev)
_nn_cache = {}


def nearest_latin(v):
    if v not in _nn_cache:
        s = _WUn @ _WUn[v]; s[v] = -2; s[~_latin] = -2; _nn_cache[v] = int(s.argmax())
    return _nn_cache[v]


def classify_ext(v, it):
    """frozen class, or 'translation' when a non-Latin atom back-translates to one of the item's four words."""
    s = tok.decode([int(v)]); c = _Q.classify_atom(s, it) if S2 else _classify_frozen(s, it)
    if c != "other" or _re.search(r"[A-Za-z]", s): return c
    c2 = (_Q.classify_atom if S2 else _classify_frozen)(tok.decode([nearest_latin(int(v))]), it)
    return "translation" if c2 != "other" else "other"


def _classify_frozen(s, it):
    s = s.strip().lower()
    if not s: return "other"
    for w in (it["answer"], it["swap_answer"]):
        if s == w.lower() or s in ANS_ALIASES.get(w, []): return "answer"
    for w in (it["intermediate"], it["swap_to"]):
        wl = w.lower()
        if s == wl or s in INT_ALIASES.get(w, []): return "intermediate"
        if len(s) >= 3 and s.isalpha() and (wl.startswith(s) or s.startswith(wl)): return "intermediate"
    return "other"


_assoc_cache = {}


def assoc_set(it, N=100):
    """broad level: the union of the top-N cosine neighbours (any script) of the item's four words in the unembedding (catches associates such as Nile, Kremlin, Toronto, and also unrelated capitals)."""
    key = (it["intermediate"], it["swap_to"], it["answer"], it["swap_answer"])
    if key not in _assoc_cache:
        s_ = set()
        for w in key:
            v = Rn.single_token_id(tok, w); s_.update(_torch.topk(_WUn @ _WUn[v], N + 1).indices.tolist())
        _assoc_cache[key] = s_
    return _assoc_cache[key]


cc_ = {w: {k: [] for k in ("frozen", "translated", "associated", "frozen_w", "translated_w", "associated_w")} for w in ("last_qpre", "s")}; trans_top = Counter(); assoc_top = Counter(); nb = len(cells)
for b in sub_p:
    bi = bidx[b]; it = cells[b]; AS = assoc_set(it)
    for l in RBL:
        for where, a, co in (("last_qpre", RAW[f"{b}|L{l}|atoms_qpre"][-1, :25], np.abs(P[f"L{l}|coef25"][bi * nq + nq - 1])), ("s", RAW[f"{b}|L{l}|atoms_s"][:25], np.abs(P[f"L{l}|coef25"][nb * nq + bi]))):
            cl = [classify_ext(int(v), it) for v in a]; fro = np.array([c in ("intermediate", "answer") for c in cl]); tr = np.array([c in ("intermediate", "answer", "translation") for c in cl])
            asc = np.array([t or (int(v) in AS) for t, v in zip(tr, a)]); w_ = co / co.sum().clip(1e-12)
            for nm_, arr in (("frozen", fro), ("translated", tr), ("associated", asc)): cc_[where][nm_].append(arr.mean()); cc_[where][nm_ + "_w"].append((arr * w_).sum())
            trans_top.update(tok.decode([int(v)]) for v, c in zip(a, cl) if c == "translation"); assoc_top.update(tok.decode([int(v)]) for v, t, s_ in zip(a, tr, asc) if s_ and not t)
T["content_check"] = {"note": "defined after seeing the six seeded cells (researcher note 2026-09-24); top-25 pursuit atoms at L51-59; 'translated' adds non-Latin atoms whose nearest Latin unembedding neighbour is one of the item's four words or aliases; 'associated' adds any atom among the top-100 unembedding cosine neighbours of the four words",
                      **{where: {k: float(np.mean(v)) for k, v in d.items()} for where, d in cc_.items()}, "top_translation_atoms": [(repr(s), n_) for s, n_ in trans_top.most_common(30)], "top_associated_atoms": [(repr(s), n_) for s, n_ in assoc_top.most_common(30)],
                      "pooled_reference_frozen_all_qpre_positions_L51_59": float(1 - atoms["25"]["count_fraction_qpre_L51_59"]["other"])}
# per-item split of the J_25 part (norm shares answer / intermediate / other; q_pre L51-59 mean and at s)
T["per_item_J25_split"] = {}
for nm in names_all:
    cb_ = [b for b in cells if b.startswith(nm + "|")]
    q = np.stack([RAW[f"{b}|L{l}|clsshare25"] for b in cb_ for l in RBL]).mean(axis=(0, 1)); s_ = np.stack([RAW[f"{b}|L{l}|clsshare25_s"] for b in cb_ for l in RBL]).mean(0)
    T["per_item_J25_split"][nm] = {"qpre": dict(zip(("answer", "intermediate", "other"), q.round(3).tolist())), "s": dict(zip(("answer", "intermediate", "other"), s_.round(3).tolist()))}
# readouts at s under the consumer clamps (the clamp is partial: these do not drop to 0)
T["clamp_readouts_s"] = {c: {"int_unclamped": rows[c]["J_int_shift_s"]["mean"], "int_cc": rows[c + "_cc"]["J_int_shift_s"]["mean"], "int_ccr": rows[c + "_ccr"]["J_int_shift_s"]["mean"],
                             "ans_unclamped": rows[c]["J_ans_shift_s"]["mean"], "ans_cc": rows[c + "_cc"]["J_ans_shift_s"]["mean"], "ans_ccr": rows[c + "_ccr"]["J_ans_shift_s"]["mean"]} for c in ROWS if c + "_cc" in rows}
T["clamp_readouts_s"]["full"] = {"int": rows["q_full_pre"]["J_int_shift_s"]["mean"], "ans": rows["q_full_pre"]["J_ans_shift_s"]["mean"]}

# ---- current base: re-entry fraction of the plane coordinate inside the band
re_, re_w, nr_ = {}, {}, {}
for l_i, l in enumerate(SWAP_L):
    fr, frw, nr = [], [], []
    for b in sub_p:
        cf = RAW[f"{b}|L{l}|plane_coord_full"].astype(np.float32); cb = RAW[f"{b}|{CB_ROW}|plane_band"][l_i].astype(np.float32)
        fr.append(float(((cb * cf).sum(1) / (cf ** 2).sum(1).clip(1e-8)).mean())); frw.append(float((cb * cf).sum() / (cf ** 2).sum().clip(1e-8))); nr.append(float(np.linalg.norm(cb, axis=1).mean() / np.linalg.norm(cf, axis=1).mean().clip(1e-8)))
    re_[str(l)] = float(np.mean(fr)); re_w[str(l)] = float(np.mean(frw)); nr_[str(l)] = float(np.mean(nr))
T["current_base"] = {"row": CB_ROW, "share": sh(CB_ROW), "rem_share": sh("q_rem_pre"), "reentry_fraction_by_block_perposition": re_, "reentry_fraction_by_block_weighted": re_w, "plane_norm_ratio_by_block": nr_,
                     "reentry_fraction_L62": re_w[str(SWAP_L[-1])], "reentry_fraction_L51_59": float(np.mean([re_w[str(l)] for l in RBL])), "plane_norm_ratio_L62": nr_[str(SWAP_L[-1])], "plane_norm_ratio_max": float(max(nr_.values())),
                     "first_block_weighted_ge_0.5": next((l for l in SWAP_L if re_w[str(l)] >= 0.5), None),
                     "P6_share_ok": bool(sh(CB_ROW) >= sh("q_rem_pre") - 0.10), "plane_rebuilt_ge_0.5_by_L62": bool(re_w[str(SWAP_L[-1])] >= 0.5), "plane_rebuilt_ge_0.5_anywhere_in_band": bool(max(re_w.values()) >= 0.5)}
T["clamp_effects"] = {}
for c in ROWS:
    if c + "_cc" in rows:
        T["clamp_effects"][c] = {"cc_delta": ci(byitem(lambda b: mg(b, c) - mg(b, c + "_cc"))), "ccr_delta": ci(byitem(lambda b: mg(b, c) - mg(b, c + "_ccr"))),
                                 "cc_delta_share_of_full": float(np.mean(byitem(lambda b: mg(b, c) - mg(b, c + "_cc"))) / full_mean), "cc_delta_share_of_row": float(np.mean(byitem(lambda b: mg(b, c) - mg(b, c + "_cc"))) / rows[c]["margin_seq"]["mean"])}
T["plane_comparison"] = {"ans_minus_int_plane": ci(byitem(lambda b: mg(b, "q_ansplane_pre") - mg(b, "q_plane_pre"))), "v_over_dh_int_plane_L51_59": rows["q_plane_pre"].get("v_over_dh_L51_59"), "v_over_dh_ans_plane_L51_59": rows["q_ansplane_pre"].get("v_over_dh_L51_59"),
                         "additivity_J25": ci([rows["q_full_pre"]["per_item_margin"][nm] - rows["q_J25_pre"]["per_item_margin"][nm] - rows["q_J25rem_pre"]["per_item_margin"][nm] for nm in names]),
                         "additivity_plane": ci([rows["q_full_pre"]["per_item_margin"][nm] - rows["q_plane_pre"]["per_item_margin"][nm] - rows["q_rem_pre"]["per_item_margin"][nm] for nm in names]),
                         "additivity_ans_plane": ci([rows["q_full_pre"]["per_item_margin"][nm] - rows["q_ansplane_pre"]["per_item_margin"][nm] - rows["q_ansrem_pre"]["per_item_margin"][nm] for nm in names])}

# ---- decision rule and predictions
A, B = sh("q_plane_pre"), sh("q_rem_pre"); Aa, Ba = sh("q_ansplane_pre"), sh("q_ansrem_pre"); RR = sh("q_rem_rand_pre")
cc25, ccr25, un25 = sh("q_J25rem_pre_cc"), sh("q_J25rem_pre_ccr"), sh("q_J25rem_pre"); un25ci = rows["q_J25rem_pre"]["margin_seq"]["ci"]
ccr_within = bool(un25ci[0] <= rows["q_J25rem_pre_ccr"]["margin_seq"]["mean"] <= un25ci[1])
dec = "non-J channel carries most of this consumer's margin" if cc25 >= 0.5 else ("the complement was J-mediated at the consumer" if cc25 <= 0.2 else "report the share(k) curve as the result")
dec_ok = T["gates_1_5_pass"] and ccr_within and (T["decision_conditions"]["met"] if S2 else True)
T["decision"] = {"consumer_clamped_complement_share_k25": cc25, "control_ccr_share_k25": ccr25, "unclamped_share_k25": un25, "ccr_within_unclamped_interval": ccr_within, "gates_1_5_pass": T["gates_1_5_pass"],
                 "reading": dec if dec_ok else f"not taken ({'gate failure' if not T['gates_1_5_pass'] else ('ccr control outside the un-clamped interval' if not ccr_within else 'admitted set too small or not competent')}): would read '{dec}'",
                 "qualifier_answer_atoms_carry_most_of_J25": bool(atoms["25"]["norm_share_qpre_L51_59"]["answer"] > 0.5), "qualifier_answer_plane_removal_kills_most": bool(Ba <= 0.5), "A_plane": A, "B_rem": B, "A_ans": Aa, "B_ans": Ba}
Jrem = [sh(f"q_J{k}rem_pre") for k in KS]; Rrem = [sh(f"q_rand{k}rem_pre") for k in KS]
T["predictions"] = {"P1_gates_1_5": T["gates_1_5_pass"], "P2_k2_majority_L51_59": bool(T["gate6_positive_control"]["L51_59"]["either"] > 0.5), "P2_value": T["gate6_positive_control"]["L51_59"]["either"],
                    "P3_B_ans_le_0.5_and_B_stays": bool(Ba <= 0.5 and B >= 0.68), "P3_values": {"A_ans": Aa, "B_ans": Ba, "B": B},
                    "P4_Jrem_nonincreasing": bool(all(Jrem[i + 1] <= Jrem[i] + 1e-9 for i in range(len(KS) - 1))), "P4_rand_rem_ge_0.8_all_k": bool(all(r >= 0.8 for r in Rrem)), "P4_values": {"J_rem": Jrem, "rand_rem": Rrem},
                    "P5_cc_lower_than_unclamped": {c: bool(rows[c + "_cc"]["margin_seq"]["mean"] < rows[c]["margin_seq"]["mean"]) for c in ROWS if c + "_cc" in rows},
                    "P5_ccr_within_unclamped_interval": {c: bool(rows[c]["margin_seq"]["ci"][0] <= rows[c + "_ccr"]["margin_seq"]["mean"] <= rows[c]["margin_seq"]["ci"][1]) for c in ROWS if c + "_ccr" in rows},
                    "P6_cb_share_ok": T["current_base"]["P6_share_ok"], "P6_plane_rebuilt": T["current_base"]["plane_rebuilt_ge_0.5_by_L62"],
                    "P7_eJ_gt_erand_every_k": bool(all(T["energy"][str(k)]["e_J_all_blocks"] > T["energy"][str(k)]["e_rand_sigma_all_blocks"] for k in KS)), "P7_blocks_holding": {str(k): T["energy"][str(k)]["blocks_e_J_gt_e_rand"] for k in KS}}
if S2:
    cat_adm = Counter(CAT[nm] for nm in admitted)
    T["predictions_A7"] = {"P1_gates": bool(all(T[f"gate{i}"]["pass"] for i in (1, 2, 3, 5, 7, 8))) and T["gate4"]["pass"], "P2_ge3_types_with_ge3_items": bool(sum(v >= 3 for v in cat_adm.values()) >= 3), "P2_admitted_per_type": dict(cat_adm),
                           "P3_J25rem_in_[0.45,0.75]": bool(0.45 <= un25 <= 0.75), "P3_J25rem_cc_in_[0.3,0.6]": bool(0.3 <= cc25 <= 0.6), "P3_rem_cc_ge_rem_minus_0.10": bool(sh("q_rem_pre_cc") >= B - 0.10), "P3_Aans_gt_A": bool(Aa > A),
                           "P5_cbr_share_ok": T["current_base"]["P6_share_ok"], "P5_cons_check_max": T["gate8"]["cons_check_max"], "P5_plane_rebuilt_by_L62": T["current_base"]["plane_rebuilt_ge_0.5_by_L62"]}
T["per_item"] = {nm: {"category": CAT[nm], "constructed_donor": CONSTR[nm], "admitted": (nm in admitted) if S2 else None,
                      **{c: (rows_all[c]["per_item_margin"][nm] / rows_all["q_full_pre"]["per_item_margin"][nm] if c != "q_full_pre" else rows_all[c]["per_item_margin"][nm]) for c in KEY}} for nm in names_all}
rng = np.random.default_rng(20260924); six = [list(cells)[i] for i in sorted(rng.choice(NC, min(6, NC), replace=False))]
T["six_random_cells"] = {b: {"clean_gap": float(RAW[f"{b}|clean|seq_answer"] - RAW[f"{b}|clean|seq_swap"]), "greedy": {c: str(RAW[f"{b}|{c}|greedy"]) for c in ["clean", "donor"] + KEY}, "admitted": (b.split("|")[0] in admitted) if S2 else None,
                             "margins": {c: mg(b, c) for c in KEY}, "J_int_shift_s": {c: zsh(b, c, "int", "s") for c in KEY}, "J_ans_shift_s": {c: zsh(b, c, "ans", "s") for c in KEY},
                             "atoms_s_L59_first8": [tok.decode([int(v)]) for v in RAW[f"{b}|L59|atoms_s"][:8]], "atoms_qpre_last_L59_first8": [tok.decode([int(v)]) for v in RAW[f"{b}|L59|atoms_qpre"][-1, :8]]} for b in six}
if S2: T["admission"] = ADM; T["screen"] = SCREEN
json.dump(T, open(os.path.join(TAB, f"two_hop_{STAGE}_tables.json"), "w"), indent=1)

# ---- report
f2 = lambda x: f"{x:+.2f}"; f3 = lambda x: f"{x:+.3f}"; NI = len(names)
title = ("the question-turn ladder finished: answer plane, k-sweep, consumer clamp, current base (Amendment 6)" if not S2 else
         f"Stage 2: the Amendment 6 ladder on {len(names_all)} items over {len(set(CAT.values()))} relation types with admission gates, answer-smuggling screen and the repaired current-base row (Amendment 7)")
L = [f"# two_hop_organism · stage `{STAGE}` — {title}\n",
     f"Run `{META['run_id']}`, {META['n_forwards']} forwards, {META['elapsed_s']} s; Qwen3.6-27B, thinking off, **float32 residual from block {META['fp32_from']}** on every forward; {NC} cells ({len(names_all)} items × {len(META['carriers'])} carriers), "
     f"cluster = item; writes at blocks {SWAP_L[0]}–{SWAP_L[-1]} on `q_pre` (question turn, scoring position excluded; {nq} positions); consumer clamps at the scoring position only; sequence-log-prob endpoint (logsumexp over spellings). "
     f"Full-vocabulary dictionary {META['vocab_size']} atoms per block; restricted word dictionary {META['restricted_dictionary_size']} atoms. Design: `H3/design_specs/two_hop_organism.md` {AMEND}; battery `H3/scripts/two_hop_qsplit6.py`; the generated sections are from `two_hop_qsplit6_analysis.py`, the last section is hand-written.\n"]
if S2:
    L.append(f"**Primary set = the admitted items** ({len(admitted)}/{len(names_all)}; Amendment 7 §2: competence in all four carriers and the intermediate swap beating the answer swap at blocks 36–50): {', '.join(admitted)}. Every table below is on the admitted set unless labelled *all items*; §2b gives all items and the per-relation split. "
             f"Admission summary: gate (a) {sum(v['gate_a'] for v in ADM.values())}/{len(ADM)}, gate (b) {sum(v['gate_b'] for v in ADM.values())}/{len(ADM)}, both {sum(v['admitted'] for v in ADM.values())}/{len(ADM)} (in this stage's cells: {len(admitted)}/{len(names_all)}); admitted per relation type {dict(Counter(CAT[nm] for nm in admitted))}; decision conditions (≥ 12 admitted over ≥ 3 types, competence ≥ 0.9): {'met' if T['decision_conditions']['met'] else 'NOT met'}.\n")
L += ["## 1. Gates\n",
      f"- Gate 1 (rendering, `q` token-id equality recipient/donor, scoring position excluded, single-token answer words): asserted per cell in the battery ({NC} cells, `q_pre` length {nq} in every cell) — PASS.",
      f"- Gate 2 (competence, sequence endpoint): clean32 {comp_p['clean']:.2f}, donor32 {comp_p['donor']:.2f}" + (f" on the admitted set (all items: {comp_all['clean']:.2f} / {comp_all['donor']:.2f}; not a stop rule in Stage 2)" if S2 else "") + f" — **{'PASS' if T['gate2']['pass'] else 'FAIL'}**.",
      f"- Gate 3 (realized writes): fixed-target rows ρ ∈ [{min(rows[c]['rho'] for c in ft_rows):.4f}, {max(rows[c]['rho'] for c in ft_rows):.4f}], κ ≥ {min(rows[c]['kappa'] for c in ft_rows):.4f}, read-back max {g3['readback_max']:.1e}; consumer clamps ρ ∈ [{min(rows[c]['clamp_rho_min'] for c in cc_all):.4f}, {max(rows[c]['clamp_rho_max'] for c in cc_all):.4f}] over every block with a nonzero request (block 36's scoring position is still clean under every row, so its request is 0), κ ≥ {min(rows[c]['clamp_kappa_min'] for c in cc_all):.4f}; current base (`{CB_ROW}`) ρ {rows[CB_ROW]['rho']:.4f} κ {rows[CB_ROW]['kappa']:.4f}; ‖v_R‖ = ‖v_J‖ asserted per position; `_ccr` realized norm within {100*g3['ccr_norm_match_max_rel_dev']:.2f} % of its `_cc` match (bar 5 %) — **{'PASS' if g3['pass'] else 'FAIL'}**."]
if S2: L.append(f"- Gate 4 (reproduction: the 12 released-donor items' `q_full_pre` inside Stage 1's interval +11.19 [+10.00, +12.38], ≥ 10/12 > 0): {f2(T['gate4']['mean'])} nats, {T['gate4']['items_pos']}/{T['gate4']['n']} items > 0 — **{'PASS' if T['gate4']['pass'] else 'FAIL'}**.")
else: L.append(f"- Gate 4 (`q_full_pre` reproduces Amendment 5, +11.19 [+10.00, +12.38], ≥ 10/12 items > 0): {f2(T['gate4']['mean'])} nats [{f2(rows['q_full_pre']['margin_seq']['ci'][0])}, {f2(rows['q_full_pre']['margin_seq']['ci'][1])}], {T['gate4']['items_pos']}/{NI} items > 0 — **{'PASS' if T['gate4']['pass'] else 'FAIL'}**.")
L += [f"- Gate 5 (controls): `q_rand_pre` share {f3(T['gate5']['rand_share'])} (≤ 0.10), flips {T['gate5']['rand_flips']}/{len(sub_p)} (≤ 2 per 48 cells); `q_rem_rand_pre` share {f3(RR)} (≥ 0.80) — **{'PASS' if T['gate5']['pass'] else 'FAIL'}**.",
      f"- Gate 6 (pursuit positive control, reported): the k = 2 selection on `q_pre` contains the leading-space `intermediate` or `swap_to` atom in {100*T['gate6_positive_control']['L51_59']['either']:.1f} % of (block, position) cells at L51–59 (both: {100*T['gate6_positive_control']['L51_59']['both']:.1f} %), {100*T['gate6_positive_control']['all']['either']:.1f} % over blocks 36–62 (both {100*T['gate6_positive_control']['all']['both']:.1f} %); chance per pick 2/{META['vocab_size']} = {100*T['gate6_positive_control']['chance_per_pick']:.4f} %. P2 (majority at L51–59): {'held' if T['predictions']['P2_k2_majority_L51_59'] else 'not held'}.",
      f"- Gate 7 (restricted-dictionary NNLS KKT pass fraction ≥ 0.99 after the scipy fallback): {T['gate7']['kkt_pass_fraction']:.4f} of {T['gate7']['n']} (block, vector) fits — **{'PASS' if T['gate7']['pass'] else 'FAIL'}**. Early stops of the full-dictionary pursuit (no positive correlation left before k = {META['kmax']}): {T['early_stops']}."]
if S2: L.append(f"- Gate 8 (`q_rem_cbr_pre` construction check ‖h' − h_clean‖/‖Δh‖ ≤ 1.5 at every block and position, all items): max {T['gate8']['cons_check_max']:.3f}, mean {T['gate8']['cons_check_mean']:.3f} — **{'PASS' if T['gate8']['pass'] else 'FAIL'}**.")
L.append(f"- Collisions in the atom classification: {'; '.join(T['collisions']) if T['collisions'] else 'none'}.\n")
L += [f"## 2. Main table ({'admitted set; ' if S2 else ''}sequence endpoint; margin = log P(swap_answer) − log P(answer) minus clean32; item-clustered 95 % t-intervals; shares are ratios of item means)\n",
      "| row | margin (nats) | 95 % CI | items > 0 | share of `q_full_pre` | share of S_donor0 (bf16, quoted) | flips | ‖v‖/‖Δh‖ (L51–59) | J_NP int shift at s | J_NP int shift on `q_pre` | J_NP answer shift at s | block-63 re-entry (`q_pre`) | ρ / κ (write) | clamp ρ (dim) | ΔNLL max |",
      "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
for c in ROWS:
    r = rows[c]; m = r["margin_seq"]; vr = f"{r['v_over_dh_L51_59']:.3f}" if "v_over_dh_L51_59" in r else "—"
    L.append(f"| `{c}` | {f2(m['mean'])} | [{f2(m['ci'][0])}, {f2(m['ci'][1])}] | {m['n_pos']}/{m['n']} | {f3(r['share_of_q_full_pre'])} | {f3(r['share_of_S_donor0_bf16'])} | {r['flips_seq']}/{len(sub_p)} | {vr} | "
             f"{f2(r['J_int_shift_s']['mean'])} ({r['J_int_shift_s']['n_pos']}/{m['n']}) | {f2(r['J_int_shift_qpre']['mean'])} | {f2(r['J_ans_shift_s']['mean'])} | {f2(r['block63_reentry_qpre']['mean'])} | "
             + (f"{r['rho']:.3f} / {r['kappa']:.3f}" if "rho" in r else "—") + " | " + (f"{r['clamp_rho']:.3f} ({r['clamp_dim'][0]}–{r['clamp_dim'][1]})" if "clamp_rho" in r else "—") + f" | {r['dNLL_max']:+.4f} |")
L.append(f"\nReference rows: natural donor rendering (`donor32`) J_NP int shift at s {f2(np.mean(byitem(lambda b: zsh(b, 'donor', 'int', 's'))))}, answer shift at s {f2(np.mean(byitem(lambda b: zsh(b, 'donor', 'ans', 's'))))}, margin {f2(np.mean(byitem(lambda b: mg(b, 'donor'))))} nats. "
         f"Candidate-set (single-token) margins are in the tables JSON as a secondary continuity column only. Columns: ‖v‖/‖Δh‖ is the removed/installed component's norm over ‖Δh‖, mean over cells × blocks 51–59 of the per-block position means; J_NP shifts are (swap_to − intermediate) and (swap_answer − answer) readouts at L51–59 minus clean; block-63 re-entry is Δproj(a_swap) − Δproj(a_int) on the raw unit naming directions at the first free block, mean over `q_pre`, minus clean.\n")
if S2:
    L += ["### 2b. All items and the per-relation split\n", "| row | all items: margin | 95 % CI | items > 0 | share | flips |", "|---|---|---|---|---|---|"]
    for c in KEY: r = rows_all[c]; m = r["margin_seq"]; L.append(f"| `{c}` | {f2(m['mean'])} | [{f2(m['ci'][0])}, {f2(m['ci'][1])}] | {m['n_pos']}/{m['n']} | {f3(r['share_of_q_full_pre'])} | {r['flips_seq']}/{NC} |")
    L += ["\nPer relation type (shares of that type's own `q_full_pre`; *all items of the type* / *admitted items of the type*; screen = leave-one-out residual fraction of the ridge affine map W_U[answer] ≈ A·W_U[intermediate] + b, flagged if ≤ 0.5 and below the mismatched-pairs null):\n",
          "| relation | items (admitted) | donor | screen | full margin (all) | plane A | rem B | ans plane | ans rem | J25 rem | J25 rem + cc | current base (repaired) |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for cat, e in T["per_relation"].items():
        g = lambda c: (f"{e['shares_all'][c]:+.2f}" + (f" / {e['shares_admitted'][c]:+.2f}" if "shares_admitted" in e else " / —"))
        L.append(f"| {cat} | {e['n_items']} ({e['n_admitted']}) | {'constructed' if e['constructed_donor'] == [True] else ('released' if e['constructed_donor'] == [False] else 'mixed')} | {('%.2f' % e['screen_loo_residual']) if e['screen_loo_residual'] is not None else '—'}{' **flag**' if e['screen_flag'] else ''} | {f2(e['full_margin']['mean'])} ({e['full_margin']['n_pos']}/{e['full_margin']['n']}) | {g('q_plane_pre')} | {g('q_rem_pre')} | {g('q_ansplane_pre')} | {g('q_ansrem_pre')} | {g('q_J25rem_pre')} | {g('q_J25rem_pre_cc')} | {g(CB_ROW)} |")
    L += ["\nAdmission table (per item; margins in nats, carriers averaged; (b) = intermediate swap beats answer swap at blocks 36–50 on the tail positions):\n", "| item | relation | donor | competent carriers | `int_tail_mid` | `ans_tail_mid` | (b) | admitted |", "|---|---|---|---|---|---|---|---|"]
    for nm, v in ADM.items(): L.append(f"| {nm} | {v['category']} | {'constructed' if v['constructed_donor'] else 'released'} | {sum(v['competent_per_carrier'])}/4 | {f2(v['int_tail_mid'])} | {f2(v['ans_tail_mid'])} | {'yes' if v['gate_b'] else 'no'} | {'**yes**' if v['admitted'] else 'no'} |")
    L.append("")
L.append("## 3. share(k) curve and energy fractions\n")
L.append("| k | J_k installed | J_k complement | J_k complement + consumer clamp | + random-k clamp (control) | random-k complement (norm- and rank-matched) | ‖v_Jk‖²/‖Δh‖² (all blocks / L51–59) | N(0, Σ) random-k fraction (all / L51–59) | k/d | blocks with e_J > e_rand |")
L.append("|---|---|---|---|---|---|---|---|---|---|")
for k in KS:
    cv = curve[str(k)]; e = T["energy"][str(k)]
    cell = lambda nm: f"{f3(cv[nm]['share'])} ({f2(cv[nm]['margin'])} [{f2(cv[nm]['ci'][0])}, {f2(cv[nm]['ci'][1])}], {cv[nm]['n_pos']}/{NI})"
    L.append(f"| {k} | {cell('J_k')} | {cell('J_k_rem')} | {cell('J_k_rem_cc')} | {cell('J_k_rem_ccr')} | {cell('rand_k_rem')} | {e['e_J_all_blocks']:.3f} / {e['e_J_L51_59']:.3f} | {e['e_rand_sigma_all_blocks']:.3f} / {e['e_rand_sigma_L51_59']:.3f} | {e['k_over_d']:.4f} | {e['blocks_e_J_gt_e_rand']}/{len(SWAP_L)} |")
L.append(f"\nPlane rows for comparison: intermediate plane A = {f3(A)}, complement B = {f3(B)} (+ consumer clamp {f3(sh('q_rem_pre_cc'))}, random-plane clamp {f3(sh('q_rem_pre_ccr'))}); answer plane A_ans = {f3(Aa)}, complement B_ans = {f3(Ba)}; restricted-dictionary NNLS k = 25: installed {f3(sh('q_J25nn_pre'))}, complement {f3(sh('q_rem25nn_pre'))} (+ clamp {f3(sh('q_rem25nn_pre_cc'))}, control {f3(sh('q_rem25nn_pre_ccr'))}); "
         f"atom-type ablations at k = 25: answer-related atoms removed {f3(sh('q_rem25ans_pre'))}, intermediate-related atoms removed {f3(sh('q_rem25int_pre'))}. Energy reference: Σ_l from {T['energy']['n_cov_samples']} clean block outputs; 5 seeds.\n")
ce_ = T["clamp_effects"]; pcmp = T["plane_comparison"]
L.append("Consumer-clamp effects as item-level differences (un-clamped minus clamped, nats; item-clustered 95 % t-intervals; the random-k control's difference beside it):\n")
L.append("| complement row | clamp Δ (nats) | 95 % CI | items > 0 | as share of `q_full_pre` | as share of the row | random-k control Δ | 95 % CI |\n|---|---|---|---|---|---|---|---|")
for c in ce_: L.append(f"| `{c}` | {f2(ce_[c]['cc_delta']['mean'])} | [{f2(ce_[c]['cc_delta']['ci'][0])}, {f2(ce_[c]['cc_delta']['ci'][1])}] | {ce_[c]['cc_delta']['n_pos']}/{NI} | {f3(ce_[c]['cc_delta_share_of_full'])} | {f3(ce_[c]['cc_delta_share_of_row'])} | {f2(ce_[c]['ccr_delta']['mean'])} | [{f2(ce_[c]['ccr_delta']['ci'][0])}, {f2(ce_[c]['ccr_delta']['ci'][1])}] |")
cr = T["clamp_readouts_s"]
L.append("\nReadouts at the scoring position under the consumer clamps (J_NP, L51–59, minus clean; the clamp pins only the selected span, so these do not drop to 0 — **the `_cc` shares are upper bounds on any non-J route**, since a complete clamp of the J-readable content at s would remove at least as much):\n")
L.append(f"| complement row | int readout at s: un-clamped → `_cc` (`_ccr`) | answer readout at s: un-clamped → `_cc` (`_ccr`) |\n|---|---|---|")
for c in [k for k in cr if k != "full"]: L.append(f"| `{c}` | {f2(cr[c]['int_unclamped'])} → {f2(cr[c]['int_cc'])} ({f2(cr[c]['int_ccr'])}) | {f2(cr[c]['ans_unclamped'])} → {f2(cr[c]['ans_cc'])} ({f2(cr[c]['ans_ccr'])}) |")
L.append(f"| `q_full_pre` (reference) | {f2(cr['full']['int'])} | {f2(cr['full']['ans'])} |")
L.append(f"\nPlanes at equal dimension: answer plane minus intermediate plane {f2(pcmp['ans_minus_int_plane']['mean'])} nats [{f2(pcmp['ans_minus_int_plane']['ci'][0])}, {f2(pcmp['ans_minus_int_plane']['ci'][1])}], {pcmp['ans_minus_int_plane']['n_pos']}/{NI} items > 0, at ‖v‖/‖Δh‖ {pcmp['v_over_dh_ans_plane_L51_59']:.3f} vs {pcmp['v_over_dh_int_plane_L51_59']:.3f}. "
         f"Additivity S = m(full) − m(part) − m(complement): intermediate plane {f2(pcmp['additivity_plane']['mean'])} [{f2(pcmp['additivity_plane']['ci'][0])}, {f2(pcmp['additivity_plane']['ci'][1])}]; answer plane {f2(pcmp['additivity_ans_plane']['mean'])} [{f2(pcmp['additivity_ans_plane']['ci'][0])}, {f2(pcmp['additivity_ans_plane']['ci'][1])}]; J_25 {f2(pcmp['additivity_J25']['mean'])} [{f2(pcmp['additivity_J25']['ci'][0])}, {f2(pcmp['additivity_J25']['ci'][1])}] (reported, not a partition).\n")
cbt = T["current_base"]; fbs = f"L{cbt['first_block_weighted_ge_0.5']}" if cbt['first_block_weighted_ge_0.5'] is not None else "none"; fbp = f"first block ≥ 0.5 at {fbs}" if cbt['first_block_weighted_ge_0.5'] is not None else "no block reaches 0.5"
cb_note = ("Current base († construction failed, see §8.3 — the registered additive form double-counts the accumulated block delta; the numbers are reported as run and **not read**)" if not S2 else
           f"Current base, repaired form (`q_rem_cbr_pre`: complement coordinates replaced by the donor's, plane free; construction check max {rows_all[CB_ROW]['cons_check_max']:.3f})")
L.append(f"{cb_note}: `{CB_ROW}` {f3(cbt['share'])} vs `q_rem_pre` {f3(B)} ({rows[CB_ROW]['flips_seq']} vs {rows['q_rem_pre']['flips_seq']} flips; J_NP int readout on `q_pre` {f2(rows[CB_ROW]['J_int_shift_qpre']['mean'])} vs {f2(rows['q_rem_pre']['J_int_shift_qpre']['mean'])} pinned and {f2(rows['q_full_pre']['J_int_shift_qpre']['mean'])} full; at s {f2(rows[CB_ROW]['J_int_shift_s']['mean'])} vs {f2(rows['q_rem_pre']['J_int_shift_s']['mean'])} and {f2(rows['q_full_pre']['J_int_shift_s']['mean'])}). "
         f"The free plane coordinate inside the band, Q_lᵀ(h' − h), projected on the full donor's plane coordinate (norm-weighted over `q_pre`, mean over cells): {fbp}, {cbt['reentry_fraction_L51_59']:.2f} over L51–59, {cbt['reentry_fraction_L62']:.2f} at block 62; the coordinate's norm relative to the donor's peaks at {cbt['plane_norm_ratio_max']:.2f}× and is {cbt['plane_norm_ratio_L62']:.2f}× at block 62. "
         f"Per block (weighted fraction): " + ", ".join(f"L{l} {cbt['reentry_fraction_by_block_weighted'][str(l)]:.2f}" for l in SWAP_L[::3] + [SWAP_L[-1]]) + ".\n")
L.append("## 4. Atom-type breakdown (norm shares ‖v_C‖/‖v_Jk‖, mean over cells × blocks × positions; atoms are not orthogonal, so the shares are components, not a partition)\n")
L.append("| k | `q_pre` L51–59: answer / intermediate / other | `q_pre` all blocks | scoring position L51–59 | scoring position all blocks | count fraction (`q_pre`, L51–59) | |coef|-weighted fraction |")
L.append("|---|---|---|---|---|---|---|")
for k in KS:
    a = atoms[str(k)]; g = lambda d: " / ".join(f"{d[w]:.3f}" for w in ("answer", "intermediate", "other"))
    L.append(f"| {k} | {g(a['norm_share_qpre_L51_59'])} | {g(a['norm_share_qpre_all'])} | {g(a['norm_share_s_L51_59'])} | {g(a['norm_share_s_all'])} | {g(a['count_fraction_qpre_L51_59'])} | {g(a['coef_weighted_fraction_qpre_L51_59'])} |")
nnshare = " / ".join(f"{atoms['nn25']['norm_share_qpre_L51_59'][w]:.3f}" for w in ("answer", "intermediate", "other"))
L.append(f"| NNLS 25 | {nnshare} | — | — | — | — | — |")
L.append("\nMost frequent atoms among the first 25 selected on `q_pre` at L51–59 (over the primary set's cells), by class:\n")
for w in ("intermediate", "answer", "other"): L.append(f"- **{w}**: " + ", ".join(f"{s} ×{n_}" for s, n_ in T["top_atoms_k25_L51_59"][w][:25]))
ck = T["content_check"]
L.append(f"\n**Content check at the two informative positions** (defined after seeing the six seeded cells, researcher note 2026-09-24; top-25 pursuit atoms, L51–59, mean over cells; 'translations included' adds non-Latin atoms whose nearest Latin-script unembedding neighbour is one of the item's four words or their aliases). "
         f"Last `q_pre` position: {100*ck['last_qpre']['frozen']:.0f} % of atoms intermediate/answer-related by the frozen classes, {100*ck['last_qpre']['translated']:.0f} % with translations ({100*ck['last_qpre']['frozen_w']:.0f} % / {100*ck['last_qpre']['translated_w']:.0f} % |coef|-weighted). "
         f"Scoring position s (pursuit on the donor's Δh_s): {100*ck['s']['frozen']:.0f} % / {100*ck['s']['translated']:.0f} % ({100*ck['s']['frozen_w']:.0f} % / {100*ck['s']['translated_w']:.0f} % weighted). "
         f"Broad level, 'associated' (any atom among the top-100 unembedding neighbours of the four words; catches associates such as the cue city, the river, the leader, and also unrelated capitals): last `q_pre` {100*ck['last_qpre']['associated']:.0f} % ({100*ck['last_qpre']['associated_w']:.0f} % weighted), s {100*ck['s']['associated']:.0f} % ({100*ck['s']['associated_w']:.0f} % weighted). "
         f"Pooled over every `q_pre` position (the Phase B statistic of §1): {100*ck['pooled_reference_frozen_all_qpre_positions_L51_59']:.1f} %. Translation atoms found: " + ", ".join(f"{s} ×{n_}" for s, n_ in ck["top_translation_atoms"][:20]) + ". Associated atoms found: " + ", ".join(f"{s} ×{n_}" for s, n_ in ck["top_associated_atoms"][:20]) + ".\n")
L.append("Per-item split of the J_25 part (norm shares answer / intermediate / other; `q_pre` L51–59 mean, and at s):\n")
L.append("| item | `q_pre`: answer / intermediate / other | s: answer / intermediate / other |\n|---|---|---|")
for nm in names_all:
    p = T["per_item_J25_split"][nm]; L.append(f"| {nm} | {p['qpre']['answer']:.2f} / {p['qpre']['intermediate']:.2f} / {p['qpre']['other']:.2f} | {p['s']['answer']:.2f} / {p['s']['intermediate']:.2f} / {p['s']['other']:.2f} |")
L.append("\n## 5. Per-item shares of `q_full_pre` (all items; first column: the full margin in nats)\n")
L.append("| item | relation | donor | adm. | full | plane A | rem B | ans-plane | ans-rem | J25 rem | J25 rem + cc | + ccr | rand25 rem | current base | NNLS25 rem | NNLS25 rem + cc |")
L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for nm in names_all:
    p = T["per_item"][nm]; L.append(f"| {nm} | {p['category']} | {'c' if p['constructed_donor'] else 'r'} | {('yes' if p['admitted'] else 'no') if S2 else '—'} | {f2(p['q_full_pre'])} | " + " | ".join(f2(p[c]) for c in KEY[1:]) + " |")
L.append("\n## 6. Six seeded-random cells (seed 20260924; numbers generated, reading hand-written in §8)\n")
for b, d in T["six_random_cells"].items():
    L.append(f"- **{b}**{'' if not S2 else (' (admitted)' if d['admitted'] else ' (not admitted)')} (clean gap {d['clean_gap']:.1f} nats; greedy clean `{d['greedy']['clean']}`, donor `{d['greedy']['donor']}`): margins " + ", ".join(f"{c} {f2(d['margins'][c])}" for c in KEY)
             + f"; greedy under J25 rem `{d['greedy']['q_J25rem_pre']}`, + cc `{d['greedy']['q_J25rem_pre_cc']}`; J_NP int shift at s under J25 rem {f2(d['J_int_shift_s']['q_J25rem_pre'])} → + cc {f2(d['J_int_shift_s']['q_J25rem_pre_cc'])}; answer shift {f2(d['J_ans_shift_s']['q_J25rem_pre'])} → {f2(d['J_ans_shift_s']['q_J25rem_pre_cc'])}; "
             f"pursuit on the donor's Δh at s, L59: {d['atoms_s_L59_first8']}; on the last `q_pre` position: {d['atoms_qpre_last_L59_first8']}.")
D = T["decision"]; Pp = T["predictions"]
L.append(f"\n## 7. Decision rule (Amendment 6 §6{'; applied to the admitted set per Amendment 7 §5' if S2 else ''}) and predictions\n")
L.append(f"Consumer-clamped complement share at k = 25: **{f3(D['consumer_clamped_complement_share_k25'])}** (un-clamped {f3(D['unclamped_share_k25'])}; random-k clamp control {f3(D['control_ccr_share_k25'])}, {'within' if D['ccr_within_unclamped_interval'] else 'outside'} the un-clamped row's interval); gates 1–5 {'pass' if D['gates_1_5_pass'] else 'FAIL'} → **{D['reading']}**. "
         f"Qualifier: answer-related atoms carry {100*atoms['25']['norm_share_qpre_L51_59']['answer']:.0f} % of the J_25 part's norm on `q_pre` at L51–59 ({'most' if D['qualifier_answer_atoms_carry_most_of_J25'] else 'not most'}); answer-plane removal leaves B_ans = {f3(Ba)} ({'kills most of the effect' if D['qualifier_answer_plane_removal_kills_most'] else 'does not kill most of the effect'}). "
         f"**Leading alternative, stated beside the rule:** the answer plane alone carries {f3(Aa)} against {f3(A)} for the intermediate plane at equal dimension ({pcmp['ans_minus_int_plane']['n_pos']}/{NI} items), so \"the answer is already computed and J-readable at the question turn\" is the reading to beat; the `_cc` shares are upper bounds on any non-J route (the clamp is partial, §3), and the J_k part is strongly privileged per dimension (J_25 complement {f3(un25)} vs random-25 complement {f3(sh('q_rand25rem_pre'))}).\n")
L.append("| prediction (Amendment 6) | held? | values |\n|---|---|---|")
L.append(f"| P1 gates 1–5 pass | {Pp['P1_gates_1_5']} | — |")
L.append(f"| P2 k = 2 selection contains intermediate/swap_to on a majority of `q_pre` cells at L51–59 | {Pp['P2_k2_majority_L51_59']} | {100*Pp['P2_value']:.1f} % |")
L.append(f"| P3 answer plane: B_ans ≤ 0.5 while B ≈ 0.78 (qualifier applies) | {Pp['P3_B_ans_le_0.5_and_B_stays']} | A_ans {f3(Aa)}, B_ans {f3(Ba)}, B {f3(B)} |")
L.append(f"| P4 share(J_k rem) non-increasing in k; random-k rem ≥ 0.80 at every k | {Pp['P4_Jrem_nonincreasing']} / {Pp['P4_rand_rem_ge_0.8_all_k']} | J rem {[round(x, 3) for x in Jrem]}; rand rem {[round(x, 3) for x in Rrem]} |")
L.append(f"| P5 `_cc` lowers each complement share; `_ccr` within the un-clamped interval | {sum(Pp['P5_cc_lower_than_unclamped'].values())}/{len(Pp['P5_cc_lower_than_unclamped'])} lower; {sum(Pp['P5_ccr_within_unclamped_interval'].values())}/{len(Pp['P5_ccr_within_unclamped_interval'])} within | " + "; ".join(f"{c}: cc {f3(sh(c + '_cc'))} vs {f3(sh(c))} (ccr {f3(sh(c + '_ccr'))})" for c in Pp['P5_cc_lower_than_unclamped']) + " |")
L.append(f"| P6 current base ≥ B − 0.10; plane rebuilt ≥ 0.5 by block 62? | {Pp['P6_cb_share_ok']} / {Pp['P6_plane_rebuilt']} (≥ 0.5 somewhere in the band: {T['current_base']['plane_rebuilt_ge_0.5_anywhere_in_band']}) | `{CB_ROW}` {f3(sh(CB_ROW))}, B {f3(B)}, weighted re-entry fraction at L62 {T['current_base']['reentry_fraction_L62']:.2f}, first block ≥ 0.5: {fbs} |")
L.append(f"| P7 e_J > N(0, Σ) random-k fraction at every k (block means) | {Pp['P7_eJ_gt_erand_every_k']} | blocks holding per k: {Pp['P7_blocks_holding']} |")
if S2:
    P7 = T["predictions_A7"]
    L.append("\n| prediction (Amendment 7) | held? | values |\n|---|---|---|")
    L.append(f"| P1 gates 1–3, 5–8 pass; gate 4 reproduces | {P7['P1_gates']} | — |")
    L.append(f"| P2 ≥ 3 relation types with ≥ 3 admitted items | {P7['P2_ge3_types_with_ge3_items']} | {P7['P2_admitted_per_type']} |")
    L.append(f"| P3 generality: J25 rem ∈ [0.45, 0.75]; J25 rem + cc ∈ [0.3, 0.6]; rem + cc ≥ rem − 0.10; A_ans > A | {P7['P3_J25rem_in_[0.45,0.75]']} / {P7['P3_J25rem_cc_in_[0.3,0.6]']} / {P7['P3_rem_cc_ge_rem_minus_0.10']} / {P7['P3_Aans_gt_A']} | {f3(un25)}, {f3(cc25)}, {f3(sh('q_rem_pre_cc'))} vs {f3(B)}, {f3(Aa)} vs {f3(A)} |")
    L.append(f"| P4 flagged relations show larger A_ans, smaller B_ans | {'no relation flagged' if not any(e['screen_flag'] for e in T['per_relation'].values()) else 'see §2b'} | screen residuals {({c: (round(e['screen_loo_residual'], 2) if e['screen_loo_residual'] is not None else None) for c, e in T['per_relation'].items()})} |")
    L.append(f"| P5 repaired current base ≥ B − 0.10, construction check ≈ 1; plane rebuilt ≥ 0.5 by block 62? | {P7['P5_cbr_share_ok']} / {P7['P5_plane_rebuilt_by_L62']} | share {f3(sh(CB_ROW))}, check max {P7['P5_cons_check_max']:.3f}, weighted re-entry at L62 {T['current_base']['reentry_fraction_L62']:.2f} |")
L.append("\nCaveats carried forward from Amendment 5: each row is a fixed state trajectory over blocks 36–62 at `q_pre` (the rows are not a partition of one computation); `q_rem_pre` pins a two-token plane; the J_k rows pin the LS projection onto k greedy atoms of one dictionary (J_NP folded directions), so \"J-readable content\" here means \"content in the span of those atoms\"; the atom classes are string-mechanical (translations and related tokens in other scripts fall in *other*); shares are ratios of item means.\n")
L.append("## 8. Interpretation, licensed / not licensed, next decision\n")
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
from matplotlib.ticker import NullFormatter, FixedFormatter
fig, axs = plt.subplots(1, 3, figsize=(5.5, 2.1), gridspec_kw={"width_ratios": [1.5, 1.1, 1.0]})
ax = axs[0]; MAIN = ["q_full_pre", "q_plane_pre", "q_rem_pre", "q_ansplane_pre", "q_ansrem_pre", "q_J25rem_pre", "q_J25rem_pre_cc", "q_J25rem_pre_ccr", "q_rand25rem_pre", CB_ROW]
lab = {"q_full_pre": "full", "q_plane_pre": "plane", "q_rem_pre": "rem", "q_ansplane_pre": "ans plane", "q_ansrem_pre": "ans rem", "q_J25rem_pre": "J25 rem", "q_J25rem_pre_cc": "J25 rem +clamp", "q_J25rem_pre_ccr": "J25 rem +rand", "q_rand25rem_pre": "rand25 rem", "q_rem_cb_pre": "rem cur. base†", "q_rem_cbr_pre": "rem cur. base"}
colr = ["#4c4c4c", "#1f77b4", "#d62728", "#6baed6", "#fb6a4a", "#a50f15", "#67000d", "#fcae91", "#bdbdbd", "#e6550d"]
ms = [rows[c]["margin_seq"]["mean"] for c in MAIN]; lo = [rows[c]["margin_seq"]["mean"] - rows[c]["margin_seq"]["ci"][0] for c in MAIN]; hi = [rows[c]["margin_seq"]["ci"][1] - rows[c]["margin_seq"]["mean"] for c in MAIN]
lo = [0 if np.isnan(x) else x for x in lo]; hi = [0 if np.isnan(x) else x for x in hi]
ax.bar(range(len(MAIN)), ms, yerr=[lo, hi], color=colr, capsize=1.5, width=0.7)
for i, c in enumerate(MAIN): ax.scatter(np.full(len(names), i) + np.linspace(-0.2, 0.2, len(names)), [rows[c]["per_item_margin"][nm] for nm in names], s=3, color="k", alpha=0.5, zorder=3)
ax.axhline(0, color="k", lw=0.5); ax.set_xticks(range(len(MAIN))); ax.set_xticklabels([lab[c] for c in MAIN], fontsize=4.5, rotation=60, ha="right", rotation_mode="anchor"); ax.set_ylabel("Δ answer margin (nats)"); ax.set_title(f"(a) rows, blocks 36–62 on q_pre ({'admitted, n=' + str(len(names)) if S2 else 'n=12'})", fontsize=7)
ax = axs[1]
for nm, st_, cl in (("J_k_rem", "-o", "#d62728"), ("J_k_rem_cc", "-s", "#67000d"), ("J_k_rem_ccr", "--^", "#fcae91"), ("rand_k_rem", ":d", "#7f7f7f"), ("J_k", "-x", "#1f77b4")):
    ax.plot(KS, [curve[str(k)][nm]["share"] for k in KS], st_, color=cl, ms=3, lw=1, label={"J_k_rem": "J_k complement", "J_k_rem_cc": "+ consumer clamp", "J_k_rem_ccr": "+ random-k clamp", "rand_k_rem": "random-k complement", "J_k": "J_k installed"}[nm])
ax.set_xscale("log"); ax.set_xticks(KS); ax.xaxis.set_major_formatter(FixedFormatter([str(k) for k in KS])); ax.xaxis.set_minor_formatter(NullFormatter()); ax.set_ylim(-0.22, 1.12); ax.axhline(0.5, color="k", lw=0.4, ls=":"); ax.axhline(0.2, color="k", lw=0.4, ls=":")
ax.set_xlabel("k atoms"); ax.set_ylabel("share of q_full_pre"); ax.set_title("(b) share(k)", fontsize=7); ax.legend(fontsize=4.2, frameon=False, loc="center", bbox_to_anchor=(0.55, 0.13), handlelength=1.6)
ax = axs[2]; w_ = 0.35; x = np.arange(len(KS))
for j, (w, cl) in enumerate((("answer", "#fb6a4a"), ("intermediate", "#1f77b4"), ("other", "#bdbdbd"))):
    ax.bar(x - w_ / 2, [atoms[str(k)]["norm_share_qpre_L51_59"][w] for k in KS], w_, bottom=[sum(atoms[str(k)]["norm_share_qpre_L51_59"][v] for v in ("answer", "intermediate", "other")[:j]) for k in KS], color=cl, label=w)
    ax.bar(x + w_ / 2, [atoms[str(k)]["norm_share_s_L51_59"][w] for k in KS], w_, bottom=[sum(atoms[str(k)]["norm_share_s_L51_59"][v] for v in ("answer", "intermediate", "other")[:j]) for k in KS], color=cl, alpha=0.55)
ax.set_xticks(x); ax.set_xticklabels([f"{k}" for k in KS]); ax.set_ylim(0, 1.4); ax.set_xlabel("k (left q_pre, right scoring pos.)"); ax.set_ylabel("norm share of v_Jk (components)"); ax.set_title("(c) atom types, L51–59", fontsize=7); ax.legend(fontsize=4.2, frameon=False, loc="upper left", ncol=3, columnspacing=0.8, handlelength=1.2)
fig.tight_layout(); fig.savefig(os.path.join(FIG, f"h3_{STAGE}.png"), dpi=200); fig.savefig(os.path.join(FIG, f"h3_{STAGE}.pdf"))
print(json.dumps({k: T[k] for k in ("competence_clean32_seq", "competence_donor32_seq", "gate3", "gate4", "gate5", "gate6_positive_control", "gate7", "decision", "predictions", "current_base") if k in T}, indent=1, default=str))
if S2: print(json.dumps({k: T[k] for k in ("gate8", "decision_conditions", "predictions_A7")}, indent=1, default=str))
for c in ROWS: print(f"  [{c:20s}] seq margin {rows[c]['margin_seq']['mean']:+6.2f} [{rows[c]['margin_seq']['ci'][0]:+6.2f},{rows[c]['margin_seq']['ci'][1]:+6.2f}] ({rows[c]['margin_seq']['n_pos']}/{rows[c]['margin_seq']['n']}) share {rows[c]['share_of_q_full_pre']:+.3f} flips {rows[c]['flips_seq']:2d} | J int s {rows[c]['J_int_shift_s']['mean']:+.2f} q {rows[c]['J_int_shift_qpre']['mean']:+.2f} ans s {rows[c]['J_ans_shift_s']['mean']:+.2f} | c63 {rows[c]['block63_reentry_qpre']['mean']:+.2f}")
