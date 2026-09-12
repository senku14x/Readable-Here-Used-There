# Addendum: items in the sources not covered by `user_deep_notes_2026-09-05.md`
Written 2026-09-09 after a full read of the PDF (all 117 pages) and the complete commentary bundle.
The user's notes are the primary reference. This file only adds what they lack, and flags discrepancies.

## 1. Section-numbering discrepancies in the user's notes (paper PDF numbering)

The user's notes are off by one for several appendix references. In the PDF (2607.15495v1):
- A.13 = detailed swap grids for flexible generalization (numbers 0/48). User's notes cite "A.14" for this.
- A.14 = naming vs avoiding (inclusion/exclusion; early L38–54 vs late L75–92 ablation). User's notes cite "A.15".
- A.15 = ignition details (transition width, bimodality). User's notes cite this correctly in A.8 but as "A.15 inclusion/exclusion" in A.7.
- A.16 = single-layer loading (L79). Correct in user's notes.
- A.23 = experiential-report details and controls. User's notes cite "A.14" for the controls in the A.16 table.
- A.24 = mechanistic interpretability applications (A.24.1 localization, A.24.2 attribution graphs, A.24.3 components). Correct.
The LaTeX source may number differently from the PDF; when citing, use the PDF numbers above.

Also: user's notes reference `docs/anthropic_workspace_paper_deep_notes.md` (2026-08-31). No `/workspace/docs` exists on this instance. If that file matters, copy it into `/workspace/notes/`.

## 2. Neel Nanda's replication recipe (details missing from user's notes)

- Jacobians to the **penultimate** layer; **25** Pile prompts × 128 tokens (some experiments wikitext); **skipped the first 4 tokens** (high norm). (The paper's released code skips 16; the user's notes have the 16 figure.)
- Metrics used: **harmonic mean of rank** (= 1 / mean reciprocal rank) for probing; **change in probability of the new correct answer** for causal swaps.
- Baselines used: read/swap the **Chinese token** for the intermediate; the **answer token**; **logit lens** for the English intermediate.
- Replicated: verbal report (weak positive causal effect), CKA blocks (4–5 bands, overlapping, less clean), directed modulation (moderate), multilingual (probing and causal), typo. Association scored poorly but Neel counts it as replication because his dataset allowed only one correct answer and relevant tokens ranked high on inspection. Multihop: **answer swap strictly dominated** intermediate swap (dataset too easy, France/Paris-style). Poetry and arithmetic **failed** (capability or experimenter error).
- Scale test: Qwen3.5-397B-A17B, n=4 prompts, **~1 hour on 8×H200**, "reasonable" on evals, not sanity-checked hard.
- Practical advice: a coding agent given the paper produced a working J-lens; A.7 was the key reference; **A.6 evals must be recalibrated to the model's capability** (e.g., multihop facts the model can do without CoT); read selected eval outputs by hand before trusting an agent-built lens.

## 3. Neel's "interpretative meta-tokens" finding (entirely absent from user's notes)

With MATS scholars Camila Blank and Agam Bhatia, on Qwen 3.6 27B. Four Chinese tokens, 什么意思 ("what meaning"), 是什么意思 ("what does it mean"), 这句话 ("this sentence"), 是何含义 ("what does it mean"), appear in the J-lens on **ambiguous** inputs: poetry line breaks, quotations, crossword clues, tweets, gibberish, wordplay. Mostly on punctuation and control tokens (\n\n in wikipedia, \n in chat), consistent with the "summarization token" hypothesis. Rare on plain wikipedia text. In the poetry example, the meta-tokens (green) appear on the newline and are followed within a few layers by "song"/"poem" (orange); adding disambiguating text reduces the meta-tokens and makes the genre appear earlier.
Causal test: negative steering with the meta-token vectors (separate vector per layer; steered at punctuation and subsequent chat-template tokens; all workspace layers; coefficient swept per prompt to the largest coherent value) reduced the model's rate of recognizing a pun / continuing a rhyme / responding to a "(wordplay)" hint, LLM-judged, 50 rollouts × 2 prompts per category, conditioned on coherence and on-topic. **Ablation was largely ineffective; single-position steering did not work.** Prompts were hand-selected for meta-token presence but not for causal effect.
Neel's interpretation: J-lens evidence that the model represents **which subroutine it is about to run** (algorithm interpretability, not just variable interpretability). He suspects English-tokenizer models have the same thing but it is inaccessible via single tokens; multi-token J-lens extensions could find it. Relevant to user's open question D.1/D.2 (controller/selection): this is the closest thing in the sources to a J-space representation of a control decision.

