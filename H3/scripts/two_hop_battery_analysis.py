"""Scoring pass for two_hop_organism stages `full` and `noclue` (Amendment 3). Cluster = item (n=12 full, 10 noclue),
carriers averaged within item; pairwise scored rule (answer vs swap_answer, logsumexp over surface forms).
Both readout pairs are reported: the maintained ANSWER pair and the BRIDGE (intermediate) pair, at the carrier and at
the question positions. Usage: two_hop_battery_analysis.py [full] [noclue]"""
import os, sys, json
import numpy as np
from scipy import stats as st

HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))
_MK = os.environ.get("TCSIF_MODEL", "")
ROOT = os.path.join(PROJ, "replication_" + _MK) if _MK else PROJ
OUT = os.path.join(ROOT, "H3", "outputs", "two_hop_organism"); RES = os.path.join(ROOT, "H3", "results"); os.makedirs(RES, exist_ok=True)
W = (51, 59)


def ct(v):
    v = np.asarray(v, float); n = len(v); mu = v.mean()
    h = st.t.ppf(0.975, n - 1) * v.std(ddof=1) / np.sqrt(n) if n > 1 else float("nan")
    return {"mean": mu, "ci": [mu - h, mu + h], "n": n, "pos": int((v > 0).sum())}


def fmt(c): return f"{c['mean']:+.2f} [{c['ci'][0]:+.2f}, {c['ci'][1]:+.2f}] ({c['pos']}/{c['n']})"


def run_stage(stage, conds, baseline, lines, TAB):
    m = json.load(open(os.path.join(OUT, f"meta_{stage}.json"))); r = np.load(os.path.join(OUT, f"raw_{stage}.npz"))
    COLS = m["columns"]; cells = list(m["cells"]); items = list(dict.fromkeys(c.split("|")[0] for c in cells))
    def byitem(f): return [float(np.mean([f(c) for c in cells if c.startswith(nm + "|")])) for nm in items]
    marg = lambda c, cond: float(r[f"{c}|{cond}|s_swap"] - r[f"{c}|{cond}|s_answer"])
    def zshift(c, cond, site, a, b):
        def z(t):
            zz = r[f"{c}|{t}|z_{site}"][W[0]:W[1] + 1].astype(np.float32).mean(axis=(0, 1)); return float(zz[COLS.index(b)] - zz[COLS.index(a)])
        return z(cond) - z(baseline)
    ceil = np.mean(byitem(lambda c: marg(c, "donor_clean") - marg(c, baseline)))
    lines += [f"# H3 · two_hop_organism — `{stage}` (Amendment 3) — run {m['run_id']}", "",
              f"{m['n_forwards']} forwards ({m['elapsed_s']} s); {len(items)} items × {m['carriers']} = {len(cells)} cells; cluster = item (n={len(items)}); "
              f"materials {m['materials']}. Question: \"{m['question']}\" (never restates the clue). Natural ceiling Δ (donor clue − recipient) = **{ceil:+.2f} nats**.", ""]
    dmg = [float(r[f"{c}|{cond}|nll"] - r[f"{c}|{baseline}|nll"]) for c in cells for cond in conds]
    gate = [m["cells"][c].get("Q_own_bitwise") for c in cells if "Q_own_bitwise" in m["cells"][c]]
    lines.append(f"**Gates.** Clue span asserted untouched under every carrier/question write; prefix untouched under question writes."
                 + (f" Q self-patch bitwise {sum(gate)}/{len(gate)}." if gate else "")
                 + f" Carrier ΔNLL max {max(dmg):+.4f} (all-block clue-span replacement is the largest; carrier writes ≤ {max([d for c in cells for cond in conds if cond.startswith('C') for d in [float(r[f'{c}|{cond}|nll'] - r[f'{c}|{baseline}|nll'])]] or [0]):+.4f})."
                 + f" Read-back error max {max([float(r[k]) for k in r.files if k.endswith('|rberr')] or [0]):.2g}.\n")
    base_fl = sum(int(marg(c, baseline) > 0) for c in cells)
    lines.append(f"Baseline: the donor answer already wins in {base_fl}/{len(cells)} cells under `{baseline}` (clean competence miss); read every flip count against that floor.\n")
    lines.append("| condition | answer margin toward the donor answer (nats) | share of Δ | flips | ANSWER pair shift at carrier | at question | BRIDGE pair shift at carrier | at question |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for cond in conds:
        beh = ct(byitem(lambda c: marg(c, cond) - marg(c, baseline)))
        fl = sum(int(marg(c, cond) > 0) for c in cells)
        A = {s: ct(byitem(lambda c: zshift(c, cond, s, m["cells"][c]["answer"], m["cells"][c]["swap_answer"]))) for s in ("carr", "q")}
        B = {s: ct(byitem(lambda c: zshift(c, cond, s, m["cells"][c]["intermediate"], m["cells"][c]["swap_to"]))) for s in ("carr", "q")}
        TAB[f"{stage}|{cond}"] = {"beh": beh, "flips": fl, "n_cells": len(cells), "share": beh["mean"] / ceil,
                                  "answer_pair": {k: v for k, v in A.items()}, "bridge_pair": {k: v for k, v in B.items()}}
        lines.append(f"| `{cond}` | {fmt(beh)} | {beh['mean']/ceil:.2f} | {fl}/{len(cells)} | {fmt(A['carr'])} | {fmt(A['q'])} | {fmt(B['carr'])} | {fmt(B['q'])} |")
    lines.append("")
    if stage == "noclue":
        lines.append("Endpoint restated in the direction of the transplanted entity's own answer (positive = the answer of the entity whose carrier was installed):\n")
        lines.append("| condition | Δ[logP(installed entity's answer) − logP(other)] | pairwise winner = installed entity's answer |"); lines.append("|---|---|---|")
        base_own = sum(int(marg(c, baseline) < 0) for c in cells)
        for cond in conds:
            own_installed = cond in ("C_from_E", "Q_from_E")
            sgn = -1 if own_installed else 1
            v = ct(byitem(lambda c: sgn * (marg(c, cond) - marg(c, baseline))))
            hit = sum(int((marg(c, cond) < 0) if own_installed else (marg(c, cond) > 0)) for c in cells)
            ref = base_own if own_installed else len(cells) - base_own
            lines.append(f"| `{cond}` | {fmt(v)} | {hit}/{len(cells)} (same direction under the placeholder clue alone: {ref}/{len(cells)}) |")
        lines.append("")
    return m, ceil


lines, TAB = [], {}
for stg in (sys.argv[1:] or ["full", "noclue"]):
    if stg == "full":
        run_stage("full", ["S_donor0", "S_donor", "C_full", "C_all", "C_rand", "NEC_all", "NEC36", "Q_donor", "Q_own"], "clean", lines, TAB)
    else:
        run_stage("noclue", ["C_from_E", "C_from_E2", "C_rand_nc", "Q_from_E"], "clean_nc", lines, TAB)
lines += ["## Interpretation", "", "(written by hand after reading the tables)"]
json.dump(TAB, open(os.path.join(RES, "two_hop_organism_tables.json"), "w"), indent=1, default=float)
open(os.path.join(RES, "two_hop_organism.md"), "w").write("\n".join(lines)); print("\n".join(lines))
