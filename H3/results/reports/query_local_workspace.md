# H3 · query_local_workspace — `queryread` — run 20260909T141648Z

446 forwards (111.9 s); 8 sums × ['C0', 'C1', 'C2', 'C3'] × parity + report; donor map offset 3; Q band blocks 36–62; cluster = sum (n=8). Parity is the primary consumer for coordinate-level rows (Q_swap, NEC_Qclamp); report is steering-susceptible there.

**Gates.** Carrier ΔNLL max +0.0019.

## consumer `parity` (primary)

| condition | behavioral margin (nats) | flips → donor value | flips → own value | J_NP sum shift at Q, L51–59 | RESID_P pair-axis shift at Q | LOGITS shift at Q | J_NP sum shift at carrier | answer-pos dist L51–59 |
|---|---|---|---|---|---|---|---|---|
| O_donor | +3.880 [+2.982, +4.778] (8/8) | 23/32 | 9/32 | +0.664 [+0.534, +0.794] (8/8) | +0.124 [+0.053, +0.195] (8/8) | +2.700 [+1.992, +3.408] (8/8) | +1.562 [+1.320, +1.805] (8/8) | 57.2 |
| C_full | +0.702 [+0.188, +1.215] (8/8) | 0/32 | 32/32 | +0.140 [+0.092, +0.188] (8/8) | +0.011 [-0.009, +0.031] (5/8) | +0.889 [+0.619, +1.159] (8/8) | +1.615 [+1.433, +1.797] (8/8) | 12.8 |
| NEC | +3.180 [+2.212, +4.147] (8/8) | 17/32 | 15/32 | +0.526 [+0.422, +0.630] (8/8) | +0.104 [+0.040, +0.167] (8/8) | +1.807 [+1.313, +2.302] (8/8) | +0.000 [+0.000, +0.000] (0/8) | 52.2 |

## consumer `report` (steering-susceptible for coordinate rows)

| condition | behavioral margin (nats) | flips → donor value | flips → own value | J_NP sum shift at Q, L51–59 | RESID_P pair-axis shift at Q | LOGITS shift at Q | J_NP sum shift at carrier | answer-pos dist L51–59 |
|---|---|---|---|---|---|---|---|---|
| O_donor | +21.211 [+19.911, +22.512] (8/8) | 32/32 | 0/32 | +1.432 [+1.232, +1.632] (8/8) | +0.363 [+0.291, +0.435] (8/8) | +5.353 [+4.702, +6.003] (8/8) | +1.552 [+1.317, +1.787] (8/8) | 55.3 |
| C_full | +1.751 [+1.169, +2.334] (8/8) | 0/32 | 32/32 | +0.189 [+0.105, +0.274] (8/8) | +0.033 [+0.014, +0.051] (8/8) | +1.158 [+0.801, +1.516] (8/8) | +1.616 [+1.426, +1.806] (8/8) | 7.7 |
| NEC | +19.261 [+17.917, +20.605] (8/8) | 32/32 | 0/32 | +1.252 [+1.091, +1.413] (8/8) | +0.328 [+0.250, +0.405] (8/8) | +4.162 [+3.691, +4.632] (8/8) | +0.000 [+0.000, +0.000] (0/8) | 53.6 |

## Own-sum presence (z_own − mean decoys, L51–59) under clean, at the carrier vs the question positions

- parity: carrier +1.908 [+1.159, +2.657] (8/8); question positions +0.706 [+0.017, +1.394] (7/8)
- report: carrier +1.902 [+1.160, +2.644] (8/8); question positions +3.058 [+2.360, +3.757] (8/8)

# H3 · query_local_workspace — `querycausal` — run 20260909T141909Z

766 forwards (204.4 s); 8 sums × ['C0', 'C1', 'C2', 'C3'] × parity + report; donor map offset 3; Q band blocks 36–62; cluster = sum (n=8). Parity is the primary consumer for coordinate-level rows (Q_swap, NEC_Qclamp); report is steering-susceptible there.

**Gates.** Carrier ΔNLL max +0.0007. Q_own bitwise: 64/64. Clamp read-back error max 2.06e-01; clamp write norm (NEC_Qclamp / perp): 0.35 / 0.15.

## consumer `parity` (primary)

