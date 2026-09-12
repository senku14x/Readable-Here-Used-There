# H1 · selection_localization — region_split (Step 1B: which position carries the pointer) — run 20260907T044736Z

## 1. Question

Regions ['tag', 'instr_tail', 'user_carrier', 'gap', 'full'] of the post-tag prefix patched B->A / C->A at L[36, 44]; restoration R along the clean A->donor presence axis. (region_split: tag / instruction-tail / user-carrier / template-gap / full — Amendment 3, since the earlier 'suffix' included the user-side carrier.) Cluster=triple (n=8).

## 2. Restoration R by region

**L48-50:**
- B->A L36: tag +0.262 [+0.189, +0.334] (8/8 >0); instr_tail +0.141 [+0.092, +0.190] (8/8 >0); user_carrier +0.026 [+0.011, +0.041] (7/8 >0); gap -0.035 [-0.067, -0.003] (1/8 >0); full +0.539 [+0.448, +0.630] (8/8 >0)
- B->A L44: tag +0.153 [+0.101, +0.205] (8/8 >0); instr_tail +0.034 [+0.019, +0.049] (8/8 >0); user_carrier +0.027 [+0.016, +0.038] (8/8 >0); gap +0.047 [+0.022, +0.073] (7/8 >0); full +0.258 [+0.189, +0.328] (8/8 >0)
- C->A L36: tag +0.243 [+0.191, +0.294] (8/8 >0); instr_tail +0.153 [+0.117, +0.189] (8/8 >0); user_carrier +0.028 [+0.013, +0.043] (7/8 >0); gap -0.028 [-0.055, -0.001] (2/8 >0); full +0.495 [+0.425, +0.565] (8/8 >0)
- C->A L44: tag +0.137 [+0.108, +0.166] (8/8 >0); instr_tail +0.044 [+0.036, +0.053] (8/8 >0); user_carrier +0.036 [+0.023, +0.048] (8/8 >0); gap +0.020 [-0.006, +0.046] (6/8 >0); full +0.237 [+0.188, +0.285] (8/8 >0)

**L51-59:**
- B->A L36: tag +0.439 [+0.344, +0.534] (8/8 >0); instr_tail +0.091 [+0.048, +0.134] (8/8 >0); user_carrier +0.036 [+0.032, +0.041] (8/8 >0); gap -0.054 [-0.079, -0.030] (0/8 >0); full +0.766 [+0.696, +0.837] (8/8 >0)
- B->A L44: tag +0.161 [+0.110, +0.212] (8/8 >0); instr_tail +0.040 [+0.025, +0.054] (8/8 >0); user_carrier +0.031 [+0.025, +0.037] (8/8 >0); gap +0.025 [+0.006, +0.044] (7/8 >0); full +0.471 [+0.390, +0.552] (8/8 >0)
- C->A L36: tag +0.479 [+0.377, +0.582] (8/8 >0); instr_tail +0.088 [+0.057, +0.120] (8/8 >0); user_carrier +0.036 [+0.024, +0.048] (8/8 >0); gap -0.013 [-0.041, +0.014] (3/8 >0); full +0.728 [+0.692, +0.764] (8/8 >0)
- C->A L44: tag +0.200 [+0.142, +0.259] (8/8 >0); instr_tail +0.032 [+0.024, +0.041] (8/8 >0); user_carrier +0.028 [+0.023, +0.033] (8/8 >0); gap +0.046 [+0.030, +0.062] (8/8 >0); full +0.446 [+0.377, +0.514] (8/8 >0)

## 3. Interpretation and next step

**Observation (L51-59, boundary L36; all 8/8, target-specific; independently recomputed).** Restoration by region: **tag +0.44** (B->A) / +0.48 (C->A); **instr_tail +0.09** / +0.09; **user_carrier +0.036** / +0.036; **gap -0.05** / -0.01; full +0.77 / +0.73. tag + instr_tail (the instruction tokens) ~= 0.53 (~69% of full); the user-side carrier ~0.036 (~5%); the delimiter gap ~0/negative. Sum of the four parts (~0.51) < full (0.77): superadditive.

**Reading (resolves Amendment 3).** The pointer-dependent state is carried by the **instruction tokens** -- tag token dominant (~57% of full), instruction tail a small additional share -- while the **user-side carrier and delimiter tokens carry essentially none of it**. This **refutes** the alternative that the pointer is propagated into the passage representation before the assistant turn. The full-region effect is **superadditive** over the parts (joint contribution across the instruction tokens, since patching one sub-region leaves the others A-valued and attending), so this is a distributed/joint effect, not an additive decomposition.

**Corrected localization statement.** The selection pointer state lives in the **instruction residuals, tag-anchored** -- now properly isolated (user carrier negligible). Causal dependence on it is largely exhausted before block 48 (1A); it causally redirects which source transfers (1C). Read-site *component* (attention vs GatedDeltaNet vs MLP) -- Step 2 -- still open.
