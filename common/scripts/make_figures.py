"""Regenerate every repository figure in the ICLR paper style, from the committed *_tables.json only.

No model forwards, no raw arrays: every number here is one already in a committed report table, so a figure can
never disagree with the text. Usage: python common/scripts/make_figures.py [name ...]   (default: all)
"""
import os, sys, json
import numpy as np
for _p in (os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".claude", "skills", "iclr-plots", "scripts"),
           "/root/.claude/skills/iclr-plots/scripts", "/workspace/.claude/skills/iclr-plots/scripts"):
    sys.path.insert(0, _p)
try:
    import iclrplot as ip; ip.setup()
except ImportError:          # the ICLR style helper is a user-level skill; fall back to matplotlib defaults
    print("iclrplot not found: figures use matplotlib defaults")
import matplotlib.pyplot as plt

PROJ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
H1F = os.path.join(PROJ, "H1", "results", "figures"); H3F = os.path.join(PROJ, "H3", "results", "figures")
os.makedirs(H1F, exist_ok=True); os.makedirs(H3F, exist_ok=True)
T = lambda p: json.load(open(os.path.join(PROJ, p)))

def mci(d):
    """(mean, lo_err, hi_err) from a cluster-t entry, as matplotlib asymmetric yerr."""
    m, (lo, hi) = d["mean"], d["ci"]; return m, m - lo, hi - m

def errbars(entries):
    ms, los, his = zip(*[mci(e) for e in entries]); return np.array(ms), np.array([los, his])

FIGS = {}
def fig(name):
    def deco(f): FIGS[name] = f; return f
    return deco

# ---------------------------------------------------------------- H1


@fig("natural_modulation_conditions")
def _(stage="evaluate"):
    d = T(f"H1/results/tables/natural_modulation_{stage}_tables.json")
    conds = ["maintain", "plain_mention", "mention", "never_think", "do_not_think", "ignore", "absent"]
    nice = ["maintain", "plain\nmention", "mention\n(control)", "never\nthink", "do not\nthink", "ignore", "absent"]
    f, axes = ip.figure(width="full", ncols=2, aspect=0.75, sharey=False)
    for ax, win in zip(axes, ["L48-50", "L51-59"]):
        e = [d[f"levels|J_NP (bf16 path)|{win}"][c] for c in conds]
        m, err = errbars(e)
        cols = [ip.HIGHLIGHT if c == "maintain" else (ip.BASELINE if c == "absent" else ip.CATEGORICAL[0]) for c in conds]
        ax.bar(np.arange(len(conds)), m, 0.68, yerr=err, color=cols,
               error_kw=dict(elinewidth=0.7, capsize=1.8, ecolor="0.25"))
        ax.set_xticks(np.arange(len(conds)), nice, fontsize=6.5)
        ax.axhline(0, color="0.35", lw=0.6); ax.grid(axis="x", visible=False)
        ax.set_ylabel("Lens presence of the introduced word" if win == "L48-50" else None)
    ip.label_panels(axes, titles=["Readout window L48–50", "Readout window L51–59"])
    ip.finish(f, os.path.join(H1F, "natural_modulation_conditions"))


@fig("source_transfer_by_Lx")
def _():
    d = T("H1/results/tables/source_transfer_tables.json")
    lxs = [23, 28, 32, 36, 40, 44]
    f, axes = ip.figure(width="full", ncols=2, aspect=0.72)
    for ax, win in zip(axes, ["L48-50", "L51-59"]):
        for k, arm in enumerate(["maintain", "mention"]):
            r = [d[f"C_over_A|J_NP|{win}|{arm}|Lx{lx}"]["ratio"] for lx in lxs]
            lo = [d[f"C_over_A|J_NP|{win}|{arm}|Lx{lx}"]["ci"][0] for lx in lxs]
            hi = [d[f"C_over_A|J_NP|{win}|{arm}|Lx{lx}"]["ci"][1] for lx in lxs]
            ip.line_ci(ax, lxs, r, lo, hi, label=arm, color=ip.CATEGORICAL[k], marker=ip.markers(2)[k])
        ip.reference_line(ax, y=1.0, label="Complete transfer" if win == "L48-50" else None)
        ax.axvline(36, color=ip.HIGHLIGHT, ls=":", lw=0.9)
        ax.set_xlabel("Replacement start block $L_x$"); ax.set_ylim(0, 1.25)
        if win == "L48-50": ax.set_ylabel("Transferred fraction $C/A$")
    axes[0].legend(loc="lower left")
    ip.label_panels(axes, titles=["L48–50", "L51–59"])
    ip.finish(f, os.path.join(H1F, "source_transfer_by_Lx"))


