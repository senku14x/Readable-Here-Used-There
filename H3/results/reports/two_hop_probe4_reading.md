_Hand-written 2026-09-24 after reading the tables (`two_hop_probe4_tables.json`). Every number is copied from §1–5 or from the tables._

### 6.1 What the three questions answered

| question | result | registered reading |
|---|---|---|
| Did clamping only the first answer token (silly mistake 5) inflate Amendment 8's surviving share? | Clamping every scored position leaves **0.413 [0.377, 0.454]**, against 0.434 for the first token only. The difference is 0.021 (0.23 nats, 29 of 35 items) | Below the registered 0.05 correction threshold. At least 0.41 bypasses the pinned readable content at every scored answer position |
| Where does that surviving part enter? | With the last layer's read of the question tokens cut: **0.040 [0.025, 0.054]**. With only that read open: **0.330 [0.298, 0.366]** | **Direct last-layer read** |
| Is the transferred upstream content the country or the city? | Country plane alone 0.80 of the transfer push, city plane alone 0.28. Removing the country plane costs 0.73, removing the city plane 0.27. The mirror direction is the same | **Country dominant**, in both directions |

Every gate passed:

- Competence was 1.00 on every rendering type.
- The references reproduce Amendment 8 to 2 × 10⁻⁶ nats.
- Every write and clamp was exact, and the random clamp's norm matched to 5 × 10⁻⁶.
- The last layer's attention from the answer positions to the question tokens was exactly 0 under every cut row.
- The both-cuts sanity row is exactly 0.000 in every item.
- Under the new clamp, the readouts at the answer position averaged −0.04 and −0.03, with every cell within ±0.3.

### 6.2 Silly mistake 5 was small

The first-token shares show where the leak lived. With the Amendment 8 clamp at the first answer token only, the sequence share is 0.434 and the first-token share 0.411. With the clamp over every scored position, both are 0.412–0.413. The 0.02 that the first-token clamp let through came entirely from continuation tokens of multi-token spellings, and the repaired clamp removes it. The registered 0.05 threshold is not crossed, so Amendment 8's reading stands, refined from 0.43 to 0.41.

The registered rule reads the point estimate 0.413 against 0.4, and the interval's lower end, 0.377, falls below 0.4. Per item, the median is 0.40: 18 of 35 items keep at least 0.4 and none falls to 0.2 or below. The rank-matched random clamp leaves 0.605, so the clamp's effect is specific. No clamped cell flips.

### 6.3 The bypass is the last layer reading the question tokens

The final block is a full-attention layer, and its attention from the scored answer positions to the question tokens was cut exactly.

- **With that one read cut**, the clamped complement keeps 0.040 (29 of 35 items above zero). The answer positions' own state through block 62, including every direction the clamp leaves free, carries almost nothing.
- **With every answer position held entirely at clean through block 62**, all 5 120 coordinates, the last layer's read alone delivers 0.330 (35 of 35 items). The readouts at the answer position are then exactly 0.
- The interaction is 0.044. Cutting that one attention read in the final layer therefore removes about nine tenths of the surviving share: 0.373 of 0.413.
- The split holds in all six relation types: with the read cut, 0.02–0.10; through the read alone, 0.20–0.44.

For the whole question-turn change, without any removal:

- Cutting the last layer's read keeps 0.694 [0.669, 0.720].
- The read alone delivers 0.411 [0.369, 0.458].
- The two overlap by 0.11, so they are partly redundant.

About two fifths of the entire question-turn effect can reach the answer through the last layer's direct attention to the question tokens, with the answer positions untouched until then.

What the route carries is outside the 25 best-fitting lens directions on the question tokens, since those are removed in the clamped rows. It is not readable at the answer position before the last layer, since the readouts there are held at zero. It is readable at the output, because the last layer writes the answer.

### 6.4 The upstream content that transfers is the country's readable plane

In the language question, writing only the country-plane component of the capital question's change (for Lyon/Naples, the France and Italy directions) gives 0.80 of the full transfer push toward the donor's language. The city plane alone (Lyon and Naples) gives 0.28, and a random plane of the country plane's size gives 0.005. Removing the country plane leaves 0.27 and removing the city plane leaves 0.73. Both bootstrap differences exclude zero: [0.49, 0.56] for installing and [0.42, 0.50] for removing. All seven pairs agree, with the country plane alone at 0.74–0.83. The mirror direction agrees: country 0.63 and city 0.18 installed, removal costs 0.75 and 0.28.

This contrasts with the within-question result. Inside the capital question, the intermediate's plane carries only 0.19 of the capital effect. The same kind of plane, carried into a different question about the same city, delivers four fifths of what the whole change delivers there.

The readable intermediate at the question turn is the part of the state that moves a different question's answer. The answer to the asked question rides mostly on other content.

**Caveat.** The country's directions are not orthogonal to the other question's answer words. The ladder items' intermediate and answer directions have a mean cosine of 0.44, and the country and city planes have a maximum principal cosine of 0.42. So part of the country plane's push toward "Italian" may be geometric overlap with the answer's own directions, not the model deriving the language from the country.

### 6.5 Licensed

1. **The bypass holds up when every scored position is clamped.** Hold readable content at every scored answer position at clean through block 62, verified at ≈ 0. At least 0.41 [0.38, 0.45] of the question-turn effect still reaches the answer. Clamping only the first answer token had inflated this by 0.02.
2. **The surviving part enters through one read.** It is the final layer's attention from the answer positions to the question tokens. Cutting that read leaves 0.04; opening only that read gives 0.33. This holds in all six relation types.
3. **The last layer's read carries a large share of the whole effect.** Of the full question-turn effect, 0.41 can reach the answer through that read alone, and 0.69 remains with it cut.
4. **The country carries over, not the city.** What carries over from one question to another about the same city is mostly the country's readable plane, not the city's, in both directions and all seven pairs. The overlap caveat of 6.4 applies.

### 6.6 Not licensed

- **"A route no lens can read."** The last layer's write is the answer and is readable at the output. The question-token content it reads lies outside the best 25 directions, which is not shown to be unreadable by any lens.
- **"The intermediate is not used."** Within a question its readable plane carries 0.19; across questions it carries 0.80 of the transfer.
- **"The model derives the language from the country."** The overlap caveat of 6.4 is not excluded.
- **Anything beyond one hybrid model**, with thinking off, one question wording and fixed state trajectories.

### 6.7 What it means for the H3 statement, in one paragraph

At the question turn of this two-hop organism:

- Most of the answer effect lies outside the best Jacobian-lens directions. Removing them keeps 0.61; removing random directions keeps 0.96.
- The readable leverage is the answer's more than the intermediate's, 0.37 against 0.19, and the state already carries the answer.
- About two fifths of the effect reaches the answer through the final layer's direct attention to the question tokens. It bypasses the readable content at the answer position, which can be held at zero without stopping it.
- The part of the state that carries over to a different question about the same city is the readable country.

The readable intermediate is therefore a poor guide to how this question's answer is produced. It is a good guide to what carries over to a neighbouring question.

### 6.8 Next decision (candidates, none registered)

1. **Check the overlap caveat of 6.4.** Install the country plane after projecting out the other question's answer directions.
2. **Test whether the last-layer read is special.** Cut the same read at each earlier full-attention layer (43, 47, 51, 55, 59), one at a time.
3. **Run the route split on the dense model** once the researcher allows it. There the middle layers can be cut too.
4. **Write the consolidated H3 section.** It is drafted in `two_hop_question_turn_ladder.md`.
