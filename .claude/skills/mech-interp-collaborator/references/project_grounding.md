# Project Grounding: North Stars, Proxy Tasks, and Project Archetypes

Distilled mainly from "A Pragmatic Vision for Interpretability" (GDM mech interp team, Dec 2025), plus Steinhardt and Nanda. Read when: choosing or scoping a project, judging whether ongoing work is grounded, designing or auditing a proxy task, deciding continue-vs-pivot, or when exploration has run a while without validation. The process wisdom here ages slowly; the *examples* of promising settings age fast — cross-check the dated snapshot in `field_map.md` and search before relying on them.

## The grounding quartet

- **North Star**: the scientific or safety-relevant outcome that ultimately matters — a meaningful stepping-stone toward the real goal (e.g. "detect deception in future systems", "stop models acting differently when tested").
- **Proxy task**: the measurable present-day task providing empirical feedback. It is a *proxy* by construction: the systems that matter don't exist yet, so the North Star can almost never be studied directly.
- **Validity argument**: why success on the proxy would genuinely update beliefs about the North Star. The acid test: *if you succeeded on this proxy, would you actually update toward believing progress on the North Star?* If not, find a different proxy.
- **Divergence risk**: how the proxy could improve without meaningful progress. Goodhart applies — a lie detector that only catches explicit admissions ("I should lie now") aces the benchmark and misses strategic deception. Regularly ask: how could this proxy diverge from what I care about? What breaks on a different distribution? Adjust or replace the proxy when it stops tracking the North Star; the North Star exists partly to enable this re-evaluation.

Proxy tasks are not restricted to boring benchmarks, and they can be *about understanding*: a non-trivial falsifiable prediction derived from the hypothesis counts — a minimal prompt change with a predicted behavioral effect, a handcrafted adversarial example, an intervention outcome predicted by the mechanistic claim ("if refusal is mediated by one direction, ablating it should jailbreak the model").

## Focused projects (proxy-task-driven)

Pipeline: theory of change → North Star (a tractable stepping stone on its critical path) → proxy task on today's models → solve it, method-agnostically. The theory of change stays stable across the project and carries the conviction that the work is worthwhile; the North Star may be refined and the proxy replaced with a better tracker.

Focused does not mean boring or linear. Canonical worked example: the concept-ablation fine-tuning project kept one theory of change (control fine-tuning when a spurious cue can't be removed from data) and one proxy task (train on 100%-spuriously-cued data; prevent the model learning the cue without touching the data) while cycling through several failed methods and candidate datasets before landing on ablating concept subspaces.

## Exploratory projects (curiosity-driven, proxy-task-validated)

Curiosity is genuinely powerful for surfacing insights nobody would have planned — and intellectual satisfaction is neither evidence of truth nor of importance, so ungrounded curiosity ends in rabbit holes. Three guardrails:

1. **Start in a robustly useful setting** (next section).
2. **Time-box, pre-committed.** Set the duration *in advance* — around two aggressive weeks is a good default; longer when experiments are inherently slow — and actually check in when it arrives, ideally with someone off-project who can keep things honest. During the box, resurface every few days to ask: what's the big idea here? Have I found anything? Am I in a rabbit hole? Which threads feel alive? Wanting to continue past the deadline without validation is permitted exactly once, with a fresh time box. The point is a mechanism that prevents indefinite exploration without grounding — "stop when it stops being interesting" fails because each week feels locally interesting.
3. **Validate with a proxy task at the end — post-hoc is fine.** The task doesn't need to have been predicted in advance; it needs to show the insight enables something objective. Phrase validation in behavioral or outcome terms, not interp vocabulary: "steering with this vector, built from eval-related prompts, increases blackmail behavior" is evidence; "this SAE latent is causally meaningful and its dashboard suggests eval awareness" is not. If genuine effort produces no such task, drop the thread — that is the guardrail doing its job, not a failure.

If several rounds of exploration validate nothing, recommend switching to focused work for a while; the skills built there make later exploration more productive.

## Robustly useful settings

A setting that looks valuable from *several* theories of change at once — typically analogous to important aspects of future systems, where interesting phenomena and usable proxy tasks are likely to surface. The durable test: would multiple distinct North Stars care about what gets found here? Neglectedness multiplies value: the field moves fast, newly emerged capabilities and phenomena are under-explored, and being early into a genuinely new setting buys low-hanging fruit (much less so once the phenomenon has gone viral).

The inverse also holds and deserves saying out loud: toy models, tiny LMs (GPT-2-Small class), and constructed model organisms *studied for their own sake* are not robustly useful settings — they are artificial enough that an investigation can easily be studying quirks that won't generalize. Projects there are held to a *higher* bar: a convincing explicit North Star and proxy task. (As tools inside a grounded project — an organism providing ground truth for an auditing game — they're fine.)

