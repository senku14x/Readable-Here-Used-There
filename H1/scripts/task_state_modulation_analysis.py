"""Analysis for H1 task-state modulation (single scoring pass per stage).

Usage: task_state_modulation_analysis.py [pilot|evaluate]
Estimands (H1.4): C_k(q,a) = m_k(swap36) − m_k(noswap); A_k = C_k(0,M) − C_k(0,N);
ΔC_{k,M} = C_k(q_M,M) − C_k(0,M); ΔC_{k,N} = C_k(q_N,N) − C_k(0,N); I_k = ½[−ΔC_{k,M} + ΔC_{k,N}].
Instruments: J_NP (bf16 path) at windows L48–50 and L51–59 (co-primary, Holm across the two), RESID_P pair
axis, LOGITS. Companions: the move's effect on the no-swap readout (content installation), realized-write
statistics, damage, the control panel at the same signed α_t, dose rows, a random-readout-column floor, and
the rank-1-anywhere hit statistic for X and Y.
Writes H1/results/task_state_modulation_<stage>.md, _tables.json, figures.
"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "common", "scripts"))
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import registry as R
import stats as S

STAGE = sys.argv[1] if len(sys.argv) > 1 else "pilot"
OUT = os.path.join(R.out_dir("H1", "outputs"), "task_state_modulation")
RES = os.path.join(R.out_dir("H1", "results")); FIG = os.path.join(RES, "figures"); QUAL = os.path.join(RES, "qualitative")
os.makedirs(FIG, exist_ok=True); os.makedirs(QUAL, exist_ok=True)
META = json.load(open(os.path.join(OUT, f"meta_{STAGE}.json"))); Z = np.load(os.path.join(OUT, f"raw_{STAGE}.npz"))
FR = json.load(open(os.path.join(OUT, "fit_report.json")))
COLS = META["columns"]; CIX = {w: i for i, w in enumerate(COLS)}; NRAND = len(META["random_column_ids"])
PAIRS = [tuple(p) for p in META["pairs"]]; ARMS = META["arms"]; CARRIERS = META["carriers"]; PANEL = META["panel"]
DOSES = META["doses"] if STAGE != "orthopanel" else []
NATIVE = [f"native_{k}" for k in META.get("native_rows", [])]
PANEL_COS = META.get("panel_cos_ghat", {})
WINDOWS = {"L48-50": [48, 49, 50], "L51-59": list(range(51, 60))}
AR = {"maintain": "M", "mention": "N"}
RANK_LAYERS = META["rank_layers"]


def m_J(tag, X, Y, layers):
    z = Z[f"{tag}|z"].astype(np.float32)[layers]
    return float((z[:, :, CIX[Y]] - z[:, :, CIX[X]]).mean())


def m_p(tag, layers):
    return float(Z[f"{tag}|p_pair"][layers].mean()) if f"{tag}|p_pair" in Z else np.nan


def m_lp(tag):
    return float(Z[f"{tag}|lp_margin"].mean())


def rand_cols(tag, layers):
    z = Z[f"{tag}|z"].astype(np.float32)[layers]
    return z[:, :, len(COLS):].mean((0, 1))          # [NRAND] mean over window × positions


def per_pair(fn):
    return np.array([np.mean([fn(ck, X, Y) for ck in CARRIERS for (X, Y) in ((a, b), (b, a))]) for (a, b) in PAIRS])


INST = {}
for wname, win in WINDOWS.items():
    INST[f"J_NP|{wname}"] = (lambda t, X, Y, w=win: m_J(t, X, Y, w))
    INST[f"RESID_P|{wname}"] = (lambda t, X, Y, w=win: m_p(t, w))
INST["LOGITS"] = (lambda t, X, Y: m_lp(t))

tables = {"fit": {k: FR[k] for k in ("norm_G", "split_half_cos", "split_half_shared_energy", "cos_panel_ghat", "top_singular_values")},
          "cells": META["cells"], "pairs": PAIRS, "excluded": META["excluded"]}


def C(mf, ck, X, Y, arm, cond):
    return mf(f"{ck}|{arm}|{X}->{Y}|{cond}|swap36", X, Y) - mf(f"{ck}|{arm}|{X}->{Y}|{cond}|noswap", X, Y)


for key, mf in INST.items():
    T = {}
    A = per_pair(lambda ck, X, Y: C(mf, ck, X, Y, "maintain", "clean") - C(mf, ck, X, Y, "mention", "clean"))
    T["A"] = S.cluster_t(A)
    for arm in ARMS:
        T[f"C_clean_{AR[arm]}"] = S.cluster_t(per_pair(lambda ck, X, Y, a=arm: C(mf, ck, X, Y, a, "clean")))
    conds = ["g"] + [f"dose{s}" for s in DOSES] + PANEL + NATIVE
    for cond in conds:
        dM = per_pair(lambda ck, X, Y, c=cond: C(mf, ck, X, Y, "maintain", c) - C(mf, ck, X, Y, "maintain", "clean"))
        if cond.startswith("dose"):
            T[f"dC_M|{cond}"] = S.cluster_t(dM); continue
        dN = per_pair(lambda ck, X, Y, c=cond: C(mf, ck, X, Y, "mention", c) - C(mf, ck, X, Y, "mention", "clean"))
        I = 0.5 * (-dM + dN)
        T[f"dC_M|{cond}"] = S.cluster_t(dM); T[f"dC_N|{cond}"] = S.cluster_t(dN); T[f"I|{cond}"] = S.cluster_t(I)
        T[f"I_over_A|{cond}"] = S.ratio_of_means(I, A)
        # content installation: the move's effect on the no-swap readout, both arms
        T[f"noswap_shift_M|{cond}"] = S.cluster_t(per_pair(lambda ck, X, Y, c=cond: mf(f"{ck}|maintain|{X}->{Y}|{c}|noswap", X, Y) - mf(f"{ck}|maintain|{X}->{Y}|clean|noswap", X, Y)))
        T[f"noswap_shift_N|{cond}"] = S.cluster_t(per_pair(lambda ck, X, Y, c=cond: mf(f"{ck}|mention|{X}->{Y}|{c}|noswap", X, Y) - mf(f"{ck}|mention|{X}->{Y}|clean|noswap", X, Y)))
    # panel summary
    panelI = {c: T[f"I|{c}"]["mean"] for c in PANEL}
    T["panel_summary"] = {"I_g": T["I|g"]["mean"], "panel_I_sorted": sorted(panelI.values()), "panel_max_abs": max(abs(v) for v in panelI.values()),
                          "panel_argmax": max(panelI, key=lambda c: abs(panelI[c])),
                          "panel_n_ge_g": int(sum(abs(v) >= abs(T["I|g"]["mean"]) for v in panelI.values())),
                          "panel_n_ge_half_g": int(sum(abs(v) >= 0.5 * abs(T["I|g"]["mean"]) for v in panelI.values())),
                          "panel_reciprocal": [c for c in PANEL if T[f"dC_M|{c}"]["mean"] < 0 and T[f"dC_N|{c}"]["mean"] > 0],
                          "panel_reciprocal_3of3": [c for c in PANEL if T[f"dC_M|{c}"]["signs_neg"] == T[f"dC_M|{c}"]["n"] and T[f"dC_N|{c}"]["signs_pos"] == T[f"dC_N|{c}"]["n"]],
                          "registered_bar_max_lt_half_g": bool(max(abs(v) for v in panelI.values()) < 0.5 * abs(T["I|g"]["mean"]))}
    tables[key] = T

# Holm across the two co-primary windows on I (J_NP)
pvals = [S.paired_p(tables[f"J_NP|{w}"]["I|g"]["per_cluster"]) for w in WINDOWS]
tables["holm_I_g_J_NP"] = dict(zip(list(WINDOWS), S.holm(pvals))); tables["raw_p_I_g_J_NP"] = dict(zip(list(WINDOWS), pvals))

# realized writes and damage
rw = {c: {k: [] for k in ("rho", "kappa", "req_norm")} for c in ["g"] + [f"dose{s}" for s in DOSES] + PANEL + NATIVE}
dmg = {}
for ck in CARRIERS:
    for (a, b) in PAIRS:
        for (X, Y) in ((a, b), (b, a)):
            for arm in ARMS:
                t0 = f"{ck}|{arm}|{X}->{Y}|clean|noswap"
                for c in rw:
                    for ph in ("noswap", "swap36"):
                        t = f"{ck}|{arm}|{X}->{Y}|{c}|{ph}"
                        if f"{t}|w_rho" not in Z:
                            continue
                        for k in rw[c]:
                            rw[c][k].append(float(Z[f"{t}|w_{k}"]))
                        dmg.setdefault(c, []).append({"dnll": float(Z[f"{t}|nll"] - Z[f"{t0}|nll"]), "top1": float((Z[f"{t}|top1"] == Z[f"{t0}|top1"]).mean())})
tables["realized_writes"] = {c: {"rho_min": min(v["rho"]), "rho_max": max(v["rho"]), "rho_median": float(np.median(v["rho"])), "kappa_min": min(v["kappa"]), "kappa_median": float(np.median(v["kappa"])),
                                 "req_norm_median": float(np.median(v["req_norm"])), "n": len(v["rho"]), "gate_pass": bool(min(v["rho"]) >= 0.9 and max(v["rho"]) <= 1.1 and min(v["kappa"]) >= 0.99)} for c, v in rw.items() if v["rho"]}
tables["damage"] = {c: {"dNLL_mean": float(np.mean([x["dnll"] for x in v])), "dNLL_max": float(np.max([x["dnll"] for x in v])), "top1_min": float(np.min([x["top1"] for x in v]))} for c, v in dmg.items()}
# levels and alpha
tables["levels"] = {t: META["cells"][t] for t in list(META["cells"])[:6]}
tables["alpha_summary"] = {"alpha_mean_M": float(np.mean([v["alpha_mean"] for k, v in META["cells"].items() if "|maintain|" in k])), "alpha_mean_N": float(np.mean([v["alpha_mean"] for k, v in META["cells"].items() if "|mention|" in k])),
                           "L_gap_mean": float(np.mean([abs(v["L_star"] - v["L_own"]) for v in META["cells"].values()]))}

# random-readout-column floor: the ĝ move's interaction on random columns (donor-column analog: z_col(swap)−z_col(noswap) change under the move)
for wname, win in WINDOWS.items():
    def Ccol(ck, X, Y, arm, cond):
        return rand_cols(f"{ck}|{arm}|{X}->{Y}|{cond}|swap36", win) - rand_cols(f"{ck}|{arm}|{X}->{Y}|{cond}|noswap", win)
    Icol = []
    for ck in CARRIERS:
        for (a, b) in PAIRS:
            for (X, Y) in ((a, b), (b, a)):
                dM = Ccol(ck, X, Y, "maintain", "g") - Ccol(ck, X, Y, "maintain", "clean"); dN = Ccol(ck, X, Y, "mention", "g") - Ccol(ck, X, Y, "mention", "clean")
                Icol.append(0.5 * (-dM + dN))
    Icol = np.mean(Icol, 0)                                   # [NRAND]: mean interaction per random column
    Ig = tables[f"J_NP|{wname}"]["I|g"]["mean"]
    tables[f"random_column_floor|{wname}"] = {"I_g_target_pair": Ig, "random_col_abs_p95": float(np.percentile(np.abs(Icol), 95)), "random_col_abs_max": float(np.abs(Icol).max()),
                                             "percentile_of_target": float((np.abs(Icol) < abs(Ig)).mean()), "note": "target is a pair margin (2 columns); random columns are single columns; comparison is indicative"}

# hit statistic (rank-1 anywhere over L24-59) for X and Y under each condition
hits = {}
for cond in ["clean", "g"] + PANEL[:2] + NATIVE:
    for arm in ARMS:
        for ph in ("noswap", "swap36"):
            hx, hy = [], []
            for ck in CARRIERS:
                for (a, b) in PAIRS:
                    for (X, Y) in ((a, b), (b, a)):
                        rk = Z[f"{ck}|{arm}|{X}->{Y}|{cond}|{ph}|rank_XY"]
                        hx.append(rk[:, :, 0].min() == 1); hy.append(rk[:, :, 1].min() == 1)
            hits[f"{cond}|{arm}|{ph}"] = {"X_rank1_rate": float(np.mean(hx)), "Y_rank1_rate": float(np.mean(hy)), "n_cells": len(hx)}
tables["hit_rank1_anywhere_L24_59"] = hits
json.dump(tables, open(os.path.join(RES, f"task_state_modulation_{STAGE}_tables.json"), "w"), indent=1, default=float)

# ------------------------------------------------------------------ figures
fig, axes = plt.subplots(1, 3, figsize=(16, 4.2))
for ax, key in zip(axes, ("J_NP|L48-50", "J_NP|L51-59", "RESID_P|L48-50")):
    T = tables[key]
    names = ["g"] + PANEL + NATIVE; vals = [T[f"I|{c}"]["mean"] for c in names]; lo = [T[f"I|{c}"]["ci"][0] for c in names]; hi = [T[f"I|{c}"]["ci"][1] for c in names]
    cols = ["tab:red"] + ["tab:gray"] * len(PANEL) + ["tab:blue"] * len(NATIVE)
    ax.bar(range(len(names)), vals, color=cols, alpha=0.7); ax.errorbar(range(len(names)), vals, yerr=[np.array(vals) - lo, np.array(hi) - vals], fmt="none", ecolor="k", capsize=2)
    for i, c in enumerate(names):
        ax.scatter(np.full(len(T[f"I|{c}"]["per_cluster"]), i), T[f"I|{c}"]["per_cluster"], s=10, color="k", zorder=3)
    ax.set_xticks(range(len(names))); ax.set_xticklabels(names, rotation=60, ha="right", fontsize=7); ax.axhline(0, color="k", lw=0.5)
    ax.set_title(f"{key}: I = ½[−ΔC_M + ΔC_N] (A = {T['A']['mean']:+.3f})"); ax.set_ylabel("interaction I")
plt.tight_layout(); plt.savefig(os.path.join(FIG, f"task_state_modulation_{STAGE}_interaction_panel.png"), dpi=130); plt.close()
fig, axes = plt.subplots(1, 2, figsize=(11, 4))
for ax, key in zip(axes, ("J_NP|L48-50", "J_NP|L51-59")):
    T = tables[key]
    if not DOSES:
        continue
    for arm, k in (("maintain", "dC_M"), ("mention", "dC_N")):
        xs = [0.5, 1.0, 2.0] if arm == "maintain" else [1.0]
        ys = [T[f"{k}|dose0.5"]["mean"], T[f"{k}|g"]["mean"], T[f"{k}|dose2.0"]["mean"]] if arm == "maintain" else [T[f"{k}|g"]["mean"]]
        ax.plot(xs, ys, "o-", label=f"ΔC_{AR[arm]} ({arm} arm move toward {'mention' if arm=='maintain' else 'maintain'})")
    ax.axhline(0, color="k", lw=0.5); ax.set_xlabel("dose (× natural gap)"); ax.set_title(f"{key}: dose response"); ax.legend(fontsize=7)
plt.tight_layout(); plt.savefig(os.path.join(FIG, f"task_state_modulation_{STAGE}_dose.png"), dpi=130); plt.close()


def cs(e):
    return f"{e['mean']:+.4f} [{e['ci'][0]:+.4f}, {e['ci'][1]:+.4f}] ({e.get('signs_pos', 0)}/{e['n']} >0)"


rep = [f"# H1 · task-state modulation — {STAGE} results (run {META['run_id']})\n", "## 1. Question and setup\n",
       f"Does the fitted block-35 task coordinate ĝ, set on interior carrier positions to the recipient word's opposite-arm natural level before the source counterfactual begins, change the incremental effect of a source replacement introduced only from block 36? G fitted on the 16 fitting words × carriers C0/C1 (|G| {FR['norm_G']:.2f}, split-half cos {FR['split_half_cos']:.3f}). Pairs {PAIRS} (excluded by geometry: {META['excluded']}), carriers {CARRIERS}, both directions, arms {ARMS}; cluster = unordered pair (n={len(PAIRS)}). Factorial {{clean, ĝ-move}} × {{noswap, swap36}} plus dose rows (maintain arm, ×{DOSES}) and 12 equal-dose panel directions at the same signed α_t (cosines with ĝ: {json.dumps({k: [round(x, 2) for x in v] for k, v in FR['cos_panel_ghat'].items()})}). Instruments J_NP (bf16 path) at L48–50 and L51–59 (co-primary), RESID_P pair axis, LOGITS. {META['n_forwards']} forwards; same-source and layer<36 identity asserted per cell.\n",
       "## 2. Main findings\n"]
for key in ("J_NP|L48-50", "J_NP|L51-59", "RESID_P|L48-50", "RESID_P|L51-59", "LOGITS"):
    T = tables[key]; ps = T["panel_summary"]
    rep.append(f"- **{key}:** A (natural arm difference in transfer) {cs(T['A'])}; ΔC_M(ĝ→mention level) {cs(T['dC_M|g'])}; ΔC_N(ĝ→maintain level) {cs(T['dC_N|g'])}; **I = {cs(T['I|g'])}**, I/A {T['I_over_A|g']['ratio']:.2f} [{T['I_over_A|g']['ci'][0]:.2f}, {T['I_over_A|g']['ci'][1]:.2f}]. Panel: max |I| {ps['panel_max_abs']:.4f}, {ps['panel_n_ge_g']}/12 ≥ |I_ĝ|, reciprocal-signed controls: {ps['panel_reciprocal'] or 'none'}. No-swap shift under the move: M {cs(T['noswap_shift_M|g'])}, N {cs(T['noswap_shift_N|g'])}.")
rep.append(f"- **Holm-adjusted p for I(ĝ) on J_NP across the two windows:** {json.dumps({k: round(v, 4) for k, v in tables['holm_I_g_J_NP'].items()})} (raw {json.dumps({k: round(v, 4) for k, v in tables['raw_p_I_g_J_NP'].items()})}).")
if DOSES:
    rep.append(f"- **Dose (J_NP L48–50, maintain arm):** ΔC_M at ×0.5 {cs(tables['J_NP|L48-50']['dC_M|dose0.5'])}, ×1 {cs(tables['J_NP|L48-50']['dC_M|g'])}, ×2 {cs(tables['J_NP|L48-50']['dC_M|dose2.0'])}.")
if NATIVE:
    for key in ("J_NP|L48-50", "J_NP|L51-59", "RESID_P|L48-50", "LOGITS"):
        rep.append(f"- **Native-level rows, {key}:** " + "; ".join(f"{c}: I {cs(tables[key]['I|'+c])}, ΔC_M {tables[key]['dC_M|'+c]['mean']:+.4f}, ΔC_N {tables[key]['dC_N|'+c]['mean']:+.4f}" for c in NATIVE) + ".")
    rep.append(f"- **Registered bar (max |I_perp| < 0.5 |I_ĝ| on J_NP at both windows):** " + json.dumps({w: tables[f'J_NP|{w}']['panel_summary']['registered_bar_max_lt_half_g'] for w in WINDOWS}) + "; strongest orthogonalized direction: " + json.dumps({w: (tables[f'J_NP|{w}']['panel_summary']['panel_argmax'], round(tables[f'J_NP|{w}']['panel_summary']['panel_max_abs'], 4)) for w in WINDOWS}) + f"; panel cosines with ĝ after projection: max |cos| {max(abs(v) for v in PANEL_COS.values()) if PANEL_COS else float('nan'):.2e}.")
    rep.append(f"- **Determinism gate (ĝ rows bitwise vs pilot):** {json.dumps(META.get('g_rows_bitwise_vs_pilot'))}.")
rep.append(f"- **Realized writes (ĝ):** ρ {tables['realized_writes']['g']['rho_min']:.3f}–{tables['realized_writes']['g']['rho_max']:.3f}, κ min {tables['realized_writes']['g']['kappa_min']:.4f}, requested norm median {tables['realized_writes']['g']['req_norm_median']:.2f}; gate {'PASS' if tables['realized_writes']['g']['gate_pass'] else 'FAIL'}. Natural level gap |L*−L_own| mean {tables['alpha_summary']['L_gap_mean']:.2f}.")
rep.append(f"- **Random-column floor (J_NP):** " + "; ".join(f"{w}: |I_ĝ| {v['I_g_target_pair']:+.4f} vs random-column p95 {v['random_col_abs_p95']:.4f}, max {v['random_col_abs_max']:.4f}" for w, v in ((w, tables[f'random_column_floor|{w}']) for w in WINDOWS)) + ".")
rep.append(f"- **Rank-1-anywhere (L24–59):** " + "; ".join(f"{k}: X {v['X_rank1_rate']:.2f} / Y {v['Y_rank1_rate']:.2f}" for k, v in hits.items() if k.startswith(("clean", "g"))) + ".\n")
rep.append("## 3. Complete numerical evidence\n")
for key in ("J_NP|L48-50", "J_NP|L51-59", "RESID_P|L48-50", "RESID_P|L51-59", "LOGITS"):
    T = tables[key]
    rep.append(f"### {key}\n\n| quantity | mean | 95% t-CI | signs >0 / n | per-pair |\n|---|---|---|---|---|")
    for q in ["A", "C_clean_M", "C_clean_N", "dC_M|g", "dC_N|g", "I|g", "noswap_shift_M|g", "noswap_shift_N|g"] + [f"dC_M|dose{s}" for s in DOSES] + [f"{k}|{c}" for c in PANEL + NATIVE for k in ("dC_M", "dC_N", "I")]:
        e = T[q]; rep.append(f"| {q} | {e['mean']:+.4f} | [{e['ci'][0]:+.4f}, {e['ci'][1]:+.4f}] | {e.get('signs_pos', 0)}/{e['n']} | {', '.join(f'{x:+.3f}' for x in e['per_cluster'])} |")
    rep.append("")
rep.append("### Realized writes and damage per condition\n\n| condition | ρ min–max | κ min | req. norm median | ΔNLL mean / max | top-1 retention min |\n|---|---|---|---|---|---|")
for c, v in tables["realized_writes"].items():
    d = tables["damage"][c]
    rep.append(f"| {c} | {v['rho_min']:.3f}–{v['rho_max']:.3f} | {v['kappa_min']:.4f} | {v['req_norm_median']:.2f} | {d['dNLL_mean']:+.4f} / {d['dNLL_max']:+.4f} | {d['top1_min']:.3f} |")
rep.append("\n### Hit statistic (rank-1 anywhere, L24–59)\n\n| condition | X rank-1 rate | Y rank-1 rate | n cells |\n|---|---|---|---|")
for k, v in hits.items():
    rep.append(f"| {k} | {v['X_rank1_rate']:.2f} | {v['Y_rank1_rate']:.2f} | {v['n_cells']} |")
rep.append(f"\nFigures: `figures/task_state_modulation_{STAGE}_interaction_panel.png`, `figures/task_state_modulation_{STAGE}_dose.png`. Machine-readable: `task_state_modulation_{STAGE}_tables.json`.\n")
rep.append("## 4. Verification and limitations\n\n- Same-source at L36 bitwise equal to clean and layers < 36 identical between futures on every cell (asserted); realized-write gate per condition above.\n- The clean-derived α_t is the recipient word's own opposite-arm level minus its clean coordinate, reused in both phases; the donor identity never enters the dose.\n- Pilot scale n=3 pairs on the fitting carriers; the panel has 12 members, so no tail probability over directions is claimed. Two background PCs have cosine up to 0.30 with ĝ.\n- Random-column floor compares a pair margin with single-column changes; indicative only.\n")
rep.append("## 5. Interpretation and next decision\n\n_Filled in by hand after reading the tables._\n")
open(os.path.join(RES, f"task_state_modulation_{STAGE}.md"), "w").write("\n".join(rep))
print("\n".join(rep[4:14]))
