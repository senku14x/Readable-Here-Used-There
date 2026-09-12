# H2 / H3 roadmap — entry points after the H1 stopping point

Not design specs; these say what the first runnable package of each hypothesis is, which prerequisite must exist first, and the decision that package makes. Write the real design spec before running.

## H2 — maintenance or reconstruction of readable content

**Prerequisite (H2.5, do first): a valid state boundary.** The model is hybrid (48 GatedDeltaNet blocks with recurrent state + 16 full-attention blocks with KV cache). A "complete prefix state" transplant must carry both the KV cache of the attention blocks and the recurrent/conv states of the linear-attention blocks. Positive control: run the prompt up to the carrier start, serialize the full state, resume with the same continuation, and assert bitwise-identical logits versus the uninterrupted run. Until that passes, no cache/recurrence transplant result is readable. Inspect `transformers` 5.15's cache classes for `Qwen3_5` (`DynamicCache` + the linear-attention state object) and record their attribute names in the design spec.

**Package 4a — one-position pulse (H2.3).** On `pulse_base` (`Copy the following text exactly, word for word:` + carrier, no introduced word), add at one interior position the naming direction of X (folded lens direction from `readout.folded_direction`, or the RESID_P one-vs-decoy direction) at block 35, and read X's presence at later positions. Endpoint: decay of s_J(X) with distance from the pulse; a "rich" pulse (the clean maintain-arm residual difference at that position) vs the naming pulse. Decision: does anything persist beyond the pulsed position? If nothing persists at 5+ positions with either pulse, maintenance is not a within-carrier residual phenomenon at this site and the erasure package is the informative path.

**Package 4b — local erasure and recovery (H2.4).** On the maintain organism, erase X's presence at k consecutive interior positions (`EraseToReference` to the absent-arm level along the presence direction) and read recovery at later positions. Recovery with the source span intact vs with the source span replaced by a donor from block 36 (does recovery re-read the source?) vs with the KV/recurrent state of the source positions transplanted from a donor (H2.6, after the boundary passes). Decision: which state supplies the recovered identity: source tokens, carrier past, or instruction state.

## H3 — downstream use

**Caution from the earlier pilot (added 2026-09-07, `earlier_pilot_notes.md` §9.4).** On the earlier pilot's word-codebook consumer the letter answer tracked the source span's layer 23–35 content: a donor from block 36 moved it by −0.58 nats against −6.7 from block 23, and under a full-attention block the delayed donor still reached the answer through the recurrent route. A block-36 boundary positive control on a word-codebook consumer is therefore expected to be weak. Options: validate the boundary from block 23 (which no longer isolates post-state-move content), or choose a consumer whose answer cannot be re-read from the span — the computed sum (`computed_sums`) or category members (`tagged_categories`) — and validate the block-36 boundary there first.

**Prerequisite (H3.2): a competent consumer.** The ordinal-list codebook query (the consumer prompts) on the tagged/ordinal organism: accuracy ≥ 0.9 for the pointed word in maintain and a defined behavior in control. Then the full-state counterfactual: replace the pointed source from block 36 by the donor and confirm the answer follows the donor (behavioral transfer). That is the boundary that controls the answer.

**Package 5 — representation ladder at the identical cut (H3.3).** At the block-36 cut on the source span, compare: full-state donor replacement (ceiling), lens-direction-only replacement (write the donor's naming direction component only), RESID_P-direction-only, d_shared-only. Endpoint: answer accuracy toward the donor letter. Decision: which representation is sufficient to move behavior. Then H3.4 (necessity: erase the same components and test rescue) and H3.5 (does the ĝ / d_shared move change the answer at all, i.e., does a readout gain reach behavior?). H3.5 is the direct test of the project's central worry: a gain and a selection can make identical lens predictions and different behavioral ones.

**Package 6 — the integrated test.** The one state–source contrast that discriminated in H1 (selection: pointed vs unpointed donor) repeated at the consumer: does the answer follow the pointed source's donor more than an unpointed source's donor?

## Reporting

Each of H2/H3 ends with its own separate verdict lines (H2.8, H3.7); never fold them into H1.

## Update 2026-09-09 — H3 state after the robustness battery, and what the researcher decided

- **Established (this model, thinking off, four carriers, two donor maps, two consumers, three instruments):** the sum consumers answer from the operand positions; the carrier's lens-readable copy of the sum, installed at the donor level, contributes ≈ 9–18 % of the answer-margin shift and never flips the answer at any cut depth. Operand route sufficient alone (carrier clamped: 32/32 flips). Word organism matched: carrier-only donors ≤ 0.04 of ceiling, 0/36. Reports: `H3/results/computed_sum_consumer_robust.md`, `selection_to_behavior_carrier_only.md`.
- **Scope that must travel with the claim:** "while the source is visible". Not licensed: use when the source is unavailable; pure-attention architectures; the workspace paper's decision-position swaps (its clamps covered source positions too, so no contradiction).
- **Researcher decisions:** no circuit localization for now; broaden and harden the dissociation instead (global clamp, decision-position swap, arithmetic chain, two-hop organism — see CLAUDE.md). Route restriction and the exact "source unavailable" test go to the planned pure-attention rerun at the end of the project, where the operand route is attention-only and a mask closes it completely. H2 unchanged: hybrid cache + recurrent-state parity is the prerequisite and has not been built.
- **Process rule reaffirmed:** the transport stage had run unregistered; Amendment 2 registered it retroactively with predictions and the battery was run only after that. Every new condition gets an amendment with predictions first.
