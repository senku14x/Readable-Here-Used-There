"""Executive-summary figures, ICLR style, from committed tables only (no forwards, no raw arrays).
Usage: python paper_draft/make_exec_figures.py
"""
import os, sys, json
import numpy as np
sys.path.insert(0, "/root/.claude/skills/iclr-plots/scripts")
import iclrplot as ip; ip.setup()
import matplotlib.pyplot as plt

PROJ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(PROJ, "paper_draft", "figures"); os.makedirs(OUT, exist_ok=True)
T = lambda p: json.load(open(os.path.join(PROJ, p)))
def mci(d): m, (lo, hi) = d["mean"], d["ci"]; return m, m - lo, hi - m
def errbars(es): ms, los, his = zip(*[mci(e) for e in es]); return np.array(ms), np.array([los, his])
EK = dict(elinewidth=0.6, capsize=1.5, ecolor="0.25")

# ---------------------------------------------------------------- Fig E1: instruction and selection
def fig_e1():
    op = T("H1/results/tables/task_state_modulation_orthopanel_tables.json")["J_NP|L51-59"]
    ts = T("H1/results/tables/tagged_selection_evaluate_tables.json")
    f, axes = plt.subplots(1, 2, figsize=(7.2, 3.3)); f.subplots_adjust(wspace=0.32)
    ax = axes[0]
    dirs = [k.split("|", 1)[1] for k in op if k.startswith("I|")]
    xs = np.array([0.5 * (op[f"noswap_shift_M|{p}"]["mean"] - op[f"noswap_shift_N|{p}"]["mean"]) for p in dirs])
    ys = np.array([op[f"I|{p}"]["mean"] for p in dirs])
    r = np.corrcoef(xs, ys)[0, 1]
    for p, x, y in zip(dirs, xs, ys):
        c = ip.HIGHLIGHT if p == "g" else (ip.CATEGORICAL[2] if p.startswith("native") else ip.CATEGORICAL[0])
        ax.scatter([x], [y], s=26 if p == "g" else 14, color=c, edgecolor="white", linewidth=0.4, zorder=3)
    ax.annotate("ĝ (fitted\nmaintain − mention)", (xs[dirs.index("g")], ys[dirs.index("g")]), xytext=(-14, -4),
                textcoords="offset points", ha="right", va="top", fontsize=6.5, color=ip.HIGHLIGHT)
    lim = max(abs(xs).max(), abs(ys).max()) * 1.15
    ax.plot([-lim, lim], [-lim, lim], color="0.6", lw=0.6, ls="--")
    ax.set_xlim(-0.35, lim); ax.set_ylim(-0.6, lim)
    ax.set_xlabel("Shift of the resident readout under the move alone")
    ax.set_ylabel("Transfer interaction $I$ (J-lens, L51–59)")
    ax.text(0.97, 0.06, f"19 directions, $r$ = {r:.3f}\nblue: ĝ-orthogonal, matched dose\ngreen: native directions", transform=ax.transAxes, fontsize=6.3, va="bottom", ha="right", color="0.25")
    ax = axes[1]
    insts = [("J_NP|L48-50", "J-lens\nL48–50"), ("J_NP|L51-59", "J-lens\nL51–59"), ("RESID_P|L51-59", "Plain axis\nL51–59"), ("LOGITS", "Output\nlogits")]
    x = np.arange(len(insts)); w = 0.36
    for k, (key, lab, col) in enumerate([("self", "Pointed source", ip.HIGHLIGHT), ("other", "Unpointed sources", ip.CATEGORICAL[0])]):
        m, err = errbars([ts[i][key] for i, _ in insts])
        ax.bar(x + (k - 0.5) * w, m, w, yerr=err, label=lab, color=col, error_kw=EK)
    cm, cerr = errbars([ts[i]["ctrl"] for i, _ in insts])
    for i in range(len(insts)):
        ax.hlines(cm[i], x[i] - 0.45, x[i] + 0.45, color="0.2", lw=1.0, ls=(0, (2, 1)), label="No pointer (control)" if i == 0 else None)
    ax.set_xticks(x, [l for _, l in insts], fontsize=6.5); ax.axhline(0, color="0.35", lw=0.6)
    ax.set_ylabel("Transfer $C$ of the replaced source"); ax.grid(axis="x", visible=False)
    ax.legend(fontsize=6.3, loc="upper left", frameon=False)
    ip.label_panels(axes, titles=["ĝ is a readout gain", "The tag selects which source transfers"])
    ip.finish(f, os.path.join(OUT, "fig_selection"))

