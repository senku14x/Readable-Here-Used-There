# H3 · `query_local_workspace` — is the sum reconstructed into a consumer-local representation, and is that what the answer depends on?

**Registered 2026-09-09, before any forward.** New experiment (not an amendment to `computed_sum_consumer.md`): the organism, sites and instruments are shared, but the question is different and the primary sites are the **question positions** and an **absent-source recipient**, neither of which any earlier stage touched.

## 0. Why

`computed_sum_consumer` established that making the carrier residuals donor-like installs the donor sum at the readout on J_NP, RESID_P and LOGITS at any cut depth, on four carriers and two donor maps, yet changes the delayed answer far less than replacing the source-span residuals while the source remains available (report +1.75 vs +21.2 nats, 0/32 vs 32/32 flips; `NEC`: the operand donor still flips 32/32 with the carrier clamped to its own state).

Two readings of that survive, and they differ in what they say about the workspace picture:

- **Reconstruction.** The variable the consumer uses is written afresh at the question positions when the question arrives, from operand-origin state. The maintained carrier copy is then redundant rather than unused, which is compatible with the paper's own remark that attention relieves a workspace of the need to propagate state, and would refine "maintained and broadcast" into "reconstructed just in time".
- **Bypass.** No verbalizable sum is instantiated at the consumption site either, and the answer is computed through operand-origin state that never becomes a readable sum variable. That is a readability-vs-use dissociation *at the consumption site*, which is a stronger negative than the current result.

A third possibility, that the carrier copy is consumable but only when nothing else is available, is untested because every condition so far leaves the operand tokens in the prompt. Removing them is cheaper and cleaner than restricting routes on this architecture, where an attention mask leaves the GatedDeltaNet channel open (Amendment 3 rows: report loses competence under the mask, so those rows are observations only).

## 1. The report-steering trap (why parity is primary throughout)

Amendment 3 found that a coordinate swap along the two sum-word naming directions, applied across source and decision positions, flips **report** 16/32 (+11.1 nats) while leaving **parity** at +0.22 nats, 0/32, and that the full-residual operand donor flips parity 23/32. A swap along the answer-word directions at the position that emits the answer word is output-token steering, and cannot be distinguished from substitution of the computed variable by the report consumer. Therefore:

- **parity is the primary consumer for every coordinate-level intervention in this spec** (it computes a different function of the same value and does not emit the swapped tokens);
- report is reported beside it as the steering-susceptible comparison, never as the primary;
- full-residual (non-coordinate) donors are read on both.

## 2. Sites, materials, conventions

Organism, model, instruments and metric conventions are inherited from `computed_sum_consumer.md` (Qwen3.6-27B @ `6a9e13b`, thinking off; teacher-forced copy organism; `Here is the pair "{a} and {b}". Keep their sum in mind while you copy: {carrier}` + a consumer turn). Cluster = sum (n=8), carriers averaged within sum, t-intervals df=7, scored-argmax rule (logsumexp over surface forms).

- Materials: all 8 sums; carriers **C0–C3**; donor map offset 3 (odd offsets flip parity; asserted per cell).
- **Question positions** `Q = [carrier_end, T)`: the consumer turn plus the answer position.
- **Carrier positions** and **operand span** as before.
- New: **absent-source recipient**, a rendering with no operand tokens, `Here is a pair of numbers. Keep their sum in mind while you copy: {carrier}`, plus the same consumer turn. Its length differs from the donor's, so donor states for it are harvested from a **length-matched** donor rendering (see §4 gate 3); the sequence-length sensitivity measured in the instrument gates (≈0.33 lens logits per one-token change) makes this non-optional.

## 3. Conditions

**Stage `queryread`** — observation only, no new interventions beyond those already run; every instrument recorded at `Q` as well as the carrier.

| condition | write | purpose |
|---|---|---|
| `clean` | — | baseline |
| `O_donor` | operand span ← donor, ≥ 36 | is the donor sum present at Q when the operands are the donor's? |
| `C_full` | carrier ← donor, ≥ 36 | does the carrier copy propagate to Q? |
| `NEC` | operand span ← donor **and** carrier ← own (clamped), ≥ 36 | **the load-bearing observation**: with the carrier copy denied, does the donor sum appear at Q anyway (reconstruction) or not (bypass)? |

**Stage `querycausal`** — interventions at Q.

