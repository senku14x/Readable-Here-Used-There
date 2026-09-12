# H3 · `recompute_cost_ladder` — is the carrier copy used more when recomputing from the source is harder?

**Registered 2026-09-09, before any forward.**

## 0. The question this settles

`computed_sum_consumer` (arithmetic) and `two_hop_organism` (factual) agree on four things: the source route dominates while the source is visible, the carrier copy is real and content-specific but secondary, the variable is rebuilt at the question positions when the copy is denied, and the copy is consumed when the source is removed. They disagree on one number: the carrier-only donor carries **0.08** of the natural swing on sums and **0.27** on two-hop facts.

Two explanations survive, and they are confounded because the comparison is *between* organisms:
- **Recompute cost.** Re-adding two visible numbers is cheap and exact, so the copy is redundant; re-resolving a factual clue is expensive, so the copy does more work.
- **Boundary position.** A source donor from block 36 reproduces the full swing on sums (share 1.00) but only 0.58 on two-hop, i.e. the two organisms differ in how much of the source's contribution is already fixed below the cut.

This experiment varies recompute cost **inside one organism** with the boundary measured per condition, so the two can be separated.

## 1. The ladder

Three tiers, same copy organism, same carriers C0–C3, same consumer form, same cut depths, same donor construction, cluster = item (n = 8 per tier).

| tier | source span | instruction | consumer question | latent |
|---|---|---|---|---|
| `t1_memorised` | `"{a} and {b}"` | keep their sum in mind | What is the sum of the pair? | a+b, in 4–10 |
| `t3_chained` | **the same 8 source strings as t1** | keep **double** their sum in mind | What is double the sum of the pair? | 2(a+b), in 8–20 |
| `t2_composed` | `"{a} and {b} and {c}"` | keep their sum in mind | What is the sum of the triple? | a+b+c, in 7–14 |

`t1` and `t3` are the load-bearing pair: identical source tokens, identical donor tokens, identical span indices; only the instruction and the question differ, so the *only* thing that changes is the computation the model must perform. `t2` adds a third point on the ladder by lengthening the source instead, and is reported as a secondary comparison because its source differs.

Donors: item i's donor is item (i+3) mod 8 of the same tier; the donor latent differs from the own latent in every cell (asserted), and donor and recipient source strings have identical token counts (asserted). Every latent and every addend is a single token (verified: all number words two…twenty are single-token under this tokenizer). Parity is **not** used as a second consumer here because every `t3` latent is even; the report-style consumer, which needs the value, is primary at all three tiers.

## 2. Conditions (identical at every tier)

`clean`, `donor_clean` (the ceiling Δ = donor_clean − clean on the margin log P(donor latent) − log P(own latent)); `S_donor0` (source span ← donor, all 64 blocks: the token-equivalent reference); **`S_donor` (source span ← donor, ≥ 36: this is the boundary covariate)**; `C_full` and `C_all` (carrier ← donor carrier, source span asserted clean, ≥ 36 / all blocks); `C_rand` (carrier ← own + per-position norm-matched isotropic); `NEC_all` (source ← donor all blocks **and** carrier ← own all blocks).

Recorded: latent-pair answer scores (logsumexp over surface forms) and greedy; J_NP z over the number-word columns at the carrier interior and at the question positions; carrier ΔNLL; write norms and read-back error.

## 3. Gates

Competence per tier (scored argmax over the number-word set equals the true latent) **≥ 0.9**, thinking off; below that the tier is reported as not competent and its intervention rows are not interpreted. Source span asserted untouched under every carrier write. Donor geometry asserted per cell.

## 4. Predictions, on record

1. Competence falls across the ladder (t1 ≥ t3 ≥ t2 is the expected ordering, but any tier below 0.9 stops that tier).
2. **The discriminating result is the carrier share by tier, read beside the block-36 source share.**
   - If the carrier share rises from `t1` to `t3` (identical source, harder computation) while the block-36 source share is unchanged, **recompute cost drives it** and the between-organism gap is a domain effect.
   - If the carrier share is flat from `t1` to `t3`, **the between-organism gap was the boundary**, and the recompute-cost reading of the sum-versus-fact difference is withdrawn.
   - If both the carrier share and the block-36 share move together across tiers, the two accounts are **not separable in this design** and that is what will be reported.
3. `S_donor0` reproduces the ceiling at every competent tier (share ≥ 0.9).
4. `C_rand` inert at every tier.
5. `NEC_all` keeps most of the source effect at every tier (the carrier copy is not necessary), as on both earlier organisms.

## 5. Reporting rules fixed in advance

Each tier is normalised by **its own** ceiling, because clean confidence falls with difficulty and raw margins are not comparable across tiers; raw margins are reported beside the shares. Flip counts are read against each tier's own clean-competence floor. The t1-versus-t3 contrast is the registered primary; t2 is secondary.

Budget: 3 tiers × 8 items × 4 carriers × 8 forwards ≈ 770.
