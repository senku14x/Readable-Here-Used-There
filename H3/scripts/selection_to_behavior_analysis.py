"""Analysis for H3 selection_to_behavior v2 (pilot or evaluate). Single scoring pass over raw_<stage>_v2.npz.

Reads the audit-corrected battery outputs (meta_<stage>_v2.json / raw_<stage>_v2.npz):
  - letter scores use LOGSUMEXP over the two surface forms per letter (llp[8,2]); never the max form.
  - two matched-norm random controls: randB (scaled to ||h_B - h_A||) is the control for B->A, randC (scaled to
    ||h_C - h_A||) is the control for C->A. Each transplant has its own norm-matched control.
  - realized write diagnostics come from the run itself (per-arm wnorm, readback error, self-patch bitwise no-op),
    not a hardcoded placeholder.

Primary (noswap): direct redirect E_D = q_D(DtoA) - q_D(cleanA), q_D = logP(F(word_D)) - logP(F(word_A)) at the answer
token; ceiling Delta_D = q_D(cleanD) - q_D(cleanA); matched control E_D(randD); restoration as ratio-of-means (never
per-cell ratios averaged); five-way answer classification.
Organism gate: internal presence restoration of the transplant reproduces H1 (~0.77). That is the gate that matters;
the absolute with/without-consumer z offset is a length-dependent linear-attention kernel effect (verified: an
equal-length different-content control gives 0.0 residual difference at every block, a different-length control diverges
from block 0) that cancels in the with-consumer contrasts. The specific kernel mechanism is not independently confirmed.
Secondary (evaluate, source swaps): C_j^R internal and C_j^B behavioral source-sensitivity profiles + their restoration.

The crossed source-margin table is reported as a raw OBSERVATION of margin shifts. No causal specific/non-specific
decomposition is drawn from it.

Usage: selection_to_behavior_analysis.py [pilot|evaluate]
"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "common", "scripts"))
import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
import registry as R
import stats as S

STAGE = sys.argv[1] if len(sys.argv) > 1 else "evaluate"
OUT = os.path.join(R.PROJECT, "H3", "outputs", "selection_to_behavior"); RES = os.path.join(R.PROJECT, "H3", "results"); FIG = os.path.join(RES, "figures")
os.makedirs(FIG, exist_ok=True)
META = json.load(open(os.path.join(OUT, f"meta_{STAGE}_v2.json"))); Z = np.load(os.path.join(OUT, f"raw_{STAGE}_v2.npz"))
CELLS = META["cells"]; LETTERS = META["letters"]; WIN = {"L48-50": [48, 49, 50], "L51-59": list(range(51, 60))}
cells = list(CELLS.keys()); ncell = len(cells); FULL = META.get("full", False)


def cs(e):
    return f"{e['mean']:+.3f} [{e['ci'][0]:+.3f}, {e['ci'][1]:+.3f}] ({e.get('signs_pos',0)}/{e['n']} >0)"


def presence_profile(tag, win):
    z = Z[f"{tag}|z"].astype(np.float32)[win]; dec = z[:, :, 6:14].mean(-1)
    return np.array([(z[:, :, j] - dec).mean() for j in range(3)])


def transfer_profile(tag_arm, win):                       # C_j^R = m_j(swap j) - m_j(noswap), m_j = z[donor_j]-z[word_j]
    def m(sub, j):
        z = Z[f"{sub}|z"].astype(np.float32)[win]; return float((z[:, :, 3 + j] - z[:, :, j]).mean())
    return np.array([m(f"{tag_arm}|swap{j}", j) - m(f"{tag_arm}|noswap", j) for j in range(3)])


def restore(pDA, pA, pD):
    ax = pD - pA; nn = float(ax @ ax); return float((pDA - pA) @ ax / nn) if nn > 1e-9 else np.nan


def lsc(tag):
    """Per-letter answer score = logsumexp over the two surface forms (bare, space-prefixed); absent form is -1e30."""
    a = Z[f"{tag}|llp"].astype(np.float64)
    return {L: float(np.logaddexp(a[i, 0], a[i, 1])) for i, L in enumerate(LETTERS)}


def qmargin(tag, wD, wA, asg):
    s = lsc(tag); return s[asg[wD]] - s[asg[wA]]


# CLUSTER = TRIPLE (project convention). Per-cell values are averaged over rotations and carriers within a triple first.
TI = [c.split("|")[0] for c in cells]
def agg(v):
    d = {}
    for t, x in zip(TI, v): d.setdefault(t, []).append(x)
    return [float(np.nanmean(d[t])) for t in sorted(d)]
def ct(v): return S.cluster_t(agg(v))
def rom(a, b): return S.ratio_of_means(agg(a), agg(b))

n_triples = len(set(TI))
T = {"stage": STAGE, "n_cells": ncell, "n_triples": n_triples, "scoring": "logsumexp over surface forms"}

# ---- realized write diagnostics (from the run, not a placeholder)
wd = {}
for arm in ("BtoA", "CtoA", "randB", "randC"):
    wn = [float(Z[f"{c}|{arm}|wnorm"]) for c in cells]; rb = [float(Z[f"{c}|{arm}|rberr"]) for c in cells]
    wd[arm] = {"mean_write_norm": float(np.mean(wn)), "max_readback_err": float(np.max(rb))}
wd["rho_randB_over_BtoA"] = float(np.mean([float(Z[f"{c}|randB|wnorm"]) / float(Z[f"{c}|BtoA|wnorm"]) for c in cells]))
wd["rho_randC_over_CtoA"] = float(np.mean([float(Z[f"{c}|randC|wnorm"]) / float(Z[f"{c}|CtoA|wnorm"]) for c in cells]))
wd["CtoA_over_BtoA_norm"] = float(np.mean([float(Z[f"{c}|CtoA|wnorm"]) / float(Z[f"{c}|BtoA|wnorm"]) for c in cells]))
wd["selfpatch_bitwise_noop"] = f"{sum(bool(CELLS[c].get('selfpatch_bitwise', False)) for c in cells)}/{ncell}"
T["write_diagnostics"] = wd

# ---- organism gate: internal presence restoration of the transplant (noswap)
for wn, win in WIN.items():
    rB, rC, sB, sC = [], [], [], []
    for c in cells:
        pA = presence_profile(f"{c}|cleanA|noswap", win); pB = presence_profile(f"{c}|cleanB|noswap", win); pC = presence_profile(f"{c}|cleanC|noswap", win)
        rB.append(restore(presence_profile(f"{c}|BtoA|noswap", win), pA, pB)); rC.append(restore(presence_profile(f"{c}|CtoA|noswap", win), pA, pC))
        sB.append(float(((pB - pA) @ (pB - pA)) ** .5)); sC.append(float(((pC - pA) @ (pC - pA)) ** .5))
    T[f"internal_presence_restore_BtoA|{wn}"] = ct(rB); T[f"internal_presence_restore_CtoA|{wn}"] = ct(rC)
    T[f"axis_sep_B|{wn}"] = float(np.mean(sB)); T[f"axis_sep_C|{wn}"] = float(np.mean(sC))

# ---- primary behavioral (noswap); randB is the matched control for B->A, randC for C->A
EB, EC, ERB, ERC, dB, dC = [], [], [], [], [], []
cls = {a: {"A": 0, "tgt": 0, "donor": 0, "other": 0, "invalid": 0} for a in ("cleanA", "cleanB", "cleanC", "BtoA", "CtoA", "randB", "randC")}
for c in cells:
    cm = CELLS[c]; wA, wB, wC = cm["words"]; asg = cm["assign"]; l2w = {asg[x]: x for x in asg}
    EB.append(qmargin(f"{c}|BtoA|noswap", wB, wA, asg) - qmargin(f"{c}|cleanA|noswap", wB, wA, asg))
    EC.append(qmargin(f"{c}|CtoA|noswap", wC, wA, asg) - qmargin(f"{c}|cleanA|noswap", wC, wA, asg))
    ERB.append(qmargin(f"{c}|randB|noswap", wB, wA, asg) - qmargin(f"{c}|cleanA|noswap", wB, wA, asg))
    ERC.append(qmargin(f"{c}|randC|noswap", wC, wA, asg) - qmargin(f"{c}|cleanA|noswap", wC, wA, asg))
    dB.append(qmargin(f"{c}|cleanB|noswap", wB, wA, asg) - qmargin(f"{c}|cleanA|noswap", wB, wA, asg))
    dC.append(qmargin(f"{c}|cleanC|noswap", wC, wA, asg) - qmargin(f"{c}|cleanA|noswap", wC, wA, asg))
    for arm, tgt in (("cleanA", wA), ("cleanB", wB), ("cleanC", wC), ("BtoA", wB), ("CtoA", wC), ("randB", wB), ("randC", wC)):
        g = str(Z[f"{c}|{arm}|noswap|greedy"]) if f"{c}|{arm}|noswap|greedy" in Z else str(Z[f"{c}|{arm}|greedy"])
        ow = l2w.get(g)
        if ow is None: cls[arm]["invalid"] += 1
        elif ow == wA: cls[arm]["A"] += 1
        elif ow == tgt: cls[arm]["tgt"] += 1
        else: cls[arm]["other"] += 1
T["E_B"] = ct(EB); T["E_C"] = ct(EC); T["E_B_randB"] = ct(ERB); T["E_C_randC"] = ct(ERC)
T["ceiling_D_B"] = ct(dB); T["ceiling_D_C"] = ct(dC)
T["restore_behav_B_ratio"] = rom(EB, dB); T["restore_behav_C_ratio"] = rom(EC, dC)
# transplant-minus-matched-control specificity contrast
T["E_B_minus_randB"] = ct([a - b for a, b in zip(EB, ERB)]); T["E_C_minus_randC"] = ct([a - b for a, b in zip(EC, ERC)])
# equivalence band context: 0.2 * D
T["equiv_eps_B"] = 0.2 * float(np.mean(dB)); T["equiv_eps_C"] = 0.2 * float(np.mean(dC))
T["answer_class_noswap"] = cls

# ---- crossed source margins: OBSERVATION only. Report how each transplant shifts each source's margin; no causal split.
XB_underB, XC_underB, XB_underC, XC_underC = [], [], [], []
for c in cells:
    cm = CELLS[c]; wA, wB, wC = cm["words"]; asg = cm["assign"]
    base_B = qmargin(f"{c}|cleanA|noswap", wB, wA, asg); base_C = qmargin(f"{c}|cleanA|noswap", wC, wA, asg)
    XB_underB.append(qmargin(f"{c}|BtoA|noswap", wB, wA, asg) - base_B)
    XC_underB.append(qmargin(f"{c}|BtoA|noswap", wC, wA, asg) - base_C)
    XB_underC.append(qmargin(f"{c}|CtoA|noswap", wB, wA, asg) - base_B)
    XC_underC.append(qmargin(f"{c}|CtoA|noswap", wC, wA, asg) - base_C)
T["crossed_observed"] = {"BtoA_shifts_B_margin": ct(XB_underB), "BtoA_shifts_C_margin": ct(XC_underB),
                         "CtoA_shifts_B_margin": ct(XB_underC), "CtoA_shifts_C_margin": ct(XC_underC)}

# ---- secondary source-sensitivity profiles (evaluate only)
if FULL:
    for wn, win in WIN.items():
        rBi, rCi = [], []
        for c in cells:
            pA = transfer_profile(f"{c}|cleanA", win); pB = transfer_profile(f"{c}|cleanB", win); pC = transfer_profile(f"{c}|cleanC", win)
            rBi.append(restore(transfer_profile(f"{c}|BtoA", win), pA, pB)); rCi.append(restore(transfer_profile(f"{c}|CtoA", win), pA, pC))
        T[f"internal_transfer_restore_BtoA|{wn}"] = ct(rBi); T[f"internal_transfer_restore_CtoA|{wn}"] = ct(rCi)
    # behavioral transfer profile C_j^B and its restoration (window-free: uses letter scores)
    rBb, rCb = [], []
    for c in cells:
        cm = CELLS[c]
        def prof(arm):
            out = []
            for j in range(3):
                sn = lsc(f"{c}|{arm}|noswap"); ss = lsc(f"{c}|{arm}|swap{j}")
                dj = cm["assign"][cm["donors"][j]]; xj = cm["assign"][cm["words"][j]]
                out.append((ss[dj] - ss[xj]) - (sn[dj] - sn[xj]))
            return np.array(out)
        pA = prof("cleanA"); pB = prof("cleanB"); pC = prof("cleanC")
        rBb.append(restore(prof("BtoA"), pA, pB)); rCb.append(restore(prof("CtoA"), pA, pC))
    T["behav_transfer_restore_BtoA"] = ct(rBb); T["behav_transfer_restore_CtoA"] = ct(rCb)

json.dump(T, open(os.path.join(RES, f"selection_to_behavior_{STAGE}_tables.json"), "w"), indent=1, default=float)

# ---- figure: internal vs behavioral restoration
fig, ax = plt.subplots(figsize=(7, 4.5))
rows = [("internal presence B->A", T["internal_presence_restore_BtoA|L51-59"]),
        ("internal presence C->A", T["internal_presence_restore_CtoA|L51-59"]),
        ("behavioral redirect B (E_B/D_B)", T["restore_behav_B_ratio"]),
        ("behavioral redirect C (E_C/D_C)", T["restore_behav_C_ratio"])]
if FULL:
    rows[2:2] = [("internal transfer B->A", T["internal_transfer_restore_BtoA|L51-59"]),
                 ("internal transfer C->A", T["internal_transfer_restore_CtoA|L51-59"]),
                 ("behavioral transfer B->A", T["behav_transfer_restore_BtoA"]),
                 ("behavioral transfer C->A", T["behav_transfer_restore_CtoA"])]
for i, (nm, e) in enumerate(rows):
    m = e.get("mean", e.get("ratio")); ci = e.get("ci", [np.nan, np.nan])
    ax.errorbar(m, i, xerr=[[m - ci[0]], [ci[1] - m]], fmt="o", color="C0" if "internal" in nm else "C3", capsize=3)
    if "per_cluster" in e:
        ax.scatter(e["per_cluster"], np.full(len(e["per_cluster"]), i), s=10, alpha=0.4, color="C0" if "internal" in nm else "C3")
ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows], fontsize=8)
ax.axvline(0, color="k", lw=0.5); ax.axvline(1, color="grey", lw=0.5, ls="--")
ax.set_xlabel("restoration toward the clean-donor profile (1 = full)"); ax.set_title(f"selection_to_behavior {STAGE} v2 (n={ncell} cells, {n_triples} triples)", fontsize=9)
plt.tight_layout(); plt.savefig(os.path.join(FIG, f"selection_to_behavior_{STAGE}.png"), dpi=130); plt.close()

print(f"== {STAGE} v2 (n={ncell} cells, {n_triples} triples) ==")
print("WRITE DIAGNOSTICS (from the run):")
print(f"  rho randB/BtoA {wd['rho_randB_over_BtoA']:.4f}  randC/CtoA {wd['rho_randC_over_CtoA']:.4f}  CtoA/BtoA norm {wd['CtoA_over_BtoA_norm']:.4f}")
print(f"  max readback err  BtoA {wd['BtoA']['max_readback_err']:.1e}  CtoA {wd['CtoA']['max_readback_err']:.1e}  self-patch bitwise no-op {wd['selfpatch_bitwise_noop']}")
print("ORGANISM GATE (internal presence restoration, should ~0.77):")
print("  B->A L51-59", cs(T["internal_presence_restore_BtoA|L51-59"]), " C->A", cs(T["internal_presence_restore_CtoA|L51-59"]))
print("PRIMARY behavioral (noswap):")
print("  E_B", cs(T["E_B"]), " ceiling D_B", cs(T["ceiling_D_B"]), " restore", f"{T['restore_behav_B_ratio']['ratio']:+.3f}")
print("  E_C", cs(T["E_C"]), " ceiling D_C", cs(T["ceiling_D_C"]), " restore", f"{T['restore_behav_C_ratio']['ratio']:+.3f}")
print("  matched control E_B(randB)", cs(T["E_B_randB"]), " E_B - randB", cs(T["E_B_minus_randB"]))
print("  matched control E_C(randC)", cs(T["E_C_randC"]), " E_C - randC", cs(T["E_C_minus_randC"]))
print("  answer class (noswap):", json.dumps(T["answer_class_noswap"]))
print("CROSSED SOURCE MARGINS (observation only; triple-clustered):")
print("             shifts B margin        shifts C margin")
print("  BtoA  ", cs(T["crossed_observed"]["BtoA_shifts_B_margin"]), " ", cs(T["crossed_observed"]["BtoA_shifts_C_margin"]))
print("  CtoA  ", cs(T["crossed_observed"]["CtoA_shifts_B_margin"]), " ", cs(T["crossed_observed"]["CtoA_shifts_C_margin"]))
if FULL:
    print("SECONDARY:")
    print("  internal transfer restore B->A", cs(T["internal_transfer_restore_BtoA|L51-59"]), " behavioral transfer restore B->A", cs(T["behav_transfer_restore_BtoA"]))
print(f"\nFigure: figures/selection_to_behavior_{STAGE}.png ; tables: selection_to_behavior_{STAGE}_tables.json")
