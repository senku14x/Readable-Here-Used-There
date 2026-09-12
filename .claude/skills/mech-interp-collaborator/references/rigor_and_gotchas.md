# Rigor Checklist, Instrument Validation, and Gotchas

Read before finalizing an experimental design, auditing results for write-up, or reviewing internals code. Sections: (1) good-science checklist, (2) the validation ladder for interpretations, (3) instrument-specific validation recipes, (4) leakage checks, (5) technical gotcha catalog.

## 1. Good-science checklist

- **No cherry-picking.** Any qualitative analysis must show randomly selected examples (appendix is fine) alongside the highlights. If only the best examples exist, say so and downgrade the claim.
- **Baselines that threaten.** A method getting "decent" results means nothing; it must beat the plausible alternative a practitioner would actually use (for steering: a system prompt; for a fancy detector: logistic regression on surface features or a mean-difference direction; for any SDL pipeline: PCA + a linear probe). Choose the baseline a hostile reviewer would choose.
- **Don't sandbag baselines.** Spend comparable tuning effort on baselines as on the method; check baselines reproduce their published numbers. A method that only wins against untuned baselines has shown nothing.
- **Ablate multi-part methods.** Remove each component and see what breaks. Cautionary tale: RMU-style unlearning was claimed to rest on a meaningful steering direction until ablations showed a random high-norm vector worked as well — the mechanism story was doing no work.
- **Informally pre-register.** Track which results were predicted before running vs. interpreted after seeing. Post-hoc analysis is hypothesis generation, not confirmation. Decision rules stated in advance are the cheap version of pre-registration.
- **Simplicity first.** Test the dumb hypothesis before the interesting one: "this component is important on *every* input", "the direction is token frequency / formality / length", "the finetune degraded the model generally". Each moving part in a fancy method is another thing that silently breaks.
- **Qualitative AND quantitative.** Summary statistics hide structure; anecdotes don't generalize. Understand via qualitative inspection, then validate quantitatively. A paper (or claim) doing only one is missing half.
- **Read your data.** Raw transcripts, raw activations, plotted distributions — before aggregating. Look for outliers, bimodality, subgroup structure, garbage examples. Dataset flaws drive more "results" than mechanisms do.
- **Don't reinvent the wheel.** Run a literature check (LLM-assisted search is cheap) before investing; know the standard baselines and gotchas of the subfield or no one will believe the work.
- **Statistics.** Multiple seeds where feasible; error bars or at least variance awareness; effect sizes over bare p-values; and remember that scanning many layers × features × prompts is massive multiple comparison — the best cell of a big grid is expected to look good by chance. Correct or replicate on held-out selections. For fuller treatment of sample sizes, inference traps, and multiple-comparison handling in this field, see Bogdan, "Statistical Suggestions for Mech Interp Research" (2025).
- **Convergent evidence.** Seek agreement between methods whose failure modes are meaningfully independent (e.g., a probe plus a behavioral prompting test), and discount agreement between correlated instruments (two probes fit on the same activations) accordingly.
- **Reproducibility.** Share code/data/configs where practical; note exact model revisions and library versions (results can change across either).
- **Excitement is evidence of bullshit.** The correct response to an exciting result is deeper skepticism and an immediate attempt to kill it, not scaling it.

## 2. The validation ladder for interpretations

An interpretation ("component/direction X does Y") earns strength by climbing:

1. **Predicts activations** on held-out data (does the story anticipate where/when X fires?).
2. **Predicts counterfactuals** — specific downstream effects of ablating/activating X, stated before intervening.
3. **Intervention with specificity** — the predicted effect occurs, matched-norm random controls don't produce it, unrelated capabilities are intact, and the effect is absent where the story predicts absence.
4. **Downstream utility** — the interpretation lets you do something (debug, detect, edit) on a non-cherry-picked task.
5. **Competitive downstream utility** — it beats tuned non-interpretability baselines on that task.

Most claimed interpretations sit at rung 0–1 while being narrated at rung 3+. Say which rung a claim is on.

## 3. Instrument validation recipes

Treat every measurement instrument as broken until it passes known-answer tests in the current context.

**Linear probes**
- Probes measure correlation in activations, not use by the model, and not causation. High accuracy is compatible with the concept being represented, a correlate being represented, or label leakage.
- Controls: shuffled-label probe (should hit chance — if not, leakage or overfitting); probes on random directions / random layers as floor; selectivity check against sibling concepts (a "deception" probe should not fire equally on "negative sentiment"); generalization to a differently-constructed dataset (different templates, topics, authors) — template-level generalization failure is the default outcome, so test it.
- Report base rates. AUROC hides class imbalance; with rare positives insist on AUPRC/precision-recall and compare against the trivial always-majority and surface-feature classifiers.
- Regularization and probe capacity matter: an expressive probe on high-dimensional activations will find *something*; prefer the simplest probe that works and validate on truly held-out structure.

