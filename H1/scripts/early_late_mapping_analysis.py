"""Analysis for H1 early_late_mapping (+ Amendment 1). Reads raw_run.npz.

Competence per condition (answer top-1 == F(X) letter). Carrier readouts:
  s_X = z_X - mean z_decoys ; s_L = z_L - mean(other 7 codebook letters).
Central estimand E_F^sc = s_F(X) - s_F(Y) under the SAME usable codebook (source-conditioned; transformation signal).
Usability contrast E_X = s_X^{early_usable} - s_X^{early_unusable} (mapping availability vs generic long-prefix effect).
Also E_F = s_F(X)^{early_usable} - s_F(X)^{late} ; raw E_X^{late-eu} = s_X^{late} - s_X^{early_usable}. Cluster = word (n=32).

Usage: early_late_mapping_analysis.py run
"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "common", "scripts"))
import numpy as np
import registry as R
import stats as S

STAGE = sys.argv[1] if len(sys.argv) > 1 else "run"
OUT = os.path.join(R.out_dir("H1", "outputs"), "early_late_mapping"); RES = os.path.join(R.out_dir("H1", "results"))
META = json.load(open(os.path.join(OUT, f"meta_{STAGE}.json"))); Z = np.load(os.path.join(OUT, f"raw_{STAGE}.npz"))
COLS = META["columns"]; CIX = {w: i for i, w in enumerate(COLS)}; LETTERS = META["letters"]; DEC = [CIX[d] for d in META["decoys"]]
WORDS = META["words"]; CARRIERS = META["carriers"]; CELLS = META["cells"]; LNS = META["letter_ns_ids"]
WINDOWS = {"L48-50": [48, 49, 50], "L51-59": list(range(51, 60))}


def sX(sub, X, win, inst):
    if inst == "LOGITS":
        lp = Z[f"{sub}|lp"]; return float(lp[:, CIX[X]].mean() - lp[:, DEC].mean())
    z = Z[f"{sub}|z"].astype(np.float32)[win]; return float((z[:, :, CIX[X]] - z[:, :, DEC].mean(-1)).mean())


def sL(sub, L, win, inst):
    others = [CIX[x] for x in LETTERS if x != L]
    if inst == "LOGITS":
        lp = Z[f"{sub}|lp"]; return float(lp[:, CIX[L]].mean() - lp[:, others].mean())
    z = Z[f"{sub}|z"].astype(np.float32)[win]; return float((z[:, :, CIX[L]] - z[:, :, others].mean(-1)).mean())


def cs(e):
    return "n/a" if e is None else f"{e['mean']:+.3f} [{e['ci'][0]:+.3f}, {e['ci'][1]:+.3f}] ({e.get('signs_pos', 0)}/{e['n']} >0)"


# competence
comp = {"early_usable": [], "late": []}
for tag, c in CELLS.items():
    if c["cond"] in comp:
        a = int(Z[f"{tag}|ans_top1"]); comp[c["cond"]].append(a == c["FX_ns_id"] or a == c["FX_ls_id"])
tables = {"competence": {k: float(np.mean(v)) for k, v in comp.items()}}

for inst in ("J_NP", "LOGITS"):
    for wname, win in ([("out", None)] if inst == "LOGITS" else list(WINDOWS.items())):
        key = inst + ("" if inst == "LOGITS" else f"|{wname}")
        EFsc, EX_use, EF, EXraw = [], [], [], []
        sXd = {"early_usable": [], "early_unusable": [], "late": []}
        sFXd = {"early_usable": [], "late": []}
        for X in WORDS:
            efsc, exu, ef, exr = [], [], [], []
            sxc = {k: [] for k in sXd}; sfx = {k: [] for k in sFXd}
            for seed in (1, 2):
                for ck in CARRIERS:
                    base = f"{X}|s{seed}|{ck}"
                    eu, ex, la = f"{base}|early_usable", f"{base}|early_unusable", f"{base}|late"
                    FX = CELLS[eu]["FX"]; FY = CELLS[eu]["FY"]
                    efsc.append(sL(eu, FX, win, inst) - sL(eu, FY, win, inst))
                    exu.append(sX(eu, X, win, inst) - sX(ex, X, win, inst))
                    ef.append(sL(eu, FX, win, inst) - sL(la, FX, win, inst))
                    exr.append(sX(la, X, win, inst) - sX(eu, X, win, inst))
                    for cond, t in (("early_usable", eu), ("early_unusable", ex), ("late", la)):
                        sxc[cond].append(sX(t, X, win, inst))
                    sfx["early_usable"].append(sL(eu, FX, win, inst)); sfx["late"].append(sL(la, FX, win, inst))
            EFsc.append(np.mean(efsc)); EX_use.append(np.mean(exu)); EF.append(np.mean(ef)); EXraw.append(np.mean(exr))
            for k in sXd: sXd[k].append(np.mean(sxc[k]))
            for k in sFXd: sFXd[k].append(np.mean(sfx[k]))
        tables[key] = {"E_F_sourcecond": S.cluster_t(EFsc), "E_X_usability": S.cluster_t(EX_use),
                       "E_F": S.cluster_t(EF), "E_X_raw_late_minus_eu": S.cluster_t(EXraw),
                       "sX": {k: S.cluster_t(v)["mean"] for k, v in sXd.items()},
                       "sFX": {k: S.cluster_t(v)["mean"] for k, v in sFXd.items()}}
json.dump(tables, open(os.path.join(RES, "early_late_mapping_run_tables.json"), "w"), indent=1, default=float)

rep = [f"# H1 · early_late_mapping — run {META['run_id']}\n", "## 1. Setup\n",
       f"Does mapping availability change whether the carrier expresses X or F(X)? Conditions: early_usable (codebook incl X before "
       f"carrier), early_unusable (length-matched codebook over 8 other words), late (codebook after). 32 words x 2 mappings x 2 "
       f"carriers; cluster=word (n=32). Central: E_F^sc = s_F(X)-s_F(Y) under the same usable codebook (transformation signal, "
       f"source-conditioned). E_X_usability = s_X^eu - s_X^unusable (controls the generic long-prefix effect). {META['n_forwards']} forwards.\n",
       "## 2. Competence\n",
       f"- answer accuracy: early_usable {tables['competence']['early_usable']:.3f}, late {tables['competence']['late']:.3f} (gate >= 0.90).\n",
       "## 3. Carrier endpoints\n"]
for key in ("J_NP|L48-50", "J_NP|L51-59", "LOGITS"):
    T = tables[key]
    rep.append(f"- **{key}:** E_F^sc {cs(T['E_F_sourcecond'])}; E_X_usability {cs(T['E_X_usability'])}; E_F {cs(T['E_F'])}; "
               f"raw E_X(late-eu) {cs(T['E_X_raw_late_minus_eu'])}. s_X[eu/unusable/late]={[round(T['sX'][k],2) for k in ('early_usable','early_unusable','late')]}; s_F(X)[eu/late]={[round(T['sFX'][k],2) for k in ('early_usable','late')]}.")
rep.append("\n## 4. Interpretation\n\n_Filled in by hand. Transformation needs E_F^sc>0 (source-conditioned) AND E_X_usability>0; E_F without source-conditioning is codebook priming; both near 0 with competence>=0.9 is a scope null._\n")
open(os.path.join(RES, "early_late_mapping_run.md"), "w").write("\n".join(rep))
print("\n".join(rep[3:10]))
