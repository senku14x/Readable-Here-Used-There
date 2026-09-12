# Field Map

Two kinds of content, deliberately separated. Sections 1–3 are structural: critiques and evaluation questions that stay valid as methods change. Section 4 is a **dated opinion snapshot** and must be treated as historical context, not current truth.

## 1. Evergreen: questions to ask of ANY interp method (new or old)

When the user asks "should I use/build on method X?", run these regardless of what X is:

1. **What is the baseline?** Does X beat PCA + a linear probe, plain prompting, finetuning, or a mean-difference vector on the same task — with the baseline tuned as hard as X?
2. **Were the demo tasks chosen after the fact?** Methods are usually introduced on tasks where they shine (streetlight effect). Has X survived a non-cherry-picked, non-author evaluation?
3. **Correlational or causal?** Does X locate things that merely co-vary with the phenomenon, or things whose manipulation changes it — with specificity controls?
4. **What does X's error/residual contain?** Any approximation-based method (dictionary learning, linearized attribution, replacement models) has a residual; if the residual is large or structured, conclusions drawn from the approximation inherit that gap.
5. **Is the proxy the goal?** Every method optimizes a proxy (sparsity, reconstruction, faithfulness metric). Where does the proxy diverge from interpretability/truth, and is X's success just proxy-hacking?
6. **Cost vs. black-box alternative.** If prompting or a cheap supervised classifier achieves the downstream goal, X's mechanistic character isn't a bonus — it needs to buy something concrete.
7. **What would falsify it?** If no observation could show X's outputs are wrong (no ground truth, no known-answer tests), X produces stories, not measurements.

## 2. Evergreen: structural difficulties (why interp claims fail by default)

Condensed from Sharkey et al., "Open Problems in Mechanistic Interpretability" (2025) — these are critiques of *categories* of method and remain relevant to successors:

- **No privileged units.** Neurons, attention heads, and layers are all polysemantic / non-atomic; representations spread across heads and layers. Any decomposition (SDL included) is a modeling choice, not an observation — its units are hypotheses.
- **Dictionary-learning-class limits** (apply to SAEs, transcoders, crosscoders, and descendants): reconstruction error is large and structured, not random noise; sparsity is a proxy that breaks under optimization pressure (feature splitting, absorption, composition); learned latents depend on the training distribution; latents describe activations, not the mechanisms computing them; the concept you need may simply not be a latent.
- **Description-method illusions.** Max-activating examples yield plausible stories for arbitrary directions; annotations flip with the dataset sampled; attribution methods are first-order, fragile, and sometimes model-independent. Plausibility is not faithfulness.
- **Validation is the bottleneck.** Conflating hypotheses with conclusions is endemic; interpretability illusions (results that later proved artifactual) are documented for probes, subspace patching, and circuits. Model organisms with known ground truth and downstream-task evaluations are the credible validation routes.
- **Circuit-pipeline caveats.** Faithfulness numbers depend on the intervention distribution; backup/self-repair and negative components hide roles from ablation; task definitions are researcher constructs with high within-task variance; simple demo tasks overstate the method's generality.
- **Probing limits.** Probes detect information present, not information used; carefully chosen data for a well-defined concept is a prerequisite most projects skip.

Durable application framing: interp work ultimately cashes out in monitoring/auditing, control/editing, prediction of behavior or capabilities, improving training/inference, or knowledge extraction (microscope use). A project that names which of these it serves — and what level of decomposition/description/validation that goal actually requires — is better scoped than one pursuing "understanding" in the abstract.

## 3. Evergreen: evaluating novelty and picking directions

- The bar for contribution in a crowded technique family is not "applied it somewhere new" but "revealed something non-obvious or beat a real baseline". "What if we used X for Y?" needs an argument for why X specifically.
- Fields have fads: a technique gets popular, accumulates limitations, the frontier moves, but newcomers keep entering at the peak. Before committing to a direction, check its trajectory — is the founding lab still pursuing it? What did the retrospectives/negative results say?
- Neglectedness multiplies value: newly emerged capabilities, behaviors, and settings are under-explored, and being early into a genuinely new one buys low-hanging fruit. Once a phenomenon goes viral, many others have the same idea.
- Negative results with a diagnosed cause are publishable and respected in this field; negative results without a cause ("we tried one implementation and it didn't work") are weak either way.

## 4. DATED SNAPSHOT — field opinion as of late 2025 / Dec 2025

