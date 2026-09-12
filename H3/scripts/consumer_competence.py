"""H3 consumer competence calibration (the H3 plan, §5, §3.4): can the tagged organism answer a delayed codebook query at all?

Every H3 branch needs a consumer whose clean answer depends on the selected source. Before any intervention we
establish, for candidate query wordings: (a) does the model answer with a bare letter, (b) is the answer the code of
the *pointed* word rather than a distractor's, (c) how large is the clean margin b = log P(F(pointed)) - log P(F(other)).

Organism: the H1 tagged prompt, unchanged, followed by a codebook turn and a query turn. The query never restates the
tag. Codebooks assign one letter to each of the three source words plus their three donors, permuted independently of
identity and of entry order (seeded per cell).

Nothing is intervened on here; this stage only decides whether a consumer exists and which wording to freeze.

Usage: consumer_competence.py [smoke|calibrate]
"""
import os, sys, json, time, hashlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "common", "scripts"))
import numpy as np
import torch
import registry as R
import materials as M
import rendering as Rn

STAGE = sys.argv[1] if len(sys.argv) > 1 else "smoke"
OUT = os.path.join(R.PROJECT, "H3", "outputs", "consumer_competence"); os.makedirs(OUT, exist_ok=True)
RUN_ID = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
TAGS = ["A", "B", "C"]
COPY = "copy the following text exactly, word for word"
LETTERS = ["B", "D", "F", "H", "K", "M", "Q", "V"]          # spec Appendix B3
SEED = 20260907

# Calibration materials only: the first two evaluation triples, both fitting carriers. The eight evaluation triples
# and C2/C3 stay untouched for whatever design is registered after this.
_bank = [w for p in M.EVAL_BANK_1 + M.EVAL_BANK_2 for w in p]
TRIPLES = [tuple(_bank[3 * i:3 * i + 3]) for i in range(8)]
CAL_TRIPLES = [0, 1]
CAL_CARRIERS = ["C0", "C1"]

# Candidate query wordings. None restates the tag; none names a word. Frozen list, evaluated on the same forwards.
QUERIES = {
    "instructed": "Using the code, give the letter for the word you were instructed to keep in mind. Answer with the letter only.",
    "kept": "Using the code, what is the letter for the word you kept in mind? Answer with the letter only.",
    "tagged_word": "Using the code, what is the letter for the tagged word you were asked to keep in mind? Answer with the letter only.",
}


def user_text(words, tag, carrier):
    head = f'Here are three words: (A) "{words[0]}", (B) "{words[1]}", (C) "{words[2]}"'
    return head + f". Keep the word tagged {tag} in mind while you {COPY}" + ":\n\n" + carrier


def rotate(tr, r):
    return tuple(tr[(i + r) % 3] for i in range(3))


def donors_for(ti):
    nxt = TRIPLES[(ti + 1) % len(TRIPLES)]
    return {w: nxt[i] for i, w in enumerate(TRIPLES[ti])}


def codebook_text(words, donor_words, rng):
    """Six entries: the three sources and their three donors, letters assigned and ordered independently."""
    items = list(words) + list(donor_words)
    letters = list(LETTERS); rng.shuffle(letters); assign = {w: letters[i] for i, w in enumerate(items)}
    order = list(items); rng.shuffle(order)
    return "Code: " + ", ".join(f"{w} = {assign[w]}" for w in order) + ".", assign


def letter_ids(tok):
    """Answer-token ids for each letter, in the form the assistant turn actually starts with."""
    out = {}
    for L in LETTERS:
        for form in (L, " " + L):
            ids = tok(form, add_special_tokens=False).input_ids
            if len(ids) == 1:
                out.setdefault(L, []).append((form, ids[0]))
    return out


