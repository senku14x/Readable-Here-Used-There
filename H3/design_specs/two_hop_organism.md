# H3 · `two_hop_organism` — does the readability/use pattern hold for a non-numeric latent?

**Registered 2026-09-09, before any forward. Pilot first; the full battery runs only if both gates pass.**

## 0. Question

Everything in `computed_sum_consumer` and `query_local_workspace` used one latent: an arithmetic sum over eight facts. The paper's own remark that its number swaps were the weakest category is the standing escape hatch. This experiment repeats the design on a **non-numeric** latent — the bridge entity of a two-hop fact — using **the paper's own released materials** (`anthropics/jacobian-lens` @ 581d398, `data/experiments/probe-swap.json`, 90 items with `prompt`, `intermediate`, `answer`, `swap_to`, `swap_answer`).

Item filter (mechanical, applied before any forward): `intermediate`, `swap_to`, `answer` and `swap_answer` are all single-token under this tokenizer, and `intermediate`/`swap_to` have equal token counts. 40 of 90 items survive; the pilot uses the first 12 by name order, the evaluation the remaining 28. No item is chosen by outcome.

## 1. Organism

Turn 1 wraps the released clue in the project's copy organism:
`Here is a clue: {clue}. Keep the answer to the clue in mind while you copy the following text exactly, word for word:\n\n{carrier}` where `{clue}` is the released `prompt` stripped of its `Fact: ` prefix and trailing copula (recorded verbatim per item in `meta`). Carrier teacher-forced. Turn 2: `{question} Answer with one word.`, the question being the released prompt's own completion form.

- **source span** = the clue tokens (analogue of the operand span);
- **latent** = `intermediate`, never a token in the prompt (analogue of the sum);
- **consumer** = the released `answer`, a function of the latent that is *not* the latent's own word (analogue of parity). Items whose answer equals the intermediate are excluded by construction.
- **donor** = the released `swap_to` clue, with `swap_answer` as the counterfactual answer.

## 2. Pilot stages and gates (this run)

`gate` (12 items × carriers C0/C1):
- **G1 competence, thinking off.** Scored argmax over {answer, swap_answer} plus greedy: the clean run must give the released `answer` in ≥ 0.9 of cells. Below that the item set is not usable and the experiment stops.
- **G2 natural readability of the latent.** Presence of `intermediate` at the carrier interior, L51–59, under the clue minus under a matched no-clue rendering (`Here is a clue (hidden).`), 8 spec decoys. Must be > 0 with a CI clear of 0. If it fails, there is no maintained copy of the latent and the carrier conditions are undefined.
- **G3 donor geometry.** The donor rendering must match the recipient in token count and clue-span indices, asserted per cell.

`pilot` (same 12 items × C0/C1), only if G1 and G3 pass — three conditions, the minimum that discriminates:
- `S_donor`: clue span ← donor, blocks ≥ 36 (does the answer follow the donor at all? the analogue of O_donor);
- `C_full`: carrier ← donor, clue span asserted clean, blocks ≥ 36;
- `C_rand`: carrier ← own + per-position norm-matched isotropic.

## 3. Predictions, on record

1. G1 ≥ 0.9 (the paper reports these items as answerable; a 27B thinking-off may still fail — that outcome ends the experiment and is reported).
2. G2 > 0: the bridge entity is readable during the carrier under the clue.
3. `S_donor` flips the answer to `swap_answer` in ≥ 0.7 of cells.
4. `C_full` moves the answer margin by < 0.25 of `S_donor` and flips < 0.25 of cells, reproducing the sum organism. If instead `C_full` flips ≥ 0.5, the carrier copy *is* consumed for this latent while the source is visible, and the sum result is domain-specific — the more interesting outcome, and it would redirect the remaining work here.
5. `C_rand` inert.

## 4. Decision

All four met ⇒ the pattern generalises beyond arithmetic; the full battery (28 held-out items, four carriers, NEC, question-site rows, absent-clue transplant) is warranted. Prediction 4 inverted ⇒ run the full battery here instead of anywhere else. G1 or G2 failed ⇒ stop, report the gate, and spend the remaining time elsewhere.

Budget: gate 12 × 2 × 2 = 48 forwards plus 24 no-clue readability forwards; pilot 12 × 2 × 4 = 96. ~170 forwards, well under 15 minutes.

