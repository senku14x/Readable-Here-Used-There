# H3 · query_local_workspace stage `clampfix32` — Amendment 4: the clamp rows under a float32 residual

**Run:** 702 forwards, 202.5 s, run id 20260910T003315Z; regime: float32 residual from block 35 on, bf16 autocast (Amendment 4). Same cells, conditions, seeds and planes as `clampfix`; cluster = sum (n = 8), carriers averaged. bf16 columns are the committed `clampfix` values.

| condition | parity margin (fp32) | flips | parity (bf16) | report margin (fp32) | flips | report (bf16) | ρ / κ (fp32) | ρ / κ (bf16) | write norm req / real (fp32, report) |
|---|---|---|---|---|---|---|---|---|---|
| `NEC` | +3.16 [+2.15, +4.17] | 18/32 | +3.18 | **+19.27** [+17.89, +20.65] | 32/32 | +19.26 | — | — | — |
| `NEC_Qclamp` | +2.91 [+1.91, +3.92] | 17/32 | +2.94 | **+1.74** [+1.22, +2.27] | 0/32 | +1.75 | 1.000 / 1.000 (min 1.000 / 1.000) | 0.59 / 0.48 | 0.465 / 0.465 |
| `NEC_Qclamp_perpm` | +3.13 [+2.14, +4.13] | 17/32 | +3.16 | **+19.24** [+17.78, +20.70] | 32/32 | +19.21 | 1.000 / 1.000 (min 1.000 / 1.000) | 0.60 / 0.49 | 0.465 / 0.465 |
| `NEC_Qclamp_noans` | +3.12 [+2.15, +4.09] | 18/32 | +3.15 | **+11.84** [+10.35, +13.33] | 20/32 | +11.79 | 1.000 / 1.000 (min 1.000 / 1.000) | 0.58 / 0.47 | 0.413 / 0.413 |
| `NEC_Qclamp_noans_perpm` | +3.17 [+2.18, +4.16] | 18/32 | +3.18 | **+19.24** [+17.84, +20.64] | 32/32 | +19.22 | 1.000 / 1.000 (min 1.000 / 1.000) | 0.59 / 0.47 | 0.413 / 0.413 |
| `NEC_Qclamp_ansonly` | +2.94 [+1.91, +3.97] | 17/32 | +2.96 | **+5.57** [+4.16, +6.97] | 0/32 | +5.56 | 1.000 / 1.000 (min 1.000 / 1.000) | 0.85 / 0.77 | 2.498 / 2.498 |
| `NEC_Qclamp_ansonly_perpm` | +3.15 [+2.16, +4.14] | 18/32 | +3.15 | **+19.26** [+17.78, +20.73] | 32/32 | +19.24 | 1.000 / 1.000 (min 1.000 / 1.000) | 0.86 / 0.78 | 2.498 / 2.498 |

Report margin removed by the emission-excluded naming clamp: **38.5 %** (fp32) vs 38.8 % (bf16); by the all-question-token clamp: 91.0 %.
Carrier ΔNLL (condition − clean), max over cells and conditions: +0.0008 nats.
ρ / κ are means over the 26 layers with a nonzero requested write (block 36 requests nothing at the question positions; see AMENDMENT_4 gate note). Plane read-back error after the naming clamps, max over cells: 5.3e-05 (bf16: 0.14–0.21).
