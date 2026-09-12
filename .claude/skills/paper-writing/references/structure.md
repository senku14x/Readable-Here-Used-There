# Structure: Section Anatomy, Claims, and Evidence

Macro-level guidance from Neel Nanda and Sebastian Farquhar. Read the relevant section when outlining, drafting, or reviewing.

## Contents

1. Claims and evidence (the foundation)
2. Abstract
3. Introduction
4. Figure 1 and figures generally
5. Background
6. Methods
7. Results
8. Related work
9. Discussion and limitations
10. Conclusion and appendices
11. Red-team checklist for reviewing a draft

---

## 1. Claims and evidence

The paper's contribution is 1-3 specific, concrete claims. Vague contributions ("we study X") fail; claims are falsifiable statements like "method X beats the alternatives on task Y under metric Z" or "behavior A is largely explained by mechanism B". Multiple claims should fit one cohesive theme — a grab-bag of unconnected findings is harder to understand, praise, and share.

**Claim strength taxonomy** — pick deliberately, and make sure the evidence matches:

- Existence proof: "at least one case where X happens" — one trustworthy example suffices.
- Systematic claim: "X happens across a wide range of settings" — needs breadth: multiple models, datasets, seeds.
- Hedged claim: "suggestive/tentative/compelling evidence that X" — calibrate the adverb honestly.
- Narrow claim: "X is best specifically under conditions V and W for objective Y".
- Guarantee: "X always holds" — essentially never supportable in deep learning.

**What makes evidence good:**

- **It distinguishes hypotheses.** A good experiment produces different results depending on which hypothesis is true. One decisive experiment beats five that are consistent with everything.
- **Quality over quantity, but diversity is robustness.** Prioritize one hard-to-deny experiment; then prefer qualitatively different lines of evidence pointing at the same conclusion over near-duplicates of one methodology.
- **Strong baselines, honestly tuned.** Showing a method gets "decent" results supports only "X works at all", not "X is worth using". Compare against the strongest plausible alternative, and put real effort into tuning it — the temptation is to polish the shiny new method and neglect the boring baseline.
- **Ablations.** A method with changes A, B, C evaluated only as all-or-nothing tells the reader nothing about which change matters. Remove one component at a time.
- **Statistical rigor.** Report sample sizes and variance. For exploratory work, treat p-values between .01 and .05 as unreliable (findings in that band replicate poorly); aim for p < .001 or effect sizes that make significance testing moot.
- **Disclose cherry-picking.** Qualitative examples are valuable, but say how they were selected and show randomly sampled ones alongside the highlights. Exception: an existence-proof claim legitimately rests on one example.
- **Track pre-hoc versus post-hoc.** Predictions made before seeing results are stronger evidence than interpretations fitted afterward. Say which is which.
- **Reproducibility.** Enough methodological detail (main text plus appendix) that a skeptic could re-implement. Released code with a working README multiplies the paper's usefulness.

**Before writing:** verify the key experiments are actually correct. Re-run or re-implement the critical ones through an independent path where feasible. Many published papers are wrong; the time to catch it is now.

**Novelty** means the paper expands knowledge — a reader should assign different probabilities to propositions they care about after reading it. Rigorous replications and negative results qualify, whatever reviewers think. Be explicit in the intro and related work about what is and is not novel: the same result reads as arrogant or as a modest solid contribution purely depending on how its relation to prior work is framed.

---

## 2. Abstract

The abstract is the whole paper for most readers. It must work for a cold-start reader who does not yet know what subfield, problem, or genre of paper this is.

Formula (roughly one sentence each; merge or split as needed):

1. **Orient**: an uncontroversially true statement placing the paper in its subfield — or, alternatively, open directly with the achievement ("We show/introduce/prove...").
2. **Gap**: the problem, unknown, or need the paper addresses — this carries the motivation.
3. **Contribution**: the central claim and why it is exciting. Losing nuance here is acceptable.
4. **Approach/clarification** (optional): what was done, with enough keyword specificity that an expert can guess the shape of the work.
5. **Evidence**: the key experiments and results, ideally with one concrete number — the most striking honest metric.
6. **Impact**: 1-2 closing sentences on why it matters, and the standard of evidence ("a preliminary step toward...", "establishes that practitioners should...").

Prefer one idea per sentence. Two short sentences beat one long one; question any medium-long pair. Minimal jargon — only what is standard in the field and helps orient.

## 3. Introduction

An extended abstract: a self-contained summary of the paper. Repetition with the abstract is fine — complex ideas need restating in varied forms. Target about one page; more than 1.5 pages means cutting.

Paragraph structure:

1. **Context**: the topic, the motivating question, why it matters. Cite liberally to establish that the problem is real and people have tried. Skip the "LLMs are a big deal" boilerplate opener — no reader needs it, and experts skip the paragraph.
2. **Technical background**: what is known, what standard techniques the paper builds on, and why existing work is inadequate. After this paragraph an expert should know how this differs from the nearest prior work.
3. **Contribution**: the main claim, precisely, with key nuance.
4. **The case**: the most critical evidence, and what flavor of evidence the reader should and should not expect. The reader should leave knowing how seriously to take the claims.
5. (Optional) additional claim + case paragraphs.
6. **Impact**: the takeaway — who should act differently and how.
7. **Contributions list**: 2-4 bullets, each a concise claim, at most one line each (two in two-column format). A reader should be able to judge the paper from these bullets alone.

