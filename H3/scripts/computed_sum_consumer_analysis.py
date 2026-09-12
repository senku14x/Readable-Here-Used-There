"""Single scoring pass for computed_sum_consumer stages `transport` and `robust` (Amendment 2).

Rule throughout: answer = argmax over candidate words of logsumexp(log-probs of surface forms); flip = answer == donor value.
Cluster = sum (n=8), carriers averaged within sum; t-intervals df = n-1.  Usage: computed_sum_consumer_analysis.py robust
"""
import os, sys, json
import numpy as np
from scipy import stats as st

HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))
_MK = os.environ.get("TCSIF_MODEL", "")
ROOT = os.path.join(PROJ, "replication_" + _MK) if _MK else PROJ
OUT = os.path.join(ROOT, "H3", "outputs", "computed_sum_consumer"); RES = os.path.join(ROOT, "H3", "results"); os.makedirs(RES, exist_ok=True)
STAGE = sys.argv[1] if len(sys.argv) > 1 else "robust"
_S = "robust" if STAGE == "global" else STAGE
m = json.load(open(os.path.join(OUT, f"meta_{_S}.json"))); r = np.load(os.path.join(OUT, f"raw_{_S}.npz"))
COLS = m["columns"]; SW = m["sum_words"]; DEC = [COLS.index(d) for d in m["decoys"]]
WIN = {"L48-50": (48, 50), "L51-59": (51, 59)}


def ct(v):
    v = np.asarray(v, float); n = len(v); mu = v.mean()
    h = st.t.ppf(0.975, n - 1) * v.std(ddof=1) / np.sqrt(n) if n > 1 else float("nan")
    return {"mean": mu, "ci": [mu - h, mu + h], "n": n, "pos": int((v > 0).sum()), "per": v.tolist()}


def fmt(c): return f"{c['mean']:+.3f} [{c['ci'][0]:+.3f}, {c['ci'][1]:+.3f}] ({c['pos']}/{c['n']} >0)"


def zshift(tag, own, don, lo, hi):
    z = r[f"{tag}|z"][lo:hi + 1].astype(np.float32).mean(axis=(0, 1)); return float(z[COLS.index(don)] - z[COLS.index(own)])


def cluster(vals):   # dict cell->value  ->  per-sum means (carriers averaged)
    by = {}
    for cell, v in vals.items():
        by.setdefault(cell.split("|")[0], []).append(v)
    return [float(np.mean(v)) for k, v in sorted(by.items(), key=lambda kv: int(kv[0][1:]))]