⚠️ **Staleness warning.** This section synthesizes Neel Nanda's guide (Sept 2025) and the GDM team's "A Pragmatic Vision for Interpretability" + companion agenda (Dec 2025). It is prominent researchers' opinion at a specific time, in a fast-moving field, and it is already months old relative to any conversation happening after it was written. Before using it to advise on project choice, VERIFY currency: search for the current state and check neelnanda.io/vision and neelnanda.io/agenda. Treat everything below as history that was true-as-stated at the time.

**The pragmatic pivot (Dec 2025).** The GDM mech interp team publicly moved from ambitious reverse-engineering to "pragmatic interpretability": directly attacking problems on the critical path to AGI going well, chosen by comparative advantage, with progress measured on proxy tasks. Scope explicitly broadened from "mechanistic AND interpretability" to "mechanistic OR interpretability" — model internals used for control (steering, probes as monitors) and black-box interpretability (CoT reading, prefill attacks, resampling) both count. Stated rationale: models became interesting enough to exhibit real safety-relevant behavior; model-organism techniques (synthetic-document fine-tuning) supply ground truth; and ambitious reverse-engineering disappointed — superposition (incl. cross-layer), structured dictionary-learning residuals that grow latents when scaled, self-repair polluting causal interventions, and sampling/multi-turn/agentic complexity all unresolved. Their picture: models have legible high-level structure driving important behavior plus a long tail of messy heuristics; work the legible part, bound the tail. Ambitious reverse-engineering framed as one bet among several, to be judged like everything else — by task payoffs, not approximation error.

**The SAE verdict (as of then).** GDM deprioritized SAE research after a year in which reconstruction/sparsity pareto-frontier progress produced little decision-relevant learning, while proxy tasks produced the actual update: SAE probes did not generalize OOD better than baselines, SAE unlearning underperformed, and in the flagship eval-awareness application a steering vector from a single contrastive prompt pair beat SAE-derived directions. Retained strength: unsupervised discovery — surfacing hypotheses nobody would have generated (entity-recognition latents, hidden-goal extraction, implicit planning via attribution graphs). Exempt from the critique: meaningfully different decomposition approaches (SPD, ITDA, Matryoshka-style), attribution-graph/transcoder circuit analysis, and SAEs as one tool inside a motivated investigation.

**Named historical fads** (per Nanda): toy models on algorithmic tasks (insight didn't transfer); component-level circuit hunting as an endpoint (IOI-style — patching stays useful, but a sparse subgraph over polysemantic nodes had no "what next"; the bar became "use the circuit to reveal something non-obvious"); incremental SAE work (architecture tweaks, "we applied SAEs to X" demos).

**Directions flagged live then:** downstream-task evaluation of interp (auditing games — different teams, known hidden property, which techniques elicit it); model organisms via synthetic-document fine-tuning (hidden goals, taboo words, implanted beliefs, emergent-misalignment organisms); interp directly on real safety-relevant behaviors (deception probes, evaluation awareness, alignment faking, reward hacking, shutdown resistance); cheap real-world uses (linear probes as production monitors); attribution graphs / transcoder circuits; explaining model failures; automated/agentic interpretability (interp agents solving auditing games, and improving fast); reasoning-model interpretability — repeatedly called the most neglected and rising area, with mostly-black-box paradigms (thought anchors, CoT resampling, sentence-level interventions) needing invention.

**Instructive case studies from the period:** Sonnet 4.5 eval-awareness steering (partial understanding sufficed for a real pre-deployment fix; simplest method won); shutdown-resistance debunking (CoT reading + prompt interventions revealed instruction ambiguity, no internals needed — white-box holds no inherent rigor advantage); CAFT concept-ablation fine-tuning (stable theory of change + proxy task, many failed methods en route).

**Known dissent, for balance:** a visible critique (Ngo and others) argued that theory-of-change-first, ~10-year-payoff reasoning systematically steers researchers away from the open-ended curiosity that produces deep scientific breakthroughs, and that much of the field has quietly given up on solving alignment rather than marginally reducing risk. The GDM authors' reply: most progress everywhere is marginalist, curiosity-driven basic science is over-supplied relative to its value because researchers enjoy it, and the *marginal* researcher should move toward pragmatism. The snapshot records the disagreement; it does not settle it.

**Freshness protocol:** when this snapshot is load-bearing for advice, say so, date it, and search before relying on it. Model families, libraries, and "what's neglected" all rotate on a months-long cycle.