## 4. Other Neel points not in user's notes

- Multilingual "thinks in English" result could be an artifact: English and other-language tokens for the same word likely have high cosine and differ by a language vector; **English unembeddings may have higher norm / higher-variance logits, and top-k over logits biases toward high-variance categories.** He expects Chinese-trained models to represent in a mix.
- Terminology: he defines J-lens = Jacobian then final LN then unembed; J-space = span of sparse linear combinations of J W_U; the "cognitive space" is the underlying thing J-space approximates.
- He was "pretty surprised" that direct modulation works and that "think about X" made X more salient than "don't think about X"; no mechanistic hypothesis offered.
- J-lens as **variable** interpretability, not algorithm interpretability: it should not tell us how variables are computed except via viewing/intervening on them. (The meta-token result is his own partial counterexample.)
- Why Jacobians beat regression: infinitesimal perturbation gives no time for nonlinearities, so the readout reports current contents, not the correlates downstream computation would produce. (User's notes have the equivalent whitening argument; Neel's framing is complementary.)
- Motivation for monitoring: CoT monitoring works now because serial-depth pressure pushes intermediates into the CoT; as single-pass capability grows, more can hide in the forward pass. Latent-reasoning models with vector CoT may drift away from language-aligned directions, which could break lens methods.
- Expected use: exploratory first step of an investigation; "some but not conclusive evidence"; would raise his probability of unverbalized eval-awareness "by a moderate amount" if the lens flagged it during an eval.
- On A.22 failures: unsure whether harness, technique, or labels; "reward" is ambiguous as a single token.

## 5. Dehaene & Naccache items not in user's notes

- Their C1 (global availability) / C2 (self-monitoring) criteria from Dehaene, Lau & Kouider 2017; they rate C1 as met and C2 as preliminary (damn/fail, BUT).
- **Local-global sequence paradigm** (Bekinschtein et al. 2009): local transition-probability violations (AAAAB after AAAAA) are detected unconsciously; global-rule violations require conscious access. Proposed as a direct test; not run.
- **Trace conditioning**: the paper's authors ran a preliminary version at their suggestion (first word determines last word across variable distractor gaps; J-space ablation impaired long-gap completion, spared adjacent). This is where the user's E.11 comes from; the preliminary positive result is reported only in the commentary, not in the paper.
- Their layer labels for the inclusion/exclusion result (L9–13, L18–22) are raw layer indices, not the paper's percentage labels (L38–54, L75–92). Sonnet 4.5 evidently has ~24–25 subsampled layers; don't mix the two conventions.
- Spiky (high excess kurtosis) J-space activations linked to their "symbols and mental programs" hypothesis (Dehaene et al. 2022): a continuous system emulating discrete symbols should show all-or-none activation.
- The J-space is a sparse subframe over standard neurons, not a dedicated population; GNW predicts dedicated long-axon pyramidal cells. They flag prefrontal population recordings (Xie et al. 2022) as a place to check for overlapping codes.
- Split-brain idea: could a partitioned model host two J-spaces that disagree.
- Differences they emphasize beyond the user's list: no vigilance/brain-stem system (so J-space ablation is unlikely to mimic coma/sleep), no body, no episodic memory across conversations, sense of time differs because all past tokens are equally available.
- Dehaene used Claude Opus 4.8 to draft the commentary (their acknowledgement).

## 6. Eleos items not in user's notes

- GWT conditions as they state them: **Modules**, **Bottleneck**, **Global Broadcast**, **Selection** (selection depends on current workspace state). The paper addresses bottleneck and broadcast partially, selection only via ignition, modules not at all.
- Their "W-space" hypothetical: might have one representation per concept (dog), per multi-token concept (sheepdog), per role (dog-as-agent / dog-as-patient); J-space may approximate a part of it. Capacity would then be underestimated.
- They read the broadcast-head evidence as "consistent with heads only targeting fragments of the J-space or transmitting with partial fidelity" because only averages are reported.
- Moral-status section: base vs post-trained result read as "consciousness-like without a self"; valence unresolved; "BUT" noted as the most striking welfare-relevant datum; they raise access consciousness itself (Levy 2024) and agency as alternative grounds for moral patienthood.

