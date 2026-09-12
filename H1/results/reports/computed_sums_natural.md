# H1 · computed_sums — natural (sum-word readability gate) — run 20260907T044111Z

## Findings

- **J_NP|L48-50:** sum presence maintain +0.091 [-0.868, +1.050] (4/8 >0), control +0.048 [-0.983, +1.079] (4/8 >0), absent +0.000 [-1.134, +1.134] (4/8 >0); **maintain-absent +0.091 [-0.301, +0.483] (4/8 >0)** gate FAIL; addend maintain-absent +2.786 [+2.552, +3.020] (8/8 >0).
- **J_NP|L51-59:** sum presence maintain +0.688 [-0.125, +1.501] (7/8 >0), control -0.027 [-0.817, +0.762] (5/8 >0), absent +0.000 [-0.790, +0.790] (4/8 >0); **maintain-absent +0.688 [+0.467, +0.909] (8/8 >0)** gate PASS; addend maintain-absent +2.406 [+2.218, +2.594] (8/8 >0).
- **LOGITS:** sum presence maintain +1.414 [-0.086, +2.914] (6/8 >0), control -0.086 [-1.458, +1.287] (5/8 >0), absent +0.000 [-1.263, +1.263] (5/8 >0); **maintain-absent +1.414 [+1.080, +1.748] (8/8 >0)** gate PASS; addend maintain-absent +1.409 [+1.165, +1.654] (8/8 >0).

**Gate:** sum-word instrument validated (J_NP|L51-59). If not validated, the transfer sum endpoint is 'instrument not validated' but the transfer stage still runs.
