# Prose Rules: The Line-Edit Checklist

Sentence- and word-level rules, mostly from Ethan Perez's tips with additions from Sebastian Farquhar. Apply these to every piece of paper prose — text you draft, text you edit, and as an audit list when reviewing the user's writing. The rules exist to cut the reader's cognitive load; when a rule conflicts with technical precision, precision wins, but flag the conflict rather than deciding silently.

## Sentence mechanics

- **Put the verb early.** Sentences parse faster when the reader hits the verb before the subject's third prepositional phrase. Restructure front-loaded noun piles.
- **One sentence, one idea.** A long sentence packed with content splits into two. A long sentence is fine only when its words are simple and it carries one idea.
- **Make the thing you care about the subject of the main clause.** If the paper is about the probe, the probe does things; it does not appear in a subordinate clause of a sentence about the dataset.
- **Active voice with an explicit actor.** "We find X", not "X was found". Passive constructions hide who did what, and reviewers notice.
- **Vary sentence openers.** Even so, do not start every sentence with "We".
- **Unfold possessives** where it improves flow: "X's Y" often reads better as "the Y of X", especially when X is long or abstract.

## Word choice

- **Prefer short, common words.** Fewer syllables, same meaning: "use" over "utilize", "show" over "demonstrate" (where the meaning allows).
- **Never use a comparative without a referent.** "Improves", "better", "faster" — than what? Every comparative names both sides of the comparison, explicitly. This includes implicit comparatives hiding in verbs.
- **Cut hedges** ("may", "can", "might", "could potentially") unless the uncertainty is the actual claim. A paper full of hedges says nothing. When hedging is warranted, hedge once, precisely ("suggestive evidence that"), and calibrate it to the evidence.
- **No scare quotes.** Words in quotation marks smuggle in imprecise or dodgy meanings. Either commit to the word or find the precise one.
- **Expand contractions.** "It's" becomes "it is" in formal manuscripts.
- **Replace wishful verbs.** "We want to show" and "we hope to demonstrate" describe intentions, not results. State what the paper does.
- **Don't repeat similar-sounding words in one sentence.** It reads clumsy and suggests the sentence has one idea wearing two hats.

**Delete on sight** (they add no information): actually, a bit, fortunately, note that, observe that, try to, very, really, extremely, "to our knowledge", and most connectives ("However", "Moreover", "Furthermore") — if the logical relation between sentences is real, the content shows it.

## Pronouns

- **Minimize "this", "it", "these", "those".** Each bare pronoun forces the reader to resolve a reference. When a pronoun is unavoidable, use it as an adjective attached to a noun — "this result", "these ablations" — never bare.

## Paragraphs

- **Lead and end strong.** The first and last sentences of a paragraph carry the point; middle sentences elaborate. Skimming readers read only the edges — most information should survive that reading.
- **Every sentence must add information.** For each sentence ask: is it necessary? Can it be said more simply? If a sentence restates its neighbor, delete one.
- **Every sentence must be true.** Separately from style, check each sentence's factual accuracy against the results it describes. Text that misdescribes its own figures is a common and embarrassing failure.

## Terminology

- **Define unusual terms at first use.** Standard field-wide concepts need no definition (a transformer, an LLM); anything newer or narrower does (a specific probe type, a niche metric). Err toward defining.

## Honesty and calibration

- **Claim exactly what the evidence supports** — no more (overclaiming) and no less (burying a solid result under reflexive hedging).
- **Don't dress up simple methods.** Plain description of a simple, effective method beats inflated framing of the same method. Sciency language is role-playing; readers with taste can tell.

## Layout and polish

- **No single-word lines.** A paragraph ending with one word on its own line wastes space and looks bad; shorten a sentence in that paragraph.
- **Minimize whitespace** across figures, captions, and headers — it buys content under a page limit.
- **Run a real typo checker** before submission. Overleaf's checking misses things that dedicated tools catch.
- **Cut in the right order:** first words, then sentences, then subsections. Do not over-compress everything into uniformly dense sentences — past a point, fewer, better-chosen ideas beat maximal compression.
- **Read the paper aloud** (or, as the editor, simulate it). Awkward rhythm and ambiguity surface when heard.

## Plots and figures (typography level — see structure.md for figure design)

- Axis tick and label fonts at least as large as body text.
- Colorblind-safe, perceptually uniform colormaps (viridis-style). For signed data with a meaningful zero, use a diverging map that is white at zero (RdBu-style). Never encode key information in red-versus-green.
- Vector graphics (PDF/SVG) so readers can zoom; consistent font sizes; legible in grayscale.

## Attention economics

- Put an eye-catching figure on the first page; many readers decide from page one alone.
- Budget roughly equal time on the title, the abstract, the intro, and the rest of the paper — proportional to how many people read each. The announcement thread or blog post deserves the same treatment.
