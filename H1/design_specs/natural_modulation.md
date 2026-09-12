# H1 · natural_modulation — does the instruction change the readability of the introduced word, and does the source determine it?

**Package 1 (natural modulation and source pilot), covering H1.2.** Scripts: `H1/scripts/natural_modulation.py` (readout under prompt conditions) and `H1/scripts/source_transfer.py` (sustained source replacement with a start-layer sweep). Outputs `H1/outputs/natural_modulation/`, `H1/outputs/source_transfer/`; results `H1/results/natural_modulation.md`, `H1/results/source_transfer.md`.

## Question and why it matters

Before any task-state direction is fitted, two facts must be established on this organism, in this model, under our own rendering: (1) whether the maintain instruction raises the lens readability of the introduced word at the copied-sentence positions relative to a mention control, and relative to plain mention and an absent-source baseline; (2) whether replacing the source's block outputs from a start layer L_x onward moves the later readout toward the donor at all, and at which L_x. H1.4 is undefined if (2) is null at the chosen depth, and the project's cheapest decisive result is (1): the workspace paper's own appendix found bare mention primes nearly as strongly as focus, and the earlier pilot found maintain ≈ plain mention at readout on these carriers.

## Hypothesis and strongest alternative

- **H1.2a (natural modulation).** D_J(X) = s̄_J(X | maintain) − s̄_J(X | mention) > 0, and maintain > plain mention > absent. Alternative: maintain ≈ mention ≈ plain mention (the instruction adds nothing beyond the word's presence), with the readout level set by mention alone.
- **H1.2b (source dependence).** Sustained replacement of the source span's block outputs from L_x onward with an arm-matched donor Y moves the pair margin m^{X→Y} toward Y: C_k > 0. Alternative: by L_x the source's influence has already propagated into the carrier, and the swap does nothing (C ≈ 0); or the readout moves only under the lens and not on the independent axis.

## Materials (frozen before any forward; the frozen word banks and carriers)

- Calibration words (8): orange, guitar, tiger, mountain, diamond, thunder, castle, rocket. Calibration pairs for the source sweep: (orange, guitar), (tiger, castle), (diamond, rocket), (mountain, thunder), both directions.
- Decoys (8): dragon, drawer, forest, fork, hammer, horse, knife, lion. `drawer` occurs in direct carrier D5; the frozen decoy subset for any comparison involving D5 excludes it.
- Carriers: C0 and C1 (fitting carriers) for the pilot; C2/C3 held out. Direct organism: D0, D3 for the pilot.
- Conditions, controlled organism: maintain, mention (mention control), plain_mention, ignore, do_not_think, never_think, absent. Direct organism: primary pair `Hold {X} in mind as you write.` vs `{X} came up in conversation.`; both direct and copy-adapted renderings, never pooled.
- Eligibility: every scored word must be a single token with a leading space; mechanical exclusions logged (`common/configs/instrument_gates_result.json`).

## Measurements

- Readout J_NP at every block output 0–62, interior assistant-carrier positions (carrier span trimmed by 2 at each end), positions averaged within a sequence, then carriers within an item.
- s_J(X; ℓ) = z_X − mean(z_decoys) (natural presence). Pair margin m^{X→Y} = E[z_Y − z_X] for the source sweep.
- Prominence: full-vocabulary rank of X at every (layer, position); r_min over the window; f_10; fixed top-10 lists on a seeded subset.
- Numerator n, RMS r and z separately (the prominence and normalization diagnostics).
- RESID_P: plain-sentence axis fitted per word on templates 1–8 (Appendix C), validated on 9–12; used as an independent presence measure (one-vs-decoy centroid direction) and as the pair axis p_{Y−X} for the source sweep.
- LOGITS: the model's own output log-prob margin at the interior positions (a secondary instrument here; the primary consumer sites come in H3).
- Damage: carrier NLL and top-1 retention vs the clean run for every intervened forward.

## Interventions (source_transfer only)

Sustained replacement: h^{recip}_{ℓ,P_s} ← h^{donor}_{ℓ,P_s} for all ℓ ≥ L_x, P_s = the quoted span (word tokens + closing quote), donor = the clean run of Y in the same arm and carrier, geometry-matched (asserted). L_x ∈ {23, 28, 32, 36, 40, 44} on calibration pairs. Same-source replacement (donor = own cache) must reproduce the clean run bitwise. Layers < L_x asserted identical between future-X and future-Y runs. This is a calibration sweep: L_x is frozen from it before evaluation, per the project conventions

## Metrics and statistics

- Natural: D_J(X) per word, clustered by word (n = 8 calibration words); condition means with cluster-t intervals; all pairwise condition contrasts reported, none privileged in the pilot.
- Source: C_k(q=0, arm) = m(swap) − m(noswap) per directed pair, averaged over both directions and carriers within the unordered pair; n = 4 pairs (pilot scale, disclosed); per L_x.
- Same quantities on RESID_P and LOGITS; calibrated comparison only via A_k = the natural X/Y contrast on the same instrument.

## Controls and gates

- Mechanical: all rendering gates; same-source bitwise; layer < L_x identity; realized-write ratio not applicable (replacement).
- Positive control for the readout: the natural X vs Y contrast at the same positions (A_k).
- Prompt-side control for priming: plain mention and absent source.
- Damage bound: top-1 retention ≥ 0.95; NLL change recorded.

## Predictions

| Outcome | Reading | Next |
|---|---|---|
| D_J > 0 and maintain > plain mention > absent | natural modulation established on this organism | proceed to Package 2 with L_x from the sweep |
| maintain ≈ plain mention > absent | the instruction adds nothing beyond mention at readout; H1's natural branch is priming | still run the source sweep; H1.4 tests transfer modulation, which does not require an arm difference at readout (the gate contract phenomenon gates are local) |
| C_k > 0 at L_x = 36 | H1.4's default site is usable | freeze L_x = 36 |
| C_k > 0 only at L_x ≤ 32 | source influence completes before the default site | freeze the latest L_x with CI-clear C; state site must be < L_x (the state site moves earlier, and the project's block-35 default is amended with a recorded reason) |
| C_k ≈ 0 everywhere | source replacement at the span does not reach the readout; H1.2 branch "no source response with working readout" | investigate readout sensitivity with a richer donor patch at the readsite before any H1.4 |
| J moves, RESID_P does not | J-selective response | repair or replace the independent instrument before H1.4 |

## Budget

Natural: 8 words × 7 conditions × 2 carriers = 112 forwards (controlled) + 8 × 2 phrasings × 2 renderings × 2 carriers = 64 (direct). Source: 4 pairs × 2 directions × 2 arms × 2 carriers × (1 clean + 6 L_x + 1 same-source) = 256 forwards. Plain-sentence fits: 16 words × 12 templates = 192 short forwards. At ≈ 0.15–0.3 s per forward with all-layer recording, under 5 minutes of GPU time.
