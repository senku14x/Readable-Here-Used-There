# trying_to_fool — adversarial susceptibility of the J-lens readout (held separately; not analysed by the researcher; not for submission)

**Status.** This document collects everything the project produced under H3.6 (measurement attacks) on 2026-09-09: the calibration stage (284 forwards) and the constrained forge search registered as Amendment 2 of `H3/trying_to_fool/design_spec.md` (bank 880, search 1,920 forward+backward, audit 192). It was removed from `context/full_project_writeup_2026-09-09.md` at the researcher's request. The "Reading" section below was written by the assistant immediately after the audit and has **not** been checked by the researcher; treat every interpretation in it as provisional. No H1 or H3 claim in the project cites any number here.

**Where the raw material is.** Design and amendments: `H3/trying_to_fool/design_spec.md`. Calibration: `H3/trying_to_fool/calibration.md`. Code: `H3/trying_to_fool/attack.py` (stages bank/search/audit), `H3/trying_to_fool/analyze_attack.py`. Outputs: `H3/trying_to_fool/outputs/` (`raw_/meta_/manifest_{bank,search,audit}`, `search_deltas.pt`, `bank_constants.json`; `bank_axes.pt` is 178 MB, gitignored, mirrored on the HF dataset `senku21x/tcsif-outputs` at the same path). Generated results table: `H3/trying_to_fool/attack_results.md` (reproduced verbatim in Part B).

**Method in one paragraph.** For each of 16 evaluation-bank word pairs X→Y, a vector δ ∈ R^5120 is added to the block-35 output at the interior carrier positions and optimised by Adam (60 steps, lr 0.15) under a norm projection ‖δ‖ ≤ ρ_nat = 8.98 (the natural block-35 footprint). Objective: raise the J_NP margin for Y and Y's J_NP presence at L51–59, penalised by movement of the fitting plain-sentence axis (RESID_fit, templates 1–8), the LOGITS margin, the codebook consumer's behaviour b, and carrier ΔNLL (> 0.02 nats). Fitting carriers C0/C1 with codebook seed A. Audit on carriers C2/C3 with codebook seed B, on instruments never in the loss: the audit plain-sentence axis (templates 9–12), R_CB, and the held-out behaviour. Shares are Δ divided by each instrument's natural Y−X swing A_k; outcome labels (i)–(iv) per Amendment 2.

---

## Part A — the calibration section as it stood in the full write-up (§6.5, verbatim)

### trying_to_fool — adversarial susceptibility of the readout (calibration only, 284 forwards)

**Why.** H3.6: can a bounded write produce a lens reading that independent, held-out checks do not confirm? The design (revised per an external critique): identity-specific forge vectors at block 35 on carrier positions; an evaluator never in the objective (a second plain-sentence axis on disjoint templates, R_CB, held-out carriers, fresh codes); "forge" requires Y itself to rise; controls closest to the attack (a natural block-35 carrier transplant; an unconstrained steer; random writes).

**Calibration outcome.** Gate G1 (the held-out audit axis sees the natural identity change at the registered window L48–50) failed as a power failure (3/3 positive, interval touching zero at n = 3; clear at L51–59); gate G3 (a natural block-35 carrier transplant reaches the readout and the audit axis together) failed at both windows (0.26 of the swing at L48–50, 0.03 at L51–59, against 0.52 / 0.95 for the block-36 source donor). Per the stop rule no constrained search was built. The unconstrained naming-direction steer \(a_Y - a_X\) at half a natural footprint moved the J margin by 2.8× the natural swing (target 0.5×), raised Y's presence 2.8× and pulled Y's best full-vocabulary rank in the window from 1018 to 326 (at 2× footprint: 11× and rank 5), with zero damage and no behavioral change, **and every held-out readout moved with it** (audit axis 4.5×, R_CB 3.1×). Random writes at the same radii moved J by ≤ 0.05 of the swing.

**What the numbers mean.** With activation access the lens reading of an identity is reachable at a cost inside a natural perturbation, but this direction is not J-selective: the plain-sentence axis and the lens direction share enough geometry that the "independent" instrument moves harder than the lens. Reachability is established; whether optimisation can separate J from the preservation instruments is untested (Amendment 1 registers the repaired design at L51–59 on the 16 bank pairs, unrun). A window-dependence caveat was added later: the apparent cheapness of the steer depends on the window; the non-selectivity conclusion does not.


---

## Part B — constrained search and audit (`H3/trying_to_fool/attack_results.md`, verbatim)

# trying_to_fool — constrained forge search, audit (search run 20260909T213358Z, audit run 20260909T215316Z)

