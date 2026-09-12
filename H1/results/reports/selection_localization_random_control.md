# H1 · selection_localization — random_control (Amendment 4: norm-matched non-specific controls) — run 20260907T194352Z

## 1. Question

How much of the instruction-region transplant's restoration R (Step 1A) is donor-specific pointer content, and how much would any equal-norm perturbation of the region produce? At boundary L36, beside B->A / C->A, three controls write h_A + delta over the same region: an isotropic direction norm-matched per (layer, position) to the donor delta (two seeds), the donor delta with region positions permuted, and the donor delta sign-flipped. Endpoint: R along the clean A->donor axis, the raw shift of s_A and of the mean unpointed presence, damage. Cluster=triple (n=8). 624 forwards.

## 2. Restoration by condition

**L48-50:** BtoA +0.539 [+0.448, +0.630] (8/8 >0); CtoA +0.495 [+0.425, +0.565] (8/8 >0); randB_s0 -0.002 [-0.023, +0.019] (4/8 >0); randB_s1 -0.001 [-0.037, +0.035] (4/8 >0); randC_s0 +0.017 [-0.020, +0.055] (4/8 >0); randC_s1 +0.016 [-0.005, +0.038] (6/8 >0); shuffB +0.065 [+0.034, +0.097] (8/8 >0); shuffC +0.066 [+0.037, +0.094] (8/8 >0); flipB -0.020 [-0.059, +0.018] (1/8 >0); flipC -0.038 [-0.093, +0.016] (2/8 >0)
**L48-50 donor-specific share R(DtoA) − mean R(rand):** B +0.541 [+0.458, +0.623] (8/8 >0); C +0.478 [+0.404, +0.553] (8/8 >0)
**L48-50 Δs_A / Δ mean-unpointed:** BtoA -0.13 / +0.13; CtoA -0.12 / +0.15; randB_s0 +0.01 / +0.00; randB_s1 +0.01 / +0.00; randC_s0 -0.01 / +0.00; randC_s1 +0.01 / +0.01; shuffB -0.02 / +0.01; shuffC -0.01 / +0.02; flipB -0.03 / -0.02; flipC -0.01 / -0.02

**L51-59:** BtoA +0.766 [+0.696, +0.837] (8/8 >0); CtoA +0.728 [+0.692, +0.764] (8/8 >0); randB_s0 -0.004 [-0.016, +0.007] (4/8 >0); randB_s1 +0.002 [-0.010, +0.014] (4/8 >0); randC_s0 +0.007 [-0.007, +0.022] (6/8 >0); randC_s1 +0.006 [-0.006, +0.018] (5/8 >0); shuffB +0.073 [+0.034, +0.112] (8/8 >0); shuffC +0.053 [+0.015, +0.091] (7/8 >0); flipB -0.006 [-0.025, +0.013] (4/8 >0); flipC -0.043 [-0.057, -0.029] (0/8 >0)
**L51-59 donor-specific share R(DtoA) − mean R(rand):** B +0.767 [+0.700, +0.835] (8/8 >0); C +0.721 [+0.689, +0.753] (8/8 >0)
**L51-59 Δs_A / Δ mean-unpointed:** BtoA -1.39 / +0.97; CtoA -1.28 / +0.94; randB_s0 -0.01 / -0.00; randB_s1 -0.01 / +0.01; randC_s0 -0.05 / -0.01; randC_s1 -0.03 / -0.01; shuffB -0.12 / +0.08; shuffC -0.04 / +0.10; flipB -0.09 / -0.06; flipC +0.11 / -0.03

**Damage:** max ΔNLL +0.0088; top-1 retention min 1.000.

Figure: `figures/selection_localization_random_control.png`. Machine-readable: `selection_localization_random_control_tables.json`.

## 3. Interpretation and next step

**Observation (cluster = triple, n = 8; boundary L36; damage nil, max ΔNLL 0.009, top-1 retention 1.000).** The donor transplants reproduce Step 1A within run-to-run noise (B→A R = +0.77 [+0.70, +0.84], C→A +0.73, 8/8 at L51–59; +0.54 / +0.50 at L48–50). Every norm-matched control is at or near zero: isotropic directions matched per layer and position to the donor delta give R = −0.004 … +0.017 (CIs include 0, signs at chance, both seeds, both donors); the donor delta with region positions shuffled gives +0.05 … +0.07 (CI-clear but under a tenth of the transplant); the sign-flipped delta gives 0 to −0.04. The raw components show why: the transplant lowers s_A by 1.3–1.4 and raises the unpointed presences by ~1.0 at L51–59, whereas the random writes move both by ≤ 0.05.

**Reading.** The restoration measured in Step 1A is donor-specific pointer content, not a nonspecific deselection of A: R(D→A) − mean R(rand) = +0.77 / +0.72 (8/8), i.e. essentially the whole effect. The small positive shuffle value shows the delta set carries a little position-free signal, but position binding accounts for over 90 % of it. The flip result (≤ 0, and −0.04 CI-clear for C) is the expected sign for a reversed pointer delta and rules out "any structured perturbation of this norm scores positive."

**Licensed.** The Step 1A/1C localization claim stands with its nonspecific share bounded at ≲ 0.02 (random) and the position-scrambled share at ≲ 0.07. **Not established:** the read-site component (Step 2), anything about behavior.

**Next.** No further H1 localization stage is warranted for the verdicts. H3 (behavioral use) is the load-bearing next hypothesis.
