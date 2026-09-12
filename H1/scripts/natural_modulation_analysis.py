"""Analysis for H1 natural modulation (single scoring pass; reads H1/outputs/natural_modulation/raw.npz).

Endpoints (the presence and pair-margin definitions, §4.5): presence s_J(X) = z_X - mean(z_decoys) per condition, positions then carriers
averaged within word; D_J(X) = maintain - mention and every other condition contrast, clustered by word;
prominence r_min, f_10; RESID_P presence and the model's own log-prob margin as companions; damage.
Writes H1/results/natural_modulation.md, natural_modulation_tables.json, figures/natural_modulation_*.png.
"""
import os, sys, json, itertools
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "common", "scripts"))
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import registry as R
import stats as S
STAGE = sys.argv[1] if len(sys.argv) > 1 else "pilot"

OUT = os.path.join(R.out_dir("H1", "outputs"), "natural_modulation")
RES = os.path.join(R.out_dir("H1", "results"))
FIG = os.path.join(RES, "figures"); QUAL = os.path.join(RES, "qualitative")
os.makedirs(FIG, exist_ok=True); os.makedirs(QUAL, exist_ok=True)
META = json.load(open(os.path.join(OUT, f"meta_{STAGE}.json")))
Z = np.load(os.path.join(OUT, f"raw_{STAGE}.npz"))
COLS = META["columns"]; CIX = {w: i for i, w in enumerate(COLS)}
WORDS, DECOYS, CARRIERS = META["words"], META["decoys"], META["carriers"]
DIRECT_CARRIERS = META["direct_carriers"]; CONDS = META["conditions"]
DEC = [CIX[d] for d in DECOYS]
WIN_DEFAULT = [48, 49, 50]
WIN_LATE = list(range(51, 60))
BAND_PAPER = list(range(24, 60))
tok = R.make_tokenizer()


def pres(tag, X, inst="J_NP", layers=WIN_DEFAULT, use32=False):
    z = Z[f"{tag}|z32|J_NP"] if use32 else Z[f"{tag}|z|{inst}"].astype(np.float32)
    zz = z[layers]
    return float((zz[:, :, CIX[X]] - zz[:, :, DEC].mean(-1)).mean())


def pres_layers(tag, X, inst="J_NP", use32=False):
    z = Z[f"{tag}|z32|J_NP"] if use32 else Z[f"{tag}|z|{inst}"].astype(np.float32)
    return (z[:, :, CIX[X]] - z[:, :, DEC].mean(-1)).mean(1)          # [L]


def tagc(cond, X, ck):
    return f"controlled|{cond}|{X if cond != 'absent' else 'NONE'}|{ck}"


def per_word(fn):
    """fn(X, ck) -> value; average carriers within word -> one value per word."""
    return np.array([np.mean([fn(X, ck) for ck in CARRIERS]) for X in WORDS])


report, tables = [], {}
# ------------------------------------------------------------------ condition levels, controlled organism
_AVAIL = {k.split("|")[-1] for k in Z.files if "|z|" in k}
_INSTR = [t for t in (("J_NP (bf16 path)", "J_NP", False), ("J_NP (float32 z=n/r)", "J_NP", True), ("J_CB", "J_CB", False), ("R_CB", "R_CB", False)) if t[1] in _AVAIL]
for inst_name, inst, use32 in _INSTR:
    for wname, win in (("L48-50", WIN_DEFAULT), ("L51-59", WIN_LATE), ("L24-59", BAND_PAPER)):
        key = f"{inst_name}|{wname}"
        lev = {c: per_word(lambda X, ck, c=c: pres(tagc(c, X, ck), X, inst, win, use32)) for c in CONDS}
        tables[f"levels|{key}"] = {c: S.cluster_t(v) for c, v in lev.items()}
        contrasts = {}
        for a, b in [("maintain", "mention"), ("maintain", "plain_mention"), ("mention", "plain_mention"), ("plain_mention", "absent"),
                     ("mention", "absent"), ("maintain", "absent"), ("ignore", "mention"), ("do_not_think", "mention"), ("never_think", "mention"),
                     ("maintain", "ignore"), ("maintain", "never_think")]:
            contrasts[f"{a}-{b}"] = S.cluster_t(lev[a] - lev[b])
        tables[f"contrasts|{key}"] = contrasts

