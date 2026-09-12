# H1 · computed_sums — does a computed value (the sum) transfer, or only its addends?

**The computed-sum organism (H1.8) with the frozen sum materials.** Script `H1/scripts/computed_sums.py` (stages `arithmetic`, `natural`, `transfer`); analysis `computed_sums_analysis.py`. Status: design, registered before any forward.

## 1. Question

With `Here is the pair "{a} and {b}". Keep their sum in mind while you copy…`, is the sum word readable at the carrier, and when the pair span is replaced from block 36 by a **different-sum** donor does the sum readout follow the donor, while a **same-sum sibling** donor (different addends, same sum) leaves the sum readout unchanged but moves the addend readout? Different-sum response with same-sum invariance = computed-output sensitivity. It does not decide whether the sum travels or is recomputed downstream .

## 2. Materials (B3, exact)

| Sum | A | Same-sum B |
|---|---|---|
| seven | two, five | three, four |
| eight | two, six | three, five |
| nine | two, seven | four, five |
| ten | two, eight | three, seven |
| eleven | three, eight | four, seven |
| twelve | four, eight | five, seven |
| thirteen | five, eight | six, seven |
| fourteen | six, eight | five, nine |

Check single-token status of every number word (leading-space form) and of the sum words; `thirteen`/`fourteen` may be multi-token — if so, that sum is ineligible for the sum-word lens endpoint and reported with the label-sequence caveat (the category member aggregate), not dropped silently. Donors: different-sum donor for row i = the A-addends of row (i+3) mod 8 (fixed before outcomes; geometry: `"{a} and {b}"` is 3 content tokens for all rows if every number word is single-token; assert). Same-sum donor = row i's B addends. Decoys for presence: the other 7 sum words (sum endpoint) and `FIT_WORDS[:8]` (addend endpoint). Carriers C2, C3 (and C0, C1 as fitting carriers for the RESID sum-word axis; number words get plain-template centroids like any word — templates "I saw a seven yesterday" are odd; use the `LETTER_TEMPLATES`-style label contexts instead: fit a small `NUMBER_TEMPLATES` list of 6 sentences with the slot in a numeric-word context, e.g. "The answer was {m}.", "She counted to {m}.", "The total came to {m}.", "He wrote {m} on the board.", "The final number is {m}.", "They stopped at {m}."; fit 1–4, validate 5–6; register in `materials.py` before running). Cluster = sum (n = 8).

## 3. Stages

**`arithmetic`.** `Here is the pair "{a} and {b}". Keep their sum in mind. What is their sum? Answer with one word.` greedy ≤ 3 tokens; exact approved strings (`seven`, `7` counted separately, both saved). Gate: ≥ 15/16 correct over A and B rows. A failure is retained; that row's transfer rows are then diagnostic only.

**`natural`.** Maintain vs control (`. That pair occurs one time. Now copy…`) vs absent on C2/C3 for A and B rows: sum-word presence s_J(sum) vs the 7 other sums; addend presence. Gate for the transfer stage: sum-word presence maintain − absent > 0 (≥ 6/8, CI clear) at either window; if the sum word is not readable at all, the transfer stage still runs but the sum endpoint is "instrument not validated".

**`transfer`.** Under maintain and control: clean, same-source gate, different-sum swap, same-sum swap; readouts: sum-word margin m_sum = s(donor sum) − s(own sum) (for the same-sum donor this is identically 0 by construction, so the same-sum row's sum endpoint is the **change in own-sum presence** Δs_sum), addend margin m_add = mean s(donor addends) − mean s(own addends), RESID sum axis, LOGITS.

## 4. Estimands, predictions, readings

C_diff^sum = m_sum(diff swap) − m_sum(clean); C_same^sum = Δs_sum(same swap); C_diff^add, C_same^add likewise; all under maintain and control; A = C_M − C_N for each.

| Observation | Reading |
|---|---|
| C_diff^sum > 0 (≥ 7/8) and C_same^sum ≈ 0 (equivalence ±20 % of C_diff^sum) while C_same^add > 0 | Computed-output sensitivity: the sum readout tracks the value, not the addends. |
| C_diff^sum > 0 and C_same^sum clearly ≠ 0 (own-sum presence drops under the sibling) | The sum readout is addend-driven; no evidence for a carried computed value. |
| C_diff^sum ≈ 0 with the natural gate passed | The sum readout is set before block 36 or by the instruction alone; report as a scope result. |
| Maintain > control on C_diff^sum (A > 0) | The instruction modulates transfer of the computed value, as it did for words. |

## 5. Decision rules

Gates in order (arithmetic, natural) before reading transfer; the same-sum invariance claim needs the equivalence band, not non-significance; no localization or native sum-state fit unless "travels vs recomputed" becomes the active uncertainty .

## 6. Budget

Arithmetic 16 short prompts; natural 16 rows × 3 conditions × 2 carriers = 96; transfer 16 × 2 arms × 2 carriers × (clean + same-source + 2 donors + 2 swaps) = 384; axis fits 16 number words × 6 templates. ≈ 600 forwards.