@fig("task_state_orthopanel")
def _():
    d = T("H1/results/tables/task_state_modulation_evaluate_tables.json")
    f, axes = ip.figure(width="full", ncols=2, aspect=0.72, sharey=False)
    for ax, win in zip(axes, ["L48-50", "L51-59"]):
        w = d[f"J_NP|{win}"]
        panel = sorted([k.split("|")[1] for k in w if k.startswith("I|") and k != "I|g" and not k.startswith("I|native")],
                       key=lambda p: -abs(w[f"I|{p}"]["mean"]))
        names = ["ĝ (fitted)"] + panel
        vals = [w["I|g"]] + [w[f"I|{p}"] for p in panel]
        m, err = errbars(vals)
        cols = [ip.HIGHLIGHT] + [ip.CATEGORICAL[0]] * len(panel)
        ax.barh(np.arange(len(names))[::-1], m, 0.7, xerr=err, color=cols,
                error_kw=dict(elinewidth=0.6, capsize=1.5, ecolor="0.25"))
        ax.set_yticks(np.arange(len(names))[::-1], [n.replace("_perp", "⊥") for n in names], fontsize=6)
        ax.axvline(0, color="0.35", lw=0.6); ax.grid(axis="y", visible=False)
        ax.set_xlabel("Interaction $I$")
    ip.label_panels(axes, titles=["L48–50", "L51–59"])
    ip.finish(f, os.path.join(H1F, "task_state_orthopanel"))


@fig("tagged_selection")
def _():
    d = T("H1/results/tables/tagged_selection_evaluate_tables.json")
    insts = [("J_NP|L48-50", "J-lens\nL48–50"), ("J_NP|L51-59", "J-lens\nL51–59"),
             ("RESID_P|L51-59", "Plain axis\nL51–59"), ("LOGITS", "Output logits")]
    f, ax = ip.figure(width="wide")
    x = np.arange(len(insts)); w = 0.26
    for k, (key, lab) in enumerate([("self", "Pointed source"), ("other", "Unpointed sources"), ("ctrl", "No pointer (control)")]):
        vals = [d[i][key] for i, _ in insts]; m, err = errbars(vals)
        ax.bar(x + (k - 1) * w, m, w, yerr=err, label=lab, color=ip.CATEGORICAL[k],
               error_kw=dict(elinewidth=0.6, capsize=1.5, ecolor="0.25"))
    ax.set_xticks(x, [l for _, l in insts], fontsize=7)
    ax.set_ylabel("Transfer $C$ of the replaced source"); ax.axhline(0, color="0.35", lw=0.6)
    ax.grid(axis="x", visible=False); ip.legend_outside(f, "top", ncol=3)
    ip.finish(f, os.path.join(H1F, "tagged_selection"))


@fig("selection_localization")
def _():
    p = T("H1/results/tables/selection_localization_ptr_transplant_tables.json")
    rs = T("H1/results/tables/selection_localization_region_split_tables.json")
    rc = T("H1/results/tables/selection_localization_random_control_tables.json")
    f, axes = ip.figure(width="full", ncols=3, aspect=0.95)
    Ls = p["l_sweep"]
    for k, tgt in enumerate(["BtoA", "CtoA"]):
        v = [p[f"R|{tgt}|L51-59"][str(L)] for L in Ls]; m, err = errbars(v)
        ip.line_ci(axes[0], Ls, m, [a - b for a, b in zip(m, err[0])], [a + b for a, b in zip(m, err[1])],
                   label=f"{tgt[0]}→A", color=ip.CATEGORICAL[k], marker=ip.markers(2)[k])
    axes[0].set_xlabel("Transplant start block"); axes[0].set_ylabel("Restoration $R$ toward the donor")
    axes[0].legend(); axes[0].set_ylim(-0.05, 0.9)
    regs = ["tag", "instr_tail", "user_carrier", "gap", "full"]
    lab = ["tag", "instruction\ntail", "user\ncarrier", "delimiters", "full\nregion"]
    v = [rs[f"R|BtoA|{r}|L36|L51-59"] for r in regs]; m, err = errbars(v)
    axes[1].bar(np.arange(len(regs)), m, 0.68, yerr=err,
                color=[ip.HIGHLIGHT] + [ip.CATEGORICAL[0]] * 3 + [ip.NEUTRAL],
                error_kw=dict(elinewidth=0.6, capsize=1.5, ecolor="0.25"))
    axes[1].set_xticks(np.arange(len(regs)), lab, fontsize=5.8); axes[1].axhline(0, color="0.35", lw=0.6)
    axes[1].grid(axis="x", visible=False); axes[1].set_xlabel("Patched sub-region (B→A, block 36)")
    conds = [("BtoA", "donor"), ("shuffB", "shuffled\npositions"), ("flipB", "sign\nflipped"), ("randB_s0", "random\nseed 0"), ("randB_s1", "random\nseed 1")]
    v = [rc[f"R|{c}|L51-59"] for c, _ in conds]; m, err = errbars(v)
    axes[2].bar(np.arange(len(conds)), m, 0.68, yerr=err,
                color=[ip.HIGHLIGHT] + [ip.CATEGORICAL[0]] * (len(conds) - 1),
                error_kw=dict(elinewidth=0.6, capsize=1.5, ecolor="0.25"))
    axes[2].set_xticks(np.arange(len(conds)), [l for _, l in conds], fontsize=5.8)
    axes[2].axhline(0, color="0.35", lw=0.6); axes[2].grid(axis="x", visible=False)
    axes[2].set_xlabel("Norm-matched controls")
    ip.label_panels(axes, titles=["Depth of sufficiency", "Which tokens carry it", "Donor specificity"])
    ip.finish(f, os.path.join(H1F, "selection_localization"))