# RESID_P presence and output log-prob margin, same structure
def pres_p(tag, X, layers):
    return float(Z[f"{tag}|p_pres"][layers].mean())
def pres_p_absent(ck, X, layers):
    return float(Z[f"{tagc('absent', X, ck)}|p_pres|{X}"][layers].mean())
def lp_margin(tag, X):
    return float((Z[f"{tag}|lp_X"] - Z[f"{tag}|lp_decoys"]).mean())
for wname, win in (("L48-50", WIN_DEFAULT), ("L51-59", WIN_LATE), ("L24-59", BAND_PAPER), ("L36-50", list(range(36, 51)))):
    lev = {c: per_word(lambda X, ck, c=c: pres_p(tagc(c, X, ck), X, win) if c != "absent" else pres_p_absent(ck, X, win)) for c in CONDS}
    tables[f"levels|RESID_P|{wname}"] = {c: S.cluster_t(v) for c, v in lev.items()}
    tables[f"contrasts|RESID_P|{wname}"] = {f"{a}-{b}": S.cluster_t(lev[a] - lev[b]) for a, b in
                                            [("maintain", "mention"), ("maintain", "plain_mention"), ("mention", "plain_mention"), ("mention", "absent"), ("plain_mention", "absent"), ("never_think", "mention"), ("ignore", "mention")]}
lev = {c: per_word(lambda X, ck, c=c: lp_margin(tagc(c, X, ck), X)) for c in CONDS if c != "absent"}
tables["levels|LOGITS"] = {c: S.cluster_t(v) for c, v in lev.items()}
tables["contrasts|LOGITS"] = {f"{a}-{b}": S.cluster_t(lev[a] - lev[b]) for a, b in [("maintain", "mention"), ("maintain", "plain_mention"), ("mention", "plain_mention"), ("never_think", "mention")]}

# ------------------------------------------------------------------ prominence
prom = {}
for c in CONDS:
    rmin, f10, r_med = [], [], []
    for X in WORDS:
        vals_rmin, vals_f10, vals_med = [], [], []
        for ck in CARRIERS:
            key = f"{tagc(c, X, ck)}|rank_X" + ("" if c != "absent" else f"|{X}")
            rk = Z[key]                                                          # [L, P]
            for wname, win in (("L48-50", WIN_DEFAULT), ("L51-59", WIN_LATE), ("L24-59", BAND_PAPER)):
                pass
            w = rk[BAND_PAPER]
            vals_rmin.append(int(w.min())); vals_f10.append(float((w <= 10).mean())); vals_med.append(float(np.median(np.log10(w))))
        rmin.append(np.median(vals_rmin)); f10.append(np.mean(vals_f10)); r_med.append(np.mean(vals_med))
    prom[c] = {"r_min_median_over_words": float(np.median(rmin)), "r_min_per_word": [int(x) for x in rmin],
               "f10_mean": float(np.mean(f10)), "rank1_anywhere_rate": float(np.mean([r == 1 for r in rmin])),
               "median_log10_rank": float(np.mean(r_med))}
tables["prominence|L24-59"] = prom
# per-layer rank-1-anywhere (paper's hit statistic) profile
prof = {}
for c in ("maintain", "mention", "plain_mention", "absent"):
    hits = np.zeros(len(META["layers"]))
    for X in WORDS:
        for ck in CARRIERS:
            key = f"{tagc(c, X, ck)}|rank_X" + ("" if c != "absent" else f"|{X}")
            hits += (Z[key].min(1) == 1)
    prof[c] = (hits / (len(WORDS) * len(CARRIERS))).tolist()
