# Project status, detailed — 2026-09-07

Everything below is on Qwen3.6-27B (`6a9e13bd`), the Neuronpedia J-lens (J_NP) as primary instrument with the plain-sentence axis (RESID_P) and the model's own logits (LOGITS) as companions, teacher-forced copy organisms, readouts at interior carrier positions, windows L48–50 and L51–59. "Evaluation scale" = the project's evaluation banks (32 words / 16 pairs / 8 triples) on held-out carriers C2/C3. "Pilot" = calibration words on the fitting carriers C0/C1. Reports are under `H1/results/`.

## 1. What has been established

### 1.1 Natural modulation (H1.2, evaluation scale, `natural_modulation_evaluate.md`)
- The maintain instruction raises the introduced word's lens readability above the project's mention control ("That word occurs one time"): J_NP +0.18 [+0.07, +0.30] (23/32 words) at L48–50, +1.41 [+1.26, +1.55] (32/32) at L51–59; J_CB, R_CB, RESID_P and LOGITS agree in sign.
- It does **not** raise readability above a bare mention at L48–50 (+0.03, 19/32); it does at L51–59 and in prominence (rank-1 anywhere over L24–59: maintain 0.56, mention 0.03, plain mention 0.03, absent 0.00).
- The project's control sits **below** a bare mention (−0.15 at L48–50); all three suppression tails sit below the control (ignore −0.35, do-not-think −0.25, never-think −0.15). "Never think about that word" lowers mean presence while surfacing the word at rank 1 in most words: mean and peak metrics disagree under negation.
- Direct organism (released phrasing, no copy bridge): focus > mention +0.85 (30/32) direct, +1.37 (32/32) copy-adapted at evaluation scale; the pilot (8 words) had the direct contrast null.
- Rank-1 surfacing of the introduced word happens at layers 51–59, at function-word carrier positions (" the", " for"); at L48–50 everything is a sub-surface column difference.

### 1.2 Source transfer (H1.2 causal, pilot only, `source_transfer.md`)
- Sustained replacement of the quoted span's block outputs from L_x onward moves the later pair margin toward the donor at every L_x ∈ {23…44}, 3/3 pairs. Fraction of the natural X/Y contrast at L_x = 36: ≈0.5 at L48–50, ≈0.95 at L51–59; monotone in L_x at the early window, flat at the late one (the late window is dominated by reads at or after block 44).
- Maintain transfers more than the control at every L_x. **Frozen: L_x = 36, state site 35, windows L48–50 + L51–59 co-primary** (`H1/design_specs/package1_decisions.md`).
- At evaluation scale the clean transfer rows live inside the task-state run: C_36 maintain vs mention arm difference A = +0.07 [+0.01, +0.14] (12/16) at L48–50 and +2.38 [+2.04, +2.72] (16/16) at L51–59.

### 1.3 Task-state coordinate ĝ (H1.3–H1.5, evaluation scale, `task_state_modulation_evaluate.md`)
- ĝ = unit mean of maintain-minus-mention block-35 interior residuals over the 16 fitting words; split-half cosine 0.989.
- Moving ĝ to the recipient word's opposite-arm natural level before a block-36 source replacement changes the incremental transfer reciprocally: I = +0.124 [+0.100, +0.149] (J_NP L48–50), +0.95 [+0.85, +1.06] (L51–59), RESID_P +0.038 / +0.74, LOGITS +1.84; all 16/16; dose-monotone; realized writes ρ 0.999–1.001, κ ≥ 0.9998; carrier damage nil; far above a 64-random-column floor.
- **Not specific to ĝ.** With the ĝ component projected out, high-variance directions of the block-35 residual reproduce ≈60 % of the interaction at L48–50 (registered bar fails) and ≈40 % at L51–59 on J_NP/LOGITS (bar passes), 71 % on RESID_P L51–59 (fails); several are reciprocal 16/16. Isotropic directions do nothing.
- **Shared consequence.** Across all 19 directions tested, the interaction is predicted by the direction's effect on the resident readout with no source change (r = 0.95 / 0.998 J_NP, 0.85 / 0.996 RESID_P, 0.999 LOGITS). Any direction that scales the readability of whichever word is currently sourced produces this reciprocal signature.
- **Reading:** ĝ is a readout gain on the sourced word, applied to resident and incoming content alike. The "task state / controller" reading is not supported. This reproduces the earlier pilot's A1-v2 phenomenon and overturns its framing.

