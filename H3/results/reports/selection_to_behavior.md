# H3 · selection_to_behavior — does the instruction-region state that redirects the internal source profile also redirect the answer?

**Design:** `H3/design_specs/selection_to_behavior.md` v2 (+ Amendment 1). **Status: pilot + evaluate complete, audit-corrected (v2 run).** Model Qwen3.6-27B @ 6a9e13b, NP lens; consumer validated in `consumer_competence.md`. **All statistics cluster by triple** (rotations and carriers averaged within triple first; pilot = 2 triples / 12 cells, evaluate = 6 triples / 36 cells). Two independent implementation audits were run and their findings are incorporated here: mine (`audit_selection_to_behavior.md`) and the researcher's (`H3/audits/selection_to_behavior/`). Letter scores use logsumexp over surface forms; the two matched random controls are norm-matched per target (randB to B→A, randC to C→A) with realized write norm ρ = 1.0002.

## 1. Question and setup

H1 localized the tagged-selection pointer: transplanting a pointed-B run's post-tag prefix states (positions [tag, turn-1 assistant carrier) — the tag, the instruction tail, the user-side carrier and the turn delimiters) into a pointed-A run redirects the carrier's source readout by ~0.76 and the causal transfer profile by ~0.74, target-specifically. That is a lens readout. Here a codebook consumer sits on the **same forwards**: turn 2 gives a six-word code (three sources + three donors) and asks "give the letter for the word you were instructed to keep in mind."

Primary endpoint (no source replacement): `E_D = q_D(DtoA) − q_D(cleanA)`, `q_D = log P(F(word_D)) − log P(F(word_A))` at the answer token, letters scored by logsumexp over both surface forms; ceiling `Δ_D = q_D(cleanD) − q_D(cleanA)`; matched control `randD` (norm-matched isotropic write over the same region, one per target); five-way answer classification. Secondary (evaluate): the source-sensitivity profile, internal and behavioral.

## 2. Findings — evaluate (triples 2–7 fresh, carriers C2/C3, 6 triples, 36 cells, 1,152 forwards)

**Organism gate passes.** Internal presence restoration with the consumer appended: **B→A +0.759 [+0.686, +0.833], C→A +0.716 [+0.674, +0.757]** (L51–59, 6/6); +0.553 / +0.516 at L48–50. Internal *transfer* restoration **+0.726 [+0.627, +0.826]** (B→A) / +0.675 (C→A). These reproduce H1's ~0.76 / ~0.74 on the identical consumer-appended forwards.

**The transplant moves the answer, by about a fifth to a quarter of the clean separation, and rarely flips it.**

| quantity | evaluate (6 triples) |
|---|---|
| E_B | **+3.32 nats [+2.72, +3.92]**, 6/6 |
| E_C | **+2.54 nats [+1.79, +3.29]**, 6/6 |
| matched control randB (on B) | +0.03 [−0.04, +0.09], 3/6 |
| matched control randC (on C) | +0.03 [−0.02, +0.08], 5/6 |
| E_B − randB | +3.29 [+2.66, +3.92], 6/6 |
| E_C − randC | +2.51 [+1.74, +3.29], 6/6 |
| ceiling Δ_B / Δ_C | +13.30 / +13.30 nats |
| behavioral restoration E_B/Δ_B, E_C/Δ_C | **+0.249 [+0.213, +0.295] / +0.191 [+0.159, +0.241]** |
| internal presence restoration (same forwards, L51–59) | **+0.76 / +0.72** |
| behavioral transfer restoration | +0.269 / +0.233, 6/6 |

The behavioral restoration is real: its interval excludes 0, is far above the matched control, and lies well below 1. The equivalence band (ε = 0.2 × Δ = 2.66 nats) does **not** contain E_B or E_C, so this is not a behavioral null — the answer does move — it is a partial redirect.

**Answer classification (greedy):** cleanA → A's letter 36/36; cleanB → B 35/36 (1 other); cleanC → C 36/36; **BtoA → A 34/36, B 2/36**; **CtoA → A 36/36**; randB → A 36/36; randC → A 36/36. The visible tag continues to determine the decode in all but 2 of 36 cells.

**Crossed source margins (observation).** How each transplant shifts each source's answer margin, triple-clustered:

| transplant | shifts B's margin | shifts C's margin |
|---|---|---|
| B→A | **+3.32** [+2.72, +3.92] 6/6 | +1.97 [+1.51, +2.44] 6/6 |
| C→A | +2.09 [+1.66, +2.52] 6/6 | **+2.54** [+1.79, +3.29] 6/6 |

Each transplant raises its own target's margin most, but also raises the off-target letter's margin. This is reported as an observation of the margin shifts; the report draws no causal decomposition of it into target-specific and non-specific components (both audits flagged that such a split is not licensed by these data, because B and C are both valid pointers and the two writes are not independent perturbations).