tables["hit_profile_by_layer"] = prof

# ------------------------------------------------------------------ damage and numerics
dmg = {c: S.cluster_t(per_word(lambda X, ck, c=c: float(Z[f"{tagc(c, X, ck)}|nll"]))) for c in CONDS}
tables["carrier_nll"] = dmg
# bf16-path vs float32 diagnostic agreement on the presence score at the default window
d32 = per_word(lambda X, ck: pres(tagc("maintain", X, ck), X, "J_NP", WIN_DEFAULT, True) - pres(tagc("maintain", X, ck), X, "J_NP", WIN_DEFAULT, False))
tables["z32_minus_zbf16_presence_maintain_L48_50"] = S.cluster_t(d32)

# ------------------------------------------------------------------ direct organism
direct = {}
for rend in ("direct", "copy_adapted"):
    for wname, win in (("L48-50", WIN_DEFAULT), ("L51-59", WIN_LATE), ("L24-59", BAND_PAPER)):
        lev = {pid: np.array([np.mean([pres(f"{rend}|{pid}|{X}|{dk}", X, "J_NP", win) for dk in DIRECT_CARRIERS]) for X in WORDS]) for pid in META["direct_pair"]}
        levp = {pid: np.array([np.mean([pres_p(f"{rend}|{pid}|{X}|{dk}", X, win) for dk in DIRECT_CARRIERS]) for X in WORDS]) for pid in META["direct_pair"]}
        direct[f"{rend}|{wname}"] = {"J_NP": {p: S.cluster_t(v) for p, v in lev.items()}, "J_NP_focus-mention": S.cluster_t(lev["hold"] - lev["conversation"]),
                                     "RESID_P": {p: S.cluster_t(v) for p, v in levp.items()}, "RESID_P_focus-mention": S.cluster_t(levp["hold"] - levp["conversation"])}
    # prominence
    pr = {}
    for pid in META["direct_pair"]:
        rmin = [np.median([int(Z[f"{rend}|{pid}|{X}|{dk}|rank_X"][BAND_PAPER].min()) for dk in DIRECT_CARRIERS]) for X in WORDS]
        pr[pid] = {"r_min_median": float(np.median(rmin)), "rank1_anywhere_rate": float(np.mean([r == 1 for r in rmin])), "r_min_per_word": [int(x) for x in rmin]}
    direct[f"{rend}|prominence"] = pr
tables["direct"] = direct

json.dump(tables, open(os.path.join(RES, f"natural_modulation_{STAGE}_tables.json"), "w"), indent=1, default=float)

# ------------------------------------------------------------------ figures
def ci_str(e):
    return f"{e['mean']:+.3f} [{e['ci'][0]:+.3f}, {e['ci'][1]:+.3f}] ({e.get('signs_pos', 0)}/{e['n']} >0)"

# Fig 1: layer trajectories of presence per condition (J_NP bf16 path), mean over words × carriers
fig, axes = plt.subplots(1, 3, figsize=(16, 4.2))
L = np.array(META["layers"])
for ax, (inst, use32, title) in zip(axes, [("J_NP", False, "J_NP presence s_J (bf16 path)"), ("J_NP", True, "J_NP presence (float32 z=n/r)"), ("RESID", False, "RESID_P presence")]):
    for c in CONDS:
        if inst == "RESID":
            curves = [Z[f"{tagc(c, X, ck)}|p_pres" + ("" if c != "absent" else f"|{X}")].mean(1) for X in WORDS for ck in CARRIERS]
        else:
            curves = [pres_layers(tagc(c, X, ck), X, inst, use32) for X in WORDS for ck in CARRIERS]
        m = np.mean(curves, 0); sd = np.std(curves, 0) / np.sqrt(len(curves))
        ax.plot(L, m, label=c); ax.fill_between(L, m - sd, m + sd, alpha=0.15)
    for x in (35, 48, 50, 51):
        ax.axvline(x, color="k", lw=0.4, ls=":")
    ax.set_title(title); ax.set_xlabel("block output (lens source layer)"); ax.set_ylabel("z_X - mean z_decoys" if inst != "RESID" else "p.h - p.centroid")
