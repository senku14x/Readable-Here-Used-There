"""Analysis for H1 scaffold_generality, `tagged` stage. Reads H1/outputs/scaffold_generality/raw_tagged.npz.

Does selection (S) survive the released directed wording and the bare presentation? For each of the four renderings
(quoted/bare x copy/directed) compute S (pointed-unpointed), Q (unpointed-control), U (pointed-control) on the word pair
margin, cluster = triple (n=8), both windows. Then the presentation and wording main effects on S, their interaction, and
the quoted_copy replication check against the tagged_selection evaluate run.

Template: tagged_selection_analysis.py. Usage: scaffold_generality_analysis.py tagged
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

STAGE = sys.argv[1] if len(sys.argv) > 1 else "tagged"
OUT = os.path.join(R.out_dir("H1", "outputs"), "scaffold_generality")
RES = os.path.join(R.out_dir("H1", "results")); FIG = os.path.join(RES, "figures"); os.makedirs(FIG, exist_ok=True)
META = json.load(open(os.path.join(OUT, f"meta_{STAGE}.json"))); Z = np.load(os.path.join(OUT, f"raw_{STAGE}.npz"))
CELLS = META["cells"]; COLS = META["columns"]; CIX = {w: i for i, w in enumerate(COLS)}
DONOR = META["donor"]; RENDERINGS = META["renderings"]; TRIPLES = [tuple(t) for t in META["triples"]]
CARRIERS = META["carriers"]; TAGS = ["A", "B", "C"]
DEC = [CIX[w] for w in COLS[24:]]                       # 24 source words + 8 decoys
WINDOWS = {"L48-50": [48, 49, 50], "L51-59": list(range(51, 60))}


def words_of(rk, ck, ti, rot):
    return CELLS[f"{rk}|{ck}|T{ti}|rot{rot}|A"]["words"]


def C(rk, ck, ti, rot, arm, j, win, inst):
    base = f"{rk}|{ck}|T{ti}|rot{rot}|{arm}"; words = CELLS[base]["words"]; X = words[j]; Y = DONOR[X]

    def m(cond):
        if inst == "J_NP":
            z = Z[f"{base}|{cond}|z"].astype(np.float32)[win]
            return float((z[:, :, CIX[Y]] - z[:, :, CIX[X]]).mean())
        if inst == "RESID_P":
            return float(Z[f"{base}|{cond}|p_pair{j}"][win].mean())
        return float(Z[f"{base}|{cond}|lp_margin{j}"].mean())
    return m(f"swap{j}") - m("clean")


def presence(rk, ck, ti, rot, arm, X, win):
    z = Z[f"{rk}|{ck}|T{ti}|rot{rot}|{arm}|clean|z"].astype(np.float32)[win]
    return float((z[:, :, CIX[X]] - z[:, :, DEC].mean(-1)).mean())


def cs(e):
    return "n/a" if e is None else f"{e['mean']:+.4f} [{e['ci'][0]:+.4f}, {e['ci'][1]:+.4f}] ({e.get('signs_pos', 0)}/{e['n']} >0)"


tables = {"renderings": RENDERINGS, "triples": [list(t) for t in TRIPLES]}
Stri = {}                                                # Stri[(inst,win)][rk] = per-triple S list (n=8)
for inst in ("J_NP", "RESID_P", "LOGITS"):
    wins = [("out", None)] if inst == "LOGITS" else list(WINDOWS.items())
    for wname, win in wins:
        key_iw = f"{inst}" + ("" if inst == "LOGITS" else f"|{wname}")
        for rk in RENDERINGS:
            rows = {q: [] for q in ("self", "other", "ctrl", "S", "Q", "U")}
            for ti, tr in enumerate(TRIPLES):
                s_, o_, c_ = [], [], []
                for ck in CARRIERS:
                    for rot in range(3):
                        for j in range(3):
                            s_.append(C(rk, ck, ti, rot, TAGS[j], j, win, inst))
                            o_.append(np.mean([C(rk, ck, ti, rot, a, j, win, inst) for a in TAGS if a != TAGS[j]]))
                            c_.append(C(rk, ck, ti, rot, "ctrl", j, win, inst))
                rows["self"].append(np.mean(s_)); rows["other"].append(np.mean(o_)); rows["ctrl"].append(np.mean(c_))
                rows["S"].append(np.mean(s_) - np.mean(o_)); rows["Q"].append(np.mean(o_) - np.mean(c_)); rows["U"].append(np.mean(s_) - np.mean(c_))
            T = {q: S.cluster_t(v) for q, v in rows.items()}
            T["S_over_U"] = S.ratio_of_means(rows["S"], rows["U"])
            tables[f"{key_iw}|{rk}"] = T
            Stri.setdefault(key_iw, {})[rk] = rows["S"]

# ---- presentation / wording main effects and interaction on S (per (inst,win)) ----
def rk_(pres, word):
    return f"{pres}_{word}"
for key_iw, byrk in Stri.items():
    n = len(TRIPLES)
    pres_eff = [0.5 * (byrk[rk_("bare", "copy")][i] + byrk[rk_("bare", "directed")][i])
                - 0.5 * (byrk[rk_("quoted", "copy")][i] + byrk[rk_("quoted", "directed")][i]) for i in range(n)]
    word_eff = [0.5 * (byrk[rk_("quoted", "directed")][i] + byrk[rk_("bare", "directed")][i])
                - 0.5 * (byrk[rk_("quoted", "copy")][i] + byrk[rk_("bare", "copy")][i]) for i in range(n)]
    inter = [(byrk[rk_("bare", "directed")][i] - byrk[rk_("bare", "copy")][i])
             - (byrk[rk_("quoted", "directed")][i] - byrk[rk_("quoted", "copy")][i]) for i in range(n)]
    tables[f"maineffect|{key_iw}"] = {"presentation_bare_minus_quoted": S.cluster_t(pres_eff),
                                      "wording_directed_minus_copy": S.cluster_t(word_eff),
                                      "interaction": S.cluster_t(inter)}

# ---- S_nat (natural readout selectivity, no swap) per rendering, J_NP ----
for wname, win in WINDOWS.items():
    for rk in RENDERINGS:
        snat = []
        for ti, tr in enumerate(TRIPLES):
            s_, o_ = [], []
            for ck in CARRIERS:
                for rot in range(3):
                    words = words_of(rk, ck, ti, rot)
                    for j, X in enumerate(words):
                        s_.append(presence(rk, ck, ti, rot, TAGS[j], X, win))
                        o_.append(np.mean([presence(rk, ck, ti, rot, a, X, win) for a in TAGS if a != TAGS[j]]))
            snat.append(np.mean(s_) - np.mean(o_))
        tables[f"S_nat|{wname}|{rk}"] = S.cluster_t(snat)

# ---- replication: quoted_copy S vs tagged_selection evaluate S ----
repl = {}
ts_path = os.path.join(RES, "tagged_selection_evaluate_tables.json")
if os.path.exists(ts_path):
    TS = json.load(open(ts_path))
    for wname in WINDOWS:
        here = Stri[f"J_NP|{wname}"][rk_("quoted", "copy")]
        there = TS.get(f"J_NP|{wname}", {}).get("S", {})
        if there:
            repl[wname] = {"here_mean": float(np.mean(here)), "there_mean": there["mean"],
                           "ratio": float(np.mean(here) / there["mean"]) if there["mean"] else float("nan")}
tables["replication_quoted_copy_vs_evaluate"] = repl

# ---- damage ----
dnll, top1r = [], []
for base in CELLS:
    cn = float(Z[f"{base}|clean|nll"]); ct = Z[f"{base}|clean|top1"]
    for j in range(3):
        dnll.append(float(Z[f"{base}|swap{j}|nll"]) - cn); top1r.append(float((Z[f"{base}|swap{j}|top1"] == ct).mean()))
tables["damage"] = {"dNLL_mean": float(np.mean(dnll)), "dNLL_max": float(np.max(dnll)),
                    "top1_retention_min": float(np.min(top1r)), "top1_retention_mean": float(np.mean(top1r))}

# ---- Holm across the two windows for S, per rendering (J_NP) ----
for rk in RENDERINGS:
    ps = [S.paired_p(Stri[f"J_NP|{wn}"][rk]) for wn in WINDOWS]
    tables[f"holm_S_JNP|{rk}"] = {wn: float(v) for wn, v in zip(WINDOWS, S.holm(ps))}

json.dump(tables, open(os.path.join(RES, f"scaffold_generality_{STAGE}_tables.json"), "w"), indent=1, default=float)

# ---- figure: S per rendering (J_NP L51-59), per-triple points ----
plt.figure(figsize=(7, 4))
for i, rk in enumerate(RENDERINGS):
    e = tables[f"J_NP|L51-59|{rk}"]["S"]
    plt.errorbar(i, e["mean"], yerr=[[e["mean"] - e["ci"][0]], [e["ci"][1] - e["mean"]]], fmt="o", color="k", capsize=3)
    plt.scatter(np.full(len(e["per_cluster"]), i), e["per_cluster"], s=16, alpha=0.6)
plt.xticks(range(len(RENDERINGS)), RENDERINGS, rotation=15); plt.axhline(0, color="k", lw=0.5)
plt.ylabel("S (pointed - unpointed), J_NP L51-59"); plt.title("scaffold_generality: does selection survive each rendering?")
plt.tight_layout(); plt.savefig(os.path.join(FIG, "scaffold_generality_S_by_rendering.png"), dpi=130); plt.close()

# ---- report ----
def line(rk):
    parts = []
    for key in (f"J_NP|L48-50|{rk}", f"J_NP|L51-59|{rk}", f"RESID_P|L51-59|{rk}", f"LOGITS|{rk}"):
        T = tables[key]; short = key.replace(f"|{rk}", "")
        parts.append(f"{short} S={cs(T['S'])} Q={cs(T['Q'])} U={cs(T['U'])}")
    return f"- **{rk}:** " + " ; ".join(parts)

rep = [f"# H1 · scaffold_generality — TAGGED (does selection survive rendering?) — run {META['run_id']}\n",
       "## 1. Question and setup\n",
       f"Every causal result so far uses the quoted-and-introduced copy scaffold. Here the tagged organism is run in all four "
       f"presentation(quoted/bare) x wording(copy/directed) renderings, keeping the 'Here are three words (A)(B)(C)' head and the copy "
       f"bridge in every cell so the tag mechanism exists throughout; presentation and wording are the only factors. 8 evaluation "
       f"triples, 3 rotations, carriers {CARRIERS}, arms A/B/C point at slots 0/1/2, ctrl none; each source replaced from block 36 by "
       f"the partner (next triple, same index). Endpoint = word pair margin (donor - source); S=pointed-unpointed, Q=unpointed-control, "
       f"U=pointed-control; cluster=triple (n=8); windows L48-50 & L51-59. {META['n_forwards']} forwards; same-source and layer<36 "
       f"identity asserted per cell.\n",
       "## 2. Main findings\n"]
for rk in RENDERINGS:
    rep.append(line(rk))
rep.append("\n**Presentation / wording main effects on S (J_NP, per-triple contrasts, n=8):**")
for wn in WINDOWS:
    me = tables[f"maineffect|J_NP|{wn}"]
    rep.append(f"- {wn}: presentation (bare−quoted) {cs(me['presentation_bare_minus_quoted'])}; wording (directed−copy) {cs(me['wording_directed_minus_copy'])}; interaction {cs(me['interaction'])}.")
rep.append(f"\n**Replication (quoted_copy S vs tagged_selection evaluate):** {json.dumps(tables['replication_quoted_copy_vs_evaluate'], default=lambda x: round(x,3))}")
rep.append(f"**S_nat (natural selectivity, no swap, L51-59):** " + "; ".join(f"{rk} {cs(tables[f'S_nat|L51-59|{rk}'])}" for rk in RENDERINGS))
rep.append(f"**Damage:** ΔNLL max {tables['damage']['dNLL_max']:+.4f}; top-1 retention min {tables['damage']['top1_retention_min']:.3f} (mean {tables['damage']['top1_retention_mean']:.3f}).")
rep.append(f"**Holm p (S, J_NP):** " + "; ".join(f"{rk} {json.dumps({k: round(v,4) for k,v in tables[f'holm_S_JNP|{rk}'].items()})}" for rk in RENDERINGS) + "\n")

rep.append("## 3. Complete tables\n")
for rk in RENDERINGS:
    rep.append(f"### {rk}\n\n| inst·win | S | Q | U | pointed | unpointed | control |\n|---|---|---|---|---|---|---|")
    for key in (f"J_NP|L48-50|{rk}", f"J_NP|L51-59|{rk}", f"RESID_P|L48-50|{rk}", f"RESID_P|L51-59|{rk}", f"LOGITS|{rk}"):
        T = tables[key]; short = key.replace(f"|{rk}", "")
        rep.append(f"| {short} | {cs(T['S'])} | {cs(T['Q'])} | {cs(T['U'])} | {T['self']['mean']:+.3f} | {T['other']['mean']:+.3f} | {T['ctrl']['mean']:+.3f} |")
    rep.append("")
rep.append(f"Figure: `figures/scaffold_generality_S_by_rendering.png`. Machine-readable: `scaffold_generality_{STAGE}_tables.json`.\n")
rep.append("## 4. Verification and limitations\n\n"
           "- Same-source (slot 0) bitwise equal to clean and layers < 36 identical between futures asserted per cell; donor geometry asserted per swap (quoted spans 3 tokens, bare 1 token). Damage above.\n"
           "- The pure direct organism (no copy bridge) and the single-word 2×2 are the `single` stage (not in this report); native-vs-transferred fits are the `directions` stage. Different instruments on the same forwards are robustness, not independent samples.\n")
rep.append("## 5. Interpretation and next decision\n\n_Filled in by hand after reading the tables (per design §5–6: S CI-clear with Q≤0 in all four renderings ⇒ selection is a property of relevance instructions, not the copy scaffold; any rendering with S≈0 is a scope limit)._\n")
open(os.path.join(RES, f"scaffold_generality_{STAGE}.md"), "w").write("\n".join(rep))
print("\n".join(rep[4:12]))
print("\n[analysis written; run after the battery completes]")
