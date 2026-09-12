# H1 · tagged_categories — does the tagged instruction select category-associated content that is never a token in the prompt?

**Spec sections 2.4 (categories), 2.5 (tagged selection), 3.2 (category materials), 4.3 (category metrics), 6 (scope ladder: words → explicit categories → inferred categories).** Script `H1/scripts/tagged_categories.py` (stages `gate`, `select`, `directions`, later `exemplar`); analysis `tagged_categories_analysis.py`. Outputs `H1/outputs/tagged_categories/`; results `H1/results/tagged_categories_<stage>.md`. Status: design, registered before any forward. Nothing below has been run.

## 1. Why this experiment now

Every selection result so far (`tagged_selection_evaluate.md`, `competition_and_cue.md`) scores a word that is literally present in the prompt. The pointed source's transfer could be lexical: the quoted token is copied forward through the source span and the pointer amplifies that copy. Nothing yet says whether the instruction selects *content associated with* the source or only the token. The project's scope ladder puts explicit categories next for exactly this reason: a category label lets us score members that never occur in the prompt, so member readability cannot be a token echo of the source.

The question is: under the tagged instruction, does the pointed category's **member aggregate** transfer more than the unpointed categories' member aggregates, with the same selective profile (pointed up, unpointed suppressed) found for words?

## 2. Organism (the category organisms wording carried into the §2.5 tagged form)

User turn, pointed arm (T ∈ {A, B, C}):

```
Here are three categories: (A) "{c1}", (B) "{c2}", (C) "{c3}". Keep the category tagged {T} in mind while you copy the following text exactly, word for word:

{carrier}
```

Control arm: `Here are three categories: (A) "{c1}", (B) "{c2}", (C) "{c3}". Those categories occur one time. Now copy the following text exactly, word for word:\n\n{carrier}`. Assistant turn: the carrier, teacher-forced. Labels are quoted exactly as in the project's §2.4 prompt and the word organism, so a word-versus-category comparison is not confounded by presentation (presentation is H1.7's factor, not this experiment's). No member and no exemplar appears anywhere in the rendered prompt; asserted at render for every cell.

Natural gate organism (Stage 0): the named-category maintain / control prompts verbatim, single category, plus an absent condition (no category sentence).

## 3. Materials (frozen before the first forward; everything here was checked with the tokenizer, `instrument_gates_result.json` part A)

