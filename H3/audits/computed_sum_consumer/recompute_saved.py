"""Independent recompute of every headline number in H3/results/computed_sum_consumer.md from the committed
raw_*.npz / meta_*.json archives. Imports NOTHING from the runner. ONE scoring rule throughout:
    answer = argmax over the candidate words of logsumexp(log-probs of their single-token surface forms)
(this is the rule the report's competence used; the runner's ad-hoc greedy-prefix flip check is re-derived here
and its discrepancy is flagged). Cluster = sum (8), carriers averaged within sum, t-interval df=7.

Usage: python recompute_saved.py            (reads H3/outputs/computed_sum_consumer/)
"""
import json, os, sys
import numpy as np
from scipy import stats as sps

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "outputs", "computed_sum_consumer")
SUMW = ["seven", "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen"]
PAR = ["even", "odd"]
REPORT = {}   # what the report claims, for side-by-side


def load(stage):
    m = json.load(open(os.path.join(OUT, f"meta_{stage}.json")))
    d = np.load(os.path.join(OUT, f"raw_{stage}.npz"), allow_pickle=True)
    return m, d


def ct(v):
    v = np.asarray(v, float); mn = v.mean(); h = sps.t.ppf(0.975, len(v) - 1) * v.std(ddof=1) / np.sqrt(len(v))
    return mn, mn - h, mn + h, int((v > 0).sum())


def fmt(v):
    mn, lo, hi, sp = ct(v); return f"{mn:+.2f} [{lo:+.2f},{hi:+.2f}] {sp}/8"


def by_sum(cells, fn):
    """average the two carriers within each of the 8 sums -> 8 cluster values."""
    return np.array([np.mean([fn(f"S{i}|{ck}", cells[f"S{i}|{ck}"]) for ck in ("C0", "C1")]) for i in range(8)])


