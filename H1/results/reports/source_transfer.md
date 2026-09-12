# H1 · source transfer — results (run 20260906T220538Z)

## 1. Question and setup

Does sustained replacement of the introduced word's span (block outputs at layers ≥ L_x) with an arm-matched donor Y move the later readout toward Y, and from which L_x? Controlled organism, geometry-matched calibration pairs [('orange', 'tiger'), ('guitar', 'mountain'), ('diamond', 'castle')] (pair table in `outputs/source_transfer/meta.json`), both directions, arms ['maintain', 'mention'], carriers ['C0', 'C1']; L_x ∈ [23, 28, 32, 36, 40, 44]. Cluster = unordered pair (n=3, pilot scale). Instruments: J_NP pair margin m = E[z_Y − z_X]; RESID_P pair axis p_{Y−X} from plain sentences; LOGITS output log-prob margin. A_natural = m(clean Y run) − m(clean X run) is the positive control / calibration denominator. 192 forwards; same-source at L_x=36 bitwise equal to clean and layers < L_x identical between futures asserted on every cell.

## 2. Main findings

- **J_NP|L48-50, maintain:** A_nat +0.838 [+0.408, +1.268] (3/3 >0); C at L_x=23 +0.706 [+0.383, +1.029] (3/3 >0); L_x=36 +0.434 [+0.049, +0.818] (3/3 >0) (C/A 0.52 [0.40, 0.56]); L_x=44 +0.296 [-0.067, +0.660] (3/3 >0).
- **J_NP|L48-50, mention:** A_nat +0.403 [+0.106, +0.700] (3/3 >0); C at L_x=23 +0.351 [+0.194, +0.507] (3/3 >0); L_x=36 +0.223 [-0.030, +0.476] (3/3 >0) (C/A 0.55 [0.40, 0.60]); L_x=44 +0.171 [-0.067, +0.409] (3/3 >0).
- **J_NP|L48-50, maintain − mention at L_x=36:** +0.211 [+0.051, +0.371] (3/3 >0); at L_x=23 +0.355 [+0.188, +0.522] (3/3 >0).
- **J_NP|L51-59, maintain:** A_nat +4.027 [+1.132, +6.922] (3/3 >0); C at L_x=23 +3.930 [+1.096, +6.765] (3/3 >0); L_x=36 +3.828 [+0.796, +6.859] (3/3 >0) (C/A 0.95 [0.90, 0.97]); L_x=44 +3.716 [+0.694, +6.738] (3/3 >0).
- **J_NP|L51-59, mention:** A_nat +1.896 [+0.556, +3.236] (3/3 >0); C at L_x=23 +1.970 [+0.593, +3.346] (3/3 >0); L_x=36 +1.810 [+0.323, +3.296] (3/3 >0) (C/A 0.95 [0.88, 0.98]); L_x=44 +1.803 [+0.301, +3.305] (3/3 >0).
- **J_NP|L51-59, maintain − mention at L_x=36:** +2.018 [+0.253, +3.783] (3/3 >0); at L_x=23 +1.961 [+0.334, +3.588] (3/3 >0).
- **RESID_P|L48-50, maintain:** A_nat +0.211 [+0.060, +0.363] (3/3 >0); C at L_x=23 +0.183 [+0.134, +0.232] (3/3 >0); L_x=36 +0.103 [-0.008, +0.213] (3/3 >0) (C/A 0.49 [0.36, 0.52]); L_x=44 +0.106 [-0.017, +0.229] (3/3 >0).
- **RESID_P|L48-50, mention:** A_nat +0.012 [-0.209, +0.233] (1/3 >0); C at L_x=23 +0.062 [-0.080, +0.204] (3/3 >0); L_x=36 +0.047 [-0.033, +0.126] (3/3 >0) (C/A 3.81 [-6.45, 3.81]); L_x=44 +0.065 [-0.023, +0.152] (3/3 >0).
- **RESID_P|L48-50, maintain − mention at L_x=36:** +0.056 [+0.024, +0.087] (3/3 >0); at L_x=23 +0.121 [+0.026, +0.216] (3/3 >0).
- **RESID_P|L51-59, maintain:** A_nat +2.872 [+0.906, +4.838] (3/3 >0); C at L_x=23 +2.807 [+0.546, +5.067] (3/3 >0); L_x=36 +2.658 [+0.567, +4.749] (3/3 >0) (C/A 0.93 [0.85, 0.97]); L_x=44 +2.638 [+0.595, +4.681] (3/3 >0).
- **RESID_P|L51-59, mention:** A_nat +0.650 [-0.227, +1.526] (3/3 >0); C at L_x=23 +0.791 [-0.206, +1.788] (3/3 >0); L_x=36 +0.706 [-0.189, +1.601] (3/3 >0) (C/A 1.09 [0.96, 1.27]); L_x=44 +0.740 [-0.169, +1.648] (3/3 >0).
- **RESID_P|L51-59, maintain − mention at L_x=36:** +1.952 [+0.621, +3.282] (3/3 >0); at L_x=23 +2.016 [+0.543, +3.489] (3/3 >0).
- **LOGITS, maintain:** A_nat +8.581 [+4.512, +12.649] (3/3 >0); C at L_x=23 +8.425 [+4.382, +12.467] (3/3 >0); L_x=36 +8.527 [+4.170, +12.885] (3/3 >0) (C/A 0.99 [0.97, 1.01]); L_x=44 +8.435 [+4.075, +12.795] (3/3 >0).
- **LOGITS, mention:** A_nat +5.727 [+4.071, +7.384] (3/3 >0); C at L_x=23 +5.735 [+3.968, +7.502] (3/3 >0); L_x=36 +5.687 [+3.931, +7.444] (3/3 >0) (C/A 0.99 [0.98, 1.00]); L_x=44 +5.691 [+3.964, +7.419] (3/3 >0).
- **LOGITS, maintain − mention at L_x=36:** +2.840 [+0.113, +5.567] (3/3 >0); at L_x=23 +2.689 [+0.377, +5.001] (3/3 >0).