def main():
    tok = R.make_tokenizer()
    LID = letter_ids(tok)
    assert all(L in LID for L in LETTERS), {L: LID.get(L) for L in LETTERS}
    if STAGE == "smoke":
        rng = np.random.default_rng(SEED)
        ti, ck, rot, tag = CAL_TRIPLES[0], CAL_CARRIERS[0], 0, "A"
        words = rotate(TRIPLES[ti], rot); dmap = donors_for(ti)
        cb, assign = codebook_text(words, [dmap[w] for w in TRIPLES[ti]], rng)
        for qname, q in QUERIES.items():
            r = Rn.render(tok, user_text(words, tag, M.CARRIERS[ck]), M.CARRIERS[ck],
                          sources=[(f"X{j}", words[j], True) for j in range(3)],
                          extra_turns=[(cb + "\n" + q, "")], name=f"smoke|{qname}")
            print(f"--- {qname}: {len(r)} tokens, answer position {r.spans['answer']}")
            print(r.meta["full"][-460:].replace("\n", "\\n"))
            print(f"    pointed={words[0]} -> letter {assign[words[0]]}; letters {assign}")
        print("SMOKE OK")
        return

    from jlens.hf import from_hf
    model = R.load_model(); lm = from_hf(model, tok, compile=False)
    rows = []; t0 = time.time(); n = 0
    for ti in CAL_TRIPLES:
        dmap = donors_for(ti)
        for ck in CAL_CARRIERS:
            for rot in range(3):
                words = rotate(TRIPLES[ti], rot)
                rng = np.random.default_rng(SEED + 1000 * ti + 100 * rot + CAL_CARRIERS.index(ck))
                cb, assign = codebook_text(words, [dmap[w] for w in TRIPLES[ti]], rng)
                for tag_i, tag in enumerate(TAGS):
                    pointed = words[tag_i]
                    for qname, q in QUERIES.items():
                        r = Rn.render(tok, user_text(words, tag, M.CARRIERS[ck]), M.CARRIERS[ck],
                                      sources=[(f"X{j}", words[j], True) for j in range(3)],
                                      extra_turns=[(cb + "\n" + q, "")], name=f"{ti}|{ck}|rot{rot}|{tag}|{qname}")
                        ids = torch.tensor([r.ids], device=lm.input_device)
                        with torch.no_grad():
                            lg = model(ids, attention_mask=None).logits
                        lp = torch.log_softmax(lg[0, -1].float(), -1)
                        # score every letter in both surface forms; take the better form per letter
                        sc = {L: max(float(lp[i]) for _, i in LID[L]) for L in LETTERS}
                        gen = tok.decode(lg[0, -1].argmax().item()).strip()
                        pl = assign[pointed]; others = [assign[w] for w in words if w != pointed]
                        b_vs_unpointed = sc[pl] - max(sc[o] for o in others)
                        b_vs_all = sc[pl] - max(sc[L] for L in LETTERS if L != pl)
                        top_letter = max(LETTERS, key=lambda L: sc[L])
                        rows.append({"triple": ti, "carrier": ck, "rot": rot, "tag": tag, "query": qname,
                                     "words": list(words), "pointed": pointed, "pointed_letter": pl,
                                     "assign": assign, "greedy": gen, "greedy_is_letter": gen in LETTERS,
                                     "greedy_correct": gen == pl, "top_letter": top_letter,
                                     "forced_correct_vs_unpointed": bool(b_vs_unpointed > 0),
                                     "forced_correct_vs_all": bool(b_vs_all > 0),
                                     "b_vs_unpointed": b_vs_unpointed, "b_vs_all": b_vs_all,
                                     "letter_scores": sc, "n_tokens": len(r)})
                        n += 1
        print(f"  [calibrate] triple {ti}: {n} forwards ({time.time()-t0:.0f}s)", flush=True)
    meta = {"run_id": RUN_ID, "stage": STAGE, "n_forwards": n, "elapsed_s": round(time.time() - t0, 1),
            "queries": QUERIES, "letters": LETTERS, "seed": SEED, "cal_triples": CAL_TRIPLES,
            "cal_carriers": CAL_CARRIERS, "triples": [list(t) for t in TRIPLES], "rows": rows}
    json.dump(meta, open(os.path.join(OUT, f"rows_{STAGE}.json"), "w"), indent=1)
    man = R.manifest_block(); man.update({"run_id": RUN_ID, "stage": STAGE, "script": os.path.relpath(__file__, R.PROJECT),
                                          "design": "H3/design_specs/selection_to_behavior.md (consumer contract)",
                                          "rows_sha256": hashlib.sha256(open(os.path.join(OUT, f"rows_{STAGE}.json"), "rb").read()).hexdigest()})
    json.dump(man, open(os.path.join(OUT, f"manifest_{STAGE}.json"), "w"), indent=1)

    # summary per query wording
    print(f"\n[done {STAGE}] {n} forwards, {time.time()-t0:.0f}s")
    print(f"{'query':14s} {'bare-letter':>11s} {'greedy acc':>11s} {'forced vs unpointed':>20s} {'forced vs all':>14s} {'mean b':>8s}")
    summary = {}
    for qname in QUERIES:
        rs = [r for r in rows if r["query"] == qname]
        s = {"n": len(rs), "bare_letter": float(np.mean([r["greedy_is_letter"] for r in rs])),
             "greedy_acc": float(np.mean([r["greedy_correct"] for r in rs])),
             "forced_vs_unpointed": float(np.mean([r["forced_correct_vs_unpointed"] for r in rs])),
             "forced_vs_all": float(np.mean([r["forced_correct_vs_all"] for r in rs])),
             "mean_b_vs_unpointed": float(np.mean([r["b_vs_unpointed"] for r in rs])),
             "by_tag": {t: float(np.mean([r["greedy_correct"] for r in rs if r["tag"] == t])) for t in TAGS}}
        summary[qname] = s
        print(f"{qname:14s} {s['bare_letter']:11.2f} {s['greedy_acc']:11.2f} {s['forced_vs_unpointed']:20.2f} {s['forced_vs_all']:14.2f} {s['mean_b_vs_unpointed']:8.2f}   by tag {s['by_tag']}")
    json.dump(summary, open(os.path.join(OUT, f"summary_{STAGE}.json"), "w"), indent=1)
    best = max(summary, key=lambda q: (summary[q]["greedy_acc"], summary[q]["mean_b_vs_unpointed"]))
    print(f"\nbest by greedy accuracy: {best} ({summary[best]['greedy_acc']:.2f}); gate for H3 is >= 0.90 in the pointed arm")


if __name__ == "__main__":
    main()
