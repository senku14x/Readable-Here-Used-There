# H3 · selection_to_behavior — `carrier_only` (Amendment 2: donor carrier states only) — run 20260909T165327Z

324 forwards (35.5 s); triples 2–7, carriers C2/C3, 3 rotations = 36 cells; cluster = triple (n=6). Writes over the assistant-carrier positions only; instruction region and source spans asserted untouched (all blocks). Carrier self-patch bitwise no-op 36/36; carrier ΔNLL max +0.0008; read-back error max 0.

Clean ceilings Δ_B = +36.78, Δ_C = +34.55 nats. Answer-position distance from cleanA at L51–59 under the natural donor arms (cleanB / cleanC, which differ in the tag token): 336.5 / 332.9.

| arm | layers | E_D (nats) | E_D/Δ_D | internal restoration R (L51–59) | greedy: A / target / other | answer-pos distance L51–59 |
|---|---|---|---|---|---|---|
| CarrBtoA | ≥ 36 | +0.531 [+0.216, +0.847] (6/6 >0) | 0.014 | +1.000 [+1.000, +1.000] (6/6 >0) | 36 / 0 / 0 | 39.3 |
| CarrCtoA | ≥ 36 | +0.545 [+0.269, +0.821] (6/6 >0) | 0.016 | +1.000 [+1.000, +1.000] (6/6 >0) | 36 / 0 / 0 | 39.7 |
| CarrBtoA_all | all 64 | +0.528 [+0.161, +0.894] (6/6 >0) | 0.014 | +1.000 [+1.000, +1.000] (6/6 >0) | 36 / 0 / 0 | 40.7 |
| CarrCtoA_all | all 64 | +0.545 [+0.240, +0.850] (5/6 >0) | 0.016 | +1.000 [+1.000, +1.000] (6/6 >0) | 36 / 0 / 0 | 41.0 |
| randCarrB | ≥ 36 | +0.056 [-0.022, +0.133] (3/6 >0) | 0.002 | +0.049 [+0.012, +0.087] (6/6 >0) | 36 / 0 / 0 | 28.5 |

R = 1.000 for the donor arms is by construction (the carrier states read at L51–59 are the donor's own from block 36 on); it is reported as the write gate, not as a finding. The informative rows are E_D, the flips and the answer-position distance.

## Interpretation

(written by hand; see `selection_to_behavior.md` §6)