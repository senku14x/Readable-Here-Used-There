# Readable Here, Used There

Doc: https://docs.google.com/document/d/1w4wG2P08Ic6ZH5UDrTg52DLaErTmTXb6j0x3dJEYVXg/edit?usp=sharing

*Where a delayed answer draws its information, and how much of it is in the naming plane.*

An empirical mechanistic-interpretability study of **where the information that drives a delayed answer sits**, on
**Qwen3.6-27B** (hybrid GatedDeltaNet + attention) with **Qwen3-32B** (dense) as a pure-attention control, using the
Jacobian lens (J-lens) from Gurnee et al. 2026 as the primary readout. A prompt introduces content (a quoted word, one of
three tagged words, a category, a number pair, a two-hop clue), the model copies an unrelated sentence teacher-forced
(the *carrier*), and a later question asks for the content. We intervene separately at the **source** positions, the
**carrier** positions and the **question** positions with matched controls, and read the answer.

Headline results and their scope are in `STATUS.md` (canonical H3 statement at the top) and `context/evidence_ledger.md`
(every load-bearing finding with its evidence level and strongest surviving alternative, including explicit withdrawals).
Start with `STATUS.md`, then `context/evidence_ledger.md` and `context/h1_stopping_point.md`.

## Layout

```
STATUS.md                       short current status (canonical H3 claim at the top)
context/                        evidence ledger, H1 stopping point (eight verdicts), project understanding, paper notes
.claude/skills/                 the figure-style helper used by make_figures.py (iclr-plots) and two writing/review skills
common/scripts/                 registry (model/lens pins, hashes), materials, rendering + span gates, readout (lens z; folded
                                directions), hooks (SpanWriter, StateMove, CoordSwap/Clamp, ...), hooks_fp32 (float32 regime),
                                stats, instrument_gates, make_figures
common/configs/                 instrument_registry*.json (hashes, layer maps), instrument_gates_result.json
H1|H3/design_specs/             one design doc per experiment, with dated amendments registered before the forwards they govern
H1|H3/scripts/                  <experiment>.py (battery, stages) + <experiment>_analysis.py (single scoring pass)
H1|H3/outputs/                  raw_<stage>.npz, meta_<stage>.json (cells, token ids, run id), manifest_<stage>.json (pins, sha256)
H1|H3/results/reports/          <experiment>_<stage>.md reports (setup, tables with intervals and sign counts, gates, interpretation)
H1|H3/results/tables/           <experiment>_<stage>_tables.json — every number in a report or figure comes from here
H1|H3/results/figures/          ICLR-style figures, regenerated from the tables only by common/scripts/make_figures.py
H1/results/qualitative/         top-10 lens readouts on fixed and seeded-random cells
H3/trying_to_fool/              the adversarial-susceptibility study (held separately; see context/fooling_study_2026-09-09.md)
replication_qwen3_32b/          the pure-attention replication (TCSIF_MODEL=qwen3_32b): plan, predictions, results, outputs
rebuild_env.sh                  rebuild recipe after an instance recycle (model + lens files at pinned revisions)
```

Conventions: analysis scripts write their report and tables into `H*/results/`; in this repository those files are filed
under `results/reports/` (Markdown) and `results/tables/` (JSON) for reading, and `make_figures.py` reads the `tables/`
paths. Raw arrays over 100 MB are git-ignored and mirrored to the private HF dataset `senku21x/tcsif-outputs` at the same
relative paths. Every experiment's materials, estimands, gates and decision rules are in its own design spec, with dated
amendments registered before the forwards they govern.

## Reproducing

```
source /venv/main/bin/activate && bash rebuild_env.sh        # transformers 5.15.0, jacobian-lens @581d398, model + lenses
python common/scripts/instrument_gates.py                    # gates before any scientific forward
python H3/scripts/two_hop_qsplit.py smoke && python H3/scripts/two_hop_qsplit.py qsplit && python H3/scripts/two_hop_qsplit_analysis.py
python common/scripts/make_figures.py                        # every figure, from the committed tables
```

Every run's `manifest_*.json` pins the model revision, lens hashes, software versions and the raw-array SHA-256; every
`meta_*.json` carries the rendered cells and token ids. Headline numbers were independently recomputed from the raw arrays
for the load-bearing stages (see `context/evidence_ledger.md` §D and the audits under `H3/audits/`).
