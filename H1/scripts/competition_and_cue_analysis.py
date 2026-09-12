"""Analysis for H1.8 competition series and mid-carrier cue (single scoring pass)."""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "..", "common", "scripts"))
import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
import registry as R, stats as S

OUT = os.path.join(R.out_dir("H1", "outputs"), "competition_and_cue"); RES = os.path.join(R.out_dir("H1", "results")); FIG = os.path.join(RES, "figures")
META = json.load(open(os.path.join(OUT, "meta.json"))); Z = np.load(os.path.join(OUT, "raw.npz"))
COLS = META["columns"]; CIX = {w: i for i, w in enumerate(COLS)}; DONOR = META["donor"]; KS = META["ks"]; CARRIERS = META["carriers"]; TRIPLES = META["triples"]
WINDOWS = {"L48-50": [48, 49, 50], "L51-59": list(range(51, 60))}


def margin(tag, j, X, win, inst):
    if inst == "J_NP":
        z = Z[f"{tag}|z"].astype(np.float32)[win]; return float((z[:, :, CIX[DONOR[X]]] - z[:, :, CIX[X]]).mean())
    if inst == "RESID_P": return float(Z[f"{tag}|p_pair{j}"][win].mean())
    return float(Z[f"{tag}|lp_margin{j}"].mean())


def C(base, j, win, inst):
    X = META["cells"][base]["words"][j]
    return margin(f"{base}|swap{j}", j, X, win, inst) - margin(f"{base}|clean", j, X, win, inst)


tables = {}
for inst in ("J_NP", "RESID_P", "LOGITS"):
    for wname, win in WINDOWS.items():
        if inst == "LOGITS" and wname != "L48-50": continue
        key = inst if inst == "LOGITS" else f"{inst}|{wname}"; T = {}
        # competition: per set (cluster), per k: C_focal pointed, C_focal ctrl, C_distractor pointed, S
        for k in KS:
            rows = {"focal_pointed": [], "focal_ctrl": [], "dist_pointed": [], "S": []}
            for si in range(4):
                fp, fc, dp = [], [], []
                for ck in CARRIERS:
                    for fi in range(2):
                        for place in (("first",) if k == 1 else ("first", "last")):
                            b = f"comp|{ck}|S{si}|F{fi}|k{k}|{place}"; cell = META["cells"][f"{b}|ctrl"]; fj = cell["focal_j"]; srcs = cell["srcs"]
                            fp.append(C(f"{b}|{chr(65 + fj)}", fj, win, inst)); fc.append(C(f"{b}|ctrl", fj, win, inst))
                            if k >= 2: dp.append(C(f"{b}|{chr(65 + fj)}", srcs[1], win, inst))
                rows["focal_pointed"].append(np.mean(fp)); rows["focal_ctrl"].append(np.mean(fc))
                if k >= 2: rows["dist_pointed"].append(np.mean(dp)); rows["S"].append(np.mean(fp) - np.mean(dp))
            for q, v in rows.items():
                if v: T[f"k{k}|{q}"] = S.cluster_t(v)
            if k > 1: T[f"k{k}|ratio_focal_pointed_vs_k1"] = S.ratio_of_means(rows["focal_pointed"], [T["k1|focal_pointed"]["per_cluster"][i] for i in range(4)])
        # cue: per triple, C_A and C_B on the second half under switchB / sameA / none; g and dsh coordinates
        rows = {c: {"C_A": [], "C_B": [], "g": [], "dsh": []} for c in ("switchB", "sameA", "none")}
        for ti in range(8):
            for c in rows:
                a, b, g, d = [], [], [], []
                for ck in CARRIERS:
                    base = f"cue|{ck}|T{ti}|{c}"
                    a.append(C(base, 0, win, inst)); b.append(C(base, 1, win, inst))
                    g.append(float(Z[f"{base}|clean|g35"].mean())); d.append(float(Z[f"{base}|clean|dsh35"].mean()))
                for q, v in zip(("C_A", "C_B", "g", "dsh"), (a, b, g, d)): rows[c][q].append(np.mean(v))
        for c in rows:
            for q in ("C_A", "C_B", "g", "dsh"): T[f"cue|{c}|{q}"] = S.cluster_t(rows[c][q])
        for q in ("C_A", "C_B", "g", "dsh"):
            T[f"cue|switch_minus_same|{q}"] = S.cluster_t(np.array(rows["switchB"][q]) - np.array(rows["sameA"][q]))
            T[f"cue|same_minus_none|{q}"] = S.cluster_t(np.array(rows["sameA"][q]) - np.array(rows["none"][q]))
        T["cue|switch_minus_same|C_B_minus_C_A"] = S.cluster_t((np.array(rows["switchB"]["C_B"]) - np.array(rows["switchB"]["C_A"])) - (np.array(rows["sameA"]["C_B"]) - np.array(rows["sameA"]["C_A"])))
        tables[key] = T
json.dump(tables, open(os.path.join(RES, "competition_and_cue_tables.json"), "w"), indent=1, default=float)