## 3. Complete numerical evidence

### J_NP|L48-50

| arm | quantity | mean | 95% t-CI | signs >0 / n | per-pair |
|---|---|---|---|---|---|
| maintain | A_natural (donor clean − clean) | +0.8377 | [+0.4076, +1.2679] | 3/3 | +0.639, +0.954, +0.920 |
| maintain | C at L_x=23 (C/A 0.84 [0.79, 0.89]) | +0.7058 | [+0.3828, +1.0287] | 3/3 | +0.567, +0.825, +0.725 |
| maintain | C at L_x=28 (C/A 0.74 [0.68, 0.80]) | +0.6158 | [+0.2043, +1.0274] | 3/3 | +0.435, +0.761, +0.651 |
| maintain | C at L_x=32 (C/A 0.68 [0.55, 0.77]) | +0.5728 | [+0.0793, +1.0664] | 3/3 | +0.352, +0.736, +0.631 |
| maintain | C at L_x=36 (C/A 0.52 [0.40, 0.56]) | +0.4335 | [+0.0493, +0.8177] | 3/3 | +0.255, +0.529, +0.516 |
| maintain | C at L_x=40 (C/A 0.33 [0.21, 0.39]) | +0.2805 | [-0.0410, +0.6020] | 3/3 | +0.131, +0.351, +0.359 |
| maintain | C at L_x=44 (C/A 0.35 [0.20, 0.41]) | +0.2962 | [-0.0674, +0.6597] | 3/3 | +0.128, +0.393, +0.367 |
| mention | A_natural (donor clean − clean) | +0.4032 | [+0.1062, +0.7002] | 3/3 | +0.279, +0.518, +0.413 |
| mention | C at L_x=23 (C/A 0.87 [0.79, 1.01]) | +0.3509 | [+0.1945, +0.5074] | 3/3 | +0.283, +0.407, +0.363 |
| mention | C at L_x=28 (C/A 0.79 [0.66, 0.85]) | +0.3174 | [+0.0009, +0.6339] | 3/3 | +0.184, +0.438, +0.330 |
| mention | C at L_x=32 (C/A 0.80 [0.67, 0.84]) | +0.3213 | [+0.0099, +0.6327] | 3/3 | +0.188, +0.436, +0.340 |
| mention | C at L_x=36 (C/A 0.55 [0.40, 0.60]) | +0.2226 | [-0.0304, +0.4756] | 3/3 | +0.112, +0.312, +0.245 |
| mention | C at L_x=40 (C/A 0.40 [0.25, 0.45]) | +0.1627 | [-0.0473, +0.3728] | 3/3 | +0.069, +0.233, +0.186 |
| mention | C at L_x=44 (C/A 0.42 [0.23, 0.49]) | +0.1713 | [-0.0666, +0.4091] | 3/3 | +0.066, +0.252, +0.196 |
| both | D = C(maintain) − C(mention) at L_x=23 | +0.3548 | [+0.1881, +0.5215] | 3/3 | +0.284, +0.418, +0.362 |
| both | D = C(maintain) − C(mention) at L_x=28 | +0.2984 | [+0.1962, +0.4006] | 3/3 | +0.251, +0.323, +0.322 |
| both | D = C(maintain) − C(mention) at L_x=32 | +0.2515 | [+0.0625, +0.4405] | 3/3 | +0.164, +0.299, +0.291 |
| both | D = C(maintain) − C(mention) at L_x=36 | +0.2109 | [+0.0511, +0.3707] | 3/3 | +0.144, +0.218, +0.272 |
| both | D = C(maintain) − C(mention) at L_x=40 | +0.1178 | [-0.0199, +0.2554] | 3/3 | +0.062, +0.118, +0.173 |
| both | D = C(maintain) − C(mention) at L_x=44 | +0.1249 | [-0.0149, +0.2647] | 3/3 | +0.062, +0.141, +0.171 |

