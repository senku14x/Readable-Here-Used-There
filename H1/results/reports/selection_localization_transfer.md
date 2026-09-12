# H1 · selection_localization — transfer (Step 1C: causal-transfer confirmation) — run 20260907T042923Z

## 1. Question

Does the B->A / C->A instruction-region transplant (block >= 36) redirect the *causal transfer* profile C_j (source-swap transfer of each of the three sources), not just natural presence? C_j = m_j(swap j) - m_j(noswap), m_j = z_donor - z_source at the carrier. Ceilings: clean pointed-A/B/C. Restoration = movement of the B->A transfer profile toward clean-B along the A->B axis (and C->A toward C). S = pointed - unpointed transfer per condition. Cluster=triple (n=8).

## 2. Transfer profiles and restoration

**L48-50 transfer profile (C_0, C_1, C_2):** cleanA ['+0.34', '+0.08', '+0.14']; cleanB ['-0.03', '+0.57', '+0.12']; cleanC ['-0.02', '+0.02', '+0.54']; BtoA ['+0.13', '+0.36', '+0.15']; CtoA ['+0.13', '+0.05', '+0.34']
**L48-50 selection S = pointed-unpointed:** cleanA +0.237 [+0.147, +0.327] (8/8 >0); cleanB +0.527 [+0.399, +0.655] (8/8 >0); cleanC +0.531 [+0.435, +0.628] (8/8 >0); BtoA +0.218 [+0.167, +0.269] (8/8 >0); CtoA +0.255 [+0.193, +0.316] (8/8 >0)
**L48-50 transfer restoration:** B->A +0.517 [+0.435, +0.598] (8/8 >0); C->A +0.508 [+0.460, +0.556] (8/8 >0)

**L51-59 transfer profile (C_0, C_1, C_2):** cleanA ['+4.30', '+1.40', '+1.34']; cleanB ['+1.14', '+6.08', '+1.50']; cleanC ['+1.16', '+1.30', '+5.84']; BtoA ['+1.66', '+4.82', '+1.65']; CtoA ['+1.77', '+1.56', '+4.37']
**L51-59 selection S = pointed-unpointed:** cleanA +2.932 [+2.349, +3.515] (8/8 >0); cleanB +4.759 [+4.340, +5.177] (8/8 >0); cleanC +4.612 [+4.305, +4.919] (8/8 >0); BtoA +3.170 [+2.718, +3.623] (8/8 >0); CtoA +2.701 [+2.354, +3.049] (8/8 >0)
**L51-59 transfer restoration:** B->A +0.740 [+0.669, +0.810] (8/8 >0); C->A +0.690 [+0.640, +0.741] (8/8 >0)

**Damage:** max ΔNLL +0.0000.

## 3. Interpretation and next step

**Observation (L51-59; all 8/8, target-specific, damage nil).** Clean transfer profiles are diagonal-dominant (pointed source transfers most): cleanA (4.30, 1.40, 1.34), cleanB (1.14, 6.08, 1.50), cleanC (1.16, 1.30, 5.84). The instruction-region transplant **redirects the causal transfer profile**: BtoA (1.66, 4.82, 1.65) -- source B now transfers most; CtoA (1.77, 1.56, 4.37) -- source C most. Transfer restoration toward the donor-arm ceiling: **B->A +0.74 [+0.67, +0.81], C->A +0.69 [+0.64, +0.74]** (8/8), matching the presence restoration (~0.77) from Step 1A. Selection persists under the transplant (S = pointed-unpointed > 0 in every condition) but with the *pointed identity redirected* to the donor.

**What this establishes.** The instruction-region residual state does not merely move the readable presence -- it redirects the **causal source-selection phenotype** (which source's block-36 replacement reaches the carrier), target-specifically, by ~70-74%. So Step 1's localization is of the selection *mechanism*, not a readable correlate (the concern that motivated freezing this confirmation, cf. ĝ). Combined Step 1 result: the pointer state lives in the instruction-region residuals (1A), tag-anchored and distributed across the region (1B), sufficient by block 36 and read into the carrier by ~block 48 (1A), and causally controls which source transfers (1C).

**Not established.** The read-site *component* (attention vs GatedDeltaNet vs MLP) -- Step 2 (`component`), not yet built. The sustained-suffix patch bounds depth-of-sufficiency, not the read-site.

**Next.** Step 2 (`component`) is the finer mechanistic step (which carrier-side component applies the read); deferred. Per the H1 plan, proceed to the remaining H1 experiments (computed_sums, early_late_mapping) and the H1 stopping-point report; localization is recorded as bounded to the instruction residuals / blocks 36-48, tag-anchored, causally confirmed.
