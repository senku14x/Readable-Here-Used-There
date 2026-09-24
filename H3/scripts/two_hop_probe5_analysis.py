"""Analysis for two_hop_organism stage `probe5` (Amendment 10): raw_probe5.npz + raw_probe5_zq.npz + meta_probe5.json (+ raw_probe4.npz for the
reproduction gates, Stage 2 tables for the J25 install share) -> H3/results/tables/two_hop_probe5_tables.json, H3/results/reports/two_hop_probe5.md
(generated sections; the hand-written reading inlined from two_hop_probe5_reading.md) and H3/results/figures/h3_probe5.{png,pdf}.
Usage: two_hop_probe5_analysis.py [probe5|smoke5]"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "..", "common", "scripts"))
import numpy as np
import registry as R

STAGE = sys.argv[1] if len(sys.argv) > 1 else "probe5"
OUT = R.out_dir("H3", "outputs", "two_hop_organism"); REP = R.out_dir("H3", "results", "reports"); TAB = R.out_dir("H3", "results", "tables"); FIG = R.out_dir("H3", "results", "figures")
RAW = dict(np.load(os.path.join(OUT, f"raw_{STAGE}.npz"), allow_pickle=True)); Z = dict(np.load(os.path.join(OUT, f"raw_{STAGE}_zq.npz"))); META = json.load(open(os.path.join(OUT, f"meta_{STAGE}.json")))
R4 = np.load(os.path.join(OUT, "raw_probe4.npz"), allow_pickle=True); S2 = json.load(open(os.path.join(TAB, "two_hop_stage2_tables.json")))
cells = list(META["cells_ab"]); names = list(dict.fromkeys(b.split("|")[0] for b in cells)); ccells = list(META["cells_c"]); pairs = list(dict.fromkeys(b.split("|")[0] for b in ccells)); NI, NP = len(names), len(pairs)
CAT = {nm: META["cells_ab"][nm + "|" + META["carriers_ab"][0]].get("category") for nm in names}; SEED_BOOT = 20260907


def ci(v):
    from scipy import stats as st
    v = np.asarray(v, float); m = float(v.mean()); n = len(v); h = float(st.t.ppf(0.975, n - 1) * v.std(ddof=1) / np.sqrt(n)) if n > 1 else float("nan")
    return {"mean": m, "ci": [m - h, m + h], "n_pos": int((v > 0).sum()), "n": n}


def boot(f, arrays, n, B=2000):
    rng = np.random.default_rng(SEED_BOOT); vals = [f(*[a[idx] for a in arrays]) for idx in (rng.integers(0, n, n) for _ in range(B))]
    vals = np.asarray(vals, float); vals = vals[np.isfinite(vals)]; return [float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))] if len(vals) else [np.nan, np.nan]


def mg(R_, b, row, base="clean"): return float((R_[f"{b}|{row}|seq_swap"] - R_[f"{b}|{row}|seq_answer"]) - (R_[f"{b}|{base}|seq_swap"] - R_[f"{b}|{base}|seq_answer"]))


byitem = lambda f: np.array([np.mean([f(b) for b in cells if b.startswith(nm + "|")]) for nm in names])
BASE = lambda row: ("clean:m63A" if row.endswith("m63A") else (("clean:" + row.split(":")[-1]) if row.split(":")[-1].startswith("cut") else "clean"))
rows_ab = [r for r in META["rows_pass1"] + META["rows_pass2"] if not r.startswith("clean")]
M_ = {r: byitem(lambda b: mg(RAW, b, r, BASE(r))) for r in rows_ab if f"{cells[0]}|{r}|seq_swap" in RAW}; full = M_["full"]
sh = lambda r: float(M_[r].mean() / full.mean()); shci = lambda r: boot(lambda a, f_: a.mean() / f_.mean(), [M_[r], full], NI)
T = {"stage": STAGE, "run_id": META["run_id"], "n_forwards": META["n_forwards"], "elapsed_s": META["elapsed_s"], "n_items": NI, "n_pairs": NP, "rows": {r: {"share": sh(r), "share_ci": shci(r), "margin": ci(M_[r])} for r in M_}}

# ---- gates
ref = {"full": ("q_full_pre", "clean", "clean"), "J25rem": ("q_J25rem_pre", "clean", "clean"), "J25rem:ccsA": ("q_J25rem_pre_ccsA", "clean", "clean"),
       "J25rem:ccsA:m63A": ("q_J25rem_pre_ccsA_m63A", "clean:m63A", "clean_m63A"), "full:sfullA": ("q_full_pre_sfullA", "clean", "clean")}
rep = {r: [abs(mg(RAW, b, r, b5) - mg(R4, b, r4, b4)) for b in cells] for r, (r4, b5, b4) in ref.items()}
def mc(R_, b, c, tm):
    base = "lang_clean" if (c == "q_xfer" or c.startswith("x_")) else "cap_clean"
    return float((R_[f"{b}|{c}|donor_{tm}"] - R_[f"{b}|{c}|own_{tm}"]) - (R_[f"{b}|{base}|donor_{tm}"] - R_[f"{b}|{base}|own_{tm}"]))
repB = {c: [abs(mc(RAW, b, c, tm) - mc(R4, b, c, tm)) for b in ccells for tm in ("lang", "cap")] for c in ("q_xfer", "x_ctry", "q_mirror", "m_ctry")}
T["gate_reproduction"] = {**{r: {"max_abs_diff": float(max(v)), "fraction_within_0.01": float(np.mean(np.array(v) <= 0.01))} for r, v in rep.items()},
                          **{f"B:{c}": {"max_abs_diff": float(max(v)), "fraction_within_0.01": float(np.mean(np.array(v) <= 0.01))} for c, v in repB.items()}}
T["gate_reproduction"]["pass"] = bool(all(v["fraction_within_0.01"] >= 0.95 for k, v in T["gate_reproduction"].items() if k != "pass"))
T["gate_L"] = {"leak_max": float(max(META["leak"].values())) if META["leak"] else float("nan")}; T["gate_L"]["pass"] = bool(T["gate_L"]["leak_max"] <= 1e-6)
T["gate_writes_partB"] = {"rho_min": float(min(float(RAW[f"{b}|{c}|rho"]) for b in ccells for c in META["rows_c"])), "rho_max": float(max(float(RAW[f"{b}|{c}|rho"]) for b in ccells for c in META["rows_c"])),
                          "kappa_min": float(min(float(RAW[f"{b}|{c}|kappa"]) for b in ccells for c in META["rows_c"]))}
T["gate_writes_partB"]["pass"] = bool(0.9 <= T["gate_writes_partB"]["rho_min"] and T["gate_writes_partB"]["rho_max"] <= 1.1 and T["gate_writes_partB"]["kappa_min"] >= 0.99)
T["gate_writes_note"] = "realized-write statistics were not logged for the Part A/C/D/E rows; the write and clamp code is Amendment 9's, and its reference rows reproduce probe4 (see gate_reproduction)"

# ---- Part B
MC = {(c, tm): np.array([np.mean([mc(RAW, b, c, tm) for b in ccells if b.startswith(p + "|")]) for p in pairs]) for c in META["rows_c"] for tm in ("lang", "cap")}
def partB(pref, refrow, tm, ans):
    r0 = MC[(refrow, tm)]; f = lambda k: float(MC[(f"{pref}_{k}", tm)].mean() / r0.mean()); fci = lambda k: boot(lambda a, b_: a.mean() / b_.mean(), [MC[(f"{pref}_{k}", tm)], r0], NP)
    out = {k: {"share": f(k), "ci": fci(k), "per_pair": (MC[(f"{pref}_{k}", tm)] / r0).tolist()} for k in ("ctry", ans, "ctry_perp", f"{ans}_perp", "rand2b")}
    rd = ("geometry: the transfer runs along the receiving question's answer directions; 'country dominant' is withdrawn and reworded" if (out["ctry_perp"]["share"] <= 0.15 and out[ans]["share"] >= out["ctry"]["share"] - 0.10)
          else ("country content: the country plane carries transferable content beyond the answer directions" if out["ctry_perp"]["share"] >= 0.35 else "partial"))
    return {**out, "reference_push": ci(r0), "reading": rd}
cosL = np.array([np.array(META["cells_c"][b]["principal_cos_ctry_lang"])[15:24].mean(0) for b in ccells]); cosK = np.array([np.array(META["cells_c"][b]["principal_cos_ctry_cap"])[15:24].mean(0) for b in ccells])
T["partB"] = {"language_question": partB("x", "q_xfer", "lang", "lang"), "capital_question_mirror": partB("m", "q_mirror", "cap", "cap"),
              "principal_cos_country_vs_language_plane_L51_59": cosL.mean(0).tolist(), "principal_cos_country_vs_capital_plane_L51_59": cosK.mean(0).tolist()}

# ---- Part A
R0, RJ, RF = sh("J25rem:m63A"), sh("J25rem:ccsA:m63A"), sh("J25rem:ccfA:m63A")
if R0 < 0.10: rdA = f"descriptive only (registration note 1): the middle-layer route carries R0 = {R0:.3f} < 0.10"
elif RF >= 0.6 * R0 and RJ <= 0.25 * R0: rdA = "readable-specific: before the last layer the complement's effect at the answer position travels through the readable span, not merely its largest directions"
elif RF <= 0.25 * R0: rdA = "not specific: any fitted span of that rank blocks the route"
else: rdA = "partial"
capJ, capF = np.array(META["capture_dh_s_J"]), np.array(META["capture_dh_s_phi"])
rcJ = np.mean([RAW[f"{b}|capture_rowchange_J"].mean() for b in cells]); rcF = np.mean([RAW[f"{b}|capture_rowchange_phi"].mean() for b in cells])
T["partA"] = {"R0": R0, "R0_ci": shci("J25rem:m63A"), "R_J": RJ, "R_J_ci": shci("J25rem:ccsA:m63A"), "R_phi": RF, "R_phi_ci": shci("J25rem:ccfA:m63A"), "C_A_J": sh("J25rem:ccsA"), "C_A_phi": sh("J25rem:ccfA"),
              "capture_dh_s": {"J": float(capJ.mean()), "phi": float(capF.mean())}, "capture_rowchange": {"J": float(rcJ), "phi": float(rcF)}, "phi_prime_triggered": META["phi_prime_triggered"], "reading": rdA}
if META["phi_prime_triggered"]: T["partA"].update({"R_phi_prime": sh("J25rem:ccf2A:m63A"), "C_A_phi_prime": sh("J25rem:ccf2A")})

# ---- Part C
J25_install = S2["rows"]["q_J25_pre"]["share_of_q_full_pre"]; F = sh("F25"); eJ, eF = float(np.mean(META["energy_qpre_J25"])), float(np.mean(META["energy_qpre_F25"]))
rdC = ("Jacobian-generic" if (F >= J25_install - 0.10 and eF <= eJ * 1.1) else ("vocabulary-specific" if F <= 0.5 * J25_install else "partial"))
T["partC"] = {"F25_install": F, "F25_install_ci": shci("F25"), "J25_install_stage2": J25_install, "F25_complement": sh("F25rem"), "R25_complement": sh("R25rem"), "energy_qpre_J25": eJ, "energy_qpre_F25": eF, "reading": rdC}

# ---- Part D
D0 = full_sfA = sh("full:sfullA"); rem = {}
for X in "TWP":
    r = f"full:sfullA:cut{X}"; rem[X] = {"share_with_cut": sh(r), "removed_fraction": 1 - sh(r) / D0, "ci": boot(lambda a, b_: 1 - a.mean() / b_.mean(), [M_[r], M_["full:sfullA"]], NI)}
DE = np.stack([RAW[f"{b}|head_DE"] for b in cells]); mass = np.stack([RAW[f"{b}|head_mass"] for b in cells]); de = DE.mean(0); order = np.argsort(-de); cum = np.cumsum(de[order]) / de.sum()
top = order[: int(np.searchsorted(cum, 0.5) + 1)]
T["partD"] = {"D0": D0, "removal": rem, "prediction_T_ge_0.7_W_le_0.3": bool(rem["T"]["removed_fraction"] >= 0.7 and rem["W"]["removed_fraction"] <= 0.3),
              "head_DE_mean": de.tolist(), "heads_for_50pct": [int(h) for h in top], "top_heads_share_of_DE": float(de[top].sum() / de.sum()), "top_heads_mass_TWP": mass.mean(0)[top].tolist(), "DE_sum_mean": float(DE.sum(1).mean())}
# ---- Part E
T["partE"] = {"depth_curve": {str(B_): sh(f"full:sfull{B_}") for B_ in META["depths"]} | {"62": D0}}
json.dump(T, open(os.path.join(TAB, f"two_hop_{STAGE}_tables.json"), "w"), indent=1, default=str)

# ---- report
f2 = lambda x: f"{x:+.2f}"; f3 = lambda x: f"{x:+.3f}"; cb = lambda c: f"[{c[0]:.3f}, {c[1]:.3f}]"
L = [f"# two_hop_organism · stage `{STAGE}` — consumer-span control, orthogonalised cross-question planes, functional-row null, where the last layer reads (Amendment 10)\n",
     f"Run `{META['run_id']}`, {META['n_forwards']} forwards, {META['elapsed_s']} s. Same model and regime as Amendment 9. Parts A, C, D, E: {len(cells)} cells ({NI} admitted items × {len(META['carriers_ab'])} carriers), cluster = item. Part B: {len(ccells)} cells ({NP} pairs), cluster = pair. Shares are ratios of item (pair) means with cluster-bootstrap intervals. Design: Amendment 10 of `H3/design_specs/two_hop_organism.md`; battery `two_hop_probe5.py`; the last section is hand-written.\n",
     "## 1. Gates\n", "- Reproduction of `probe4`: " + "; ".join(f"`{k}` max |Δ| {v['max_abs_diff']:.1e}" for k, v in T["gate_reproduction"].items() if k != "pass") + f" — **{'PASS' if T['gate_reproduction']['pass'] else 'FAIL'}**.",
     f"- Gate L (block-63 cuts): maximum post-softmax weight {T['gate_L']['leak_max']:.1e} — **{'PASS' if T['gate_L']['pass'] else 'FAIL'}**. Part B writes ρ {T['gate_writes_partB']['rho_min']:.4f}–{T['gate_writes_partB']['rho_max']:.4f}, κ ≥ {T['gate_writes_partB']['kappa_min']:.4f} — **{'PASS' if T['gate_writes_partB']['pass'] else 'FAIL'}**. {T['gate_writes_note']}.",
     f"- Part D position classes asserted per cell (T = `q_pre` 19–26, W = 5–18, P = 0–4); Φ′ {'triggered' if META['phi_prime_triggered'] else 'not triggered'} (Φ/J capture of Δh_s = {META['phi_over_J_capture']:.2f}).\n", "## 2. Part B: planes orthogonalised against the receiving question's answer\n",
     "| question (delta) | transfer push (nats) | country plane | answer plane | country ⊥ answer | answer ⊥ country | random | reading |", "|---|---|---|---|---|---|---|---|"]
for lab, key, ans in (("language question (capital delta)", "language_question", "lang"), ("capital question (language delta)", "capital_question_mirror", "cap")):
    v = T["partB"][key]; g = lambda k: f"{v[k]['share']:.2f} {cb(v[k]['ci'])}"
    L.append(f"| {lab} | {f2(v['reference_push']['mean'])} | {g('ctry')} | {g(ans)} | {g('ctry_perp')} | {g(ans + '_perp')} | {g('rand2b')} | **{v['reading']}** |")
L.append(f"\nPrincipal cosines, L51–59: country plane vs language plane {np.round(T['partB']['principal_cos_country_vs_language_plane_L51_59'], 2).tolist()}; country plane vs capital plane {np.round(T['partB']['principal_cos_country_vs_capital_plane_L51_59'], 2).tolist()}.\n")
A = T["partA"]
L += ["## 3. Part A: the fitted non-lens span at the consumer\n", f"R0 (J_25 complement, block-63 read cut, no clamp) = **{f3(A['R0'])}** {cb(A['R0_ci'])}; with the pinned readable span clamped R_J = **{f3(A['R_J'])}** {cb(A['R_J_ci'])}; with the fitted non-lens span Φ clamped R_Φ = **{f3(A['R_phi'])}** {cb(A['R_phi_ci'])}. Without the cut: pinned span {f3(A['C_A_J'])}, Φ {f3(A['C_A_phi'])}. "
      f"Energy captured of the natural change at s: pinned {A['capture_dh_s']['J']:.3f}, Φ {A['capture_dh_s']['phi']:.3f}; of the un-clamped row's change at the answer positions: pinned {A['capture_rowchange']['J']:.3f}, Φ {A['capture_rowchange']['phi']:.3f} → registered reading: **{A['reading']}**.\n"]
C = T["partC"]
L += ["## 4. Part C: the functional-row null\n", f"Installing the best 25 functional directions f_u = J_lᵀ(γ ⊙ u), u ~ N(0, Cov W_U), gives **{f3(C['F25_install'])}** {cb(C['F25_install_ci'])} of the effect, against {f3(C['J25_install_stage2'])} for the best 25 vocabulary directions (Stage 2, same cells). "
      f"Complements: functional {f3(C['F25_complement'])}, norm- and rank-matched random {f3(C['R25_complement'])}. Energy captured on `q_pre`: vocabulary {C['energy_qpre_J25']:.3f}, functional {C['energy_qpre_F25']:.3f} → registered reading: **{C['reading']}**.\n"]
Dd = T["partD"]
L += ["## 5. Part D: where the last layer reads\n", f"D0 = share with the answer positions held clean through block 62 = {f3(Dd['D0'])}. Fraction of D0 removed by cutting block 63's read from the answer positions to each class: " + "; ".join(f"**{X}** {v['removed_fraction']:.2f} {cb(v['ci'])}" for X, v in Dd["removal"].items())
      + f". Registered (post hoc) prediction T ≥ 0.7 and W ≤ 0.3: {'held' if Dd['prediction_T_ge_0.7_W_le_0.3'] else 'not held'}. Heads carrying ≥ 50 % of the summed direct effect on the first-token margin: {Dd['heads_for_50pct']} ({Dd['top_heads_share_of_DE']:.2f} of it); their attention mass on T / W / P: {np.round(Dd['top_heads_mass_TWP'], 2).tolist()}.\n",
      "## 6. Part E: delivery depth\n", "Share delivered with the answer positions held clean through block B and free afterwards: " + ", ".join(f"B = {k}: {v:.3f}" for k, v in T["partE"]["depth_curve"].items()) + ".\n", "## 7. Interpretation, licensed / not licensed, next decision\n"]
_r = os.path.join(REP, f"two_hop_{STAGE}_reading.md"); L.append(open(_r).read() if os.path.exists(_r) else "_(hand-written; kept in `two_hop_" + STAGE + "_reading.md`)_\n")
open(os.path.join(REP, f"two_hop_{STAGE}.md"), "w").write("\n".join(L))
try:
    for _p in (os.path.join(R.PROJECT, ".claude", "skills", "iclr-plots", "scripts"), "/workspace/.claude/skills/iclr-plots/scripts"): sys.path.insert(0, _p)
    import iclrplot as ip; ip.setup(); fig, axes = ip.figure(width="full", nrows=2, ncols=2, aspect=0.62); axes = axes.ravel(); cat = ip.palette("categorical", 6)
except Exception:
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt; fig, axes = plt.subplots(2, 2, figsize=(5.5, 3.4)); axes = axes.ravel(); cat = ["C0", "C1", "C2", "C3", "C4", "C5"]; ip = None
def bars(ax, labs, vals, cis, cols, ylab):
    for i, (v, c_, col) in enumerate(zip(vals, cis, cols)):
        ax.bar(i, v, color=col, width=0.7)
        if c_ is not None: ax.errorbar(i, v, yerr=[[v - c_[0]], [c_[1] - v]], color="k", lw=0.8, capsize=2)
    ax.set_xticks(range(len(labs))); ax.set_xticklabels(labs, fontsize=5.5); ax.set_ylabel(ylab, fontsize=6.5); ax.axhline(0, color="k", lw=0.4)
v = T["partB"]["language_question"]; bars(axes[0], ["Country", "Language", "Country\n⊥ language", "Language\n⊥ country", "Random"], [v[k]["share"] for k in ("ctry", "lang", "ctry_perp", "lang_perp", "rand2b")], [v[k]["ci"] for k in ("ctry", "lang", "ctry_perp", "lang_perp", "rand2b")], [cat[1], cat[0], cat[1], cat[0], "#9e9e9e"], "Fraction of transfer push")
bars(axes[1], ["No clamp\n(R0)", "Readable\nspan (R_J)", "Fitted\nnon-lens (R_Φ)"], [A["R0"], A["R_J"], A["R_phi"]], [A["R0_ci"], A["R_J_ci"], A["R_phi_ci"]], [cat[3], cat[2], "#9e9e9e"], "Share, block-63 read cut")
bars(axes[2], ["Vocabulary\n25 installed", "Functional\n25 installed", "Functional\n25 removed", "Random\n25 removed"], [C["J25_install_stage2"], C["F25_install"], C["F25_complement"], C["R25_complement"]], [None, C["F25_install_ci"], None, None], [cat[0], cat[4], cat[4], "#9e9e9e"], "Share of the question-turn effect")
bars(axes[3], ["Cut T", "Cut W", "Cut P"], [Dd["removal"][X]["removed_fraction"] for X in "TWP"], [Dd["removal"][X]["ci"] for X in "TWP"], [cat[5], cat[1], cat[3]], "Fraction of last-layer delivery removed")
if ip is not None: ip.label_panels(axes, titles=["Cross-question planes", "Consumer route (read cut)", "Functional-row null", "Last-layer read by position"]); ip.finish(fig, os.path.join(FIG, f"h3_{STAGE}"))
else: fig.tight_layout(); fig.savefig(os.path.join(FIG, f"h3_{STAGE}.png"), dpi=200)
print(json.dumps({k: T[k] for k in ("gate_reproduction", "gate_L", "gate_writes_partB")}, default=str)[:1500]); print(json.dumps({"B": {k: (v["reading"], {kk: round(vv["share"], 3) for kk, vv in v.items() if isinstance(vv, dict) and "share" in vv}) for k, v in T["partB"].items() if isinstance(v, dict) and "reading" in v}, "A": {k: v for k, v in T["partA"].items()}, "C": T["partC"], "D": {k: v for k, v in T["partD"].items() if k not in ("head_DE_mean",)}, "E": T["partE"]}, default=str, indent=0)[:3000])
