# Replication on Qwen3-32B (pure attention) — registered 2026-09-09, before any forward

_Why a second model at all: the whole pipeline (materials, rendering gates, hooks, readouts, analysis) had already been built and validated on Qwen3.6-27B, so re-running it on a dense model of the same depth and width cost little; I re-ran the built pipeline end to end as a check that the H3 result was not a property of the hybrid architecture, with the plan and predictions registered below before any forward._

## Why this model

Every result in this project is on **Qwen3.6-27B**, a hybrid with 48 GatedDeltaNet blocks and 16 full-attention blocks. The standing caveat on all of H3 is that the source reaches the consumer by two channels — attention, which can be masked, and the recurrent state, which cannot — so "the source route is sufficient" is really "attention plus recurrent state is sufficient", and the absent-source transplant has been the only clean way to remove the source rather than restrict the route.

**Qwen3-32B** is the control: `Qwen3ForCausalLM`, 64 blocks, d_model 5120, **every block full attention**, released Neuronpedia J-lens. Same depth and width as the primary model, so block indices, hooks, readout code and materials transfer unchanged; the recurrent channel simply does not exist. A pattern that reproduces here is architecture-independent within this family; a pattern that does not is a property of the hybrid.

## What carries over unchanged, and what does not

**Unchanged:** the design (hypotheses, estimands, materials, gates, decision rules), all prompt renderings (`enable_thinking=False` is supported), and every intervention contract. Verified before running: all fit / calibration / decoy / bank words, the 19 number words, the 8 codebook letters, `even`/`odd`, and all 12 two-hop items are **single-token** under this tokenizer. **Category words are not** (51 of them are multi-token), so `tagged_categories` is out of scope here.

**Not inherited — re-measured per model:**
- **Sites.** Block 35 as the state site, `L_x = 36`, and the L48–50 / L51–59 readout windows were *calibrated* on the primary model. Defaults are hypotheses. The `source_transfer` L_x sweep and the natural-readability gate are re-run here and the windows are re-chosen from this model's own layer profile before any H3 number is read.
- **RMSNorm gain.** `Qwen3RMSNorm` computes `weight * x`, not `(1 + weight) * x`; `readout.py` branches on the class name and takes the `weight` branch here (verified in the transformers source).
- **Layer map.** `Qwen3ForCausalLM` has no `layer_types` field; `registry.layer_types()` falls back to all-`full_attention` and records the fallback.
- **Lens.** The released Qwen3-32B fit (`Salesforce-wikitext`), which is the default-n fit, not the n1000 fit used for the primary model. Recorded in the registry; a lens difference is a scope note, not a confound, because every contrast is within-model.

## Scope of this replication (stated before running)

Five hours of compute does not reproduce ten H1 experiments. The **load-bearing subset** is run, in this order, each gated on the previous:

1. `instrument_gates` — model class, layer map, bitwise repeat, empty-patch and same-source identity, realized-write ρ and κ, sequence-length nondeterminism.
2. `source_transfer` (L_x sweep, calibration pairs) — **site calibration**: does replacing the source span transfer identity, and from which block; this chooses `L_x` and the readout windows for everything below.
3. `natural_modulation` (pilot) — the readability gate: does the maintain instruction raise the introduced word's readability at all on this model.
4. `tagged_selection` (pilot) — the discriminating H1 result: does the instruction select *which* of three tagged sources transfers.
5. `computed_sum_consumer` (competence → calibrate → robust) — the H3 core: source donor vs carrier donor vs carrier clamped vs matched random, on three instruments.
6. `query_local_workspace` (`nosource2`) — the absent-source transplant: is the carrier copy consumed when the source is not in the prompt.

Everything writes to `replication_qwen3_32b/` (`TCSIF_MODEL=qwen3_32b` switches the registry and the output root). The primary model's results are untouched.

## Predictions, on record

1. Gates pass; sequence-length nondeterminism is **smaller** than the hybrid's 0.33 lens logits per token (that effect was attributed to the linear-attention kernel, which is absent here). A comparable or larger value would falsify that attribution.
2. The natural readability and selection results reproduce qualitatively (maintain > control; S > 0). If selection fails here, it was hybrid-specific.
3. `L_x = 36` may **not** be the right cut: the transfer profile is re-read from this model's sweep.
4. **H3 core:** source donor reproduces the natural swing; carrier donor moves the readout to the donor on all three instruments while moving the answer far less and rarely flipping it; carrier clamped under a source donor still follows the source; matched random inert.
5. **Absent-source:** the carrier copy is consumed when the source is not in the prompt.
6. If 4 and 5 hold, the H3 headline is architecture-independent within this family and the recurrent-channel caveat is closed. If the carrier share is much larger here, the primary model's result was partly a property of the recurrent route.

## Amendment 1 — remaining H3 stages on this model (registered 2026-09-09, before these forwards)

The first pass ran only the H3 core (`computed_sum_consumer` competence/calibrate/robust) and the absent-source transplant. The remaining H3 stages are now run on Qwen3-32B with **no design changes**: `computed_sum_consumer global` (token-level operand donor, consistent clamp, paper-style lens coordinate swap, decision-position donors, and the attention-mask route restriction), `query_local_workspace` (`queryread`, `querycausal`, `clampsplit`), `selection_to_behavior carrier_only` (word organism), `two_hop_battery full` + `noclue` (the paper's released items), and `recompute_cost_ladder`.

**Why the mask rows matter more here than on the primary model.** Qwen3-32B is dense: blocking the consumer positions' attention to the source span at every attention block closes the *only* path from source to answer. On the hybrid the same mask left the GatedDeltaNet channel open, so those rows were reported as observations. Here the route restriction is exact, subject to the competence gate (`mask_clean` must stay ≥ 0.9 or the rows are uninterpretable).

**Predictions.** (i) `queryread`: with the carrier clamped, the donor value still appears at the question positions (reconstruction) at a similar fraction of its free level as on the hybrid. (ii) `querycausal`: clamping the reconstructed value at the question tokens costs the report consumer a substantial share and parity little or nothing. (iii) `Q_swap` flips report and not parity (answer-token steering), reproducing the method finding. (iv) `mask_clean` competence: **uncertain and load-bearing** — if it collapses, the exact route restriction is not available on this organism either and that is the finding. If it holds, `mask_C_full` exceeding unmasked `C_full` is the first clean evidence that the carrier copy is consulted when re-reading is genuinely impossible. (v) Word and two-hop organisms reproduce their carrier-share pattern. (vi) The ladder's boundary column may differ here; the carrier share is not expected to rise with difficulty.

Donor-geometry note: the two-hop items are all single-token under this tokenizer, but every donor/placeholder alignment is asserted per cell at generation, so any material that does not port will fail loudly rather than silently.