@fig("scaffold_generality")
def _():
    d = T("H1/results/tables/scaffold_generality_tagged_tables.json")
    rends = d["renderings"]; nice = [r.replace("_", "\n") for r in rends]
    f, ax = ip.figure(width="wide")
    x = np.arange(len(rends)); w = 0.38
    for k, win in enumerate(["L48-50", "L51-59"]):
        v = [d[f"J_NP|{win}|{r}"]["S"] for r in rends]; m, err = errbars(v)
        ax.bar(x + (k - 0.5) * w, m, w, yerr=err, label=f"L{win[1:]}", color=ip.CATEGORICAL[k],
               error_kw=dict(elinewidth=0.6, capsize=1.5, ecolor="0.25"))
    ax.set_xticks(x, nice, fontsize=7); ax.set_ylabel("Selection $S$ (pointed − unpointed)")
    ax.axhline(0, color="0.35", lw=0.6); ax.grid(axis="x", visible=False); ax.legend(title="Readout window")
    ip.finish(f, os.path.join(H1F, "scaffold_generality"))


@fig("competition_and_cue")
def _():
    d = T("H1/results/tables/competition_and_cue_tables.json")
    ks = [1, 2, 3, 4, 6]
    f, axes = ip.figure(width="full", ncols=2, aspect=0.72)
    for k, (key, lab) in enumerate([("focal_pointed", "Pointed"), ("focal_ctrl", "No pointer")]):
        v = [d["J_NP|L51-59"][f"k{i}|{key}"] for i in ks]; m, err = errbars(v)
        ip.line_ci(axes[0], ks, m, m - err[0], m + err[1], label=lab, color=ip.CATEGORICAL[k], marker=ip.markers(2)[k])
    axes[0].set_xlabel("Number of tagged sources $k$"); axes[0].set_ylabel("Transfer of the focal source")
    axes[0].set_xticks(ks); axes[0].legend()
    cues = ["none", "sameA", "switchB"]; nice = ["no cue", "same-tag cue", "switch cue"]
    x = np.arange(3); w = 0.38
    for k, (src, lab) in enumerate([("C_A", "Source A (originally pointed)"), ("C_B", "Source B (cue target)")]):
        v = [d["J_NP|L51-59"][f"cue|{c}|{src}"] for c in cues]; m, err = errbars(v)
        axes[1].bar(x + (k - 0.5) * w, m, w, yerr=err, label=lab, color=ip.CATEGORICAL[k],
                    error_kw=dict(elinewidth=0.6, capsize=1.5, ecolor="0.25"))
    axes[1].set_xticks(x, nice, fontsize=7); axes[1].grid(axis="x", visible=False)
    axes[1].axhline(0, color="0.35", lw=0.6); axes[1].legend(fontsize=6)
    axes[1].set_ylabel("Transfer $C$ after the cue")
    ip.label_panels(axes, titles=["Competition", "Mid-carrier re-assignment"])
    ip.finish(f, os.path.join(H1F, "competition_and_cue"))


