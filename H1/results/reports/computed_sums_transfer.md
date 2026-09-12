# H1 · computed_sums — transfer — run 20260907T044151Z

## 1. Question

Does a different-sum donor move the sum readout (C_diff^sum>0) while a same-sum sibling leaves the sum readout invariant (C_same^sum~=0, equivalence-tested) but moves the addends (C_same^add>0)? That would be computed-output sensitivity. Cluster=sum (n=8). RESID axis not fit (J_NP+LOGITS). 384 forwards.

## 2. Findings (maintain arm)

- **J_NP|L48-50:** C_diff^sum +0.256 [+0.174, +0.339] (8/8 >0); **C_same^sum +0.008 [-0.001, +0.017] (6/8 >0)** (equivalence to 0 within ±0.051: YES); C_diff^add +0.021 [-0.070, +0.112] (5/8 >0); C_same^add +0.052 [-0.023, +0.126] (5/8 >0).
- **J_NP|L51-59:** C_diff^sum +1.899 [+1.558, +2.241] (8/8 >0); **C_same^sum -0.006 [-0.018, +0.007] (2/8 >0)** (equivalence to 0 within ±0.380: YES); C_diff^add +0.379 [+0.249, +0.509] (8/8 >0); C_same^add +0.541 [+0.470, +0.611] (8/8 >0).
- **LOGITS:** C_diff^sum +3.315 [+2.599, +4.031] (8/8 >0); **C_same^sum -0.048 [-0.082, -0.014] (1/8 >0)** (equivalence to 0 within ±0.663: YES); C_diff^add +0.721 [+0.450, +0.991] (8/8 >0); C_same^add +1.108 [+0.995, +1.222] (8/8 >0).

## 3. Instruction modulation A = maintain - control

- J_NP|L51-59: A(C_diff^sum) +2.011 [+1.649, +2.372] (8/8 >0); A(C_diff^add) -0.242 [-0.389, -0.095] (1/8 >0).
- LOGITS: A(C_diff^sum) +3.580 [+2.935, +4.224] (8/8 >0); A(C_diff^add) -0.540 [-0.802, -0.278] (0/8 >0).

**Damage:** max ΔNLL +0.0012.

## 4. Interpretation

**Observation (maintain, L51-59; cluster=sum, n=8; competence 16/16; sum-word instrument validated by the natural gate, +0.69).** A **different-sum** donor moves the sum readout strongly (C_diff^sum +1.90 [+1.56, +2.24], 8/8; LOGITS +3.32). A **same-sum sibling** donor (different addends, same value) leaves the sum readout **invariant** (C_same^sum -0.006 [-0.018, +0.007], equivalent to 0 within +/-0.38 by the pre-registered +/-20%-of-C_diff band) **while it moves the addend readout** (C_same^add +0.54, 8/8; LOGITS +1.11). Damage nil (max delta-NLL 0.001).

**Reading: computed-output sensitivity.** The sum readout at the carrier tracks the **value**, not the addends: the sum word is never in the prompt, yet a different-sum donor redirects it and a same-sum re-pairing does not, even though the same re-pairing demonstrably changes the addend readout. So the transferred content includes the **model's computed sum** (a latent that is never a token), not merely its addend tokens. The instruction modulates transfer of this computed value as it did for words: A(C_diff^sum) = maintain - control = +2.01 (8/8).

**Scope / not established (design section 1).** This does **not** decide whether the completed sum *travels* through the carrier or is *recomputed* downstream at each position -- both are compatible with these readouts. Re-pairing the same addends is not independent arithmetic replication (8 specific facts: seven..fourteen). RESID sum axis not fit; J_NP and LOGITS agree. Extends the earlier pilot's computed-sum result with a proper equivalence-tested same-sum invariance and an addend-moves positive control.
