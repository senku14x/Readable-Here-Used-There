# H1 · tagged_categories — GATE (member-instrument positive control) — run 20260907T020651Z

## 1. Question and setup

Before reading the selection stage: can the member instrument even *see* a maintained category's unshown members? For each eligible category (birds, fish, insects, tools, vehicles, furniture, mammals, vegetables) score the 4 unshown members' aggregate s_bar(c)=mean_members(z_w - mean z_decoys) and the label, under maintain / mention / absent, carriers ['C0', 'C1', 'C3'], interior carrier positions, windows L48-50 and L51-59. Decoys = ['anchor', 'apple', 'arrow', 'badge', 'basket', 'bread', 'brick', 'bridge']. Cluster = category (n=8). **Gate rule (design §4):** maintain must exceed absent on the member aggregate (signs >= 6/8 and 95% CI clear of 0) at >= 1 window, else the member endpoint is 'instrument not validated' and the select stage is read on the label endpoint only. maintain vs mention is reported but not gating.

## 2. Main findings

- **J_NP|member|L48-50:** maintain +0.4527 [-0.4949, +1.4004] (5/8 >0); mention +0.3552 [-0.5741, +1.2845] (4/8 >0); absent +0.2745 [-0.6212, +1.1703] (4/8 >0). maintain-absent +0.1782 [-0.0954, +0.4518] (6/8 >0); maintain-mention +0.0975 [-0.0000, +0.1951] (7/8 >0); mention-absent +0.0806 [-0.1666, +0.3279] (6/8 >0). **gate FAIL**; max-member(maint-abs) +0.4442 [+0.1347, +0.7537] (7/8 >0)
- **J_NP|member|L51-59:** maintain +0.6865 [-0.1361, +1.5090] (6/8 >0); mention +0.6398 [-0.2123, +1.4919] (6/8 >0); absent +0.3216 [-0.4085, +1.0517] (5/8 >0). maintain-absent +0.3648 [+0.1320, +0.5977] (7/8 >0); maintain-mention +0.0466 [-0.0466, +0.1398] (6/8 >0); mention-absent +0.3182 [+0.0868, +0.5496] (7/8 >0). **gate PASS**; max-member(maint-abs) +0.5396 [+0.2437, +0.8355] (8/8 >0)
- **J_NP|label|L48-50:** maintain +1.0239 [-0.0467, +2.0945] (6/8 >0); mention +0.6431 [-0.4425, +1.7287] (5/8 >0); absent -0.0158 [-1.0831, +1.0514] (4/8 >0). maintain-absent +1.0397 [+0.6942, +1.3853] (8/8 >0); maintain-mention +0.3808 [+0.1299, +0.6317] (6/8 >0); mention-absent +0.6589 [+0.4696, +0.8483] (8/8 >0).
- **J_NP|label|L51-59:** maintain +1.2565 [+0.5901, +1.9229] (8/8 >0); mention +1.1247 [+0.2728, +1.9767] (6/8 >0); absent -0.4394 [-1.1608, +0.2819] (2/8 >0). maintain-absent +1.6959 [+1.4265, +1.9653] (8/8 >0); maintain-mention +0.1318 [-0.1423, +0.4058] (6/8 >0); mention-absent +1.5641 [+1.3078, +1.8205] (8/8 >0).
- **LOGITS|member:** maintain +0.1257 [-0.4169, +0.6683] (6/8 >0); mention -0.0122 [-0.5348, +0.5104] (4/8 >0); absent -0.4949 [-0.9856, -0.0043] (2/8 >0). maintain-absent +0.6207 [+0.3709, +0.8704] (8/8 >0); maintain-mention +0.1379 [+0.0299, +0.2459] (7/8 >0); mention-absent +0.4828 [+0.2927, +0.6729] (8/8 >0). **gate PASS**
- **LOGITS|label:** maintain +1.7425 [+0.4115, +3.0735] (7/8 >0); mention +1.3424 [+0.0503, +2.6345] (7/8 >0); absent -0.9517 [-2.2724, +0.3691] (3/8 >0). maintain-absent +2.6942 [+2.3461, +3.0422] (8/8 >0); maintain-mention +0.4001 [+0.1317, +0.6685] (7/8 >0); mention-absent +2.2941 [+2.1361, +2.4520] (8/8 >0).

