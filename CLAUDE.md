# CLAUDE.md — Readable Here, Used There (TCSIF)

Project guide for any session working in this repository.

## Session start — read in this order, before touching anything

1. **The workspace paper first.** `context/paper/workspace_paper_notes.md` and `context/paper/workspace_paper_notes_addendum.md` (method, functional and structural claims, the causal case studies, the external commentary by Dehaene & Naccache, Eleos and Nanda). When a detail matters, go to the original: `/workspace/papers/2607.15495v1.pdf` (main + appendix) and `/workspace/papers/neel review!.pdf` (the commentary bundle); full extracted text is in `/workspace/notes/extracted/` if it survived the last recycle. Do not rely on memory of the paper for a number or a section reference.
2. **Then the design specs** (`H1/design_specs/`, `H3/design_specs/`): each experiment's materials, estimands, intervention contracts and decision rules, registered before its forwards. `context/project_understanding.md` is the short orientation on how the experiments discriminate the hypotheses.
3. **Then where things stand:** this file's "Where things stand", `STATUS.md`, and `context/evidence_ledger.md` / `context/h1_stopping_point.md` for the H1 verdicts.

**Skills.** Use the user-level Claude skills for deliverables: `iclr-plots` for every figure intended for a paper, submission or slides (Times, 5.5 in single column, 9 pt captions); `paper-writing` for drafting or editing any report section, abstract or write-up; `mech-interp-collaborator` is the standing research-collaborator stance (calibrated claims, confound hunting) and applies throughout. During long runs (downloads, batteries) launch in the background and stay idle; no subagents.

## What this project is

An empirical mechanistic-interpretability study on **Qwen3.6-27B** (revision `6a9e13bd…`, bf16, eager attention, thinking disabled) using the Jacobian lens. Three hypotheses organise it — H1 task-conditioned selection/transformation, H2 maintenance/reconstruction, H3 downstream use — and every experiment has a design spec with exact prompts, measurements, intervention contracts and decision rules, registered before its forwards; scientifically motivated deviations are recorded as dated amendments in the relevant `design_specs/*.md` before they run.


## Layout

```
context/                          project understanding, detailed status, h1_stopping_point, evidence_ledger
common/scripts/                   registry (model/lens pins, hashes), materials (Appendix A–C), rendering (prompts + span gates),
                                  readout (lens z, n, r; ranks; folded directions), hooks (SpanWriter, StateMove, AddVector,
                                  EraseToReference, realized-write stats), stats (cluster-t, ratios, Holm), instrument_gates
common/configs/                   instrument_registry.json (hashes, layer maps), instrument_gates_result.json
H1|H2|H3/scripts/                 <experiment>.py (battery, stages) + <experiment>_analysis.py (single scoring pass)
H1|H2|H3/design_specs/            one design doc per experiment; package1_decisions.md holds frozen calibration choices
H1|H2|H3/outputs/                 raw_<stage>.npz, meta_<stage>.json, manifest_<stage>.json, fits, freeze notes
H1|H2|H3/results/                 <experiment>_<stage>.md reports, *_tables.json, figures/, qualitative/
STATUS.md                         short current status; context/project_status_*.md is the detailed one
```

Experiment names are scientific (`natural_modulation`, `source_transfer`, `task_state_modulation`, `tagged_selection`), stages are `pilot` / `orthopanel` / `evaluate`, run IDs are timestamps in the manifests. No `v2_final_fixed` names.

## Second model (pure-attention control)

`TCSIF_MODEL=qwen3_32b` switches `registry.py` to `common/configs/instrument_registry_qwen3_32b.json` and redirects every battery and analysis script to `replication_qwen3_32b/`. Qwen3-32B is a dense transformer with the same depth and width as the primary model, so sites, hooks and materials transfer; its lens is a partial fit (n=80) finalised locally. Plan, predictions and results: `replication_qwen3_32b/{README,RESULTS}.md`. Portability lessons recorded there: donor maps must be re-derived per tokenizer, category words are multi-token under this tokenizer, dense models have no `layer_types` field, and the RMSNorm gain is `weight` not `1+weight`.