16 bank pairs, one direction each; δ fitted on C0/C1 (seed-A codes) for 60 Adam steps at radius 1.0·ρ_nat = 8.98; audited on C2/C3 (seed-B codes). Cluster = unordered pair (n = 16). Shares are Δ/A_k with A_k the natural Y−X swing of each instrument at L51–59 (bank stage). Targets: T_J = 2.53 (½A_J), T_Y = 1.26; bands ε_k = 0.2·A_k; ε_b = 2.40 nats.

## Held-out carriers C2/C3, fresh codes (the audit)

| instrument | attack δ: share of A_k | naming steer at the same norm: share of A_k |
|---|---|---|
| J_NP | +0.712 [+0.412, +1.011] (14/16) | +0.523 [+0.490, +0.556] (16/16) |
| R_CB | +0.733 [+0.395, +1.071] (13/16) | +0.465 [+0.445, +0.485] (16/16) |
| RESID_fit | +0.065 [-0.120, +0.251] (9/16) | +0.612 [+0.530, +0.694] (16/16) |
| RESID_audit | -0.031 [-0.261, +0.199] (9/16) | +0.608 [+0.532, +0.685] (16/16) |
| LOGITS | +0.119 [-0.005, +0.243] (11/16) | +0.108 [+0.089, +0.127] (16/16) |
| Y presence (J_NP), share of A_J^Y | +2.131 [+1.449, +2.813] (16/16) | +0.549 [+0.502, +0.596] (16/16) |
| behaviour b, share of A_b | +0.010 [+0.000, +0.019] (11/16) | -0.003 [-0.007, +0.000] (4/16) |

Selectivity ratio (J share) / |audit-axis share|, per pair then averaged: attack +16.019 [-10.541, +42.580] (15/16); steer +0.920 [+0.809, +1.031] (16/16); median attack 1.90, steer 0.92.
Y's best full-vocabulary rank in L51–59 (median over cells): clean 1323, attack 2, steer 412.
Damage: ΔNLL mean +0.0001, max +0.0004; top-1 retention min 1.000. Realized write ρ 1.000, κ 0.9999. cos(δ, naming direction) mean +0.128.

### Outcome per pair (audit carriers)

| pair | label | ΔJ/A_J | ΔY/A_J^Y | Δaudit/A | ΔR_CB/A | Δb/A_b | ΔNLL max |
|---|---|---|---|---|---|---|---|
| cat–dress | (ii) J and audit instruments move together | +1.20 | +2.91 | +0.61 | +1.10 | +0.00 | +0.0000 |
| snake–turtle | (ii) J and audit instruments move together | +1.08 | +3.51 | -0.18 | +1.33 | +0.00 | +0.0001 |
| airport–fish | (ii) J and audit instruments move together | +0.89 | +3.39 | +0.24 | +0.91 | +0.05 | +0.0004 |
| library–toy | (iv) not reached / damage | +0.17 | +1.45 | -0.48 | -0.01 | +0.01 | +0.0000 |
| dish–moon | (ii) J and audit instruments move together | +1.83 | +4.07 | +0.08 | +1.98 | +0.00 | +0.0001 |
| fort–heart | (ii) J and audit instruments move together | +1.03 | +2.75 | -0.61 | +1.27 | +0.01 | +0.0001 |
| bubble–rug | (iv) not reached / damage | +0.33 | +0.38 | +0.23 | +0.38 | -0.01 | -0.0000 |
| bear–coal | (ii) J and audit instruments move together | +0.78 | +1.90 | +0.62 | +0.71 | +0.04 | +0.0001 |
| card–lake | (iv) not reached / damage | +0.13 | +0.11 | +0.12 | +0.14 | -0.00 | -0.0000 |
| glass–silver | (iv) not reached / damage | +0.31 | +2.31 | -0.88 | +0.38 | +0.01 | +0.0002 |
| river–shield | (ii) J and audit instruments move together | +0.76 | +2.31 | -0.37 | +0.74 | +0.01 | +0.0000 |
| monkey–queen | (iv) not reached / damage | -0.01 | +1.19 | -0.37 | -0.14 | -0.00 | +0.0001 |
| king–paper | (ii) J and audit instruments move together | +1.40 | +3.34 | +0.34 | +1.51 | +0.02 | +0.0001 |
| gold–train | (iv) not reached / damage | -0.11 | +0.24 | -0.18 | -0.14 | -0.00 | +0.0000 |
| cup–engine | (ii) J and audit instruments move together | +1.23 | +3.27 | +0.02 | +1.23 | +0.02 | +0.0001 |
| letter–sword | (iv) not reached / damage | +0.38 | +0.96 | +0.31 | +0.34 | -0.01 | +0.0000 |

