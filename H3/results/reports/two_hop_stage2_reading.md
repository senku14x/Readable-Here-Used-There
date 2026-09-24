_Hand-written 2026-09-24 after reading the tables (`two_hop_stage2_tables.json`), the admission table, the screen and the six seeded cells. Numbers are copied from §1–7 or from the tables; the cluster-bootstrap intervals on shares (`common/scripts/stats.ratio_of_means`, 2 000 resamples of items) and the item-level difference for the current-base row are the only quantities computed here, on the same raw arrays, and are marked as such._

### 8.1 The six seeded cells, read by hand

- **Naples–Barcelona, C2 and C3** (admitted; clean gaps 10.0 and 10.2 nats). Full question-turn donor +11.4 / +9.9, crossing in C2 (greedy `Madrid`) and not in C3; intermediate plane +3.0 / +1.9; complement +8.8 / +7.6; answer-plane complement +8.0 / +6.1; J25 complement +8.9 / +6.9, which the consumer clamp takes to +5.4 / +4.8 (−3.5 and −2.1 nats, the largest clamp effects of the six), random-k clamp +8.7 / +6.8. The span pinned at s at L59 is ` Spain`, ` Barcelona`, ` PSOE`, ` Cataluña`, ` span`, plus ` MAD`: mostly the intermediate and its associates.
- **Cairo, C1** (not admitted: the answer swap beats the intermediate swap at mid depth). Every number is identical to the same cell in Stage 1 (full +12.19, plane +5.32, J25 complement +6.43 → +4.48 clamped): the fp32 regime reproduces across runs to the printed precision. Pinned span: ` Russian`, ` روسيا`, `莫斯科`, ` Rus`, ` Slav`, ` بوتين`.
- **Mumbai–Salzburg, C0** (admitted; gap 13.5; clean greedy `New`, the first token of New Delhi). Full +13.3; intermediate plane +1.3; answer plane +5.1; J25 complement +4.8, clamped +4.6 (−0.25): here removing the 25 atoms on `q_pre` already takes the effect to 0.36 of full and the clamp adds almost nothing. Pinned span: ` Vienna`, ` Salz`, ` Austrian`, `Wi`, ` Inns`, ` Vien` — the answer in pieces, the intermediate's adjective and the donor's own cue.
- **Osaka–Rotterdam, C1** (not admitted; the answer is the intermediate's adjective). Full +14.8 (crosses to `D`utch); J25 complement +11.5, clamped +11.0 (−0.5) although the pinned span is `荷兰` (Netherlands), ` Rotterdam`, ` Dut`, ` Flem`, ` Holland`: pinning the donor's J-readable Netherlands/Dutch content at the answer position barely moves this item.
- **Tagus–Tiber, C0** (admitted; gap 10.4; river template, constructed donor). Full +9.3; plane +1.6; J25 complement +5.2 → +4.2 clamped (−1.0). Pinned span: `罗马` (Rome), ` Italy`, ` Rome`, then junk (`常州市`, `�`, `财务会计`).

What the six say beyond the means. (i) Every effect is still an additive margin shift: three of the six full rows cross (Naples–Barcelona C2, Cairo, Osaka–Rotterdam), and no clamped row does (1/140 over the admitted set). (ii) The consumer clamp's effect ranges from −0.25 to −3.5 nats across cells whose pinned spans all name the intermediate or the answer, so how much the clamp removes is not predicted by whether the span looks like content. (iii) Constructed-donor cells behave like released-donor cells.

### 8.2 The registered decision rule

Rule (Amendment 6 §6, verbatim; applied to the admitted set per Amendment 7 §5): consumer-clamped complement share ≥ 0.5 at k = 25 → a non-J channel carries most of this consumer's margin; ≤ 0.2 → the complement was J-mediated at the consumer; otherwise → report the share(k) curve. Conditions: gates 1–5 pass, 35 items over 6 relation types admitted with competence 1.00, and the random-k clamp control (0.608) lies inside the un-clamped row's interval — all met.

Value: **0.511** (5.71 of 11.16 nats). Cluster-bootstrap interval **[0.474, 0.550]** (computed here); per-item median 0.52, 21 of 35 items ≥ 0.5, range 0.31–0.77; all 42 items 0.513. **The rule's output is its first branch.** Two facts, both recorded before this run, bound what that output licenses:

1. The clamp is partial. Under `q_J25rem_pre_cc` the intermediate and answer readouts at s are +1.49 and +1.32 (un-clamped +2.67 / +2.45; full donor +5.80 / +5.38). Per the researcher's note of 2026-09-24 the `_cc` shares are upper bounds on any non-J route. The rule's condition is therefore met by an upper bound, not by the quantity the rule names.
2. The threshold is inside the interval, and Stage 1's twelve items gave 0.466 (the middle branch). The quantity sits at the rule's boundary in both runs.

So the licensed reading of the rule's output is: **at most about half** of the question-turn effect can reach the answer by a route that is not J-readable at the consumer; the partial clamp cannot tell whether the true figure is near half or much lower. The first branch is recorded as the rule's output and is not upgraded to a finding. The registered qualifier does not fire as written (answer-class atoms are 2 % of the J_25 norm on `q_pre`; B_ans = 0.62 > 0.5), but the leading alternative stands beside the rule, stronger than in Stage 1 because it now holds in every item and every relation type (8.4).

### 8.3 Generality: the Stage 1 pattern on 35 items over six relation types

All four registered generality predictions hold (Amendment 7 P3). Admitted set, shares of `q_full_pre` (+11.16 nats [+10.53, +11.80], 35/35 items, 50/140 flips), cluster-bootstrap intervals where given:

| k | J_k installed | J_k complement | + consumer clamp | random-k complement |
|---|---|---|---|---|
| 2 | 0.297 | 0.730 | 0.578 | 0.983 |
| 8 | 0.372 | 0.638 | 0.520 | 0.970 |
| 25 | 0.390 | 0.612 [0.574, 0.651] | 0.511 [0.474, 0.550] | 0.957 |
| 64 | 0.392 | 0.608 | 0.514 [0.478, 0.553] | 0.947 |

Stage 1 on its twelve items: complement 0.72 / 0.62 / 0.60 / 0.59, clamped 0.52 / 0.47 / 0.47 / 0.47. Every k-sweep row moves the answer donorward in 35/35 items. The clamp's own effect is positive in 35/35 items at k = 2 and 8 and in 34/35 at k = 25 and 64. The J part saturates at k = 25 (0.39 installed, 0.27–0.29 of ‖Δh‖) and is strongly privileged per dimension: 25 atoms carry 0.39 of the effect where 25 norm-matched random directions carry 0.04. Additivity holds for the J_25 split (S = −0.02 [−0.55, +0.51]). The 42-item numbers differ from the admitted ones by ≤ 0.03 on every share, so admission changes nothing in the pooled result.

Per relation type (admitted items; each type has 3–11 items, so these are descriptive): the clamped J25 complement is 0.51 for city→capital (11 items), 0.49 for language→capital (8), 0.54 for river→capital (6), **0.62 for city→currency** (6) and **0.33 for the three admitted city→language items**. Currency items carry the least readable leverage (intermediate plane 0.10, answer plane 0.25, complement 0.92); language items the most (0.34, 0.65, 0.63), and they are the demonym items whose intermediate and answer coincide as concepts. The screen flagged no relation (leave-one-out residual fractions 0.94–1.00 against mismatched-pair nulls at 1.00–1.04; the food items could not be screened with two pairs), so no relation's pattern is explained by an affine map from the intermediate's unembedding row to the answer's; the screen has little power at 10–22 pairs.

### 8.4 Answer plane versus intermediate plane

Answer plane **0.373 [0.330, 0.418]** against intermediate plane **0.186 [0.154, 0.227]**; difference +2.08 nats [+1.63, +2.54], **35/35 items**, at a slightly smaller norm (0.154 vs 0.171 of ‖Δh‖ at L51–59). It holds in every relation type (city→capital 0.38 vs 0.18, language→capital 0.31 vs 0.13, river→capital 0.41 vs 0.28, city→currency 0.25 vs 0.10, city→language 0.65 vs 0.34, the butter item 0.52 vs 0.23). Removing the few answer-class atoms among 25 costs 0.11 of the effect, the intermediate-class ones 0.04. At the question turn, the J-readable leverage is the answer's more than the intermediate's, in all six kinds of fact tested. That keeps "the answer is already computed and J-readable at the question turn" as the leading alternative to a non-J channel for the half that survives the clamp.

### 8.5 The repaired current-base row

Construction check passes (‖h' − h_clean‖/‖Δh‖ ≤ 1.009 at every block and position; mean 0.988; the failed additive form of Stage 1 overshot 6.5–9×). With the complement replaced by the donor's and the two plane coordinates left free, the share is **0.846 [0.820, 0.870]** against 0.795 [0.754, 0.829] with the plane pinned: **+0.57 nats [+0.36, +0.78] (computed here), 35/35 items**, 18 vs 16 flips. The free plane coordinate rebuilds toward the donor's: a norm-weighted projection of 0.16–0.22 of the donor's plane coordinate over blocks 41–50, 0.16–0.37 over 51–60 with the peak at block 58, and 0.19 at block 62; the intermediate readout on `q_pre` reaches +0.78 (pinned −0.01, full +3.09) and the block-63 re-entry +1.57 (pinned −0.42, full +14.31). The registered criterion for re-scoping B (rebuilt coordinate ≥ 0.5 by block 62) is not met, so **B = 0.79 stands as registered**. The recorded qualification: pinning the plane costs about 0.05 of the effect in every item, because the complement regenerates about a fifth of the intermediate's readable coordinate inside the band.

### 8.6 Admission

42/42 items are competent in all four carriers; 35/42 pass the mid-depth test (the intermediate swap at blocks 36–50 on the tail positions moves the answer more than the answer swap). Five of the seven failures are city→language items: four whose answer is the intermediate's own adjective (Danish, Norwegian, Italian, Japanese) and Cairo/Arabic; the others are the released Osaka capital item and honey→bee. On the twelve released items this is 9/12, against Amendment 4's full-band result where the answer swap was larger in aggregate: the intermediate is the more effective handle at mid depth and the answer at full depth, consistent with the ordering a two-step computation predicts. This is the admission test, not a separately registered claim.

### 8.7 The dictionary

Unchanged from Stage 1. The k = 2 pursuit contains the exact intermediate or swap_to atom in 4.1 % of L51–59 cells (never both). Junk dominates the pooled selection (`\n\n`, end-of-text, digits). At the two informative positions the top-25 atoms are 2.2 / 4.1 / 7.5 % (last `q_pre`) and 3.9 / 7.5 / 14.1 % (s) entity content by the frozen classes / with back-translations / with unembedding associates (coefficient-weighted up to 22.5 % at s), against 1.1 % pooled; the translation rule recovers `意大利`, ` япон`, `土耳其`, `英国`, `法国`, `巴黎`, `埃及`, `欧元区`, and the associates rule `€`, `£`, `英镑`, ` Greenland`, ` Wales`. The J part beats covariance-matched random directions in energy at k ≤ 25 (24–27 of 27 blocks) and not at k = 64 (8 of 27): P7 fails at 64 again. Early stops: 19 of about 122 000 pursuit vectors. KKT: 127 008 of 127 008 fits pass without fallback.

### 8.8 Licensed

1. **Generality.** On 35 admitted items over six relation types (constructed donors for 26 of them), the question-turn state's answer effect is carried mostly outside the span of the best k J_NP atoms: the complement keeps 0.73 / 0.64 / 0.61 / 0.61 at k = 2 / 8 / 25 / 64 (35/35 items at every k) against 0.95–0.98 for norm- and rank-matched random directions. The Stage 1 numbers were not a property of its twelve items.
2. **Consumer clamp, intermediate plane.** Pinning the intermediate's plane at clean at the answer position removes 0.036 (+0.41 nats [+0.27, +0.54], 35/35; control +0.01) while holding the intermediate readout there at −0.07.
3. **Consumer clamp, k atoms.** Pinning the k-atom span of the donor's Δh at s removes 0.09–0.15 (34–35/35; random-k controls ≤ 0.10 nats) and leaves 0.51 at k = 25, an upper bound on any non-J route because the readouts at s stay at +1.3 to +1.5.
4. **Answer plane.** 0.37 vs 0.19 for the intermediate plane, 35/35 items, every relation type.
5. **Current base.** Freeing the plane raises the complement's share by about 0.05 (35/35) and rebuilds about a fifth of the donor's plane coordinate by block 62; B stands as registered.
6. **Regime.** Exact writes and clamps (ρ = κ = 1.000, read-back 0, control norms within 0.02 %), construction check ≤ 1.009, the twelve released items reproduce Stage 1 to the second decimal, and a re-run cell reproduces identically.

### 8.9 Not licensed

- "A non-J channel carries most of the consumer's margin" as a finding: it is the rule's output on an upper bound whose interval contains the threshold (8.2).
- "Outside the J-space" or "outside the workspace": the dictionary is at noise level by 64 atoms; the licensed phrase remains "not in the span of the atoms this dictionary selects".
- "The readable intermediate is unused": 0.19 on `q_pre` and 0.04 at s, privileged per unit norm, not zero.
- Relation-level claims beyond description: 3–11 items per type, and the admitted language items are three demonym items.
- Anything beyond one hybrid model, thinking off, one question wording, same-template minimal-pair donors, and fixed state trajectories.

### 8.10 What it means for the H3 statement, in one paragraph

Across 35 two-hop items of six kinds, the question-turn state's effect on the answer is mostly not carried by the coordinates a J_NP vocabulary dictionary names: removing the best 25–64 atoms on the question tokens keeps 0.61 of the effect against 0.95 for random directions of the same size, and additionally pinning the same span at the answer position keeps 0.51. The readable part that matters is more the answer's naming directions (0.37) than the intermediate's (0.19), in every item, and the intermediate's readable coordinates at the answer position carry 0.04. At most about half of the effect can travel by a route that is not J-readable at the consumer; how much less cannot be told from a partial clamp. On the *what* axis, as on the *where* axis, readability of the intermediate is a poor proxy for how the answer is produced; the verbalizable representation is causally connected and privileged, not the main channel, in this organism.

### 8.11 Next decision

Amendment 8 is the discriminating experiment and is registered, not run. Its stronger clamp is verified by the readouts at s falling to ≈ 0, which removes the upper-bound caveat that decides 8.2. Its joint-plane removal and relation-transfer rows test the answer-precomputed alternative that 8.4 makes the leading one. It runs on the researcher's go, on the admitted items and the seven registered city pairs.
