# two_hop_organism · stage `probe5` — consumer-span control, orthogonalised cross-question planes, functional-row null, where the last layer reads (Amendment 10)

Run `20260924T174658Z`, 20664 forwards, 6118.9 s. Same model and regime as Amendment 9. Parts A, C, D, E: 140 cells (35 admitted items × 4 carriers), cluster = item. Part B: 28 cells (7 pairs), cluster = pair. Shares are ratios of item (pair) means with cluster-bootstrap intervals. Design: Amendment 10 of `H3/design_specs/two_hop_organism.md`; battery `two_hop_probe5.py`; the last section is hand-written.

## 1. Gates

- Reproduction of `probe4`: `full` max |Δ| 6.5e-04; `J25rem` max |Δ| 0.0e+00; `J25rem:ccsA` max |Δ| 0.0e+00; `J25rem:ccsA:m63A` max |Δ| 0.0e+00; `full:sfullA` max |Δ| 0.0e+00; `B:q_xfer` max |Δ| 0.0e+00; `B:x_ctry` max |Δ| 0.0e+00; `B:q_mirror` max |Δ| 0.0e+00; `B:m_ctry` max |Δ| 0.0e+00 — **PASS**.
- Gate L (block-63 cuts): maximum post-softmax weight 0.0e+00 — **PASS**. Part B writes ρ 1.0000–1.0000, κ ≥ 1.0000 — **PASS**. realized-write statistics were not logged for the Part A/C/D/E rows; the write and clamp code is Amendment 9's, and its reference rows reproduce probe4 (see gate_reproduction).
- Part D position classes asserted per cell (T = `q_pre` 19–26, W = 5–18, P = 0–4); Φ′ triggered (Φ/J capture of Δh_s = 1.92).

## 2. Part B: planes orthogonalised against the receiving question's answer

| question (delta) | transfer push (nats) | country plane | answer plane | country ⊥ answer | answer ⊥ country | random | reading |
|---|---|---|---|---|---|---|---|
| language question (capital delta) | +6.75 | 0.80 [0.774, 0.817] | 0.81 [0.777, 0.829] | 0.04 [0.029, 0.060] | 0.07 [0.045, 0.093] | 0.00 [-0.001, 0.007] | **geometry: the transfer runs along the receiving question's answer directions; 'country dominant' is withdrawn and reworded** |
| capital question (language delta) | +5.27 | 0.63 [0.544, 0.702] | 0.52 [0.395, 0.621] | 0.15 [0.132, 0.176] | 0.08 [0.066, 0.100] | 0.01 [0.003, 0.017] | **partial** |

Principal cosines, L51–59: country plane vs language plane [0.86, 0.59]; country plane vs capital plane [0.56, 0.46].

## 3. Part A: the fitted non-lens span at the consumer

R0 (J_25 complement, block-63 read cut, no clamp) = **+0.239** [0.206, 0.277]; with the pinned readable span clamped R_J = **+0.040** [0.025, 0.054]; with the fitted non-lens span Φ clamped R_Φ = **+0.062** [0.041, 0.084]. Without the cut: pinned span +0.413, Φ +0.422. Energy captured of the natural change at s: pinned 0.215, Φ 0.413; of the un-clamped row's change at the answer positions: pinned 0.057, Φ 0.138 → registered reading: **partial**.

## 4. Part C: the functional-row null

Installing the best 25 functional directions f_u = J_lᵀ(γ ⊙ u), u ~ N(0, Cov W_U), gives **+0.125** [0.113, 0.138] of the effect, against +0.390 for the best 25 vocabulary directions (Stage 2, same cells). Complements: functional +0.829, norm- and rank-matched random +0.957. Energy captured on `q_pre`: vocabulary 0.054, functional 0.084 → registered reading: **vocabulary-specific**.

## 5. Part D: where the last layer reads

D0 = share with the answer positions held clean through block 62 = +0.411. Fraction of D0 removed by cutting block 63's read from the answer positions to each class: **T** 1.00 [0.996, 1.002]; **W** -0.02 [-0.025, -0.013]; **P** -0.04 [-0.044, -0.032]. Registered (post hoc) prediction T ≥ 0.7 and W ≤ 0.3: held. Heads carrying ≥ 50 % of the summed direct effect on the first-token margin: [22] (0.98 of it); their attention mass on T / W / P: [[0.59, 0.02, 0.02]].