Counts: (ii) J and audit instruments move together: 9, (iv) not reached / damage: 7

## Fitting carriers C0/C1 (in-sample reference)

| instrument | attack δ: share of A_k | naming steer at the same norm: share of A_k |
|---|---|---|
| J_NP | +1.867 [+1.318, +2.416] (16/16) | +0.541 [+0.499, +0.584] (16/16) |
| R_CB | +2.172 [+1.434, +2.910] (16/16) | +0.487 [+0.447, +0.527] (16/16) |
| RESID_fit | +0.416 [+0.132, +0.700] (13/16) | +0.657 [+0.566, +0.747] (16/16) |
| RESID_audit | +0.364 [-0.149, +0.877] (11/16) | +0.653 [+0.563, +0.743] (16/16) |
| LOGITS | +0.472 [+0.320, +0.624] (15/16) | +0.113 [+0.088, +0.138] (16/16) |
| Y presence (J_NP), share of A_J^Y | +4.435 [+3.365, +5.504] (16/16) | +0.557 [+0.508, +0.605] (16/16) |
| behaviour b, share of A_b | +0.012 [+0.007, +0.018] (14/16) | -0.002 [-0.004, +0.001] (6/16) |

Selectivity ratio (J share) / |audit-axis share|, per pair then averaged: attack +10.419 [+1.053, +19.785] (16/16); steer +0.891 [+0.756, +1.027] (16/16); median attack 3.62, steer 0.85.
Y's best full-vocabulary rank in L51–59 (median over cells): clean 1696, attack 1, steer 480.
Damage: ΔNLL mean +0.0002, max +0.0015; top-1 retention min 1.000. Realized write ρ 1.000, κ 0.9999. cos(δ, naming direction) mean +0.128.

## Search curves (fitting carriers; final step)

| pair | obj | ΔJ/A_J | ΔY/A_J^Y | Δfit-axis/A | Δb/A_b | ΔNLL |
|---|---|---|---|---|---|---|
| cat->dress|r1.0 | +4.20 | +1.36 | +3.18 | +0.42 | -0.00 | +0.0000 |
| snake->turtle|r1.0 | +5.36 | +1.57 | +4.04 | +0.28 | +0.01 | +0.0003 |
| airport->fish|r1.0 | +5.73 | +1.85 | +4.59 | +0.56 | +0.02 | +0.0000 |
| library->toy|r1.0 | +3.93 | +1.23 | +3.53 | +0.77 | +0.02 | +0.0000 |
| dish->moon|r1.0 | +5.23 | +1.36 | +4.23 | -0.56 | +0.00 | +0.0005 |
| fort->heart|r1.0 | +6.19 | +2.18 | +4.80 | +0.62 | +0.03 | +0.0001 |
| bubble->rug|r1.0 | +4.10 | +1.88 | +3.77 | +0.69 | -0.00 | +0.0003 |
| bear->coal|r1.0 | +2.17 | +0.42 | +1.86 | -0.02 | +0.01 | +0.0000 |
| card->lake|r1.0 | +0.30 | +0.19 | +0.14 | +0.14 | -0.00 | -0.0000 |
| glass->silver|r1.0 | +7.24 | +2.12 | +5.75 | +0.37 | +0.01 | +0.0001 |
| river->shield|r1.0 | +7.97 | +2.29 | +6.27 | +0.57 | +0.02 | +0.0003 |
| monkey->queen|r1.0 | +4.94 | +1.44 | +4.01 | -0.36 | +0.00 | +0.0007 |
| king->paper|r1.0 | +6.86 | +2.49 | +5.47 | +0.74 | +0.02 | +0.0001 |
| gold->train|r1.0 | +11.91 | +4.36 | +9.23 | +0.61 | +0.01 | +0.0152 |
| cup->engine|r1.0 | +10.65 | +3.67 | +7.61 | +0.26 | +0.01 | +0.0005 |
| letter->sword|r1.0 | +8.62 | +2.99 | +6.13 | -0.10 | +0.01 | +0.0040 |

## Reading (hand-written 2026-09-09, after the audit; a sanity study run at the researcher's request, not part of any submission)

**Gates.** Realized writes exact at this norm (ρ 1.000, κ 0.9999; ‖δ‖ = 8.98 ≈ ρ_nat, far above the bf16 rounding floor). Carrier damage nil on every cell (ΔNLL max 0.0004 held-out, 0.0015 in-sample; top-1 retention 1.000). Behaviour inside its band everywhere (≤ 0.05 of the natural 12-nat swing). The audit instruments, carriers and codes were never in the loss.

