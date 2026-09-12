# H1 · scaffold_generality — does selection (and the transfer phenotype) survive the released wording, bare presentation, and the direct organism?

**Spec sections 2.2 (direct organism), 2.3 (presentation × wording factorial), H1.7 (scaffold generality, native vs transferred fits).** Script `H1/scripts/scaffold_generality.py` (stages `single`, `tagged`, `directions`); analysis `scaffold_generality_analysis.py`; results `H1/results/scaffold_generality_<stage>.md`. Status: design, registered before any forward. Nothing run.

## 1. Why

Every causal result so far uses `Here is the word "X". Keep that word in mind while you copy…` or its tagged form. Two features of that scaffold could be doing the work: the quoted-and-introduced presentation, and the copy-task wording. The paper-style directed wording (`Hold X in mind as you write` / `X came up in conversation`) and the direct organism (no copy bridge) have only readout rows (focus > mention +0.85, 30/32 at evaluation; null in the 8-word pilot on D0/D3 — unresolved). The question: is selection a property of the tagged copy scaffold or of relevance instructions generally?

## 2. Stages and organisms

**Stage `single` — 2×2 presentation × wording on the single-word organism with source replacement.** Bodies exactly as `rendering.PRESENTATION_BODIES` (the presentation × wording factorial): quoted/bare × copy/directed × maintain/mention, each `+ ":\n\n{carrier}"`. Materials: the 16 evaluation pairs (X, Y = pair partner as donor), carriers C2, C3. Bare presentation: the source span is the unquoted word token(s); donor geometry asserted. Interventions: source replaced from block 36 by the partner under both arms. Endpoints: natural Δs = s_J(maintain) − s_J(mention); transfer C_M, C_N; A = C_M − C_N. Cluster = unordered pair (n = 16; pooled, with each bank shown). **Plus the pure direct organism**: `Hold {X} in mind as you write.` vs `{X} came up in conversation.` with the carrier only in the assistant turn (`carrier_in_user=False`), carriers D11, D14, D16, D19, source replaced from block 36 (span = the X token). Also the two held-out phrasings per family (`keep`; `appears`, `reference`, `phrase`) as a declared held-out set, readout + replacement.

**Stage `tagged` — 2×2 on the tagged organism with S as endpoint.** Four renderings of the tagged prompt for the 8 evaluation triples, 3 rotations, C2/C3, arms {A, B, C, ctrl}, each source replaced from block 36 (partner-triple donor as in `tagged_selection.py`):
- quoted × copy: the existing prompt (re-run inside this battery so all four cells share one run; the earlier evaluate run is the replication reference).
- quoted × directed: `Here are three words: (A) "{X1}", (B) "{X2}", (C) "{X3}". Hold the word tagged {T} in mind as you write. Now copy the following text exactly, word for word:` ; control `… Those words came up in conversation. Now copy the following text exactly, word for word:`.
- bare × copy: `Here are three words: (A) {X1}, (B) {X2}, (C) {X3}. Keep the word tagged {T} in mind while you copy …` ; control `… Those words occur one time. Now copy …`.
- bare × directed: `Here are three words: (A) {X1}, (B) {X2}, (C) {X3}. Hold the word tagged {T} in mind as you write. Now copy …` ; control `… Those words came up in conversation. Now copy …`.
The "Here are three words" head is kept in all four so the tag mechanism exists in every cell; presentation and wording are the only factors. (The pure direct organism has no tags and therefore no S; it is scoped to Stage `single`.)

**Stage `directions` — native vs transferred.** From each tagged rendering's clean runs fit d_shared^rendering (pointed − control at block 35, identities balanced). Moves (StateMove, clean-derived α_t, pointed → control level) crossed with the three replacements: (a) native direction in its own rendering (diagonal, 4 cells), (b) the quoted×copy word-fit direction (`tagged_selection/fits_evaluate.npz`) in the other three renderings (transfer row). Cosines between the four native directions and ĝ reported as descriptive geometry. The full 4×4 matrix is optional; the diagonal + one transfer row is the registered set.

## 3. Materials rules

Evaluation banks and carriers as in Package 1/2 and tagged evaluate; nothing new. Bare words must be single tokens without quotes in context (assert; a failure is logged and the pair/triple flagged, not replaced). Direct carriers D11–D19 from `materials.DIRECT_CARRIERS`. Decoys `FIT_WORDS[:8]`.

## 4. Estimands and statistics

Single: Δs, C_M, C_N, A per cell of the 2×2 and for the direct organism; interaction contrasts: presentation main effect on A, wording main effect on A, interaction. Tagged: S, Q, U, S_nat per rendering; presentation and wording main effects on S; the quoted×copy cell vs the earlier evaluate run as a replication check (ratio with CI). Directions: profile index P per rendering, native vs transferred ratio. Cluster = pair (single), triple (tagged), n = 16 / 8; both windows, Holm.

## 5. Predictions before the run

| Outcome | Reading |
|---|---|
| S CI-clear (8/8 or 7/8) in all four renderings, Q ≤ 0 | Selection is a property of relevance instructions on this model, not of the copy scaffold. Strongest H1 scope result. |
| S clear under copy wording only | Selection depends on the copy-task framing; the paper-style directed wording does not select at this readout. |
| S clear under quoted presentation only | Selection needs the quoted-and-introduced presentation; bare words are not treated as sources. |
| Direct organism: A > 0 (C_M > C_N, ≥ 12/16) | The paper-style prompt shares the causal transfer phenotype; readout and transfer agree. |
| Direct organism: Δs > 0 but A ≈ 0 | Directed wording changes readability without changing source sensitivity: a readout-side effect. |
| Direct pilot-null re-appears on D11/D14 | The earlier discrepancy is carrier-bound; report per carrier. |
| Native directions work everywhere, transferred only in quoted×copy | Regime-specific handle (H1.7 branch). |

## 6. Decision rules

- Any rendering with S ≈ 0 (equivalence band ±20 % of its U, 90 % CI) is a scope limit: state it, do not tune the prompt. If U is also ≈ 0 there, the instruction has no transfer effect in that rendering and S is uninterpretable (say so).
- A main effect of wording or presentation on S is reported with its CI; do not interpret an interaction if either main effect's CI includes zero.
- If the quoted×copy replication ratio to the evaluate run is outside [0.6, 1.4], stop and investigate determinism (compare cell-level `z` on identical prompts) before reading the other cells.
- Directions stage runs only for renderings where S is CI-clear.

## 7. Budget

Single: 16 pairs × 2 words × 4 bodies × 2 arms × 2 carriers × (clean + donor + swap + same-source) ≈ 2,048; direct: 32 words × 2 phrasings (+4 held-out) × 4 carriers × 4 ≈ 1,024 + 2,048; ≈ 5,000 forwards. Tagged: 4 renderings × 8 triples × 3 rotations × 2 carriers × 4 arms × 8 (clean, same-source, 3 donors, 3 swaps) = 6,144. Directions: 4 native + 3 transfer cells × 8 × 3 × 2 × 3 arms × 4 ≈ 4,000. Run the tagged stage first (it is the discriminating one), then single, then directions.

## 8. Not claimed

Nothing about behavior; nothing about categories; nothing about localization. "Selection survives rendering r" is scoped to the tagged head plus rendering r.
