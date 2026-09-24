# two_hop_organism · stage `qsplit6` — the question-turn ladder finished: answer plane, k-sweep, consumer clamp, current base (Amendment 6)

Run `20260924T091935Z`, 8624 forwards, 2707.3 s; Qwen3.6-27B, thinking off, **float32 residual from block 35** on every forward; 48 cells (12 items × 4 carriers), cluster = item; writes at blocks 36–62 on `q_pre` (question turn, scoring position excluded; 27 positions); consumer clamps at the scoring position only; sequence-log-prob endpoint (logsumexp over spellings). Full-vocabulary dictionary 248320 atoms per block; restricted word dictionary 66032 atoms. Design: `H3/design_specs/two_hop_organism.md` Amendment 6; battery `H3/scripts/two_hop_qsplit6.py`; the generated sections are from `two_hop_qsplit6_analysis.py`, the last section is hand-written.

## 1. Gates

- Gate 1 (rendering, `q` token-id equality recipient/donor, scoring position excluded, single-token answer words): asserted per cell in the battery (48 cells, `q_pre` length 27 in every cell) — PASS.
- Gate 2 (competence, sequence endpoint): clean32 1.00, donor32 1.00 — **PASS**.
- Gate 3 (realized writes): fixed-target rows ρ ∈ [1.0000, 1.0000], κ ≥ 1.0000, read-back max 0.0e+00; consumer clamps ρ ∈ [0.9999, 1.0002] over every block with a nonzero request (block 36's scoring position is still clean under every row, so its request is 0), κ ≥ 1.0000; current base (`q_rem_cb_pre`) ρ 1.0000 κ 1.0000; ‖v_R‖ = ‖v_J‖ asserted per position; `_ccr` realized norm within 0.02 % of its `_cc` match (bar 5 %) — **PASS**.
- Gate 4 (`q_full_pre` reproduces Amendment 5, +11.19 [+10.00, +12.38], ≥ 10/12 items > 0): +11.19 nats [+10.00, +12.38], 12/12 items > 0 — **PASS**.
- Gate 5 (controls): `q_rand_pre` share +0.001 (≤ 0.10), flips 0/48 (≤ 2 per 48 cells); `q_rem_rand_pre` share +0.982 (≥ 0.80) — **PASS**.
- Gate 6 (pursuit positive control, reported): the k = 2 selection on `q_pre` contains the leading-space `intermediate` or `swap_to` atom in 4.1 % of (block, position) cells at L51–59 (both: 0.0 %), 2.5 % over blocks 36–62 (both 0.0 %); chance per pick 2/248320 = 0.0008 %. P2 (majority at L51–59): not held.
- Gate 7 (restricted-dictionary NNLS KKT pass fraction ≥ 0.99 after the scipy fallback): 1.0000 of 36288 (block, vector) fits — **PASS**. Early stops of the full-dictionary pursuit (no positive correlation left before k = 64): 0.
- Collisions in the atom classification: ex2-city-language-Cairo: ['russian'] (answer class takes priority); ex2-city-language-Moscow: ['russian'] (answer class takes priority).

## 2. Main table (sequence endpoint; margin = log P(swap_answer) − log P(answer) minus clean32; item-clustered 95 % t-intervals; shares are ratios of item means)

| row | margin (nats) | 95 % CI | items > 0 | share of `q_full_pre` | share of S_donor0 (bf16, quoted) | flips | ‖v‖/‖Δh‖ (L51–59) | J_NP int shift at s | J_NP int shift on `q_pre` | J_NP answer shift at s | block-63 re-entry (`q_pre`) | ρ / κ (write) | clamp ρ (dim) | ΔNLL max |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `q_full_pre` | +11.19 | [+10.00, +12.38] | 12/12 | +1.000 | +0.469 | 18/48 | 1.000 | +5.50 (12/12) | +2.83 | +5.39 | +14.15 | 1.000 / 1.000 | — | +0.0000 |
| `q_plane_pre` | +2.25 | [+1.34, +3.16] | 11/12 | +0.201 | +0.094 | 0/48 | 0.175 | +2.70 (12/12) | +2.83 | +2.09 | +14.87 | 1.000 / 1.000 | — | +0.0000 |
| `q_rem_pre` | +8.77 | [+7.76, +9.79] | 12/12 | +0.784 | +0.367 | 1/48 | 0.175 | +1.73 (12/12) | -0.01 | +2.13 | -0.62 | 1.000 / 1.000 | — | +0.0000 |
| `q_ansplane_pre` | +5.04 | [+3.92, +6.16] | 12/12 | +0.450 | +0.211 | 0/48 | 0.163 | +1.44 (12/12) | +1.11 | +1.93 | +4.87 | 1.000 / 1.000 | — | +0.0000 |
| `q_ansrem_pre` | +6.24 | [+5.44, +7.04] | 12/12 | +0.558 | +0.261 | 0/48 | 0.163 | +3.17 (12/12) | +1.72 | +2.43 | +9.30 | 1.000 / 1.000 | — | +0.0000 |
| `q_J25nn_pre` | +4.11 | [+3.12, +5.09] | 12/12 | +0.367 | +0.172 | 0/48 | 0.247 | +1.45 (12/12) | +0.99 | +1.31 | +4.21 | 1.000 / 1.000 | — | +0.0000 |
| `q_rem25nn_pre` | +7.44 | [+6.84, +8.03] | 12/12 | +0.665 | +0.311 | 0/48 | 0.247 | +3.01 (12/12) | +1.85 | +2.91 | +10.39 | 1.000 / 1.000 | — | +0.0000 |
| `q_rem25ans_pre` | +9.66 | [+8.57, +10.76] | 12/12 | +0.864 | +0.405 | 4/48 | — | +5.13 (12/12) | +2.66 | +4.90 | +13.09 | 1.000 / 1.000 | — | +0.0000 |
| `q_rem25int_pre` | +10.83 | [+9.65, +12.01] | 12/12 | +0.968 | +0.454 | 12/48 | — | +4.95 (12/12) | +2.46 | +4.87 | +11.65 | 1.000 / 1.000 | — | +0.0000 |
| `q_rand_pre` | +0.01 | [-0.02, +0.05] | 7/12 | +0.001 | +0.001 | 0/48 | 0.175 | +0.03 (12/12) | +0.03 | +0.02 | +0.10 | 1.000 / 1.000 | — | +0.0000 |
| `q_rem_rand_pre` | +10.98 | [+9.85, +12.11] | 12/12 | +0.982 | +0.460 | 14/48 | 0.175 | +5.38 (12/12) | +2.80 | +5.26 | +14.07 | 1.000 / 1.000 | — | +0.0000 |
| `q_J2_pre` | +3.49 | [+2.63, +4.34] | 12/12 | +0.312 | +0.146 | 0/48 | 0.175 | +1.11 (12/12) | +0.83 | +0.98 | +3.26 | 1.000 / 1.000 | — | +0.0000 |
| `q_J2rem_pre` | +8.02 | [+7.38, +8.65] | 12/12 | +0.717 | +0.336 | 0/48 | 0.175 | +3.49 (12/12) | +2.03 | +3.38 | +11.35 | 1.000 / 1.000 | — | +0.0000 |
| `q_rand2rem_pre` | +10.94 | [+9.78, +12.10] | 12/12 | +0.978 | +0.458 | 14/48 | 0.175 | +5.40 (12/12) | +2.81 | +5.27 | +14.12 | 1.000 / 1.000 | — | +0.0000 |
| `q_J8_pre` | +4.34 | [+3.30, +5.37] | 12/12 | +0.388 | +0.182 | 0/48 | 0.228 | +1.42 (12/12) | +0.97 | +1.28 | +4.22 | 1.000 / 1.000 | — | +0.0000 |
| `q_J8rem_pre` | +6.97 | [+6.45, +7.49] | 12/12 | +0.623 | +0.292 | 0/48 | 0.228 | +3.06 (12/12) | +1.87 | +2.95 | +10.44 | 1.000 / 1.000 | — | +0.0000 |
| `q_rand8rem_pre` | +10.93 | [+9.81, +12.05] | 12/12 | +0.977 | +0.458 | 13/48 | 0.228 | +5.36 (12/12) | +2.79 | +5.24 | +14.05 | 1.000 / 1.000 | — | +0.0000 |
| `q_J25_pre` | +4.56 | [+3.48, +5.64] | 12/12 | +0.407 | +0.191 | 0/48 | 0.272 | +1.62 (12/12) | +1.06 | +1.46 | +4.49 | 1.000 / 1.000 | — | +0.0000 |
| `q_J25rem_pre` | +6.68 | [+6.18, +7.17] | 12/12 | +0.597 | +0.280 | 0/48 | 0.272 | +2.79 (12/12) | +1.78 | +2.70 | +10.15 | 1.000 / 1.000 | — | +0.0000 |
| `q_rand25rem_pre` | +10.75 | [+9.62, +11.88] | 12/12 | +0.960 | +0.450 | 10/48 | 0.272 | +5.25 (12/12) | +2.75 | +5.13 | +13.83 | 1.000 / 1.000 | — | +0.0000 |
| `q_J64_pre` | +4.56 | [+3.47, +5.65] | 12/12 | +0.407 | +0.191 | 0/48 | 0.297 | +1.73 (12/12) | +1.10 | +1.56 | +4.51 | 1.000 / 1.000 | — | +0.0000 |
| `q_J64rem_pre` | +6.62 | [+6.13, +7.10] | 12/12 | +0.592 | +0.277 | 0/48 | 0.297 | +2.66 (12/12) | +1.72 | +2.58 | +10.12 | 1.000 / 1.000 | — | +0.0000 |
| `q_rand64rem_pre` | +10.59 | [+9.51, +11.67] | 12/12 | +0.947 | +0.444 | 8/48 | 0.297 | +5.15 (12/12) | +2.71 | +5.02 | +13.70 | 1.000 / 1.000 | — | +0.0000 |
| `q_rem_cb_pre` | +9.23 | [+7.18, +11.28] | 12/12 | +0.825 | +0.386 | 9/48 | 0.175 | +4.30 (12/12) | +1.06 | +5.62 | -4.74 | 1.000 / 1.000 | — | +0.0000 |
| `q_rem_pre_cc` | +8.28 | [+7.13, +9.43] | 12/12 | +0.740 | +0.347 | 1/48 | 0.175 | -0.07 (0/12) | -0.01 | +1.11 | -0.62 | 1.000 / 1.000 | 1.000 (2–2) | +0.0000 |
| `q_rem25nn_pre_cc` | +5.79 | [+5.10, +6.49] | 12/12 | +0.518 | +0.243 | 0/48 | 0.247 | +1.79 (12/12) | +1.85 | +1.70 | +10.39 | 1.000 / 1.000 | 1.000 (23–25) | +0.0000 |
| `q_J2rem_pre_cc` | +5.78 | [+5.13, +6.43] | 12/12 | +0.517 | +0.242 | 0/48 | 0.175 | +2.19 (12/12) | +2.03 | +2.13 | +11.35 | 1.000 / 1.000 | 1.000 (2–2) | +0.0000 |
| `q_J8rem_pre_cc` | +5.23 | [+4.76, +5.71] | 12/12 | +0.468 | +0.219 | 0/48 | 0.228 | +1.81 (12/12) | +1.87 | +1.70 | +10.44 | 1.000 / 1.000 | 1.000 (8–8) | +0.0000 |
| `q_J25rem_pre_cc` | +5.21 | [+4.75, +5.67] | 12/12 | +0.466 | +0.218 | 0/48 | 0.272 | +1.61 (12/12) | +1.78 | +1.52 | +10.15 | 1.000 / 1.000 | 1.000 (25–25) | +0.0000 |
| `q_J64rem_pre_cc` | +5.24 | [+4.77, +5.71] | 12/12 | +0.468 | +0.219 | 0/48 | 0.297 | +1.55 (12/12) | +1.72 | +1.47 | +10.12 | 1.000 / 1.000 | 1.000 (64–64) | +0.0000 |
| `q_rem_pre_ccr` | +8.74 | [+7.73, +9.75] | 12/12 | +0.781 | +0.366 | 1/48 | 0.175 | +1.73 (12/12) | -0.01 | +2.12 | -0.62 | 1.000 / 1.000 | 1.000 (2–2) | +0.0000 |
| `q_rem25nn_pre_ccr` | +7.38 | [+6.79, +7.97] | 12/12 | +0.660 | +0.309 | 0/48 | 0.247 | +2.95 (12/12) | +1.85 | +2.84 | +10.39 | 1.000 / 1.000 | 1.000 (23–25) | +0.0000 |
| `q_J2rem_pre_ccr` | +7.98 | [+7.34, +8.62] | 12/12 | +0.714 | +0.334 | 0/48 | 0.175 | +3.48 (12/12) | +2.03 | +3.37 | +11.35 | 1.000 / 1.000 | 1.000 (2–2) | +0.0000 |
| `q_J8rem_pre_ccr` | +6.92 | [+6.42, +7.42] | 12/12 | +0.619 | +0.290 | 0/48 | 0.228 | +3.02 (12/12) | +1.87 | +2.92 | +10.44 | 1.000 / 1.000 | 1.000 (8–8) | +0.0000 |
| `q_J25rem_pre_ccr` | +6.62 | [+6.11, +7.12] | 12/12 | +0.591 | +0.277 | 0/48 | 0.272 | +2.73 (12/12) | +1.78 | +2.64 | +10.15 | 1.000 / 1.000 | 1.000 (25–25) | +0.0000 |
| `q_J64rem_pre_ccr` | +6.50 | [+6.00, +6.99] | 12/12 | +0.581 | +0.272 | 0/48 | 0.297 | +2.55 (12/12) | +1.72 | +2.45 | +10.12 | 1.000 / 1.000 | 1.000 (64–64) | +0.0000 |

Reference rows: natural donor rendering (`donor32`) J_NP int shift at s +19.75, answer shift at s +19.75, margin +23.88 nats. Candidate-set (single-token) margins are in the tables JSON as a secondary continuity column only. Columns: ‖v‖/‖Δh‖ is the removed/installed component's norm over ‖Δh‖, mean over cells × blocks 51–59 of the per-block position means; J_NP shifts are (swap_to − intermediate) and (swap_answer − answer) readouts at L51–59 minus clean; block-63 re-entry is Δproj(a_swap) − Δproj(a_int) on the raw unit naming directions at the first free block, mean over `q_pre`, minus clean.

## 3. share(k) curve and energy fractions

| k | J_k installed | J_k complement | J_k complement + consumer clamp | + random-k clamp (control) | random-k complement (norm- and rank-matched) | ‖v_Jk‖²/‖Δh‖² (all blocks / L51–59) | N(0, Σ) random-k fraction (all / L51–59) | k/d | blocks with e_J > e_rand |
|---|---|---|---|---|---|---|---|---|---|
| 2 | +0.312 (+3.49 [+2.63, +4.34], 12/12) | +0.717 (+8.02 [+7.38, +8.65], 12/12) | +0.517 (+5.78 [+5.13, +6.43], 12/12) | +0.714 (+7.98 [+7.34, +8.62], 12/12) | +0.978 (+10.94 [+9.78, +12.10], 12/12) | 0.021 / 0.023 | 0.005 / 0.005 | 0.0004 | 27/27 |
| 8 | +0.388 (+4.34 [+3.30, +5.37], 12/12) | +0.623 (+6.97 [+6.45, +7.49], 12/12) | +0.468 (+5.23 [+4.76, +5.71], 12/12) | +0.619 (+6.92 [+6.42, +7.42], 12/12) | +0.977 (+10.93 [+9.81, +12.05], 12/12) | 0.038 / 0.041 | 0.017 / 0.018 | 0.0016 | 26/27 |
| 25 | +0.407 (+4.56 [+3.48, +5.64], 12/12) | +0.597 (+6.68 [+6.18, +7.17], 12/12) | +0.466 (+5.21 [+4.75, +5.67], 12/12) | +0.591 (+6.62 [+6.11, +7.12], 12/12) | +0.960 (+10.75 [+9.62, +11.88], 12/12) | 0.055 / 0.061 | 0.038 / 0.040 | 0.0049 | 24/27 |
| 64 | +0.407 (+4.56 [+3.47, +5.65], 12/12) | +0.592 (+6.62 [+6.13, +7.10], 12/12) | +0.468 (+5.24 [+4.77, +5.71], 12/12) | +0.581 (+6.50 [+6.00, +6.99], 12/12) | +0.947 (+10.59 [+9.51, +11.67], 12/12) | 0.067 / 0.075 | 0.073 / 0.074 | 0.0125 | 10/27 |

Plane rows for comparison: intermediate plane A = +0.201, complement B = +0.784 (+ consumer clamp +0.740, random-plane clamp +0.781); answer plane A_ans = +0.450, complement B_ans = +0.558; restricted-dictionary NNLS k = 25: installed +0.367, complement +0.665 (+ clamp +0.518, control +0.660); atom-type ablations at k = 25: answer-related atoms removed +0.864, intermediate-related atoms removed +0.968. Energy reference: Σ_l from 5876 clean block outputs; 5 seeds.

Consumer-clamp effects as item-level differences (un-clamped minus clamped, nats; item-clustered 95 % t-intervals; the random-k control's difference beside it):

| complement row | clamp Δ (nats) | 95 % CI | items > 0 | as share of `q_full_pre` | as share of the row | random-k control Δ | 95 % CI |
|---|---|---|---|---|---|---|---|
| `q_rem_pre` | +0.49 | [+0.26, +0.73] | 12/12 | +0.044 | +0.056 | +0.03 | [+0.01, +0.05] |
| `q_rem25nn_pre` | +1.64 | [+1.17, +2.12] | 12/12 | +0.147 | +0.221 | +0.06 | [+0.03, +0.08] |
| `q_J2rem_pre` | +2.24 | [+1.75, +2.72] | 12/12 | +0.200 | +0.279 | +0.03 | [-0.00, +0.07] |
| `q_J8rem_pre` | +1.73 | [+1.23, +2.24] | 12/12 | +0.155 | +0.249 | +0.05 | [+0.01, +0.09] |
| `q_J25rem_pre` | +1.47 | [+0.98, +1.95] | 12/12 | +0.131 | +0.220 | +0.06 | [+0.03, +0.09] |
| `q_J64rem_pre` | +1.38 | [+0.87, +1.89] | 12/12 | +0.123 | +0.208 | +0.12 | [+0.06, +0.18] |

Readouts at the scoring position under the consumer clamps (J_NP, L51–59, minus clean; the clamp pins only the selected span, so these do not drop to 0 — **the `_cc` shares are upper bounds on any non-J route**, since a complete clamp of the J-readable content at s would remove at least as much):

| complement row | int readout at s: un-clamped → `_cc` (`_ccr`) | answer readout at s: un-clamped → `_cc` (`_ccr`) |
|---|---|---|
| `q_rem_pre` | +1.73 → -0.07 (+1.73) | +2.13 → +1.11 (+2.12) |
| `q_rem25nn_pre` | +3.01 → +1.79 (+2.95) | +2.91 → +1.70 (+2.84) |
| `q_J2rem_pre` | +3.49 → +2.19 (+3.48) | +3.38 → +2.13 (+3.37) |
| `q_J8rem_pre` | +3.06 → +1.81 (+3.02) | +2.95 → +1.70 (+2.92) |
| `q_J25rem_pre` | +2.79 → +1.61 (+2.73) | +2.70 → +1.52 (+2.64) |
| `q_J64rem_pre` | +2.66 → +1.55 (+2.55) | +2.58 → +1.47 (+2.45) |
| `q_full_pre` (reference) | +5.50 | +5.39 |

Planes at equal dimension: answer plane minus intermediate plane +2.79 nats [+1.79, +3.78], 12/12 items > 0, at ‖v‖/‖Δh‖ 0.163 vs 0.175. Additivity S = m(full) − m(part) − m(complement): intermediate plane +0.16 [-0.12, +0.44]; answer plane -0.09 [-0.70, +0.52]; J_25 -0.05 [-0.78, +0.69] (reported, not a partition).

Current base († construction failed, see §8.3 — the registered additive form double-counts the accumulated block delta; the numbers are reported as run and **not read**): `q_rem_cb_pre` +0.825 vs `q_rem_pre` +0.784 (9 vs 1 flips; J_NP int readout on `q_pre` +1.06 vs -0.01 pinned and +2.83 full; at s +4.30 vs +1.73 and +5.50). The free plane coordinate inside the band, Q_lᵀ(h' − h), projected on the full donor's plane coordinate (norm-weighted over `q_pre`, mean over cells): first block ≥ 0.5 at L41, 0.23 over L51–59, -0.13 at block 62; the coordinate's norm relative to the donor's peaks at 1.26× and is 0.74× at block 62. Per block (weighted fraction): L36 0.00, L39 0.17, L42 0.55, L45 0.59, L48 0.52, L51 0.37, L54 0.05, L57 0.32, L60 0.35, L62 -0.13.

## 4. Atom-type breakdown (norm shares ‖v_C‖/‖v_Jk‖, mean over cells × blocks × positions; atoms are not orthogonal, so the shares are components, not a partition)

| k | `q_pre` L51–59: answer / intermediate / other | `q_pre` all blocks | scoring position L51–59 | scoring position all blocks | count fraction (`q_pre`, L51–59) | |coef|-weighted fraction |
|---|---|---|---|---|---|---|
| 2 | 0.035 / 0.068 / 0.936 | 0.033 / 0.050 / 0.949 | 0.176 / 0.131 / 0.799 | 0.133 / 0.092 / 0.855 | 0.027 / 0.046 / 0.926 | 0.028 / 0.053 / 0.920 |
| 8 | 0.026 / 0.052 / 0.963 | 0.024 / 0.039 / 0.970 | 0.129 / 0.098 / 0.877 | 0.089 / 0.080 / 0.912 | 0.010 / 0.017 / 0.973 | 0.013 / 0.024 / 0.963 |
| 25 | 0.021 / 0.041 / 0.973 | 0.018 / 0.032 / 0.978 | 0.098 / 0.092 / 0.902 | 0.068 / 0.075 / 0.929 | 0.004 / 0.008 / 0.988 | 0.007 / 0.013 / 0.980 |
| 64 | 0.018 / 0.038 / 0.976 | 0.016 / 0.029 / 0.980 | 0.089 / 0.092 / 0.908 | 0.065 / 0.076 / 0.933 | 0.002 / 0.005 / 0.993 | 0.005 / 0.010 / 0.986 |
| NNLS 25 | 0.029 / 0.069 / 0.952 | — | — | — | — | — |

Most frequent atoms among the first 25 selected on `q_pre` at L51–59 (over the primary set's cells), by class:

- **intermediate**: ' Canada' ×223, ' canad' ×143, ' Canadian' ×121, ' Egypt' ×105, ' Egyptian' ×102, ' Greek' ×96, ' Poland' ×86, ' Polish' ×67, ' russ' ×64, ' spanish' ×62, ' Japan' ×61, ' Italian' ×59, ' Ital' ×55, ' polish' ×52, ' Honey' ×52, ' Russ' ×49, 'Egypt' ×44, ' Russia' ×42, 'Russ' ×40, ' ital' ×33, ' Egyptians' ×33, 'Canadian' ×32, ' Japanese' ×32, ' Rus' ×32, 'Pol' ×31
- **answer**: ' Ottawa' ×247, ' Athens' ×170, ' Arab' ×113, ' Russian' ×87, ' Madrid' ×83, ' Arabic' ×67, ' cows' ×60, ' Rome' ×38, ' Berlin' ×38, ' Tokyo' ×35, ' Warsaw' ×35, ' Bee' ×35, ' Paris' ×32, ' cow' ×24, ' cattle' ×23, 'Berlin' ×21, ' russian' ×16, ' paris' ×12, ' bees' ×12, ' arab' ×10, ' bee' ×10, ' Cow' ×10, ' PARIS' ×8, 'Russian' ×6, 'Arab' ×6
- **other**: '<|endoftext|>' ×720, '\n\n' ×658, '3' ×584, '2' ×523, '0' ×522, '1' ×477, '7' ×390, '<|im_end|>' ×349, '4' ×344, '“' ×340, '5' ×314, '8' ×303, ' insect' ×280, '\n' ×253, '9' ×251, ' Osaka' ×222, '6' ×214, '希腊' ×196, ' Munich' ×194, '法国' ×193, ' Abdel' ×184, ' RCMP' ×178, ' Bav' ×178, ' Naples' ×177, '「' ×176

**Content check at the two informative positions** (defined after seeing the six seeded cells, researcher note 2026-09-24; top-25 pursuit atoms, L51–59, mean over cells; 'translations included' adds non-Latin atoms whose nearest Latin-script unembedding neighbour is one of the item's four words or their aliases). Last `q_pre` position: 2 % of atoms intermediate/answer-related by the frozen classes, 5 % with translations (4 % / 8 % |coef|-weighted). Scoring position s (pursuit on the donor's Δh_s): 4 % / 8 % (7 % / 15 % weighted). Broad level, 'associated' (any atom among the top-100 unembedding neighbours of the four words; catches associates such as the cue city, the river, the leader, and also unrelated capitals): last `q_pre` 8 % (12 % weighted), s 16 % (24 % weighted). Pooled over every `q_pre` position (the Phase B statistic of §1): 1.2 %. Translation atoms found: ' япон' ×52, '希腊' ×47, '黄油' ×41, '埃及' ×40, '法国' ×36, '蜂蜜' ×35, '奶牛' ×34, '巴黎' ×33, '在德国' ×33, '波兰' ×33, ' روسيا' ×25, ' 독일' ×21, '罗马' ×20, '德国' ×20, ' ара' ×20, '�' ×18, '俄罗斯' ×18, '西班牙' ×16, '蜜' ×16, '意大利' ×14. Associated atoms found: '多伦多' ×43, ' Naples' ×42, ' Osaka' ×42, ' Zeus' ×42, ' RCMP' ×37, ' insect' ×32, ' Saskatchewan' ×26, ' Barcelona' ×26, ' Munich' ×26, ' Dairy' ×26, ' Nile' ×25, ' Kyoto' ×24, ' buzzing' ×24, ' cairo' ×23, ' calf' ×23, ' Cairo' ×22, ' Catalonia' ×21, ' الروسي' ×21, '/graphql' ×19, '糖浆' ×19.

Per-item split of the J_25 part (norm shares answer / intermediate / other; `q_pre` L51–59 mean, and at s):

| item | `q_pre`: answer / intermediate / other | s: answer / intermediate / other |
|---|---|---|
| ex-city-capital-Barcelona-Toronto | 0.05 / 0.12 / 0.92 | 0.23 / 0.23 / 0.75 |
| ex-city-capital-Lyon-Naples | 0.01 / 0.03 / 0.99 | 0.07 / 0.07 / 0.93 |
| ex-city-capital-Naples-Barcelona | 0.02 / 0.03 / 0.98 | 0.04 / 0.10 / 0.94 |
| ex-city-capital-Toronto-Lyon | 0.01 / 0.02 / 0.99 | 0.05 / 0.06 / 0.94 |
| ex2-city-capital-Munich | 0.01 / 0.03 / 0.98 | 0.00 / 0.02 / 0.99 |
| ex2-city-capital-Osaka | 0.01 / 0.01 / 0.99 | 0.03 / 0.00 / 0.99 |
| ex2-city-language-Cairo | 0.03 / 0.05 / 0.96 | 0.04 / 0.22 / 0.84 |
| ex2-city-language-Moscow | 0.04 / 0.07 / 0.95 | 0.24 / 0.09 / 0.81 |
| ex2-language-capital-Hungarian | 0.01 / 0.07 / 0.97 | 0.08 / 0.16 / 0.90 |
| ex2-language-capital-Polish | 0.04 / 0.04 / 0.97 | 0.16 / 0.08 / 0.87 |
| food-animal-butter | 0.01 / 0.02 / 0.99 | 0.03 / 0.05 / 0.97 |
| food-animal-honey | 0.03 / 0.01 / 0.99 | 0.20 / 0.03 / 0.91 |

## 5. Per-item shares of `q_full_pre` (all items; first column: the full margin in nats)

| item | relation | donor | adm. | full | plane A | rem B | ans-plane | ans-rem | J25 rem | J25 rem + cc | + ccr | rand25 rem | current base | NNLS25 rem | NNLS25 rem + cc |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ex-city-capital-Barcelona-Toronto | city-capital | r | — | +11.06 | +0.09 | +0.93 | +0.25 | +0.66 | +0.61 | +0.60 | +0.60 | +0.95 | +1.03 | +0.78 | +0.74 |
| ex-city-capital-Lyon-Naples | city-capital | r | — | +10.25 | +0.18 | +0.84 | +0.51 | +0.69 | +0.69 | +0.56 | +0.69 | +0.95 | +0.79 | +0.78 | +0.67 |
| ex-city-capital-Naples-Barcelona | city-capital | r | — | +10.89 | +0.21 | +0.76 | +0.34 | +0.65 | +0.72 | +0.47 | +0.71 | +0.97 | +0.70 | +0.78 | +0.51 |
| ex-city-capital-Toronto-Lyon | city-capital | r | — | +11.02 | +0.24 | +0.74 | +0.36 | +0.60 | +0.65 | +0.51 | +0.65 | +0.95 | +0.63 | +0.71 | +0.57 |
| ex2-city-capital-Munich | city-capital | r | — | +13.15 | +0.27 | +0.72 | +0.45 | +0.51 | +0.58 | +0.48 | +0.58 | +0.97 | +0.70 | +0.63 | +0.53 |
| ex2-city-capital-Osaka | city-capital | r | — | +11.75 | +0.31 | +0.70 | +0.52 | +0.50 | +0.57 | +0.42 | +0.57 | +0.97 | +0.61 | +0.63 | +0.46 |
| ex2-city-language-Cairo | city-language | r | — | +12.20 | +0.44 | +0.54 | +0.57 | +0.40 | +0.54 | +0.38 | +0.54 | +0.98 | +0.98 | +0.60 | +0.42 |
| ex2-city-language-Moscow | city-language | r | — | +12.22 | +0.18 | +0.79 | +0.69 | +0.41 | +0.45 | +0.36 | +0.44 | +0.94 | +0.60 | +0.52 | +0.41 |
| ex2-language-capital-Hungarian | language-capital | r | — | +11.68 | +0.11 | +0.80 | +0.27 | +0.61 | +0.53 | +0.39 | +0.52 | +0.95 | +0.87 | +0.60 | +0.45 |
| ex2-language-capital-Polish | language-capital | r | — | +13.52 | +0.13 | +0.82 | +0.47 | +0.57 | +0.49 | +0.40 | +0.49 | +0.96 | +0.58 | +0.54 | +0.42 |
| food-animal-butter | food-animal | r | — | +6.23 | +0.23 | +0.86 | +0.52 | +0.55 | +0.83 | +0.77 | +0.82 | +0.98 | +2.81 | +0.86 | +0.73 |
| food-animal-honey | food-animal | r | — | +10.28 | -0.00 | +0.98 | +0.44 | +0.60 | +0.67 | +0.43 | +0.65 | +0.97 | +0.53 | +0.72 | +0.45 |

## 6. Six seeded-random cells (seed 20260924; numbers generated, reading hand-written in §8)

- **ex-city-capital-Barcelona-Toronto|C2** (clean gap 14.8 nats; greedy clean `Madrid`, donor `O`): margins q_full_pre +11.01, q_plane_pre +0.95, q_rem_pre +9.87, q_ansplane_pre +2.59, q_ansrem_pre +7.23, q_J25rem_pre +6.44, q_J25rem_pre_cc +6.43, q_J25rem_pre_ccr +6.51, q_rand25rem_pre +10.63, q_rem_cb_pre +11.61, q_rem25nn_pre +8.71, q_rem25nn_pre_cc +8.27; greedy under J25 rem `Madrid`, + cc `Madrid`; J_NP int shift at s under J25 rem +1.92 → + cc +1.07; answer shift +1.55 → +0.82; pursuit on the donor's Δh at s, L59: [' Ottawa', ' canadian', ' Hull', '>O', '女王', ' Ride', ' ott', '镍']; on the last `q_pre` position: ['Canadian', ' Ottawa', ' Saskatchewan', '总理', '枫叶', ' Dominion', 'Yaw', ' TLC'].
- **ex-city-capital-Barcelona-Toronto|C3** (clean gap 14.4 nats; greedy clean `Madrid`, donor `O`): margins q_full_pre +10.64, q_plane_pre +0.73, q_rem_pre +10.26, q_ansplane_pre +2.47, q_ansrem_pre +7.22, q_J25rem_pre +6.84, q_J25rem_pre_cc +6.78, q_J25rem_pre_ccr +6.78, q_rand25rem_pre +10.50, q_rem_cb_pre +10.35, q_rem25nn_pre +8.59, q_rem25nn_pre_cc +8.34; greedy under J25 rem `Madrid`, + cc `Madrid`; J_NP int shift at s under J25 rem +0.97 → + cc +0.32; answer shift +1.05 → +0.45; pursuit on the donor's Δh at s, L59: [' Ottawa', ' Hull', ' canadian', '>O', ' ott', '尹', ' Ride', '魁']; on the last `q_pre` position: [' Canada', ' Ottawa', '枫叶', ' Dominion', 'Canadian', '总理', '(MAX', ' Burgess'].
- **ex-city-capital-Lyon-Naples|C3** (clean gap 10.1 nats; greedy clean `Paris`, donor `R`): margins q_full_pre +9.18, q_plane_pre +1.59, q_rem_pre +7.99, q_ansplane_pre +4.72, q_ansrem_pre +6.34, q_J25rem_pre +6.22, q_J25rem_pre_cc +5.35, q_J25rem_pre_ccr +6.22, q_rand25rem_pre +9.22, q_rem_cb_pre +7.59, q_rem25nn_pre +7.10, q_rem25nn_pre_cc +6.35; greedy under J25 rem `Paris`, + cc `Paris`; J_NP int shift at s under J25 rem +1.51 → + cc +0.84; answer shift +1.28 → +0.67; pursuit on the donor's Δh at s, L59: ['罗马', ' Naples', ' Rome', ' Rom', ' piazza', '朝天', ' Salerno', ' Nap']; on the last `q_pre` position: [' италья', ' Naples', ' Romano', ' Giulia', '披萨', '辛弃疾', ' Colleg', ' itching'].
- **ex-city-capital-Toronto-Lyon|C3** (clean gap 11.0 nats; greedy clean `O`, donor `Paris`): margins q_full_pre +9.94, q_plane_pre +2.12, q_rem_pre +7.25, q_ansplane_pre +3.62, q_ansrem_pre +5.49, q_J25rem_pre +6.24, q_J25rem_pre_cc +4.75, q_J25rem_pre_ccr +6.13, q_rand25rem_pre +9.39, q_rem_cb_pre +5.76, q_rem25nn_pre +6.75, q_rem25nn_pre_cc +5.37; greedy under J25 rem `O`, + cc `O`; J_NP int shift at s under J25 rem +2.35 → + cc +1.28; answer shift +2.04 → +0.95; pursuit on the donor's Δh at s, L59: ['巴黎', ' LY', ' Versailles', ' Бор', ' Zidane', ' Aix', ' parf', ' Mou']; on the last `q_pre` position: ['法国', ' Paris', ' Aristotle', '豫', ' Zidane', '情人', '螺丝', ' Provence'].
- **ex2-city-language-Cairo|C1** (clean gap 12.1 nats; greedy clean `Ar`, donor `Russian`): margins q_full_pre +12.19, q_plane_pre +5.32, q_rem_pre +6.66, q_ansplane_pre +6.94, q_ansrem_pre +4.69, q_J25rem_pre +6.43, q_J25rem_pre_cc +4.48, q_J25rem_pre_ccr +6.42, q_rand25rem_pre +11.87, q_rem_cb_pre +10.40, q_rem25nn_pre +7.29, q_rem25nn_pre_cc +5.05; greedy under J25 rem `Ar`, + cc `Ar`; J_NP int shift at s under J25 rem +3.03 → + cc +1.62; answer shift +3.76 → +2.16; pursuit on the donor's Δh at s, L59: [' Russian', ' روسيا', '莫斯科', ' Rus', ' Slav', '小熊', ' بوتين', '鹿']; on the last `q_pre` position: [' Russian', ' روسيا', ' Kremlin', '仓', ' Bols', ' vin', '霜', ' ми'].
- **ex2-city-language-Moscow|C3** (clean gap 13.4 nats; greedy clean `Russian`, donor `Ar`): margins q_full_pre +11.68, q_plane_pre +1.99, q_rem_pre +9.48, q_ansplane_pre +8.01, q_ansrem_pre +4.72, q_J25rem_pre +4.98, q_J25rem_pre_cc +4.08, q_J25rem_pre_ccr +4.97, q_rand25rem_pre +11.43, q_rem_cb_pre +7.41, q_rem25nn_pre +5.87, q_rem25nn_pre_cc +4.94; greedy under J25 rem `Russian`, + cc `Russian`; J_NP int shift at s under J25 rem +2.21 → + cc +1.74; answer shift +2.68 → +1.84; pursuit on the donor's Δh at s, L59: [' Arabic', '埃及', '阿', ' Nile', ' ара', ' Cairo', '枣', ' Ara']; on the last `q_pre` position: [' Egypt', ' ара', 'tri', ' Ahmed', ' Tipps', '肛', '枣', 'Aud'].

## 7. Decision rule (Amendment 6 §6) and predictions

Consumer-clamped complement share at k = 25: **+0.466** (un-clamped +0.597; random-k clamp control +0.591, within the un-clamped row's interval); gates 1–5 pass → **report the share(k) curve as the result**. Qualifier: answer-related atoms carry 2 % of the J_25 part's norm on `q_pre` at L51–59 (not most); answer-plane removal leaves B_ans = +0.558 (does not kill most of the effect). **Leading alternative, stated beside the rule:** the answer plane alone carries +0.450 against +0.201 for the intermediate plane at equal dimension (12/12 items), so "the answer is already computed and J-readable at the question turn" is the reading to beat; the `_cc` shares are upper bounds on any non-J route (the clamp is partial, §3), and the J_k part is strongly privileged per dimension (J_25 complement +0.597 vs random-25 complement +0.960).

| prediction (Amendment 6) | held? | values |
|---|---|---|
| P1 gates 1–5 pass | True | — |
| P2 k = 2 selection contains intermediate/swap_to on a majority of `q_pre` cells at L51–59 | False | 4.1 % |
| P3 answer plane: B_ans ≤ 0.5 while B ≈ 0.78 (qualifier applies) | False | A_ans +0.450, B_ans +0.558, B +0.784 |
| P4 share(J_k rem) non-increasing in k; random-k rem ≥ 0.80 at every k | True / True | J rem [0.717, 0.623, 0.597, 0.592]; rand rem [0.978, 0.977, 0.96, 0.947] |
| P5 `_cc` lowers each complement share; `_ccr` within the un-clamped interval | 6/6 lower; 6/6 within | q_rem_pre: cc +0.740 vs +0.784 (ccr +0.781); q_rem25nn_pre: cc +0.518 vs +0.665 (ccr +0.660); q_J2rem_pre: cc +0.517 vs +0.717 (ccr +0.714); q_J8rem_pre: cc +0.468 vs +0.623 (ccr +0.619); q_J25rem_pre: cc +0.466 vs +0.597 (ccr +0.591); q_J64rem_pre: cc +0.468 vs +0.592 (ccr +0.581) |
| P6 current base ≥ B − 0.10; plane rebuilt ≥ 0.5 by block 62? | True / False (≥ 0.5 somewhere in the band: True) | `q_rem_cb_pre` +0.825, B +0.784, weighted re-entry fraction at L62 -0.13, first block ≥ 0.5: L41 |
| P7 e_J > N(0, Σ) random-k fraction at every k (block means) | False | blocks holding per k: {'2': 27, '8': 26, '25': 24, '64': 10} |

Caveats carried forward from Amendment 5: each row is a fixed state trajectory over blocks 36–62 at `q_pre` (the rows are not a partition of one computation); `q_rem_pre` pins a two-token plane; the J_k rows pin the LS projection onto k greedy atoms of one dictionary (J_NP folded directions), so "J-readable content" here means "content in the span of those atoms"; the atom classes are string-mechanical (translations and related tokens in other scripts fall in *other*); shares are ratios of item means.

## 8. Interpretation, licensed / not licensed, next decision

_Hand-written 2026-09-24 after reading the tables (`two_hop_qsplit6_tables.json`), the six seeded cells and the current-base diagnostic (`cbdiag_qsplit6.txt`). Numbers below are copied from §1–7; nothing here is computed separately._

### 8.1 The six seeded cells, read by hand

- **Barcelona–Toronto, C2 and C3** (clean gaps 14.8 and 14.4 nats). Full donor +11.0 / +10.6; intermediate plane +0.9 / +0.7 (this item has the smallest A in the set, 0.09); complement +9.9 / +10.3; answer-plane complement +7.2 / +7.2; J25 complement +6.4 / +6.8; with the consumer clamp +6.4 / +6.8 (no change); random-k clamp the same; greedy stays `Madrid` under every row. The pinned span at s at L59 is ` Ottawa`, ` canadian`, ` Hull`, `>O`, ` ott`: the answer word, its city-neighbour and its first letters. In this item the clamp at the scoring position does nothing at all.
- **Lyon–Naples, C3** (gap 10.1). Full +9.2; plane +1.6; complement +8.0; answer-plane complement +6.3; J25 complement +6.2 → +5.35 clamped (−0.9), control +6.2; greedy `Paris` throughout. Pinned span: `罗马` (Rome, Chinese), ` Naples`, ` Rome`, ` Rom`, ` piazza`, ` Salerno`, ` Nap`: the answer in two scripts plus the donor's cue city.
- **Toronto–Lyon, C3** (gap 11.0). Full +9.9; plane +2.1; complement +7.3; answer-plane complement +5.5; J25 complement +6.2 → +4.75 clamped (−1.5), control +6.1; greedy `O` (first token of Ottawa) throughout. Pinned span: `巴黎` (Paris), ` LY`, ` Versailles`, ` Zidane`, ` Aix`, ` parf`: the answer in Chinese and France-associated tokens; no intermediate atom in the first eight.
- **Cairo, C1** (gap 12.1). Full +12.2 (the only one of the six that crosses, by 0.1 nats); plane +5.3 (the largest A of the set, 0.44); complement +6.7; answer-plane complement +4.7; J25 complement +6.4 → +4.5 clamped (−1.9), control +6.4; current base +10.4 with greedy **`Egypt`**, the intermediate itself emitted (the overshoot of §8.3). Pinned span: ` Russian`, ` روسيا`, `莫斯科`, ` Rus`, ` Slav`, ` بوتين`: the answer word, Russia in Arabic, Moscow in Chinese, Putin in Arabic.
- **Moscow, C3** (gap 13.4). Full +11.7; plane +2.0; complement +9.5; answer-plane complement +4.7; J25 complement +5.0 → +4.1 clamped (−0.9), control +5.0; greedy `Russian` throughout. Pinned span: ` Arabic`, `埃及` (Egypt), `阿`, ` Nile`, ` ара`, ` Cairo`.

What the six say that the means do not. (i) No row crosses the answer in five of the six cells: with clean gaps of 10–15 nats and pushes of 4–12, every number in this stage is an additive margin shift, as Stage 0 said of Amendment 5. (ii) The consumer clamp's effect ranges from exactly zero (both Barcelona cells) to −1.9 nats (Cairo); wherever it acts, the pinned span at the scoring position is the **answer word and its translations**, not the intermediate. (iii) The intermediate plane's share varies eightfold across cells (0.07 to 0.44) while the answer-plane complement sits consistently below the intermediate-plane complement.

### 8.2 The registered decision rule

Consumer-clamped complement share at k = 25: **0.466** (un-clamped 0.597; random-k clamp control 0.591, inside the un-clamped interval [6.18, 7.17] nats; gates 1–5 pass). That is between 0.2 and 0.5, so the registered outcome is the third branch: **report the share(k) curve as the result.** The curve: J_k complement 0.72 → 0.62 → 0.60 → 0.59 for k = 2, 8, 25, 64; with the consumer clamp 0.52 → 0.47 → 0.47 → 0.47; random-k complement 0.98 → 0.98 → 0.96 → 0.95. Neither branch of the qualifier fires as written (answer-related atoms are 2–4 % of the J_k norm on `q_pre`; the answer-plane complement is 0.56, not ≤ 0.5), but the answer-plane rows decide what "J-readable leverage at the question turn" means here: the answer's two-token plane carries 0.45 against the intermediate's 0.20 (+2.79 nats at equal dimension and slightly smaller norm, 12/12 items), and among the 25 pursuit atoms the handful classified answer-related cost 0.14 when removed against 0.03 for the intermediate-related ones.

### 8.3 Construction failure: the current-base row (silly mistake 4)

The registered `q_rem_cb_pre` writes h'_l = h^evolving_l + (I − P_l)Δh_l at every block. Δh_l is the donor-minus-clean **block output**, which already contains every earlier block's contribution, so adding it again at each block sums the accumulated deltas. The diagnostic (`two_hop_qsplit6_cbdiag.py`, two cells, 5 forwards each; not a scored row) measures ‖h'_cb − h‖ at `q_pre`: 0.97× the donor's deviation at block 36, 4.1× at block 40, 9.2× at block 50, 6.5× at block 62 (367 vs 56 for Barcelona–Toronto C0; 473 vs 61 for butter C0), and 6.2–7.2× at the free block 63. The symptoms were visible in the tables before the diagnostic: 9/48 flips against 1/48 for the pinned complement, the butter item at 2.81 of its own full margin, greedy `Egypt` and `The` in cells where every other row emits the answer word, and a free plane coordinate whose norm exceeds the donor's inside the band. Gate 3 as registered still passes for this row (the write is exact against the evolving base: ρ = κ = 1.000), which is why a construction check has to be a separate gate. **None of the row's numbers is read; P6 stays open.** The correct free-plane row replaces the complement coordinates instead of adding them, h'_l = P_l h^evolving_l + (I − P_l)(h_l + Δh_l), and is registered as a repair in Amendment 7. The re-scoping the row was meant to test survives by construction: B of Amendment 5 is "with the plane pinned".

### 8.4 What the dictionary did

The greedy nonnegative pursuit over all 248 077 vocabulary atoms selects the exact leading-space intermediate or swap_to atom in 4.1 % of `q_pre` cells at L51–59 (never both; 2.5 % over the band), thousands of times chance but far from the registered majority (P2 fails). Its selections are dominated by junk (`�`, end-of-text, `\n\n`, digits, `<|im_end|>`) and by other-script and demonym forms of the right entities (`希腊`, `法国`, `埃及`, ` Egyptian`, ` canad`, ` Athens`, ` Ottawa`), which the frozen classifier counts as "other". The J part saturates at 0.27–0.30 of ‖Δh‖ (7–9 % of the energy) from k = 25, and at k = 64 it captures **less** energy than k random directions drawn from the block's own covariance (0.067 vs 0.073; beats them in 10/27 blocks; P7 fails at 64, holds in 24–27/27 blocks at k ≤ 25). The restricted word dictionary (66 032 atoms, NNLS with KKT 1.000, no fallbacks) selects cleaner atoms (` Canada`, ` Greek`, ` Egyptian`, ` Russian`, ` Barcelona`, ` Ottawa`, ` Osaka`) and gives the same picture: installed 0.37, complement 0.67, clamped 0.52. The classifier limitation is stated, not repaired: translations and demonyms are "other" by the frozen rule, and every selected atom is saved so the classification can be audited.

### 8.5 Licensed

1. **k-sweep.** At the question turn (scoring position excluded, blocks 36–62), the part of the donor state that a k-atom J_NP dictionary can name installs 0.31 / 0.39 / 0.41 / 0.41 of the answer effect at k = 2 / 8 / 25 / 64 and its complement carries 0.72 / 0.62 / 0.60 / 0.59 (12/12 items at every k, 0/48 flips, additive within ±0.05); norm- and rank-matched random-k complements carry 0.95–0.98. The complement share stops falling at k = 25 while the dictionary's own energy capture stops rising.
2. **Consumer clamp, intermediate.** Holding the intermediate's naming plane at its clean coordinates at the scoring position removes 0.044 of the effect (+0.49 nats [+0.26, +0.73], 12/12; random-plane control +0.03) while holding the intermediate's J_NP readout at clean there (−0.07 vs +1.73 unclamped, +5.50 full). The complement's effect does not reach the answer through the intermediate's J-readable coordinates at the consumer position.
3. **Consumer clamp, k atoms.** Holding the k-atom span selected on the donor's Δh at the scoring position removes 0.12–0.20 of the effect (12/12 at every k; random-k controls 0.03–0.12 nats, one tenth of it), leaving 0.47 of the full effect at k = 25. The pinned atoms are 80–91 % "other" by norm and, in the hand-read cells, the answer word in several scripts, so this clamp is partly a clamp on the emitted word's own directions inside the band. The clamp is partial (the intermediate and answer readouts at s stay at +1.6 and +1.5 under it, §3), so the 0.13 it removes is a **lower** bound on how much of the complement's effect passes through J-readable content at the consumer, and the 0.47 it leaves is an **upper** bound on any non-J route; neither is a measurement of the intermediate's route, because the pinned span is mostly the answer word. (Corrected 2026-09-24 after the researcher's note; the first version of this sentence had the bound the wrong way round.)
4. **Answer plane.** The answer's two-token plane at the question turn carries 0.45 of the effect (12/12), more than the intermediate's 0.20 in every item at equal dimension and 0.16 vs 0.18 of ‖Δh‖; its complement carries 0.56. Of the J-readable leverage at the question turn, more is the answer's naming directions than the intermediate's.
5. **Regime.** Every fixed-target write, consumer clamp and current-base write is exact (ρ = κ = 1.000, read-back 0, control norms matched to 0.02 %); `q_full_pre` reproduces Amendment 5 to the second decimal; competence 1.00 / 1.00; the random plane 0.001 (0/48).

### 8.6 Not licensed

- "The complement lives outside the J-space" or "outside the workspace": the dictionary names a third of the delta's norm and is at noise level by k = 64; a better basis could name more. The licensed phrase is "not in the span of the atoms this dictionary selects".
- "The consumer ignores the readable intermediate": the intermediate plane carries 0.20 on `q_pre` and 0.04 at the scoring position — small, privileged per unit norm (the random plane is 0.001), not zero.
- "J-mediated at the consumer" from the k-atom clamp: the pinned span is mostly the answer word and translations; see 8.5(3).
- Anything from the current-base row (8.3), including the plane re-entry numbers in §3 and §7.
- Generalisation beyond twelve items of four relation types on one hybrid model with thinking off; the rows are fixed state trajectories, not the model's own computation; shares are ratios of item means.

### 8.7 What it means for the H3 statement, in one paragraph

At the question turn of this two-hop organism, the donor state's effect on the answer is mostly not carried by the coordinates a J_NP vocabulary dictionary names: removing the 64 best atoms on the question tokens and holding the same span at clean at the answer position leaves 0.47 of the effect (an upper bound on any non-J route, the clamp being partial), and removing the intermediate's own two-token plane leaves 0.78. The J-readable leverage that does exist is more the answer's naming directions (0.45) than the intermediate's (0.20), and the intermediate's readable coordinates at the consumer position carry 0.04. Readability of the intermediate at the question turn is therefore a poor proxy for how the answer is produced there, on the *what* axis as it was on the *where* axis (carrier vs source); the verbalizable representation is causally connected and privileged, not the main channel, in this organism.

### 8.8 Next decision

Stage 2 as registered in the task: Amendment 7 — grow the bank to ≥ 24 items over ≥ 3 relation types with the admission gates (competence; intermediate swap beats answer swap at mid depth, reported for the existing 12 too), the answer-smuggling ridge screen per relation, and the Stage 1 rows rerun on the full set; the repaired projection-replace current-base row; the restricted word dictionary as the primary J_k instrument with the full dictionary as the registered secondary (junk atoms); the stage-name note (the registered `pursuit` stage ran inside `qsplit6` as Phase B and the one-cell stage is `smoke1`). No further row on the 12 items without that amendment.

### 8.9 Additions after the researcher's notes (2026-09-24; post hoc, analysis of the same raw arrays, no forward)

1. **J_k rows against their random-k controls.** J_25 complement 0.60 against 0.96 for the norm- and rank-matched random-25 complement (12/12 items; on the six seeded cells 0.58 vs 0.98): twenty-five dictionary atoms carry 0.40 of the effect where twenty-five random directions of the same norm carry 0.04. The J part is strongly privileged per dimension; this is now stated in §7 beside the decision rule.
2. **Content check at the two informative positions** (§4; defined after seeing the six cells, so a post-hoc statistic). Top-25 pursuit atoms at L51–59, fraction that is the four words or their aliases / plus back-translations / plus top-100 unembedding associates: last `q_pre` position 2.5 % / 4.7 % / 8.2 % (coefficient-weighted 4.0 / 7.9 / 12.3 %); scoring position 4.0 % / 8.4 % / 16.1 % (weighted 6.6 / 14.8 / 24.4 %); pooled over every `q_pre` position, the Phase B statistic, 1.2 %. The informative positions are 3–20× richer in entity content than the pooled statistic, and the translation rule does recover the other-script forms (япон, 希腊, 埃及, 法国, 巴黎, 波兰, روسيا, 黄油, 蜂蜜, 奶牛) and the associates rule the cue cities, rivers and leaders (多伦多, Naples, Osaka, Zeus, Nile, Kyoto, Trudeau, Warszawa). But even at the broadest level three quarters of the J_25 weight at s and 88 % at the last `q_pre` position is not identifiable entity content. The six cells' first-eight lists were the content-rich head of each selection; the tail of the 25 is not content. Both readings hold together: the atoms that carry the effect are entity content, and the dictionary pads the fit with atoms that are not.
3. **The consumer clamp is partial** (table in §3). Under `q_J25rem_pre_cc` the intermediate readout at s goes +2.79 → +1.61 (control +2.73) and the answer readout +2.70 → +1.52; under the plane clamp the intermediate readout goes +1.73 → −0.07 (held) while the answer readout goes +2.13 → +1.11 (not held). The `_cc` shares are therefore upper bounds on any non-J route, as labelled in §3 and §7 and corrected in 8.5(3); the intermediate-plane clamp is the one complete clamp of the intermediate readout and leaves 0.74.
4. **Per-item split of the J_25 part** (§4). On `q_pre` the answer and intermediate classes are ≤ 0.12 of the norm in every item (other ≥ 0.92). At the scoring position the answer class reaches 0.23 (Barcelona–Toronto), 0.24 (Moscow), 0.20 (honey), 0.16 (Polish) and the intermediate class 0.23 (Barcelona–Toronto), 0.22 (Cairo), 0.16 (Hungarian). With the answer plane at 0.45 against the intermediate plane's 0.20 (12/12), **"the answer is already computed and J-readable at the question turn" is the leading alternative** to a non-J channel, and §7 now says so beside the rule.
5. **Registered, not run (Amendment 8):** (a) joint removal of the intermediate and answer planes with a random-4 control; (b) a stronger consumer clamp pinning the four directions, the pursuit atoms and the translation atoms at s, read only if the readouts at s drop to ≈ 0, with a matched control; (c) the relation-transfer row (a capital item's `q_pre` delta pasted into the language question for the same city; a push toward the donor's language means intermediate content, toward its capital or nothing means answer content), seven pairs, mirror row, random control.
