"""Analysis for H1 source transfer (single scoring pass; reads H1/outputs/source_transfer/raw.npz).

C_k(L_x, arm) = m(swap L_x) − m(noswap), m = E[z_Y − z_X] over window × interior positions, on J_NP (bf16 path),
the plain-sentence pair axis p_{Y−X} (RESID_P), and the output log-prob margin (LOGITS). Both directions and
carriers averaged within the unordered pair; cluster = pair. Natural X/Y contrast A_k = m(donor clean) − m(clean)
on each instrument for the calibrated comparison (§4.6). Also the arm difference D = C(maintain) − C(mention).
Writes H1/results/source_transfer.md, source_transfer_tables.json, figures/source_transfer_*.png.
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

OUT = os.path.join(R.out_dir("H1", "outputs"), "source_transfer")
RES = os.path.join(R.out_dir("H1", "results")); FIG = os.path.join(RES, "figures")
os.makedirs(FIG, exist_ok=True)
META = json.load(open(os.path.join(OUT, "meta.json"))); Z = np.load(os.path.join(OUT, "raw.npz"))
COLS = META["columns"]; CIX = {w: i for i, w in enumerate(COLS)}
PAIRS = [tuple(p) for p in META["pairs"]]; ARMS = META["arms"]; CARRIERS = META["carriers"]; LX = META["lx_sweep"]
WINDOWS = {"L48-50": [48, 49, 50], "L51-59": list(range(51, 60)), "L24-59": list(range(24, 60))}
L = np.array(META["layers"])


def m_J(tag, X, Y, layers):
    z = Z[f"{tag}|z"].astype(np.float32)[layers]
    return float((z[:, :, CIX[Y]] - z[:, :, CIX[X]]).mean())


def m_p(tag, layers):
    return float(Z[f"{tag}|p_pair"][layers].mean())


def m_lp(tag):
    return float(Z[f"{tag}|lp_margin"].mean())


def m_J_layers(tag, X, Y):
    z = Z[f"{tag}|z"].astype(np.float32)
    return (z[:, :, CIX[Y]] - z[:, :, CIX[X]]).mean(1)


def per_pair(fn):
    """fn(ck, arm, X, Y) -> value; average both directions × carriers -> one value per unordered pair."""
    return np.array([np.mean([fn(ck, X, Y) for ck in CARRIERS for (X, Y) in ((a, b), (b, a))]) for (a, b) in PAIRS])


tables = {}
for wname, win in WINDOWS.items():
    for inst, mf in (("J_NP", lambda t, X, Y, w=win: m_J(t, X, Y, w)), ("RESID_P", lambda t, X, Y, w=win: m_p(t, w)), ("LOGITS", lambda t, X, Y: m_lp(t))):
        if inst == "LOGITS" and wname != "L48-50":
            continue
        key = f"{inst}|{wname}" if inst != "LOGITS" else "LOGITS"
        for arm in ARMS:
            A = per_pair(lambda ck, X, Y, a=arm: mf(f"{ck}|{a}|{X}->{Y}|donor_clean", X, Y) - mf(f"{ck}|{a}|{X}->{Y}|clean", X, Y))
            tables[f"A_natural|{key}|{arm}"] = S.cluster_t(A)
            for lx in LX:
                C = per_pair(lambda ck, X, Y, a=arm, l=lx: mf(f"{ck}|{a}|{X}->{Y}|swap{l}", X, Y) - mf(f"{ck}|{a}|{X}->{Y}|clean", X, Y))
                tables[f"C|{key}|{arm}|Lx{lx}"] = S.cluster_t(C)
                tables[f"C_over_A|{key}|{arm}|Lx{lx}"] = S.ratio_of_means(C, A)
        for lx in LX:
            D = per_pair(lambda ck, X, Y, l=lx: (mf(f"{ck}|maintain|{X}->{Y}|swap{l}", X, Y) - mf(f"{ck}|maintain|{X}->{Y}|clean", X, Y))
                         - (mf(f"{ck}|mention|{X}->{Y}|swap{l}", X, Y) - mf(f"{ck}|mention|{X}->{Y}|clean", X, Y)))
            tables[f"D_maintain_minus_mention|{key}|Lx{lx}"] = S.cluster_t(D)
# rank-1 surfacing of the donor after the swap (prominence, L24-59)
prom = {}
for arm in ARMS:
    for lx in ["clean"] + LX:
        hits = []
        for ck in CARRIERS:
            for (a, b) in PAIRS:
                for (X, Y) in ((a, b), (b, a)):
                    t = f"{ck}|{arm}|{X}->{Y}|" + ("clean" if lx == "clean" else f"swap{lx}")
                    rk = Z[f"{t}|rank"][24:60]
                    hits.append({"Y_r_min": int(rk[:, :, 1].min()), "X_r_min": int(rk[:, :, 0].min())})
        prom[f"{arm}|{lx}"] = {"Y_rank1_rate": float(np.mean([h["Y_r_min"] == 1 for h in hits])), "Y_r_min_median": float(np.median([h["Y_r_min"] for h in hits])),
                               "X_rank1_rate": float(np.mean([h["X_r_min"] == 1 for h in hits])), "X_r_min_median": float(np.median([h["X_r_min"] for h in hits]))}
tables["prominence"] = prom
# damage
dmg = {}
for arm in ARMS:
    for lx in LX:
        d = []
        for ck in CARRIERS:
            for (a, b) in PAIRS:
                for (X, Y) in ((a, b), (b, a)):
                    t0 = f"{ck}|{arm}|{X}->{Y}|clean"; t1 = f"{ck}|{arm}|{X}->{Y}|swap{lx}"
                    d.append({"dnll": float(Z[f"{t1}|nll"] - Z[f"{t0}|nll"]), "top1": float((Z[f"{t1}|top1"] == Z[f"{t0}|top1"]).mean())})
        dmg[f"{arm}|Lx{lx}"] = {"dNLL_mean": float(np.mean([x["dnll"] for x in d])), "dNLL_max": float(np.max([x["dnll"] for x in d])), "top1_retention_mean": float(np.mean([x["top1"] for x in d])), "top1_retention_min": float(np.min([x["top1"] for x in d]))}
tables["damage"] = dmg
json.dump(tables, open(os.path.join(RES, "source_transfer_tables.json"), "w"), indent=1, default=float)

# figures: C by L_x per instrument and arm; layer profile of the margin for L_x=36 and 23
fig, axes = plt.subplots(1, 3, figsize=(15, 4))
for ax, (inst, key) in zip(axes, [("J_NP L48-50", "J_NP|L48-50"), ("J_NP L51-59", "J_NP|L51-59"), ("RESID_P L48-50", "RESID_P|L48-50")]):
    for arm in ARMS:
        means = [tables[f"C|{key}|{arm}|Lx{lx}"]["mean"] for lx in LX]
        lo = [tables[f"C|{key}|{arm}|Lx{lx}"]["ci"][0] for lx in LX]; hi = [tables[f"C|{key}|{arm}|Lx{lx}"]["ci"][1] for lx in LX]
        ax.errorbar(LX, means, yerr=[np.array(means) - lo, np.array(hi) - means], marker="o", capsize=3, label=f"{arm} (A_nat={tables[f'A_natural|{key}|{arm}']['mean']:+.2f})")
    ax.axhline(0, color="k", lw=0.5); ax.set_xlabel("source replacement start layer L_x"); ax.set_ylabel("C = m(swap) - m(clean)"); ax.set_title(inst); ax.legend(fontsize=7)
plt.tight_layout(); plt.savefig(os.path.join(FIG, "source_transfer_C_by_Lx.png"), dpi=130); plt.close()
fig, axes = plt.subplots(1, 2, figsize=(12, 4))
for ax, arm in zip(axes, ARMS):
    for lx in (23, 36, 44):
        curves = [m_J_layers(f"{ck}|{arm}|{X}->{Y}|swap{lx}", X, Y) - m_J_layers(f"{ck}|{arm}|{X}->{Y}|clean", X, Y) for ck in CARRIERS for (a, b) in PAIRS for (X, Y) in ((a, b), (b, a))]
        ax.plot(L, np.mean(curves, 0), label=f"L_x={lx}")
    curves = [m_J_layers(f"{ck}|{arm}|{X}->{Y}|donor_clean", X, Y) - m_J_layers(f"{ck}|{arm}|{X}->{Y}|clean", X, Y) for ck in CARRIERS for (a, b) in PAIRS for (X, Y) in ((a, b), (b, a))]
    ax.plot(L, np.mean(curves, 0), "k--", label="natural Y - X (donor clean)")
    ax.axhline(0, color="k", lw=0.5); ax.set_title(f"{arm}: J_NP margin shift by layer"); ax.set_xlabel("layer"); ax.legend(fontsize=7)
plt.tight_layout(); plt.savefig(os.path.join(FIG, "source_transfer_layer_profile.png"), dpi=130); plt.close()


def ci_str(e):
    return f"{e['mean']:+.3f} [{e['ci'][0]:+.3f}, {e['ci'][1]:+.3f}] ({e.get('signs_pos', 0)}/{e['n']} >0)"


rep = [f"# H1 · source transfer — results (run {META['run_id']})\n", "## 1. Question and setup\n",
       f"Does sustained replacement of the introduced word's span (block outputs at layers ≥ L_x) with an arm-matched donor Y move the later readout toward Y, and from which L_x? Controlled organism, geometry-matched calibration pairs {PAIRS} (pair table in `outputs/source_transfer/meta.json`), both directions, arms {ARMS}, carriers {CARRIERS}; L_x ∈ {LX}. Cluster = unordered pair (n={len(PAIRS)}, pilot scale). Instruments: J_NP pair margin m = E[z_Y − z_X]; RESID_P pair axis p_{{Y−X}} from plain sentences; LOGITS output log-prob margin. A_natural = m(clean Y run) − m(clean X run) is the positive control / calibration denominator. {META['n_forwards']} forwards; same-source at L_x=36 bitwise equal to clean and layers < L_x identical between futures asserted on every cell.\n",
       "## 2. Main findings\n"]
for key in ("J_NP|L48-50", "J_NP|L51-59", "RESID_P|L48-50", "RESID_P|L51-59", "LOGITS"):
    for arm in ARMS:
        rep.append(f"- **{key}, {arm}:** A_nat {ci_str(tables[f'A_natural|{key}|{arm}'])}; C at L_x=23 {ci_str(tables[f'C|{key}|{arm}|Lx23'])}; L_x=36 {ci_str(tables[f'C|{key}|{arm}|Lx36'])} (C/A {tables[f'C_over_A|{key}|{arm}|Lx36']['ratio']:.2f} [{tables[f'C_over_A|{key}|{arm}|Lx36']['ci'][0]:.2f}, {tables[f'C_over_A|{key}|{arm}|Lx36']['ci'][1]:.2f}]); L_x=44 {ci_str(tables[f'C|{key}|{arm}|Lx44'])}.")
    rep.append(f"- **{key}, maintain − mention at L_x=36:** {ci_str(tables[f'D_maintain_minus_mention|{key}|Lx36'])}; at L_x=23 {ci_str(tables[f'D_maintain_minus_mention|{key}|Lx23'])}.")
rep.append("\n## 3. Complete numerical evidence\n")
for key in ("J_NP|L48-50", "J_NP|L51-59", "J_NP|L24-59", "RESID_P|L48-50", "RESID_P|L51-59", "RESID_P|L24-59", "LOGITS"):
    rep.append(f"### {key}\n\n| arm | quantity | mean | 95% t-CI | signs >0 / n | per-pair |\n|---|---|---|---|---|---|")
    for arm in ARMS:
        e = tables[f"A_natural|{key}|{arm}"]
        rep.append(f"| {arm} | A_natural (donor clean − clean) | {e['mean']:+.4f} | [{e['ci'][0]:+.4f}, {e['ci'][1]:+.4f}] | {e['signs_pos']}/{e['n']} | {', '.join(f'{x:+.3f}' for x in e['per_cluster'])} |")
        for lx in LX:
            e = tables[f"C|{key}|{arm}|Lx{lx}"]; r = tables[f"C_over_A|{key}|{arm}|Lx{lx}"]
            rep.append(f"| {arm} | C at L_x={lx} (C/A {r['ratio']:.2f} [{r['ci'][0]:.2f}, {r['ci'][1]:.2f}]) | {e['mean']:+.4f} | [{e['ci'][0]:+.4f}, {e['ci'][1]:+.4f}] | {e['signs_pos']}/{e['n']} | {', '.join(f'{x:+.3f}' for x in e['per_cluster'])} |")
    for lx in LX:
        e = tables[f"D_maintain_minus_mention|{key}|Lx{lx}"]
        rep.append(f"| both | D = C(maintain) − C(mention) at L_x={lx} | {e['mean']:+.4f} | [{e['ci'][0]:+.4f}, {e['ci'][1]:+.4f}] | {e['signs_pos']}/{e['n']} | {', '.join(f'{x:+.3f}' for x in e['per_cluster'])} |")
    rep.append("")
rep.append("### Prominence (L24–59): donor Y and source X rank statistics after the swap\n\n| arm | condition | Y rank-1 rate | Y median r_min | X rank-1 rate | X median r_min |\n|---|---|---|---|---|---|")
for k, e in prom.items():
    arm, lx = k.split("|")
    rep.append(f"| {arm} | {lx} | {e['Y_rank1_rate']:.2f} | {e['Y_r_min_median']:.0f} | {e['X_rank1_rate']:.2f} | {e['X_r_min_median']:.0f} |")
rep.append("\n### Damage\n\n| arm | L_x | ΔNLL mean | ΔNLL max | top-1 retention mean | min |\n|---|---|---|---|---|---|")
for k, e in dmg.items():
    arm, lx = k.split("|")
    rep.append(f"| {arm} | {lx} | {e['dNLL_mean']:+.4f} | {e['dNLL_max']:+.4f} | {e['top1_retention_mean']:.3f} | {e['top1_retention_min']:.3f} |")
rep.append("\nFigures: `figures/source_transfer_C_by_Lx.png`, `figures/source_transfer_layer_profile.png`. Machine-readable: `source_transfer_tables.json`.\n")
rep.append("## 4. Verification and limitations\n\n- Same-source replacement at L_x=36 reproduced the clean run bitwise on every cell; layers < L_x identical between future-X and future-Y on every cell (asserted in the battery).\n- n = 3 geometry-matched pairs at pilot scale (orange–guitar was excluded by the geometry rule: `guitar` is two pieces in the quoted context). Intervals are wide by construction; this run calibrates L_x, it does not establish transfer.\n- RESID_P is the plain-sentence pair axis fitted on templates 1–8; its scale differs from the lens and is never compared in raw units.\n")
rep.append("## 5. Interpretation and next decision\n\n_Filled in by hand after reading the tables (see the end of this file)._\n")
open(os.path.join(RES, "source_transfer.md"), "w").write("\n".join(rep))
print("\n".join(rep[:16]))
