# H3 `selection_to_behavior` implementation audit

Audit date: 2026-09-08  
Scientific target pinned for audit: `55cf66e1a656acb210d11bef4e720dcc54928360`  
Existing `H3/outputs/selection_to_behavior/` and `H3/results/selection_to_behavior.md` are preserved unchanged.  
Audit code/output lives only under `H3/audits/selection_to_behavior/`.

## Bottom line before GPU trace

The saved pilot mean effects are reproducible from the committed summary numbers, but the implementation audit is **not a clean pass yet**. Four issues matter before using the pilot as validated implementation evidence:

1. The required with/without-consumer prefix-reproducibility gate failed numerically (`max_abs_dz_carrier_interior = 10.96875`), and the runner did not locate the first residual divergence or test masks/equal-length suffixes/reference execution. The result report currently assumes this is harmless; this audit does not.
2. The patched region called the “instruction region” is actually `[tag_position, carrier_start)`, where `carrier_start` is the start of the **assistant** carrier. Because the user turn itself contains the carrier, this full region includes the tag/instruction tail, the **user-carrier occurrence**, and the chat-template gap up to the assistant carrier. It does not patch the assistant carrier or consumer suffix. This is consistent with H1's later `region_split` naming, but the H3 result should not describe it as instruction-only state.
3. `randA` is not verified to be norm-matched to the **realized sustained transplant write**. It is constructed from the clean `||h_B-h_A||` per layer/position, and `rho` is stored as the constant `1.0`; no realized transplant/rand write statistics are measured. There is no separately C-matched random control.
4. The analysis violates the registered primary inferential unit: it calls `cluster_t` on 12 carrier/rotation cells rather than averaging the six cells within each triple first. The pilot therefore has **2 clusters, not 12**. Means are unchanged; reported CIs/sign counts are not valid cluster-level intervals.

A fifth scoring issue is narrower but should be fixed for the audit: the runner scores the two accepted single-token letter forms by `max(log P)` rather than deduplicated probability mass via `logsumexp`. The committed NPZ stores only the resulting eight letter scores, not candidate raw logits, so the corrected score cannot be reconstructed from the old archive alone; the GPU trace saves both.

## End-to-end traced cell definition

The audit trace script fixes the first pilot cell: `T0|C0|rot0`.

- source slots: A=`cat`, B=`dress`, C=`snake`
- source donors: `turtle`, `airport`, `fish`
- deterministic codebook assignment recovered from the registered seed: `cat→Q`, `dress→V`, `snake→F`, `turtle→B`, `airport→H`, `fish→M`
- deterministic codebook order: `airport, cat, turtle, fish, snake, dress`
- committed metadata: `tag_pos=30`, `carrier_start=78`, `answer_pos=165`, `instr_len=48`
- clean A, clean B, and B→A use the same full codebook/query rendering; only the A/B tag token differs for clean donor construction.

`trace_gpu.py` independently reruns this cell and emits the exact token IDs/decoded tokens, layerwise prefix residual deltas, patch-write diagnostics, raw answer logits, accepted letter token IDs, old/max scoring, corrected deduplicated-logsumexp scoring, and hook-lifetime checks.

---

## 1. Prefix discrepancy

**Code locations**

- `H3/scripts/selection_to_behavior.py`: `render_arm`, one-time `gate3` block.
- `common/scripts/rendering.py`: `render_conversation`, `render`.
- `common/scripts/hooks.py`: `make_run`.

**Concrete committed diagnostic**

`meta_pilot.json` records:

```json
{"prefix_ids_identical": true,
 "max_abs_dz_carrier_interior": 10.96875}
```

But the assertion is only `r_nc.ids[:cs] == rr["A"].ids[:cs]`, i.e. token IDs before `carrier_start`. It does not assert equality of the assistant-carrier/interior IDs that are subsequently scored. It also does not compare positions, masks, raw residuals layer by layer, or an alternate execution path.

`make_run` calls `model(ids, attention_mask=None)`; no explicit all-ones mask is tested.