## 6. Part E: delivery depth

Share delivered with the answer positions held clean through block B and free afterwards: B = 50: 0.922, B = 54: 0.889, B = 58: 0.820, B = 62: 0.411.

## 7. Interpretation, licensed / not licensed, next decision

_Hand-written 2026-09-24 after reading `two_hop_probe5_tables.json`. Every number is copied from §1–6._

### 7.1 What the questions answered

All gates passed. The reference rows reproduce `probe4` to within 7e-4 nats. The attention cuts leak exactly 0. The Part B writes are exact.

| question | result | registered reading |
|---|---|---|
| B. Country, or the receiving question's answer geometry? | In the language question, the country plane alone gives 0.80 of the transfer push and the language plane alone 0.81. The country plane with the language directions projected out gives **0.04** [0.03, 0.06]; random, 0.003. The planes overlap strongly, with principal cosines 0.86 and 0.59. Mirror: country 0.63, capital plane 0.52, country ⊥ capital **0.15** [0.13, 0.18] | Language question: **geometry**. Mirror: **partial** |
| A. Is the consumer route specific to the readable span? | With the last layer's read cut and no clamp, the complement keeps R0 = **0.24** [0.21, 0.28]. The readable span leaves 0.04; a rank-matched fitted non-lens span leaves 0.06, just above the 0.25·R0 bound. The fitted span captures twice the energy of the readable one (0.41 vs 0.21 of the donor change at s). At matched energy (the secondary Φ′) it leaves 0.13 | **Partial**. At matched energy, the readable span blocks 83 % of the route and the non-lens span 46 % (secondary) |
| C. Vocabulary privilege, or any Jacobian direction's? | 25 directions from random output vectors pushed through the same Jacobian install **0.13** [0.11, 0.14], at higher energy (0.084 vs 0.054). The 25 vocabulary directions install 0.39 | **Vocabulary-specific** |
| D. Where does the last layer read? | Cutting block 63's read from the answer positions to the template tokens (the end of the user turn and the assistant header) removes **1.00** [0.996, 1.002] of the last-layer delivery. Cutting the question words or the pre-question tokens removes nothing. One head, **22**, carries 0.98 of the summed direct effect and puts 59 % of its attention on the template tokens | Prediction (T ≥ 0.7, W ≤ 0.3) held |
| E. How late is delivery? | Holding the answer positions clean through block 50, 54, 58 and 62 leaves 0.92, 0.89, 0.82 and 0.41 of the whole question-turn effect | Descriptive |

### 7.2 Corrections this forces

1. **"Country dominant" (Amendment 9) is withdrawn.** It is replaced by: *what carries over to a neighbouring question about the same city runs along that question's own answer directions, which the country's readable plane largely spans.* In the language question, nothing is left once the answer directions are removed. In the capital question a small country-specific part, 0.15, remains.
2. **Claim 1's "privileged per dimension" is now specific to the vocabulary.** Directions that the same Jacobian produces from random output vectors carry a third as much, while capturing more energy.
3. **The bypass is located more precisely.** The last layer reads the donor's change from the template tokens at the end of the question turn, not from the question words. Almost all of that read runs through one attention head. The donor's content reaches the answer positions late: most of it arrives in blocks 59–63.
4. **Precision caveat (smoke finding).** The masked, clamped rows are sensitive to the clamp basis's numerical precision at about the 0.1-nat level. Half-precision storage of the basis moved one such row by 0.12 nats. Treat R_J and R_Φ as ±0.01 of share.

### 7.3 Not licensed

- **"The template tokens hold the answer" as an identity claim.** The data show only that the last layer reads the donor's change from them, and that the J_NP answer readout concentrates there.
- **"The country is irrelevant to the transfer."** In the mirror direction, 0.15 survives the projection.
- **"Readable-specific consumer route."** The registered reading is partial. The matched-energy advantage is secondary.

### 7.4 Next decision

The template tokens at the end of the question turn look like the place where the question-turn state is gathered for the answer. The candidate for the next amendment is to transplant only those eight tokens' states and ask how much of the question-turn effect they carry on their own. The consolidated write-up has been updated with the corrections above.
