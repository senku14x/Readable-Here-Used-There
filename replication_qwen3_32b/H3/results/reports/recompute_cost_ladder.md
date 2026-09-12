# H3 · recompute_cost_ladder — run 20260909T165735Z

768 forwards (94.7 s); 3 tiers × 8 items × ['C0', 'C1', 'C2', 'C3'] = 96 cells; cluster = item (n=8 per tier). Each tier is normalised by its own ceiling Δ = donor_clean − clean. `t1` and `t3` use **identical source strings and donors** and differ only in the instruction and the question.

## Competence gate (scored argmax over the 19 number words = the true latent)

| tier | latents | clean competence | ceiling Δ (nats) |
|---|---|---|---|
| t1 memorised (a+b) | four, five, six, seven, eight, nine, ten | **1.000** PASS | +25.47 |
| t3 chained (2(a+b), same source as t1) | eight, ten, twelve, fourteen, sixteen, eighteen, twenty | **0.406** **FAIL (rows not interpreted)** | +14.26 |
| t2 composed (a+b+c) | seven, eight, nine, ten, eleven, twelve, thirteen, fourteen | **0.594** **FAIL (rows not interpreted)** | +19.92 |

## t1 memorised (a+b) — ceiling +25.47 nats; flip floor under clean 0/32

| condition | answer margin toward the donor latent | share of Δ | flips | latent shift at carrier | at question | ΔNLL max |
|---|---|---|---|---|---|---|
| `S_donor0` | +25.48 [+23.23, +27.72] (8/8) | 1.00 | 32/32 | +0.39 [+0.25, +0.54] (8/8) | +1.02 [+0.81, +1.23] (8/8) | +0.0062 |
| `S_donor` | +25.41 [+23.23, +27.59] (8/8) | 1.00 | 32/32 | +0.35 [+0.21, +0.48] (8/8) | +0.99 [+0.80, +1.19] (8/8) | +0.0044 |
| `C_full` | +0.49 [+0.13, +0.84] (8/8) | 0.02 | 0/32 | +0.38 [+0.24, +0.53] (8/8) | +0.03 [+0.01, +0.05] (8/8) | +0.0007 |
| `C_all` | +0.50 [+0.10, +0.91] (8/8) | 0.02 | 0/32 | +0.38 [+0.24, +0.53] (8/8) | +0.03 [+0.01, +0.05] (7/8) | +0.0007 |
| `C_rand` | +0.02 [-0.10, +0.14] (3/8) | 0.00 | 0/32 | +0.03 [+0.01, +0.04] (8/8) | -0.01 [-0.02, -0.00] (1/8) | +0.0052 |
| `NEC_all` | +25.18 [+23.03, +27.33] (8/8) | 0.99 | 32/32 | +0.00 [+0.00, +0.00] (0/8) | +0.99 [+0.78, +1.19] (8/8) | +0.0062 |

## t3 chained (2(a+b), same source as t1) — ceiling +14.26 nats; flip floor under clean 12/32

| condition | answer margin toward the donor latent | share of Δ | flips | latent shift at carrier | at question | ΔNLL max |
|---|---|---|---|---|---|---|
| `S_donor0` | +14.14 [+9.40, +18.88] (8/8) | 0.99 | 22/32 | +0.06 [-0.02, +0.14] (7/8) | +0.32 [+0.17, +0.48] (8/8) | +0.0119 |
| `S_donor` | +13.83 [+8.57, +19.09] (8/8) | 0.97 | 20/32 | +0.04 [-0.01, +0.09] (6/8) | +0.31 [+0.16, +0.45] (8/8) | +0.0060 |
| `C_full` | +0.34 [+0.19, +0.49] (8/8) | 0.02 | 10/32 | +0.06 [-0.02, +0.14] (5/8) | +0.01 [-0.00, +0.03] (6/8) | +0.0004 |
| `C_all` | +0.33 [+0.17, +0.48] (7/8) | 0.02 | 11/32 | +0.06 [-0.02, +0.14] (5/8) | +0.01 [-0.00, +0.03] (6/8) | +0.0004 |
| `C_rand` | +0.03 [-0.08, +0.14] (5/8) | 0.00 | 12/32 | -0.00 [-0.03, +0.03] (4/8) | +0.00 [-0.01, +0.01] (4/8) | +0.0009 |
| `NEC_all` | +13.82 [+8.99, +18.64] (8/8) | 0.97 | 21/32 | +0.00 [+0.00, +0.00] (0/8) | +0.31 [+0.16, +0.46] (8/8) | +0.0119 |

## t2 composed (a+b+c) — ceiling +19.92 nats; flip floor under clean 5/32

| condition | answer margin toward the donor latent | share of Δ | flips | latent shift at carrier | at question | ΔNLL max |
|---|---|---|---|---|---|---|
| `S_donor0` | +19.86 [+17.86, +21.86] (8/8) | 1.00 | 32/32 | +0.03 [-0.01, +0.07] (7/8) | +0.38 [+0.28, +0.49] (8/8) | +0.0297 |
| `S_donor` | +19.81 [+17.80, +21.81] (8/8) | 0.99 | 32/32 | +0.05 [+0.03, +0.07] (7/8) | +0.40 [+0.29, +0.50] (8/8) | +0.0153 |
| `C_full` | +0.13 [-0.05, +0.31] (7/8) | 0.01 | 5/32 | +0.03 [-0.01, +0.06] (6/8) | -0.00 [-0.01, +0.01] (2/8) | +0.0187 |
| `C_all` | +0.04 [-0.12, +0.20] (5/8) | 0.00 | 5/32 | +0.03 [-0.01, +0.06] (6/8) | -0.00 [-0.01, +0.00] (4/8) | +0.0187 |
| `C_rand` | +0.04 [-0.10, +0.17] (3/8) | 0.00 | 5/32 | +0.00 [-0.02, +0.02] (4/8) | -0.00 [-0.01, +0.01] (4/8) | +0.0158 |
| `NEC_all` | +19.82 [+17.85, +21.79] (8/8) | 0.99 | 32/32 | +0.00 [+0.00, +0.00] (0/8) | +0.38 [+0.27, +0.49] (8/8) | +0.0297 |

## The registered contrast: carrier share vs boundary position, by tier

| tier | competence | carrier share `C_full` | carrier share `C_all` | boundary: source share at ≥36 | source share all blocks | `NEC_all` share |
|---|---|---|---|---|---|---|
| t1 memorised (a+b) | 1.000 | **0.02** | 0.02 | **1.00** | 1.00 | 0.99 |
| t3 chained (2(a+b), same source as t1) | 0.406 | **0.02** | 0.02 | **0.97** | 0.99 | 0.97 |
| t2 composed (a+b+c) | 0.594 | **0.01** | 0.00 | **0.99** | 1.00 | 0.99 |

**Primary contrast (paired by item, identical source strings): carrier share t3 − t1 = +0.00 [-0.01, +0.02] (5/8); boundary share t3 − t1 = -0.03 [-0.40, +0.35] (5/8).**

## Interpretation

(written by hand after reading the tables)