if STAGE == "robust":
    CONDS = ["O_donor", "C_full", "C_all", "C_rand", "NEC"]
    MAPS = list(m["maps"]); CARR = m["carriers"]
    CONSUMERS = {"report": SW, "parity": ["even", "odd"]}
    lines = [f"# H3 · computed_sum_consumer — `robust` (Amendment 2 robustness battery) — run {m['run_id']}", "",
             f"Model forwards {m['n_forwards']} ({m['elapsed_s']} s). Carriers {CARR}; donor maps {m['maps']}; consumers parity + report; cluster = sum (n=8), carriers averaged within sum; scored-argmax rule.",
             f"RESID_P number axis fitted in-run (templates 1–4 fit, 5–6 validate); held-out pair margins at L36–59: " + ", ".join(f"{k} {v:+.2f}" for k, v in m['resid_axis']['heldout_pair_margin_L36_59'].items()), ""]
    TAB = {}
    gate_own = [m["cells"][c][f"{k}_C_own_bitwise"] for c in m["cells"] for k in CONSUMERS]
    lines.append(f"**Gates.** Carrier self-patch bitwise no-op: {sum(gate_own)}/{len(gate_own)}. Operand span asserted untouched under every carrier write (assert at generation).")
    dmg = [float(r[f"{c}|{k}|{mk}|{cond}|nll"] - r[f"{c}|{k}|clean|nll"]) for c in m["cells"] for k in CONSUMERS for mk in MAPS for cond in CONDS]
    lines.append(f"Carrier ΔNLL over all writes: mean {np.mean(dmg):+.4f}, max {np.max(dmg):+.4f}. Read-back error max: {max(float(r[k]) for k in r.files if k.endswith('|rberr')):.3g}.")
    lines.append("")
    for subset_name, subset in (("all carriers", CARR), ("C0/C1", ["C0", "C1"]), ("C2/C3", ["C2", "C3"])):
        for mk in MAPS:
            lines.append(f"## {subset_name} · map {mk} (donor sum = {m['cells']['S0|C0']['maps'][mk]['sum']} for seven, …)")
            for cname, words in CONSUMERS.items():
                lines.append(f"\n### consumer `{cname}`\n")
                lines.append("| condition | behavioral margin logP(donor)−logP(own), minus clean | flips (scored) | J_NP carrier sum shift L51–59 | RESID_P pair-axis shift L51–59 | LOGITS interior shift | answer-pos distance L51–59 / L36–50 |")
                lines.append("|---|---|---|---|---|---|---|")
                comp = 0; ncell = 0
                for cond in CONDS:
                    beh, fl, zj, rp, lg, dl, de = {}, 0, {}, {}, {}, {}, {}
                    for cell, info in m["cells"].items():
                        if cell.split("|")[1] not in subset: continue
                        own = info["sum"] if cname == "report" else info["own_parity"]
                        don = info["maps"][mk]["sum"] if cname == "report" else info["maps"][mk]["parity"]
                        oi, di = words.index(own), words.index(don)
                        s0 = r[f"{cell}|{cname}|clean|scores"]; s1 = r[f"{cell}|{cname}|{mk}|{cond}|scores"]
                        if cond == CONDS[0]: comp += int(s0.argmax() == oi); ncell += 1
                        beh[cell] = float((s1[di] - s1[oi]) - (s0[di] - s0[oi])); fl += int(s1.argmax() == di)
                        osum, dsum = info["sum"], info["maps"][mk]["sum"]
                        zj[cell] = zshift(f"{cell}|{cname}|{mk}|{cond}", osum, dsum, 51, 59) - zshift(f"{cell}|{cname}|clean", osum, dsum, 51, 59)
                        mi = MAPS.index(mk)
                        rp[cell] = float(r[f"{cell}|{cname}|{mk}|{cond}|p_pair"][51:60, mi].mean() - r[f"{cell}|{cname}|clean|p_pair"][51:60, mi].mean())
                        l0 = r[f"{cell}|{cname}|clean|lp_cols"]; l1 = r[f"{cell}|{cname}|{mk}|{cond}|lp_cols"]
                        lg[cell] = float((l1[COLS.index(dsum)] - l1[COLS.index(osum)]) - (l0[COLS.index(dsum)] - l0[COLS.index(osum)]))
                        d = r[f"{cell}|{cname}|{mk}|{cond}|ans_dist"]; dl[cell] = float(d[51:60].mean()); de[cell] = float(d[36:51].mean())
                    C = {k: ct(cluster(v)) for k, v in (("beh", beh), ("zj", zj), ("rp", rp), ("lg", lg))}
                    TAB[f"{subset_name}|{mk}|{cname}|{cond}"] = {**{k: C[k] for k in C}, "flips": fl, "n_cells": len(beh), "ans_dist_late": float(np.mean(list(dl.values()))), "ans_dist_mid": float(np.mean(list(de.values())))}
                    lines.append(f"| {cond} | {fmt(C['beh'])} | {fl}/{len(beh)} | {fmt(C['zj'])} | {fmt(C['rp'])} | {fmt(C['lg'])} | {np.mean(list(dl.values())):.1f} / {np.mean(list(de.values())):.1f} |")
                T = TAB
                k0 = f"{subset_name}|{mk}|{cname}|"
                rat = lambda a, b, q: T[k0 + a][q]["mean"] / T[k0 + b][q]["mean"] if T[k0 + b][q]["mean"] != 0 else float("nan")
                lines.append(f"\nClean competence {comp}/{ncell}. Ratios C_full/O_donor: behavioral {rat('C_full','O_donor','beh'):.3f}, J_NP {rat('C_full','O_donor','zj'):.2f}, RESID_P {rat('C_full','O_donor','rp'):.2f}, LOGITS {rat('C_full','O_donor','lg'):.2f}; "
                             f"C_all/O_donor behavioral {rat('C_all','O_donor','beh'):.3f}; answer-position distance C_full/O_donor (L51–59) {T[k0+'C_full']['ans_dist_late']/T[k0+'O_donor']['ans_dist_late']:.2f}, C_all/O_donor {T[k0+'C_all']['ans_dist_late']/T[k0+'O_donor']['ans_dist_late']:.2f}.")
            lines.append("")
    # answer-position distance profile by block (all carriers, off3, report)
    lines.append("## Answer-position distance from clean by block (all carriers, map off3, report consumer; mean over cells)\n")
    lines.append("| block | " + " | ".join(CONDS) + " | ‖h_clean‖ |"); lines.append("|---|" + "---|" * (len(CONDS) + 1))
    prof = {cond: np.mean([r[f"{c}|report|off3|{cond}|ans_dist"] for c in m["cells"]], 0) for cond in CONDS}
    hn = np.mean([r[f"{c}|report|clean|ans_norm"] for c in m["cells"]], 0)
    for b in [0, 8, 16, 24, 32, 35, 36, 39, 43, 47, 51, 55, 59, 63]:
        lines.append(f"| {b} | " + " | ".join(f"{prof[cond][b]:.1f}" for cond in CONDS) + f" | {hn[b]:.0f} |")
    lines.append("\n## Interpretation\n\n(written by hand after reading the tables; see the report section 11 in `computed_sum_consumer.md`)\n")
    json.dump(TAB, open(os.path.join(RES, f"computed_sum_consumer_{STAGE}_tables.json"), "w"), indent=1, default=float)
    open(os.path.join(RES, f"computed_sum_consumer_{STAGE}.md"), "w").write("\n".join(lines))
    print("\n".join(lines))



