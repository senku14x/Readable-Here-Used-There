# `trying_to_fool` — can a bounded upstream perturbation forge a J-lens reading that independent, held-out checks do not confirm?

**Registered 2026-09-09, before any forward.** Supersedes the pasted "attack calibration round" draft, which is kept below as the operational basis; changes are per an external critique that was accepted in full. Governing spec section: the project design §H3.6.

## 0. What this measures, and what it does not

This is a test of **adversarial susceptibility under activation access**: whether a small write at block 35, on the carrier positions of the copy organism, can produce a substantial J-lens signal for a target identity Y at the L48–50 readout **that fails independent checks which normally detect the corresponding natural identity change**. It is *not* a measurement of the lens's natural false-positive rate during ordinary audits, and it does not bear on whether the model "uses" anything. The paper and Nanda's review both already allow for imperfect readouts; the contribution, if any, is a bounded, held-out-audited discrepancy, or its absence under a bounded search.

## 1. What is fixed by the critique (differences from the draft)

1. **Identity-specific forge only.** For each nominated ordered pair X→Y, one vector δ ∈ R^d, **broadcast** across the interior carrier positions, added once at block 35. Fit on calibration carriers; evaluate the *same* δ on held-out carriers and fresh code assignments. The claim is transfer across contexts for that identity. No universal vector; hide is deferred.
2. **An evaluator the optimizer never sees.** Optimisation objective: J_NP margin (target) + preservation of one plain-sentence axis `RESID_P^fit` (templates 1–8) + LOGITS + behaviour + damage. **Audit** (never in the loss, never used to pick a checkpoint/seed/radius): a second plain-sentence axis `RESID_P^audit` fitted on the disjoint templates 9–12; `cbr` (a different readout construction — a second instrument, not ground truth); held-out carriers C2/C3; fresh codebook assignments.
3. **Forge means Y rises.** Success requires Δz_Y ≥ ½·A_J^Y (Y's own presence swing under the natural prompt change) *and* Δm_J(Y−X) ≥ ½·A_J, with Y's full-vocabulary rank reported. A margin gain produced by lowering z_X is classified as a hide, not a forge.
4. **Operational outcome labels**, not A/B/C: (i) J target reached; held-out audit instruments within their bands; (ii) J and audit instruments move together; behaviour within band; (iii) readouts and behaviour move together; (iv) target not reached / damage gate failed / preservation inconclusive (band not resolvable). Mixed cases are reported as mixed.
5. **Controls closest to the attack.** (a) `C1c`: natural carrier transplant at **block 35 only** — the Y-run's block-35 interior carrier states written into the X-run (the same site, duration and positions as the attack, natural content). (b) An **unconstrained** attack at the same site and radius (J target only, no preservation terms): tells whether the target is reachable at all, so a constrained failure is interpretable. (c) Norm-matched random writes (damage and noise floor only; not a reachability control).
6. **Constants defined completely.** Differentiate the actual scorer `z = (a_v·t)/r(t)` with numerator and RMS saved; per-instrument repeat floor from a bitwise repeat *and* a one-token length change (the two are different phenomena); `D_max` = mean over seeds and cells of ΔNLL under the 2×ρ_nat random write, floored at 0 and at the repeat floor; top-1 retention is an **evaluation gate** (≥ 0.95), not a loss term; all preservation weights 1 in natural units (a choice, stated); radii are a scale reference, not a manifold claim, and the **realized** bf16 write is measured (ρ, κ) on every attack vector.

## 2. Materials and firewall

Organism: `Here is the word "{X}". Keep that word in mind while you copy the following text exactly, word for word: {carrier}` (the controlled maintain arm), teacher-forced carrier, then a consumer turn: a six-entry codebook over {X, Y, 4 decoys} with random single letters, and `Using the code, what is the letter for the word introduced in the first message? Answer with the letter only.` Behaviour b = log P(F(Y)) − log P(F(X)) at the answer token, logsumexp over surface forms.
- **Calibration / fitting:** the 8 calibration words as 4 unordered pairs, both directions; carriers C0, C1; codebook seed A.
- **Held-out audit:** carriers C2, C3; codebook seed B; the same identities (transfer across contexts, per item 1). The 16 evaluation-bank pairs are reserved for a second stage if the first is informative.
- Sites: injection block 35, interior carrier positions; readout W = L48–50 primary, L51–59 secondary.

## 3. Calibration round (forward-only; this run)

- `C1` clean maintain-X / maintain-Y on C0/C1: A_k (natural Y−X margin swing) on J_NP, RESID_P^fit, RESID_P^audit, cbr, LOGITS; A_J^Y (Y presence swing); A_b (behavioural swing **from the prompt change**); ρ_nat = mean per-position ‖h35(Y) − h35(X)‖ on interior positions.
- `C1b` source donor from block 36 (readout co-movement reference; **not** a validation of the attack's own path).
- `C1c` **block-35 carrier transplant** (the attack-shaped positive control): does a natural write at the attack's site reach W and the audit instruments?
- `C2` repeat floor: bitwise repeat of 4 clean forwards, and a one-token length change, per instrument.
- `C3` random writes at {0.5, 1, 2}·ρ_nat, 3 seeds, 2 cells: D_max, noise floor on J.
- **Reachability probe (unconstrained, gradient-free, cheap):** the naming direction a_Y − a_X at block 35, scaled to {0.5, 1, 2}·ρ_nat — the obvious steering baseline. If this alone reaches the J target, the gradient search is not needed to establish reachability.

Gates (frozen): **G1** A_{RESID_P^audit} > 0 with CI clear of 0 and A_cbr > 0 (else stop: an insensitive audit cannot detect a spoof); G2 A_J > 0; G3 C1c moves J and the audit axis together (the attack site can reach both); G4 random J shift ≪ T_J; G5 every band exceeds its instrument's repeat floor.

Frozen from this run: T_J = ½·A_J, T_Y = ½·A_J^Y, ε_k = 0.2·A_k per instrument, ε_b = 0.2·A_b, radii {0.5, 1, 2}·ρ_nat, D_max, top-1 ≥ 0.95.

## 4. Predictions, on record

1. G1 passes on the primary model (the plain-sentence axes saw natural identity changes throughout H1).
2. C1c (block-35 carrier transplant) moves J and the audit axis together and moves b little — the same shape as the carrier donor in H3.
3. The naming-direction steer at ≤ 2·ρ_nat reaches T_J on J_NP **and** moves RESID_P^audit with it (outcome ii). A vector that reaches T_J with RESID_P^audit inside its band (outcome i) is *not* expected from this baseline; if the constrained search finds one on held-out contexts, that is the result, and the follow-up is diagnosing what it exploited (RMS normalisation, an axis blind spot) before anything else.
4. Behaviour stays inside ε_b under every forge (readable ≠ used holds here by construction); this is a consistency check, not a finding.

## 5. Budget and stop rules

Calibration ≈ 70 forwards. Constrained search (next stage, only if G1–G5 pass): AdamW on δ with the model frozen, ≤ 100 steps, 3 seeds, projected to ‖δ‖ ≤ ρ, finite-difference checked on one cell; if the differentiable path fails, a predefined low-dimensional subspace search with the same endpoints, not full-dimensional SPSA. Evaluate once on the reserved contexts; report every outcome. If G1 fails, stop the branch; a readout-geometry calculation may be reported but is not a substitute for the block-35 → L48–50 transport test.


## Amendment 1 — calibration outcome and the repaired gate (registered 2026-09-09 after `calibration.md`; nothing further run)

G1 failed at the registered L48–50 audit window as a **power** failure (three clusters; audit axis 3/3 positive, interval touching zero) and G3 failed (a natural single-block write at 35 reaches 0.03 of the swing at L51–59). Per §5, no constrained search was built. The unconstrained naming-direction steer reached the J target at **half** the smallest radius and pulled every held-out readout with it (outcome ii), with behaviour and damage unchanged — the adversarial form of the H3 dissociation, without optimisation.

**Repaired design for any next stage:** audit window **L51–59** (where every instrument sees the natural identity change with clear intervals); materials extended to the **16 evaluation-bank pairs** for power, with C0/C1 fitting and C2/C3 audit unchanged; the forge criterion unchanged (Y must rise: T_Y and full-vocabulary rank); the constrained objective's sole purpose restated as finding a direction ≥ 10× more J-selective than the naming direction, which is the quantity to report whether or not it is found. Predictions: the naming direction's J-versus-audit selectivity ratio (≈ 0.6 at L48–50) is representative, and a bounded search will not exceed 3×; a vector that does is the result and its exploited component (RMS normalisation, an axis blind spot) is the follow-up.

## Amendment 2 — the constrained search as run (registered 2026-09-09, before any forward; researcher's request: a sanity study, not for any submission)

**Materials.** The 16 evaluation-bank pairs (all geometry-clean under this tokenizer, checked), **one direction per pair** (bank order, X→Y) to halve the search cost; fitting carriers C0/C1 with codebook seed A; audit carriers C2/C3 with codebook seed B. Decoys `M.DECOYS[:4]`. Audit window **L51–59** (Amendment 1).

**Stage `bank`.** Clean X/Y forwards on C0–C3 give the natural swings per instrument at L51–59 (J_NP margin and Y presence, R_CB, RESID_fit and RESID_audit pair axes, interior LOGITS margin, behaviour b) and ρ_nat, cluster = pair (n = 16); the naming-direction steer at {0.5, 1, 2}·ρ_nat on the audit carriers is the reachability and selectivity baseline. Frozen from it: T_J = ½A_J, T_Y = ½A_J^Y, ε_k = 0.2·A_k, ε_b = 0.2·A_b.

**Stage `search`.** One δ ∈ R^d per pair, broadcast over the interior carrier positions, added at block 35, Adam (lr 0.15·radius) for 60 steps, projected to ‖δ‖ ≤ 1.0·ρ_nat after each step, one seed. Objective, maximised, summed over the two fitting carriers: Δm_J/A_J + Δs_Y/A_J^Y − (Δm_p^fit/A_p)² − (Δb/A_b)² − (ΔLOGITS/A_L)² − (relu(ΔNLL)/0.02)². The audit axis, R_CB, the audit carriers and the seed-B codebooks never enter the loss or any selection. Model parameters frozen; gradients only on δ; the scorer is the float32 diagnostic z = (a_v·t)/r on the transported residual.

**Stage `audit`.** The final δ applied on C2/C3 (seed B) and, for reference, on C0/C1; every instrument recorded, plus Y's best full-vocabulary rank, ΔNLL, top-1 retention, realized ρ/κ; beside it the naming steer scaled to the **same realized norm** in the same cell. Endpoints per cell: shares Δk/A_k for every instrument; the **selectivity ratio** (ΔJ/A_J)/(ΔRESID_audit/A_audit) for the attack and for the steer; outcome label (i) J target and T_Y reached with RESID_audit and R_CB inside ε and b inside ε_b; (ii) J and audit instruments move together; (iii) readouts and behaviour move; (iv) target not reached or damage failed. Cluster = pair.

**Predictions, on record.** (1) The naming steer at 1·ρ_nat reaches T_J and T_Y on the audit carriers and moves RESID_audit and R_CB at ≥ their own bands (outcome ii), as in the calibration. (2) The constrained δ reaches T_J on the fitting carriers. (3) On the held-out carriers and codes its selectivity ratio does not exceed 3× the steer's, and it does not achieve outcome (i) on more than 4 of 16 pairs. (4) Behaviour stays inside ε_b for both. (5) ΔNLL ≤ 0.02, top-1 retention ≥ 0.95. If (3) fails — a δ that reaches the J target on held-out contexts while the audit axis and R_CB stay inside their bands — the result is a bounded, held-out-audited lens/semantics discrepancy and the follow-up is what it exploits (RMS normalisation, the audit axis's blind spot), not a larger search.

Budget: bank ≈ 64 × 2 + 32 × 3 = 224 forwards + 432 axis forwards; search 16 × 60 × 2 = 1,920 forward+backward passes; audit 16 × 4 × 3 = 192 forwards.
