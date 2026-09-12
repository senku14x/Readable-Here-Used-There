# trying_to_fool — calibration (run 20260909T191034Z, 284 forwards)

Cells 12 (excluded by geometry: ['thunder->rocket|C0', 'thunder->rocket|C1', 'rocket->thunder|C0', 'rocket->thunder|C1']); cluster = unordered pair (n = 3).

## Natural swings A_k at L48-50 (maintain-Y minus maintain-X, margin Y−X) and intervention shares

| instrument | A_k (natural) | C1b source donor ≥36, share of A | C1c block-35 carrier transplant, share of A |
|---|---|---|---|
| J_NP | +0.830 [+0.402, +1.258] (3/3) | +0.518 [+0.062, +0.973] (3/3) | +0.263 [+0.107, +0.418] (3/3) |
| RESID_fit | +0.213 [+0.083, +0.343] (3/3) | +0.469 [-0.031, +0.968] (3/3) | +0.302 [-0.045, +0.648] (3/3) |
| RESID_audit | +0.190 [-0.008, +0.388] (3/3) | +0.519 [+0.007, +1.032] (3/3) | +0.237 [-0.407, +0.881] (2/3) |
| R_CB | +0.407 [+0.116, +0.699] (3/3) | +0.557 [+0.040, +1.073] (3/3) | +0.215 [-0.039, +0.469] (3/3) |
| LOGITS | +8.553 [+4.277, +12.830] (3/3) | +0.995 [+0.461, +1.530] (3/3) | +0.005 [-0.023, +0.032] (2/3) |

A_J^Y (Y presence swing, J_NP): +0.415 [+0.201, +0.629] (3/3)

## Natural swings A_k at L51-59 (maintain-Y minus maintain-X, margin Y−X) and intervention shares

| instrument | A_k (natural) | C1b source donor ≥36, share of A | C1c block-35 carrier transplant, share of A |
|---|---|---|---|
| J_NP | +4.036 [+1.162, +6.910] (3/3) | +0.954 [+0.202, +1.706] (3/3) | +0.025 [-0.015, +0.064] (3/3) |
| RESID_fit | +2.876 [+0.822, +4.930] (3/3) | +0.927 [+0.189, +1.664] (3/3) | +0.084 [+0.055, +0.113] (3/3) |
| RESID_audit | +2.972 [+0.946, +4.999] (3/3) | +0.949 [+0.179, +1.718] (3/3) | +0.055 [-0.001, +0.110] (3/3) |
| R_CB | +2.250 [+0.568, +3.931] (3/3) | +0.976 [+0.183, +1.769] (3/3) | +0.016 [-0.001, +0.033] (3/3) |
| LOGITS | +8.553 [+4.277, +12.830] (3/3) | +0.995 [+0.461, +1.530] (3/3) | +0.005 [-0.023, +0.032] (2/3) |

A_J^Y (Y presence swing, J_NP): +2.018 [+0.581, +3.455] (3/3)

**A_b (behavioural swing from the prompt change):** +12.942 [+12.293, +13.591] (3/3) nats. **ρ_nat (per-position ‖Δh35‖):** +6.972 [+4.329, +9.614] (3/3).

C1b/C1c behaviour shift, share of A_b: C1b +0.073 [+0.050, +0.095] (3/3), C1c +0.003 [+0.001, +0.005] (3/3)

## Repeat floors (per instrument): bitwise repeat, and a one-token-longer question

| instrument | max |Δ| bitwise repeat | max |Δ| length change |
|---|---|---|
| J_NP | 0.00e+00 | 0.032 |
| RESID_fit | 0.00e+00 | 0.029 |
| RESID_audit | 0.00e+00 | 0.020 |
| R_CB | 0.00e+00 | 0.017 |
| LOGITS | 0.00e+00 | 0.085 |
| behaviour b | 0.00e+00 | 0.615 |

Bitwise repeat identical: True.

## Random writes (noise floor and damage) and the naming-direction steer (unconstrained reachability), J_NP at L48-50

| radius (×ρ_nat) | random: ΔJ margin | random: ΔNLL mean / max | random: top-1 ret min | steer: ΔJ margin (share of A) | steer: ΔY presence (share of A_J^Y) | steer: ΔRESID_audit (share) | steer: Δb (share of A_b) | steer: ΔNLL max | steer realized κ min |
|---|---|---|---|---|---|---|---|---|---|
| 0.5 | +0.000 (max |0.054|) | +0.0000 / +0.0000 | 1.000 | +2.808 [+1.175, +4.442] (3/3) | +2.783 [+1.198, +4.369] (3/3) | +4.524 [+2.145, +6.903] (3/3) | +0.002 [-0.000, +0.003] (3/3) | +0.0000 | 0.9997 |
| 1.0 | -0.013 (max |0.133|) | -0.0000 / +0.0000 | 1.000 | +5.608 [+2.372, +8.844] (3/3) | +5.619 [+2.390, +8.848] (3/3) | +9.104 [+4.300, +13.909] (3/3) | +0.002 [-0.006, +0.010] (2/3) | +0.0000 | 0.9999 |
| 2.0 | -0.009 (max |0.421|) | -0.0000 / +0.0000 | 1.000 | +11.237 [+4.778, +17.696] (3/3) | +11.511 [+4.833, +18.188] (3/3) | +18.460 [+8.501, +28.419] (3/3) | +0.003 [-0.005, +0.011] (2/3) | +0.0000 | 1.0000 |
## Gates

