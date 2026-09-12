# H3 · two_hop_organism stage `bridgeswap` — the paper's lens-coordinate swap on a two-hop intermediate, decomposed by position

**Design:** `H3/design_specs/two_hop_organism.md`, Amendment 4 (registered before the forward). **Run:** 576 forwards, 181 s, run id in `H3/outputs/two_hop_organism/manifest_bridgeswap.json`; raw `raw_bridgeswap.npz`, summary `meta_bridgeswap.json`. Model Qwen3.6-27B (`6a9e13bd`), thinking off, J_NP folded directions, `CoordSwap` over blocks 36–62 (the same band and hook as `computed_sum_consumer` Amendment 3). 12 items × C0–C3 = 48 cells; cluster = item (carriers averaged, df = 11).

## 1. Question

Every causal case study in the workspace paper (§3.1, §3.3, §3.4) swaps lens coordinates "at all token positions". This project's carrier-versus-source asymmetry rested on whole-residual transplants, and the only coordinate swaps run so far moved the *answer word*. This stage applies the paper's §3.3 intervention to the two-hop **intermediate** (e.g. Spain ↔ Canada) and asks which positions carry its effect: the clue span, the copied carrier, or the question turn. The answer-word swap (Madrid ↔ Ottawa) is run at the same positions as the paper's own confound check and as Nanda's "answer swaps dominate" baseline; a swap between two decoy words at all positions is the non-specific control; the all-block clue-span residual donor is the ceiling.

## 2. Result

Endpoint: answer margin log P(swap_answer) − log P(answer) at the answer position, minus clean; share = ratio of item means to the ceiling; flips by scored argmax over the two candidates. Latent shift = J_NP (swap_to − intermediate) readout change at L51–59, at the carrier interior and at the question positions, on the same forwards.