| condition | behavioral margin (nats) | flips → donor value | flips → own value | J_NP sum shift at Q, L51–59 | RESID_P pair-axis shift at Q | LOGITS shift at Q | J_NP sum shift at carrier | answer-pos dist L51–59 |
|---|---|---|---|---|---|---|---|---|
| NEC | +3.180 [+2.212, +4.147] (8/8) | 17/32 | 15/32 | +0.526 [+0.422, +0.630] (8/8) | +0.104 [+0.040, +0.167] (8/8) | +1.807 [+1.313, +2.302] (8/8) | +0.000 [+0.000, +0.000] (0/8) | 52.2 |
| Q_own | +0.000 [+0.000, +0.000] (0/8) | 0/32 | 32/32 | +0.000 [+0.000, +0.000] (0/8) | +0.000 [+0.000, +0.000] (0/8) | +0.000 [+0.000, +0.000] (0/8) | +0.000 [+0.000, +0.000] (0/8) | 0.0 |
| Q_donor_50 | +4.050 [+2.844, +5.256] (8/8) | 21/32 | 11/32 | +0.190 [+0.120, +0.259] (8/8) | +0.015 [-0.129, +0.158] (4/8) | +0.153 [+0.071, +0.235] (8/8) | +0.000 [+0.000, +0.000] (0/8) | 51.9 |
| Q_donor_62 | +6.885 [+6.196, +7.574] (8/8) | 32/32 | 0/32 | +0.763 [+0.605, +0.920] (8/8) | +0.115 [-0.053, +0.283] (5/8) | +2.557 [+1.857, +3.257] (8/8) | +0.000 [+0.000, +0.000] (0/8) | 75.2 |
| Q_rand | +0.355 [-0.157, +0.868] (7/8) | 0/32 | 32/32 | +0.032 [+0.014, +0.049] (8/8) | -0.010 [-0.019, -0.002] (1/8) | +0.049 [-0.012, +0.110] (6/8) | +0.000 [+0.000, +0.000] (0/8) | 75.2 |
| Q_swap | +0.220 [-0.130, +0.570] (5/8) | 0/32 | 32/32 | +0.418 [-0.604, +1.440] (6/8) | +0.071 [-0.263, +0.405] (5/8) | +2.003 [+1.266, +2.741] (8/8) | +0.000 [+0.000, +0.000] (0/8) | 9.4 |
| NEC_Qclamp | +2.943 [+1.965, +3.921] (8/8) | 16/32 | 16/32 | -0.002 [-0.011, +0.007] (3/8) | +0.009 [-0.060, +0.077] (5/8) | +0.095 [+0.033, +0.157] (8/8) | +0.000 [+0.000, +0.000] (0/8) | 50.4 |
| NEC_Qclamp_perp | +3.171 [+2.208, +4.135] (8/8) | 17/32 | 15/32 | +0.526 [+0.421, +0.630] (8/8) | +0.104 [+0.037, +0.170] (8/8) | +1.807 [+1.313, +2.300] (8/8) | +0.000 [+0.000, +0.000] (0/8) | 52.2 |

## consumer `report` (steering-susceptible for coordinate rows)

