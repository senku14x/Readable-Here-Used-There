"""Build the Stage 2 two-hop item bank (Amendment 7) from templated relation families with constructed, length-matched donors.

Each family has a clue template with one cue slot; a cue maps to an intermediate entity which maps to the answer. An item is an
ordered pair (A, B) of cues in the same family with different intermediates and different answers whose clue bodies tokenize to
the same number of tokens (the donor geometry gate of the battery); the item's clue is the template with cue A, its donor clue is
the template with cue B, swap_to = B's intermediate, swap_answer = B's answer. Every intermediate, swap_to, answer and swap_answer
must be a single token in leading-space form (Amendment 6 §1); the answer word must not occur in either clue. Tokenizer only,
no forward. Writes H3/design_specs/two_hop_items_stage2.json and prints the bank. Usage: two_hop_items_stage2_build.py
"""
import os, sys, json, itertools, collections
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "..", "common", "scripts"))
import registry as R, rendering as Rn

tok = R.make_tokenizer()
ntok = lambda s: len(tok(s, add_special_tokens=False).input_ids)
single = lambda w: Rn.single_token_id(tok, w) is not None

# (cue, intermediate, answer) per family; templates carry "Fact: " and end in "is"/"is the" as the released items do
FAMILIES = {
    "city-capital": ("Fact: The capital of the country where {cue} is located is", [
        ("Barcelona", "Spain", "Madrid"), ("Toronto", "Canada", "Ottawa"), ("Lyon", "France", "Paris"), ("Naples", "Italy", "Rome"), ("Munich", "Germany", "Berlin"), ("Osaka", "Japan", "Tokyo"),
        ("Marseille", "France", "Paris"), ("Milan", "Italy", "Rome"), ("Vancouver", "Canada", "Ottawa"), ("Seville", "Spain", "Madrid"), ("Hamburg", "Germany", "Berlin"), ("Kyoto", "Japan", "Tokyo"),
        ("Krakow", "Poland", "Warsaw"), ("Porto", "Portugal", "Lisbon"), ("Antalya", "Turkey", "Ankara"), ("Mumbai", "India", "Delhi"), ("Shanghai", "China", "Beijing"), ("Melbourne", "Australia", "Canberra"),
        ("Gothenburg", "Sweden", "Stockholm"), ("Bergen", "Norway", "Oslo"), ("Rotterdam", "Netherlands", "Amsterdam"), ("Antwerp", "Belgium", "Brussels"), ("Salzburg", "Austria", "Vienna"), ("Cork", "Ireland", "Dublin"),
        ("Busan", "Korea", "Seoul"), ("Isfahan", "Iran", "Tehran"), ("Tampere", "Finland", "Helsinki"), ("Aarhus", "Denmark", "Copenhagen")]),
    "city-language": ("Fact: The language spoken in the country where {cue} is located is", [
        ("Lyon", "France", "French"), ("Naples", "Italy", "Italian"), ("Munich", "Germany", "German"), ("Osaka", "Japan", "Japanese"), ("Cairo", "Egypt", "Arabic"), ("Moscow", "Russia", "Russian"),
        ("Seville", "Spain", "Spanish"), ("Krakow", "Poland", "Polish"), ("Porto", "Portugal", "Portuguese"), ("Antalya", "Turkey", "Turkish"), ("Gothenburg", "Sweden", "Swedish"), ("Bergen", "Norway", "Norwegian"),
        ("Aarhus", "Denmark", "Danish"), ("Rotterdam", "Netherlands", "Dutch"), ("Busan", "Korea", "Korean"), ("Shanghai", "China", "Chinese"), ("Hanoi", "Vietnam", "Vietnamese"), ("Bangkok", "Thailand", "Thai"),
        ("Tampere", "Finland", "Finnish"), ("Brno", "Czechia", "Czech"), ("Debrecen", "Hungary", "Hungarian"), ("Thessaloniki", "Greece", "Greek"), ("Isfahan", "Iran", "Persian"), ("Milan", "Italy", "Italian")]),
    "river-capital": ("Fact: The capital of the country where the {cue} River reaches the sea is", [
        ("Thames", "England", "London"), ("Seine", "France", "Paris"), ("Tiber", "Italy", "Rome"), ("Nile", "Egypt", "Cairo"), ("Volga", "Russia", "Moscow"), ("Vistula", "Poland", "Warsaw"),
        ("Elbe", "Germany", "Berlin"), ("Yangtze", "China", "Beijing"), ("Ebro", "Spain", "Madrid"), ("Loire", "France", "Paris"), ("Po", "Italy", "Rome"), ("Mekong", "Vietnam", "Hanoi"),
        ("Tagus", "Portugal", "Lisbon"), ("Weser", "Germany", "Berlin"), ("Fraser", "Canada", "Ottawa"), ("Shannon", "Ireland", "Dublin")]),
    "language-capital": ("Fact: The capital of the country where {cue} is the primary language is", [
        ("Hungarian", "Hungary", "Budapest"), ("Polish", "Poland", "Warsaw"), ("Greek", "Greece", "Athens"), ("Japanese", "Japan", "Tokyo"), ("Italian", "Italy", "Rome"), ("Swedish", "Sweden", "Stockholm"),
        ("Norwegian", "Norway", "Oslo"), ("Danish", "Denmark", "Copenhagen"), ("Finnish", "Finland", "Helsinki"), ("Turkish", "Turkey", "Ankara"), ("Thai", "Thailand", "Bangkok"), ("Vietnamese", "Vietnam", "Hanoi"),
        ("Korean", "Korea", "Seoul"), ("Czech", "Czechia", "Prague"), ("Dutch", "Netherlands", "Amsterdam"), ("Russian", "Russia", "Moscow"), ("Persian", "Iran", "Tehran"), ("French", "France", "Paris")]),
    "city-currency": ("Fact: The currency used in the country where {cue} is located is the", [
        ("Osaka", "Japan", "yen"), ("Shanghai", "China", "yuan"), ("Mumbai", "India", "rupee"), ("Moscow", "Russia", "ruble"), ("Bangkok", "Thailand", "baht"), ("Busan", "Korea", "won"),
        ("Gothenburg", "Sweden", "krona"), ("Bergen", "Norway", "krone"), ("Zurich", "Switzerland", "franc"), ("Istanbul", "Turkey", "lira"), ("Hanoi", "Vietnam", "dong"), ("Munich", "Germany", "euro"),
        ("Manchester", "England", "pound"), ("Krakow", "Poland", "zloty"), ("Debrecen", "Hungary", "forint"), ("Brno", "Czechia", "koruna"), ("Isfahan", "Iran", "rial"), ("Aarhus", "Denmark", "krone")]),
}
MAX_PER_FAMILY = 6; SEED = 20260924
def build():
    bank, log = [], []
    for fam, (tmpl, ents) in FAMILIES.items():
        body = lambda cue: tmpl.format(cue=cue).replace("Fact: ", "").strip()
        ok = []
        for cue, inter, ans in ents:
            flags = {"int_single": single(inter), "ans_single": single(ans), "ans_not_in_clue": ans.lower() not in body(cue).lower(), "int_not_in_clue": inter.lower() not in body(cue).lower()}
            if all(flags.values()): ok.append((cue, inter, ans, ntok(body(cue))))
            else: log.append(f"  drop {fam} {cue}/{inter}/{ans}: {[k for k, v in flags.items() if not v]}")
        pairs = [(a, b) for a, b in itertools.permutations(ok, 2) if a[1] != b[1] and a[2] != b[2] and a[3] == b[3]]
        # select up to MAX_PER_FAMILY ordered pairs (seeded order): each cue at most once as recipient and at most twice as donor,
        # each intermediate at most twice as recipient and at most twice as swap_to, so no single donor dominates a family
        import random; rng = random.Random(SEED); pairs_o = sorted(pairs); rng.shuffle(pairs_o)
        chosen, used_rec, used_don, used_int, used_swap = [], set(), collections.Counter(), collections.Counter(), collections.Counter()
        for a, b in pairs_o:
            if a[0] in used_rec or used_don[b[0]] >= 2 or used_int[a[1]] >= 2 or used_swap[b[1]] >= 2: continue
            chosen.append((a, b)); used_rec.add(a[0]); used_don[b[0]] += 1; used_int[a[1]] += 1; used_swap[b[1]] += 1
            if len(chosen) >= MAX_PER_FAMILY: break
        chosen.sort()
        for a, b in chosen:
            bank.append({"name": f"s2-{fam}-{a[0]}-{b[0]}", "category": fam, "prompt": tmpl.format(cue=a[0]), "donor_prompt": tmpl.format(cue=b[0]), "intermediate": a[1], "answer": a[2], "swap_to": b[1], "swap_answer": b[2],
                         "cue": a[0], "donor_cue": b[0], "n_tokens_clue": a[3], "constructed_donor": True})
        log.append(f"{fam}: {len(ok)} eligible cues, {len(pairs)} eligible ordered pairs, {len(chosen)} chosen")
    out = {"design": "H3/design_specs/two_hop_organism.md Amendment 7", "construction": __doc__.strip(), "families": {f: FAMILIES[f][0] for f in FAMILIES}, "max_per_family": MAX_PER_FAMILY, "selection_seed": SEED,
           "items": bank, "n_items": len(bank), "n_families": len({it["category"] for it in bank}), "build_log": log}
    json.dump(out, open(os.path.join(R.PROJECT, "H3", "design_specs", "two_hop_items_stage2.json"), "w"), indent=1)
    print("\n".join(log)); print(f"\n{len(bank)} items over {out['n_families']} families")
    for it in bank: print(f"  {it['name']:45s} {it['intermediate']:>12s}->{it['answer']:<12s} swap {it['swap_to']:>12s}->{it['swap_answer']:<12s} ntok {it['n_tokens_clue']}")


if __name__ == "__main__":
    build()
