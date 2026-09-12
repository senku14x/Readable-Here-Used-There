# Replication on Qwen3-32B (pure attention) — results

Registered plan and predictions: `replication_qwen3_32b/README.md` (written before any forward). Everything here uses `TCSIF_MODEL=qwen3_32b`; the primary model's results are untouched. Run 2026-09-09, ~2,000 forwards.

## 1. What ran, and what did not

| stage | status |
|---|---|
| `instrument_gates` | run; one sub-gate fails (below) |
| `source_transfer` (L_x sweep, site calibration) | run, 4 calibration pairs |
| `natural_modulation` (pilot, readability gate) | run, 8 calibration words × C0/C1 |
| `computed_sum_consumer` competence → calibrate → **robust** | run, the H3 core |
| `query_local_workspace` `nosource2` (absent-source) | run |
| `tagged_selection` (H1 discriminating result) | **not run** — see §5 |

## 2. Instrument and material portability

- **The released Qwen3-32B lens is a fit checkpoint, not a finished lens** (`jacobian_sum`, `n_done = 80`). Finalised here as `J = jacobian_sum / n_done` and saved locally with its own hash in `common/configs/instrument_registry_qwen3_32b.json`. **n = 80 against n = 1000** for the primary model's lens; the paper's public replication used n = 25, so a partial fit is usable, and every contrast here is within-model. Lens quality is a scope note that bears on §4's absolute magnitudes, not on any ratio.
- **Materials transfer** except category words: all fit / calibration / decoy / bank words, the 19 number words, the 8 codebook letters and `even`/`odd` are single-token under this tokenizer; **51 category words are not**, so `tagged_categories` is out of scope here.
- **Code changes required** (all committed): a `layer_types` fallback for dense transformers (`Qwen3ForCausalLM` has no such field; all 64 blocks are full attention), a registry/output switch so a replication writes to its own tree, lens loading restricted to instruments present in the registry, and one stale rendering call in the gates script.

## 3. Gates — one registered prediction falsified, one gate failed

- **Falsified (prediction 1).** Sequence-length nondeterminism is **larger** here, not smaller: **0.578** lens logits per one-token length change against 0.332 on the hybrid. The project had attributed that effect to the GatedDeltaNet kernel; that attribution is wrong, since this model has no linear-attention blocks. No result depends on it (every contrast is within a fixed rendering), but the provisional explanation in `H3/results/selection_to_behavior.md` should be corrected.
- **Failed: realized-write direction.** κ = **0.975** (bar 0.99; ρ = 1.013 is fine), so ≈ 22 % of a coordinate-move write's norm lands off-target, against ≈ 6 % on the primary model. Cause: residual norms are ≈ 6× larger here (RMS median 4.24 vs 0.67), so a fixed-size write is a smaller relative perturbation and bf16 rounding takes proportionally more of it. **This constrains only the coordinate-move family** (fitted-direction steers). Exact span overwrites are unaffected — read-back error 0 — which covers every condition in §4.
- Passed: bitwise repeat, empty-patch and same-source identity, rendering gates. The float32-vs-implementation agreement is far tighter than on the hybrid (0.035 vs 2.74), as expected once the RMSNorm gain convention is right (`weight`, not `1 + weight`).

## 4. H3 core — the headline replicates, and the carrier copy matters *less*

All carriers, donor map offset 3, cluster = sum (n = 8). Clean competence: parity 32/32, **report 24/32** (below the 0.9 bar, so report rows are weaker evidence here and parity carries the result).

| condition | report margin (nats) | flips | parity margin | flips |
|---|---|---|---|---|
| operands → donor | +26.69 | 24/32 | +15.97 | 32/32 |
| carrier → donor (≥36) | +0.53 | 0/32 | +0.66 | 0/32 |
| carrier → donor (all blocks) | +0.56 | 0/32 | +0.61 | 0/32 |
| carrier random | +0.02 | 0/32 | +0.03 | 0/32 |
| operands → donor, carrier clamped | +26.01 | 24/32 | +15.47 | 32/32 |

**Carrier share of the source effect: 0.020 (report), 0.041 (parity)** — against 0.083 and 0.181 on the hybrid. Depth-independent as before (`C_all` ≈ `C_full`). The carrier donor installs the donor sum at the readout at the source donor's own magnitude on all three instruments (J_NP ratio ≈ 1.0, RESID_P ≈ 1.0–1.15, LOGITS ≈ 1.1), the carrier clamp reads exactly 0.000, and the matched random write is inert.