Current examples of robustly useful settings are dated field opinion; see the snapshot in `field_map.md`.

## Blending: tentative proxy tasks

A recommended default, especially for less experienced researchers: pick a robustly useful setting, set a *tentative* proxy task, explore against it for a few days, then reflect and revise or replace the task. Decisions stay task-grounded while remaining responsive to what's learned. The reported experience: before there was *a* North Star in mind, the work was much less productive.

## Contribution type: methodology vs. understanding

Orthogonal to focused/exploratory, and it changes what evidence a project owes:

- **Methodology** — "here is how to solve this class of problem." Comparisons to tuned, non-sandbagged baselines are mandatory; proxy tasks usually need direct safety relevance; discovering that *standard* methods just work on a new problem is itself a legitimate methodology contribution.
- **Understanding** — "here is what's happening in this phenomenon." The proxy task is validating non-trivial falsifiable predictions of the interpretation; baselines mainly contextualize; the safety relevance lives in the phenomenon itself.

Name which one the project is. A subtle consequence: on models far from the frontier, most safety-relevant contributions are actually *methodology* — the object-level insight won't transfer, but "this method surfaces this kind of structure" does. (The entity-recognition work mattered more as evidence for SAEs-as-discovery-method than as facts about hallucination.)

## Comparative advantage as a project filter

Before committing, ask whether the problem rewards what interp researchers are distinctively good at: working with internals (steering or probing where data fixes can't reach — e.g. suppressing eval awareness when realistic eval data can't be constructed); deep dives with a scientific mindset on fuzzy questions lacking ground truth; qualitative insight into what drove a specific behavior; unsupervised discovery of hypotheses nobody would have generated. If prompting or a cheap supervised classifier plausibly achieves the downstream goal, internals must buy something concrete. Then — having chosen the problem for the edge — still proceed method-agnostically: maybe the guess about which method wins is wrong, and if you don't check, you don't know.

## When to relax the guardrails

The "mess around until you understand it, validate at the end" style demonstrably works for some teams, and treating proxy tasks as a mid-course optimization target can even be counterproductive (a steering vector tuned directly on the misalignment-rate readout is a cherry-pick; the readout must stay pure). But the style's success rests on two conditions: (a) access to a highly neglected, robustly useful setting — first eyes on a new frontier model's internals, proprietary RL transcripts — where the base rate of stumbling onto something real is high; and (b) strong, demonstrated research taste for which threads are alive. When both hold, objective tasks can serve as final validation rather than mid-course driver. For most researchers most of the time, they don't hold — keep the time box.

## When to develop new methods

Not "I have a hammer"; the sequence is: a well-motivated proxy task → standard and simple methods honestly tried on it → diagnosis of what's actually wrong with them → a targeted improvement → comparison against those methods as baselines → hill-climbing with overfitting guards. Method minimalism means the simplest thing that *works*, not simple things per se — a complex method that verifiably beats baselines on an important task is excellent. But every added layer costs hyperparameters, bugs, compute, and adoption odds (especially at frontier scale or in production); complexity must pay rent. Infrastructure and dataset-building are legitimate contributions once the blocking issue they unblock has been identified — not before.

## Failure modes this file exists to catch

- Optimizing a measurable metric whose link to any North Star was never argued. The field's SAE detour is the canonical case: a year of reconstruction/sparsity pareto-frontier progress produced little decision-relevant learning, while proxy tasks (OOD probe generalization, unlearning, auditing games) produced the actual update — SAEs strong for unsupervised discovery, weak against tuned baselines elsewhere.
- "Apply method X to domain Y and see what happens" as a project *commitment* (fine as a bounded mini-exploration).
- Exploration extended indefinitely because each week feels locally interesting, with the validation step perpetually deferred.
- Validation phrased entirely inside interp's own concepts, so the story can never fail.
- A claimed methodology contribution with sandbagged or missing baselines; a claimed understanding contribution with no falsifiable prediction.
- Sunk-cost continuation — "I've already built…" — instead of a fresh would-I-start-this-today decision at the sprint boundary.
