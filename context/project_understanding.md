# Project understanding: hypotheses, competing predictions, and what discriminates them

Written 2026-09-06, before any experiment ran, after reading the Anthropic global-workspace paper and Nanda's review. This is the orientation document for the investigation. It records no results.

## 1. The question in one paragraph

A prompt introduces a word (or category, or a pair of numbers) and then asks the model to copy an unrelated sentence. The copy is teacher-forced, so the visible text is identical across conditions. Three things can differ inside the model: how much the introduced content influences later computation (H1), what keeps that content available across the copied sentence (H2), and whether any later computation reads the specific representation our instruments expose (H3). Each is a separate causal claim with its own alternative.

## 2. The three hypotheses, their strongest alternatives, and the discriminating experiment

### H1: task-conditioned selection and transformation

**Claim.** A task-associated internal state, manipulable before the source counterfactual begins, changes the later response to source information. Stronger forms: the state selects which of several sources is carried, and it can change which variable is carried (X vs F(X)).

**Strongest alternative.** The instruction only adds an instruction-related readout (a label) without changing source influence; or the fitted direction is a generic high-variance perturbation any matched direction reproduces; or the effect is a lexical handle specific to one prompt wording.

**Operational form.** R(do(S=Y), T) − R(do(S=X), T) changes when a task-associated state is manipulated before the source counterfactual begins. The estimand is the interaction I = ½[−ΔC_M + ΔC_N], where C is the swap-minus-noswap contrast and ΔC is its change under the state move, with the primary prediction ΔC_M < 0 and ΔC_N > 0 (reciprocal).

**Discrimination.** The temporal-order design: move the state coordinate at block 35 on carrier positions; introduce the source counterfactual only at layers ≥ 36; assert bit-identical histories through block 35. A reciprocal interaction that beats a small frozen panel of equal-dose controls, transfers across held-out identities, and is registered by an independent plain-sentence axis as well as the lens, supports shared task modulation. A one-sided effect, a matched control reproducing it, a J-only response, or a native-only direction each fires a named branch (H1.1 table).

**What the earlier pilot already showed on the same organism family.** All of this exists at n=8 pairs on Qwen3.6-27B: reciprocal interaction −0.104/+0.126, beating isotropic and covariance-p95 floors but only barely the ĝ-orthogonalized covariance max (0.1032 vs 0.1039), with reciprocity as the distinguishing property. It also showed that the direction's effect is scoped to quoted introduced targets, is at floor on bare category names, and carries about a third of the instruction's effect. The new project must re-establish this under its own manifests and cannot inherit it.

### H2: maintenance and reconstruction

**Claim.** Later readable identity depends on an identifiable supporting state (source cache, other-prompt cache, earlier-carrier cache, injected-token cache, recurrent state) that can reconstruct the readable component after it is perturbed.

**Strongest alternative.** The readable component itself is sufficient to seed later identity (a self-propagating state); or apparent recovery is incomplete erasure or measurement variation.

**Discrimination.** Two entry paths. Pulse: one write at (ℓ₀, t₀), then no hook; compare a full-residual pulse against a naming-contrast pulse and a plain-axis pulse, with matched-norm controls, on the clean-subtracted later trajectory. Natural recovery: erase to a reference level over a block interval or at one position, release, and measure the deficit at depth and at later tokens. Then the boundary experiment: at a completed prefix boundary, define every state class the future can read, validate a complete-state transplant that reproduces the Y continuation, and factor it (attention K/V vs recurrent Z, then source vs other-prompt vs earlier-carrier cache) while future tokens stay fixed.

**Why this model.** Qwen3.6-27B is a hybrid with 48 GatedDeltaNet blocks and 16 full-attention blocks. It has a genuine carried recurrent state, so "persistence vs re-retrieval" has a third real answer here that a pure transformer cannot offer. The earlier pilot showed the recurrent read of the source span carries about two-thirds of post-L36 transfer and that subspace erasure is partly undone from carrier-internal state, but never transplanted caches or recurrent state and never ran a one-position pulse. H2 is where the new project is most novel and most at risk of implementation failure (state serialization for a hybrid cache).