### J_NP|L51-59

| arm | quantity | mean | 95% t-CI | signs >0 / n | per-pair |
|---|---|---|---|---|---|
| maintain | A_natural (donor clean − clean) | +4.0269 | [+1.1323, +6.9216] | 3/3 | +2.690, +4.829, +4.561 |
| maintain | C at L_x=23 (C/A 0.98 [0.97, 0.98]) | +3.9304 | [+1.0963, +6.7645] | 3/3 | +2.621, +4.710, +4.461 |
| maintain | C at L_x=28 (C/A 0.97 [0.92, 0.99]) | +3.9158 | [+0.8177, +7.0139] | 3/3 | +2.483, +4.758, +4.506 |
| maintain | C at L_x=32 (C/A 0.97 [0.92, 0.99]) | +3.8908 | [+0.8176, +6.9641] | 3/3 | +2.475, +4.761, +4.437 |
| maintain | C at L_x=36 (C/A 0.95 [0.90, 0.97]) | +3.8277 | [+0.7964, +6.8590] | 3/3 | +2.424, +4.639, +4.419 |
| maintain | C at L_x=40 (C/A 0.92 [0.87, 0.96]) | +3.7213 | [+0.7419, +6.7006] | 3/3 | +2.338, +4.465, +4.362 |
| maintain | C at L_x=44 (C/A 0.92 [0.86, 0.95]) | +3.7159 | [+0.6936, +6.7383] | 3/3 | +2.313, +4.489, +4.346 |
| mention | A_natural (donor clean − clean) | +1.8958 | [+0.5561, +3.2355] | 3/3 | +1.359, +2.438, +1.890 |
| mention | C at L_x=23 (C/A 1.04 [1.03, 1.06]) | +1.9695 | [+0.5929, +3.3462] | 3/3 | +1.401, +2.508, +1.999 |
| mention | C at L_x=28 (C/A 0.96 [0.90, 1.00]) | +1.8288 | [+0.3061, +3.3515] | 3/3 | +1.219, +2.445, +1.823 |
| mention | C at L_x=32 (C/A 0.97 [0.91, 1.01]) | +1.8409 | [+0.3218, +3.3600] | 3/3 | +1.231, +2.454, +1.838 |
| mention | C at L_x=36 (C/A 0.95 [0.88, 0.98]) | +1.8096 | [+0.3231, +3.2961] | 3/3 | +1.202, +2.398, +1.830 |
| mention | C at L_x=40 (C/A 0.94 [0.86, 0.97]) | +1.7794 | [+0.3149, +3.2439] | 3/3 | +1.175, +2.353, +1.811 |
| mention | C at L_x=44 (C/A 0.95 [0.87, 0.98]) | +1.8031 | [+0.3013, +3.3049] | 3/3 | +1.183, +2.391, +1.836 |
| both | D = C(maintain) − C(mention) at L_x=23 | +1.9609 | [+0.3339, +3.5879] | 3/3 | +1.220, +2.201, +2.462 |
| both | D = C(maintain) − C(mention) at L_x=28 | +2.0870 | [+0.2589, +3.9151] | 3/3 | +1.264, +2.314, +2.683 |
| both | D = C(maintain) − C(mention) at L_x=32 | +2.0500 | [+0.2775, +3.8224] | 3/3 | +1.244, +2.307, +2.600 |
| both | D = C(maintain) − C(mention) at L_x=36 | +2.0181 | [+0.2533, +3.7828] | 3/3 | +1.223, +2.241, +2.590 |
| both | D = C(maintain) − C(mention) at L_x=40 | +1.9419 | [+0.1794, +3.7044] | 3/3 | +1.163, +2.112, +2.551 |
| both | D = C(maintain) − C(mention) at L_x=44 | +1.9128 | [+0.1541, +3.6714] | 3/3 | +1.131, +2.098, +2.510 |

### J_NP|L24-59

