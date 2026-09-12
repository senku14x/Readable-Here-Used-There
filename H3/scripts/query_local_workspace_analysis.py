"""Scoring pass for query_local_workspace stages (queryread, querycausal, nosource). Cluster = sum (n=8), carriers averaged
within sum; scored-argmax rule; parity is the primary consumer for coordinate-level rows."""
import os, sys, json
import numpy as np
from scipy import stats as st

HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))
_MK = os.environ.get("TCSIF_MODEL", "")
ROOT = os.path.join(PROJ, "replication_" + _MK) if _MK else PROJ
OUT = os.path.join(ROOT, "H3", "outputs", "query_local_workspace"); RES = os.path.join(ROOT, "H3", "results"); os.makedirs(RES, exist_ok=True)


def ct(v):
    v = np.asarray(v, float); n = len(v); mu = v.mean(); h = st.t.ppf(0.975, n - 1) * v.std(ddof=1) / np.sqrt(n) if n > 1 else float("nan")
    return {"mean": mu, "ci": [mu - h, mu + h], "n": n, "pos": int((v > 0).sum())}


def fmt(c): return f"{c['mean']:+.3f} [{c['ci'][0]:+.3f}, {c['ci'][1]:+.3f}] ({c['pos']}/{c['n']})"
def cluster(d):
    by = {}
    for cell, v in d.items():
        by.setdefault(cell.split("|")[0], []).append(v)
    return [float(np.mean(v)) for k, v in sorted(by.items(), key=lambda kv: int(kv[0][1:]))]


def stage_tables(stage, conds, baseline, lines, TAB):
    m = json.load(open(os.path.join(OUT, f"meta_{stage}.json"))); r = np.load(os.path.join(OUT, f"raw_{stage}.npz"))
    COLS = m["columns"]; SW = m["sum_words"]
    lines += [f"# H3 · query_local_workspace — `{stage}` — run {m['run_id']}", "",
              f"{m['n_forwards']} forwards ({m['elapsed_s']} s); 8 sums × {m['carriers']} × parity + report; donor map offset {m['map']}; Q band blocks {m['q_layers'][0]}–{m['q_layers'][1]}; cluster = sum (n=8). Parity is the primary consumer for coordinate-level rows (Q_swap, NEC_Qclamp); report is steering-susceptible there.", ""]
    dmg = [float(r[f"{c}|{k}|{cond}|nll"] - r[f"{c}|{k}|{baseline}|nll"]) for c in m["cells"] for k in ("report", "parity") for cond in conds]
    lines.append(f"**Gates.** Carrier ΔNLL max {max(dmg):+.4f}." + (f" Q_own bitwise: {sum(m['cells'][c].get(k + '_Qown_bitwise', False) for c in m['cells'] for k in ('report','parity'))}/64." if stage == "querycausal" else "")
                 + (f" Clamp read-back error max {max(float(r[k]) for k in r.files if k.endswith('|clamperr')):.2e}; clamp write norm (NEC_Qclamp / perp): {np.mean([np.nanmean(r[k]) for k in r.files if k.endswith('NEC_Qclamp|clampnorm')]):.2f} / {np.mean([np.nanmean(r[k]) for k in r.files if k.endswith('NEC_Qclamp_perp|clampnorm')]):.2f}." if stage == "querycausal" else "") + "\n")
    for cname, words in (("parity", ["even", "odd"]), ("report", SW)):
        lines.append(f"## consumer `{cname}`" + (" (primary)" if cname == "parity" else " (steering-susceptible for coordinate rows)") + "\n")
        lines.append("| condition | behavioral margin (nats) | flips → donor value | flips → own value | J_NP sum shift at Q, L51–59 | RESID_P pair-axis shift at Q | LOGITS shift at Q | J_NP sum shift at carrier | answer-pos dist L51–59 |")
        lines.append("|---|---|---|---|---|---|---|---|---|")
        for cond in conds:
            beh, zq, rq, lq, zc, dl = {}, {}, {}, {}, {}, {}; fl = 0; own_fl = 0
            for cell, info in m["cells"].items():
                own = info["sum"] if cname == "report" else info["own_parity"]; don = info["donor_sum"] if cname == "report" else info["donor_parity"]
                oi, di = words.index(own), words.index(don)
                s0 = r[f"{cell}|{cname}|{baseline}|scores"]; s1 = r[f"{cell}|{cname}|{cond}|scores"]
                beh[cell] = float((s1[di] - s1[oi]) - (s0[di] - s0[oi])); fl += int(s1.argmax() == di); own_fl += int(s1.argmax() == oi)
                osum, dsum = info["sum"], info["donor_sum"]; oc, dc = COLS.index(osum), COLS.index(dsum)
                def zs(tag, site):
                    z = r[f"{tag}|z_{site}"][51:60].astype(np.float32).mean(axis=(0, 1)); return float(z[dc] - z[oc])
                zq[cell] = zs(f"{cell}|{cname}|{cond}", "q") - zs(f"{cell}|{cname}|{baseline}", "q")
                zc[cell] = zs(f"{cell}|{cname}|{cond}", "carr") - zs(f"{cell}|{cname}|{baseline}", "carr")
                rq[cell] = float(r[f"{cell}|{cname}|{cond}|ppair_q"][51:60].mean() - r[f"{cell}|{cname}|{baseline}|ppair_q"][51:60].mean())
                l0 = r[f"{cell}|{cname}|{baseline}|lp_q"]; l1 = r[f"{cell}|{cname}|{cond}|lp_q"]
                lq[cell] = float((l1[dc] - l1[oc]) - (l0[dc] - l0[oc]))
                dl[cell] = float(r[f"{cell}|{cname}|{cond}|ans_dist"][51:60].mean())
            C = {k: ct(cluster(v)) for k, v in (("beh", beh), ("zq", zq), ("rq", rq), ("lq", lq), ("zc", zc))}
            TAB[f"{stage}|{cname}|{cond}"] = {**C, "flips_donor": fl, "flips_own": own_fl, "n": len(beh), "ans_dist": float(np.mean(list(dl.values())))}
            lines.append(f"| {cond} | {fmt(C['beh'])} | {fl}/{len(beh)} | {own_fl}/{len(beh)} | {fmt(C['zq'])} | {fmt(C['rq'])} | {fmt(C['lq'])} | {fmt(C['zc'])} | {np.mean(list(dl.values())):.1f} |")
        lines.append("")
    # clean presence of the own sum at Q vs carrier (is the sum readable at the question at all?)
    if stage == "queryread":
        lines.append("## Own-sum presence (z_own − mean decoys, L51–59) under clean, at the carrier vs the question positions\n")
        DEC = [COLS.index(d) for d in m["decoys"]]
        for cname in ("parity", "report"):
            pc, pq = {}, {}
            for cell, info in m["cells"].items():
                oc = COLS.index(info["sum"])
                for site, dst in (("carr", pc), ("q", pq)):
                    z = r[f"{cell}|{cname}|clean|z_{site}"][51:60].astype(np.float32).mean(axis=(0, 1)); dst[cell] = float(z[oc] - z[DEC].mean())
            lines.append(f"- {cname}: carrier {fmt(ct(cluster(pc)))}; question positions {fmt(ct(cluster(pq)))}")
        lines.append("")
    return m


