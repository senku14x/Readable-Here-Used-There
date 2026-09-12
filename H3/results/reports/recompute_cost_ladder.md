# H3 · recompute_cost_ladder — run 20260909T154529Z

768 forwards (207.8 s); 3 tiers × 8 items × ['C0', 'C1', 'C2', 'C3'] = 96 cells; cluster = item (n=8 per tier). Each tier is normalised by its own ceiling Δ = donor_clean − clean. `t1` and `t3` use **identical source strings and donors** and differ only in the instruction and the question.

## Competence gate (scored argmax over the 19 number words = the true latent)

| tier | latents | clean competence | ceiling Δ (nats) |
|---|---|---|---|
| t1 memorised (a+b) | four, five, six, seven, eight, nine, ten | **1.000** PASS | +22.72 |
| t3 chained (2(a+b), same source as t1) | eight, ten, twelve, fourteen, sixteen, eighteen, twenty | **0.625** **FAIL (rows not interpreted)** | +18.32 |
| t2 composed (a+b+c) | seven, eight, nine, ten, eleven, twelve, thirteen, fourteen | **0.875** **FAIL (rows not interpreted)** | +19.20 |

## t1 memorised (a+b) — ceiling +22.72 nats; flip floor under clean 0/32

| condition | answer margin toward the donor latent | share of Δ | flips | latent shift at carrier | at question | ΔNLL max |
|---|---|---|---|---|---|---|
| `S_donor0` | +22.74 [+21.76, +23.72] (8/8) | 1.00 | 32/32 | +2.30 [+1.94, +2.65] (8/8) | +2.13 [+1.76, +2.51] (8/8) | +0.0025 |
| `S_donor` | +22.34 [+21.47, +23.21] (8/8) | 0.98 | 32/32 | +2.18 [+1.79, +2.57] (8/8) | +1.96 [+1.68, +2.24] (8/8) | +0.0013 |
| `C_full` | +2.86 [+2.14, +3.58] (8/8) | 0.13 | 0/32 | +2.32 [+1.97, +2.66] (8/8) | +0.48 [+0.31, +0.65] (8/8) | +0.0021 |
| `C_all` | +2.87 [+2.16, +3.59] (8/8) | 0.13 | 0/32 | +2.32 [+1.97, +2.66] (8/8) | +0.48 [+0.32, +0.65] (8/8) | +0.0021 |
| `C_rand` | +0.03 [-0.02, +0.08] (6/8) | 0.00 | 0/32 | +0.20 [+0.15, +0.26] (8/8) | +0.04 [+0.02, +0.06] (7/8) | +0.0039 |
| `NEC_all` | +19.97 [+19.08, +20.85] (8/8) | 0.88 | 32/32 | +0.00 [+0.00, +0.00] (0/8) | +1.66 [+1.41, +1.91] (8/8) | +0.0024 |

## t3 chained (2(a+b), same source as t1) — ceiling +18.32 nats; flip floor under clean 4/32

| condition | answer margin toward the donor latent | share of Δ | flips | latent shift at carrier | at question | ΔNLL max |
|---|---|---|---|---|---|---|
| `S_donor0` | +18.36 [+15.22, +21.51] (8/8) | 1.00 | 32/32 | +0.20 [+0.01, +0.39] (7/8) | +0.57 [+0.33, +0.82] (7/8) | +0.0110 |
| `S_donor` | +18.08 [+14.80, +21.36] (8/8) | 0.99 | 32/32 | +0.19 [+0.00, +0.38] (7/8) | +0.51 [+0.28, +0.73] (7/8) | +0.0026 |
| `C_full` | +0.50 [+0.29, +0.71] (8/8) | 0.03 | 4/32 | +0.20 [+0.02, +0.39] (7/8) | +0.06 [+0.01, +0.11] (8/8) | +0.0016 |
| `C_all` | +0.54 [+0.35, +0.73] (8/8) | 0.03 | 4/32 | +0.20 [+0.02, +0.39] (7/8) | +0.05 [+0.00, +0.11] (8/8) | +0.0016 |
| `C_rand` | -0.02 [-0.08, +0.03] (2/8) | -0.00 | 4/32 | +0.02 [-0.02, +0.06] (5/8) | -0.00 [-0.01, +0.01] (5/8) | +0.0006 |
| `NEC_all` | +17.76 [+14.58, +20.94] (8/8) | 0.97 | 32/32 | +0.00 [+0.00, +0.00] (0/8) | +0.53 [+0.32, +0.74] (8/8) | +0.0110 |

## t2 composed (a+b+c) — ceiling +19.20 nats; flip floor under clean 0/32

