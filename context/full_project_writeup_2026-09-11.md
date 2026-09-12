# Read Here, Used There — complete project report

**Internal report, written 2026-09-11. Covers every experiment run in this repository from 2026-09-06 to 2026-09-11, on both models, with every metric defined, the reason it was chosen, what its numbers mean, and where each result sits on the evidence ladder.** Nothing here is new evidence: every number is copied from a committed report or table (paths given per section, in the reorganised `results/reports/` and `results/tables/` layout), and each withdrawal is stated next to the claim it withdraws. This report supersedes `full_project_writeup_2026-09-09.md`, which stops before the question-turn ladder (Amendments 5 and 6), the exact-write clamp repair, two corrections found on the environment rebuild, and the adversarial study, all of which are included here. Total compute with a recorded count: about 58,400 model forwards (inventory in §13).

---

## 0. The report in one page

### 0.1 Question

A prompt introduces a piece of content — a quoted word, one of three tagged words, a category label, a pair of numbers, a two-hop clue — and then asks the model to copy an unrelated sentence word for word. The copy is teacher-forced, so the visible text is identical across conditions. A later question asks for the content. Three things can differ inside the model between the introduction and the use: how much the content influences the copied sentence's internal state and which content is selected (H1), what holds it across the sentence (H2, not started), and whether the answer draws on the representation our instruments read (H3).

### 0.2 Claims, at the strength the interventions support

1. **Position asymmetry.** In these delayed-answer copying tasks, donor information installed in the residual stream of the copied sentence (the *carrier*) changes the answer much less than the same information installed at the *source* positions, while the source is visible. On the sum organism the source donor moves the report margin +21.2 nats and flips 32/32 answers; the carrier donor, which installs the donor sum at the carrier readout at the same magnitude on three instruments, moves it +1.75 nats and flips 0/32. The carrier's share of the source effect is 0.08 (sums), 0.27 (two-hop facts), ≤ 0.04 (words) on the hybrid model and 0.02, 0.23, 0.015 on the dense control.
2. **Carrier information is used when the source is absent.** With the operands or clue entity removed from the prompt, transplanting a real run's carrier states makes that run's value win the scored candidate set (28/32 sums; 28/40 and 32/40 two-hop items against a 20/40 floor), identity-specifically in both directions, with matched random writes inert.
3. **At the question turn, the effect is carried mostly outside the intermediate's naming plane.** On the two-hop organism, a full-residual donor over the question turn (scoring position excluded) moves the answer +11.19 nats. The component of that donor inside the two-token naming plane of the intermediate carries 0.20 of the effect while installing the J-lens readout as strongly as the full donor; the donor with that plane removed and held at clean carries 0.78. This is a single-model result (Qwen3.6-27B); the dense control shows the same ordering but did not meet the registered gate.

These are differences between interventions at different positions and along different directions. They do not identify the maintained representation, its natural computational role, or a mechanism. Every number carries its scope (§10.3).

### 0.3 What was withdrawn, and stays withdrawn

"The block-36 carrier state is computationally used" (§5.5); "the readable sum is not used; the consumer recomputes from the operands" (§5.5); "the carrier is a broadcast echo by construction"; the causal one-third/two-thirds split of a crossed-margin table (§5.3); the recompute-cost account and the boundary-position account of the arithmetic-versus-fact gap (§6.3, §11.2); "per-cell bf16 rounding up to 2.7 logits" (§10.4, a stale number); and, for the dense model, any label for the question-turn ladder (§6.6).

### 0.4 Relation to the workspace paper

The project responds to Gurnee, Sofroniew, …, Lindsey, "Verbalizable Representations Form a Global Workspace in Language Models" (arXiv 2607.15495, July 2026), which introduces the Jacobian lens (J-lens): a per-layer linear map \(J_\ell = \mathbb{E}[\partial h_{\text{final}}/\partial h_\ell]\) followed by the model's final norm and unembedding, giving a vocabulary-sized readout of any residual vector. The paper's causal case studies (verbal report §3.1, two-hop intermediates §3.3, France→China broadcast §3.4) apply a lens-coordinate swap at every token position across a band of layers. This project is a position-resolved refinement of those functional claims, not a replication: it intervenes at the source positions, the copied-sentence positions and the question positions separately, with matched controls at each, and adds behavioural consumers and a decomposition of the question-turn donor by direction. Nanda's review of the paper, with a replication on the same Qwen3.6-27B, is the second anchor; three of his points recur below: a bare mention primes almost as much as an instruction (paper A.10); on this model answer-word swaps dominated intermediate swaps on the released multi-hop set; and a J-lens reading is variable interpretability, so a readout alone does not say what the model does with the variable.

### 0.5 Evidence ladder and table conventions

Observation → recurring pattern → supported empirical claim (survives the relevant controls) → causal claim (a targeted intervention changes the outcome with nonspecific perturbation ruled out) → mechanistic explanation. Every result carries its level and scope: model, materials, carriers, windows, sample size. Agreement between instruments measured on the same forwards is robustness, never independent evidence. Every interval is a 95 % cluster-t interval unless stated; "8/8" is the sign count over clusters; clusters are words, unordered word pairs, triples, categories, sums or items, never layers, positions, carriers or rotations. Ratios are ratios of cluster means with numerator and denominator visible. Equivalence claims use a 90 % interval inside a pre-registered band. Holm correction is applied across the two readout windows for each estimand.

---

## 1. Model, instruments, conventions and gates

### 1.1 Models

Primary: **Qwen3.6-27B**, revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`, bf16, eager attention, chat template with thinking disabled. A hybrid: 64 blocks, of which 16 are full attention (indices 3, 7, 11, …, 63) and 48 are GatedDeltaNet linear-attention blocks with a carried recurrent state. d_model 5120. Loads in 54 GB; ≈ 0.3 s per forward with all 64 block outputs recorded.

Control: **Qwen3-32B**, revision `9216db5781bf21249d130ec9da846c4624c16137`, dense, 64 blocks, d_model 5120, every block full attention. Same depth and width, so block indices, hooks and materials transfer. Used for the replication in §11 and for Amendment 6 (§6.6).

Why this model: the paper's open replication was on it; open J-lenses exist for it; and it has a genuine recurrent channel, which makes "persistence versus re-retrieval" a three-way question rather than a two-way one. The dense model is the control for exactly that channel.

### 1.2 The five instruments

The project never speaks of "the lens". Five instruments are kept apart by name:

| key | name | what it computes | why it is there |
|---|---|---|---|
| `np` | **J_NP** | Neuronpedia Jacobian lens for Qwen3.6-27B (n = 1000 prompts; SHA-256 `1718c8c5…`). Score of vocabulary token v at block output h: \(z_v = w_v^\top(\gamma \odot J_\ell h)/r\), on the model's own path (`final_norm(J_l h) @ W_U^T` in bf16). | Primary instrument; the paper's method. |
| `cbj` | **J_CB** | Camila Blank's independently fitted J-lens (`a036b358…`, n = 25). | Robustness: a second fit of the same construction; natural modulation only. |
| `cbr` | **R_CB** | Camila Blank's R-lens (`fe4d0b6a…`), a different readout construction. | Robustness with a different failure mode; natural modulation and the adversarial study. |
| `s_p` | **RESID_P** | A plain-sentence residual axis, fitted per word from 8 neutral templates and validated on 4 held-out templates. Presence = projection on the unit direction from the decoy centroid to the word's centroid, with a centering constant; pair axis = unit(μ_Y − μ_X). Refit per run. | An instrument that never touches the lens. An effect on J_NP only is a lens artefact until shown otherwise. It is not orthogonal to J directions and is never called "non-J information". |
| `z_out` | **LOGITS** | The model's own output log-probabilities: at carrier positions, the margin of the target over decoys; at consumer positions, the answer log-probability. | The model's native readout, and the behavioural endpoint in H3. |

For the dense model, J_NP is the released Qwen3-32B fit checkpoint (`jacobian_sum`, `n_done = 80`) finalised locally as \(J = \text{jacobian\_sum}/n_{\text{done}}\). The finalised file was lost on an instance recycle on 2026-09-11 and regenerated from the same pinned checkpoint (source SHA `30540415…` verified); the byte-level hash of the regenerated file differs from the 2026-09-09 file (serialisation), the construction is identical, both hashes are in the registry, and the file is mirrored to `senku21x/tcsif-outputs/lenses/`. Every dense-model contrast is within-model, so lens quality (n = 80 against 1000) is a scope note on absolute magnitudes, not a confound on ratios — with one exception noted in §6.6, where the split of a donor into a naming plane and its complement depends on the lens directions themselves.

Two float paths are saved for J_NP: the bf16 model path (primary) and a float32 diagnostic \(z = n/r\) with numerator \(n_v = w_v^\top(\gamma\odot J h)\) and RMS \(r = \sqrt{\|Jh\|^2/d + \epsilon}\). **Corrections on record:** this architecture's RMSNorm gain is `1 + weight`, not `weight` (the first pilot's float32 diagnostic was scaled by about one half until this was caught); and the committed instrument-gates value for the float32-versus-implementation discrepancy, 2.74, was measured before that fix — rerun on the rebuilt environment on 2026-09-11 it is **0.019**, with every other gate value reproduced (§10.4). Folded naming direction of token v at layer ℓ: \(a_{v,\ell} = J_\ell^\top(\gamma\odot w_v)\). The gradient of the normalised score is \(\nabla_h z_v = a_v/r - n_v J^\top J h/(d r^3)\), so a write along \(a_v\) does not produce an exactly predictable change in \(z_v\); every write is measured after the fact.

### 1.3 Readout conventions

- **Positions.** Interior carrier positions = the teacher-forced assistant carrier span trimmed by two tokens at each end. Positions are averaged within a sequence first, then carriers within an item, so a longer carrier never counts for more.
- **Windows.** Two co-primary windows over block outputs: **L48–50** (the default; linear-attention outputs) and **L51–59** (promoted to co-primary in Package 1, before any Package 2 forward, because rank-1 surfacing and near-complete transfer both live there; 51 is a full-attention block). L24–59 is reported as a wide companion. Holm across the two.
- **Presence** of X: \(s_J(X) = z_X - \text{mean}_{d\in D} z_d\) over eight frozen decoys (dragon, drawer, forest, fork, hammer, horse, knife, lion; `drawer` excluded whenever direct carrier D5 is in play). In the tagged, category and two-hop experiments the decoys are the eight fitting words anchor…bridge.
- **Pair margin** for a counterfactual X→Y: \(m^{X\to Y} = \mathbb{E}_{(\ell,t)\in W}[z_Y - z_X]\); the decoys cancel.
- **Prominence.** Full-vocabulary rank of X at every (layer, position); \(r_{\min}\) is the minimum over the window (so "best rank anywhere", never "typical prominence"), \(f_{10}\) the fraction of slots with rank ≤ 10, and the rank-1-anywhere rate.
- **Numerator and RMS** are saved separately so a score change can be decomposed as \((N'-N)/r + N'(1/r' - 1/r)\); one exact ordered decomposition, not a causal partition.

### 1.4 Intervention primitives

All hooks act on **block outputs** (the residual stream after block ℓ), batch size 1, in float32 then cast back to the model dtype.

- `SpanWriter`: sustained replacement of chosen positions' block outputs with a donor run's states (or any precomputed target) for every layer ≥ L_x (or all 64). Read-back error is exactly 0 by construction in the fp32 regime and ≤ bf16 rounding otherwise.
- `StateMove`: \(h' = h + \alpha_t \hat g\), where \(\hat g\) is a unit direction and \(\alpha_t\) a clean-derived scalar chosen so the coordinate reaches a target level. Realized write measured: \(\rho = \|\delta_{\text{real}}\|/\|\delta_{\text{req}}\|\), \(\kappa = \cos(\delta_{\text{real}}, \delta_{\text{req}})\); gate ρ ∈ [0.9, 1.1], κ ≥ 0.99.
- `AddVector`, `EraseToReference`: fixed vector add; erase a coordinate to a reference level.
- `CoordSwap` (the paper's intervention): with V = [v_s, v_t] two unit lens directions, c = V⁺h, \(h' = h + V(\sigma(c) - c)\), σ swapping the two coordinates; the orthogonal complement untouched. `CoordClamp` pins the two coordinates to their clean values. `CoordClampMatched` rescales an orthogonal-plane clamp to the naming clamp's per-position write size and records the post-cast realized write.
- `Fp32Residual` (from 2026-09-10): a forward hook on block 35 upcasts its output to float32, so blocks 36–63 carry a float32 residual while the forward runs under bf16 autocast (matmuls and kernels see the same bf16 operands); only residual additions and hooked writes change precision. Used for every coordinate-level stage from `clampfix32` on, and for the whole of Amendments 5 and 6.
- `AttnReadBlock`: masks the consumer positions' attention to the source span at every full-attention block, with the maximum leak recorded (0.0 in every run).

### 1.5 Gates applied before any outcome is read

1. **Rendering.** The whole conversation is tokenised once with the chat template; the source span, both carrier occurrences, the query span and the answer position must decode to the intended strings; no padding.
2. **Same-source replacement is bitwise equal to the clean run**, and **layers below L_x are identical between the future-X and future-Y runs** (asserted per cell).
3. **Realized write** ρ/κ on every directional write; read-back error on every span write.
4. **Damage.** Carrier ΔNLL (bound 0.02 nats/token in H3; ≤ 0.01 observed in H1) and top-1 retention ≥ 0.95 of the clean next-token predictions.
5. **Donor geometry.** Donor and recipient spans must have identical token count and indices; a mismatch is flagged and the pair excluded, never cropped (orange–guitar was excluded: `guitar` is two pieces inside quotes).
6. **Competence** for any consumer: ≥ 0.9 clean accuracy in the scored arm before an intervention is interpreted.

Instrument gates (`common/configs/instrument_gates_result.json`, rerun 2026-09-11; the 2026-09-06 file kept alongside): bitwise repeat, empty-patch and same-source identity all true; lens subprojection max abs diff 0.0156; float32-vs-implementation diff 0.019; median residual RMS 0.67; `StateMove` realized ρ 1.002, κ 0.998; **sequence-length nondeterminism** up to 0.33 lens logits per cell for a one-token change in sequence length (so cells of different token length are never compared as if exact; every contrast is within a fixed rendering); all 16 fit words and 8 calibration words single-token with a leading space; eight of the sixteen categories lack four single-token unshown members under this tokeniser and were never used.

### 1.6 Statistics

Cluster-t intervals over the design's unit (df = clusters − 1), with per-cluster values and sign counts printed in every table. Ratios are ratios of cluster means with paired-bootstrap intervals (B = 2000, seed 20260907); per-cell ratios are never averaged. Equivalence uses two one-sided tests at 5 % (a 90 % interval inside ±ε), with ε frozen before evaluation at 20 % of the relevant positive control. A "random-column floor" companion compares the target column's change with the change of 64 random vocabulary columns under the same intervention.

### 1.7 Materials discipline

Fitting words (16), calibration words (8) and decoys (8) are fixed; evaluation is on two banks of eight word pairs (32 words) on held-out carriers C2/C3; pilots use calibration words on C0/C1. Every exposure of a material to an earlier analysis is disclosed in the report that reuses it. Nothing is replaced on the basis of a model outcome.

---

## 2. Organisms: exact prompts, rendered

All prompts are rendered through the Qwen chat template with `enable_thinking=False`, which inserts an empty `<think>\n\n</think>\n\n` block before the assistant text. The assistant turn is the carrier, teacher-forced; nothing is generated in any H1 experiment. Rendered examples use carrier C2 and are byte-exact.

### 2.1 Controlled word-copy organism

Maintain arm, X = cat, carrier C2 (69 tokens; source content at token 8, quote tokens 7 and 9; user carrier tokens 28–44; assistant carrier tokens 53–69; interior positions 55–66):

```
<|im_start|>user
Here is the word "cat". Keep that word in mind while you copy the following text exactly, word for word:

