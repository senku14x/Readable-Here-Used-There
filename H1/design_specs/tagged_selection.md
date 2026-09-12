# H1 · tagged_selection — does the instruction select which source is carried, or scale whichever word is sourced?

**Spec section H1.8 (selection) with the H1.4 state move crossed into it.** Script `H1/scripts/tagged_selection.py` (stages `pilot`, later `evaluate`); analysis `tagged_selection_analysis.py`. Outputs `H1/outputs/tagged_selection/`; results `H1/results/tagged_selection.md`. Status: design, registered before any forward.

## 1. Why this experiment now

Package 2 showed that the block-35 direction ĝ reciprocally changes both the resident readout of the introduced word and the incremental transfer of a post-block-36 source replacement, and that directions with no ĝ component do the same at the default window. Across all 19 directions tested the transfer interaction is predicted (r ≥ 0.97) by the direction's effect on the resident readout with no source change. The single-source organism therefore cannot separate two accounts:

- **Gain on the sourced word (G).** Task state, ĝ, and other high-variance directions scale the readability of whatever word is currently sourced. Resident and incoming content scale together. Nothing chooses among words.
- **Selection (S).** Task state determines *which* available source is carried. Relevance raises the pointed source's influence and does not raise, or suppresses, the others.

With one source these make identical lens predictions. With three simultaneously available sources and an arbitrary pointer they do not. This experiment is chosen because it produces an observation G cannot produce, and because its primary result does not depend on ĝ at all.

## 2. Organism (the tagged-selection and computed-sum organisms, exact strings)

User turn, maintain arm:

```
Here are three words: (A) "{X1}", (B) "{X2}", (C) "{X3}". Keep the word tagged {T} in mind while you copy the following text exactly, word for word:

{carrier}
```

Control arm: `Here are three words: (A) "{X1}", (B) "{X2}", (C) "{X3}". Those words occur one time. Now copy the following text exactly, word for word:\n\n{carrier}`. Assistant turn: the carrier, teacher-forced. Tags A/B/C are fixed labels; the pointed tag T ∈ {A, B, C} and the ordinal position of each lexical identity are counterbalanced (below), so relevance is carried by an arbitrary tag and is not confounded with position or identity.

## 3. Materials (frozen before the first forward)