**Gate decision:** member instrument VALIDATED (passes at L51-59). Holm-adjusted p (J_NP member maint-abs): {"L48-50": 0.1674, "L51-59": 0.0152}.

## 3. Per-member distribution (J_NP member, maintain-absent, mean over carriers)

### L48-50

| category | m1 | m2 | m3 | m4 | members |
|---|---|---|---|---|---|
| birds | +0.132 (owl) | +0.321 (duck) | +0.225 (goose) | +0.647 (pigeon) | +0.331 |
| fish | +0.220 (cod) | +0.136 (carp) | +0.096 (bass) | +0.177 (perch) | +0.157 |
| insects | +0.654 (beetle) | +0.153 (moth) | -0.127 (fly) | +1.016 (mosquito) | +0.424 |
| tools | +0.068 (hammer) | -0.194 (saw) | -0.191 (drill) | -0.431 (axe) | -0.187 |
| vehicles | +0.294 (car) | +0.646 (bicycle) | +0.720 (motorcycle) | +0.519 (scooter) | +0.545 |
| furniture | -0.332 (desk) | -0.418 (bed) | -0.837 (stool) | -0.119 (dresser) | -0.426 |
| mammals | +0.203 (horse) | +0.505 (rabbit) | +0.479 (mouse) | +0.205 (camel) | +0.348 |
| vegetables | +0.375 (cabbage) | +0.228 (spinach) | +0.496 (broccoli) | -0.165 (celery) | +0.234 |

### L51-59

| category | m1 | m2 | m3 | m4 | members |
|---|---|---|---|---|---|
| birds | +0.324 (owl) | +0.377 (duck) | +0.404 (goose) | +0.696 (pigeon) | +0.450 |
| fish | +0.178 (cod) | +0.118 (carp) | +0.231 (bass) | +0.243 (perch) | +0.193 |
| insects | +1.170 (beetle) | +0.646 (moth) | +0.368 (fly) | +1.173 (mosquito) | +0.839 |
| tools | +0.110 (hammer) | -0.086 (saw) | +0.068 (drill) | -0.282 (axe) | -0.048 |
| vehicles | +0.623 (car) | +0.599 (bicycle) | +0.826 (motorcycle) | +0.381 (scooter) | +0.607 |
| furniture | +0.082 (desk) | +0.235 (bed) | +0.046 (stool) | +0.213 (dresser) | +0.144 |
| mammals | +0.174 (horse) | +0.460 (rabbit) | +0.476 (mouse) | +0.187 (camel) | +0.324 |
| vegetables | +0.478 (cabbage) | +0.433 (spinach) | +0.558 (broccoli) | +0.166 (celery) | +0.409 |

## 4. Complete tables

### J_NP|member|L48-50

| quantity | mean | 95% CI | signs>0/n | per-category |
|---|---|---|---|---|
| maintain | +0.4527 | [-0.4949,+1.4004] | 5/8 | +1.190, -0.564, +1.011, -0.940, +0.128, +0.197, -0.035, +2.634 |
| mention | +0.3552 | [-0.5741,+1.2845] | 4/8 | +1.100, -0.522, +0.668, -0.991, -0.053, +0.130, -0.083, +2.592 |
| absent | +0.2745 | [-0.6212,+1.1703] | 4/8 | +0.858, -0.721, +0.587, -0.752, -0.417, +0.623, -0.383, +2.401 |
| maint_abs | +0.1782 | [-0.0954,+0.4518] | 6/8 | +0.331, +0.157, +0.424, -0.187, +0.545, -0.426, +0.348, +0.234 |
| maint_ment | +0.0975 | [-0.0000,+0.1951] | 7/8 | +0.089, -0.042, +0.343, +0.052, +0.181, +0.067, +0.048, +0.042 |
| ment_abs | +0.0806 | [-0.1666,+0.3279] | 6/8 | +0.242, +0.199, +0.081, -0.239, +0.364, -0.493, +0.300, +0.192 |

