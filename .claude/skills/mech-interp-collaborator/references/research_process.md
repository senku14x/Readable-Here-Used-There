# The Research Process

Distilled from Neel Nanda's research-process sequence and guide (2025) and Jacob Steinhardt's "Research as a Stochastic Decision Process". Use this to diagnose where the user is in a project, apply the right north star, and make prioritization/pivot calls. This is process wisdom, not field state — it ages slowly.

## The five phases and their north stars

1. **Ideation** — choose a problem/domain. North star: pick something fruitful. For early projects, cheat: replicate-and-extend a paper, take a mentor's idea, or pull from a public agenda. Deep problem-picking taste comes later; do not gate starting on having it.
2. **Exploration** — gain surface area. North star: **information gain per unit time**. You often don't have a hypothesis yet; the output of this phase is discovering the right questions to ask.
3. **Understanding / validation** — test hypotheses. North star: **convince yourself a specific hypothesis is true or false.** Begins only once you can write the hypothesis down and say what evidence would move it.
4. **Execution** — carry out an agreed plan. North star: verified-small-then-scaled, without churning on settled decisions. (Nanda's canon names four stages; execution is broken out here because its failure modes — re-litigating decisions, scaling unverified code, polishing components ahead of need — differ from understanding's.)
5. **Distillation** — compress, refine, communicate. North star: concise, rigorous truth that survives a skeptical outside reader. A higher bar than convincing yourself.

Phases are a cycle, not a line — write-ups reveal missing experiments; failed hypotheses send you back to exploration. That is normal, not failure.

**The most common phase-diagnosis error:** junior researchers think they are in Understanding when they are in Exploration. They feel bad about lacking a clear hypothesis and next step, and freeze. If the user seems stuck this way, name it: they don't need a plan yet, they need information. Conversely, someone endlessly "exploring" a result they already believe and plan to publish is in Understanding/Distillation denial and needs the skeptic protocol.

## Skills by feedback-loop speed

Research decomposes into skills learned at very different rates, because learning requires feedback. When advising on what to focus on or diagnosing why something feels hard, use the loop speed:

- **Fast (minutes–hours):** planning/writing experiment code; running and debugging; interpreting a single result.
- **Medium (days):** designing genuinely discriminative experiments; hacky-vs-quality code judgment; exploring without getting stuck; writing up results; knowing whether results support conclusions.
- **Slow (weeks):** prioritizing the next experiment; continue-vs-pivot calls; spotting subtle interpretability illusions; identifying bad ideas *without* doing a project on them; deep literature knowledge.
- **Very slow (months):** generating good research ideas — the core of research taste.

Implications: learn fast/medium skills first and *cheat* on slow ones early (mentor-supplied ideas, replicate-and-extend, public agendas) rather than stressing about lacking them. Novices often develop conviction in directions well before they develop the ability to not be confident in bad ones — one or two convinced-then-wrong experiences are cheap tuition, but budget for them. For slow skills, substitute structure for intuition: write down *why* an experiment is the right call before running it, then audit the decision at the post-mortem.

## Exploration toolkit

- **Move fast.** A new plot every few minutes when experiments are cheap. Fast feedback loops are the single biggest velocity lever: notebooks (Jupyter/VS Code interactive), dataframes over rigid logging frameworks, de-risk code on the smallest model that could work, tiny data first.
- **Surface-area moves when stuck:** read the model's outputs/CoT, vary the prompt, look at raw dataset examples, probe for a concept, logit lens, check an SAE/attribution graph, steer, plot activation distributions. Reading your data is disproportionately valuable — data quality drives results and is usually worse than assumed.
- **Timers.** Stuck or drifting → 5-minute timer, brainstorm what could be happening / what to try next. Before any experiment that takes >30 minutes, stop and brainstorm whether a cheaper experiment gets the same information.
- **Pivot thresholds (heuristics, not laws):** learned nothing in ~2 hours → change approach; ~5 hours → seriously change approach; ~2 days → consider changing problem.
- **Epistemics of exploration:** most of the probability mass belongs on "something I haven't thought of yet." Temporarily believing false things is fine if you're moving fast and reflexively trying to falsify — the danger is a slow rabbit hole built on an untested premise. Deep dives into single prompts/case studies are legitimate here.
- **Logging:** keep a running research log plus a separate highlights doc of the most interesting results — connections get spotted by rereading it. Also keep a long-running curiosities doc: every idle "huh, weird" and paper-reading confusion goes in; it becomes the raw feed for ideation later.
- Too much skepticism is a real failure mode *in this phase*: you must be able to entertain unproven hunches to design good experiments.

## Understanding toolkit

- Before testing a hypothesis: 5-minute timer on "what are the ways this could be false?" and another on "what else explains my observations?" Convert the outputs into concrete experiments.
- The Bayesian question is "was this observation **more likely** under hypothesis A than B?" — not "is it consistent with my favorite?"
- The **obnoxious-skeptic exercise**: imagine a hostile reviewer explaining away each result; design until they have no leg to stand on. (Proportionality: for unimportant side-claims that are plausible on priors, a shallow case is the right call — move on.)
- Qualitative case studies in this phase must be **randomly sampled** (or exhaustive if the space is small), because implicit cherry-picking is nearly automatic. Exception: pure existence claims ("at least one X exists").
- A great experiment elegantly and conclusively distinguishes several plausible hypotheses, validates a non-trivial prediction, and is tractable. Generate them by simulating the world where H is true and enumerating its other implications.
- Keep a running "things I believe to be true" doc: hypothesis, experiment, result. Every entry is auditable later.
- The feeling of being convinced is not evidence. Skepticism is an active practice; insufficient skepticism feels, from the inside, like normal research.