@fig("tagged_categories")
def _():
    d = T("H1/results/tables/tagged_categories_select_tables.json")
    f, ax = ip.figure(width="wide")
    combos = [("J_NP|member|L48-50", "J-lens\nmembers\nL48–50"), ("J_NP|member|L51-59", "J-lens\nmembers\nL51–59"),
              ("RESID_P|member|L51-59", "Plain axis\nmembers"), ("LOGITS|member", "Logits\nmembers"),
              ("J_NP|label|L51-59", "J-lens\nlabel")]
    x = np.arange(len(combos)); w = 0.26
    for k, (key, lab) in enumerate([("self", "Pointed category"), ("other", "Unpointed"), ("ctrl", "No pointer")]):
        v = [d[c]["cluster_triple"][key] for c, _ in combos]; m, err = errbars(v)
        ax.bar(x + (k - 1) * w, m, w, yerr=err, label=lab, color=ip.CATEGORICAL[k],
               error_kw=dict(elinewidth=0.6, capsize=1.5, ecolor="0.25"))
    ax.set_xticks(x, [l for _, l in combos], fontsize=6.5); ax.axhline(0, color="0.35", lw=0.6)
    ax.set_ylabel("Transfer of the replaced category"); ax.grid(axis="x", visible=False)
    ip.legend_outside(f, "top", ncol=3)
    ip.finish(f, os.path.join(H1F, "tagged_categories"))


# ---------------------------------------------------------------- H3


@fig("h3_dissociation")
def _():
    """The centrepiece: internal readout vs behaviour, both organisms."""
    r = T("H3/results/tables/computed_sum_consumer_robust_tables.json")
    c = T("H3/results/tables/selection_to_behavior_carrier_only_tables.json")
    f, axes = ip.figure(width="full", ncols=2, aspect=0.8)
    conds = [("O_donor", "Source\nresiduals"), ("C_full", "Carrier\n(≥36)"), ("C_all", "Carrier\n(all blocks)"), ("NEC", "Source, carrier\nclamped"), ("C_rand", "Carrier\nrandom")]
    ax = axes[0]; x = np.arange(len(conds)); w = 0.38
    internal = [r[f"all carriers|off3|report|{k}"]["zj"]["mean"] for k, _ in conds]
    ref_i = r["all carriers|off3|report|O_donor"]["zj"]["mean"]
    ref_b = r["all carriers|off3|report|O_donor"]["beh"]["mean"]
    behav = [r[f"all carriers|off3|report|{k}"]["beh"]["mean"] for k, _ in conds]
    ax.bar(x - w / 2, np.array(internal) / ref_i, w, label="Internal readout (J-lens)", color=ip.CATEGORICAL[0])
    ax.bar(x + w / 2, np.array(behav) / ref_b, w, label="Answer margin", color=ip.HIGHLIGHT)
    for i, (k, _) in enumerate(conds):
        fl = r[f"all carriers|off3|report|{k}"]["flips"]
        ax.annotate(f"{fl}/32", (i + w / 2, max(behav[i] / ref_b, 0) + 0.03), ha="center", fontsize=6, color=ip.HIGHLIGHT)
    ax.set_xticks(x, [l for _, l in conds], fontsize=6.5); ax.set_ylabel("Effect, relative to the source donor")
    ax.axhline(0, color="0.35", lw=0.6); ip.reference_line(ax, y=1.0)
    ax.grid(axis="x", visible=False); ax.legend(fontsize=6.5, loc="upper right"); ax.set_ylim(-0.05, 1.25)
    ax = axes[1]
    arms = [("CarrBtoA", "B→A\n(≥36)"), ("CarrCtoA", "C→A\n(≥36)"), ("CarrBtoA_all", "B→A\n(all)"), ("CarrCtoA_all", "C→A\n(all)"), ("randCarrB", "random")]
    ints = [c[a]["R"]["mean"] for a, _ in arms]; behs = [c[a]["ratio"] for a, _ in arms]
    ax.bar(np.arange(len(arms)) - w / 2, ints, w, color=ip.CATEGORICAL[0])
    ax.bar(np.arange(len(arms)) + w / 2, behs, w, color=ip.HIGHLIGHT)
    for i, (a, _) in enumerate(arms):
        ax.annotate(f"{c[a]['flips']}/36", (i + w / 2, max(behs[i], 0) + 0.03), ha="center", fontsize=6, color=ip.HIGHLIGHT)
    ax.set_xticks(np.arange(len(arms)), [l for _, l in arms], fontsize=6.5)
    ax.set_ylabel("Restoration toward the donor"); ax.axhline(0, color="0.35", lw=0.6)
    ip.reference_line(ax, y=1.0); ax.grid(axis="x", visible=False); ax.set_ylim(-0.05, 1.25)
    ip.label_panels(axes, titles=["Sum consumer (report)", "Word consumer (carrier-only donor)"])
    ip.finish(f, os.path.join(H3F, "h3_dissociation"))


