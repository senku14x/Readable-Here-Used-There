# Audit — H3 `computed_sum_consumer` (competence → calibration → boundary gate → transport test)

**Audit date:** 2026-09-08. **Target pinned:** commit `dfb949c` (report `H3/results/computed_sum_consumer.md` §§1–10; design + Amendment 1; battery `H3/scripts/computed_sum_consumer.py`; archives `H3/outputs/computed_sum_consumer/`). **Auditor:** the researcher, model-assisted, after the session that produced the results.

**Method.** `recompute_saved.py` re-derives every headline number from the committed `raw_*.npz` / `meta_*.json` archives. It imports **nothing** from the runner, and applies **one** scoring rule throughout — `argmax over candidate words of logsumexp(log-probs of single-token surface forms)`, the rule the report's competence gate used — so any inconsistency in what was reported is exposed. Cluster = sum (8), carriers averaged within sum, t-interval df=7. Output: `recompute_saved_output.txt`. Existing results and archives are preserved unchanged; corrections are applied to the report with this audit cited.

---

## 1. Verdict

**The load-bearing conclusion is verified.** The transport test's dissociation stands under independent recomputation: with the lens-readable carrier sum moved by the same internal magnitude via the operands (O_donor) or the carrier (C_full), the answer flips only when the operands change; a matched-norm random carrier write is inert. **One reporting mistake and one precision issue were found and are corrected below.** Neither changes any conclusion.

## 2. What was verified (recompute vs report)

| Claim (report §) | Recomputed | Verdict |
|---|---|---|
| Parity mapping `own_parity`/`diff_parity` correct; diff donor flips parity in every cell (Amend. 1) | numeric check (not index arithmetic): consistent, 16/16 cells flip | **PASS** |
| Boundary: self-patch bitwise no-op (§9) | 32/32 | **PASS** |
| Boundary: parity clean 16/16; diff→donor **16/16 L23, 12/16 L36**; same-stays 16/16 (§9) | identical | **PASS** |
| Boundary: report clean 16/16; diff→donor **16/16 L23/L36**; same-stays 16/16 (§9) | identical | **PASS** |
| Boundary margins (§9): report diff +21.3/+21.1, parity diff +6.5/+3.9, same ≈0 | +21.31/+21.11, +6.45/+3.91, same −0.42/−0.29/−0.08/−0.47 (CIs include 0) | **PASS** |
| Boundary internal C_diff^sum L51–59: +1.55 / +1.50, 8/8 (§9) | +1.55 [1.30,1.80] / +1.50 [1.30,1.69] | **PASS** |
| Boundary carrier damage nil (§9) | ΔNLL mean −0.0001, max +0.0013 | **PASS** |
| Transport: `n_forwards` 160 = 8×2×2×5 | 160 | **PASS** |
| Transport: **C_full flips 0/16** (report & parity), margin **+1.70 [1.09,2.31]** / **+0.53 [0.19,0.87]** (§10) | 0/16 under **both** scoring rules; margins identical | **PASS** |
| Transport: C_rand inert (§10) | flips 0/16; margin +0.05 [−0.01,+0.11] / −0.07; internal +0.13 | **PASS** |
| **Matched internal control** (§10): C_full internal ≈ O_donor internal (+1.55 vs +1.50) | per-sum ratio C_full/O_donor = [1.07, 0.94, 1.03, 0.97, 0.98, 1.05, 1.19, 1.05], **mean 1.04** | **PASS** (matched within ~5% on average) |
| "~8% contributor" (§10) | behavioral ratio of means C_full/O_donor = **0.081** | **PASS** |
| Transport clean competence 16/16 both consumers | 16/16, 16/16 | **PASS** |
| Transport carrier damage nil under C_full (§10) | ΔNLL mean −0.0000, max +0.0019 | **PASS** |
| O_donor reproducibility across the two independent runs (boundary lx36 vs transport) | **+1.50 [1.30,1.69] in both** — identical to the reported precision | **PASS** (determinism) |
| Calibration §8: A explicit 1.00 / latent 0.25; `>10?` 0.81; parity 1.00 | 1.000/0.250 (16/16, 4/16); 0.812 (13/16); 1.000 (16/16) | **PASS** |
| Competence §3: codebook 0.25 / 0.00 / 0.125 | identical | **PASS** |
| RNG-confound (§7, review): original competence run used a different codebook per wording | `assign` identical across wordings? **False** — confound confirmed as described | **PASS** (documented) |

