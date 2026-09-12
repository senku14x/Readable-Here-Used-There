"""H3 selection_to_behavior (design: H3/design_specs/selection_to_behavior.md v2; audit-corrected battery).

Does the instruction-region-state transplant that redirects the internal source profile (H1 selection_localization)
also redirect the ANSWER of a codebook consumer on the same forwards?

Audit corrections vs the first battery (this file writes raw_<stage>_v2.npz; the first-run raw_<stage>.npz is preserved):
  - letter scoring saves the full per-letter per-form log-probs (llp[8,2]); analysis uses LOGSUMEXP over forms.
  - donors for the source-swap (secondary) rows are rendered WITH the consumer turn -> matched length (no cross-length
    contamination of source-span states).
  - a second matched-norm random control randC (scaled to ||h_C - h_A||) so C->A has its own control, not B->A's.
  - real write diagnostics per intervention (mean write norm; read-back max error), not a hardcoded placeholder.
  - self-patch compared to the recorded clean-A logits (bitwise no-op gate).

Arms: cleanA/B/C, BtoA, CtoA, randB (norm-matched to B->A), randC (norm-matched to C->A), AtoA self-patch.
Stages: smoke | pilot (triples 0-1, C0/C1, primary-only) | evaluate (triples 2-7, C2/C3, full).
Usage: selection_to_behavior.py smoke|pilot|evaluate
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
assert STAGE in ("smoke", "pilot", "evaluate", "carrier_only")
SUF = "" if STAGE == "carrier_only" else "_v2"
OUT = R.out_dir("H3", "outputs", "selection_to_behavior")
RUN_ID = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
TAGS = ["A", "B", "C"]
COPY = "copy the following text exactly, word for word"
LETTERS = ["B", "D", "F", "H", "K", "M", "Q", "V"]
QUERY = "Using the code, give the letter for the word you were instructed to keep in mind. Answer with the letter only."
SEED = 20260907
DECOYS = M.FIT_WORDS[:8]
LX = 36

_bank = [w for p in M.EVAL_BANK_1 + M.EVAL_BANK_2 for w in p]
TRIPLES = [tuple(_bank[3 * i:3 * i + 3]) for i in range(8)]
DONOR = {}
for _i, _tr in enumerate(TRIPLES):
    _nx = TRIPLES[(_i + 1) % len(TRIPLES)]
    for _j, _w in enumerate(_tr):
        DONOR[_w] = _nx[_j]

if STAGE == "pilot":
    CELL_TRIPLES, CARRIERS, FULL = [0, 1], ["C0", "C1"], False
elif STAGE == "carrier_only":
    CELL_TRIPLES, CARRIERS, FULL = list(range(2, 8)), ["C2", "C3"], False
else:
    CELL_TRIPLES, CARRIERS, FULL = list(range(2, 8)), ["C2", "C3"], True


def rotate(tr, r):
    return tuple(tr[(i + r) % 3] for i in range(3))


def codebook_text(words, rng):
    items = list(words) + [DONOR[w] for w in words]
    letters = list(LETTERS); rng.shuffle(letters); assign = {w: letters[i] for i, w in enumerate(items)}
    order = list(items); rng.shuffle(order)
    return "Code: " + ", ".join(f"{w} = {assign[w]}" for w in order) + ".", assign


def user_text(words, tag):
    head = f'Here are three words: (A) "{words[0]}", (B) "{words[1]}", (C) "{words[2]}"'
    return head + f". Keep the word tagged {tag} in mind while you {COPY}"


def render_arm(tok, words, tag, ck, cb, consumer=True):
    car = M.CARRIERS[ck]
    ut = user_text(words, tag) + ":\n\n" + car
    extra = [(cb + "\n" + QUERY, "")] if consumer else None
    return Rn.render(tok, ut, car, sources=[(f"X{j}", words[j], True) for j in range(3)],
                     extra_turns=extra, name=f"{words}|{tag}|{ck}")


def tag_position(rA, rB, rC):
    a, b, c = rA.ids, rB.ids, rC.ids
    assert len(a) == len(b) == len(c)
    diff = [i for i in range(len(a)) if not (a[i] == b[i] == c[i])]
    assert len(diff) == 1, f"arms differ at {len(diff)} positions: {diff}"
    return diff[0]


def letter_ids(tok):
    out = {}
    for L in LETTERS:
        forms = []
        for form in (L, " " + L):
            ids = tok(form, add_special_tokens=False).input_ids
            forms.append(ids[0] if len(ids) == 1 else -1)
        out[L] = forms                                        # [bare_id, spaced_id], -1 if not single-token
    assert all(out[L][0] >= 0 for L in LETTERS)
    return out


def smoke():
    tok = R.make_tokenizer(); letter_ids(tok)
    rng = np.random.default_rng(SEED)
    for ti in (0, 2, 7):
        words = rotate(TRIPLES[ti], 0); cb, assign = codebook_text(words, rng)
        rr = {a: render_arm(tok, words, a, CARRIERS[0] if ti == 0 else "C2", cb) for a in TAGS}
        tp = tag_position(rr["A"], rr["B"], rr["C"]); cs = rr["A"].meta["carrier_start"]
        dw = list(words); dw[0] = DONOR[words[0]]
        rd = render_arm(tok, tuple(dw), "A", CARRIERS[0] if ti == 0 else "C2", cb, consumer=True)
        print(f"T{ti} {words}: len={len(rr['A'])} donor_len={len(rd)} tag_pos={tp} instr=[{tp},{cs}) "
              f"donor_geom_ok={rd.spans['X0']['full']==rr['A'].spans['X0']['full']} donor_len_match={len(rd)==len(rr['A'])}")
    print("SMOKE OK")


def main():
    if STAGE == "smoke":
        smoke(); return
    tok = R.make_tokenizer(); LID = letter_ids(tok)
    from jlens.hf import from_hf
    model = R.load_model(); lm = from_hf(model, tok, compile=False)
    ALL = list(range(R.N_BLOCKS)); LGE = [l for l in ALL if l >= LX]
    run = H.make_run(model, lm, ALL); LEN = R.load_lenses(("J_NP",))["J_NP"]
    ro = RO.LensReadout(model, lm, LEN, [0]); src_layers = list(range(R.N_SRC))
    RAW, META = {}, {"cells": {}, "triples": [list(t) for t in TRIPLES], "carriers": CARRIERS, "tags": TAGS,
                     "decoys": DECOYS, "l_x": LX, "query": QUERY, "letters": LETTERS, "letter_ids": LID,
                     "seed": SEED, "cell_triples": CELL_TRIPLES, "stage": STAGE, "full": FULL, "scoring": "llp[8,2] saved; analysis uses logsumexp over forms"}
    t0 = time.time(); n = 0

    def llp_at_answer(logits):
        lp = torch.log_softmax(logits[0, -1].float(), -1)
        arr = np.full((len(LETTERS), 2), -1e30, np.float32)
        for i, L in enumerate(LETTERS):
            for f, tid in enumerate(LID[L]):
                if tid >= 0:
                    arr[i, f] = float(lp[tid])
        return arr, tok.decode(int(logits[0, -1].argmax())).strip()

    def record(tag, r, acts, logits, cols):
        ro.set_columns(cols)
        RAW[f"{tag}|z"] = ro.z(acts, r.interior, src_layers).astype(np.float16)
        arr, top = llp_at_answer(logits); RAW[f"{tag}|llp"] = arr; RAW[f"{tag}|greedy"] = top
        cs, ce = r.meta["carrier_start"], r.meta["carrier_end"]; nll, top1, _ = RO.carrier_damage(logits, r.ids, cs, ce)
        RAW[f"{tag}|nll"] = np.float32(nll); RAW[f"{tag}|top1"] = top1

    def wdiag(base, arm, src, acts_recip, instr, acts_after):
        wn = float(np.mean([ (src[l].float() - acts_recip[l][0, instr, :].float()).norm(dim=1).mean().item() for l in LGE]))
        rb = float(np.max([ (acts_after[l][0, instr, :].float() - src[l].float()).abs().max().item() for l in LGE]))
        RAW[f"{base}|{arm}|wnorm"] = np.float32(wn); RAW[f"{base}|{arm}|rberr"] = np.float32(rb)

    # -------------------- carrier_only (Amendment 2): donor CARRIER states only; instruction region and sources never written --------------------
    if STAGE == "carrier_only":
        META["design"] = "Amendment 2 (carrier-only donor)"
        for ti in CELL_TRIPLES:
            for ck in CARRIERS:
                for rot in range(3):
                    words = rotate(TRIPLES[ti], rot)
                    rng = np.random.default_rng(SEED + 1000 * ti + 100 * rot + CARRIERS.index(ck))
                    cb, assign = codebook_text(words, rng)
                    cols = [Rn.single_token_id(tok, w) for w in list(words) + [DONOR[w] for w in words] + DECOYS]
                    assert all(c is not None for c in cols)
                    rr = {a: render_arm(tok, words, a, ck, cb) for a in TAGS}
                    tp = tag_position(rr["A"], rr["B"], rr["C"]); cs, ce = rr["A"].meta["carrier_start"], rr["A"].meta["carrier_end"]
                    carr = list(range(cs, ce)); pre = list(range(0, cs))
                    base = f"T{ti}|{ck}|rot{rot}"
                    META["cells"][base] = {"words": list(words), "donors": [DONOR[w] for w in words], "assign": assign, "tag_pos": tp,
                                           "carrier_start": cs, "carrier_end": ce, "answer_pos": int(rr["A"].spans["answer"]),
                                           "A_word": words[0], "B_word": words[1], "C_word": words[2]}
                    acts = {}; lg_clean = {}
                    for a in TAGS:
                        ac, lg = run(rr[a].ids); n += 1
                        record(f"{base}|clean{a}", rr[a], ac, lg, cols); acts[a] = ac; lg_clean[a] = lg
                    h0 = torch.stack([acts["A"][l][0, -1, :].float() for l in ALL])
                    RAW[f"{base}|cleanA|ans_dist"] = np.zeros(len(ALL), np.float32)
                    for a in ("B", "C"):
                        RAW[f"{base}|clean{a}|ans_dist"] = (torch.stack([acts[a][l][0, -1, :].float() for l in ALL]) - h0).norm(dim=-1).cpu().numpy().astype(np.float32)
                    own36 = {l: acts["A"][l][0, carr, :].clone() for l in LGE}
                    a_o, l_o = run(rr["A"].ids, H.SpanWriter(lm.layers, LGE, carr, own36)); n += 1
                    META["cells"][base]["carr_own_bitwise"] = bool(torch.equal(l_o, lg_clean["A"]) and all(torch.equal(a_o[l], acts["A"][l]) for l in ALL)); del a_o
                    Bsrc = {l: acts["B"][l][0, carr, :].clone() for l in ALL}; Csrc = {l: acts["C"][l][0, carr, :].clone() for l in ALL}
                    g = torch.Generator(device="cpu").manual_seed(SEED + 7 + 13 * ti + rot + CARRIERS.index(ck))
                    randB = {}
                    for l in LGE:
                        hA = acts["A"][l][0, carr, :].float(); dn = (Bsrc[l].float() - hA).norm(dim=1, keepdim=True)
                        v = torch.randn(len(carr), hA.shape[1], generator=g).to(hA.device)
                        randB[l] = (hA + v / v.norm(dim=1, keepdim=True) * dn).to(acts["A"][l].dtype)
                    arms = {"CarrBtoA": (LGE, {l: Bsrc[l] for l in LGE}), "CarrCtoA": (LGE, {l: Csrc[l] for l in LGE}),
                            "CarrBtoA_all": (ALL, Bsrc), "CarrCtoA_all": (ALL, Csrc), "randCarrB": (LGE, randB)}
                    for arm, (lw, src) in arms.items():
                        ac, lg = run(rr["A"].ids, H.SpanWriter(lm.layers, lw, carr, src)); n += 1
                        assert all(torch.equal(ac[l][0, pre, :], acts["A"][l][0, pre, :]) for l in ALL), f"prefix touched under {arm} {base}"
                        record(f"{base}|{arm}", rr["A"], ac, lg, cols)
                        RAW[f"{base}|{arm}|ans_dist"] = (torch.stack([ac[l][0, -1, :].float() for l in ALL]) - h0).norm(dim=-1).cpu().numpy().astype(np.float32)
                        RAW[f"{base}|{arm}|wnorm"] = np.float32(np.mean([(src[l].float() - acts["A"][l][0, carr, :].float()).norm(dim=1).mean().item() for l in lw]))
                        RAW[f"{base}|{arm}|rberr"] = np.float32(np.max([(ac[l][0, carr, :].float() - src[l].float()).abs().max().item() for l in lw]))
                        del ac
                    del acts
                print(f"  [carrier_only] triple {ti} {ck}: {n} forwards ({time.time()-t0:.0f}s)", flush=True)
        META.update({"run_id": RUN_ID, "n_forwards": n, "elapsed_s": round(time.time() - t0, 1)})
        np.savez_compressed(os.path.join(OUT, "raw_carrier_only.npz"), **RAW)
        json.dump(META, open(os.path.join(OUT, "meta_carrier_only.json"), "w"), indent=1)
        man = R.manifest_block(); man.update({"run_id": RUN_ID, "stage": "carrier_only", "script": os.path.relpath(__file__, R.PROJECT),
                                              "design": "H3/design_specs/selection_to_behavior.md (Amendment 2)",
                                              "raw_sha256": hashlib.sha256(open(os.path.join(OUT, "raw_carrier_only.npz"), "rb").read()).hexdigest()})
        json.dump(man, open(os.path.join(OUT, "manifest_carrier_only.json"), "w"), indent=1)
        sb = [META["cells"][c]["carr_own_bitwise"] for c in META["cells"]]
        print(f"[done carrier_only] {n} forwards, {time.time()-t0:.0f}s; carrier self-patch bitwise no-op: {sum(sb)}/{len(sb)}")
        return

    for ti in CELL_TRIPLES:
        for ck in CARRIERS:
            for rot in range(3):
                words = rotate(TRIPLES[ti], rot)
                rng = np.random.default_rng(SEED + 1000 * ti + 100 * rot + CARRIERS.index(ck))
                cb, assign = codebook_text(words, rng)
                cols = [Rn.single_token_id(tok, w) for w in list(words) + [DONOR[w] for w in words] + DECOYS]
                assert all(c is not None for c in cols)
                rr = {a: render_arm(tok, words, a, ck, cb) for a in TAGS}
                tp = tag_position(rr["A"], rr["B"], rr["C"]); cs = rr["A"].meta["carrier_start"]
                instr = list(range(tp, cs)); spans = {j: rr["A"].spans[f"X{j}"]["full"] for j in range(3)}
                assert all(max(spans[j]) < tp for j in range(3))
                base = f"T{ti}|{ck}|rot{rot}"
                META["cells"][base] = {"words": list(words), "donors": [DONOR[w] for w in words], "assign": assign,
                                       "tag_pos": tp, "carrier_start": cs, "answer_pos": int(rr["A"].spans["answer"]),
                                       "instr_len": len(instr), "A_word": words[0], "B_word": words[1], "C_word": words[2]}
                acts = {}; lg_clean = {}
                for a in TAGS:
                    ac, lg = run(rr[a].ids); n += 1
                    record(f"{base}|clean{a}|noswap", rr[a], ac, lg, cols); acts[a] = ac; lg_clean[a] = lg
                # self-patch no-op gate (compare to recorded clean-A logits)
                selfsrc = {l: acts["A"][l][0, instr, :].clone() for l in LGE}
                ac_s, lg_s = run(rr["A"].ids, H.SpanWriter(lm.layers, LGE, instr, selfsrc)); n += 1
                META["cells"][base]["selfpatch_bitwise"] = bool(torch.equal(lg_s, lg_clean["A"]))
                # instruction-region transplant sources + two matched-norm random controls
                Bsrc = {l: acts["B"][l][0, instr, :].clone() for l in LGE}
                Csrc = {l: acts["C"][l][0, instr, :].clone() for l in LGE}
                def mkrand(donor_states, seedoff):
                    g = torch.Generator(device="cpu").manual_seed(SEED + seedoff + 13 * ti + rot + CARRIERS.index(ck))
                    out = {}
                    for l in LGE:
                        hA = acts["A"][l][0, instr, :].float(); dn = (donor_states[l].float() - hA).norm(dim=1, keepdim=True)
                        v = torch.randn(len(instr), hA.shape[1], generator=g).to(hA.device)
                        out[l] = (hA + v / v.norm(dim=1, keepdim=True) * dn).to(acts["A"][l].dtype)
                    return out
                randBsrc = mkrand(Bsrc, 7); randCsrc = mkrand(Csrc, 700)
                for arm, src in (("BtoA", Bsrc), ("CtoA", Csrc), ("randB", randBsrc), ("randC", randCsrc)):
                    ac, lg = run(rr["A"].ids, H.SpanWriter(lm.layers, LGE, instr, src)); n += 1
                    record(f"{base}|{arm}|noswap", rr["A"], ac, lg, cols); wdiag(base, arm, src, acts["A"], instr, ac)

                if FULL:
                    donor_src = {}
                    for j in range(3):
                        dw = list(words); dw[j] = DONOR[words[j]]
                        rd = render_arm(tok, tuple(dw), "A", ck, cb, consumer=True)       # matched length
                        assert len(rd) == len(rr["A"]) and rd.spans[f"X{j}"]["full"] == spans[j], f"donor geom/len {base} j={j}"
                        ad, _ = run(rd.ids); n += 1; donor_src[j] = {l: ad[l][0, spans[j], :].clone() for l in LGE}; del ad
                    arms = {"cleanA": (rr["A"].ids, None), "cleanB": (rr["B"].ids, None), "cleanC": (rr["C"].ids, None),
                            "BtoA": (rr["A"].ids, Bsrc), "CtoA": (rr["A"].ids, Csrc),
                            "randB": (rr["A"].ids, randBsrc), "randC": (rr["A"].ids, randCsrc)}
                    for aname, (ids, ipatch) in arms.items():
                        ip = H.SpanWriter(lm.layers, LGE, instr, ipatch) if ipatch is not None else None
                        rec_r = rr[aname[-1]] if aname.startswith("clean") else rr["A"]
                        for j in range(3):
                            sw = H.SpanWriter(lm.layers, LGE, spans[j], donor_src[j])
                            ac, lg = run(ids, H.Both(ip, sw)); n += 1
                            record(f"{base}|{aname}|swap{j}", rec_r, ac, lg, cols)
                del acts
            print(f"  [{STAGE}{SUF}] triple {ti} {ck}: {n} forwards ({time.time()-t0:.0f}s)", flush=True)
    META.update({"run_id": RUN_ID, "n_forwards": n, "elapsed_s": round(time.time() - t0, 1)})
    np.savez_compressed(os.path.join(OUT, f"raw_{STAGE}{SUF}.npz"), **RAW)
    json.dump(META, open(os.path.join(OUT, f"meta_{STAGE}{SUF}.json"), "w"), indent=1)
    man = R.manifest_block(); man.update({"run_id": RUN_ID, "stage": STAGE + SUF, "script": os.path.relpath(__file__, R.PROJECT),
                                          "design": "H3/design_specs/selection_to_behavior.md",
                                          "raw_sha256": hashlib.sha256(open(os.path.join(OUT, f"raw_{STAGE}{SUF}.npz"), "rb").read()).hexdigest()})
    json.dump(man, open(os.path.join(OUT, f"manifest_{STAGE}{SUF}.json"), "w"), indent=1)
    sb = [META["cells"][c]["selfpatch_bitwise"] for c in META["cells"]]
    print(f"[done {STAGE}{SUF}] {n} forwards, {time.time()-t0:.0f}s; self-patch bitwise no-op: {sum(sb)}/{len(sb)}")


if __name__ == "__main__":
    main()
