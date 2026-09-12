# H3 · computed_sum_consumer — does a computed latent (the sum) reach a consumer where a re-readable token did not?

**H3: `computed_value_versus_recomputation` + `consumer_boundary_and_rescue`.** Script `H3/scripts/computed_sum_consumer.py` (stages `smoke`, `competence`, `boundary`; later `recomputation`, `ladder`); analysis `computed_sum_consumer_analysis.py`. Outputs `H3/outputs/computed_sum_consumer/`; results `H3/results/computed_sum_consumer.md`. **Status: registered design, nothing run.** Written 2026-09-08.

---

## 0. Why this experiment, and why now

`selection_to_behavior` put a word-codebook consumer on the tagged organism and found an internal-vs-behavioral *dissociation*: the H1 instruction-region transplant moved the lens ~0.76 but the answer only ~0.2, greedy flips 2/36. An independent recomputation from the saved arrays (`raw_evaluate_v2.npz`) sharpened this: **a full source-donor replacement at block 36 — the strongest available intervention there, which moves the internal readout ~0.95 — flips the greedy answer in 0/36 cells** (non-pointed swaps 0/72). Per H3.2 and the earlier pilot (`earlier_pilot_notes.md` §9: the word answer tracks the source span's layer 23–35 content), that means **block 36 is not a validated boundary for the word consumer** — its answer is re-read from the still-visible source token, below the cut. A partial/null representation effect at an unvalidated boundary is uninterpretable (H3.2: "Do not require a scalar hypothesis to survive an unresponsive site").

A **computed sum has no surface token to re-read.** The identity the consumer needs (the value, e.g. `seven`) is never printed; only the addends are. So this is the cleanest available test of H3's actual question — *does the carrier's representation of a latent control a consumer?* — because re-reading a surface token is not a route to the answer. H1 (`computed_sums`) already established that the **computed sum transfers to the readout** (C_diff^sum +1.90, 8/8; same-sum sibling invariant C_same^sum ≈0). This experiment appends a codebook consumer to those same interventions and asks whether that transfer reaches the answer.

## 1. Endpoints, in order

1. **Competence** — does a sum→letter codebook consumer answer `F(sum)` at all? (Gate; the arithmetic itself is 16/16 in H1, but the codebook indirection is a harder task and must be validated, exactly as `consumer_competence` validated the word consumer.)
2. **Boundary validation (the H3.2 positive control that failed for the word consumer)** — does a full-state **different-sum** donor at the addend span **flip the greedy answer** toward the donor's sum-letter, at some L_x, while a **same-sum sibling** donor does not? Directly comparable to `selection_to_behavior`'s 0/36 at block 36 (same L_x, same "full source-donor" intervention class, latent-vs-token as the only difference).
3. **(deferred to later stages, only if the boundary validates)** transport-vs-recomputation (transport vs recomputation) and the representation ladder + rescue (§6).

The first thing run is **competence + boundary**, not the ladder. Nothing downstream is interpretable until a full donor moves the answer.

## 2. Hypotheses and what each outcome licenses

The visible addend tokens are unchanged in every condition; only the addend-span **residuals** (block outputs) are replaced from L_x. To answer, the model must produce the sum, from one of: (a) the carrier's transported sum representation, (b) recomputation from the operand residuals at the cut, (c) re-reading the visible operand tokens (below L_x) and recomputing.

| Observed | Licensed interpretation |
|---|---|
| **Different-sum** donor flips the greedy answer toward `F(sum_donor)` (CI-clear), **same-sum** sibling does not, internal C_diff^sum reproduced | The carrier's block-≥L_x representation of the **computed sum** controls this consumer at that boundary. A latent reaches behavior **where a re-readable token (word consumer) did not** — a double dissociation with `selection_to_behavior`. **Route caveat (§12):** transport of the completed sum vs recomputation from the *patched operand residuals* is not yet separated. |
| Neither donor flips the answer at any tested L_x, **while the internal sum readout still moves** (C_diff^sum reproduced → intervention live, instrument sensitive) | Clean **negative**: even a latent value is not behaviorally controlled by a residual patch on this consumer at these cuts; the answer is recomputed from the operand tokens below L_x (or read from cache/recurrent state a block-output hook cannot reach). H3's "use" question needs the **H2 complete-state (cache + recurrent) boundary**, not residual patches. Scoped to residual patch at these L_x — **not** "the sum is globally unused." |
| Different-sum donor flips at block 23 but not block 36 | The consumed sum is fixed between blocks ~23 and ~36; the boundary that controls behavior precedes 36 (consistent with the earlier pilot's layer 23–35 finding, now for a latent). |
| **Same-sum** sibling flips the answer | The consumer tracks the **addends**, not the sum; competence/consumer misspecified — fix before interpreting anything else. |
| Full donor flips but clean competence < 0.9 | A low-competence arm cannot support a strong claim; simplify the consumer (ask for the sum word directly first) before the boundary stage. |

Predictions before the run: I expect the different-sum donor to have a **better chance of flipping than the word consumer did (0/36)**, because there is no surface token to fall back on — but recomputation from the visible operands is a live route that could still yield 0 flips. I am near 50/50 on which way the boundary stage lands; both are decision-relevant.

## 3. Organism and exact strings

Turn 1 (H1 `computed_sums`, unchanged, so the internal effect is the established one):

```
Here is the pair "{a} and {b}". Keep their sum in mind while you copy the following text exactly, word for word:

{carrier}
```

Assistant turn: the carrier, teacher-forced. Turn 2, appended via `rendering.render(..., extra_turns=[(codebook + "\n" + query, "")])`:

```
Code: {n1} = {L1}, {n2} = {L2}, ..., {n8} = {L8}.
Using the code, give the letter for the sum of the pair. Answer with the letter only.
```

**Query wording frozen after the competence stage** (mirror `consumer_competence`: pick the highest-margin competent wording; record it; do not re-open). The query does not restate the sum or the addends. Candidate wordings for competence: `the sum of the pair`, `the sum of the two numbers`, `the total of the pair`.

**Codebook.** Eight entries: the number-words **`seven, eight, nine, ten, eleven, twelve, thirteen, fourteen`** (every reachable sum) → letters `B D F H K M Q V`, a bijection. Entry order and letter assignment permuted independently of each other and of identity, seeded per cell (`SEED=20260908`, key `SEED + 1000*sum_idx + 100*Lx + carrier`). Save the realized assignment. Because all eight sums are in the codebook, the recipient's sum **and every donor's sum** have a defined counterfactual letter. Multi-token sum words (`thirteen`, `fourteen`) are fine here: they appear only as codebook entries the model reads; the scored answer is always a single-token letter.

## 4. Materials and exposure

Appendix B3, exact:

| idx | Sum | A-addends (recipient) | Same-sum B (sibling donor) |
|---|---|---|---|
| 0 | seven | two, five | three, four |
| 1 | eight | two, six | three, five |
| 2 | nine | two, seven | four, five |
| 3 | ten | two, eight | three, seven |
| 4 | eleven | three, eight | four, seven |
| 5 | twelve | four, eight | five, seven |
| 6 | thirteen | five, eight | six, seven |
| 7 | fourteen | six, eight | five, nine |

- **Recipient** always uses the **A-addends**, maintain arm.
- **Different-sum donor** for row i = the **A-addends of row (i+3) mod 8** (the same map as H1 `computed_sums`, so internal rows are directly comparable). Its sum differs from the recipient's.
- **Same-sum sibling donor** for row i = row i's **B-addends** (same sum, different operands; H1 showed C_same^sum ≈ 0).
- **Competence stage:** all 8 sums, carriers C0/C1 (competence readout only — no intervention). Disclosed exposure of all 8 sums at competence.
- **Boundary pilot:** calibration sums **{0 seven, 3 ten, 6 thirteen}** (spread across the range; `thirteen` also checks a multi-token sum word in the codebook), carriers C0/C1, L_x ∈ {23, 36}. **Cluster = sum.**
- **Evaluation (only if the boundary validates):** all 8 sums, carriers C2/C3, the validated L_x, plus the maintain/control arm for instruction modulation. Registered separately after the pilot.
- Donor geometry: `"{a} and {b}"` is 3 content tokens iff every number-word is single-token; **assert per cell**, flag/skip any pair whose donor is not token-count- and index-matched (do not crop). Verify in `smoke`.

## 5. Conditions (boundary stage)

Sustained block-output replacement of the **addend span** (the `{a} and {b}` content tokens inside the quotes) from L_x onward, on the recipient's own rendering (visible text identical across conditions).

- `clean` (recipient A-addends, maintain, no replacement) — ceiling / competence-in-context.
- `diff_donor@Lx` for L_x ∈ {23, 36} — replace addend span with the different-sum donor's states.
- `same_donor@Lx` for L_x ∈ {23, 36} — replace with the same-sum sibling's states (specificity control: sum unchanged ⇒ answer should not move).
- `noop` — same-source replacement (bitwise gate).

**Internal companion, same forwards:** the H1 sum-word margin `m_sum = z(sum_donor) − z(sum_recipient)` and addend margin at carrier interior (both windows), giving C_diff^sum and C_same^sum in-experiment, to confirm the readout effect reproduces H1's +1.90 / ≈0 (the sensitivity anchor).

## 6. Endpoints and measurement

Score every letter at the answer token (last position), both surface forms, combined by **logsumexp**; save the full `llp[8,2]` and the greedy decode.

**Competence.** greedy = `F(sum)`; accuracy per sum; margin `b_sum = logsumexp F(sum) − logsumexp over the 7 other sum-letters`. Also the forced margin vs all 8. Report per sum and per wording.

**Boundary (primary).**
- **Greedy answer classification** per cell: recipient-sum letter / donor-sum letter / other-valid / invalid. **The headline is the flip rate `diff_donor → F(sum_donor)`.**
- `U_full = b_dr(diff_donor) − b_dr(clean)`, where `b_dr = logsumexp F(sum_donor) − logsumexp F(sum_recipient)`. `U_full > 0` with donor-letter flips = the boundary controls the answer.
- `same_donor` classification (should stay recipient-sum) and its `b_dr` (should be ≈0).
- Internal C_diff^sum / C_same^sum on the same forwards (reproduce H1).
- **Direct comparison:** the `diff_donor@36` flip rate beside `selection_to_behavior`'s 0/36.
- Cluster-t over sums; per-sum values and sign counts; ratios (if any) with numerator and denominator.

## 7. Gates (before any outcome is read)

1. Rendering: quoted pair span, both carrier occurrences, appended turn, answer = last token — all decoded and asserted.
2. Addend-span token geometry: donor and recipient identical token count and span indices (assert per cell; flag/skip mismatches).
3. Same-source replacement bitwise equal to clean; layers < L_x identical between futures; `noop` self-check.
4. Realized writes: ρ ∈ [0.9, 1.1], κ ≥ 0.99 (SpanWriter overwrites ⇒ ρ ≈ 1, read-back error 0.0; record it).
5. Codebook: all 8 sum-words present; answer letters single-token in both forms; realized assignment saved.
6. Competence in context: `clean` greedy = `F(sum)`. A clean cell failing this is reported, not dropped; accuracy is not an intervention endpoint (use the classification).
7. Consumer/answer positions never patched; the intervention is confined to the addend span at layers ≥ L_x.

## 8. Decision rules

- **`diff_donor` flips greedy → `F(sum_donor)` CI-clear at some L_x, `same_donor` does not, internal C_diff^sum reproduced** → validated boundary; the computed sum reaches this consumer. This is the positive the word consumer lacked. **Next:** transport-vs-recomputation (§23.5: a fitted native sum-state patched in isolation vs an operand-only patch) and the representation ladder + rescue (§6).
- **`diff_donor` flips ≈0 at every L_x while internal C_diff^sum is reproduced (sensitivity present)** → clean negative, scoped to residual patch at these L_x: the answer is recomputed from operands below the cut, or read from cache/recurrent state a block-output hook cannot reach. **Pivot to the H2 complete-state boundary** (cache + GatedDeltaNet recurrent serialization with bitwise parity) before further H3 residual work; do **not** read it as "the sum is unused."
- **`same_donor` flips the answer** → the consumer tracks addends, not the sum; fix the consumer/competence first.
- **Competence < 0.9 on the calibration sums** → simplify the consumer (ask for the sum word directly first) before the boundary stage.
- **Internal C_diff^sum not reproduced on these forwards** → an implementation/appended-turn fault (cf. `selection_to_behavior` gate 3); debug tokenization/positions/hooks/length before interpreting behavior.

## 9. Budget

- `competence`: 8 sums × 2 carriers × 3 wordings × 1 = **48 forwards** (~30 s).
- `boundary` pilot: 3 sums × 2 carriers × (clean + diff_donor×2 L_x + same_donor×2 L_x + noop) = 3×2×6 = **36 forwards** (~20 s).
- Pilot total ≈ **84 forwards**, ~1 min. Evaluation (post-validation): 8 sums × 2 carriers × 6 + maintain/control ≈ 200–400 forwards.

The primary decision (competence + does a full donor flip?) costs ~1 minute of GPU. Cheap and decisive.

## 10. Implementation notes

- Base on `H1/scripts/computed_sums.py` stage `transfer` (addend-span replacement, geometry/identity asserts, sum instrument) + `H3/scripts/consumer_competence.py` (letter ids both forms, seeded codebook) + `H3/scripts/selection_to_behavior.py` (consumer-turn append via `extra_turns`, answer scoring, five-way classification, self-patch gate, matched-length donor rendering). Lift shared pieces into `common/`; do not import an H1 runner from an H3 runner.
- Donors are rendered **with the consumer turn** (matched length), the `selection_to_behavior` v2 fix; the primary noswap/clean endpoint never uses donor source states.
- Save per cell: `z` (all layers, carrier interior), sum-word and addend presence columns, `llp[8,2]`, greedy token, `nll`, `top1`, realized-write stats, codebook assignment, geometry asserts.
- Report: internal (C_diff^sum) vs behavioral (flip rate / U_full) beside each other; per-sum paired points; seeded qualitative cells with the exact prompt, codebook, intervention, top readouts, letter probabilities, generated answer, classification.

## 11. Verification companion

Independent recomputation of the headline flip rate and U_full from the saved `llp`/greedy arrays (a `recompute_saved`-style script, no runner import), and a GPU trace of one cell (token ids, patched positions, donor immutability, layers<L_x untouched, answer alignment), before the numbers are promoted — the same two-audit discipline as `selection_to_behavior`.

## 12. What this experiment cannot claim

- **Transport vs recomputation (§23.5).** A `diff_donor` flip with unchanged visible operand tokens rules out surface re-reading, but **not** recomputation from the patched operand *residuals*. Separating them needs a fitted native sum-state patched in isolation (H1 deferred the RESID sum axis), or a competence-preserving operand-route restriction — the `recomputation` stage, only after the boundary validates.
- **Instruction modulation** (maintain vs control on the answer) — deferred to the evaluation stage.
- Anything about other consumers, the word/tagged organism, categories, or non-sum latents. A negative is scoped to residual patches at the tested L_x on this consumer; the cache/recurrent route is untested (that is H2).

---

## Amendment 1 — codebook consumer failed competence; boundary gate uses parity (2026-09-08, after the competence + A/B/C calibration, researcher-directed)

The codebook-on-a-latent consumer (§3) **failed competence** (6/48 ≈ chance). The researcher-directed calibration (`calibrate` stage) established: (A) explicit-sum→codebook 1.00 vs latent-sum 0.25 ⇒ composition bottleneck, not a bad task; (B) `>10?` 0.81 (sub-competent, comparison errors); (C) **parity 1.00 (competent)**. Corrections to the interim report (RNG-confound; "needs CoT" downgraded to a hypothesis; the written codebook boundary must not run) are in `H3/results/computed_sum_consumer.md` §4/§7/§8.

**Boundary stage rewritten** (the codebook version is withdrawn, never run):
- **Consumers (multi-consumer on the same intervention):** `parity` (`Is their sum even or odd?`, primary — a distinct computation, 1.00) and `report` (`What is the sum?`, secondary, cheap boundary positive control). Same donor intervention, two revealed consumers.
- **Intervention:** sustained block-output replacement of the quoted pair span from L_x, L_x ∈ {23, 36}. `diff_donor` = A-addends of row (i+3) mod 8 (**always opposite parity** — verified 8/8) → the parity-flip; `same_donor` = same-sum B-addends (**same parity**) → matched control. Same-source no-op gate; layers < L_x asserted identical; realized-write diagnostics.
- **Materials:** all 8 sums × C0/C1 (calibration carriers; C2/C3 reserved). Cluster = sum. ~256 forwards.
- **Endpoints:** greedy parity flip toward donor parity (and report flip toward donor sum) under `diff_donor`, vs no flip under `same_donor`; internal J_NP sum readout (C_diff^sum, reproduce H1 ~+1.90) on the same forwards as the sensitivity anchor; per-L_x.
- **Decision:** a full donor that cannot move a competent consumer at a cut ⇒ stop selective residual interventions there (H3.2). If it flips, the licensed claim is scoped per report §6/§8 (block-36 carrier state is *computationally used*, not "the sum latent specifically").
- **Prediction (on record before the run):** internal C_diff^sum reproduces H1 (high confidence); parity/report flips genuinely uncertain, weak prior L23 > L36 (operands patched before vs after the sum is fixed); same_donor must not flip.

## Amendment 2 — robustness battery for the transport dissociation (registered 2026-09-09, before any forward)

**Why.** The transport result (report §10: a carrier-only donor installs the donor sum at the readout at the O_donor level yet moves the answer +1.7 nats and flips 0/16, while the operand donor flips 16/16) is the load-bearing H3 finding. It was designed after the boundary result and is not covered by Amendment 1, so this amendment registers it retroactively together with the battery that must survive before it is cited. The battery attacks the three legs the dissociation rests on: (i) the installed-sum premise is measured on J_NP only; (ii) the carrier below block 36 stays the recipient's, and it is assumed rather than measured that the carrier change reaches the consumer position; (iii) materials are two calibration carriers and one donor map.

**Stage `robust`** (`computed_sum_consumer.py robust`), all 8 sums × carriers **C0/C1/C2/C3** × consumers **parity + report** × donor maps **offset 3** (the original, `SUMS[(i+3)%8]`) **and offset 1** (`SUMS[(i+1)%8]`; odd offset ⇒ parity flips, asserted per cell). Cluster = sum (n = 8); carriers averaged within sum; the C0/C1 and C2/C3 halves are reported separately as well as pooled. Conditions per (sum, carrier, consumer, map), all sustained block-output replacements:

| condition | positions written | layers | answers |
|---|---|---|---|
| `clean` | — | — | baseline |
| `C_own` | carrier ← own carrier state | ≥ 36 | self-patch gate (must be bitwise equal to clean) |
| `O_donor` | operand span ← donor | ≥ 36 | positive control (row 4 reference) |
| `C_full` | carrier ← donor carrier, operand span asserted untouched | ≥ 36 | the original transport condition |
| `C_all` | carrier ← donor carrier, operand span asserted untouched | **all 64 blocks** | row 2: removes the "layers < 36 still recipient" objection |
| `C_rand` | carrier ← own + per-position norm-matched isotropic write | ≥ 36 | non-specific control |
| `NEC` | operand span ← donor **and** carrier ← own (clamped) | ≥ 36 | row 4: necessity complement |

Recorded on every forward: answer scores (logsumexp over surface forms, scored-argmax rule); J_NP z at interior positions (13 number words + 8 decoys); **RESID_P number axis** projections at interior positions (Appendix C number templates, fit 1–4, validate 5–6, fitted in this run; presence direction per sum word = unit(μ_w − decoy centroid) with centering constant; pair axis per map = unit(μ_donor_sum − μ_own_sum)); **LOGITS** at interior positions (mean log-prob of the 21 column words); carrier ΔNLL; **answer-position residual distance from clean per block** (‖h_cond − h_clean‖ and ‖h_clean‖, 64 values) — row 3; mean write norms and read-back error for the carrier writes.

**Endpoints and predictions (on record).**
1. *Row 1, instrument-independence of the premise.* Internal shift z(donor sum) − z(own sum) minus clean at L51–59 under C_full vs O_donor on J_NP (expect ratio ≈ 1 as before), and the same contrast on the RESID_P pair axis and on the interior LOGITS margin. Prediction: all three agree the donor sum is installed under C_full at ≥ 0.8 of the O_donor level. If RESID_P or LOGITS show < 0.5, the premise is J-specific and §10 must be reframed.
2. *Row 2, full-depth carrier.* C_all flips: prediction 0/16 per carrier pair with margin < 25 % of O_donor. If C_all flips ≥ 8/16 on report, the block-36 cut was carrying the null and §10's dissociation is withdrawn as stated.
3. *Row 3, does the consumer see it.* Answer-position distance by block. Prediction: C_full and C_all perturb the answer position by at least half as much as O_donor at the late blocks (≥ 51). If C_full's perturbation is < 10 % of O_donor's, the licensed claim shrinks to "the carrier is not consulted by this consumer", not "consulted and discounted".
4. *Row 4, necessity complement.* NEC flips report ≥ 14/16 and parity ≥ 10/16 (as O_donor); carrier readout under NEC stays at the own sum (internal shift within ±0.3 of 0). If NEC does not flip, the carrier clamp is doing work and the operand route is not sufficient on its own.
5. *Row 5, materials.* C2/C3 and the offset-1 map reproduce the C0/C1 offset-3 pattern (O_donor flips, C_full 0 flips, C_full margin < 25 % of O_donor). Any half that diverges is reported as a materials dependence, not averaged away.
6. Damage: carrier ΔNLL ≤ 0.02 under every write; C_own bitwise.

**Decision.** All six survive ⇒ the dissociation is cited as instrument-independent and materials-robust, scoped to consumers with the operand tokens visible. Any of 1, 2 or 4 fails ⇒ §10 is rewritten before anything is built on it; 3 fails ⇒ scope wording changes. Budget: 8 × 4 × 2 × (2 + 2 × 6) = 896 forwards, plus the number-axis fit (21 words × 6 templates = 126 short forwards).

## Amendment 3 — bridge to the paper's clamped swaps, decision-position swap, token-level operand control, consistent global clamp, first route-restriction pass (registered 2026-09-09, before any forward)

**Why.** An external critique of the repository (2026-09-09) raised two objections the robustness battery does not answer: (a) the donor's *late operand residuals* may already contain the computed sum, so "the answer follows the operand donor" does not by itself show recomputation from the numbers; (b) donor carrier + recipient operands is a *conflicting* state no clean run contains, so the consumer's preference for the source could be conflict resolution rather than natural non-use. Two further questions decide how the result relates to the workspace paper: the paper's swaps were clamped over all positions in a band (source included) and were coordinate swaps along lens directions, not full residual replacements; and the paper's claim concerns the representation at the decision positions, which no condition here has touched. Finally, a first route-restriction pass tests whether the carrier copy is consulted more once the consumer's direct attention read of the operands is closed — with the GatedDeltaNet channel and the sub-band attention reads explicitly reported as open.

**Stage `global`** (`computed_sum_consumer.py global`): 8 sums × C0–C3 × parity + report, donor map offset 3, cluster = sum. Per cell: `clean`, donor forward, and

| condition | what is written | positions | layers |
|---|---|---|---|
| `O_donor36` | operand span ← donor | span | ≥ 36 (reference, as before) |
| `O_donor0` | operand span ← donor | span | **all 64** (token-equivalent operand change) |
| `C_full` | carrier ← donor | carrier | ≥ 36 (reference) |
| `G_full` | operands **and** carrier ← donor (consistent global state) | span ∪ carrier | ≥ 36 |
| `G_swap_all` | coordinate swap along the two sum-word naming directions a_v = J_l^T(γ⊙w_v) (own ↔ donor sum) | every position from the operand span to the end of the sequence | 36–62 |
| `G_swap_carrier` | same swap | carrier only | 36–62 |
| `D_band` | decision positions ← donor (second user turn + answer position) | [carrier_end, T) | 36–50 |
| `D_band_early` | same | same | 36–43 |
| `mask_clean` | attention read block: consumer queries (positions ≥ carrier_end) cannot attend operand-span keys | — | all 16 full-attention blocks |
| `mask_C_full` | block + carrier ← donor (≥ 36) | carrier | — |
| `mask_O_donor36` | block + operand span ← donor (≥ 36) | span | — |

Recorded per forward as in `robust` (scores, J_NP z, RESID_P projections, LOGITS, answer-position distance, ΔNLL, write norms), plus the per-layer maximum attention leak under the mask and the realized swap norms.

**Predictions (on record).**
1. `O_donor0` flips report 32/32 with margin within ±20 % of `O_donor36`. If `O_donor0` is much larger, the late operand residuals were carrying less than the token change does; if smaller, they carried more (computed content) — either way reported.
2. `G_full` flips 32/32 with margin ≥ `O_donor36`; if `G_full` − `O_donor36` ≈ `C_full` (additivity holds in the consistent state), the conflict objection loses force.
3. `G_swap_all` moves the report margin > 0 (8/8) and flips ≥ 8/32 (the paper's two-hop swaps succeeded 54–70 % at α = 1 on a different task; no closer prior). `G_swap_carrier` ≤ 25 % of `G_swap_all`'s margin. If `G_swap_all` fails to move the answer, the paper-style swap does not transfer to this organism and the bridge claim is withdrawn.
4. `D_band` flips ≥ 16/32; `D_band_early` uncertain. A flip here bounds where a full donor works; it does not identify a mechanism (the donor's decision-position states may already encode the donor answer).
5. Mask: `mask_clean` competence must be ≥ 0.9 on both consumers or the mask rows are reported as uninterpretable. Leak < 1e-3 at every masked layer. If competent: `mask_O_donor36` still flips ≥ 16/32 (recurrent channel carries operand content); `mask_C_full` margin exceeds unmasked `C_full` (carrier consulted more when the direct read is closed) — the discriminating row; no prior on whether it flips.
6. Damage: carrier ΔNLL ≤ 0.02 for every non-mask write (the mask acts after the carrier, so carrier NLL is unaffected by construction).

Budget: 8 × 4 × 2 × 13 = 832 forwards. Two-hop organism (paper case study 5) is a separate stage with its own competence and natural-readability gates; not part of this amendment.
