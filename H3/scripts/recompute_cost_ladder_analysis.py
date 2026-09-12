"""Scoring pass for recompute_cost_ladder. Cluster = item (n=8 per tier), carriers averaged within item.
Answer rule: argmax over the 19 number words (logsumexp over surface forms); margin = logP(donor latent) - logP(own latent).
Each tier is normalised by its OWN ceiling (donor_clean - clean). Primary contrast: t1 vs t3 (identical source strings)."""
import os, json
import numpy as np
from scipy import stats as st

HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))
_MK = os.environ.get("TCSIF_MODEL", "")
ROOT = os.path.join(PROJ, "replication_" + _MK) if _MK else PROJ
OUT = os.path.join(ROOT, "H3", "outputs", "recompute_cost_ladder"); RES = os.path.join(ROOT, "H3", "results"); os.makedirs(RES, exist_ok=True)
m = json.load(open(os.path.join(OUT, "meta_run.json"))); r = np.load(os.path.join(OUT, "raw_run.npz"))
AO = m["answer_order"]; COLS = m["columns"]; W = (51, 59)
TIERS = ["t1_memorised", "t3_chained", "t2_composed"]
NICE = {"t1_memorised": "t1 memorised (a+b)", "t3_chained": "t3 chained (2(a+b), same source as t1)", "t2_composed": "t2 composed (a+b+c)"}
CONDS = ["S_donor0", "S_donor", "C_full", "C_all", "C_rand", "NEC_all"]


def ct(v):
    v = np.asarray(v, float); n = len(v); mu = v.mean()
    h = st.t.ppf(0.975, n - 1) * v.std(ddof=1) / np.sqrt(n) if n > 1 else float("nan")
    return {"mean": mu, "ci": [mu - h, mu + h], "n": n, "pos": int((v > 0).sum())}


def fmt(c): return f"{c['mean']:+.2f} [{c['ci'][0]:+.2f}, {c['ci'][1]:+.2f}] ({c['pos']}/{c['n']})"
def cells_of(t): return [c for c in m["cells"] if m["cells"][c]["tier"] == t]
def items_of(t): return sorted({m["cells"][c]["item"] for c in cells_of(t)})
def byitem(t, f): return [float(np.mean([f(c) for c in cells_of(t) if m["cells"][c]["item"] == i])) for i in items_of(t)]
def marg(c, cond):
    s = r[f"{c}|{cond}|scores"]; k = m["cells"][c]
    return float(s[AO.index(k["donor_latent"])] - s[AO.index(k["latent"])])
def zsh(c, cond, site):
    k = m["cells"][c]
    def z(t):
        zz = r[f"{c}|{t}|z_{site}"][W[0]:W[1] + 1].astype(np.float32).mean(axis=(0, 1))
        return float(zz[COLS.index(k["donor_latent"])] - zz[COLS.index(k["latent"])])
    return z(cond) - z("clean")


lines = [f"# H3 · recompute_cost_ladder — run {m['run_id']}", "",
         f"{m['n_forwards']} forwards ({m['elapsed_s']} s); 3 tiers × 8 items × {m['carriers']} = {len(m['cells'])} cells; cluster = item (n=8 per tier). "
         "Each tier is normalised by its own ceiling Δ = donor_clean − clean. `t1` and `t3` use **identical source strings and donors** and differ only in the instruction and the question.", ""]
TAB = {}
lines.append("## Competence gate (scored argmax over the 19 number words = the true latent)\n")
lines.append("| tier | latents | clean competence | ceiling Δ (nats) |"); lines.append("|---|---|---|---|")
CEIL = {}
for t in TIERS:
    cc = cells_of(t)
    comp = np.mean([int(r[f"{c}|clean|scores"].argmax() == AO.index(m["cells"][c]["latent"])) for c in cc])
    CEIL[t] = float(np.mean(byitem(t, lambda c: marg(c, "donor_clean") - marg(c, "clean"))))
    TAB[f"{t}|competence"] = float(comp); TAB[f"{t}|ceiling"] = CEIL[t]
    lines.append(f"| {NICE[t]} | {', '.join(sorted({m['cells'][c]['latent'] for c in cc}, key=lambda w: AO.index(w)))} | **{comp:.3f}** {'PASS' if comp >= 0.9 else '**FAIL (rows not interpreted)**'} | {CEIL[t]:+.2f} |")
