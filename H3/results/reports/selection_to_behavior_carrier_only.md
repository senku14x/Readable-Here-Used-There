# H3 · selection_to_behavior — `carrier_only` (Amendment 2: donor carrier states only) — run 20260909T121823Z

324 forwards (85.3 s); triples 2–7, carriers C2/C3, 3 rotations = 36 cells; cluster = triple (n=6). Writes over the assistant-carrier positions only; instruction region and source spans asserted untouched (all blocks). Carrier self-patch bitwise no-op 36/36; carrier ΔNLL max +0.0002; read-back error max 0.

Clean ceilings Δ_B = +13.30, Δ_C = +13.30 nats. Answer-position distance from cleanA at L51–59 under the natural donor arms (cleanB / cleanC, which differ in the tag token): 48.6 / 49.6.

| arm | layers | E_D (nats) | E_D/Δ_D | internal restoration R (L51–59) | greedy: A / target / other | answer-pos distance L51–59 |
|---|---|---|---|---|---|---|
| CarrBtoA | ≥ 36 | +0.332 [+0.218, +0.446] (6/6 >0) | 0.025 | +1.000 [+1.000, +1.000] (6/6 >0) | 36 / 0 / 0 | 4.7 |
| CarrCtoA | ≥ 36 | +0.163 [+0.076, +0.251] (6/6 >0) | 0.012 | +1.000 [+1.000, +1.000] (6/6 >0) | 36 / 0 / 0 | 4.0 |
| CarrBtoA_all | all 64 | +0.564 [+0.378, +0.749] (6/6 >0) | 0.042 | +1.000 [+1.000, +1.000] (6/6 >0) | 36 / 0 / 0 | 6.7 |
| CarrCtoA_all | all 64 | +0.254 [+0.133, +0.375] (6/6 >0) | 0.019 | +1.000 [+1.000, +1.000] (6/6 >0) | 36 / 0 / 0 | 5.8 |
| randCarrB | ≥ 36 | +0.024 [-0.001, +0.049] (4/6 >0) | 0.002 | +0.039 [+0.023, +0.054] (6/6 >0) | 36 / 0 / 0 | 2.9 |

R = 1.000 for the donor arms is by construction (the carrier states read at L51–59 are the donor's own from block 36 on); it is reported as the write gate, not as a finding. The informative rows are E_D, the flips and the answer-position distance.

## Interpretation

**The word organism gives the same shape as the sum organism, and a stronger null.** Replacing the carrier states with those of the pointed-B or pointed-C run (same tokens, teacher-forced; the instruction region and source spans never written) moves the letter margin by 0.025 / 0.012 of the clean separation (+0.33 / +0.16 nats, 6/6, above the matched random write's +0.02) and changes the greedy answer in 0/36 cells; replacing all 64 blocks gives 0.042 / 0.019 and still 0/36. The answer position moves by 4–7 units at L51–59 under the carrier writes against 49 under the natural tag change, i.e. the consumer barely registers the carrier content.

**What this adds to `selection_to_behavior.md`.** The instruction-region transplant moved the answer by 0.25 / 0.19 of the ceiling with the route unidentified. The carrier-only transplant, which installs the donor's entire carrier representation, moves it by 0.025 / 0.012. So the behavioral effect of the instruction-region transplant was not carried through the carrier representation; the remaining candidate is later attention onto the transplanted instruction positions (the tag and instruction tail, which the consumer's query refers to). This is an inference from two interventions, not a route measurement; it is scoped to this consumer and rendering.

**Matched pair with the sum organism.** Both organisms now have the same intervention shape (carrier-only donor, block ≥ 36 and all-depth, matched-norm random control, self-patch gate) and the same outcome: the lens-readable carrier representation is installed at the donor level and the answer does not follow it. Word consumer: E/Δ ≤ 0.04, 0/36 flips. Sum consumer: 8–18 % of the operand-donor margin, 0/32 flips (report). Not licensed: use when the visible source or instruction is unavailable.