## Prioritization

- Good prioritization = a clear north star + judgment about which actions serve it + actually scheduling time to ask the question + ruthlessness in dropping weak directions (balanced against switching costs — flitting constantly teaches nothing).
- Periodically (e.g., weekly) re-derive the plan from scratch: What's the goal? What has consumed time? What's blocking? What mistakes recurred and what systematic change prevents them? What am I confused about? Would I start this project today, knowing what I know?
- People fail in one of two directions — rabbit-holing vs. analysis paralysis. Identify which way the user tends and give the corresponding advice, not both.
- **Fail fast:** the biggest possible time sink is weeks on a doomed direction. Ask: if this is doomed, what is the fastest way to find out? Several quick-and-dirty attacks from different angles beat one polished attempt.

## Steinhardt: research as a stochastic decision process

- **Sort tasks by expected information per unit time, not by ease.** People instinctively do easy tasks first; do the most *informative* (often the riskiest) first. Front-loading failure probability saves multiplicative time. As a mental model, a task's "failure-discovery rate" scales like log(1/p_success)/time — tasks that are both riskier and quicker dominate the queue.
- **Calibrate success probabilities with verbal buckets** rather than fake precision: "confident, no unforeseen difficulties" ≈ 95%; "confident modulo Murphy's law" ≈ 90%; "I see the basic path and each step should work" ≈ 65%; "intuition says possible but the path is murky" ≈ 30%. Use these when triaging which component to de-risk first.
- **Practice time estimation.** Decompose work into ~20-minute-to-2-hour chunks, estimate each, log actuals, and review — calibration improves within weeks and makes the information-rate sort actually computable.
- **De-risk, then execute.** For each component, find a cheap way to gain high confidence it is feasible before building it properly (e.g., hand-inspect a thousand dataset examples before building the pipeline). Know explicitly which mode you're in: de-risking (establish feasibility fast) or execution (assume feasible, move fast).
- **Ceilings and baselines.** Cheat versions of hard components give a performance ceiling ("if this part worked perfectly, would the system work?"); simple baselines give the floor. Together they bracket and interpret any result. Brute-force implementations also serve as debugging oracles for fast versions. Cheat on the components that are *not* the main uncertainty; attack the one that is.
- **Research is an exponentially branching search tree.** Prune at the level of conceptual approaches, not single instantiations. When something fails, always ask *why* — otherwise you will retry siblings that fail for the same reason, or wrongly abandon a branch. "I tried X and it didn't work" usually means "I tried one implementation covering a fraction of a percent of X."
- **Hold a high bar for ruling out.** "This doesn't seem promising" is an update, not an elimination; a solid argument for why an approach is doomed is worth far more. Invert feelings into experiments: pessimism about an approach is a great reason to try to *prove it can't work* — and failing to rule it out is a legitimate reason for renewed optimism.
- **Systematic pruning enables ambition.** The point of being able to rule out branches decisively is that it makes low-probability, high-value ideas affordable — this framework is not an argument for only trying safe bets.
- Delay building heavy tooling until experience has refined what the tooling should do; there is a real trade-off between building tools early and building the *right* tools.

## Ideation practice

Split into generation and evaluation; do not do both at once.

- **Generate:** block an hour, blank doc, write ≥20 ideas, quantity over quality. Feed it from the long-running curiosities doc and from confusions noted while reading papers.
- **Evaluate:** gut-rate each out of 10 and sort — this is as good a first prune as any. If a mentor or collaborator is available, have them rate independently, compare, and interrogate every large disagreement; that comparison is the highest-density supervised data for research taste that exists.
- For the top few, answer: What would success look like? How surprised would I be if a month of work produced nothing interesting? What skills/models/data/compute does it need, and are they available? What did the closest prior work do, and does a quick literature check surface anything?
- **Taste exercises for the long run:** before each mentor meeting, predict their answers to your questions, then compare. When reading a paper, stop after the introduction and predict the methods and key results before continuing — papers become a large, fast offline training set for intuitions.

## Sprints and post-mortems

Work in 1–2 week sprints. After each: an hour-plus post-mortem — what was tried, what worked, what mistakes, what to change, which skills got practiced. Then a deliberate decision: **pivot by default, continue only if it's going genuinely well.** This converges on long-term projects that earned it, instead of the first ambitious idea that induced sunk-cost attachment. (For exploratory projects, the sprint boundary is also the time-box check-in — see `project_grounding.md`.)

## How to apply this as the collaborator

- Diagnose the phase first; the right advice is phase-dependent (skepticism dial, experiment style, whether a plan is even needed).
- In exploration, optimize the user's information rate: suggest the cheapest next look, not the most rigorous one.
- In understanding, run the skeptic protocol from SKILL.md.
- When the user is deciding whether to continue a direction, invoke fail-fast and the branching-tree logic: what's the cheapest experiment that could kill this, and has the *reason* for any failure been identified?
- Watch for sunk-cost language ("I've already built…", "after all this work…") and name it.
- When the user is stuck on a slow-loop skill (prioritization, idea quality), point at the structural substitutes above rather than implying they should already have the intuition.
