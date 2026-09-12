# Backup figures for the write-up and the form answers

All regenerated from committed tables (or, for B2, from `raw_nosource2.npz`) by `common/scripts/make_figures.py`, `paper_draft/make_exec_figures.py` and `paper_draft/make_backup_figures.py`. PNG for docs, PDF for LaTeX.

| file | what it shows | where it could go |
|---|---|---|
| fig_selection | ĝ orthopanel scatter (a); tagged selection bars with the control line (b) | main text Fig. 1 |
| fig_readout_vs_leverage | readout installed at the carrier vs answer moved, every condition, both models | first page / Fig. 3a / summary |
| fig_source_hidden | carrier-identity effect, clue visible vs replaced, paired items | Fig. 3b / summary |
| fig_question_split | qsplit ladder with flips (a) and the installed readout (b) | Fig. 5 / summary |
| fig_setup | the three sites and the four interventions on the two-hop rendering | page 2 |
| fig_selection_localization | restoration by start block, by sub-region, and the norm-matched controls | Fig. 2 |
| fig_swap_by_position | the paper's swap by position, hybrid and dense | Fig. 4 |
| h3_qsplit, h3_qsplit_dense | the six-row ladder on each model (dense: gate failed, no label) | appendix D |
| h3_dissociation | sum consumer bars: readout vs answer; word consumer carrier-only | form answer on the centrepiece |
| h3_robustness_grid | carrier subsets × donor maps × consumers heatmap | appendix C |
| h3_query_local | reconstruction at the question; is the rebuilt sum used; no operands | §7 support |
| h3_global_conditions | paper-style swap global vs carrier-only; decision-position donors; mask rows | appendix C |
| h3_two_hop | two-hop clue visible vs placeholder | §6–7 support |
| h3_carrier_vs_boundary | difficulty ladder; carrier share vs boundary, every organism | §12 rows 3–4 |
| h3_answer_position_profile | answer-position residual distance by block under each intervention | appendix |
| natural_modulation_conditions | all seven instruction conditions at both windows | §3 |
| source_transfer_by_Lx | transferred fraction by replacement start block | appendix C |
| task_state_orthopanel | interaction I per direction, both windows | §3 support |
| tagged_selection, tagged_categories, scaffold_generality, competition_and_cue | readout extensions | appendix C |
| B1_logprob_moves_not_flips | Δ log P(own) and Δ log P(donor) per condition, both consumers | §6 "moves but does not flip" |
| B2_source_hidden_sums | candidate-set wins per condition; greedy breakdown (10 word, 4 digit, 9 leading digit, 7 hidden, 2 other) | §7 |
| B3_carrier_share_by_organism_and_model | carrier share, three organisms, hybrid vs dense | §6 / summary |
| B4_priming_and_surfacing | maintain / plain mention / mention / absent at both windows; rank-1 surfacing | §3 |
| fig_question_split_dense | qsplit shares side by side; dense hatched, gate failed | §11 dense inset |
| B6_position_additivity | stacked single-position swaps vs the all-positions swap, both models | §8 |
| B7_question_clamp_fp32 | exact question clamp vs norm-matched orthogonal control, report and parity | §7 |
| B8_reconstruction_at_question | donor-sum readout at the carrier vs at the question under each intervention | §7 |

Caveats to carry with the figures: B4(a,b) show condition *levels* with across-word intervals; the paired contrasts (maintain − mention +0.18 / +1.40) are far tighter than the level bars suggest. B6 dense panel: the stacked single-position swaps exceed the all-positions swap (15.1 vs 12.3), and the dense clue-span and all-positions rows exceed the carrier-damage bound.