| condition | behavioral margin (nats) | flips → donor value | flips → own value | J_NP sum shift at Q, L51–59 | RESID_P pair-axis shift at Q | LOGITS shift at Q | J_NP sum shift at carrier | answer-pos dist L51–59 |
|---|---|---|---|---|---|---|---|---|
| NEC | +19.261 [+17.917, +20.605] (8/8) | 32/32 | 0/32 | +1.252 [+1.091, +1.413] (8/8) | +0.328 [+0.250, +0.405] (8/8) | +4.162 [+3.691, +4.632] (8/8) | +0.000 [+0.000, +0.000] (0/8) | 53.6 |
| Q_own | +0.000 [+0.000, +0.000] (0/8) | 0/32 | 32/32 | +0.000 [+0.000, +0.000] (0/8) | +0.000 [+0.000, +0.000] (0/8) | +0.000 [+0.000, +0.000] (0/8) | +0.000 [+0.000, +0.000] (0/8) | 0.0 |
| Q_donor_50 | +0.724 [+0.456, +0.992] (8/8) | 0/32 | 32/32 | +0.245 [+0.140, +0.351] (8/8) | +0.130 [+0.061, +0.199] (8/8) | +0.162 [+0.078, +0.246] (8/8) | +0.000 [+0.000, +0.000] (0/8) | 17.0 |
| Q_donor_62 | +20.488 [+18.971, +22.006] (8/8) | 32/32 | 0/32 | +1.512 [+1.311, +1.714] (8/8) | +0.402 [+0.311, +0.492] (8/8) | +5.143 [+4.521, +5.765] (8/8) | +0.000 [+0.000, +0.000] (0/8) | 56.7 |
| Q_rand | +1.358 [+0.763, +1.954] (8/8) | 0/32 | 32/32 | +0.078 [+0.046, +0.111] (8/8) | +0.011 [+0.003, +0.020] (8/8) | +0.150 [+0.023, +0.278] (6/8) | +0.000 [+0.000, +0.000] (0/8) | 56.7 |
| Q_swap | +11.072 [+8.257, +13.886] (8/8) | 19/32 | 12/32 | +0.857 [-0.202, +1.917] (6/8) | +0.164 [-0.169, +0.497] (6/8) | +3.713 [+3.106, +4.319] (8/8) | +0.000 [+0.000, +0.000] (0/8) | 11.2 |
| NEC_Qclamp | +1.747 [+1.237, +2.258] (8/8) | 0/32 | 32/32 | -0.003 [-0.020, +0.014] (5/8) | +0.090 [+0.000, +0.179] (7/8) | +0.039 [-0.035, +0.112] (5/8) | +0.000 [+0.000, +0.000] (0/8) | 51.8 |
| NEC_Qclamp_perp | +19.196 [+17.847, +20.546] (8/8) | 32/32 | 0/32 | +1.250 [+1.089, +1.412] (8/8) | +0.326 [+0.248, +0.404] (8/8) | +4.159 [+3.687, +4.632] (8/8) | +0.000 [+0.000, +0.000] (0/8) | 53.5 |

# H3 · query_local_workspace — `clampsplit` — run 20260909T142727Z

446 forwards (114.9 s); 8 sums × ['C0', 'C1', 'C2', 'C3'] × parity + report; donor map offset 3; Q band blocks 36–62; cluster = sum (n=8). Parity is the primary consumer for coordinate-level rows (Q_swap, NEC_Qclamp); report is steering-susceptible there.

**Gates.** Carrier ΔNLL max +0.0007.

## consumer `parity` (primary)

| condition | behavioral margin (nats) | flips → donor value | flips → own value | J_NP sum shift at Q, L51–59 | RESID_P pair-axis shift at Q | LOGITS shift at Q | J_NP sum shift at carrier | answer-pos dist L51–59 |
|---|---|---|---|---|---|---|---|---|
| NEC | +3.180 [+2.212, +4.147] (8/8) | 17/32 | 15/32 | +0.526 [+0.422, +0.630] (8/8) | +0.104 [+0.040, +0.167] (8/8) | +1.807 [+1.313, +2.302] (8/8) | +0.000 [+0.000, +0.000] (0/8) | 52.2 |
| NEC_Qclamp_noans | +3.148 [+2.209, +4.086] (8/8) | 17/32 | 15/32 | +0.249 [+0.162, +0.336] (8/8) | +0.044 [-0.025, +0.113] (6/8) | +0.385 [+0.300, +0.470] (8/8) | +0.000 [+0.000, +0.000] (0/8) | 52.2 |
| NEC_Qclamp_ansonly | +2.965 [+1.960, +3.969] (8/8) | 16/32 | 16/32 | +0.272 [+0.219, +0.325] (8/8) | +0.068 [+0.006, +0.130] (6/8) | +1.377 [+0.965, +1.789] (8/8) | +0.000 [+0.000, +0.000] (0/8) | 50.5 |

## consumer `report` (steering-susceptible for coordinate rows)

| condition | behavioral margin (nats) | flips → donor value | flips → own value | J_NP sum shift at Q, L51–59 | RESID_P pair-axis shift at Q | LOGITS shift at Q | J_NP sum shift at carrier | answer-pos dist L51–59 |
|---|---|---|---|---|---|---|---|---|
| NEC | +19.261 [+17.917, +20.605] (8/8) | 32/32 | 0/32 | +1.252 [+1.091, +1.413] (8/8) | +0.328 [+0.250, +0.405] (8/8) | +4.162 [+3.691, +4.632] (8/8) | +0.000 [+0.000, +0.000] (0/8) | 53.6 |
| NEC_Qclamp_noans | +11.786 [+10.292, +13.280] (8/8) | 20/32 | 10/32 | +0.289 [+0.243, +0.335] (8/8) | +0.136 [+0.054, +0.219] (8/8) | +0.439 [+0.375, +0.504] (8/8) | +0.000 [+0.000, +0.000] (0/8) | 53.5 |
| NEC_Qclamp_ansonly | +5.560 [+4.143, +6.978] (8/8) | 0/32 | 32/32 | +0.956 [+0.840, +1.071] (8/8) | +0.280 [+0.204, +0.357] (8/8) | +3.593 [+3.140, +4.046] (8/8) | +0.000 [+0.000, +0.000] (0/8) | 51.8 |