### J_NP|member|L51-59

| quantity | mean | 95% CI | signs>0/n | per-category |
|---|---|---|---|---|
| maintain | +0.6865 | [-0.1361,+1.5090] | 6/8 | +1.669, -0.455, +1.026, -0.597, +0.655, +0.981, +0.033, +2.180 |
| mention | +0.6398 | [-0.2123,+1.4919] | 6/8 | +1.572, -0.518, +0.803, -0.705, +0.631, +0.918, +0.090, +2.328 |
| absent | +0.3216 | [-0.4085,+1.0517] | 5/8 | +1.218, -0.648, +0.187, -0.550, +0.048, +0.837, -0.291, +1.771 |
| maint_abs | +0.3648 | [+0.1320,+0.5977] | 7/8 | +0.450, +0.193, +0.839, -0.048, +0.607, +0.144, +0.324, +0.409 |
| maint_ment | +0.0466 | [-0.0466,+0.1398] | 6/8 | +0.097, +0.062, +0.224, +0.107, +0.024, +0.063, -0.057, -0.148 |
| ment_abs | +0.3182 | [+0.0868,+0.5496] | 7/8 | +0.353, +0.130, +0.616, -0.155, +0.583, +0.081, +0.381, +0.557 |

### J_NP|label|L48-50

| quantity | mean | 95% CI | signs>0/n | per-category |
|---|---|---|---|---|
| maintain | +1.0239 | [-0.0467,+2.0945] | 6/8 | +1.331, -0.602, +2.207, -0.778, +0.154, +1.525, +1.714, +2.640 |
| mention | +0.6431 | [-0.4425,+1.7287] | 5/8 | +0.982, -0.544, +1.636, -1.435, -0.125, +0.765, +1.212, +2.654 |
| absent | -0.0158 | [-1.0831,+1.0514] | 4/8 | +0.564, -1.182, +0.967, -1.842, -0.869, -0.028, +0.117, +2.144 |
| maint_abs | +1.0397 | [+0.6942,+1.3853] | 8/8 | +0.767, +0.580, +1.239, +1.064, +1.023, +1.552, +1.597, +0.496 |
| maint_ment | +0.3808 | [+0.1299,+0.6317] | 6/8 | +0.349, -0.058, +0.571, +0.658, +0.279, +0.760, +0.503, -0.014 |
| ment_abs | +0.6589 | [+0.4696,+0.8483] | 8/8 | +0.418, +0.638, +0.669, +0.406, +0.744, +0.793, +1.094, +0.510 |

### J_NP|label|L51-59

| quantity | mean | 95% CI | signs>0/n | per-category |
|---|---|---|---|---|
| maintain | +1.2565 | [+0.5901,+1.9229] | 8/8 | +1.567, +0.163, +1.997, +0.066, +1.102, +2.070, +1.132, +1.955 |
| mention | +1.1247 | [+0.2728,+1.9767] | 6/8 | +1.111, -0.079, +1.821, -0.527, +1.106, +2.058, +1.068, +2.441 |
| absent | -0.4394 | [-1.1608,+0.2819] | 2/8 | -0.178, -1.546, -0.181, -1.560, -0.623, +0.327, -0.695, +0.942 |
| maint_abs | +1.6959 | [+1.4265,+1.9653] | 8/8 | +1.745, +1.709, +2.179, +1.626, +1.726, +1.742, +1.827, +1.013 |
| maint_ment | +0.1318 | [-0.1423,+0.4058] | 6/8 | +0.457, +0.241, +0.176, +0.593, -0.003, +0.012, +0.064, -0.486 |
| ment_abs | +1.5641 | [+1.3078,+1.8205] | 8/8 | +1.288, +1.467, +2.002, +1.033, +1.729, +1.730, +1.763, +1.500 |

