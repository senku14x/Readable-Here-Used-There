"""Ordinal-position breakdown of tagged selection (analysis-only re-scoring of an existing run).

The registered tagged_selection analysis indexes relevance by lexical identity after averaging the three
rotations, so any dependence of transfer on the ordinal slot of the pointed source is averaged away. This
script re-scores the same raw arrays by slot: for each triple, carrier and rotation, and each slot j, the
transfer C_j under the pointer at j (pointed), under the other two pointers (unpointed), and under the
control arm. S = pointed − unpointed per slot. Cluster = triple. No new forwards.

Usage: tagged_selection_ordinal_analysis.py [evaluate|pilot]
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

STAGE = sys.argv[1] if len(sys.argv) > 1 else "evaluate"
OUT = os.path.join(R.out_dir("H1", "outputs"), "tagged_selection"); RES = os.path.join(R.out_dir("H1", "results")); FIG = os.path.join(RES, "figures")
META = json.load(open(os.path.join(OUT, f"meta_{STAGE}.json"))); Z = np.load(os.path.join(OUT, f"raw_{STAGE}.npz"))
COLS = META["columns"]; CIX = {w: i for i, w in enumerate(COLS)}; TRIPLES = [tuple(t) for t in META["triples"]]; DONOR = META["donor"]
CARRIERS = META["carriers"]; TAGS = ["A", "B", "C"]
WINDOWS = {"L48-50": [48, 49, 50], "L51-59": list(range(51, 60))}


def words_of(ck, ti, rot):
    return META["cells"][f"{ck}|{ti}|rot{rot}|A"]["words"]


def margin(tag, X, j, win, inst):
    if inst == "J_NP":
        z = Z[f"{tag}|z"].astype(np.float32)[win]; return float((z[:, :, CIX[DONOR[X]]] - z[:, :, CIX[X]]).mean())
    if inst == "RESID_P":
        return float(Z[f"{tag}|p_pair{j+1}"][win].mean())
    return float(Z[f"{tag}|lp_margin{j+1}"].mean())


def C(ck, ti, rot, arm, j, win, inst):
    base = f"{ck}|{ti}|rot{rot}|{arm}"; X = words_of(ck, ti, rot)[j]
    return margin(f"{base}|clean|swap{j+1}", X, j, win, inst) - margin(f"{base}|clean|noswap", X, j, win, inst)


tables = {"triples": TRIPLES, "n_forwards_reused": META["n_forwards"], "run_id": META["run_id"]}
for inst in ("J_NP", "RESID_P", "LOGITS"):
    for wname, win in WINDOWS.items():
        if inst == "LOGITS" and wname != "L48-50":
            continue
        key = inst if inst == "LOGITS" else f"{inst}|{wname}"
        per = {q: {j: [] for j in range(3)} for q in ("S", "pointed", "unpointed", "control")}
        for ti in range(len(TRIPLES)):
            acc = {q: {j: [] for j in range(3)} for q in per}
            for ck in CARRIERS:
                for rot in range(3):
                    for j in range(3):
                        p = C(ck, ti, rot, TAGS[j], j, win, inst)
                        u = np.mean([C(ck, ti, rot, a, j, win, inst) for a in TAGS if a != TAGS[j]])
                        c = C(ck, ti, rot, "ctrl", j, win, inst)
                        acc["S"][j].append(p - u); acc["pointed"][j].append(p); acc["unpointed"][j].append(u); acc["control"][j].append(c)
            for q in per:
                for j in range(3):
                    per[q][j].append(float(np.mean(acc[q][j])))
        T = {}
        for q in per:
            for j in range(3):
                T[f"{q}|slot{j+1}"] = S.cluster_t(per[q][j])
            T[f"{q}|slot3_minus_slot1"] = S.cluster_t([a - b for a, b in zip(per[q][2], per[q][0])])
            T[f"{q}|slot2_minus_slot1"] = S.cluster_t([a - b for a, b in zip(per[q][1], per[q][0])])
        tables[key] = T
json.dump(tables, open(os.path.join(RES, f"tagged_selection_ordinal_tables.json"), "w"), indent=1, default=float)

# figure: transfer by slot under pointed / unpointed / control, per instrument and window
keys = [k for k in tables if "|" in k and k.split("|")[0] in ("J_NP", "RESID_P")] + ["LOGITS"]
fig, axes = plt.subplots(1, len(keys), figsize=(3.6 * len(keys), 3.8))
for ax, key in zip(axes, keys):
    T = tables[key]
    for q, col in (("pointed", "C0"), ("unpointed", "C1"), ("control", "C7")):
        m = [T[f"{q}|slot{j}"]["mean"] for j in (1, 2, 3)]
        lo = [m[i] - T[f"{q}|slot{j}"]["ci"][0] for i, j in enumerate((1, 2, 3))]
        hi = [T[f"{q}|slot{j}"]["ci"][1] - m[i] for i, j in enumerate((1, 2, 3))]
        ax.errorbar([1, 2, 3], m, yerr=[lo, hi], fmt="o-", color=col, capsize=3, label=q)
        for j in (1, 2, 3):
            ax.scatter(np.full(8, j) + (0.08 if q == "pointed" else -0.08 if q == "unpointed" else 0), T[f"{q}|slot{j}"]["per_cluster"], s=8, alpha=0.5, color=col)
    ax.set_xticks([1, 2, 3]); ax.set_xlabel("ordinal slot of the source"); ax.set_ylabel("C_j (pair margin, swap − noswap)")
    ax.set_title(key, fontsize=9); ax.axhline(0, color="k", lw=0.5)
axes[0].legend(fontsize=8)
plt.tight_layout(); plt.savefig(os.path.join(FIG, f"tagged_selection_ordinal_{STAGE}.png"), dpi=130); plt.close()


def cs(e):
    return f"{e['mean']:+.3f} [{e['ci'][0]:+.3f}, {e['ci'][1]:+.3f}] ({e.get('signs_pos', 0)}/{e['n']} >0)"


rep = [f"# H1 · tagged_selection — ordinal-position breakdown ({STAGE}; analysis-only re-scoring of run {META['run_id']})\n",
       "## 1. Question and setup\n",
       f"Does the transfer of a tagged source, and the selection contrast, depend on the ordinal slot the source occupies? The registered analysis indexes relevance by identity after averaging rotations, which hides any slot effect. Here the same {META['n_forwards']} forwards are re-scored by slot: C_j under the pointer at j (pointed), under the two other pointers (unpointed) and under the control arm; S = pointed − unpointed. Triples {TRIPLES}, carriers {CARRIERS}, three rotations. Cluster = triple (n={len(TRIPLES)}); windows L48–50 and L51–59; no new forwards, no state moves.\n",
       "## 2. Main findings\n"]
for key in keys:
    T = tables[key]
    rep.append(f"- **{key}:** S by slot 1/2/3: {cs(T['S|slot1'])} / {cs(T['S|slot2'])} / {cs(T['S|slot3'])}; pointed C: {cs(T['pointed|slot1'])} / {cs(T['pointed|slot2'])} / {cs(T['pointed|slot3'])}; control C: {cs(T['control|slot1'])} / {cs(T['control|slot2'])} / {cs(T['control|slot3'])}. Slot 3 − slot 1: pointed {cs(T['pointed|slot3_minus_slot1'])}; control {cs(T['control|slot3_minus_slot1'])}; S {cs(T['S|slot3_minus_slot1'])}.")
rep.append("\n## 3. Complete tables\n")
for key in keys:
    T = tables[key]; rep.append(f"### {key}\n\n| quantity | mean | 95% t-CI | signs >0 / n | per-triple |\n|---|---|---|---|---|")
    for q in ("S", "pointed", "unpointed", "control"):
        for s in ("slot1", "slot2", "slot3", "slot2_minus_slot1", "slot3_minus_slot1"):
            e = T[f"{q}|{s}"]; rep.append(f"| {q}|{s} | {e['mean']:+.4f} | [{e['ci'][0]:+.4f}, {e['ci'][1]:+.4f}] | {e.get('signs_pos', 0)}/{e['n']} | {', '.join(f'{x:+.3f}' for x in e['per_cluster'])} |")
    rep.append("")
rep.append(f"Figure: `figures/tagged_selection_ordinal_{STAGE}.png`. Machine-readable: `tagged_selection_ordinal_tables.json`.\n")
rep.append("## 4. Verification and limitations\n\n- Re-scoring of the registered run's arrays; gates as in the original report. The slot factor is confounded with nothing by design (each identity occupies each slot once per triple) but slots differ in distance to the tag token and to the carrier; no intervention separates those. Different instruments on the same forwards are robustness, not independent samples.\n")
rep.append("## 5. Interpretation and next decision\n\n_Filled in by hand after reading the tables._\n")
open(os.path.join(RES, f"tagged_selection_ordinal.md"), "w").write("\n".join(rep))
print("\n".join(rep[4:8]))