| condition | answer margin toward the donor latent | share of Δ | flips | latent shift at carrier | at question | ΔNLL max |
|---|---|---|---|---|---|---|
| `S_donor0` | +19.21 [+17.70, +20.72] (8/8) | 1.00 | 32/32 | +0.68 [+0.48, +0.88] (8/8) | +0.77 [+0.57, +0.97] (8/8) | +0.0070 |
| `S_donor` | +18.82 [+17.42, +20.22] (8/8) | 0.98 | 32/32 | +0.62 [+0.43, +0.81] (8/8) | +0.72 [+0.54, +0.91] (8/8) | +0.0016 |
| `C_full` | +2.06 [+1.32, +2.80] (8/8) | 0.11 | 1/32 | +0.67 [+0.47, +0.87] (8/8) | +0.07 [+0.02, +0.13] (7/8) | +0.0043 |
| `C_all` | +2.01 [+1.29, +2.73] (8/8) | 0.10 | 1/32 | +0.67 [+0.47, +0.87] (8/8) | +0.08 [+0.01, +0.14] (7/8) | +0.0043 |
| `C_rand` | +0.06 [-0.13, +0.25] (3/8) | 0.00 | 0/32 | +0.07 [+0.01, +0.13] (7/8) | +0.00 [-0.00, +0.01] (5/8) | +0.0024 |
| `NEC_all` | +17.20 [+15.93, +18.46] (8/8) | 0.90 | 32/32 | +0.00 [+0.00, +0.00] (0/8) | +0.70 [+0.53, +0.86] (8/8) | +0.0070 |

## The registered contrast: carrier share vs boundary position, by tier

| tier | competence | carrier share `C_full` | carrier share `C_all` | boundary: source share at ≥36 | source share all blocks | `NEC_all` share |
|---|---|---|---|---|---|---|
| t1 memorised (a+b) | 1.000 | **0.13** | 0.13 | **0.98** | 1.00 | 0.88 |
| t3 chained (2(a+b), same source as t1) | 0.625 | **0.03** | 0.03 | **0.99** | 1.00 | 0.97 |
| t2 composed (a+b+c) | 0.875 | **0.11** | 0.10 | **0.98** | 1.00 | 0.90 |

**Primary contrast (paired by item, identical source strings): carrier share t3 − t1 = -0.10 [-0.13, -0.07] (0/8); boundary share t3 − t1 = +0.00 [-0.19, +0.20] (5/8).**

## Interpretation (hand-written 2026-09-09)

**The registered primary test could not be run as designed, and the reason is itself the finding.** Competence falls across the ladder exactly as predicted (t1 1.000, t2 0.875, t3 0.625), but two of the three tiers land below the registered 0.9 gate, so by §3 their intervention rows are observations rather than tests. The manipulation was therefore not clean: making the computation harder did not only raise recompute cost, it degraded how reliably the model computes and holds the latent at all. That is visible internally — the donor carrier installs the donor latent at the readout by +2.32 at t1, +0.67 at t2 and +0.20 at t3. There is less of a copy to transplant at the harder tiers, and any behavioural share is bounded by that.

**What the design did achieve: the boundary is held fixed.** The source-donor share from block 36 is 0.98 / 0.98 / 0.99 across the three tiers, statistically identical, against 1.00 for the all-block reference. So within this organism the cut is complete regardless of difficulty, which is what makes the carrier column readable at all.

**With the boundary fixed, the carrier share does not rise with difficulty — it falls.** Paired by item on identical source strings, carrier share t3 − t1 = **−0.10 [−0.13, −0.07], 0/8 items positive**, while the boundary share is unchanged (+0.00 [−0.19, +0.20]). The tier ordering is 0.13 (t1), 0.11 (t2), 0.03 (t3). **The recompute-cost explanation of the sum-versus-two-hop gap gains no support here.** Stated precisely: *this manipulation failed to isolate recompute cost*, because it also degraded competence and the installed readout. It does not establish that recompute cost is irrelevant. I proposed that explanation before this run and am withdrawing it as an account of that gap.

**What that leaves.** The between-organism difference (carrier share 0.08 on the original sum organism, 0.27 on two-hop) now sits alongside a second between-organism difference that this run makes salient: the block-36 source share is ≈ 1.00 in every arithmetic variant tested (original sums, and all three tiers here) and 0.58 on two-hop. The two move together across organisms, and within arithmetic the carrier share does not respond to difficulty once the boundary is fixed. The leading account of the gap is therefore **how much of the source's contribution is already fixed below the cut**, not what kind of latent it is. That is an inference from four organism-level points with the two properties confounded, not a test; a direct test would need a factual organism whose clue is fully resolved above block 36, or an arithmetic organism whose operands are resolved below it.

**What replicates unchanged at every tier, competent or not.** The source route is sufficient without the carrier copy: with the carrier clamped to its own states at all blocks (readout exactly 0.00 on every tier) the answer still follows the source at 0.88 / 0.90 / 0.97 of the ceiling, and the donor latent is rebuilt at the question positions at 78 % / 91 % / 93 % of its free level. The matched random carrier write is inert everywhere. Damage is nil (max ΔNLL 0.011).

**Scope and the design lesson.** Eight items per tier, four carriers, one model, thinking off; t2 and t3 are below the competence gate. The lesson for any repeat: a difficulty ladder that changes the computation also changes whether the latent is maintained, so the two cannot be separated this way. A cleaner manipulation would hold both competence and the latent's readout magnitude fixed and vary only the cost of re-deriving it from the source — for example by moving the source further from the question, or by making it harder to attend to, rather than by making the arithmetic harder.