| arm | quantity | mean | 95% t-CI | signs >0 / n | per-pair |
|---|---|---|---|---|---|
| maintain | A_natural (donor clean − clean) | +1.4180 | [+0.4769, +2.3591] | 3/3 | +0.984, +1.680, +1.590 |
| maintain | C at L_x=23 (C/A 0.90 [0.88, 0.91]) | +1.2724 | [+0.4465, +2.0984] | 3/3 | +0.896, +1.526, +1.395 |
| maintain | C at L_x=28 (C/A 0.86 [0.83, 0.88]) | +1.2147 | [+0.3401, +2.0892] | 3/3 | +0.813, +1.471, +1.359 |
| maintain | C at L_x=32 (C/A 0.84 [0.78, 0.87]) | +1.1852 | [+0.2697, +2.1007] | 3/3 | +0.766, +1.459, +1.331 |
| maintain | C at L_x=36 (C/A 0.74 [0.68, 0.76]) | +1.0510 | [+0.2298, +1.8723] | 3/3 | +0.671, +1.273, +1.209 |
| maintain | C at L_x=40 (C/A 0.67 [0.60, 0.71]) | +0.9549 | [+0.1802, +1.7296] | 3/3 | +0.595, +1.147, +1.122 |
| maintain | C at L_x=44 (C/A 0.67 [0.60, 0.70]) | +0.9546 | [+0.1688, +1.7404] | 3/3 | +0.590, +1.156, +1.118 |
| mention | A_natural (donor clean − clean) | +0.6834 | [+0.2098, +1.1571] | 3/3 | +0.489, +0.871, +0.690 |
| mention | C at L_x=23 (C/A 0.94 [0.93, 0.96]) | +0.6455 | [+0.2054, +1.0857] | 3/3 | +0.460, +0.813, +0.663 |
| mention | C at L_x=28 (C/A 0.88 [0.81, 0.92]) | +0.6043 | [+0.0970, +1.1117] | 3/3 | +0.395, +0.803, +0.615 |
| mention | C at L_x=32 (C/A 0.89 [0.82, 0.93]) | +0.6090 | [+0.1047, +1.1132] | 3/3 | +0.402, +0.807, +0.618 |
| mention | C at L_x=36 (C/A 0.73 [0.67, 0.77]) | +0.5019 | [+0.0811, +0.9227] | 3/3 | +0.329, +0.667, +0.510 |
| mention | C at L_x=40 (C/A 0.67 [0.61, 0.70]) | +0.4602 | [+0.0748, +0.8456] | 3/3 | +0.300, +0.609, +0.472 |
| mention | C at L_x=44 (C/A 0.68 [0.62, 0.71]) | +0.4654 | [+0.0700, +0.8608] | 3/3 | +0.301, +0.619, +0.476 |
| both | D = C(maintain) − C(mention) at L_x=23 | +0.6269 | [+0.2149, +1.0390] | 3/3 | +0.436, +0.713, +0.732 |
| both | D = C(maintain) − C(mention) at L_x=28 | +0.6104 | [+0.1861, +1.0346] | 3/3 | +0.418, +0.668, +0.745 |
| both | D = C(maintain) − C(mention) at L_x=32 | +0.5762 | [+0.1147, +1.0377] | 3/3 | +0.365, +0.652, +0.712 |
| both | D = C(maintain) − C(mention) at L_x=36 | +0.5491 | [+0.0897, +1.0086] | 3/3 | +0.342, +0.606, +0.699 |
| both | D = C(maintain) − C(mention) at L_x=40 | +0.4946 | [+0.0436, +0.9457] | 3/3 | +0.295, +0.538, +0.651 |
| both | D = C(maintain) − C(mention) at L_x=44 | +0.4892 | [+0.0386, +0.9399] | 3/3 | +0.289, +0.537, +0.642 |

### RESID_P|L48-50