**Status: FAIL / unresolved root cause.** The registered gate required reproducibility and said failure should be debugged before interpretation. A ~11-unit J-score discrepancy is not accepted here as benign without locating the first residual divergence.

**Does it change the reported result?** Potentially. The within-consumer B→A behavioral contrast can still be internally consistent, but the claim that the appended consumer leaves the H1 carrier phenomenon mechanically unchanged is not established. It is especially relevant for evaluate-stage source donors, which are generated with `consumer=False`.

**Audit execution added**

`trace_gpu.py` compares:

- consumer vs no-consumer token IDs through the assistant-carrier end;
- identical carrier positions/IDs;
- layer-by-layer carrier residuals, reporting the first non-bitwise layer;
- equal-length, different-content suffixes;
- `attention_mask=None` vs explicit all-ones mask;
- `model(...)` vs an available `lm.forward(...)` reference path.

## 2. What is patched

**Code locations**

- `common/scripts/hooks.py::SpanWriter`: a PyTorch **forward hook on decoder block output**; it clones the block output and replaces `h[0, positions, :]`.
- `common/scripts/registry.py`: 64 blocks; zero-based block-output indexing.
- `H3/scripts/selection_to_behavior.py`: `LX=36`, `LGE = [l for l in ALL if l >= LX]`, and `instr = list(range(tp, cs))`.

**Concrete diagnostic from code + committed metadata**

For `T0|C0|rot0`, the replacement is at block outputs 36..63 over token positions 30..77. The source spans are asserted to end before position 30. Position 78 is the first assistant-carrier token.

Critically, `cs` is the start of the assistant carrier, not the end of the textual instruction. Therefore positions 30..77 include the user-side carrier and template tokens as well as the tag/instruction tail. H1's `region_split` code explicitly decomposes this same “full” region into `tag`, `instr_tail`, `user_carrier`, and `gap`.

B donor tensors are built as immutable `.clone()` slices from the clean-B activations of the **same cell/full consumer rendering**. C is analogous. The `Both`/`SpanWriter` context managers remove hooks on exit.

**Hybrid/cache semantics**

The run is a single full-sequence forward; no `past_key_values` object is supplied or transplanted. A block-output hook cannot retroactively replace the recurrent/attention state already computed inside that block. The modified residual sequence feeds the next block, where downstream attention/GatedDeltaNet computation is recomputed from that changed trajectory. Thus this is a sustained residual-output transplant, not a complete recurrent/cache-state transplant.

**Status: PARTIAL PASS, with a labeling correction.** Block/output semantics, donor cell identity, tensor cloning, and hook lifetime are sound by inspection. The region is broader than “instruction only,” and recurrent/cache state is not transplanted.

**Does it change the reported result?** It changes the mechanistic description. The causal intervention should be called the full post-tag pre-assistant-carrier residual region, not an isolated instruction state. The numerical endpoint is not thereby invalidated.

`trace_gpu.py` prints every patched token and hashes donor tensors before/after the transplant, and checks hook counts return to baseline.

## 3. Donor leakage and condition matching

**Code location**

`H3/scripts/selection_to_behavior.py`, inside the cell loop.

**Concrete diagnostic**

The codebook and query are generated once per `(triple, carrier, rotation)` before rendering A/B/C, so A/B/C/B→A/C→A/randA share the identical suffix and code assignment within a cell. `tag_position` asserts that the three full A/B/C renderings differ at exactly one token. Source spans are asserted to precede that tag. B→A/C→A run the A recipient IDs and patch only `[tp,cs)`, so answer/consumer positions are not deliberately patched.

Primary instruction donors come from `rr["B"]`/`rr["C"]` with the consumer present, so there is no cross-render donor mismatch for the primary endpoint.

For the evaluate secondary factorial, however, source-donor states are explicitly rendered with `consumer=False`. Because gate 1 currently shows unexplained sequence-length-dependent prefix divergence, these source-donor states are not yet proven numerically comparable to the consumer rendering.

