# H1 · selection_localization — ptr_transplant (Step 1A) — run 20260907T041407Z

## 1. Question and setup

Amendment 1 withdrew the source-token cross-arm stage (predetermined: sources precede the tag, so their states are arm-invariant). Here: pointed-A/B/C prompts are token-aligned (differ only at the tag token, position 30). For each triple/rotation/carrier, transplant the donor's block outputs over the instruction region [tag token, end of user turn) into the recipient-A run at blocks >= L (sweep [36, 40, 44, 48, 51, 55]), and read the carrier presence profile p=(s_A,s_B,s_C). **R_L** = movement along the clean A->donor axis (0=stays A-like, 1=reaches the clean donor profile). This tests whether pointer-dependent instruction-region residual state is *sufficient* to redirect the later carrier profile and bounds the depth by which such state is available — NOT where it is read. Cluster=triple (n=8); both windows. Target specificity: B->A should move toward B, C->A toward C; A->A self-patch is a bitwise no-op gate (asserted). 768 forwards.

## 2. Clean profiles (the S_nat ceiling) and restoration

**L48-50 clean presence profile (s_A, s_B, s_C):** pointed-A ['+0.20', '-0.04', '+0.02'], pointed-B ['-0.12', '+0.32', '-0.04'], pointed-C ['-0.07', '-0.01', '+0.42']. axis norm |p_B-p_A| 0.55, |p_C-p_A| 0.56.
**L51-59 clean presence profile (s_A, s_B, s_C):** pointed-A ['+2.06', '+0.48', '+0.43'], pointed-B ['+0.38', '+2.79', '+0.47'], pointed-C ['+0.44', '+0.48', '+2.81']. axis norm |p_B-p_A| 2.93, |p_C-p_A| 2.96.

**R_L — L48-50:**
- B->A: L36 +0.539 [+0.448, +0.630] (8/8 >0); L40 +0.389 [+0.304, +0.473] (8/8 >0); L44 +0.258 [+0.189, +0.328] (8/8 >0); L48 +0.026 [+0.016, +0.036] (8/8 >0); L51 +0.000 [+0.000, +0.000] (0/8 >0); L55 +0.000 [+0.000, +0.000] (0/8 >0)
- C->A: L36 +0.495 [+0.425, +0.565] (8/8 >0); L40 +0.363 [+0.297, +0.430] (8/8 >0); L44 +0.237 [+0.188, +0.285] (8/8 >0); L48 +0.022 [+0.012, +0.033] (8/8 >0); L51 +0.000 [+0.000, +0.000] (0/8 >0); L55 +0.000 [+0.000, +0.000] (0/8 >0)

**R_L — L51-59:**
- B->A: L36 +0.766 [+0.696, +0.837] (8/8 >0); L40 +0.654 [+0.594, +0.714] (8/8 >0); L44 +0.471 [+0.390, +0.552] (8/8 >0); L48 +0.052 [+0.040, +0.063] (8/8 >0); L51 -0.010 [-0.014, -0.006] (0/8 >0); L55 +0.003 [+0.002, +0.005] (8/8 >0)
- C->A: L36 +0.728 [+0.692, +0.764] (8/8 >0); L40 +0.624 [+0.585, +0.662] (8/8 >0); L44 +0.446 [+0.377, +0.514] (8/8 >0); L48 +0.054 [+0.044, +0.065] (8/8 >0); L51 -0.001 [-0.006, +0.003] (4/8 >0); L55 +0.004 [+0.003, +0.005] (8/8 >0)

**Raw delta components (Δs_A, Δs_B, Δs_C) at L51-59** (B->A should show s_A down, s_B up):
- B->A: L36 ['-1.39', '+1.80', '+0.14']; L40 ['-1.30', '+1.43', '+0.16']; L44 ['-0.86', '+1.14', '+0.09']; L48 ['-0.05', '+0.12', '+0.02']; L51 ['+0.03', '-0.01', '-0.00']; L55 ['-0.00', '+0.01', '+0.00']
- C->A: L36 ['-1.28', '+0.11', '+1.76']; L40 ['-1.19', '+0.08', '+1.42']; L44 ['-0.74', '+0.03', '+1.05']; L48 ['-0.04', '+0.02', '+0.14']; L51 ['+0.03', '+0.00', '+0.01']; L55 ['-0.01', '-0.00', '+0.01']

**Damage:** ΔNLL max +0.0002; top-1 retention min 1.000. A→A self-patch bitwise no-op asserted per cell.

Figure: `figures/selection_localization_R_by_L.png`. Machine-readable: `selection_localization_ptr_transplant_tables.json`.

## 3. Interpretation and next step

**Observation.** Clean natural selectivity is strong (L51-59: the pointed word's carrier presence ~2.8 vs ~0.45 for the two unpointed; axis norm ~2.93) -- the ceiling. Transplanting the donor's **instruction-region residual state** ([tag token, end of user turn)) into the recipient-A run:
- from **block 36**: restores R = **+0.77** (B->A) / **+0.73** (C->A) of the donor profile at L51-59 (8/8 triples), **target-specific** -- B->A moves the profile toward B (Δ = -1.39, +1.80, +0.14 on s_A/s_B/s_C), C->A toward C (-1.28, +0.11, +1.76); the off-target component stays ~0;
- and **decays monotonically with depth**: R = 0.77 (L36) -> 0.65 (L40) -> 0.47 (L44) -> **0.05 (L48)** -> ~0 (L51+).
- Damage nil (ΔNLL <= 2e-4, top-1 retention 1.000); A->A self-patch bitwise no-op; independently recomputed.

**What this establishes (scoped).** The pointer state that redirects the carrier's source-selection profile lives in the **post-tag prefix residuals** -- confirming Amendment 1's deduction that it is *not* on the source tokens -- and is **sufficient by block 36**. (Correction, Amendment 3: the patched region included the user-side carrier + delimiters; the region_split experiment isolates the effect to the **instruction tokens, tag-dominant** -- user carrier and delimiters negligible. See `selection_localization_region_split.md`.) Its sufficiency is **exhausted by ~block 48** (patching from >=48 restores essentially nothing): since a block->=L suffix patch influences the carrier only through blocks > L, causal dependence on the patched post-tag prefix state is largely **exhausted before block 48** (Step 2 earns the word 'read'), before the L51-59 readout window. Target specificity (B->A->B-like, C->A->C-like, off-target ~0) rules out a generic-perturbation account: the transplant installs the *specific* donor's selection.

**What this does NOT establish (Amendment 2).**
- *Where* the pointer is read/applied (attention vs GatedDeltaNet vs MLP) -- the sustained-suffix patch bounds the depth of *sufficiency*, not the read-site. That is Step 2 (`component`).
- *Which position* in the instruction region carries it (the tag state itself vs the propagated suffix) -- Step 1B (decomposition).
- Whether the **causal transfer S** (not just natural presence) is also redirected -- Step 1C, the load-bearing confirmation before this counts as localizing the *selection* mechanism, since readable-state and source-transfer effects need not share a causal interpretation (cf. ĝ).

**Next.** Step 1B: at the informative boundary (L36, and L44 for dynamic range) patch tag-only vs post-tag suffix vs full region -- does the pointer stay local to the tag state or propagate into the suffix? Step 1C: at L36 (and one deeper boundary), cross the B->A transplant with source replacements and verify the transfer profile C_j / S is redirected toward B.