| arm | quantity | mean | 95% t-CI | signs >0 / n | per-pair |
|---|---|---|---|---|---|
| maintain | A_natural (donor clean − clean) | +0.2114 | [+0.0597, +0.3631] | 3/3 | +0.141, +0.241, +0.252 |
| maintain | C at L_x=23 (C/A 0.87 [0.76, 1.15]) | +0.1829 | [+0.1340, +0.2319] | 3/3 | +0.163, +0.184, +0.202 |
| maintain | C at L_x=28 (C/A 0.87 [0.81, 1.09]) | +0.1848 | [+0.1168, +0.2528] | 3/3 | +0.154, +0.195, +0.206 |
| maintain | C at L_x=32 (C/A 0.79 [0.77, 0.81]) | +0.1670 | [+0.0465, +0.2875] | 3/3 | +0.111, +0.196, +0.194 |
| maintain | C at L_x=36 (C/A 0.49 [0.36, 0.52]) | +0.1027 | [-0.0078, +0.2132] | 3/3 | +0.051, +0.126, +0.131 |
| maintain | C at L_x=40 (C/A 0.30 [0.15, 0.37]) | +0.0645 | [-0.0293, +0.1582] | 3/3 | +0.021, +0.089, +0.083 |
| maintain | C at L_x=44 (C/A 0.50 [0.36, 0.60]) | +0.1062 | [-0.0168, +0.2292] | 3/3 | +0.050, +0.145, +0.123 |
| mention | A_natural (donor clean − clean) | +0.0123 | [-0.2085, +0.2332] | 1/3 | -0.063, -0.010, +0.110 |
| mention | C at L_x=23 (C/A 5.04 [-9.10, 5.04]) | +0.0620 | [-0.0801, +0.2041] | 3/3 | +0.012, +0.050, +0.124 |
| mention | C at L_x=28 (C/A 6.29 [-11.36, 6.29]) | +0.0774 | [-0.0182, +0.1730] | 3/3 | +0.036, +0.084, +0.112 |
| mention | C at L_x=32 (C/A 7.62 [-13.18, 7.62]) | +0.0939 | [-0.0075, +0.1952] | 3/3 | +0.047, +0.115, +0.120 |
| mention | C at L_x=36 (C/A 3.81 [-6.45, 3.81]) | +0.0469 | [-0.0326, +0.1264] | 3/3 | +0.010, +0.065, +0.066 |
| mention | C at L_x=40 (C/A 2.90 [-5.58, 2.90]) | +0.0357 | [-0.0342, +0.1057] | 3/3 | +0.004, +0.056, +0.047 |
| mention | C at L_x=44 (C/A 5.25 [-9.37, 5.25]) | +0.0646 | [-0.0226, +0.1519] | 3/3 | +0.026, +0.095, +0.073 |
| both | D = C(maintain) − C(mention) at L_x=23 | +0.1209 | [+0.0257, +0.2160] | 3/3 | +0.151, +0.134, +0.078 |
| both | D = C(maintain) − C(mention) at L_x=28 | +0.1074 | [+0.0770, +0.1379] | 3/3 | +0.118, +0.110, +0.094 |
| both | D = C(maintain) − C(mention) at L_x=32 | +0.0732 | [+0.0520, +0.0943] | 3/3 | +0.064, +0.081, +0.074 |
| both | D = C(maintain) − C(mention) at L_x=36 | +0.0558 | [+0.0245, +0.0871] | 3/3 | +0.041, +0.061, +0.065 |
| both | D = C(maintain) − C(mention) at L_x=40 | +0.0288 | [+0.0040, +0.0535] | 3/3 | +0.017, +0.033, +0.036 |
| both | D = C(maintain) − C(mention) at L_x=44 | +0.0415 | [+0.0045, +0.0786] | 3/3 | +0.024, +0.050, +0.050 |

### RESID_P|L51-59

| arm | quantity | mean | 95% t-CI | signs >0 / n | per-pair |
|---|---|---|---|---|---|
| maintain | A_natural (donor clean − clean) | +2.8723 | [+0.9063, +4.8383] | 3/3 | +1.985, +3.127, +3.505 |
| maintain | C at L_x=23 (C/A 0.98 [0.90, 1.00]) | +2.8068 | [+0.5461, +5.0675] | 3/3 | +1.783, +3.116, +3.522 |
| maintain | C at L_x=28 (C/A 0.95 [0.84, 1.00]) | +2.7202 | [+0.4465, +4.9940] | 3/3 | +1.671, +3.133, +3.357 |
| maintain | C at L_x=32 (C/A 0.95 [0.88, 1.01]) | +2.7201 | [+0.6089, +4.8313] | 3/3 | +1.741, +3.150, +3.269 |
| maintain | C at L_x=36 (C/A 0.93 [0.85, 0.97]) | +2.6577 | [+0.5667, +4.7486] | 3/3 | +1.693, +3.038, +3.242 |
| maintain | C at L_x=40 (C/A 0.91 [0.84, 0.94]) | +2.6117 | [+0.5371, +4.6863] | 3/3 | +1.662, +2.944, +3.229 |
| maintain | C at L_x=44 (C/A 0.92 [0.86, 0.96]) | +2.6382 | [+0.5953, +4.6811] | 3/3 | +1.697, +2.997, +3.220 |
| mention | A_natural (donor clean − clean) | +0.6499 | [-0.2266, +1.5264] | 3/3 | +0.243, +0.877, +0.829 |
| mention | C at L_x=23 (C/A 1.22 [1.09, 1.42]) | +0.7909 | [-0.2059, +1.7877] | 3/3 | +0.346, +1.126, +0.901 |
| mention | C at L_x=28 (C/A 1.10 [0.96, 1.23]) | +0.7139 | [-0.2341, +1.6620] | 3/3 | +0.299, +1.050, +0.793 |
| mention | C at L_x=32 (C/A 1.16 [1.00, 1.43]) | +0.7520 | [-0.1688, +1.6728] | 3/3 | +0.349, +1.079, +0.828 |
| mention | C at L_x=36 (C/A 1.09 [0.96, 1.27]) | +0.7060 | [-0.1892, +1.6012] | 3/3 | +0.310, +1.014, +0.795 |
| mention | C at L_x=40 (C/A 1.08 [0.94, 1.28]) | +0.7012 | [-0.1849, +1.5873] | 3/3 | +0.312, +1.012, +0.780 |
| mention | C at L_x=44 (C/A 1.14 [0.98, 1.41]) | +0.7395 | [-0.1687, +1.6478] | 3/3 | +0.343, +1.064, +0.812 |
| both | D = C(maintain) − C(mention) at L_x=23 | +2.0159 | [+0.5431, +3.4887] | 3/3 | +1.436, +1.990, +2.621 |
| both | D = C(maintain) − C(mention) at L_x=28 | +2.0063 | [+0.5170, +3.4956] | 3/3 | +1.372, +2.083, +2.564 |
| both | D = C(maintain) − C(mention) at L_x=32 | +1.9681 | [+0.6461, +3.2900] | 3/3 | +1.392, +2.071, +2.441 |
| both | D = C(maintain) − C(mention) at L_x=36 | +1.9516 | [+0.6213, +3.2820] | 3/3 | +1.383, +2.025, +2.447 |
| both | D = C(maintain) − C(mention) at L_x=40 | +1.9105 | [+0.5442, +3.2767] | 3/3 | +1.350, +1.932, +2.449 |
| both | D = C(maintain) − C(mention) at L_x=44 | +1.8987 | [+0.5866, +3.2107] | 3/3 | +1.354, +1.933, +2.409 |