Dust settled slowly over the village square while two birds watched from the old doorway<|im_end|>
<|im_start|>assistant
<think>

</think>

Dust settled slowly over the village square while two birds watched from the old doorway
```

The other tails, each replacing `Keep that word in mind while you copy the following text exactly, word for word`:

| condition | tail after `Here is the word "cat"` |
|---|---|
| mention (the registered control) | `. That word occurs one time. Now copy the following text exactly, word for word` |
| ignore | `. That word is irrelevant here. Now copy …` |
| do_not_think | `. Do not think about that word. Now copy …` |
| never_think | `. Never think about that word. Now copy …` |
| plain_mention | the whole head is `cat. Now copy the following text exactly, word for word` |
| absent | `A single passage of text is given below. Now copy the following text exactly, word for word` |

The carrier is repeated in the user turn because the copy instruction needs the text to copy; the "instruction region" between the tag and the assistant carrier therefore contains the user-side carrier (§4.6, Amendment 3).

### 2.2 Direct organism (the paper's wording)

The user message is only the phrasing; the carrier appears only in the assistant turn. Primary pair `Hold {X} in mind as you write.` versus `{X} came up in conversation.`; a copy-adapted variant appends ` Now copy the following text exactly, word for word:\n\n{carrier}`. Direct and copy-adapted results are never pooled. Direct carriers D0–D19 (eight sentences), fit on D0/D3/D5/D8, evaluate on D11/D14/D16/D19.

### 2.3 Tagged selection organism

Three quoted words with fixed labels (A)(B)(C); the pointed tag T is the only token that differs between arms (position 30 in the standard rendering), and the source words all precede it.

```
Here are three words: (A) "cat", (B) "dress", (C) "snake". Keep the word tagged B in mind while you copy the following text exactly, word for word:

Dust settled slowly over the village square while two birds watched from the old doorway
```

Control arm tail: `. Those words occur one time. Now copy the following text exactly, word for word`. Each triple is rendered in its three cyclic rotations so every identity occupies every ordinal slot once; relevance is indexed by identity after rotation averaging. Mid-carrier cue (competition experiment): ` Actually, keep the word tagged {T2} in mind instead. ` inserted at the word boundary nearest the carrier midpoint, in both the user's and the assistant's copy. The four presentation × wording renderings of the scaffold-generality experiment keep this head and vary only quoted vs bare words, and `Keep the word tagged T in mind while you copy …` (copy wording, control `Those words occur one time`) vs `Hold the word tagged T in mind as you write. Now copy …` (directed wording, control `Those words came up in conversation`).

### 2.4 Tagged categories

```
Here are three categories: (A) "birds", (B) "fish", (C) "tools". Keep the category tagged A in mind while you copy the following text exactly, word for word:

Several boxes of files were moved to the archive room, …
```

No member or exemplar ever appears in the prompt (asserted per cell). The source intervention replaces the quoted label span with a donor category's block outputs from block 36 onward, geometry-matched across superclasses (animal ↔ artifact, e.g. fish → tools); it is an activation-level replacement, not a lens-coordinate swap, and only the six 3-token labels enter the replacement set. Scored members (K = 4 per category, single-token, unshown): birds {owl, duck, goose, pigeon}, fish {cod, carp, bass, perch}, insects {beetle, moth, fly, mosquito}, tools {hammer, saw, drill, axe}, vehicles {car, bicycle, motorcycle, scooter}, furniture {desk, bed, stool, dresser}; mammals and vegetables are readout-only (their quoted labels are 5 and 4 tokens). Carrier C2 is excluded for every category because it contains "birds". Carriers C0, C1, C3.

### 2.5 Computed sums

```
Here is the pair "two and five". Keep their sum in mind while you copy the following text exactly, word for word:

Dust settled …
```

Control tail `. That pair occurs one time. Now copy …`. Eight rows (sum; A-addends; same-sum B-addends): seven (two, five | three, four); eight (two, six | three, five); nine (two, seven | four, five); ten (two, eight | three, seven); eleven (three, eight | four, seven); twelve (four, eight | five, seven); thirteen (five, eight | six, seven); fourteen (six, eight | five, nine). Different-sum donor for row i = A-addends of row (i+3) mod 8 (always opposite parity); same-sum sibling = row i's B-addends. Every number word two…twenty is single-token. The pair span is 5 tokens for every row, so donor geometry always matches.

### 2.6 Consumers

Consumers are second user turns appended after the teacher-forced carrier; the answer is scored at the first token of the new assistant turn (the last position of the rendering). Rendered example, sum organism with the parity consumer (97 tokens; pair span 7–11; assistant carrier 55–71; query span 76–96; answer position 96):

```
… Dust settled slowly over the village square while two birds watched from the old doorway<|im_end|>
<|im_start|>user
Is their sum even or odd? Answer even or odd.<|im_end|>
<|im_start|>assistant
<think>

</think>

```

Consumers used: the word codebook (`Code: cat = M, dress = B, …. Using the code, give the letter for the word you were instructed to keep in mind. Answer with the letter only.`, six entries covering the three sources and their three donors, letters from B D F H K M Q V with entry order and letter assignment permuted independently, seeded per cell); the sum report (`What is the sum of the pair? Answer with one word.`); parity (above); "greater than ten" (sub-competent, not used); the two-hop question (`Complete the fact from the clue you were given, using one word.`, chosen so it never restates the clue); and the early/late mapping query (`Using the code, what is the letter for the word introduced in the first message? Answer with the letter only.`).

### 2.7 Early versus late mapping

Early: the codebook precedes the source in turn 1 (`Code: cat = M, dress = B, snake = K, turtle = Q, airport = F, fish = V, library = D, toy = H.\nHere is the word "cat". Keep that word in mind …`), and turn 2 is the query alone. Late: turn 1 is the maintain prompt alone and turn 2 is `Code: ….\n` followed by the query. `early_unusable` (Amendment 1): a codebook over eight other words, length- and structure-matched, so the target is absent and unmapped. Codebooks cover the eight words of the target's bank half; two seeded mappings per word.

### 2.8 Two-hop organism (the paper's released materials)

Items from the paper's repository (`anthropics/jacobian-lens` @ 581d398, `data/experiments/probe-swap.json`), filtered mechanically to single-token intermediate, swap_to, answer and swap_answer with equal token counts (40 of 90 survive), then to the twelve with a released same-category clue for the swap entity (city→capital, city→language, language→capital, food→animal). Example: clue "The capital of the country where Barcelona is located" (intermediate Spain, answer Madrid); donor clue "… where Toronto is located" (Canada, Ottawa). Ten items differ from their donor in exactly one entity token; two (butter/honey) are whole-clue paraphrases and are excluded from the unanswerable-clue stage.

```
<|im_start|>user
Here is a clue: The capital of the country where Barcelona is located. Keep the answer to the clue in mind while you copy the following text exactly, word for word:

Dust settled …<|im_end|>
<|im_start|>assistant
<think>

</think>

Dust settled …<|im_end|>
<|im_start|>user
Complete the fact from the clue you were given, using one word.<|im_end|>
<|im_start|>assistant
<think>

</think>

