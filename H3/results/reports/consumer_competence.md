# H3 · consumer_competence — is there a tagged codebook consumer at all? (calibration)

## 1. Question and setup

Every H3 experiment needs a consumer whose clean answer depends on the *selected* source. Before any intervention: does the tagged organism, followed by a codebook turn and a query that never restates the tag, produce a bare letter, and is it the pointed word's letter?

Organism unchanged from H1 (`Here are three words: (A) "X1", (B) "X2", (C) "X3". Keep the word tagged {T} in mind while you copy…` + teacher-forced carrier), then a second user turn: a six-entry codebook covering the three sources **and their three donors**, followed by one of three candidate query wordings. Letters `B D F H K M Q V`; letter assignment and entry order permuted independently of identity, seeded per cell. Calibration materials only: evaluation triples 0–1, carriers C0/C1, three rotations, all three tags, three wordings = 108 forwards, 60 s. Evaluation triples 2–7 and carriers C2/C3 untouched.

Endpoints: greedy answer is a bare letter; greedy answer equals the pointed word's letter; forced-choice margin b = log P(pointed letter) − max over the two unpointed sources' letters; and the same against all eight letters.

## 2. Findings

| query wording | bare letter | greedy accuracy | forced vs unpointed | forced vs all 8 | mean b (nats) |
|---|---|---|---|---|---|
| "the word you were instructed to keep in mind" | 1.00 | 1.00 | 1.00 | 1.00 | 5.35 |
| "the word you kept in mind" | 1.00 | 1.00 | 1.00 | 1.00 | 5.45 |
| "the tagged word you were asked to keep in mind" | 1.00 | 1.00 | 1.00 | 1.00 | 5.55 |

Accuracy is 1.00 for every tag (A, B, C) under every wording; n = 36 cells per wording.

## 3. Verification and limitations

- Rendering gates passed for every cell (three quoted source spans, both carrier occurrences, the appended turns); answer position is the last token; letters verified single-token in both bare and leading-space forms and scored at the better form.
- Donors are in the codebook, so a later source-replacement condition has a defined counterfactual answer.
- **Ceiling.** Accuracy cannot move upward and has little room to move downward before an intervention counts as damage: the margin b (≈ 5.4 nats) is the endpoint with dynamic range, not accuracy. Any registered design must report b and donor-flip rate, not accuracy alone.
- Calibration scale: 2 triples × 2 carriers × 3 rotations. This establishes that a consumer exists, not an effect size.
- The query is answerable by re-reading the source words and the tag from the prompt. That is exactly what the boundary controls exist to test; a null on a representation ladder here would be uninformative without them.

## 4. Next decision

A competent consumer exists on the tagged organism with all three wordings, so wording is not the bottleneck. Freeze one wording (the "tagged word" variant has the largest margin; the "instructed" variant is the plan's §2 default and does not restate the tag either) and proceed to the `selection_to_behavior` factorial: pointer-region transplant × source replacement, scoring b and the donor-flip profile beside the internal C_j on the same forwards.
