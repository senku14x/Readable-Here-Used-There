_Hand-written 2026-09-24 after reading the tables (`two_hop_probe3_tables.json`). Every number is copied from §1–6 or the tables. The flip counts for row (c) were counted from the raw file for this section and are secondary to the margins._

### 7.1 What the three rows answered

| row | question it was registered to answer | registered reading |
|---|---|---|
| (a) both readable planes removed | Is the intermediate's readable handle separate from the answer's, or inside it? | **partly shared**: about three quarters of the intermediate plane's effect is also carried by the answer plane |
| (b) verified clamp at the answer position | Was Stage 2's surviving half a route the lens cannot read, or a leaky clamp? | **a route that bypasses the pinned readable content carries at least 0.43** of the effect, bracketed at [0.43, 0.51] with Stage 2 |
| (c) relation transfer | Does the question-turn state carry the country or the answer? | **both**: upstream content that another question can use, and answer content strong enough to flip its own answer's ordering inside the other question |

Every gate passed. Competence was 1.00 on all six rendering types. The five same-run reference rows reproduce Stage 2 exactly, with a maximum difference of 0.0 nats, and the pursuit selected identical atoms. Every write and clamp was exact, and the random clamp's norm matched to within 3 × 10⁻⁶. Gate V passed: under the stronger clamp the readouts at the answer position averaged −0.04 for the intermediate pair and −0.03 for the answer pair, and every cell stayed within ±0.3.

### 7.2 Row (a): the two readable handles mostly overlap

Removing the intermediate plane costs 0.21 of the effect, removing the answer plane costs 0.38, and removing both costs 0.43. The both-removed share is 0.566, with interval [0.517, 0.614]. If the two planes carried separate parts, it would be 0.418; if the intermediate's part sat entirely inside the answer's, it would be 0.623. The overlap fraction is **0.72 [0.64, 0.79]**. Its interval includes 0.75, so by the run registration the reading is "partly shared", not "nested". The intermediate plane adds only 0.057 of the effect beyond what the answer plane already removes. The random 4-frame control keeps 0.968.

The two binary tests in the original registration disagree at their margins. The "separate" test (D ≤ B_ans − 0.05) passes by 0.007, and the "nested" test (|D − B_ans| ≤ 0.05) fails by 0.007. Both are reported as written. The overlap fraction is the quantitative answer, and it says "mostly shared".

The intermediate's and the answer's folded directions have a mean cosine of 0.44 at L51–59, so part of the overlap is geometric. Per relation, the overlap is 0.81 for city→capital, 0.64 for language→capital, 0.63 for river→capital and 0.91 for the three language items. It is 0.23 for currency, but there the intermediate plane's own effect is small, a removal cost of 0.08, so the fraction is noisy.

### 7.3 Row (b): the verified clamp leaves 0.43

With the four words' readouts at the answer position held at clean through block 62, **0.434 [0.396, 0.476]** of the question-turn effect still reaches the answer. The un-clamped share is 0.612 and Stage 2's partial clamp left 0.511. The rank-matched random clamp leaves 0.605, so the stronger clamp's effect is specific. It removes 0.87 nats beyond the partial clamp [0.69, 1.05], in 35 of 35 items. Per item, the median share is 0.45: 19 of 35 items keep at least 0.4 and none falls to 0.2 or below. No clamped cell flips, 0 of 140.

The registered rule reads the point estimate against 0.4. The point estimate clears it, but the interval's lower end, 0.396, touches it. Per relation, the share runs from 0.25 for the three language items to 0.54 for currency, with the other relations at 0.43–0.50.

What was pinned defines what the reading means. The pinned span has a median rank of 58, with a range of 36–116. It contains every single-token form of the four words and their aliases, their translations (median 18 per item), and the 25 atoms that best fit the donor's change at the answer position. Readable directions outside that span were not pinned.

The final block, which is outside every clamp, still writes the answer direction at the answer position under the clamp. Its answer-pair projection is +10.1, against +20.0 without the clamp and +35.0 for the full donor. Its intermediate-pair projection is +2.7, against +11.5 without the clamp and +26.1 for the full donor. So the surviving route turns into an answer write in the final block. It is not identified whether that block reads the route from the answer position's unpinned directions or directly from the question tokens.

### 7.4 Row (c): the question-turn state carries the answer and something upstream of it