# ---------------------------------------------------------------- Fig E2: readout installed vs answer moved
def fig_e2():
    f, ax = plt.subplots(figsize=(6.0, 5.2)); f.subplots_adjust(bottom=0.26)
    pts = []  # (x readout ratio, y answer share, model, organism, label)
    for model, root, filled in [("Qwen3.6-27B", "", True), ("Qwen3-32B", "replication_qwen3_32b/", False)]:
        r = T(root + "H3/results/tables/computed_sum_consumer_robust_tables.json")
        ref = r["all carriers|off3|report|O_donor"]
        for c, lab in [("O_donor", "source"), ("C_full", "carrier"), ("C_all", "carrier (all blocks)"), ("NEC", "source, carrier clamped"), ("C_rand", "random")]:
            e = r[f"all carriers|off3|report|{c}"]
            pts.append((e["zj"]["mean"] / ref["zj"]["mean"], e["beh"]["mean"] / ref["beh"]["mean"], model, "sum (report)", lab))
        w = T(root + "H3/results/tables/selection_to_behavior_carrier_only_tables.json")
        for c, lab in [("CarrBtoA_all", "carrier"), ("CarrCtoA_all", "carrier"), ("randCarrB", "random")]:
            pts.append((w[c]["R"]["mean"], w[c]["ratio"], model, "word codebook", lab))
    fc = T("writeup/figure1_candidate_data.json")["models"]
    for model in ["Qwen3.6-27B", "Qwen3-32B"]:
        v = fc[model]["visible"]
        for c, lab in [("S_donor0", "source"), ("C_all", "carrier"), ("NEC_all", "source, carrier clamped")]:
            pts.append((v[c]["readout_ratio"], v[c]["answer_ratio"], model, "two-hop facts", lab))
    marks = {"sum (report)": "o", "two-hop facts": "s", "word codebook": "^"}
    cols = {"sum (report)": ip.CATEGORICAL[0], "two-hop facts": ip.HIGHLIGHT, "word codebook": ip.CATEGORICAL[2]}
    seen = set()
    for x, y, model, org, lab in pts:
        filled = model == "Qwen3.6-27B"
        key = (org, model)
        ax.scatter([x], [y], marker=marks[org], s=30, facecolor=cols[org] if filled else "white",
                   edgecolor=cols[org], linewidth=0.9, zorder=3,
                   label=(f"{org}, {model}" if key not in seen else None)); seen.add(key)
    ax.plot([0, 1.05], [0, 1.05], color="0.6", lw=0.6, ls="--")
    ax.annotate("source donors", (1.0, 1.0), xytext=(-70, 4), textcoords="offset points", fontsize=7, color="0.25", va="center")
    ax.text(0.97, 0.36, "carrier donors:\nreadout fully installed,\nanswer barely moved", ha="right", va="bottom", fontsize=7, color="0.25")
    ax.text(0.05, 0.86, "source donor,\ncarrier held at clean", ha="left", va="center", fontsize=7, color="0.25")
    ax.annotate("random writes", (0.07, 0.0), xytext=(40, 12), textcoords="offset points", fontsize=7, color="0.25",
                arrowprops=dict(arrowstyle="-", color="0.5", lw=0.6))
    ax.set_xlim(-0.06, 1.14); ax.set_ylim(-0.06, 1.1)
    ax.set_xlabel("Donor readout installed at the carrier (ratio to the source donor's readout)")
    ax.set_ylabel("Answer moved (share of the source donor's effect)")
    ax.legend(fontsize=6.8, loc="upper center", bbox_to_anchor=(0.5, -0.14), ncol=3, frameon=False, columnspacing=1.2)
    ip.finish(f, os.path.join(OUT, "fig_readout_vs_leverage"))

