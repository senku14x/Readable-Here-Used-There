# Implementation audit — H3 selection_to_behavior

Two independent audits of the pilot/evaluate implementation, in agreement:
- **This audit** (GPU trace via `H3/scripts/audit_selection_to_behavior.py`, outputs `H3/outputs/audit/audit_results.json`).
- **The researcher's independent audit** (`H3/audits/selection_to_behavior/`: `AUDIT.md`, `trace_gpu.py` [independent execution path, does not import the H3 runner], `recompute_saved.py` [re-clusters the committed archive]).

**Existing results were preserved**: the v1 raw archives (`raw_{pilot,evaluate}.npz`) are untouched; the corrected run writes `*_v2` outputs, and the report above (`selection_to_behavior.md`) quotes the v2 numbers. Every finding below was either resolved in the v2 re-run or is a scoping note. The corrected numbers match across both audits and both scoring rules.

## 1. Checks and verdicts

| # | Check | Concrete diagnostic | Verdict | Resolution in v2 |
|---|---|---|---|---|
| 1 | Prefix / leakage | Equal-length different-content suffix: max residual diff **0.0 at every one of 64 blocks**. Without-consumer (len 101 vs 166): diverges from block **0**, growing to ~549 late. Independent trace: explicit all-ones mask vs default = **0.0 every layer**; jlens reference path vs model = **0.0 every layer** | **PASS (no leakage)** | The offset is sequence-length-driven, verified (mask and execution path ruled out; equal-length control null). All H3 conditions share length 166, so it cancels in contrasts. Kernel mechanism left provisional |
| 2 | What is patched | Forward hook on **block output** (matches `ActivationRecorder`); patched positions equal donor **exactly (0.0)**; blocks < 36 unchanged (0.0); source spans unchanged below L_x (0.0); region = positions [tag, carrier_start) | **PASS + labelling correction** | Region described as the **post-tag prefix** (tag + instruction tail + user-side carrier + delimiters), not "instruction only". No cache/recurrent state is transplanted (single full forward) |
| 3 | Donor matching | Arms differ at exactly one position (the tag); suffix identical; codebook/query appear once; instr positions max < answer position; instr ∩ source spans = ∅ | **PASS** | — |
| 4 | Answer scoring | Scored position is the last token; 2 ids per letter, no cross-letter duplicates; independent rerun reproduces saved E_B **exactly (rerun − saved = 0.0)**; max-rule vs logsumexp differ by ~0.003 nats (one surface form dominates) | **PASS** | v2 saves `llp[8,2]` and the analysis uses **logsumexp** over forms |
| 5 | Random control | v1 used a single isotropic `randA` matched to B→A, `rho` stored as a hardcoded `1.0` placeholder; 14% norm-mismatched for C→A | **FIXED** | v2 builds **randB** (matched to B→A) and **randC** (matched to C→A); measured realized ρ = **1.0002** each, read-back error **0.0** |
| 6 | Secondary composition | Instruction and source-span writers act on disjoint positions (`Both`); random realization fixed across an arm's swaps | **PASS, was conditional on #6b** | — |
| 6b | Donor cross-length | v1 harvested donor states at length 101 and wrote them into length-166 runs (~1% relative) | **FIXED** | v2 renders donors **with the consumer turn** (matched length; smoke 152 = 152). Primary noswap never used donor states |
| 7 | Statistics | v1 analysis clustered over **cells** not triples (pseudo-replication) | **FIXED** | v2 clusters by **triple** (pilot = 2 triples / 12 cells, evaluate = 6 triples / 36 cells). Point estimates unchanged, intervals widen |

## 2. Norm-ratio reconciliation (full-layer means)

The v1 audit table displayed **first-5-layer** mean write norms (B→A 6.60, C→A 6.12) but stated an all-layer ratio (C→A / B→A = 1.14 in one cell), which looked inconsistent. Reconciled: write norms grow with residual depth, so the full-LGE-layer mean is roughly double the first-5 mean, and the ratio is depth-dependent. Reporting the full-layer means removes the apparent mismatch:

| arm | v2 evaluate full-layer mean write norm | matched to | realized ρ |
|---|---|---|---|
| B→A | 12.43 | — | — |
| C→A | 12.68 | — | — |
| randB | 12.43 | B→A | 1.0002 |
| randC | 12.68 | C→A | 1.0002 |

`SpanWriter` overwrites, so realized equals requested by construction (read-back error 0.0 across all 48 pilot writes and all evaluate writes); ρ is now a measurement, not a placeholder. C→A / B→A ≈ 1.02 at evaluate scale (the single audited cell gave 0.87; the ratio is cell-dependent). Each target now has its own matched control, so no arm is scored against a mismatched norm.

## 3. The crossed source-margin table (observation only)

The crossed table (each transplant's effect on each source's answer margin), triple-clustered, evaluate:

| transplant | shifts B's margin | shifts C's margin |
|---|---|---|
| B→A | +3.32 [+2.72, +3.92] 6/6 | +1.97 [+1.51, +2.44] 6/6 |
| C→A | +2.09 [+1.66, +2.52] 6/6 | +2.54 [+1.79, +3.29] 6/6 |

Each transplant raises its own target most and also raises the off-target letter. **This is reported as an observation of the margin shifts and nothing more.** The earlier draft's decomposition of it into a target-specific increment and a non-specific off-target rise (a causal split) is **withdrawn**: B and C are both valid pointers and the two transplants are not independent perturbations, so the difference of two crossed shifts is not a clean causal quantity. The specificity claim that the data do support is the narrow one — each transplant's effect is null under a per-target norm-matched random write (randB, randC ≈ +0.03) — not a partition of the crossed table.

## 4. What changed vs the first draft

1. Letter scores recomputed with logsumexp (negligible move; archive now supports it directly).
2. Secondary rows re-run with matched-length donors; C→A given its own matched control randC.
3. Placeholder diagnostics replaced by measured realized-write ρ and read-back error.
4. Cluster counts stated consistently (pilot 2 triples, evaluate 6 triples); norm ratios presented as full-layer means.
5. The cross-length explanation is verified as length-driven (three independent controls) with only the kernel mechanism left provisional.
6. Removed from the conclusions: "rereading" as an asserted mechanism (route is unidentified; re-reading is one unexcluded possibility), "three times more", and the causal one-third / two-thirds decomposition of the crossed table.

## 5. Unresolved

- The specific bf16 linear-attention kernel mechanism behind the length-dependent numerics (verified to be length-driven; mechanism not instrumented).
- The behavioral route (carrier mediation vs the visible instruction) — by design out of scope here; needs a consumer whose answer cannot be read off the visible prompt.
