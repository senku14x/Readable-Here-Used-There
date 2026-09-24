# two_hop_organism · stage `stage2` — Stage 2: the Amendment 6 ladder on 42 items over 6 relation types with admission gates, answer-smuggling screen and the repaired current-base row (Amendment 7)

Run `20260924T105049Z`, 30800 forwards, 9555.7 s; Qwen3.6-27B, thinking off, **float32 residual from block 35** on every forward; 168 cells (42 items × 4 carriers), cluster = item; writes at blocks 36–62 on `q_pre` (question turn, scoring position excluded; 27 positions); consumer clamps at the scoring position only; sequence-log-prob endpoint (logsumexp over spellings). Full-vocabulary dictionary 248320 atoms per block; restricted word dictionary 66032 atoms. Design: `H3/design_specs/two_hop_organism.md` Amendment 7; battery `H3/scripts/two_hop_qsplit6.py`; the generated sections are from `two_hop_qsplit6_analysis.py`, the last section is hand-written.

**Primary set = the admitted items** (35/42; Amendment 7 §2: competence in all four carriers and the intermediate swap beating the answer swap at blocks 36–50): ex-city-capital-Barcelona-Toronto, ex-city-capital-Lyon-Naples, ex-city-capital-Naples-Barcelona, ex-city-capital-Toronto-Lyon, ex2-city-capital-Munich, ex2-city-language-Moscow, ex2-language-capital-Hungarian, ex2-language-capital-Polish, food-animal-butter, s2-city-capital-Bergen-Kyoto, s2-city-capital-Cork-Antalya, s2-city-capital-Marseille-Aarhus, s2-city-capital-Mumbai-Salzburg, s2-city-capital-Salzburg-Kyoto, s2-city-capital-Vancouver-Naples, s2-city-language-Gothenburg-Isfahan, s2-city-language-Shanghai-Antalya, s2-river-capital-Elbe-Tagus, s2-river-capital-Fraser-Loire, s2-river-capital-Nile-Thames, s2-river-capital-Tagus-Tiber, s2-river-capital-Tiber-Weser, s2-river-capital-Volga-Weser, s2-language-capital-Dutch-Danish, s2-language-capital-Finnish-Thai, s2-language-capital-French-Swedish, s2-language-capital-Italian-Persian, s2-language-capital-Norwegian-Italian, s2-language-capital-Polish-Turkish, s2-city-currency-Hanoi-Busan, s2-city-currency-Manchester-Shanghai, s2-city-currency-Munich-Manchester, s2-city-currency-Osaka-Munich, s2-city-currency-Shanghai-Manchester, s2-city-currency-Zurich-Munich. Every table below is on the admitted set unless labelled *all items*; §2b gives all items and the per-relation split. Admission summary: gate (a) 42/42, gate (b) 35/42, both 35/42 (in this stage's cells: 35/42); admitted per relation type {'city-capital': 11, 'city-language': 3, 'language-capital': 8, 'food-animal': 1, 'river-capital': 6, 'city-currency': 6}; decision conditions (≥ 12 admitted over ≥ 3 types, competence ≥ 0.9): met.

## 1. Gates

- Gate 1 (rendering, `q` token-id equality recipient/donor, scoring position excluded, single-token answer words): asserted per cell in the battery (168 cells, `q_pre` length 27 in every cell) — PASS.
- Gate 2 (competence, sequence endpoint): clean32 1.00, donor32 1.00 on the admitted set (all items: 1.00 / 1.00; not a stop rule in Stage 2) — **PASS**.
- Gate 3 (realized writes): fixed-target rows ρ ∈ [1.0000, 1.0000], κ ≥ 1.0000, read-back max 0.0e+00; consumer clamps ρ ∈ [0.9999, 1.0002] over every block with a nonzero request (block 36's scoring position is still clean under every row, so its request is 0), κ ≥ 1.0000; current base (`q_rem_cbr_pre`) ρ 1.0000 κ 1.0000; ‖v_R‖ = ‖v_J‖ asserted per position; `_ccr` realized norm within 0.02 % of its `_cc` match (bar 5 %) — **PASS**.
- Gate 4 (reproduction: the 12 released-donor items' `q_full_pre` inside Stage 1's interval +11.19 [+10.00, +12.38], ≥ 10/12 > 0): +11.19 nats, 12/12 items > 0 — **PASS**.
- Gate 5 (controls): `q_rand_pre` share +0.003 (≤ 0.10), flips 0/140 (≤ 2 per 48 cells); `q_rem_rand_pre` share +0.982 (≥ 0.80) — **PASS**.
- Gate 6 (pursuit positive control, reported): the k = 2 selection on `q_pre` contains the leading-space `intermediate` or `swap_to` atom in 4.1 % of (block, position) cells at L51–59 (both: 0.0 %), 2.4 % over blocks 36–62 (both 0.0 %); chance per pick 2/248320 = 0.0008 %. P2 (majority at L51–59): not held.
- Gate 7 (restricted-dictionary NNLS KKT pass fraction ≥ 0.99 after the scipy fallback): 1.0000 of 127008 (block, vector) fits — **PASS**. Early stops of the full-dictionary pursuit (no positive correlation left before k = 64): 19.
- Gate 8 (`q_rem_cbr_pre` construction check ‖h' − h_clean‖/‖Δh‖ ≤ 1.5 at every block and position, all items): max 1.009, mean 0.988 — **PASS**.
- Collisions in the atom classification: ex2-city-language-Cairo: ['russian'] (answer class takes priority); ex2-city-language-Moscow: ['russian'] (answer class takes priority); s2-city-language-Aarhus-Naples: ['dane', 'danish', 'italian'] (answer class takes priority); s2-city-language-Bergen-Lyon: ['french', 'norwegian'] (answer class takes priority); s2-city-language-Gothenburg-Isfahan: ['persian', 'swedish'] (answer class takes priority); s2-city-language-Naples-Rotterdam: ['dutch', 'italian'] (answer class takes priority); s2-city-language-Osaka-Rotterdam: ['dutch', 'japanese'] (answer class takes priority); s2-city-language-Shanghai-Antalya: ['chinese', 'turkish'] (answer class takes priority).

## 2. Main table (admitted set; sequence endpoint; margin = log P(swap_answer) − log P(answer) minus clean32; item-clustered 95 % t-intervals; shares are ratios of item means)

| row | margin (nats) | 95 % CI | items > 0 | share of `q_full_pre` | share of S_donor0 (bf16, quoted) | flips | ‖v‖/‖Δh‖ (L51–59) | J_NP int shift at s | J_NP int shift on `q_pre` | J_NP answer shift at s | block-63 re-entry (`q_pre`) | ρ / κ (write) | clamp ρ (dim) | ΔNLL max |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `q_full_pre` | +11.16 | [+10.53, +11.80] | 35/35 | +1.000 | +0.467 | 50/140 | 1.000 | +5.80 (35/35) | +3.09 | +5.38 | +14.31 | 1.000 / 1.000 | — | +0.0000 |
| `q_plane_pre` | +2.08 | [+1.63, +2.52] | 35/35 | +0.186 | +0.087 | 0/140 | 0.171 | +2.96 (35/35) | +3.09 | +2.27 | +14.85 | 1.000 / 1.000 | — | +0.0000 |
| `q_rem_pre` | +8.87 | [+8.23, +9.50] | 35/35 | +0.795 | +0.371 | 16/140 | 0.171 | +1.58 (35/35) | -0.01 | +1.79 | -0.42 | 1.000 / 1.000 | — | +0.0000 |
| `q_ansplane_pre` | +4.16 | [+3.56, +4.76] | 35/35 | +0.373 | +0.174 | 0/140 | 0.154 | +1.57 (34/35) | +1.18 | +1.96 | +5.08 | 1.000 / 1.000 | — | +0.0000 |
| `q_ansrem_pre` | +6.96 | [+6.31, +7.60] | 35/35 | +0.623 | +0.291 | 14/140 | 0.154 | +3.19 (35/35) | +1.90 | +2.33 | +9.35 | 1.000 / 1.000 | — | +0.0000 |
| `q_J25nn_pre` | +3.83 | [+3.40, +4.26] | 35/35 | +0.343 | +0.160 | 0/140 | 0.243 | +1.61 (35/35) | +1.09 | +1.39 | +4.10 | 1.000 / 1.000 | — | +0.0000 |
| `q_rem25nn_pre` | +7.67 | [+7.19, +8.15] | 35/35 | +0.687 | +0.321 | 15/140 | 0.243 | +2.90 (35/35) | +2.01 | +2.65 | +10.58 | 1.000 / 1.000 | — | +0.0000 |
| `q_rem25ans_pre` | +9.94 | [+9.37, +10.50] | 35/35 | +0.890 | +0.416 | 30/140 | — | +5.44 (35/35) | +2.92 | +4.97 | +13.16 | 1.000 / 1.000 | — | +0.0000 |
| `q_rem25int_pre` | +10.70 | [+10.11, +11.29] | 35/35 | +0.959 | +0.448 | 38/140 | — | +4.98 (35/35) | +2.62 | +4.60 | +11.96 | 1.000 / 1.000 | — | +0.0000 |
| `q_rand_pre` | +0.04 | [+0.01, +0.06] | 25/35 | +0.003 | +0.002 | 0/140 | 0.171 | +0.03 (31/35) | +0.03 | +0.02 | +0.08 | 1.000 / 1.000 | — | +0.0000 |
| `q_rem_rand_pre` | +10.97 | [+10.35, +11.58] | 35/35 | +0.982 | +0.459 | 44/140 | 0.171 | +5.64 (35/35) | +3.05 | +5.21 | +14.24 | 1.000 / 1.000 | — | +0.0000 |
| `q_J2_pre` | +3.31 | [+2.91, +3.71] | 35/35 | +0.297 | +0.139 | 0/140 | 0.171 | +1.25 (35/35) | +0.91 | +1.08 | +3.23 | 1.000 / 1.000 | — | +0.0000 |
| `q_J2rem_pre` | +8.15 | [+7.68, +8.63] | 35/35 | +0.730 | +0.341 | 15/140 | 0.171 | +3.43 (35/35) | +2.21 | +3.15 | +11.47 | 1.000 / 1.000 | — | +0.0000 |
| `q_rand2rem_pre` | +10.97 | [+10.34, +11.59] | 35/35 | +0.983 | +0.459 | 46/140 | 0.171 | +5.71 (35/35) | +3.07 | +5.30 | +14.28 | 1.000 / 1.000 | — | +0.0000 |
| `q_J8_pre` | +4.15 | [+3.70, +4.61] | 35/35 | +0.372 | +0.174 | 0/140 | 0.224 | +1.59 (35/35) | +1.07 | +1.38 | +4.11 | 1.000 / 1.000 | — | +0.0000 |
| `q_J8rem_pre` | +7.13 | [+6.68, +7.57] | 35/35 | +0.638 | +0.298 | 11/140 | 0.224 | +2.95 (35/35) | +2.04 | +2.70 | +10.63 | 1.000 / 1.000 | — | +0.0000 |
| `q_rand8rem_pre` | +10.83 | [+10.23, +11.43] | 35/35 | +0.970 | +0.454 | 41/140 | 0.224 | +5.62 (35/35) | +3.04 | +5.20 | +14.18 | 1.000 / 1.000 | — | +0.0000 |
| `q_J25_pre` | +4.36 | [+3.89, +4.83] | 35/35 | +0.390 | +0.182 | 0/140 | 0.268 | +1.80 (35/35) | +1.16 | +1.56 | +4.39 | 1.000 / 1.000 | — | +0.0000 |
| `q_J25rem_pre` | +6.83 | [+6.39, +7.26] | 35/35 | +0.612 | +0.286 | 10/140 | 0.268 | +2.67 (35/35) | +1.93 | +2.45 | +10.35 | 1.000 / 1.000 | — | +0.0000 |
| `q_rand25rem_pre` | +10.68 | [+10.08, +11.28] | 35/35 | +0.957 | +0.447 | 39/140 | 0.268 | +5.51 (35/35) | +3.01 | +5.10 | +13.98 | 1.000 / 1.000 | — | +0.0000 |
| `q_J64_pre` | +4.37 | [+3.89, +4.85] | 35/35 | +0.392 | +0.183 | 0/140 | 0.293 | +1.91 (35/35) | +1.21 | +1.65 | +4.43 | 1.000 / 1.000 | — | +0.0000 |
| `q_J64rem_pre` | +6.78 | [+6.36, +7.21] | 35/35 | +0.608 | +0.284 | 11/140 | 0.293 | +2.53 (35/35) | +1.87 | +2.33 | +10.31 | 1.000 / 1.000 | — | +0.0000 |
| `q_rand64rem_pre` | +10.57 | [+10.00, +11.15] | 35/35 | +0.947 | +0.443 | 38/140 | 0.293 | +5.39 (35/35) | +2.96 | +4.98 | +13.82 | 1.000 / 1.000 | — | +0.0000 |
| `q_rem_cbr_pre` | +9.44 | [+8.85, +10.03] | 35/35 | +0.846 | +0.395 | 18/140 | 0.171 | +2.28 (35/35) | +0.78 | +2.35 | +1.57 | 1.000 / 1.000 | — | +0.0000 |
| `q_rem_pre_cc` | +8.46 | [+7.75, +9.17] | 35/35 | +0.758 | +0.354 | 15/140 | 0.171 | -0.07 (9/35) | -0.01 | +0.83 | -0.42 | 1.000 / 1.000 | 1.000 (2–2) | +0.0000 |
| `q_rem25nn_pre_cc` | +6.48 | [+5.98, +6.97] | 35/35 | +0.580 | +0.271 | 8/140 | 0.243 | +1.72 (35/35) | +2.01 | +1.50 | +10.58 | 1.000 / 1.000 | 1.000 (23–25) | +0.0000 |
| `q_J2rem_pre_cc` | +6.46 | [+5.95, +6.96] | 35/35 | +0.578 | +0.270 | 3/140 | 0.171 | +2.06 (35/35) | +2.21 | +1.83 | +11.47 | 1.000 / 1.000 | 1.000 (2–2) | +0.0000 |
| `q_J8rem_pre_cc` | +5.81 | [+5.38, +6.23] | 35/35 | +0.520 | +0.243 | 1/140 | 0.224 | +1.67 (35/35) | +2.04 | +1.47 | +10.63 | 1.000 / 1.000 | 1.000 (8–8) | +0.0000 |
| `q_J25rem_pre_cc` | +5.71 | [+5.30, +6.11] | 35/35 | +0.511 | +0.239 | 1/140 | 0.268 | +1.49 (35/35) | +1.93 | +1.32 | +10.35 | 1.000 / 1.000 | 1.000 (25–25) | +0.0000 |
| `q_J64rem_pre_cc` | +5.74 | [+5.33, +6.15] | 35/35 | +0.514 | +0.240 | 1/140 | 0.293 | +1.44 (35/35) | +1.87 | +1.28 | +10.31 | 1.000 / 1.000 | 1.000 (64–64) | +0.0000 |
| `q_rem_pre_ccr` | +8.86 | [+8.23, +9.50] | 35/35 | +0.794 | +0.371 | 16/140 | 0.171 | +1.58 (35/35) | -0.01 | +1.78 | -0.42 | 1.000 / 1.000 | 1.000 (2–2) | +0.0000 |
| `q_rem25nn_pre_ccr` | +7.63 | [+7.15, +8.10] | 35/35 | +0.683 | +0.319 | 15/140 | 0.243 | +2.85 (35/35) | +2.01 | +2.60 | +10.58 | 1.000 / 1.000 | 1.000 (23–25) | +0.0000 |
| `q_J2rem_pre_ccr` | +8.13 | [+7.66, +8.61] | 35/35 | +0.729 | +0.341 | 14/140 | 0.171 | +3.42 (35/35) | +2.21 | +3.14 | +11.47 | 1.000 / 1.000 | 1.000 (2–2) | +0.0000 |
| `q_J8rem_pre_ccr` | +7.09 | [+6.65, +7.53] | 35/35 | +0.635 | +0.297 | 12/140 | 0.224 | +2.92 (35/35) | +2.04 | +2.66 | +10.63 | 1.000 / 1.000 | 1.000 (8–8) | +0.0000 |
| `q_J25rem_pre_ccr` | +6.79 | [+6.35, +7.23] | 35/35 | +0.608 | +0.284 | 10/140 | 0.268 | +2.62 (35/35) | +1.93 | +2.40 | +10.35 | 1.000 / 1.000 | 1.000 (25–25) | +0.0000 |
| `q_J64rem_pre_ccr` | +6.68 | [+6.25, +7.11] | 35/35 | +0.599 | +0.280 | 9/140 | 0.293 | +2.43 (35/35) | +1.87 | +2.22 | +10.31 | 1.000 / 1.000 | 1.000 (64–64) | +0.0000 |

Reference rows: natural donor rendering (`donor32`) J_NP int shift at s +21.42, answer shift at s +20.23, margin +24.27 nats. Candidate-set (single-token) margins are in the tables JSON as a secondary continuity column only. Columns: ‖v‖/‖Δh‖ is the removed/installed component's norm over ‖Δh‖, mean over cells × blocks 51–59 of the per-block position means; J_NP shifts are (swap_to − intermediate) and (swap_answer − answer) readouts at L51–59 minus clean; block-63 re-entry is Δproj(a_swap) − Δproj(a_int) on the raw unit naming directions at the first free block, mean over `q_pre`, minus clean.

### 2b. All items and the per-relation split

| row | all items: margin | 95 % CI | items > 0 | share | flips |
|---|---|---|---|---|---|
| `q_full_pre` | +11.46 | [+10.85, +12.08] | 42/42 | +1.000 | 65/168 |
| `q_plane_pre` | +2.45 | [+1.91, +2.98] | 41/42 | +0.213 | 0/168 |
| `q_rem_pre` | +8.91 | [+8.25, +9.56] | 42/42 | +0.777 | 17/168 |
| `q_ansplane_pre` | +4.60 | [+3.99, +5.20] | 42/42 | +0.401 | 0/168 |
| `q_ansrem_pre` | +6.99 | [+6.34, +7.64] | 42/42 | +0.610 | 14/168 |
| `q_J25rem_pre` | +7.06 | [+6.57, +7.56] | 42/42 | +0.616 | 10/168 |
| `q_J25rem_pre_cc` | +5.88 | [+5.36, +6.40] | 42/42 | +0.513 | 1/168 |
| `q_J25rem_pre_ccr` | +7.02 | [+6.53, +7.52] | 42/42 | +0.613 | 10/168 |
| `q_rand25rem_pre` | +11.00 | [+10.40, +11.59] | 42/42 | +0.959 | 50/168 |
| `q_rem_cbr_pre` | +9.61 | [+9.04, +10.19] | 42/42 | +0.839 | 21/168 |
| `q_rem25nn_pre` | +7.91 | [+7.37, +8.45] | 42/42 | +0.690 | 15/168 |
| `q_rem25nn_pre_cc` | +6.63 | [+6.03, +7.23] | 42/42 | +0.579 | 8/168 |

Per relation type (shares of that type's own `q_full_pre`; *all items of the type* / *admitted items of the type*; screen = leave-one-out residual fraction of the ridge affine map W_U[answer] ≈ A·W_U[intermediate] + b, flagged if ≤ 0.5 and below the mismatched-pairs null):

| relation | items (admitted) | donor | screen | full margin (all) | plane A | rem B | ans plane | ans rem | J25 rem | J25 rem + cc | current base (repaired) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| city-capital | 12 (11) | mixed | 0.98 | +11.74 (12/12) | +0.19 / +0.18 | +0.77 / +0.78 | +0.39 / +0.38 | +0.59 / +0.59 | +0.59 / +0.59 | +0.50 / +0.51 | +0.82 / +0.82 |
| city-currency | 6 (6) | constructed | 1.00 | +10.96 (6/6) | +0.10 / +0.10 | +0.92 / +0.92 | +0.25 / +0.25 | +0.82 / +0.82 | +0.75 / +0.75 | +0.62 / +0.62 | +0.94 / +0.94 |
| city-language | 8 (3) | mixed | 0.94 | +13.51 (8/8) | +0.37 / +0.34 | +0.65 / +0.63 | +0.58 / +0.65 | +0.48 / +0.36 | +0.57 / +0.45 | +0.47 / +0.33 | +0.78 / +0.77 |
| food-animal | 2 (1) | released | — | +8.26 (2/2) | +0.09 / — | +0.94 / — | +0.47 / — | +0.58 / — | +0.73 / — | +0.56 / — | +0.97 / — |
| language-capital | 8 (8) | mixed | 0.98 | +12.03 (8/8) | +0.13 / +0.13 | +0.83 / +0.83 | +0.31 / +0.31 | +0.66 / +0.66 | +0.58 / +0.58 | +0.49 / +0.49 | +0.86 / +0.86 |
| river-capital | 6 (6) | constructed | 0.99 | +9.00 (6/6) | +0.28 / +0.28 | +0.73 / +0.73 | +0.41 / +0.41 | +0.59 / +0.59 | +0.64 / +0.64 | +0.54 / +0.54 | +0.80 / +0.80 |

Admission table (per item; margins in nats, carriers averaged; (b) = intermediate swap beats answer swap at blocks 36–50 on the tail positions):

| item | relation | donor | competent carriers | `int_tail_mid` | `ans_tail_mid` | (b) | admitted |
|---|---|---|---|---|---|---|---|
| ex-city-capital-Barcelona-Toronto | city-capital | released | 4/4 | +24.63 | +22.74 | yes | **yes** |
| ex-city-capital-Lyon-Naples | city-capital | released | 4/4 | +3.98 | +3.61 | yes | **yes** |
| ex-city-capital-Naples-Barcelona | city-capital | released | 4/4 | +12.21 | +0.03 | yes | **yes** |
| ex-city-capital-Toronto-Lyon | city-capital | released | 4/4 | +20.84 | +10.97 | yes | **yes** |
| ex2-city-capital-Munich | city-capital | released | 4/4 | +23.01 | +5.73 | yes | **yes** |
| ex2-city-capital-Osaka | city-capital | released | 4/4 | +20.67 | +21.88 | no | no |
| ex2-city-language-Cairo | city-language | released | 4/4 | +14.45 | +17.95 | no | no |
| ex2-city-language-Moscow | city-language | released | 4/4 | +18.77 | +6.50 | yes | **yes** |
| ex2-language-capital-Hungarian | language-capital | released | 4/4 | +5.15 | +1.32 | yes | **yes** |
| ex2-language-capital-Polish | language-capital | released | 4/4 | +18.99 | +15.06 | yes | **yes** |
| food-animal-butter | food-animal | released | 4/4 | +5.83 | +2.47 | yes | **yes** |
| food-animal-honey | food-animal | released | 4/4 | +1.64 | +11.33 | no | no |
| s2-city-capital-Bergen-Kyoto | city-capital | constructed | 4/4 | +18.77 | +14.46 | yes | **yes** |
| s2-city-capital-Cork-Antalya | city-capital | constructed | 4/4 | +19.56 | +2.00 | yes | **yes** |
| s2-city-capital-Marseille-Aarhus | city-capital | constructed | 4/4 | +12.36 | +2.65 | yes | **yes** |
| s2-city-capital-Mumbai-Salzburg | city-capital | constructed | 4/4 | +16.77 | +11.02 | yes | **yes** |
| s2-city-capital-Salzburg-Kyoto | city-capital | constructed | 4/4 | +28.00 | +17.85 | yes | **yes** |
| s2-city-capital-Vancouver-Naples | city-capital | constructed | 4/4 | +24.65 | +10.41 | yes | **yes** |
| s2-city-language-Aarhus-Naples | city-language | constructed | 4/4 | +25.47 | +26.48 | no | no |
| s2-city-language-Bergen-Lyon | city-language | constructed | 4/4 | +22.85 | +23.33 | no | no |
| s2-city-language-Gothenburg-Isfahan | city-language | constructed | 4/4 | +24.65 | +24.61 | yes | **yes** |
| s2-city-language-Naples-Rotterdam | city-language | constructed | 4/4 | +15.39 | +25.23 | no | no |
| s2-city-language-Osaka-Rotterdam | city-language | constructed | 4/4 | +11.40 | +19.24 | no | no |
| s2-city-language-Shanghai-Antalya | city-language | constructed | 4/4 | +9.49 | +7.97 | yes | **yes** |
| s2-river-capital-Elbe-Tagus | river-capital | constructed | 4/4 | +5.90 | +3.92 | yes | **yes** |
| s2-river-capital-Fraser-Loire | river-capital | constructed | 4/4 | +15.48 | +10.54 | yes | **yes** |
| s2-river-capital-Nile-Thames | river-capital | constructed | 4/4 | +18.74 | +11.22 | yes | **yes** |
| s2-river-capital-Tagus-Tiber | river-capital | constructed | 4/4 | +18.16 | +12.97 | yes | **yes** |
| s2-river-capital-Tiber-Weser | river-capital | constructed | 4/4 | +17.54 | +6.38 | yes | **yes** |
| s2-river-capital-Volga-Weser | river-capital | constructed | 4/4 | +13.63 | +10.58 | yes | **yes** |
| s2-language-capital-Dutch-Danish | language-capital | constructed | 4/4 | +15.59 | +3.28 | yes | **yes** |
| s2-language-capital-Finnish-Thai | language-capital | constructed | 4/4 | +25.81 | +8.04 | yes | **yes** |
| s2-language-capital-French-Swedish | language-capital | constructed | 4/4 | +9.43 | +3.44 | yes | **yes** |
| s2-language-capital-Italian-Persian | language-capital | constructed | 4/4 | +18.82 | +0.88 | yes | **yes** |
| s2-language-capital-Norwegian-Italian | language-capital | constructed | 4/4 | +23.79 | +15.52 | yes | **yes** |
| s2-language-capital-Polish-Turkish | language-capital | constructed | 4/4 | +23.11 | +1.61 | yes | **yes** |
| s2-city-currency-Hanoi-Busan | city-currency | constructed | 4/4 | +7.04 | +0.06 | yes | **yes** |
| s2-city-currency-Manchester-Shanghai | city-currency | constructed | 4/4 | +11.48 | +0.93 | yes | **yes** |
| s2-city-currency-Munich-Manchester | city-currency | constructed | 4/4 | +9.25 | +2.38 | yes | **yes** |
| s2-city-currency-Osaka-Munich | city-currency | constructed | 4/4 | +14.32 | +4.17 | yes | **yes** |
| s2-city-currency-Shanghai-Manchester | city-currency | constructed | 4/4 | +16.37 | +2.66 | yes | **yes** |
| s2-city-currency-Zurich-Munich | city-currency | constructed | 4/4 | +13.71 | -1.37 | yes | **yes** |

## 3. share(k) curve and energy fractions

| k | J_k installed | J_k complement | J_k complement + consumer clamp | + random-k clamp (control) | random-k complement (norm- and rank-matched) | ‖v_Jk‖²/‖Δh‖² (all blocks / L51–59) | N(0, Σ) random-k fraction (all / L51–59) | k/d | blocks with e_J > e_rand |
|---|---|---|---|---|---|---|---|---|---|
| 2 | +0.297 (+3.31 [+2.91, +3.71], 35/35) | +0.730 (+8.15 [+7.68, +8.63], 35/35) | +0.578 (+6.46 [+5.95, +6.96], 35/35) | +0.729 (+8.13 [+7.66, +8.61], 35/35) | +0.983 (+10.97 [+10.34, +11.59], 35/35) | 0.021 / 0.023 | 0.005 / 0.005 | 0.0004 | 27/27 |
| 8 | +0.372 (+4.15 [+3.70, +4.61], 35/35) | +0.638 (+7.13 [+6.68, +7.57], 35/35) | +0.520 (+5.81 [+5.38, +6.23], 35/35) | +0.635 (+7.09 [+6.65, +7.53], 35/35) | +0.970 (+10.83 [+10.23, +11.43], 35/35) | 0.038 / 0.041 | 0.017 / 0.019 | 0.0016 | 27/27 |
| 25 | +0.390 (+4.36 [+3.89, +4.83], 35/35) | +0.612 (+6.83 [+6.39, +7.26], 35/35) | +0.511 (+5.71 [+5.30, +6.11], 35/35) | +0.608 (+6.79 [+6.35, +7.23], 35/35) | +0.957 (+10.68 [+10.08, +11.28], 35/35) | 0.055 / 0.060 | 0.037 / 0.040 | 0.0049 | 24/27 |
| 64 | +0.392 (+4.37 [+3.89, +4.85], 35/35) | +0.608 (+6.78 [+6.36, +7.21], 35/35) | +0.514 (+5.74 [+5.33, +6.15], 35/35) | +0.599 (+6.68 [+6.25, +7.11], 35/35) | +0.947 (+10.57 [+10.00, +11.15], 35/35) | 0.066 / 0.074 | 0.069 / 0.072 | 0.0125 | 8/27 |

Plane rows for comparison: intermediate plane A = +0.186, complement B = +0.795 (+ consumer clamp +0.758, random-plane clamp +0.794); answer plane A_ans = +0.373, complement B_ans = +0.623; restricted-dictionary NNLS k = 25: installed +0.343, complement +0.687 (+ clamp +0.580, control +0.683); atom-type ablations at k = 25: answer-related atoms removed +0.890, intermediate-related atoms removed +0.959. Energy reference: Σ_l from 20688 clean block outputs; 5 seeds.

Consumer-clamp effects as item-level differences (un-clamped minus clamped, nats; item-clustered 95 % t-intervals; the random-k control's difference beside it):

| complement row | clamp Δ (nats) | 95 % CI | items > 0 | as share of `q_full_pre` | as share of the row | random-k control Δ | 95 % CI |
|---|---|---|---|---|---|---|---|
| `q_rem_pre` | +0.41 | [+0.27, +0.54] | 35/35 | +0.036 | +0.046 | +0.01 | [-0.01, +0.02] |
| `q_rem25nn_pre` | +1.20 | [+0.90, +1.49] | 35/35 | +0.107 | +0.156 | +0.05 | [+0.03, +0.07] |
| `q_J2rem_pre` | +1.70 | [+1.34, +2.05] | 35/35 | +0.152 | +0.208 | +0.02 | [+0.00, +0.03] |
| `q_J8rem_pre` | +1.32 | [+1.02, +1.62] | 35/35 | +0.118 | +0.185 | +0.04 | [+0.02, +0.06] |
| `q_J25rem_pre` | +1.12 | [+0.85, +1.40] | 34/35 | +0.100 | +0.164 | +0.04 | [+0.02, +0.06] |
| `q_J64rem_pre` | +1.04 | [+0.76, +1.33] | 34/35 | +0.093 | +0.154 | +0.10 | [+0.07, +0.13] |

Readouts at the scoring position under the consumer clamps (J_NP, L51–59, minus clean; the clamp pins only the selected span, so these do not drop to 0 — **the `_cc` shares are upper bounds on any non-J route**, since a complete clamp of the J-readable content at s would remove at least as much):

| complement row | int readout at s: un-clamped → `_cc` (`_ccr`) | answer readout at s: un-clamped → `_cc` (`_ccr`) |
|---|---|---|
| `q_rem_pre` | +1.58 → -0.07 (+1.58) | +1.79 → +0.83 (+1.78) |
| `q_rem25nn_pre` | +2.90 → +1.72 (+2.85) | +2.65 → +1.50 (+2.60) |
| `q_J2rem_pre` | +3.43 → +2.06 (+3.42) | +3.15 → +1.83 (+3.14) |
| `q_J8rem_pre` | +2.95 → +1.67 (+2.92) | +2.70 → +1.47 (+2.66) |
| `q_J25rem_pre` | +2.67 → +1.49 (+2.62) | +2.45 → +1.32 (+2.40) |
| `q_J64rem_pre` | +2.53 → +1.44 (+2.43) | +2.33 → +1.28 (+2.22) |
| `q_full_pre` (reference) | +5.80 | +5.38 |

Planes at equal dimension: answer plane minus intermediate plane +2.08 nats [+1.63, +2.54], 35/35 items > 0, at ‖v‖/‖Δh‖ 0.154 vs 0.171. Additivity S = m(full) − m(part) − m(complement): intermediate plane +0.22 [-0.06, +0.49]; answer plane +0.04 [-0.37, +0.46]; J_25 -0.02 [-0.55, +0.51] (reported, not a partition).

Current base, repaired form (`q_rem_cbr_pre`: complement coordinates replaced by the donor's, plane free; construction check max 1.009): `q_rem_cbr_pre` +0.846 vs `q_rem_pre` +0.795 (18 vs 16 flips; J_NP int readout on `q_pre` +0.78 vs -0.01 pinned and +3.09 full; at s +2.28 vs +1.58 and +5.80). The free plane coordinate inside the band, Q_lᵀ(h' − h), projected on the full donor's plane coordinate (norm-weighted over `q_pre`, mean over cells): no block reaches 0.5, 0.28 over L51–59, 0.19 at block 62; the coordinate's norm relative to the donor's peaks at 0.37× and is 0.24× at block 62. Per block (weighted fraction): L36 0.00, L39 0.05, L42 0.16, L45 0.18, L48 0.19, L51 0.26, L54 0.27, L57 0.34, L60 0.35, L62 0.19.

## 4. Atom-type breakdown (norm shares ‖v_C‖/‖v_Jk‖, mean over cells × blocks × positions; atoms are not orthogonal, so the shares are components, not a partition)

| k | `q_pre` L51–59: answer / intermediate / other | `q_pre` all blocks | scoring position L51–59 | scoring position all blocks | count fraction (`q_pre`, L51–59) | |coef|-weighted fraction |
|---|---|---|---|---|---|---|
| 2 | 0.030 / 0.071 / 0.937 | 0.030 / 0.051 / 0.950 | 0.164 / 0.226 / 0.733 | 0.127 / 0.130 / 0.831 | 0.024 / 0.048 / 0.928 | 0.024 / 0.055 / 0.921 |
| 8 | 0.024 / 0.050 / 0.965 | 0.022 / 0.037 / 0.972 | 0.119 / 0.147 / 0.850 | 0.085 / 0.095 / 0.904 | 0.009 / 0.016 / 0.975 | 0.011 / 0.024 / 0.965 |
| 25 | 0.019 / 0.039 / 0.975 | 0.017 / 0.030 / 0.979 | 0.092 / 0.114 / 0.892 | 0.063 / 0.078 / 0.930 | 0.004 / 0.007 / 0.989 | 0.006 / 0.012 / 0.982 |
| 64 | 0.018 / 0.036 / 0.978 | 0.016 / 0.029 / 0.981 | 0.083 / 0.107 / 0.903 | 0.057 / 0.074 / 0.936 | 0.002 / 0.005 / 0.993 | 0.004 / 0.009 / 0.987 |
| NNLS 25 | 0.029 / 0.067 / 0.954 | — | — | — | — | — |

Most frequent atoms among the first 25 selected on `q_pre` at L51–59 (over the primary set's cells), by class:

- **intermediate**: ' Italy' ×289, ' Danish' ×272, ' Iran' ×250, ' Japan' ×238, ' Canada' ×223, ' Turkey' ×160, ' Japanese' ×151, ' Germany' ×144, ' canad' ×143, ' Iranian' ×141, ' Thai' ×141, ' Italian' ×125, ' Canadian' ×122, ' Austrian' ×119, 'Iran' ×119, ' Egypt' ×109, ' Turkish' ×109, ' turkey' ×109, ' ITAL' ×106, ' Persian' ×98, ' Greek' ×96, ' Tur' ×96, ' Egyptian' ×92, ' Ital' ×91, ' Poland' ×91
- **answer**: ' Rome' ×280, ' Ottawa' ×247, ' Tokyo' ×245, ' Ankara' ×229, ' Athens' ×170, ' Bangkok' ×170, ' Tehran' ×162, ' Euro' ×159, ' Arab' ×113, ' Copenhagen' ×99, ' euro' ×97, ' London' ×88, ' Stockholm' ×87, ' Madrid' ×83, ' Yuan' ×72, ' Arabic' ×67, ' Lisbon' ×67, ' Paris' ×60, ' yuan' ×51, ' Pound' ×50, ' Persian' ×48, 'Won' ×43, ' Euros' ×41, 'London' ×37, ' Warsaw' ×35
- **other**: '\n\n' ×2423, '<|endoftext|>' ×2295, '3' ×1633, '2' ×1581, '1' ×1262, '7' ×1122, '0' ×1055, '\n' ×1050, '4' ×1013, '5' ×917, '<|im_end|>' ×867, '“' ×823, '8' ×802, '6' ×718, '9' ×650, '土耳其' ×569, ' €' ×516, '意大利' ×509, ' :' ×503, ' Loire' ×477, '「' ×473, ' Antalya' ×462, '：“' ×428, ' япон' ×422, ' Naples' ×414

**Content check at the two informative positions** (defined after seeing the six seeded cells, researcher note 2026-09-24; top-25 pursuit atoms, L51–59, mean over cells; 'translations included' adds non-Latin atoms whose nearest Latin-script unembedding neighbour is one of the item's four words or their aliases). Last `q_pre` position: 2 % of atoms intermediate/answer-related by the frozen classes, 4 % with translations (4 % / 7 % |coef|-weighted). Scoring position s (pursuit on the donor's Δh_s): 4 % / 7 % (7 % / 14 % weighted). Broad level, 'associated' (any atom among the top-100 unembedding neighbours of the four words; catches associates such as the cue city, the river, the leader, and also unrelated capitals): last `q_pre` 8 % (12 % weighted), s 14 % (23 % weighted). Pooled over every `q_pre` position (the Phase B statistic of §1): 1.1 %. Translation atoms found: '意大利' ×134, ' япон' ×128, '土耳其' ×112, '英国' ×67, '在德国' ×64, '法国' ×60, '巴黎' ×50, ' китай' ×48, '希腊' ×47, '英國' ×45, '罗马' ×44, '英' ×43, '英伦' ×42, '埃及' ×40, '欧元区' ×40, '蜂蜜' ×35, '英格兰' ×34, '波兰' ×33, '伦敦' ×33, '瑞典' ×33. Associated atoms found: ' Naples' ×78, ' Aarhus' ×66, ' Greenland' ×65, '欧盟' ×63, ' Wales' ×61, '英镑' ×59, ' Salzburg' ×52, '€' ×51, ' £' ×47, '在英国' ×46, ' Shanghai' ×45, ' Osaka' ×44, ' Antalya' ×44, '多伦多' ×43, ' Naruto' ×43, ' Zeus' ×42, ' Istanbul' ×42, ' pounds' ×41, ' Kyoto' ×39, ' Volvo' ×38.

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
| s2-city-capital-Bergen-Kyoto | 0.02 / 0.05 / 0.97 | 0.07 / 0.25 / 0.84 |
| s2-city-capital-Cork-Antalya | 0.03 / 0.03 / 0.98 | 0.16 / 0.07 / 0.89 |
| s2-city-capital-Marseille-Aarhus | 0.01 / 0.06 / 0.97 | 0.04 / 0.18 / 0.88 |
| s2-city-capital-Mumbai-Salzburg | 0.01 / 0.04 / 0.98 | 0.03 / 0.27 / 0.83 |
| s2-city-capital-Salzburg-Kyoto | 0.04 / 0.03 / 0.97 | 0.23 / 0.10 / 0.83 |
| s2-city-capital-Vancouver-Naples | 0.01 / 0.01 / 0.99 | 0.06 / 0.03 / 0.95 |
| s2-city-language-Aarhus-Naples | 0.04 / 0.02 / 0.98 | 0.04 / 0.10 / 0.93 |
| s2-city-language-Bergen-Lyon | 0.05 / 0.02 / 0.97 | 0.01 / 0.12 / 0.93 |
| s2-city-language-Gothenburg-Isfahan | 0.01 / 0.09 / 0.96 | 0.12 / 0.25 / 0.78 |
| s2-city-language-Naples-Rotterdam | 0.04 / 0.02 / 0.97 | 0.06 / 0.03 / 0.94 |
| s2-city-language-Osaka-Rotterdam | 0.05 / 0.03 / 0.97 | 0.03 / 0.03 / 0.96 |
| s2-city-language-Shanghai-Antalya | 0.01 / 0.04 / 0.98 | 0.00 / 0.15 / 0.89 |
| s2-river-capital-Elbe-Tagus | 0.01 / 0.02 / 0.99 | 0.05 / 0.11 / 0.93 |
| s2-river-capital-Fraser-Loire | 0.01 / 0.02 / 0.99 | 0.00 / 0.01 / 1.00 |
| s2-river-capital-Nile-Thames | 0.03 / 0.03 / 0.97 | 0.04 / 0.13 / 0.91 |
| s2-river-capital-Tagus-Tiber | 0.04 / 0.05 / 0.96 | 0.13 / 0.17 / 0.85 |
| s2-river-capital-Tiber-Weser | 0.00 / 0.01 / 1.00 | 0.00 / 0.00 / 1.00 |
| s2-river-capital-Volga-Weser | 0.00 / 0.01 / 1.00 | 0.00 / 0.00 / 1.00 |
| s2-language-capital-Dutch-Danish | 0.01 / 0.04 / 0.98 | 0.06 / 0.14 / 0.89 |
| s2-language-capital-Finnish-Thai | 0.05 / 0.06 / 0.95 | 0.26 / 0.15 / 0.78 |
| s2-language-capital-French-Swedish | 0.02 / 0.04 / 0.97 | 0.12 / 0.07 / 0.91 |
| s2-language-capital-Italian-Persian | 0.04 / 0.08 / 0.94 | 0.25 / 0.33 / 0.69 |
| s2-language-capital-Norwegian-Italian | 0.01 / 0.08 / 0.96 | 0.07 / 0.26 / 0.81 |
| s2-language-capital-Polish-Turkish | 0.01 / 0.06 / 0.97 | 0.08 / 0.22 / 0.84 |
| s2-city-currency-Hanoi-Busan | 0.01 / 0.03 / 0.99 | 0.09 / 0.13 / 0.91 |
| s2-city-currency-Manchester-Shanghai | 0.03 / 0.02 / 0.98 | 0.17 / 0.01 / 0.91 |
| s2-city-currency-Munich-Manchester | 0.01 / 0.01 / 0.99 | 0.06 / 0.03 / 0.96 |
| s2-city-currency-Osaka-Munich | 0.04 / 0.04 / 0.97 | 0.09 / 0.02 / 0.95 |
| s2-city-currency-Shanghai-Manchester | 0.01 / 0.00 / 1.00 | 0.02 / 0.00 / 0.99 |
| s2-city-currency-Zurich-Munich | 0.03 / 0.02 / 0.98 | 0.13 / 0.05 / 0.92 |

## 5. Per-item shares of `q_full_pre` (all items; first column: the full margin in nats)

| item | relation | donor | adm. | full | plane A | rem B | ans-plane | ans-rem | J25 rem | J25 rem + cc | + ccr | rand25 rem | current base | NNLS25 rem | NNLS25 rem + cc |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ex-city-capital-Barcelona-Toronto | city-capital | r | yes | +11.06 | +0.09 | +0.93 | +0.25 | +0.66 | +0.61 | +0.60 | +0.60 | +0.95 | +0.93 | +0.78 | +0.74 |
| ex-city-capital-Lyon-Naples | city-capital | r | yes | +10.25 | +0.18 | +0.84 | +0.51 | +0.69 | +0.69 | +0.56 | +0.69 | +0.95 | +0.85 | +0.78 | +0.67 |
| ex-city-capital-Naples-Barcelona | city-capital | r | yes | +10.89 | +0.21 | +0.76 | +0.34 | +0.65 | +0.72 | +0.47 | +0.71 | +0.97 | +0.84 | +0.78 | +0.51 |
| ex-city-capital-Toronto-Lyon | city-capital | r | yes | +11.02 | +0.24 | +0.74 | +0.36 | +0.60 | +0.65 | +0.51 | +0.65 | +0.95 | +0.79 | +0.71 | +0.57 |
| ex2-city-capital-Munich | city-capital | r | yes | +13.15 | +0.27 | +0.72 | +0.45 | +0.51 | +0.58 | +0.48 | +0.58 | +0.97 | +0.76 | +0.63 | +0.53 |
| ex2-city-capital-Osaka | city-capital | r | no | +11.75 | +0.31 | +0.70 | +0.52 | +0.50 | +0.57 | +0.42 | +0.57 | +0.97 | +0.77 | +0.63 | +0.46 |
| ex2-city-language-Cairo | city-language | r | no | +12.20 | +0.44 | +0.54 | +0.57 | +0.40 | +0.54 | +0.38 | +0.54 | +0.98 | +0.71 | +0.60 | +0.42 |
| ex2-city-language-Moscow | city-language | r | yes | +12.22 | +0.18 | +0.79 | +0.69 | +0.41 | +0.45 | +0.36 | +0.44 | +0.94 | +0.85 | +0.52 | +0.41 |
| ex2-language-capital-Hungarian | language-capital | r | yes | +11.68 | +0.11 | +0.80 | +0.27 | +0.61 | +0.53 | +0.39 | +0.52 | +0.95 | +0.88 | +0.60 | +0.45 |
| ex2-language-capital-Polish | language-capital | r | yes | +13.52 | +0.13 | +0.82 | +0.47 | +0.57 | +0.49 | +0.40 | +0.49 | +0.96 | +0.87 | +0.54 | +0.42 |
| food-animal-butter | food-animal | r | yes | +6.23 | +0.23 | +0.86 | +0.52 | +0.55 | +0.83 | +0.77 | +0.82 | +0.98 | +0.94 | +0.86 | +0.73 |
| food-animal-honey | food-animal | r | no | +10.28 | -0.00 | +0.98 | +0.44 | +0.60 | +0.67 | +0.43 | +0.65 | +0.97 | +0.99 | +0.72 | +0.45 |
| s2-city-capital-Bergen-Kyoto | city-capital | c | yes | +11.24 | +0.25 | +0.73 | +0.36 | +0.58 | +0.67 | +0.57 | +0.67 | +0.98 | +0.85 | +0.72 | +0.62 |
| s2-city-capital-Cork-Antalya | city-capital | c | yes | +11.17 | +0.09 | +0.89 | +0.45 | +0.77 | +0.63 | +0.55 | +0.62 | +0.96 | +0.91 | +0.76 | +0.68 |
| s2-city-capital-Marseille-Aarhus | city-capital | c | yes | +12.10 | +0.17 | +0.86 | +0.29 | +0.69 | +0.66 | +0.62 | +0.66 | +0.96 | +0.87 | +0.73 | +0.70 |
| s2-city-capital-Mumbai-Salzburg | city-capital | c | yes | +13.15 | +0.09 | +0.69 | +0.40 | +0.35 | +0.37 | +0.34 | +0.36 | +0.93 | +0.74 | +0.46 | +0.44 |
| s2-city-capital-Salzburg-Kyoto | city-capital | c | yes | +12.99 | +0.22 | +0.73 | +0.40 | +0.51 | +0.52 | +0.43 | +0.51 | +0.96 | +0.81 | +0.59 | +0.49 |
| s2-city-capital-Vancouver-Naples | city-capital | c | yes | +12.06 | +0.19 | +0.72 | +0.31 | +0.59 | +0.51 | +0.48 | +0.51 | +0.97 | +0.75 | +0.63 | +0.59 |
| s2-city-language-Aarhus-Naples | city-language | c | no | +13.46 | +0.52 | +0.34 | +0.59 | +0.27 | +0.46 | +0.37 | +0.46 | +0.94 | +0.59 | +0.52 | +0.40 |
| s2-city-language-Bergen-Lyon | city-language | c | no | +12.13 | +0.53 | +0.61 | +0.57 | +0.54 | +0.62 | +0.46 | +0.62 | +0.97 | +0.81 | +0.72 | +0.51 |
| s2-city-language-Gothenburg-Isfahan | city-language | c | yes | +13.41 | +0.24 | +0.62 | +0.59 | +0.29 | +0.38 | +0.31 | +0.38 | +0.94 | +0.74 | +0.42 | +0.34 |
| s2-city-language-Naples-Rotterdam | city-language | c | no | +15.91 | +0.25 | +0.87 | +0.52 | +0.75 | +0.77 | +0.74 | +0.78 | +0.99 | +0.90 | +0.85 | +0.82 |
| s2-city-language-Osaka-Rotterdam | city-language | c | no | +15.02 | +0.24 | +0.85 | +0.44 | +0.74 | +0.76 | +0.72 | +0.75 | +0.97 | +0.89 | +0.84 | +0.80 |
| s2-city-language-Shanghai-Antalya | city-language | c | yes | +13.70 | +0.59 | +0.48 | +0.67 | +0.38 | +0.53 | +0.32 | +0.52 | +0.98 | +0.73 | +0.60 | +0.35 |
| s2-river-capital-Elbe-Tagus | river-capital | c | yes | +10.88 | +0.29 | +0.77 | +0.38 | +0.69 | +0.63 | +0.64 | +0.64 | +0.97 | +0.82 | +0.73 | +0.72 |
| s2-river-capital-Fraser-Loire | river-capital | c | yes | +7.72 | +0.37 | +0.62 | +0.44 | +0.51 | +0.64 | +0.51 | +0.63 | +0.95 | +0.68 | +0.68 | +0.58 |
| s2-river-capital-Nile-Thames | river-capital | c | yes | +10.52 | +0.24 | +0.85 | +0.41 | +0.63 | +0.63 | +0.46 | +0.62 | +0.96 | +0.91 | +0.72 | +0.52 |
| s2-river-capital-Tagus-Tiber | river-capital | c | yes | +9.56 | +0.21 | +0.82 | +0.37 | +0.64 | +0.64 | +0.49 | +0.63 | +0.97 | +0.89 | +0.74 | +0.63 |
| s2-river-capital-Tiber-Weser | river-capital | c | yes | +8.05 | +0.25 | +0.60 | +0.37 | +0.54 | +0.65 | +0.52 | +0.64 | +0.95 | +0.67 | +0.68 | +0.54 |
| s2-river-capital-Volga-Weser | river-capital | c | yes | +7.30 | +0.34 | +0.63 | +0.50 | +0.48 | +0.66 | +0.59 | +0.65 | +0.97 | +0.75 | +0.70 | +0.61 |
| s2-language-capital-Dutch-Danish | language-capital | c | yes | +11.09 | +0.06 | +0.88 | +0.19 | +0.69 | +0.66 | +0.55 | +0.66 | +0.94 | +0.89 | +0.77 | +0.68 |
| s2-language-capital-Finnish-Thai | language-capital | c | yes | +11.15 | +0.16 | +0.76 | +0.27 | +0.53 | +0.45 | +0.40 | +0.46 | +0.91 | +0.81 | +0.51 | +0.43 |
| s2-language-capital-French-Swedish | language-capital | c | yes | +13.47 | +0.16 | +0.75 | +0.32 | +0.65 | +0.63 | +0.43 | +0.63 | +0.96 | +0.77 | +0.66 | +0.46 |
| s2-language-capital-Italian-Persian | language-capital | c | yes | +13.19 | +0.11 | +0.88 | +0.19 | +0.76 | +0.60 | +0.57 | +0.60 | +0.93 | +0.89 | +0.68 | +0.65 |
| s2-language-capital-Norwegian-Italian | language-capital | c | yes | +10.26 | +0.22 | +0.83 | +0.39 | +0.64 | +0.59 | +0.55 | +0.58 | +0.98 | +0.88 | +0.72 | +0.68 |
| s2-language-capital-Polish-Turkish | language-capital | c | yes | +11.88 | +0.09 | +0.91 | +0.35 | +0.78 | +0.66 | +0.60 | +0.67 | +0.93 | +0.93 | +0.79 | +0.70 |
| s2-city-currency-Hanoi-Busan | city-currency | c | yes | +8.89 | +0.12 | +0.92 | +0.13 | +0.94 | +0.85 | +0.65 | +0.84 | +0.99 | +0.94 | +0.91 | +0.74 |
| s2-city-currency-Manchester-Shanghai | city-currency | c | yes | +11.49 | +0.16 | +0.90 | +0.28 | +0.81 | +0.59 | +0.54 | +0.60 | +0.94 | +0.91 | +0.66 | +0.62 |
| s2-city-currency-Munich-Manchester | city-currency | c | yes | +9.52 | +0.05 | +0.92 | +0.21 | +0.82 | +0.79 | +0.73 | +0.78 | +0.95 | +0.93 | +0.84 | +0.79 |
| s2-city-currency-Osaka-Munich | city-currency | c | yes | +12.23 | +0.12 | +0.92 | +0.35 | +0.74 | +0.71 | +0.52 | +0.70 | +0.96 | +0.95 | +0.79 | +0.56 |
| s2-city-currency-Shanghai-Manchester | city-currency | c | yes | +11.96 | +0.10 | +0.93 | +0.18 | +0.85 | +0.80 | +0.77 | +0.80 | +0.96 | +0.94 | +0.89 | +0.87 |
| s2-city-currency-Zurich-Munich | city-currency | c | yes | +11.67 | +0.07 | +0.95 | +0.32 | +0.81 | +0.79 | +0.55 | +0.79 | +0.98 | +0.97 | +0.87 | +0.62 |

## 6. Six seeded-random cells (seed 20260924; numbers generated, reading hand-written in §8)

- **ex-city-capital-Naples-Barcelona|C2** (admitted) (clean gap 10.0 nats; greedy clean `R`, donor `Madrid`): margins q_full_pre +11.37, q_plane_pre +3.00, q_rem_pre +8.75, q_ansplane_pre +3.75, q_ansrem_pre +7.98, q_J25rem_pre +8.85, q_J25rem_pre_cc +5.38, q_J25rem_pre_ccr +8.73, q_rand25rem_pre +11.50, q_rem_cbr_pre +9.63, q_rem25nn_pre +9.33, q_rem25nn_pre_cc +5.74; greedy under J25 rem `R`, + cc `R`; J_NP int shift at s under J25 rem +4.74 → + cc +2.31; answer shift +4.92 → +2.61; pursuit on the donor's Δh at s, L59: [' Spain', ' Barcelona', ' PSOE', ' Lle', ' MAD', '芒果', ' Cataluña', ' span']; on the last `q_pre` position: [' spanish', ' Barcelona', '¡', ' royal', ' Jordi', ' SPORT', ' Lle', '厨'].
- **ex-city-capital-Naples-Barcelona|C3** (admitted) (clean gap 10.2 nats; greedy clean `R`, donor `Madrid`): margins q_full_pre +9.94, q_plane_pre +1.94, q_rem_pre +7.56, q_ansplane_pre +3.56, q_ansrem_pre +6.06, q_J25rem_pre +6.94, q_J25rem_pre_cc +4.81, q_J25rem_pre_ccr +6.81, q_rand25rem_pre +9.39, q_rem_cbr_pre +8.31, q_rem25nn_pre +7.55, q_rem25nn_pre_cc +5.19; greedy under J25 rem `R`, + cc `R`; J_NP int shift at s under J25 rem +2.35 → + cc +1.17; answer shift +2.42 → +1.13; pursuit on the donor's Δh at s, L59: [' Spain', ' Barcelona', ' MAD', ' Lle', '芒果', 'Pu', ' cfg', '不可']; on the last `q_pre` position: ['西班牙', ' Barcelona', ' spinal', '¡', ' Alonso', '城中村', 'span', '路易斯'].
- **ex2-city-language-Cairo|C1** (not admitted) (clean gap 12.1 nats; greedy clean `Ar`, donor `Russian`): margins q_full_pre +12.19, q_plane_pre +5.32, q_rem_pre +6.66, q_ansplane_pre +6.94, q_ansrem_pre +4.69, q_J25rem_pre +6.43, q_J25rem_pre_cc +4.48, q_J25rem_pre_ccr +6.42, q_rand25rem_pre +11.87, q_rem_cbr_pre +8.69, q_rem25nn_pre +7.29, q_rem25nn_pre_cc +5.05; greedy under J25 rem `Ar`, + cc `Ar`; J_NP int shift at s under J25 rem +3.03 → + cc +1.62; answer shift +3.76 → +2.16; pursuit on the donor's Δh at s, L59: [' Russian', ' روسيا', '莫斯科', ' Rus', ' Slav', '小熊', ' بوتين', '鹿']; on the last `q_pre` position: [' Russian', ' روسيا', ' Kremlin', '仓', ' Bols', ' vin', '霜', ' ми'].
- **s2-city-capital-Mumbai-Salzburg|C0** (admitted) (clean gap 13.5 nats; greedy clean `New`, donor `Vi`): margins q_full_pre +13.26, q_plane_pre +1.26, q_rem_pre +9.38, q_ansplane_pre +5.12, q_ansrem_pre +4.82, q_J25rem_pre +4.81, q_J25rem_pre_cc +4.56, q_J25rem_pre_ccr +4.69, q_rand25rem_pre +12.26, q_rem_cbr_pre +10.01, q_rem25nn_pre +6.07, q_rem25nn_pre_cc +5.75; greedy under J25 rem `New`, + cc `New`; J_NP int shift at s under J25 rem +2.53 → + cc +1.34; answer shift +2.17 → +1.31; pursuit on the donor's Δh at s, L59: [' Vienna', ' Salz', ' Austrian', 'Wi', ' Inns', ' vi', '吸血鬼', ' Vien']; on the last `q_pre` position: [' Austrian', ' Salzburg', ' Wiener', ' Universität', '(md', '小溪', ' Otto', 'Vi'].
- **s2-city-language-Osaka-Rotterdam|C1** (not admitted) (clean gap 14.7 nats; greedy clean `Japanese`, donor `D`): margins q_full_pre +14.79, q_plane_pre +3.57, q_rem_pre +12.35, q_ansplane_pre +6.70, q_ansrem_pre +11.24, q_J25rem_pre +11.48, q_J25rem_pre_cc +10.99, q_J25rem_pre_ccr +11.60, q_rand25rem_pre +14.19, q_rem_cbr_pre +12.98, q_rem25nn_pre +12.49, q_rem25nn_pre_cc +12.08; greedy under J25 rem `Japanese`, + cc `Japanese`; J_NP int shift at s under J25 rem +4.05 → + cc +2.27; answer shift +4.71 → +2.69; pursuit on the donor's Δh at s, L59: ['荷兰', ' Rotterdam', ' Dut', ' Flem', '荷', ' nieder', 'fris', ' Holland']; on the last `q_pre` position: [' Rotterdam', '荷兰', ' Peter', '淤泥', ' duty', 'Cir', ' ING', ' Amor'].
- **s2-river-capital-Tagus-Tiber|C0** (admitted) (clean gap 10.4 nats; greedy clean `L`, donor `R`): margins q_full_pre +9.25, q_plane_pre +1.56, q_rem_pre +7.61, q_ansplane_pre +3.35, q_ansrem_pre +5.48, q_J25rem_pre +5.22, q_J25rem_pre_cc +4.21, q_J25rem_pre_ccr +5.23, q_rand25rem_pre +9.00, q_rem_cbr_pre +8.17, q_rem25nn_pre +6.23, q_rem25nn_pre_cc +5.34; greedy under J25 rem `L`, + cc `L`; J_NP int shift at s under J25 rem +1.80 → + cc +1.04; answer shift +1.91 → +0.89; pursuit on the donor's Δh at s, L59: ['罗马', ' Italy', ' Rome', '常州市', '�', '财务会计', ' Rav', ' Federazione']; on the last `q_pre` position: ['罗马', ' Italy', ' Integer', '翡翠', '喷雾', '滨湖', '�', ' iTunes'].

## 7. Decision rule (Amendment 6 §6; applied to the admitted set per Amendment 7 §5) and predictions

Consumer-clamped complement share at k = 25: **+0.511** (un-clamped +0.612; random-k clamp control +0.608, within the un-clamped row's interval); gates 1–5 pass → **non-J channel carries most of this consumer's margin**. Qualifier: answer-related atoms carry 2 % of the J_25 part's norm on `q_pre` at L51–59 (not most); answer-plane removal leaves B_ans = +0.623 (does not kill most of the effect). **Leading alternative, stated beside the rule:** the answer plane alone carries +0.373 against +0.186 for the intermediate plane at equal dimension (35/35 items), so "the answer is already computed and J-readable at the question turn" is the reading to beat; the `_cc` shares are upper bounds on any non-J route (the clamp is partial, §3), and the J_k part is strongly privileged per dimension (J_25 complement +0.612 vs random-25 complement +0.957).

| prediction (Amendment 6) | held? | values |
|---|---|---|
| P1 gates 1–5 pass | True | — |
| P2 k = 2 selection contains intermediate/swap_to on a majority of `q_pre` cells at L51–59 | False | 4.1 % |
| P3 answer plane: B_ans ≤ 0.5 while B ≈ 0.78 (qualifier applies) | False | A_ans +0.373, B_ans +0.623, B +0.795 |
| P4 share(J_k rem) non-increasing in k; random-k rem ≥ 0.80 at every k | True / True | J rem [0.73, 0.638, 0.612, 0.608]; rand rem [0.983, 0.97, 0.957, 0.947] |
| P5 `_cc` lowers each complement share; `_ccr` within the un-clamped interval | 6/6 lower; 6/6 within | q_rem_pre: cc +0.758 vs +0.795 (ccr +0.794); q_rem25nn_pre: cc +0.580 vs +0.687 (ccr +0.683); q_J2rem_pre: cc +0.578 vs +0.730 (ccr +0.729); q_J8rem_pre: cc +0.520 vs +0.638 (ccr +0.635); q_J25rem_pre: cc +0.511 vs +0.612 (ccr +0.608); q_J64rem_pre: cc +0.514 vs +0.608 (ccr +0.599) |
| P6 current base ≥ B − 0.10; plane rebuilt ≥ 0.5 by block 62? | True / False (≥ 0.5 somewhere in the band: False) | `q_rem_cbr_pre` +0.846, B +0.795, weighted re-entry fraction at L62 0.19, first block ≥ 0.5: none |
| P7 e_J > N(0, Σ) random-k fraction at every k (block means) | False | blocks holding per k: {'2': 27, '8': 27, '25': 24, '64': 8} |

| prediction (Amendment 7) | held? | values |
|---|---|---|
| P1 gates 1–3, 5–8 pass; gate 4 reproduces | True | — |
| P2 ≥ 3 relation types with ≥ 3 admitted items | True | {'city-capital': 11, 'city-language': 3, 'language-capital': 8, 'food-animal': 1, 'river-capital': 6, 'city-currency': 6} |
| P3 generality: J25 rem ∈ [0.45, 0.75]; J25 rem + cc ∈ [0.3, 0.6]; rem + cc ≥ rem − 0.10; A_ans > A | True / True / True / True | +0.612, +0.511, +0.758 vs +0.795, +0.373 vs +0.186 |
| P4 flagged relations show larger A_ans, smaller B_ans | no relation flagged | screen residuals {'city-capital': 0.98, 'city-currency': 1.0, 'city-language': 0.94, 'food-animal': None, 'language-capital': 0.98, 'river-capital': 0.99} |
| P5 repaired current base ≥ B − 0.10, construction check ≈ 1; plane rebuilt ≥ 0.5 by block 62? | True / False | share +0.846, check max 1.009, weighted re-entry at L62 0.19 |

Caveats carried forward from Amendment 5: each row is a fixed state trajectory over blocks 36–62 at `q_pre` (the rows are not a partition of one computation); `q_rem_pre` pins a two-token plane; the J_k rows pin the LS projection onto k greedy atoms of one dictionary (J_NP folded directions), so "J-readable content" here means "content in the span of those atoms"; the atom classes are string-mechanical (translations and related tokens in other scripts fall in *other*); shares are ratios of item means.

## 8. Interpretation, licensed / not licensed, next decision

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