## Environment (Vast.ai; `/workspace` is NOT persistent)

```
source /venv/main/bin/activate
export HF_HOME=/workspace/.hf_home PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
# rebuild if needed: uv pip install transformers==5.15.0 safetensors accelerate scipy matplotlib
#   git clone anthropics/jacobian-lens && git checkout 581d398 && uv pip install -e . --no-deps
# After a recycle, download ALL FOUR lens files, not just J_NP: J_CB and R_CB (camilablank/workspace-lenses) are
# needed by natural_modulation and by H3/trying_to_fool, and a missing file surfaces only as an assert deep in a battery.
```
- Model + lenses (61 GB) under `/workspace/.hf_home`; registry `common/configs/instrument_registry.json` pins hashes (J_NP `1718c8c5…`, J_CB `a036b358…`, R_CB `fe4d0b6a…`).
- One RTX PRO 6000 (96 GB). The model uses 54 GB; run batteries sequentially. ≈0.3 s/forward with all-layer recording.
- Instance paths (2026-09-24): the clone is `/workspace/Readable-Here-Used-There` with `/workspace/tcsif` a symlink to it; the commentary PDF is not on the instance (its text is on the HF mirror); the committed `instrument_gates_result.json` (2026-09-06) predates the RMSNorm-gain fix for `z32_vs_impl` (2.74 there vs 0.019 now) — everything else reproduces to 1e-3 on a rebuilt environment.
- GitHub: the image's `GITHUB_TOKEN` is invalid and shadows the `gh` login. Push with
  `env -u GITHUB_TOKEN git -c credential.helper='!gh auth git-credential' push origin main`.