lines.append("")
for t in TIERS:
    cc = cells_of(t); floor = sum(int(marg(c, "clean") > 0) for c in cc)
    lines.append(f"## {NICE[t]} — ceiling {CEIL[t]:+.2f} nats; flip floor under clean {floor}/{len(cc)}\n")
    lines.append("| condition | answer margin toward the donor latent | share of Δ | flips | latent shift at carrier | at question | ΔNLL max |")
    lines.append("|---|---|---|---|---|---|---|")
    for cond in CONDS:
        beh = ct(byitem(t, lambda c: marg(c, cond) - marg(c, "clean")))
        fl = sum(int(marg(c, cond) > 0) for c in cc)
        zc = ct(byitem(t, lambda c: zsh(c, cond, "carr"))); zq = ct(byitem(t, lambda c: zsh(c, cond, "q")))
        dn = max(float(r[f"{c}|{cond}|nll"] - r[f"{c}|clean|nll"]) for c in cc)
        TAB[f"{t}|{cond}"] = {"beh": beh, "share": beh["mean"] / CEIL[t], "flips": fl, "n": len(cc), "z_carr": zc, "z_q": zq, "dNLL_max": dn}
        lines.append(f"| `{cond}` | {fmt(beh)} | {beh['mean']/CEIL[t]:.2f} | {fl}/{len(cc)} | {fmt(zc)} | {fmt(zq)} | {dn:+.4f} |")
    lines.append("")
lines.append("## The registered contrast: carrier share vs boundary position, by tier\n")
lines.append("| tier | competence | carrier share `C_full` | carrier share `C_all` | boundary: source share at ≥36 | source share all blocks | `NEC_all` share |")
lines.append("|---|---|---|---|---|---|---|")
for t in TIERS:
    g = lambda c: TAB[f"{t}|{c}"]["share"]
    lines.append(f"| {NICE[t]} | {TAB[f'{t}|competence']:.3f} | **{g('C_full'):.2f}** | {g('C_all'):.2f} | **{g('S_donor'):.2f}** | {g('S_donor0'):.2f} | {g('NEC_all'):.2f} |")
lines.append("")
d13 = ct(np.array(byitem("t3_chained", lambda c: marg(c, "C_full") - marg(c, "clean"))) / CEIL["t3_chained"]
          - np.array(byitem("t1_memorised", lambda c: marg(c, "C_full") - marg(c, "clean"))) / CEIL["t1_memorised"])
b13 = ct(np.array(byitem("t3_chained", lambda c: marg(c, "S_donor") - marg(c, "clean"))) / CEIL["t3_chained"]
         - np.array(byitem("t1_memorised", lambda c: marg(c, "S_donor") - marg(c, "clean"))) / CEIL["t1_memorised"])
TAB["t3_minus_t1|carrier_share"] = d13; TAB["t3_minus_t1|boundary_share"] = b13
lines.append(f"**Primary contrast (paired by item, identical source strings): carrier share t3 − t1 = {fmt(d13)}; boundary share t3 − t1 = {fmt(b13)}.**\n")
lines.append("## Interpretation\n\n(written by hand after reading the tables)")
json.dump(TAB, open(os.path.join(RES, "recompute_cost_ladder_tables.json"), "w"), indent=1, default=float)
open(os.path.join(RES, "recompute_cost_ladder.md"), "w").write("\n".join(lines)); print("\n".join(lines))