# H3 · query_local_workspace — `nosource` — run 20260909T142306Z

574 forwards (149.9 s); 8 sums × ['C0', 'C1', 'C2', 'C3'] × parity + report; donor map offset 3; Q band blocks 36–62; cluster = sum (n=8). Parity is the primary consumer for coordinate-level rows (Q_swap, NEC_Qclamp); report is steering-susceptible there.

**Gates.** Carrier ΔNLL max +0.0169.

## consumer `parity` (primary)

| condition | behavioral margin (nats) | flips → donor value | flips → own value | J_NP sum shift at Q, L51–59 | RESID_P pair-axis shift at Q | LOGITS shift at Q | J_NP sum shift at carrier | answer-pos dist L51–59 |
|---|---|---|---|---|---|---|---|---|
| C_from_S | -0.121 [-0.216, -0.025] (2/8) | 16/32 | 16/32 | -0.075 [-0.119, -0.030] (0/8) | -0.009 [-0.051, +0.033] (3/8) | -0.690 [-0.940, -0.439] (0/8) | -0.802 [-1.050, -0.553] (0/8) | 23.0 |
| C_from_S2 | +0.121 [+0.025, +0.216] (6/8) | 16/32 | 16/32 | +0.073 [+0.031, +0.115] (8/8) | +0.004 [-0.036, +0.043] (3/8) | +0.676 [+0.415, +0.938] (8/8) | +0.814 [+0.537, +1.090] (8/8) | 23.0 |
| C_rand_ns | -0.008 [-0.044, +0.028] (4/8) | 16/32 | 16/32 | -0.001 [-0.011, +0.008] (3/8) | +0.009 [-0.019, +0.036] (6/8) | -0.008 [-0.024, +0.009] (5/8) | -0.003 [-0.061, +0.055] (4/8) | 8.4 |
| Q_from_S | -3.590 [-4.180, -2.999] (0/8) | 0/32 | 32/32 | -0.371 [-0.494, -0.248] (0/8) | -0.031 [-0.295, +0.234] (5/8) | -1.309 [-1.884, -0.735] (0/8) | +0.000 [+0.000, +0.000] (0/8) | 113.2 |

## consumer `report` (steering-susceptible for coordinate rows)

| condition | behavioral margin (nats) | flips → donor value | flips → own value | J_NP sum shift at Q, L51–59 | RESID_P pair-axis shift at Q | LOGITS shift at Q | J_NP sum shift at carrier | answer-pos dist L51–59 |
|---|---|---|---|---|---|---|---|---|
| C_from_S | -3.773 [-4.365, -3.182] (0/8) | 1/32 | 21/32 | -0.132 [-0.235, -0.028] (0/8) | -0.020 [-0.109, +0.069] (4/8) | -1.085 [-1.462, -0.708] (0/8) | -0.802 [-1.054, -0.551] (0/8) | 34.6 |
| C_from_S2 | +3.827 [+3.003, +4.650] (8/8) | 21/32 | 3/32 | +0.136 [+0.024, +0.248] (7/8) | +0.013 [-0.069, +0.095] (5/8) | +1.051 [+0.670, +1.431] (8/8) | +0.814 [+0.531, +1.097] (8/8) | 34.6 |
| C_rand_ns | +0.014 [-0.090, +0.119] (6/8) | 4/32 | 4/32 | +0.004 [-0.013, +0.020] (4/8) | -0.001 [-0.035, +0.032] (5/8) | -0.008 [-0.029, +0.013] (4/8) | -0.009 [-0.089, +0.070] (4/8) | 9.7 |
| Q_from_S | -10.714 [-12.260, -9.169] (0/8) | 0/32 | 32/32 | -0.745 [-1.044, -0.445] (0/8) | -0.195 [-0.363, -0.028] (1/8) | -2.663 [-3.307, -2.019] (0/8) | +0.000 [+0.000, +0.000] (0/8) | 107.3 |