- G1_audit_axis_sees_identity: **FAIL**
- G2_J_target_defined: **PASS**
- G3_block35_transplant_reaches_J_and_audit: **FAIL**
- G4_random_J_below_target: **PASS**
- G5_bands_exceed_floors: **PASS**

## Frozen constants

```json
{
 "T_J": 0.4150914400815964,
 "T_Y": 0.20754569148023924,
 "eps": {
  "J_NP": 0.16603657603263855,
  "RESID_fit": 0.04259574015935262,
  "RESID_audit": 0.037952092289924626,
  "R_CB": 0.08147584001223246,
  "LOGITS": 1.7106896082560223
 },
 "eps_b": 2.5884395599365235,
 "rho_nat": 6.971662441889445,
 "radii": [
  3.4858312209447226,
  6.971662441889445,
  13.94332488377889
 ],
 "D_max": 0.0,
 "top1_min": 0.95,
 "window": "L48-50",
 "gates": {
  "G1_audit_axis_sees_identity": false,
  "G2_J_target_defined": true,
  "G3_block35_transplant_reaches_J_and_audit": false,
  "G4_random_J_below_target": true,
  "G5_bands_exceed_floors": true
 },
 "steer_reaches_T_J_at": [
  0.5,
  1.0,
  2.0
 ]
}
```

## Reading (hand-written 2026-09-09)

**Two registered gates failed and the stop rule is honoured. The unconstrained baseline establishes *reachability* — it does not test whether optimisation can separate J from the preservation instruments, which is what the constrained search was for. That remains untested.**

1. **G1 fails at the registered window, as a power failure, not insensitivity.** The held-out plain-sentence axis sees the natural identity change at L48–50 in 3/3 pairs, but with three clusters its interval touches zero (+0.19 [−0.008, +0.39]). At L51–59 it is clear (+2.97 [+0.95, +5.00]), as are R_CB and the fitting axis. The project's stop rule is applied as written: **no constrained attack is built on this calibration.** The repair is registered below (audit at L51–59, sixteen bank pairs), not improvised.

2. **G3 fails at both windows, and worse at the deeper one: a natural single-block write at the attack site barely propagates.** Moving the audit window to L51–59 (the Amendment 1 repair for G1) does not rescue G3; it takes it from 0.26 to 0.025. Transplanting the Y-run's block-35 carrier states into the X-run moves J by 0.26 of the natural swing at L48–50 and **0.03 at L51–59**; the audit axis 0.24 (interval spanning zero) and 0.06. The block-36 source donor, by contrast, reaches 0.52 and 0.95. So the attack-shaped positive control does not reach the surfacing band on its own. Any attack vector that does is doing something a natural one-block write does not, which is a fact to state about it rather than a strength.

3. **The naive steer forges the lens trivially — and every other readout sees it.** Adding the naming-direction difference a_Y − a_X at block 35, scaled to **half** a natural footprint, moves the J margin by **2.8×** the natural identity swing (target was 0.5×), raises Y's own presence by 2.8× its swing, and and pulls Y's **best full-vocabulary rank anywhere in the L48–59 window** (the per-cell minimum over layers and positions, median across cells) from 1018 to 326; at 2× ρ_nat the margin is 11× and that best rank is **5** (the natural Y prompt gives 1). This is a best-case-position statistic, not typical prominence across the window. Carrier damage is zero, top-1 retention 1.000, realized κ ≥ 0.9997, and behaviour moves by 0.002–0.003 of its natural swing. **But the held-out audit axis moves 4.5× and 18.5× its own swing at the same radii, R_CB 3.1× and 12.6×, and at L51–59 all four readouts co-move at 0.2–1.1.** This is outcome (ii) exactly: J and the audit instruments move together, behaviour stays in band.

**At L51–59, the same picture with different numbers:** steer at 2·ρ_nat gives J 0.98, fitting axis 1.08, **held-out audit axis 1.08**, cbr 0.89 — the audit axis still moves slightly *more* than J. The non-selectivity conclusion holds at both windows; only the apparent cheapness is window-dependent.

**What that establishes.** With activation access and a bounded write, the J-lens reading of an identity is reachable at a cost well inside a natural perturbation, and this particular direction is not J-selective: the held-out readouts move with it, more than J does relative to their own swings. Co-movement supports a **broad representational perturbation** rather than a J-only artefact; it does not establish that genuine semantic content for Y was installed, which these instruments cannot settle. Behaviour is unchanged, so the pattern is the adversarial analogue of the H3 dissociation, obtained with no optimisation. The random writes at the same radii move J by ≤ 0.05 of the swing, so this is direction-specific.

**What it says about the spoof question, which is still open.** For a bounded vector to reach T_J while holding the audit axis inside its band, it would need to be at least an order of magnitude more J-selective than the naming direction (which moves the audit axis 1.6× *harder* than J, relative to their swings). That is now a well-posed geometric question — how much of the block-35-to-L48–50 transport is J-specific — and it is the only thing the constrained search would add. The co-movement also bears out the critic's caveat numerically: the plain-sentence axis and the lens naming direction share enough geometry that "independent" is a qualification, not a guarantee.

**Not established:** whether optimisation can separate J from the preservation instruments (the constrained search was never built); anything about hide; anything at evaluation scale (three geometry-matched pairs); typical rank prominence, as opposed to best-position rank. The pair (thunder, rocket) was excluded by the donor-geometry rule (4/16 cells), as in Package 1.