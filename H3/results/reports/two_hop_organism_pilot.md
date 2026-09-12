# H3 · two_hop_organism — pilot (design `H3/design_specs/two_hop_organism.md`, Amendments 1–2) — run 20260909T151319Z

**Materials.** The workspace paper's released two-hop set (`anthropics/jacobian-lens` @ 581d398, `data/experiments/probe-swap.json`); the 12 items that have a released, length-matched donor clue for their swap entity (city→capital, city→language, language→capital, food→animal), carriers C0/C1, 24 cells, cluster = item (n = 12). Organism: turn 1 = `Here is a clue: {clue}. Keep the answer to the clue in mind while you copy …`, teacher-forced carrier; turn 2 = `Complete the fact from the clue you were given, using one word.` (Amendment 2 — the question never restates the clue). Latent = the released `intermediate` (never a token); consumer answer = the released `answer`, a function of the latent that is not its own word; donor = the released partner clue whose intermediate is `swap_to`, with `swap_answer` as the counterfactual. Scored rule: logsumexp over surface forms of `answer` vs `swap_answer`.

## Gates
- **G1 competence (thinking off, clue only in turn 1):** scored answer > swap_answer in 0.958 of cells (greedy token equals the full answer word in 0.417; the rest are first sub-tokens such as `R`, `Tok`, `Bud`) → PASS.
- **G2 readability of the latent during the carrier (J_NP presence, L51–59):** own clue − donor clue +2.42 [+1.93, +2.91] (12/12); own − no-clue +4.58 [+3.70, +5.45] (12/12) → PASS. The bridge entity (France, Italy, bee, …) is readable on the copied sentence.
- **G3 donor geometry:** asserted per cell (24/24). Carrier self-consistency: clue span asserted untouched under every carrier write.

## Results (Amendment 2 question; natural ceiling Δ = donor prompt − clean = +22.74 nats)

| condition | answer margin toward `swap_answer` (nats) | share of Δ | flips → swap_answer | carrier ΔNLL max |
|---|---|---|---|---|
| `S_donor` | +12.88 [+9.09, +16.66] (12/12) | 0.57 | 12/24 | +0.011 |
| `S_donor0` | +22.72 [+21.19, +24.25] (12/12) | 1.00 | 24/24 | +0.041 |
| `C_full` | +5.98 [+4.12, +7.85] (12/12) | 0.26 | 6/24 | +0.016 |
| `C_all` | +5.86 [+4.00, +7.71] (12/12) | 0.26 | 6/24 | +0.016 |
| `C_rand` | +0.01 [-0.07, +0.08] (7/12) | 0.00 | 0/24 | +0.017 |

`S_donor0` = clue span ← donor at all 64 blocks (token-equivalent); `S_donor` = same from block 36; `C_full` / `C_all` = carrier ← donor carrier from block 36 / all blocks, clue span untouched; `C_rand` = norm-matched isotropic carrier write.

## The restated-question variant (Amendment 1 archive, `*_pilot_a1.*`; Δ = +22.78)

| condition | answer margin (nats) | share of Δ | flips | ΔNLL max |
|---|---|---|---|---|
| `S_donor` | +5.82 [+4.37, +7.27] (12/12) | 0.26 | 4/24 | +0.009 |
| `S_donor0` | +2.99 [+1.73, +4.24] (12/12) | 0.13 | 3/24 | +0.044 |
| `C_full` | +3.00 [+1.86, +4.13] (12/12) | 0.13 | 0/24 | +0.017 |
| `C_all` | +2.92 [+1.77, +4.07] (12/12) | 0.13 | 1/24 | +0.017 |
| `C_rand` | -0.01 [-0.08, +0.06] (5/12) | -0.00 | 0/24 | +0.010 |

With the released completion form as the question, the token-level source donor moved the answer only 13 % of Δ: the consumer answered from the restated clue in the question. This is the re-readable-source trap the project documented on the word consumer, reproduced here and fixed by Amendment 2 before any conclusion was drawn.

## Reading (pilot scale; 12 items, two carriers)

1. **The organism is valid under Amendment 2.** The token-level source donor reproduces the natural ceiling (share 1.00, 24/24 flips); block 36 is a partial boundary for this consumer (share 0.57, 12/24) — the clue is partly resolved below block 36, unlike the sum, whose block-36 operand donor reproduced the ceiling.
2. **The carrier copy of a factual bridge entity carries about a quarter of the answer swing while the source is visible** (`C_full` 0.26 of Δ, 6/24 flips; `C_all` identical; random inert) — against 0.08 and 0/32 for the sum consumer under the same intervention shape. Registered prediction 4 put the sum-like outcome at < 0.25 on both statistics; the result sits at the boundary (0.26, 0.25) and is read as **more carrier use than the sum, not decisive use**.
3. The carrier donor installs the donor entity at the readout at the same magnitude as the source donor (J_NP latent shift +4.9 vs +4.9 for `S_donor0`), so, as on the sum, the dissociation is between an installed readable representation and a much smaller behavioral effect — smaller here by a factor of four rather than twelve.
4. Gate note: `S_donor0` carrier ΔNLL max 0.041 (all-block clue-span replacement; bound 0.02); every carrier-donor row ≤ 0.017.

**Decision.** Promise shown in the informative direction: a non-numeric latent behaves qualitatively like the sum (readable at the carrier; source-dominant; carrier copy real, secondary, content-specific) but with a three-fold larger carrier share, which is the first sign of a domain difference inside one model. Not established: the difference is at pilot scale on 12 templated items, the block-36 boundary is partial here, and the effect sits on the registered threshold. The full battery (NEC, question-site rows, absent-clue transplant, four carriers) on these 12 items would cost ≈ 700 forwards and would say whether the just-in-time reconstruction and the absent-source consumption also generalise.
