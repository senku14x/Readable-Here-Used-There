"""Analysis for H1 computed_sums. Dispatches on stage: natural (readability gate), transfer (the contrast).

Endpoints (J_NP + LOGITS): sum-word presence s(sum) = z_sum - mean(z over the other 7 sums); addend presence
s(add) = z_add - mean(z_decoys). transfer: C_diff^sum = m_sum(diffswap)-m_sum(clean) with m_sum = s(diff_sum)-s(own_sum);
C_same^sum = own-sum presence change under the same-sum sibling swap (equivalence-tested against ~0); C_diff^add, C_same^add
on the addend endpoint. Cluster = sum (n=8; A/B addend-versions and carriers averaged within sum).

Note: the RESID sum axis (design) was not fit; J_NP + LOGITS carry the same-sum/diff-sum contrast. Disclosed limitation.

Usage: computed_sums_analysis.py natural|transfer
"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "common", "scripts"))
import numpy as np
import registry as R
import stats as S

STAGE = sys.argv[1] if len(sys.argv) > 1 else "transfer"
OUT = os.path.join(R.out_dir("H1", "outputs"), "computed_sums"); RES = os.path.join(R.out_dir("H1", "results"))
META = json.load(open(os.path.join(OUT, f"meta_{STAGE}.json"))); Z = np.load(os.path.join(OUT, f"raw_{STAGE}.npz"))
COLS = META["columns"]; CIX = {w: i for i, w in enumerate(COLS)}; SUM_WORDS = META["sum_words"]; DEC = [CIX[d] for d in META["decoys"]]
CARRIERS = META["carriers"]; CELLS = META["cells"]
WINDOWS = {"L48-50": [48, 49, 50], "L51-59": list(range(51, 60))}


def s_sum(sub, sw, win, inst):
    others = [CIX[w] for w in SUM_WORDS if w != sw]
    if inst == "LOGITS":
        lp = Z[f"{sub}|lp"]; return float(lp[:, CIX[sw]].mean() - lp[:, others].mean())
    z = Z[f"{sub}|z"].astype(np.float32)[win]; return float((z[:, :, CIX[sw]] - z[:, :, others].mean(-1)).mean())


def s_add(sub, add, win, inst):
    if inst == "LOGITS":
        lp = Z[f"{sub}|lp"]; return float(lp[:, CIX[add]].mean() - lp[:, DEC].mean())
    z = Z[f"{sub}|z"].astype(np.float32)[win]; return float((z[:, :, CIX[add]] - z[:, :, DEC].mean(-1)).mean())


def cs(e):
    return "n/a" if e is None else f"{e['mean']:+.3f} [{e['ci'][0]:+.3f}, {e['ci'][1]:+.3f}] ({e.get('signs_pos', 0)}/{e['n']} >0)"


# rows/cells are keyed "{i}{x}|{ck}|..."; cluster by sum index i (n=8)
def sum_idx(cellkey):
    return int(cellkey.split("|")[0][:-1])


if STAGE == "natural":
    tables = {}
    for inst in ("J_NP", "LOGITS"):
        for wname, win in ([("out", None)] if inst == "LOGITS" else list(WINDOWS.items())):
            key = inst + ("" if inst == "LOGITS" else f"|{wname}")
            rows = {"maintain": [[] for _ in range(8)], "control": [[] for _ in range(8)], "absent": [[] for _ in range(8)]}
            adds = {"maintain": [[] for _ in range(8)], "absent": [[] for _ in range(8)]}
            for tag, c in CELLS.items():
                i = sum_idx(tag); cond = c["cond"]
                rows[cond][i].append(s_sum(tag, c["sum"], win, inst))
                if cond in adds:
                    adds[cond][i].append(np.mean([s_add(tag, a, win, inst) for a in c["pair"]]))
            m = {k: [np.mean(v) for v in rows[k]] for k in rows}
            T = {k: S.cluster_t(m[k]) for k in rows}
            T["maint_minus_absent"] = S.cluster_t([a - b for a, b in zip(m["maintain"], m["absent"])])
            am = {k: [np.mean(v) for v in adds[k]] for k in adds}
            T["addend_maint_minus_absent"] = S.cluster_t([a - b for a, b in zip(am["maintain"], am["absent"])])
            g = T["maint_minus_absent"]; T["GATE_PASS"] = bool(g["ci"][0] > 0 and g.get("signs_pos", 0) >= 6)
            tables[key] = T
    json.dump(tables, open(os.path.join(RES, "computed_sums_natural_tables.json"), "w"), indent=1, default=float)
    rep = [f"# H1 · computed_sums — natural (sum-word readability gate) — run {META['run_id']}\n", "## Findings\n"]
    for key in ("J_NP|L48-50", "J_NP|L51-59", "LOGITS"):
        T = tables[key]
        rep.append(f"- **{key}:** sum presence maintain {cs(T['maintain'])}, control {cs(T['control'])}, absent {cs(T['absent'])}; "
                   f"**maintain-absent {cs(T['maint_minus_absent'])}** gate {'PASS' if T['GATE_PASS'] else 'FAIL'}; addend maintain-absent {cs(T['addend_maint_minus_absent'])}.")
    passes = [k for k in ("J_NP|L48-50", "J_NP|L51-59") if tables[k]["GATE_PASS"]]
    rep.append(f"\n**Gate:** sum-word instrument {'validated' if passes else 'NOT validated'} ({', '.join(passes) or 'fails'}). "
               f"If not validated, the transfer sum endpoint is 'instrument not validated' but the transfer stage still runs.\n")
    open(os.path.join(RES, "computed_sums_natural.md"), "w").write("\n".join(rep))
    print("\n".join(rep))

else:  # transfer
    tables = {}
    for inst in ("J_NP", "LOGITS"):
        for wname, win in ([("out", None)] if inst == "LOGITS" else list(WINDOWS.items())):
            key = inst + ("" if inst == "LOGITS" else f"|{wname}")
            acc = {arm: {q: [[] for _ in range(8)] for q in ("Cdiff_sum", "Csame_sum", "Cdiff_add", "Csame_add")} for arm in ("maintain", "control")}
            for tag, c in CELLS.items():
                i = sum_idx(tag); arm = c["arm"]
                own, dsum = c["sum"], c["diff_sum"]; ownadd, dadd, sadd = c["pair"], c["diff_donor"], c["same_donor"]
                # sum endpoint
                m_clean = s_sum(f"{tag}|clean", dsum, win, inst) - s_sum(f"{tag}|clean", own, win, inst)
                m_diff = s_sum(f"{tag}|diffswap", dsum, win, inst) - s_sum(f"{tag}|diffswap", own, win, inst)
                acc[arm]["Cdiff_sum"][i].append(m_diff - m_clean)
                acc[arm]["Csame_sum"][i].append(s_sum(f"{tag}|sameswap", own, win, inst) - s_sum(f"{tag}|clean", own, win, inst))
                # addend endpoint
                a_clean_d = np.mean([s_add(f"{tag}|clean", a, win, inst) for a in dadd]) - np.mean([s_add(f"{tag}|clean", a, win, inst) for a in ownadd])
                a_diff = np.mean([s_add(f"{tag}|diffswap", a, win, inst) for a in dadd]) - np.mean([s_add(f"{tag}|diffswap", a, win, inst) for a in ownadd])
                acc[arm]["Cdiff_add"][i].append(a_diff - a_clean_d)
                a_clean_s = np.mean([s_add(f"{tag}|clean", a, win, inst) for a in sadd]) - np.mean([s_add(f"{tag}|clean", a, win, inst) for a in ownadd])
                a_same = np.mean([s_add(f"{tag}|sameswap", a, win, inst) for a in sadd]) - np.mean([s_add(f"{tag}|sameswap", a, win, inst) for a in ownadd])
                acc[arm]["Csame_add"][i].append(a_same - a_clean_s)
            T = {}
            for arm in ("maintain", "control"):
                for q in ("Cdiff_sum", "Csame_sum", "Cdiff_add", "Csame_add"):
                    T[f"{arm}|{q}"] = S.cluster_t([np.mean(v) for v in acc[arm][q]])
            # equivalence: Csame_sum within +-20% of Cdiff_sum (maintain)
            eps = 0.2 * abs(T["maintain|Cdiff_sum"]["mean"])
            T["same_sum_equivalence"] = S.equivalence([np.mean(v) for v in acc["maintain"]["Csame_sum"]], eps)
            for q in ("Cdiff_sum", "Csame_sum", "Cdiff_add", "Csame_add"):     # A = maintain - control
                T[f"A|{q}"] = S.cluster_t([np.mean(a) - np.mean(b) for a, b in zip(acc["maintain"][q], acc["control"][q])])
            tables[key] = T
    # damage
    dn = [float(Z[f"{t}|{d}swap|nll"]) - float(Z[f"{t}|clean|nll"]) for t in CELLS for d in ("diff", "same")]
    tables["damage_dNLL_max"] = float(np.max(dn))
    json.dump(tables, open(os.path.join(RES, "computed_sums_transfer_tables.json"), "w"), indent=1, default=float)
    rep = [f"# H1 · computed_sums — transfer — run {META['run_id']}\n", "## 1. Question\n",
           "Does a different-sum donor move the sum readout (C_diff^sum>0) while a same-sum sibling leaves the sum readout "
           "invariant (C_same^sum~=0, equivalence-tested) but moves the addends (C_same^add>0)? That would be computed-output "
           f"sensitivity. Cluster=sum (n=8). RESID axis not fit (J_NP+LOGITS). {META['n_forwards']} forwards.\n", "## 2. Findings (maintain arm)\n"]
    for key in ("J_NP|L48-50", "J_NP|L51-59", "LOGITS"):
        T = tables[key]
        rep.append(f"- **{key}:** C_diff^sum {cs(T['maintain|Cdiff_sum'])}; **C_same^sum {cs(T['maintain|Csame_sum'])}** "
                   f"(equivalence to 0 within ±{T['same_sum_equivalence']['eps']:.3f}: {'YES' if T['same_sum_equivalence']['equivalent'] else 'NO'}); "
                   f"C_diff^add {cs(T['maintain|Cdiff_add'])}; C_same^add {cs(T['maintain|Csame_add'])}.")
    rep.append("\n## 3. Instruction modulation A = maintain - control\n")
    for key in ("J_NP|L51-59", "LOGITS"):
        T = tables[key]
        rep.append(f"- {key}: A(C_diff^sum) {cs(T['A|Cdiff_sum'])}; A(C_diff^add) {cs(T['A|Cdiff_add'])}.")
    rep.append(f"\n**Damage:** max ΔNLL {tables['damage_dNLL_max']:+.4f}.\n\n## 4. Interpretation\n\n_Filled in by hand._\n")
    open(os.path.join(RES, "computed_sums_transfer.md"), "w").write("\n".join(rep))
    print("\n".join(rep[4:12]))
