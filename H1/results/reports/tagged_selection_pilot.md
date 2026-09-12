# H1 · tagged selection — pilot results (run 20260907T000038Z)

## 1. Question and setup

Does the instruction select which of three tagged sources is carried to the later readout, or scale whichever word is sourced? Triples [('orange', 'tiger', 'castle'), ('diamond', 'rocket', 'dragon'), ('forest', 'hammer', 'horse'), ('lion', 'knife', 'fork')], three rotations each, carriers ['C0', 'C1'], arms pointed A/B/C and control; each source replaced from block 36 by its donor ({'orange': 'diamond', 'tiger': 'rocket', 'castle': 'dragon', 'diamond': 'forest', 'rocket': 'hammer', 'dragon': 'horse', 'forest': 'lion', 'hammer': 'knife', 'horse': 'fork', 'lion': 'orange', 'knife': 'tiger', 'fork': 'castle'}); readout per source = its own pair margin on J_NP, RESID_P and LOGITS at interior carrier positions, windows L48–50 and L51–59. Cluster = triple (n=4). State moves: frozen single-word ĝ (cos with this organism's native shared direction 0.65), native d_shared, native pointer contrast d_pointer(A→B) (cos with ĝ -0.03, |d| 3.69 vs |d_shared| 8.44). 1536 forwards; same-source and layer<36 identity asserted per cell.

## 2. Main findings

- **J_NP|L48-50:** pointed-source transfer C(self) +0.3937 [+0.3234, +0.4640] (4/4 >0); unpointed C(other) +0.0783 [+0.0366, +0.1200] (4/4 >0); control C(ctrl) +0.0739 [+0.0307, +0.1170] (4/4 >0). **S = +0.3154 [+0.2668, +0.3640] (4/4 >0)**; Q = +0.0045 [-0.0005, +0.0094] (4/4 >0); U = +0.3199 [+0.2690, +0.3707] (4/4 >0); S/U 0.99.
  - ĝ move (pointed→control level): ΔC pointed -0.0311 [-0.0359, -0.0263] (0/4 >0), ΔC unpointed -0.0106 [-0.0216, +0.0004] (0/4 >0); ratio pointed +0.9204 [+0.9018, +0.9389] (4/4 >0), unpointed +0.8688 [+0.7399, +0.9976] (4/4 >0); P index +0.0516 [-0.0660, +0.1692] (3/4 >0). d_shared: ΔC pointed -0.0754 [-0.0952, -0.0555] (0/4 >0), unpointed -0.0127 [-0.0305, +0.0051] (1/4 >0). d_pointer A→B under pointed-A: ΔC_A -0.0197 [-0.0599, +0.0205] (0/4 >0), ΔC_B +0.1402 [+0.1220, +0.1584] (4/4 >0), ΔC_C +0.0127 [+0.0045, +0.0209] (4/4 >0), redistribution B−A +0.1600 [+0.1139, +0.2060] (4/4 >0). Reverse ĝ on control (one-sided) ΔC all sources +0.0172 [+0.0080, +0.0264] (4/4 >0).
- **J_NP|L51-59:** pointed-source transfer C(self) +4.5653 [+3.8637, +5.2668] (4/4 >0); unpointed C(other) +1.1490 [+1.0047, +1.2934] (4/4 >0); control C(ctrl) +1.2752 [+1.1155, +1.4349] (4/4 >0). **S = +3.4163 [+2.8035, +4.0290] (4/4 >0)**; Q = -0.1261 [-0.2145, -0.0378] (0/4 >0); U = +3.2901 [+2.5971, +3.9832] (4/4 >0); S/U 1.04.
  - ĝ move (pointed→control level): ΔC pointed -0.4558 [-0.5136, -0.3979] (0/4 >0), ΔC unpointed -0.0824 [-0.1336, -0.0311] (0/4 >0); ratio pointed +0.8995 [+0.8799, +0.9190] (4/4 >0), unpointed +0.9284 [+0.8881, +0.9688] (4/4 >0); P index -0.0290 [-0.0545, -0.0034] (0/4 >0). d_shared: ΔC pointed -1.0807 [-1.3981, -0.7632] (0/4 >0), unpointed -0.0674 [-0.1531, +0.0182] (0/4 >0). d_pointer A→B under pointed-A: ΔC_A +0.2828 [+0.0527, +0.5129] (4/4 >0), ΔC_B +0.4814 [+0.2646, +0.6981] (4/4 >0), ΔC_C +0.2391 [+0.0653, +0.4130] (4/4 >0), redistribution B−A +0.1986 [+0.0589, +0.3383] (4/4 >0). Reverse ĝ on control (one-sided) ΔC all sources +0.2389 [+0.2086, +0.2692] (4/4 >0).
- **RESID_P|L48-50:** pointed-source transfer C(self) +0.1810 [+0.1467, +0.2154] (4/4 >0); unpointed C(other) +0.0029 [-0.0094, +0.0152] (2/4 >0); control C(ctrl) +0.0119 [+0.0010, +0.0229] (4/4 >0). **S = +0.1782 [+0.1378, +0.2185] (4/4 >0)**; Q = -0.0091 [-0.0131, -0.0050] (0/4 >0); U = +0.1691 [+0.1314, +0.2068] (4/4 >0); S/U 1.05.
  - ĝ move (pointed→control level): ΔC pointed -0.0180 [-0.0303, -0.0057] (0/4 >0), ΔC unpointed -0.0000 [-0.0040, +0.0039] (2/4 >0); ratio pointed +0.9017 [+0.8369, +0.9665] (4/4 >0), unpointed +0.4953 [-0.1644, +1.1549] (3/4 >0); P index +0.4065 [-0.2221, +1.0350] (4/4 >0). d_shared: ΔC pointed -0.0516 [-0.0712, -0.0321] (0/4 >0), unpointed +0.0020 [-0.0048, +0.0087] (3/4 >0). d_pointer A→B under pointed-A: ΔC_A -0.0104 [-0.0391, +0.0184] (2/4 >0), ΔC_B +0.0569 [+0.0327, +0.0811] (4/4 >0), ΔC_C -0.0014 [-0.0088, +0.0060] (2/4 >0), redistribution B−A +0.0672 [+0.0182, +0.1163] (4/4 >0). Reverse ĝ on control (one-sided) ΔC all sources +0.0032 [-0.0021, +0.0084] (3/4 >0).
- **RESID_P|L51-59:** pointed-source transfer C(self) +5.4987 [+4.9794, +6.0180] (4/4 >0); unpointed C(other) +0.3931 [+0.3382, +0.4479] (4/4 >0); control C(ctrl) +0.6267 [+0.4385, +0.8149] (4/4 >0). **S = +5.1057 [+4.5507, +5.6606] (4/4 >0)**; Q = -0.2337 [-0.3869, -0.0804] (0/4 >0); U = +4.8720 [+4.3018, +5.4421] (4/4 >0); S/U 1.05.
  - ĝ move (pointed→control level): ΔC pointed -0.6361 [-0.7845, -0.4876] (0/4 >0), ΔC unpointed -0.0424 [-0.0735, -0.0113] (0/4 >0); ratio pointed +0.8835 [+0.8492, +0.9178] (4/4 >0), unpointed +0.8931 [+0.8234, +0.9628] (4/4 >0); P index -0.0096 [-0.0587, +0.0395] (1/4 >0). d_shared: ΔC pointed -1.9269 [-2.2242, -1.6296] (0/4 >0), unpointed -0.0682 [-0.1172, -0.0191] (0/4 >0). d_pointer A→B under pointed-A: ΔC_A +0.0224 [-0.3036, +0.3484] (2/4 >0), ΔC_B +0.7088 [+0.5400, +0.8776] (4/4 >0), ΔC_C +0.0710 [+0.0296, +0.1124] (4/4 >0), redistribution B−A +0.6864 [+0.2391, +1.1336] (4/4 >0). Reverse ĝ on control (one-sided) ΔC all sources +0.1742 [+0.0687, +0.2798] (4/4 >0).
- **LOGITS:** pointed-source transfer C(self) +8.7695 [+6.6385, +10.9005] (4/4 >0); unpointed C(other) +4.1210 [+3.4112, +4.8307] (4/4 >0); control C(ctrl) +3.9232 [+3.5857, +4.2607] (4/4 >0). **S = +4.6486 [+3.1779, +6.1192] (4/4 >0)**; Q = +0.1978 [-0.3417, +0.7372] (3/4 >0); U = +4.8463 [+2.8528, +6.8398] (4/4 >0); S/U 0.96.
  - ĝ move (pointed→control level): ΔC pointed -1.0341 [-1.3094, -0.7588] (0/4 >0), ΔC unpointed -0.3601 [-0.5013, -0.2190] (0/4 >0); ratio pointed +0.8820 [+0.8659, +0.8982] (4/4 >0), unpointed +0.9133 [+0.8888, +0.9377] (4/4 >0); P index -0.0312 [-0.0434, -0.0190] (0/4 >0). d_shared: ΔC pointed -1.3292 [-1.8026, -0.8559] (0/4 >0), unpointed -0.1918 [-0.3933, +0.0096] (0/4 >0). d_pointer A→B under pointed-A: ΔC_A +0.3081 [+0.1207, +0.4955] (4/4 >0), ΔC_B +0.6118 [+0.3248, +0.8988] (4/4 >0), ΔC_C +0.4543 [+0.2215, +0.6871] (4/4 >0), redistribution B−A +0.3037 [-0.0930, +0.7005] (4/4 >0). Reverse ĝ on control (one-sided) ΔC all sources +0.6482 [+0.4961, +0.8002] (4/4 >0).
- **Natural readout selectivity S_nat (J_NP):** L48–50 +0.2588 [+0.1755, +0.3420] (4/4 >0); L51–59 +1.7572 [+1.6092, +1.9051] (4/4 >0). Presence L51–59: self +2.576, other +0.819, control +0.779.
- **Rank-1-anywhere (L24–59):** pointed 0.86, unpointed 0.06, control 0.19. Output-disposition screen (median final-layer rank of each word at interior positions): pointed 550, unpointed 1881, control 2438 (min 47).
- **Gates:** realized ρ ranges {"g": [0.999, 1.001], "dshared": [1.0, 1.0], "dptr": [0.999, 1.001], "grev": [1.0, 1.001]}; damage max ΔNLL 0.0007, min top-1 retention 1.000.

## 3. Complete numerical evidence

### J_NP|L48-50

| quantity | mean | 95% t-CI | signs >0 / n | per-triple |
|---|---|---|---|---|
| self | +0.3937 | [+0.3234, +0.4640] | 4/4 | +0.425, +0.432, +0.336, +0.382 |
| other | +0.0783 | [+0.0366, +0.1200] | 4/4 | +0.074, +0.117, +0.061, +0.062 |
| ctrl | +0.0739 | [+0.0307, +0.1170] | 4/4 | +0.066, +0.114, +0.056, +0.060 |
| S | +0.3154 | [+0.2668, +0.3640] | 4/4 | +0.350, +0.316, +0.276, +0.320 |
| Q | +0.0045 | [-0.0005, +0.0094] | 4/4 | +0.009, +0.002, +0.005, +0.002 |
| U | +0.3199 | [+0.2690, +0.3707] | 4/4 | +0.359, +0.318, +0.281, +0.322 |
| g|dC_pointed | -0.0311 | [-0.0359, -0.0263] | 0/4 | -0.034, -0.031, -0.032, -0.027 |
| g|dC_unpointed | -0.0106 | [-0.0216, +0.0004] | 0/4 | -0.014, -0.017, -0.011, -0.001 |
| g|ratio_pointed | +0.9204 | [+0.9018, +0.9389] | 4/4 | +0.919, +0.929, +0.904, +0.929 |
| g|ratio_unpointed | +0.8688 | [+0.7399, +0.9976] | 4/4 | +0.816, +0.857, +0.816, +0.987 |
| g|P_index | +0.0516 | [-0.0660, +0.1692] | 3/4 | +0.104, +0.072, +0.088, -0.058 |
| dshared|dC_pointed | -0.0754 | [-0.0952, -0.0555] | 0/4 | -0.082, -0.079, -0.057, -0.083 |
| dshared|dC_unpointed | -0.0127 | [-0.0305, +0.0051] | 1/4 | -0.020, -0.022, -0.010, +0.002 |
| dshared|ratio_pointed | +0.8090 | [+0.7757, +0.8423] | 4/4 | +0.806, +0.817, +0.831, +0.781 |
| dshared|ratio_unpointed | +0.8494 | [+0.6396, +1.0592] | 4/4 | +0.724, +0.810, +0.828, +1.035 |
| dshared|P_index | -0.0404 | [-0.2739, +0.1931] | 3/4 | +0.082, +0.007, +0.003, -0.254 |
| dptr|dC_A | -0.0197 | [-0.0599, +0.0205] | 0/4 | -0.002, -0.004, -0.016, -0.057 |
| dptr|dC_B | +0.1402 | [+0.1220, +0.1584] | 4/4 | +0.125, +0.145, +0.152, +0.139 |
| dptr|dC_C | +0.0127 | [+0.0045, +0.0209] | 4/4 | +0.006, +0.018, +0.014, +0.012 |
| dptr|redistribution_B_minus_A | +0.1600 | [+0.1139, +0.2060] | 4/4 | +0.127, +0.150, +0.167, +0.196 |
| grev|dC_all_sources | +0.0172 | [+0.0080, +0.0264] | 4/4 | +0.013, +0.021, +0.012, +0.023 |

### J_NP|L51-59

| quantity | mean | 95% t-CI | signs >0 / n | per-triple |
|---|---|---|---|---|
| self | +4.5653 | [+3.8637, +5.2668] | 4/4 | +4.216, +4.446, +4.389, +5.210 |
| other | +1.1490 | [+1.0047, +1.2934] | 4/4 | +1.036, +1.225, +1.116, +1.219 |
| ctrl | +1.2752 | [+1.1155, +1.4349] | 4/4 | +1.171, +1.411, +1.248, +1.271 |
| S | +3.4163 | [+2.8035, +4.0290] | 4/4 | +3.181, +3.221, +3.273, +3.991 |
| Q | -0.1261 | [-0.2145, -0.0378] | 0/4 | -0.135, -0.186, -0.132, -0.052 |
| U | +3.2901 | [+2.5971, +3.9832] | 4/4 | +3.046, +3.035, +3.140, +3.940 |
| g|dC_pointed | -0.4558 | [-0.5136, -0.3979] | 0/4 | -0.416, -0.499, -0.469, -0.438 |
| g|dC_unpointed | -0.0824 | [-0.1336, -0.0311] | 0/4 | -0.076, -0.128, -0.072, -0.053 |
| g|ratio_pointed | +0.8995 | [+0.8799, +0.9190] | 4/4 | +0.901, +0.888, +0.893, +0.916 |
| g|ratio_unpointed | +0.9284 | [+0.8881, +0.9688] | 4/4 | +0.927, +0.895, +0.935, +0.956 |
| g|P_index | -0.0290 | [-0.0545, -0.0034] | 0/4 | -0.026, -0.008, -0.042, -0.040 |
| dshared|dC_pointed | -1.0807 | [-1.3981, -0.7632] | 0/4 | -0.831, -1.127, -1.051, -1.313 |
| dshared|dC_unpointed | -0.0674 | [-0.1531, +0.0182] | 0/4 | -0.030, -0.147, -0.039, -0.055 |
| dshared|ratio_pointed | +0.7645 | [+0.7225, +0.8064] | 4/4 | +0.803, +0.746, +0.761, +0.748 |
| dshared|ratio_unpointed | +0.9430 | [+0.8757, +1.0104] | 4/4 | +0.971, +0.880, +0.965, +0.955 |
| dshared|P_index | -0.1786 | [-0.2336, -0.1235] | 0/4 | -0.169, -0.134, -0.205, -0.207 |
| dptr|dC_A | +0.2828 | [+0.0527, +0.5129] | 4/4 | +0.336, +0.147, +0.186, +0.462 |
| dptr|dC_B | +0.4814 | [+0.2646, +0.6981] | 4/4 | +0.416, +0.439, +0.387, +0.683 |
| dptr|dC_C | +0.2391 | [+0.0653, +0.4130] | 4/4 | +0.259, +0.148, +0.164, +0.386 |
| dptr|redistribution_B_minus_A | +0.1986 | [+0.0589, +0.3383] | 4/4 | +0.081, +0.292, +0.201, +0.221 |
| grev|dC_all_sources | +0.2389 | [+0.2086, +0.2692] | 4/4 | +0.235, +0.263, +0.217, +0.241 |

### RESID_P|L48-50

| quantity | mean | 95% t-CI | signs >0 / n | per-triple |
|---|---|---|---|---|
| self | +0.1810 | [+0.1467, +0.2154] | 4/4 | +0.193, +0.157, +0.170, +0.204 |
| other | +0.0029 | [-0.0094, +0.0152] | 2/4 | +0.011, +0.008, -0.002, -0.006 |
| ctrl | +0.0119 | [+0.0010, +0.0229] | 4/4 | +0.019, +0.017, +0.005, +0.007 |
| S | +0.1782 | [+0.1378, +0.2185] | 4/4 | +0.183, +0.149, +0.172, +0.210 |
| Q | -0.0091 | [-0.0131, -0.0050] | 0/4 | -0.008, -0.009, -0.007, -0.013 |
| U | +0.1691 | [+0.1314, +0.2068] | 4/4 | +0.174, +0.140, +0.165, +0.197 |
| g|dC_pointed | -0.0180 | [-0.0303, -0.0057] | 0/4 | -0.025, -0.007, -0.023, -0.017 |
| g|dC_unpointed | -0.0000 | [-0.0040, +0.0039] | 2/4 | -0.002, -0.002, +0.002, +0.002 |
| g|ratio_pointed | +0.9017 | [+0.8369, +0.9665] | 4/4 | +0.873, +0.952, +0.865, +0.917 |
| g|ratio_unpointed | +0.4953 | [-0.1644, +1.1549] | 3/4 | +0.800, +0.727, -0.108, +0.562 |
| g|P_index | +0.4065 | [-0.2221, +1.0350] | 4/4 | +0.073, +0.226, +0.973, +0.354 |
| dshared|dC_pointed | -0.0516 | [-0.0712, -0.0321] | 0/4 | -0.051, -0.039, -0.048, -0.069 |
| dshared|dC_unpointed | +0.0020 | [-0.0048, +0.0087] | 3/4 | -0.003, +0.002, +0.002, +0.007 |
| dshared|ratio_pointed | +0.7172 | [+0.6569, +0.7775] | 4/4 | +0.738, +0.750, +0.716, +0.664 |
| dshared|ratio_unpointed | +0.2886 | [-0.9832, +1.5605] | 2/4 | +0.684, +1.216, -0.484, -0.262 |
| dshared|P_index | +0.4286 | [-0.7985, +1.6556] | 3/4 | +0.054, -0.466, +1.200, +0.926 |
| dptr|dC_A | -0.0104 | [-0.0391, +0.0184] | 2/4 | +0.001, -0.012, +0.005, -0.035 |
| dptr|dC_B | +0.0569 | [+0.0327, +0.0811] | 4/4 | +0.036, +0.059, +0.060, +0.073 |
| dptr|dC_C | -0.0014 | [-0.0088, +0.0060] | 2/4 | -0.007, +0.001, -0.004, +0.003 |
| dptr|redistribution_B_minus_A | +0.0672 | [+0.0182, +0.1163] | 4/4 | +0.035, +0.071, +0.055, +0.108 |
| grev|dC_all_sources | +0.0032 | [-0.0021, +0.0084] | 3/4 | -0.000, +0.004, +0.002, +0.007 |

### RESID_P|L51-59

| quantity | mean | 95% t-CI | signs >0 / n | per-triple |
|---|---|---|---|---|
| self | +5.4987 | [+4.9794, +6.0180] | 4/4 | +5.204, +5.239, +5.701, +5.851 |
| other | +0.3931 | [+0.3382, +0.4479] | 4/4 | +0.401, +0.430, +0.347, +0.394 |
| ctrl | +0.6267 | [+0.4385, +0.8149] | 4/4 | +0.667, +0.644, +0.459, +0.736 |
| S | +5.1057 | [+4.5507, +5.6606] | 4/4 | +4.802, +4.809, +5.355, +5.457 |
| Q | -0.2337 | [-0.3869, -0.0804] | 0/4 | -0.266, -0.214, -0.113, -0.342 |
| U | +4.8720 | [+4.3018, +5.4421] | 4/4 | +4.536, +4.595, +5.242, +5.115 |
| g|dC_pointed | -0.6361 | [-0.7845, -0.4876] | 0/4 | -0.717, -0.635, -0.687, -0.506 |
| g|dC_unpointed | -0.0424 | [-0.0735, -0.0113] | 0/4 | -0.046, -0.066, -0.039, -0.019 |
| g|ratio_pointed | +0.8835 | [+0.8492, +0.9178] | 4/4 | +0.862, +0.879, +0.879, +0.914 |
| g|ratio_unpointed | +0.8931 | [+0.8234, +0.9628] | 4/4 | +0.886, +0.846, +0.889, +0.952 |
| g|P_index | -0.0096 | [-0.0587, +0.0395] | 1/4 | -0.024, +0.033, -0.009, -0.038 |
| dshared|dC_pointed | -1.9269 | [-2.2242, -1.6296] | 0/4 | -1.725, -1.816, -2.118, -2.049 |
| dshared|dC_unpointed | -0.0682 | [-0.1172, -0.0191] | 0/4 | -0.073, -0.110, -0.046, -0.043 |
| dshared|ratio_pointed | +0.6501 | [+0.6238, +0.6763] | 4/4 | +0.669, +0.653, +0.628, +0.650 |
| dshared|ratio_unpointed | +0.8297 | [+0.7273, +0.9320] | 4/4 | +0.817, +0.745, +0.866, +0.891 |
| dshared|P_index | -0.1796 | [-0.2954, -0.0638] | 0/4 | -0.148, -0.091, -0.238, -0.241 |
| dptr|dC_A | +0.0224 | [-0.3036, +0.3484] | 2/4 | +0.189, +0.184, -0.238, -0.045 |
| dptr|dC_B | +0.7088 | [+0.5400, +0.8776] | 4/4 | +0.562, +0.717, +0.742, +0.814 |
| dptr|dC_C | +0.0710 | [+0.0296, +0.1124] | 4/4 | +0.070, +0.042, +0.066, +0.105 |
| dptr|redistribution_B_minus_A | +0.6864 | [+0.2391, +1.1336] | 4/4 | +0.373, +0.534, +0.979, +0.859 |
| grev|dC_all_sources | +0.1742 | [+0.0687, +0.2798] | 4/4 | +0.198, +0.253, +0.147, +0.099 |

### LOGITS

| quantity | mean | 95% t-CI | signs >0 / n | per-triple |
|---|---|---|---|---|
| self | +8.7695 | [+6.6385, +10.9005] | 4/4 | +7.996, +8.480, +7.863, +10.739 |
| other | +4.1210 | [+3.4112, +4.8307] | 4/4 | +3.904, +4.196, +3.675, +4.709 |
| ctrl | +3.9232 | [+3.5857, +4.2607] | 4/4 | +3.770, +4.178, +3.729, +4.016 |
| S | +4.6486 | [+3.1779, +6.1192] | 4/4 | +4.092, +4.284, +4.188, +6.030 |
| Q | +0.1978 | [-0.3417, +0.7372] | 3/4 | +0.134, +0.018, -0.054, +0.693 |
| U | +4.8463 | [+2.8528, +6.8398] | 4/4 | +4.226, +4.302, +4.134, +6.723 |
| g|dC_pointed | -1.0341 | [-1.3094, -0.7588] | 0/4 | -0.860, -1.117, -0.924, -1.235 |
| g|dC_unpointed | -0.3601 | [-0.5013, -0.2190] | 0/4 | -0.284, -0.449, -0.284, -0.424 |
| g|ratio_pointed | +0.8820 | [+0.8659, +0.8982] | 4/4 | +0.892, +0.868, +0.883, +0.885 |
| g|ratio_unpointed | +0.9133 | [+0.8888, +0.9377] | 4/4 | +0.927, +0.893, +0.923, +0.910 |
| g|P_index | -0.0312 | [-0.0434, -0.0190] | 0/4 | -0.035, -0.025, -0.040, -0.025 |
| dshared|dC_pointed | -1.3292 | [-1.8026, -0.8559] | 0/4 | -1.038, -1.441, -1.144, -1.695 |
| dshared|dC_unpointed | -0.1918 | [-0.3933, +0.0096] | 0/4 | -0.082, -0.354, -0.101, -0.231 |
| dshared|ratio_pointed | +0.8493 | [+0.8220, +0.8766] | 4/4 | +0.870, +0.830, +0.855, +0.842 |
| dshared|ratio_unpointed | +0.9546 | [+0.9091, +1.0000] | 4/4 | +0.979, +0.916, +0.973, +0.951 |
| dshared|P_index | -0.1053 | [-0.1273, -0.0833] | 0/4 | -0.109, -0.086, -0.118, -0.109 |
| dptr|dC_A | +0.3081 | [+0.1207, +0.4955] | 4/4 | +0.455, +0.185, +0.345, +0.248 |
| dptr|dC_B | +0.6118 | [+0.3248, +0.8988] | 4/4 | +0.494, +0.517, +0.556, +0.880 |
| dptr|dC_C | +0.4543 | [+0.2215, +0.6871] | 4/4 | +0.438, +0.315, +0.404, +0.659 |
| dptr|redistribution_B_minus_A | +0.3037 | [-0.0930, +0.7005] | 4/4 | +0.040, +0.332, +0.211, +0.632 |
| grev|dC_all_sources | +0.6482 | [+0.4961, +0.8002] | 4/4 | +0.545, +0.749, +0.591, +0.707 |

Figure: `figures/tagged_selection_pilot_transfer.png`. Machine-readable: `tagged_selection_pilot_tables.json`.

## 4. Verification and limitations

- Same-source (position 1) bitwise equal to clean and layers < 36 identical between futures on every cell; donor geometry asserted per source. Realized writes and damage above.
- Pilot: n = 4 triples of previously exposed words, fitting carriers only; ĝ is a cross-organism transfer from the single-word fit; d_pointer and d_shared are fit on these same cells (identity-specific contextual generalization is not claimed).
- Unpointed ratios are undefined where the unpointed clean transfer is near zero; reported as n/a where so.

## 5. Interpretation and next decision

**Selection is established at pilot scale, and the gain account is rejected as the account of the instruction.** With three sources present and relevance carried by an arbitrary tag, the pointed source's transfer is 0.39 (J_NP L48–50) against 0.08 for an unpointed source and 0.07 with no pointer; S = +0.32 [+0.27, +0.36], 4/4 triples, and the same on J_NP L51–59 (+3.42), RESID_P (+0.18, +5.11) and the model's own logits (+4.65), all 4/4. Q is zero at L48–50 and negative at L51–59 on J_NP (−0.13, 0/4) and RESID_P (−0.23, 0/4): an unpointed source transfers no more, and at the late window slightly less, than with no pointer. U ≈ S on every instrument: the instruction's entire effect on transfer lands on the pointed source. Both accounts that predicted S ≈ 0 (a gain on whichever word is sourced; a generic gain on all introduced words) fail here. The readout agrees without any intervention: pointed-word presence 0.35 vs 0.09 (unpointed) at L48–50, rank-1 surfacing 0.86 vs 0.06, S_nat 4/4 at both windows. The output-disposition screen passes (median final-layer rank of the pointed word 550, minimum 47).

**ĝ is a uniform gain on top of selection, not the selector.** Moving the single-word ĝ from the pointed level to the control level scales the pointed source's transfer by 0.88–0.92 and the unpointed sources' by 0.87–0.93 on every instrument; the profile index P is within ±0.05 of zero (CI straddles zero at L48–50, −0.03 [−0.05, −0.00] at L51–59). The natural removal of the pointer takes 80 % of the pointed transfer away; the ĝ move takes 10 % from every source alike. This resolves Package 2's ambiguity for this coordinate: ĝ's effect is a readout gain applied to whatever transfers, and it carries none of the selection.

**A native direction on this organism is selective; a native pointer contrast partially redirects.** d_shared (pointed minus control, fit on these cells; cos 0.65 with ĝ) moved to the control level scales the pointed source by 0.65–0.81 and the unpointed by 0.83–0.95; P = −0.18 [−0.23, −0.12] at J_NP L51–59, 0/4, and −0.18 on RESID_P L51–59, −0.11 on LOGITS. It reduces the pointed source's transfer proportionally more than the others: a relevance-weighted gain, the pattern the earlier pilot reported for its gN. d_pointer (pointed B minus pointed A, balanced over identities and positions; |d| 3.7, cos −0.03 with ĝ) applied under the pointed-A arm raises source B's transfer on every instrument, 4/4 (J_NP +0.14, about 45 % of the pointed level; RESID_P +0.057; LOGITS +0.61), while source A is not reduced at L48–50 (−0.02, ns) and is raised at L51–59 along with C. The pointer contrast installs B's selection without revoking A's: partial address control with a gain component, not a clean redirect.

**What this licenses (n = 4 triples, exposed words, fitting carriers).** At this site and readout, the maintain-type instruction selects among simultaneously available sources; the single-word ĝ coordinate is a non-selective readout gain; a natively fitted pointed-minus-control direction is a selective gain; a natively fitted pointer contrast adds the pointed source's transfer without removing the previously pointed one. d_shared and d_pointer are fit on the evaluated cells (contextual, not identity holdout) and are reported as such. Nothing about behavior.

**Next decision.** The discriminating result is clear enough to scale: run the 8 evaluation triples from the bank words on carriers C2/C3 with the pilot-fit d_shared and d_pointer transferred (identity holdout for both directions) and native refits reported alongside; about 3,000 forwards. Then H1.8's competition series (k = 1, 2, 3, 4, 6) and the mid-carrier cue can follow on the same organism. The wording factorial (H1.7) and categories come after, since the selection readout now gives them a sharper endpoint than the single-word margin.