# ---------------------------------------------------------------- Fig E3: copy used when the source is hidden
def fig_e3():
    fc = T("writeup/figure1_candidate_data.json")["models"]
    f, ax = plt.subplots(figsize=(6.0, 3.8))
    for idx, model in enumerate(["Qwen3.6-27B", "Qwen3-32B"]):
        a = fc[model]["availability"]; ref = a["natural_answer_contrast_nats"]
        xs = np.array([0, 1]) + 2.6 * idx
        items = list(a["visible_by_item_nats"])
        for it, jit in zip(items, np.linspace(-0.05, 0.05, len(items))):
            ax.plot(xs + jit, [a["visible_by_item_nats"][it] / ref, a["unavailable_by_item_nats"][it] / ref], color="0.66", lw=0.55, alpha=0.7, marker="o", ms=2.2)
        means = [a["visible_ratio"], a["unavailable_ratio"]]
        ax.plot(xs, means, color=ip.HIGHLIGHT, lw=1.3, marker="D", ms=4.5, zorder=4)
        for x, y in zip(xs, means):
            ax.annotate(f"{y:.2f}", (x, y), xytext=(8, -1), textcoords="offset points", fontsize=7, va="center")
        ax.text(xs.mean(), 1.02, f"{model} ({a['n_items']} items)", transform=ax.get_xaxis_transform(), ha="center", fontsize=7.5)
    ax.set_xticks([0, 1, 2.6, 3.6], ["Clue\nvisible", "Clue\nunavailable", "Clue\nvisible", "Clue\nunavailable"], fontsize=7)
    ax.set_xlim(-0.3, 4.0); ax.set_ylim(-0.02, 1.15); ax.axhline(0, color="0.6", lw=0.6)
    ax.set_ylabel("Carrier-identity effect on the answer /\nnatural identity contrast"); ax.grid(axis="x", visible=False)
    ip.finish(f, os.path.join(OUT, "fig_source_hidden"))

# ---------------------------------------------------------------- Fig E4: plane vs complement at the question turn
def fig_e4():
    q = T("H3/results/tables/two_hop_qsplit_tables.json")["rows"]
    rows = [("q_full_pre", "full\nresidual"), ("q_plane_pre", "naming\nplane"), ("q_rem_pre", "complement\n(plane pinned)"),
            ("q_rand_pre", "random\nplane"), ("q_rem_rand_pre", "compl. of\nrandom plane"), ("int_q32", "paper's\ncoord. swap")]
    cols = ["0.3", ip.CATEGORICAL[0], ip.HIGHLIGHT, "0.75", "#f4a582", "0.55"]
    f, axes = plt.subplots(1, 2, figsize=(8.0, 3.6), gridspec_kw=dict(width_ratios=[2.4, 1])); f.subplots_adjust(wspace=0.35, bottom=0.22)
    ax = axes[0]; x = np.arange(len(rows))
    m, err = errbars([q[k]["margin_seq"] for k, _ in rows])
    ax.bar(x, m, 0.66, yerr=err, color=cols, error_kw=EK)
    for i, (k, _) in enumerate(rows):
        per = list(q[k]["per_item_margin"].values())
        ax.scatter(np.full(len(per), x[i]) + np.linspace(-0.18, 0.18, len(per)), per, s=6, color="0.15", alpha=0.55, zorder=3)
        ax.annotate(f"{q[k]['flips_seq']}/48 flips", (x[i], m[i] + err[1][i] + 0.4), ha="center", fontsize=6.5, color="0.2")
        ax.annotate(f"{q[k]['share_of_q_full_pre']:.2f}", (x[i], -1.0), ha="center", fontsize=6.8, color="0.35")
    ax.set_xticks(x, [l for _, l in rows], fontsize=6.8); ax.axhline(0, color="0.35", lw=0.6)
    ax.set_ylabel("Δ answer margin (nats)"); ax.grid(axis="x", visible=False)
    ax.set_ylim(-1.8, 15.8); ax.set_xlim(-1.05, 5.6); ax.text(-1.0, -1.0, "share", fontsize=6.8, color="0.35")
    ax = axes[1]
    m2, err2 = errbars([q[k]["J_qpre_readout_shift_L51_59"] for k, _ in rows])
    ax.bar(x, m2, 0.66, yerr=err2, color=cols, error_kw=EK)
    ax.set_xticks(x, ["full", "plane", "compl.", "rand.", "compl.\nof rand.", "swap"], fontsize=6.5)
    ax.axhline(0, color="0.35", lw=0.6); ax.grid(axis="x", visible=False)
    ax.set_ylabel("Readout of the swapped\nintermediate (J-lens, L51–59)")
    ip.label_panels(axes, titles=["Answer effect, blocks 36–62, fp32 exact write", "Readout installed"])
    ip.finish(f, os.path.join(OUT, "fig_question_split"))

