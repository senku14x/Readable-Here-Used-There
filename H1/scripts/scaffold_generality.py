"""H1 scaffold_generality (design: H1/design_specs/scaffold_generality.md).

Does selection (S) survive the released directed wording, the bare presentation, and (single stage) the direct organism,
or is it a property of the quoted-and-introduced copy scaffold? This file implements the discriminating stage first.

Stage `tagged`: the 2x2 presentation(quoted/bare) x wording(copy/directed) factorial on the tagged organism, S as endpoint.
                All four renderings keep the "Here are three words: (A)(B)(C)" head and the copy bridge, so the tag mechanism
                exists in every cell; presentation and wording are the only factors. 8 evaluation triples, 3 rotations, carriers
                C2/C3, arms {A,B,C,ctrl}, each source replaced from block 36 by the partner (next-triple, same index).
Stage `smoke` : tokenizer-only render + span + donor-geometry check of all four renderings for one triple (no model load).

Usage: scaffold_generality.py smoke|tagged
Writes H1/outputs/scaffold_generality/{raw_<stage>.npz, meta_<stage>.json, manifest_<stage>.json}.
"""
import os, sys, json, time, hashlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "common", "scripts"))
import numpy as np
import torch
import registry as R
import materials as M
import rendering as Rn
import readout as RO
import hooks as H

STAGE = sys.argv[1] if len(sys.argv) > 1 else "smoke"
assert STAGE in ("smoke", "tagged")
OUT = os.path.join(R.PROJECT, "H1", "outputs", "scaffold_generality"); os.makedirs(OUT, exist_ok=True)
RUN_ID = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
L_STATE, L_X = 35, 36
TAGS = ["A", "B", "C"]; ARMS = ["A", "B", "C", "ctrl"]
RENDERINGS = [("quoted", "copy"), ("quoted", "directed"), ("bare", "copy"), ("bare", "directed")]
_bank = [w for p in M.EVAL_BANK_1 + M.EVAL_BANK_2 for w in p]                 # same registered rule as tagged_selection evaluate
TRIPLES = [tuple(_bank[3 * i:3 * i + 3]) for i in range(8)]
CARRIERS = M.EVAL_CARRIERS                                                     # C2, C3
DECOYS = M.FIT_WORDS[:8]
ALL_LAYERS = list(range(R.N_SRC)); RANK_LAYERS = list(range(24, 60))
COPY = "copy the following text exactly, word for word"; COPY_NOW = "Now " + COPY
DONOR = {}
for _ti, _tr in enumerate(TRIPLES):
    _nxt = TRIPLES[(_ti + 1) % len(TRIPLES)]
    for _i, _w in enumerate(_tr):
        DONOR[_w] = _nxt[_i]
SRC = [w for tr in TRIPLES for w in tr]


def user_text(words, arm, carrier, pres, wording):
    q = pres == "quoted"
    head = "Here are three words: " + ", ".join(f'({TAGS[j]}) ' + (f'"{words[j]}"' if q else f"{words[j]}") for j in range(3))
    if arm in TAGS:
        tail = (f". Keep the word tagged {arm} in mind while you {COPY}" if wording == "copy"
                else f". Hold the word tagged {arm} in mind as you write. {COPY_NOW}")
    else:
        tail = (f". Those words occur one time. {COPY_NOW}" if wording == "copy"
                else f". Those words came up in conversation. {COPY_NOW}")
    return head + tail + ":\n\n" + carrier


def rotate(tr, r):
    return tuple(tr[(i + r) % 3] for i in range(3))


def do_render(tok, words, arm, ck, pres, wording, name=""):
    car = M.CARRIERS[ck]; q = pres == "quoted"
    return Rn.render(tok, user_text(words, arm, car, pres, wording), car,
                     sources=[(f"X{j}", words[j], q) for j in range(3)], name=name)