**Status: PASS for primary condition matching; UNRESOLVED for evaluate source donors until prefix discrepancy is fixed.**

**Does it change the reported result?** No immediate change to the pilot primary. It can affect the secondary evaluate interpretation.

## 4. Answer scoring

**Code locations**

- `H3/scripts/selection_to_behavior.py::letter_ids`, `letter_scores`, `record`.
- `common/scripts/rendering.py::render`: `spans["answer"] = len(ids)-1`.

**Concrete diagnostic**

The model is scored at `logits[0,-1]`, which is the next-token distribution after the final rendered assistant-prefix input token. The saved metadata for the traced cell says `answer_pos=165`; the audit trace prints the final input tokens and verifies this alignment.

Current scoring is:

```python
sc = {L: max(float(lp[i]) for i in LID[L]) for L in LETTERS}
```

This does **not** implement the requested accepted-form probability mass. It also does not deduplicate token IDs before combining forms. Greedy output is taken independently from `argmax(logits[0,-1])`.

The committed NPZ saves only eight aggregated `lsc` values, not the candidate raw logits/token IDs, so a corrected historical `logsumexp` score cannot be recovered exactly from that archive.

**Status: FAIL for the requested scoring audit; likely no off-by-one by code inspection, but runtime token dump remains required.**

**Does it change the reported result?** Unknown until rerun. The old/max endpoint is internally consistent with the reported pilot; the corrected endpoint needs the trace/evaluation rerun. `trace_gpu.py` reports both for the same cleanA/cleanB/B→A forward.

## 5. Random control

**Code location**

`H3/scripts/selection_to_behavior.py`, `randA` construction.

**Concrete diagnostic**

At every layer/position it computes the clean-state distance

```python
dn = ||hB_clean - hA_clean||
randsrc = hA_clean + unit_random * dn
```

and then uses `SpanWriter` to write that absolute target throughout layers 36..63.

A sustained transplant's **realized** write at later layers is instead `hB_clean - h_current_before_patch`, where `h_current_before_patch` has already been changed by earlier patches. The current control therefore does not, by construction, match the realized B→A write schedule. The same issue applies to the random arm's own realized writes.

Moreover:

```python
RAW[f"{base}|randA|rho"] = np.float32(1.0)
```

is hard-coded. `SpanWriter` itself does not collect realized-write statistics. There is one B-scaled `randA`; no separately C-scaled control exists.

The random tensor target is constructed once per cell and reused across noswap/swap runs in evaluate, so the **random realization is fixed across the paired secondary conditions**, which is correct.

**Status: FAIL as a verified matched-dose control.**

**Does it change the reported result?** It weakens the claim that `E_D - randA` establishes donor specificity at a matched realized dose. The null random arm is still useful as a generic perturbation control, but it is not yet the control described in the result text.

`trace_gpu.py` measures actual per-layer/per-position B→A, C→A and current-rand writes and reports the rand/transplant norm-ratio distribution.

## 6. Secondary factorial composition

**Code locations**

`H3/scripts/selection_to_behavior.py` evaluate branch; `common/scripts/hooks.py::Both`.

**Concrete diagnostic**

For each arm, the instruction hook is created once and combined with a source-span `SpanWriter` via `H.Both(ip, sw)`. The two position sets are statically disjoint because source spans are asserted `< tp` while the instruction/full region begins at `tp`. Therefore the hooks do not overwrite the same tensor positions. `Both` enters both and removes them in reverse order.

The same `ids`, codebook, instruction patch object and random source tensor are reused across the arm's `swap0/1/2` runs; each `C_j` compares the matching arm's swap and noswap records.

The unresolved problem is upstream: source donor tensors are produced from no-consumer forwards, which are unsafe to treat as prefix-identical until check 1 is resolved. Also the original evaluate code does not save hook-level composition diagnostics or same-source swap parity for these H3 rows.

**Status: PASS by static composition logic, conditional on check 1; runtime parity still required.**