axes[0].legend(fontsize=7)
plt.tight_layout(); plt.savefig(os.path.join(FIG, f"natural_modulation_{STAGE}_layer_trajectories.png"), dpi=130); plt.close()

# Fig 2: condition levels at L48-50 and L51-59 with per-word points
fig, axes = plt.subplots(1, 2, figsize=(12, 4))
for ax, wname in zip(axes, ("L48-50", "L51-59")):
    t = tables[f"levels|J_NP (bf16 path)|{wname}"]
    for i, c in enumerate(CONDS):
        e = t[c]; ax.errorbar(i, e["mean"], yerr=[[e["mean"] - e["ci"][0]], [e["ci"][1] - e["mean"]]], fmt="o", color="k", capsize=3)
        ax.scatter(np.full(len(e["per_cluster"]), i) + np.random.default_rng(0).uniform(-0.15, 0.15, len(e["per_cluster"])), e["per_cluster"], s=12, alpha=0.6)
    ax.set_xticks(range(len(CONDS))); ax.set_xticklabels(CONDS, rotation=30, ha="right"); ax.set_title(f"J_NP presence, {wname}, n={len(WORDS)} words (dots) with 95% t-CI")
plt.tight_layout(); plt.savefig(os.path.join(FIG, f"natural_modulation_{STAGE}_condition_levels.png"), dpi=130); plt.close()

# Fig 3: rank-1-anywhere hit profile by layer
plt.figure(figsize=(7, 3.5))
for c, v in prof.items():
    plt.plot(L, v, label=c)
plt.xlabel("layer"); plt.ylabel("fraction of (word,carrier) cells with rank 1 at some interior position"); plt.legend(fontsize=7); plt.title("Rank-1 surfacing of the introduced word by layer")
plt.tight_layout(); plt.savefig(os.path.join(FIG, f"natural_modulation_{STAGE}_hit_profile.png"), dpi=130); plt.close()

# ------------------------------------------------------------------ qualitative: top-10 at fixed and random cells
def decode_top(ids):
    return " · ".join(repr(tok.decode([int(t)]))[1:-1] for t in ids)
qual = ["# Natural modulation — qualitative readouts (J_NP top-10, interior carrier positions)\n",
        "Teacher-forced text: the assistant turn is the carrier copied verbatim; nothing is generated. Position shown = middle interior token. Ranks are over the full 248k vocabulary. Selection: the fixed cells listed in `meta.json.topk_cells` plus a seeded random sample (`qual_random_cells`, seed 20260907).\n"]
for key in [f"controlled|{c}|{X if c != 'absent' else 'NONE'}|{ck}" for c, X, ck in META["topk_cells"]] + META["qual_random_cells"]:
    k10 = f"{key}|top10_ids" if f"{key}|top10_ids" in Z else f"{key}|qual_top10_ids"
    if k10 not in Z:
        continue
    ids10 = Z[k10]; cell = META["cells"][key]; P = len(cell["interior"]); mid = P // 2
    X = key.split("|")[2]
    qual.append(f"\n## {key}  (user text: `{cell['user_text'][:90]}…`)\n\n| layer | top-10 at the middle interior token | rank of X over window L24-59 (min / median) |\n|---|---|---|")
    rk = Z[f"{key}|rank_X"] if X != "NONE" else None
    for l in (23, 31, 35, 39, 43, 47, 48, 50, 51, 55, 59, 62):
        rstr = "" if rk is None else f"{int(rk[l].min())} / {int(np.median(rk[l]))}"
        qual.append(f"| {l} | {decode_top(ids10[l, mid])} | {rstr} |")
