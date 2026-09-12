# H3 · `late_mapping_identity_use` — does a source-absent carrier transplant supply an *identity* to a mapping revealed afterwards, or an answer?

**Registered 2026-09-09, before any forward.** Design due to an external review; adopted because it tests a confound in a claim the project already makes.

## 0. Rationale — corrected before any forward (2026-09-09)

**The rationale first registered here was wrong and is withdrawn.** It claimed that donor carrier states "were computed in a context where the eventual question already existed" and could therefore carry an answer tendency. Carrier positions precede the consumer turn and attention is causal, so the later question cannot influence them; the project's own implementation audit already established this directly, finding a maximum residual difference of **0.0 at every one of 64 blocks** for an equal-length different-content suffix (`H3/results/audit_selection_to_behavior.md`, check 1). The only cross-length effect on record is a numerical kernel offset, not an informational one. Recorded as an error rather than deleted.

**The real gap this experiment closes.** In the organisms where a source-absent transplant has been run, the consumer's answer *is* the identity: the sum organism's report consumer emits the sum word, and parity is a function of it. So "the transplant supplied the identity S" and "the transplant supplied the answer" are not separable there by construction, whatever the donor saw. The separation needs a consumer whose answer is **arbitrary with respect to the identity**, and a mapping revealed **after** the carrier so that the same transplanted state must serve two different correct answers. That is the word-codebook consumer with two counterbalanced codebooks, below. Harvesting donors under a neutral third turn is retained as a cheap belt-and-braces measure, not as the justification.

**A second gap, equally real.** Every source-absent positive in this project transplants **whole carrier residuals**, so "the readable representation is consumed" is not distinguished from "the whole carrier state is consumed". The ladder in §3 is the project's own H3.3 comparison and is the point of the experiment; the gate in §2 exists only to make the ladder interpretable.

## 1. Organism and the separation

Word-copy organism with the codebook consumer, whose clean lookup is competent at 1.00 (`consumer_competence.md`).

- **Recipient:** `Here is a word (hidden). Keep that word in mind while you copy …` — length- and span-matched to the donor rendering, asserted per cell.
- **Donor:** the same rendering with the word X (or Y) present.
- **The mapping is revealed only after the carrier**, in turn 2, and is **counterbalanced**: two codebooks `F1`, `F2` assign *different* letters to the same word (`F1(X) ≠ F2(X)`, both single-token, decoys re-lettered too). The identity is constant across the two mappings; the correct answer is not.
- **Crucially, donor states are harvested from runs rendered with a *third*, neutral turn** (`Answer with one letter.`), so the donor's carrier cannot have been computed in the presence of either codebook. This is the piece the existing absent-source runs lack.

If a transplant supplies the **identity**, the answer follows `F1(X)` under `F1` and `F2(X)` under `F2`. If it supplies an **answer tendency**, the answer does not track the mapping.

## 2. Gate first (tens of forwards)

**G1.** Full carrier transplant (all 64 blocks) from the X-donor into the hidden recipient — note this is also the **first source-absent test on the word organism**; the absent-source leg has so far run on the sum and two-hop organisms only, under both codebooks, 8 word pairs × 2 carriers: does the answer become `F1(X)` under `F1` **and** `F2(X)` under `F2`, against the hidden-recipient baseline and a matched-norm random carrier write? Require the mapping-appropriate letter to win the scored candidate set in ≥ 0.6 of cells under both mappings, and the random control at chance. **If G1 fails, stop**: source-absent *word*-carrier transfer is not established merely because the factual and arithmetic versions worked, and the component ladder below would be uninterpretable.

## 3. Ladder, only if G1 passes

At the **same positions and the same layer schedule** (all 64 blocks; no comparing an all-layer donor against a one-layer coordinate write): full residual donor; the J naming basis for X (top-k folded directions, k declared before running); the plain-sentence residual direction for X; a matched random subspace of equal dimension and norm. Endpoints as in G1, plus the installed-readout check (each component must actually move the X readout, or its behavioural null is uninterpretable).

Outcomes: a small component that works **under both mappings** is evidence that the intervention supplies information a later mapping can use; full donor works while an adequately-installed component fails is a controlled insufficiency result for that representation class; full donor fails ends the ladder at this boundary.

## 4. Predictions

1. G1: no prior. The hidden recipient's clean answer is at chance among the six letters.
2. If G1 passes, mapping-tracking is expected to be **partial**, in line with the factual absent-source result (28/40 and 32/40 against a 20/40 floor).
3. The naming-basis component is expected to install the readout but track the mapping worse than the full donor.

Budget: G1 ≈ 8 pairs × 2 carriers × 2 mappings × 4 conditions ≈ 130 forwards plus donors; the ladder roughly the same again.

## 5. What this cannot claim

Nothing about arithmetic (the sum codebook failed competence and is not reused here); nothing about consumption of a precomputed value; success would establish a narrower *identity-use* result for this consumer and boundary.
