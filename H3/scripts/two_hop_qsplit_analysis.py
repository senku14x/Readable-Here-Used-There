"""Analysis for two_hop_organism stage `qsplit` (Amendment 5): one scoring pass from raw_qsplit.npz + meta_qsplit.json to
H3/results/two_hop_qsplit_tables.json, H3/results/two_hop_qsplit.md (sections 1-4 generated, 5 left for the hand-written
reading) and H3/results/figures/h3_qsplit.png. Usage: two_hop_qsplit_analysis.py [stage]"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "..", "common", "scripts"))
import numpy as np
import registry as R

STAGE = sys.argv[1] if len(sys.argv) > 1 else "qsplit"
OUT = R.out_dir("H3", "outputs", "two_hop_organism"); RES = R.out_dir("H3", "results"); FIG = R.out_dir("H3", "results", "figures")
RAW = np.load(os.path.join(OUT, f"raw_{STAGE}.npz"), allow_pickle=True); META = json.load(open(os.path.join(OUT, f"meta_{STAGE}.json")))
cells = META["cells"]; names = list(dict.fromkeys(b.split("|")[0] for b in cells)); COLS = META["columns"]; dec = [COLS.index(d) for d in META["decoys"]]
CONDS = ["q_full_pre", "q_plane_pre", "q_rem_pre", "q_rand_pre", "q_rem_rand_pre", "int_q32"]
S0 = META["s_donor0_seq_bf16_quoted"]; RB = slice(51, 60)


def ci(v):
    from scipy import stats as st
    v = np.asarray(v, float); m = v.mean(); h = st.t.ppf(0.975, len(v) - 1) * v.std(ddof=1) / np.sqrt(len(v)) if len(v) > 1 else float("nan")
    return {"mean": float(m), "ci": [float(m - h), float(m + h)], "n_pos": int((v > 0).sum()), "n": int(len(v))}


byitem = lambda f: [float(np.mean([f(b) for b in cells if b.startswith(nm + "|")])) for nm in names]
mg = lambda b, c: float((RAW[f"{b}|{c}|seq_swap"] - RAW[f"{b}|{c}|seq_answer"]) - (RAW[f"{b}|clean|seq_swap"] - RAW[f"{b}|clean|seq_answer"]))
mgc = lambda b, c: float((RAW[f"{b}|{c}|s_swap"] - RAW[f"{b}|{c}|s_answer"]) - (RAW[f"{b}|clean|s_swap"] - RAW[f"{b}|clean|s_answer"]))
def pres(tag, w, key): z = RAW[f"{tag}|{key}"][RB].astype(np.float32).mean(axis=(0, 1)); return float(z[COLS.index(w)] - z[dec].mean())
def jshift(b, c, key="zq"): it = cells[b]; return (pres(f"{b}|{c}", it["swap_to"], key) - pres(f"{b}|{c}", it["intermediate"], key)) - (pres(f"{b}|clean", it["swap_to"], key) - pres(f"{b}|clean", it["intermediate"], key))
def c63(b, c): d = RAW[f"{b}|{c}|c63"].astype(np.float32).mean(0) - RAW[f"{b}|clean|c63"].astype(np.float32).mean(0); return [float(d[0]), float(d[1])]

T = {"stage": STAGE, "run_id": META["run_id"], "n_forwards": META["n_forwards"], "n_cells": len(cells), "n_items": len(names), "s_donor0_seq_bf16_quoted": S0}
# gates 1-2
T["gate1_q_token_equality"] = True   # asserted per cell in the battery
T["competence_clean32_seq"] = float(np.mean([RAW[f"{b}|clean|seq_answer"] > RAW[f"{b}|clean|seq_swap"] for b in cells]))
T["competence_donor32_seq"] = float(np.mean([RAW[f"{b}|donor|seq_swap"] > RAW[f"{b}|donor|seq_answer"] for b in cells]))
T["plane_degenerate_cells"] = [b for b in cells if cells[b]["plane_degenerate"]]
T["cos_int_swap_max_abs"] = float(max(cells[b]["cos_int_swap_max_abs"] for b in cells))
nd = np.stack([RAW[f"{b}|normdiag"] for b in cells]); T["norms_mean_over_cells_and_blocks"] = {"dh": float(nd[:, :, 0].mean()), "vJ": float(nd[:, :, 1].mean()), "vR": float(nd[:, :, 2].mean()), "vJ_over_dh": float((nd[:, :, 1] / nd[:, :, 0]).mean())}
rows = {}; full_mean = float(np.mean(byitem(lambda b: mg(b, "q_full_pre"))))
for c in CONDS:
    marg = byitem(lambda b: mg(b, c)); row = {"margin_seq": ci(marg), "share_of_q_full_pre": float(np.mean(marg) / full_mean), "share_of_S_donor0_bf16": float(np.mean(marg) / S0),
                                            "flips_seq": int(sum(RAW[f"{b}|{c}|seq_swap"] > RAW[f"{b}|{c}|seq_answer"] for b in cells)),
                                            "margin_candidate": ci(byitem(lambda b: mgc(b, c))), "flips_candidate": int(sum(RAW[f"{b}|{c}|s_swap"] > RAW[f"{b}|{c}|s_answer"] for b in cells)),
                                            "J_q_readout_shift_L51_59": ci(byitem(lambda b: jshift(b, c))), "J_qpre_readout_shift_L51_59": ci(byitem(lambda b: jshift(b, c, "zq_pre"))),
                                            "block63_plane_coord_shift_int_swap": ci(byitem(lambda b: c63(b, c)[1] - c63(b, c)[0])),
                                            "dNLL_max": float(max(RAW[f"{b}|{c}|nll"] - RAW[f"{b}|clean|nll"] for b in cells)), "per_item_margin": dict(zip(names, marg))}
    if c != "int_q32":
        row.update({"rho": float(np.mean([RAW[f"{b}|{c}|rho"] for b in cells])), "kappa": float(np.mean([RAW[f"{b}|{c}|kappa"] for b in cells])),
                    "readback_max": float(max(RAW[f"{b}|{c}|rberr"] for b in cells)), "plane_dev_max": float(max(RAW[f"{b}|{c}|plane_dev"] for b in cells))})
    rows[c] = row
T["rows"] = rows
A = rows["q_plane_pre"]["share_of_q_full_pre"]; B = rows["q_rem_pre"]["share_of_q_full_pre"]; RR = rows["q_rem_rand_pre"]["share_of_q_full_pre"]
T["A_plane_share"], T["B_rem_share"] = A, B
S = [rows["q_full_pre"]["per_item_margin"][nm] - rows["q_plane_pre"]["per_item_margin"][nm] - rows["q_rem_pre"]["per_item_margin"][nm] for nm in names]
T["additivity_S"] = ci(S); T["per_item_A"] = {nm: rows["q_plane_pre"]["per_item_margin"][nm] / rows["q_full_pre"]["per_item_margin"][nm] for nm in names}
T["per_item_B"] = {nm: rows["q_rem_pre"]["per_item_margin"][nm] / rows["q_full_pre"]["per_item_margin"][nm] for nm in names}
g4 = rows["q_full_pre"]["margin_seq"]; T["gate4"] = {"items_pos": g4["n_pos"], "mean": g4["mean"], "bar_0.3_S_donor0": 0.3 * S0, "pass": bool(g4["n_pos"] >= 10 and g4["mean"] >= 0.3 * S0)}
T["gate5"] = {"rand_share": rows["q_rand_pre"]["share_of_q_full_pre"], "rand_flips": rows["q_rand_pre"]["flips_seq"], "rem_rand_share": RR,
              "pass": bool(rows["q_rand_pre"]["share_of_q_full_pre"] <= 0.10 and rows["q_rand_pre"]["flips_seq"] <= 2 and RR >= 0.80)}
T["gate3"] = {"pass": bool(all(0.9 <= rows[c]["rho"] <= 1.1 and rows[c]["kappa"] >= 0.99 for c in CONDS if c != "int_q32"))}
T["gate2"] = {"pass": bool(T["competence_clean32_seq"] >= 0.9 and T["competence_donor32_seq"] >= 0.9)}
if A >= B and B <= 0.5: lab = "naming-plane dominant"
elif B >= 0.75 and A <= 0.35 and RR >= 0.80: lab = "complement dominant"
elif A >= 0.5 and B >= 0.5: lab = "redundant / non-additive"
elif A <= 0.35 and B <= 0.5: lab = "jointly necessary / sub-additive"
else: lab = "ambiguous"
T["P3_reading"] = lab if (T["gate4"]["pass"] and T["gate5"]["pass"]) else f"not read (gate failure): would be '{lab}'"
json.dump(T, open(os.path.join(RES, f"two_hop_{STAGE}_tables.json"), "w"), indent=1)

# ---- report
L = []
L.append(f"# two_hop_organism · stage `{STAGE}` — the H3.3 ladder at the question-turn cut (Amendment 5)\n")
L.append(f"Run `{META['run_id']}`, {META['n_forwards']} forwards, {META['elapsed_s']} s; Qwen3.6-27B, thinking off, **float32 residual from block {META['fp32_from']}** on every forward; "
         f"{len(cells)} cells ({len(names)} items × {len(META['carriers'])} carriers), cluster = item; writes at blocks {META['swap_layers'][0]}–{META['swap_layers'][1]} on `q_pre` (question turn, scoring position excluded); "
         f"sequence-log-prob endpoint (logsumexp over spellings). Design: `H3/design_specs/two_hop_organism.md` Amendment 5.\n")
L.append("## 1. Gates\n")
L.append(f"- Gate 1 (rendering, `q` token-id equality recipient/donor, scoring position excluded): asserted per cell in the battery.")
L.append(f"- Gate 2 (competence, sequence endpoint): clean32 {T['competence_clean32_seq']:.2f}, donor32 {T['competence_donor32_seq']:.2f} — {'PASS' if T['gate2']['pass'] else 'FAIL'}.")
L.append(f"- Gate 3 (realized writes): " + "; ".join(f"`{c}` ρ {rows[c]['rho']:.3f} κ {rows[c]['kappa']:.3f} read-back {rows[c]['readback_max']:.1e}" for c in CONDS if c != 'int_q32') + f" — {'PASS' if T['gate3']['pass'] else 'FAIL'}. ‖v_R‖ = ‖v_J‖ asserted per position.")
L.append(f"- Plane geometry: max |cos(a_int, a_swap)| over cells and blocks {T['cos_int_swap_max_abs']:.2f}; degenerate cells {T['plane_degenerate_cells'] or 'none'}. Mean norms over cells × blocks: ‖Δh‖ {T['norms_mean_over_cells_and_blocks']['dh']:.2f}, ‖v_J‖ {T['norms_mean_over_cells_and_blocks']['vJ']:.2f} ({100*T['norms_mean_over_cells_and_blocks']['vJ_over_dh']:.1f} % of ‖Δh‖).")
L.append(f"- Gate 4 (`q_full_pre` strong donorward): margin {g4['mean']:+.2f} nats, {g4['n_pos']}/{g4['n']} items > 0, bar ≥ {0.3*S0:.2f} (0.3 × S_donor0 bf16 {S0:.2f}) and ≥ 10/12 — **{'PASS' if T['gate4']['pass'] else 'FAIL'}**.")
L.append(f"- Gate 5 (controls): `q_rand_pre` share {T['gate5']['rand_share']:+.3f} (≤ 0.10), flips {T['gate5']['rand_flips']}/{len(cells)} (≤ 2); `q_rem_rand_pre` share {RR:+.3f} (≥ 0.80) — **{'PASS' if T['gate5']['pass'] else 'FAIL'}**.\n")
L.append("## 2. Main table (sequence endpoint; margin = log P(swap_answer) − log P(answer) minus clean32; item-clustered 95 % t-intervals)\n")
L.append("| condition | margin (nats) | 95 % CI | items > 0 | share of `q_full_pre` | share of S_donor0 (bf16, quoted) | flips | candidate-set margin | J_NP q-readout shift L51–59 | block-63 Δproj(a_swap) − Δproj(a_int) | ρ / κ | read-back max | ΔNLL max |")
L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for c in CONDS:
    r = rows[c]; m = r["margin_seq"]
    L.append(f"| `{c}` | {m['mean']:+.2f} | [{m['ci'][0]:+.2f}, {m['ci'][1]:+.2f}] | {m['n_pos']}/{m['n']} | {r['share_of_q_full_pre']:+.3f} | {r['share_of_S_donor0_bf16']:+.3f} | {r['flips_seq']}/{len(cells)} | {r['margin_candidate']['mean']:+.2f} | {r['J_q_readout_shift_L51_59']['mean']:+.2f} ({r['J_q_readout_shift_L51_59']['n_pos']}/{m['n']}) | {r['block63_plane_coord_shift_int_swap']['mean']:+.2f} | "
             + (f"{r['rho']:.3f} / {r['kappa']:.3f} | {r['readback_max']:.1e}" if c != 'int_q32' else "— | —") + f" | {r['dNLL_max']:+.4f} |")
L.append(f"\nAdditivity S = m(full) − m(plane) − m(rem): {T['additivity_S']['mean']:+.2f} nats [{T['additivity_S']['ci'][0]:+.2f}, {T['additivity_S']['ci'][1]:+.2f}], {T['additivity_S']['n_pos']}/{T['additivity_S']['n']} items > 0 (reported, not a partition).\n")
L.append("## 3. Per-item shares of `q_full_pre`\n")
L.append("| item | full margin | A = plane | B = complement | S |")
L.append("|---|---|---|---|---|")
for nm, s in zip(names, S):
    L.append(f"| {nm} | {rows['q_full_pre']['per_item_margin'][nm]:+.2f} | {T['per_item_A'][nm]:+.2f} | {T['per_item_B'][nm]:+.2f} | {s:+.2f} |")
L.append(f"\n## 4. P3 reading (thresholds fixed in Amendment 5 §5)\n\nA = {A:+.3f}, B = {B:+.3f}, `q_rem_rand_pre` = {RR:+.3f} → **{T['P3_reading']}**.\n")
L.append("Caveat beside the result: `q_rem_pre` removes the **two-token naming plane** of one counterfactual pair, not a k = 25 J-space reconstruction; the licensed comparison to the paper's Fig. 16 is \"the position-resolved analogue of the paper's split, restricted to the pair's naming plane\". "
         "Each row is a fixed state trajectory over blocks 36–62 at `q_pre` (the complement of the written component is held at its clean or donor value at every written block), so the rows are not a partition of one computation. The block-63 column is Δproj(a_swap) − Δproj(a_int) on the raw unit naming directions (identity transport, γ⊙w_v) at `q_pre` at the first free block after the sustained write, minus clean: the re-entry observation for `q_rem_pre`.\n")
L.append("## 5. Interpretation and next decision\n\n_(hand-written after reading the tables)_\n")
open(os.path.join(RES, f"two_hop_{STAGE}.md"), "w").write("\n".join(L))

# ---- figure from the tables only
try:
    for _p in ("/root/.claude/skills/iclr-plots/scripts", os.path.join(R.PROJECT, ".claude", "skills", "iclr-plots", "scripts"), "/workspace/.claude/skills/iclr-plots/scripts"):
        sys.path.insert(0, _p)
    import iclrplot as ip; ip.setup()
except Exception as e:
    print("iclrplot not used:", e)
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
labels = {"q_full_pre": "full residual", "q_plane_pre": "naming plane", "q_rem_pre": "complement\n(plane removed)", "q_rand_pre": "random plane", "q_rem_rand_pre": "complement of\nrandom plane", "int_q32": "coord. swap\n(paper-style)"}
fig, ax = plt.subplots(figsize=(5.5, 2.4))
ms = [rows[c]["margin_seq"]["mean"] for c in CONDS]; lo = [rows[c]["margin_seq"]["mean"] - rows[c]["margin_seq"]["ci"][0] for c in CONDS]; hi = [rows[c]["margin_seq"]["ci"][1] - rows[c]["margin_seq"]["mean"] for c in CONDS]
cols = ["#4c4c4c", "#1f77b4", "#d62728", "#9ecae1", "#f4a6a6", "#7f7f7f"]
ax.bar(range(len(CONDS)), ms, yerr=[lo, hi], color=cols, capsize=2, width=0.65)
for i, c in enumerate(CONDS):
    ax.scatter(np.full(len(names), i) + np.linspace(-0.18, 0.18, len(names)), [rows[c]["per_item_margin"][nm] for nm in names], s=6, color="k", alpha=0.5, zorder=3)
ax.axhline(0, color="k", lw=0.5); ax.set_xticks(range(len(CONDS))); ax.set_xticklabels([labels[c] for c in CONDS], fontsize=7)
ax.set_ylabel("Δ answer margin (nats)"); ax.set_title(f"Question-turn donor, scoring position excluded (blocks 36–62, fp32): plane A = {A:.2f}, complement B = {B:.2f}", fontsize=7)
fig.tight_layout(); fig.savefig(os.path.join(FIG, "h3_qsplit.png"), dpi=200); fig.savefig(os.path.join(FIG, "h3_qsplit.pdf"))
print(json.dumps({k: T[k] for k in ("competence_clean32_seq", "competence_donor32_seq", "gate3", "gate4", "gate5", "A_plane_share", "B_rem_share", "P3_reading")}, indent=1))
for c in CONDS: print(f"  [{c:15s}] seq margin {rows[c]['margin_seq']['mean']:+6.2f} [{rows[c]['margin_seq']['ci'][0]:+6.2f},{rows[c]['margin_seq']['ci'][1]:+6.2f}] ({rows[c]['margin_seq']['n_pos']}/{rows[c]['margin_seq']['n']}) share {rows[c]['share_of_q_full_pre']:+.3f} flips {rows[c]['flips_seq']} | Jq {rows[c]['J_q_readout_shift_L51_59']['mean']:+.2f} | c63 {rows[c]['block63_plane_coord_shift_int_swap']['mean']:+.2f}")