Never misrepresent prior work to inflate the contribution. It poisons the field, angers exactly the reviewers who know the area, and papers good enough to publish never needed it.

## 4. Figure 1 and figures generally

Many readers skip the text and go straight to figure 1. It should communicate the single most important thing — an explanatory diagram of the key idea or a combined panel of the key results — and would be the lead image of the announcement thread. Two-column format: top right of page 1, across from the abstract. One-column: top of page 2.

For every figure, ask: what exactly should the reader take away, and which part of the plot shows it? Design the visualization around that answer rather than dumping numbers into default plotting settings. Emphasize the line that matters (dark and saturated against light, low-opacity alternatives). Annotate directly on the plot where helpful.

Captions carry real weight: what the figure shows, how to interpret it, and the key technical context. Aim for figure-plus-caption to be understandable standalone — skimmers read exactly that.

(Typography-level rules — font sizes, colormaps, vector formats — are in prose-rules.md.)

## 5. Background

Include only material that passes all three tests: essential to make the paper make sense, not novel to this paper, and plausibly unfamiliar to many readers. It is not a related-work section and not a boilerplate formalism dump (nobody needs the RL formalism restated; put it in an appendix and reference it).

Be brief — think information momentum. The reader should be rushing toward the contribution, not bogged down before reaching it. Definitions of new terms introduced by this paper go in a clearly separate section, never mixed into background. A glossary appendix is a cheap gift to readers when space is tight.

## 6. Methods

Self-sufficiency test: a reader who understands the problem, knows the background, and trusts the experiments should be able to read this section alone and know what was done and why.

Present the final method cleanly. When a design involved choosing among alternatives (three candidate distance metrics, say), frame the method as requiring the component, state the choice, and push the empirical comparison to an appendix. The main text tells one clean story; the appendix holds the archaeology.

Pacing rule: if methods start after page 3, restructure. Rarely correct after page 2.

## 7. Results

Open the results section with a signpost: the main insight the experiments establish. Then one subsection per experiment (or per claim, when several experiments serve one claim), each covering:

1. What claim this experiment supports and how it ties to the paper's contribution.
2. The experimental setting — enough for an expert to roughly reimplement, with a pointer to an appendix holding exhaustive detail.
3. The result, walked through at the level of the actual figure: which lines, which points, which gap between bars demonstrates the claim. Not just the conclusion the figure "shows".

Triple-check the text against the plots. Reviewers regularly catch papers whose prose misdescribes their own graphs, and it destroys trust in everything else.

If experiments share a methodology, a Methods → Results split works. If each claim has its own boutique evidence, give each claim a section containing its method and results together — readers forget a method by the time they reach its results three sections later.

## 8. Related work

Purpose: communicate the diff between this paper and the field, prove awareness of the key work, and assign credit. Write it methodologically, grouping papers by approach and stating why this work differs ("prior work assumes A [x, y, z]; we instead assume B, which fits our setting because..."). Paper-by-paper summaries ("Smith et al. did X. Jones et al. did Y.") compress badly and communicate nothing.

Placement: fine as the penultimate section, unless the paper's motivation is inseparable from the literature (plugging a known gap, correcting a known flaw), in which case put it early. When a nearby paper looks similar, address it head-on: what is different, or if little is, say "parallel work" or explain politely what flaw this work fixes. Critique methods, never authors.

## 9. Discussion and limitations

Stating limitations honestly is not optional politeness; it is what lets readers calibrate what they learned, and the author knows failure modes the reader cannot see. Papers that acknowledge limitations up front read as stronger to the researchers whose opinion matters. Also fine here: broader implications, future work (best framed as limitations of the present work), and reflections. Consider a tacit-knowledge appendix or companion post: what was hard, what kept breaking, intuitions that cannot be fully defended, advice for replicators — often the most valuable part of a project and usually discarded.

## 10. Conclusion and appendices

A conclusion is optional; a couple of sentences for the readers who skip to the end, or nothing.

Appendices: think of the paper as much longer than the page limit, with the main body as the aggressively prioritized highlights reel. Everything else — full technical detail, secondary experiments, glossaries — goes to appendices, held to a lower polish standard. The scarce resource being managed is reader attention.

## 11. Red-team checklist for reviewing a draft

Work top-down; report the highest-level failure first.

1. **Narrative**: Can you state the paper's 1-3 claims in one sentence each after reading the abstract and intro? If not, that is the finding.
2. **Claim-evidence fit**: For each claim, does the evidence actually support it at the strength stated? Could the evidence be true and the claim false? What alternative explanation is unaddressed?
3. **Baselines and ablations**: Is anything shown to be "good" without comparison to a strong, honestly-tuned alternative? Multi-component methods without ablations?
4. **Cherry-picking and post-hoc fitting**: Are qualitative examples' selection process disclosed? Are post-hoc interpretations presented as predictions?
5. **Novelty framing**: Is it clear what is new versus inherited? Is prior work represented fairly?
6. **Reader drop-off**: Do the title, abstract, and figure 1 alone convey the contribution? Does methods start by page 3?
7. **Limitations**: Present, specific, and honest — or a token paragraph?
8. **Text-figure agreement**: Does the prose accurately describe the plots?
9. Only then: prose-rules.md as a line-edit audit.
