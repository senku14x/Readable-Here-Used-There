# H3 · computed_sum_consumer — carrier-residual replacement changes the delayed answer far less than source-residual replacement while the source is visible, despite a donor-like carrier readout on three instruments (readability vs behavioral substitutability)

**Design:** `H3/design_specs/computed_sum_consumer.md` (+ Amendment 1). **Status: competence + calibration + boundary gate + transport test complete (INTERIM, C0/C1).** Arc: §§1–5 competence (codebook-on-a-latent consumer fails); §8 calibration (composition bottleneck; **parity** is the competent distal consumer); §9 boundary gate (a full different-sum **operand** donor flips both parity and report to the donor sum, same-sum control clean, C_diff^sum +1.5); **§10 the resolution** — a **carrier** donor that installs the donor sum at the readout by the *same* internal magnitude (C_full +1.55 vs O_donor +1.50) but leaves the operands clean moves the answer only +1.7 nats and flips it **0/16**, a matched-norm random carrier write does nothing. **So the consumer does NOT consume the lens-readable maintained carrier sum — it recomputes from the operand span; the §9 "carrier state is used" framing is corrected (the operands are the used variable, the readable sum a minor ~8% contributor).** Consistent with the word consumer (0/36): the lens-readable *maintained* representation is largely not the consumer's input. **Not evaluation-grade:** C0/C1 only; necessity complement and a C2/C3 rerun pending.

Model Qwen3.6-27B @ `6a9e13b`, thinking disabled, teacher-forced copy organism, J_NP as the internal instrument. Runs: `smoke` (CPU), `competence` (48), `sumreport` (16), `calibrate` (64), `boundary` (256), `transport` (160). ~608 model forwards.

## 1. What this run was for

