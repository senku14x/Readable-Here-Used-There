# H1 · early_late_mapping — run 20260907T045952Z

## 1. Setup

Does mapping availability change whether the carrier expresses X or F(X)? Conditions: early_usable (codebook incl X before carrier), early_unusable (length-matched codebook over 8 other words), late (codebook after). 32 words x 2 mappings x 2 carriers; cluster=word (n=32). Central: E_F^sc = s_F(X)-s_F(Y) under the same usable codebook (transformation signal, source-conditioned). E_X_usability = s_X^eu - s_X^unusable (controls the generic long-prefix effect). 384 forwards.

## 2. Competence

- answer accuracy: early_usable 1.000, late 0.992 (gate >= 0.90).

## 3. Carrier endpoints

- **J_NP|L48-50:** E_F^sc +0.006 [-0.405, +0.418] (17/32 >0); E_X_usability -0.091 [-0.157, -0.024] (11/32 >0); E_F +0.010 [-0.028, +0.048] (14/32 >0); raw E_X(late-eu) +0.451 [+0.336, +0.566] (31/32 >0). s_X[eu/unusable/late]=[-0.12, -0.03, 0.33]; s_F(X)[eu/late]=[0.01, -0.0].
- **J_NP|L51-59:** E_F^sc +1.070 [+0.594, +1.547] (25/32 >0); E_X_usability -0.219 [-0.373, -0.064] (9/32 >0); E_F +0.952 [+0.821, +1.082] (32/32 >0); raw E_X(late-eu) +0.013 [-0.164, +0.189] (19/32 >0). s_X[eu/unusable/late]=[2.06, 2.28, 2.07]; s_F(X)[eu/late]=[0.92, -0.03].
- **LOGITS:** E_F^sc +2.451 [+2.123, +2.778] (32/32 >0); E_X_usability +0.165 [-0.234, +0.565] (19/32 >0); E_F +2.091 [+1.827, +2.354] (32/32 >0); raw E_X(late-eu) -1.120 [-1.502, -0.738] (4/32 >0). s_X[eu/unusable/late]=[6.35, 6.18, 5.23]; s_F(X)[eu/late]=[2.07, -0.02].

## 4. Interpretation

**Observation (cluster=word, n=32; competence early 1.00 / late 0.99).**
- **Central signal (transformation): E_F^sc > 0.** Under the early usable codebook, X's *own* mapped letter F(X) is more readable during the carrier than its pair-partner's letter F(Y): E_F^sc = +1.07 [+0.59, +1.55] (25/32) at L51-59, +2.45 (32/32) on LOGITS. Because it is **source-conditioned** (F(X) beats F(Y) under the *same* codebook), it is not generic codebook priming. And F(X) is far more readable early than late (E_F +0.95 / +2.09, 32/32): the mapping being available before the carrier causes the transformed variable F(X) to be computed and read out during the carrier.
- **But not zero-sum.** X itself stays readable under the usable codebook (s_X ~2.06, essentially unchanged from late 2.07); the **length-matched usability control** shows only a small mapping-specific drop (E_X_usability = -0.22 [-0.37, -0.06], 9/32 at L51-59; near zero on LOGITS). So the carrier carries **both X and F(X)** -- a richer representation, not a replacement of X by F(X).
- **The control mattered.** The *raw* late-minus-early X difference is +0.45 (31/32) at L48-50 -- X looks much more readable "late." But that is dominated by the generic long-prefix effect (the early codebook prefix), present equally in the unusable control: the usability contrast strips it out and leaves only the small -0.09..-0.22 mapping-specific effect. Without the Amendment-1 control this would have been mis-read as "X drops when mapped early."

**Reading.** Mapping availability causes **precomputation/availability of the transformed variable F(X)** during the carrier, source-conditioned to X -- establishing the transformation (availability) claim under these conditions -- while X remains expressed (additive, not a zero-sum reorganization). Scope: this does not claim late use requires retained carrier information (H2/H3); one word->letter mapping family; RESID letter axis not fit (J_NP + LOGITS agree).