### RESID_P|L24-59

| arm | quantity | mean | 95% t-CI | signs >0 / n | per-pair |
|---|---|---|---|---|---|
| maintain | A_natural (donor clean − clean) | +0.7975 | [+0.2299, +1.3652] | 3/3 | +0.549, +0.846, +0.998 |
| maintain | C at L_x=23 (C/A 0.96 [0.92, 0.98]) | +0.7628 | [+0.1836, +1.3420] | 3/3 | +0.504, +0.829, +0.956 |
| maintain | C at L_x=28 (C/A 0.93 [0.87, 0.99]) | +0.7427 | [+0.1656, +1.3199] | 3/3 | +0.477, +0.841, +0.909 |
| maintain | C at L_x=32 (C/A 0.92 [0.86, 1.01]) | +0.7360 | [+0.1701, +1.3020] | 3/3 | +0.474, +0.850, +0.884 |
| maintain | C at L_x=36 (C/A 0.85 [0.78, 0.92]) | +0.6792 | [+0.1396, +1.2188] | 3/3 | +0.431, +0.775, +0.832 |
| maintain | C at L_x=40 (C/A 0.82 [0.75, 0.87]) | +0.6546 | [+0.1281, +1.1811] | 3/3 | +0.413, +0.739, +0.811 |
| maintain | C at L_x=44 (C/A 0.84 [0.78, 0.90]) | +0.6689 | [+0.1483, +1.1895] | 3/3 | +0.429, +0.762, +0.816 |
| mention | A_natural (donor clean − clean) | +0.1813 | [-0.0879, +0.4505] | 3/3 | +0.058, +0.226, +0.260 |
| mention | C at L_x=23 (C/A 1.24 [1.07, 1.72]) | +0.2251 | [-0.0466, +0.4968] | 3/3 | +0.099, +0.298, +0.278 |
| mention | C at L_x=28 (C/A 1.18 [0.95, 1.77]) | +0.2148 | [-0.0348, +0.4643] | 3/3 | +0.102, +0.295, +0.247 |
| mention | C at L_x=32 (C/A 1.26 [0.99, 1.98]) | +0.2286 | [-0.0269, +0.4840] | 3/3 | +0.114, +0.314, +0.257 |
| mention | C at L_x=36 (C/A 1.00 [0.80, 1.34]) | +0.1820 | [-0.0511, +0.4152] | 3/3 | +0.078, +0.259, +0.209 |
| mention | C at L_x=40 (C/A 0.97 [0.76, 1.30]) | +0.1759 | [-0.0516, +0.4033] | 3/3 | +0.075, +0.255, +0.198 |
| mention | C at L_x=44 (C/A 1.05 [0.80, 1.52]) | +0.1905 | [-0.0443, +0.4253] | 3/3 | +0.088, +0.274, +0.209 |
| both | D = C(maintain) − C(mention) at L_x=23 | +0.5377 | [+0.1973, +0.8781] | 3/3 | +0.404, +0.531, +0.678 |
| both | D = C(maintain) − C(mention) at L_x=28 | +0.5280 | [+0.1697, +0.8862] | 3/3 | +0.375, +0.547, +0.662 |
| both | D = C(maintain) − C(mention) at L_x=32 | +0.5075 | [+0.1690, +0.8460] | 3/3 | +0.359, +0.536, +0.627 |
| both | D = C(maintain) − C(mention) at L_x=36 | +0.4972 | [+0.1592, +0.8352] | 3/3 | +0.353, +0.515, +0.623 |
| both | D = C(maintain) − C(mention) at L_x=40 | +0.4787 | [+0.1362, +0.8212] | 3/3 | +0.338, +0.485, +0.614 |
| both | D = C(maintain) − C(mention) at L_x=44 | +0.4784 | [+0.1478, +0.8091] | 3/3 | +0.341, +0.488, +0.607 |