def parity_independent(sword):
    """independent parity: numeric value of the sum word."""
    val = {"seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14}[sword]
    return "odd" if val % 2 else "even"


def argmax_word(scores, words):
    return words[int(np.argmax(scores))]


def section(t):
    print("\n" + "=" * 100 + f"\n{t}\n" + "=" * 100)


# ----------------------------------------------------------------------------------------------------------------
section("0. PARITY MAPPING — independent check of own_parity / diff_parity in meta (numeric, not index arithmetic)")
m_b, d_b = load("boundary")
bad = 0
for b, info in m_b["cells"].items():
    if info["own_parity"] != parity_independent(info["sum"]) or info["diff_parity"] != parity_independent(info["diff_sum"]):
        bad += 1; print("  MISMATCH", b, info["sum"], info["own_parity"], info["diff_sum"], info["diff_parity"])
    if info["own_parity"] == info["diff_parity"]:
        bad += 1; print("  diff donor does NOT flip parity:", b)
print(f"  parity mapping consistent with numeric values, diff donor flips parity in all cells: {'YES' if bad == 0 else 'NO (' + str(bad) + ')'}")

# ----------------------------------------------------------------------------------------------------------------
section("1. BOUNDARY GATE (raw_boundary) — scored-argmax rule, all 16 cells and cluster-t over 8 sums")
cells = m_b["cells"]; COLS = m_b["columns"]
sp = [cells[b].get(f"{cn}_selfpatch_bitwise") for b in cells for cn in ("parity", "report")]
print(f"  self-patch bitwise no-op: {sum(bool(x) for x in sp)}/{len(sp)}")
for cn, words in (("parity", PAR), ("report", SUMW)):
    print(f"  -- {cn} --")
    for lx in (23, 36):
        clean_ok = flip = same_stay = 0
        for b, info in cells.items():
            own = info["own_parity"] if cn == "parity" else info["sum"]
            don = info["diff_parity"] if cn == "parity" else info["diff_sum"]
            cl = argmax_word(d_b[f"{b}|{cn}|clean|scores"], words)
            df = argmax_word(d_b[f"{b}|{cn}|diffswap|lx{lx}|scores"], words)
            sm = argmax_word(d_b[f"{b}|{cn}|sameswap|lx{lx}|scores"], words)
            clean_ok += (cl == own); flip += (df == don); same_stay += (sm == own)
        def msh(dn):
            def f(b, info):
                if cn == "parity":
                    oi = 0 if info["own_parity"] == "even" else 1; di = 1 - oi
                else:
                    oi = SUMW.index(info["sum"]); di = SUMW.index(info["diff_sum"])
                c = d_b[f"{b}|{cn}|clean|scores"]; s = d_b[f"{b}|{cn}|{dn}swap|lx{lx}|scores"]
                return (s[di] - s[oi]) - (c[di] - c[oi])
            return f
        print(f"    L{lx}: clean-correct {clean_ok}/16 | diff->donor FLIP {flip}/16 | same stays {same_stay}/16"
              f" | margin diff {fmt(by_sum(cells, msh('diff')))} | same {fmt(by_sum(cells, msh('same')))}")
W = slice(51, 60)
print("  -- internal C_diff^sum, L51-59, report forwards --")
for lx in (23, 36):
    def cds(b, info):
        oi = COLS.index(info["sum"]); di = COLS.index(info["diff_sum"])
        zc = d_b[f"{b}|report|clean|z"]; zd = d_b[f"{b}|report|diffswap|lx{lx}|z"]
        return float((zd[W, :, di] - zd[W, :, oi]).mean() - (zc[W, :, di] - zc[W, :, oi]).mean())
    print(f"    L{lx}: {fmt(by_sum(cells, cds))}")
print("  -- carrier damage (report): dNLL diffswap - clean --")
for lx in (23, 36):
    dd = np.array([float(d_b[f"{b}|report|diffswap|lx{lx}|nll"][()]) - float(d_b[f"{b}|report|clean|nll"][()]) for b in cells])
    print(f"    L{lx}: mean {dd.mean():+.4f} max {dd.max():+.4f}")

# ----------------------------------------------------------------------------------------------------------------
section("2. TRANSPORT (raw_transport) — the load-bearing dissociation; scored-argmax rule (fixes the runner's greedy-prefix check)")
m_t, d_t = load("transport"); cells = m_t["cells"]; COLS = m_t["columns"]
print(f"  lx={m_t['lx']}  n_forwards={m_t['n_forwards']}  (expect 8 sums x 2 carriers x 2 consumers x 5 = 160)")
for cn, words in (("report", SUMW), ("parity", PAR)):
    print(f"  -- {cn} --")
    for cond in ("O_donor", "C_full", "C_rand"):
        flip_scored = flip_greedy_prefix = 0
        for b, info in cells.items():
            don = info["diff_parity"] if cn == "parity" else info["diff_sum"]
            sc = argmax_word(d_t[f"{b}|{cn}|{cond}|scores"], words)
            flip_scored += (sc == don)
            g = str(d_t[f"{b}|{cn}|{cond}|greedy"][()]).strip().lower()
            flip_greedy_prefix += (g.startswith(don[:3]) if cn == "report" else g == don)   # the runner's ad-hoc rule
        def msh(b, info):
            if cn == "parity":
                oi = 0 if info["own_parity"] == "even" else 1; di = 1 - oi
            else:
                oi = SUMW.index(info["sum"]); di = SUMW.index(info["diff_sum"])
            c = d_t[f"{b}|{cn}|clean|scores"]; s = d_t[f"{b}|{cn}|{cond}|scores"]
            return (s[di] - s[oi]) - (c[di] - c[oi])
        def intl(b, info):
            oi = COLS.index(info["sum"]); di = COLS.index(info["diff_sum"])
            zc = d_t[f"{b}|report|clean|z"]; zx = d_t[f"{b}|report|{cond}|z"]
            return float((zx[W, :, di] - zx[W, :, oi]).mean() - (zc[W, :, di] - zc[W, :, oi]).mean())
        print(f"    {cond:8s} flip(scored) {flip_scored:2d}/16  flip(greedy-prefix, runner rule) {flip_greedy_prefix:2d}/16"
              f" | margin {fmt(by_sum(cells, msh))} | internal(carrier sum) {fmt(by_sum(cells, intl))}")
print("  -- clean competence in transport forwards --")
for cn, words in (("report", SUMW), ("parity", PAR)):
    ok = sum(argmax_word(d_t[f"{b}|{cn}|clean|scores"], words) == (info["sum"] if cn == "report" else info["own_parity"]) for b, info in cells.items())
    print(f"    {cn}: {ok}/16")
print("  -- carrier damage under C_full (dNLL vs clean) --")
for cn in ("report", "parity"):
    dd = np.array([float(d_t[f"{b}|{cn}|C_full|nll"][()]) - float(d_t[f"{b}|{cn}|clean|nll"][()]) for b in cells])
    print(f"    {cn}: mean {dd.mean():+.4f} max {dd.max():+.4f}")
print("  -- MATCHED INTERNAL CONTROL: ratio of C_full to O_donor internal shift (per-sum, report) --")
def r_int(cond):
    def f(b, info):
        oi = COLS.index(info["sum"]); di = COLS.index(info["diff_sum"])
        zc = d_t[f"{b}|report|clean|z"]; zx = d_t[f"{b}|report|{cond}|z"]
        return float((zx[W, :, di] - zx[W, :, oi]).mean() - (zc[W, :, di] - zc[W, :, oi]).mean())
    return f
a, c = by_sum(cells, r_int("O_donor")), by_sum(cells, r_int("C_full"))
print(f"    C_full/O_donor internal per-sum: {np.round(c / a, 2)}   mean ratio {(c / a).mean():.2f}")
print("  -- BEHAVIORAL ratio C_full/O_donor margin (report; ratio of cluster means) --")
def r_b(cond):
    def f(b, info):
        oi = SUMW.index(info["sum"]); di = SUMW.index(info["diff_sum"])
        cl = d_t[f"{b}|report|clean|scores"]; s = d_t[f"{b}|report|{cond}|scores"]; return (s[di] - s[oi]) - (cl[di] - cl[oi])
    return f
print(f"    C_full/O_donor behavioral (ratio of means): {by_sum(cells, r_b('C_full')).mean() / by_sum(cells, r_b('O_donor')).mean():.3f}")
print("  -- O_donor reproducibility: transport vs boundary internal C_diff^sum at L36 (same intervention, independent runs) --")
def cds36(b, info):
    oi = COLS.index(info["sum"]); di = COLS.index(info["diff_sum"])
    zc = d_b[f"{b}|report|clean|z"]; zd = d_b[f"{b}|report|diffswap|lx36|z"]
    return float((zd[W, :, di] - zd[W, :, oi]).mean() - (zc[W, :, di] - zc[W, :, oi]).mean())
print(f"    boundary lx36 {fmt(by_sum(m_b['cells'], cds36))}   transport O_donor {fmt(by_sum(cells, r_int('O_donor')))}")

# ----------------------------------------------------------------------------------------------------------------
section("3. CALIBRATION (meta_calibrate) — A/B/C recomputed from meta")
m_c = json.load(open(os.path.join(OUT, "meta_calibrate.json")))
A = m_c["calibrate"]["A_lookup"]; BC = m_c["calibrate"]["BC_predicate"]
for cond in ("explicit", "latent"):
    v = [x["correct"] for x in A.values() if x["cond"] == cond]; print(f"  A {cond:8s} {np.mean(v):.3f} ({sum(v)}/{len(v)})")
for p in ("gt10", "parity"):
    v = [x["correct"] for k, x in BC.items() if k.startswith(p + "|")]; print(f"  {p:7s} {np.mean(v):.3f} ({sum(v)}/{len(v)})")
# competence-stage (codebook) recount + confound check
m_k = json.load(open(os.path.join(OUT, "meta_competence.json")))["competence"]
for q in ("sum_pair", "sum_two", "total_pair"):
    v = [x["correct"] for k, x in m_k.items() if k.endswith(q)]; print(f"  codebook {q:10s} {np.mean(v):.3f} ({sum(v)}/{len(v)})")
# was the codebook shared across wordings in the ORIGINAL competence run? (the RNG confound)
shared = all(m_k[f"{i}|{ck}|sum_pair"]["assign"] == m_k[f"{i}|{ck}|sum_two"]["assign"] for i in range(8) for ck in ("C0", "C1"))
print(f"  original competence run: codebook identical across wordings? {shared}  (False = the RNG confound the review caught)")
print("\nDONE")