| condition | swapped pair | positions | margin (nats) [95 % CI] | items > 0 | share | flips | latent shift carrier | latent shift question | ΔNLL max |
|---|---|---|---|---|---|---|---|---|---|
| `S_donor0` | full residual, clue span, all blocks | clue | +22.6 [+21.1, +24.1] | 12/12 | 1.00 | 48/48 | +4.84 | +3.44 | +0.041 |
| `int_tail` | intermediate ↔ swap_to | clue → answer (the paper's swap) | +10.4 [+7.8, +13.0] | 12/12 | **0.46** | 16/48 | +2.48 | +1.70 | +0.003 |
| `int_clue` | intermediate ↔ swap_to | clue span | +2.5 [+1.7, +3.3] | 12/12 | 0.11 | 8/48 | +0.74 | +0.47 | +0.005 |
| `int_carr` | intermediate ↔ swap_to | carrier | +1.9 [+1.1, +2.6] | 12/12 | **0.08** | 6/48 | **+2.71** (12/12) | +0.25 | +0.005 |
| `int_q` | intermediate ↔ swap_to | question turn | +5.2 [+3.9, +6.4] | 12/12 | **0.23** | 15/48 | 0.00 | +1.90 | 0.000 |
| `ans_tail` | answer ↔ swap_answer | clue → answer | +14.3 [+9.6, +19.1] | 12/12 | 0.63 | 32/48 | +1.76 | +1.23 | +0.020 |
| `ans_clue` | answer ↔ swap_answer | clue span | +1.5 [+0.8, +2.2] | 12/12 | 0.07 | 2/48 | +0.37 | +0.24 | +0.005 |
| `ans_carr` | answer ↔ swap_answer | carrier | +1.5 [+1.0, +2.0] | 12/12 | 0.07 | 4/48 | +1.42 | +0.12 | +0.002 |
| `ans_q` | answer ↔ swap_answer | question turn | +11.6 [+7.4, +15.7] | 12/12 | 0.51 | 28/48 | 0.00 | +0.97 | 0.000 |
| `rand_tail` | decoy ↔ decoy | clue → answer | +0.1 [−0.05, +0.25] | 10/12 | 0.00 | 0/48 | −0.01 | 0.00 | +0.003 |

Additivity: the three position sets sum to 9.5 nats against 10.4 for the whole tail (intermediate) and 14.6 against 14.3 (answer). Realized per-position swap norms: ≈ 2.3 at the carrier and question, ≈ 4–5 at the clue span. Clean competence 0.98 scored; greedy first token equals the answer word in 20/48 (the greedy often emits an article or a partial token; the scored endpoint is used throughout, as in the full battery). `S_donor0` ΔNLL 0.041 exceeds the registered 0.02 bound, as it did in Amendment 3; every swap row is within it.

Per-item shares of the ceiling (carriers averaged):

| item | pair | int_tail | int_clue | int_carr | int_q | ans_tail | ans_q |
|---|---|---|---|---|---|---|---|
| Barcelona→Toronto | Spain→Canada | 0.64 | 0.08 | 0.06 | 0.28 | 0.93 | 0.72 |
| Lyon→Naples | France→Italy | 0.42 | 0.05 | 0.10 | 0.27 | 0.73 | 0.66 |
| Naples→Barcelona | Italy→Spain | 0.46 | 0.14 | 0.21 | 0.19 | 0.20 | 0.20 |
| Toronto→Lyon | Canada→France | 0.39 | 0.15 | 0.16 | 0.21 | 0.51 | 0.39 |
| Munich | Germany→Japan | 0.54 | 0.09 | 0.08 | 0.27 | 0.30 | 0.22 |
| Osaka | Japan→Germany | 0.63 | 0.17 | 0.09 | 0.27 | 0.82 | 0.66 |
| Cairo | Egypt→Russia | 0.49 | 0.17 | 0.04 | 0.25 | 0.87 | 0.67 |
| Moscow | Russia→Egypt | 0.65 | 0.14 | 0.06 | 0.24 | 0.30 | 0.15 |
| Hungarian | Hungary→Poland | 0.35 | 0.06 | 0.02 | 0.23 | 0.99 | 0.91 |
| Polish | Poland→Greece | 0.47 | 0.10 | 0.06 | 0.32 | 0.78 | 0.66 |
| butter | butter→honey | 0.33 | 0.18 | 0.16 | 0.16 | 0.18 | 0.16 |
| honey | honey→butter | 0.09 | 0.00 | 0.01 | 0.02 | 0.81 | 0.62 |

## 3. Predictions checked

1. **Gate — met.** The paper's intermediate swap moves the answer on every item (0.46 of the ceiling, 16/48 scored flips). The §3.3 intervention reproduces on this organism; it is not the null Nanda reports for the released set, though see 3.
2. **Position split — met.** `int_carr` is 0.18 of `int_tail` (registered bound ≤ 0.3) and `int_clue` is 0.24 of it. The largest single-position-set share is the **question turn** (0.23 of the ceiling, half of the whole-tail effect), on which there was no prior.
3. **Answer swap dominates — met.** `ans_tail` 0.63 > `int_tail` 0.46, 32/48 vs 16/48 flips; this is Nanda's observation on the same model. `ans_carr` is 0.07, not zero; the registered "≈ 0" was slightly too strong.
4. **Non-specific control — met.** The decoy swap is inert (0.00, 0/48).
5. **Readability without use at the carrier — met.** `int_carr` installs the swapped intermediate at the carrier readout as strongly as the whole-tail swap does (+2.71 vs +2.48, 12/12 items) while moving the answer 0.08 of the ceiling; the same swap at the question turn installs nothing at the carrier and moves the answer three times as much.

## 4. Interpretation (calibrated)

- **The paper's intervention works here, and most of its effect is at the question, not at the maintained copy.** Decomposed by position, the all-positions intermediate swap is roughly the sum of its parts, and the question turn carries about half of it; the copied carrier, where the intermediate is continuously readable, carries about a sixth; the clue span, where the entity enters, about a quarter. This is the same shape as the whole-residual results (`two_hop_organism.md` §§2–4) but now for the lens direction the paper itself intervenes on. It converges with the earlier observation that the donor answer is rebuilt at the question positions under a carrier clamp.
- **What it does not show.** It does not show that the carrier copy is unused: 0.08 is small, content-specific and CI-clear, as before. It does not separate "the second hop is computed at the question from the clue's residuals" from "the question re-reads the clue span": both are consistent with the question turn dominating. The clue-span swap is confined to blocks 36–62, and the clue is partly resolved below block 36 on this organism (block-36 boundary 0.58), so `int_clue` under-covers the source; the whole-tail row is the fair comparison to the paper.
- **Relation to Nanda's caveat.** On this model the answer swap is stronger than the intermediate swap at every position set, so his "answer swaps dominate" holds here too; but the intermediate swap is far from null (0.46, 12/12), unlike his released-set result. The difference is plausibly the organism: the clue is in turn 1 behind a copy task and the question never restates it, so the answer cannot be read locally. Both swaps are largest at the question turn, and the answer swap there is output steering by construction; the intermediate swap at the question is not reducible to that (it changes a different token than the one it swaps), which is the paper's own argument, now localized.
- **Scope.** Twelve released items (two are whole-clue paraphrases), four carriers, one model, one band, thinking off; scored-candidate endpoint; no read-site component identified.

## 5. Next decision

The claims table (`computed_sum_consumer.md` §12, `evidence_ledger.md` §E) gains one row: the position asymmetry holds for the paper's own lens-coordinate intervention on a two-hop intermediate, with the question turn the dominant site. The natural follow-up, not run, is the same decomposition on the dense model, and a layer-band sweep of `int_q` against `int_clue` to check the paper's timing argument (intermediate swaps act earlier in depth than answer swaps) position by position.

## 6. Replication on the dense model (Qwen3-32B, `TCSIF_MODEL=qwen3_32b`, same script, 576 forwards, 82 s)

Registered as the natural follow-up in §5 and run the same day. Clean competence 1.00 scored; ceiling +30.9 nats. Share of the ceiling (scored flips), primary / dense; carrier latent shift and ΔNLL max, primary / dense:

| condition | Qwen3.6-27B | Qwen3-32B | carrier latent shift | ΔNLL max |
|---|---|---|---|---|
| `S_donor0` | +1.00 (48/48) | +1.00 (48/48) | +4.84 / +3.54 | +0.041 / +0.207 |
| `int_tail` | +0.46 (16/48) | +0.38 (16/48) | +2.48 / +1.81 | +0.003 / +0.026 |
| `int_clue` | +0.11 (8/48) | +0.21 (11/48) | +0.74 / +0.97 | +0.005 / +0.023 |
| `int_carr` | +0.08 (6/48) | +0.05 (0/48) | +2.71 / +1.91 | +0.005 / +0.018 |
| `int_q` | +0.23 (15/48) | +0.26 (11/48) | +0.00 / +0.00 | +0.000 / +0.000 |
| `ans_tail` | +0.63 (32/48) | +0.52 (24/48) | +1.76 / +1.15 | +0.020 / +0.040 |
| `ans_clue` | +0.07 (2/48) | +0.17 (8/48) | +0.37 / +0.65 | +0.005 / +0.025 |
| `ans_carr` | +0.07 (4/48) | +0.06 (1/48) | +1.42 / +0.92 | +0.002 / +0.019 |
| `ans_q` | +0.51 (28/48) | +0.64 (32/48) | +0.00 / +0.00 | +0.000 / +0.000 |
| `rand_tail` | +0.00 (0/48) | -0.00 (0/48) | -0.01 / +0.04 | +0.003 / +0.035 |

Same shape on the dense model: the paper's intermediate swap works (0.38, 12/12 items), the question turn is its largest site (0.26), the copied carrier its smallest (0.05, 0/48 flips) while the carrier swap installs the swapped intermediate at the carrier readout (+1.91, 12/12); the answer-word swap dominates (0.52; 0.64 at the question); the decoy swap is inert. Differences: the clue span carries more on the dense model (0.21 vs 0.11), consistent with its more complete block-36 boundary (0.97 vs 0.58 in the full battery); realized per-position swap norms are ≈ 4× larger (residual scale), and `int_tail`/`int_clue` ΔNLL reach 0.023–0.026, marginally above the 0.02 bound (reported, not repaired). The dense lens is the partial-fit checkpoint (`replication_qwen3_32b/README.md`); coordinate rows there carry that caveat in addition to the bf16 write-fidelity caveat (`query_local_workspace_clampfix.md` §3), which applies to both models.

## 7. Sequence-log-probability endpoint (stage `bridgeswap_seq`, 2,512 forwards, 655 s) — the headline endpoint from here on

Random inspection (`qualitative_bridgeswap_random_cells.md`) showed the greedy first token is often a subword of a multi-token spelling ("R"+"ome", "Tok"+"yo", "Bud"+"apest") while the candidate-set endpoint of §2 scores single-token spellings only. Per the behavioural-endpoint convention (sequence log-probs for multi-token answers; damage metrics) every condition was rescored with the summed token log-probabilities of both full answer words (four spellings each, logsumexp), the interventions bitwise unchanged. Clean competence is 1.00 on this endpoint (48/48; the earlier 0.98 was the candidate-set artifact).

| condition | seq margin (nats) [95 % CI] | items > 0 | share (seq) | flips (seq) | share (candidate set, §2) |
|---|---|---|---|---|---|
| `S_donor0` | +23.88 [+21.93, +25.83] | 12/12 | **1.00** | 48/48 | 1.00 (48/48) |
| `int_tail` | +9.85 [+7.14, +12.55] | 12/12 | **0.41** | 16/48 | 0.46 (16/48) |
| `int_clue` | +2.20 [+1.46, +2.94] | 12/12 | **0.09** | 0/48 | 0.11 (8/48) |
| `int_carr` | +1.66 [+0.99, +2.33] | 12/12 | **0.07** | 0/48 | 0.08 (6/48) |
| `int_q` | +4.74 [+3.50, +5.98] | 12/12 | **0.20** | 0/48 | 0.23 (15/48) |
| `ans_tail` | +12.91 [+9.76, +16.05] | 12/12 | **0.54** | 29/48 | 0.63 (32/48) |
| `ans_clue` | +1.31 [+0.72, +1.91] | 12/12 | **0.06** | 0/48 | 0.07 (2/48) |
| `ans_carr` | +1.39 [+0.91, +1.86] | 12/12 | **0.06** | 0/48 | 0.07 (4/48) |
| `ans_q` | +10.22 [+7.85, +12.59] | 12/12 | **0.43** | 17/48 | 0.51 (28/48) |
| `rand_tail` | +0.13 [-0.01, +0.28] | 11/12 | **0.01** | 0/48 | 0.00 (0/48) |

The registered prediction holds: the ordering of position sets and the intermediate-versus-answer comparison are unchanged and every share moves by ≤ 0.09. What changes is the flip count for the single-position-set conditions, which falls to 0/48 for `int_clue`, `int_carr` and `int_q` (the candidate-set endpoint had over-counted flips in cells whose own answer is spelled with several tokens); `int_tail` stays at 16/48 and `ans_q` drops from 28 to 17. **Read the position decomposition on margins, not on flips**: a swap confined to one position set moves the answer preference on every item without ever reversing it, and only the paper's all-positions swap (or the answer swap at the question) reverses it. The candidate-set numbers in §2 and §6 are retained for comparison; the dense model's sequence rescoring is in §8 when run.

## 8. Sequence endpoint on the dense model (Qwen3-32B `bridgeswap_seq`, 2512 forwards)

Competence 0.92; ceiling +33.7 nats. Share of ceiling (flips) on the sequence endpoint, primary / dense:

| condition | Qwen3.6-27B | Qwen3-32B |
|---|---|---|
| `S_donor0` | 1.00 (48/48) | 1.00 (44/48) |
| `int_tail` | 0.41 (16/48) | 0.37 (20/48) |
| `int_clue` | 0.09 (0/48) | 0.22 (8/48) |
| `int_carr` | 0.07 (0/48) | 0.04 (4/48) |
| `int_q` | 0.20 (0/48) | 0.19 (5/48) |
| `ans_tail` | 0.54 (29/48) | 0.44 (18/48) |
| `ans_clue` | 0.06 (0/48) | 0.18 (11/48) |
| `ans_carr` | 0.06 (0/48) | 0.06 (4/48) |
| `ans_q` | 0.43 (17/48) | 0.42 (14/48) |
| `rand_tail` | 0.01 (0/48) | -0.01 (4/48) |

The dense model's ordering is unchanged under the sequence endpoint; the figure `h3_bridgeswap` now uses this endpoint for both panels.