### H3: downstream use

**Claim.** A specified readable representation supplies identity information used by a specified downstream consumer (a codebook letter for the introduced word).

**Strongest alternative.** The consumer accesses a richer, different, or redundant encoding; or the measurement moves without installing the consumed variable.

**Discrimination.** Validate a boundary at which a full donor moves the answer (U_full > 0 with donor flips). At that identical cut, compare full residual, naming contrast, plain-axis contrast, a small orthonormal naming basis, and matched random subspaces. Then cross the representation intervention with route restriction (Ω) and attempt rescue. The interpretation table in H3.3 fixes what each outcome licenses.

**What the earlier pilot already showed.** With coverage 0.94–1.00 and same-site positive controls of 2 to 33 nats, single-direction clamps and the fitted task direction changed no codebook answer, and every tested organism could still re-read the source span at the answer. The new spec's boundary validation and route restriction are designed to close exactly that gap.

## 3. How the experiments are ordered and why

Package 1 (natural and source pilot) comes first because H1.4 is undefined if the source contrast C is near zero at the chosen depth, and because the cheapest decisive result in the whole project is whether maintain exceeds mention at all on this organism. Package 2 (task-state pilot) fits G on fitting words only and runs the eight-forward factorial. Package 3 extends to steering, scaffolds and categories. Packages 4 and 5 (maintenance and consumer) each begin with their own positive control. Package 6 ties one state-source contrast to a consumer.

## 4. Consequential issues identified before implementation

1. **The source-replacement start layer.** The default is L_x = 36. In the earlier pilot, post-L36 content reached the readout at about half the L23 effect on the project scaffold. Content that reached the carrier below block 36 is untouched by the swap. I will sweep L_x on calibration pairs inside Package 1 before freezing it, (defaults are hypotheses).
2. **Sites vs architecture.** Block 35 is a full-attention block output (index 35 = 8×4+3); blocks 48–50 are linear-attention outputs; 51 is the next full-attention block. The readout window and any transplant boundary must be stated in these terms.
3. **The control arm.** "That word occurs one time" was causally indistinguishable from plain mention but sat below it at readout in the earlier pilot. Plain mention and absent source are run as co-primary diagnostics in Package 1.
4. **G absorbs wording.** The maintain-minus-control mean at block 35 contains instruction-wording residue. The specificity panel and the target-presentation factorial address this; a wording-transfer check (G from one wording tested on another) is cheap and will be added to the design spec.
5. **Sub-surface regime.** On this scaffold the maintained word is outside the lens top-50 at the readout window; effects are differences between two named columns of a 248k-way readout. The project's prominence diagnostics (r_min, f_10) are mandatory companions, and the readout window may need to extend to L51–59 where rank-1 surfacing begins.
6. **Nondeterminism across sequence lengths.** Lens values differ at the fourth decimal between renderings of the same prefix. Mechanical gates compare within a rendering; the numerical tolerance will be measured on calibration and frozen.
7. **Hybrid cache serialization (H2).** transformers' cache object for this architecture carries both K/V and DeltaNet recurrent state plus conv buffers. The complete-prefix-state positive control is a hard prerequisite, and the reference never built it. Do not start H2 transplants until it passes.
8. **Effect sizes will be lens-dependent** and the reference found the direct (no copy instruction) rendering gives a higher mention baseline than the copy rendering. Direct and controlled organisms are never pooled.
9. **Compute.** About 0.15 s per forward with all-layer recording. Package 1 is a few hundred forwards; Package 2 is about 8 forwards per directed pair per carrier plus controls, roughly 2,000 to 4,000 forwards.

## 5. Instrument registry names

J_NP (`np`) primary; RESID_P (`s_p`) plain-sentence axis; LOGITS (`z_out`) at output/consumer sites; J_CB (`cbj`) and R_CB (`cbr`) on a declared robustness subset. The registry with hashes and loading configuration lives at `common/configs/instrument_registry.json`.