H3 asks whether lens-**readable** content is actually **used** by downstream computation. The prior H3 experiment (`selection_to_behavior`) used a **word**-codebook consumer and found the answer barely moved when the readout did — a full source-donor at block 36 moved the internal readout ~0.95 but flipped the greedy answer **0/36** (independently re-verified from `raw_evaluate_v2.npz`; non-pointed swaps 0/72). That is **confounded**: the answer word is a **visible token the model can re-read** below the block-36 cut, so "no flip" may just mean re-reading, not non-use — i.e. block 36 is an **unvalidated boundary** for that consumer (H3.2; reference `earlier_pilot_notes.md` §9: the word answer tracks the source span's layer 23–35 content).

The computed **sum** has **no surface token** to re-read (only the operands are visible), so it is the cleanest available consumer for isolating carrier use from re-reading. **Before any intervention**, H3.2 requires a competent consumer: one that reliably produces the right answer with **no** intervention. The word consumer had this at 1.00 (`consumer_competence.md`). **This run tested whether a computed-sum consumer clears that same gate.** Nothing downstream is interpretable until it does.

## 2. What was tested

| Step | Consumer turn (after `Here is the pair "{a} and {b}". Keep their sum in mind while you copy: {carrier}`) | Question | Forwards |
|---|---|---|---|
| `smoke` (CPU) | — | number-words single-token? donor geometry matched? spans/answer position correct? | 0 (model) |
| `competence` | `Code: seven=…, …, fourteen=…. Using the code, give the **letter** for the sum of the pair.` (3 wordings × 8 sums × C0/C1) | does the codebook consumer answer `F(sum)` clean? | 48 |
| `sumreport` | `What is the sum of the pair? Answer with one word.` (no codebook; 8 sums × C0/C1) | diagnostic: is the blocker the **arithmetic** or the **codebook-lookup** hop? | 16 |

The codebook (answer = a **letter**, not the sum word) was chosen deliberately: it decouples the answer token from the latent, so that a later donor-induced flip would mean "the sum was used," not "a token was re-read." When it failed the gate, `sumreport` isolated the cause.

`smoke` confirmed: all 21 number/decoy words single-token; different-sum and same-sum donor spans token-count- and index-matched for all calibration sums; rendered conversation and answer position correct.

## 3. Findings

**Codebook competence — FAILED.**

| query wording | accuracy |
|---|---|
| `…the sum of the pair` | **0.25** (4/16) |
| `…the sum of the two numbers` | **0.00** (0/16) |
| `…the total of the pair` | **0.125** (2/16) |

Overall **6/48**, essentially the 1/8 chance rate. Greedy outputs were valid letters but wrong ones, biased toward B/F — a genuine task failure, not a scoring artifact (the answer position produces a letter; it is just the wrong letter).

**Direct sum report — COMPETENT.** greedy 12/16; **argmax over the 8 sum-words (logsumexp over surface forms) 16/16 = 1.00.** The 4 greedy "misses" are `thirteen`/`fourteen`, where the model writes the correct word but starts it with a subtoken (`Th`/`Four`); the scored answers are correct.

## 4. Interpretation (calibrated — a viability finding, not an internal claim)

The model **computes the sum correctly** after the copy task (16/16 scored) but the **sum → arbitrary-letter codebook consumer is not competent** (≈ chance). A **direct sum-report consumer is competent**, but it is **report-like**: reporting the sum is closer to the readout than a distinct downstream computation, so a positive from it would be a **weaker** "use" claim than a codebook flip would have been.

**Hypothesis, NOT established (correction after researcher review 2026-09-08):** an earlier draft claimed the failure specifically means the model "cannot chain recall → add → codebook-lookup without CoT" / "the blocker is lookup on a computed intermediate," and tied it to the paper's §3.4 (computed latents need CoT to be used). **That is too strong for the current evidence.** A required control is missing: **`explicit-sum → same 8-entry codebook → letter`** (state the sum, then look it up). Two outcomes discriminate:

- explicit-sum lookup ≈ 1.0 while latent-sum lookup ≈ 1/8 ⇒ the arbitrary mapping *is* usable and the specific bottleneck is **composing the internally computed latent into it** (the interesting "limited compositional accessibility" reading).
- explicit-sum lookup *also* fails ⇒ the interpretation is wrong: the 8-entry random number-codebook task is simply too hard / poorly elicited, and this competence failure says little about computed-latent use.

The word consumer's earlier 1.00 (arbitrary 6-entry lookup on an *available* identity) is *suggestive* of the first outcome but is not matched (nouns not numbers, 6 not 8 entries, a visible token not a latent), so the explicit-sum control is still required. **(Update: this control has now run — see §8. It gives explicit 1.00 / latent 0.25, i.e. the first outcome: the composition step is the bottleneck, not the lookup task. The narrower "needs CoT" mechanism remains unproven.)**

## 5. What was NOT tested

**Nothing about the H3 "use" question.** No donor, no source replacement, no boundary, no dissociation. This run only established **which consumers are competent enough to test with**. No claim is made or implied about whether the computed sum is behaviorally used, or about any internal-vs-behavioral dissociation for the sum.

## 6. Next decision (reoriented after researcher review — objective changed from "make the codebook work" to "find the simplest competent computation of the latent, validate a boundary, test multi-consumer")

**A tiny calibration round first (~64 forwards):**
- **A. explicit-sum → codebook control** — the missing control of §4; isolates arbitrary-lookup competence from latent→lookup composition. Same codebook across matched latent/explicit conditions.
- **B. sum → `Is their sum greater than ten?`** competence — a distinct computation of the latent (no lookup); the preferred **primary** consumer because it is more distal from the readout than a report.
- **C. sum → parity** competence — an independent second consumer.
Require ≥ 0.9 (preferably 1.0) before any intervention.

**Then, only if a competent consumer exists:** a **full-donor boundary gate at L23 and L36** (different-sum donors chosen to cross the predicate; same-sum siblings as controls; internal J_NP sum readout on the same forwards). If a full donor cannot move a competent consumer at a cut, stop selective residual interventions there. Let the L_x sweep pick the boundary — do not assume block 36.

**Then the strong step — `same_content / different_consumers`:** apply the *same* pre-consumer counterfactual, then reveal report / >10? / parity. If one fixed latent drives each appropriately, output-token-steering is excluded (the outputs are different tokens). Licensed claim at that point: the block-36 **carrier state is computationally used** (not just an output bias) — **not** yet "the sum latent specifically is the reusable variable" (that needs a fitted sum-state patch or operand-route restriction). Representation ladder/rescue only after a rich donor proves the consumer/boundary is manipulable.

(Not pivoting to H2 yet; the multi-consumer route keeps the question in H3 and avoids the hybrid cache/GatedDeltaNet serialization until it is actually required.)

## 7. Verification and limitations

- Calibration scale (8 sums × C0/C1; wordings ×3 at competence). Establishes viability, not effect size. No evaluation-bank materials touched.
- Greedy vs scored: `sumreport` competence is reported as **argmax over the 8 sum-words (logsumexp over `{w, ' '+w, Cap, ' '+Cap}`)**; the multi-token generation of `thirteen`/`fourteen` (`Th`/`Four`) is why greedy (12/16) < scored (16/16); the scored value is the competence.
- Thinking disabled throughout (project convention). The codebook failure is scoped to that setting; it does not claim the model could not do the lookup with CoT.
- **Uncontrolled wording comparison (bug, researcher review).** The competence battery seeded a *different* random codebook per query wording (the RNG key included `list(QUERIES).index(qname)`), so the 0.25 / 0.00 / 0.125 wording spread is not a controlled comparison (different codebooks). Overall performance is chance-level either way, so no consumer is rescued; but wording is neither selected nor rejected on those relative numbers. Fixed to seed per (sum, carrier) going forward.
- **The written `boundary` stage must NOT be run as-is (researcher review).** It hardcodes the *failed* codebook consumer (`query = QUERIES[FROZEN_QUERY]`); it is **not** the "direct sum-report boundary test" discussed in §6. Running it would interpret an intervention at a consumer that failed its competence gate, violating H3.2 / project rule. It stays unrun and will be rewritten around a validated consumer.
- Artifacts: `H3/outputs/computed_sum_consumer/{meta,raw,manifest}_{competence,sumreport,calibrate}.json/.npz`, logs. All < 25 KB (git). Script `H3/scripts/computed_sum_consumer.py`.

## 8. Update (2026-09-08) — A/B/C calibration (researcher-directed; `calibrate` stage, 64 forwards, RNG fixed to one codebook per (sum, carrier))

- **A. explicit-sum vs latent-sum codebook lookup (same codebook): explicit 1.000, latent 0.250 (n=16 each).** The arbitrary 8-entry lookup is fully usable when the sum is stated; it fails when the sum must come from the model's own computation. **Supports the composition-bottleneck reading (§4) and rejects the "the codebook task is just bad" alternative.** Scoped claim: latent→arbitrary-lookup composition fails while explicit lookup succeeds — *limited compositional accessibility of the computed latent*, thinking-off. It localizes the failure to the composition step; it does **not** prove the mechanism is specifically "no CoT."
- **B. `Is their sum greater than ten?`: 0.812 (13/16) — sub-competent.** The 3 misses are *comparison* errors (nine→"yes", twelve→"no"), not sum errors (parity is 1.00, so the sum is computed correctly). Not usable as a boundary consumer as-is.
- **C. parity (`even/odd`): 1.000 (16/16) — competent.** A distinct computation of the latent (not a report), balanced 4/4. **This is the primary boundary consumer.**

**Consequence for the (still unrun) boundary gate:** the existing different-sum donor always has *opposite* parity to the recipient (donor sum = row (i+3) mod 8; +3 flips parity mod 8), and the same-sum sibling preserves it — so `diff_donor` is a clean parity-flip and `same_donor` the matched control, no new materials. Plan: rewrite the `boundary` stage around **parity** (primary) + **direct sum-report** (cheap secondary, same intervention), sweep L_x ∈ {23, 36}, keep the internal J_NP sum readout on the same forwards; let the sweep pick the boundary. A full donor that cannot move a competent consumer at a cut ends selective residual interventions there.

## 9. Boundary gate — RESULT (2026-09-08, `boundary` stage, 256 forwards, all 8 sums × C0/C1, parity + report, L_x ∈ {23,36})

**A full different-sum donor on the pair span causally controls the sum consumers' answers, where the re-readable word consumer's answer was not controlled at block 36.**

Gates: self-patch bitwise no-op **32/32**; layers < L_x identical (asserted, run clean); donor geometry matched 8/8; realized write exact (read-back error 0.0); **carrier ΔNLL ≈ 0.000** (max +0.001) — no copy damage.

| endpoint (greedy) | word consumer (`selection_to_behavior`, full source-donor @36) | **sum — report** | **sum — parity** |
|---|---|---|---|
| diff-donor flips the answer to the donor value, **@L36** | **0/36** | **16/16** | **12/16** |
| @L23 | — | 16/16 | 16/16 |
| **same-sum sibling** flips (control) | — | 0/16 | 0/16 |
| clean competence in-context | — | 16/16 | 16/16 |
| internal J_NP sum readout C_diff^sum (L51–59, same forwards) | (word rep moved ~0.95, answer didn't) | **+1.5, 16/16** | +1.5, 16/16 |

The 4 parity-L36 non-flips are the two highest sums (twelve, thirteen) × both carriers; report flips there, so it is a mild robustness dip of the coarse parity readout at the later cut. Qualitative S0 (seven→ten): parity clean=odd, diff@{23,36}=even (flip), same@{23,36}=odd (stays); report clean=Seven, diff=ten, same=Seven.

**Prediction check:** the pre-registered prior (L36 might not flip; weak L23 > L36) was **too pessimistic** — report flips 16/16 at both cuts; parity 16/16 (L23) / 12/16 (L36). Block-36 carrier content *does* control the answer for this latent.

**Licensed (causal, this organism, C0/C1, 8 sums, thinking-off):** the block-36 carrier state is **computationally used** by the sum consumers — two *different* output computations (parity vs the sum word) exclude output-token-steering, the same-sum control excludes non-specific perturbation, and there is no surface sum-token to re-read. This is the H3 positive the word consumer lacked (0/36 at the same intervention shape, because its answer re-reads the visible word below the cut).

**NOT licensed (transport vs recomputation — the open crux):** whether the **readable sum specifically** is the reusable variable, or the model **recomputes** the sum from the patched **operand** residuals per consumer. The full-operand donor changes both; multi-consumer rules out output-steering, not per-consumer recompute. The same-sum control (tracks value not operands) and the graded L23≥L36 pattern are consistent with *either*. **Next:** the transport-vs-recomputation step (the H3 plan) — a fitted sum-state patch that preserves operands, or an operand-route restriction.

**Cluster-t over the 8 sums (df=7; carriers averaged within sum), behavioral margin shift logP(donor value)−logP(own value), diff/same minus clean:** report diff **+21.3 [20.0,22.7]** / **+21.1 [19.8,22.4]** at L23/L36 (8/8), same ≈0 (−0.4 / −0.3); parity diff **+6.5 [5.9,7.0]** / **+3.9 [3.0,4.8]** (8/8), same ≈0. Internal C_diff^sum **+1.55 [1.30,1.80]** / **+1.50 [1.30,1.69]** (8/8). The effect survives the registered clustering; the report margin is larger than parity because report emits the sum word directly whereas parity is a 1-bit output.

**Scope/limits:** one organism, C0/C1 (C2/C3 reserved), thinking-off, 8 arithmetic facts. The word-vs-sum comparison shares the "full source-span donor from block 36" intervention shape but differs in consumer; the mechanistic reading (token re-read below the cut vs computed content spanning it) is an interpretation, not yet an isolated cause. **The transport-vs-recomputation crux is not yet resolved (see below).**

## 10. Transport vs recomputation — RESULT (2026-09-08, `transport` stage, 160 forwards): the carrier-only donor moves the answer ~8 % as much as the operand donor and never flips it — wording here superseded by §11–§12; see the claims table in §12

**Design.** The carrier is the copied sentence — it holds the sum-latent but **no operand tokens**. So intervene at the carrier (operand span clean) vs the operand span, and read which the consumer follows. Conditions (from L_x=36, all 8 sums × C0/C1, parity + report): `O_donor` (operand span → donor, carrier free — the boundary reference), `C_full` (carrier → donor carrier state, operand span **asserted clean**), `C_rand` (carrier → recipient + per-position norm-matched random). Gates: operand span bitwise-untouched under C_full (asserted); carrier ΔNLL ≈ 0.

**The matched internal control.** C_full installs the donor sum at the carrier readout by the **same magnitude as O_donor**: internal z(donor_sum)−z(own_sum) minus clean, L51–59, cluster-t(8): **O_donor +1.50 [1.30,1.69]**, **C_full +1.55 [1.31,1.80]** (both 8/8); C_rand +0.13 (content-specific: random moves it ~12× less).

**Result (report consumer; parity in parentheses):**

| condition | internal carrier sum-readout | behavioral margin (logP donor−own, cluster-t 8) | greedy flips |
|---|---|---|---|
| O_donor (operands→donor) | +1.50 | **+21.1 [19.8,22.4]** (parity +3.9 [3.0,4.8]) | 16/16 (12/16) |
| **C_full (carrier→donor, operands clean)** | **+1.55** | **+1.70 [1.09,2.31]** (parity +0.53 [0.19,0.87]) | **0/16 (0/16)** |
| C_rand (carrier random, matched norm) | +0.13 | +0.05 [−0.01,+0.11] (parity −0.07) | 0/16 (0/16) |

**Reading (causal, this organism/site/dose).** With the lens-readable carrier sum moved to the donor by the **same internal magnitude** under C_full and O_donor, the answer flips under O_donor (operands changed) but **not** under C_full (operands clean, 0/16, +1.7 nats ≈ 1/12 of O_donor). A matched-norm random carrier write does nothing. Therefore **the consumer does not consume the lens-readable maintained carrier sum; it recomputes the answer from the operand span** (re-read at layers ≥ L_x). C_full transplants the carrier state **from block 36 onward** (the sum-bearing layers; it is readable at L51–59 and the internal readout confirms the donor sum is installed at its full natural level, C_full/O_donor internal ratio 1.04), so this is not a single-direction false negative — the maintained sum-bearing state fails to drive the answer. *Flip counts use the scored-argmax rule throughout (audit §3.1: an earlier draft's greedy-prefix rule under-counted O_donor report flips as 14/16; the correct count is 16/16).*

**This corrects §9's framing.** The O_donor flip was driven by the **operand-span content**, not the maintained carrier sum. "The block-36 carrier state is used" (§9) is too strong: the *specific readable sum-latent* is a **minor** contributor (C_full +1.7, 8/8 — real, content-specific vs C_rand, but never flips), while the **operands** are the used variable. This is a **readability-vs-use dissociation with a matched internal readout** — the project's H3.3 row "J moves toward Y; answer remains X-like ⇒ this intervention is insufficient to substitute for the state used by this consumer."

**Consistent with the word consumer (0/36).** Across both organisms, the lens-readable *maintained* representation (word / carrier sum) is largely **not** the consumer's input — the consumer re-reads/recomputes from the still-visible original source. A refinement of the paper's "the workspace is used" on this open model: the paper's swaps were **global** (over source positions too); **localized** interventions that leave the source re-readable give a more deflationary answer for these consumers.

**Limits / next.** One organism, C0/C1, block-36 carrier site, thinking-off, 8 facts. Convergent confirmation = the necessity complement (O_donor with the carrier sum **clamped to own** — does the answer still flip to donor? expected yes, confirming the operand route). The small real C_full effect (+1.7) bounds the maintained sum's contribution rather than zeroing it. A C2/C3 evaluation rerun and the necessity test are the next passes.

## 11. Robustness battery (Amendment 2, 2026-09-09) — the dissociation survives; C_all, NEC, C2/C3 and a second donor map added

Full tables: `computed_sum_consumer_robust.md` (analysis `computed_sum_consumer_analysis.py robust`; 1,022 forwards, run 20260909T121335Z). Registered predictions in the design spec, Amendment 2. Pooled over C0–C3, map offset 3, report consumer (parity in parentheses):

| condition | behavioral margin | flips | carrier sum shift J_NP / RESID_P / LOGITS (L51–59) |
|---|---|---|---|
| O_donor (operands → donor) | +21.2 [+19.9, +22.5] (+3.88) | 32/32 (23/32) | +1.55 / +0.76 / +2.49, all 8/8 |
| C_full (carrier → donor, ≥ 36) | +1.75 [+1.17, +2.33] (+0.70) | 0/32 (0/32) | +1.62 / +0.68 / +2.58 (by construction) |
| C_all (carrier → donor, all 64 blocks) | +1.76 [+1.16, +2.36] (+0.74) | 0/32 (2/32) | same |
| C_rand (matched norm) | +0.05 (+0.02) | 0/32 | +0.14 / +0.01 / +0.11 |
| NEC (operands → donor, carrier clamped own) | +19.3 [+17.9, +20.6] (+3.18) | 32/32 (17/32) | 0.000 (clamp gate) |

- The premise is instrument-independent: under donor operands the free-running carrier holds the donor sum on the lens, on an independently fitted plain-sentence number axis and on the carrier logits. (Under C_full the agreement is trivial: those positions are the donor's states.)
- Replacing the carrier from block 0 instead of block 36 changes nothing (C_all ≈ C_full). The earlier null was not a depth artifact (§10 precision fix now moot).
- The operand route is sufficient alone (NEC flips 32/32), and the two routes are roughly additive: O_donor ≈ NEC + C_full. The carrier copy's share is ≈ 9 % (report) to 18 % (parity) of the operand-donor effect, and never decisive.
- Answer-position residual: C_full moves it 0.14–0.22 as far as O_donor and ≈ 1.7× a matched random write. The consumer registers the carrier content weakly; the registered "≥ 0.5" prediction was not met, the "< 0.1, not consulted" verdict was not triggered either. Wording: the carrier is weakly consulted and not acted on.
- C2/C3 and the offset-1 donor map reproduce every row (report C_full +1.80 / +1.32, 0 flips; O_donor +21.3 / +17.7, all flips).
- The word organism gives the matched result (`selection_to_behavior_carrier_only.md`): carrier-only donors move the letter margin ≤ 0.04 of the ceiling, 0/36 flips, at either depth.

**Corrected headline for §10.** With the operand tokens visible, the sum consumers compute their answer from the operand positions; the carrier's lens-readable copy of the sum, confirmed on three instruments, contributes about a tenth of the effect and never changes the answer, at any cut depth, on four carriers and two donor maps. Still not licensed: what the consumer does when the operands cannot be re-read (route restriction, the H3 plan), which is the remaining question before "use" can be asserted or denied in general.


## 12. Current claims and withdrawals (2026-09-09)

Read this table before quoting any earlier section; it supersedes conflicting wording above. Same table in `context/evidence_ledger.md` §E.

| claim | status |
|---|---|
| §9 "the block-36 carrier state is computationally used" | withdrawn (operand-span content drove the flip) |
| §10 "the readable sum is NOT used; the consumer recomputes from the operands" | superseded: the carrier copy has a real content-specific effect (×5.8 donor odds on report, ×2 on parity; +1.75 / +0.70 nats; P(own) unchanged on report, −0.07 on parity; 0/32 flips), and "operand positions" is not yet "raw operands" (token-level control in the `global` stage) |
| "the consumer does not consult the carrier" | superseded: the answer position moves 0.14–0.22 as far under the carrier donor as under the operand donor, 1.7× a matched random write — weakly consulted, not acted on |
| **defensible statement** | making the carrier residuals donor-like — which installs the donor sum at the readout on J_NP, RESID_P and LOGITS, from block 36 or block 0, on four carriers and two donor maps — changes the delayed answer far less than replacing the source-span residuals while the source remains available. This separates selective readability from behavioral substitutability; it does not identify the maintenance mechanism, establish natural non-use, or say what the consumer does when the source is unavailable |
| `two_hop_organism` `qsplit` (2026-09-11, Amendment 5): the H3.3 ladder at the question turn, scoring position excluded, fp32, sequence endpoint | **supported — complement dominant**: full question-turn donor +11.19 nats (12/12); the intermediate's two-token naming plane alone 0.20 of that while installing the J_NP q-readout as strongly as the full donor; the donor delta with the plane removed and clamped to clean 0.78 (plane readout at clean, no re-entry at block 63); norm-matched random plane 0.003; donor minus an equal-norm random component 0.98. Scope: a 2-token plane, not a k = 25 J-space reconstruction; three fixed trajectories, not a partition; one organism, one model. Report `H3/results/two_hop_qsplit.md`; ledger §E. |


## 13. Amendment 3 — token-level operand control, consistent clamp, paper-style coordinate swap, decision-position donor, first route-restriction pass (2026-09-09, `global` stage, 958 forwards)

Full tables and the prediction-by-prediction reading: `computed_sum_consumer_global.md`. Headlines (all carriers, report; parity in parentheses):

| condition | margin (nats) | flips |
|---|---|---|
| operands → donor, all 64 blocks (token-equivalent) | +21.6 (+6.8) | 32/32 (32/32) |
| operands → donor, ≥ 36 | +21.2 (+3.9) | 32/32 (23/32) |
| carrier → donor, ≥ 36 | +1.75 (+0.70) | 0/32 (0/32) |
| operands + carrier → donor, ≥ 36 (consistent) | +21.3 (+4.2) | 32/32 (24/32) |
| paper-style coordinate swap, all positions from the operands on, L36–62 | +11.1 (+0.2, ns) | 16/32 (0/32) |
| same swap, carrier only | +0.35 (+0.04) | 0/32 (0/32) |
| decision positions ← donor, L36–50 | +0.7 (+4.1) | 0/32 (21/32) |
| mask consumer→operand attention, clean | +6.7, competence FAIL (+2.2, competence 29/32) | — |
| mask + carrier → donor | — (+3.4) | — (17/32) |
| mask + operands → donor | — (+3.6) | — (18/32) |

- Late operand residuals ≡ operand tokens for the report consumer (closes the critique's first objection).
- The consistent global clamp behaves like the operand donor; the carrier's marginal contribution is bounded by its conflicting-state contribution. The conflict objection is bounded, not removed.
- The paper's coordinate-swap intervention reproduces when it covers source and decision positions, not when confined to the carrier; its parity null shows the report flips are consistent with answer-token steering rather than substitution of the computed sum.
- The parity answer is settled in the decision-position residuals by block 50; the report answer is not.
- With the direct attention read of the operands closed (parity only; report loses competence), the carrier copy's influence rises to the size of the operand donor's remaining influence (+1.2 vs +1.35 nats over a degraded baseline). First evidence toward "consulted when needed"; not established (recurrent channel open, baseline degraded).
