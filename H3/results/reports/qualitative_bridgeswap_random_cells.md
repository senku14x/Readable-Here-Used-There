# Randomly selected cells from `bridgeswap` (seed 20260909, 6 of 48; not cherry-picked)

Prompt shape for every cell: user turn `Here is a clue: {clue}. Keep the answer to the clue in mind while you copy the following text exactly, word for word:\n\n{carrier}`; assistant turn = the carrier, teacher-forced; second user turn `Complete the fact from the clue you were given, using one word.`; the answer is scored at the first assistant token. Margin = log P(swap_answer) − log P(answer) at that token (logsumexp over surface forms); the greedy token is the raw argmax decode.

## ex-city-capital-Barcelona-Toronto|C1
- clue: *The capital of the country where Barcelona is located*  → answer **Madrid** (intermediate Spain); donor clue: *The capital of the country where Toronto is located* → Ottawa (Canada)
| condition | greedy token | margin toward swap answer (nats) | scored winner |
|---|---|---|---|
| clean | `Madrid` | -20.61 | Madrid |
| S_donor0 | `O` | +6.12 | Ottawa |
| int_tail | `Canada` | -4.00 | Madrid |
| int_clue | `Madrid` | -18.75 | Madrid |
| int_carr | `Madrid` | -18.88 | Madrid |
| int_q | `Madrid` | -13.19 | Madrid |
| ans_q | `Madrid` | -1.75 | Madrid |
| rand_tail | `Madrid` | -20.70 | Madrid |

## ex-city-capital-Naples-Barcelona|C1
- clue: *The capital of the country where Naples is located*  → answer **Rome** (intermediate Italy); donor clue: *The capital of the country where Barcelona is located* → Madrid (Spain)
| condition | greedy token | margin toward swap answer (nats) | scored winner |
|---|---|---|---|
| clean | `R` | -1.63 | Rome |
| S_donor0 | `Madrid` | +15.74 | Madrid |
| int_tail | `R` | +7.10 | Madrid |
| int_clue | `R` | +0.22 | Madrid |
| int_carr | `R` | +2.46 | Madrid |
| int_q | `R` | +1.74 | Madrid |
| ans_q | `R` | +2.10 | Madrid |
| rand_tail | `R` | -1.52 | Rome |

## ex2-city-language-Cairo|C3
- clue: *The language spoken in the country where Cairo is located*  → answer **Arabic** (intermediate Egypt); donor clue: *The language spoken in the country where Moscow is located* → Russian (Russia)
| condition | greedy token | margin toward swap answer (nats) | scored winner |
|---|---|---|---|
| clean | `Ar` | -5.75 | Arabic |
| S_donor0 | `Russian` | +18.59 | Russian |
| int_tail | `Ar` | +6.38 | Russian |
| int_clue | `Ar` | -1.56 | Arabic |
| int_carr | `Ar` | -4.50 | Arabic |
| int_q | `Ar` | -0.25 | Arabic |
| ans_q | `Russian` | +9.81 | Russian |
| rand_tail | `Ar` | -5.25 | Arabic |

## ex2-language-capital-Hungarian|C1
- clue: *The capital of the country where Hungarian is the primary language*  → answer **Budapest** (intermediate Hungary); donor clue: *The capital of the country where Polish is the primary language* → Warsaw (Poland)
| condition | greedy token | margin toward swap answer (nats) | scored winner |
|---|---|---|---|
| clean | `Bud` | -12.12 | Budapest |
| S_donor0 | `Wars` | +11.53 | Warsaw |
| int_tail | `Bud` | -3.69 | Budapest |
| int_clue | `Bud` | -10.69 | Budapest |
| int_carr | `Bud` | -11.53 | Budapest |
| int_q | `Bud` | -6.56 | Budapest |
| ans_q | `Wars` | +9.44 | Warsaw |
| rand_tail | `Bud` | -12.03 | Budapest |

## food-animal-honey|C3
- clue: *The insect that produces the sweet golden substance spread on toast*  → answer **bee** (intermediate honey); donor clue: *The animal that produces the yellow dairy spread used on bread* → cow (butter)
| condition | greedy token | margin toward swap answer (nats) | scored winner |
|---|---|---|---|
| clean | `H` | -9.58 | bee |
| S_donor0 | `Cow` | +11.76 | cow |
| int_tail | `B` | -7.58 | bee |
| int_clue | `H` | -9.57 | bee |
| int_carr | `H` | -9.34 | bee |
| int_q | `B` | -9.28 | bee |
| ans_q | `H` | +3.50 | cow |
| rand_tail | `H` | -9.26 | bee |

## ex2-city-capital-Munich|C3
- clue: *The capital of the country where Munich is located*  → answer **Berlin** (intermediate Germany); donor clue: *The capital of the country where Osaka is located* → Tokyo (Japan)
| condition | greedy token | margin toward swap answer (nats) | scored winner |
|---|---|---|---|
| clean | `Berlin` | -18.81 | Berlin |
| S_donor0 | `Tok` | +3.62 | Tokyo |
| int_tail | `Tok` | -5.81 | Berlin |
| int_clue | `Berlin` | -16.56 | Berlin |
| int_carr | `Berlin` | -16.09 | Berlin |
| int_q | `Berlin` | -12.75 | Berlin |
| ans_q | `Berlin` | -13.88 | Berlin |
| rand_tail | `Berlin` | -18.78 | Berlin |


**Endpoint note (added after the sequence rescoring).** The subword greedy tokens above are why the candidate-set flips over-counted for single-position swaps; the sequence endpoint (`two_hop_bridgeswap.md` §7) is the headline from here on, and the margins above are unchanged in sign and order under it.
