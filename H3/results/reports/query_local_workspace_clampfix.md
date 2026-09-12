# H3 · query_local_workspace stage `clampfix` — Amendment 3 control repairs: norm-matched orthogonal clamps and the realized write

**Design:** `H3/design_specs/query_local_workspace.md`, Amendment 3 + implementation note (registered before the forward). **Run:** 702 forwards (126 axis-fit + 576 scientific), 215 s; artifacts `H3/outputs/query_local_workspace/{raw,meta,manifest}_clampfix.*`; tables `query_local_workspace_clampfix_tables.json`. 8 sums × C0–C3 × two consumers; cluster = sum (df = 7), carriers averaged. Model Qwen3.6-27B, thinking off, blocks 36–62.

## 1. What was repaired

The audit found three defects in the question-clamp rows: the orthogonal control was not norm-matched (a gentler perturbation than the naming-plane clamp), the emission-excluded clamp (`clampsplit`) had no orthogonal control at all, and `CoordClamp`/`CoordSwap` logged the *requested* delta as `realized`. This stage reruns every clamp with `CoordClampMatched`, which records the post-cast realized write (ρ, κ, per-position norms), and pairs each naming-plane clamp with a random orthogonal 2-plane clamp whose per-position delta is rescaled, cell by cell and layer by layer, to the naming clamp's realized per-position norm.

## 2. Result

Margin = log P(donor value) − log P(own value) at the answer, minus clean; all rows are `NEC` (donor operands, carrier clamped to own) plus the named question-site clamp.

| condition | parity margin [95 % CI] | parity flips | report margin [95 % CI] | report flips | write norm (req / realized) |
|---|---|---|---|---|---|
| `NEC` (reference) | +3.18 [+2.21, +4.15] | 17/32 | +19.26 [+17.92, +20.61] | 32/32 | — |
| `NEC_Qclamp` (naming plane, all question tokens) | +2.94 | 16/32 | **+1.75** [+1.24, +2.26] | 0/32 | 0.23 / 0.22 (parity), 0.48 / 0.47 (report) |
| `NEC_Qclamp_perpm` (orthogonal plane, norm-matched) | +3.16 | 17/32 | **+19.21** [+17.79, +20.64] | 32/32 | same |
| `NEC_Qclamp_noans` (naming plane, answer position excluded) | +3.15 | 17/32 | **+11.79** [+10.29, +13.28] | 20/32 | 0.20 / 0.19, 0.42 / 0.42 |
| `NEC_Qclamp_noans_perpm` | +3.18 | 17/32 | **+19.22** [+17.86, +20.59] | 32/32 | same |
| `NEC_Qclamp_ansonly` (answer position only) | +2.96 | 16/32 | +5.56 [+4.14, +6.98] | 0/32 | 1.44 / 1.44, 2.50 / 2.50 |
| `NEC_Qclamp_ansonly_perpm` | +3.15 | 18/32 | +19.24 [+17.81, +20.68] | 32/32 | same |

- Every norm-matched orthogonal control leaves both consumers at the `NEC` reference (report within 0.05 nats, parity within 0.03, flips unchanged). The earlier rows reproduce: the emission-excluded naming clamp removes **38.8 %** of the report margin (19.26 → 11.79) and 12/32 flips, and moves parity by 0.03 nats.
- **The registered predictions are met**, so the phrase withdrawn after the audit, that the report consumer draws roughly 40 % of its answer margin on the reconstructed sum representation at the question tokens while parity is insensitive to that plane, is licensed again, now against a control of identical write size in an orthogonal plane.

## 3. The realized write — a gate failure that must travel with every coordinate-level row

The post-cast measurement shows what the requested-norm logging hid. For the question-token clamps the requested per-position delta is 0.2–0.5 in residual norm; after the cast back to bf16 the realized write has **ρ ≈ 0.53–0.59 and κ ≈ 0.42–0.48** averaged over positions and layers (per-layer values 0.27–0.56 and 0.20–0.44 in a typical cell), against the project gate ρ ∈ [0.9, 1.1], κ ≥ 0.99. The answer-only clamps, with 5–10× larger deltas, reach ρ 0.77–0.86, κ 0.69–0.78; still failing. The mechanism is precision, not a bug in the hook: a residual entry of magnitude a few units has a bf16 step of about 0.02–0.04, and over 5120 dimensions that rounding is of the same size as a 0.2–0.5 write. Read-back of the naming-plane coordinates after the clamp confirms the plane is pinned only to within 0.14–0.21 of the clean coordinates (0.04–0.05 for the answer-only clamp).

What this does and does not undermine:
- The **effect is not a rounding artifact**: the norm-matched orthogonal control carries rounding of the same magnitude and is inert on both consumers.
- The **clamp under-delivers**: the plane is moved most of the way, not all the way, so "removes ~40 % of the report margin" is a lower bound on what a precise clamp would do, and the parity null is a null against a partial clamp. The registered prediction "ρ ∈ [0.9, 1.1], κ ≥ 0.99 for every clamp" is **not met**.
- The same limitation applies to **every earlier `CoordClamp` and `CoordSwap` row** in this project (the sum-word swaps of `computed_sum_consumer` Amendment 3, `Q_swap`, and today's `bridgeswap` stage, whose per-position deltas of 2–5 sit in the ρ ≈ 0.8 regime), whose `realized` fields were requested norms. Their behavioural effects stand, with matched controls where run; their write fidelity was never at the declared gate. Repair would need the affected blocks to run their hooked outputs in float32, which is out of scope today and is registered as the open item.

## 4. Claims table changes

- `STATUS.md` known control weaknesses 1 and 2 are **closed** by this stage: the orthogonal controls are norm-matched, `clampsplit` has its controls, and the realized write is measured.
- A **new** weakness replaces them: coordinate-level writes below ≈ 1 in residual norm are realized at ρ ≈ 0.5–0.6, κ ≈ 0.4–0.5 in bf16; all coordinate-level rows carry this.
- The "≈ 40 % mediation at the question tokens, parity bypasses the plane" statement returns to **supported**, with the under-delivery caveat attached.