open(os.path.join(QUAL, f"natural_modulation_{STAGE}_readouts.md"), "w").write("\n".join(qual))

# ------------------------------------------------------------------ report
def tab(d, title):
    rows = [f"### {title}", "", "| condition / contrast | mean | 95% t-CI | signs >0 / n | per-word |", "|---|---|---|---|---|"]
    for k, e in d.items():
        rows.append(f"| {k} | {e['mean']:+.4f} | [{e['ci'][0]:+.4f}, {e['ci'][1]:+.4f}] | {e.get('signs_pos', 0)}/{e['n']} | {', '.join(f'{x:+.3f}' for x in e['per_cluster'])} |")
    return "\n".join(rows) + "\n"

rep = [f"# H1 · natural modulation — results (run {META['run_id']}, stage {META['stage']})\n",
       "## 1. Question and setup\n",
       f"Does the maintain instruction raise the lens readability of the introduced word at the copied sentence? Controlled copy organism, {len(WORDS)} calibration words × {len(CONDS)} conditions × carriers {CARRIERS}; direct organism primary pair {META['direct_pair']} on carriers {DIRECT_CARRIERS}, direct and copy-adapted renderings never pooled. Readout J_NP at interior carrier positions; presence s_J(X) = z_X − mean(z_decoys); RESID_P = plain-sentence one-vs-decoy-centroid axis (fit templates 1–8; held-out margins at L36–50: {json.dumps({k: round(v, 2) for k, v in META['resid_axis']['heldout_margin_L36_50'].items()})}); LOGITS = model output log-prob margin. Cluster = word (n={len(WORDS)}); carriers averaged within word. {META['n_forwards']} forwards.\n",
       "## 2. Main findings\n"]
c0 = tables["contrasts|J_NP (bf16 path)|L48-50"]; c1 = tables["contrasts|J_NP (bf16 path)|L51-59"]; cp = tables["contrasts|RESID_P|L48-50"]
rep.append(f"- **maintain − mention (D_J), J_NP L48–50:** {ci_str(c0['maintain-mention'])}; L51–59: {ci_str(c1['maintain-mention'])}; RESID_P L48–50: {ci_str(cp['maintain-mention'])}.")
rep.append(f"- **maintain − plain mention, J_NP L48–50:** {ci_str(c0['maintain-plain_mention'])}; **mention − plain mention:** {ci_str(c0['mention-plain_mention'])}; **plain mention − absent:** {ci_str(c0['plain_mention-absent'])}.")
rep.append(f"- **Suppression tails vs mention (J_NP L48–50):** ignore {ci_str(c0['ignore-mention'])}; do-not-think {ci_str(c0['do_not_think-mention'])}; never-think {ci_str(c0['never_think-mention'])}.")
rep.append(f"- **Prominence (L24–59):** rank-1-anywhere rate maintain {prom['maintain']['rank1_anywhere_rate']:.2f} / mention {prom['mention']['rank1_anywhere_rate']:.2f} / plain mention {prom['plain_mention']['rank1_anywhere_rate']:.2f} / absent {prom['absent']['rank1_anywhere_rate']:.2f}; median r_min maintain {prom['maintain']['r_min_median_over_words']:.0f}, mention {prom['mention']['r_min_median_over_words']:.0f}.")
dd = tables["direct"]
rep.append(f"- **Direct organism (hold − conversation), J_NP L48–50:** direct rendering {ci_str(dd['direct|L48-50']['J_NP_focus-mention'])}; copy-adapted {ci_str(dd['copy_adapted|L48-50']['J_NP_focus-mention'])}; RESID_P direct {ci_str(dd['direct|L48-50']['RESID_P_focus-mention'])}.")
rep.append(f"- **Instrument note:** float32 z=n/r minus the bf16-path score on maintain presence at L48–50: {ci_str(tables['z32_minus_zbf16_presence_maintain_L48_50'])} (per-cell bf16 rounding averages out at the window; both saved).\n")
rep.append("Interpretation is in section 5 after the full tables.\n")
rep.append("## 3. Complete numerical evidence\n")
for inst_name in [t[0] for t in _INSTR]:
    for wname in ("L48-50", "L51-59", "L24-59"):
        rep.append(tab(tables[f"levels|{inst_name}|{wname}"], f"Levels, {inst_name}, {wname}"))
        rep.append(tab(tables[f"contrasts|{inst_name}|{wname}"], f"Contrasts, {inst_name}, {wname}"))
