"""Analysis for H1 tagged selection (single scoring pass). Reads H1/outputs/tagged_selection/raw_<stage>.npz.

Relevance is indexed by lexical identity after averaging the three rotations: for word w in triple t,
C_w(pointed w), C_w(pointed other), C_w(control). Estimands: S (selectivity), Q (suppression), U (instruction
gain), S_nat (readout selectivity), the g / d_shared / d_pointer move profiles (per-source ratios, P index),
realized writes, damage, output-disposition screen. Cluster = triple.
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
OUT = os.path.join(R.out_dir("H1", "outputs"), "tagged_selection"); RES = os.path.join(R.out_dir("H1", "results")); FIG = os.path.join(RES, "figures")
META = json.load(open(os.path.join(OUT, f"meta_{STAGE}.json"))); Z = np.load(os.path.join(OUT, f"raw_{STAGE}.npz"))
COLS = META["columns"]; CIX = {w: i for i, w in enumerate(COLS)}; TRIPLES = [tuple(t) for t in META["triples"]]; DONOR = META["donor"]
CARRIERS = META["carriers"]; TAGS = ["A", "B", "C"]; DEC = [CIX[d] for d in COLS[12:]]
WINDOWS = {"L48-50": [48, 49, 50], "L51-59": list(range(51, 60))}
RANK_LAYERS = META["rank_layers"]


def words_of(ck, ti, rot):
    return META["cells"][f"{ck}|{ti}|rot{rot}|A"]["words"]


def m_J(tag, j, win):
    z = Z[f"{tag}|z"].astype(np.float32)[win]; w = words_of(*tag.split("|")[:1], int(tag.split("|")[1]), int(tag.split("|")[2][3:]))[j] if False else None
    return z


def margin(tag, j, X, win, inst):
    if inst == "J_NP":
        z = Z[f"{tag}|z"].astype(np.float32)[win]; return float((z[:, :, CIX[DONOR[X]]] - z[:, :, CIX[X]]).mean())
    if inst == "RESID_P":
        return float(Z[f"{tag}|p_pair{j+1}"][win].mean())
    return float(Z[f"{tag}|lp_margin{j+1}"].mean())


def presence(tag, X, win):
    z = Z[f"{tag}|z"].astype(np.float32)[win]; return float((z[:, :, CIX[X]] - z[:, :, DEC].mean(-1)).mean())


def C(ck, ti, rot, arm, cond, j, win, inst):
    base = f"{ck}|{ti}|rot{rot}|{arm}"; X = words_of(ck, ti, rot)[j]
    return margin(f"{base}|{cond}|swap{j+1}", j, X, win, inst) - margin(f"{base}|{cond}|noswap", j, X, win, inst)


tables = {"fits": META["fits"], "triples": TRIPLES}
for inst in ("J_NP", "RESID_P", "LOGITS"):
    for wname, win in WINDOWS.items():
        if inst == "LOGITS" and wname != "L48-50":
            continue
        key = inst if inst == "LOGITS" else f"{inst}|{wname}"
        T = {}
        # per triple: for each word w, C under pointed-self, pointed-other (mean of 2), control; averaged over rotations & carriers
        rows = {"self": [], "other": [], "ctrl": [], "S": [], "Q": [], "U": []}
        GAIN_CONDS = ["g", "dshared"] + (["dshared_pilot"] if any("|dshared_pilot|" in k for k in Z.files) else [])
        PTR_CONDS = ["dptr"] + (["dptr_pilot"] if any("|dptr_pilot|" in k for k in Z.files) else [])
        prof = {c: {"pointed": [], "unpointed": [], "pointed_clean": [], "unpointed_clean": []} for c in GAIN_CONDS}
        dptr = {pc: {"A_clean": [], "B_clean": [], "C_clean": [], "A_moved": [], "B_moved": [], "C_moved": []} for pc in PTR_CONDS}
        grev = {"clean": [], "moved": []}
        for ti, tr in enumerate(TRIPLES):
            self_, other_, ctrl_ = [], [], []
            for ck in CARRIERS:
                for rot in range(3):
                    words = words_of(ck, ti, rot)
                    for j, X in enumerate(words):
                        tag_pointed = TAGS[j]      # tag at position j
                        self_.append(C(ck, ti, rot, tag_pointed, "clean", j, win, inst))
                        other_.append(np.mean([C(ck, ti, rot, a, "clean", j, win, inst) for a in TAGS if a != tag_pointed]))
                        ctrl_.append(C(ck, ti, rot, "ctrl", "clean", j, win, inst))
                        # state-move profiles under pointer at position j
                        for c in GAIN_CONDS:
                            prof[c]["pointed"].append(C(ck, ti, rot, tag_pointed, c, j, win, inst)); prof[c]["pointed_clean"].append(self_[-1])
                            for a in TAGS:
                                if a != tag_pointed:
                                    prof[c]["unpointed"].append(C(ck, ti, rot, a, c, j, win, inst)); prof[c]["unpointed_clean"].append(C(ck, ti, rot, a, "clean", j, win, inst))
                    # d_pointer transplant under the A arm: C of each position before/after the A->B move
                    for pc in PTR_CONDS:
                        for j, a in enumerate(TAGS):
                            dptr[pc][f"{a}_clean"].append(C(ck, ti, rot, "A", "clean", j, win, inst)); dptr[pc][f"{a}_moved"].append(C(ck, ti, rot, "A", pc, j, win, inst))
                    for j in range(3):
                        grev["clean"].append(C(ck, ti, rot, "ctrl", "clean", j, win, inst)); grev["moved"].append(C(ck, ti, rot, "ctrl", "grev", j, win, inst))
            rows["self"].append(np.mean(self_)); rows["other"].append(np.mean(other_)); rows["ctrl"].append(np.mean(ctrl_))
            rows["S"].append(np.mean(self_) - np.mean(other_)); rows["Q"].append(np.mean(other_) - np.mean(ctrl_)); rows["U"].append(np.mean(self_) - np.mean(ctrl_))
        for k, v in rows.items():
            T[k] = S.cluster_t(v)
        T["S_over_U"] = S.ratio_of_means(rows["S"], rows["U"])
        # profiles: per triple means (clusters) computed by splitting the flat lists into triples
        nper = len(CARRIERS) * 3 * 3
        for c in GAIN_CONDS:
            p = prof[c]; k = len(p["pointed"]) // len(TRIPLES); ku = len(p["unpointed"]) // len(TRIPLES)
            dP = [np.mean(p["pointed"][i*k:(i+1)*k]) - np.mean(p["pointed_clean"][i*k:(i+1)*k]) for i in range(len(TRIPLES))]
            dU = [np.mean(p["unpointed"][i*ku:(i+1)*ku]) - np.mean(p["unpointed_clean"][i*ku:(i+1)*ku]) for i in range(len(TRIPLES))]
            rP = [np.mean(p["pointed"][i*k:(i+1)*k]) / np.mean(p["pointed_clean"][i*k:(i+1)*k]) for i in range(len(TRIPLES))]
            rU = [np.mean(p["unpointed"][i*ku:(i+1)*ku]) / np.mean(p["unpointed_clean"][i*ku:(i+1)*ku]) if abs(np.mean(p["unpointed_clean"][i*ku:(i+1)*ku])) > 1e-3 else np.nan for i in range(len(TRIPLES))]
            T[f"{c}|dC_pointed"] = S.cluster_t(dP); T[f"{c}|dC_unpointed"] = S.cluster_t(dU); T[f"{c}|ratio_pointed"] = S.cluster_t(rP)
            T[f"{c}|ratio_unpointed"] = S.cluster_t([x for x in rU if np.isfinite(x)]) if any(np.isfinite(rU)) else None
            T[f"{c}|P_index"] = S.cluster_t([a - b for a, b in zip(rP, rU) if np.isfinite(b)]) if any(np.isfinite(rU)) else None
        for pc in PTR_CONDS:
            d = dptr[pc]; k = len(d["A_clean"]) // len(TRIPLES)
            for a in TAGS:
                T[f"{pc}|dC_{a}"] = S.cluster_t([np.mean(d[f"{a}_moved"][i*k:(i+1)*k]) - np.mean(d[f"{a}_clean"][i*k:(i+1)*k]) for i in range(len(TRIPLES))])
            T[f"{pc}|redistribution_B_minus_A"] = S.cluster_t([(np.mean(d["B_moved"][i*k:(i+1)*k]) - np.mean(d["B_clean"][i*k:(i+1)*k])) - (np.mean(d["A_moved"][i*k:(i+1)*k]) - np.mean(d["A_clean"][i*k:(i+1)*k])) for i in range(len(TRIPLES))])
        T["_gain_conds"] = GAIN_CONDS; T["_ptr_conds"] = PTR_CONDS
        k = len(grev["clean"]) // len(TRIPLES)
        T["grev|dC_all_sources"] = S.cluster_t([np.mean(grev["moved"][i*k:(i+1)*k]) - np.mean(grev["clean"][i*k:(i+1)*k]) for i in range(len(TRIPLES))])
        tables[key] = T
# natural readout selectivity and prominence (J_NP)
for wname, win in WINDOWS.items():
    snat, pres = [], {"self": [], "other": [], "ctrl": []}
    for ti, tr in enumerate(TRIPLES):
        s_, o_, c_ = [], [], []
        for ck in CARRIERS:
            for rot in range(3):
                words = words_of(ck, ti, rot)
                for j, X in enumerate(words):
                    s_.append(presence(f"{ck}|{ti}|rot{rot}|{TAGS[j]}|clean|noswap", X, win))
                    o_.append(np.mean([presence(f"{ck}|{ti}|rot{rot}|{a}|clean|noswap", X, win) for a in TAGS if a != TAGS[j]]))
                    c_.append(presence(f"{ck}|{ti}|rot{rot}|ctrl|clean|noswap", X, win))
        snat.append(np.mean(s_) - np.mean(o_)); pres["self"].append(np.mean(s_)); pres["other"].append(np.mean(o_)); pres["ctrl"].append(np.mean(c_))
    tables[f"S_nat|{wname}"] = S.cluster_t(snat); tables[f"presence|{wname}"] = {k: S.cluster_t(v) for k, v in pres.items()}
# rank-1-anywhere (L24-59) of each word under self / other / control pointer, and output-disposition screen
hits = {"self": [], "other": [], "ctrl": []}; fin = {"self": [], "other": [], "ctrl": []}
for ti in range(len(TRIPLES)):
    for ck in CARRIERS:
        for rot in range(3):
            for j in range(3):
                rk = lambda a: Z[f"{ck}|{ti}|rot{rot}|{a}|clean|noswap|rank"][:, :, j].min() == 1
                fr = lambda a: int(Z[f"{ck}|{ti}|rot{rot}|{a}|clean|noswap|fin_rank"][j])
                hits["self"].append(rk(TAGS[j])); hits["other"].append(np.mean([rk(a) for a in TAGS if a != TAGS[j]])); hits["ctrl"].append(rk("ctrl"))
                fin["self"].append(fr(TAGS[j])); fin["other"].append(np.mean([fr(a) for a in TAGS if a != TAGS[j]])); fin["ctrl"].append(fr("ctrl"))
tables["rank1_anywhere"] = {k: float(np.mean(v)) for k, v in hits.items()}
tables["output_disposition_median_final_rank"] = {k: float(np.median(v)) for k, v in fin.items()}
tables["output_disposition_min_final_rank"] = {k: float(np.min(v)) for k, v in fin.items()}
# realized writes + damage
rw, dmg = {}, {}
for k in Z.files:
    if k.endswith("|w_rho"):
        c = k.split("|")[4]; rw.setdefault(c, []).append(float(Z[k]))
    if k.endswith("|nll") and "|clean|noswap|" not in k:
        parts = k.split("|"); base = "|".join(parts[:4]); c = parts[4]
        dmg.setdefault(c, []).append({"dnll": float(Z[k] - Z[f"{base}|clean|noswap|nll"]), "top1": float((Z[k[:-4] + "|top1"] == Z[f"{base}|clean|noswap|top1"]).mean())})
tables["realized_rho"] = {c: [min(v), max(v)] for c, v in rw.items()}
tables["damage"] = {c: {"dNLL_max": max(x["dnll"] for x in v), "top1_min": min(x["top1"] for x in v)} for c, v in dmg.items()}
json.dump(tables, open(os.path.join(RES, f"tagged_selection_{STAGE}_tables.json"), "w"), indent=1, default=float)

# figure: self / other / ctrl transfer per instrument & window, with per-triple points
keys = [k for k in tables if "|" in k and k.split("|")[0] in ("J_NP", "RESID_P")] + ["LOGITS"]
fig, axes = plt.subplots(1, len(keys), figsize=(4 * len(keys), 4))
for ax, key in zip(axes, keys):
    T = tables[key]
    for i, q in enumerate(("self", "other", "ctrl")):
        e = T[q]; ax.errorbar(i, e["mean"], yerr=[[e["mean"] - e["ci"][0]], [e["ci"][1] - e["mean"]]], fmt="o", color="k", capsize=3)
        ax.scatter(np.full(len(e["per_cluster"]), i), e["per_cluster"], s=14, alpha=0.7)
    ax.set_xticks(range(3)); ax.set_xticklabels(["pointed\n(self)", "unpointed\n(other pointed)", "control\n(no pointer)"]); ax.axhline(0, color="k", lw=0.5)
    ax.set_title(f"{key}\nS={T['S']['mean']:+.3f} Q={T['Q']['mean']:+.3f} U={T['U']['mean']:+.3f}", fontsize=9); ax.set_ylabel("C_w = m_w(swap w) − m_w(noswap)")
plt.tight_layout(); plt.savefig(os.path.join(FIG, f"tagged_selection_{STAGE}_transfer.png"), dpi=130); plt.close()


def cs(e):
    return "n/a" if e is None else f"{e['mean']:+.4f} [{e['ci'][0]:+.4f}, {e['ci'][1]:+.4f}] ({e.get('signs_pos', 0)}/{e['n']} >0)"


rep = [f"# H1 · tagged selection — {STAGE} results (run {META['run_id']})\n", "## 1. Question and setup\n",
       f"Does the instruction select which of three tagged sources is carried to the later readout, or scale whichever word is sourced? Triples {TRIPLES}, three rotations each, carriers {CARRIERS}, arms pointed A/B/C and control; each source replaced from block 36 by its donor ({DONOR}); readout per source = its own pair margin on J_NP, RESID_P and LOGITS at interior carrier positions, windows L48–50 and L51–59. Cluster = triple (n={len(TRIPLES)}). State moves: frozen single-word ĝ (cos with this organism's native shared direction {META['fits']['cos_dshared_ghat']:.2f}), native d_shared, native pointer contrast d_pointer(A→B) (cos with ĝ {META['fits']['cos_dptr_ghat']:.2f}, |d| {META['fits']['norm_d_pointer_AB']:.2f} vs |d_shared| {META['fits']['norm_d_shared']:.2f}). {META['n_forwards']} forwards; same-source and layer<36 identity asserted per cell.\n",
       "## 2. Main findings\n"]
for key in ("J_NP|L48-50", "J_NP|L51-59", "RESID_P|L48-50", "RESID_P|L51-59", "LOGITS"):
    T = tables[key]
    rep.append(f"- **{key}:** pointed-source transfer C(self) {cs(T['self'])}; unpointed C(other) {cs(T['other'])}; control C(ctrl) {cs(T['ctrl'])}. **S = {cs(T['S'])}**; Q = {cs(T['Q'])}; U = {cs(T['U'])}; S/U {T['S_over_U']['ratio']:.2f}.")
    for c in T["_gain_conds"]:
        rep.append(f"  - {c} (pointed→control level): ΔC pointed {cs(T[c+'|dC_pointed'])}, unpointed {cs(T[c+'|dC_unpointed'])}; ratio pointed {cs(T[c+'|ratio_pointed'])}, unpointed {cs(T[c+'|ratio_unpointed'])}; P {cs(T[c+'|P_index'])}.")
    for pc in T["_ptr_conds"]:
        rep.append(f"  - {pc} A→B under pointed-A: ΔC_A {cs(T[pc+'|dC_A'])}, ΔC_B {cs(T[pc+'|dC_B'])}, ΔC_C {cs(T[pc+'|dC_C'])}, redistribution B−A {cs(T[pc+'|redistribution_B_minus_A'])}.")
    rep.append(f"  - reverse ĝ on control (one-sided) ΔC all sources {cs(T['grev|dC_all_sources'])}.")
rep.append(f"- **Natural readout selectivity S_nat (J_NP):** L48–50 {cs(tables['S_nat|L48-50'])}; L51–59 {cs(tables['S_nat|L51-59'])}. Presence L51–59: self {tables['presence|L51-59']['self']['mean']:+.3f}, other {tables['presence|L51-59']['other']['mean']:+.3f}, control {tables['presence|L51-59']['ctrl']['mean']:+.3f}.")
rep.append(f"- **Rank-1-anywhere (L24–59):** pointed {tables['rank1_anywhere']['self']:.2f}, unpointed {tables['rank1_anywhere']['other']:.2f}, control {tables['rank1_anywhere']['ctrl']:.2f}. Output-disposition screen (median final-layer rank of each word at interior positions): pointed {tables['output_disposition_median_final_rank']['self']:.0f}, unpointed {tables['output_disposition_median_final_rank']['other']:.0f}, control {tables['output_disposition_median_final_rank']['ctrl']:.0f} (min {tables['output_disposition_min_final_rank']['self']:.0f}).")
rep.append(f"- **Gates:** realized ρ ranges {json.dumps({c: [round(a, 3), round(b, 3)] for c, (a, b) in tables['realized_rho'].items()})}; damage max ΔNLL {max(v['dNLL_max'] for v in tables['damage'].values()):.4f}, min top-1 retention {min(v['top1_min'] for v in tables['damage'].values()):.3f}.\n")
rep.append("## 3. Complete numerical evidence\n")
for key in ("J_NP|L48-50", "J_NP|L51-59", "RESID_P|L48-50", "RESID_P|L51-59", "LOGITS"):
    T = tables[key]; rep.append(f"### {key}\n\n| quantity | mean | 95% t-CI | signs >0 / n | per-triple |\n|---|---|---|---|---|")
    for q in ["self", "other", "ctrl", "S", "Q", "U"] + [f"{c}|{x}" for c in T["_gain_conds"] for x in ("dC_pointed", "dC_unpointed", "ratio_pointed", "ratio_unpointed", "P_index")] + [f"{pc}|{x}" for pc in T["_ptr_conds"] for x in ("dC_A", "dC_B", "dC_C", "redistribution_B_minus_A")] + ["grev|dC_all_sources"]:
        e = T[q]
        if e is None:
            rep.append(f"| {q} | n/a | | | |"); continue
        rep.append(f"| {q} | {e['mean']:+.4f} | [{e['ci'][0]:+.4f}, {e['ci'][1]:+.4f}] | {e.get('signs_pos', 0)}/{e['n']} | {', '.join(f'{x:+.3f}' for x in e['per_cluster'])} |")
    rep.append("")
rep.append(f"Figure: `figures/tagged_selection_{STAGE}_transfer.png`. Machine-readable: `tagged_selection_{STAGE}_tables.json`.\n")
rep.append("## 4. Verification and limitations\n\n- Same-source (position 1) bitwise equal to clean and layers < 36 identical between futures on every cell; donor geometry asserted per source. Realized writes and damage above.\n- Pilot: n = 4 triples of previously exposed words, fitting carriers only; ĝ is a cross-organism transfer from the single-word fit; d_pointer and d_shared are fit on these same cells (identity-specific contextual generalization is not claimed).\n- Unpointed ratios are undefined where the unpointed clean transfer is near zero; reported as n/a where so.\n")
rep.append("## 5. Interpretation and next decision\n\n_Filled in by hand after reading the tables._\n")
open(os.path.join(RES, f"tagged_selection_{STAGE}.md"), "w").write("\n".join(rep))
print("\n".join(rep[4:12]))
