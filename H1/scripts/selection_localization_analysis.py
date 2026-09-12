"""Analysis for selection_localization. Dispatches on stage: ptr_transplant (1A), decomp (1B), transfer (1C).

- ptr_transplant: restoration R_L = (p_{D->A,L}-p_A).(p_D-p_A)/||p_D-p_A||^2 on the carrier presence profile p=(s_A,s_B,s_C).
- decomp: same R, split by patched region (tag-only / suffix / full) at boundaries {36,44} -> is the pointer local to the tag
  state or propagated into the instruction suffix?
- transfer: does the B->A / C->A instruction transplant redirect the *causal transfer* profile C_j (source-swap), not just
  presence? Restoration along the clean A->donor transfer axis.

Usage: selection_localization_analysis.py ptr_transplant|decomp|transfer
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

STAGE = sys.argv[1] if len(sys.argv) > 1 else "ptr_transplant"
OUT = os.path.join(R.out_dir("H1", "outputs"), "selection_localization")
RES = os.path.join(R.out_dir("H1", "results")); FIG = os.path.join(RES, "figures"); os.makedirs(FIG, exist_ok=True)
META = json.load(open(os.path.join(OUT, f"meta_{STAGE}.json"))); Z = np.load(os.path.join(OUT, f"raw_{STAGE}.npz"))
CELLS = META["cells"]; COLS = META["columns"]; CIX = {w: i for i, w in enumerate(COLS)}
TRIPLES = [tuple(t) for t in META["triples"]]; CARRIERS = META["carriers"]
DEC = [CIX[d] for d in META["decoys"]]; TAGS = ["A", "B", "C"]
WINDOWS = {"L48-50": [48, 49, 50], "L51-59": list(range(51, 60))}


def presw(sub, wcol, win):
    z = Z[f"{sub}|z"].astype(np.float32)[win]
    return float((z[:, :, wcol] - z[:, :, DEC].mean(-1)).mean())


def prof(sub, wcols, win):
    return np.array([presw(sub, c, win) for c in wcols])


def restore(pDA, pA, pD):
    ax = pD - pA; nn = float(ax @ ax)
    return float((pDA - pA) @ ax / nn) if nn > 1e-9 else np.nan


def cs(e):
    return "n/a" if e is None else f"{e['mean']:+.3f} [{e['ci'][0]:+.3f}, {e['ci'][1]:+.3f}] ({e.get('signs_pos', 0)}/{e['n']} >0)"


def tri_of(base):
    return int(base.split("|")[0][1:])


# ======================================================================= decomp (1B)
if STAGE in ("decomp", "region_split"):
    LREG = META["l_reg"]; REGIONS = META["regions"]
    tables = {"l_reg": LREG, "regions": REGIONS}
    for wname, win in WINDOWS.items():
        for D in ("B", "C"):
            for rname in REGIONS:
                for L in LREG:
                    per = [[] for _ in TRIPLES]
                    for base, cell in CELLS.items():
                        ti = tri_of(base); wc = [CIX[w] for w in cell["words"]]
                        pA = prof(f"{base}|cleanA", wc, win); pD = prof(f"{base}|clean{D}", wc, win)
                        pDA = prof(f"{base}|{D}toA|{rname}|L{L}", wc, win)
                        per[ti].append(restore(pDA, pA, pD))
                    tables[f"R|{D}toA|{rname}|L{L}|{wname}"] = S.cluster_t([np.nanmean(x) for x in per])
    json.dump(tables, open(os.path.join(RES, f"selection_localization_{STAGE}_tables.json"), "w"), indent=1, default=float)
    rep = [f"# H1 · selection_localization — {STAGE} (Step 1B: which position carries the pointer) — run {META['run_id']}\n",
           "## 1. Question\n",
           f"Regions {REGIONS} of the post-tag prefix patched B->A / C->A at L{LREG}; restoration R along the clean A->donor "
           f"presence axis. (region_split: tag / instruction-tail / user-carrier / template-gap / full — Amendment 3, since the "
           f"earlier 'suffix' included the user-side carrier.) Cluster=triple (n={len(TRIPLES)}).\n", "## 2. Restoration R by region\n"]
    for wname in WINDOWS:
        rep.append(f"**{wname}:**")
        for D in ("B", "C"):
            for L in LREG:
                rep.append(f"- {D}->A L{L}: " + "; ".join(f"{rn} {cs(tables[f'R|{D}toA|{rn}|L{L}|{wname}'])}" for rn in REGIONS))
        rep.append("")
    rep.append("## 3. Interpretation and next step\n\n_Filled in by hand._\n")
    open(os.path.join(RES, f"selection_localization_{STAGE}.md"), "w").write("\n".join(rep))
    print("\n".join(rep[4:20]))

# ======================================================================= transfer (1C)
elif STAGE == "transfer":
    DONOR = META["donor"]; LT = META["l_transplant"]
    CONDS = ["cleanA", "cleanB", "cleanC", "BtoA", "CtoA"]

    def m_j(sub, X, Y, win):                                   # pair margin z_donor - z_source at carrier
        z = Z[f"{sub}|z"].astype(np.float32)[win]
        return float((z[:, :, CIX[Y]] - z[:, :, CIX[X]]).mean())

    def Cprofile(base, cond, win):                             # (C_0, C_1, C_2): transfer of each source under `cond`
        words = CELLS[base]["words"]; out = []
        for j in range(3):
            X = words[j]; Y = DONOR[X]
            out.append(m_j(f"{base}|{cond}|swap{j}", X, Y, win) - m_j(f"{base}|{cond}|noswap", X, Y, win))
        return np.array(out)

    tables = {"conds": CONDS, "l_transplant": LT}
    for wname, win in WINDOWS.items():
        # mean transfer profile per condition, and S = pointed - mean(unpointed) per condition
        prof_acc = {c: [] for c in CONDS}; Sacc = {c: [[] for _ in TRIPLES] for c in CONDS}
        rest = {"BtoA": [[] for _ in TRIPLES], "CtoA": [[] for _ in TRIPLES]}
        for base, cell in CELLS.items():
            ti = tri_of(base)
            Cc = {c: Cprofile(base, c, win) for c in CONDS}
            for c in CONDS:
                prof_acc[c].append(Cc[c])
                # pointed slot for cleanA=0, cleanB=1, cleanC=2, BtoA->slot1 (B), CtoA->slot2 (C)
                pt = {"cleanA": 0, "cleanB": 1, "cleanC": 2, "BtoA": 1, "CtoA": 2}[c]
                Sacc[c][ti].append(Cc[c][pt] - np.mean([Cc[c][k] for k in range(3) if k != pt]))
            # restoration of the transfer profile toward the donor-arm ceiling
            rest["BtoA"][ti].append(restore(Cc["BtoA"], Cc["cleanA"], Cc["cleanB"]))
            rest["CtoA"][ti].append(restore(Cc["CtoA"], Cc["cleanA"], Cc["cleanC"]))
        tables[f"Cprofile|{wname}"] = {c: np.mean(prof_acc[c], axis=0).tolist() for c in CONDS}
        tables[f"S|{wname}"] = {c: S.cluster_t([np.mean(x) for x in Sacc[c]]) for c in CONDS}
        tables[f"restore|{wname}"] = {d: S.cluster_t([np.nanmean(x) for x in rest[d]]) for d in ("BtoA", "CtoA")}
    # damage
    dn = []
    for base in CELLS:
        for c in ("BtoA", "CtoA"):
            cn = float(Z[f"{base}|{c}|noswap|nll"])
            for j in range(3):
                dn.append(float(Z[f"{base}|{c}|swap{j}|nll"]) - cn)
    tables["damage_dNLL_max"] = float(np.max(dn))
    json.dump(tables, open(os.path.join(RES, f"selection_localization_{STAGE}_tables.json"), "w"), indent=1, default=float)
    rep = [f"# H1 · selection_localization — transfer (Step 1C: causal-transfer confirmation) — run {META['run_id']}\n",
           "## 1. Question\n",
           f"Does the B->A / C->A instruction-region transplant (block >= {LT}) redirect the *causal transfer* profile C_j "
           f"(source-swap transfer of each of the three sources), not just natural presence? C_j = m_j(swap j) - m_j(noswap), "
           f"m_j = z_donor - z_source at the carrier. Ceilings: clean pointed-A/B/C. Restoration = movement of the B->A transfer "
           f"profile toward clean-B along the A->B axis (and C->A toward C). S = pointed - unpointed transfer per condition. "
           f"Cluster=triple (n={len(TRIPLES)}).\n", "## 2. Transfer profiles and restoration\n"]
    for wname in WINDOWS:
        rep.append(f"**{wname} transfer profile (C_0, C_1, C_2):** " + "; ".join(f"{c} {['%+.2f'%x for x in tables[f'Cprofile|{wname}'][c]]}" for c in CONDS))
        rep.append(f"**{wname} selection S = pointed-unpointed:** " + "; ".join(f"{c} {cs(tables[f'S|{wname}'][c])}" for c in CONDS))
        rep.append(f"**{wname} transfer restoration:** B->A {cs(tables[f'restore|{wname}']['BtoA'])}; C->A {cs(tables[f'restore|{wname}']['CtoA'])}")
        rep.append("")
    rep.append(f"**Damage:** max ΔNLL {tables['damage_dNLL_max']:+.4f}.\n")
    rep.append("## 3. Interpretation and next step\n\n_Filled in by hand._\n")
    open(os.path.join(RES, f"selection_localization_{STAGE}.md"), "w").write("\n".join(rep))
    print("\n".join(rep[4:16]))

# ======================================================================= random_control (Amendment 4)
elif STAGE == "random_control":
    CONDS = META["conds"]; AX = {"B": "B", "C": "C"}
    def donor_of(c):
        for D in ("B", "C"):
            if c.endswith(f"{D}toA") or c.startswith(f"rand{D}") or c == f"shuff{D}" or c == f"flip{D}":
                return D
        return None
    tables = {"conds": CONDS, "l_transplant": META["l_transplant"]}
    for wname, win in WINDOWS.items():
        R_acc = {c: [[] for _ in TRIPLES] for c in CONDS if donor_of(c)}
        dA = {c: [[] for _ in TRIPLES] for c in CONDS if donor_of(c)}; dU = {c: [[] for _ in TRIPLES] for c in CONDS if donor_of(c)}
        for base, cell in CELLS.items():
            ti = tri_of(base); wc = [CIX[w] for w in cell["words"]]
            pA = prof(f"{base}|cleanA", wc, win); pD = {"B": prof(f"{base}|cleanB", wc, win), "C": prof(f"{base}|cleanC", wc, win)}
            for c in R_acc:
                D = donor_of(c); p = prof(f"{base}|{c}", wc, win)
                R_acc[c][ti].append(restore(p, pA, pD[D]))
                d = p - pA; dA[c][ti].append(float(d[0])); dU[c][ti].append(float(np.mean(d[1:])))
        for c in R_acc:
            tables[f"R|{c}|{wname}"] = S.cluster_t([np.nanmean(x) for x in R_acc[c]])
            tables[f"dsA|{c}|{wname}"] = S.cluster_t([np.mean(x) for x in dA[c]])
            tables[f"dsUnpointed|{c}|{wname}"] = S.cluster_t([np.mean(x) for x in dU[c]])
        for D in ("B", "C"):
            rand_mean = [np.mean([np.nanmean(R_acc[f"rand{D}_s{s}"][ti]) for s in META["seeds"]]) for ti in range(len(TRIPLES))]
            tables[f"R_specific|{D}toA|{wname}"] = S.cluster_t([np.nanmean(R_acc[f"{D}toA"][ti]) - rand_mean[ti] for ti in range(len(TRIPLES))])
            tables[f"R_rand_mean|{D}|{wname}"] = S.cluster_t(rand_mean)
    dn, ret = [], []
    for base in CELLS:
        cn = float(Z[f"{base}|cleanA|nll"]); t1 = Z[f"{base}|cleanA|top1"]
        for c in CONDS:
            if donor_of(c):
                dn.append(float(Z[f"{base}|{c}|nll"]) - cn); ret.append(float((Z[f"{base}|{c}|top1"] == t1).mean()))
    tables["damage_dNLL_max"] = float(np.max(dn)); tables["top1_retention_min"] = float(np.min(ret))
    json.dump(tables, open(os.path.join(RES, f"selection_localization_{STAGE}_tables.json"), "w"), indent=1, default=float)
    # figure
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    order = [c for c in CONDS if donor_of(c)]
    for ax, wname in zip(axes, WINDOWS):
        m = [tables[f"R|{c}|{wname}"]["mean"] for c in order]; lo = [m[i] - tables[f"R|{c}|{wname}"]["ci"][0] for i, c in enumerate(order)]; hi = [tables[f"R|{c}|{wname}"]["ci"][1] - m[i] for i, c in enumerate(order)]
        ax.errorbar(range(len(order)), m, yerr=[lo, hi], fmt="o", color="k", capsize=3)
        for i, c in enumerate(order):
            ax.scatter(np.full(len(TRIPLES), i), tables[f"R|{c}|{wname}"]["per_cluster"], s=10, alpha=0.6)
        ax.set_xticks(range(len(order))); ax.set_xticklabels(order, rotation=60, fontsize=8); ax.axhline(0, color="k", lw=0.5); ax.axhline(1, color="grey", lw=0.5, ls="--")
        ax.set_ylabel("restoration R along clean A->donor axis"); ax.set_title(f"{wname}, boundary L{META['l_transplant']} (n=8 triples)", fontsize=9)
    plt.tight_layout(); plt.savefig(os.path.join(FIG, "selection_localization_random_control.png"), dpi=130); plt.close()
    rep = [f"# H1 · selection_localization — random_control (Amendment 4: norm-matched non-specific controls) — run {META['run_id']}\n",
           "## 1. Question\n",
           f"How much of the instruction-region transplant's restoration R (Step 1A) is donor-specific pointer content, and how much would any equal-norm perturbation of the region produce? At boundary L{META['l_transplant']}, beside B->A / C->A, three controls write h_A + delta over the same region: an isotropic direction norm-matched per (layer, position) to the donor delta (two seeds), the donor delta with region positions permuted, and the donor delta sign-flipped. Endpoint: R along the clean A->donor axis, the raw shift of s_A and of the mean unpointed presence, damage. Cluster=triple (n={len(TRIPLES)}). {META['n_forwards']} forwards.\n",
           "## 2. Restoration by condition\n"]
    for wname in WINDOWS:
        rep.append(f"**{wname}:** " + "; ".join(f"{c} {cs(tables[f'R|{c}|{wname}'])}" for c in order))
        rep.append(f"**{wname} donor-specific share R(DtoA) − mean R(rand):** B {cs(tables[f'R_specific|BtoA|{wname}'])}; C {cs(tables[f'R_specific|CtoA|{wname}'])}")
        rep.append(f"**{wname} Δs_A / Δ mean-unpointed:** " + "; ".join(f"{c} {tables[f'dsA|{c}|{wname}']['mean']:+.2f} / {tables[f'dsUnpointed|{c}|{wname}']['mean']:+.2f}" for c in order))
        rep.append("")
    rep.append(f"**Damage:** max ΔNLL {tables['damage_dNLL_max']:+.4f}; top-1 retention min {tables['top1_retention_min']:.3f}.\n")
    rep.append(f"Figure: `figures/selection_localization_random_control.png`. Machine-readable: `selection_localization_{STAGE}_tables.json`.\n")
    rep.append("## 3. Interpretation and next step\n\n_Filled in by hand._\n")
    open(os.path.join(RES, f"selection_localization_{STAGE}.md"), "w").write("\n".join(rep))
    print("\n".join(rep[4:12]))

# ======================================================================= ptr_transplant (1A) — unchanged
else:
    L_SWEEP = META["l_sweep"]
    tables = {"l_sweep": L_SWEEP}
    for wname, win in WINDOWS.items():
        Rd = {D: {L: [[] for _ in TRIPLES] for L in L_SWEEP} for D in ("B", "C")}
        dcomp = {D: {L: [] for L in L_SWEEP} for D in ("B", "C")}
        cleanp = {a: [] for a in TAGS}; axisn = {D: [] for D in ("B", "C")}
        for base, cell in CELLS.items():
            ti = tri_of(base); wc = [CIX[w] for w in cell["words"]]
            pA = prof(f"{base}|cleanA", wc, win); pB = prof(f"{base}|cleanB", wc, win); pC = prof(f"{base}|cleanC", wc, win)
            cleanp["A"].append(pA); cleanp["B"].append(pB); cleanp["C"].append(pC)
            for D, pD in (("B", pB), ("C", pC)):
                axisn[D].append(float(((pD - pA) @ (pD - pA)) ** 0.5))
                for L in L_SWEEP:
                    pDA = prof(f"{base}|{D}toA|L{L}", wc, win)
                    Rd[D][L][ti].append(restore(pDA, pA, pD)); dcomp[D][L].append(pDA - pA)
        tables[f"clean_profile|{wname}"] = {a: np.mean(cleanp[a], axis=0).tolist() for a in TAGS}
        for D in ("B", "C"):
            tables[f"R|{D}toA|{wname}"] = {str(L): S.cluster_t([np.nanmean(Rd[D][L][ti]) for ti in range(len(TRIPLES))]) for L in L_SWEEP}
            tables[f"delta|{D}toA|{wname}"] = {str(L): np.mean(dcomp[D][L], axis=0).tolist() for L in L_SWEEP}
    json.dump(tables, open(os.path.join(RES, f"selection_localization_{STAGE}_tables.json"), "w"), indent=1, default=float)
    print("ptr_transplant re-analyzed ->", f"selection_localization_{STAGE}_tables.json")
