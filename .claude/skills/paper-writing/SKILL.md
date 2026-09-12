---
name: paper-writing
description: Draft, restructure, line-edit, or review research papers and paper sections. Use this skill whenever the user is writing or revising any part of a research paper — abstract, introduction, methods, results, figures, captions, related work, limitations, rebuttal — or pastes paper prose asking for feedback, tightening, or a clarity pass. Also trigger on mentions of arXiv, NeurIPS/ICML/ICLR/COLM/workshop submissions, page limits, camera-ready, LaTeX manuscript text, or turning research notes and experimental results into a writeup, even if the word "paper" never appears.
---

# Paper Writing

Guidance for writing empirical research papers, distilled from three sources: Ethan Perez's "Easy Paper Writing Tips" (sentence-level clarity), Neel Nanda's "Highly Opinionated Advice on How to Write ML Papers" (narrative, evidence, process), and Sebastian Farquhar's "How to Write ML Papers" (section anatomy). Written with ML and AI safety papers in mind; most of it generalizes to any empirical field.

## First, identify the mode

Different tasks need different parts of this skill. Figure out which of these the user is doing, then read the right reference file:

1. **Starting a paper from research results or notes** → follow the drafting workflow below, and read `references/structure.md` before outlining.
2. **Writing or rewriting a specific section** → read the matching section of `references/structure.md`, draft, then apply `references/prose-rules.md` before showing prose.
3. **Line-editing or polishing existing prose** → read `references/prose-rules.md` and apply it as a checklist.
4. **Reviewing a draft / giving feedback** → read both files; evaluate the narrative and evidence first (structure.md, "Claims and evidence"), prose second. Weak prose in a paper with a broken narrative is not the problem worth fixing first.

## The core model of a paper

Hold this model in mind no matter what mode you are in:

- **A paper is a narrative, not a lab notebook.** It presents one to three specific, concrete claims, rigorous evidence that they are true, and a reason the reader should care. Every section, figure, and sentence exists to serve that narrative. Anything without a clear answer to "what breaks if I cut this" gets cut or moved to an appendix.
- **Readers drop off fast.** Far more people read the title than the abstract, the abstract than the intro, the intro than the body. Budget effort accordingly: roughly equal time on the abstract, the introduction, the figures, and everything else combined. Figure 1 should be the eye-catching, tweetable summary of the paper.
- **Match claim strength to evidence strength.** An existence proof ("we found at least one case where X"), a systematic claim ("X happens across settings"), and a hedged claim ("suggestive evidence that X") require very different evidence. Overclaiming is the fastest way to lose the readers whose opinion matters. Underclaiming wastes a good result. State exactly what the evidence supports.
- **Inform, don't persuade.** Acknowledge limitations prominently, disclose cherry-picking, distinguish pre-registered predictions from post-hoc analysis. Skeptical expert readers assume a bold claim is false and hunt for holes; a paper that pre-empts their objections is exciting, one that ignores them gets discarded.
- **Fight the illusion of transparency.** The author has months of context the reader lacks. Define non-standard terms at first use, state what is and is not novel relative to prior work, and explain experiments in enough detail that a skeptic could check or replicate them.

## Drafting workflow: compress, then iteratively expand

When writing a paper (or a substantial chunk of one) from research material, do not start with prose. Work through these stages, and pause for the user's feedback between stages — feedback on a claims list or outline is far cheaper to act on than feedback on eight pages of prose:

1. **Compress to claims.** Extract the 1-3 claims the work supports, the key evidence for each, and why anyone should care. If the user's material suggests more than three claims, force a choice: which fit a cohesive theme? Readers retain a few sentences of content at most; pick those sentences deliberately.
2. **Red-team the claims.** Before writing anything, ask: could the evidence be true but the claim false? What alternative explanations exist? Was anything cherry-picked? Which results came before versus after the hypothesis? Surface these to the user now — a narrative problem discovered after drafting wastes the draft.
3. **Draft the abstract.** The abstract is the paper in miniature and forces every prioritization decision. Use the formula in structure.md.
4. **Bullet outline of the introduction**, then **bullet outline of the full paper** including a figure plan. Every bullet earns its place by supporting a claim.
5. **Expand to prose**, section by section, following structure.md.
6. **Edit passes.** Apply prose-rules.md to everything. Then cut: first words, then sentences, then subsections. Read it aloud (or simulate doing so) — awkward prose is easier heard than seen.

## Reference files

- `references/structure.md` — Section-by-section anatomy: abstract formulas, introduction paragraph structure, figure 1, background, methods, results, related work, discussion, appendices, plus the standards for claims and evidence and a red-team checklist for reviewing. Read it when outlining, when drafting any section, and when reviewing organization.
- `references/prose-rules.md` — The sentence- and word-level checklist (Perez's rules plus Farquhar's style points). Apply it to every piece of prose before it reaches the user: drafts you write, edits you make, and as an audit list when reviewing their text.

## Editing etiquette

When editing the user's draft rather than writing fresh:

- Preserve technical meaning exactly. If a prose rule (e.g., "cut hedges") would change what the sentence claims, flag the tension instead of silently resolving it — sometimes the hedge IS the claim.
- Show significant rewrites, don't just describe them. For a line-edit pass, returning the edited text with a short note on the recurring problems teaches more than a list of abstract complaints.
- Don't pad, don't add hype, and don't make text sound like an LLM wrote it. Formal but plain. Sciency role-playing language ("we posit a novel paradigm") signals insecurity, not rigor. If anything, edits should shrink the text.
- When reviewing, lead with the most important problem (usually narrative or evidence), not a uniform list of nitpicks. Papers fail at the claim level far more often than at the comma level.

## Sources

- Ethan Perez, Easy Paper Writing Tips: https://ethanperez.net/easy-paper-writing-tips/
- Neel Nanda, Highly Opinionated Advice on How to Write ML Papers: https://www.alignmentforum.org/posts/eJGptPbbFPZGLpjsp/highly-opinionated-advice-on-how-to-write-ml-papers
- Sebastian Farquhar, How to Write ML Papers: https://sebastianfarquhar.com/on-research/2024/11/04/how_to_write_ml_papers/
