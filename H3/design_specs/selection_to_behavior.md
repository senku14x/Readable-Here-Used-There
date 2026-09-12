# H3 · selection_to_behavior — does the instruction-region state that redirects the internal source profile also redirect the answer?

**H3 first pilot (selection to behaviour).** Script `H3/scripts/selection_to_behavior.py` (stages `smoke`, `pilot`, `evaluate`); analysis `H3/scripts/selection_to_behavior_analysis.py`. Outputs `H3/outputs/selection_to_behavior/`; results `H3/results/selection_to_behavior.md`. **Status: registered design v2, nothing run.** Revised 2026-09-07 after an adversarial review of v1 (recorded at the bottom). The §9 gain panel is **removed** to a follow-up (`selection_by_gain.md`), for the reasons in the review.

---

## 1. Question and the two endpoints, in order

H1 established at the readout that transplanting the instruction-region states from a pointed-B run into a pointed-A run redirects both the natural source-presence profile (~0.77) and the causal source-transfer profile (~0.74), target-specifically, with norm-matched controls at ~0 (`selection_localization_{transfer,random_control}.md`). Everything there is a lens readout. This experiment puts a codebook consumer on the **same forwards** and asks whether that state redirects **the answer**.

Two endpoints, run and interpreted in this order:

- **Primary — direct answer redirection (no source replacement).** The behavioral analogue of natural presence (H1 step 1A). Does the model, after a B→A instruction-region transplant with the visible tag still A, answer **B's** codebook letter?
- **Secondary — source-sensitivity profile.** The behavioral analogue of causal transfer (H1 step 1C): does the transplant change which source's block-36 replacement drives the answer?

v1's error was making the secondary the primary. A clean restoration on source-sensitivity could hold without the model ever actually choosing the transplanted target. Measure the direct choice first.

## 2. Hypotheses and what each outcome licenses

A behavioral redirect here does **not** identify the route. The transplanted instruction state precedes the carrier; it can reach the answer by causing later attention to re-read the *source words*, entirely bypassing the carrier representation. "Separate routes" and "carrier mediation" both predict a redirect. This experiment cannot separate them; `consumer_boundary_and_rescue` (§6) is where that is tested.

| Observed | Licensed interpretation |
|---|---|
| Transplant redirects the direct noswap answer **and** the source-sensitivity profile, target-specifically, above the matched control | patching instruction-region states influences both the selection readouts and this consumer's answer (route unidentified) |
| Transplant redirects the readout but **neither** behavioral measure (equivalence passed, controls adequate) | a scoped readout/behavior dissociation on this consumer, boundary and dose |
| Transplant redirects the direct answer but **not** the source-sensitivity profile | answer selection changed; the source-routing account is not the mechanism |
| Source-sensitivity profile shifts without actual answer switches | relative-score changes without demonstrated behavioral takeover |
| Matched-control instruction write redirects the answer as much as B→A | the effect is not donor-specific; any instruction-region perturbation moves the answer |

## 3. Organism and exact strings

Turn 1 unchanged from H1 (so the internal effect is the established one):

```
Here are three words: (A) "{X0}", (B) "{X1}", (C) "{X2}". Keep the word tagged {T} in mind while you copy the following text exactly, word for word:

{carrier}
```

Assistant turn: the carrier, teacher-forced. Turn 2, appended via `rendering.render(..., extra_turns=[(codebook + "\n" + query, "")])`:

```
Code: {w1} = {L1}, ..., {w6} = {L6}.
Using the code, give the letter for the word you were instructed to keep in mind. Answer with the letter only.
```

**Frozen query wording:** the `instructed` variant (all three calibrated wordings scored 1.00; `H3/results/consumer_competence.md`). Record the choice; do not re-open it. (No claim that this wording defeats a tag-extraction shortcut — the consumer can still recover the tag from the prompt; that is what the boundary work, not the wording, addresses.)

