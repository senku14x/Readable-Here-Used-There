"""Backup figures for the application write-up, from committed tables and raw arrays only. Usage: python paper_draft/make_backup_figures.py"""
import os, sys, json
import numpy as np
sys.path.insert(0, "/root/.claude/skills/iclr-plots/scripts")
import iclrplot as ip; ip.setup()
import matplotlib.pyplot as plt
PROJ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(PROJ, "paper_draft", "figures_backup"); os.makedirs(OUT, exist_ok=True)
T = lambda p: json.load(open(os.path.join(PROJ, p)))
EK = dict(elinewidth=0.6, capsize=1.5, ecolor="0.25")
def mci(d): m, (lo, hi) = d["mean"], d["ci"]; return m, m - lo, hi - m
def errbars(es): ms, los, his = zip(*[mci(e) for e in es]); return np.array(ms), np.array([los, his])

# B1: moves but does not flip — Δ log P(own) and Δ log P(donor), sum organism (values from computed_sum_consumer_robust.md, "Effect sizes beyond flips")
def b1():
    rows = [("source donor", -10.530, 10.681, -1.083, 2.797), ("carrier donor", -0.004, 1.747, -0.072, 0.630), ("carrier random", -0.000, 0.045, 0.001, 0.022)]
    f, axes = plt.subplots(1, 2, figsize=(6.8, 3.0), sharey=False); f.subplots_adjust(wspace=0.35)
    for ax, (cons, io, idn) in zip(axes, [("report", 1, 2), ("parity", 3, 4)]):
        x = np.arange(3); w = 0.36
        ax.bar(x - w/2, [r[io] for r in rows], w, color=ip.CATEGORICAL[0], label="Δ log P(own answer)")
        ax.bar(x + w/2, [r[idn] for r in rows], w, color=ip.HIGHLIGHT, label="Δ log P(donor answer)")
        for i, r in enumerate(rows):
            ax.annotate(f"{r[io]:+.2f}", (i - w/2, r[io] + (0.3 if r[io] >= 0 else -0.9)), ha="center", fontsize=6)
            ax.annotate(f"{r[idn]:+.2f}", (i + w/2, r[idn] + 0.3), ha="center", fontsize=6)
        ax.set_xticks(x, [r[0] for r in rows], fontsize=7); ax.axhline(0, color="0.35", lw=0.6); ax.grid(axis="x", visible=False)
        ax.set_ylabel("Δ log-probability (nats), renormalised over candidates")
    axes[0].set_ylim(-12.5, 13); axes[1].set_ylim(-2, 3.6); axes[0].legend(fontsize=6.5, loc="lower right")
    ip.label_panels(axes, titles=["Report consumer", "Parity consumer"])
    ip.finish(f, os.path.join(OUT, "B1_logprob_moves_not_flips"))