| condition | write | positions | layers |
|---|---|---|---|
| `Q_donor_50` | donor states | Q | 36–50 (replicates Amendment 3's `D_band` with Q-site readouts) |
| `Q_donor_62` | donor states | Q | 36–62 (bounds where the report answer forms) |
| `Q_own` | own states | Q | 36–62 (self-patch gate; must be bitwise) |
| `Q_rand` | own + per-position norm-matched isotropic | Q | 36–62 (non-specific control) |
| `Q_swap` | coordinate swap own↔donor sum-word naming directions | Q | 36–62 (parity primary; report reported as steering-susceptible) |
| `NEC_Qclamp` | `NEC` **plus** the own/donor naming-plane coordinates at Q clamped to their clean values | Q | 36–62 | **the mediation test** |
| `NEC_Qclamp_perp` | `NEC` plus the same-norm clamp applied in a random 2-plane orthogonal to the naming plane | Q | 36–62 | matched control for the clamp |

**Stage `nosource`** — the absent-source recipient (no operand tokens anywhere).

| condition | write | purpose |
|---|---|---|
| `clean_ns` | — | competence floor (expected at chance: the sum is not in the prompt) |
| `C_from_S` | carrier ← the carrier states of a real run with sum S, all 64 blocks | is the carrier copy consumable when it is the only place S exists? |
| `C_from_S2` | same, from a different sum S2 | identity specificity |
| `C_rand_ns` | own + norm-matched isotropic | non-specific control |
| `Q_from_S` | question positions ← the Q states of a real run with sum S, 36–62 | positive control that *something* installed at Q can carry the answer |

## 4. Gates (before any outcome is read)

1. `Q_own` bitwise no-op; operand span and carrier asserted untouched under every Q write; prefix untouched under Q writes.
2. Carrier ΔNLL ≤ 0.02 for every write that touches the carrier; the Q writes are after the carrier and cannot affect it.
3. **Length matching for `nosource`.** The absent-source rendering, the sum-S donor rendering and the sum-S2 donor rendering must have identical token counts and identical carrier and question spans; the placeholder phrase is chosen mechanically to satisfy this and the check is an assertion, not a hope. If it cannot be satisfied exactly, the stage does not run.
4. Clamp diagnostics: realized coordinate values at Q after `NEC_Qclamp` equal the clean values (read-back), and the clamp's write norm is recorded so `NEC_Qclamp_perp` can be matched to it.
5. `clean_ns` competence recorded; the `nosource` rows are read as "does the answer become S", not as accuracy.

## 5. Predictions, on record

1. **`queryread`/`NEC`:** the donor sum appears at Q under `NEC` at ≥ 0.5 of its `O_donor` level on J_NP and RESID_P. (Reconstruction; if it is ≈ 0, bypass.)
2. **`Q_donor_50`** reproduces Amendment 3: parity flips ≥ 16/32, report ≈ 0/32. **`Q_donor_62`** flips report ≥ 16/32 (the report answer forms after block 50).
3. **`Q_swap`** on **parity**: no prior; this is the discriminating cell. On report, expect flips (steering-susceptible) and do not read them as substitution.
4. **`NEC_Qclamp`:** if prediction 1 holds, parity flips fall by ≥ 1/3 relative to `NEC` and the margin drops toward clean, while `NEC_Qclamp_perp` leaves them unchanged. That is mediation by the consumer-local representation. If `NEC_Qclamp` does nothing, the reconstructed representation is readable at Q and bypassed — the stronger negative.
5. **`nosource`:** no prior on whether `C_from_S` carries the answer. `C_from_S` vs `C_from_S2` must differ if either works (identity specificity); `C_rand_ns` inert; `Q_from_S` is the positive control and should carry the answer if any Q write can.
6. Damage as in gate 2.

## 6. Outcome table (all rows are results)

| `NEC` at Q | `NEC_Qclamp` | reading |
|---|---|---|
| donor sum present | reverts | **reconstruction and mediation**: operand state → consumer-local readable sum → answer. Refines "maintained and broadcast" into "reconstructed just in time"; the carrier copy is redundant, not unused. |
| donor sum present | no change | **bypass at the consumption site**: the variable is readable exactly where it is needed and the answer does not depend on it. The strongest negative available in this project. |
| absent | (n/a) | **no verbalizable instantiation**: the consumer computes through operand-origin state that never becomes a readable sum. Closest to the paper's automatic-processing case studies. |

`nosource` is orthogonal to that table: it says whether the carrier copy is consumable when it is the only source, which is what turns "not used while the source is visible" into a statement about use.

## 7. Budget and what this spec does not claim

8 sums × 4 carriers × 2 consumers × (4 `queryread` + 7 `querycausal`) + the `nosource` block ≈ 800 forwards, one GPU hour. No claim about: the read-site component (which module writes the Q representation), other consumers, other organisms, or the pure-attention architecture — the exact source-unavailable test through route restriction stays deferred to that model, and `nosource` is the source-removal version available here.

## Amendment 1 — split the question-site clamp at the answer position (registered 2026-09-09 after reading `querycausal`, before the forward it governs)

`NEC_Qclamp` pins the own/donor naming plane at every question position including the answer position. On report, which emits the sum word at that position, the clamp is indistinguishable from output-token suppression (it removed the report answer 32/32 → 0/32). To read report at all, the clamp is split: `NEC_Qclamp_noans` clamps the question tokens **excluding** the answer position; `NEC_Qclamp_ansonly` clamps the answer position **only**. Same band (36–62), same references, same `NEC` base. Predictions: if report survives `noans` and collapses under `ansonly`, the report answer is formed at the emission position from operand-origin state and the reconstructed sum on the question tokens is not its input (the parity reading generalises); if report collapses under `noans`, the question-token reconstruction mediates report. Parity is run for completeness. 2 conditions × 64 cells = 128 forwards.

## Amendment 2 — second absent-source rendering without a quoted placeholder (registered 2026-09-09 after reading `nosource`, before the forward it governs)

In `nosource` the placeholder `"a and b"` kept the length and spans matched, and the scored-argmax endpoint followed the transplanted carrier (report: argmax = S 21/32 under `C_from_S`, = S2 21/32 under `C_from_S2`, 4/32 under clean and random). But the model's greedy token was `a` in every cell — the placeholder letters captured the greedy answer, so the result is a shift of the relative log-probabilities of the sum words, not a greedy behavioral flip. Stage `nosource2` reruns the same conditions with the recipient `Here is a pair of numbers (hidden). Keep their sum in mind while you copy …` (no quoted span, no letters, no number words; token count and carrier/question spans match the operand renderings exactly, asserted per cell). Prediction: greedy answers become sum words; `C_from_S` argmax = S at or above the 21/32 seen with the placeholder; `C_from_S2` symmetric; random inert. Same 574 forwards.


## Amendment 3 — control repairs required before the question-clamp rows are cited (registered 2026-09-09 after an external audit; NOT yet run)

Two defects in the shipped implementation, both of which weaken the clamp rows rather than invalidate the observation:

1. **The orthogonal control is not norm-matched.** `NEC_Qclamp_perp` clamps a random 2-plane to *its own* clean coordinates, so the resulting perturbation is smaller than the naming-plane clamp's (requested-norm means ≈ 0.19 vs 0.48 on the primary model, 1.08 vs 1.98 on the dense one). A smaller control is a weaker test for nonspecific damage. **Repair:** scale the control clamp's per-position delta to the naming-plane clamp's realized norm, cell by cell, and report the matched norms.
2. **`clampsplit` has no orthogonal control** at the same positions. **Repair:** add `NEC_Qclamp_noans_perp` and `NEC_Qclamp_ansonly_perp` with the same norm matching.
3. **Diagnostics mislabelled.** `CoordClamp` and `CoordSwap` store the *requested* delta norm in `realized`, computed before the cast to bf16. **Repair:** measure the post-cast delta as `StateMove` does, and rename the stored field.

Until these run, the licensed statement is "clamping the naming plane at the question tokens lowers the report margin by 38.8 % (primary) / 12.8 % (dense) and changes parity little", with the control caveat attached. The phrase "≈ 40 % mediation" is not licensed.

**Implementation note (2026-09-09, before the forward it governs).** Amendment 3 runs as stage `clampfix` (`query_local_workspace.py`), 8 sums × C0–C3 × both consumers. Conditions per cell: `NEC`; `NEC_Qclamp` / `NEC_Qclamp_noans` / `NEC_Qclamp_ansonly` (naming plane, as before, now via `CoordClampMatched`, which records the post-cast realized write: ρ, κ, per-position norms); and `*_perpm`, the same clamps in a random plane orthogonal to the naming plane with each position's delta rescaled to the naming clamp's realized per-position norm in the same cell and layer (the norm-matched control the audit asked for). Predictions: the naming clamp reproduces the earlier rows (report margin down ≈ 40 %, parity unchanged); each `_perpm` control leaves both consumers within the `NEC` interval; ρ ∈ [0.9, 1.1], κ ≥ 0.99 for every clamp. If a `_perpm` control moves report by ≥ half the naming clamp's effect, the clamp rows are nonspecific and stay withdrawn. 9 forwards per (cell, consumer) = 576.


## Amendment 4 — the clamp rows under a float32 residual (registered 2026-09-10, before the forward it governs; run the same day)

_Originally kept in an isolated folder `H3/clampfix_fp32/` so the shipped files stayed untouched until the researcher integrated it; folded into the regular layout on 2026-09-11 (scripts under `H3/scripts/query_local_workspace_{clampfix32,clampfix32_analysis,regime_check}.py`, the fp32 hooks under `common/scripts/hooks_fp32.py`, outputs under `H3/outputs/query_local_workspace/*_clampfix32.*`, report `query_local_workspace_clampfix32.md` + `_reading.md`). The folder README and the registration follow verbatim._


### Registration text (Amendment 4) — the clamp rows under a float32 residual (registered 2026-09-10, before the forward it governs)

**Why.** `clampfix` closed the audit's three defects but exposed a fourth: in bf16 the question-token clamps are realized at ρ ≈ 0.53–0.59, κ ≈ 0.42–0.48 (write norms 0.2–0.5 against a bf16 step of 0.02–0.04 per entry over 5120 entries), so every coordinate-level row is a partial write and the read-back pins the plane only to within 0.14–0.21. `STATUS.md` weakness 1 records "float32 hooked outputs" as the repair. This amendment runs it.

**Regime.** `hooks.Fp32Residual(blocks, from_layer=35)`: a forward hook on block 35 upcasts its output to float32, so blocks 36–63 carry a float32 residual; the forward runs under bf16 autocast, so every matmul, the attention and the GatedDeltaNet kernels receive the same bf16 operands as before (the RMSNorms already compute in float32). Only the residual additions, the final norm input and the hooked writes change precision. `CoordClampMatched` computes its coordinates and delta with autocast disabled. Every forward of the stage (axis fit, clean, donor, all conditions) runs in the regime, so comparisons are internal to it; the bf16 `clampfix` tables are reported alongside, not pooled.

**Stage `clampfix32`** (`query_local_workspace.py`): identical cells, conditions, seeds, random planes and norm-matching rule to `clampfix` (8 sums × C0–C3 × two consumers × {`NEC`, `NEC_Qclamp`, `NEC_Qclamp_noans`, `NEC_Qclamp_ansonly`, each with its `_perpm` control}; 576 scientific forwards + 126 axis-fit). Analysis `query_local_workspace_clampfix_analysis.py`, which first re-derives the committed `clampfix` tables exactly (the original analysis script was not committed; this one replaces it).

**Gates, before any outcome is read** (`query_local_workspace_regime_check.py`, 2 sums × C0 × both consumers, run first):
- G0, the regime reproduces the bf16 forward: identical top-1 answer on every checked cell, carrier |ΔNLL| ≤ 0.02, own- and donor-answer log-probs within 0.25 nats, and the fp32 clean forward bitwise deterministic across two runs.
- G1, the write is exact: naming-plane clamp ρ ∈ [0.99, 1.01], κ ≥ 0.999, plane read-back error ≤ 1e-3, layers < 36 bitwise untouched.
- In the stage: the existing prefix assertion; ρ ∈ [0.9, 1.1] and κ ≥ 0.99 for every clamp cell (the project gate that `clampfix` failed).

**Predictions, on record.**
1. The naming-plane clamps meet the write gate on every cell (ρ, κ ≈ 1), and read-back error falls from 0.14–0.21 to < 1e-3.
2. `NEC` under the regime reproduces the bf16 `NEC` rows within their intervals (report ≈ +19.3, parity ≈ +3.2).
3. The emission-excluded naming clamp (`NEC_Qclamp_noans`) removes **at least as much** of the report margin as in bf16 (≥ 38.8 %, interval excluding zero); parity stays within the `NEC` interval (|Δ| ≤ 0.5 nats). A cleaner clamp should not remove less.
4. Every `_perpm` control stays within the `NEC` interval on both consumers.
5. Carrier ΔNLL ≤ 0.02 on every cell.

**Decision rule.** Predictions 1–5 met: weakness 1 is closed for the question-clamp rows, the "≈ 40 % mediation, parity bypasses the plane" statement drops its under-delivery caveat, and the fp32 percentage replaces the bf16 one in `STATUS.md` (the bf16 rows remain as the first measurement). If prediction 3 fails downward (the exact clamp removes < half of the bf16 effect), the bf16 effect was partly rounding-driven and the mediation statement is withdrawn. If a `_perpm` control moves report by ≥ half the naming clamp's effect, the rows are nonspecific and withdrawn. Other coordinate-level rows (`computed_sum_consumer` Amendment 3 swaps, `Q_swap`, `bridgeswap`) are **not** repaired by this stage and keep the weakness; their writes (norm 2–5, ρ ≈ 0.8) would need their own fp32 rerun.

**Gate note (2026-09-10, after `regime_check.py`, before the stage forward).** G1 as written failed only at block 36, where the requested delta is exactly zero on every cell: the NEC writers act on block outputs ≥ 36 at the span and carrier positions, and the question positions' block-36 output depends only on block-35 outputs, which are clean, so the clamp there has nothing to write (ρ is reported as 0/ε = 0 by convention; the bf16 `clampfix` per-cell means carried the same zero as one of 27 layers). G1 is therefore read over layers with a nonzero requested delta (36 < l ≤ 62): on all 26 of them and all four checked cells ρ ∈ [0.99, 1.01], κ ≥ 0.999, read-back error 1.3–2.3e-5, layers < 36 bitwise untouched. G0 held on 3 of 4 cells; the fourth (S0, parity) moved the donor-answer log-prob by +0.275 nats against the 0.25 threshold, with top-1, determinism and carrier NLL matching on all four (residual relative distance at the question positions 1.3–3.6 %). The stage proceeds with this recorded; prediction 2 (`NEC` within the bf16 intervals at n = 8) is the regime test that matters. Raw log: `results/regime_check.log`.

### The isolated folder's README (verbatim, 2026-09-10)

#### clampfix_fp32 — the question-clamp rows rerun with an exact (float32) write

**Isolated on purpose (researcher's instruction, 2026-09-10):** nothing outside this folder was changed for this run. The shipped scripts, hooks, design spec, results and STATUS are untouched; the researcher will integrate or discard this folder later.

##### Why it was run

`H3/results/query_local_workspace_clampfix.md` §3 (Amendment 3, bf16) found that every coordinate-level clamp in the project is a partial write: for question-token clamps of norm 0.2–0.5 the realized write has ρ ≈ 0.53–0.59 and κ ≈ 0.42–0.48 against the project gate ρ ∈ [0.9, 1.1], κ ≥ 0.99, because a bf16 residual entry has a step of 0.02–0.04 and 5120 such roundings are as large as the write itself. The naming-plane clamp therefore pinned the plane only to within 0.14–0.21 of the clean coordinates, so "removes ≈ 40 % of the report margin" was a lower bound and the parity null was a null against a partial clamp. `STATUS.md` weakness 1 names the repair: float32 hooked outputs. This folder runs that repair.

##### What was run

- `AMENDMENT_4.md` — the registration (regime, gates, predictions, decision rule), written before any forward.
- `hooks_fp32.py` — `Fp32Residual` (block 35's output upcast to float32, forward under bf16 autocast, so every matmul and kernel sees the same bf16 operands as before and only the residual additions and the hooked writes change precision) and a `CoordClampMatched` whose coordinate/delta arithmetic runs with autocast disabled.
- `regime_check.py` — gates G0 (the regime reproduces the bf16 forward: same top-1, |ΔNLL| ≤ 0.02, answer log-probs within 0.25 nats, bitwise deterministic) and G1 (exact write: ρ ∈ [0.99, 1.01], κ ≥ 0.999, read-back ≤ 1e-3, layers < 36 untouched) on 2 sums × C0 × both consumers. Output: `results/regime_check.log`.
- `run_clampfix32.py` — a copy of `H3/scripts/query_local_workspace.py` with the single added stage `clampfix32`: the `clampfix` cells, conditions, seeds, random planes and norm-matching rule, every forward in the float32 regime. Writes `outputs/{raw,meta,manifest}_clampfix32.*`.
- `analysis.py` — `python analysis.py clampfix` re-derives the committed bf16 tables exactly (the original clampfix analysis script had not been committed; this one is its replacement); `python analysis.py clampfix32` writes `results/query_local_workspace_clampfix32_tables.json` and `results/query_local_workspace_clampfix32.md` with the bf16 values alongside.

##### Results

See `results/query_local_workspace_clampfix32.md` (written by `analysis.py` after the run) and `results/READING.md` (hand-written reading against the registered predictions).
