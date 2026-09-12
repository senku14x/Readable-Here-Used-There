# H3 · computed_sum_consumer — `global` (Amendment 3) — run 20260909T134342Z

958 forwards (243.3 s); 8 sums × ['C0', 'C1', 'C2', 'C3'] × parity + report; donor map offset 3; cluster = sum (n=8); scored-argmax rule. Swap layers 36–62; masked full-attention blocks [3, 7, 11, 15, 19, 23, 27, 31, 35, 39, 43, 47, 51, 55, 59, 63].

**Gates.** Carrier ΔNLL max +0.0019; attention leak under the mask max 0.00e+00; mean realized swap norm per position 2.41; operand span untouched under carrier-only writes and prefix untouched under decision-position writes (asserted at generation).

## consumer `report`

| condition | behavioral margin (nats) | odds ratio | flips (scored) | greedy = own value (word or digit) | J_NP carrier sum shift L51–59 | RESID_P pair-axis shift | answer-pos distance L51–59 |
|---|---|---|---|---|---|---|---|
| O_donor36 | +21.211 [+19.911, +22.512] (8/8 >0) | ×1628681781.1 | 32/32 | 0/32 | +1.552 [+1.317, +1.787] (8/8 >0) | +0.762 [+0.582, +0.943] (8/8 >0) | 55.3 |
| O_donor0 | +21.578 [+20.185, +22.971] (8/8 >0) | ×2350461763.1 | 32/32 | 0/32 | +1.610 [+1.437, +1.783] (8/8 >0) | +0.678 [+0.507, +0.848] (8/8 >0) | 56.8 |
| C_full | +1.751 [+1.169, +2.334] (8/8 >0) | ×5.8 | 0/32 | 26/32 | +1.616 [+1.426, +1.806] (8/8 >0) | +0.679 [+0.500, +0.858] (8/8 >0) | 7.7 |
| G_full | +21.273 [+19.944, +22.601] (8/8 >0) | ×1732271131.5 | 32/32 | 0/32 | +1.616 [+1.426, +1.806] (8/8 >0) | +0.679 [+0.500, +0.858] (8/8 >0) | 55.7 |
| G_swap_all | +11.067 [+7.995, +14.139] (8/8 >0) | ×64015.6 | 16/32 | 14/32 | +0.924 [-0.170, +2.018] (5/8 >0) | +0.275 [-0.190, +0.741] (5/8 >0) | 11.7 |
| G_swap_carrier | +0.348 [+0.208, +0.489] (8/8 >0) | ×1.4 | 0/32 | 25/32 | +0.926 [-0.194, +2.046] (5/8 >0) | +0.279 [-0.207, +0.766] (5/8 >0) | 2.4 |
| D_band | +0.724 [+0.456, +0.992] (8/8 >0) | ×2.1 | 0/32 | 25/32 | +0.000 [+0.000, +0.000] (0/8 >0) | +0.000 [+0.000, +0.000] (0/8 >0) | 17.0 |
| D_band_early | +0.379 [+0.085, +0.673] (6/8 >0) | ×1.5 | 0/32 | 25/32 | +0.000 [+0.000, +0.000] (0/8 >0) | +0.000 [+0.000, +0.000] (0/8 >0) | 11.6 |
| mask_clean | +6.680 [+4.518, +8.842] (8/8 >0) | ×796.3 | 1/32 | 15/32 | +0.000 [+0.000, +0.000] (0/8 >0) | +0.000 [+0.000, +0.000] (0/8 >0) | 71.0 |
| mask_C_full | +11.632 [+9.145, +14.118] (8/8 >0) | ×112612.8 | 10/32 | 6/32 | +1.616 [+1.426, +1.806] (8/8 >0) | +0.679 [+0.500, +0.858] (8/8 >0) | 74.1 |
| mask_O_donor36 | +14.134 [+11.499, +16.769] (8/8 >0) | ×1375246.2 | 21/32 | 1/32 | +1.552 [+1.317, +1.787] (8/8 >0) | +0.762 [+0.582, +0.943] (8/8 >0) | 74.8 |