# B2: source hidden, sums — candidate wins and greedy breakdown (from tables + raw_nosource2.npz)
def b2():
    q = T("H3/results/tables/query_local_workspace_tables.json")
    conds = [("C_from_S", "carrier from\nrun with S", "flips_own"), ("C_from_S2", "carrier from\nrun with S2", "flips_donor"), ("C_rand_ns", "carrier\nrandom", "flips_own"), ("Q_from_S", "question positions\nfrom S (control)", "flips_own")]
    wins = [q[f"nosource2|report|{c}"][k] for c, _, k in conds]
    z = np.load(os.path.join(PROJ, "H3/outputs/query_local_workspace/raw_nosource2.npz")); m = json.load(open(os.path.join(PROJ, "H3/outputs/query_local_workspace/meta_nosource2.json")))
    dig = {"seven":"7","eight":"8","nine":"9","ten":"10","eleven":"11","twelve":"12","thirteen":"13","fourteen":"14"}
    cat = {"complete word":0, "complete digit":0, "leading digit":0, "'hidden' echoed":0, "other / partial":0}
    for c, info in m["cells"].items():
        g = str(np.asarray(z[f"{c}|report|C_from_S|greedy"]).ravel()[0]); s = info["sum"]
        if g.lower() == s: cat["complete word"] += 1
        elif g == dig[s]: cat["complete digit"] += 1
        elif g == "1" and len(dig[s]) == 2: cat["leading digit"] += 1
        elif g.lower() == "hidden": cat["'hidden' echoed"] += 1
        else: cat["other / partial"] += 1
    f, axes = plt.subplots(1, 2, figsize=(6.8, 3.0), gridspec_kw=dict(width_ratios=[1.3, 1])); f.subplots_adjust(wspace=0.4)
    ax = axes[0]; x = np.arange(len(conds))
    ax.bar(x, wins, 0.62, color=[ip.HIGHLIGHT, ip.CATEGORICAL[0], ip.NEUTRAL, ip.CATEGORICAL[2]])
    for i, wv in enumerate(wins): ax.annotate(f"{wv}/32", (i, wv + 0.6), ha="center", fontsize=7)
    ax.axhline(4, color="0.45", lw=0.8, ls="--"); ax.text(3.45, 6.4, "clean placeholder: 4/32", fontsize=6, ha="right", color="0.35")
    ax.set_xticks(x, [l for _, l, _ in conds], fontsize=6.5); ax.set_ylim(0, 36); ax.set_ylabel("cells where the installed sum wins the candidate set"); ax.grid(axis="x", visible=False)
    ax = axes[1]; ks = list(cat); vs = [cat[k] for k in ks]
    ax.barh(np.arange(len(ks))[::-1], vs, 0.6, color=[ip.HIGHLIGHT, ip.HIGHLIGHT, ip.CATEGORICAL[0], ip.NEUTRAL, ip.NEUTRAL])
    for i, v in enumerate(vs): ax.annotate(str(v), (v + 0.4, len(ks) - 1 - i), va="center", fontsize=7)
    ax.set_yticks(np.arange(len(ks))[::-1], ks, fontsize=6.5); ax.set_xlim(0, 18); ax.set_xlabel("greedy decode under the installed carrier (32 cells)"); ax.grid(axis="y", visible=False)
    ip.label_panels(axes, titles=["Scored candidate set", "Greedy decode"])
    ip.finish(f, os.path.join(OUT, "B2_source_hidden_sums"))

# B3: carrier share by organism, hybrid vs dense (tables)
def b3():
    def share(root, org):
        if org == "sums":
            r = T(root + "H3/results/tables/computed_sum_consumer_robust_tables.json"); return r["all carriers|off3|report|C_full"]["beh"]["mean"] / r["all carriers|off3|report|O_donor"]["beh"]["mean"]
        if org == "facts":
            t = T(root + "H3/results/tables/two_hop_organism_tables.json"); return t["full|C_full"]["share"]
        c = T(root + "H3/results/tables/selection_to_behavior_carrier_only_tables.json"); return max(c["CarrBtoA_all"]["ratio"], c["CarrCtoA_all"]["ratio"])
    orgs = ["sums", "facts", "words"]; hy = [share("", o) for o in orgs]; de = [share("replication_qwen3_32b/", o) for o in orgs]
    f, ax = plt.subplots(figsize=(4.6, 3.0)); x = np.arange(3); w = 0.36
    ax.bar(x - w/2, hy, w, color=ip.HIGHLIGHT, label="Qwen3.6-27B (hybrid)"); ax.bar(x + w/2, de, w, color=ip.CATEGORICAL[0], label="Qwen3-32B (dense)")
    for i in range(3):
        ax.annotate(f"{hy[i]:.2f}", (i - w/2, hy[i] + 0.008), ha="center", fontsize=6.5); ax.annotate(f"{de[i]:.2f}", (i + w/2, de[i] + 0.008), ha="center", fontsize=6.5)
    ax.set_xticks(x, ["sums (report)", "two-hop facts", "word codebook"]); ax.set_ylim(0, 0.36); ax.grid(axis="x", visible=False)
    ax.set_ylabel("carrier donor's share of the source donor's answer effect"); ax.legend(fontsize=6.5)
    ip.finish(f, os.path.join(OUT, "B3_carrier_share_by_organism_and_model"))