# ---------------------------------------------------------------- Fig M1: organism-and-sites board
def fig_m1():
    """Schematic of the two-hop rendering (Barcelona|C2, 108 tokens) with the three sites and the interventions."""
    f, ax = plt.subplots(figsize=(8.0, 3.2))
    spans = [("system/template", 0, 8, "0.85"), ("clue span (source)", 8, 16, ip.CATEGORICAL[0]), ("instruction + user copy of carrier", 16, 64, "0.85"),
             ("copied carrier (assistant, teacher-forced)", 64, 80, ip.HIGHLIGHT), ("question turn", 80, 107, ip.CATEGORICAL[2]), ("answer", 107, 108, "0.2")]
    for lab, a, b, c in spans:
        ax.barh(0, b - a, left=a, height=0.55, color=c, edgecolor="white", linewidth=0.6)
    ax.text(12, 0.45, "source\n8–16", ha="center", va="bottom", fontsize=6.5, color=ip.CATEGORICAL[0])
    ax.text(72, 0.45, "carrier\n64–80", ha="center", va="bottom", fontsize=6.5, color=ip.HIGHLIGHT)
    ax.text(93.5, 0.45, "question\n80–107", ha="center", va="bottom", fontsize=6.5, color=ip.CATEGORICAL[2])
    ax.text(107.5, 0.45, "scored\n107", ha="center", va="bottom", fontsize=6.5, color="0.2")
    ax.text(40, -0.42, "instruction + the user's copy of the carrier text (16–64)", ha="center", va="top", fontsize=5.8, color="0.35")
    rows = [(-0.9, "source donor", [(8, 16)], ip.CATEGORICAL[0]), (-1.4, "carrier donor", [(64, 80)], ip.HIGHLIGHT),
            (-1.9, "source donor, carrier held at clean", [(8, 16), (64, 80)], "0.4"), (-2.4, "question-turn donor (scoring position excluded)", [(80, 106)], ip.CATEGORICAL[2])]
    for y, lab, segs, c in rows:
        for a, b in segs:
            ax.barh(y, b - a, left=a, height=0.3, color=c if "held" not in lab or a == 8 else "white", edgecolor=c, linewidth=0.8, hatch=None if a == 8 or "held" not in lab else "////")
        ax.text(-1.5, y, lab, ha="right", va="center", fontsize=6.2)
    ax.text(-1.5, -3.0, "each row: a norm-matched random write at the same site is its control", ha="right", va="center", fontsize=5.8, color="0.35")
    ax.set_xlim(-62, 110); ax.set_ylim(-3.3, 1.2); ax.set_yticks([]); ax.grid(visible=False)
    ax.set_xlabel("Token index in the rendered conversation (Qwen chat template, thinking disabled)")
    for s in ["left", "top", "right"]: ax.spines[s].set_visible(False)
    ax.set_xticks([0, 8, 16, 64, 80, 107])
    ip.finish(f, os.path.join(OUT, "fig_setup"))

if __name__ == "__main__":
    for fn in [fig_e1, fig_e2, fig_e3, fig_e4, fig_m1]:
        fn(); plt.close("all"); print("wrote", fn.__name__)