@fig("h3_robustness_grid")
def _():
    """Every carrier subset x donor map x consumer: is the pattern the same everywhere?"""
    r = T("H3/results/tables/computed_sum_consumer_robust_tables.json")
    subsets = ["all carriers", "C0/C1", "C2/C3"]; maps = ["off3", "off1"]; conds = ["O_donor", "C_full", "C_all", "NEC", "C_rand"]
    f, axes = ip.figure(width="full", ncols=2, aspect=0.85)
    for ax, cons in zip(axes, ["report", "parity"]):
        rows, ylab = [], []
        for s in subsets:
            for mp in maps:
                ref = r[f"{s}|{mp}|{cons}|O_donor"]["beh"]["mean"]
                rows.append([r[f"{s}|{mp}|{cons}|{c}"]["beh"]["mean"] / ref for c in conds])
                ylab.append(f"{s}, {mp}")
        ip.heatmap(ax, np.array(rows), xlabels=["source", "carrier\n≥36", "carrier\nall", "source,\ncarrier\nclamped", "carrier\nrandom"],
                   ylabels=ylab if cons == "report" else [""] * len(ylab), signed=True, annotate=True, fmt="{:.2f}",
                   cbar=(cons == "parity"), cbar_label="Answer-margin effect / source-donor effect")
        ax.tick_params(axis="x", labelsize=6); ax.tick_params(axis="y", labelsize=6)
    ip.label_panels(axes, titles=["report", "parity"])
    ip.finish(f, os.path.join(H3F, "h3_robustness_grid"))


@fig("h3_query_local")
def _():
    """Reconstruction at the question positions, and whether the answer depends on it."""
    q = T("H3/results/tables/query_local_workspace_tables.json")
    f, axes = ip.figure(width="full", ncols=3, aspect=0.95)
    ax = axes[0]
    conds = [("O_donor", "Source\ndonor"), ("NEC", "Source donor,\ncarrier clamped"), ("C_full", "Carrier\ndonor")]
    x = np.arange(len(conds)); w = 0.38
    for k, (site, lab) in enumerate([("zc", "at the carrier"), ("zq", "at the question")]):
        v = [q[f"queryread|report|{c}"][site] for c, _ in conds]; m, err = errbars(v)
        ax.bar(x + (k - 0.5) * w, m, w, yerr=err, label=lab, color=ip.CATEGORICAL[k],
               error_kw=dict(elinewidth=0.6, capsize=1.5, ecolor="0.25"))
    ax.set_xticks(x, [l for _, l in conds], fontsize=6.5); ax.axhline(0, color="0.35", lw=0.6)
    ax.set_ylabel("Donor-sum shift (J-lens)"); ax.grid(axis="x", visible=False); ax.legend(fontsize=6)
    ax = axes[1]
    cs = T("H3/results/tables/query_local_workspace_tables.json")
    rows = [("NEC", "source donor,\ncarrier clamped"), ("NEC_Qclamp_noans", "+ clamp sum on\nquestion tokens")]
    x = np.arange(len(rows)); w = 0.38
    for k, cons in enumerate(["parity", "report"]):
        ref = cs[f"clampsplit|{cons}|NEC"]["beh"]["mean"]
        v = [cs[f"clampsplit|{cons}|{c}"]["beh"] for c, _ in rows]; m, err = errbars(v)
        ax.bar(x + (k - 0.5) * w, m / ref, w, yerr=err / ref, label=cons, color=ip.CATEGORICAL[k],
               error_kw=dict(elinewidth=0.6, capsize=1.5, ecolor="0.25"))
        for i, (c, _) in enumerate(rows):
            ax.annotate(f"{cs[f'clampsplit|{cons}|{c}']['flips_donor']}/32", (i + (k - 0.5) * w, m[i] / ref + err[1][i] / ref + 0.03), ha="center", fontsize=5.5, color=ip.CATEGORICAL[k])
    ax.set_xticks(x, [l for _, l in rows], fontsize=6); ax.set_ylim(0, 1.7)
    ax.set_ylabel("Answer margin, relative to no clamp"); ax.axhline(0, color="0.35", lw=0.6); ax.grid(axis="x", visible=False); ax.legend(fontsize=6, loc="upper left", ncol=2, frameon=False)
    ax = axes[2]
    ns = [("C_from_S", "carrier\nfrom $S$"), ("C_from_S2", "carrier\nfrom $S_2$"), ("C_rand_ns", "carrier\nrandom"), ("Q_from_S", "question\nfrom $S$")]
    v = [q[f"nosource2|report|{c}"]["beh"] for c, _ in ns]; m, err = errbars(v); m = -m; err = err[::-1]
    ax.bar(np.arange(len(ns)), m, 0.6, yerr=err, color=[ip.HIGHLIGHT, ip.CATEGORICAL[0], ip.NEUTRAL, ip.CATEGORICAL[2]],
           error_kw=dict(elinewidth=0.6, capsize=1.5, ecolor="0.25"))
    for i, (c, _) in enumerate(ns):
        k = q[f"nosource2|report|{c}"]; ax.annotate(f"$S$: {k['flips_own']}/32", (i, (m[i] + err[1][i] if m[i] >= 0 else m[i] - err[0][i] - 2.2) + 0.3), ha="center", fontsize=5.5)
    ax.set_xticks(np.arange(len(ns)), [l for _, l in ns], fontsize=6)
    ax.set_ylabel("$\\log P(S) - \\log P(S_2)$ shift (report)"); ax.axhline(0, color="0.35", lw=0.6); ax.grid(axis="x", visible=False)
    ip.label_panels(axes, titles=["Where the sum is readable", "Is the rebuilt sum used", "No operands in the prompt"])
    ip.finish(f, os.path.join(H3F, "h3_query_local"))