**Reading.** The internal-versus-behavioural dissociation is **architecture-independent within this family**, and on a pure-attention model the maintained carrier copy contributes *less*, not more. That is the opposite of what a "the recurrent channel was doing the work" account predicts, and it closes the standing caveat in the direction that favours the original claim rather than undermining it.

## 5. Absent-source — the copy is consumed when the source is gone

With the operands replaced by a length-matched placeholder (unanswerable; the two candidate answers split at chance), installing a real run's carrier states moves the answer toward that run's sum: report Δ = **±3.6 nats, 8/8 items**, pairwise winner = the installed sum in 13/32 against 4/32 under the clean placeholder, symmetric for the alternative sum (13/32); parity 22/32 against a 16/32 chance floor; the matched random write is inert; the question-position transplant is the positive control. Weaker than the hybrid's 28/32. **Lens quality cannot explain this**: the transplant and the answer scoring do not involve the lens at all. The difference is between models (and this model's lower report competence), not between instruments. Same direction, identity-specific in both directions.

## 6. H1 — partial

- **`source_transfer` (site calibration).** Sustained replacement of the source span transfers identity to the readout at every start block, 4/4 pairs. At L48–50 the transferred fraction is C/A = **0.75 at L_x = 36** (0.52 on the hybrid), falling monotonically with L_x. So block 36 is usable here, and *more* of the readout effect arrives above the cut than on the hybrid. Worth noting against the open boundary-versus-domain question: the boundary here is *less* complete than on the hybrid, yet the carrier share is *smaller*, which does not fit a simple "more above-cut source contribution ⇒ larger carrier share" account. The two quantities are measured differently (readout transfer vs answer margin), so this is a tension to test, not a refutation.
- **`natural_modulation` (pilot).** The instruction effect is present but weak: maintain − mention +0.18 (7/8) at L48–50 and +0.21 (7/8) at L51–59, with intervals touching zero at pilot scale; maintain − plain mention +0.19 (6/8). **No rank-1 surfacing at all** (0.00 everywhere, against 0.56 for maintain on the hybrid). Consistent with a 12×-less-converged lens, a genuinely weaker effect, or both; not separable here.
- **`tagged_selection` — not run.** Two blockers, both worth recording as portability findings. (i) The pilot's donor map is **not token-length-matched under this tokenizer**: `"tiger"` is 4 tokens quoted and `"rocket"` is 3, breaking the donor-geometry gate on 2 of 12 pairs (the evaluation-bank map is clean, 0/24). Donor maps must be re-derived per tokenizer, not inherited. (ii) The evaluate stage needs a fitted ĝ from `task_state_modulation`, which was not run for this model — and would in any case carry the §3 coordinate-move caveat.

## 7. What this replication establishes, and what it does not

**Establishes:** the H3 core dissociation and the absent-source consumption reproduce on a pure-attention model of the same depth and width, with the carrier share smaller rather than larger. The recurrent-channel caveat that has qualified every H3 claim is closed in the favourable direction.

**Does not establish:** anything about H1 selection on this model (not run); anything with a fitted direction (gate failed); anything about magnitudes, which are confounded with lens convergence (n = 80). And the exact route-restriction test that this model *makes possible* — masking the consumer's attention to the source, which here would be a complete cut rather than a partial one — was not run for lack of time. That is the single highest-value follow-up and it is now unblocked.


## 8. Amendment 1 — the remaining H3 stages (run 2026-09-09, ~5,000 forwards)

All eight remaining stages ran with no design changes: `computed_sum_consumer global`, `query_local_workspace` (`queryread`, `querycausal`, `clampsplit`), `selection_to_behavior carrier_only`, `two_hop_battery` (`full`, `noclue`), `recompute_cost_ladder`.

### 8.1 Everything qualitative replicates

| result | primary model (hybrid) | Qwen3-32B (dense) |
|---|---|---|
| carrier share, sum organism | 0.083 report / 0.181 parity | **0.020 / 0.041** |
| carrier share, two-hop organism | 0.27 (12/48 flips) | **0.23** (5/48) |
| carrier share, word organism (of ceiling) | 0.012–0.042, 0/36 flips | **0.014–0.016, 0/36** |
| source donor, all blocks | 1.00 | **1.00** (48/48) |
| clue donor with carrier clamped (`NEC_all`) | 0.73 | **0.78** (39/48) |
| reconstruction at the question under the clamp | 78–93 % of free level | **89%** (two-hop); parity clamp leaves the answer unchanged (15.47 → 15.08 nats, orthogonal-plane control 15.32) |
| lens coordinate swap at the question | report flips, parity does not | **report 19/32, parity 0/32** — identical |
| difficulty ladder, carrier share by tier | 0.13 / 0.11 / 0.03, falls | **0.02 / 0.01 / 0.02**, flat; paired t3 − t1 = +0.00 [−0.01, +0.02] |