# ======================================================================================================================
# Stage `global` (Amendment 3) and the effect-size addendum for `robust` (odds ratios, P(own), entropy) — appended 2026-09-09
# ======================================================================================================================
def _lse(v): return float(np.logaddexp.reduce(v))


def robust_effects():
    m = json.load(open(os.path.join(OUT, "meta_robust.json"))); r = np.load(os.path.join(OUT, "raw_robust.npz"))
    SW = m["sum_words"]; out = ["## Effect sizes beyond flips (all carriers, map off3)", "",
                                "| consumer | condition | donor-vs-own odds ratio (geometric mean) | Δ log P(own) | Δ log P(donor) | Δ entropy over candidates (nats) |", "|---|---|---|---|---|---|"]
    for cname, words in (("report", SW), ("parity", ["even", "odd"])):
        for cond in ["O_donor", "C_full", "C_all", "C_rand", "NEC"]:
            lo, lp_own, lp_don, dH = {}, {}, {}, {}
            for cell, info in m["cells"].items():
                own = info["sum"] if cname == "report" else info["own_parity"]; don = info["maps"]["off3"]["sum"] if cname == "report" else info["maps"]["off3"]["parity"]
                oi, di = words.index(own), words.index(don)
                s0 = r[f"{cell}|{cname}|clean|scores"].astype(np.float64); s1 = r[f"{cell}|{cname}|off3|{cond}|scores"].astype(np.float64)
                p0, p1 = s0 - _lse(s0), s1 - _lse(s1)                       # renormalised over the candidate set
                lo[cell] = float((s1[di] - s1[oi]) - (s0[di] - s0[oi])); lp_own[cell] = float(p1[oi] - p0[oi]); lp_don[cell] = float(p1[di] - p0[di])
                H0 = -float((np.exp(p0) * p0).sum()); H1 = -float((np.exp(p1) * p1).sum()); dH[cell] = H1 - H0
            c = {k: ct(cluster(v)) for k, v in (("lo", lo), ("own", lp_own), ("don", lp_don), ("dH", dH))}
            out.append(f"| {cname} | {cond} | ×{np.exp(c['lo']['mean']):.1f} [{np.exp(c['lo']['ci'][0]):.1f}, {np.exp(c['lo']['ci'][1]):.1f}] | {fmt(c['own'])} | {fmt(c['don'])} | {fmt(c['dH'])} |")
    out += ["", "Odds ratio = exp(mean margin shift over sums); log P renormalised over the candidate words (8 sum words or even/odd)."]
    return "\n".join(out)