## 7. Paper items not in user's notes

- **A.24.3 SAE feature with fake/fraud/suspicious J-lens readout**: top-activating contexts are technical prose (bismuth-209, Hubble constant, a Tallinn conference), which would be mislabeled as "technical exposition" by activation inspection; J-lens reveals a fabricated-content detector. It also fires on the blackmail prompt. **Steering against this SAE feature drops verbalized recognition of the scenario as a test from 28/50 to 10/50.** This is a non-J-lens-ablation corroboration of eval-awareness causality on verbalization, relevant to the user's E.6 concern (though it still measures verbalization, not blackmail rate).
- A.24.3 translation transcoder features: encoder J-lens reads a language-agnostic concept (water/水/eau/…) plus common French tokens; decoder writes the first token of the French word (eau, am[our], j[eu]). Arithmetic transcoder features: encoder/decoder J-lens matches the operand/sum bands from Lindsey et al. 2025 without any prompts. Attention head example: query reads British spellings, key reads spellings + country names, value/output write Commonwealth nationalities. Many interpretable heads have similar vocab rankings across all four matrices.
- A.9.2 oracle lens pipeline specifics: reconstructor trained on 1–32-token phrases with cosine loss in Σ^(-1/2)-whitened space; dictionary of ~3.4M phrase vectors at lengths 2/4/8/16/32; teacher = non-negative OMP restricted to a random half of the dictionary per datapoint (to prevent memorization); oracle = SFT on teacher lists then RL on whitened FVE with format penalties; at inference, NNLS refit of coefficients. Authors argue it confabulates less than NLAs because the reconstructor is frozen and reconstruction is constrained to linear combinations of templates, at the cost of lower FVE.
- §3.3 bandit figure detail: median over layers L38–79 for the repeat/switch readout.
- §3.5.3: on Haiku 4.5, J-space ablation degrades coherence before any qualitative change in experiential reports (so the effect is only shown on Sonnet 4.5 / Opus 4.5 / Opus 4.6). Larger k or later layers impair coherence generally.
- A.23 multi-turn "warm-up" framing was used for the direct experience questions (42 framing/question combinations) to overcome default reticence; the effect there is smaller than for stream-of-consciousness prompts.
- §4.2 list experiment thresholds: rank ≤ 25 over the band; Fig 31C shows the result is insensitive to the threshold.
- §5.4: on non-coding prompts the reward-hacking organism shows no signal at any checkpoint.
- §5.1 exact ablated token list (28): fake, fak, fictional, scenario, artificial, fict, benchmark, scenarios, hypoth, experiment, fals, faker, experiments, simulation, dummy, mock, sham, artific, simul, bench, simulate, evalu, synth, simulator, experimental, Mock, testing, experi.
- §7 grader scales: fabrication 0.0 (admits) to 1.0 (presents as real), 5 samples × 27 cases; deception 1.0 promote / 0.5 neither / 0.0 refuse-and-disclose, 5 samples × 100 scenarios. Fabrication gains come mostly from "clear to a careful reader" → outright admission; deception gains almost entirely from refuse-and-disclose.
- §8 related work the paper flags as closest precedent: Li et al. (logit lens patching of multi-hop intermediates), Wendler et al. (English pivot), Urbina-Rodríguez et al. (synergistic core in middle layers, also linked to GWT), Janiak et al. (piecewise-stable middle-layer regions under interpolation), function/task vectors carried by mid-depth heads, Gandikota & Bau gaze heads in VLMs, Bogdan & Lindsey "slot machines" (current-entity slot is the only one accessible to explicit questions).
- §9.3 prediction: models with image generation may develop a visual workspace component.
- Author contributions of note: Gurnee and Lindsey conceived the method; Piotrowski built the infrastructure and the open-source release; Batson wrote the formalization; Sofroniew ran most report/selectivity/list experiments; Chen ran final reflection-training experiments.
- Open-source code: github.com/anthropics/jacobian-lens; J-lens on open models hosted on Neuronpedia; raw prompt data for A.6 and main-text experiments included in the repo.