### LOGITS

| arm | quantity | mean | 95% t-CI | signs >0 / n | per-pair |
|---|---|---|---|---|---|
| maintain | A_natural (donor clean − clean) | +8.5807 | [+4.5120, +12.6494] | 3/3 | +6.929, +8.608, +10.205 |
| maintain | C at L_x=23 (C/A 0.98 [0.97, 0.99]) | +8.4246 | [+4.3821, +12.4671] | 3/3 | +6.748, +8.528, +9.998 |
| maintain | C at L_x=28 (C/A 1.00 [0.97, 1.01]) | +8.5459 | [+4.1834, +12.9084] | 3/3 | +6.704, +8.731, +10.202 |
| maintain | C at L_x=32 (C/A 1.00 [0.98, 1.01]) | +8.5629 | [+4.3248, +12.8010] | 3/3 | +6.788, +8.710, +10.191 |
| maintain | C at L_x=36 (C/A 0.99 [0.97, 1.01]) | +8.5274 | [+4.1695, +12.8852] | 3/3 | +6.713, +8.656, +10.214 |
| maintain | C at L_x=40 (C/A 0.99 [0.96, 1.00]) | +8.4710 | [+4.1279, +12.8140] | 3/3 | +6.682, +8.556, +10.175 |
| maintain | C at L_x=44 (C/A 0.98 [0.96, 0.99]) | +8.4350 | [+4.0750, +12.7949] | 3/3 | +6.635, +8.529, +10.141 |
| mention | A_natural (donor clean − clean) | +5.7273 | [+4.0706, +7.3840] | 3/3 | +4.975, +5.960, +6.246 |
| mention | C at L_x=23 (C/A 1.00 [0.99, 1.02]) | +5.7355 | [+3.9685, +7.5025] | 3/3 | +4.955, +5.905, +6.346 |
| mention | C at L_x=28 (C/A 0.99 [0.98, 1.00]) | +5.6752 | [+3.8986, +7.4518] | 3/3 | +4.866, +5.937, +6.223 |
| mention | C at L_x=32 (C/A 0.99 [0.99, 1.00]) | +5.6958 | [+3.9855, +7.4062] | 3/3 | +4.913, +5.966, +6.208 |
| mention | C at L_x=36 (C/A 0.99 [0.98, 1.00]) | +5.6874 | [+3.9312, +7.4435] | 3/3 | +4.882, +5.975, +6.205 |
| mention | C at L_x=40 (C/A 0.99 [0.98, 1.00]) | +5.6659 | [+3.9179, +7.4139] | 3/3 | +4.866, +5.941, +6.191 |
| mention | C at L_x=44 (C/A 0.99 [0.98, 1.00]) | +5.6912 | [+3.9635, +7.4188] | 3/3 | +4.900, +5.967, +6.206 |
| both | D = C(maintain) − C(mention) at L_x=23 | +2.6891 | [+0.3772, +5.0011] | 3/3 | +1.793, +2.623, +3.651 |
| both | D = C(maintain) − C(mention) at L_x=28 | +2.8707 | [+0.2067, +5.5348] | 3/3 | +1.838, +2.795, +3.979 |
| both | D = C(maintain) − C(mention) at L_x=32 | +2.8671 | [+0.2363, +5.4979] | 3/3 | +1.875, +2.744, +3.982 |
| both | D = C(maintain) − C(mention) at L_x=36 | +2.8400 | [+0.1131, +5.5669] | 3/3 | +1.831, +2.681, +4.009 |
| both | D = C(maintain) − C(mention) at L_x=40 | +2.8050 | [+0.0801, +5.5300] | 3/3 | +1.815, +2.615, +3.984 |
| both | D = C(maintain) − C(mention) at L_x=44 | +2.7438 | [-0.0170, +5.5045] | 3/3 | +1.735, +2.562, +3.935 |

### Prominence (L24–59): donor Y and source X rank statistics after the swap

