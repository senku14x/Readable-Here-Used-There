# H1 · steering_decomposition — what do G, v_c and d_c each change at raw dose? (H1.6, minimal version)

**H1.6 (steering decomposition).** Script `H1/scripts/steering_decomposition.py` (stage `grid`); analysis `steering_decomposition_analysis.py`. Status: design, registered before any forward. **Priority: last among H1.** Reason: Package 2 already showed that any block-35 direction's effect on transfer is predicted by its effect on the resident readout (r ≥ 0.85 across 19 directions), so the project's central H1.6 question (does G change source sensitivity while v changes content?) has a strong prior answer: both will change both, in proportion to their resident-readout effect. This battery is run in its minimal form to record dose-response, asymmetry and additivity as the design requires, not because it is expected to change a belief.

## 1. Vectors (exist; `H1/outputs/task_state_modulation/G.npz`)

G (raw mean of d_c over the 16 fitting words, block 35, carrier-pooled C0/C1), d_c and v_c = d_c − G per fitting word (raw, not unit). Names: `shared_word_controlled`, fold = all 16 (identity holdout impossible for d_c/v_c by definition, the holdout definitions; disclosed). Report ‖G‖, ‖d_c‖, ‖v_c‖, split-half cosine of G (0.989) and the cos(v_c, G) distribution.

## 2. Design

Words: the 16 fitting words (d_c requires c in the fit); carriers C0, C1 (the fit contexts; also disclosed). Arms: **maintain with subtraction** h' = h − β r and **mention with addition** h' = h + β r, r ∈ {G, v_c, d_c}, β ∈ {0, 0.5, 1} first; add {0.25, 2} only if the 0.5/1 pair is monotone and damage passes (top-1 retention ≥ 0.95, ΔNLL < 0.05 nats/token). AddVector hook at block 35, interior positions, realized-write stats. A limited crossed-arm set (maintain + addition, mention − subtraction) on 4 words for asymmetry. Equal-dose orientation comparison h' = h + λ r̂, λ = ‖G‖ (separately labelled `unitdose`). Each steered forward is also crossed with the block-36 pair-partner source replacement (donor = word's Package 1 pair partner; use the calibration pairing rule from `task_state_modulation.py`) to obtain C and I.

Readouts: (i) natural presence s_J(X); (ii) counterfactual identity: pair margin toward the partner Y with no swap; (iii) C and I from the swap; (iv) RESID_P presence; (v) rank and damage. Additivity residual S_y = {y(h + βd) − y(h)} − {y(h + βG) − y(h)} − {y(h + βv) − y(h)} per readout y, at β = 1.

## 3. Predictions and readings

| Observation | Reading |
|---|---|
| All three vectors change presence and C in proportion to their resident-readout effect (as Package 2's law) | Confirms the shared-consequence account; v_c is not a content-only handle here. |
| v_c changes identity margin (ii) without changing C | A content/gain dissociation; would be the one result that revises Package 2. |
| G changes C without changing presence | A pure gain that is not a readout gain; contradicts Package 2 (would require re-checking the orthopanel). |
| Non-additive S_y large relative to the single-vector effects | Nonlinearity; report, no interpretation. |

## 4. Decision rules

Cluster = word (n = 16); dose curves reported per vector; no claim of "necessity" from cancellation (cancellation is sensitivity). If damage fails at β = 1 for a vector, report that dose as not readable and do not extrapolate.

## 5. Budget

16 words × 2 carriers × 2 arm-sign combos × 3 vectors × 2 nonzero β × (noswap + swap) = 768, + β = 0 references 64, + unitdose 192, + crossed-arm 96 ≈ 1,100 forwards.
