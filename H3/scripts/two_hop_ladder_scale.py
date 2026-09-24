"""Scale and attribution arithmetic for the frozen question-turn ladder write-up (H3/results/reports/two_hop_question_turn_ladder.md).
No model forwards: reads only committed raw arrays and tables, and writes H3/results/tables/two_hop_ladder_scale.json.

1. Same-item denominator. Stage 2 (Amendment 7) scored the natural donor rendering (the recipient prompt with the donor's clue, run
   in the same float32-from-block-35 regime, same geometry, same sequence endpoint) in every cell. Its margin, computed with the
   analysis scripts' own margin function, is the whole effect of the clue swap on the same 35 admitted items. The ladder rows
   (question-turn full donor, last-layer-only row, consumer-clamp survivor, planes, J25) are divided by it as ratios of item means,
   with item-cluster bootstrap intervals (2 000 resamples, seed 20260907, percentile), the project's convention.
2. Construct check. On the 12 released items shared with Amendment 4 (`bridgeswap_seq`, bf16), the natural donor rendering is
   compared item by item with the full-residual reference S_donor0 (the donor's clue-span residual written at every block output).
3. Cross-run ratio. The earlier cross-run comparison (35-item rows over the 12-item S_donor0 mean) is recomputed for reference.
4. Endpoints of Amendment 4. First-token and sequence-endpoint shares of every bridgeswap row, from its committed table.
5. Head attribution arithmetic. Positive total, negative total and net of Amendment 10 Part D's linearised first-token direct-effect
   attribution per block-63 head, from the committed probe5 table.
Usage: two_hop_ladder_scale.py"""
import os, json
import numpy as np
from scipy import stats as st

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT = os.path.join(ROOT, "H3", "outputs", "two_hop_organism"); TAB = os.path.join(ROOT, "H3", "results", "tables")
B_BOOT, SEED_BOOT = 2000, 20260907
S0_SEQ = 23.87764283021291          # bridgeswap_seq ceiling (meta_bridgeswap_seq.json; quoted as s_donor0_seq_bf16_quoted in Stage 2)

S2 = np.load(os.path.join(OUT, "raw_stage2.npz"), allow_pickle=True); M2 = json.load(open(os.path.join(OUT, "meta_stage2.json")))
P4 = np.load(os.path.join(OUT, "raw_probe4.npz"), allow_pickle=True); M4 = json.load(open(os.path.join(OUT, "meta_probe4.json")))
BS = np.load(os.path.join(OUT, "raw_bridgeswap_seq.npz"), allow_pickle=True); MB = json.load(open(os.path.join(OUT, "meta_bridgeswap_seq.json")))
T2 = json.load(open(os.path.join(TAB, "two_hop_stage2_tables.json"))); T5 = json.load(open(os.path.join(TAB, "two_hop_probe5_tables.json")))
TB = json.load(open(os.path.join(TAB, "two_hop_bridgeswap_tables.json")))
adm = T2["admitted"]


def ci(v):
    v = np.asarray(v, float); m = float(v.mean()); h = float(st.t.ppf(0.975, len(v) - 1) * v.std(ddof=1) / np.sqrt(len(v)))
    return {"mean": m, "ci": [m - h, m + h], "n_pos": int((v > 0).sum()), "n": len(v)}


def ratio(num, den):
    rng = np.random.default_rng(SEED_BOOT); n = len(num); bs = []
    for _ in range(B_BOOT):
        i = rng.integers(0, n, n); bs.append(num[i].mean() / den[i].mean())
    return {"ratio_of_means": float(num.mean() / den.mean()), "ci": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]}


def mg(R_, b, row, base="clean"):
    """sequence-endpoint margin (swap - answer) of `row` minus that of `base`, as in the stage analysis scripts."""
    return float((R_[f"{b}|{row}|seq_swap"] - R_[f"{b}|{row}|seq_answer"]) - (R_[f"{b}|{base}|seq_swap"] - R_[f"{b}|{base}|seq_answer"]))


def byitem(cells, names, f):
    return np.array([np.mean([f(b) for b in cells if b.split("|")[0] == nm]) for nm in names])


