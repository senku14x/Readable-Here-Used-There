"""Consolidated figure for the question-turn ladder write-up (H3/results/reports/two_hop_question_turn_ladder.md), built only from the
committed tables of Stage 2 (Amendment 7), probe3 (Amendment 8) and probe4 (Amendment 9). ICLR style (iclr-plots skill), full width.
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

# (d) relation transfer: what the question-turn state carries
ax = axes[3]; c3 = P3["c"]; p2 = P4["part2"]["language_question"]
bars = [("Donor's\nlanguage", c3["f_L"], cat[0]), ("Donor's\ncapital", c3["capital_push_in_language_question_over_native_capital_push"], cat[2]),
        ("Country\nplane only", p2["f_ctry"], cat[1]), ("City\nplane only", p2["f_city"], cat[3])]
for i, (lab, v, c) in enumerate(bars): ax.bar(i, v, color=c, width=0.7)
ax.errorbar(0, c3["f_L"], yerr=[[c3["f_L"] - c3["f_L_ci"][0]], [c3["f_L_ci"][1] - c3["f_L"]]], color="k", lw=0.8, capsize=2)
ax.set_xticks(range(4)); ax.set_xticklabels([b[0] for b in bars], fontsize=5.5); ax.set_ylim(0, 1.05)
ax.set(ylabel="Fraction of the reference push"); ax.axvline(1.5, color=grey, lw=0.6, ls=":")
ax.text(0.5, 1.0, "vs each answer's native push", ha="center", va="bottom", fontsize=5.5, color="#555555"); ax.text(2.5, 1.0, "vs the transfer push", ha="center", va="bottom", fontsize=5.5, color="#555555")
ip.label_panels(axes, titles=["Removal at the question", "Answer vs intermediate", "Clamp at the answer", "Transfer to another question"])
ip.finish(fig, os.path.join(FIG, "h3_question_turn_ladder"))
print("wrote", os.path.join(FIG, "h3_question_turn_ladder.png"))