## 3. Mistakes found

### 3.1 Reporting error — O_donor report flip count in §10 (CORRECTED)
§10's table stated O_donor **report** flips = **14/16**. The correct count under the report's own scoring rule (scored argmax) is **16/16**. Cause: the in-session analysis used an ad-hoc greedy-prefix rule, `greedy.lower().startswith(donor_sum[:3])`, which **fails for `thirteen`** (greedy first-subtoken `Th` → `"th".startswith("thi")` is False) **and `fourteen`** (`Four`), miscounting 2 correct flips as non-flips. This is an **inconsistency with §9**, which used the scored rule for the very same intervention (16/16). Parity (12/16) is unaffected (both rules agree). **Impact on conclusions: none** — O_donor flips strongly either way and C_full is 0/16 under both rules. Corrected in §10; the scoring rule is now stated explicitly.

### 3.2 Precision — "entire carrier state" (CORRECTED)
§10 said C_full "transplants the **entire** carrier state." It transplants the carrier state **from block 36 onward** (layers < 36 remain the recipient's). The sum is computed late and read at L51–59 (all ≥ 36), and the internal readout confirms the donor sum is installed at full natural magnitude (ratio 1.04), so the conclusion holds — but "entire" overstates the intervention. Corrected to "from block 36 onward."

### 3.3 Process gap — no committed analysis script (LOGGED)
The §9/§10 headline numbers were computed by inline python in the session rather than a committed `computed_sum_consumer_analysis.py`, contrary to the project convention (one analysis script per experiment). 3.1 is a direct consequence (an ad-hoc rule drifted from the canonical one). `recompute_saved.py` now serves as the committed, reproducible analysis for these stages.

## 4. Alternatives considered against the dissociation (and why they do not rescue "the readable sum is used")

- **"C_full is off-manifold, so the model ignores it."** C_full is the donor's *genuine natural* carrier state from a real forward, not a synthetic perturbation; carrier ΔNLL ≈ 0; the matched-norm random control is inert; and the internal readout shows the donor sum installed at the donor's full natural level (ratio 1.04). The null is meaningful.
- **"The consumer reads the carrier at layers < 36, which C_full leaves as recipient."** The sum-bearing carrier content is at ≥ 36 (readable L51–59); layers < 36 carry copied-text content. This is the basis of the §3.2 precision fix, not a rescue.
- **"The small C_full effect (+1.7) means the sum *is* used."** It is real and content-specific (vs C_rand +0.05), but ≈ 8% of the operand effect and never decisive; it may also reflect the carrier's memory-of-the-donor-operands rather than the sum per se. It **bounds** the maintained state's contribution; it does not make it the used variable.
- **"The word-vs-sum comparison is not matched."** Both use a full source-span donor from block 36 and ask whether the behavioral answer follows the donor; the consumers differ (report §9 scope note). The two organisms agree in direction (readable maintained content largely not the consumer's input), which is the generalization claim, not a matched pair.

## 5. Scope reminders (unchanged from the report)
One organism; C0/C1 calibration carriers (C2/C3 reserved — **not yet evaluation-grade**); thinking disabled; 8 arithmetic facts; block-36 carrier site. Necessity complement (O_donor + carrier clamped to own) and a C2/C3 rerun are the next passes.

## 6. Files
- `recompute_saved.py` — independent recompute (no runner import).
- `recompute_saved_output.txt` — its output at audit time.