| arm | condition | Y rank-1 rate | Y median r_min | X rank-1 rate | X median r_min |
|---|---|---|---|---|---|
| maintain | clean | 0.00 | 962 | 0.50 | 2 |
| maintain | 23 | 0.75 | 1 | 0.00 | 740 |
| maintain | 28 | 0.75 | 1 | 0.00 | 656 |
| maintain | 32 | 0.67 | 1 | 0.00 | 671 |
| maintain | 36 | 0.58 | 1 | 0.00 | 594 |
| maintain | 40 | 0.58 | 1 | 0.00 | 112 |
| maintain | 44 | 0.50 | 2 | 0.00 | 120 |
| mention | clean | 0.00 | 1810 | 0.00 | 44 |
| mention | 23 | 0.17 | 64 | 0.00 | 1690 |
| mention | 28 | 0.00 | 55 | 0.00 | 1610 |
| mention | 32 | 0.00 | 59 | 0.00 | 1674 |
| mention | 36 | 0.00 | 53 | 0.00 | 1618 |
| mention | 40 | 0.00 | 46 | 0.00 | 691 |
| mention | 44 | 0.00 | 50 | 0.00 | 731 |

### Damage

| arm | L_x | ΔNLL mean | ΔNLL max | top-1 retention mean | min |
|---|---|---|---|---|---|
| maintain | Lx23 | -0.0000 | +0.0001 | 1.000 | 1.000 |
| maintain | Lx28 | +0.0000 | +0.0001 | 1.000 | 1.000 |
| maintain | Lx32 | +0.0000 | +0.0001 | 1.000 | 1.000 |
| maintain | Lx36 | +0.0000 | +0.0001 | 1.000 | 1.000 |
| maintain | Lx40 | +0.0000 | +0.0001 | 1.000 | 1.000 |
| maintain | Lx44 | +0.0000 | +0.0001 | 1.000 | 1.000 |
| mention | Lx23 | -0.0000 | +0.0001 | 1.000 | 1.000 |
| mention | Lx28 | +0.0000 | +0.0001 | 1.000 | 1.000 |
| mention | Lx32 | +0.0000 | +0.0001 | 1.000 | 1.000 |
| mention | Lx36 | +0.0000 | +0.0001 | 1.000 | 1.000 |
| mention | Lx40 | +0.0000 | +0.0001 | 1.000 | 1.000 |
| mention | Lx44 | +0.0000 | +0.0001 | 1.000 | 1.000 |

Figures: `figures/source_transfer_C_by_Lx.png`, `figures/source_transfer_layer_profile.png`. Machine-readable: `source_transfer_tables.json`.

## 4. Verification and limitations

- Same-source replacement at L_x=36 reproduced the clean run bitwise on every cell; layers < L_x identical between future-X and future-Y on every cell (asserted in the battery).
- n = 3 geometry-matched pairs at pilot scale (orange–guitar was excluded by the geometry rule: `guitar` is two pieces in the quoted context). Intervals are wide by construction; this run calibrates L_x, it does not establish transfer.
- RESID_P is the plain-sentence pair axis fitted on templates 1–8; its scale differs from the lens and is never compared in raw units.

## 5. Interpretation and next decision

**Observation (n=3 geometry-matched calibration pairs, 2 carriers, both arms).** Sustained replacement of the introduced word's span from layer L_x onward moves the later readout toward the donor at every L_x tested, 3/3 pairs on J_NP at both windows and on RESID_P in the maintain arm. At the registered window L48–50 the transferred fraction of the natural X/Y contrast falls with L_x (J_NP maintain: C/A 0.84 at L_x=23, 0.52 at 36, 0.35 at 44); at L51–59 it is nearly complete from any start layer (C/A 0.95 at 36, 0.92 at 44). The late window's readout is therefore dominated by reads of the span that occur at or after block 44; the default window mixes earlier-arrived and later-read content. In the mention arm RESID_P's natural contrast A is itself near zero at L48–50 (+0.01), so its ratio there is undefined; the J_NP and late-window RESID_P rows carry the mention-arm reading.

**Arm difference.** Transfer is larger under maintain than under the mention control at every L_x on both instruments (J_NP L48–50: +0.21 at L_x=36, 3/3; L51–59: +2.02, 3/3; RESID_P L48–50 +0.06, 3/3). This is the earlier pilot's D_36 pattern, reproduced under the new rendering with independent code.

**Decision.** L_x = 36 is frozen for Package 2 (the project's default is usable: C/A ≈ 0.5 at L48–50 and ≈ 0.95 at L51–59, 3/3). The state site remains block 35. Both windows are carried: L48–50 registered primary, L51–59 registered secondary. Damage under every swap: ΔNLL ≤ 0.01, top-1 retention ≥ 0.95 (table above). Nothing here is an estimate of transfer size at evaluation scale; the pilot's purpose was site calibration.