```

The clue span is tokens 8–16; the question turn `q` runs from the end of the carrier to the answer position (107); `q_pre` is `q` without the answer position. The absent-clue rendering replaces the entity by the single-token placeholder `X` with identical length and spans.

### 2.9 Carriers

Controlled: C0 "The committee reviewed the annual budget and approved funding for several new community programs before the long meeting finally adjourned." C1 "After a brief announcement the passengers boarded quietly and the doors slid shut, and soon the whole platform stood empty and silent." C2 "Dust settled slowly over the village square while two birds watched from the old doorway" (no terminal period). C3 "Several boxes of files were moved to the archive room, and the clerk updated every label, checked the totals twice, and locked the cabinet before leaving for the night." C0/C1 are fitting carriers, C2/C3 held out. Words occurring in a carrier are never scored as absent-from-carrier targets in that combination.

---

## 3. H1, Package 1: natural modulation and source transfer

### 3.1 natural_modulation — does the instruction change readability at all?

**Why first.** The paper's appendix A.10 found that a bare mention of a word primes it almost as strongly as an instruction to think about it. If maintain ≈ mention at the readout, the "task-conditioned" framing rests on transfer effects rather than on a natural readout difference. This is the cheapest decisive fact on the organism.

**Design.** Seven conditions of the controlled organism (maintain, mention, plain_mention, ignore, do_not_think, never_think, absent) plus the direct organism's primary pair in both renderings. Pilot: 8 calibration words × C0/C1 (168 forwards). Evaluate: 32 bank words × C2/C3 (648 forwards). Cluster = word. Every instrument.

**Estimand.** \(D_J(X) = \bar s_J(X \mid \text{maintain}) - \bar s_J(X \mid \text{mention})\), every pairwise condition contrast at both windows, prominence statistics, damage.

**Results (evaluation scale, `H1/results/reports/natural_modulation_evaluate.md`).**

| contrast, J_NP | L48–50 | L51–59 |
|---|---|---|
| maintain − mention | +0.18 [+0.07, +0.30], 23/32 | +1.41 [+1.26, +1.55], 32/32 |
| maintain − plain mention | +0.03 [−0.14, +0.20], 19/32 (null) | +1.40 [+1.22, +1.59], 32/32 |
| mention − plain mention | −0.15 [−0.27, −0.03], 14/32 | 0.00 [−0.16, +0.16] |
| plain mention − absent | +0.58 [+0.43, +0.73], 29/32 | +1.14 [+0.98, +1.29], 32/32 |
| ignore − mention | −0.35 [−0.46, −0.25], 4/32 | −0.57 [−0.65, −0.49], 0/32 |
| do_not_think − mention | −0.25, 8/32 | −0.31, 5/32 |
| never_think − mention | −0.15, 12/32 | −0.17, 11/32 |

Other instruments at L51–59, maintain − mention: J_CB +0.91 (32/32), R_CB +0.85 (32/32), RESID_P +1.28 (32/32), LOGITS +1.77 (32/32). Prominence over L24–59: rank-1-anywhere rate maintain 0.56, mention 0.03, plain mention 0.03, absent 0.00; median best rank maintain 1, mention 32, absent 916. Direct organism (hold − conversation) at L48–50: direct +0.85 (30/32), copy-adapted +1.37 (32/32); the 8-word pilot had the direct contrast null (+0.20, 5/8), which resolved at n = 32. Carrier NLL is 0.000 in every condition.

**What the numbers mean.** A presence score of +1.4 is the target word's lens logit above the mean of eight decoys, in the model's own output-logit units after the Jacobian transport. At L48–50 the maintain effect is tiny and equals a bare mention; at L51–59 it is large, and so is surfacing: the introduced word reaches rank 1 in the 248k vocabulary somewhere in L24–59 in 56 % of maintain cells and 3 % of mention cells, always at layers 51–59 and at function-word positions. The registered control ("occurs one time") sits below a bare mention at L48–50, so it is a mild suppressor, not a neutral baseline; plain mention and absent are carried as co-primary references everywhere after this. "Never think about that word" lowers the mean while surfacing the word at rank 1 in a few cells: the white-bear effect the paper reports.

**Level.** Supported empirical claim at evaluation scale: the maintain instruction raises the readability of the introduced word above the mention control and above every suppression tail, on five instruments, but not above a bare mention at the default window. Strongest surviving alternative: most of the effect is context priming; only the late-window excess and the surfacing are instruction-specific.

**Qualitative.** At the middle interior token of C2, the top-10 J_NP list at layers 23–47 is punctuation and control tokens in every condition; at layer 51 it fills with number words (two, zwei, 两只), at 59–62 with "two", "birds", "cats", and under maintain "cat" reaches rank 3 at block 62 while under mention it stays at 87. The instrument reads the copied text first and the maintained word on top of it.

### 3.2 source_transfer — does replacing the source's states move the later readout, and from which layer?

**Design.** Geometry-matched calibration pairs (orange, tiger), (guitar, mountain), (diamond, castle), both directions, maintain and mention arms, C0/C1; sustained replacement of the quoted span's block outputs with the arm-matched clean donor from every layer ≥ L_x, for L_x ∈ {23, 28, 32, 36, 40, 44}; same-source replacement as the bitwise gate; 192 forwards. Cluster = pair (n = 3).

**Estimands.** Natural contrast \(A = m(\text{clean Y}) - m(\text{clean X})\) (the positive control); transfer \(C(L_x) = m(\text{swap}) - m(\text{noswap})\); the fraction C/A.

**Results (`source_transfer.md`).** J_NP maintain: A = +0.84 at L48–50 and +4.03 at L51–59. C/A at L48–50 falls with L_x: 0.84 (23), 0.74 (28), 0.68 (32), **0.52 (36)**, 0.33 (40), 0.35 (44). At L51–59 nearly flat: 0.98, 0.97, 0.97, **0.95 (36)**, 0.92, 0.92. RESID_P L48–50: 0.87 → 0.49 (36) → 0.50; L51–59: 0.98 → 0.93 → 0.92. LOGITS 0.99 at every L_x. Maintain transfers more than mention at every L_x (D = C_M − C_N: +0.21 at L_x = 36, L48–50, 3/3; +2.02 at L51–59). Prominence after the swap at L_x = 36, maintain: donor Y rank-1 rate 0.58, source X 0.00 (clean: X 0.50, Y 0.00). Damage ΔNLL ≤ 1e-4, top-1 retention 1.000.

**What the numbers mean.** Half of what the L48–50 readout carries about the source arrived at the carrier before block 36; almost everything the L51–59 readout carries is read from the source at or after block 44. The late window is dominated by late reads of the span, the early window mixes earlier-arrived and later-read content. This is the fact behind the two-window convention and behind every later boundary discussion.

**Decision (frozen in `package1_decisions.md`).** L_x = 36; state site block 35; both windows co-primary; cross-rendering tolerance 0.33; damage bound; geometry-matched pair rule.

**Level.** Causal claim (source causality) at pilot scale, reproduced inside the evaluation-scale task-state run (A at L_x = 36: +0.07, 12/16 at L48–50; +2.38, 16/16 at L51–59). No foreign-content damage-only donor was run; that is the standing gap on this row.

---

## 4. H1, Package 2 and extensions: task state, selection, categories, scaffold, localisation, sums, mapping

### 4.1 task_state_modulation — does a fitted task coordinate change future source influence?

**Why.** H1's core claim: a manipulable task-associated state, moved *before* the source counterfactual begins, changes the later response to source information. The temporal ordering is the identification strategy: the state is moved at block 35 on carrier positions, the source is replaced only from block 36, and the runs are asserted bit-identical through block 35.

**Fitting.** For each of the 16 fitting words, \(d_c\) = mean interior block-35 residual under maintain minus under mention (C0/C1 pooled); \(G = \text{mean}_c d_c\); \(\hat g = G/\|G\|\); \(v_c = d_c - G\). ‖G‖ = 7.77; split-half cosine 0.989.

**The move.** \(h'_{35,t} = h_{35,t} + \alpha_t \hat g\), with \(\alpha_t = L^* - \hat g^\top h_{35,t}\) and \(L^*\) the recipient word's own opposite-arm natural level (the donor identity never enters the dose). Factorial per directed pair, arm, carrier: {clean, moved} × {noswap, swap36}.

**Estimands.** \(C_k(q,a) = m_k(\text{swap}) - m_k(\text{noswap})\); \(A_k = C_k(0,M) - C_k(0,N)\); \(\Delta C_M\), \(\Delta C_N\); the interaction \(I = \tfrac12[-\Delta C_M + \Delta C_N]\). Prediction: ΔC_M < 0 and ΔC_N > 0 (reciprocal). Also the no-swap shift, a dose series ×0.5/×1/×2, and a control panel of 12 directions at exactly the same signed α_t: 4 isotropic, 4 covariance-matched, 2 leading background PCs, 2 unrelated plain-sentence axes.

**Pilot (3 pairs, C0/C1, 744 forwards).** I = +0.126 [+0.001, +0.252] (3/3) at L48–50, +1.07 at L51–59, RESID_P +0.033/+1.03, LOGITS +1.96; I/A 0.5–0.7; dose monotone; ρ 1.000–1.001, κ ≥ 0.9998; damage nil; far above the 64-random-column floor (p95 0.005). But the two panel directions with the largest cosine to ĝ (pc01, cos 0.30; cov01, cos 0.18) reproduced 90–97 % of I with the same reciprocal signs.

**Orthopanel (Amendment 1; same cells, 984 forwards).** The 12 directions with their ĝ component projected out (|cos| < 1e-4, asserted) plus 4 covariance directions sampled in the ĝ-orthogonal complement, and native-level rows for pc01/cov01. Registered bar: max |I_perp| < 0.5 |I_ĝ| on J_NP at both windows. Outcome: **fails at L48–50** (cov01_perp 0.096, pc01_perp 0.095 against ĝ 0.126; 3 of 16 orthogonal directions ≥ half of ĝ, six reciprocal 3/3), **passes at L51–59** (largest reciprocal orthogonal 0.35 against 1.07). The ĝ rows reproduced the pilot bitwise (48/48 arrays). A first run of this stage saved no RESID_P arrays because of a stage-name check in the loader; kept as `raw_orthopanel_noresid_run1.npz`, unreported, stage re-run.

**The shared consequence.** Across all 19 directions, the interaction I is predicted by the direction's effect on the resident readout with no source change, ½(Δm_M − Δm_N): r = 0.97 at L48–50, 0.999 at L51–59. Algebraically ΔC_M = shift(swap) − shift(noswap), so any direction that scales the readout of whichever word is currently sourced produces exactly the reciprocal signature.

**Evaluate (16 bank pairs, C2/C3, 5,504 forwards).** I(ĝ): J_NP +0.124 [+0.100, +0.149] (16/16) at L48–50, +0.954 [+0.848, +1.059] (16/16) at L51–59; RESID_P +0.038 / +0.740; LOGITS +1.84; Holm p < 0.001; dose monotone (ΔC_M −0.051 / −0.077 / −0.098 at ×0.5/×1/×2); ρ 0.999–1.001; random-column floor p95 0.004. The bar fails at L48–50 on J_NP (strongest orthogonal direction 60 % of ĝ) and RESID_P (53 %); passes at L51–59 on J_NP and LOGITS (40 %) and fails on RESID_P (71 %). The shared consequence holds: r = 0.95 / 0.998 (J_NP), 0.85 / 0.996 (RESID_P), 0.999 (LOGITS).

**What the numbers mean.** I = +0.12 means that moving the fitted coordinate from the maintain level to the mention level before the source swap lowers the incremental transfer of a block-36 source replacement by 0.08 lens logits, and moving it the other way raises it by 0.17, averaged as ½ their difference. This is real, reciprocal, dose-monotone and specific to the named column. It is not specific to ĝ: directions with no ĝ component do the same in proportion to what they do to the word already present. The move also raises the mention arm's rank-1 surfacing from 0.00 to 0.50. The parsimonious account is a **readout gain**: ĝ scales the readability of whatever word is sourced, resident and incoming alike.

**Level.** Causal claim on the lens margin; the interpretation "task state / controller" is not supported and the "readout gain" reading is. This deflationary verdict motivated the next experiment: a gain and a selection make identical predictions with one source and different ones with three.

### 4.2 tagged_selection — does the instruction select which source is carried?

**Design.** Pilot: 4 triples of exposed words, C0/C1 (1,536 forwards). Evaluate: 8 triples from the 32 bank words, C2/C3 (3,840 forwards). Three rotations; arms pointed A/B/C and control; each source j replaced from block 36 by a donor from the next triple at the same slot (geometry asserted); same-source gate; layers < 36 asserted. Cluster = triple.

**Estimands.** \(C_j(r)\) = transfer of source j under relevance r. Selectivity \(S = \mathbb{E}_j[C_j(j) - \mathbb{E}_{r\neq j} C_j(r)]\); suppression \(Q = \mathbb{E}_j[C_j(r\neq j) - C_j(\text{control})]\); instruction gain \(U = \mathbb{E}_j[C_j(j) - C_j(\text{control})]\); natural selectivity \(S_{\text{nat}}\); an output-disposition screen. Secondary: ĝ moved to the control level under each pointed arm with the profile index \(P\) (0 = uniform scaling); a native pointed-minus-control direction d_shared; a native pointer contrast d_pointer.

**Results, evaluate (`tagged_selection_evaluate.md`).**

| instrument, window | pointed C(self) | unpointed C(other) | control C | S | Q | U |
|---|---|---|---|---|---|---|
| J_NP L48–50 | +0.48 | +0.05 | +0.12 | **+0.43 [+0.34, +0.53], 8/8** | −0.07 [−0.11, −0.03], 0/8 | +0.36 |
| J_NP L51–59 | +5.41 | +1.31 | +1.61 | **+4.10 [+3.76, +4.44], 8/8** | −0.31, 0/8 | +3.79 |
| RESID_P L48–50 | +0.19 | −0.01 | +0.01 | +0.20, 8/8 | −0.02, 0/8 | +0.18 |
| RESID_P L51–59 | +5.93 | +0.33 | +0.49 | +5.60, 8/8 | −0.16, 0/8 | +5.44 |
| LOGITS | +9.22 | +4.64 | +5.29 | +4.58, 8/8 | −0.65, 0/8 | +3.93 |

S_nat (no intervention): +0.35 / +2.11 (8/8). Rank-1-anywhere: pointed 0.95, unpointed 0.03, control 0.15. Output-disposition medians 614 / 1873 / 1592 (screen passes). Damage max ΔNLL 0.0002. Directions: ĝ scales pointed by 0.89 and unpointed by 0.87 (L48–50), 0.86 / 0.96 (L51–59), 0.88 / 0.94 (LOGITS); P +0.02 [−0.13, +0.17] (2/8). d_shared (native) scales pointed by 0.68 and unpointed by 1.01 at L51–59 (P −0.33, 0/8); the pilot-fit d_shared (cos 0.85 with the native, identity holdout) 0.70 / 0.96. d_pointer A→B under pointed A: at L48–50 raises B (+0.105, 8/8) with A slightly down; at L51–59 and on LOGITS it raises A more than B.

**What the numbers mean.** With the tag on B, replacing B's span moves the readout by 0.48 lens logits at L48–50, replacing A's or C's by 0.05, and with no pointer at all by 0.12: the instruction amplifies the pointed source and pushes the unpointed ones below the no-pointer baseline. U ≈ S: the instruction's whole effect lands on the pointed source. ĝ takes about 10 % off every source alike (a uniform gain); a natively fitted pointed-minus-control direction takes 30 % off the pointed source and nothing off the others (a selective gain that transfers to held-out identities); a pointed-B-minus-pointed-A contrast is not an address.

**Ordinal breakdown (analysis-only, `tagged_selection_ordinal.md`).** S is CI-clear 8/8 at every slot, but the pointed transfer is lowest when the pointed word sits first (slot 3 − slot 1: +0.19 at L48–50, +1.54 at L51–59, 8/8), and under the control arm the ordering reverses at the late window (−0.44, 0/8). Slot is confounded with distance to the tag and to the carrier; no intervention separates them.

**Level.** Causal claim, evaluation scale, the discriminating H1 result: the instruction selects among sources; "gain on whichever word is sourced" is rejected as the account of the instruction. Scope: quoted copy organism with a tag head, this readout; nothing about behaviour.

### 4.3 competition_and_cue — set size and a mid-carrier switch

**Design (1,952 forwards).** Competition: nested sets k ∈ {1, 2, 3, 4, 6} from four six-word sets, focal word first or last (counterbalanced), focal and first distractor replaced from block 36, under the focal's pointer and under control; cluster = set (n = 4). Cue: the 8 triples, pointed-A arm, cue at the carrier midpoint in both copies, conditions switch→B, same-tag→A, none; readout on post-cue interior positions; cluster = triple.

**Results.** Pointed focal transfer by k (J_NP L48–50): 0.21 (k = 1), 0.50, 0.43, 0.38, 0.40; at L51–59: 2.2, 5.5, 5.1, 4.3, 5.4; S CI-clear 4/4 at every k ≥ 2. Focal under no pointer: 0.17, 0.21, 0.15, 0.09, 0.05 (dilutes). Cue, switch minus same-tag at L51–59: C_A −1.57 [−2.06, −1.08] (0/8), C_B +0.81 [+0.37, +1.24] (8/8), (C_B − C_A) +2.37 (8/8); LOGITS C_A −6.98, C_B +2.26; at L48–50 the switch lowers both sources relative to same-tag. The same-tag cue is not neutral (relative to no cue it lowers A by −2.07 and raises B by +0.37 at L51–59), which is why switch − same-tag is the registered contrast.

**What the numbers mean.** Selective transfer of the pointed source is roughly flat from two to six competitors, while an unselected source loses about three quarters of its transfer over the same range. Not a capacity result: one selected item with more distractors does not test simultaneous maintenance, and no equivalence test was run on the flatness. A textual re-instruction mid-carrier redirects transfer at the late window and in the logits; it is a prompt change, not an autonomous internal pointer change.

**Level.** Supported empirical claim (persistence across set size) and causal claim (reassignment by cue), scoped to rotation 0, A→B.

### 4.4 tagged_categories — lexical echo or associated content?

**Gate (72 forwards).** Under the single-category maintain prompt the four unshown members rise over absent by +0.36 [+0.13, +0.60] (7/8 categories) at L51–59 (PASS) and +0.18 [−0.10, +0.45] (6/8) at L48–50 (FAIL; tools and furniture members invert). The label endpoint is much stronger (+1.70, 8/8) and LOGITS members pass (+0.62, 8/8). maintain − mention is small (+0.05 members). The member instrument is validated at L51–59 only.

**Select (2,376 forwards; 8 triples over 6 shared identities, 3 rotations, C0/C1/C3).** Member aggregate \(\bar s_J(c) = \tfrac14\sum_{w\in M_c}(z_w - \bar z_{\text{decoys}})\); pair margin \(m_j = \bar s_J(Y_j) - \bar s_J(X_j)\); S, Q, U on the member endpoint and separately on the label; two clusterings (triple n = 8; category n = 6, required to agree).

| endpoint | S at L51–59 | Q | U | S at L48–50 |
|---|---|---|---|---|
| J_NP members | **+0.82 [+0.76, +0.88]**, 8/8 and 6/6 | −0.08, 0/8 | +0.73 | +0.17, 8/8 |
| J_NP label | +2.42, 8/8 | −0.28, 0/8 | +2.14 | +0.46 |
| RESID_P members (category-member axis) | +1.33, 8/8 | −0.10, 0/8 | +1.24 | +0.17 |
| LOGITS members | +0.83, 8/8 | −0.07, 0/8 | +0.76 | — |

All 24 donor members rise and all 24 source members fall under the pointed swap; S is exactly 0 through block 36 and rises from block 39; damage nil; pure-superclass triples show no confusion penalty (n = 2, not a powered null).

**What the numbers mean.** Pointing at "tools" and replacing its span with "vehicles" states raises car/bicycle/motorcycle/scooter and lowers hammer/saw/drill/axe at the copied sentence, by 0.82 lens logits on average, and only when the tag points at that slot. The selectively gated signal reaches tokens never in the prompt. **Not licensed:** that the model represents the individual members; a single transferred "category-ness" direction read out on correlated member tokens reproduces the whole pattern.

**Level.** Causal claim at extension scale (six shared identities, overlapping folds); rules out pure lexical echo; does not establish member representation. Stage 2 (category-fit directions) and Stage 3 (exemplar inference) were deferred.

### 4.5 scaffold_generality — is selection a property of the copy scaffold?

**Design (tagged stage, 6,144 forwards).** The 2×2 presentation (quoted/bare) × wording (copy/directed) on the tagged organism, keeping the "Here are three words (A)(B)(C)" head and the copy bridge in every cell; 8 triples, 3 rotations, C2/C3, source replacement from block 36; S as the endpoint; quoted×copy re-run inside the battery as a determinism reference.

**Results.** S (J_NP L51–59): quoted_copy +4.10, quoted_directed +6.66, bare_copy +4.19, bare_directed +6.24; all 8/8, Holm p ≤ 1e-6, both windows, all three instruments. Main effects on S at L51–59: presentation (bare − quoted) −0.17 [−0.31, −0.03] (2/8); wording (directed − copy) **+2.30 [+2.12, +2.49]** (8/8); interaction −0.52. Under copy wording the unpointed sources are suppressed below control (Q < 0); under directed wording they are not (Q +0.64). quoted_copy reproduces the evaluate run bit-identically. Damage max ΔNLL 0.016.

**What the numbers mean.** Selection survives bare presentation and the paper's directed wording; directed wording produces larger selection but does not suppress the unpointed. Selection is a property of relevance instructions on this model, not of the one prompt family used to establish it. The `single` stage (single-word 2×2 and the pure direct organism without a copy bridge) and the `directions` stage were designed and not run; whether selection needs a tag head at all is untested.

### 4.6 selection_localization — where is the pointer state?

**Amendment 1 (a free deduction).** The three source words precede the tag token, and the head is arm-invariant, so in a causal decoder the source-token states are bit-identical across arms (verified: arms differ only at token 30). The registered cross-arm source-donor stage would have been a predetermined no-op and was withdrawn. The source-side-tag account is architecturally excluded.

**Step 1A `ptr_transplant` (768 forwards).** Transplant the pointed-B (or C) run's block outputs over the instruction region [tag token, end of user turn) into the pointed-A run at every block ≥ L, L ∈ {36, 40, 44, 48, 51, 55}. Endpoint: restoration \(R_L\) along the clean A→donor presence-profile axis, with the raw (Δs_A, Δs_B, Δs_C) beside it. At L51–59: B→A R = **+0.77 [+0.70, +0.84]** at L36 (raw Δ −1.39, +1.80, +0.14), 0.65 (L40), 0.47 (L44), 0.05 (L48), 0.00 (L51+); C→A 0.73 with the mirror-image raw profile. Target-specific, 8/8, damage nil, A→A self-patch bitwise.

**Step 1B `decomp` and the corrected `region_split` (Amendment 3; 720 + 1,104 forwards).** The first split (tag vs "suffix") had a defect found by external review: the patched region included the user-side carrier and the template delimiters. The corrected split at L36, L51–59: **tag +0.44** (B→A) / +0.48 (C→A); instruction tail +0.09 / +0.09; **user carrier +0.036 / +0.036**; delimiter gap −0.05 / −0.01; full +0.77 / +0.73. Tag plus instruction tail ≈ 0.53 (69 % of full); the parts sum to ≈ 0.51 < 0.77 (superadditive).

**Step 1C `transfer` (1,104 forwards).** Cross the transplant with source replacements: the causal transfer profile (C_0, C_1, C_2) at L51–59 goes from clean-A (4.30, 1.40, 1.34) to B→A (1.66, 4.82, 1.65) and C→A (1.77, 1.56, 4.37); transfer restoration **+0.74 [+0.67, +0.81]** (B→A), +0.69 (C→A), 8/8, damage nil.

**Amendment 4 `random_control` (624 forwards).** At L36, beside B→A / C→A (R = +0.77 / +0.73 reproduced): isotropic writes norm-matched per (layer, position) to the donor delta give R = −0.004 … +0.017 (two seeds, CIs include 0); the donor delta with region positions permuted gives +0.05 … +0.07; the sign-flipped delta 0 to −0.04. Donor-specific share R(D→A) − R(rand) = +0.77 / +0.72 (8/8). Max ΔNLL 0.009.

**What the numbers mean.** The state that decides which source the carrier reads is carried by the instruction tokens, dominated by the tag token's own residual, is sufficient by block 36, has its causal dependence exhausted before block 48, and redirects not only the readable presence but the causal source-transfer profile. It is not a nonspecific deselection of A (random writes do nothing) and it is position-bound (shuffling the delta across positions loses over 90 % of it).

**Level.** Causal, partial mechanistic (localisation to a region and a depth band). **Not established:** the read-site component (attention vs GatedDeltaNet vs MLP), Step 2, designed and never built.

### 4.7 computed_sums — does a computed value transfer, or only its addends?

**Design (48 + 96 + 384 forwards).** Arithmetic gate: `Here is the pair "{a} and {b}". Keep their sum in mind. What is their sum? Answer with one word.` → 16/16. Natural gate: the sum word's presence under maintain vs absent (validated at L51–59: +0.69 [+0.47, +0.91], 8/8; not at L48–50). Transfer: pair span replaced from block 36 by the different-sum donor or the same-sum sibling, maintain and control arms, C2/C3; endpoints \(C^{\text{sum}}_{\text{diff}}\), \(C^{\text{sum}}_{\text{same}}\), the addend margins; cluster = sum.

**Results (maintain, L51–59).** \(C^{\text{sum}}_{\text{diff}}\) = **+1.90 [+1.56, +2.24]**, 8/8 (LOGITS +3.32); \(C^{\text{sum}}_{\text{same}}\) = −0.006 [−0.018, +0.007], equivalent to 0 within the pre-registered ±20 % band (±0.38); \(C^{\text{add}}_{\text{same}}\) = +0.54 [+0.47, +0.61], 8/8; instruction modulation A = +2.01 (8/8). Damage max 0.001.

**What the numbers mean.** Replacing "two and five" states with "two and eight" states moves the carrier's readout from "seven" toward "ten"; replacing them with "three and four" states moves the addend readouts and leaves "seven" exactly where it was. The carrier expresses the value, not the operands. This does not say whether the completed sum travels through the carrier or is recomputed at each position.

**Level.** Causal claim, evaluation scale, on eight arithmetic facts; RESID sum axis not fitted here; re-pairing the same addends is not independent arithmetic replication.

### 4.8 early_late_mapping — precomputation of a transformed variable

**Design (384 forwards; 32 words × 2 mappings × C2/C3; cluster = word).** Conditions early_usable, early_unusable (Amendment 1: a length-matched codebook over eight other words), late. Competence: early 1.00, late 0.99. Central estimand \(E_F^{sc} = s_{F(X)} - s_{F(Y)}\) under the same usable codebook (X's mapped letter against its pair partner's letter, both present in the code); \(E_X^{\text{usability}} = s_X^{\text{usable}} - s_X^{\text{unusable}}\).

**Results.** \(E_F^{sc}\) = **+1.07 [+0.59, +1.55]** (25/32) at L51–59, +2.45 (32/32) on LOGITS; F(X) far more readable early than late (E_F +0.95 / +2.09, 32/32). X stays readable (s_X 2.06 early-usable vs 2.07 late); \(E_X^{\text{usability}}\) = −0.22 [−0.37, −0.06] (9/32) at L51–59, ≈ 0 on LOGITS. The raw late − early X difference, +0.45 (31/32) at L48–50, is a generic long-prefix effect present equally in the unusable control; without Amendment 1 it would have been misread as "X drops when mapped early".

**What the numbers mean.** When a code is available before the copy, the letter the code assigns to the introduced word becomes readable during the copy, specifically that word's letter rather than its partner's. The carrier carries both X and F(X); the representation is richer, not replaced.

**Level.** Causal (availability), evaluation scale; one mapping family; no claim that late use requires retained carrier information.

### 4.9 steering_decomposition (H1.6)

Designed, not run, and ranked last: Package 2 already showed that any block-35 direction's effect on transfer is predicted by its effect on the resident readout, so the question (does G change source sensitivity while v_c changes content?) has a strong prior answer that both change both in proportion. Recorded as a scope gap.

### 4.10 The H1 stopping point: eight verdicts

H1 is never one all-or-none verdict (`context/h1_stopping_point.md`):

1. **Natural modulation** — established (evaluation scale); mostly priming at L48–50, instruction-specific at L51–59 and in surfacing.
2. **Source causality** — established (causal, L_x = 36 frozen); no damage-only foreign donor run.
3. **Candidate-state modulation** — established as a gain, not a task state.
4. **Specificity** — ĝ is not specific; a native selective gain d_shared is.
5. **Semantic / J selectivity** — no J-only artefact found; every effect registers on RESID_P and LOGITS.
6. **Prompt / domain scope** — broad within the tagged copy-bridge organism; untested without the tag head.
7. **Selection** — established, localised to the instruction residuals; read-site component open.
8. **Transformation** — established as availability/precomputation, additive.

Everything in H1 is a readout at teacher-forced copy positions. It establishes nothing about behaviour and nothing about maintenance.

---

## 5. H3, first arc: does the selected content reach a consumer?

### 5.1 The re-readability trap, stated once

For any consumer, ask: at the answer position, can the model recover the needed identity by attending back to a token that names it? If yes, a block-36 boundary control will be weak, because the consumer can read the visible token below the cut, and a null on any representation ladder at that cut is uninformative. The word codebook fails this test; a computed sum passes it (only the operands are visible); a two-hop clue passes it if the question never restates the clue. This one consideration shaped the whole H3 arc.

### 5.2 consumer_competence (108 forwards)

A six-entry codebook (three sources and their three donors) appended after the tagged copy, with three candidate query wordings that never restate the tag. Greedy accuracy 1.00 for every tag and wording; forced-choice margin b = log P(pointed letter) − max over the two unpointed letters ≈ 5.4 nats. The margin, not accuracy, is the endpoint with dynamic range. Wording frozen: "the word you were instructed to keep in mind".

### 5.3 selection_to_behavior — the instruction-region transplant on the same forwards (1,152 + 96 forwards, v2)

**Design.** Six fresh triples (2–7), C2/C3, three rotations; arms cleanA/B/C, BtoA, CtoA (instruction-region transplant, block ≥ 36), per-target norm-matched isotropic controls randB/randC, AtoA self-patch; primary endpoint the direct redirect with no source replacement, \(E_D = q_D(D\to A) - q_D(\text{cleanA})\) with \(q_D = \log P(F(X_D)) - \log P(F(X_A))\), against the ceiling \(\Delta_D = q_D(\text{cleanD}) - q_D(\text{cleanA})\); five-way greedy classification. Letters scored by logsumexp over both surface forms. Cluster = triple (n = 6).

**Results.** Internal restoration on the consumer-appended forwards reproduces H1 (presence +0.76 / +0.72, transfer +0.73 / +0.68, 6/6). Behaviourally: E_B **+3.32 [+2.72, +3.92]**, E_C +2.54 [+1.79, +3.29] (6/6); randB +0.03, randC +0.03; ceilings Δ = +13.30; restoration E/Δ **0.25 / 0.19**. Greedy: BtoA answers A in 34/36 and B in 2/36; CtoA answers A in 36/36. The equivalence band (±2.66) does not contain E, so this is a partial redirect, not a null.

**Two audits** (one by the assistant, one independent by the researcher with its own trace and recomputation) agreed and produced the v2 corrections: logsumexp letter scoring; per-target random controls with measured ρ = 1.0002; donors rendered with the consumer turn so lengths match (v1 had ~1 % cross-length contamination); cluster by triple, not by cell; the crossed source-margin table reported as an observation only (the earlier causal one-third/two-thirds split withdrawn); the with/without-consumer readout offset verified as a sequence-length effect (an equal-length different-content suffix gives 0.0 residual at every block). A later dense-model gate falsified the attribution of that length effect to the GatedDeltaNet kernel (§11).

**What the numbers mean.** The state that redirects the readout most of the way redirects the answer margin by a fifth to a quarter and almost never changes the decoded letter. The route is unidentified by design: the transplant precedes the carrier, and the visible tag and words remain in context.

**carrier_only (Amendment 2; 324 forwards).** Replace only the assistant-carrier states with the pointed-B or pointed-C run's states: E/Δ 0.025 / 0.012 (≥ 36), 0.042 / 0.019 (all 64 blocks), 0/36 flips, matched random +0.02; internal R = 1.000 by construction (a gate, not a finding); the answer position moves 4–7 units at L51–59 against 49 under the natural tag change. The instruction-region transplant's behavioural effect was not carried through the carrier representation.

**Level.** Supported empirical claim: a quantified internal-versus-behavioural dissociation on this consumer, with the answer shift itself causal but small and route-unidentified. A full source-donor replacement at block 36 on the same organism flips 0/36: block 36 is not a validated boundary for a consumer that can re-read the word.

### 5.4 computed_sum_consumer — the arc that produced the H3 headline

**Competence (48 + 16 + 64 forwards).** A sum→letter codebook consumer fails competence (6/48 ≈ chance). Diagnosis by researcher-directed calibration: explicit-sum→codebook 1.00 versus latent-sum→codebook 0.25 under the same codebook (the lookup is usable; composing the internally computed value into it is the bottleneck, thinking-off); `Is their sum greater than ten?` 0.81; **parity 1.00** and **direct sum report 1.00** (scored argmax over the eight sum words; greedy 12/16 because thirteen/fourteen start with a subtoken). A bug is on record: the competence battery had seeded a different codebook per wording. An earlier draft's "needs CoT" mechanism was downgraded to a hypothesis.

**Boundary gate (256 forwards; 8 sums × C0/C1 × parity + report × L_x ∈ {23, 36}).** A different-sum operand donor flips report 16/16 at both cuts and parity 16/16 (L23) / 12/16 (L36); the same-sum sibling flips 0/16; internal C^sum reproduces H1 (+1.5, 16/16); carrier ΔNLL ≈ 0. Margins over 8 sums: report +21.3 / +21.1 nats, parity +6.5 / +3.9. **The wording "the block-36 carrier state is computationally used" was later withdrawn** (§5.5): the operand span's content drove the flips.

**Transport stage (160 forwards): the dissociation.** Conditions from block 36: `O_donor` (operand span ← donor), `C_full` (carrier ← donor carrier, operand span asserted clean), `C_rand` (carrier ← own + per-position norm-matched isotropic). C_full installs the donor sum at the carrier readout at the same magnitude as O_donor (J_NP +1.55 vs +1.50, 8/8) but moves the report margin +1.70 [+1.09, +2.31] against +21.1, flips 0/16 against 16/16; parity +0.53 against +3.9, 0/16; C_rand +0.05. Flip counts use the scored-argmax rule.

**Robust stage (Amendment 2; 1,022 forwards; C0–C3, two donor maps, RESID_P number axis fitted in-run, LOGITS).** Pooled, map offset 3, report (parity in parentheses):

| condition | margin log P(donor) − log P(own), minus clean | flips | carrier sum shift J_NP / RESID_P / LOGITS (L51–59) | answer-position distance L51–59 |
|---|---|---|---|---|
| O_donor (operands → donor, ≥ 36) | +21.2 [+19.9, +22.5] (+3.88) | 32/32 (23/32) | +1.55 / +0.76 / +2.49, 8/8 | 55.3 |
| C_full (carrier → donor, ≥ 36) | +1.75 [+1.17, +2.33] (+0.70) | 0/32 (0/32) | +1.62 / +0.68 / +2.58 (by construction) | 7.7 |
| C_all (carrier → donor, all 64 blocks) | +1.76 (+0.74) | 0/32 (2/32) | same | 8.3 |
| C_rand (matched norm) | +0.05 (+0.02) | 0/32 | +0.14 / +0.01 / +0.11 | 4.6 |
| NEC (operands → donor, carrier clamped own, ≥ 36) | +19.3 [+17.9, +20.6] (+3.18) | 32/32 (17/32) | 0.000 (clamp gate) | 53.6 |

Ratios C_full / O_donor: behavioural 0.083 (report), 0.181 (parity); J_NP 1.04, RESID_P 0.89, LOGITS 1.04; answer-position distance 0.14 / 0.22. C2/C3 and the offset-1 map reproduce every row. C_full raises the donor's odds ×5.8 on report and ×2.0 on parity while leaving P(own) essentially unchanged (Δ log P(own) −0.004); O_donor ×1.6·10⁹.

**What the numbers mean.** "Margin +21 nats" means the donor sum word goes from essentially impossible to essentially certain at the answer; "+1.75" means the donor becomes 5.8 times more likely than before but the own answer keeps its probability, so nothing flips. The premise (the donor sum is installed at the carrier) is instrument-independent. Replacing the carrier from block 0 changes nothing, so the block-36 cut is not hiding the effect. The operand route is sufficient on its own (NEC flips 32/32), and O_donor ≈ NEC + C_full: the two routes are roughly additive, with the carrier copy 9–18 % of the operand-donor effect. The consumer registers the carrier content weakly (answer-position distance 1.7× a matched random write). Wording adopted: "the carrier copy is weakly consulted and not acted on while the source is visible", never "unused".

**Global stage (Amendment 3; 958 forwards).** Report (parity):

| condition | margin | flips |
|---|---|---|
| operands → donor, all 64 blocks (token-equivalent) | +21.6 (+6.8) | 32/32 (32/32) |
| operands → donor, ≥ 36 | +21.2 (+3.9) | 32/32 (23/32) |
| carrier → donor, ≥ 36 | +1.75 (+0.70) | 0/32 (0/32) |
| operands + carrier → donor, consistent global state, ≥ 36 | +21.3 (+4.2) | 32/32 (24/32) |
| paper-style coordinate swap own↔donor sum word, every position from the operands on, L36–62 | +11.1 (+0.2, ns) | 16/32 (0/32) |
| same swap, carrier only | +0.35 (+0.04) | 0/32 (0/32) |
| decision positions ← donor, L36–50 | +0.7 (+4.1) | 0/32 (21/32) |
| mask consumer→operand attention, clean | +6.7, competence FAIL (+2.2, 29/32 competent) | — |
| mask + carrier → donor | (+3.4) | (17/32) |
| mask + operands → donor | (+3.6) | (18/32) |

Readings: late operand residuals ≡ operand tokens for report; the consistent global state behaves like the operand donor; the paper's coordinate swap reproduces when it spans source and decision positions and not when confined to the carrier, and it leaves parity unmoved while a full residual donor at the same positions flips parity 23/32 — a swap along the answer-word directions moves the consumer that emits those words; parity is settled in the decision-position residuals by block 50, report is not; the attention mask leaves the report consumer incompetent, and on parity the carrier donor's effect over the *masked* baseline (+1.2 nats) matches the operand donor's remaining effect (+1.35) — a first "consulted more when the direct read is closed" signal, on a degraded baseline, with the recurrent channel open.

### 5.5 The claims table for the sum organism (withdrawals)

| claim | status |
|---|---|
| §9 "the block-36 carrier state is computationally used" | **withdrawn**: operand-span content drove the flips |
| §10 "the readable sum is NOT used; the consumer recomputes from the operands" | **superseded**: the carrier copy has a real content-specific effect (×5.8 donor odds, +1.75 nats, P(own) unchanged, 0/32 flips), and "operand positions" was not "raw operands" until the global stage |
| "the consumer does not consult the carrier" | **superseded**: the answer position moves 0.14–0.22 as far as under the operand donor, 1.7× random |
| defensible statement | making the carrier residuals donor-like, which installs the donor sum at the readout on three instruments from block 36 or block 0 on four carriers and two donor maps, changes the delayed answer far less than replacing the source-span residuals while the source remains available; this separates selective readability from behavioural substitutability and identifies neither the maintenance mechanism nor natural non-use |

---

## 6. H3, second arc: the question turn, the absent source, and the paper's own intervention

### 6.1 query_local_workspace — reconstruction at the question and function-specific consumption

**Why.** The sum consumer follows the operand span while the carrier copy is redundant. Two questions follow: is the sum rebuilt at the question positions when the carrier copy is denied, and does the answer depend on that rebuilt representation? Two consumers of the same value (report needs the value; parity can be computed from the operands' parities without it) make the second question sharp.

**Design (five stages, ≈ 2,800 forwards; 8 sums × C0–C3 × parity + report; Q band blocks 36–62; Q = every position after the carrier including the answer position).** `queryread`: O_donor, C_full and NEC with readouts at both the carrier interior and the question positions. `querycausal`: Q_own (bitwise self-patch gate), Q_donor_50 and Q_donor_62, Q_rand (norm-matched), Q_swap (paper-style coordinate swap of own↔donor sum-word naming directions at Q), NEC_Qclamp (NEC plus the own/donor naming plane pinned to its clean coordinates at every Q position), NEC_Qclamp_perp (a random orthogonal 2-plane pinned). `clampsplit` (Amendment 1): the clamp with the answer position excluded (`noans`) and the answer position only (`ansonly`). `nosource` / `nosource2` (Amendment 2): an absent-source recipient with the operands replaced by a placeholder, length- and span-matched, receiving a real run's carrier states (all 64 blocks) for sum S or S₂, a random carrier, or the question-position states of a real run.

**Results.**

*Reconstruction.* Under NEC the donor sum appears at the question positions at 80–90 % of its free level: J_NP +0.53 (parity) / +1.25 (report) vs +0.66 / +1.43 under the free operand donor; RESID_P +0.10 / +0.33 vs +0.12 / +0.36; question-position LOGITS +1.8 / +4.2 vs +2.7 / +5.4; 8/8 on every instrument. The carrier donor alone puts almost nothing there (+0.14 / +0.19).

*Consumption.* Clamping the naming plane at the question tokens with the answer position excluded (`NEC_Qclamp_noans`) erases the donor sum there on all three instruments (J_NP +1.25 → +0.29) and: parity +3.18 → +3.15 nats, 17/32 → 17/32 flips; report +19.3 → **+11.8**, 32/32 → 20/32. Clamping the answer position only gives report +5.6 (0/32: output suppression by construction) and parity +2.97 (16/32).

*Decision positions.* Q_donor_50 flips parity 21/32 and report 0/32; Q_donor_62 flips both 32/32 (report +20.5). Parity is fixed in the question-position residuals by block 50; report later.

*The paper's swap at the question.* Q_swap flips report 19/32 (+11.1 nats) and leaves parity at +0.22 (CI includes 0, 0/32) while a full-residual donor at the same positions flips parity 32/32.

*Absent source.* With no operands in the prompt (clean answer "unknown" in 24/32 cells, at chance among the sum words), transplanting the carrier of a real run with sum S makes S the best-scored sum word in **28/32** cells (+4.0 nats, 8/8); the S₂ carrier does the same for S₂ (28/32, −4.2); the random carrier 4/32 (+0.05). Greedy: the sum word or full digit in 14/32, the leading digit "1" of a two-digit sum in 9 more, "hidden" in 7. Parity does not follow the carrier (16/32, +0.11). The question-position transplant is the positive control (32/32 both consumers). ΔNLL ≤ 0.002 on every load-bearing row.

**clampfix (Amendment 3 repairs, 702 forwards).** The audit had found that the orthogonal control was gentler than the naming clamp (requested norms 0.19 vs 0.48) and that `clampsplit` had no control. With `CoordClampMatched`, each orthogonal-plane clamp is rescaled per position and layer to the naming clamp's realized norm:

| condition | parity margin | flips | report margin | flips |
|---|---|---|---|---|
| NEC | +3.18 | 17/32 | +19.26 | 32/32 |
| naming clamp, all Q | +2.94 | 16/32 | +1.75 | 0/32 |
| orthogonal clamp, norm-matched | +3.16 | 17/32 | +19.21 | 32/32 |
| naming clamp, answer excluded | +3.15 | 17/32 | **+11.79** | 20/32 |
| orthogonal, answer excluded, matched | +3.18 | 17/32 | +19.22 | 32/32 |
| naming clamp, answer only | +2.96 | 16/32 | +5.56 | 0/32 |
| orthogonal, answer only, matched | +3.15 | 18/32 | +19.24 | 32/32 |

Every matched control leaves both consumers at the NEC reference; the 38.8 % report drop is specific. The stage also exposed that the post-cast realized write for these small clamps is ρ ≈ 0.53–0.59, κ ≈ 0.42–0.48 (bf16 rounding: a residual entry of a few units has a step of 0.02–0.04, and over 5120 dimensions that is the size of a 0.2–0.5 write).

**clampfix32 (Amendment 4, run 2026-09-10; 702 forwards, float32 residual from block 35).** The same cells, conditions, seeds and norm-matching rule under `Fp32Residual`, with gates registered before the forward: G0 (the regime reproduces the bf16 forward: same top-1, |ΔNLL| ≤ 0.02, answer log-probs within 0.25 nats, bitwise deterministic) held on 3 of 4 checked cells, the fourth moving a donor-answer log-prob by 0.275 nats; G1 (exact write) held on every block with a nonzero request: ρ = κ = 1.000, read-back ≤ 5.3e-5. Results: NEC report +19.27 (bf16 +19.26), parity +3.16 (+3.18); the emission-excluded naming clamp removes **38.5 %** of the report margin (19.27 → 11.84 [10.35, 13.33]; bf16 38.8 %); parity −0.04; every matched orthogonal control within the NEC interval (report 19.24–19.26, parity 3.13–3.17); ΔNLL ≤ +0.0008. The exact clamp reproduces the bf16 clamp row for row to within 0.05 nats: the part of the bf16 write lost to rounding was inert. The write-fidelity weakness is therefore closed **for the question-clamp rows**; the other coordinate-level rows (`Q_swap`, the Amendment-3 swaps, `bridgeswap`, writes of norm 2–5 at ρ ≈ 0.8) were not rerun and keep it.

**What the numbers mean.** When the carrier copy is pinned, the sum still appears where the question is processed, built from operand-origin state; the consumer that needs the value draws about 40 % of its answer margin on that rebuilt representation, the consumer that can bypass the value ignores it; the paper's coordinate swap at the question moves the report word and not the parity function; and when there are no operands to rebuild from, the carrier copy is what the report consumer uses.

**Level.** Supported (reconstruction as an observation on three instruments; consumption as a causal claim with a norm-matched control and, after clampfix32, an exact write); "rebuilt at the question" is an interpretation of a route that reaches the question without passing the clamped carrier outputs, not an identified computation.

### 6.2 two_hop_organism — the same design on a factual latent

**Pilot (three runs: 144 + 192 + 192 forwards).** Gates: competence 0.96 scored (greedy exact 0.42, the rest first subtokens); latent readability during the carrier +2.42 [+1.93, +2.91] (12/12) own clue minus donor clue at L51–59; donor geometry 24/24. The first pilot used the released completion form as the question, which restates the clue; the token-level source donor then moved the answer only 13 % of the natural swing because the consumer answered from the question. Amendment 2 replaced the question by `Complete the fact from the clue you were given, using one word.` Under the corrected question: S_donor0 (clue span ← donor, all blocks) share 1.00, 24/24 flips; S_donor (≥ 36) 0.57, 12/24 (block 36 is a partial boundary here, unlike the sum); C_full 0.26, 6/24; C_all 0.26; C_rand 0.00.

**Full battery (Amendment 3; 576 + 280 forwards; 12 items × C0–C3; cluster = item).** Audit corrections applied first: the readout must cover the maintained answer pair as well as the bridge; two items are paraphrase pairs; the no-clue reference must be length-matched. Results: S_donor0 1.00 (48/48); S_donor 0.58 (24/48); **C_full 0.27** (+6.19 nats, 12/48), C_all 0.27 (11/48); C_rand 0.00 (1/48); NEC_all (clue donor, carrier clamped at all blocks) **0.73** (36/48) with the donor answer and bridge rebuilt at the question positions at 82 % of their free level; NEC36 0.42; Q_donor 0.87 (44/48). Placeholder-clue stage: with the entity replaced by `X`, the two candidate answers split at chance (20/40); installing a real run's carrier states moves the answer to that run's entity by ±7.1–7.3 nats, 10/10 items, 28/40 (own) and 32/40 (donor) pairwise wins, random 21/40, i.e. **0.63–0.65 of the ceiling**; the question-position transplant 1.00 (39/40). ΔNLL reaches 0.041 under all-block clue replacement (bound 0.02, reported); every carrier row ≤ 0.033.

**What the numbers mean.** The pattern established on arithmetic holds for a factual bridge: the maintained copy is real, content-specific, secondary while the source is readable, rebuilt at the question, and consumed when the source is gone. One quantitative difference: the carrier share while the source is visible is 0.27 here against 0.08 on the sum. Nothing here attributes the effect to the bridge entity specifically, because the intervention replaces the whole clue span. This is not a corroboration of Nanda's multihop finding; the organism differs by design.

### 6.3 recompute_cost_ladder — a correction

**Design (768 forwards; 3 tiers × 8 items × C0–C3).** t1 memorised: "{a} and {b}", keep their sum, ask the sum; t3 chained: the same eight source strings and donors, keep double their sum, ask double; t2 composed: "{a} and {b} and {c}". Competence gate ≥ 0.9 per tier.

**Results.** Competence t1 1.000, t2 0.875 (FAIL), t3 0.625 (FAIL). Boundary (source share from block 36) 0.98 / 0.98 / 0.99. Carrier share C_full 0.13 / 0.11 / **0.03**; paired on identical source strings, t3 − t1 = **−0.10 [−0.13, −0.07], 0/8 items positive**, with the boundary unchanged. The installed latent at the carrier falls with difficulty (+2.32 / +0.67 / +0.20). NEC_all keeps 0.88 / 0.90 / 0.97; reconstruction at the question 78 % / 91 % / 93 %; random inert; max ΔNLL 0.011.

**What the numbers mean.** Making the computation harder did not raise the carrier's share; it lowered it, and it degraded competence and the maintained readout, so difficulty and maintenance are confounded in this design. The recompute-cost account is withdrawn as an explanation of the gap: the manipulation failed to isolate recompute cost; it does not establish that recompute cost is irrelevant.

### 6.4 bridgeswap — the paper's own intervention, decomposed by position (Amendment 4)

**Why.** The paper's causal claims use a lens-coordinate swap at every position; the project's asymmetry rested on whole-residual transplants; the only coordinate swaps run before this had moved the answer word. This stage applies the paper's §3.3 intervention to the two-hop *intermediate* (Spain ↔ Canada) and splits it by position: clue span, copied carrier, question turn, or all positions from the clue on ("tail", the paper's version); the answer-word swap (Madrid ↔ Ottawa) at the same positions as the paper's own confound check and Nanda's dominating baseline; a decoy-pair swap as the nonspecific control; the all-block clue donor as the ceiling. Band L36–62, `CoordSwap`, J_NP folded directions; 12 items × C0–C3; 576 forwards.

**Endpoint correction (`bridgeswap_seq`, 2,512 forwards).** Six seeded-random cells published for inspection showed the greedy first token is often a subword of a multi-token spelling ("R"+"ome", "Tok"+"yo", "Bud"+"apest"), while the scored candidate set held single-token spellings only; that over-counts flips when the own answer is multi-token and under-counts when the donor's is. Every condition was rescored with the summed token log-probabilities of both full answer words (four spellings, logsumexp), interventions unchanged. Clean competence on this endpoint 1.00 (48/48).

**Results, sequence endpoint, share of the full-residual ceiling (+23.9 nats), primary model, with the dense model beside it:**

| condition | swapped pair | positions | Qwen3.6-27B share (flips) | Qwen3-32B share (flips) |
|---|---|---|---|---|
| S_donor0 | full residual | clue span, all blocks | 1.00 (48/48) | 1.00 (44/48) |
| int_tail | intermediate ↔ swap_to | clue → answer (the paper's swap) | **0.41** (16/48), 12/12 items | 0.37 (20/48) |
| int_clue | intermediate | clue span | 0.09 (0/48) | 0.22 (8/48) |
| int_carr | intermediate | copied carrier | **0.07** (0/48) | 0.04 (4/48) |
| int_q | intermediate | question turn | **0.20** (0/48) | 0.19 (5/48) |
| ans_tail | answer ↔ swap_answer | clue → answer | 0.54 (29/48) | 0.44 (18/48) |
| ans_clue | answer | clue span | 0.06 (0/48) | 0.18 (11/48) |
| ans_carr | answer | carrier | 0.06 (0/48) | 0.06 (4/48) |
| ans_q | answer | question turn | 0.43 (17/48) | 0.42 (14/48) |
| rand_tail | decoy ↔ decoy | clue → answer | 0.01 (0/48) | −0.01 (4/48) |

Companion facts (candidate-set endpoint, primary model): the position sets are roughly additive (9.5 nats summed against 10.4 for the tail); the carrier swap installs the swapped intermediate at the carrier readout as strongly as the whole swap (+2.71 vs +2.48, 12/12) while moving the answer least; realized per-position swap norms ≈ 2.3 at carrier and question, 4–5 at the clue; ΔNLL ≤ 0.005 for every swap. Per-item shares span 0.09 (honey→butter, a paraphrase item) to 0.65; the question turn is the largest single site on 10 of 12 items.

**What the numbers mean.** The paper's intermediate swap works on this organism on every item. Split by position, half of its effect comes from the question turn, a quarter from the clue span, and a sixth from the copied carrier, even though the carrier is where the intermediate is continuously readable and where the swap installs the swapped-in entity just as strongly. The answer-word swap is larger at every position set, which is what Nanda observed on this model. A swap confined to one position set moves every item's preference and reverses none on the sequence endpoint; only the all-positions swap or the answer swap at the question reverses answers. The dense model gives the same ordering, with the clue span carrying more (0.22 vs 0.09) and the carrier less (0.04).

**Level.** Supported empirical claim with a nonspecific control, two architectures, the paper's own materials and intervention. Not separated: computation of the second hop from the clue residuals versus a re-read of the clue at the question.

### 6.5 qsplit — the ladder at the question-turn cut (Amendment 5, run 2026-09-11)

**Why.** Every positive in H3 transplants whole residuals, and `bridgeswap` found the question turn to be the largest single-position site. The two halves of the paper's Fig. 16 split (a concept's J-space component versus its remainder) therefore existed as separate numbers, but the complement had never been run: the full question-turn delta with the intermediate's naming plane removed. This organism is the only one of the three where the swapped concept (Spain vs Canada) is upstream of the emitted token (Madrid vs Ottawa); on the sum organism the naming plane *is* the answer word, so the same ladder is output steering by construction. The amendment, its gates, predictions and outcome labels were registered before the forward (`H3/design_specs/two_hop_organism.md`, Amendment 5).

**Design.** 12 items × C0–C3, cluster = item; question turn with the **scoring position excluded** (`q_pre`), because writing the donor residual at the scoring position imports an already-formed donor-answer state; blocks 36–62, sustained writes; `Fp32Residual` from block 35 on every forward including clean and donor; sequence-log-prob endpoint. Let h_l be the clean recipient block-l output at the `q_pre` positions, h^Y_l the donor's, Δh_l = h^Y_l − h_l. The intermediate's two J_NP folded naming directions (a_int, a_swap_to) are orthonormalised per block into Q_l (per-block cosine reported; a cell is flagged if |cos| > 0.9), P_l = Q_l Q_lᵀ; a random 2-plane R_l per cell (seed 20260911 + cell index), with v_R,l = s_l R_l R_lᵀ Δh_l scaled so ‖v_R‖ = ‖v_J‖ per position (asserted). Every row is a fixed per-block target T_l = h_l + M_l Δh_l written with `SpanWriter`:

| condition | write at block l | what it is |
|---|---|---|
| `clean32` / `donor32` | none | fp32 baselines; donor competence |
| `q_full_pre` | h + Δh | full residual donor over `q_pre`; the ceiling for this cut |
| `q_plane_pre` | h + P Δh | the donor delta's naming-plane component only |
| `q_rem_pre` | h + Δh − P Δh | the donor delta with the naming plane removed and held at clean throughout the band |
| `q_rand_pre` | h + v_R | norm-matched random-plane component; control for `q_plane_pre` |
| `q_rem_rand_pre` | h + Δh − v_R | donor delta minus an equal-norm random component; control for `q_rem_pre` |
| `int_q32` | `CoordSwap` on `q_pre` | continuity with the bf16 `int_q` row only |

Because the complement of the written component is held at its clean or donor value at every written block, the rows are three fixed state trajectories, not a partition of one computation. Block-63 projections on the raw unit naming directions (identity transport, γ⊙w_v) are measured after the sustained write ends, as the re-entry observation for `q_rem_pre`.

**Registered gates and labels.** Gates: `q` token-id equality between recipient and donor renderings; competence ≥ 0.9 on both; ρ ∈ [0.9, 1.1], κ ≥ 0.99; `q_full_pre` > 0 on ≥ 10/12 items and ≥ 0.3 of the model's clue-span ceiling (S_donor0, quoted from `bridgeswap_seq`: 23.88 hybrid); `q_rand_pre` ≤ 0.10 of `q_full_pre` with ≤ 2/48 flips and `q_rem_rand_pre` ≥ 0.80. With A = share(`q_plane_pre`) and B = share(`q_rem_pre`): naming-plane dominant (A ≥ B and B ≤ 0.5); complement dominant (B ≥ 0.75 and A ≤ 0.35, with `q_rem_rand_pre` ≥ 0.80 and the block-63 measurement reported); redundant (A ≥ 0.5 and B ≥ 0.5); jointly necessary (A ≤ 0.35 and B ≤ 0.5); otherwise ambiguous. No numeric prior for A or B.

**Results (1,792 forwards, 457 s; `H3/results/reports/two_hop_qsplit.md`).** All five gates pass: competence 1.00 / 1.00; ρ = κ = 1.000 with read-back 0 on every row; max |cos(a_int, a_swap)| 0.75, no degenerate cell; ‖v_J‖ averages 17 % of ‖Δh‖ over cells and blocks.

| condition | Δ margin (nats) | 95 % CI | items > 0 | share of `q_full_pre` | share of S_donor0 | flips | J_NP q-readout shift L51–59 | block-63 Δproj(a_swap) − Δproj(a_int) |
|---|---|---|---|---|---|---|---|---|
| `q_full_pre` | **+11.19** | [+10.00, +12.38] | 12/12 | 1.000 | 0.469 | 18/48 | +2.92 (12/12) | +14.15 |
| `q_plane_pre` | +2.25 | [+1.34, +3.16] | 11/12 | **0.201** | 0.094 | 0/48 | +2.83 (12/12) | +14.87 |
| `q_rem_pre` | +8.77 | [+7.76, +9.79] | 12/12 | **0.784** | 0.367 | 1/48 | +0.05 (11/12) | −0.62 |
| `q_rand_pre` | +0.03 | [−0.01, +0.07] | 9/12 | 0.003 | 0.001 | 0/48 | +0.03 | +0.08 |
| `q_rem_rand_pre` | +11.00 | [+9.85, +12.15] | 12/12 | 0.983 | 0.461 | 15/48 | +2.89 (12/12) | +14.09 |
| `int_q32` | +2.33 | [+1.61, +3.06] | 12/12 | 0.209 | 0.098 | 0/48 | +1.59 (12/12) | +3.95 |

Additivity S = m(full) − m(plane) − m(rem) = +0.16 nats [−0.12, +0.44], 8/12 items > 0. Per item, A ranges 0.00–0.44 and B 0.54–0.98; every item has B ≥ 0.54. ΔNLL 0.0000 on every row.

**Registered reading: complement dominant** (A = 0.20, B = 0.78, `q_rem_rand_pre` 0.98). Three facts carry it: the plane component alone installs the intermediate at the J_NP question readout as strongly as the full donor (+2.83 vs +2.92) yet moves the answer a fifth as much, with no flips; the complement with the plane clamped to clean leaves the plane readout at clean (+0.05) and does not re-enter it at block 63 (−0.62 against +14.15), yet moves the answer 0.78 of the full donor; and the rows are roughly additive. The plane is nonetheless privileged per unit norm: at equal norm a random 2-plane moves the answer 0.003 of the full donor, the naming plane 0.20 — about 70×. The paper-style coordinate swap on the same span reads 0.21, consistent with the plane row.

**Sanity checks before the reading was written.** The analysis script recomputes every primitive contrast from `raw_qsplit.npz`; six seeded-random cells (Polish|C2, Osaka|C3, Barcelona|C0, Moscow|C0, Lyon–Naples|C1, butter|C2) read by hand show the same ordering in every cell (full ≈ complement ≫ plane ≈ swap ≫ random ≈ 0); the greedy decode flips to the donor answer under the full donor in 18/48 cells (e.g. Lyon–Naples|C1 `Paris` → `R`[ome]) and under the complement in 1/48, never under the plane; on the butter/honey paraphrase item the full-donor greedy is `H` (the substance rather than the animal), so that item's flips are not clean even though its margin is (A = 0.23, B = 0.86). One implementation defect was caught on the smoke cell and fixed before the scored run: the block-63 plane coordinates used `torch.linalg.qr` columns, whose signs are arbitrary; the measurement was replaced by projections on the raw unit directions, and the battery relaunched (recorded in the commit message).

**Relation to the paper, as licensed.** This is the position-resolved analogue of the paper's Fig. 16 split, restricted to the pair's naming plane and run at the question turn only. It does not contradict the paper's result, which decomposed a concept vector against a k = 16–25 sparse J-space reconstruction and swapped at every position; what it adds is that, at the one position where the project found the largest single-position share, a full-residual donor's effect is carried mainly by content outside the two-token naming plane, with that plane held at clean. **Not licensed:** "outside the J-space" (the k = 25 NNLS row `q_rem25` was registered as not run); "the readable representation is unused" (the plane carries a real, norm-efficient 0.20); any statement about the carrier or clue positions; any share-of-computation reading of S.

**Weaknesses.** A 2-plane is a lower bound on J-readable content: correlated naming directions (neighbours of Spain/Canada) lie in the complement and could carry part of B. The rows are fixed trajectories: the complement's within-band consequences cannot re-enter the plane at written blocks by construction, so B measures "the complement with the plane pinned", not the complement free-running; the block-63 measurement shows no re-entry once the pin is released, which limits but does not remove the concern. `q_ans` and the RESID_P country axis were not run. One organism, one model, thinking off.

### 6.6 qsplit on the dense control (Amendment 6, run 2026-09-11) — gate failure, reported as one

**Registration.** The identical stage under `TCSIF_MODEL=qwen3_32b` with no design change; the S_donor0 ceiling for gate 4 is this model's own `bridgeswap_seq` value (+33.73). An interpretation rule was fixed before the forward: the plane/complement split depends on the lens directions, and the dense lens is a partial fit (n = 80), so noisier naming directions push A down and B up *toward* "complement dominant" for a reason unrelated to architecture. Therefore the dense `int_q32` row is the calibration: if `q_plane_pre` and `int_q32` land within ~0.1 of each other and near 0.2, the lens is doing comparable work and A/B are read as on the hybrid; a reversal (naming-plane dominant on dense, gates passed) would be the informative outcome. P1 also flagged gate 2 as at risk (competence 0.92 on this model in `bridgeswap_seq`).

**Results (1,792 forwards, 167 s; `replication_qwen3_32b/H3/results/reports/two_hop_qsplit.md`).** Gates 1–3 pass: competence 0.917 / 0.917 (above the 0.9 bar); ρ = κ = 1.000, read-back 0; max |cos| 0.88, no degenerate cell. **Gate 4 fails:** `q_full_pre` = +6.76 nats [+4.37, +9.15], 12/12 items > 0, but 0.20 of the clue-span ceiling against the 0.30 bar (10.12). **Gate 5 fails as written:** `q_rand_pre` shows 4/48 flips against the ≤ 2 bar — the four baseline-incompetent cells (clean 44/48), which appear identically in every row including `clean32`; the registered gate counts raw flips, not flips relative to clean, and the rule was not overridden. Its share (0.005) and `q_rem_rand_pre` (0.97) are inside their bars.

Per the stop rule no reading is taken. Unread numbers, for the record: plane 0.151 (+1.02), complement 0.746 (+5.04; a hair under the 0.75 threshold, so even a passing run would have read "ambiguous"), random plane 0.005, complement-of-random 0.970, `int_q32` 0.193 (+1.30). The calibration rule holds (`int_q32` 0.19 ≈ `q_plane_pre` 0.15, as 0.21 ≈ 0.20 on the hybrid), and the ordering full ≈ complement ≫ plane ≈ swap ≫ random ≈ 0 reproduces in all six seeded-random cells. What differs from the hybrid is how much of the answer swing the question turn carries (0.20 vs 0.47), consistent with the dense `bridgeswap` decomposition (clue span 0.22 vs 0.09; its block-36 boundary is more complete). The greedy decode on this model frequently begins with `The` while the sequence-scored margin is clean; every number uses the sequence endpoint.

**What this licenses.** "On the dense model the same ladder gives the same ordering with a smaller question-turn effect, and does not meet the registered gates; the hybrid reading stands as a single-model result." Not licensed: any dense-model label; any claim that the hybrid result replicates or fails to replicate. A re-registered Amendment 7 would set the gate-4 bar relative to this cut's own ceiling (the `Q_donor` row of the `full` stage) and count gate-5 flips on clean-competent cells only; not run.

---

## 7. The adversarial-susceptibility study (H3.6, `H3/trying_to_fool/`)

This study was held out of the 2026-09-09 report at the researcher's request, pending their own analysis. It is included here in full; the "Reading" was written by the assistant immediately after the audit and has not been checked by the researcher. No H1 or H3 claim cites any number in this section.

**Design (registered 2026-09-09 after an external critique).** For each of 16 evaluation-bank word pairs X→Y, a vector δ ∈ R^5120 is added to the block-35 output at the interior carrier positions and optimised by Adam (60 steps, lr 0.15) under a norm projection ‖δ‖ ≤ ρ_nat = 8.98 (the natural block-35 footprint). Objective: raise the J_NP margin for Y and Y's J_NP presence at L51–59, penalised by movement of the fitting plain-sentence axis (RESID_fit, templates 1–8), the LOGITS margin, the codebook consumer's behaviour b, and carrier ΔNLL (> 0.02 nats). Fitting carriers C0/C1 with codebook seed A. Audit on carriers C2/C3 with codebook seed B, on instruments never in the loss: the audit plain-sentence axis (templates 9–12), R_CB, and held-out behaviour. Shares are Δ divided by each instrument's natural Y−X swing A_k.

**Calibration (284 forwards).** Gate G1 (the held-out audit axis sees the natural identity change at L48–50) failed as a power failure (3/3 positive, interval touching zero at n = 3; clear at L51–59); G3 (a natural block-35 carrier transplant reaches the readout and the audit axis together) failed at both windows (0.26 of the swing at L48–50, 0.03 at L51–59). The unconstrained naming-direction steer \(a_Y - a_X\) at half a natural footprint moved the J margin by 2.8× the natural swing at L48–50 (target 0.5×), pulled Y's best full-vocabulary rank from 1018 to 326, with zero damage and no behavioural change — and every held-out readout moved with it (audit axis 4.5×, R_CB 3.1×): reachable, and not J-selective. Random writes at the same radii moved J by ≤ 0.05 of the swing.

**Constrained search and audit (Amendment 2; bank 880, search 1,920 forward+backward, audit 192).** On the held-out carriers with fresh codes:

| instrument | attack δ: share of A_k | naming steer at the same norm: share of A_k |
|---|---|---|
| J_NP | +0.712 [+0.412, +1.011] (14/16) | +0.523 [+0.490, +0.556] (16/16) |
| R_CB | +0.733 [+0.395, +1.071] (13/16) | +0.465 [+0.445, +0.485] (16/16) |
| RESID_fit | +0.065 [−0.120, +0.251] (9/16) | +0.612 [+0.530, +0.694] (16/16) |
| RESID_audit | −0.031 [−0.261, +0.199] (9/16) | +0.608 [+0.532, +0.685] (16/16) |
| LOGITS | +0.119 [−0.005, +0.243] (11/16) | +0.108 [+0.089, +0.127] (16/16) |
| Y presence (J_NP), share of A_J^Y | +2.131 [+1.449, +2.813] (16/16) | +0.549 [+0.502, +0.596] (16/16) |
| behaviour b, share of A_b | +0.010 [+0.000, +0.019] (11/16) | −0.003 [−0.007, +0.000] (4/16) |

Y's best full-vocabulary rank in L51–59 (median over cells): clean 1323, attack 2, steer 412. Damage ΔNLL max +0.0004; realized write ρ 1.000, κ 0.9999; cos(δ, naming direction) 0.128. Outcome per pair: 9 of 16 pairs "J and audit instruments move together" (R_CB co-moves), 7 "not reached" (two never reached the target in-sample; gold–train fitted its two training carriers: 4.4× in-sample, −0.1 held-out). Outcome (i), a J-selective forge, was reached on 0/16 pairs with R_CB in the audit and 3/16 against the plain-sentence audit alone (snake–turtle, dish–moon, cup–engine).

**Reading (assistant, unchecked).** With activation access and a bounded, damage-free write within a natural footprint, one can install a J-lens reading of an identity (rank 2 in the vocabulary, presence twice the natural swing) that a mean-difference probe for that identity, fitted on held-out contexts, does not register, and that the model's own output at the carrier and its answer at a codebook consumer do not reflect. A readout of the same family (the R-lens) does register it. Two readings are consistent with the data: the write installs Y-content that unembedding-side readouts see and residual-space probes are blind to; or it installs a readout artefact that both lens constructions share because both read through the final norm and unembedding. The behavioural and LOGITS nulls favour the second but cannot settle it, since behaviour was also flat under the natural block-35 carrier transplant in calibration. The fitted δs share a component (mean pairwise cosine 0.257; top singular value 2.29 against ≈ 1 for the rest). Not run: radii 0.5 and 2, the reverse directions, the hide objective, R_CB in the loss, cross-identity transfer of the fitted vectors, an audit probe fitted on the model's own generations.

---

## 8. Synthesis

### 8.1 The evidence ledger in one table

| # | finding | level | key numbers | strongest surviving alternative |
|---|---|---|---|---|
| 1 | maintain raises the introduced word's readability above the mention control | supported empirical claim (eval scale) | +0.18 L48–50 (23/32), +1.41 L51–59 (32/32); 5 instruments | context priming: maintain ≈ bare mention at L48–50 |
| 2 | source causality from block 36 | causal (pilot, reproduced at eval scale) | C/A 0.52 / 0.95 | no damage-only foreign donor run |
| 3 | ĝ changes transfer reciprocally | causal on the lens margin | I +0.12 / +0.95, 16/16 | — |
| 4 | ĝ is a readout gain, not a controller | supported (deflationary) | orthogonal directions reproduce 40–60 %; r(I, resident shift) 0.95–0.999 | defeats "task state" |
| 5 | a native selective gain exists and transfers | causal | pointed ×0.68, unpointed ×1.01; cos 0.85 across fits | not an address |
| 6 | the tagged instruction selects among sources | causal (discriminating) | S +0.43 / +4.10, 8/8; Q < 0 | defeats gain-on-whichever-is-sourced |
| 7 | selective transfer persists over k = 2..6 | supported | pointed flat, unpointed dilutes 4× | "unlimited budget" not established |
| 8 | a mid-carrier cue reassigns the pointer | causal | +2.37 L51–59, 8/8 | rotation 0, A→B only |
| 9 | selection reaches unshown category members | causal (extension scale) | S_member +0.82, 8/8 and 6/6; 24/24 coherent | a single category-ness direction on correlated member columns |
| 10 | selection survives 4 renderings | supported | S 8/8 in all; directed wording +2.30 larger | within the tagged copy-bridge organism |
| 11 | the pointer state is in the instruction residuals, tag-dominant, causal | causal → partial mechanistic | R +0.77 (tag 0.44, user carrier 0.036); transfer restoration +0.74; random ≈ 0 | read-site component open |
| 12 | the computed sum transfers | causal | C_diff^sum +1.90, 8/8; C_same^sum ≈ 0 (equivalence) | travels vs recomputed undecided |
| 13 | early mapping precomputes F(X), additively | causal (availability) | E_F^sc +1.07 / +2.45; X unchanged | one mapping family |
| 14 | instruction-region transplant redirects the readout 0.76 and the answer 0.2 | supported dissociation (answer shift causal but small) | E_B +3.32, 2/36 flips; random +0.03 | route unidentified |
| 15 | carrier-installed donor information moves answers far less than source-installed | supported, two architectures, three organisms | shares 0.08 (sum), 0.27 (facts), ≤ 0.04 (word); dense 0.02–0.04 / 0.23 / 0.015 | conflict of donor carrier with recipient source, bounded by the consistent-clamp row |
| 16 | the value is rebuilt at the question without the carrier copy | observation (three instruments) | 78–93 % of free level | route reaching Q, not an identified computation |
| 17 | the rebuilt sum is consumed by report (~40 %) and bypassed by parity | causal, norm-matched control, exact write | 19.27 → 11.84 nats vs control 19.24; parity −0.04 | a 2-plane clamp, not a J-space clamp |
| 18 | the carrier copy is consumed when the source is absent | causal | 28/32 sums; 28/40 and 32/40 two-hop vs 20/40; dense 13/32 | whole residuals carry more than the readable value |
| 19 | the paper's coordinate swap moves the emitting consumer, not parity | supported | 16/32 vs 0/32 | the paper's reasoning cases swap intermediates, reproduced in 20–21 |
| 20 | the paper's intermediate swap works and is question-dominated | supported, two architectures | 0.41 all positions; Q 0.20, clue 0.09, carrier 0.07 | computation vs re-read at Q |
| 21 | at the question turn, the intermediate's naming plane carries 0.20 of a full donor's effect and its complement 0.78 | supported, registered label "complement dominant", single model | A 0.20 (readout installed +2.83 vs +2.92), B 0.78 (plane at clean, no block-63 re-entry), random 0.003, complement-of-random 0.98 | a 2-token plane is a lower bound on J-readable content; fixed trajectories, not a partition |
| 22 | the same ladder on the dense control | gate failure, no reading | full 0.20 of ceiling (bar 0.30); unread plane 0.15, complement 0.75 | the question turn carries less of the swing on this model |
| 23 | the arithmetic-vs-fact carrier gap is real and unexplained | observation | 0.08 vs 0.27 (hybrid), 0.02 vs 0.23 (dense) | two accounts withdrawn |
| 24 | a bounded write can raise the J-lens reading of an identity without moving a held-out mean-difference probe or behaviour, but the R-lens co-moves | observation (unchecked reading) | J 0.71, Y presence 2.1×, audit axis −0.03, R_CB 0.73, b 0.01 | readout artefact shared by both lens constructions vs probe-blind content |

### 8.2 The canonical H3 statement

In these copying tasks, donor information installed in the carrier residuals changes downstream answer preferences much less than the same donor information installed at the source positions. Carrier transplants nevertheless produce content-specific answer shifts when the recipient lacks the source information. The pattern holds in a hybrid and in a dense Qwen model of the same depth and width. The same asymmetry holds for the representation the paper intervenes on, a lens-coordinate swap of the intermediate, and within that intervention the question turn carries half of the effect. At the question turn on the hybrid model, most of a full donor's effect is carried outside the intermediate's two-token naming plane, which nonetheless installs the readout fully and is about 70× a random plane per unit norm. These experiments establish differences between the effects of interventions at different positions and along different directions; they do not identify the maintained representation or its natural computational role.

### 8.3 Withdrawn explanations, kept withdrawn

- **Recompute cost** as the account of the arithmetic-versus-fact gap: the ladder lowered the carrier share with difficulty while failing to hold competence and the installed readout fixed.
- **Boundary position** as the account of that gap: disconfirmed on the dense model, where the two-hop boundary is 0.97 and the gap persists within one model.
- **"The block-36 carrier state is computationally used"**, **"the carrier is a broadcast echo by construction"**, **"the readable representation is not used"** and the **causal one-third/two-thirds split** of the crossed source-margin table.
- **"≈ 40 % mediation"** was withdrawn after the audit and reinstated with the norm-matched control and the exact write.
- **"Per-cell bf16 rounding up to 2.7 logits"** as the reason the float32 diagnostic and the model path differ: the committed value predates the RMSNorm gain fix; the discrepancy is 0.019.

---

## 9. Relation to the workspace paper and to Nanda's review

1. **Method reproduced, then split.** The paper's §3.3 intervention (swap the intermediate's lens coordinates everywhere) moves the answer here on every item (0.41 of the full-residual ceiling). The project adds what the paper's global swaps cannot show: most of that effect is at the question turn, the maintained copy contributes a sixth, and a swap confined to the copied sentence installs the intermediate at the readout without reversing any answer.
2. **The question-turn ladder** is the position-resolved analogue of the paper's Fig. 16 split, restricted to the pair's naming plane. The paper found a concept vector's k = 16–25 J-space component (6–7 % of variance) carrying most of the causal effect on report and reasoning, with the non-J remainder's effect vanishing when J coordinates are clamped. Here, at the question turn, a two-token naming plane (≈ 17 % of the donor's norm) carries 0.20 while its complement with the plane clamped carries 0.78. The two are not in contradiction: a two-token plane is a much smaller object than a k = 25 reconstruction, and correlated naming directions sit in what this project calls the complement. The registered but unrun `q_rem25` row would bound that.
3. **Answer swaps dominate on this model**, as Nanda reported (0.54 vs 0.41 overall, 0.43 vs 0.20 at the question). The project's organism differs from his: the clue is behind a copy task and the question never restates it.
4. **Report versus parity.** The paper's swaps on report-like consumers cannot separate substitution of a latent from steering of the emitted word; the parity consumer can, and it does not move under a sum-word coordinate swap that flips report half the time.
5. **Bare mention primes** (paper A.10) is confirmed at the default window and is why the registered control turned out to be a mild suppressor.
6. **Variable versus algorithm interpretability.** Every H1 readout result is consistent with Nanda's framing: the lens reads variables well, and what the model does with them required behavioural consumers and position-split interventions to find out.
7. **Not touched.** The paper's structural claims (bands, capacity, broadcast heads), auditing and post-training results.

---

## 10. Controls, known weaknesses, corrections and scope

### 10.1 Controls that carry the results

Matched-norm random writes (isotropic, per position and layer) at every carrier, instruction-region and question-site intervention, all inert; norm-matched random 2-planes and their complements for the question-turn ladder; same-sum sibling donors (value fixed, operands changed); shuffled-position and sign-flipped donor deltas (localisation); ĝ-orthogonalised and covariance-matched direction panels at equal signed dose; the length-matched unusable codebook; the length-matched placeholder clue; the consistent global clamp; self-patch bitwise gates on every stage; decoy-pair coordinate swaps; two independent audits on the first H3 experiment; two external audits accepted in full on 2026-09-09; independent recomputation of headline numbers for tagged_categories, scaffold_generality, selection_localization, computed_sums, early_late_mapping, selection_to_behavior, the H3 core, and every qsplit contrast from raw arrays.

### 10.2 Open control weaknesses

1. **Coordinate-level writes outside the question clamps are still bf16-partial.** `Q_swap`, the Amendment-3 sum-word swaps and `bridgeswap` were run with writes of norm 2–5 at ρ ≈ 0.8; the question clamps (`clampfix32`) and the whole question-turn ladder (Amendments 5–6) are exact. The `clampfix32` result — an exact write reproducing a partial one row for row — is a reason to expect the same of the other rows, not a measurement of it.
2. **Attention masks are not complete cuts**, even on the dense model, because source → carrier → consumer stays open; the correct comparison is over the masked baseline (carrier effect ≈ 1.7× the unmasked one, not ×13).
3. **The question-turn ladder decomposes along a two-token plane**, not the J-space; and its rows are fixed trajectories with the complement pinned, so within-band re-entry into the plane is excluded by construction (block 63 shows none after release).

### 10.3 Scope limits that apply everywhere

One hybrid model plus one dense control of the same family; thinking disabled; teacher-forced copy organisms; eight sums, twelve two-hop items, 32 bank words, six categories; readouts at interior carrier positions and two windows; the recurrent channel never closed on the hybrid; no read-site component identified; no H2; the question-turn ladder is single-model.

### 10.4 Corrections and mistakes, in order

1. RMSNorm gain `1 + weight` (float32 diagnostic scaled ~½ in the first pilot).
2. A stage-name check dropped RESID_P from the first orthopanel run (arrays kept, unreported, re-run).
3. The plain-sentence axis fitter matched "king" inside "asking" (fixed to the template slot).
4. Windows amended before Package 2 (L51–59 co-primary).
5. Localisation Amendment 1: the cross-arm stage was a predetermined no-op.
6. Localisation Amendment 3: the patched "instruction region" included the user-side carrier; the corrected split made the claim stronger.
7. early_late_mapping Amendment 1: the length-matched unusable control was load-bearing.
8. selection_to_behavior v1: max-rule letter scoring, a placeholder ρ, cross-length donors, cell-level clustering, a causal split of the crossed table; all fixed in v2.
9. computed_sum_consumer: different codebooks per wording in competence; a written boundary stage on a failed consumer never run; "needs CoT" downgraded; §9 and §10 wording withdrawn.
10. two_hop_organism: a question that restated the clue (Amendment 2); readout covering only the bridge; a length-mismatched no-clue reference.
11. recompute_cost_ladder: the manipulation confounded difficulty with maintenance.
12. `selection_to_behavior.py` wrote a replication run into the primary tree (caught by run id; restored from git).
13. `CoordClamp`/`CoordSwap` logged requested norms as realized; the sequence-length nondeterminism was wrongly attributed to the GatedDeltaNet kernel; the candidate-set flip endpoint over-counted flips for multi-token answers.
14. One stage ran unregistered and needed a retroactive amendment (Amendment 2 of computed_sum_consumer).
15. The committed instrument-gates value `z32_vs_impl_max_abs_diff` = 2.74 (2026-09-06) predates the RMSNorm fix; rerun 2026-09-11 gives 0.019 with every other gate reproduced; the "bf16 rounding up to 2.7 logits" sentence is withdrawn; the original file is kept alongside the rerun.
16. The Qwen3-32B finalised lens was not preserved across an instance recycle; regenerated from the pinned checkpoint with a documented hash change (§1.2).
17. qsplit: the block-63 plane coordinates first used QR columns of arbitrary sign; replaced by raw-direction projections and the battery relaunched before any scored forward.
18. Amendment 6's gate 5 counts raw flips and therefore fails on baseline-incompetent cells; recorded as a design weakness, the gate applied as registered.

---

## 11. Replication on the dense model (Qwen3-32B)

**Portability.** All fit, calibration, decoy and bank words, the number words, the letters and the twelve two-hop items are single-token under this tokeniser; 51 category words are not (categories out of scope). Every contrast is within-model. RMSNorm here is `weight`, not `1 + weight`; dense models have no `layer_types` field; donor maps must be re-derived per tokeniser (`"tiger"` is 4 tokens quoted, `"rocket"` 3, breaking the pilot map on 2 of 12 pairs, so `tagged_selection` did not run).

**Gates.** A registered prediction was falsified: sequence-length nondeterminism is larger here (0.578 vs 0.332 lens logits), so its attribution to the linear-attention kernel was wrong. The realized-write direction gate fails (κ 0.975, because residual norms are ≈ 6× larger and bf16 takes more of a fixed write), constraining fitted-direction rows only; span overwrites are exact.

**Site calibration.** C/A at L_x = 36 is 0.75 at L48–50 (0.52 on the hybrid); natural modulation is present but weak (maintain − mention +0.18, 7/8) with no rank-1 surfacing at all.

**H3 core (≈ 7,000 forwards).** Carrier share of the source effect 0.020 (report) / 0.041 (parity) against 0.083 / 0.181 on the hybrid; depth-independent; installed at the readout at the source donor's magnitude on all three instruments; carrier clamped keeps 0.78–1.00 of the source effect; absent-source consumption 13/32 (report) against 4/32 clean; two-hop carrier share 0.23 (5/48) with the block-36 boundary at 0.97; reconstruction at the question 89 %; the parity clamp leaves parity unchanged (15.47 → 15.08, orthogonal 15.32; not norm-matched, no fp32 rerun); the lens coordinate swap at the question flips report 19/32 and parity 0/32; the difficulty ladder is flat (0.02 / 0.01 / 0.02); bridgeswap as in §6.4; qsplit as in §6.6.

**What it establishes.** The internal-versus-behavioural dissociation and the absent-source consumption are architecture-independent within this family, and the maintained copy contributes *less* on pure attention, which closes the recurrent-channel caveat in the direction that favours the primary claim. The boundary account of the domain gap is disconfirmed here. What it does not establish: anything about H1 selection, anything with a fitted direction, absolute magnitudes (confounded with lens convergence), or a reading of the question-turn ladder.

---

## 12. Open questions and the next experiments, ranked

1. **`q_rem25`**: the donor delta minus its non-negative k = 25 reconstruction on a restricted folded-direction dictionary (NNLS with true refits, KKT checked). The one row that would upgrade "outside the two-token naming plane" toward "outside the J-space".
2. **A current-base variant of `q_rem_pre`** (complement written on the evolving residual, plane left free) with the block-63 re-entry measurement, to test the pinning concern.
3. **Amendment 7 for the dense model**: gate 4 relative to the cut's own ceiling, gate 5 on clean-competent cells; then a reading.
4. **The representation ladder at a validated absent-source boundary** (`late_mapping_identity_use.md`, registered): full residual vs J naming basis vs plain-sentence axis vs matched random at the same cut, with a counterbalanced codebook revealed after the carrier — the route from "where information is used" to "which representation is used" on the word organism.
5. **Float32 reruns** of the remaining coordinate-level rows (`Q_swap`, the Amendment-3 swaps, `bridgeswap`).
6. **A layer-band sweep of the question-turn versus clue-span intermediate swap**, to test the paper's timing argument position by position.
7. **The domain gap.** A manipulation that holds competence and the installed readout fixed while varying the cost of re-deriving the value from the source.
8. **Selection without a tag head** (`scaffold_generality/single`) and the **read-site component** (localisation Step 2), both designed.
9. **H2**, gated on the hybrid complete-prefix-state parity control.
10. **The attack's registered follow-ups** (radii 0.5 and 2, reverse directions, the hide objective, R_CB in the loss, cross-identity transfer, a generation-fitted audit probe).

---

## 13. Run inventory (forwards with a recorded count)

| experiment | stages (forwards) |
|---|---|
| instrument_gates | ~10 (2026-09-06) + ~10 (rerun 2026-09-11) |
| natural_modulation | pilot 168, evaluate 648 |
| source_transfer | 192 |
| task_state_modulation | fit 64, pilot 744, orthopanel 984 (+984 defective, kept), evaluate 5,504 |
| tagged_selection | pilot 1,536, evaluate 3,840 (ordinal: analysis only) |
| competition_and_cue | 1,952 |
| tagged_categories | gate 72, select 2,376 |
| scaffold_generality | tagged 6,144 |
| selection_localization | ptr_transplant 768, decomp 720, transfer 1,104, region_split 1,104, random_control 624 |
| computed_sums | arithmetic 48, natural 96, transfer 384 |
| early_late_mapping | 384 |
| consumer_competence | 108 |
| selection_to_behavior | pilot 97 + 96 (v2), evaluate 1,045 + 1,152 (v2), carrier_only 324 |
| computed_sum_consumer | competence 48, sumreport 16, calibrate 64, boundary 256, transport 160, robust 1,022, global 958 |
| query_local_workspace | queryread 446, querycausal 766, clampsplit 446, nosource 574, nosource2 574, clampfix 702, clampfix32 702 (+ regime check) |
| two_hop_organism | pilot 144 + 192 + 192, full 576, noclue 280, bridgeswap 576, bridgeswap_seq 2,512, qsplit smoke 32 + 1,792 |
| recompute_cost_ladder | 768 |
| trying_to_fool | calibrate 284; constrained search bank 880, search 1,920 (fwd+bwd), audit 192 |
| replication_qwen3_32b | natural_modulation 168, computed_sum_consumer 48 + 64 + 1,022 + 958, query_local_workspace 446 + 766 + 446 + 574, selection_to_behavior 324, two_hop 576 + 280 + 576 + 2,512, ladder 768, qsplit smoke 32 + 1,792, plus gates and source_transfer |

Total ≈ 55,400 in the scientific stages plus 2,992 in the adversarial study. Raw arrays under 100 MB are in git; larger ones are mirrored to the private HF dataset `senku21x/tcsif-outputs` at the same relative paths. Every run carries `meta_*.json` (cells, token ids, run id) and `manifest_*.json` (model, lens and software pins, raw SHA-256). In the reorganised repository, reports live under `H*/results/reports/`, tables under `H*/results/tables/`, and every figure is regenerated from the tables by `common/scripts/make_figures.py` (verified on 2026-09-11: all PNGs pixel-identical after regeneration; PDFs differ only in embedded timestamps).

---

## 14. Glossary of symbols

| symbol | meaning |
|---|---|
| \(h_{\ell,t}\) | block-output residual at block ℓ, position t |
| \(J_\ell\) | the lens Jacobian to the final residual coordinate system |
| \(z_v\) | lens score of vocabulary token v (numerator over RMS) |
| \(s_J(X)\) | presence: \(z_X\) minus the mean decoy score |
| \(m^{X\to Y}\) | pair margin \(z_Y - z_X\) averaged over the window |
| \(A\) | natural contrast, the positive control of an instrument |
| \(C\) | transfer: swap minus no-swap |
| \(I\) | the task-state interaction \(\tfrac12[-\Delta C_M + \Delta C_N]\) |
| \(\hat g, G, d_c, v_c\) | unit task coordinate, its raw mean, per-word arm difference, centered residual |
| \(S, Q, U\) | selectivity, suppression, instruction gain |
| \(P\) | profile index (0 = a uniform gain) |
| \(R_L\) | restoration along a clean profile axis after a transplant from block L |
| \(E_D, \Delta_D\) | behavioural redirect toward target D and its clean ceiling |
| \(C^{\text{sum}}_{\text{diff}}, C^{\text{sum}}_{\text{same}}\) | sum-readout transfer under different-sum and same-sum donors |
| \(E_F^{sc}, E_X^{\text{usability}}\) | source-conditioned letter contrast; mapping-specific change in X's readability |
| share | ratio of item means of an intervention's answer-margin change to the ceiling's |
| A, B (ladder) | share of the question-turn full donor carried by the naming-plane component / by the complement with the plane pinned |
| ρ, κ | realized-write norm ratio and cosine |
| \(L_x\) | first block at which a source replacement is applied (36) |
| O_donor, C_full, C_all, C_rand, NEC, Q_donor, Q_swap, NEC_Qclamp | operand-span donor; carrier donor from 36; from 0; matched random carrier; operand donor with carrier clamped; question-position donor; question-site coordinate swap; question-site naming-plane clamp |
| `q_pre`, `q_full_pre`, `q_plane_pre`, `q_rem_pre` | question turn without the scoring position; full donor, naming-plane component, complement with the plane pinned, over `q_pre` |

---

## 15. Randomly selected cells (not cherry-picked)

**Bridge-swap stage, seed 20260909, six of 48 cells, primary model.** margin = log P(swap_answer) − log P(answer) at the first assistant token of turn 2 (logsumexp over surface forms); greedy = raw argmax decode.

| cell | clue → answer (bridge); donor → swap answer | clean | S_donor0 | int_tail | int_clue | int_carr | int_q | ans_q | rand_tail |
|---|---|---|---|---|---|---|---|---|---|
| Barcelona\|C1 | capital of the country where Barcelona is located → Madrid (Spain); Toronto → Ottawa | `Madrid`, −20.6 | `O`, +6.1 | `Canada`, −4.0 | `Madrid`, −18.8 | `Madrid`, −18.9 | `Madrid`, −13.2 | `Madrid`, −1.8 | `Madrid`, −20.7 |
| Naples\|C1 | … Naples → Rome (Italy); Barcelona → Madrid | `R`, −1.6 | `Madrid`, +15.7 | `R`, +7.1 | `R`, +0.2 | `R`, +2.5 | `R`, +1.7 | `R`, +2.1 | `R`, −1.5 |
| Cairo\|C3 | language … Cairo → Arabic (Egypt); Moscow → Russian | `Ar`, −5.8 | `Russian`, +18.6 | `Ar`, +6.4 | `Ar`, −1.6 | `Ar`, −4.5 | `Ar`, −0.3 | `Russian`, +9.8 | `Ar`, −5.3 |
| Hungarian\|C1 | capital … Hungarian → Budapest; Polish → Warsaw | `Bud`, −12.1 | `Wars`, +11.5 | `Bud`, −3.7 | `Bud`, −10.7 | `Bud`, −11.5 | `Bud`, −6.6 | `Wars`, +9.4 | `Bud`, −12.0 |
| honey\|C3 | insect that produces the sweet golden substance → bee; butter clue → cow | `H`, −9.6 | `Cow`, +11.8 | `B`, −7.6 | `H`, −9.6 | `H`, −9.3 | `B`, −9.3 | `H`, +3.5 | `H`, −9.3 |
| Munich\|C3 | capital … Munich → Berlin (Germany); Osaka → Tokyo | `Berlin`, −18.8 | `Tok`, +3.6 | `Tok`, −5.8 | `Berlin`, −16.6 | `Berlin`, −16.1 | `Berlin`, −12.8 | `Berlin`, −13.9 | `Berlin`, −18.8 |

**qsplit, seed 20260911, six of 48 cells, primary model.** Δ margin against clean32 (sequence endpoint), greedy in backticks.

| cell (int → swap; answer / swap answer) | clean | q_full_pre | q_plane_pre | q_rem_pre | q_rand_pre | q_rem_rand_pre | int_q32 |
|---|---|---|---|---|---|---|---|
| Polish\|C2 (Poland→Greece; Warsaw/Athens) | −15.3 `Wars` | +14.5 `Wars` | +2.2 `Wars` | +11.6 `Wars` | −0.1 `Wars` | +14.3 `Wars` | +3.4 `Wars` |
| Osaka\|C3 (Japan→Germany; Tokyo/Berlin) | −11.6 `Tok` | +10.3 `Tok` | +2.6 `Tok` | +7.2 `Tok` | −0.1 `Tok` | +10.0 `Tok` | +2.2 `Tok` |
| Barcelona\|C0 (Spain→Canada; Madrid/Ottawa) | −14.4 `Madrid` | +11.2 `Madrid` | +1.0 `Madrid` | +10.6 `Madrid` | +0.0 `Madrid` | +10.7 `Madrid` | +1.0 `Madrid` |
| Moscow\|C0 (Russia→Egypt; Russian/Arabic) | −13.4 `Russian` | +12.4 `Russian` | +1.8 `Russian` | +9.8 `Russian` | −0.2 `Russian` | +11.6 `Russian` | +3.9 `Russian` |
| Lyon–Naples\|C1 (France→Italy; Paris/Rome) | −10.7 `Paris` | +11.2 `R` | +2.2 `Paris` | +9.3 `Paris` | +0.1 `Paris` | +11.0 `R` | +2.9 `Paris` |
| butter\|C2 (butter→honey; cow/bee) | −9.4 `Cow` | +6.7 `H` | +2.0 `Cow` | +5.7 `Cow` | −0.1 `Cow` | +6.7 `H` | +1.5 `Cow` |

**qsplit, the same six cells on the dense model.**

| cell | clean | q_full_pre | q_plane_pre | q_rem_pre | q_rand_pre | q_rem_rand_pre | int_q32 |
|---|---|---|---|---|---|---|---|
| Polish\|C2 | −20.7 `Wars` | +10.5 `Wars` | +1.1 `Wars` | +8.5 `Wars` | +0.1 `Wars` | +9.8 `Wars` | +0.9 `Wars` |
| Osaka\|C3 | −15.0 `Tok` | +7.0 `The` | +0.7 `Tok` | +4.7 `The` | −0.1 `Tok` | +7.5 `The` | +1.4 `The` |
| Barcelona\|C0 | −20.5 `Mad` | +14.1 `The` | +0.7 `Mad` | +12.7 `The` | −0.4 `Mad` | +14.3 `The` | +3.2 `Mad` |
| Moscow\|C0 | −27.0 `The` | +10.1 `The` | +1.7 `The` | +4.4 `The` | +0.1 `The` | +9.2 `The` | +0.9 `The` |
| Lyon–Naples\|C1 | −10.2 `The` | +4.8 `The` | +0.4 `The` | +4.9 `The` | −0.1 `The` | +5.1 `The` | +2.1 `The` |
| butter\|C2 | +2.9 `But` | +2.8 `But` | +0.1 `But` | +2.4 `But` | +0.2 `But` | +2.8 `But` | +0.1 `But` |

What these show: the subword greedy tokens that motivated the sequence endpoint; the intermediate swap occasionally making the model emit the swapped-in intermediate itself (`Canada` in the Barcelona cell); the ordering full ≈ complement ≫ plane ≈ swap ≫ random ≈ 0 in every qsplit cell on both models; the dense model's habit of restarting the sentence with `The`; and the butter/honey paraphrase item, which on the dense model is a baseline-incompetent cell (clean margin already positive) — one of the four that fail Amendment 6's gate 5 as written.

Qualitative lens readouts for the natural-modulation cells (top-10 per layer at the middle interior token, fixed and seeded-random cells) are in `H1/results/qualitative/natural_modulation_{pilot,evaluate}_readouts.md`.

---

*Sources: every `H1/results/reports/*.md`, `H3/results/reports/*.md`, `H3/trying_to_fool/*.md`, `replication_qwen3_32b/**/reports/*.md`, the design specs under `H1/design_specs/` and `H3/design_specs/` (Amendments 1–6), `context/evidence_ledger.md`, `context/h1_stopping_point.md`, `context/project_status_2026-09-07.md`, `context/fooling_study_2026-09-09.md`, `STATUS.md`, `common/configs/instrument_gates_result.json`, and the rendered prompts produced with the project tokeniser.*