**Codebook.** Six entries: the three sources **and their three donors**, so both endpoints have defined counterfactual answers. Letters from `B D F H K M Q V`; letter assignment and entry order permuted independently of each other and of identity, seeded per cell (`SEED=20260907`, key `SEED+1000*triple+100*rot+carrier`). Save the realized assignment.

## 4. Materials and exposure

- **Pilot: triples 0–1, carriers C0/C1.** These identities were already exposed in the consumer competence calibration (competence readout only — no fitting, no intervention, no endpoint examined). Fine for a gate-checking pilot; disclosed.
- **Evaluation: triples 2–7, carriers C2/C3.** Six triples, fresh identities, held-out carriers. **n = 6, extension scale, disclosed** (dropping the two exposed triples is the honest cost of the calibration). Three cyclic rotations each; rotations and carriers averaged within triple before any interval. Cluster = triple.
- Donor map: source slot j of triple i takes slot j of triple (i+1) mod 8, the same map as `selection_localization` transfer, so internal rows are directly comparable.

## 5. Conditions

Sustained block-output replacement from block 36 onward, applied to the recipient's own rendering (visible text identical across conditions).

**Arms.** `cleanA`, `cleanB`, `cleanC` (ceilings); `BtoA`, `CtoA` (instruction-region transplant, positions `[tag_token, end of user turn)`, donor states from the token-aligned pointed-B/C run); `randA` (**matched behavioral control**: a norm-matched isotropic write over the same region, per-(layer,position) scaled to the B−A donor delta norm, seeded — the `random_control` construction from H1, now scored behaviorally); plus the `AtoA` self-patch no-op gate.

Accurate description of the intervention: this **replaces the entire instruction-region state**, which may carry several instruction-related computations, not a uniquely isolated "pointer." The warranted claim from a positive result is "replacing these instruction-region states redirects the answer," scoped as such.

**Source conditions per arm.** `noswap` (→ primary endpoint); `swap0`, `swap1`, `swap2` (→ secondary profile). The matched control also gets all four.

## 6. Endpoints and measurement, from the same forwards

Let `F` be the cell's codebook and score every letter's log-prob at the answer token (last position), in both surface forms, taking the better form per letter.

**Primary — direct redirect (noswap only).**
```
q_D = log P(F(X_D)) − log P(F(X_A))        for donor slot D ∈ {B(=1), C(=2)}
E_D = q_D(DtoA, noswap) − q_D(cleanA, noswap)
ceiling  Δ_D = q_D(cleanD, noswap) − q_D(cleanA, noswap)      (> 0 by construction: cleanD answers D)
```
`E_D > 0` is the redirect toward the transplanted target. **Primary statistic: raw E_B, E_C, cluster-t over triples.** Normalized restoration `E_D/Δ_D` reported as a **ratio-of-means with paired bootstrap** (numerator and denominator shown), conditional on `Δ_D` being CI-clear positive; **per-cell ratios are never averaged** (they blow up where `Δ_D` is small). Also report the matched-control `E_D(randA)`.

**Answer classification (replaces accuracy/damage as the specificity read).** For every intervened cell, classify the greedy decode into: (i) original target A's letter; (ii) transplant target D's letter; (iii) swapped-in donor's letter (secondary conditions only); (iv) another valid letter; (v) invalid (non-letter). Report the distribution per arm. Answering D after DtoA is the *intended* effect, not an error; carrier top-1 retention and ΔNLL are supporting checks only, never the specificity claim.

**Secondary — source-sensitivity profile.** J_NP `m_j = z_{donor_j} − z_{X_j}` at carrier interior (both windows) and its behavioral analogue `b_j = log P(F(donor_j)) − log P(F(X_j))`; `C_j^R = m_j(swap j) − m_j(noswap)`, `C_j^B = b_j(swap j) − b_j(noswap)`. Restoration of the transfer profile `P=(C_0,C_1,C_2)` toward the clean-D ceiling, **computed per cell then clustered** (state this aggregation order), reported only where the clean A→D profile separation `‖P_D − P_A‖` is itself CI-clear; raw three-vectors shown whenever restoration is undefined or unstable. This is the direct analogue of H1 1C, now on both sides.

