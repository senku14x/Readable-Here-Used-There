# H3 figures (ICLR style; `common/scripts/make_figures.py`, numbers from the committed `*_tables.json`)

| file | what it shows | report |
|---|---|---|
| `h3_dissociation` | The centrepiece. (a) Sum consumer: internal J-lens readout vs answer margin, each relative to the source-residual donor, for source donor / carrier donor (≥36, all blocks) / source donor with carrier clamped / random carrier; greedy flips annotated. (b) Word consumer with the matched carrier-only donor. | `computed_sum_consumer_robust.md`, `selection_to_behavior_carrier_only.md` |
| `h3_robustness_grid` | The same answer-margin ratios for every carrier subset × donor map × consumer | `computed_sum_consumer_robust.md` |
| `h3_global_conditions` | Amendment 3: token-level operand donor, consistent global clamp, paper-style lens coordinate swap (global vs carrier-only), decision-position donors; report and parity, relative to the source donor | `computed_sum_consumer_global.md` |
| `h3_answer_position_profile` | Residual distance of the answer position from clean, by block, under each intervention | `computed_sum_consumer_robust.md` |
| `h3_query_local` | (a) donor-sum readout at the carrier vs the question positions under source donor, source donor with carrier clamped, carrier donor; (b) parity margin under the source-donor/carrier-clamped condition with and without the question-site sum clamp (and the orthogonal-plane control); (c) absent-source recipient: report log-odds toward the transplanted sum, with scored-argmax = S counts | `query_local_workspace.md` |

| `h3_two_hop` | The paper's released two-hop items: source vs carrier conditions with the clue visible, and the unanswerable-clue transplant | `two_hop_organism.md` |
| `h3_carrier_vs_boundary` | (a) the difficulty ladder with the boundary held fixed and competence annotated; (b) every organism tested, carrier share against boundary position — the figure that shows the two properties are confounded across organisms and that difficulty does not move the carrier share within one | `recompute_cost_ladder.md` |

Error bars are 95 % cluster-t intervals over the 8 sums (carriers averaged within sum), the 6 triples, the 12 two-hop items, or the 8 items per ladder tier.

- `h3_bridgeswap`: the paper's lens-coordinate swap of a two-hop intermediate (and of the answer word) applied to the clue span, the copied carrier, the question turn, or all positions; share of the full-residual clue-donor ceiling, 95 % cluster-t intervals over 12 items, scored flips annotated. From `two_hop_bridgeswap_tables.json` (Amendment 4, 2026-09-09).