**SAE latents / dictionary features**
- Auto-generated labels from max-activating examples are hypotheses, not facts. Plausible stories can be told about *arbitrary* directions — that's an interpretability illusion, demonstrated repeatedly. Annotator conclusions also shift with the dataset examples are drawn from.
- SAE latents are dataset-dependent (an SAE trained on pretraining text may lack chat-relevant latents), subject to feature splitting/absorption, and describe activation structure, not mechanisms.
- Validate a latent the same way as a probe: known positives, known negatives, selectivity, causal check if the claim is causal.

**LLM judges**
- Run positive and negative controls: texts where the correct judgment is known, in both directions. Measure agreement with a hand-labeled subset before trusting scale.
- Check prompt sensitivity (rephrase the rubric), order/position bias in pairwise comparisons, and sycophancy toward framing ("does this show X?" begets yes).
- Never let the same LLM generate and judge without a control for self-preference.

**Steering / activation addition**
- Sweep coefficients — behavior varies enormously with scale, and a single coefficient is a cherry-pick.
- Controls: matched-norm random direction; fluency/perplexity or unrelated-benchmark check for general damage; check the effect is absent on inputs where the story predicts absence.
- Score steered outputs with a validated judge (see above), on random samples.

**Patching / attribution**
- Attribution patching and gradient methods are first-order approximations; verify top candidates with real interventions.
- Beware backup/self-repair effects (ablating a component can be compensated downstream, hiding its role) and negative components — faithfulness metrics depend heavily on the intervention distribution chosen.
- The choice of corrupt/counterfactual prompt defines what the patch can show; state what is held constant and what varies.

## 4. Leakage and split hygiene

- Split at the level of the generating structure, not the row: prompts sharing a template, topic, entity, or author must not straddle train/test. Template-level leakage is the most common cause of inflated probe/classifier numbers in interp.
- Check the label isn't literally present in the input to the instrument (e.g., probing tokens that spell out the class; judging text that contains the rubric word).
- Dedupe near-duplicates before splitting. Verify the "held-out" model/dataset wasn't in any tuning loop, including hyperparameter selection by peeking.

## 5. Technical gotcha catalog

Tokenization and formatting
- Leading spaces change token identity (" cat" ≠ "cat"); multi-token words/entities mean "the token for X" often doesn't exist. Always print the actual token IDs/strings at the positions being read.
- Chat templates: each model family has its own; applying the wrong one (or none, or inconsistently between conditions) can *partially* degrade behavior — bad enough to corrupt results, mild enough to miss. Sanity check by reproducing an official eval number or comparing generations against the reference chat format.
- If the experimental manipulation correlates with template position (e.g., trigger text always adjacent to a role token), position-based and content-based explanations are confounded — test by moving the content within the template.
- Padding side matters (left-pad for decoder-only generation); attention masks must match. Batch-vs-single-example disagreement is usually padding/masking.

Positions and readout
- Token position 0 / BOS is an attention sink with anomalous, high-norm activations — exclude it from aggregate statistics and don't read "the meaning" off it.
- Activation norms grow along the sequence; any length- or position-correlated condition difference will show up in norms and probe accuracy for free. Control length/position or normalize deliberately.
- Off-by-one at readout: logits at position i predict token i+1. The "answer token" for teacher-forced scoring is the position *before* the answer.
- Teacher forcing vs. generation are different regimes (KV cache, sampling); an effect measured under one doesn't automatically transfer to the other.

Numerics and infrastructure
- bf16/fp16 introduce nondeterminism and noise floors; tiny patching/ablation effects can be below numerical noise — measure the noise floor (run the identity intervention twice).
- Hooks: remove/reset them between experiments; beware in-place tensor mutation propagating outside the intended scope.
- Libraries preprocess weights differently (folded LayerNorm, centered unembeddings in TransformerLens-style processing) — activations are not comparable across libraries or across processing flags; know which convention is on.
- Pin and record model revision and library versions; behavior shifts across both. Seed everything, and still expect GPU nondeterminism.
- Prefer dense models over MoE for interp work when there's a choice; MoE routing adds a layer of pain and variance.

Design-level
- Selecting the best layer/feature/head on the evaluation data is selection, not discovery — re-validate the selected object on fresh data.
- When comparing a finetuned model to its base, general capability drift is the default explanation for any behavioral difference until targeted-ness is shown.
