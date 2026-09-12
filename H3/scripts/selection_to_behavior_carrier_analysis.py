"""Scoring pass for selection_to_behavior stage `carrier_only` (Amendment 2). Cluster = triple (n=6); letters scored by
logsumexp over surface forms; internal restoration R along the clean A->donor presence-profile axis at L51-59."""
import os, json
import numpy as np
from scipy import stats as st

HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))
_MK = os.environ.get("TCSIF_MODEL", "")
ROOT = os.path.join(PROJ, "replication_" + _MK) if _MK else PROJ
OUT = os.path.join(ROOT, "H3", "outputs", "selection_to_behavior"); RES = os.path.join(ROOT, "H3", "results"); os.makedirs(RES, exist_ok=True)
m = json.load(open(os.path.join(OUT, "meta_carrier_only.json"))); r = np.load(os.path.join(OUT, "raw_carrier_only.npz"))
L = m["letters"]; ls = lambda a: np.logaddexp(a[:, 0], a[:, 1])


def ct(v):
    v = np.asarray(v, float); n = len(v); mu = v.mean(); h = st.t.ppf(0.975, n - 1) * v.std(ddof=1) / np.sqrt(n)
    return {"mean": mu, "ci": [mu - h, mu + h], "n": n, "pos": int((v > 0).sum()), "per": v.tolist()}


def fmt(c): return f"{c['mean']:+.3f} [{c['ci'][0]:+.3f}, {c['ci'][1]:+.3f}] ({c['pos']}/{c['n']} >0)"
def q(cell, arm, D, A):
    a = m["cells"][cell]["assign"]; s = ls(r[f"{cell}|{arm}|llp"].astype(np.float64)); return s[L.index(a[D])] - s[L.index(a[A])]
def prof(cell, arm, lo=51, hi=59):
    z = r[f"{cell}|{arm}|z"][lo:hi + 1].astype(np.float32).mean(axis=(0, 1)); return z[:3] - z[6:].mean()
def cl(d): return [float(np.mean(v)) for k, v in sorted(d.items())]


ARMS = ["CarrBtoA", "CarrCtoA", "CarrBtoA_all", "CarrCtoA_all", "randCarrB"]
E = {a: {} for a in ARMS}; Rint = {a: {} for a in ARMS}; flips = {a: 0 for a in ARMS}; ceil = {"B": {}, "C": {}}
dist = {a: {} for a in ARMS + ["cleanB", "cleanC"]}; dmg = []; cls = {}
for cell, info in m["cells"].items():
    ti = cell.split("|")[0]; A, B, C = info["A_word"], info["B_word"], info["C_word"]; a = info["assign"]; W = {"B": B, "C": C}
    pA = prof(cell, "cleanA"); P = {"B": prof(cell, "cleanB"), "C": prof(cell, "cleanC")}
    for D in "BC":
        ceil[D].setdefault(ti, []).append(q(cell, f"clean{D}", W[D], A) - q(cell, "cleanA", W[D], A))
        dist[f"clean{D}"].setdefault(ti, []).append(float(r[f"{cell}|clean{D}|ans_dist"][51:60].mean()))
    for arm in ARMS:
        D = "B" if "B" in arm else "C"
        E[arm].setdefault(ti, []).append(q(cell, arm, W[D], A) - q(cell, "cleanA", W[D], A))
        ax = P[D] - pA; Rint[arm].setdefault(ti, []).append(float((prof(cell, arm) - pA) @ ax / (ax @ ax)))
        g = str(r[f"{cell}|{arm}|greedy"]).strip(); flips[arm] += int(g == a[W[D]]); cls.setdefault(arm, {}).setdefault("A" if g == a[A] else ("target" if g == a[W[D]] else "other"), 0); cls[arm]["A" if g == a[A] else ("target" if g == a[W[D]] else "other")] += 1
        dist[arm].setdefault(ti, []).append(float(r[f"{cell}|{arm}|ans_dist"][51:60].mean()))
        dmg.append(float(r[f"{cell}|{arm}|nll"] - r[f"{cell}|cleanA|nll"]))
gate = sum(m["cells"][c]["carr_own_bitwise"] for c in m["cells"])
lines = [f"# H3 · selection_to_behavior — `carrier_only` (Amendment 2: donor carrier states only) — run {m['run_id']}", "",
         f"{m['n_forwards']} forwards ({m['elapsed_s']} s); triples 2–7, carriers C2/C3, 3 rotations = 36 cells; cluster = triple (n=6). Writes over the assistant-carrier positions only; instruction region and source spans asserted untouched (all blocks). Carrier self-patch bitwise no-op {gate}/36; carrier ΔNLL max {max(dmg):+.4f}; read-back error max {max(float(r[k]) for k in r.files if k.endswith('|rberr')):.3g}.", "",
         f"Clean ceilings Δ_B = {np.mean(cl(ceil['B'])):+.2f}, Δ_C = {np.mean(cl(ceil['C'])):+.2f} nats. Answer-position distance from cleanA at L51–59 under the natural donor arms (cleanB / cleanC, which differ in the tag token): {np.mean(cl(dist['cleanB'])):.1f} / {np.mean(cl(dist['cleanC'])):.1f}.", "",
         "| arm | layers | E_D (nats) | E_D/Δ_D | internal restoration R (L51–59) | greedy: A / target / other | answer-pos distance L51–59 |", "|---|---|---|---|---|---|---|"]
TAB = {}
for arm in ARMS:
    D = "B" if "B" in arm else "C"; cE, cR = ct(cl(E[arm])), ct(cl(Rint[arm])); ratio = cE["mean"] / np.mean(cl(ceil[D]))
    TAB[arm] = {"E": cE, "R": cR, "ratio": ratio, "flips": flips[arm], "greedy": cls[arm], "ans_dist_late": float(np.mean(cl(dist[arm])))}
    lines.append(f"| {arm} | {'all 64' if arm.endswith('_all') else '≥ 36'} | {fmt(cE)} | {ratio:.3f} | {fmt(cR)} | {cls[arm].get('A',0)} / {cls[arm].get('target',0)} / {cls[arm].get('other',0)} | {np.mean(cl(dist[arm])):.1f} |")
lines += ["", "R = 1.000 for the donor arms is by construction (the carrier states read at L51–59 are the donor's own from block 36 on); it is reported as the write gate, not as a finding. The informative rows are E_D, the flips and the answer-position distance.", "",
          "## Interpretation", "", "(written by hand; see `selection_to_behavior.md` §6)"]
json.dump(TAB, open(os.path.join(RES, "selection_to_behavior_carrier_only_tables.json"), "w"), indent=1, default=float)
open(os.path.join(RES, "selection_to_behavior_carrier_only.md"), "w").write("\n".join(lines)); print("\n".join(lines))