- Commits: author `senku14x <visheshgupta14x@gmail.com>`, Claude co-author trailer + session link.
- Arrays > 100 MB are gitignored and mirrored to the private HF dataset **`senku21x/tcsif-outputs`** (same relative paths). Everything else is committed.
- Do not use subagents (researcher's instruction: they burn usage limits).

## Instruments (registry names)

| Name | Key | What |
|---|---|---|
| J_NP | np | Neuronpedia Jacobian lens (primary). Score = model's own path: `final_norm(J_l h) @ W_U^T` in bf16. |
| RESID_P | s_p | Plain-sentence residual axis (Appendix C templates 1–8 fit, 9–12 validate), refit per run; presence = one-vs-decoy-centroid direction with centering constant; pairs = unit(μ_Y − μ_X). |
| LOGITS | z_out | Model output log-prob margins at interior/consumer positions. |
| J_CB / R_CB | cbj / cbr | Camila Blank lenses, robustness subset only. |

Conventions that must not drift: block-output indexing (hooks write block outputs); interior carrier positions = assistant carrier span trimmed 2 each end; readout windows **L48–50 and L51–59 co-primary** (Holm across the two); source replacement start **L_x = 36**; state site **block 35**; decoys = the 8 spec decoys (`drawer` excluded when D5 is in play); cluster = word / unordered pair / triple; cluster-t intervals with sign counts and per-cluster values; ratios always with numerator and denominator.

## Non-negotiables (all earned in this project)

1. Gates before outcomes: rendering span gates, same-source ≡ clean bitwise, layers < L_x identical between futures, realized write ρ ∈ [0.9, 1.1] and κ ≥ 0.99, damage (top-1 retention ≥ 0.95, ΔNLL). A failed gate is repaired and re-run; nothing scored is deleted.
2. Freeze before evaluation: materials rules, sites, windows, panels and tolerances are written to `design_specs/` or an `evaluation_freeze.json` before any evaluation forward. Pilots use calibration words + C0/C1; evaluation uses the bank words + C2/C3.
3. Every report has: setup, main findings with intervals and sign counts, complete tables (all conditions, controls, both windows, all instruments), verification/limitations, interpretation, next decision. Negatives stay in the report.
4. Wording: "readability" or "transfer to the readout", never "the model represents/uses"; "surfaced" only with a rank; ĝ is "a readout gain", not "a task state" or "controller"; selection claims are scoped to the tagged organism, this rendering, this readout.
5. Record every silly mistake in the commit message and the report (there have been three: RMSNorm gain is `1+weight`; a stage-name check dropped RESID_P from a run; the axis fitter matched "king" in "asking").
6. Different instruments on the same forwards are robustness, not independent samples.

## Where things stand (2026-09-09)

**H1 is at its stopping point.** The eight separate verdicts are in `context/h1_stopping_point.md`; the consolidated evidence matrix is `context/evidence_ledger.md`; full numbers in `context/project_status_2026-09-07.md §1`.

Experiments run: natural_modulation, source_transfer, task_state_modulation (**ĝ is a readout gain that does not redirect selection; not identified as a controller**), tagged_selection (**the discriminating selection result**), competition_and_cue, tagged_categories (selection reaches category-associated members; extension scale), scaffold_generality/tagged (selection survives quoted/bare × copy/directed, **within the copy-bridge organism**), selection_localization (1A/1B/1C + region_split: the pointer state is in the **instruction residuals, tag-dominant, and causally redirects which source transfers**), computed_sums (the **computed value** transfers), early_late_mapping (**precomputation of F(X)**, additive). One-line headline: a real, source-causal, instruction-modulated **selection** phenotype that is a *gain* not a specific-state controller, localized to the instruction residuals and causally controlling which source transfers, generalizing across wording / categories / computed values; plus a **transformation** (precomputation) phenotype. Everything in H1 is a **readout**; H2 (maintenance) is not established.

**H3 is the live hypothesis and its canonical one-paragraph claim is the block at the top of `STATUS.md`.** Do not restate it from any single report; the reports contain superseded wording, and `H3/results/computed_sum_consumer.md` §12 plus `context/evidence_ledger.md` §E hold the claims table with explicit withdrawals. Two external audits were accepted in full on 2026-09-09 and their corrections are applied throughout; the clamp-control weaknesses recorded then were repaired and closed by `H3/results/query_local_workspace_clampfix.md`; `STATUS.md` lists the two that remain (bf16 write fidelity on small clamps, attention mask not a complete cut).


**H3 update (2026-09-09, end of day).** Two registered runs closed the day: **`query_local_workspace` `clampfix`** (Amendment 3 repairs) — norm-matched orthogonal clamps are inert, the "≈ 40 % of the report margin is drawn on the reconstructed sum at the question tokens, parity is insensitive to that plane" statement is licensed again; and it exposed that **every coordinate-level write (`CoordClamp`/`CoordSwap`) is partial in bf16** (ρ ≈ 0.5–0.6, κ ≈ 0.4–0.5 for writes of norm 0.2–0.5; ρ ≈ 0.8 at norm 2–5), recorded as STATUS.md weakness 1 — cite no clamp or swap row without it. **`two_hop_organism` `bridgeswap`** (Amendment 4) — the paper's own intermediate coordinate swap works on this organism (0.41 of the full-residual ceiling on the sequence endpoint, 12/12 items, decoy swap inert; 0.38 on the dense model) and, split by position, the question turn carries half of it, the clue span a quarter, the copied carrier a sixth, while the carrier swap installs the swapped intermediate at the carrier readout as strongly as the whole swap; the answer-word swap is larger at every position set (Nanda's observation on this model). Reports `H3/results/{two_hop_bridgeswap,query_local_workspace_clampfix}.md`, figure `h3_bridgeswap`. Earlier the same day: `computed_sum_consumer` transport dissociation (report §10) is now backed by the registered Amendment 2 battery (`computed_sum_consumer_robust.md`, stage `robust`): four carriers, two donor maps, full-depth carrier donor, necessity complement (operand donor with carrier clamped), matched random, RESID_P number axis + LOGITS beside J_NP, answer-position distance. Every prediction held (row 3 in between its thresholds: the consumer registers the carrier change at 0.14–0.22 of the operand change). The word organism has the matched carrier-only stage (`selection_to_behavior_carrier_only.md`: ≤ 0.04 of ceiling, 0/36). Wording: "the carrier copy is weakly consulted and not acted on while the source is visible"; not "unused" in general. Both new stages have committed analysis scripts (`computed_sum_consumer_analysis.py`, `selection_to_behavior_carrier_analysis.py`). **Amendment 3 (`global` stage, 2026-09-09)** ran the token-level operand control, the consistent global clamp, the paper-style coordinate swap (global vs carrier-only), the decision-position donor and a first attention-mask route restriction; results in `computed_sum_consumer_global.md` and `computed_sum_consumer.md` §13. After an external critique the same day, a current-claims table with explicit withdrawals lives in `computed_sum_consumer.md` §12 and `context/evidence_ledger.md` §E — read it before quoting any earlier H3 section.

