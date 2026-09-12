# H1 stopping point — the eight separate verdicts (2026-09-07)

By design (H1.10), H1 is reported as **eight separate verdicts**, not one all-or-none. Each is scoped to the conditions actually tested. All evidence is on Qwen3.6-27B (`6a9e13bd`), the teacher-forced copy organism(s), J-lens (J_NP) primary with a plain-sentence axis (RESID_P) and the model's own logits (LOGITS) as companions (agreement across them is robustness, **not** independent samples), readouts at interior carrier positions, windows L48–50 and L51–59. "Evaluation scale" = the evaluation banks on held-out carriers C2/C3. **Everything here is a lens/axis/logit readout; nothing about behavior (H3) or maintenance mechanism (H2) is established.** Detailed findings and numbers are in `context/project_status_2026-09-07.md §1`; reports under `H1/results/`.

---

## 1. Natural modulation — **established (evaluation scale)**
The maintain instruction raises the introduced content's readability above the project's mention/control: J_NP +0.18 (23/32) at L48–50, +1.41 (32/32) at L51–59; agrees on RESID_P and LOGITS. maintain ≈ a bare mention at L48–50 (most of the effect is priming, cf. paper A.10), exceeds it at L51–59 and in prominence (rank-1-anywhere 0.56 vs 0.03). The direct (no copy bridge) organism shows focus > mention at evaluation scale. **Scope:** readout only; a readability increase, not "the model represents/uses" the word.

## 2. Source causality — **established (causal, L_x = 36 frozen)**
Sustained replacement of the source span's block outputs from block 36 onward moves the later readout toward the donor identity (fraction of the natural contrast ≈0.5 at L48–50, ≈0.95 at L51–59; 8/8). Same-source replacement is a bitwise no-op; layers < 36 identical between futures; damage nil. **Scope:** single-token quoted sources, this scaffold; a foreign-content damage-only donor control was not run.

## 3. Candidate-state modulation — **established as a GAIN, not a task-specific state (deflationary)**
Moving a fitted coordinate ĝ (maintain−mention at block 35) to the opposite arm's level before the block-36 source swap changes transfer reciprocally (I 16/16, dose-monotone, exact writes). **But ĝ is a uniform readout gain, not a controller:** the interaction is predicted by each direction's effect on the resident readout (r 0.95–0.999), and the "task state / controller" reading is not supported. This reproduces and overturns the earlier pilot's framing.

## 4. Specificity — **ĝ is not specific; a selective gain (d_shared) is**
ĝ-orthogonal high-variance directions reproduce ~40–60% of the interaction with the same reciprocal signs (registered bar fails at L48–50, passes at L51–59). A **native pointed−control direction d_shared is a selective gain** (scales the pointed source, ~1.0 on unpointed) that transfers to held-out identities (cos 0.85). So a *selective* state exists; ĝ is not it. A native pointer contrast is a gain with a small early-window bias, **not an address**.

## 5. Semantic / J selectivity — **no J-only artifact found**
Every established effect above and below registers on the independent plain-sentence axis (RESID_P) and the model's own output logits, not J_NP alone. No effect is J-lens-specific at the tested sites. **Scope:** the instruments share the same forwards (robustness, not independent evidence); J_CB/R_CB run for natural modulation only.

## 6. Prompt / domain scope — **broad within the tagged copy-bridge organism; untested without it**
Selection survives all four presentation(quoted/bare) × wording(copy/directed) renderings (S 8/8 each, evaluation scale) **within the tagged copy-bridge organism** (`scaffold_generality`); the directed wording amplifies *more* but suppresses unpointed less. It extends to **explicit categories** (associated-member content, `tagged_categories`) and to **computed sums** (the computed value, `computed_sums`). **Not established:** selection without the copy bridge / tag head — the pure direct organism was not run causally.

## 7. Selection — **established, localized (the strongest H1 result)**
The tagged instruction **selects** which of three tagged sources is carried: S 8/8 on every instrument, unpointed sources suppressed **below** control (amplify + suppress); no 1/k dilution through k=6 (**not** an established "flat/unlimited budget** — no equivalence test; strong selectivity persists while no-pointer transfer dilutes); a mid-carrier textual cue reassigns the pointer at L≥51 and in the logits. It reaches **category-associated members** never present as tokens (S_member +0.82, 8/8; but member *readability* ≠ member *representation*). **Localization (`selection_localization`):** the source-side-tag account is architecturally excluded (sources precede the tag); the pointer state is carried by the **instruction residuals, tag-dominant** (region_split: user-side carrier & delimiters negligible), sufficient by block 36 with causal dependence exhausted before ~48, and it **causally redirects which source transfers** (B→A→B, C→A→C, ~0.7, 8/8, damage nil). **Open:** the read-site *component* (attention vs GatedDeltaNet vs MLP) — Step 2, not run.

## 8. Transformation — **established as availability/precomputation, additive (not zero-sum)**
Two organisms show the carrier expressing a *derived* variable. **Computed sums:** a different-sum donor moves the sum readout (C_diff^sum +1.90, 8/8) while a same-sum sibling leaves it **invariant** (equivalence-tested) but moves the addends — the transferred content includes the model's **computed sum**, a latent never a token. **Early/late mapping:** early availability of a word→letter codebook **precomputes F(X)** during the carrier, source-conditioned to X (E_F^sc +1.07 / +2.45, competence 1.00/0.99), while X stays readable — **both X and F(X)** (additive), a length-matched control ruling out a generic long-prefix artifact. **Scope:** does not decide whether the derived value travels or is recomputed downstream (H2); one mapping family; specific arithmetic facts.

---

## What H1 does NOT establish
- **Any behavioral (H3) consumption.** Every result is a readout; whether any selected/transformed content is *used* by a downstream consumer is untested. A gain and a selection can make identical lens predictions and different behavioral ones.
- **Maintenance mechanism (H2).** What holds the content across the carrier (source K/V, GatedDeltaNet recurrent state, re-retrieval) is not started; the hybrid complete-state parity control is a prerequisite.
- **The read-site component** of selection (Step 2 of localization).
- **Member/individual representation** from category labels (only member readability).
- **Cross-model generality** (one model), and **domain generality without the copy bridge/tag head**.

## Bottom line
H1 establishes, at the readout: a real, source-causal, instruction-modulated **selection** phenotype that is a *gain* rather than a specific-state controller (ĝ), carried by a *selective* direction, generalizing across presentation/wording and to categories and computed values, with the pointer state **localized to the instruction residuals (tag-dominant, blocks 36–48) and causally controlling which source transfers**, and a **transformation** phenotype (precomputation of a derived variable, additive). The load-bearing next questions are **H3 (is any of this used?)** and **H2 (what maintains it?)** — where a negative result is still fully possible.