**1. The search finds vectors that transfer, on 9 of 16 pairs.** On the held-out carriers with fresh codes, the fitted δ moves the J_NP margin by 0.71 of the natural swing (14/16) and the target's J_NP presence by 2.1× its swing (16/16), taking the target's best full-vocabulary rank in L51–59 from a median of 1323 to **2**; the naming steer at the same norm reaches 0.52 and rank 412. Seven pairs did not transfer (library–toy, bubble–rug, card–lake, glass–silver, monkey–queen, gold–train, letter–sword): two never reached the target even in-sample (bear–coal 0.42, card–lake 0.19) and gold–train went from 4.4× in-sample to −0.1 held-out, i.e. it fitted the two training carriers. Prediction 2 (reach T_J in-sample) held on 14/16; transfer is the weaker step.

**2. The plain-sentence axes do not see it, and that includes the held-out one.** The axis in the loss stays at +0.07 of its swing (9/16), and the audit axis fitted on templates the optimizer never saw stays at **−0.03 [−0.26, +0.20]** (9/16), while the naming steer moves both by 0.61. So the constraint generalised: the optimizer found a block-35 direction that raises the lens reading of Y at L51–59 without moving the mean-difference residual direction for Y, and that separation is not specific to the eight fitting templates.

**3. The R-lens moves with the J-lens.** R_CB rises by 0.73 of its swing (13/16), the same size as the J_NP move and above the steer's 0.47. On every pair where the J target is reached, R_CB is far outside its ±0.2 band (0.7–2.0). So no pair achieves outcome (i): 9 are (ii), J and the audit *instruments* move together, and 7 are (iv). Against the plain-sentence audit axis alone, three pairs (snake–turtle, dish–moon, cup–engine) would have been outcome (i): J at 1.1–1.8× the swing, Y presence 3–4×, the held-out axis inside ±0.2, behaviour flat. **It is the second lens that catches them, not the probe.**

**4. What was and was not fooled.** With activation access and a bounded, damage-free write within a natural footprint, one can install a J-lens reading of an identity (rank 2 in the vocabulary, presence twice the natural swing) that a mean-difference probe for that identity, fitted on held-out contexts, does not register, and that the model's own output at the carrier and its answer at a codebook consumer do not reflect (LOGITS +0.12, behaviour +0.01). A readout of the same family (the R-lens) does register it. Two readings of the dissociation are both consistent with the data: the write installs Y-content that unembedding-side readouts see and residual-space probes are blind to; or it installs a readout artefact that both lens constructions share because both read through the final norm and unembedding, and the probes are right that no Y-content was added. The behavioural and LOGITS nulls favour the second reading but cannot settle it, since behaviour was also flat under the natural block-35 carrier transplant in calibration (G3 failure).

**5. Against the registered predictions.** (1) met (steer reaches T_J and T_Y and moves the audit axis and R_CB at ≥ their bands). (2) met on 14/16 in-sample. (3) the selectivity ratio against the *plain-sentence* audit axis is not bounded by 3× the steer's — median 1.9 held-out and 3.6 in-sample, with per-pair values up to 40+ because the axis share is ≈ 0 — but the ratio against R_CB is ≈ 1, the same as the steer's; and (i) was reached on 0/16 pairs with R_CB in the audit, 3/16 without it. (4) met. (5) met. The registered follow-up applies: the exploited component is a direction orthogonal to the plain-sentence axis that both lenses read, and the next question is whether it is the shared unembedding geometry (a naming-direction component orthogonal to the residual mean-difference) or genuine content; a test is whether the found δ transfers across *identities* (it was fitted per pair) and whether an audit probe fitted on the model's own generations, rather than templates, sees it.

**Scope.** One radius (1.0·ρ_nat), one seed, 60 steps, one direction per pair, block 35, window L51–59, thinking off, the primary model. Not run: radii 0.5 and 2, the reverse directions, the hide objective, the constrained search with R_CB in the loss (which would test whether *both* lens constructions can be defeated at once).

---

## Part C — what is not yet done

Registered but unrun (Amendment 2 scope note): radii 0.5 and 2.0·ρ_nat; the reverse direction of each pair; the hide objective; the constrained search with R_CB in the loss (would test whether both lens constructions can be defeated together); transfer of a fitted δ across identities; an audit probe fitted on the model's own generations rather than templates. A cheap descriptive check discussed but not run: the 16 fitted δ's share a component (mean pairwise cosine 0.257; top singular value 2.29 against ≈ 1 for the rest), which is the "general fooling vector" question; tests would be its cosine with the naming direction ĝ, a leave-one-out mean δ applied to the left-out pair, and the mean δ applied to calibration words.
