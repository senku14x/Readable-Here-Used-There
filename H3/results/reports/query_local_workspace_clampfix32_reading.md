# Reading of `clampfix32` against the registered predictions (Amendment 4; written 2026-09-10 after the run)

Stage run id 20260910T003315Z, 702 forwards (126 axis-fit + 576 scientific), 203 s, Qwen3.6-27B, thinking off, float32 residual from block 35 on. Tables: `query_local_workspace_clampfix32_tables.json`; report with the bf16 stage alongside: `query_local_workspace_clampfix32.md`; gate log: `regime_check.log`.

## Gates

- **Write fidelity (the project gate that `clampfix` failed).** On every one of the 32 cells × 6 clamp conditions × 2 consumers, ρ = 1.000 and κ = 1.000 over the 26 layers with a nonzero requested write, and the naming-plane read-back error after the clamp is ≤ 5.3e-5 (bf16: 0.14–0.21). Block 36 requests nothing at the question positions (its output there is clean under NEC; see the gate note in `AMENDMENT_4.md`) and is excluded; the committed bf16 ρ/κ means included that zero as one of 27 layers, which the analysis script's reproduction check accounts for.
- **Regime gate G0.** 3 of 4 checked cells inside every threshold; the fourth moved a donor-answer log-prob by +0.275 nats against 0.25, with top-1, bitwise determinism and carrier NLL matching on all four. Prediction 2 below is the n = 8 version of the same check and holds.
- **Damage.** Carrier ΔNLL ≤ +0.0008 nats on every cell; prefix (layers < 36) untouched, asserted per forward.

## Predictions

| # | registered | outcome |
|---|---|---|
| 1 | naming clamps meet ρ ∈ [0.9, 1.1], κ ≥ 0.99 on every cell; read-back < 1e-3 | **met**: ρ = κ = 1.000, read-back ≤ 5.3e-5 |
| 2 | `NEC` reproduces the bf16 rows within their intervals | **met**: report +19.27 (bf16 +19.26), parity +3.16 (bf16 +3.18) |
| 3 | emission-excluded naming clamp removes ≥ 38.8 % of the report margin, interval excluding zero; parity within 0.5 nats of NEC | **met in substance**: 38.5 % (19.27 → 11.84, [10.35, 13.33]); parity −0.04. The point estimate is 0.3 pp below the bf16 figure, far inside its interval; the registered failure condition (< half of the bf16 effect) is not approached |
| 4 | every `_perpm` control within the `NEC` interval on both consumers | **met**: report 19.24–19.26 vs 19.27, parity 3.13–3.17 vs 3.16, flips unchanged |
| 5 | carrier ΔNLL ≤ 0.02 on every cell | **met**: max +0.0008 |

## What the numbers say

The exact clamp reproduces the bf16 clamp row for row, to within 0.05 nats on every margin and to within one cell on every flip count. So the bf16 write, although it delivered only ρ ≈ 0.55, κ ≈ 0.45 of the requested delta per layer, had the same downstream effect as an exact write: the part it lost to rounding was inert, and the plane component it did deliver, pinned to within 0.14–0.21 across 27 successive layers, was enough. The "≈ 40 % of the report margin is drawn on the naming plane at the question tokens, parity is insensitive to that plane" statement therefore no longer needs the under-delivery caveat for these rows, and 38.5 % is the figure under an exact write.

**Decision rule, applied.** Predictions 1–5 met: per Amendment 4, `STATUS.md` weakness 1 is closed **for the question-clamp rows** and the mediation statement drops its caveat. The researcher decides whether to integrate this folder; the shipped files are unchanged.

**What this does not repair.** The other coordinate-level rows (`computed_sum_consumer` Amendment 3 swaps, `Q_swap`, `bridgeswap`, writes of norm 2–5 at ρ ≈ 0.8) were not rerun and keep the weakness. This stage gives a reason to expect they would also reproduce (a partial write with a matched inert control behaved like an exact one here), but that is an expectation, not a measurement.
