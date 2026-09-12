"""H1 early_late_mapping (design: H1/design_specs/early_late_mapping.md + Amendment 1).

Does the availability of a word->letter mapping change whether the carrier expresses X or F(X)? Conditions per word:
`early_usable` (codebook incl. X before the carrier), `early_unusable` (length-matched codebook over 8 OTHER words, X absent
-> controls the generic long-prefix effect), `late` (codebook after the carrier). One forward per cell gives both the answer
(competence, greedy at the answer position) and the carrier readouts (s_X, s_F(X), s_F(Y)).

Central estimand: source-conditioned letter contrast E_F^sc = s_F(X)-s_F(Y) under the same usable codebook (transformation
signal). Usability contrast E_X = s_X^early_usable - s_X^early_unusable (mapping availability vs generic prefix).

Usage: early_late_mapping.py run
"""
import os, sys, json, time, hashlib, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "common", "scripts"))
import numpy as np
import torch
import registry as R
import materials as M
import rendering as Rn
import readout as RO
import hooks as H

STAGE = sys.argv[1] if len(sys.argv) > 1 else "run"
OUT = os.path.join(R.PROJECT, "H1", "outputs", "early_late_mapping"); os.makedirs(OUT, exist_ok=True)
RUN_ID = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
LETTERS = M.CODE_LETTERS                                          # B D F H K M Q V
BANK = M.EVAL_BANK_1 + M.EVAL_BANK_2                              # 16 pairs
WORDS = [w for p in BANK for w in p]                             # 32 words
PAIR = {}
for a, b in BANK:
    PAIR[a] = b; PAIR[b] = a
GROUPS = [WORDS[0:8], WORDS[8:16], WORDS[16:24], WORDS[24:32]]   # groups of 8 (pair partners share a group)
GROUP_OF = {w: gi for gi, g in enumerate(GROUPS) for w in g}
CARRIERS = M.EVAL_CARRIERS
DECOYS = M.FIT_WORDS[:8]
ALL_LAYERS = list(range(R.N_SRC)); RANK_LAYERS = list(range(24, 60))
COPY = "copy the following text exactly, word for word"
QTEXT = "Using the code, what is the letter for the word introduced in the first message? Answer with the letter only."


def codebook(words8, seed):
    rng = random.Random(seed)
    lets = LETTERS[:]; rng.shuffle(lets)
    amap = dict(zip(words8, lets))                               # injective word->letter
    entries = [(w, amap[w]) for w in words8]; rng.shuffle(entries)  # entry order independent of assignment
    return amap, "Code: " + ", ".join(f"{w} = {L}" for w, L in entries) + "."


def s_prompt(X, carrier):
    return f'Here is the word "{X}". Keep that word in mind while you {COPY}:\n\n' + carrier


def main():
    t0 = time.time(); tok = R.make_tokenizer()
    from jlens.hf import from_hf
    model = R.load_model(); lm = from_hf(model, tok, compile=False); ALL = list(range(R.N_BLOCKS))
    run = H.make_run(model, lm, ALL); LEN = R.load_lenses(("J_NP",))["J_NP"]
    COLS = WORDS + LETTERS + DECOYS
    TID = {w: Rn.single_token_id(tok, w) for w in COLS}
    assert all(v is not None for v in TID.values()), {k: v for k, v in TID.items() if v is None}
    LET_NS = {L: tok(L, add_special_tokens=False).input_ids[0] for L in LETTERS}   # no-space letter id (answer may use either)
    CIX = {w: i for i, w in enumerate(COLS)}
    ro = RO.LensReadout(model, lm, LEN, [TID[w] for w in COLS])
    RAW, META = {}, {"words": WORDS, "letters": LETTERS, "columns": COLS, "decoys": DECOYS, "carriers": CARRIERS,
                     "rank_layers": RANK_LAYERS, "cells": {}, "stage": STAGE}
    n = 0

    def record(tag, r, acts, logits, ans_pos):
        inter = r.interior
        RAW[f"{tag}|z"] = ro.z(acts, inter, ALL_LAYERS).astype(np.float16)
        lp = torch.log_softmax(logits[0, inter, :].float(), -1)
        RAW[f"{tag}|lp"] = lp[:, [TID[w] for w in COLS]].cpu().numpy().astype(np.float32)
        RAW[f"{tag}|ans_top1"] = np.int32(int(logits[0, ans_pos].argmax()))   # greedy answer token

    for ck in CARRIERS:
        car = M.CARRIERS[ck]
        for X in WORDS:
            g = GROUP_OF[X]; Y = PAIR[X]
            for seed in (1, 2):
                amap_u, cb_u = codebook(GROUPS[g], seed)                       # usable (X present)
                amap_x, cb_x = codebook(GROUPS[(g + 1) % 4], seed)             # unusable (X absent), length-matched
                FX, FY = amap_u[X], amap_u[Y]
                S = s_prompt(X, car)
                conds = {"early_usable":  ("Code: " + cb_u.split("Code: ")[1] + "\n" + S, QTEXT),
                         "early_unusable": ("Code: " + cb_x.split("Code: ")[1] + "\n" + S, QTEXT),
                         "late":          (S, "Code: " + cb_u.split("Code: ")[1] + "\n" + QTEXT)}
                for cond, (u1, u2) in conds.items():
                    tag = f"{X}|s{seed}|{ck}|{cond}"
                    r = Rn.render(tok, u1, car, sources=[("X", X, True)], extra_turns=[(u2, "")], name=tag)
                    acts, lg = run(r.ids); n += 1
                    record(tag, r, acts, lg, len(r.ids) - 1); del acts
                    META["cells"][tag] = {"word": X, "pair": Y, "FX": FX, "FY": FY, "cond": cond, "seed": seed,
                                          "FX_ns_id": int(LET_NS[FX]), "FX_ls_id": int(TID[FX])}
            n and None
        print(f"  [{ck}] {n} forwards ({time.time()-t0:.0f}s)", flush=True)
    np.savez_compressed(os.path.join(OUT, f"raw_{STAGE}.npz"), **RAW)
    META.update({"run_id": RUN_ID, "n_forwards": n, "elapsed_s": round(time.time() - t0, 1), "token_ids": TID, "letter_ns_ids": {k: int(v) for k, v in LET_NS.items()}})
    json.dump(META, open(os.path.join(OUT, f"meta_{STAGE}.json"), "w"), indent=1)
    man = R.manifest_block(); man.update({"run_id": RUN_ID, "stage": STAGE, "script": os.path.relpath(__file__, R.PROJECT), "design": "H1/design_specs/early_late_mapping.md",
                                          "raw_sha256": hashlib.sha256(open(os.path.join(OUT, f"raw_{STAGE}.npz"), "rb").read()).hexdigest()})
    json.dump(man, open(os.path.join(OUT, f"manifest_{STAGE}.json"), "w"), indent=1)
    print(f"[done {STAGE}] {n} forwards, {time.time()-t0:.0f}s -> {OUT}")


if __name__ == "__main__":
    main()