Pilot (triples 0–1, C0/C1, 2 triples, primary only) agrees: internal presence restoration +0.82 / +0.72; E_B +2.52 [+1.17, +3.87], E_C +2.17 [+1.05, +3.28]; randB +0.03, randC +0.00; no greedy flips (0/12). With only two clusters the pilot intervals are wide and are not treated as confirmatory on their own.

## 3. Reading (scoped)

A **quantified internal-versus-behavioral dissociation** on a contrast whose internal effect is beyond doubt. On the same forwards, the transplant redirects the carrier's source readout most of the way toward the donor (presence ~0.72–0.76, transfer ~0.68–0.73) while the consumer's answer margin moves only ~0.19–0.25 of the clean separation — a real effect (6/6, far above per-target norm-matched controls) that changes the greedy answer in 2 of 36 cells and only for B→A. The visibly pointed tag continues to determine the answer.

Two qualifications the audits enforced:

- **The route is not identified.** The transplant precedes the carrier. A redirect is predicted both by carrier mediation and by the transplant causing later attention to attend differently to the visible "(A) → word" mapping (positions before the tag, never patched); this experiment cannot separate them. Because the source words and the tag remain in context, an account in which the consumer's answer is driven mainly by that visible mapping rather than by the carrier representation is not excluded. Identifying the route is `consumer_boundary_and_rescue` (§6) territory, or a consumer whose answer cannot be recovered from the visible prompt (computed sum, category members).
- **The crossed table is observational.** Each transplant shifts both source margins; the data do not license a causal split of that into "specific" and "non-specific" parts.

## 4. Verification and limitations

Gates and diagnostics (all from the run): arms token-aligned (single differing position); source spans precede the tag; self-patch a bitwise no-op (36/36 evaluate, 12/12 pilot); patched positions receive donor states exactly (read-back error 0.0) with blocks < 36 untouched; consumer/answer tokens never patched; realized write norm ρ = 1.0002 for both matched controls (full-LGE-layer mean write norms: B→A 12.4, C→A 12.7, randB 12.4, randC 12.7; C→A / B→A = 1.02), κ effectively 1 by exact overwrite. Secondary source-donor states are now rendered with the consumer turn so donor and recipient lengths match (fixing v1's ~1% cross-length donor contamination). Full detail in `audit_selection_to_behavior.md`.

**The with/without-consumer z offset is a sequence-length effect, independently verified.** A with-consumer render (166 tokens) and a without-consumer render (101 tokens) differ in the carrier-interior residuals from block 0, but three controls locate the cause in sequence length alone, not information flow: an equal-length different-content suffix produces **0.0** residual difference at every block; an explicit all-ones attention mask versus the default reproduces the run **bit-for-bit** (0.0 at every layer), ruling out the mask; and the jlens wrapper execution path bit-matches the direct model path (0.0 at every layer), ruling out an execution-path artifact. All H3 conditions share length 166, so the offset cancels in every reported contrast. The specific bf16 linear-attention kernel mechanism behind the length dependence is not directly instrumented and remains provisional; that it is length-driven is verified.

Limitations: 6 triples (extension scale); one consumer, one boundary (block 36), one dose; the patched region is a post-tag prefix that includes the user-side carrier and delimiters, not the instruction alone; the route is unidentified (§3); different instruments on the same forwards are robustness, not independent samples. The earlier pilot predicts a block-36 boundary positive control is weak on a word-codebook consumer, because its letter answer tracked the source span's layer 23–35 content (earlier calibration notes).

## 5. Next decision

The licensed claim: **on this consumer, the readable selection state is redirected most of the way toward the donor while the answer margin moves about a fifth to a quarter of the clean separation and the greedy answer almost never changes; the shift tracks the transplanted content (it is null under per-target norm-matched writes) but its route is not identified.** Whether the *carrier* representation mediates the residual behavioral effect needs a consumer whose answer cannot be read off the visible prompt: the computed-sum or category-member codebook (`consumer_boundary_and_rescue`, §6). That is the informative next H3 step; a dose/boundary sweep on this consumer is the cheaper alternative.

## 6. Carrier-only donor (Amendment 2, 2026-09-09)

`selection_to_behavior_carrier_only.md` (324 forwards, 36 cells, cluster = triple n = 6). Replacing only the assistant-carrier states with the pointed-B / pointed-C run's states (≥ 36 or all 64 blocks; instruction region and sources untouched; self-patch bitwise 36/36) moves the letter margin by 0.012–0.042 of the clean separation (+0.16 to +0.56 nats, 6/6, matched random +0.02) and flips 0/36 greedy answers. The instruction-region transplant of §2 moved it 0.19–0.25, so that residual effect was not carried by the carrier representation; the remaining candidate is later attention onto the transplanted instruction positions. Together with the sum organism this makes a matched pair: the lens-readable carrier representation, installed at the donor level, is not what either consumer answers from while the visible source is available.