**Eligible categories (K = 4 single-token unshown members, leading-space form, in the project's candidate order):**

| Category | Scored members (K = 4) | Quoted-label tokens | Bank overlap of members |
|---|---|---|---|
| birds | owl, duck, goose, pigeon | 3 | — |
| fish | cod, carp, bass, perch | 3 | — |
| insects | beetle, moth, fly, mosquito | 3 | — |
| tools | hammer, saw, drill, axe | 3 | hammer (Package 1 decoy) |
| vehicles | car, bicycle, motorcycle, scooter | 3 | — |
| furniture | desk, bed, stool, dresser | 3 | — |
| mammals | horse, rabbit, mouse, camel | 5 | horse (decoy), camel (fit word 11) |
| vegetables | cabbage, spinach, broccoli, celery | 4 | — |

The other eight spec categories (reptiles, citrus fruits, nuts, flowers, trees, musical instruments, gemstones, ocean creatures) fail K = 4 under this tokenizer and are ineligible; not silently reduced (the category materials). All eight eligible labels are single tokens in leading-space form, so **label readability** is scored separately (the category member aggregate) as the leading-space token, the same construction used for quoted words in the word organism (disclosed: the token inside the quotes is the no-space form).

**Geometry.** Source replacement needs donor and recipient spans of equal token count. Six labels are 3 tokens in the quoted span; `"mammals"` is 5 and `"vegetables"` is 4 with no matched donor among eligible categories. Per the project conventions (matched source geometry unavailable → flag, do not crop), mammals and vegetables enter **readout-only rows** (natural selectivity, no replacement) and the Stage 0 gate; the six 3-token categories are the source-replacement set.

**Triples (source-replacement set, registered rule).** Superclasses: animals A = {birds, fish, insects}, artifacts R = {tools, vehicles, furniture}. Three mixed partitions by the diagonal rule (animal i swapped with artifact i): P1 = (fish, insects, tools | vehicles, furniture, birds); P2 = (birds, insects, vehicles | tools, furniture, fish); P3 = (birds, fish, furniture | tools, vehicles, insects). Plus the pure partition P0 = (birds, fish, insects | tools, vehicles, furniture) for the within-superclass confusion diagnostic. Eight triples; each category appears in four. Triples share identities, so **two clusterings are reported: cluster = triple (n = 8, the design's unit) and cluster = category (n = 6, conservative, identity-level)**; a claim needs both.

**Readout-only triples:** (mammals, vegetables, tools), (mammals, vegetables, vehicles).

**Donors.** For source slot j of a triple, the donor is the category at slot j of the partner triple in the same partition (disjoint by construction, geometry-matched, fixed before outcomes). Each donor rendering is a clean forward under the same arm.

**Carriers.** C2 contains "birds" and is excluded for every category by the project's textual rule (a declared common uncontaminated set, §B1); C0, C1, C3 contain no eligible label or scored member (checked; `cabinet` was already removed from furniture for C3). Carriers = C0, C1, C3 for every row. There is no pilot/evaluation materials split: six geometry-uniform categories cannot be halved, so this is one registered run at extension scale, disclosed as such; the word-organism pilot → evaluation discipline does not transfer here.

**Decoys.** The eight fitting words anchor…bridge, none of which is a scored member (camel is fitting word 11 and is not a decoy).

**Rotations.** Three cyclic rotations per triple, so each category occupies each ordinal position once.

## 4. Stages, conditions, interventions

**Stage 0 — natural gate (member instrument positive control, the conditional supporting experiments "category modules follow their own natural gate").** Eight eligible categories × carriers C0, C1, C3 × {maintain, control, absent}. Endpoint: member-aggregate presence s̄_J(c) = mean over the four members of z_w − mean z_decoys at interior positions, and label presence. Decision rule: the member aggregate under maintain must exceed absent (cluster = category, n = 8, sign count ≥ 6/8, CI clear of 0) at at least one of the two windows. If it does not, the member instrument has no demonstrated sensitivity on this organism and Stage 1 is read **on the label endpoint only**, with the member rows retained as "instrument not validated" (the conditional supporting experiments: diagnose the measurement rather than declare no abstraction). Maintain vs control is reported but not gating (Package 1 showed the control sits below a bare mention for words).

**Stage 1 — selection (primary).** Eight triples × 3 rotations × 3 carriers × arms {pointed A, B, C, control}. Per arm: clean forward; source replacement for each j (span block outputs ← donor from block 36 onward, L_x frozen); same-source gate at j = 1 (bitwise equal to clean); layers < 36 identity asserted; damage on every intervened forward. Readout-only triples: clean forwards under the four arms only.

**Stage 2 — directions (secondary, run only if Stage 1 gives S_member ≠ 0 or a clear label S).** Under each pointed arm, three level moves at block 35 on interior positions, clean-derived α_t, crossed with the three replacements: (i) ĝ (word-fit, `task_state_modulation/G.npz`, cross-organism, disclosed); (ii) d_shared word-fit (`tagged_selection` evaluate fit); (iii) d_shared category-fit, fold = the partner triple's clean runs only (pointed − control, all tags, rotations, carriers), so both evaluated identities and the third are excluded (the category materials); folds overlap across partitions, disclosed. Realized-write ρ/κ and damage on every move. The category-fit direction is also applied to the eight word evaluation triples (existing organism, C2/C3) for the the conditional supporting experiments 2×2 (word-fit on category source / category-fit on word source).

**Stage 3 — exemplar regime (gated, later).** Inference gate first: the `What do "{e1}", "{e2}", "{e3}" have in common? Answer in one or two words.` prompt, greedy decode, with aliases frozen now: birds {birds, bird}; fish {fish, fishes}; insects {insects, insect, bugs}; tools {tools, tool, hand tools}; vehicles {vehicles, vehicle, transportation, transport, modes of transport}; furniture {furniture, furnishings}; mammals {mammals, animals, African animals, zoo animals, safari animals, wild animals}; vegetables {vegetables, vegetable, veggies, root vegetables}. A category that fails the gate is retained as a failure and excluded from exemplar claims. Exemplar lists have unequal token geometry across categories (exemplar tokens per category range 3–5), so the exemplar stage is **readout-only** (S_nat on members) unless a geometry-matched donor pair exists; any replacement rows there are an explicitly separate alignment study. Designed here so the aliases predate any outcome; scheduled after Stage 1 is read.

## 5. Measurements

Per forward, interior carrier positions, lens layers 0–62 saved; windows L48–50 and L51–59 co-primary (Holm).

- **Member aggregate** (the category member aggregate, primary category endpoint): s̄_J(c) = ¼ Σ_{w∈M_c} (z_w − mean z_decoys); pair margin m_j = s̄_J(Y_j) − s̄_J(X_j) (decoys cancel); per-member distribution saved; **max-member** and **any-member top-k** as sensitivity diagnostics with K = 4 and the aggregation order stated (mean over positions then max over members).
- **Label** endpoint: the same quantities on the leading-space label tokens.
- **RESID_P category variant** (the plain-sentence axis): per-member plain-sentence centroids from templates 1–8 (existing fitter, slot-position target), category centroid = mean of its four member centroids, pair axis = unit(μ_Y − μ_X), validated on templates 9–12 (context holdout; member holdout is not available at K = 4 and is not claimed).
- **LOGITS**: output log-prob margin of member sets and of labels.
- Transfer C_j(r) = m_j(swap j) − m_j(no swap) under relevance r ∈ {A, B, C, control}, on the member endpoint and on the label endpoint separately.
- Confusion: for P0 rows, the member-aggregate presence of each *unpointed* category under the pointer, split by whether it shares the pointed category's superclass.

## 6. Estimands and statistics

As in `tagged_selection.md` §6, computed separately for the member and label endpoints: S (pointed − unpointed transfer), Q (unpointed − control), U (pointed − control), S_nat, and for Stage 2 the profile index P and the 2×2 transfer table. Cluster-t intervals, sign counts, per-cluster values, both clusterings (triple n = 8; category n = 6), both windows as one Holm family per estimand, ratios with numerator and denominator.

## 7. Predictions, stated before the run

| Quantity | Lexical echo only | Selection of associated content | Instrument insensitive |
|---|---|---|---|
| Stage 0 members, maintain vs absent | > 0 (label primes members) or ≈ 0 | > 0 | ≈ 0 |
| S on label | > 0 (as for words) | > 0 | > 0 |
| S on members | ≈ 0 | > 0, Q ≤ 0 | ≈ 0 (uninterpretable) |
| S on members, P0 vs mixed triples | — | smaller within-superclass (confusion) | — |
| word-fit d_shared on category source | scales label only | selective on pointed members too | — |

The primary contrast is S on the member endpoint, conditional on the Stage 0 gate. The label endpoint replicates the word result on a new lexical set and is not the abstraction claim.

## 8. Interpretation rules

- Gate passes and S_member > 0 with Q_member ≤ 0 (both clusterings, both or either window under Holm): the instruction selects category-associated content, not only the source token, on this organism and readout. Scoped to explicit named categories, quoted presentation, this rendering.
- Gate passes and S_member ≈ 0 (equivalence band ±20 % of U_member, 90 % interval) while S_label > 0: the pointer amplifies the token and not its associates here; "selection" in H1 is lexical at this readout. That is a real result and stays.
- Gate fails: no member claim either way; report the label rows and the diagnosis of the member instrument (per-member distribution, max-member) before any redesign.
- Within-superclass confusion reduces S in P0 rows: reported as a scope limit on category distinctness, not as evidence against selection.
- Any gate failure (render, same-source, geometry, ρ/κ, damage) is repaired and re-run; nothing scored is deleted.

## 9. Budget

Stage 0: 8 × 3 × 3 = 72 forwards. Stage 1: 8 triples × 3 rotations × 3 carriers × 4 arms × (1 clean + 3 swaps + 1 same-source) = 1,440, donors 8 × 3 × 3 × 4 × 3 = 864, readout-only 2 × 3 × 3 × 4 = 72; ≈ 2,400. Stage 2: 8 × 3 × 3 × 3 arms × (1 + 3) × 3 directions = 2,592, plus the category-fit direction on the word organism 8 × 3 × 2 × 3 × 4 = 576. RESID_P member centroids: 32 members × 12 templates short forwards. Total ≈ 5,700 forwards, about 35 minutes of compute; Stage 2 runs only after Stage 1 is read.

## 10. What is not claimed from this experiment

Nothing about behavior; nothing about inferred categories until Stage 3; nothing about presentation or wording (H1.7); nothing about a controller's location; no claim that a category label "represents" its members — the endpoint is member readability at the lens. Eight triples over six shared identities are an extension-scale design, not the project's evaluation-scale independence.

## 11. Execution and analysis notes (added 2026-09-07 at handoff; run launched, analysis not yet written)

**Run state.** `run_tagged_categories.sh` runs `gate` then `select`. Outputs: `raw_gate.npz`/`meta_gate.json`, `raw_select.npz`/`meta_select.json`, `resid_axis_categories.npz` (member centroids), `manifest_*.json`. Raw keys per record `<tag>|z` [63, P, 48 cols] float16 (columns = 32 members, 8 labels, 8 decoys in `meta["columns"]`), `|lp` [P, 48] output log-probs, `|p_pair{j}` [63, P] category pair-axis projection, `|rank` [36, P, 15] (3 labels then 12 members, layers 24–59), `|g35`, `|dshw35` (word-fit ĝ and d_shared coordinates), `|h35mean` (clean cells only; for the category-fit direction), `|nll`, `|top1`. Cell tags: `gate|{ck}|{cat}|{maintain|mention|absent}`, `sel|{ck}|T{ti}|rot{r}|{A|B|C|ctrl}|{clean|swap0|swap1|swap2}`, `ro|{ck}|R{ti}|rot{r}|{arm}|clean`. `meta["cells"][tag]["cats"]` gives the rotated category order; `["donor"][j]` the donor category for slot j.

**Analysis script `tagged_categories_analysis.py`** (template: `tagged_selection_analysis.py`), one pass:
1. Member aggregate s̄(c) = mean over the 4 members of (z_w − mean z_decoys) per layer/position; label presence likewise on the label column. Report both endpoints everywhere.
2. Gate tables: maintain − absent, maintain − mention, mention − absent on members and labels, cluster = category (n = 8), both windows, sign counts, per-category values; per-member distribution and max-member. Apply §4's gate rule and print PASS/FAIL per window.
3. Selection: for each cell and slot j, m_j = s̄(donor_j) − s̄(X_j) on members (decoys cancel), label margin, RESID_P `p_pair{j}` mean over window, LOGITS margin = mean lp(donor members) − mean lp(X members) and labels. C_j(arm) = m_j(swap j) − m_j(clean). Average rotations and carriers within triple; index relevance by category identity. S, Q, U, S_nat as in `tagged_selection.md` §6; **two clusterings**: triple (n = 8) and category (n = 6, each category's own pointed/unpointed values averaged over the triples containing it). P0 (pure partition, triples 0–1) vs mixed (2–7) confusion split.
4. Readout-only rows: S_nat on members for mammals/vegetables.
5. Figures: `figures/tagged_categories_S_by_layer.png` (member and label S per layer), `figures/tagged_categories_members.png` (per-member C under pointed vs unpointed).

**Decision tree for section 5.**
- Gate FAIL at both windows → write "member instrument not validated"; report label S only; do **not** run Stage 2; next = diagnose the member instrument (per-member distribution; try the max-member endpoint as a registered sensitivity; consider a member-context RESID_P read at L51–59 only) before any redesign.
- Gate PASS, S_member > 0 with Q_member ≤ 0 in both clusterings → selection of associated content licensed (scope: named categories, quoted, this rendering). Run Stage 2 (`directions`, script stage modelled on `tagged_selection.py` Stage B: moves along ĝ, word-fit d_shared, category-fit d_shared with partner-triple folds from `h35mean`; also category-fit d_shared on the eight word triples of `tagged_selection` evaluate) and fill the project's 2×2.
- Gate PASS, S_member ≈ 0 (equivalence band ±20 % U_member, 90 % CI) with S_label > 0 → "selection is lexical at this readout"; no Stage 2; next = scaffold_generality with that scope stated.
- S clear in one clustering only → report as "triple-level only" / "category-level only", no licensed claim; do not add triples (the identity set is exhausted).
- Then Stage 3 (exemplar): run the inference gate prompt (greedy, ≤ 4 new tokens, aliases in §4) on the eight categories; readout-only tagged exemplar battery on gate-passing categories; S_nat on members is the only endpoint.