The method finding — that the paper's coordinate-swap intervention moves the consumer which *emits* the swapped word and not the consumer that computes a different function of the same value — reproduces exactly on a second architecture.

### 8.2 The boundary explanation of the arithmetic-versus-fact gap is disconfirmed

The open question after the ladder was whether the larger carrier share on two-hop facts (0.27) versus arithmetic (0.08) came from the *domain* or from the *boundary*: on the hybrid, the block-36 source share was ≈ 1.00 for arithmetic and only 0.58 for two-hop, and the two were confounded.

**On this model they are not confounded.** The two-hop source share at block 36 is **0.97** — the cut is essentially complete, as it is for arithmetic (1.00). Yet the carrier shares remain far apart within the same model, same cut, same instruments:

| organism, same model, boundary ≈ 1.0 | carrier share |
|---|---|
| arithmetic (all three ladder tiers) | 0.02 / 0.01 / 0.02 |
| two-hop facts | **0.23** |

So the gap survives controlling for boundary position. Combined with the ladder — which shows the gap is not produced by computational difficulty either — **the difference between a computed arithmetic latent and a looked-up factual one is real and neither of the two explanations proposed today accounts for it.** The cause is open. This supersedes the "leading account" recorded in `H3/results/two_hop_organism.md` and `context/evidence_ledger.md`, both of which are corrected.

### 8.3 Route restriction — the gate passes, but the cut is still not complete

`mask_clean` competence: **parity 29/32 (PASS)**, report 19/32 (fail, so report mask rows stay observations). With every attention block's consumer→operand read blocked (leak 0), parity margins:

| condition | margin (nats) | flips | over the masked baseline |
|---|---|---|---|
| `mask_clean` | +7.22 | 3/32 | — |
| `mask_C_full` | +8.37 | 14/32 | +1.14 |
| `mask_O_donor36` | +8.86 | 22/32 | +1.63 |

Unmasked, the carrier donor gives +0.66 and 0/32. The direction is as predicted, but the magnitude must be read against the **masked** baseline, not the unmasked one: +1.14 over +7.22, i.e. about 1.7× the unmasked carrier effect of +0.66, not the ×13 that comparing +8.37 with +0.66 would suggest. The large change in flip counts rides on a big baseline shift.

**But the cut is not complete, and I predicted otherwise.** If masking removed every path from source to answer, the operand donor under the mask would add nothing over the masked baseline; it adds +1.63. The reason is structural rather than architectural: blocking consumer→source attention leaves the indirect path source → carrier → consumer open, because the carrier positions still attend to the source and the consumer still attends to the carrier. A dense model makes the *direct* read maskable; it does not make the source unreachable. The masked baseline is also badly degraded (+7.22 toward the donor answer before any donor is applied), so these rows bound the effect rather than measuring it cleanly. **The absent-source transplant remains the only clean way this project has to remove the source.**

### 8.4 A procedural error, caught and corrected

`selection_to_behavior.py` was missing from the per-model output patch, so its replication run wrote into the primary model's tree. Detected by the run-id in the metadata, the replication data was moved to `replication_qwen3_32b/`, the primary files were restored from git (verified: run_id back to `20260909T121823Z`), and the script is now model-aware. No primary result was lost or reported from corrupted data.


## `bridgeswap` (Amendment 4 of `two_hop_organism`, 2026-09-09; 576 forwards)

The paper's lens-coordinate swap on the two-hop intermediate, decomposed by position, reproduces on the dense model: all-positions swap 0.38 of the full-residual ceiling (12/12 items, 16/48 scored flips), question turn 0.26, clue span 0.21, copied carrier 0.05 (0/48) while installing the swapped intermediate at the carrier readout (+1.91, 12/12); answer-word swap 0.52 (0.64 at the question); decoy-pair swap inert. Full table in `H3/results/two_hop_bridgeswap.md` §6; tables `replication_qwen3_32b/H3/results/two_hop_bridgeswap_tables.json`. ΔNLL for the tail/clue swaps reaches 0.023–0.026 (bound 0.02; reported).