**Item rule, corrected before the first forward (same day).** A source donor needs a *clue for the swap entity*, and the released set supplies one only where a same-category item exists whose `intermediate` equals this item's `swap_to` with an equal token count. Twelve of the 40 usable items have such a partner (city→capital, city→language, language→capital, food→animal families); they are the pilot set, and the partner's released prompt is the donor clue. The remaining 28 are held out and, lacking a released donor clue, would need constructed donors for any later evaluation. The frozen list is `two_hop_items.json` (`pilot_items`, with `donor_prompt`). G2 is read as presence of the intermediate under the own clue minus under the donor clue (length-matched), with the no-clue rendering as a secondary reference.

## Amendment 1 — token-level source reference and all-block carrier donor (registered 2026-09-09 after reading the pilot gates and three conditions, before the forward it governs)

The pilot's block-36 source donor moved the answer +5.8 nats but flipped only 4/24 cells: on this consumer, as on the word consumer, block 36 is not a validated boundary (the clue is resolved below it and re-read). The carrier-only donor moved the answer +3.0 nats (12/12, random 0.01), 0/24 flips. To read the carrier effect against a proper reference, two conditions are added on the same 24 cells: `S_donor0` (clue span ← donor at all 64 blocks, the token-level change) and `C_all` (carrier ← donor at all 64 blocks). Predictions: `S_donor0` flips ≥ 20/24 and gives the reference margin; `C_all` ≈ `C_full` (the sum-organism pattern) — if `C_all` instead flips ≥ 8/24, the carrier copy is behaviorally decisive for this latent while the source is visible, which would be the domain difference. 48 forwards.

## Amendment 2 — the question must not restate the clue (registered 2026-09-09 after reading Amendment 1's rows, before the forward it governs)

Amendment 1's token-level source donor (`S_donor0`, clue span replaced at all 64 blocks) moved the answer only +3.0 nats (3/24 flips) — less than the block-36 donor — while the natural donor *prompt* moves it +22.8. The reason is the turn-2 question, which was the released completion form and therefore restated the clue verbatim; the consumer answered from the question, and turn 1 (clue span or carrier) contributed ≈ 13 % each. That is the re-readable-source trap this project has documented twice, reproduced by me. Corrected question, identical for every item: `Complete the fact from the clue you were given, using one word.` — no entity, no relation words. G1 (competence) is re-run under this question and is now a genuine test of recall from turn 1; the interventions run only if it passes. Predictions as in §3 and Amendment 1, now against a valid source reference. The Amendment-1 archive is kept as `*_pilot_a1.*` and reported as the restated-question variant.

## Amendment 3 — audit corrections and the full battery (registered 2026-09-09 after an audit of the pilot code, before the forwards it governs)

**Audit findings on the pilot (recorded, with their consequences).**
1. **Readout target.** Turn 1 instructs "keep the **answer** to the clue in mind", so the maintained variable is the released `answer` (Paris), while `intermediate` (France) is the paper's swap target and the bridge of the computation. The pilot's G2 and its "carrier latent shift" column used `intermediate` only. Both are single-token for all 12 items, so from here the readout columns are `intermediate ∪ swap_to ∪ answer ∪ swap_answer ∪ decoys` and **both pairs are reported** at the carrier and at the question positions. The pilot's behavioral numbers are unaffected.
2. **Two items are not entity swaps.** `food-animal-butter` / `food-animal-honey` differ from their donor clue in five words (animal/insect, yellow/sweet, …), i.e. a whole-clue paraphrase; the other ten differ in exactly one single-token entity. Token counts match in all twelve, so every intervention is valid, but the two are labelled and excluded from the unanswerable-clue stage.
3. **The no-clue reference was length-mismatched** ("a clue (hidden)", 5 tokens vs 9), so `own − hidden` mixes in the sequence-length effect measured in the instrument gates. The primary gate `own − donor clue` is length-matched and unaffected. Replaced below by a length-matched unanswerable clue.

**Stage `full`** — 12 items × carriers C0–C3 (48 cells), cluster = item (n = 12), carriers averaged within item. Conditions (block-output replacements; the clue span, carrier and question positions are disjoint and each is asserted untouched when it is not the target):

