# H1 · selection_localization — decomp (Step 1B: which position carries the pointer) — run 20260907T042553Z

## 1. Question

At boundaries {36,44}, transplant the donor's block outputs over **tag-only** / **post-tag suffix** / **full** instruction region B->A and C->A; restoration R along the clean A->donor presence axis. tag-only~=full => pointer local to the tag state; suffix~=full => propagated into the instruction suffix; neither alone => distributed. Cluster=triple (n=8).

## 2. Restoration R by region

**L48-50:**
- B->A L36: tag +0.262 [+0.189, +0.334] (8/8 >0); suffix +0.172 [+0.116, +0.229] (8/8 >0); full +0.539 [+0.448, +0.630] (8/8 >0)
- B->A L44: tag +0.153 [+0.101, +0.205] (8/8 >0); suffix +0.119 [+0.092, +0.147] (8/8 >0); full +0.258 [+0.189, +0.328] (8/8 >0)
- C->A L36: tag +0.243 [+0.191, +0.294] (8/8 >0); suffix +0.229 [+0.187, +0.270] (8/8 >0); full +0.495 [+0.425, +0.565] (8/8 >0)
- C->A L44: tag +0.137 [+0.108, +0.166] (8/8 >0); suffix +0.107 [+0.073, +0.142] (8/8 >0); full +0.237 [+0.188, +0.285] (8/8 >0)

**L51-59:**
- B->A L36: tag +0.439 [+0.344, +0.534] (8/8 >0); suffix +0.240 [+0.180, +0.300] (8/8 >0); full +0.766 [+0.696, +0.837] (8/8 >0)
- B->A L44: tag +0.161 [+0.110, +0.212] (8/8 >0); suffix +0.126 [+0.097, +0.156] (8/8 >0); full +0.471 [+0.390, +0.552] (8/8 >0)
- C->A L36: tag +0.479 [+0.377, +0.582] (8/8 >0); suffix +0.229 [+0.188, +0.271] (8/8 >0); full +0.728 [+0.692, +0.764] (8/8 >0)
- C->A L44: tag +0.200 [+0.142, +0.259] (8/8 >0); suffix +0.129 [+0.105, +0.152] (8/8 >0); full +0.446 [+0.377, +0.514] (8/8 >0)

## 3. Interpretation and next step

**Observation (L51-59, boundary L36; all 8/8, target-specific).** Restoration by patched region: tag-only +0.44 (B->A) / +0.48 (C->A); post-tag suffix-only +0.24 / +0.23; full region +0.77 / +0.73. tag + suffix approx = full (0.44+0.24=0.68 ~ 0.77; 0.48+0.23=0.71 ~ 0.73) -- roughly additive. Same pattern at L44 (smaller) and L48-50.

**Reading.** The pointer state is **distributed across the instruction region, anchored at the tag token**: the tag token's own residual carries the largest single share (~60% of the full effect), and the remainder is propagated into the instruction suffix positions (which attended to the tag). Neither position alone reaches the full restoration; both together do. So the pointer is neither a purely local tag-token variable nor purely a propagated suffix state -- it is tag-anchored and distributed. (Scoped: instruction-region residual *sufficiency*, not read-site; Amendment 2.)

**Correction (Amendment 3).** The `suffix` region here = [tag+1, assistant_carrier_start), which includes the **user-side carrier + delimiters**, not just the instruction. The corrected `region_split` shows the post-tag effect beyond the tag is in the **instruction tail** (~0.09), not the user carrier (~0.036) or delimiters (~0); so 'propagated into the instruction suffix' should read 'the tag token is dominant and the remainder is a joint/superadditive contribution across the instruction tokens'. See `selection_localization_region_split.md`.

**Next.** Step 1C (`transfer`) confirms whether the causal transfer S -- not just natural presence -- is redirected by the B->A / C->A transplant.