@fig("h3_global_conditions")
def _():
    """Amendment 3: paper-style swap, decision-position donor, mask rows."""
    g = T("H3/results/tables/computed_sum_consumer_global_tables.json")
    conds = [("O_donor36", "source ≥36"), ("O_donor0", "source, all blocks"), ("C_full", "carrier ≥36"),
             ("G_full", "source + carrier"), ("G_swap_all", "lens swap, source→answer"), ("G_swap_carrier", "lens swap, carrier only"),
             ("D_band", "decision positions 36–50"), ("D_band_early", "decision positions 36–43")]
    f, ax = ip.figure(width="full", aspect=0.5)
    y = np.arange(len(conds))[::-1]; h = 0.38
    for k, cons in enumerate(["report", "parity"]):
        ref = g[f"{cons}|O_donor36"]["beh"]["mean"]
        v = [g[f"{cons}|{c}"]["beh"] for c, _ in conds]; m, err = errbars(v)
        ax.barh(y + (0.5 - k) * h, m / ref, h, xerr=err / abs(ref), label=cons, color=ip.CATEGORICAL[k],
                error_kw=dict(elinewidth=0.6, capsize=1.5, ecolor="0.25"))
        for i, (c, _) in enumerate(conds):
            ax.annotate(f"{g[f'{cons}|{c}']['flips']}/32", (max(m[i] / ref, 0) + 0.02, y[i] + (0.5 - k) * h),
                        va="center", fontsize=5.5, color=ip.CATEGORICAL[k])
    ax.set_yticks(y, [l for _, l in conds], fontsize=6.5)
    ax.set_xlabel("Answer-margin effect, relative to the source donor"); ax.axvline(0, color="0.35", lw=0.6)
    ip.reference_line(ax, x=1.0); ax.grid(axis="y", visible=False); ax.legend(fontsize=6.5, loc="lower right")
    ip.finish(f, os.path.join(H3F, "h3_global_conditions"))


@fig("h3_answer_position_profile")
def _():
    """How far the answer position moves under each intervention, by block."""
    import re
    md = open(os.path.join(PROJ, "H3/results/reports/computed_sum_consumer_robust.md")).read()
    tbl = md.split("## Answer-position distance from clean by block")[1].split("\n\n")[1]
    rows = [r.strip("| ").split(" | ") for r in tbl.strip().splitlines()[2:]]
    blocks = [int(r[0]) for r in rows]
    conds = ["O_donor", "C_full", "C_all", "C_rand", "NEC"]
    nice = {"O_donor": "Source donor", "C_full": "Carrier ≥36", "C_all": "Carrier, all blocks", "C_rand": "Carrier random", "NEC": "Source, carrier clamped"}
    f, ax = ip.figure(width="wide")
    for k, c in enumerate(conds):
        vals = [float(r[1 + k]) for r in rows]
        ax.plot(blocks, vals, label=nice[c], color=ip.CATEGORICAL[k], marker=ip.markers(5)[k], ms=2.5)
    ax.set_xlabel("Block"); ax.set_ylabel("Answer-position residual distance from clean")
    ax.set_yscale("symlog", linthresh=1); ax.legend(fontsize=6)
    ip.finish(f, os.path.join(H3F, "h3_answer_position_profile"))