# ------------------------------------------------------------------ smoke: tokenizer-only render/geometry check
def smoke():
    tok = R.make_tokenizer()
    tr = TRIPLES[0]; ck = CARRIERS[0]
    print(f"triple={tr} carrier={ck}\n")
    for pres, wording in RENDERINGS:
        for arm in ("A", "ctrl"):
            r = do_render(tok, tr, arm, ck, pres, wording, name=f"{pres}_{wording}|{arm}")
            print(f"--- {pres}x{wording} arm={arm} ---")
            print("USER:", r.meta["user_text"])
            for j in range(3):
                sp = r.spans[f"X{j}"]; print(f"   X{j}={tr[j]!r} full_tokens={len(sp['full'])} decodes={tok.decode(r.ids[sp['first']:sp['last']+1])!r}")
        # donor geometry for arm A
        r = do_render(tok, tr, "A", ck, pres, wording)
        for j in range(3):
            dw = list(tr); dw[j] = DONOR[tr[j]]
            rd = do_render(tok, tuple(dw), "A", ck, pres, wording)
            ok = (len(rd) == len(r) and rd.spans[f"X{j}"]["full"] == r.spans[f"X{j}"]["full"])
            print(f"   donor geom j={j} {tr[j]}->{DONOR[tr[j]]}: {'OK' if ok else 'MISMATCH len %d vs %d'%(len(rd),len(r))}")
        print()
    # single-token check for bare words in context
    bad = [w for w in SRC if Rn.single_token_id(tok, w) is None]
    print("words not single-token (leading-space):", bad or "none")
    print("SMOKE OK" if not bad else "SMOKE: flag multi-token words above")