- **Pilot triples (4)** from words already exposed at calibration, all single-piece in the quoted context (asserted at render; a word failing the check is replaced from the reserve and logged): T1 = (orange, tiger, castle), T2 = (diamond, rocket, dragon), T3 = (forest, hammer, horse), T4 = (lion, knife, fork). Reserve: drawer. Exposure note: T1–T2 words were Package 1/2 calibration words; T2–T4 words were Package 1 decoys. This is a pilot; the confirmatory set is separate.
- **Decoy columns for the pilot (frozen):** the 8 fitting words `anchor, apple, arrow, badge, basket, bread, brick, bridge` (never sources here; their only prior use is the G fit on the single-word organism, which is not an instrument in this experiment's primary rows).
- **Evaluation triples (later, untouched now):** 8 triples formed from the 32 evaluation-bank words by a registered rule (consecutive words of Bank 1 then Bank 2, geometry-checked), decoys from the fitting words.
- **Donor for source j:** the same rendering with X_j replaced by a donor word Y_j drawn from a different triple at the same ordinal position; geometry (token count of the quoted span and of the whole prompt) must match, asserted per cell. Donor identity is fixed per (triple, j) before outcomes.
- **Carriers:** C0, C1 for the pilot; C2, C3 for evaluation.
- **Rotations:** each triple is rendered in its 3 cyclic rotations, so each lexical identity occupies each ordinal position once.

## 4. Conditions and interventions

**Stage A: natural selectivity (no fitted direction).** For each triple × rotation × carrier: arms {pointed A, pointed B, pointed C, control}. Per arm: clean forward; source replacement for each j ∈ {1, 2, 3} (span block outputs ← donor Y_j from block 36 onward, L_x frozen by Package 1); same-source gate at j = 1 (bitwise equal to clean). Layers < 36 identity asserted.

**Stage B: the state move crossed with relevance.** Under each pointed arm, the frozen single-word ĝ (`task_state_modulation/G.npz`; a cross-organism transfer, disclosed) is moved on interior carrier positions to the control arm's level (measured on this organism from the control-arm clean run of the same triple/rotation/carrier), with the same clean-derived α_t in swap and no-swap phases, for each source replacement j. Reverse move (control → pointed level) uses the pointed arm's level; by construction the control arm carries no pointer, so the reverse row is reported as one-sided (the earlier pilot's PT-5 lesson).

**Stage B2: a native pointer contrast (address candidate).** From Stage A clean runs only (no swap outcome read): d_pointer(A→B) = mean over triples, rotations, carriers of [h̄_35 | pointed B] − [h̄_35 | pointed A], with identities and positions balanced by the rotation design. Applied as a level move under the pointed-A arm (A-level → B-level along unit d_pointer, same clean-derived α_t rule), crossed with all three source replacements. Also fitted: the shared pointed-minus-control direction on this organism, d_shared = mean over tags of [pointed T] − [control], as the native gain candidate.

**Realized writes** (ρ, κ) on every move; **damage** (carrier ΔNLL, top-1 retention) on every intervened forward; **output-disposition screen**: final-layer rank of each of the three words at interior positions must stay far from the top (median rank > 100) in every arm, otherwise the arm is flagged.

## 5. Measurements

Per forward, at interior carrier positions, lens layers 0–62 saved; windows L48–50 and L51–59 co-primary (Package 1 decision):

- Per source j: pair margin m_j = E[z_{Y_j} − z_{X_j}] (J_NP bf16 path), the plain-sentence pair axis p_{Y_j − X_j} (RESID_P, fitted from `natural_modulation/resid_axis.npz`; words lacking an axis get one fitted first, same templates), and the output log-prob margin (LOGITS).
- Transfer: C_j(r) = m_j(swap j) − m_j(noswap) under relevance r ∈ {A, B, C, control}.
- Natural presence of each word s_J(X_j) = z_{X_j} − mean(z_decoys) under each relevance, and its full-vocabulary rank (prominence r_min, rank-1-anywhere, L24–59).
- Under the state moves: ΔC_j(r) = C_j(r; moved) − C_j(r; clean) and the no-swap resident shift Δs_J(X_j).

## 6. Estimands and statistics

Cluster = triple (n = 4 pilot; 8 evaluation). Rotations and carriers averaged within triple; relevance indexed by lexical identity after rotation averaging (so "pointed" means the pointed identity, wherever it sat).

- **Selectivity** S = E_j[C_j(j) − E_{r≠j} C_j(r)], with both halves reported: C_j(j) (pointed source's transfer) and E_{r≠j} C_j(r) (unpointed source's transfer under someone else's pointer).
- **Suppression** Q = E_j[C_j(r≠j) − C_j(control)]: negative means an unpointed source transfers less than with no pointer at all.
- **Instruction gain** U = E_j[C_j(j) − C_j(control)].
- **Natural readout selectivity** S_nat = E_j[s_J(X_j | pointed j) − E_{r≠j} s_J(X_j | pointed r)].
- **State-move profile** under pointed r: the vector (ΔC_1, ΔC_2, ΔC_3)(r) and the per-source ratios ΔC_j/C_j. Profile invariance index P = ΔC_pointed/C_pointed − E_{j unpointed} ΔC_j/C_j.
- **Pointer transplant** (B2): the change in (C_1, C_2, C_3) under the pointed-A arm when moved to the B level along d_pointer; the address prediction is C_B up and C_A down.
- Cluster-t intervals, sign counts, per-triple values; the two windows as one Holm family per estimand; no ratio without its numerator and denominator.

## 7. Predictions, stated before the run

| Quantity | Gain on the sourced word (G) | Selection (S) | Generic instruction gain (all words up) |
|---|---|---|---|
| C_j(j) vs C_j(r≠j) | equal | pointed > unpointed | equal |
| Q (unpointed vs control) | ≈ 0 | ≤ 0 (suppression possible) | > 0 |
| S_nat | ≈ 0 | > 0 | ≈ 0 |
| ĝ move under pointed r, profile | scales all C_j by one factor (P ≈ 0) | scales the pointed source more (P > 0), or changes the profile | scales all |
| d_pointer transplant A→B | no redistribution | C_B up, C_A down | no redistribution |
| No-swap resident shift under ĝ | all three words shift together | pointed word shifts more | all shift together |

The primary contrast is S (Stage A). It is decided by the instruction alone and is independent of any fitted direction. The ĝ and d_pointer rows are secondary and speak to what the state moves do once selection is or is not present.

## 8. Interpretation rules

- S > 0 with Q ≤ 0: the instruction selects among available sources; G is insufficient as the account of the instruction's effect. Then P decides whether ĝ inherits selection (P > 0) or is a gain applied on top of it (P ≈ 0), and B2 decides whether a native pointer direction redistributes transfer.
- S ≈ 0 (equivalence band ±20 % of U, 90 % interval) with U > 0: the instruction raises transfer of every introduced word regardless of the tag; the pointer is not implemented at this site or is not read at this readout. H1's "selection" extension is not supported on this organism; the gain account stands and the project's H1 story becomes "task-conditioned gain".
- S > 0 but the state moves scale all sources equally: selection exists but neither ĝ nor d_pointer is its handle; the selection state is elsewhere (H1.10 localization becomes warranted).
- Any move whose realized write or damage gate fails is not read.
- The earlier pilot reported S = +0.37 on its own materials with suppression below zero and a recency ordinal effect (PT-2..4); that is a prior, not an outcome, and its materials are not reused.

## 9. Budget

Stage A: 4 triples × 3 rotations × 2 carriers × 4 arms × (1 clean + 3 swaps + 1 same-source) = 480 forwards, plus 12 donor clean runs per carrier. Stage B: pointed arms only, 4 × 3 × 2 × 3 arms × (ĝ noswap + 3 ĝ-swaps) = 288; reverse rows on the control arm 4 × 3 × 2 × 4 = 96. Stage B2: fit from Stage A caches (no forwards) + 4 × 3 × 2 × (1 + 3) × 2 directions = 192. Total ≈ 1,100 forwards, about 7 minutes; RESID_P axis fits for new source words ≈ 100 short forwards.

## 10. What is not claimed from this experiment

Nothing about behavior; nothing about categories; nothing about a controller's location; nothing about the evaluation banks. A positive S at n = 4 is a pilot observation to be confirmed on the 8 evaluation triples on C2/C3 before it enters any H1 verdict.

## Amendment 2 (2026-09-07, registered before the run): competition series and mid-carrier cue (the tagged-selection and computed-sum organisms, H1.8)

**Competition.** Nested sets k ∈ {1, 2, 3, 4, 6} built from the 8 evaluation triples paired into 4 six-word sets (T1+T2, T3+T4, T5+T6, T7+T8; fixed order). Per set, two focal identities (the first word of each constituent triple); the focal word is placed at the first slot in one placement and the last slot in the other (counterbalanced), distractors in fixed order. Prompt: `Here {is|are} {k} word{s}: (A) "w1", … Keep the word tagged {T} in mind while you copy…` (k = 1: `Here is one word: (A) "w1". Keep the word tagged A in mind…`); control tail as before. Interventions: focal source replaced from block 36 (all k) and, for k ≥ 2, the first distractor replaced (for S). Endpoints: C_focal(k) under the pointer and under control; S(k) = C_focal − C_distractor (k ≥ 2); ratio C_focal(k)/C_focal(1). Cluster = six-word set (n = 4; extension scale, disclosed), carriers C2/C3. Predictions: no shared budget → C_focal flat in k and S CI-clear at every k; budget → C_focal falls with k (1/k reference).

**Mid-carrier cue.** The 8 evaluation triples (rotation 0), pointed-A arm, carriers C2/C3. The carrier is split at the word boundary nearest its midpoint and the cue sentence ` Actually, keep the word tagged {T2} in mind instead.` is inserted there, in both the user's and the assistant's copy (the cue is copied text). Conditions: cue→B (switch), cue→A (same-tag control, length-matched by construction), no cue. Sources A and B replaced from block 36. Readout: interior positions after the cue (second half). Endpoints: C_A, C_B on the second half; switch − same-tag contrast for each; the ĝ and d_shared (evaluate-fit) coordinates on the second half under each condition. Cluster = triple (n = 8). Prediction under re-assignment: C_B up and C_A down under switch relative to same-tag; a textual instruction update, not an internal pointer change (the tagged-selection and computed-sum organisms wording).

Budget ≈ 2,200 forwards.

## Amendment 3 (2026-09-07, analysis-only; no forward affected): ordinal-position breakdown of the evaluate run

Motivation: the earlier pilot reported that pointed-source transfer on its tagged organism grows with the ordinal slot of the pointed word (recency), whereas the registered analysis here indexes relevance by identity after averaging the three rotations and so cannot show a slot effect. Added: `H1/scripts/tagged_selection_ordinal_analysis.py`, a re-scoring of the existing `raw_evaluate.npz` (no new forwards, no state moves) reporting S, pointed C, unpointed C and control C separately per slot, cluster = triple, both windows, all three instruments, plus slot 3 − slot 1 and slot 2 − slot 1 contrasts. Predictions stated before running: if selection is slot-independent, S is CI-clear at every slot with slot contrasts inside noise; if the earlier pilot's recency holds here, pointed C rises with slot. Report: `H1/results/tagged_selection_ordinal.md`. This amendment adds a secondary breakdown; the registered rotation-averaged S remains the primary estimand.
