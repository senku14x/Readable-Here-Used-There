# H1 · early_late_mapping — does the availability of a mapping change whether the carrier expresses X or F(X)?

**H1.9, §2.6 (codebook query), B3 (letters), Appendix C (letter templates).** Script `H1/scripts/early_late_mapping.py` (stages `competence`, `pilot`, `anticipation`); analysis `early_late_mapping_analysis.py`. Status: design, registered before any forward.

## 1. Setup (exact)

S = the controlled single-word maintain prompt (`Here is the word "{X}". Keep that word in mind while you copy the following text exactly, word for word:\n\n{carrier}`); mention arm as a secondary row. B = `Code: {codebook}.` where the codebook is a comma-separated permutation of `word = letter` over **8 candidate words** (the evaluation bank half containing X: Bank 1 words 1–8 or 9–16, etc., fixed groups of 8 by bank order) and the 8 letters `B, D, F, H, K, M, Q, V` with a seeded injective assignment; entry order permuted independently of letter assignment; the realized mapping saved per trial. Q = `Using the code, what is the letter for the word introduced in the first message? Answer with the letter only.` A = `After this passage, you will use a code to answer a question about the introduced word.`

| Condition | User turn 1 | Assistant turn | User turn 2 |
|---|---|---|---|
| Early | `B\nS` (`B\nA\nS` with anticipation) | carrier (teacher-forced) | `Q` |
| Late | `S` (`A\nS`) | carrier | `B\nQ` |

Rendering via `rendering.render(..., extra_turns=[(Q_text, "")])`; the answer position is the last token. Letter token: verify `tok(" B")` vs `tok("B")` at the actual answer prefix (the assistant turn starts fresh; take whichever single token the model's own greedy answer uses in the competence stage, and score that id). Two mappings per word (seeds 1, 2); 32 evaluation words; carriers C2, C3. Cluster = word (n = 32); mappings are repetitions.

## 2. Stages

**`competence`.** Greedy decode ≤ 3 tokens at the answer position for every (word, mapping, condition, carrier); parse exact letter strings. Gate: accuracy ≥ 0.9 in both early and late, maintain arm. If late < 0.9, the query is not a competent consumer here; the mapping experiment is still readable during the carrier but the "late use" branch is unsupported. Also decode a **referent check**: the plain word query `Which word were you asked to keep in mind at the start? Answer with the word only.`

**`pilot`** (no A). During the carrier (interior positions), read: s_X (word presence, J_NP; RESID_P word axis from `natural_modulation/resid_axis.npz`), s_F(X) (letter presence: lens column of the mapped letter minus mean of the 7 other codebook letters — all equally present in the early prefix, mention control 3; and a **letter RESID axis** fit from `materials.LETTER_TEMPLATES` fit/val, one-vs-other-letters), plus full-vocab rank of X and of F(X). Endpoints E_X = s_X^late − s_X^early, E_F = s_F(X)^early − s_F(X)^late. Control 1: two early runs with different codebooks but the same prefix up to S are *not* identical prefixes (the codebook precedes S), so the permutation prior is the test: F(X)'s letter must beat the other 7 letters present in the same codebook; a letter-presence effect that does not depend on the assignment is codebook priming. Control 4: the same codebook with source X vs its pair partner Y (both in the codebook) — source-conditioned letter contrast F(X) vs F(Y).

**`anticipation`.** Repeat the pilot with A in both arms (separately labelled; never pooled).

## 3. Predictions and readings

| Observation | Reading |
|---|---|
| E_X > 0 and source-conditioned E_F > 0 (letter of X beats the letter of Y under the same codebook) | Consistent with specialization: early mapping availability shifts the carrier toward F(X) and away from X. |
| E_F > 0 but not source-conditioned (F(X) and F(Y) letters rise alike) | Unselective codebook priming; not transformation. |
| E_X ≈ 0 and E_F ≈ 0 with competence ≥ 0.9 | This manipulation does not establish representational reorganization; state as a scope result. |
| Only J_NP moves, RESID axes flat | Instrument-selective; not licensed without further validation. |
| Both X and F(X) rise early | Richer representation, not a zero-sum budget . |

Cluster-t over 32 words; the two windows Holm; the letter endpoint reported with its permutation-prior baseline (mean over the 7 other letters) shown.

## 4. Decision rules

- Competence gate first; a failed gate is reported and the pilot still runs for the carrier endpoints (they do not need the answer).
- Any E_F claim must survive control 4 (source-conditioned); otherwise it is priming.
- Ordering robustness (`A\nS\nB`) only if E_F > 0 survives.
- No claim that late use requires retained carrier information: that is the H2/H3 boundary experiment.

## 5. Budget

Competence: 32 × 2 mappings × 2 conditions × 2 carriers × 2 arms = 512 forwards (+ decoding). Pilot: same forwards recorded (the competence forwards can be the pilot forwards if all-layer recording is on: do that, one run). Anticipation: another 512. Letter axis: 8 letters × 6 templates. ≈ 1,100 forwards total.

## Amendment 1 (2026-09-07, before any forward) — length-matched control + source-conditioned central estimand

Adopted before outcomes (external review): raw E_X = s_X^late − s_X^early conflates transformation with a generic long-prefix effect (early puts a large codebook before the carrier; this project has measured cross-sequence-length readout sensitivity). Fixes:

1. **Add `early_unusable`:** an early condition whose codebook is over 8 *other* words (a different bank group of 8, so X is absent and unmapped), **length/structure-matched** to `early_usable`. The usability contrast **E_X^usability = s_X^{early_usable} − s_X^{early_unusable}** isolates the mapping-availability effect on X's readability from the generic prefix effect; raw late−early is reported but not load-bearing.
2. **Central estimand = source-conditioned letter contrast** (mention control 4): under the *same* usable codebook, **E_F^sc = s_F(X) − s_F(Y)** (X's mapped letter vs its pair-partner Y's letter, both present in the codebook). E_F^sc > 0 during the carrier is the transformation signal; a letter-presence effect that is not source-conditioned is codebook priming. Conditions this run: `early_usable`, `early_unusable`, `late` (anticipation deferred). Letter presence on J_NP (letter column minus mean of the other 7 codebook letters) and LOGITS; RESID letter axis deferred. Cluster = word (n=32), mappings are repetitions.
