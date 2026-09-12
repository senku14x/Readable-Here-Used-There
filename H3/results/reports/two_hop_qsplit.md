# two_hop_organism · stage `qsplit` — the H3.3 ladder at the question-turn cut (Amendment 5)

Run `20260911T030657Z`, 1792 forwards, 453.0 s; Qwen3.6-27B, thinking off, **float32 residual from block 35** on every forward; 48 cells (12 items × 4 carriers), cluster = item; writes at blocks 36–62 on `q_pre` (question turn, scoring position excluded); sequence-log-prob endpoint (logsumexp over spellings). Design: `H3/design_specs/two_hop_organism.md` Amendment 5.

## 1. Gates

- Gate 1 (rendering, `q` token-id equality recipient/donor, scoring position excluded): asserted per cell in the battery.
- Gate 2 (competence, sequence endpoint): clean32 1.00, donor32 1.00 — PASS.
- Gate 3 (realized writes): `q_full_pre` ρ 1.000 κ 1.000 read-back 0.0e+00; `q_plane_pre` ρ 1.000 κ 1.000 read-back 0.0e+00; `q_rem_pre` ρ 1.000 κ 1.000 read-back 0.0e+00; `q_rand_pre` ρ 1.000 κ 1.000 read-back 0.0e+00; `q_rem_rand_pre` ρ 1.000 κ 1.000 read-back 0.0e+00 — PASS. ‖v_R‖ = ‖v_J‖ asserted per position.
- Plane geometry: max |cos(a_int, a_swap)| over cells and blocks 0.75; degenerate cells none. Mean norms over cells × blocks: ‖Δh‖ 12.76, ‖v_J‖ 2.57 (17.3 % of ‖Δh‖).
- Gate 4 (`q_full_pre` strong donorward): margin +11.19 nats, 12/12 items > 0, bar ≥ 7.16 (0.3 × S_donor0 bf16 23.88) and ≥ 10/12 — **PASS**.
- Gate 5 (controls): `q_rand_pre` share +0.003 (≤ 0.10), flips 0/48 (≤ 2); `q_rem_rand_pre` share +0.983 (≥ 0.80) — **PASS**.

## 2. Main table (sequence endpoint; margin = log P(swap_answer) − log P(answer) minus clean32; item-clustered 95 % t-intervals)

| condition | margin (nats) | 95 % CI | items > 0 | share of `q_full_pre` | share of S_donor0 (bf16, quoted) | flips | candidate-set margin | J_NP q-readout shift L51–59 | block-63 Δproj(a_swap) − Δproj(a_int) | ρ / κ | read-back max | ΔNLL max |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `q_full_pre` | +11.19 | [+10.00, +12.38] | 12/12 | +1.000 | +0.469 | 18/48 | +10.91 | +2.92 (12/12) | +14.15 | 1.000 / 1.000 | 0.0e+00 | +0.0000 |
| `q_plane_pre` | +2.25 | [+1.34, +3.16] | 11/12 | +0.201 | +0.094 | 0/48 | +2.74 | +2.83 (12/12) | +14.87 | 1.000 / 1.000 | 0.0e+00 | +0.0000 |
| `q_rem_pre` | +8.77 | [+7.76, +9.79] | 12/12 | +0.784 | +0.367 | 1/48 | +8.05 | +0.05 (11/12) | -0.62 | 1.000 / 1.000 | 0.0e+00 | +0.0000 |
| `q_rand_pre` | +0.03 | [-0.01, +0.07] | 9/12 | +0.003 | +0.001 | 0/48 | +0.02 | +0.03 (12/12) | +0.08 | 1.000 / 1.000 | 0.0e+00 | +0.0000 |
| `q_rem_rand_pre` | +11.00 | [+9.85, +12.15] | 12/12 | +0.983 | +0.461 | 15/48 | +10.78 | +2.89 (12/12) | +14.09 | 1.000 / 1.000 | 0.0e+00 | +0.0000 |
| `int_q32` | +2.33 | [+1.61, +3.06] | 12/12 | +0.209 | +0.098 | 0/48 | +2.59 | +1.59 (12/12) | +3.95 | — | — | +0.0000 |

Additivity S = m(full) − m(plane) − m(rem): +0.16 nats [-0.12, +0.44], 8/12 items > 0 (reported, not a partition).

## 3. Per-item shares of `q_full_pre`

| item | full margin | A = plane | B = complement | S |
|---|---|---|---|---|
| ex-city-capital-Barcelona-Toronto | +11.06 | +0.09 | +0.93 | -0.17 |
| ex-city-capital-Lyon-Naples | +10.25 | +0.18 | +0.84 | -0.24 |
| ex-city-capital-Naples-Barcelona | +10.89 | +0.21 | +0.76 | +0.33 |
| ex-city-capital-Toronto-Lyon | +11.02 | +0.24 | +0.74 | +0.19 |
| ex2-city-capital-Munich | +13.15 | +0.27 | +0.72 | +0.10 |
| ex2-city-capital-Osaka | +11.75 | +0.31 | +0.70 | -0.14 |
| ex2-city-language-Cairo | +12.20 | +0.44 | +0.54 | +0.17 |
| ex2-city-language-Moscow | +12.22 | +0.18 | +0.79 | +0.30 |
| ex2-language-capital-Hungarian | +11.68 | +0.11 | +0.80 | +1.13 |
| ex2-language-capital-Polish | +13.52 | +0.13 | +0.82 | +0.63 |
| food-animal-butter | +6.23 | +0.23 | +0.86 | -0.57 |
| food-animal-honey | +10.28 | -0.00 | +0.98 | +0.23 |