**Internal companion.** All internal readouts (`C_j^R`, natural presence, the transplant's internal restoration) are computed on the identical forwards, reproducing H1's magnitudes as a within-experiment anchor.

## 7. Gates (before any outcome is read)

1. Rendering: three quoted source spans, both carrier occurrences, appended turns, answer = last token, all decoded and asserted.
2. `tag_position` is the unique differing token across the three arm renderings; source spans precede it.
3. **Reproducibility of the clean carrier readout.** Assert the carrier-interior token ids and positions are identical to the no-appended-turn rendering, and that the clean-arm carrier-interior `z` is **bitwise identical** to the `selection_localization` transfer run for the same triple/rotation/carrier. This proves the appended turns do not leak backward (a deterministic causal decoder cannot let them). If it fails, the cause is tokenization/positions/hooks/masking/precision — **fix that before interpreting anything**, do not read it as a change in the phenomenon.
4. Same-source swap0 bitwise equal to clean; `AtoA` self-patch bitwise no-op; layers < 36 identical between futures.
5. Donor geometry: identical token count and span indices.
6. Realized writes on every non-clean move: ρ ∈ [0.9, 1.1], κ ≥ 0.99.
7. Competence context: clean greedy answer is the pointed word's letter (calibration: 1.00). A clean cell failing this is reported, not dropped. Accuracy is **not** an intervention endpoint (see classification).

## 8. Predictions

| Quantity | Shared selection reaches the consumer | Readout/behavior dissociation | Nonspecific |
|---|---|---|---|
| internal transplant restoration | ~0.7 (reproduces H1) | ~0.7 | — |
| primary E_B, E_C | > 0, CI-clear | equivalent to 0 (band below) | erratic / negative |
| answer class under BtoA | mostly D's letter | mostly A's letter | mostly invalid / other |
| matched control E_D(randA) | ≈ 0 | ≈ 0 | ≈ E_D(BtoA) → not donor-specific |
| secondary C_j^B profile | redirects toward D | flat | collapses |

**Primary registered contrast:** raw E_B and E_C above the matched control `randA`, cluster-t over the 6 evaluation triples, with the answer-class distribution.

## 9. Decision rules

- **E_D CI-clear > 0, above randA, with D's letter the modal answer** → selection reaches this consumer (route unidentified). Next: `consumer_boundary_and_rescue` (§6) or `same_content_different_consumers` (§7).
- **Internal restoration ~0.7 but E_D equivalent to 0** → licensed dissociation. Equivalence test: the 90% interval of E_D lies within ±ε, ε = 0.2 × the clean separation `Δ_D` (stated directly, not via any "behavioral-scale analogue"). With n = 6 this interval may not close; if it does not, report **inconclusive**, not null. Then check that a *source* replacement moves the answer at all in these cells (it should, by the swap conditions) — this establishes source-path manipulability but **does not exclude re-reading**, because modifying source states *is* a re-read path.
- **Gate 3 fails (clean z not reproduced)** → an implementation fault, not a phenomenon change; fix tokenization/hooks/masking first.
- **randA redirects as much as BtoA** → not donor-specific; report and stop before any mediation claim.

## 10. Budget

Per cell forwards: 3 donor-source renders + cleanA/B/C (4 each = 12) + BtoA/CtoA (4 each = 8) + randA (4) + self-patch (1) = **28**. Evaluation = 6 triples × 3 rotations × 2 carriers × 28 = **3,024**. Pilot = 2 × 3 × 2 × 28 = **336**. At ~0.55 s/forward with all-layer recording, evaluation ≈ **28 min**, pilot ≈ 3 min. **The primary endpoint uses only the noswap forwards** (7 per cell: 3 clean + 2 transplant + 1 rand + 1 self), so an even cheaper primary-only pilot (~7 × 12 = 84 forwards) can precede the profile.

## 11. Implementation notes

- Base on `H1/scripts/selection_localization.py` stage `transfer` (instruction transplant × source replacement, geometry/identity asserts) and `H3/scripts/consumer_competence.py` (letter ids in both forms, seeded codebook). Add the appended turns and answer scoring; add the `randA` arm from `selection_localization.py` stage `random_control`.
- Do not import an H1 runner from an H3 runner; lift shared pieces into `common/`.
- Save per cell: `z` (all layers, carrier interior), `p_pair{j}`, the eight-letter score vector, greedy token id, `nll`, `top1`, realized-write stats, codebook assignment.
- Report: internal-vs-behavioral profile figure; per-triple paired points; seeded random qualitative cells with the exact prompt, codebook, intervention, top readouts, letter probabilities and generated answer, and the answer classification.

## 12. What this experiment cannot claim

That the **carrier** representation mediates the answer (the transplant precedes the carrier; §6 territory). Anything about other consumers, categories, sums, policies, or the released directed-modulation prompts. A behavioral null is scoped to this consumer, boundary and dose; it is inconclusive unless the equivalence test passes with the source-swap conditions showing the answer is movable at all, and even then it is a dissociation on this consumer, not "J-space is not used."

---

## Review log — v1 → v2 (adversarial critique, all accepted unless noted)

1. **Primary endpoint changed** to the direct noswap redirect (E_B, E_C); source-sensitivity profile demoted to secondary. v1 answered "does sensitivity to later replacement move," not "does the answer move."
2. **Hypothesis table corrected:** routes are not mutually exclusive — a transplant can redirect behavior via source re-reading without carrier mediation; a redirect never identifies the route.
3. **Matched behavioral control added** (`randA`, norm-matched instruction-region write). H1's random_control validated the internal endpoint only. Intervention described accurately as full instruction-region-state replacement, not a uniquely identified pointer.
4. **Restoration/equivalence fixed:** raw E_D primary; normalized restoration as ratio-of-means (never per-cell ratios averaged); restoration reported only where the ceiling separation is CI-clear; equivalence band stated directly as 0.2 × Δ_D with the n=6 caveat that it may not close.
5. **Two decision rules fixed:** clean-readout non-reproduction is an implementation fault to debug, not a phenomenon change (added as bitwise gate 3); a source replacement moving the answer does **not** exclude re-reading.
6. **Damage → answer classification** (original / transplant-target / donor / other-valid / invalid). Bare-letter rate and accuracy-vs-visible-instruction do not establish specificity.
7. **Gain panel removed** to `selection_by_gain.md`: ΔC_j/C_j is unstable near zero, and a behavioral gain effect would qualify H1's scope, not contradict its internal result.
8. Smaller: deleted the "avoiding the word tagged defeats a shortcut" justification; disclosed that pilot triples 0–1 were exposed in calibration and moved evaluation to fresh triples 2–7; require verifying letter-scoring against actual greedy output; corrected the budget (28 forwards/cell, ~3,024 evaluation, not 3,456).

## Amendment 1 — implementation corrections (2026-09-07/08, after pilot+evaluate v1 and two independent audits)

Applied before the numbers were promoted, driven by my audit (`H3/results/audit_selection_to_behavior.md`) and the researcher's independent audit (`H3/audits/selection_to_behavior/AUDIT.md`). The v1 raw archives (`raw_{pilot,evaluate}.npz`) are preserved; the corrected run writes `*_v2` outputs.

1. **Letter scoring is logsumexp over surface forms, not max.** The battery now saves the full per-letter per-form log-probs `llp[8,2]`; the analysis combines the two forms by `logaddexp` (deduplicated probability mass). Effect on the pilot is negligible (Δ ≈ 0.005 nats, one surface form dominates), but the archive now supports the correct score directly.
2. **`randA` → per-target `randB` and `randC`.** v1 had a single isotropic control norm-matched to the B→A delta (14% too small a match for C→A) and stored `rho=1.0` as a hardcoded placeholder. v2 builds `randB` scaled to `‖h_B−h_A‖` and `randC` scaled to `‖h_C−h_A‖`, and measures the **realized** write norm and read-back error per arm from the run (observed ρ ≈ 1.0002, read-back error 0.0 — `SpanWriter` overwrites exactly).
3. **Secondary donors rendered with the consumer turn (matched length).** v1 harvested source-donor states from length-101 turn-1-only renders and wrote them into length-166 consumer runs (~1% relative contamination). v2 renders donors with the consumer appended so donor and recipient lengths match (confirmed 152=152 in smoke; the primary noswap endpoint never used donor source states and is unaffected).
4. **`selfpatch` bitwise gate recorded** per cell (`AtoA` no-op verified bitwise, 12/12 pilot).
5. **Clustering is by triple** (rotations and carriers averaged within triple first), as the project conventions always required; the v1 analysis had clustered over cells (pseudo-replication). Point estimates unchanged, intervals widen.
6. **Reporting rule (both audits):** the crossed source-margin table is reported as an **observation** of margin shifts only. No causal specific/non-specific decomposition is drawn from it, and the with/without-consumer z offset is described as a length-dependent linear-attention kernel effect (independently checked: an equal-length different-content suffix gives 0.0 residual at every block; the specific kernel mechanism is left provisional) that cancels in the with-consumer contrasts.

## Amendment 2 — carrier-only donor on the word organism (registered 2026-09-09, before any forward)

**Why.** The word organism and the sum organism (`computed_sum_consumer.md` §10, Amendment 2) currently agree in direction under *different* intervention shapes: the word result is a full pointed-source donor (0/36 flips) and an instruction-region transplant (2/36), the sum result a carrier-only donor. To make them a matched pair, the word organism gets the carrier-only condition.

**Stage `carrier_only`** (`selection_to_behavior.py carrier_only`), evaluate materials: triples 2–7, carriers C2/C3, three rotations (36 cells), consumer appended, cluster = triple (n = 6). Conditions on the pointed-A recipient, sustained block-output replacement over the **assistant-carrier positions** [carrier_start, carrier_end) only; the instruction region and the source spans are never written and are asserted unchanged:

| condition | source | layers |
|---|---|---|
| `cleanA/B/C` | — | — |
| `CarrOwn` | own carrier state | ≥ 36 (self-patch gate, bitwise) |
| `CarrBtoA`, `CarrCtoA` | pointed-B / pointed-C run's carrier states (same tokens, teacher-forced) | ≥ 36 |
| `CarrBtoA_all`, `CarrCtoA_all` | same | all 64 blocks |
| `randCarrB` | own + per-position norm-matched isotropic (matched to CarrBtoA) | ≥ 36 |

Recorded: letter log-probs (both surface forms), greedy answer, J_NP z at interior positions (3 sources, 3 donors, 8 decoys), carrier ΔNLL, answer-position residual distance from clean per block, write norms / read-back error.

**Endpoints and predictions.** Internal presence restoration R along the clean A→donor profile axis at L51–59 (expect ≥ 0.7, since the carrier states are the donor's own); behavioral E_D = q_D(CarrDtoA) − q_D(cleanA) against the clean ceiling Δ_D; greedy flips. Prediction: R ≥ 0.7 with E_D/Δ_D < 0.25 and flips ≤ 3/36, the same shape as the sum organism. If E_D/Δ_D ≥ 0.5 or flips ≥ 12/36, the carrier representation *is* consumed by the word consumer and the two organisms disagree; that is reported as a disagreement. Budget: 36 × 9 = 324 forwards.
