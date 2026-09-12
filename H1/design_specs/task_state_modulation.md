# H1 · task_state_modulation — does a fitted task-associated coordinate change the later effect of a source counterfactual?

**Package 2 (task-state pilot), covering H1.3–H1.5.** Script `H1/scripts/task_state_modulation.py` (stages `fit`, `pilot`, `evaluate`); analysis `task_state_modulation_analysis.py`. Outputs `H1/outputs/task_state_modulation/`; results `H1/results/task_state_modulation.md`.

## Question and why it matters

H1's core claim is that a manipulable task-associated state, moved before the source counterfactual begins, changes the later response to source information. Package 1 established that post-L36 source replacement reaches the readout (C/A ≈ 0.5 at L48–50, ≈ 0.95 at L51–59) and that maintain transfers more than the mention control. Package 2 asks whether one fitted coordinate at block 35, set to the other arm's natural level on carrier positions, reproduces part of that arm difference in the incremental effect of a source perturbation introduced only from block 36.

## Hypothesis and strongest alternatives (H1.1)

- **Shared task modulation:** moving the coordinate toward the mention level lowers C (ΔC_M < 0) and toward the maintain level raises it (ΔC_N > 0), across held-out identities; the move itself installs little consistent donor identity without a source.
- **Content installation:** the fitted direction carries concept content; the move changes the readout without changing future-source sensitivity.
- **Generic state sensitivity:** equal-dose moves along matched directions reproduce the interaction.
- **Prompt-specific handle:** the native fit works but a fit from another wording does not.
- **J-selective measurement response:** J moves disproportionately after calibration; RESID_P has a small equivalent effect.

## Materials and fitting (the frozen word banks and carriers, H1.3)

- **Shared direction G** fitted on the 16 fitting words × arms {maintain, mention} × carriers {C0, C1}: d_c = mean_k(h̄_{c,M,k}) − mean_k(h̄_{c,N,k}) with h̄ the interior-position mean of the block-35 output; G = mean_c d_c; v_c = d_c − G; ĝ = G/‖G‖. Raw vectors and norms stored; split-half reliability (words 1–8 vs 9–16) reported as cos and as the fraction of ‖G‖² shared.
- **Control panel (frozen from fit-word residuals only):** 4 isotropic unit directions (seed 20260907), 4 covariance-matched directions from the per-position block-35 interior residual covariance of the fit words (full covariance, u ∝ Σ^{1/2} ξ, computed from the centered residual matrix), 2 leading background PCs of that covariance, 2 unrelated semantic axes (plain-sentence one-vs-centroid directions of the decoys `dragon` and `horse` at layer 35, from `natural_modulation/resid_axis.npz`). All unprojected. Cosines with ĝ recorded.
- **Pilot materials:** calibration pairs (orange, tiger), (guitar, mountain), (diamond, castle), carriers C0, C1 (fitting carriers; disclosed). **Evaluation:** Banks 1 and 2 (8 + 8 pairs) on carriers C2, C3, run only after the pilot's gates pass and this document's tolerances are frozen.

## Interventions (H1.4)