**Does it change the reported pilot?** No; the pilot has no source swaps. It conditions the evaluate result.

## 7. Statistics and raw-output recomputation

**Code locations**

- Registered design: rotations/carriers averaged within triple before any interval; cluster = triple.
- `H3/scripts/selection_to_behavior_analysis.py`: loops over `cells`, appends one value per cell, and calls `S.cluster_t` directly.
- `common/scripts/stats.py::cluster_t`: treats each supplied value as an independent cluster.

**Concrete diagnostic**

The committed pilot has 12 cells = 2 triples × 2 carriers × 3 rotations. The current analysis reports `n=12`; this is not the registered cluster structure.

Using the committed per-cell values and first averaging the six cells inside each triple gives:

| quantity | T0 mean | T1 mean | correct n=2 mean | 95% cluster-t CI |
|---|---:|---:|---:|---:|
| E_B | 2.417 | 2.625 | 2.521 | [1.197, 3.844] |
| E_C | 2.260 | 2.073 | 2.167 | [0.975, 3.358] |
| rand on B margin | 0.073 | -0.010 | 0.031 | [-0.498, 0.561] |
| rand on C margin | 0.052 | -0.031 | 0.010 | [-0.519, 0.540] |
| E_B - current rand | 2.344 | 2.635 | 2.490 | [0.637, 4.343] |
| E_C - current rand | 2.208 | 2.104 | 2.156 | [1.494, 2.818] |

The means are exactly the same as reported because the design is balanced. The pilot CIs change substantially. The two-triple internal-restoration intervals become too wide to treat as confirmatory (`B→A L51–59` mean 0.821, 95% CI approximately [-0.546, 2.189]; `C→A` mean 0.720, approximately [-0.180, 1.619]). That does not contradict the 12/12 descriptive cell signs or the prior H1 result; it means this pilot itself supplies only two independent material clusters.

The behavioral restoration point estimates remain 0.205 and 0.172 after correct clustering. A bootstrap interval with only two clusters is not very informative and should not be overinterpreted.

No failed cells appear to have been silently excluded: `meta_pilot.json` contains 12 cells and the run count is 97, exactly matching 8 primary-model forwards per cell plus the one extra no-consumer gate forward. The existing summary has all six primary arms for all 12 cells.

**Crossed specificity table**

The registered result only reports the diagonal pulls (B→A on B-vs-A and C→A on C-vs-A). The off-diagonal pulls require the saved per-letter scores. `recompute_saved.py` computes the full 3×2 table directly from the NPZ:

- B→A effect on B-vs-A margin (diagonal)
- B→A effect on C-vs-A margin (off-diagonal)
- C→A effect on B-vs-A margin (off-diagonal)
- C→A effect on C-vs-A margin (diagonal)
- current randA effects on both margins

with rotations/carriers averaged inside triple before inference.

**Status: FAIL for the published pilot intervals; point estimates pass. Crossed table pending execution of the saved-output audit script.**

**Does it change the reported result?** It does not change the reported pilot means or the fact that all 12 cell-level `E_B/E_C` values are positive. It downgrades the certainty that should be attached to pilot-only CIs and makes the fresh six-triple evaluation more important.

---

## Required runtime deliverables

Run, on the experiment environment:

```bash
python H3/audits/selection_to_behavior/recompute_saved.py pilot
python H3/audits/selection_to_behavior/trace_gpu.py
```

and after evaluate finishes:

```bash
python H3/audits/selection_to_behavior/recompute_saved.py evaluate
```

The scripts preserve existing results and write only to the audit `outputs/` directory.

The current pilot should not be promoted from “pilot-scale evidence” to a validated H3 result until the prefix discrepancy and realized-dose control are resolved. The mean behavioral pull itself is not presently explained away by the audit; the main changes are (i) weaker inferential accounting, (ii) a broader intervention than the prose label suggests, (iii) an unverified matched-random control, and (iv) an unresolved forward-prefix numerical discrepancy.