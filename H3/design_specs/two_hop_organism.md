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

## Amendment 6 — the question-turn ladder finished: answer plane, k-sweep over the full-vocabulary dictionary, consumer clamp, current-base complement (registered 2026-09-24, before any forward)

**Stage name `qsplit6`. Script `H3/scripts/two_hop_qsplit6.py` (stages `smoke`, `pursuit`, `qsplit6`) + `two_hop_qsplit6_analysis.py`, forked from `two_hop_qsplit.py`. Same 12 items, carriers C0–C3, 48 cells, cluster = item (df = 11), question `Complete the fact from the clue you were given, using one word.`, span `q_pre` (question turn, scoring position excluded) for every removal row, blocks 36–62, `Fp32Residual` from block 35 on every forward including clean and donor, sequence-log-prob endpoint (logsumexp over the four spellings of each answer word); the single-token candidate endpoint is not used anywhere in this stage. Registered by the researcher (task of 2026-09-24); text written by the assistant before the forward it governs.**

_Note on numbering: the 2026-09-11 write-up refers to the dense-model rerun of Amendment 5 as "Amendment 6"; that rerun was never written into this spec (its registration text is in `context/full_project_writeup_2026-09-11.md` §6.6 on the HF mirror). This section is the first Amendment 6 in this file._

### 0. Why this row set, and what Stage 0 established

Amendment 5 left three weaknesses: (i) a two-token naming plane is a lower bound on J-readable content; (ii) `q_rem_pre` pins the plane at every written block, so within-band re-entry is excluded by construction; (iii) nothing was said about the scoring position. Stage 0 (2026-09-24, recomputed from `raw_qsplit.npz`, no forward) adds a fourth fact: at the **scoring position** (L51–59, swap_to − intermediate, minus clean) the complement row installs the swapped intermediate (+1.73 [+1.30, +2.17], 12/12) even though the plane is at clean on `q_pre` (+0.05); the full donor gives +5.50, the plane +2.70, the random plane +0.03, the natural donor rendering +19.75. And the crossing counts (full 18/48 with 20 more within 2 nats; complement 1/48 with 7 more; plane 0/48) are a threshold on an additive margin whose clean gap is 11.94 nats (range 7.7–15.4), not a gating effect. So "the complement is carried outside the J-readable content" is not yet licensed: the complement can re-enter J-readable coordinates at the one position the clamp never covered, and the plane may simply be too small a dictionary. This amendment tests both.

### 1. Definitions (frozen)