def global_stage():
    global m, r
    m = json.load(open(os.path.join(OUT, "meta_global.json"))); r = np.load(os.path.join(OUT, "raw_global.npz"))
    SW = m["sum_words"]; COLS_ = m["columns"]; FA = m["full_attention_layers"]
    CONDS = ["O_donor36", "O_donor0", "C_full", "G_full", "G_swap_all", "G_swap_carrier", "D_band", "D_band_early", "mask_clean", "mask_C_full", "mask_O_donor36"]
    lines = [f"# H3 · computed_sum_consumer — `global` (Amendment 3) — run {m['run_id']}", "",
             f"{m['n_forwards']} forwards ({m['elapsed_s']} s); 8 sums × {m['carriers']} × parity + report; donor map offset {m['map']}; cluster = sum (n=8); scored-argmax rule. Swap layers {m['swap_layers'][0]}–{m['swap_layers'][-1]}; masked full-attention blocks {FA}.", ""]
    TAB = {}
    dmg = [float(r[f"{c}|{k}|{cond}|nll"] - r[f"{c}|{k}|clean|nll"]) for c in m["cells"] for k in ("report", "parity") for cond in CONDS]
    leak = max(float(np.nanmax(r[f"{c}|{k}|{cond}|leak"])) for c in m["cells"] for k in ("report", "parity") for cond in CONDS if cond.startswith("mask"))
    swapn = np.mean([np.nanmean(r[f"{c}|report|G_swap_all|swapnorm"]) for c in m["cells"]])
    lines.append(f"**Gates.** Carrier ΔNLL max {max(dmg):+.4f}; attention leak under the mask max {leak:.2e}; mean realized swap norm per position {swapn:.2f}; operand span untouched under carrier-only writes and prefix untouched under decision-position writes (asserted at generation).\n")
    for cname, words in (("report", SW), ("parity", ["even", "odd"])):
        lines.append(f"## consumer `{cname}`\n")
        lines.append("| condition | behavioral margin (nats) | odds ratio | flips (scored) | greedy = own value (word or digit) | J_NP carrier sum shift L51–59 | RESID_P pair-axis shift | answer-pos distance L51–59 |")
        lines.append("|---|---|---|---|---|---|---|---|")
        for cond in CONDS:
            beh, zj, rp, dl = {}, {}, {}, {}; fl = 0; ok = 0; ncell = 0
            for cell, info in m["cells"].items():
                own = info["sum"] if cname == "report" else info["own_parity"]; don = info["diff_sum"] if cname == "report" else info["diff_parity"]
                oi, di = words.index(own), words.index(don)
                s0 = r[f"{cell}|{cname}|clean|scores"]; s1 = r[f"{cell}|{cname}|{cond}|scores"]
                beh[cell] = float((s1[di] - s1[oi]) - (s0[di] - s0[oi])); fl += int(s1.argmax() == di); ncell += 1
                g = str(r[f"{cell}|{cname}|{cond}|greedy"]).strip().lower()
                ok += int(g == own or (cname == "report" and g == str(SW.index(own) + 7)))
                osum, dsum = info["sum"], info["diff_sum"]
                zj[cell] = zshift(f"{cell}|{cname}|{cond}", osum, dsum, 51, 59) - zshift(f"{cell}|{cname}|clean", osum, dsum, 51, 59)
                rp[cell] = float(r[f"{cell}|{cname}|{cond}|p_pair"][51:60].mean() - r[f"{cell}|{cname}|clean|p_pair"][51:60].mean())
                dl[cell] = float(r[f"{cell}|{cname}|{cond}|ans_dist"][51:60].mean())
            C = {k: ct(cluster(v)) for k, v in (("beh", beh), ("zj", zj), ("rp", rp))}
            TAB[f"{cname}|{cond}"] = {**C, "flips": fl, "n": ncell, "greedy_own": ok, "ans_dist_late": float(np.mean(list(dl.values())))}
            lines.append(f"| {cond} | {fmt(C['beh'])} | ×{np.exp(C['beh']['mean']):.1f} | {fl}/{ncell} | {ok}/{ncell} | {fmt(C['zj'])} | {fmt(C['rp'])} | {np.mean(list(dl.values())):.1f} |")
        lines.append("")
        # clean competence under the mask (gate for the mask rows)
        okc = sum(int(str(r[f'{c}|{cname}|mask_clean|greedy']).strip().lower() in (m['cells'][c]['sum'] if cname == 'report' else m['cells'][c]['own_parity'], str(SW.index(m['cells'][c]['sum']) + 7))) for c in m["cells"])
        oks = sum(int(r[f'{c}|{cname}|mask_clean|scores'].argmax() == words.index(m['cells'][c]['sum'] if cname == 'report' else m['cells'][c]['own_parity'])) for c in m["cells"])
        lines.append(f"Mask competence gate (`mask_clean`): greedy = own value {okc}/{len(m['cells'])}; scored-argmax = own {oks}/{len(m['cells'])} (gate ≥ 0.9 → {'PASS' if oks/len(m['cells']) >= 0.9 else 'FAIL — mask rows are uninterpretable as use tests and are reported as observations'}).\n")
    lines += ["## Interpretation", "", "(written by hand; see `computed_sum_consumer.md` §13)"]
    json.dump(TAB, open(os.path.join(RES, "computed_sum_consumer_global_tables.json"), "w"), indent=1, default=float)
    open(os.path.join(RES, "computed_sum_consumer_global.md"), "w").write("\n".join(lines)); print("\n".join(lines))


if STAGE == "global":
    global_stage()
elif STAGE == "robust":
    txt = robust_effects(); print(txt)
    p = os.path.join(RES, "computed_sum_consumer_robust.md"); s = open(p).read()
    if "## Effect sizes beyond flips" not in s:
        s = s.replace("## Interpretation", txt + "\n\n## Interpretation"); open(p, "w").write(s)
