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
