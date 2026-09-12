# Figures (ICLR style, regenerated from the committed `*_tables.json` by `common/scripts/make_figures.py`)

Each figure is written as PDF (for LaTeX, `width=\linewidth` for two- and three-panel figures, `0.8\linewidth` for single panels) and PNG. Every plotted number is one that appears in a committed report table, so a figure cannot disagree with its report. Error bars are 95 % cluster-t intervals (cluster = word / unordered pair / triple / sum as in the corresponding report); annotations of the form `k/n` are greedy-flip counts.

| file | what it shows | report |
|---|---|---|
| `natural_modulation_conditions` | Lens presence of the introduced word under the seven instruction conditions, both readout windows (32 bank words, C2/C3) | `natural_modulation_evaluate.md` |
| `source_transfer_by_Lx` | Transferred fraction $C/A$ vs the replacement start block, maintain and mention arms, both windows; the frozen $L_x=36$ marked | `source_transfer.md` |
| `task_state_orthopanel` | Interaction $I$ for the fitted coordinate ĝ against every equal-dose ĝ-orthogonal control direction, both windows | `task_state_modulation_evaluate.md` |
| `tagged_selection` | Transfer of the pointed, unpointed and control sources on four readouts (the discriminating H1 result) | `tagged_selection_evaluate.md` |
| `selection_localization` | (a) restoration vs transplant depth, (b) sub-region decomposition, (c) norm-matched controls | `selection_localization_*.md` |
| `scaffold_generality` | Selection $S$ in all four presentation × wording renderings | `scaffold_generality_tagged.md` |
| `competition_and_cue` | (a) focal-source transfer vs the number of tagged sources, (b) mid-carrier cue re-assignment | `competition_and_cue.md` |
| `tagged_categories` | Transfer of unshown category members and of the label under the pointer | `tagged_categories_select.md` |

The earlier matplotlib-default figures from the individual analysis scripts are kept beside these for provenance.