for wname in ("L36-50", "L48-50", "L51-59", "L24-59"):
    rep.append(tab(tables[f"levels|RESID_P|{wname}"], f"Levels, RESID_P, {wname}")); rep.append(tab(tables[f"contrasts|RESID_P|{wname}"], f"Contrasts, RESID_P, {wname}"))
rep.append(tab(tables["levels|LOGITS"], "Levels, LOGITS (output log-prob margin X − decoys, interior positions)")); rep.append(tab(tables["contrasts|LOGITS"], "Contrasts, LOGITS"))
rep.append("### Prominence (L24–59)\n\n| condition | median r_min | rank-1-anywhere rate | f_10 | mean median log10 rank |\n|---|---|---|---|---|")
for c, e in prom.items():
    rep.append(f"| {c} | {e['r_min_median_over_words']:.0f} | {e['rank1_anywhere_rate']:.2f} | {e['f10_mean']:.3f} | {e['median_log10_rank']:.2f} |")
rep.append("\n### Direct organism\n")
for k, v in dd.items():
    if k.endswith("prominence"):
        rep.append(f"- {k}: " + "; ".join(f"{p}: median r_min {e['r_min_median']:.0f}, rank-1 rate {e['rank1_anywhere_rate']:.2f}" for p, e in v.items()))
    else:
        rep.append(f"- {k}: J_NP hold {ci_str(v['J_NP']['hold'])}, conversation {ci_str(v['J_NP']['conversation'])}, focus−mention {ci_str(v['J_NP_focus-mention'])}; RESID_P focus−mention {ci_str(v['RESID_P_focus-mention'])}")
rep.append("\n### Damage (carrier NLL per condition; teacher-forced copy)\n\n| condition | mean NLL | CI |\n|---|---|---|")
for c, e in dmg.items():
    rep.append(f"| {c} | {e['mean']:.3f} | [{e['ci'][0]:.3f}, {e['ci'][1]:.3f}] |")
rep.append("\nFigures: `figures/natural_modulation_{STAGE}_*.png`. Qualitative: `qualitative/natural_modulation_{STAGE}_readouts.md`. Machine-readable: `natural_modulation_{STAGE}_tables.json`.\n")
rep.append("## 4. Verification and limitations\n")
rep.append(f"- Gates: all rendering gates passed for every cell (asserted at render). Instrument gates: `common/configs/instrument_gates_result.json` (repeat/empty-patch/same-source bitwise; subprojection diff 0.016; realized state-move ρ 1.002, κ 0.998).\n- Pilot scale: n={len(WORDS)} calibration words, {len(CARRIERS)} fitting carriers; evaluation banks and held-out carriers not yet touched.\n- The default window L48–50 sits before rank-1 surfacing begins in the earlier pilot; L51–59 and L24–59 are reported alongside.\n- bf16 path vs float32 diagnostic: per-cell differences of up to ~2.7 logits exist; window means agree to the level reported above.\n- The absent-source baseline is word-independent (one rendering per carrier scored against every word).\n")
rep.append("## 5. Interpretation and next decision\n")
rep.append("_Filled in by hand after reading the tables and qualitative samples (see the end of this file)._\n")
open(os.path.join(RES, f"natural_modulation_{STAGE}.md"), "w").write("\n".join(rep))
print("\n".join(rep[:12]))
print(f"-> {RES}/natural_modulation.md")