# ------------------------------------------------------------------ tagged: full 2x2 factorial
def tagged():
    t0 = time.time(); tok = R.make_tokenizer()
    from jlens.hf import from_hf
    model = R.load_model(); lm = from_hf(model, tok, compile=False)
    ALL = list(range(R.N_BLOCKS)); run = H.make_run(model, lm, ALL); dev = lm.input_device
    LEN = R.load_lenses(("J_NP",))["J_NP"]
    TID = {w: Rn.single_token_id(tok, w) for w in SRC + DECOYS}
    assert all(v is not None for v in TID.values()), {k: v for k, v in TID.items() if v is None}
    COLS = SRC + DECOYS
    ro = RO.LensReadout(model, lm, LEN, [TID[w] for w in COLS])
    ra = np.load(os.path.join(R.PROJECT, "H1", "outputs", "natural_modulation", "resid_axis.npz"))
    MU = {w: torch.tensor(ra[f"{w}|fit"].astype(np.float32), device=dev) for w in SRC if f"{w}|fit" in ra}
    assert len(MU) == len(SRC), [w for w in SRC if w not in MU]

    def pair_axis(X, Y):
        v = MU[Y] - MU[X]; return v / v.norm(dim=-1, keepdim=True)

    RAW, META = {}, {"cells": {}, "renderings": [f"{p}_{w}" for p, w in RENDERINGS], "triples": [list(t) for t in TRIPLES],
                     "donor": DONOR, "columns": COLS, "carriers": CARRIERS, "arms": ARMS, "rank_layers": RANK_LAYERS,
                     "l_state": L_STATE, "l_x": L_X, "stage": STAGE}
    n = 0

    def record(tag, r, acts, logits, words):
        inter = r.interior
        RAW[f"{tag}|z"] = ro.z(acts, inter, ALL_LAYERS).astype(np.float16)
        hs = torch.stack([acts[l][0, inter, :].float() for l in ALL_LAYERS])
        lp = torch.log_softmax(logits[0, inter, :].float(), -1)
        for j, X in enumerate(words):
            Y = DONOR[X]
            RAW[f"{tag}|p_pair{j}"] = (hs * pair_axis(X, Y)[:, None, :]).sum(-1).cpu().numpy().astype(np.float32)
            RAW[f"{tag}|lp_margin{j}"] = (lp[:, TID[Y]] - lp[:, TID[X]]).cpu().numpy().astype(np.float32)
        RAW[f"{tag}|rank"] = ro.full_vocab_ranks(acts, inter, RANK_LAYERS, [TID[w] for w in words]).astype(np.int32)
        cs, ce = r.meta["carrier_start"], r.meta["carrier_end"]; nll, top1, _ = RO.carrier_damage(logits, r.ids, cs, ce)
        RAW[f"{tag}|nll"] = np.float32(nll); RAW[f"{tag}|top1"] = top1

    for pres, wording in RENDERINGS:
        rk = f"{pres}_{wording}"
        for ck in CARRIERS:
            for ti, tr in enumerate(TRIPLES):
                for rot in range(3):
                    words = rotate(tr, rot)
                    for arm in ARMS:
                        tag = f"{rk}|{ck}|T{ti}|rot{rot}|{arm}"
                        r = do_render(tok, words, arm, ck, pres, wording, name=tag)
                        acts, lg = run(r.ids); n += 1
                        spans = {j: r.spans[f"X{j}"]["full"] for j in range(3)}
                        own0 = {l: acts[l][0, spans[0], :].clone() for l in ALL}
                        record(f"{tag}|clean", r, acts, lg, words)
                        META["cells"][tag] = {"words": list(words), "pres": pres, "wording": wording, "arm": arm,
                                              "n_tokens": len(r), "interior_n": len(r.interior)}
                        # same-source gate (slot 0): must be bitwise equal to clean
                        a_s, l_s = run(r.ids, H.SpanWriter(lm.layers, [l for l in ALL if l >= L_X], spans[0], own0)); n += 1
                        assert torch.equal(l_s, lg) and all(torch.equal(a_s[l], acts[l]) for l in ALL), f"same-source != clean {tag}"
                        del a_s
                        for j in range(3):
                            dw = list(words); dw[j] = DONOR[words[j]]
                            rd = do_render(tok, tuple(dw), arm, ck, pres, wording)
                            assert len(rd) == len(r) and rd.spans[f"X{j}"]["full"] == spans[j], f"donor geometry {tag} j={j} ({words[j]}->{dw[j]})"
                            ad, _ = run(rd.ids); n += 1
                            dn = {l: ad[l][0, spans[j], :].clone() for l in ALL}; del ad
                            a2, l2 = run(r.ids, H.SpanWriter(lm.layers, [l for l in ALL if l >= L_X], spans[j], dn)); n += 1
                            for l in range(L_X):
                                assert torch.equal(a2[l][0, r.interior, :], acts[l][0, r.interior, :]), f"layer<{L_X} identity {tag} j={j}"
                            record(f"{tag}|swap{j}", r, a2, l2, words); del a2
                        del acts
                print(f"  [{rk}] {ck} T{ti}: {n} forwards ({time.time()-t0:.0f}s)", flush=True)
    META.update({"run_id": RUN_ID, "n_forwards": n, "elapsed_s": round(time.time() - t0, 1), "token_ids": TID})
    np.savez_compressed(os.path.join(OUT, f"raw_{STAGE}.npz"), **RAW)
    json.dump(META, open(os.path.join(OUT, f"meta_{STAGE}.json"), "w"), indent=1)
    man = R.manifest_block(); man.update({"run_id": RUN_ID, "stage": STAGE, "script": os.path.relpath(__file__, R.PROJECT),
                                          "design": "H1/design_specs/scaffold_generality.md",
                                          "raw_sha256": hashlib.sha256(open(os.path.join(OUT, f"raw_{STAGE}.npz"), "rb").read()).hexdigest()})
    json.dump(man, open(os.path.join(OUT, f"manifest_{STAGE}.json"), "w"), indent=1)
    print(f"[done {STAGE}] {n} forwards, {time.time()-t0:.0f}s -> {OUT}")


if __name__ == "__main__":
    (smoke if STAGE == "smoke" else tagged)()