@fig("h3_two_hop")
def _():
    """The paper's released two-hop items: source vs carrier, and the unanswerable-clue transplant."""
    d = T("H3/results/tables/two_hop_organism_tables.json")
    f, axes = ip.figure(width="full", ncols=2, aspect=0.8)
    ax = axes[0]
    conds = [("S_donor0", "Clue span\n(all blocks)"), ("S_donor", "Clue span\n(≥36)"), ("C_full", "Carrier\n(≥36)"),
             ("C_all", "Carrier\n(all blocks)"), ("NEC_all", "Clue donor,\ncarrier clamped"), ("C_rand", "Carrier\nrandom")]
    v = [d[f"full|{k}"] for k, _ in conds]
    cols = [ip.CATEGORICAL[0]] * 2 + [ip.HIGHLIGHT] * 2 + [ip.CATEGORICAL[0], ip.NEUTRAL]
    ax.bar(np.arange(len(conds)), [x["share"] for x in v], 0.68, color=cols)
    for i, x in enumerate(v):
        ax.annotate(f"{x['flips']}/48", (i, max(x["share"], 0) + 0.03), ha="center", fontsize=6)
    ax.set_xticks(np.arange(len(conds)), [l for _, l in conds], fontsize=6)
    ax.set_ylabel("Answer effect, share of the natural swing"); ax.axhline(0, color="0.35", lw=0.6)
    ip.reference_line(ax, y=1.0); ax.grid(axis="x", visible=False); ax.set_ylim(0, 1.2)
    ax = axes[1]
    ns = [("C_from_E", "carrier from\nentity $E$"), ("C_from_E2", "carrier from\nentity $E_2$"),
          ("C_rand_nc", "carrier\nrandom"), ("Q_from_E", "question\nfrom $E$")]
    sh = [abs(d[f"noclue|{k}"]["share"]) for k, _ in ns]
    ax.bar(np.arange(len(ns)), sh, 0.68, color=[ip.HIGHLIGHT, ip.CATEGORICAL[0], ip.NEUTRAL, ip.CATEGORICAL[2]])
    for i, (k, _) in enumerate(ns):
        ax.annotate(f"{d[f'noclue|{k}']['flips']}/40", (i, sh[i] + 0.03), ha="center", fontsize=6)
    ax.set_xticks(np.arange(len(ns)), [l for _, l in ns], fontsize=6)
    ax.set_ylabel("Move toward the installed entity's answer"); ax.axhline(0, color="0.35", lw=0.6)
    ip.reference_line(ax, y=1.0); ax.grid(axis="x", visible=False); ax.set_ylim(0, 1.2)
    ip.label_panels(axes, titles=["Clue visible", "Clue unanswerable (placeholder)"])
    ip.finish(f, os.path.join(H3F, "h3_two_hop"))