# B4: priming compact + rank-1 surfacing (natural_modulation evaluate tables)
def b4():
    d = T("H1/results/tables/natural_modulation_evaluate_tables.json")
    conds = [("maintain", "maintain"), ("plain_mention", "plain\nmention"), ("mention", "mention\n(control)"), ("absent", "absent")]
    f, axes = plt.subplots(1, 3, figsize=(7.4, 2.8), gridspec_kw=dict(width_ratios=[1, 1, 0.9])); f.subplots_adjust(wspace=0.45)
    for ax, win in zip(axes[:2], ["L48-50", "L51-59"]):
        m, err = errbars([d[f"levels|J_NP (bf16 path)|{win}"][c] for c, _ in conds])
        ax.bar(np.arange(4), m, 0.62, yerr=err, color=[ip.HIGHLIGHT, ip.CATEGORICAL[0], ip.CATEGORICAL[0], ip.BASELINE], error_kw=EK)
        ax.set_xticks(np.arange(4), [l for _, l in conds], fontsize=6.5); ax.axhline(0, color="0.35", lw=0.6); ax.grid(axis="x", visible=False)
        ax.set_ylabel("J-lens presence of the word" if win == "L48-50" else None)
    ax = axes[2]
    pr = d.get("prominence|L24-59", {})
    rates = []
    for c, _ in conds:
        v = pr.get(c, {}); r = v.get("rank1_anywhere_rate", v.get("rank1_rate", None)) if isinstance(v, dict) else None
        rates.append(r)
    if any(r is None for r in rates): rates = [0.56, 0.03, 0.03, 0.00]  # natural_modulation_evaluate.md, prominence over L24–59
    ax.bar(np.arange(4), rates, 0.62, color=[ip.HIGHLIGHT, ip.CATEGORICAL[0], ip.CATEGORICAL[0], ip.BASELINE])
    for i, r in enumerate(rates): ax.annotate(f"{r:.2f}", (i, r + 0.02), ha="center", fontsize=6.5)
    ax.set_xticks(np.arange(4), [l for _, l in conds], fontsize=6.5); ax.set_ylim(0, 0.7); ax.grid(axis="x", visible=False); ax.set_ylabel("rank-1 surfacing rate, blocks 24–59")
    ip.label_panels(axes, titles=["Blocks 48–50", "Blocks 51–59", "Top of the vocabulary"])
    ip.finish(f, os.path.join(OUT, "B4_priming_and_surfacing"))

# B5: qsplit hybrid vs dense, shares (dense unlabelled: gate 4 failed)
def b5():
    H = T("H3/results/tables/two_hop_qsplit_tables.json")["rows"]; D = T("replication_qwen3_32b/H3/results/tables/two_hop_qsplit_tables.json")["rows"]
    rows = [("q_full_pre", "full"), ("q_plane_pre", "naming\nplane"), ("q_rem_pre", "complement"), ("q_rand_pre", "random\nplane"), ("q_rem_rand_pre", "compl. of\nrandom"), ("int_q32", "paper's\nswap")]
    f, ax = plt.subplots(figsize=(6.0, 3.0)); x = np.arange(len(rows)); w = 0.36
    ax.bar(x - w/2, [H[k]["share_of_q_full_pre"] for k, _ in rows], w, color=ip.HIGHLIGHT, label="Qwen3.6-27B: pre-specified reading taken (complement dominant)")
    ax.bar(x + w/2, [D[k]["share_of_q_full_pre"] for k, _ in rows], w, color="white", edgecolor=ip.CATEGORICAL[0], hatch="////", label="Qwen3-32B: strength gate failed (0.20 of ceiling < 0.30), no label assigned")
    for i, (k, _) in enumerate(rows):
        ax.annotate(f"{H[k]['share_of_q_full_pre']:.2f}", (i - w/2, H[k]["share_of_q_full_pre"] + 0.02), ha="center", fontsize=6)
        ax.annotate(f"{D[k]['share_of_q_full_pre']:.2f}", (i + w/2, D[k]["share_of_q_full_pre"] + 0.02), ha="center", fontsize=6, color=ip.CATEGORICAL[0])
    ax.set_xticks(x, [l for _, l in rows], fontsize=6.5); ax.set_ylim(0, 1.2); ax.grid(axis="x", visible=False)
    ax.set_ylabel("share of the full question-turn donor's answer effect"); ip.legend_outside(f, "top", ncol=1)
    ip.finish(f, os.path.join(OUT, "fig_question_split_dense"))