- State move at block-output 35, interior carrier positions: h′ = h + α_t ĝ with α_t = L*_{c,ā} − ĝ·h_35,t, where L* is the opposite-arm natural level of the recipient word (mean over interior positions of ĝ·h in that word's clean opposite-arm run, same carrier). α_t is computed from the clean run once and reused in swap and no-swap conditions.
- Source counterfactual: span block outputs ← arm-matched donor Y from block 36 onward (L_x = 36 frozen by Package 1).
- Factorial per directed pair, arm, carrier: {clean, state-moved} × {no-swap, swap36}; same-source gate; layer ≤ 35 identity assert between future-X and future-Y; realized-write readback (ρ, κ) on every state move.
- Controls: each panel direction u_i receives exactly the candidate's signed α_t (h′ = h + α_t u_i), both arms, both phases.
- Dose rows (maintain arm): scale 0.5 and 2 on ĝ.

## Metrics (H1.4, §4.6)

- C_k(q, a) = m_k(swap) − m_k(noswap); A_k = C_k(0, M) − C_k(0, N); ΔC_{k,M} = C_k(q_M, M) − C_k(0, M); ΔC_{k,N} = C_k(q_N, N) − C_k(0, N); I_k = ½[−ΔC_{k,M} + ΔC_{k,N}], for k ∈ {J_NP (bf16 path), RESID_P pair axis, LOGITS}, at windows L48–50 (primary) and L51–59 (secondary).
- Calibrated I_k / A_k with the natural arm difference as the denominator (ratio of cluster means, pair bootstrap).
- Current-content effect of the move: Δm(noswap) and Δs_J(X, noswap) (does the move change what is read before any source change?).
- Realized writes: ρ ∈ [0.9, 1.1], κ ≥ 0.99 per cell; damage: ΔNLL, top-1 retention ≥ 0.95.
- Cluster = unordered pair (both directions and carriers averaged within); pilot n = 3, evaluation n = 8 per bank and 16 pooled with bank agreement reported.

## Predictions and interpretation

| Outcome | Reading |
|---|---|
| ΔC_M < 0 and ΔC_N > 0, I above the whole control panel, RESID_P agrees | shared task modulation, specific under this panel |
| Reciprocal I but one or more controls match it | generic state sensitivity; specificity not licensed |
| One-sided ΔC only | asymmetry reported; inspect arm floors/ceilings |
| Move changes m(noswap) but I ≈ 0 (equivalence band ±20 % of A) | content installation without future-transfer control |
| I on J only, RESID_P equivalent to zero | J-selective response; instrument comparison before any channel claim |
| Realized-write gate fails | repair before any reading |

## Budget

Fit: 64 forwards. Pilot: per directed cell ≈ 2 clean (shared per pair) + 1 same-source + 1 swap + 2 (ĝ) + 4 (dose) + 24 (12 controls × 2 phases) ≈ 33; 3 pairs × 2 directions × 2 arms × 2 carriers = 24 cells → ≈ 800 forwards, ≈ 6 min. Evaluation: 16 pairs × 2 × 2 × 2 = 128 cells → ≈ 4,200 forwards, ≈ 30 min.

## Amendment 1 (2026-09-07, registered before the run): ĝ-orthogonalized panel on the pilot cells

Pilot finding: the interaction reproduces along panel directions in proportion to their cosine with ĝ (pc01 cos 0.30 → 97 % of I at L48–50; cov01 cos 0.18 → 90 %); directions orthogonal to ĝ give small or opposite effects. An unprojected panel therefore cannot separate "ĝ carries the effect" from "any high-variance direction carries it".

Added stage `orthopanel`, same 24 pilot cells (3 pairs × 2 directions × 2 arms × C0/C1), same clean-derived signed α_t:
- the 12 panel directions with their ĝ component projected out and renormalized (`*_perp`), asserted cos(u_perp, ĝ) < 1e-4;
- 4 covariance-matched directions sampled in the ĝ-orthogonal complement (`covperp00–03`);
- ĝ itself, re-run as a determinism replication gate (must reproduce the pilot's ĝ rows bitwise);
- native-level rows for `pc01` and `cov01`: h′ = h + (L*_u − u·h) u with L*_u the recipient word's opposite-arm level along u (a different question: is u an independent handle at its own natural dose?).

Predictions. Shared task modulation specific to ĝ: ĝ reciprocal as before; every `*_perp` and `covperp` direction well below it (registered bar: max |I_perp| < 0.5 |I_ĝ| on J_NP at both windows) and not reciprocal 3/3. Generic sensitivity: some orthogonalized direction retains ≥ 0.5 |I_ĝ| with reciprocal sign. Native-level rows are reported descriptively (a native-level move along a direction with cos 0.30 to ĝ moves the ĝ coordinate by 0.30 × its own gap and is not an independent test).
Budget ≈ 1,000 forwards.