fig, axes = plt.subplots(1, 3, figsize=(15, 4))
for ax, key in zip(axes, ("J_NP|L48-50", "J_NP|L51-59", "LOGITS")):
    T = tables[key]
    for q, lab in (("focal_pointed", "focal, pointed"), ("focal_ctrl", "focal, no pointer"), ("dist_pointed", "distractor, focal pointed")):
        ks = [k for k in KS if f"k{k}|{q}" in T]; m = [T[f"k{k}|{q}"]["mean"] for k in ks]; lo = [T[f"k{k}|{q}"]["ci"][0] for k in ks]; hi = [T[f"k{k}|{q}"]["ci"][1] for k in ks]
        ax.errorbar(ks, m, yerr=[np.array(m) - lo, np.array(hi) - m], marker="o", capsize=3, label=lab)
    ax.axhline(0, color="k", lw=0.5); ax.set_xlabel("number of tagged sources k"); ax.set_ylabel("C = m(swap) - m(clean)"); ax.set_title(key); ax.legend(fontsize=7)
plt.tight_layout(); plt.savefig(os.path.join(FIG, "competition_by_k.png"), dpi=130); plt.close()


def cs(e): return f"{e['mean']:+.4f} [{e['ci'][0]:+.4f}, {e['ci'][1]:+.4f}] ({e.get('signs_pos', 0)}/{e['n']} >0)"


rep = [f"# H1.8 · competition series and mid-carrier cue — results (run {META['run_id']})\n", "## 1. Question and setup\n",
       f"Competition: nested tagged sets k ∈ {KS} from 4 six-word sets of evaluation-bank words, two focal identities per set, focal placed first or last (counterbalanced), carriers {CARRIERS}; focal and first-distractor sources replaced from block 36 under the focal's pointer and under control. Cluster = set (n=4). Cue: the 8 evaluation triples, pointed-A arm, cue sentence inserted at the carrier midpoint in both copies: switch→B, same-tag→A, none; readout on the post-cue interior positions; sources A and B replaced. Cluster = triple (n=8). {META['n_forwards']} forwards; same-source and layer<36 identity asserted per cell.\n", "## 2. Main findings\n"]
for key in ("J_NP|L48-50", "J_NP|L51-59", "RESID_P|L48-50", "RESID_P|L51-59", "LOGITS"):
    T = tables[key]
    rep.append(f"- **{key}, competition:** focal pointed C by k: " + "; ".join(f"k={k} {T[f'k{k}|focal_pointed']['mean']:+.3f} [{T[f'k{k}|focal_pointed']['ci'][0]:+.3f}, {T[f'k{k}|focal_pointed']['ci'][1]:+.3f}]" for k in KS) + ". Ratio to k=1: " + ", ".join(f"k={k} {T[f'k{k}|ratio_focal_pointed_vs_k1']['ratio']:.2f}" for k in KS[1:]) + ". S by k: " + "; ".join(f"k={k} {cs(T[f'k{k}|S'])}" for k in KS[1:]) + ". Focal under no pointer: " + ", ".join(f"k={k} {T[f'k{k}|focal_ctrl']['mean']:+.3f}" for k in KS) + ".")
    rep.append(f"- **{key}, cue:** C_A switch {cs(T['cue|switchB|C_A'])} vs same-tag {cs(T['cue|sameA|C_A'])} vs none {cs(T['cue|none|C_A'])}; C_B switch {cs(T['cue|switchB|C_B'])} vs same-tag {cs(T['cue|sameA|C_B'])} vs none {cs(T['cue|none|C_B'])}. Switch − same-tag: C_A {cs(T['cue|switch_minus_same|C_A'])}, C_B {cs(T['cue|switch_minus_same|C_B'])}, (C_B−C_A) {cs(T['cue|switch_minus_same|C_B_minus_C_A'])}. ĝ coordinate switch−same {cs(T['cue|switch_minus_same|g'])}, d_shared coordinate {cs(T['cue|switch_minus_same|dsh'])}. Same-tag − none: C_A {cs(T['cue|same_minus_none|C_A'])}, C_B {cs(T['cue|same_minus_none|C_B'])}.")
rep.append("\n## 3. Complete numerical evidence\n")
for key in ("J_NP|L48-50", "J_NP|L51-59", "RESID_P|L48-50", "RESID_P|L51-59", "LOGITS"):
    T = tables[key]; rep.append(f"### {key}\n\n| quantity | mean | 95% t-CI | signs >0 / n | per-cluster |\n|---|---|---|---|---|")
    for q in sorted(T):
        e = T[q]
        if "ratio" in q and "per_cluster" not in e: rep.append(f"| {q} | {e['ratio']:.3f} | [{e['ci'][0]:.3f}, {e['ci'][1]:.3f}] | | num {e['numerator_mean']:+.3f} / den {e['denominator_mean']:+.3f} |"); continue
        rep.append(f"| {q} | {e['mean']:+.4f} | [{e['ci'][0]:+.4f}, {e['ci'][1]:+.4f}] | {e.get('signs_pos', 0)}/{e['n']} | {', '.join(f'{x:+.3f}' for x in e['per_cluster'])} |")
    rep.append("")
rep.append("Figure: `figures/competition_by_k.png`. Machine-readable: `competition_and_cue_tables.json`.\n\n## 4. Verification and limitations\n\n- Same-source bitwise and layer<36 identity asserted on every cell; donor geometry asserted. n=4 sets for competition (extension scale); the k=1 reference has one placement. The cue is copied text in both turns; the 'none' readout uses the same post-midpoint positions. No state moves in this run.\n\n## 5. Interpretation and next decision\n\n_Filled in by hand after reading the tables._\n")
open(os.path.join(RES, "competition_and_cue.md"), "w").write("\n".join(rep)); print("\n".join(rep[4:14]))