@fig("h3_carrier_vs_boundary")
def _():
    """The current state of knowledge: carrier share against boundary position, every organism tested."""
    L = T("H3/results/tables/recompute_cost_ladder_tables.json")
    G = T("H3/results/tables/computed_sum_consumer_global_tables.json")
    TH = T("H3/results/tables/two_hop_organism_tables.json")
    f, axes = ip.figure(width="full", ncols=2, aspect=0.82)
    ax = axes[0]
    tiers = [("t1_memorised", "a+b"), ("t2_composed", "a+b+c"), ("t3_chained", "2(a+b)")]
    x = np.arange(len(tiers)); w = 0.38
    ax.bar(x - w / 2, [L[f"{t}|C_full"]["share"] for t, _ in tiers], w, label="Carrier copy", color=ip.HIGHLIGHT)
    ax.bar(x + w / 2, [L[f"{t}|S_donor"]["share"] for t, _ in tiers], w, label="Source at block 36", color=ip.CATEGORICAL[0])
    for i, (t, _) in enumerate(tiers):
        ax.annotate(f"competence\n{L[f'{t}|competence']:.2f}", (i, 1.05), ha="center", fontsize=5.5, color="0.35")
    ax.set_xticks(x, [l for _, l in tiers]); ax.set_ylim(0, 1.25)
    ax.set_xlabel("Latent, by difficulty")
    ax.set_ylabel("Share of the natural swing"); ax.grid(axis="x", visible=False); ax.legend(fontsize=6, loc="center left")
    ax = axes[1]
    pts = [("a+b (original)", G["report|O_donor36"]["beh"]["mean"] / G["report|O_donor0"]["beh"]["mean"],
            G["report|C_full"]["beh"]["mean"] / G["report|O_donor0"]["beh"]["mean"], ip.CATEGORICAL[0]),
           ("a+b", L["t1_memorised|S_donor"]["share"], L["t1_memorised|C_full"]["share"], ip.CATEGORICAL[0]),
           ("a+b+c", L["t2_composed|S_donor"]["share"], L["t2_composed|C_full"]["share"], ip.CATEGORICAL[0]),
           ("2(a+b)", L["t3_chained|S_donor"]["share"], L["t3_chained|C_full"]["share"], ip.CATEGORICAL[0]),
           ("two-hop facts", TH["full|S_donor"]["share"], TH["full|C_full"]["share"], ip.HIGHLIGHT)]
    off = {"a+b (original)": (-46, -2), "a+b": (-20, 8), "a+b+c": (-30, 0), "2(a+b)": (-30, -3), "two-hop facts": (0, 9)}
    for lab, bx, cy, c in pts:
        ax.scatter([bx], [cy], s=34, color=c, edgecolor="white", linewidth=0.5, zorder=3)
        ax.annotate(lab, (bx, cy), xytext=off.get(lab, (0, 7)), textcoords="offset points",
                    ha="center" if off.get(lab, (0, 7))[0] == 0 else "right", va="center", fontsize=6, color=c)
    ax.set_xlabel("Boundary: source effect already fixed by block 36"); ax.set_ylabel("Carrier copy's share")
    ax.set_xlim(0.42, 1.10); ax.set_ylim(-0.02, 0.36)
    ip.label_panels(axes, titles=["Difficulty ladder (boundary held fixed)", "Every organism tested"])
    ip.finish(f, os.path.join(H3F, "h3_carrier_vs_boundary"))


@fig("h3_bridgeswap")
def _():
    """The paper's lens-coordinate swap on a two-hop intermediate, split by the positions it is applied to; both models; sequence-log-prob endpoint."""
    panels = [("H3/results/tables/two_hop_bridgeswap_tables.json", "Qwen3.6-27B (hybrid)"), ("replication_qwen3_32b/H3/results/tables/two_hop_bridgeswap_tables.json", "Qwen3-32B (dense)")]
    f, axes = ip.figure(width="full", ncols=2, sharey=True, aspect=0.78)
    sets = [("clue", "Clue\nspan"), ("carr", "Copied\ncarrier"), ("q", "Question\nturn"), ("tail", "All positions\n(paper's swap)")]
    x = np.arange(len(sets)); w = 0.38
    for ax, (path, title) in zip(axes, panels):
        B = T(path)
        for k, (pre, lab, col) in enumerate((("int", "Intermediate swap (e.g. Spain\u2194Canada)", ip.HIGHLIGHT), ("ans", "Answer-word swap (Madrid\u2194Ottawa)", ip.CATEGORICAL[0]))):
            ms, errs = errbars([B[f"{pre}_{s}"]["seq"]["share"] for s, _ in sets])
            ax.bar(x + (k - 0.5) * w, ms, w, yerr=errs, label=lab, color=col, error_kw={"lw": 0.6, "capsize": 2})
            for i, (s, _) in enumerate(sets):
                ax.annotate(f"{B[f'{pre}_{s}']['seq']['flips']}/{B[f'{pre}_{s}']['cells']}", (x[i] + (k - 0.5) * w, ms[i] + errs[1][i] + 0.02), ha="center", fontsize=5.5, color="0.3")
        ax.axhline(1.0, color="0.45", lw=0.8, ls="--", label="Full-residual clue donor (ceiling)")
        ax.axhline(B["rand_tail"]["seq"]["share"]["mean"], color="0.45", lw=0.8, ls=":", label="Decoy-pair swap, all positions")
        ax.set_xticks(x, [l for _, l in sets]); ax.set_ylim(0, 1.12); ax.grid(axis="x", visible=False)
    axes[0].set_ylabel("Share of the natural answer swing")
    ip.label_panels(axes, titles=[t for _, t in panels])
    ip.legend_outside(f, "top", ncol=2)
    ip.finish(f, os.path.join(H3F, "h3_bridgeswap"))

if __name__ == "__main__":
    want = sys.argv[1:] or list(FIGS)
    for name in want:
        FIGS[name](); print("wrote", name)
        plt.close("all")
