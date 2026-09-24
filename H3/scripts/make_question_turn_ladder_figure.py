"""Consolidated figure for the question-turn ladder write-up (H3/results/reports/two_hop_question_turn_ladder.md), built only from the
committed tables of Stage 2 (Amendment 7), probe3 (Amendment 8), probe4 (Amendment 9) and probe5 (Amendment 10; panel d is its Part B
alone, replotted at the 2026-09-24 freeze in place of the Amendment 8/9 panel that showed the withdrawn "country dominant" reading).
No model forwards. ICLR style (iclr-plots skill), full width.
Writes H3/results/figures/h3_question_turn_ladder.{pdf,png}. Usage: make_question_turn_ladder_figure.py"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "..", "common", "scripts"))
import numpy as np
import registry as R
for _p in (os.path.join(R.PROJECT, ".claude", "skills", "iclr-plots", "scripts"), "/workspace/.claude/skills/iclr-plots/scripts"): sys.path.insert(0, _p)
import iclrplot as ip
import matplotlib.pyplot as plt

TAB = R.out_dir("H3", "results", "tables"); FIG = R.out_dir("H3", "results", "figures")
S2 = json.load(open(os.path.join(TAB, "two_hop_stage2_tables.json"))); P3 = json.load(open(os.path.join(TAB, "two_hop_probe3_tables.json"))); P4 = json.load(open(os.path.join(TAB, "two_hop_probe4_tables.json")))
P5 = json.load(open(os.path.join(TAB, "two_hop_probe5_tables.json")))
adm = S2["admitted"]; rows = S2["rows"]; full = np.array([rows["q_full_pre"]["per_item_margin"][nm] for nm in adm])
rng = np.random.default_rng(20260907)


def share_ci(row):
    """share of q_full_pre on the admitted items with a cluster-bootstrap 95 % interval (2 000 resamples of items)."""
    v = np.array([rows[row]["per_item_margin"][nm] for nm in adm]); pt = v.mean() / full.mean(); bs = []
    for _ in range(2000):
        i = rng.integers(0, len(adm), len(adm)); bs.append(v[i].mean() / full[i].mean())
    return pt, np.percentile(bs, 2.5), np.percentile(bs, 97.5)


ip.setup()
fig, axes = ip.figure(width="full", nrows=2, ncols=2, aspect=0.68); axes = axes.ravel()
cat = ip.palette("categorical", 6); grey = "#9e9e9e"

# (a) removing the best k lens directions vs k random directions, on the question tokens
ax = axes[0]; ks = [2, 8, 25, 64]
for lab, fmt, col in (("Best k lens directions removed", "q_J{k}rem_pre", cat[0]), ("k random directions removed", "q_rand{k}rem_pre", grey)):
    pts = [share_ci(fmt.format(k=k)) for k in ks]
    ip.line_ci(ax, ks, [p[0] for p in pts], [p[1] for p in pts], [p[2] for p in pts], label=lab, color=col)
ax.set_xscale("log"); ax.set_xticks(ks); ax.set_xticklabels([str(k) for k in ks]); ax.minorticks_off(); ax.set_ylim(0, 1.05)
ax.set(xlabel="k", ylabel="Share of the question-turn effect kept"); ax.legend(loc="lower left", fontsize=6)

# (b) the answer's readable directions vs the intermediate's
ax = axes[1]; labs = ["Intermediate\nonly", "Answer\nonly", "Intermediate\nremoved", "Answer\nremoved", "Both\nremoved"]
vals = [share_ci("q_plane_pre"), share_ci("q_ansplane_pre"), share_ci("q_rem_pre"), share_ci("q_ansrem_pre")]
d = P3["rows_ab"]["q_bothrem_pre"]; vals.append((d["share"], d["share_ci"][0], d["share_ci"][1]))
cols = [cat[1], cat[2], cat[1], cat[2], cat[3]]
for i, (v, c) in enumerate(zip(vals, cols)):
    ax.bar(i, v[0], color=c, alpha=0.55 if i >= 2 else 1.0, width=0.7); ax.errorbar(i, v[0], yerr=[[v[0] - v[1]], [v[2] - v[0]]], color="k", lw=0.8, capsize=2)
ax.set_xticks(range(5)); ax.set_xticklabels(labs, fontsize=5.5); ax.set_ylim(0, 1.05); ax.set(ylabel="Share of the question-turn effect")

# (c) holding readable content fixed at the answer position, and where the surviving part enters
ax = axes[2]; p4 = P4["rows_ab"]
seq = [("Best 25\nremoved", share_ci("q_J25rem_pre"), cat[0]), ("+ partial\nclamp at s", share_ci("q_J25rem_pre_cc"), cat[4]),
       ("+ verified\nclamp, all\nanswer pos.", (p4["q_J25rem_pre_ccsA"]["share"], *p4["q_J25rem_pre_ccsA"]["share_ci"]), cat[5]),
       ("  block-63\n  read cut", (p4["q_J25rem_pre_ccsA_m63A"]["share"], *p4["q_J25rem_pre_ccsA_m63A"]["share_ci"]), cat[5]),
       ("  block-63\n  read only", (p4["q_J25rem_pre_sfullA"]["share"], *p4["q_J25rem_pre_sfullA"]["share_ci"]), cat[5]),
       ("Random\nclamp", (p4["q_J25rem_pre_ccsrA"]["share"], *p4["q_J25rem_pre_ccsrA"]["share_ci"]), grey)]
for i, (lab, v, c) in enumerate(seq):
    ax.bar(i, v[0], color=c, alpha=0.55 if i in (3, 4) else 1.0, hatch="//" if i in (3, 4) else None, width=0.7, edgecolor="white")
    ax.errorbar(i, v[0], yerr=[[v[0] - v[1]], [v[2] - v[0]]], color="k", lw=0.8, capsize=2)
ax.set_xticks(range(len(seq))); ax.set_xticklabels([s[0] for s in seq], fontsize=5); ax.set_ylim(0, 1.05); ax.set(ylabel="Share of the question-turn effect")

# (d) cross-question transfer, decomposed against the receiving question's answer geometry (Amendment 10 Part B only).
# Each bar is the push toward the receiving question's donor answer from writing one component of the transferred change,
# as a fraction of the full transferred change's push (the dashed line at 1); points are the seven city pairs.
ax = axes[3]; pB = P5["partB"]
groups = [("Language question\nreceives", pB["language_question"], "lang"), ("Capital question\nreceives (mirror)", pB["capital_question_mirror"], "cap")]
comps = [("Receiving answer's plane", None, cat[2], None), ("Country plane", "ctry", cat[1], None),
         ("Country $\\perp$ receiving answer", "ctry_perp", cat[1], "////"), ("Matched random plane", "rand2b", grey, None)]
bw = 0.19
for gi, (glab, g, own) in enumerate(groups):
    for ci_, (clab, key, col, hatch) in enumerate(comps):
        e = g[key or own]; x = gi + (ci_ - 1.5) * bw
        ax.bar(x, e["share"], bw * 0.92, color=col, alpha=0.5 if hatch else 1.0, hatch=hatch, edgecolor="white", lw=0, label=clab if gi == 0 else None)
        ax.errorbar(x, e["share"], yerr=[[e["share"] - e["ci"][0]], [e["ci"][1] - e["share"]]], color="k", lw=0.8, capsize=1.5)
        pp = np.asarray(e["per_pair"], float); ax.scatter(x + np.linspace(-0.045, 0.045, len(pp)), pp, s=2.5, color="k", alpha=0.55, lw=0, zorder=3)
        if key == "ctry_perp": ax.annotate(f"{e['share']:.2f}", (x, e["ci"][1]), xytext=(0, 2), textcoords="offset points", ha="center", va="bottom", fontsize=5.5)
ip.reference_line(ax, y=1.0, label="Full transferred change")
ax.set_xticks(range(len(groups))); ax.set_xticklabels([g[0] for g in groups], fontsize=5.5); ax.set_xlim(-0.5, 1.5); ax.set_ylim(0, 1.42); ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
ax.set(ylabel="Fraction of the transfer push"); ax.legend(loc="upper center", fontsize=5, ncol=2, frameon=False, columnspacing=0.8, handlelength=1.4)
ip.label_panels(axes, titles=["Removal at the question", "Answer vs intermediate", "Clamp at the answer", "Transfer to another question"])
ip.finish(fig, os.path.join(FIG, "h3_question_turn_ladder"))
print("wrote", os.path.join(FIG, "h3_question_turn_ladder.png"))
