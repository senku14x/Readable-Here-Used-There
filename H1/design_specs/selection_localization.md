# H1 · selection_localization — where is the pointed source's relevance applied: on the source tokens, or at the carrier-side read?

**H1.10 (localize only a reproducible causal contrast).** The contrast: selectivity S on the tagged organism (8/8, evaluation scale) and the mid-carrier switch (8/8 at L ≥ 51). Script `H1/scripts/selection_localization.py` (stages `ptr_transplant`, `decomp`, `transfer`, `component`; see the stage-name map at the end — original `crossarm` withdrawn per Amendment 1); analysis `selection_localization_analysis.py`. Status: design, registered before any forward.

## 1. Two accounts to separate

- **Source-side tag.** The instruction writes relevance into the pointed source's own token states before block 36 (the source span's residuals carry "I am the pointed one"). The carrier reads all sources alike; the tagged one is louder.
- **Carrier-side read.** The source states are arm-independent (or nearly); relevance lives in the carrier positions' queries/recurrent state, which fetch the pointed source preferentially at the full-attention blocks.

Everything so far is compatible with both because donors were always rendered under the *same* arm as the recipient.

## 2. Stage `crossarm` (Step 0, cheapest and sharpest)

Materials: the 8 evaluation triples, 3 rotations, C2/C3 (as `tagged_selection` evaluate). Recipient run: pointed arm T. For source j, donors rendered under (i) the same pointed arm T (baseline, = evaluate), (ii) the **control arm**, (iii) a **different pointed arm** T' ≠ T (pointer on another slot), (iv) pointed arm T with donor identity = recipient identity (same-source under a different arm: isolates the arm's imprint on the source states with identity fixed — H1.10 "patch same-identity maintain/control instruction-derived state while holding source identity fixed"). Replacement from block 36 as before; geometry identical by construction (same prompt length across arms? **No** — arms differ in tail wording, so token counts differ; the span indices of the sources are identical because the head precedes the tail, and only the span is written; assert span equality and that positions < span end are identical across arms). Readouts as in `tagged_selection.py`.

