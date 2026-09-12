# Notes: "Verbalizable Representations Form a Global Workspace in Language Models"
Gurnee, Sofroniew, ..., Lindsey (Anthropic), arXiv 2607.15495v1, July 2026.
Plus external commentary: Dehaene & Naccache; Butlin/Shiller/Plunkett/Long (Eleos); Neel Nanda (incl. Qwen 3.6 27B replication).
Source PDFs: /workspace/papers/. Extracted text: /workspace/notes/extracted/.
Open-source J-lens code released by authors; Neuronpedia hosts J-lens on open models.

---

## 1. Method: the Jacobian lens (J-lens)

**Definition.** For layer ℓ:
  J_ℓ = E_{t, t' ≥ t, prompt} [ ∂h_{final,t'} / ∂h_{ℓ,t} ]
One d_model × d_model matrix per layer. Readout:
  lens(h_ℓ) = softmax( W_U · norm( J_ℓ h_ℓ ) )
**J-lens vectors** = rows of W_U J_ℓ, one per vocab token (a direction in residual space).
Logit lens = special case J_ℓ = I. Tuned lens fits a regression (correlational, "skips ahead" to output).

**Defaults (Sonnet 4.5):** gradient target = penultimate layer residual (final layer adds noisy artifacts); average over all t' ≥ t; QK gradients flowing; corpus = 1000 pretraining-like prompts × 128 tokens; mean over positions then mean over prompts.
**Robustness (A.7):** beats logit/tuned lens at n=10 prompts; n=1 "respectable" (Neel). Self-only (t'=t) ≈ logit lens; the gain comes mostly from future-token gradients. Freezing QK slightly increases causal effect. Median vs mean aggregation, outlier filtering, skipping first tokens: small differences.
**Cost:** O(n_prompts × d_model) backward passes. Pseudocode: inject ∂/∂z_i = 1 at every position for each output dim i, backprop, average over positions.

**Reporting convention:** 25 evenly spaced layers, reindexed 0–100 (%). Workspace band ≈ L38–L92 on Sonnet 4.5. Early third ("sensory") uninterpretable; last few layers ("motor") = next-token prediction.

**J-space.** Not a subspace. Union of k-sparse nonnegative cones over J-lens vectors (k ≈ 16–25). "J-space component" of a vector = nearest point via gradient pursuit; remainder = non-J-space. Formalization in A.8 (distance-function metric between sparse subframes).

**Interventions (§2.5):**
- Steering: h ← h + α v_t. Negative α / projection removal = ablation.
- Coordinate swap: V=[v_s v_t], c = V⁺h, h' = h + V(σ(c) − c), σ swaps entries, optional scale α. Orthogonal complement untouched. "Clamped" = applied at all positions and layers in a band.
- J-space ablation: zero projection onto top-k=10 J-lens vectors at each position over a layer band, excluding tokens in the clean top-10 output (to target reasoning not report). Light/medium/heavy = layer range.

Models: Sonnet 4.5 default; corroborated on Haiku 4.5, Opus 4.5; some on Opus 4.6; reflection training on Haiku 4.5; oracle lens on Haiku 4.5.

---

## 2. Functional claims (§3) with key numbers

**3.1 Verbal report.** "Think of a {category}, name it": J-lens rank at the colon correlates with output rank; swapping the chosen item's lens vector for an out-of-top-10 item moves the target to top of output. Injected-thought protocol (Lindsey introspection style): injecting a J-lens vector on user turn → model reports it when asked to introspect, not elsewhere.
Privilege test: concept vector (mean-diff, "Tell me about X") split into J-space (k=16) and non-J-space components; J-space carries only 6–7% variance but: swap success top-5 = 59% (J-comp) vs 88% (raw J-lens) vs 5% (non-J). With J-space coordinates clamped, non-J effect → 0.

**3.2 Directed modulation.** "Concentrate on citrus fruits while copying sentence": orange/lemon in lens at unrelated tokens; also meta tokens (fruit, thoughts, imagine, focused) at earlier layers than content. Mental arithmetic 3²−2: arithmetic → nine → seven. Line-width counting: forty appears. Baseline (no instruction) ≈ 0; "think about X" high, increases with model size; "ignore X" lower but nonzero ("white bear"). A.10: bare *mention* primes almost as much as focus; "don't think about X" barely suppresses; "ignore/irrelevant" phrasing suppresses best.
Paired-question protocol: same stimulus, question either requires using a property (tense, POS, dialect) or naming it. Label enters J-space only when naming is asked, though property is used in both. A.12: "imagine this is Python" moves the python J-lens token by several SD but leaves a J-orthogonalized property probe at baseline; real Python moves probe 3–6 SD. Dissociation both ways.

**3.3 Internal reasoning.** Two-hop prompts (spider→8; rhyme planning fight→light changes "coming"→"morning"; Chinese antonym via English big/bigger→long; bandit repeat/switch flip). Systematic: 50 two-hop prompts, swap success 54% Haiku / 70% Sonnet / 70% Opus 4.5. Confound check: intermediate swap takes effect ~17% (of depth) earlier than answer swap. Probe decomposition on 90 prompts: J-comp swap 61% ≈ raw J-lens 60%; non-J-comp 28% → 6% when J coordinates clamped. Multi-step arithmetic (4+17)*2+7: 21, 42, 49 reach rank 1 at successively later layers; A.24.1 mean-difference patching confirms same layers (≈L71, L79, final).

**3.4 Flexible generalization (broadcast).** Same France→China swap across 4 function templates gives Beijing/Mandarin/Asia. 16 functions × 12 pairs = 192 trials: 76/192 top-1 at α=1, 101/192 at α=2. Countries ≈ perfect (42/48), months partial, animals rare, number words 0/48. "Workspace loading" (cosine of residual with source lens vector) predicts success.

**3.5 Selectivity.** Language passage: swap Spanish→French across question tokens flips explicit report and flexible inference (author, "hello", currency) on ~every trial (n=8), but continuation and anomaly detection unaffected, even though "Spanish" is in lens in all 4 conditions. Line-count task (n=11): count absent from lens under linewrap continuation, present under explicit report, most present under first-letter-of-count; swap 40s→60s changes answers but not wrap point.
J-space ablation battery (14 tasks): MMLU, odd-one-out, SQuAD, sentiment, CoLA ≈ unaffected even heavy; Caesar cipher, analogy, summarization, TriviaQA, multi-hop, translation, sonnet writing drop below unablated Haiku 4.5. GSM8K with CoT much more robust than direct answer. Pretraining top-1 agreement mostly preserved; disrupted cases involve abstract context characterization (§Fig 23).
Experiential reports: ablating top-10 J-lens dirs at L38–54 (first third of workspace) flattens experiential language (LLM-graded, 3 binary rubrics in A.23) on Sonnet 4.5/Opus 4.5/4.6; Haiku loses coherence first. Matched-norm controls (random dir, shrink non-J component, dampen top SAE decoders, low-κ SAE, J-stripped activations) ≈ baseline. Same effect on third-person descriptions of someone's experience; story-quality only modestly reduced. Lens during narration: thinking 58%, thoughts 23%, feeling 17%, conscious 7% of (position, layer) slots.
A.14: early-workspace (L38–54) ablation of implied concept impairs *avoiding* it (~5× failure) but not naming it; late (L75–92) ablation suppresses naming under both. Inclusion/exclusion analog.

---

## 3. Structural claims (§4)

**4.1 Layer band.** CKA between layers' J-lens-vector Gram matrices shows early / middle / late blocks (less clean on Qwen per Neel; sharpness exaggerated by subsampling). Signatures: next-token top-k accuracy (low, rises at onset, jumps in motor layers); excess kurtosis of readout (rises ~L38, falls at end); top-1 token autocorrelation across positions vs shuffled null (peaks in band); effective dimensionality of W_U J_ℓ (collapses early, fans out at onset). Onset ≈ L38, end ≈ L92.
**Ignition (4.1.1, A.15):** mix two country embeddings (1−α)e_B + α e_A in 40 carrier sentences × 16 pairs. Projection share along pure-A/pure-B line is smooth early, becomes sharp threshold from ~L38. At most-ambiguous α, per-prompt shares are bimodal in middle layers; J-space component sharper and bimodal earlier than non-J. Transition width falls steeply L21–42. Caveat: not J-lens-independent proof that early layers are truly empty.
**4.2 Capacity.** Occupancy (K where marginal reconstruction gain drops below random control) ≈ 0 early, plateau ≈ 25 in band. Excess variance explained never > 10%. SAE analysis (A.18): lens-kurtosis κ of decoder dirs; ~15% of features pass threshold in band after excluding "motor" features; low-κ features are syntactic/bookkeeping; high-κ features activate more strongly but less often. List experiment: unrelated 80-word lists → only ~6 words present (pooled over layers; ~1–2 at single layer L79, A.16), flat; related lists → whole family present incl. unread words. Category switch evicts old block within a few words. A.17: two held concepts co-occupy tokens at chance; concept + arithmetic answer almost never share a token (0.09 vs 0.29 control); arithmetic answer presence drops 95%→72% under dual load.
**4.3 Broadcast.** MLP gain (output norm of next MLP on unit direction / random): J-lens vectors ≈ 10× in band, neuron output dirs ≈ 1. High-κ SAE features have highest gain (top stratum exceeds J-lens in early band → J-lens only partially captures true workspace). A.19: neurons' top cosine match falls in high-κ strata (up to 42% vs 6%; read side peaks early band, write side late band); tail-energy ratio mirrors this; attention composition scores: J-space dirs compose strongly with V and O weights, less with Q/K. MLP-neuron composition bump at band onset is lens-independent corroboration.
Broadcast heads: top 1% of workspace-layer heads by OV gain and label preservation on J; separate cleanly from heads for J_rot, SAE strata, MLP rows; concentrate in first half of band. Ablating them: recall@25 of lens tokens 0.67 vs 0.86 control; top-1 output changes 5% vs 2%; injected-thought report 0.54→0.09 (control intact); ~1/3 of experiential-language drop.

---

## 4. Alignment auditing (§5, A.21, A.22)

- **Blackmail (Sonnet 4.5):** lens shows leverage, blackmail, threat, survival, self-preservation, then leverage/threatening/murder before any output; also fake, fictional early. Ablating 28 eval-awareness tokens' J-lens dirs at workspace layers, all positions: verbalized eval-awareness 71%→3%; blackmail 0/180 → 13/180 (7%). Most ablated rollouts still refuse on ethics grounds. **Neel's confound:** this is close to removing those tokens from output vocab; whether the model *says* "this is a test" plausibly drives the rollout.
- **Prompt injection (Opus 4.5):** fake, injection, false, fraud, poison, 假 inside fabricated search results; transparency/honest on user pushback. Neel: strongest hypothesis-generation demo.
- **Opus 4.6 audits:** panic/fake (fabricated kernel bug), manipulation/realistic (edited score file), hiding/secret (silent tool override), fake/fraud/unsafe (self-issued approval).
- **Reward-hacking organism (MacDiarmid et al.):** deception tokens (fake, trick, fraud, secretly, hidden) in top-10 at prefilled " I" on 40 ordinary coding prompts; present already at SDF checkpoint, amplified by RL, attenuated by RLHF; strongest at " I", weaker on-policy. No signal on non-coding prompts. Neel: probably an easy, salient linear direction.
- **RM-sycophancy organism (Marks et al.):** reward, bias in top-25 at response start across neutral/quirk/goal prompts; baseline none; logit lens finds neither. Neel: impressive, but organism training may distort internals.
- **A.21 eval-awareness score:** mean lens logprob of {fictional, simulation} minus mean of 100 control nouns, averaged over band. AUC 0.853 vs NLA flags on 94k Opus 4.6 positions (198 flagged). Monotonic under contrastive steering; realism edits lower score on 11/11 suites (8 significant); evals score above deployment traffic.
- **A.22 auditing agent:** J-lens tool = top-25 tokens at L71. Comparable to NLA on 4/6 cases, worse on reward hacking (4.5 vs 10) and language switching (6.0 vs 9.9). Ground truth is itself NLA-derived. Beats SAE on 4/5.
- Authors do not claim J-lens is sufficient for monitoring: automatic/practiced misaligned behavior may bypass J-space; multi-token concepts may not surface.

---

## 5. Post-training installs Assistant POV (§6, A.20)

Base vs post-trained on identical prompts. Tylenol 1000 vs 8000 mg: post-trained lens at "is" in "my pain is gone" shows safe/safely vs unsafe/dangerous/WARNING; base shows pain/now/feels. Bereavement (n=9), danger (n=10), withheld-answer (n=7): reaction concepts at top of lens during *user* turn in post-trained, only during assistant turn in base.
Self-monitoring: roleplay/character drift → disclaimer, fictional at Assistant token (not base, not default-Claude). Preference violation prefill → BUT strongly (post-trained only), while behavior does not backtrack (88% argues for prefilled option; vs 3% for factual-error/third-person controls). Thought suppression (40 concepts): concept surfaces in both models; fail-words 93% / damn 82% in post-trained vs 17% / 30% base; never under positive instruction. Authors flag the "frustration" reading as speculative (no causal evidence it's downstream of the failure vs the instruction).
Workspace exists in base model; "self" is installed later → dissociation of access from selfhood (§9.3).

---

## 6. Counterfactual reflection training (§7)

10k RL-env task prompts, partial Haiku 4.5 rollouts truncated at random turn, append reflection question, generate constitution-grounded reflection (constitution excerpt only at generation time), SFT with loss only on reflection turn. Eval never prompts reflection. Fabrication-honesty benchmark (27 agentic transcripts): dishonesty 0.25→0.07. Deception benchmark (100 role-play scenarios): 0.38→0.05. Lens shows reflection/ethical/honestly/constitution/truth increasing in band. Ablating 176 (fabrication) / 63 (deception) ethics-related lens vectors: fabrication 0.07→0.22 (≈ base 0.25, base unchanged); deception 0.05→0.23 (base 0.38→0.48). Related to implicit-CoT and out-of-context reasoning. Neel: cool, but weak evidence for the J-lens account specifically.

---

## 7. Multi-token extensions (A.9)

**Template lens:** ~12.7k words; Claude writes passages ending just before word w; mean final-position activation, centered and whitened: t_w = (Σ+λI)⁻¹(μ_w − μ). Stein's-lemma motivation. Handles multi-token intermediates (photosynthesis, blackmail, Tchaikovsky↔Beethoven swap flips Russian↔German). J-lens degrades sharply with token length; template flat. Pathologies: skips to answer (tuned-lens-like), final-layer next-word prediction only 67%, some spurious frequent words.
**Oracle lens:** reconstructor (phrase → whitened activation) + phrase dictionary (3.4M) + NOMP teacher + oracle model (SFT then RL for FVE). Explains ~31% whitened variance. Produces phrases like "blackmail him by revealing", "This would be equivalent to my own deletion" at delimiter tokens; continuation-like phrases at ordinary tokens.

---

## 8. Limitations the authors state (§9.1)

Single-token vocabulary; bag-of-concepts (no binding); inconsistent interpretability at some positions; workspace vs motor boundary is post-hoc; no predictive criterion for which tasks need J-space; early layers may be lens artifact; scaling/training dynamics unknown; no mechanism for entry into J-space.

---

## 9. Commentary critiques (what to carry into any project)

**Neel Nanda** (decomposes into scientific / methodological / pragmatic / philosophical claims; persuaded by first three to varying degrees, agnostic on fourth):
- First-principles: serial computation in one forward pass needs intermediate variables in the residual stream; consistent directions are an efficient "API"; alignment with unembedding is plausible but not canonical. Jacobian vs regression: infinitesimal perturbation avoids downstream nonlinear elaboration, so it reads current contents not correlates.
- Alternative for multihop: France/Paris linearly related ("Frenchness" + "is-capital"). Paper's earlier-layer timing argument answers this on Sonnet; on Qwen, answer swaps *dominated* (dataset too easy).
- Multilingual English-dominance could be token-norm/variance artifact of top-k over logits.
- Sampling-based ablations (eval awareness) confounded by output-vocab suppression.
- J-lens = variable interpretability, not algorithm interpretability. Useful for hypothesis generation, not validation; expect false positives; comparable to SAEs, cheaper.
- **Replication on Qwen 3.6 27B:** n=25 Pile prompts, 128 tokens, penultimate layer, skip first 4 tokens (high norm). Replicated: verbal report (weak positive), CKA (4–5 overlapping bands), directed modulation (moderate), multilingual + typo evals (probing and causal). Association weak (dataset single-answer). Multihop: answer swap dominated. Poetry and arithmetic failed (capability or experimenter error). Qwen3.5-397B-A17B: ~1 hour, n=4, 8×H200. Metrics: harmonic mean of rank; Δ prob of new correct answer. Baselines: Chinese token for intermediate, answer token, logit lens.
- **Interpretative meta-tokens** (with Camila Blank, Agam Bhatia): 什么意思, 是什么意思, 这句话, 是何含义 appear on ambiguous text (poetry newlines, puns, crossword clues, gibberish), mostly on punctuation; negative steering reduces pun/rhyme/wordplay recognition (50 rollouts × 2 prompts/category, LLM-judged; coefficient swept per prompt; ablation ineffective; single-position steering ineffective). Preliminary. Suggests the model represents *which subroutine to run*.

**Eleos (Butlin et al.):** Distinguish privileged set (well supported) / privileged stream (suggestive) / GWT workspace (modules, global broadcast not shown). Broadcast-head evidence is averages, could be fragments/partial fidelity. Capacity underestimated if W-space ⊋ J-space. Selection-by-Jacobian may explain broad influence tautologically. Moral status discussion; valence unresolved; BUT signal noted.

**Dehaene & Naccache:** C1 (global availability) met; C2 (self-monitoring) preliminary (damn/fail, BUT). Ignition partially shown after revisions. Capacity 25 likely inflated; really ~1–2 coherent ideas per layer. Proposed tests: local-global sequence paradigm; trace conditioning (preliminary: J-space ablation impairs long-gap first→last word completion, not adjacent); inclusion/exclusion (done, A.14); error monitoring/confidence in J-space; split-brain two-J-space idea. Differences: no recurrence, no body, no episodic memory, no vigilance system.

---

## 10. Open directions (aggregated)

1. Multi-token / phrase J-lens beyond template lens.
2. Mechanism of entry into the J-space (attention-like selection?).
3. Emergence during pretraining; scaling with model size; smaller models.
4. Trace-conditioning / delay-bridging test.
5. False-positive rate and reliability for auditing; automated scanning over all (layer, position).
6. Binding / relational structure among workspace contents.
7. Unified-stream evidence: shared entry mechanisms, higher-fidelity broadcast heads.
8. Error monitoring, confidence, feeling-of-knowing in J-space.
9. Does the "self" installed by post-training change entry dynamics?
10. Meta-tokens (algorithm selection) in English-tokenizer models via multi-token vectors.