Mask competence gate (`mask_clean`): greedy = own value 15/32; scored-argmax = own 22/32 (gate ≥ 0.9 → FAIL — mask rows are uninterpretable as use tests and are reported as observations).

## consumer `parity`

| condition | behavioral margin (nats) | odds ratio | flips (scored) | greedy = own value (word or digit) | J_NP carrier sum shift L51–59 | RESID_P pair-axis shift | answer-pos distance L51–59 |
|---|---|---|---|---|---|---|---|
| O_donor36 | +3.880 [+2.982, +4.778] (8/8 >0) | ×48.4 | 23/32 | 11/32 | +1.562 [+1.320, +1.805] (8/8 >0) | +0.762 [+0.585, +0.939] (8/8 >0) | 57.2 |
| O_donor0 | +6.791 [+6.163, +7.420] (8/8 >0) | ×890.0 | 32/32 | 0/32 | +1.631 [+1.425, +1.837] (8/8 >0) | +0.693 [+0.514, +0.872] (8/8 >0) | 75.1 |
| C_full | +0.702 [+0.188, +1.215] (8/8 >0) | ×2.0 | 0/32 | 30/32 | +1.615 [+1.433, +1.797] (8/8 >0) | +0.691 [+0.534, +0.849] (8/8 >0) | 12.8 |
| G_full | +4.150 [+3.264, +5.035] (8/8 >0) | ×63.4 | 24/32 | 7/32 | +1.615 [+1.433, +1.797] (8/8 >0) | +0.691 [+0.534, +0.849] (8/8 >0) | 59.0 |
| G_swap_all | +0.218 [-0.162, +0.598] (5/8 >0) | ×1.2 | 0/32 | 32/32 | +0.925 [-0.170, +2.021] (5/8 >0) | +0.277 [-0.191, +0.745] (5/8 >0) | 10.2 |
| G_swap_carrier | +0.038 [-0.007, +0.082] (6/8 >0) | ×1.0 | 0/32 | 32/32 | +0.925 [-0.196, +2.047] (5/8 >0) | +0.286 [-0.204, +0.776] (5/8 >0) | 2.6 |
| D_band | +4.050 [+2.844, +5.256] (8/8 >0) | ×57.4 | 21/32 | 10/32 | +0.000 [+0.000, +0.000] (0/8 >0) | +0.000 [+0.000, +0.000] (0/8 >0) | 51.9 |
| D_band_early | +3.625 [+2.415, +4.835] (8/8 >0) | ×37.5 | 16/32 | 13/32 | +0.000 [+0.000, +0.000] (0/8 >0) | +0.000 [+0.000, +0.000] (0/8 >0) | 50.5 |
| mask_clean | +2.222 [+1.820, +2.625] (8/8 >0) | ×9.2 | 3/32 | 27/32 | +0.000 [+0.000, +0.000] (0/8 >0) | +0.000 [+0.000, +0.000] (0/8 >0) | 52.1 |
| mask_C_full | +3.419 [+2.800, +4.038] (8/8 >0) | ×30.5 | 17/32 | 14/32 | +1.615 [+1.433, +1.797] (8/8 >0) | +0.691 [+0.534, +0.849] (8/8 >0) | 57.2 |
| mask_O_donor36 | +3.571 [+2.757, +4.385] (8/8 >0) | ×35.6 | 18/32 | 13/32 | +1.562 [+1.320, +1.805] (8/8 >0) | +0.762 [+0.585, +0.939] (8/8 >0) | 59.4 |

Mask competence gate (`mask_clean`): greedy = own value 27/32; scored-argmax = own 29/32 (gate ≥ 0.9 → PASS).

## Interpretation

Registered predictions (design spec, Amendment 3) against outcome, all carriers pooled, cluster = sum:

1. **Token-level operand control — met.** `O_donor0` (all 64 blocks, equivalent to changing the operand tokens) equals `O_donor36` on report (+21.6 vs +21.2 nats, 32/32 both). The late operand residuals carry what the tokens carry; "operand positions" can be read as "operands" for the report consumer. On parity the token-level change is stronger (+6.8, 32/32 vs +3.9, 23/32): the block-≥36 operand residuals carry somewhat less of what the parity consumer uses than the tokens do.
2. **Consistent global clamp — met on flips, additivity not observed.** `G_full` (operands + carrier) flips 32/32 at +21.3 nats, indistinguishable from `O_donor36` (+21.2) on report, where the margin is saturated (P(donor) ≈ 1); on parity `G_full` − `O_donor36` = +0.27 against the carrier-only +0.70. So in the consistent state the carrier's marginal contribution is at most what it is in the conflicting state. This bounds the conflict objection (donor carrier + recipient operands is an unnatural pairing) rather than removing it: no condition can present the donor sum in the carrier with no source at all.
3. **Paper-style coordinate swap — met on report, with a caveat the parity consumer exposes.** Swapping the two sum-word naming coordinates at every position from the operands onward, layers 36–62, moves the report margin +11.1 nats and flips 16/32 (the paper's two-hop swaps: 54–70 %); confined to the carrier it does +0.35 and 0/32. The split between global and carrier-only holds for the paper's own intervention type. But the same global swap leaves **parity** untouched (+0.22, CI includes 0, 0/32) while the full-residual `O_donor36` flips parity 23/32. A swap along the answer-word directions applied through the decision positions moves the consumer that *emits those words* and not the consumer that computes a different function of the same value. The report flips under `G_swap_all` are therefore consistent with steering of the answer token rather than substitution of the computed sum; the parity null is the control that shows it.
4. **Decision-position donor — met for parity, not for report.** Writing the donor's decision-position states at blocks 36–50 (carrier and operands untouched) flips parity 21/32 at +4.1 nats, the `O_donor36` level, and 16/32 from blocks 36–43; report moves +0.7 and flips 0/32. The parity answer is fixed in the decision-position residuals by block 50; the report answer is not (the sum word surfaces later). As registered, this bounds where a full donor works and identifies no mechanism: the donor's decision-position states were produced by a run with donor operands and already encode the donor answer.
5. **Route restriction — report gate fails; parity gate passes and gives the first "consulted more when the direct read is closed" signal, with caveats.** With every full-attention block's consumer→operand attention masked (leak exactly 0), the report consumer loses competence (scored 22/32, greedy 15/32, and it drifts to digits), so its mask rows are observations only. Parity stays competent (29/32 scored) but less confident: the masked clean baseline already moves +2.2 nats toward the opposite parity. Against that baseline, the carrier-only donor adds +1.2 nats and 14 flips (`mask_C_full` +3.42, 17/32) — versus +0.70 and 0 flips unmasked — and the operand donor through the remaining routes (GatedDeltaNet state, and the carrier it feeds) adds +1.35 and 15 flips (`mask_O_donor36` +3.57, 18/32). So once the consumer cannot attend the operands directly, the carrier copy's influence rises to the level of the operand donor's remaining influence. The flip counts are inflated by the less confident masked baseline; the margin differences (+1.2 vs +1.35 vs +0.70) are the statistic to quote. The mask itself perturbs the answer position heavily (distance 52–74 against 5–13 for the carrier writes), so this is a strong, unnatural regime and the recurrent channel remains open.
6. **Damage — met.** Carrier ΔNLL max +0.002; operand span and prefix asserted untouched where required.

**What changes.** (i) The "operand positions vs raw operands" objection is closed for report (prediction 1). (ii) The bridge to the paper is now concrete: the paper's clamped coordinate swap reproduces here when it spans the source and decision positions and not when confined to the carrier; and its success on the sum-word consumer, with a null on parity, is consistent with answer-token steering, which the paper's designs (report the item, name the capital) cannot separate from substitution of the latent. (iii) The decision-position result says the parity answer is settled in the decision-position residuals by block 50, which is where a representation ladder should be run. (iv) The masked parity rows are the first evidence in the direction of "consulted when needed", at the size of the remaining operand route, under a degraded baseline; they do not establish it. Scope unchanged: one model (hybrid), thinking off, 8 sums, 4 carriers, one donor map here.