Endpoints: C_j^{same}, C_j^{ctrl-donor}, C_j^{T'-donor} for the pointed slot and the unpointed slots; the same-identity cross-arm row gives ΔS_imprint = change in the pointed source's readability when its own states come from the control arm.

| Outcome | Reading |
|---|---|
| Pointed-slot C falls to the unpointed level with a control-arm donor (ratio ≤ 0.3) and the same-identity control-arm row lowers the pointed word's readability | Relevance is written on the source tokens before block 36 (source-side tag). |
| Pointed-slot C unchanged with a control-arm donor (ratio ≥ 0.7) | Relevance is applied at the read; the source states are interchangeable across arms (carrier-side). |
| Intermediate | Both; report the ratio and proceed with both stages below. |

Cluster = triple (n = 8), both windows, Holm. Budget: 8 × 3 × 2 × 3 pointed arms × (3 slots × 3 extra donors + 3 same-identity rows) × 2 ≈ 1,700 forwards.

## 3. Stage `lx_sweep` (bounding where the read happens)

S as a function of the replacement start L_x ∈ {23, 27, 31, 35, 36, 39, 43, 47, 51, 55} on 4 of the 8 triples (fixed: T0, T2, T4, T6), rotations 0–2, C2/C3, pointed arms, all three slots. S(L_x) rising from 0 as L_x decreases bounds the first block at which the pointed source is read into the carrier; the late window's flatness in Package 1 predicts S(L_x) ≈ constant for L_x ≤ 44 at L51–59 and a drop for L_x > 47. Also the *end-bounded* variant: replace only on blocks [36, L_end] for L_end ∈ {39, 43, 47, 51, 55, 59}; the smallest L_end giving ≥ 80 % of full S bounds the last read. Budget ≈ 4 × 3 × 2 × 3 × 3 × 16 ≈ 3,500.

## 4. Stage `component` (only if Stage 2 or the sweep gives a target)

At the full-attention blocks in the bounded range (indices i with i % 4 == 3: 39, 43, 47, 51, 55, 59; check `registry.full_attention_layers(model)`), patch **one component's output at carrier positions** from a donor run into the recipient run, with sources fixed:
- attention sublayer output (`self_attn` output before the residual add) at interior positions, from the pointed-B run into the pointed-A run of the same triple/rotation/carrier: does the C profile move toward B (C_B up, C_A down)? Matched control: the same patch from a second pointed-A run rendered with a different carrier position offset is not possible (determinism), so the matched control is the patch from the **control-arm** run (no pointer): it should move both down, not redistribute.
- the GatedDeltaNet block outputs at the same positions for the neighbouring linear-attention blocks, as the alternative path.
- MLP outputs at the same blocks (should not redistribute if the read is attentional).
Before hooking, print `model.model.layers[i]` for one full-attention and one linear-attention index and record the module names in the report; hooks must target the sublayer output, not the block output. Verify with a same-run self-patch (bitwise equality).
Endpoint: fraction of the A→B natural profile difference (from the clean pointed-A vs pointed-B runs) restored by each component patch; cluster = triple (n = 8); one block at a time, then the union of the full-attention blocks ≥ 51.

| Outcome | Reading |
|---|---|
| Attention-output patch at blocks ≥ 51 restores ≥ 50 % of the A→B profile, control-arm patch does not redistribute | The read is attentional at the late full-attention blocks; a candidate site for H2/H3 interventions. |
| Only the union of all components restores | Distributed; report and stop localizing (stopping point). |
| Nothing restores while the block-output restoration does | The relevant state is upstream of every sublayer tested at those blocks (source-side, or earlier blocks); return to Stage 2's answer. |

## 5. Decision rules and stopping point

- Run `crossarm` first; its answer decides whether `component` targets the carrier side (patch at carrier positions) or the source side (patch the source span's pre-36 states across arms — already done as the same-identity row).
- Do not localize below 50 % restoration with a matched control; report the ceiling and stop. Localization is not required for the H1 verdict; it is the bridge to H2/H3.
- Restoring whole block outputs at a cut is a reference, not a localization .

## 6. Not claimed

No mechanism beyond "which component at which blocks moves the profile under these patches"; no head-level claims; nothing about behavior.

---

## Amendment 1 (2026-09-07, before any forward) — withdraw Stage `crossarm`; promote the pointer-state transplant

**Withdrawn: Stage `crossarm` (§2).** It is a predetermined no-op. The source words occur in the prompt *before* the tag instruction ("Keep the word tagged {T}"), and the head "Here are three words: (A)(B)(C)" is arm-invariant. Empirically (tokenizer check, this session): arms A and B first diverge at the tag token (index 30, `ĠA` vs `ĠB`); all three source words are in the arm-identical prefix. In a causal decoder every source-position state at every layer depends only on positions ≤ itself (full-attention masking and the GatedDeltaNet left-to-right recurrence alike), so the source-token states are **bit-identical across arms**. Every donor-arm variant in §2 installs the same arm-invariant source states; C_j^{same} = C_j^{ctrl-donor} = C_j^{T'-donor} exactly, and ΔS_imprint = 0 by construction. The stage would only re-derive an architectural fact.

**Free deduction (recorded, no forward):** the selection is **not** a source-side tag written into the source-token residuals. It is applied at/after the instruction — in the instruction/tag-token states and/or the carrier-side read. The §1 "source-side tag" account is architecturally excluded, not merely disfavoured.

**Revised stage order and content.**
1. **`component` (primary).** Recipient = pointed arm A; donor = pointed arm B; same triple, rotation, carrier, lexical sources (no source swap here — this localizes the *pointer* state, not the source read). The natural clean pointed-A vs pointed-B runs give the profile ceiling (A: C_A high / C_B low; B: reversed). Patch B→A, one locus at a time, and measure the fraction of the A→B profile difference restored:
   - (a) **instruction/tag-token states** (the tag span, geometry-matched: "tagged A" vs "tagged B" are both single tokens) at blocks in the bounded range — does moving the instruction state alone redistribute the profile?
   - (b) **full-attention sublayer output** at interior carrier positions (blocks i%4==3 in the bounded range; verify names via `registry.full_attention_layers`), the read-time attentional path;
   - (c) **GatedDeltaNet block output** at the same carrier positions (the recurrent path);
   - (d) **MLP output** at the same blocks (should not redistribute if the read is attentional).
   Matched control: the **control-arm** patch (no pointer) at each locus — should lower both C_A and C_B, not redistribute. Self-patch bitwise-equality gate. Cluster = triple (n=8), both windows, Holm. This is the project's original §4 `component` stage, extended with locus (a) per the review.
2. **`lx_sweep` (supporting, §3 unchanged).** Bounds which blocks read the *source content* into the carrier (a different sub-question from the pointer localization); keep as a secondary bound if the component stage needs a block range.

**Decision rule.** Attention-output patch (b) at the late full-attention blocks restoring ≥50% of the A→B profile with the control-arm patch not redistributing → the read is attentional at those blocks (candidate H2/H3 site). Instruction-state patch (a) alone restoring the profile → the pointer state is carried by the instruction tokens and read by the carrier. Only the union restoring → distributed; report the ceiling and stop (the gate contract). Below 50% with a matched control → do not localize; report the ceiling.

## Amendment 2 (2026-09-07, before any forward) — freeze the endpoint, controls, and staged decision tree

Refinements adopted before outcomes (from external review):

**Endpoint = profile-restoration fraction, natural presence as screen, causal transfer as confirmation.** Clean carrier presence profiles p_A=(s_A,s_B,s_C | pointed A), p_B, p_C (s_j = z_{word_j} − mean decoys at the carrier interior). After a donor→A transplant at boundary L, R_L = (p_{D→A,L} − p_A)·(p_D − p_A)/‖p_D − p_A‖². R=0 stays A-like, R=1 reaches the clean donor profile, <0 opposite, >1 overshoot. **Always report the three raw components beside R.** Natural presence is the *screen*; at the 1–2 boundaries with substantial R, a *confirmation* step reruns the transplant crossed with A/B source replacements and checks that causal transfer S is also redirected — because readable-state and source-transfer effects need not share a causal interpretation (cf. ĝ). This is frozen in the tree, not optional.

**Sufficiency, not "where read."** A sustained block-≥L suffix patch tests only whether pointer-dependent instruction-region residual state is *sufficient* to redirect the later carrier profile, and bounds the depth by which such sufficient state is available. It does not show where the carrier reads/applies the pointer (hook semantics: overwriting block-L outputs at instruction positions influences carrier positions only through subsequent blocks). "Where it is read/applied" is Step 2 (component).

**Controls = donor target-specificity, not the control arm.** The control-arm prompt is not token-aligned to the pointed arms (different wording/length), so control→A changes more than pointer identity — descriptive only. The load-bearing specificity control is: A→A self-patch (bitwise no-op gate); B→A redirects toward B; C→A redirects toward C. Comparable target-specific restoration (B→A→B-like, C→A→C-like) is far stronger than "a control lowers both." A norm-matched random B−A delta may be added later if needed.

**Staged decision tree.**
- **1A — full instruction-region sweep.** B→A and C→A, patch positions [tag token, end of user turn) at blocks ≥ L, L ∈ {36,40,44,48,51,55}. Endpoint R_L + raw A/B/C readouts, both windows. A→A self-patch no-op gate. Identify the earliest/highest-depth boundary retaining most of the effect.
- **1B — spatial decomposition** at the informative boundary: tag-only vs post-tag suffix vs full region → is the pointer locally at the tag state, propagated into the suffix, or distributed?
- **1C — causal-transfer confirmation** at 1–2 boundaries chosen without looking at transfer outcomes: cross the transplant with A/B source replacements, verify transfer S is redirected.
- **Step 2 — component** (attention vs GatedDeltaNet vs MLP at carrier positions), presence ceiling + transfer as load-bearing, only after 1A–1C bound the depth.

**Stage names (script ↔ this spec, after Amendments 1–2).** `smoke` (tokenizer-only render/geometry check) · `ptr_transplant` = Step **1A** (full instruction-region B→A/C→A sweep) · `decomp` = Step **1B** (tag-only vs suffix vs full at the informative boundary) · `transfer` = Step **1C** (causal-transfer confirmation) · `component` = **Step 2** (attention vs GatedDeltaNet vs MLP read-site; not yet built). The original `crossarm` stage is withdrawn (Amendment 1); `lx_sweep` (the project conventions, source-read depth) remains available but is secondary and not yet run. `H1/scripts/selection_localization.py` and its docstring carry the same mapping.

## Amendment 3 (2026-09-07, after 1A/1B ran) — the patched "instruction region" also contained the user-side carrier; correct the claim and split it

**Error found (external review, verified).** In `ptr_transplant`/`decomp` the patched span was `instr = range(tag_pos, carrier_start)` where `carrier_start` is the **assistant** carrier start. In the copy organism the carrier is repeated *inside the user turn*, so this span = tag (1) + instruction tail (~15) + **user-side carrier (~16)** + template/delimiter tokens (~9) = ~41 tokens, not just the instruction. Verified by decoding the span.

**Corrected claims.** 1A/1B localize the pointer to the **post-tag prefix**, not specifically the instruction residuals. What survives cleanly: (i) the source-side-tag account is architecturally excluded (Amendment 1); (ii) the **tag-token-only** residual carries causally-effective, target-specific pointer information by block 36 (1B tag-only: +0.44 B→A / +0.48 C→A) — a genuine downstream (non-source) pointer state; (iii) the broader post-tag prefix transplant redirects both natural presence (1A) and **causal source transfer** (1C) by ~0.7–0.75, target-specific. The "suffix" of 1B conflated instruction tail + user carrier + template, so "distributed across the instruction residuals" is **not** established. "roughly additive" holds only at L36 (superadditive at L44 → distributed/joint). Depth: "causal dependence on the patched post-tag prefix is largely exhausted before block 48"; Step 2 earns "read".

**Corrected Step 1B (`region_split`).** Split the post-tag prefix into four disjoint pieces using `spans["user_carrier"]`: **tag** [tp], **instr_tail** [tp+1, user_carrier_start), **user_carrier** [user_carrier_start, user_carrier_end), **gap** [user_carrier_end, assistant_carrier_start), plus **full** as the ceiling. Patch each B→A/C→A at L36 (and L44); presence restoration R. Outcome map: tag+instr_tail ≈ full → genuine instruction-state localization; user_carrier a large fraction → the pointer is propagated into the passage representation before the assistant turn; gap matters → aggregation at delimiter/control tokens (cf. workspace/interpretative-token observations); only combinations → distributed prefix state. Then rerun 1C causal transfer on whichever restricted region carries the effect.

## Amendment 4 (2026-09-07, before any forward) — norm-matched non-specific controls for the instruction-region transplant

**Why.** Steps 1A–1C measure restoration R as the projection of (p_{D→A} − p_A) onto the clean A→D axis. That axis has a large negative s_A component and a large positive s_D component, so any perturbation that merely *degrades* the A-pointer (s_A down, s_B and s_C up together) projects positively onto it. Target specificity (B→A moves B, C→A moves C, off-target ≈ 0) argues against a purely generic account, but it does not bound how much of R = 0.74–0.77 is a nonspecific "deselection" component. The earlier pilot's practice (equal-dose random and structured controls beside every transplant) supplies the missing bound cheaply.

**Stage `random_control`** (boundary L36, full instruction region [tag, end of user turn), the 8 evaluation triples × 3 rotations × C2/C3, cluster = triple):
- `cleanA/B/C`, `BtoA`, `CtoA` re-run inside this stage (same renderings; determinism makes them a within-run anchor).
- `randD_s{0,1}` (D ∈ {B, C}): h_A + δ with δ at each (layer ≥ 36, region position) an isotropic Gaussian direction scaled to ‖h_D − h_A‖ at that (layer, position). Norm-matched per cell, no donor content. Two seeds.
- `shuffD` (D ∈ {B, C}): h_A + Π(h_D − h_A), the donor delta with region positions permuted (seeded). Same per-position delta *set*, broken position binding.
- `flipD`: h_A − (h_D − h_A). The donor delta reversed.
Endpoints: R along the A→D axis for every condition (for `rand`/`shuff`/`flip` with D's norm, along A→D); raw Δ(s_A, s_B, s_C); a deselection index Δs_A versus mean(Δs_B, Δs_C); damage (ΔNLL, top-1 retention). Windows L48–50 and L51–59.

**Predictions.** Donor-specific pointer content: R(rand) ≈ 0 with |R| < 0.15, R(flip) < 0, R(shuff) substantially below R(DtoA) (position binding matters) or ≈ R(DtoA) (content is position-free within the region). Nonspecific deselection share: R(rand) > 0 with Δs_A negative and Δs_B ≈ Δs_C positive; the licensed restoration is then R(DtoA) − R(rand). Damage above the bound voids the row.

Budget: 48 cells × 13 forwards ≈ 624 forwards. Report: `H1/results/selection_localization_random_control.md`.