### LOGITS|member

| quantity | mean | 95% CI | signs>0/n | per-category |
|---|---|---|---|---|
| maintain | +0.1257 | [-0.4169,+0.6683] | 6/8 | +0.577, +0.069, +0.185, -0.667, +0.949, +0.265, +0.594, -0.967 |
| mention | -0.0122 | [-0.5348,+0.5104] | 4/8 | +0.372, -0.003, -0.164, -0.828, +0.709, +0.148, +0.642, -0.974 |
| absent | -0.4949 | [-0.9856,-0.0043] | 2/8 | -0.317, -0.166, -0.881, -0.949, +0.088, -0.309, +0.138, -1.563 |
| maint_abs | +0.6207 | [+0.3709,+0.8704] | 8/8 | +0.894, +0.235, +1.066, +0.283, +0.861, +0.575, +0.455, +0.596 |
| maint_ment | +0.1379 | [+0.0299,+0.2459] | 7/8 | +0.205, +0.072, +0.349, +0.161, +0.240, +0.118, -0.049, +0.007 |
| ment_abs | +0.4828 | [+0.2927,+0.6729] | 8/8 | +0.689, +0.163, +0.718, +0.121, +0.621, +0.457, +0.504, +0.589 |

### LOGITS|label

| quantity | mean | 95% CI | signs>0/n | per-category |
|---|---|---|---|---|
| maintain | +1.7425 | [+0.4115,+3.0735] | 7/8 | +2.124, +3.326, +0.875, +2.870, +2.246, +3.376, -1.001, +0.124 |
| mention | +1.3424 | [+0.0503,+2.6345] | 7/8 | +1.500, +3.009, +0.109, +2.220, +1.571, +3.310, -1.193, +0.213 |
| absent | -0.9517 | [-2.2724,+0.3691] | 3/8 | -0.569, +0.605, -2.541, +0.029, -0.706, +0.988, -3.549, -1.871 |
| maint_abs | +2.6942 | [+2.3461,+3.0422] | 8/8 | +2.693, +2.721, +3.416, +2.840, +2.951, +2.388, +2.548, +1.995 |
| maint_ment | +0.4001 | [+0.1317,+0.6685] | 7/8 | +0.624, +0.317, +0.765, +0.650, +0.674, +0.067, +0.193, -0.089 |
| ment_abs | +2.2941 | [+2.1361,+2.4520] | 8/8 | +2.069, +2.404, +2.651, +2.191, +2.277, +2.322, +2.355, +2.084 |

## 5. Interpretation and next decision

**Observation.** A maintained category raises its four unshown members over the absent condition by +0.36 [+0.13, +0.60] (7/8 categories) at L51-59 -- the member instrument's positive control **passes** there -- but by only +0.18 [-0.10, +0.45] (6/8) at L48-50, where the CI includes 0 (**fails**). The label endpoint is far stronger and cleaner (maintain-minus-absent +1.70 at L51-59, 8/8; LOGITS label +2.69). maintain-minus-mention is small (+0.05 member, +0.13 label at L51-59): most of the maintain-minus-absent gap is *mention* (naming the category loads it -- paper A.10), not maintenance per se.

**What this licenses.** The member instrument has demonstrated sensitivity at L51-59, so the select-stage member endpoint is interpretable there and is read primarily at L51-59. At L48-50 the member instrument is *not* validated -- and tools/furniture members invert under maintenance -- so any L48-50 member claim rests on the more sensitive swap contrast, not this positive control. The strong, even label/LOGITS gate confirms the labels themselves are robustly read on this new lexical set.

**Caveat / non-implication.** That the gate is largely a mention effect does not weaken the selection test: the select stage points at one of three categories that are *all* named, so mention is held constant across pointed and unpointed arms. The gate's job is only to show the member instrument can see a present category's members -- which it does at L51-59.

**Next.** Proceed to the select stage on the member endpoint at L51-59 (primary), reporting L48-50 as secondary with the instrument caveat. (Done: see `tagged_categories_select.md`.)