### 1.4 Tagged selection (H1.8, evaluation scale, `tagged_selection_evaluate.md`) — the discriminating result
- Organism: three quoted words tagged (A)(B)(C); "Keep the word tagged {T} in mind while you copy…"; three rotations per triple; each source replaced from block 36 by an arm-matched donor.
- **The instruction selects.** Pointed source's transfer 0.48 vs unpointed 0.05 vs no-pointer 0.12 (J_NP L48–50): S = +0.43 [+0.34, +0.53], 8/8; L51–59 S = +4.10; RESID_P +0.20 / +5.60; LOGITS +4.58; all 8/8. Unpointed sources transfer **less** than with no pointer on every instrument (Q = −0.07 … −0.65, 0/8 positive): amplification of the pointed source plus suppression of the others. U ≈ S: the instruction's whole effect lands on the pointed source. Readout without intervention agrees (S_nat 8/8; rank-1 pointed 0.95 vs unpointed 0.03). Output-disposition screen passes.
- Accounts predicting S ≈ 0 (gain on whichever word is sourced; generic gain on all introduced words) are rejected here.
- **ĝ scales every source by the same ~10 % regardless of relevance** (pointed ratio 0.87–0.89, unpointed 0.87–1.06): a uniform gain, not the selector.
- **A native pointed-minus-control direction (d_shared) is a selective gain**: pointed ratio 0.59–0.83, unpointed ≈1.0 (and slightly up at L48–50); the pilot-fit version transfers to held-out identities (cos 0.85 with the native refit) with the same profile, 8/8.
- **A pointer contrast (pointed B − pointed A) is not an address**: at L48–50 it raises the newly pointed source (+0.105, 8/8) with A slightly down; at L51–59 and on LOGITS it raises the already-pointed A more than B. Mostly a gain with a small early-window B bias.

### 1.5 Competition and mid-carrier cue (H1.8, evaluation materials, `competition_and_cue.md`)
- Under a pointer the pointed source's transfer is flat from k = 2 to 6 (4/4 sets, every instrument; a 1/k budget is excluded) and S is CI-clear at every k. Without a pointer the focal source's transfer falls with k (dilution). No shared budget; the pointer overrides dilution.
- A mid-carrier cue switching the pointer A→B lowers A's and raises B's transfer on the post-cue positions at L51–59 and in the logits (8/8), not yet at L48–50; the same-tag cue is not neutral (it lowers A and raises B relative to no cue). ĝ and d_shared coordinates move with the switch (8/8), unlike the earlier pilot's CP-5.