## Absent-source endpoint: log P(S) − log P(S2) at the answer, and argmax identity

| consumer | condition | Δ[logP(S) − logP(S2)] vs clean_ns | argmax = S | argmax = S2 |
|---|---|---|---|---|
| parity | clean_ns | +0.000 [+0.000, +0.000] (0/8) | 16/32 | 16/32 |
| parity | C_from_S | +0.121 [+0.025, +0.216] (6/8) | 16/32 | 16/32 |
| parity | C_from_S2 | -0.121 [-0.216, -0.025] (2/8) | 16/32 | 16/32 |
| parity | C_rand_ns | +0.008 [-0.028, +0.044] (4/8) | 16/32 | 16/32 |
| parity | Q_from_S | +3.590 [+2.999, +4.180] (8/8) | 32/32 | 0/32 |
| report | clean_ns | +0.000 [+0.000, +0.000] (0/8) | 4/32 | 4/32 |
| report | C_from_S | +3.773 [+3.182, +4.365] (8/8) | 21/32 | 1/32 |
| report | C_from_S2 | -3.827 [-4.650, -3.003] (0/8) | 3/32 | 21/32 |
| report | C_rand_ns | -0.014 [-0.119, +0.090] (2/8) | 4/32 | 4/32 |
| report | Q_from_S | +10.714 [+9.169, +12.260] (8/8) | 32/32 | 0/32 |
- report greedy under `clean_ns`: greedy = S in 0/32; most common tokens [('a', 32)]
- report greedy under `C_from_S`: greedy = S in 0/32; most common tokens [('a', 32)]
- report greedy under `C_from_S2`: greedy = S in 0/32; most common tokens [('a', 32)]
- report greedy under `Q_from_S`: greedy = S in 25/32; most common tokens [('seven', 4), ('eight', 4), ('nine', 4), ('ten', 4)]

# H3 · query_local_workspace — `nosource2` — run 20260909T144856Z

574 forwards (149.6 s); 8 sums × ['C0', 'C1', 'C2', 'C3'] × parity + report; donor map offset 3; Q band blocks 36–62; cluster = sum (n=8). Parity is the primary consumer for coordinate-level rows (Q_swap, NEC_Qclamp); report is steering-susceptible there.

**Gates.** Carrier ΔNLL max +0.0263.

## consumer `parity` (primary)

| condition | behavioral margin (nats) | flips → donor value | flips → own value | J_NP sum shift at Q, L51–59 | RESID_P pair-axis shift at Q | LOGITS shift at Q | J_NP sum shift at carrier | answer-pos dist L51–59 |
|---|---|---|---|---|---|---|---|---|
| C_from_S | -0.114 [-0.381, +0.154] (4/8) | 16/32 | 16/32 | -0.085 [-0.144, -0.025] (0/8) | -0.014 [-0.061, +0.034] (4/8) | -0.638 [-0.926, -0.351] (0/8) | -0.802 [-1.054, -0.549] (0/8) | 24.5 |
| C_from_S2 | +0.114 [-0.154, +0.381] (4/8) | 16/32 | 16/32 | +0.086 [+0.020, +0.151] (7/8) | +0.013 [-0.027, +0.052] (5/8) | +0.636 [+0.325, +0.946] (8/8) | +0.814 [+0.530, +1.097] (8/8) | 24.5 |
| C_rand_ns | +0.004 [-0.111, +0.119] (4/8) | 16/32 | 16/32 | -0.002 [-0.014, +0.011] (4/8) | -0.001 [-0.024, +0.022] (4/8) | +0.001 [-0.014, +0.015] (5/8) | -0.006 [-0.061, +0.050] (4/8) | 8.0 |
| Q_from_S | -3.565 [-4.438, -2.691] (0/8) | 0/32 | 32/32 | -0.371 [-0.556, -0.186] (0/8) | -0.023 [-0.582, +0.535] (5/8) | -1.311 [-1.714, -0.908] (0/8) | +0.000 [+0.000, +0.000] (0/8) | 132.6 |

## consumer `report` (steering-susceptible for coordinate rows)