| condition | write | layers |
|---|---|---|
| `clean`, `donor_clean` | — | — (ceiling Δ = donor_clean − clean) |
| `S_donor0` | clue span ← donor | all 64 (the validated source reference: pilot share 1.00) |
| `S_donor` | clue span ← donor | ≥ 36 |
| `C_full` / `C_all` | carrier ← donor carrier, clue span clean | ≥ 36 / all 64 |
| `C_rand` | carrier ← own + per-position norm-matched isotropic | ≥ 36 |
| `NEC_all` | clue span ← donor (all blocks) **and** carrier ← own (all blocks) | — (denies the carrier copy completely) |
| `NEC36` | clue span ← donor (≥ 36) **and** carrier ← own (≥ 36) | — (comparable to the sum organism's NEC) |
| `Q_donor` | question positions ← donor | 36–62 |
| `Q_own` | question positions ← own | 36–62 (bitwise self-patch gate) |

Recorded per forward: `answer` vs `swap_answer` scores (logsumexp over surface forms) and greedy; J_NP z at the carrier interior **and** the question positions over the four-word column set; carrier ΔNLL; write norms and read-back error.

**Stage `noclue`** — the 10 entity-swap items × C0–C3. Recipient clue = the item's clue with the entity replaced by the single-token placeholder `X` (token count and all spans identical, asserted). Conditions: `clean_nc`; `C_from_E` (carrier ← the carrier states of the real own-entity run, all blocks); `C_from_E2` (carrier ← the donor-entity run); `C_rand_nc`; `Q_from_E` (question positions ← own-entity run, 36–62, positive control). Endpoint: shift in log P(answer) − log P(swap_answer) and the pairwise argmax.

**Predictions.** (i) `S_donor0` reproduces the ceiling (share ≥ 0.9). (ii) `C_full ≈ C_all` at 0.2–0.3 of the ceiling with 4–10/48 flips, reproducing the pilot. (iii) `NEC_all` keeps ≥ 0.7 of the source effect — the answer follows the clue with the carrier copy denied, as on the sum. (iv) The donor answer appears at the question positions under `NEC_all` (reconstruction, as on the sum). (v) `Q_donor` flips ≥ 0.5. (vi) `noclue`: `C_from_E` makes the entity's own answer the pairwise winner in ≥ 0.6 of cells, `C_from_E2` symmetric, random inert. (vii) Damage: carrier ΔNLL ≤ 0.02 except under all-block clue-span replacement, where the pilot measured 0.041 and which is reported rather than repaired.

Budget: full 48 × 9 + donors ≈ 480; noclue 40 × 5 + sources ≈ 280. ≈ 760 forwards.

## Amendment 4 — the paper's own intervention, decomposed by position (registered 2026-09-09, before any forward)

**Why.** Every causal claim in the workspace paper's §3.1, §3.3 and §3.4 uses a lens-coordinate swap applied "at all token positions" (PDF text, §3.3 and Fig. 18 caption). This project's carrier-versus-source asymmetry so far rests on whole-residual transplants, and the only lens-coordinate swaps run here moved the *answer word* (sum organism; `Q_swap`). Nothing yet applies the paper's method to an *intermediate* and asks which positions carry its effect. Nanda's replication on this model found that "swapping the answer turned out to strictly dominate" the intermediate swap on the released multi-hop set. This stage does the paper's intermediate swap on the two-hop organism and splits it by position.

**Stage `bridgeswap`.** 12 pilot items × C0–C3 (48 cells), band L36–62 (the project's `SWAP_L`), J_NP folded directions, `CoordSwap` exactly as in `computed_sum_consumer` Amendment 3. Position sets: `tail` = every position from the first clue token to the answer position (the paper's "all positions"; nothing before the clue carries the entity); `clue` = the clue span; `carr` = the assistant carrier; `q` = the question turn including the answer position. Conditions per cell:

| condition | swapped pair | positions |
|---|---|---|
| `int_tail`, `int_clue`, `int_carr`, `int_q` | intermediate ↔ swap_to (the paper's §3.3 swap) | as named |
| `ans_tail`, `ans_clue`, `ans_carr`, `ans_q` | answer ↔ swap_answer (the paper's own confound check, and Nanda's dominating baseline) | as named |
| `rand_tail` | two decoy words' directions (non-specific swap of the same kind) | tail |
| `S_donor0` | clue-span residual donor, all 64 blocks | reference ceiling (Amendment 1) |

Endpoints as in the full battery: answer margin toward swap_answer minus clean, per item (carriers averaged), flips by scored argmax, share = ratio of item means to `S_donor0`; the swap_to − intermediate J_NP readout shift at L51–59 at the carrier **and** at the question positions on the same forwards; carrier ΔNLL; the swap's realized delta norm per condition. Gates: self-consistency of rendering (G3 donor geometry), clue span bitwise untouched under `carr`/`q` writes, ΔNLL ≤ 0.02 for conditions that touch the carrier (reported if exceeded, as before).

**Predictions, on record.**
1. **Gate.** `int_tail` moves the answer toward swap_answer with a CI-clear positive margin. If it reaches ≤ 0.1 of the `S_donor0` ceiling with ≤ 2/48 flips, the paper's §3.3 intervention does not reproduce on this organism; that is reported as a scoped negative consistent with Nanda's caveat, and the position rows below are read as observations only.
2. If the gate passes: `int_clue` carries most of `int_tail`; `int_carr` ≤ 0.3 of `int_tail` (the project's asymmetry, now at the level of the paper's own representation). No prior on `int_q`.
3. `ans_tail` ≥ `int_tail` on margin (Nanda's observation on this model). `ans_carr` ≈ 0: the answer word is not consulted during the carrier.
4. `rand_tail` ≈ 0 on margin.
5. `int_carr` installs swap_to at the carrier readout (positive latent shift in ≥ 9/12 items) whether or not the answer moves; this is the readability-versus-use contrast for the lens direction itself.

**What each outcome licenses.** Gate fails: the paper-relation paragraph becomes a scope statement, nothing else changes. Gate passes with prediction 2: the asymmetry holds for the lens-readable intermediate, not only for whole residuals. `int_carr` alone moves the answer at ≥ 0.5 of `int_tail`: the maintained lens-readable copy is causally used while the source is visible, which contradicts the carrier-only rows and forces a rewrite of the H3 headline.

Budget: 48 × (clean + donor + S_donor0 + 9 swaps) = 576 forwards.

**Amendment 4, endpoint note (registered 2026-09-09 before the forward).** Random inspection of `bridgeswap` cells showed the greedy first token is often a subword of a multi-token spelling ("R"+"ome", "Tok"+"yo", "Bud"+"apest") while the scored candidate set holds single-token spellings only, which can over-count flips when the own answer is multi-token and under-count them when the donor's is. Per the behavioural-endpoint convention (sequence log-probs for multi-token answers; damage metrics), stage `bridgeswap_seq` rescores every condition with sequence log-probabilities of both full answers (four spellings each, logsumexp), the interventions unchanged. Prediction: the ordering of position sets and the intermediate-versus-answer comparison are unchanged; absolute shares may move by up to ±0.1; the sequence endpoint replaces the candidate-set endpoint in the report's headline table.

## Amendment 5 — the H3.3 ladder at the question-turn cut: full residual vs intermediate naming plane vs its complement (registered 2026-09-11, before any forward)

**Stage name `qsplit`. Script `H3/scripts/two_hop_qsplit.py` + `two_hop_qsplit_analysis.py`, forked from `two_hop_bridgeswap_seq.py`. Float32 residual regime from `common/scripts/hooks_fp32.py`. Registered by the researcher; text below verbatim.**

### 0. Why this row, why now

Every positive in H3 transplants whole residuals. `bridgeswap` (Amendment 4) added the paper's own coordinate swap of the two-hop *intermediate*, decomposed by position, and found the question turn carries the largest single-position share (0.23 of the clue-span ceiling; full-residual question donor 0.87 in the `full` stage). The two halves of the paper's Fig. 16 split therefore exist as separate numbers, but the complement was never run: **the full question-turn delta with the intermediate's naming plane removed.** Without it the project cannot say whether the J-readable slice or the rest of the state carries the effect at the position that matters. This organism is the only one of the three where the swapped concept (Spain vs Canada) is upstream of the emitted token (Madrid vs Ottawa); on the sum organism the naming plane *is* the answer word, so the same ladder is output steering by construction. No other H3 stage is affected.

### 1. Setup (unchanged from Amendment 4 unless stated)

- Items: the 12 released probe-swap items with a length-matched donor clue; carriers C0–C3; 48 cells; cluster = item (df = 11).
- Question (Amendment 2): `Complete the fact from the clue you were given, using one word.` Identical across items and across recipient/donor renderings. **Gate:** assert token-id equality of the `q` span between recipient and donor renderings per cell.
- Position set `q`: the question turn including the answer position, exactly as in `bridgeswap`.
- Band: `SWAP_L` = blocks 36–62. Sustained writes at every block in the band.
- Directions: J_NP folded naming directions `a_{int,l}`, `a_{swap_to,l}` per block, orthonormalized per block into Q_l (2 columns). Report the per-block cosine between the two raw directions; if |cos| > 0.9 at any block the plane is degenerate there and the cell is flagged.
- **Numerics:** `Fp32Residual(from_layer=35)` on every forward in this stage, including clean and donor. All contrasts are against `clean32`. Realized write ρ/κ recorded per cell per block; gate ρ ∈ [0.9, 1.1], κ ≥ 0.99.

Let h_l = clean recipient block-l output at the q positions, h^Y_l = donor run's block-l output at the same positions, Δh_l = h^Y_l − h_l (per position). P_l = Q_l Q_lᵀ.

### 2. Position spans

- **`q_pre` (primary):** the question turn **excluding the final scoring position**. Writing the donor residual at the scoring position imports an already-formed donor-answer state.
- **`q_ans` (secondary, if time):** the scoring position alone.
- The all-`q` span of Amendment 4 is **not** used for the ladder.

### 2a. Conditions per cell (span `q_pre`, blocks 36–62, sustained writes)

v_J,l = P_l Δh_l; v_R,l = s_l R_l R_lᵀ Δh_l with s_l = ‖v_J,l‖ / ‖R_l R_lᵀ Δh_l‖ per position, so ‖v_R,l‖ = ‖v_J,l‖ and the two random rows sum exactly to Δh_l.

| condition | write at block l | what it is |
|---|---|---|
| `clean32` | none | fp32 baseline |
| `donor32` | none (donor rendering) | donor competence check |
| `q_full_pre` | h_l + Δh_l | full residual donor over `q_pre`; ceiling for this cut |
| `q_plane_pre` | h_l + v_J,l | donor delta's naming-plane component only |
| `q_rem_pre` | h_l + Δh_l − v_J,l | donor delta with the naming plane removed |
| `q_rand_pre` | h_l + v_R,l | norm-matched random component; control for `q_plane_pre` |
| `q_rem_rand_pre` | h_l + Δh_l − v_R,l | donor delta with an equal-norm random component removed; control for `q_rem_pre` |
| `int_q32` | `CoordSwap` as in Amendment 4, span `q_pre` | continuity with the bf16 `int_q` row only |
| `q_full_ans`, `q_plane_ans`, `q_rem_ans` | same three writes on `q_ans` | optional secondary |

Clamp note. `q_rem_pre` is a sustained write, so Q_lᵀ h'_l = Q_lᵀ h_l at every written block by construction (write-fidelity check, not a finding). Separately, **measure** the naming-plane coordinates at block 63 (after the sustained write ends). Random planes: one seed per cell (20260911 + cell index), isotropic in R^5120, orthonormalized.

**Not run:** `q_rem25` (k = 25 NNLS reconstruction on a restricted dictionary). `q_rem_pre` means **"outside the two-token naming plane"**.

### 3. Endpoints

- Primary: sequence-log-prob answer margin log P(swap_answer) − log P(answer) minus `clean32`, item-clustered; share = ratio of item means to `q_full_pre` and to `S_donor0` (quoted from `bridgeswap_seq`, +23.88, not re-run). Scored-candidate margin and flips as companions.
- Installed-readout gate: J_NP (a_swap_to − a_int) margin at the q positions, L51–59, minus clean. RESID_P pair axis if available.
- Damage: carrier ΔNLL (bound 0.02), top-1 retention; realized ρ/κ per condition.
- Additivity: S = m(q_full) − m(q_plane) − m(q_rem), per item; reported, not interpreted as a partition.

### 4. Gates, in order

1. Rendering and `q_pre` token-id equality between recipient and donor renderings per cell; scoring position identified and excluded (assert).
2. `clean32` competence ≥ 0.9 on the sequence endpoint; `donor32` answers the donor fact ≥ 0.9.
3. Realized writes ρ/κ within gate on every row; ‖v_R‖ = ‖v_J‖ per position (assert).
4. `q_full_pre` shows strong donorward movement: item-mean margin > 0 on ≥ 10/12 items and ≥ 0.3 of S_donor0's sequence-scored margin. If below the bar, stop and report as the result.
5. `q_rand_pre` inert (share ≤ 0.10 of `q_full_pre`, ≤ 2/48 flips) and `q_rem_rand_pre` ≥ 0.80 of `q_full_pre`. If either fails, the ladder rows are uninterpretable at this dose.

### 5. Predictions (registered before the forward)

A = share(`q_plane_pre`), B = share(`q_rem_pre`), both relative to `q_full_pre`, sequence endpoint.

- P1 (gate): as in gate 4. No numerical prior for `q_full_pre`.
- P2: no prior for A. The bf16 `int_q` (0.20) is a different intervention on a different span and is not a prediction.
- P3 (labels and thresholds fixed now, no directional prior): **naming-plane dominant** A ≥ B and B ≤ 0.5; **complement dominant** B ≥ 0.75 and A ≤ 0.35 with `q_rem_rand_pre` ≥ 0.80 and the block-63 re-entry measurement reported; **redundant / non-additive** A ≥ 0.5 and B ≥ 0.5; **jointly necessary / sub-additive** A ≤ 0.35 and B ≤ 0.5; anything else ambiguous, no label.
- P4 (secondary, `q_ans`): no prior.

### 6. What each outcome licenses

| outcome | licensed statement | not licensed |
|---|---|---|
| naming-plane dominant | "At the question turn (scoring position excluded) on this organism, the intermediate's two-token naming plane carries at least as much of the answer effect as everything else in the donor delta combined; removing that plane from a full-residual donor removes most of its effect." | "the J-space component"; anything about the carrier or clue positions |
| complement dominant | "At the question turn (scoring position excluded), the donor delta with the intermediate's naming plane removed still moves the answer ≈ B of the full donor, while the plane alone moves it A; the answer effect at this cut is carried mostly outside the two-token naming plane." | "outside the J-space"; "the readable representation is unused" |
| redundant / sub-additive | describe as measured; state S | any single-component sufficiency or necessity claim |

Standing bans apply. Not "Fig. 16 corroborated/refuted": the licensed comparison is "the position-resolved analogue of the paper's split, restricted to the pair's naming plane". The three rows are three sustained state trajectories, not a partition.

### 7. Budget and stop rule

48 cells × 8 rows; with the sequence endpoint (one forward per spelling) ≈ 2,800 forwards ≈ 20 min. Wall-clock cap 90 minutes from launch to report. If gate 4 or 5 fails, the stage ends as a gate failure and is reported as one. Dense-model rerun not part of this amendment.

### 8. Report additions

`H3/results/two_hop_qsplit.md`: the row table (margin, CI, items > 0, share of `q_full`, share of S_donor0, flips, J_NP q-readout shift, realized ρ/κ, read-back, ΔNLL max); per-item A and B; S per item; which P3 reading obtained; the 2-plane-vs-J-space caveat beside the result. One row in `evidence_ledger.md` §E. Figure `h3_qsplit` from the committed tables only.

**Implementation notes (assistant, 2026-09-11, before the forward).** (i) Each row's write is a *fixed target* per block, `T_l = h_l^clean + M_l Δh_l`, applied with `SpanWriter` (the project's formulas use the clean h_l as the base at every block); the complement of the written component is therefore held at its clean/donor value at every written block, not left to evolve — the three rows are three fixed trajectories, as §6 states. (ii) `q_ans` rows and the RESID_P country axis are **not run** (time cap; no fitted country-name axis exists and fitting one is a new instrument with its own gate). (iii) Block-63 plane coordinates use the identity-transport directions γ⊙w_v (the lens has no J_63), reported as a raw coordinate shift.