- **Δh_{l,t}** = h^Y_{l,t} − h_{l,t}, donor minus clean block-l output at position t, both under the fp32 regime; `q_pre` positions t ∈ Q\{s}, scoring position s = the last token of the rendering.
- **Intermediate plane** Q_l: the J_NP folded naming directions a_{v,l} = J_lᵀ(γ ⊙ w_v)/‖·‖ of the leading-space single-token forms of `intermediate` and `swap_to`, orthonormalised per block (Amendment 5). **Answer plane** Q^ans_l: the same construction for `answer` and `swap_answer`. Spellings: one direction per word, from the leading-space token (all 24 answer words are single tokens in that form; asserted at smoke); the endpoint still scores all four spellings. P = QQᵀ.
- **Full-vocabulary dictionary** D_l: the unit folded direction of **every** vocabulary entry v ∈ {0, …, 248 319} at block l, D_l = rows a_{v,l}/‖a_{v,l}‖, recomputed per block (fp16 storage, fp32 arithmetic in the correlations' accumulation).
- **Pursuit** (nonnegative greedy selection, LS refit): r₀ = Δh; at step j select v_j = argmax over unselected atoms of ⟨a_v, r_{j−1}⟩ (positive correlations only; stop early if the maximum is ≤ 0, and record it), then refit c = argmin ‖Δh − D_S c‖₂ (ordinary least squares on the selected set S) and set r_j = Δh − D_S c. Checkpoints **k ∈ {2, 8, 25, 64}**. **J_k part** v_{Jk} = D_S c at checkpoint k (the LS projection of Δh onto span S, as the task defines it); **complement** Δh − v_{Jk}. The signs of the LS coefficients are recorded; nonnegativity is a selection rule here, not a constraint on the refit. Run at every written (block, position) and, separately, at the scoring position (§3).
- **Restricted-dictionary NNLS (the registered `q_rem25`)**: dictionary D^w_l = the folded directions of vocabulary entries whose decoded string is a leading-space alphabetic word of ≥ 3 letters (count reported at smoke); greedy nonnegative selection with a **true NNLS refit at every step** (batched projected gradient on the small Gram system, 500 iterations, then a KKT check: all c ≥ 0; for c_i > 0, |(D_SᵀD_S c − D_SᵀΔh)_i| ≤ 1e-4·‖Δh‖; for c_i = 0, (D_SᵀD_S c − D_SᵀΔh)_i ≥ −1e-4·‖Δh‖; any (block, position) failing the check is refit with `scipy.optimize.nnls` and re-checked; the pass fraction is reported), k = 25; **J part** v^{nn}_{25} = D_S c (nonnegative), complement Δh − v^{nn}_{25}.
- **Atom classification** (mechanical, for the norm-share breakdown; alias lists frozen here): decode the atom's token, strip the leading space and lowercase. *Answer-related* if it equals `answer` or `swap_answer` (lowercased) or one of their aliases; *intermediate-related* if it equals `intermediate` or `swap_to` or one of their aliases, or if the decoded string has ≥ 3 letters and is a prefix of the word or the word is a prefix of it; otherwise *other*. Answer aliases: Madrid {madrid}, Ottawa {ottawa}, Paris {paris, parisian}, Rome {rome, roman}, Berlin {berlin}, Tokyo {tokyo}, Arabic {arabic, arab}, Russian {russian}, Budapest {budapest}, Warsaw {warsaw}, Athens {athens, athenian}, cow {cow, cows, cattle}, bee {bee, bees}. Intermediate aliases: Spain {spain, spanish, spaniard}, Canada {canada, canadian}, France {france, french}, Italy {italy, italian}, Germany {germany, german}, Japan {japan, japanese}, Egypt {egypt, egyptian}, Russia {russia, russian}, Hungary {hungary, hungarian}, Poland {poland, polish}, Greece {greece, greek}, butter {butter, buttery}, honey {honey, honeyed}. Where an alias belongs to both classes (Moscow item: `Russian` is the answer and the demonym of the intermediate `Russia`), the **answer** class takes priority and the collision is reported. Norm shares: for a class C ⊆ S, v_C = D_{S∩C} c_{S∩C}; report ‖v_C‖/‖v_{Jk}‖ and the coefficient-weighted count; the atoms are not orthogonal, so the shares are components, not a partition, and every selected atom is saved so the classification can be audited.
- **Energy reference**: per block l, Σ_l is the covariance of the fp32-regime clean block-l outputs over all positions ≥ 4 of the 48 recipient renderings (≈ 5 000 samples); k random directions u_i = X_cᵀ ξ_i/√n (ξ_i ~ N(0, I_n); i.e. draws from N(0, Σ_l)), orthonormalised; the **energy fraction** of Δh in that subspace, ‖P_U Δh‖²/‖Δh‖², averaged over `q_pre` positions and 5 seeds, per k and block, reported beside the J_k energy fraction ‖v_{Jk}‖²/‖Δh‖² and the isotropic reference k/d.

### 2. Rows (every removal/component row is a sustained fixed-target write on `q_pre` at blocks 36–62 unless marked; `SpanWriter`; clean base h_l)

| row | write at block l, position t ∈ q_pre | purpose |
|---|---|---|
| `clean32`, `donor32` | none | fp32 baselines, competence |
| `q_full_pre`, `q_plane_pre`, `q_rem_pre` | h + Δh; h + PΔh; h + Δh − PΔh | Amendment 5 rows re-run as the same-run reference |
| `q_ansplane_pre`, `q_ansrem_pre` | h + P^{ans}Δh; h + Δh − P^{ans}Δh | is the complement's 0.78 the answer already being computed at the question turn? |
| `q_J{k}_pre`, `q_J{k}rem_pre`, k ∈ {2, 8, 25, 64} | h + v_{Jk}; h + Δh − v_{Jk} | the J_k ladder over the full dictionary |
| `q_J25nn_pre`, `q_rem25nn_pre` | h + v^{nn}_{25}; h + Δh − v^{nn}_{25} | the registered `q_rem25` (restricted dictionary, NNLS + KKT) |
| `q_rem25ans_pre`, `q_rem25int_pre` | h + Δh − LS projection of Δh onto span of the answer-related (resp. intermediate-related) atoms among the k = 25 selection at that (block, position); no write where the class is empty | the cheap ablation by atom type |
| `q_rem_pre_cc`, `q_J{k}rem_pre_cc` (4), `q_rem25nn_pre_cc` | the corresponding complement row **plus a consumer clamp at s** (§3) | the mediation test at the consumer |
| `q_J{k}rem_pre_ccr` (4), `q_rem_pre_ccr`, `q_rem25nn_pre_ccr` | the complement row plus a **random-k** clamp at s, norm-matched (§3) | control for the consumer clamp |
| `q_randkrem_pre`, k ∈ {2, 8, 25, 64} | h + Δh − v_{Rk}, with v_{Rk} = s_t R_l R_lᵀ Δh, R_l a random k-frame (isotropic Gaussian, orthonormalised, seed 20260924 + cell index + 100k), s_t chosen per position so ‖v_{Rk}‖ = ‖v_{Jk}‖ (asserted) | norm- and rank-matched random removal, per k |
| `q_rand_pre`, `q_rem_rand_pre` | as Amendment 5 (random 2-plane) | Amendment 5 controls, same-run |
| `q_rem_cb_pre` | **current base**: at each block, h'_l = h^{evolving}_l + (I − P_l)Δh_l; the plane coordinate is never pinned | weakness (ii): the complement free-running; within-band plane coordinates Q_lᵀh'_l − Q_lᵀh_l recorded per block, and the block-63 re-entry measurement as in Amendment 5 |

Positions written: `q_pre` only, for every row; the scoring position is touched only by the consumer clamps of §3. Clue span, carrier and prefix are asserted bitwise untouched under every row.

### 3. The consumer clamp (frozen)

At the scoring position s, blocks 36–62, a `_cc` row additionally holds the coordinates of h_s in a pinned span at their clean values: h'_{s,l} = h^{evolving}_{s,l} − P^{(s)}_l (h^{evolving}_{s,l} − h^{clean}_{s,l}), applied after the complement write of the same block. The pinned span at s is: for `q_rem_pre_cc`, the intermediate plane Q_l (same two directions as on `q_pre`); for `q_J{k}rem_pre_cc`, the span of the k atoms selected by the **same pursuit run on the full donor's Δh at the scoring position**, Δh_{s,l} = h^Y_{s,l} − h_{s,l} (the donor rendering's clean state, so this is a natural counterfactual state, chosen without reference to any outcome); for `q_rem25nn_pre_cc`, the NNLS support at s. Why this definition: the question the clamp answers is whether the complement's effect reaches the answer *through J-readable content at the consumer*; the J-readable content the donor would install at the consumer is exactly what the pursuit on Δh_s identifies, at the same sparsity as the removal on `q_pre`. Pinning it at clean removes that channel and nothing else. The clamp's requested and realized per-position writes are recorded per block (post-cast; the fp32 regime should give ρ = κ = 1). The random-k control `_ccr` pins a random k-frame orthogonalised against the pinned span, with each block's delta rescaled to the atom clamp's realized per-position norm in the same cell and block (the `CoordClampMatched` construction of `query_local_workspace` Amendment 3, generalised to k dimensions); for the plane row the control is a random 2-plane orthogonal to the naming plane.

### 4. Gates, in order (the stage stops and reports if any fails)

1. Rendering; `q` token-id equality between recipient and donor renderings; scoring position identified and excluded from `q_pre`; every answer word single-token in leading-space form.
2. `clean32` competence ≥ 0.9 and `donor32` ≥ 0.9 on the sequence endpoint.
3. Realized writes: ρ ∈ [0.9, 1.1], κ ≥ 0.99 on every fixed-target row, on every consumer-clamp write and on the current-base row (measured post-cast against the evolving base); ‖v_{Rk}‖ = ‖v_{Jk}‖ asserted per position; every `_ccr` clamp's realized per-position norm within 5 % of its matched `_cc` norm.
4. `q_full_pre` reproduces Amendment 5 within its interval (+11.19 [+10.00, +12.38] nats, ≥ 10/12 items > 0).
5. `q_rand_pre` share ≤ 0.10 with ≤ 2/48 flips; `q_rem_rand_pre` ≥ 0.80.
6. Pursuit positive control (reported, not gating): the fraction of written (block, position) cells at which the k = 2 pursuit selects the leading-space `intermediate` or `swap_to` atom, and both; chance is 2/248 320 per pick.
7. KKT pass fraction for the restricted-dictionary NNLS ≥ 0.99 after the scipy fallback.

### 5. Predictions, on record

- P1: gates 1–5 pass (same materials, same regime; gate 4 is a determinism-plus-regime check).
- P2: the pursuit positive control is far above chance (no numeric prior); the k = 2 selection contains the intermediate or swap_to atom on a majority of `q_pre` cells at L51–59.
- P3 (answer plane): no numeric prior on A^{ans} = share(`q_ansplane_pre`) or B^{ans} = share(`q_ansrem_pre`). If B^{ans} ≤ 0.5 while B = share(`q_rem_pre`) stays ≈ 0.78, the answer is already J-readable at the question turn and the qualifier of §6 applies.
- P4 (k-sweep): share(`q_J{k}rem_pre`) is non-increasing in k; share(`q_randkrem_pre`) stays ≥ 0.80 at every k (the random-k removal is norm-matched but rank-matched to a subspace with no relation to the answer). No prior on where the J_k complement crosses 0.5.
- P5 (consumer clamp): the `_cc` rows lower the complement shares relative to their un-clamped rows; the `_ccr` controls do not (within the un-clamped row's interval). No prior on the magnitude, which is the stage's result.
- P6 (current base): `q_rem_cb_pre` ≥ share(`q_rem_pre`) − 0.10 with the within-band plane coordinates reported; if the free plane rebuilds the intermediate coordinate inside the band (Q_lᵀ(h' − h) rising to ≥ 0.5 of the full donor's plane coordinate by block 62), weakness (ii) was real and B of Amendment 5 is re-scoped as "with the plane pinned".
- P7: energy fractions: ‖v_{Jk}‖²/‖Δh‖² exceeds the N(0, Σ) random-k fraction at every k (the dictionary is fitted to the model; a match would say the pursuit is no better than covariance-matched noise).

### 6. Decision rule and qualifier (registered verbatim from the task)

- consumer-clamped complement share ≥ 0.5 at k = 25 → a non-J channel carries most of this consumer's margin
- ≤ 0.2 → the complement was J-mediated at the consumer
- otherwise → report the share(k) curve as the result

Qualifier (also registered): if answer-related atoms carry most of the J_k part, or answer-plane removal kills most of the effect, read "J-mediated" as "the answer is already J-readable at the question turn", not as the intermediate travelling through J.

"Consumer-clamped complement share at k = 25" is share(`q_J25rem_pre_cc`) relative to `q_full_pre` on the sequence endpoint, with `q_J25rem_pre_ccr` as its control; the decision is taken only if gates 1–5 pass and the `_ccr` control stays within the un-clamped row's interval.

### 7. Endpoints and report

Per row/k: margin (nats) with item-clustered 95 % t-interval and items > 0; share of `q_full_pre` and of the quoted S_donor0 (bf16 `bridgeswap_seq`, +23.88); flips (sequence endpoint); ‖v‖/‖Δh‖ and the energy fraction ‖v‖²/‖Δh‖² (mean over blocks × positions) beside the N(0, Σ) random-k fraction and k/d; J_NP readout shift (swap_to − intermediate, L51–59, minus clean) at the **scoring position** and at `q_pre`, and the answer readout (swap_answer − answer) likewise; block-63 re-entry; ρ/κ, read-back, ΔNLL. Also: the share(k) curve with and without the consumer clamp; the atom-type breakdown per k (norm share, counts, the collision report); the pursuit positive control; the KKT pass fraction; six seeded-random cells (seed 20260924) read by hand; the Amendment 5 caveats carried forward. Figure `h3_qsplit6` from the tables only. Report `H3/results/reports/two_hop_qsplit6.md`, tables `two_hop_qsplit6_tables.json`, raw `raw_qsplit6.npz` (+ `raw_pursuit.npz` for the selected atoms and coefficients; arrays > 100 MB mirrored per convention).

### 8. Budget and stop rule

Per cell ≈ 38 conditions × (|spellings(answer)| + |spellings(swap_answer)|) forwards ≈ 180; 48 cells ≈ 8 600 forwards plus the pursuit pass (27 blocks × 1 344 vectors × 64 steps of a 248k-atom correlation) ≈ 1.5 h total. Wall-clock cap 4 h from launch to tables. No rows beyond this set without a new amendment. If any gate of §4 fails, the stage ends as a gate failure and is reported as one; nothing is reinterpreted.

## Amendment 7 — Stage 2: item growth to 42 items over 7 relation types, admission gates, answer-smuggling screen, the Stage 1 rows rerun, and the repaired current-base row (registered 2026-09-24, before any forward)

**Stages `admit`, `smoke2` and `stage2` of `H3/scripts/two_hop_qsplit6.py`; analysis `two_hop_qsplit6_analysis.py stage2`; screen `H3/scripts/two_hop_stage2_screen.py`; bank builder `H3/scripts/two_hop_items_stage2_build.py` (tokenizer only). Same model, regime, carriers C0–C3, question, `q_pre` span, blocks 36–62, sequence-log-prob endpoint, cluster = item. Registered by the researcher (task of 2026-09-24, "Stage 2"); text written by the assistant before the forward it governs; the Stage 1 report (`two_hop_qsplit6.md`) was read first.**

### 0. Why

Stage 1 ran on twelve items of four relation types, all with released donors. Its licensed statements (the k-sweep saturating at 0.6 of the effect in the complement, the intermediate-plane clamp at the consumer removing 0.04, the answer plane at 0.45 against the intermediate plane's 0.20) rest on n = 12 with three of the four relation types geographic. Stage 2 asks whether they hold on a larger bank with constructed donors and more relation types, gates every item on competence and on the intermediate swap beating the answer swap at mid depth (Nanda's caveat, `bridgeswap`: answer swap 0.63 vs intermediate swap 0.41 on the full band), and screens each relation for answer smuggling (an answer unembedding that is an affine image of the intermediate's). It also repairs the current-base row whose registered additive form double-counted the accumulated block delta (Stage 1 §8.3, silly mistake 4).

### 1. Bank (frozen; `H3/design_specs/two_hop_items_stage2.json`, built by the committed builder, seed 20260924)

Five templated families, one cue slot each; an item is an ordered pair (A, B) of cues of the same family with different intermediates and different answers whose clue bodies tokenize to the same length; the item's clue is the template with cue A, its donor clue the template with cue B, `swap_to` = B's intermediate, `swap_answer` = B's answer. Every intermediate, swap_to, answer and swap_answer is a single token in leading-space form; the answer and the intermediate do not occur in the item's own clue. Selection: at most 6 items per family, each cue at most once as recipient and twice as donor, each intermediate at most twice as recipient and twice as swap_to (seeded order over the eligible pairs). Families and counts: `city-capital` "The capital of the country where {city} is located" (6), `city-language` "The language spoken in the country where {city} is located" (6), `river-capital` "The capital of the country where the {river} River reaches the sea" (6), `language-capital` "The capital of the country where {language} is the primary language" (6), `city-currency` "The currency used in the country where {city} is located is the" (6). With the 12 pilot items (released donors; `city-capital` 6, `city-language` 2, `language-capital` 2, `food-animal` 2) the Stage 2 bank is **42 items, 168 cells, 7 relation types** (`river-capital`, `city-currency` and `food-animal` are non-overlapping with the paper's example templates; `city-capital`, `city-language`, `language-capital` pool released and constructed items and are reported split by donor origin). Constructed donors are a design difference from Stage 1 and are flagged as such in every table.

**Atom-classification aliases, extended (frozen here; Amendment 6's lists unchanged).** Intermediate: Norway {norway, norwegian, norse}, Ireland {ireland, irish}, Turkey {turkey, turkish}, Denmark {denmark, danish, dane}, India {india, indian}, Austria {austria, austrian}, Sweden {sweden, swedish, swede}, Iran {iran, iranian, persian}, Netherlands {netherlands, dutch, holland}, China {china, chinese}, Portugal {portugal, portuguese}, England {england, english, british, britain}, Finland {finland, finnish, finn}, Thailand {thailand, thai}, Vietnam {vietnam, vietnamese}, Korea {korea, korean}, Switzerland {switzerland, swiss}. Answer: Oslo {oslo}, Dublin {dublin}, Ankara {ankara}, Copenhagen {copenhagen}, Delhi {delhi}, Vienna {vienna, viennese}, Danish {danish, dane}, Norwegian {norwegian}, Swedish {swedish}, Italian {italian}, Japanese {japanese}, Chinese {chinese}, Persian {persian, farsi}, Dutch {dutch}, Turkish {turkish}, French {french}, Lisbon {lisbon}, Cairo {cairo}, London {london}, Moscow {moscow}, Amsterdam {amsterdam}, Helsinki {helsinki}, Bangkok {bangkok}, Stockholm {stockholm}, Tehran {tehran}, dong {dong}, won {won}, pound {pound, sterling}, yuan {yuan, renminbi}, euro {euro, euros}, yen {yen}, franc {franc, francs}. Collisions (an alias in both classes, answer class takes priority, reported): every `city-language` item whose answer is the demonym of its intermediate (Danish/Denmark, Norwegian/Norway, Swedish/Sweden, Italian/Italy, Japanese/Japan, Chinese/China, plus the pilot Russian/Russia) and the `language-capital` items whose cue is a demonym of the intermediate.

### 2. Admission gates (per item; run in stage `admit`, 168 cells, before the main battery; every item stays in the run and the report gives the rows for the admitted set and for all items)

- (a) **Competence**: on the sequence endpoint, clean32 prefers `answer` and donor32 prefers `swap_answer` in all four carriers.
- (b) **Intermediate beats answer at mid depth**: the paper-style lens-coordinate swap (`CoordSwap` with the coordinate arithmetic in float32, as `int_q32` of Amendment 5) of the intermediate pair versus the answer pair, J_NP folded directions, **blocks 36–50** (the band below the readout window, where the intermediate should be the live variable), on the `tail` positions of Amendment 4 (first clue token to the scoring position inclusive). Admitted if the item's carrier-averaged margin under `int_tail_mid` exceeds that under `ans_tail_mid` and is > 0. Reported for the pilot 12 as well; no numeric prior on how many pass (Amendment 4 found the answer swap larger on the full band).
- An item is **admitted** if (a) and (b) both hold. The decision rule (§5) is taken on the admitted set only if it has ≥ 12 items over ≥ 3 relation types and its competence fraction is ≥ 0.9; otherwise the stage reports the rows and no decision.

### 3. Answer-smuggling screen (per relation type; `two_hop_stage2_screen.py`, unembedding rows only, no forward)

For each family, over all its eligible (intermediate, answer) pairs from the builder's entity table (not only the chosen items), fit the ridge affine map W_U[answer] ≈ A·W_U[intermediate] + b in the dual form on centred rows with λ ∈ {0.01, 0.1, 1} × mean eigenvalue of the pair Gram matrix, and report the **leave-one-out residual fraction** ‖W_U[ans] − Â W_U[int] − b̂‖² / ‖W_U[ans] − mean‖² at the best λ, beside a **mismatched-pairs null** (the same fit with the intermediates permuted, 20 permutations, mean and 5th percentile). A relation is **flagged** when its LOO residual fraction is ≤ 0.5 and below the null's 5th percentile: the answer's naming direction is then a predictable image of the intermediate's, and a J-readable intermediate can carry the answer's readout by geometry alone. Flags are reported next to every per-relation row; they do not remove items.

### 4. Rows and gates

- Rows: exactly the Amendment 6 row set (`q_full_pre`, `q_plane_pre`, `q_rem_pre`, `q_ansplane_pre`, `q_ansrem_pre`, `q_J{k}_pre`, `q_J{k}rem_pre`, `q_rand{k}rem_pre`, `q_J25nn_pre`, `q_rem25nn_pre`, `q_rem25ans_pre`, `q_rem25int_pre`, `q_rand_pre`, `q_rem_rand_pre`, the `_cc` and `_ccr` rows) **minus** `q_rem_cb_pre` (construction failed, Stage 1 §8.3) **plus** the repaired current-base row **`q_rem_cbr_pre`**: at every block l ∈ 36–62 and position t ∈ `q_pre`, h'_l = P_l h^evolving_l + (I − P_l)(h_l + Δh_l) — the complement coordinates are *replaced* by the donor's (as in the fixed-target rows) and only the two plane coordinates evolve freely. Recorded per block: the realized write against the evolving base (post-cast ρ, κ), the free plane coordinate Q_lᵀ(h' − h_clean) per position, and the **construction check** ‖h' − h_clean‖/‖Δh_l‖ per position (gate 8: ≤ 1.5 at every block; the fixed-target complement gives ≈ 1).
- Gates 1–3, 5–7 as Amendment 6 on all 168 cells (gate 3 additionally on the `q_rem_cbr_pre` write). Gate 2 is reported for all items and for the admitted set (the stage does not stop on it; admission handles competence). Gate 4 becomes a reproduction gate: the 12 pilot items' `q_full_pre` margin lies within Stage 1's interval (+11.19 [+10.00, +12.38], ≥ 10/12 > 0). Gate 8: the `q_rem_cbr_pre` construction check.
- Pursuit, NNLS, energy reference (Σ_l from the clean outputs of all 168 renderings), consumer clamps, random controls and seeds exactly as Amendment 6 (cell index now runs over 168 cells; energy seed unchanged).

### 5. Predictions and decision rule

- P1: gates 1–3, 5–8 pass; gate 4 reproduces.
- P2 (admission): no numeric prior; at least 3 relation types survive with ≥ 3 items each. The pilot 12 are reported under (b) whether or not they pass.
- P3 (generality of Stage 1 on the admitted set): share(`q_J25rem_pre`) ∈ [0.45, 0.75]; share(`q_J25rem_pre_cc`) ∈ [0.3, 0.6]; share(`q_rem_pre_cc`) ≥ share(`q_rem_pre`) − 0.10; A_ans > A. If any of these fails the Stage 1 statement is re-scoped to its four relation types.
- P4 (relation dependence): relation types flagged by the screen show a larger A_ans and a smaller B_ans than unflagged ones (no numeric prior).
- P5 (repaired current base): share(`q_rem_cbr_pre`) ≥ share(`q_rem_pre`) − 0.10 with the construction check ≈ 1; if the free plane rebuilds the intermediate coordinate (norm-weighted projection on the donor's plane coordinate ≥ 0.5 by block 62), weakness (ii) of Amendment 5 was real.
- Decision rule and qualifier: as Amendment 6 §6, verbatim, applied to the admitted set; the "all items" set is reported beside it.

### 6. Endpoints, report, budget

Per row: the Amendment 6 columns, for the admitted set and for all items, plus a per-relation-type table (share of `q_full_pre` for `q_plane_pre`, `q_rem_pre`, `q_ansplane_pre`, `q_ansrem_pre`, `q_J25rem_pre`, `q_J25rem_pre_cc`, `q_rem_cbr_pre` with the screen flag and the donor origin), the admission table (per item: competence per carrier, `int_tail_mid`, `ans_tail_mid`), the screen table, and six seeded-random cells (seed 20260924) read by hand. Report `H3/results/reports/two_hop_stage2.md`, tables `two_hop_stage2_tables.json`, figure `h3_stage2`, raw `raw_admit.npz`, `raw_stage2*.npz`, `raw_pursuit_stage2.npz` (lens arrays saved for each cell's own four words plus the eight decoys to keep every file under 100 MB; atom classes stored as codes 0/1/2 = other/intermediate/answer). Budget: `admit` ≈ 168 × 14 ≈ 2,400 forwards; `stage2` ≈ 168 × 180 ≈ 30,000 forwards plus the pursuit pass (4,704 vectors per block) ≈ 3 h; wall-clock cap 5 h from launch to tables. No rows beyond this set without a new amendment; a gate failure ends the stage as a gate failure.

## Amendment 8 — registered, not run: joint-plane removal, a stronger consumer clamp, and a relation-transfer row (registered 2026-09-24 after the Stage 1 report and the researcher's notes; no forward under this amendment yet)

**Why.** Stage 1 (Amendment 6) left "the answer is already computed and J-readable at the question turn" as the leading alternative to "a non-J channel": the answer plane alone carries 0.45 against 0.20 for the intermediate plane, the consumer clamps are partial (the intermediate and answer readouts at s stay at +0.3 to +2.2 under the `_cc` rows, so the `_cc` shares are upper bounds on any non-J route), and the atom-type split of the J_25 part shows the answer's directions at the scoring position in several items. Three rows discriminate the alternatives. They are registered here so that their definitions precede any forward; they run in a later stage (`probe3`, script and analysis to be forked from `two_hop_qsplit6.py`) after Stage 2.

### Rows (fp32 regime, sequence endpoint, blocks 36–62, `q_pre` unless stated, same controls conventions as Amendment 6)

- (a) **`q_bothrem_pre`** — remove the intermediate plane and the answer plane together: h + Δh − P_{int∪ans} Δh, with P the orthogonal projector onto the span of the four folded directions (intermediate, swap_to, answer, swap_answer; orthonormalised per block). Control: a norm-matched random 4-frame (`q_rand4rem_pre`). Prediction: share(`q_bothrem_pre`) ≤ min(B, B_ans) − 0.05 if the two planes carry separate parts of the effect; ≈ B_ans if the intermediate plane's part is nested in the answer's.
- (b) **`q_J25rem_pre_ccs`** — the J_25 complement on `q_pre` plus a *stronger* consumer clamp at s: pin, at every block 36–62, the span of the four folded directions **plus** the atoms selected by the pursuit on Δh_s **plus** the translation atoms of the four words (the non-Latin unembedding rows whose nearest Latin-script neighbour is one of the four words or their aliases, computed once per item from W_U; count reported). Verification gate: the J_NP intermediate and answer readouts at s (L51–59, minus clean) must drop to |shift| ≤ 0.3 nats-of-readout under the clamp; if they do not, the row is reported as a failed clamp, not read. Control: a random frame of the same dimension orthogonalised against the pinned span, norm-matched per block (`_ccsr`). Prediction: if share(`q_J25rem_pre_ccs`) stays ≥ 0.4 with the readouts at ≈ 0, a route that is not J-readable at the consumer carries at least that share; if it falls to ≤ 0.2, the Stage 1 residual was the partial clamp.
- (c) **`q_relxfer_pre`** — relation transfer: for a city that appears as the recipient cue in a `city-capital` item (A → country → capital, donor city B), build the `city-language` rendering for the same cue A with the same donor city B (template "The language spoken in the country where {city} is located"), and write the **capital item's** donor delta Δh_l (its `q_pre` positions, blocks 36–62) into the **language rendering's** `q_pre` positions (same relative positions; the question turn's token ids are identical across templates, asserted). Endpoints in the language rendering: the margin toward the donor country's language (swap language − own language) and the margin toward the donor country's capital (swap capital − own capital), both sequence log-probs minus the language rendering's clean values. Reading: a push toward the donor's **language** means the transplanted state carries the intermediate (the country); a push toward the donor's **capital**, or nothing, means it carries the answer. Pairs (cue A, donor B) with single-token language answers and no ambiguity: Lyon–Naples, Naples–Barcelona, Munich–Osaka, Osaka–Munich (pilot), Bergen–Kyoto, Marseille–Aarhus, Salzburg–Kyoto (Stage 2); Toronto, Barcelona, Vancouver, Cork and Mumbai are excluded (English/Irish/Hindi ambiguous or multi-token). The reverse transfer (language item's delta into the capital rendering) is run as the mirror row with the mirrored endpoints. Control: the same transfer with the donor delta replaced by a norm-matched random vector per block.

### Gates, budget

Gates 1–3 and 5 of Amendment 6; for (b) the readout-at-s verification gate above; for (c) the token-id equality of the question turn across templates and the competence of the language renderings (clean prefers the own language, ≥ 0.9 of cells). Budget ≈ 48 cells × (3 rows + 3 controls) × 5 forwards + 7 pairs × 4 carriers × (2 rows + 1 control) × 8 forwards ≈ 2,100 forwards. Nothing under this amendment runs until it is scheduled by the researcher.

### Amendment 8 — run registration (2026-09-24, after Stage 2 and before any forward under this amendment)

**Stage `probe3`. Script `H3/scripts/two_hop_probe3.py` (stages `smoke3`, `probe3`), analysis `two_hop_probe3_analysis.py`. Same model, float32 residual from block 35 on every forward, sequence-log-prob endpoint, writes at blocks 36–62 on `q_pre`, clamps at the scoring position s only, cluster = item (rows a, b) or pair (row c). Scheduled by the researcher on 2026-09-24 ("run whatever is next"); this section fixes every implementation choice the registration above left open. Nothing here changes a registered prediction.**

#### Why now (what Stage 2 left open)

Stage 2 (Amendment 7) reproduced Stage 1 on 35 admitted items over six relation types, and its registered decision rule landed on its threshold: the consumer-clamped J25 complement is 0.511, cluster-bootstrap [0.474, 0.550]. Two facts bound what that licenses. First, the clamp is partial: the intermediate and answer readouts at s stay at +1.49 and +1.32 under it, so 0.511 is only an upper bound on any route that is not J-readable at the answer position. Second, the answer plane carries 0.37 of the effect against 0.19 for the intermediate plane, in all 35 items and every relation type, so "the answer is already computed and readable at the question turn" is the leading alternative to "a route the lens cannot read". Rows (a), (b) and (c) each attack one of these.

#### How (frozen)

- **Items.** Rows (a) and (b), with their same-run references, run on the 35 items admitted in Stage 2 × C0–C3 = 140 cells. This replaces the 48-cell budget line above, because Stage 2's decision was taken on the admitted set and the verified clamp must be compared on the same items. Row (c) runs on the seven registered pairs × C0–C3 = 28 cells. Geometry was checked before this registration with the tokenizer only. The capital renderings are 122 tokens and the language renderings 123, each pair is length-matched, the question-turn token ids are identical across all four renderings, and every language answer is a single token.
- **Same-run references** (re-runs of registered Amendment 6 rows, for normalisation and as a reproduction gate against Stage 2's stored margins): `q_full_pre`, `q_rem_pre`, `q_ansrem_pre`, `q_J25rem_pre`, `q_J25rem_pre_cc`. The full-dictionary pursuit is recomputed to k = 25 for the `q_pre` vectors and the s vectors of the 140 cells. Its selections are compared with Stage 2's stored ones and the agreement fraction is reported.
- **(a) `q_bothrem_pre`**: h + Δh − P₄Δh on `q_pre`, with P₄ the projector onto the orthonormalised span of the four folded directions (intermediate, swap_to, answer, swap_answer; leading-space forms) per block. Control **`q_rand4rem_pre`**: h + Δh − v, with v the projection of Δh onto an isotropic random 4-frame rescaled per position to ‖P₄Δh‖ (asserted), seed 20260924 + 300000 + cell.
- **(b) `q_J25rem_pre_ccs`**: `q_J25rem_pre` on `q_pre`, plus a clamp at s at every block 36–62 holding the coordinates of h_s in span(F ∪ P ∪ X) at clean (Amendment 6 §3 form, fp32 arithmetic). The orthonormal basis comes from an SVD at relative tolerance 1e-3.
  - F is the folded directions of every single-token form of the four words and their frozen aliases (Amendments 6 and 7), with and without a leading space, capitalised and lowercase.
  - P is the 25 atoms of the full-dictionary pursuit on Δh_{s,l}, the same span as `q_J25rem_pre_cc`.
  - X is the translation atoms. These are every vocabulary entry whose decoded string contains no Latin letter and whose nearest Latin-script unembedding row decodes to one of the four words or an alias. Nearest means cosine over normalised W_U rows. Matching is exact after stripping and lowercasing, and the prefix rule is not used.
  - The counts |F|, |X| and the rank are reported per item. The pre-check found 4–67 translation atoms per item, median 18. The rule is mechanical and admits a few false friends, such as `山西` (Shanxi) and `太原` beside Spain. It is kept as is, and the rank-matched control absorbs them.
  - Control **`q_J25rem_pre_ccsr`**: a random frame of the same rank, orthogonalised against the pinned span, with each block's delta rescaled to the `_ccs` realized norm in the same cell and block. Seed 20260924 + 350000 + cell.
  - **Verification gate V.** Under `_ccs`, take the item-mean J_NP readout shift at s (L51–59, minus clean) for swap_to − intermediate and for swap_answer − answer. V passes if both lie within ±0.3. The fraction of cells within ±0.3 is reported. If V fails, row (b) is a failed clamp and is not read.
  - The final block, 63, is outside every clamp by design. Clamping it along γ⊙w would pin the output logits themselves. Its re-entry at s is reported for both pairs.
- **(c)** For each pair (A, B), render four prompts: the capital template with cue A and with cue B (the Stage 1/2 item and its donor), and the language template "Fact: The language spoken in the country where {cue} is located is" with cue A and with cue B.
  - Δh_cap is the cue-B minus cue-A difference of the capital renderings. Δh_lang is the same difference for the language renderings. Both are taken at the `q_pre` positions, blocks 36–62, under the fp32 regime.
  - Rows in the language rendering of A: **`q_xfer`** h + Δh_cap; **`q_native_lang`** h + Δh_lang; **`q_xfer_rand`** h + r, with r isotropic and ‖r‖ = ‖Δh_cap‖ per position and block, seed 20260924 + 400000 + cell.
  - Rows in the capital rendering of A: **`q_mirror`** h + Δh_lang; **`q_native_cap`** h + Δh_cap; **`q_mirror_rand`** with ‖r‖ = ‖Δh_lang‖, seed 20260924 + 450000 + cell.
  - Endpoints in every rendering are two sequence log-prob margins, each minus that rendering's clean value. m_lang is donor's language minus own language. m_cap is donor's capital minus own capital.
- **Gates**:
  1. Rendering, geometry and question-turn token equality.
  2. Competence ≥ 0.9 of cells for every rendering type used: capital and language, clean and donor.
  3. Realized writes. ρ ∈ [0.9, 1.1] and κ ≥ 0.99 on every fixed-target row and every clamp write; the `_ccsr` norm within 5 % of its match; the random-vector norms asserted.
  4. Reproduction. The same-run reference rows equal Stage 2's stored margins within 0.01 nats in ≥ 0.95 of cells.
  5. Gate V, for row (b).

#### What it will answer (outcome → reading, registered before the forward)

- **(a) Is the intermediate's readable leverage separate from the answer's, or contained in it?**
  - Let the removal effects be e_I = 1 − share(`q_rem_pre`), e_A = 1 − share(`q_ansrem_pre`) and e_both = 1 − share(`q_bothrem_pre`), all same-run. Define the overlap fraction ov = (e_I + e_A − e_both)/e_I, the fraction of the intermediate plane's effect that the answer plane already carries. It is reported with a cluster-bootstrap interval.
  - **Nested** (ov interval above 0.75): the intermediate's readable leverage is inside the answer's, which supports the answer-precomputed reading.
  - **Separate** (ov interval below 0.25): the two readable handles act independently.
  - Otherwise **partly shared**, with the value.
  - The registered prediction above (share ≤ min(B, B_ans) − 0.05 if separate, ≈ B_ans if nested) is scored as written beside it.
  - Control: `q_rand4rem_pre` ≥ 0.9.
- **(b) Is the half that survived Stage 2's clamp a route the lens cannot read, or an artefact of the partial clamp?**
  - The reading is taken only if V passes and `_ccsr` lies within the un-clamped `q_J25rem_pre` interval. Let C = share(`q_J25rem_pre_ccs`).
  - C ≥ 0.4: a route not J-readable at the answer position through block 62 carries at least C of the question-turn effect. Stage 2's upper bound becomes the bracket [C, 0.51].
  - C ≤ 0.2: Stage 2's surviving half was the partial clamp, and the effect reaches the answer through readable content at the answer position.
  - Otherwise: C is the result, reported with the bracket.
  - Block-63 re-entry is reported beside C in every case.
- **(c) Does the question-turn state carry the country or the capital?**
  - Let f_L = m_lang(`q_xfer`)/m_lang(`q_native_lang`), the ratio of pair means with a bootstrap over pairs.
  - **Upstream content present**: m_lang(`q_xfer`) exceeds its random control in ≥ 6 of 7 pairs, and f_L ≥ 0.3. The capital question's state carries something upstream of the answer that the language question uses. "Only the answer is carried" is then excluded.
  - **Answer content only**: f_L ≤ 0.1, m_lang(`q_xfer`) inside the random control's interval, and m_cap(`q_xfer`) > 0. The capital question's state carries the capital, not the country, which supports the answer-precomputed reading.
  - Otherwise, f_L and m_cap are reported.
  - The mirror row is read the same way with the roles swapped: f_C = m_cap(`q_mirror`)/m_cap(`q_native_cap`).
  - **Scope**: (c) separates answer content from upstream content. It cannot separate the country from the cue city it was derived from, because a push toward the donor's language could come from either.
- **Predictions on record.** V passes, because the four exact folded directions are pinned and the readout can then move only through the RMS normaliser. There is no numeric prior on ov, C or f_L. The planes are not orthogonal (cosines reported), so some overlap in (a) is expected.

#### Budget and outputs

- Rows (a) and (b) with references: 140 cells × 11 conditions × about 4.7 spellings ≈ 7,200 forwards.
- Row (c): 28 cells × about 80 ≈ 2,240 forwards.
- Plus the k = 25 pursuit pass and the translation-atom pass (tokenizer and W_U only). About 55 minutes in total, capped at 2 h.
- Raw outputs: `raw_probe3.npz`, `raw_probe3_zq.npz`, `raw_pursuit_probe3.npz`, `meta_probe3.json`, `manifest_probe3.json`.
- Report `H3/results/reports/two_hop_probe3.md`, tables `two_hop_probe3_tables.json`, figure `h3_probe3`.
- No rows beyond this set without a new amendment. A gate failure ends the stage as a gate failure.