c2, c4, cb = list(M2["cells"]), list(M4["cells_ab"]), list(MB["cells"])
assert sorted(dict.fromkeys(b.split("|")[0] for b in c4)) == sorted(adm), "probe4 item set differs from the Stage 2 admitted set"
nat = byitem(c2, adm, lambda b: mg(S2, b, "donor")); nat4 = byitem(c4, adm, lambda b: mg(P4, b, "donor"))
rows = {"q_full_pre": byitem(c2, adm, lambda b: mg(S2, b, "q_full_pre")),
        "q_full_pre_sfullA (last-layer-only row, whole question-turn change)": byitem(c4, adm, lambda b: mg(P4, b, "q_full_pre_sfullA")),
        "q_J25rem_pre_ccsA (consumer-clamp survivor)": byitem(c4, adm, lambda b: mg(P4, b, "q_J25rem_pre_ccsA")),
        "q_J25_pre (best 25 vocabulary directions installed)": byitem(c2, adm, lambda b: mg(S2, b, "q_J25_pre")),
        "q_ansplane_pre (answer plane installed)": byitem(c2, adm, lambda b: mg(S2, b, "q_ansplane_pre")),
        "q_plane_pre (intermediate plane installed)": byitem(c2, adm, lambda b: mg(S2, b, "q_plane_pre"))}
qf4 = byitem(c4, adm, lambda b: mg(P4, b, "q_full_pre"))
T = {"note": "no model forwards; ratios of item means over the 35 admitted items; item-cluster bootstrap 2000 resamples, seed 20260907, percentile",
     "denominator": {"natural_donor_rendering_margin_stage2": ci(nat), "natural_donor_rendering_margin_probe4_reproduction": ci(nat4),
                     "max_abs_item_difference_stage2_vs_probe4": float(np.abs(nat - nat4).max()),
                     "per_item_q_full_pre_over_natural": {"median": float(np.median(rows["q_full_pre"] / nat)), "min": float((rows["q_full_pre"] / nat).min()), "max": float((rows["q_full_pre"] / nat).max())}},
     "rows_nats": {k: ci(v) for k, v in rows.items()},
     "q_full_pre_probe4_max_abs_item_difference_vs_stage2": float(np.abs(qf4 - rows["q_full_pre"]).max()),
     "same_item_share_of_natural_clue_swap_effect": {k: ratio(v, nat) for k, v in rows.items()},
     "share_of_question_turn_effect_last_layer_only": ratio(rows["q_full_pre_sfullA (last-layer-only row, whole question-turn change)"], qf4),
     "cross_run_ratio_over_12_item_S_donor0_seq": {k: float(v.mean() / S0_SEQ) for k, v in rows.items()}}
shared = [nm for nm in dict.fromkeys(b.split("|")[0] for b in cb) if any(b.split("|")[0] == nm for b in c2)]
s0 = byitem(cb, shared, lambda b: mg(BS, b, "S_donor0")); natS = byitem(c2, shared, lambda b: mg(S2, b, "donor"))
T["construct_check_12_released_items"] = {"n_items": len(shared), "S_donor0_seq_bf16": ci(s0), "natural_donor_rendering_fp32": ci(natS),
                                          "natural_minus_S_donor0": ci(natS - s0), "max_abs_item_difference": float(np.abs(natS - s0).max())}
T["bridgeswap_endpoints"] = {c: {"first_token_share": TB[c]["share"]["mean"], "first_token_ci": TB[c]["share"]["ci"],
                                 "sequence_share": TB[c]["seq"]["share"]["mean"], "sequence_ci": TB[c]["seq"]["share"]["ci"], "sequence_flips": TB[c]["seq"]["flips"]}
                             for c in TB if c != "_meta"}
de = np.array(T5["partD"]["head_DE_mean"], float)
T["head_attribution_probe5_partD"] = {"method": "linearised first-token direct effect of each block-63 head's output change at s under q_full_pre_sfullA vs clean (Amendment 10 registration note 4); not a causal ablation",
                                      "head_22": float(de[22]), "head_21": float(de[21]), "positive_total": float(de[de > 0].sum()), "negative_total": float(de[de < 0].sum()),
                                      "net_sum": float(de.sum()), "head_22_share_of_positive_total": float(de[22] / de[de > 0].sum()), "head_22_share_of_net": float(de[22] / de.sum()),
                                      "top_positive_heads": [[int(h), float(de[h])] for h in np.argsort(-de)[:5]], "top_negative_heads": [[int(h), float(de[h])] for h in np.argsort(de)[:3]]}
json.dump(T, open(os.path.join(TAB, "two_hop_ladder_scale.json"), "w"), indent=1)
print(json.dumps({"natural": T["denominator"]["natural_donor_rendering_margin_stage2"], "same_item": {k: [round(v["ratio_of_means"], 3), [round(x, 3) for x in v["ci"]]] for k, v in T["same_item_share_of_natural_clue_swap_effect"].items()},
                  "construct_check": T["construct_check_12_released_items"]["natural_minus_S_donor0"], "heads": {k: v for k, v in T["head_attribution_probe5_partD"].items() if k != "method"}}, indent=1))