## 4. P3 reading (thresholds fixed in Amendment 5 §5)

A = +0.201, B = +0.784, `q_rem_rand_pre` = +0.983 → **complement dominant**.

Caveat beside the result: `q_rem_pre` removes the **two-token naming plane** of one counterfactual pair, not a k = 25 J-space reconstruction; the licensed comparison to the paper's Fig. 16 is "the position-resolved analogue of the paper's split, restricted to the pair's naming plane". Each row is a fixed state trajectory over blocks 36–62 at `q_pre` (the complement of the written component is held at its clean or donor value at every written block), so the rows are not a partition of one computation. The block-63 column is Δproj(a_swap) − Δproj(a_int) on the raw unit naming directions (identity transport, γ⊙w_v) at `q_pre` at the first free block after the sustained write, minus clean: the re-entry observation for `q_rem_pre`.

## 5. Interpretation and next decision

**What was measured.** At the question turn with the scoring position excluded, three fixed state trajectories over blocks 36–62 were compared on the same 48 cells under an exact (float32) write: the full donor delta; the component of that delta inside the intermediate's two-token naming plane (a_int, a_swap_to; on average 17 % of ‖Δh‖); and the delta with that plane removed and held at its clean value at every written block. Every gate registered in Amendment 5 passed: competence 1.00 on both renderings, ρ = κ = 1.000 with zero read-back error on every row, the full donor above the 0.3 × S_donor0 bar on 12/12 items, the norm-matched random plane inert (0.003, 0/48) and the donor minus an equal-norm random component at 0.98 of the full donor.

**Result, at the strength the rows support.** The registered reading is **complement dominant** (A = 0.20, B = 0.78, random controls as above). Three facts carry it:

1. The plane component alone installs the intermediate at the J_NP q-readout as strongly as the full donor does (+2.83 vs +2.92 at L51–59, 12/12) yet moves the answer 0.20 of the full donor's effect (+2.25 nats, 0/48 flips). Installing the readout is not the same as installing the effect at this cut.
2. The complement, with the plane clamped to clean throughout the band, leaves the plane readout at clean (+0.05) and does not re-enter it at the first free block (block 63: −0.62, against +14.15 under the full donor), yet moves the answer 0.78 of the full donor (+8.77 nats, 12/12 items, every item ≥ 0.54). The effect at this cut travels mostly outside the two-token plane, and it does so without the plane being rebuilt downstream of the write.
3. The rows are roughly additive (S = +0.16 [−0.12, +0.44]): the plane and its complement contribute separately rather than redundantly or jointly.

The plane is nonetheless **privileged per unit norm**: at equal norm a random 2-plane moves the answer 0.003 of the full donor, the naming plane 0.20 — about 70×. The paper-style coordinate swap on the same span reads 0.21, consistent with the plane row. So the naming directions are causally efficient, as the paper's construction predicts, and insufficient for most of the effect at this position.

**Relation to the paper, as licensed.** This is the position-resolved analogue of the paper's Fig. 16 split, restricted to the pair's naming plane and run at the question turn only. It does not contradict the paper's result, which decomposed a concept vector against a k = 16–25 sparse J-space reconstruction and swapped at every position; what it adds is that, at the one position where the project found the largest single-position share, a full-residual donor's effect is carried mainly by content outside the two-token naming plane, with that plane held at clean. Not licensed: "outside the J-space" (the `q_rem25` row was registered as not run), "the readable representation is unused" (the plane carries a real, norm-efficient 0.20), any statement about the carrier or clue positions, and any share-of-computation reading of S.

**Sanity checks done before this section was written.** The analysis script recomputes every primitive contrast from `raw_qsplit.npz`; six seeded-random cells (seed 20260911) were read by hand (Polish|C2, Osaka|C3, Barcelona|C0, Moscow|C0, Lyon–Naples|C1, butter|C2) and show the same ordering in every cell (full ≈ complement ≫ plane ≈ swap ≫ random ≈ 0); the greedy decode flips to the donor answer under the full donor in 18/48 cells (e.g. Lyon–Naples|C1 `Paris` → `R`[ome]) and under the complement in 1/48, never under the plane; on the butter/honey paraphrase item the full-donor greedy is `H` (the substance rather than the animal), so that item's flips are not clean even though its margin is (its A = 0.23, B = 0.86). Realized-write and read-back gates were checked on the smoke cell before the battery and hold on every cell of the run.

**Weaknesses.** (i) A 2-plane is a lower bound on "J-readable content": correlated naming directions (arachnid/web-style neighbours of Spain/Canada) lie in the complement and could carry part of B; the k = 25 restricted-dictionary row would bound this and was not run. (ii) The three rows are fixed trajectories: the complement's within-band consequences cannot re-enter the plane at written blocks by construction, so B measures "the complement with the plane pinned", not the complement free-running — the block-63 measurement shows no re-entry once the pin is released, which limits but does not remove this concern. (iii) `q_ans` was not run, so nothing is said about the scoring position itself. (iv) One organism, one model, thinking off; the dense-model rerun is not part of this amendment.

**Next decision.** If any of this is quoted, quote the pair (A = 0.20, B = 0.78) with the 2-plane caveat and the norm-efficiency fact together. The one experiment that would upgrade "two-token plane" toward "J-space" is the registered-but-unrun `q_rem25` (NNLS with KKT checks on a restricted folded-direction dictionary); the one that would test the pinning concern is a current-base variant of `q_rem_pre` (complement written on the evolving residual, plane left free) with the block-63 re-entry measurement. Neither is run at the time limit.
