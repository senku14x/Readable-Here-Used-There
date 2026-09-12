# Writing Up: Distillation

Distilled from Neel Nanda's "Highly Opinionated Advice on How to Write ML Papers" and the distillation-stage guidance, plus Ethan Perez's "Easy Paper Writing Tips" (for the line-editing pass). Applies to papers, workshop submissions, arXiv preprints, and high-effort blog posts alike. The collaborator's job in write-up mode: protect the claim–evidence correspondence while making the narrative as clear and compelling as the evidence honestly allows.

## The narrative is the paper

- Readers retain a few sentences. Distill the work into **1–3 concrete claims** (the contribution), the **evidence** for each, and the **motivation** for caring — then build everything around that spine.
- Write to inform, not persuade. "Persuasive" means the evidence is actually strong, not that the prose hides weaknesses. The readers worth impressing are the experienced ones, who see through inflation — overclaiming is a bad strategy even selfishly.
- The narrative must be chosen for truth, not for looking good. If the honest version is "method X helps in regime A and not B", that is the narrative. Messier-than-hoped findings mean revisiting understanding, not massaging the story.

## Compress, then iteratively expand

Work in this order, getting feedback at the earliest stages where it's cheapest:
1. The 1–3 claims (lightning-talk version).
2. Abstract / TL;DR — sentence by sentence: context, gap, what we did, key result (with a number), why it matters. Expect to rewrite it many times.
3. Bullet-point outline of the full document — points, evidence, ordering. **Best single point for collaborator/mentor feedback.**
4. Figures — often the most-consumed content after the abstract; each must stand alone with its caption. Figure 1 should carry the core claim.
5. Introduction — the abstract expanded with context and contributions; most of the reading time lands here.
6. Body, discussion, appendices.

Time-per-word should track readership: abstract ≫ intro ≫ figures ≫ body. Start distillation well before deadlines — writing exposes missing experiments and confusions; people routinely report not understanding their own project until they wrote it up.

## The claim–evidence audit (do this on every draft)

For each sentence making an empirical claim:
- Which rung of the claim ladder is it phrased at, and which rung does the cited evidence support? Fix every mismatch — especially pattern-narrated-as-validated and correlation-narrated-as-mechanism.
- Is the qualifying caveat adjacent to the claim, or exiled to a limitations section three pages away? Move it adjacent.
- Was this result predicted or post-hoc? Post-hoc findings should be framed as such ("exploratory analysis suggested…").
- What varied (models, seeds, prompts, datasets) and is the claim's scope phrased to match?

## Honesty machinery that builds credibility

- **Limitations**: a substantive limitations discussion with nuanced partial rebuttals reads as competence; an unacknowledged limitation the reader spots reads as either ignorance or concealment, and costs far more than admitting it would have.
- **Random examples**: any qualitative analysis ships with randomly sampled examples (appendix), plus failure cases. This is the anti-cherry-picking proof.
- **Negative results**: well-analyzed negatives with a diagnosed cause are respected contributions in this field; frame them as "what this rules out and why", not as apology.
- **Reproducibility**: code, data, exact model revisions, configs; a README that runs on a fresh machine if time allows.
- **Re-implement before you publish**: key experiments that were LLM-vibe-coded during exploration get re-implemented or line-audited by hand before the numbers go in a paper.

## The line-editing pass (Perez)

Run this only after the narrative, claims, and structure are settled — polishing sentences earlier wastes effort on prose that will be cut. These are cheap edits with outsized clarity payoff:

**Sentence mechanics.** Put the verb early and make the thing the sentence is about the grammatical subject of the main clause. One idea per sentence: length is fine when the words are simple, but a long sentence dense with content should become two. Name the actor ("We find…", "The probe recovers…") — passive voice hides who did what, which matters in a field where "was observed" can conceal whose selection effects produced the observation. Bare pronouns (this, it, these) tax the reader; when one is unavoidable, attach a noun ("this ablation", "that intervention"). Prefer short, common words; unfold stacked possessives ("the SAE's latents' labels" → "the labels of the SAE latents"); avoid echoing similar-sounding words in one sentence; vary sentence openings so a paragraph doesn't march along on "We… We… We…".

**Delete on sight.** Throat-clearing and filler: "actually", "note that", "observe that", "to our knowledge", "try to", intensifiers ("very", "really", "extremely"), and most connectives. Scare quotes — they smuggle in an imprecise word the author already suspects is dodgy; find the precise word instead. Contractions, in formal venues. "Want" and "hope" — state what was done or found.

**Comparatives need referents.** "Better", "faster", "improves" mean nothing without both comparands named — and implicit comparatives are exactly how sandbagged or missing baselines hide in prose. Force every comparative to say compared-to-what.

**Hedging vs. calibration — reconcile, don't conflate.** Perez's rule is to drop hedge words ("may", "can") almost always. The evidence ladder still governs: the claim–evidence audit decides how strong the claim is *allowed* to be, and the sentence then states exactly that strength, plainly. "May improve robustness" as decorative mush is banned; "improves robustness on X under conditions Y" is calibrated *and* direct. Reflexive hedging and reflexive confidence are the same failure — language strength not chosen to match the evidence.

**Paragraph and page shape.** First and last sentences of a paragraph carry the weight; middles elaborate. Every sentence must add information — ask of each word "necessary? sayable more simply?" and of each sentence "is this actually true?". Kill widow lines (a lone word on a paragraph's final line) and excess white space in figures, captions, and headers; the page limit is a content budget.

**Production checklist.** An eye-catching Figure 1 on the first page — many readers see only that page and decide there. Figure fonts at least body-text size; colorblind-safe, perceptually uniform colormaps (viridis-style). Define uncommon terminology at first use. Run an external grammar/typo checker before submission; the editor's built-in check misses things.

**Time allocation.** Malik's rule, paraphrased: budget roughly equal writing time to each of the title, the abstract, the introduction, and everything else combined — reading time concentrates in exactly that order. The modern fifth part: the public announcement (thread / TL;DR) deserves the same per-word care, since for many readers it *is* the paper.

## Common mistakes to intercept

- **The reader has no context.** The author has weeks of immersion; the reader has none. Whatever feels "too obvious to state" is the correct level of explicitness. Motivation must be spelled out — the reader will not infer why the work matters.
- Writing treated as an afterthought and started at the deadline.
- Publishability warping the work: choosing questions or evidence forms for reviewers rather than truth. (Peer review is noisy; optimize for the informed reader.)
- Verbosity and fake sophistication. Simple writing about careful work beats complex writing about anything.
- Related work as a laundry list instead of positioning: state what the closest works did and precisely what is different/new here.

## Venue ladder

Blog post → arXiv → workshop paper → conference paper is a ladder of formality, not of worth; a strong blog post is most of an arXiv paper, and people systematically overestimate the bar for arXiv/workshops. Public output is the field's main credential; the format matters less than clear claims and honest evidence.