### 1.6 Instruments and infrastructure
- Gates: repeat/empty-patch/same-source bitwise; lens subprojection diff 0.016; realized-write ρ/κ; sequence-length nondeterminism up to 0.33 lens logits per cell for a one-token length change (cross-rendering tolerance input); all in `common/configs/instrument_gates_result.json`.
- RMSNorm in this architecture is `norm(x)·(1 + weight)`; the float32 diagnostic uses that gain and now equals the model path to 1e-4. (The earlier pilot's folded naming directions used `weight`; cosine 0.998 with the correct direction.)
- Materials: 8 of the 16 spec categories lack four single-token unshown members under this tokenizer (reptiles, citrus fruits, nuts, flowers, trees, musical instruments, gemstones, ocean creatures); recorded, not yet used.

### 1.7 Tagged categories (H1.7 scope ladder: abstraction vs lexical echo, extension scale, `tagged_categories_{gate,select}.md`)
- **Gate (member-instrument positive control).** A maintained category raises its four unshown members over absent by +0.36 [+0.13, +0.60] (7/8 categories) at L51–59 (**PASS**); +0.18 [−0.10, +0.45] (6/8) at L48–50 (**FAIL**, CI includes 0; tools/furniture members invert — instrument uneven across categories). Label/LOGITS gates far stronger (maintain−absent +1.70 label, 8/8). maintain−mention small: most of the gate is mention (paper A.10). Member endpoint validated at L51–59 only.
- **Select (the result).** Pointing at one of three tagged category labels and replacing its source from block 36 selectively transfers the pointed category's four **unshown members** (never tokens in the prompt): S_member = +0.82 [+0.76, +0.88] at L51–59 (8/8 triples, 6/6 categories; +0.17 at L48–50), Q < 0 (unpointed suppressed below control), U = +0.73. Same profile on label (S +2.42), the independent RESID_P member axis (+1.33) and LOGITS (+0.83). Transfer coherent across the whole set (24/24 donor members up, 24/24 source members down); damage nil (top-1 retention 1.000); S = 0 exactly through L36 (the intervention boundary), rising from L39, late-band dominant.
- **Licensed (scoped):** selection of category-**associated** content, not merely the literal label token — rules out lexical echo; the signal reaches tokens never in the prompt, on two differently-constructed readouts + the output logits. **Extension scale** (6 shared identities, overlapping folds): weaker footing than word-level tagged_selection.
- **Not licensed:** member *readability* is not member *representation*. A single transferred "category-ness" direction read out on correlated member tokens reproduces the pattern; RESID_P cannot separate category-level from member-specific content (design §10 disclaims label→member representation).
- Decision tree: gate PASS + S_member>0 & Q≤0 (both clusterings) ⇒ Stage 2 (`directions`) warranted; deprioritized in favour of `scaffold_generality` (H1.7 wording/presentation) per researcher decision.

### 1.8 Scaffold generality (H1.7, tagged 2×2, evaluation scale, `scaffold_generality_tagged.md`)
- The tagged selection organism run in all four presentation(quoted/bare) × wording(copy/directed) renderings (head "Here are three words (A)(B)(C)" and copy bridge kept in every cell). **S is CI-clear 8/8 in all four**, both windows, J_NP/RESID_P/LOGITS (Holm p ≤ 1e-6): J_NP L51–59 S = quoted_copy +4.10, quoted_directed +6.66, bare_copy +4.19, bare_directed +6.24. Damage nil.
- **Selection is a property of relevance instructions, not the quoted-copy scaffold.** Presentation (quoted vs bare) barely affects S (main effect −0.17 L51–59, 2/8); directed wording gives **larger** S (main effect +2.30 L51–59, 8/8, pointed +8.58 vs +5.41) but does **not** suppress unpointed below control (Q>0), unlike copy wording (Q<0) — partly the different control tails ("occurs one time" vs "came up in conversation"); read the wording contrast on S, not Q/U.
- quoted_copy reproduces tagged_selection evaluate **bit-identically** (ratio 1.0): determinism confirmed; the quoted_copy cell is a faithful re-run, validating the cross-rendering comparison.
- Open within H1.7: the pure direct organism (no copy bridge) and single-word 2×2 (`single` stage) — the earlier direct pilot null is still unresolved there; native-vs-transferred fits (`directions` stage).

### 1.9 Selection localization (H1.10, evaluation scale, `selection_localization_{ptr_transplant,decomp,transfer}.md`)
- **Design fix (Amendment 1, before any forward).** The registered cross-arm source-token stage is withdrawn: the three source words precede the tag instruction, so in a causal decoder their states are arm-invariant (confirmed: pointed-A/B/C prompts are token-aligned, differ only at the tag token; source states bit-identical across arms). Free deduction: the selection is **not** a source-side tag written on the source tokens; it is applied at/after the instruction.
- **1A (sufficiency/depth; presence).** Transplanting the donor's instruction-region residual state ([tag token, end of user turn)) B→A / C→A restores R = +0.77 / +0.73 of the donor presence profile from block 36, decaying monotonically to ~0 by block 48; target-specific (B→A→B, C→A→C), 8/8, damage nil, A→A self-patch a no-op. ⇒ the pointer state lives in the instruction residuals, sufficient by block 36; the carrier reads it by ~block 48 (before the L51–59 readout).
- **1B (position; presence).** Corrected `region_split` (Amendment 3 — the earlier 'suffix' had included the user-side carrier): restoration is **tag +0.44, instruction-tail +0.09, user-carrier +0.036, delimiter-gap ~0** (L36, L51–59). The pointer is **tag-dominant and carried by the instruction tokens**; the user-side carrier and delimiters carry essentially none of it (refuting 'propagated into the passage'); full is superadditive over the parts (joint across instruction tokens).
- **1C (causal-transfer confirmation).** The transplant redirects the **causal transfer** profile (which source's block-36 replacement reaches the carrier), not just presence: restoration +0.74 (B→A) / +0.69 (C→A), target-specific, 8/8, damage nil. ⇒ localization is of the selection *mechanism*, not a readable correlate (the concern that motivated freezing this, cf. ĝ).
- **Open:** read-site component (attention vs GatedDeltaNet vs MLP) — Step 2 (`component`), not built.

### 1.10 Computed sums (H1.8, evaluation scale, `computed_sums_{natural,transfer}.md`)
- Competence gate **16/16** (the model computes every sum). Sum-word instrument validated at L51–59 (maintain−absent +0.69, 8/8).
- **Computed-output sensitivity.** A different-sum donor moves the sum readout (C_diff^sum +1.90 [+1.56, +2.24], 8/8; LOGITS +3.32); a same-sum sibling (different addends, **same value**) leaves the sum readout **invariant** (C_same^sum −0.006, equivalent to 0 within the pre-registered ±20% band) while moving the addend readout (C_same^add +0.54, 8/8). Damage nil. ⇒ the transferred content includes the model's **computed sum** — a latent that is never a token — not merely its addends. Instruction modulates it: A(C_diff^sum) = maintain−control +2.01 (8/8).
- Scope: does not decide whether the sum *travels* or is *recomputed* downstream; 8 specific arithmetic facts; RESID sum axis not fit (J_NP + LOGITS agree).

### 1.11 Early/late mapping (H1.9, transformation, evaluation scale, `early_late_mapping_run.md`)
- Competence 1.00 (early) / 0.99 (late). **Transformation (availability) established:** under the early usable codebook, X's own mapped letter F(X) is more readable during the carrier than its pair-partner's (source-conditioned E_F^sc +1.07 [+0.59, +1.55] L51–59, 25/32; +2.45 LOGITS, 32/32), and far more readable early than late (E_F +0.95 / +2.09, 32/32). ⇒ mapping availability **precomputes** F(X) during the carrier, source-conditioned to X (not generic codebook priming).
- **Not zero-sum:** X stays readable (s_X ~2.06 vs late 2.07); the length-matched usability control shows only a small mapping-specific X drop (E_X_usability −0.22, 9/32). The carrier carries **both** X and F(X).
- The Amendment-1 length-matched `early_unusable` control was load-bearing: the raw late−early X difference (+0.45, 31/32) is dominated by the generic long-prefix effect, stripped by the usability contrast. RESID letter axis not fit (J_NP + LOGITS agree).

## 2. What has NOT been done or established

- **H1.6** steering/cancellation β-grid on G, v_c, d_c: not started.
- **H1.7** instrument/scaffold generality: the direct organism has readout rows only (no interventions); the target-presentation × wording 2×2 on the tagged organism is **done** (§1.8: selection survives all four renderings; named-category rung done §1.7); the single-word 2×2, the pure direct organism (`single` stage), and native-vs-transferred fits (`directions` stage) remain; exemplar/inferred categories not run. Whether selection needs the quoted-and-introduced presentation or the copy bridge is untested.
- **H1.8** computed sums: **done (§1.10)** — computed-output sensitivity established (same-sum invariance, different-sum transfer).
- **H1.9** early vs late mapping: **done (§1.11)** — transformation (precomputation of F(X)) established, source-conditioned, additive (not zero-sum).
- **H1.10** localization: **Step 1 done (§1.9)** — the pointer state is in the instruction residuals, tag-anchored, blocks 36–48, causally confirmed. Step 2 (read-site component) not built.
- **H2** (pulse, erasure/recovery, state boundary, cache/recurrent transplants): not started. The hybrid cache serialization and the complete-prefix-state positive control are prerequisites.
- **H3** (consumer, boundary validation, representation ladder, route restriction, attacks): **started.** `consumer_competence` validated a codebook consumer at 1.00 greedy accuracy; `selection_to_behavior` (pilot 2 triples + evaluate 6 triples, audit-corrected v2) found an **internal-vs-behavioral dissociation** — the H1 instruction-region transplant reproduces the readout redirect (internal presence restore +0.759/+0.716 L51–59, transfer +0.726/+0.675, 6/6, same forwards) but moves the answer margin only ~0.19–0.25 of the clean separation (E_B +3.32, E_C +2.54, restore 0.249/0.191, 6/6), flipping the greedy decode in 2/36 cells (B→A) and 0/36 (C→A). Null under per-target norm-matched writes (randB/randC, ρ=1.0002). The route is unidentified (the transplant precedes the carrier; the visible instruction and source words remain in context). Two independent audits agree; the with/without-consumer z offset is verified length-driven (mask and execution path ruled out, equal-length control null; kernel mechanism provisional). `H3/results/selection_to_behavior.md`, `H3/results/audit_selection_to_behavior.md`, evidence_ledger row 14. Next: a consumer whose answer cannot be read off the visible prompt (computed sum, category members) to isolate the carrier route. Everything else above remains a readout at teacher-forced copy positions.
- Foreign-content (damage-only) donor control for source transfer: not run.
- Source transfer L_x sweep at evaluation scale: only L_x = 36 (inside the task-state run).
- J_CB / R_CB robustness subset: run for natural modulation only.
- Cross-model replication: none.

## 3. Open questions the results raise
1. What is the selection state, and where? — **localized (§1.9):** the pointer state is in the instruction-region residuals (tag-anchored, blocks 36–48), causally redirecting which source transfers. The read-site *component* (attention vs recurrent vs MLP) is the open Step 2.
2. Does selection survive the released wordings, bare presentation, and the direct organism (H1.7)? — **tagged organism: yes (§1.8)**, all four renderings; the pure direct organism (no copy bridge) is the open `single` stage.
3. Does it hold for categories, where the scored content is never a token in the prompt? — **partially answered (§1.7):** category-associated member *readability* transfers selectively; member *representation* not established.
4. Is any of this consumed downstream (H3)? A gain and a selection can make identical lens predictions and different behavioral ones.

## 4. Run inventory (forwards) and artifacts
| Run | Stage | Forwards | Raw arrays |
|---|---|---|---|
| instrument gates | — | ~10 | `common/configs/instrument_gates_result.json` |
| natural_modulation | pilot / evaluate | 168 / 648 | git / HF (322 MB) |
| source_transfer | pilot | 192 | git |
| task_state_modulation | fit / pilot / orthopanel / evaluate | 64 / 744 / 984 (+984 defective, kept) / 5,504 | HF |
| tagged_selection | pilot / evaluate | 1,536 / 3,840 | git / HF (264 MB) |
| competition_and_cue | evaluate | 1,952 | git (70 MB) + HF |
| tagged_categories | gate / select | 72 / 2,376 | git (gate 9.8 MB, resid 38 MB) / HF (raw_select 200 MB) |
| scaffold_generality | tagged | 6,144 | git (meta) / HF (raw_tagged 260 MB) |
| selection_localization | ptr_transplant / decomp / transfer / region_split | 768 / 720 / 1,104 / 1,104 | git |
| computed_sums | arithmetic / natural / transfer | 48 / 96 / 384 | git |
| early_late_mapping | run | 384 | git |
HF dataset: `senku21x/tcsif-outputs` (private). Git: `senku14x/ReadableHereUsedThere`, branch `main`.

## 5. Corrections and defects on record
- RMSNorm gain (`1+weight`) — float32 diagnostic in the natural-modulation pilot scaled ~½; corrected before any use.
- `orthopanel` run 1 saved no RESID_P projections (stage-name check in the loader); arrays kept as `raw_orthopanel_noresid_run1.npz`, unreported; stage re-run.
- Plain-sentence axis fitter matched the first substring ("king" in "asking"); fixed to the template slot before the evaluation run.
- Package 1 windows amended (L51–59 promoted to co-primary) before any Package 2 forward, with reasons recorded.