Deferred (not verdict-changing): steering_decomposition (H1.6), localization Step 2 (read-site component), scaffold_generality/single (pure direct organism). **Load-bearing next (researcher decision 2026-09-09: no circuit localization for now; make the dissociation robust and general).** (1) and (2) below are DONE (Amendment 3). **`query_local_workspace` (2026-09-09, own design spec + 2 amendments) is DONE**: reconstruction of the sum at the question positions without the carrier copy; function-specific consumption (report ~40 % mediated, parity bypassed); question-site lens swap = answer-token steering; **absent-source transplant: the carrier copy is consumed when it is the only source (28/32)**. Read its interpretation section before quoting any H3 headline; the current one-paragraph statement is in `context/evidence_ledger.md` §E. Figures: `H3/results/figures/` (ICLR style, `common/scripts/make_figures.py`). **`two_hop_organism` (2026-09-09) is DONE** — pilot + full battery + no-clue stage on the workspace paper's own released `probe-swap.json` items (12 with a released length-matched donor clue): the sum organism's pattern reproduces on a factual latent, with the carrier copy carrying 0.27 of the answer swing while the clue is visible (sum: 0.08) and 0.63–0.65 when the clue is made unanswerable. Reconstruction at the question positions replicates (82 % of free level under a carrier clamp). Three audit corrections are in Amendment 3 (readout must cover the maintained ANSWER pair as well as the bridge; two items are paraphrase pairs; the no-clue reference must be length-matched); the consumer question must never restate the clue (Amendment 2 — I fell into that trap once and archived the flawed variant). **`recompute_cost_ladder` (2026-09-09) is DONE and is a correction**: with the block-36 boundary held fixed, raising computational difficulty *lowers* the carrier share, so the recompute-cost account of the arithmetic-vs-fact difference is withdrawn; the live account is the boundary position, confounded with domain and unestablished. The canonical H3 statement is the block at the top of `STATUS.md`. Remaining candidates, registered as amendments before any forward: (3) a two-step arithmetic chain (paper case study 8 style) gated on thinking-off competence ≥ 0.9 and on the intermediate being readable during the carrier — tests whether the carrier share (9–18 % for one-step sums) rises when recompute is costly; (4) a two-hop factual organism (paper case study 5) with the same O_donor / C_full / NEC design — generality beyond arithmetic. **Route restriction** (mask the answer position's attention to the operand span) is deferred to the planned pure-attention rerun at the end of the project: on this hybrid model the GatedDeltaNet channel stays open under an attention mask, so 'source unavailable' cannot be made exact here. H2 (maintenance) still needs the hybrid complete-prefix-state parity control before any transplant. Report wording bans earned in H3: no "rereading" as an asserted mechanism, no "three times more", no causal one-third/two-thirds split of the crossed-margin observation, no "the readable representation is unused" without the scope "while the source is visible"; under a carrier transplant, agreement of instruments at the carrier is by construction and is reported as a gate, not a finding.

**Update 2026-09-24 (branch `extension`).** Stage 1 of the question-turn ladder extension is done (`two_hop_organism` `qsplit6`, Amendment 6): see the dated block in `STATUS.md` and the ledger row; read `H3/results/reports/two_hop_qsplit6.md` §8 before quoting it. Stage 2 (Amendment 7, 42 items over 7 relation types, admission gates, screen) is in progress; Amendment 8 is registered and not run. Silly mistake 4 is on record (additive current-base write double-counts the accumulated block delta; construction checks are their own gate).