| condition | behavioral margin (nats) | flips → donor value | flips → own value | J_NP sum shift at Q, L51–59 | RESID_P pair-axis shift at Q | LOGITS shift at Q | J_NP sum shift at carrier | answer-pos dist L51–59 |
|---|---|---|---|---|---|---|---|---|
| C_from_S | -4.016 [-4.473, -3.559] (0/8) | 0/32 | 28/32 | -0.212 [-0.311, -0.113] (0/8) | -0.056 [-0.135, +0.022] (3/8) | -1.358 [-1.674, -1.042] (0/8) | -0.802 [-1.052, -0.553] (0/8) | 55.0 |
| C_from_S2 | +4.152 [+3.399, +4.906] (8/8) | 28/32 | 1/32 | +0.212 [+0.076, +0.348] (7/8) | +0.048 [-0.036, +0.133] (4/8) | +1.348 [+0.979, +1.717] (8/8) | +0.814 [+0.531, +1.097] (8/8) | 55.0 |
| C_rand_ns | +0.049 [-0.062, +0.159] (5/8) | 4/32 | 4/32 | +0.003 [-0.015, +0.021] (3/8) | -0.015 [-0.068, +0.037] (2/8) | +0.011 [-0.018, +0.041] (6/8) | -0.010 [-0.092, +0.071] (5/8) | 14.6 |
| Q_from_S | -10.780 [-11.950, -9.610] (0/8) | 0/32 | 32/32 | -0.745 [-1.004, -0.485] (0/8) | -0.184 [-0.748, +0.380] (4/8) | -2.667 [-3.050, -2.285] (0/8) | +0.000 [+0.000, +0.000] (0/8) | 118.4 |

## Absent-source endpoint: log P(S) − log P(S2) at the answer, and argmax identity

| consumer | condition | Δ[logP(S) − logP(S2)] vs clean_ns | argmax = S | argmax = S2 |
|---|---|---|---|---|
| parity | clean_ns | +0.000 [+0.000, +0.000] (0/8) | 16/32 | 16/32 |
| parity | C_from_S | +0.114 [-0.154, +0.381] (4/8) | 16/32 | 16/32 |
| parity | C_from_S2 | -0.114 [-0.381, +0.154] (4/8) | 16/32 | 16/32 |
| parity | C_rand_ns | -0.004 [-0.119, +0.111] (4/8) | 16/32 | 16/32 |
| parity | Q_from_S | +3.565 [+2.691, +4.438] (8/8) | 32/32 | 0/32 |
| report | clean_ns | +0.000 [+0.000, +0.000] (0/8) | 4/32 | 4/32 |
| report | C_from_S | +4.016 [+3.559, +4.473] (8/8) | 28/32 | 0/32 |
| report | C_from_S2 | -4.152 [-4.906, -3.399] (0/8) | 1/32 | 28/32 |
| report | C_rand_ns | -0.049 [-0.159, +0.062] (3/8) | 4/32 | 4/32 |
| report | Q_from_S | +10.780 [+9.610, +11.950] (8/8) | 32/32 | 0/32 |
- report greedy under `clean_ns`: greedy = S in 0/32; most common tokens [('unknown', 24), ('two', 8)]
- report greedy under `C_from_S`: greedy = S in 10/32; most common tokens [('1', 9), ('hidden', 7), ('7', 3), ('eight', 3)]
- report greedy under `C_from_S2`: greedy = S in 0/32; most common tokens [('1', 9), ('hidden', 7), ('7', 3), ('eight', 3)]
- report greedy under `Q_from_S`: greedy = S in 25/32; most common tokens [('seven', 4), ('eight', 4), ('nine', 4), ('ten', 4)]

## Interpretation (hand-written 2026-09-09, after all five stages)

**Gates.** Q self-patch bitwise 64/64; operand span, carrier and prefix asserted untouched under every question-site write; clamp write norms 0.35 (naming plane) vs 0.15 (orthogonal control plane, so the control is if anything gentler); carrier ΔNLL ≤ 0.002 in every stage except `nosource2`, where two of 256 writes reach 0.026 (the `Q_from_S` positive control on two cells; the load-bearing `C_from_S` rows have mean 0.0003, max 0.0025). The registered 0.02 bound is therefore met for every row that carries a conclusion and marginally exceeded on two positive-control cells; reported, not repaired.