lines, TAB = [], {}
stages = sys.argv[1:] or ["queryread", "querycausal", "clampsplit", "nosource", "nosource2"]
for stg in stages:
    if stg == "queryread":
        stage_tables("queryread", ["O_donor", "C_full", "NEC"], "clean", lines, TAB)
    elif stg == "querycausal":
        stage_tables("querycausal", ["NEC", "Q_own", "Q_donor_50", "Q_donor_62", "Q_rand", "Q_swap", "NEC_Qclamp", "NEC_Qclamp_perp"], "clean", lines, TAB)
    elif stg == "clampsplit":
        stage_tables("clampsplit", ["NEC", "NEC_Qclamp_noans", "NEC_Qclamp_ansonly"], "clean", lines, TAB)
    elif stg in ("nosource", "nosource2"):
        m = stage_tables(stg, ["C_from_S", "C_from_S2", "C_rand_ns", "Q_from_S"], "clean_ns", lines, TAB)
        # the nosource endpoint proper: does the answer become S (own) or S2 (donor)?  score(S) - max(others), relative to clean_ns
        r = np.load(os.path.join(OUT, f"raw_{stg}.npz")); SW = m["sum_words"]
        lines.append("## Absent-source endpoint: log P(S) − log P(S2) at the answer, and argmax identity\n")
        lines.append("| consumer | condition | Δ[logP(S) − logP(S2)] vs clean_ns | argmax = S | argmax = S2 |"); lines.append("|---|---|---|---|---|")
        for cname, words in (("parity", ["even", "odd"]), ("report", SW)):
            for cond in ["clean_ns", "C_from_S", "C_from_S2", "C_rand_ns", "Q_from_S"]:
                d, aS, aS2 = {}, 0, 0
                for cell, info in m["cells"].items():
                    S = info["sum"] if cname == "report" else info["own_parity"]; S2 = info["donor_sum"] if cname == "report" else info["donor_parity"]
                    si, s2i = words.index(S), words.index(S2)
                    s0 = r[f"{cell}|{cname}|clean_ns|scores"]; s1 = r[f"{cell}|{cname}|{cond}|scores"]
                    d[cell] = float((s1[si] - s1[s2i]) - (s0[si] - s0[s2i])); aS += int(s1.argmax() == si); aS2 += int(s1.argmax() == s2i)
                lines.append(f"| {cname} | {cond} | {fmt(ct(cluster(d)))} | {aS}/{len(d)} | {aS2}/{len(d)} |")
        from collections import Counter
        for cond in ["clean_ns", "C_from_S", "C_from_S2", "Q_from_S"]:
            g = Counter(str(r[f"{c}|report|{cond}|greedy"]).strip().lower() for c in m["cells"])
            gS = sum(int(str(r[f"{c}|report|{cond}|greedy"]).strip().lower() == m["cells"][c]["sum"]) for c in m["cells"])
            lines.append(f"- report greedy under `{cond}`: greedy = S in {gS}/32; most common tokens {g.most_common(4)}")
        lines.append("")
lines += ["## Interpretation", "", "(written by hand after reading the tables)"]
json.dump(TAB, open(os.path.join(RES, "query_local_workspace_tables.json"), "w"), indent=1, default=float)
open(os.path.join(RES, "query_local_workspace.md"), "w").write("\n".join(lines)); print("\n".join(lines))