# B6: position decomposition, stacked single-position swaps vs the all-positions swap (sequence endpoint)
def b6():
    f, axes = plt.subplots(1, 2, figsize=(6.4, 3.0), sharey=True); f.subplots_adjust(wspace=0.15)
    for ax, (path, title) in zip(axes, [("H3/results/tables/two_hop_bridgeswap_tables.json", "Qwen3.6-27B"), ("replication_qwen3_32b/H3/results/tables/two_hop_bridgeswap_tables.json", "Qwen3-32B")]):
        B = T(path); seg = [("int_clue", "clue span", ip.CATEGORICAL[0]), ("int_carr", "copied carrier", ip.HIGHLIGHT), ("int_q", "question turn", ip.CATEGORICAL[2])]
        bottom = 0
        for k, lab, c in seg:
            v = B[k]["seq"]["margin"]["mean"]; ax.bar(0, v, 0.55, bottom=bottom, color=c, label=lab if ax is axes[0] else None); ax.annotate(f"{v:+.2f}", (0, bottom + v/2), ha="center", va="center", fontsize=6.5, color="white"); bottom += v
        allv = B["int_tail"]["seq"]["margin"]["mean"]; ax.bar(1, allv, 0.55, color="0.35"); ax.annotate(f"{allv:+.2f}", (1, allv/2), ha="center", va="center", fontsize=6.5, color="white")
        ax.annotate(f"sum {bottom:.2f}", (0, bottom + 0.3), ha="center", fontsize=6.5)
        ax.set_xticks([0, 1], ["single-position swaps,\nstacked", "all positions\n(the paper's swap)"], fontsize=6.5); ax.grid(axis="x", visible=False); ax.set_title(title, fontsize=8, loc="left")
    axes[0].set_ylabel("intermediate-swap Δ margin (nats), sequence endpoint"); axes[0].legend(fontsize=6.5, loc="upper left")
    ip.finish(f, os.path.join(OUT, "B6_position_additivity"))

# B7: exact question clamp (clampfix32): naming plane vs norm-matched orthogonal control, report and parity
def b7():
    c = T("H3/results/tables/query_local_workspace_clampfix32_tables.json")
    rows = [("NEC", "no clamp"), ("NEC_Qclamp_noans", "naming-plane\nclamp"), ("NEC_Qclamp_noans_perpm", "orthogonal plane,\nnorm-matched")]
    f, axes = plt.subplots(1, 2, figsize=(6.6, 3.0)); f.subplots_adjust(wspace=0.35)
    for ax, cons in zip(axes, ["report", "parity"]):
        m, err = errbars([c[f"{cons}|{k}"]["margin"] for k, _ in rows])
        ax.bar(np.arange(3), m, 0.6, yerr=err, color=["0.4", ip.HIGHLIGHT, ip.CATEGORICAL[0]], error_kw=EK)
        for i, (k, _) in enumerate(rows): ax.annotate(f"{c[f'{cons}|{k}']['flips']}/32", (i, m[i] + err[1][i] + (0.4 if cons == "report" else 0.1)), ha="center", fontsize=6.5)
        ax.set_xticks(np.arange(3), [l for _, l in rows], fontsize=6); ax.grid(axis="x", visible=False); ax.set_ylabel("answer margin toward the donor (nats)")
    ip.label_panels(axes, titles=["Report: 19.27 → 11.84 (−38.5 %), control 19.24", "Parity: unchanged under either clamp"])
    ip.finish(f, os.path.join(OUT, "B7_question_clamp_fp32"))

# B8: reconstruction at the question under the carrier clamp (query_local_workspace queryread)
def b8():
    q = T("H3/results/tables/query_local_workspace_tables.json")
    conds = [("O_donor", "source donor"), ("NEC", "source donor,\ncarrier held at clean"), ("C_full", "carrier donor")]
    f, ax = plt.subplots(figsize=(4.8, 3.0)); x = np.arange(3); w = 0.36
    for k, (site, lab) in enumerate([("zc", "at the carrier"), ("zq", "at the question")]):
        m, err = errbars([q[f"queryread|report|{c}"][site] for c, _ in conds]); ax.bar(x + (k - 0.5) * w, m, w, yerr=err, label=lab, color=ip.CATEGORICAL[k], error_kw=EK)
        for i in range(3): ax.annotate(f"{m[i]:.2f}", (x[i] + (k - 0.5) * w, m[i] + err[1][i] + 0.03), ha="center", fontsize=6)
    ax.set_xticks(x, [l for _, l in conds], fontsize=6.5); ax.axhline(0, color="0.35", lw=0.6); ax.grid(axis="x", visible=False)
    ax.set_ylabel("donor-sum J-lens shift, blocks 51–59"); ax.legend(fontsize=6.5)
    ip.finish(f, os.path.join(OUT, "B8_reconstruction_at_question"))

if __name__ == "__main__":
    for fn in [b1, b2, b3, b4, b5, b6, b7, b8]:
        try: fn(); print("wrote", fn.__name__)
        except Exception as e: print("FAILED", fn.__name__, repr(e))
        plt.close("all")