**1. The sum is reconstructed at the question positions without the carrier copy (prediction 1 met).** Under `NEC` — donor operands, carrier clamped to the recipient's own state — the donor sum appears at the question positions on J_NP (+0.53 parity / +1.25 report vs +0.66 / +1.43 under the free operand donor), on the plain-sentence number axis (+0.10 / +0.33 vs +0.12 / +0.36) and on the question-position logits (+1.8 / +4.2 vs +2.7 / +5.4): 80–90 % of its free-carrier level, 8/8 on every instrument. The carrier donor alone puts almost none of it there (+0.14 / +0.19 on J_NP). So the consumer-local representation is rebuilt from operand-origin state when the question arrives, not propagated from the carrier. Under clean prompts the own sum is also readable at the question positions (parity +0.71, 7/8; report +3.06, which includes the emission position).

**2. Whether that reconstructed sum is consumed depends on what the consumer computes (predictions 3–4 partially met, in the informative direction).** Clamping the own/donor naming plane at the question tokens — answer position excluded — erases the donor sum there on all three instruments (J_NP +1.25 → +0.29, LOGITS +4.2 → +0.44):
- **parity** does not change: +3.18 → +3.15 nats, 17/32 → 17/32 flips; the orthogonal-plane clamp gives +3.17, 17/32. Parity is computable from the two operands' parities without a sum, and the data say it is: the readable sum at the question is bypassed by this consumer.
- **report** loses about 40 % of its margin and a third of its flips: +19.3 → +11.8 nats, 32/32 → 20/32. The consumer that needs the value partly depends on the reconstructed representation; the rest is carried by the answer position's own state, which the clamp leaves alone and which the operand donor also reaches directly.
- Clamping the answer position only (the emission site) gives +5.6 nats, 0/32 on report and +2.97, 16/32 on parity: for report this is output suppression, as registered, and it is why the whole-Q clamp (`NEC_Qclamp`: +1.75, 0/32) cannot be read on report.
So the outcome-table row is **reconstructed and partially mediating** for the sum-requiring consumer, and **reconstructed and bypassed** for the consumer whose function does not require the sum. That is a function-specific answer, not a single verdict on "the workspace".

**3. Decision-position donors bound where each answer is settled (prediction 2 met).** Donor states at blocks 36–50 over the question positions flip parity 21/32 at the operand-donor level and report 0/32; extending the band to 36–62 flips both 32/32 (report +20.5). Parity is fixed in the question-position residuals by block 50; report is not until later. No mechanism is identified by this.

**4. The paper-style coordinate swap at the question is answer-token steering.** `Q_swap` (own↔donor sum-word naming coordinates at the question positions only, 36–62) flips report 19/32 at +11.1 nats — the same as the global swap of Amendment 3, so all of that swap's report effect came from the question positions — and leaves parity at +0.22 (CI includes 0), 0/32. A full-residual donor at the same positions flips parity 32/32. The swap moves the consumer that emits the swapped words and not the one that computes a different function of the same value.

**5. The carrier copy is consumed when it is the only place the sum exists (`nosource`, `nosource2`; no prior registered).** In a recipient with no operand tokens ("Here is a pair of numbers (hidden)"), whose clean answer is "unknown" in 24/32 cells and at chance among the sum words, transplanting the carrier states of a real run with sum S (all 64 blocks) makes S the best-scored sum word in **28/32** cells (+4.0 nats over the alternative, 8/8); the S₂ carrier does the same for S₂ (28/32, −4.2); a norm-matched random carrier does nothing (4/32, +0.05). The greedy token moves from "unknown" to the sum in 14/32 cells (word or full digit) and to the leading digit "1" of a two-digit sum in 9 more. The placeholder rendering (`nosource`, "a and b") gives the same scored result (21/32) with the greedy captured by the placeholder letter. Parity does not follow the carrier (16/32, +0.11): with no operands there are no operand parities to combine, and the carrier sum is not converted into one — consistent with §2. The question-position donor is the positive control (32/32 both consumers).

**What this changes, in one paragraph.** The maintained carrier copy is not epiphenomenal: it is consumed when the source is unavailable (§5) and ignored when the source is visible (`computed_sum_consumer` §11), which is a redundancy result, not a non-use result. At the question, the sum is rebuilt from operand-origin state (§1); the consumer whose function needs the value draws on that rebuilt representation for about 40 % of its answer margin (§2), the consumer whose function does not need it bypasses it entirely (§2), and the paper's own coordinate-swap method reads out on this organism as steering of the emitted word rather than substitution of the computed value (§4). Scope: Qwen3.6-27B, thinking off, eight sums, four carriers, one donor map, one cut band; the recurrent channel is never closed; no read-site component is identified.