- **Capital state into the language question.** It pushes toward the donor's language by 6.75 nats [6.07, 7.42], in 7 of 7 pairs. The language question's own change pushes by 10.98, and the random control by 0.14. That gives **f_L = 0.61 [0.54, 0.69]**, and the registered reading is "upstream content present". The same transplant pushes the language question toward the donor's *capital* by 9.87, which is 0.84 of the capital question's own push. It reverses the capital ordering in 26 of 28 cells but never the language answer, 0 of 28.
- **Language state into the capital question (the mirror).** It pushes toward the donor's capital by 5.27 [4.39, 6.14], in 7 of 7 pairs, against 11.77 native and 0.18 random. That gives **f_C = 0.45 [0.38, 0.50]**, again "upstream content present". It pushes the capital question toward the donor's *language* by 10.55, 0.96 of the language question's own push. It reverses the language ordering in 26 of 28 cells and never the capital answer.
- **Consistency.** The content of each change looks the same whichever question it is written into. The capital change carries capital content, 9.87 in the language rendering and 11.77 native, plus language content, 6.75 and 7.68. The language change carries language content, 10.98 native and 10.55, plus capital content, 4.70 and 5.27. Each change carries more of its own answer than of the other's, and a sizeable amount of both.
- **Scope, as registered.** Row (c) separates answer content from content upstream of the answer. It cannot tell the country apart from the cue city it came from.

### 7.5 Licensed

1. **Answer content is present at the question turn.** The state written while reading a capital clue carries the capital strongly enough that, pasted into a language question, it reverses the capital ordering in 26 of 28 cells. The mirror is the same for the language. "The answer is already computed by the question turn" is supported as a component.
2. **It is not the only content.** The same states move the other question's answer by 0.45–0.61 of that question's own change, in 7 of 7 pairs, with random controls under 0.02 of native. "Only the answer is carried" is excluded.
3. **The readable handles overlap.** About three quarters, 0.72 [0.64, 0.79], of the intermediate plane's effect on the answer is also carried by the answer plane.
4. **A route bypasses the pinned readable content at the answer position.** Hold the intermediate's and the answer's readable directions at the answer position at clean, verified at ≈ 0, along with their translations and the 25 best-fitting atoms, through block 62. At least 0.43 of the question-turn effect still reaches the answer, bracketed at [0.43, 0.51] with Stage 2's partial clamp. The route enters the output as an answer write in the final block.
5. **Regime.** Every gate passed, and Stage 2 reproduces exactly on the same cells.

### 7.6 Not licensed

- **"A route no lens can read."** Readable directions outside the pinned span were not pinned. The route becomes a readable answer write in the final block, and the question-tokens-to-final-block path was not cut.
- **"The intermediate plays no role."** The intermediate plane keeps 0.28 of its effect as its own, and row (c)'s upstream content could be the country.
- **"The country, not the city, is carried."** Row (c) cannot separate them.
- Anything beyond one model, thinking off, one question wording, same-template minimal-pair donors and fixed state trajectories.
- Per-relation claims beyond description, on 1–11 items per type.

### 7.7 What it means for the H3 statement, in one paragraph

At the question turn of this two-hop organism, the state already contains the answer: enough of it that a different question reads it out. It also contains something upstream of the answer that a different question can reuse at about half strength. Of the intermediate's readable handle on the answer, about three quarters is shared with the answer's own. Holding the intermediate's and the answer's readable content at the answer position fixed, including translations and the directions most tied to the donor's change, still leaves at least 0.43 of the effect. That part reaches the output only through the final block's answer write. The answer-precomputed reading and the bypass reading are both partly right: the answer is present early, and a substantial share of its effect does not pass through the readable directions at the answer position before the last block.

### 7.8 Next decision (candidates, none registered)

1. **Where the bypass enters the final block.** Compare a clamp of the final block's attention and linear-attention reads from the question tokens at the answer position with a clamp of the answer position's own unpinned directions. On this hybrid model the linear-attention channel makes a complete cut hard; the project's pure-attention replication model is the cleaner place for it.
2. **Country or city in row (c).** Answer-level endpoints cannot separate them, because the city fixes the country and a same-country pair shares both answers. Two routes could: read the cue city and the country with the lens on the transplanted question tokens, or add a relation that depends on the city itself rather than its country.
3. **Write-up.** Stages 1 and 2 and this run close the question-turn ladder for this organism. A consolidated H3 section is the natural next deliverable.
