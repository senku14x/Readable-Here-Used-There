# Package 1 decisions (frozen 2026-09-06 before any Package 2 forward)

Source: `H1/results/natural_modulation.md` (run 20260906T220309Z) and `H1/results/source_transfer.md` (run 20260906T220538Z).

| Item | Decision | Basis |
|---|---|---|
| Source replacement start layer L_x | **36** (default) | C/A 0.52 at L48–50 and 0.95 at L51–59 (J_NP, maintain, 3/3 pairs); monotone in L_x at L48–50 |
| State site | block-output **35**, interior assistant-carrier positions | default; precedes L_x |
| Readout windows | **L48–50 and L51–59 co-primary** (registered as one primary family, Holm-corrected across the two; amended 2026-09-07 before any Package 2 forward) | maintain − plain mention is null at L48–50 and positive at L51–59; transfer nearly complete at L51–59 |
| Natural controls | mention (mention control) and plain mention both reported as co-primary; absent source as the floor | mention sits below plain mention at L48–50 (−0.28, 1/8) |
| Instrument | J_NP bf16-path score is the primary; float32 diagnostics recomputed with gain 1+weight from now on | RMSNorm parameterization verified in the transformers source |
| Numerical tolerance | cross-rendering comparisons: per-cell |Δz| up to 0.33 at L48 for a one-token change in sequence length (gates B5); within-rendering repeat is bitwise | `common/configs/instrument_gates_result.json` |
| Damage bound | top-1 retention ≥ 0.95; ΔNLL reported | all swaps ≤ 0.01 ΔNLL, retention ≥ 0.95 |
| Calibration pairs (geometry-matched) | (orange, tiger), (guitar, mountain), (diamond, castle); orange–guitar and thunder–rocket excluded by the span-length rule | `outputs/source_transfer/meta.json` pair table |
| Evaluation materials | Banks 1 and 2 (16 pairs), carriers C2 and C3; untouched so far | the frozen word banks and carriers |


## Amendment 2026-09-07 (before any Package 2 forward)

- L51–59 promoted to co-primary alongside L48–50 (rank-1 surfacing, maintain − plain mention, and near-complete transfer all live at L51–59).
- Package 2 analysis will report a random-readout-column floor (target column's change vs the change of random vocabulary columns under the same intervention) and the paper's rank-1-anywhere hit statistic as companions.
- Decoy `drawer` is excluded from the frozen decoy set whenever carrier D5 is in play (not relevant to Package 2, which uses C carriers).
