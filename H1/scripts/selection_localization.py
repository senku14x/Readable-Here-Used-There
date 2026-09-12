"""H1 selection_localization (design: H1/design_specs/selection_localization.md + Amendments 1-2).

Where does the pointer state that selects among three tagged sources live? Amendment 1 withdrew the source-token
cross-arm stage (predetermined: source tokens precede the tag, so their states are arm-invariant). This file is Step 1A:
the instruction-region B->A / C->A transplant.

Pointed-A/B/C prompts are token-aligned (differ only at the tag token). For each triple/rotation/carrier we run clean
pointed-A, -B, -C (ceilings + donors), then transplant the donor's block outputs over the instruction region
[tag token, end of user turn) into the recipient-A run at blocks >= L (sweep). Endpoint: carrier presence profile
p = (s_A, s_B, s_C); analysis computes the restoration fraction R_L along the clean A->donor axis. A->A self-patch is a
bitwise no-op gate; B->A should move toward B, C->A toward C (target specificity).

Stage `smoke` : tokenizer-only token-alignment + tag-position + instruction-region check (no model).
Usage: selection_localization.py smoke|ptr_transplant
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
assert STAGE in ("smoke", "ptr_transplant", "decomp", "transfer", "region_split", "random_control")
OUT = os.path.join(R.PROJECT, "H1", "outputs", "selection_localization"); os.makedirs(OUT, exist_ok=True)
RUN_ID = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
TAGS = ["A", "B", "C"]
L_SWEEP = [36, 40, 44, 48, 51, 55]
_bank = [w for p in M.EVAL_BANK_1 + M.EVAL_BANK_2 for w in p]
TRIPLES = [tuple(_bank[3 * i:3 * i + 3]) for i in range(8)]
CARRIERS = M.EVAL_CARRIERS
DECOYS = M.FIT_WORDS[:8]
ALL_LAYERS = list(range(R.N_SRC))
COPY = "copy the following text exactly, word for word"


def user_text(words, arm, carrier):
    head = f'Here are three words: (A) "{words[0]}", (B) "{words[1]}", (C) "{words[2]}"'
    tail = f". Keep the word tagged {arm} in mind while you {COPY}"      # pointed arms only (A/B/C)
    return head + tail + ":\n\n" + carrier


def rotate(tr, r):
    return tuple(tr[(i + r) % 3] for i in range(3))


def render_arm(tok, words, arm, ck):
    car = M.CARRIERS[ck]
    return Rn.render(tok, user_text(words, arm, car), car, sources=[(f"X{j}", words[j], True) for j in range(3)], name=f"{words}|{arm}|{ck}")


def tag_position(rA, rB, rC):
    """The single token position where the three token-aligned arm renderings differ."""
    a, b, c = rA.ids, rB.ids, rC.ids
    assert len(a) == len(b) == len(c), f"arm renderings not token-aligned: {len(a)},{len(b)},{len(c)}"
    diff = [i for i in range(len(a)) if not (a[i] == b[i] == c[i])]
    assert len(diff) == 1, f"arms differ at {len(diff)} positions, expected 1: {diff}"
    return diff[0]


def smoke():
    tok = R.make_tokenizer()
    for ti in (0, 3, 7):
        tr = TRIPLES[ti]
        for ck in CARRIERS:
            rA = render_arm(tok, tr, "A", ck); rB = render_arm(tok, tr, "B", ck); rC = render_arm(tok, tr, "C", ck)
            tp = tag_position(rA, rB, rC); cs = rA.meta["carrier_start"]
            print(f"T{ti} {tr} {ck}: len={len(rA)} tag_pos={tp} instr_region=[{tp},{cs}) ({cs-tp} tokens) "
                  f"tag_tokens={[tok.decode([r.ids[tp]]) for r in (rA,rB,rC)]}")
    print("SMOKE OK")


def presence_cols(tok):
    SRC = [w for tr in TRIPLES for w in tr]
    TID = {w: Rn.single_token_id(tok, w) for w in SRC + DECOYS}
    assert all(v is not None for v in TID.values()), {k: v for k, v in TID.items() if v is None}
    return SRC, DECOYS, TID


def ptr_transplant():
    t0 = time.time(); tok = R.make_tokenizer()
    from jlens.hf import from_hf
    model = R.load_model(); lm = from_hf(model, tok, compile=False); ALL = list(range(R.N_BLOCKS))
    run = H.make_run(model, lm, ALL); LEN = R.load_lenses(("J_NP",))["J_NP"]
    SRC, DEC, TID = presence_cols(tok); COLS = SRC + DEC
    ro = RO.LensReadout(model, lm, LEN, [TID[w] for w in COLS])
    RAW, META = {}, {"cells": {}, "triples": [list(t) for t in TRIPLES], "columns": COLS, "carriers": CARRIERS,
                     "tags": TAGS, "l_sweep": L_SWEEP, "decoys": DEC, "stage": STAGE}
    n = 0

    def record(tag, r, acts, logits):
        inter = r.interior
        RAW[f"{tag}|z"] = ro.z(acts, inter, ALL_LAYERS).astype(np.float16)
        cs, ce = r.meta["carrier_start"], r.meta["carrier_end"]; nll, top1, _ = RO.carrier_damage(logits, r.ids, cs, ce)
        RAW[f"{tag}|nll"] = np.float32(nll); RAW[f"{tag}|top1"] = top1

    for ck in CARRIERS:
        for ti, tr in enumerate(TRIPLES):
            for rot in range(3):
                words = rotate(tr, rot)
                rr = {a: render_arm(tok, words, a, ck) for a in TAGS}
                tp = tag_position(rr["A"], rr["B"], rr["C"]); cs = rr["A"].meta["carrier_start"]
                instr = list(range(tp, cs))                              # [tag token, end of user turn)
                acts = {}; lgA = None
                for a in TAGS:                                           # clean pointed A/B/C (ceilings + donor states)
                    ac, lg = run(rr[a].ids); n += 1
                    record(f"T{ti}|{ck}|rot{rot}|clean{a}", rr[a], ac, lg)
                    acts[a] = ac
                    if a == "A":
                        lgA = lg
                base = f"T{ti}|{ck}|rot{rot}"
                META["cells"][base] = {"words": list(words), "tag_pos": tp, "carrier_start": cs, "instr_len": len(instr)}
                # A->A self-patch no-op gate (at the largest sweep block set): must be bitwise equal to clean A
                own = {l: acts["A"][l][0, instr, :].clone() for l in ALL}
                a_s, l_s = run(rr["A"].ids, H.SpanWriter(lm.layers, [l for l in ALL if l >= L_SWEEP[0]], instr, own)); n += 1
                assert torch.equal(l_s, lgA) and all(torch.equal(a_s[l], acts["A"][l]) for l in ALL), f"self-patch != clean {base}"
                del a_s
                # donor -> A transplants over the instruction region at blocks >= L
                for D in ("B", "C"):
                    dstate = {l: acts[D][l][0, instr, :].clone() for l in ALL}
                    for L in L_SWEEP:
                        aD, lD = run(rr["A"].ids, H.SpanWriter(lm.layers, [l for l in ALL if l >= L], instr, dstate)); n += 1
                        for l in range(L):                              # positions patched only at >=L: <L identical to clean A
                            assert torch.equal(aD[l][0, rr["A"].interior, :], acts["A"][l][0, rr["A"].interior, :]), f"<L identity {base} {D} L{L}"
                        record(f"{base}|{D}toA|L{L}", rr["A"], aD, lD); del aD
                del acts
            print(f"  [ptr] {ck} T{ti}: {n} forwards ({time.time()-t0:.0f}s)", flush=True)
    META.update({"run_id": RUN_ID, "n_forwards": n, "elapsed_s": round(time.time() - t0, 1), "token_ids": TID})
    np.savez_compressed(os.path.join(OUT, f"raw_{STAGE}.npz"), **RAW)
    json.dump(META, open(os.path.join(OUT, f"meta_{STAGE}.json"), "w"), indent=1)
    man = R.manifest_block(); man.update({"run_id": RUN_ID, "stage": STAGE, "script": os.path.relpath(__file__, R.PROJECT),
                                          "design": "H1/design_specs/selection_localization.md",
                                          "raw_sha256": hashlib.sha256(open(os.path.join(OUT, f"raw_{STAGE}.npz"), "rb").read()).hexdigest()})
    json.dump(man, open(os.path.join(OUT, f"manifest_{STAGE}.json"), "w"), indent=1)
    print(f"[done {STAGE}] {n} forwards, {time.time()-t0:.0f}s -> {OUT}")


def _setup():
    tok = R.make_tokenizer()
    from jlens.hf import from_hf
    model = R.load_model(); lm = from_hf(model, tok, compile=False); ALL = list(range(R.N_BLOCKS))
    run = H.make_run(model, lm, ALL); LEN = R.load_lenses(("J_NP",))["J_NP"]
    SRC, DEC, TID = presence_cols(tok); COLS = SRC + DEC
    ro = RO.LensReadout(model, lm, LEN, [TID[w] for w in COLS])
    return tok, lm, ALL, run, ro, COLS, DEC, TID


def decomp():
    """Step 1B: at boundaries {36,44}, patch tag-only vs suffix vs full region B->A / C->A; presence profile."""
    t0 = time.time(); tok, lm, ALL, run, ro, COLS, DEC, TID = _setup()
    LREG = [36, 44]
    RAW, META = {}, {"cells": {}, "triples": [list(t) for t in TRIPLES], "columns": COLS, "carriers": CARRIERS,
                     "tags": TAGS, "l_reg": LREG, "decoys": [COLS[i] for i in range(len(COLS) - len(DECOYS), len(COLS))], "stage": STAGE}
    n = 0

    def record(tag, r, acts, logits):
        RAW[f"{tag}|z"] = ro.z(acts, r.interior, ALL_LAYERS).astype(np.float16)
        cs, ce = r.meta["carrier_start"], r.meta["carrier_end"]; nll, top1, _ = RO.carrier_damage(logits, r.ids, cs, ce)
        RAW[f"{tag}|nll"] = np.float32(nll); RAW[f"{tag}|top1"] = top1

    for ck in CARRIERS:
        for ti, tr in enumerate(TRIPLES):
            for rot in range(3):
                words = rotate(tr, rot); rr = {a: render_arm(tok, words, a, ck) for a in TAGS}
                tp = tag_position(rr["A"], rr["B"], rr["C"]); cs = rr["A"].meta["carrier_start"]
                regions = {"tag": [tp], "suffix": list(range(tp + 1, cs)), "full": list(range(tp, cs))}
                acts = {}
                for a in TAGS:
                    ac, lg = run(rr[a].ids); n += 1; record(f"T{ti}|{ck}|rot{rot}|clean{a}", rr[a], ac, lg); acts[a] = ac
                base = f"T{ti}|{ck}|rot{rot}"; META["cells"][base] = {"words": list(words), "tag_pos": tp, "carrier_start": cs}
                for D in ("B", "C"):
                    for rname, rpos in regions.items():
                        dstate = {l: acts[D][l][0, rpos, :].clone() for l in ALL}
                        for L in LREG:
                            aD, lD = run(rr["A"].ids, H.SpanWriter(lm.layers, [l for l in ALL if l >= L], rpos, dstate)); n += 1
                            record(f"{base}|{D}toA|{rname}|L{L}", rr["A"], aD, lD); del aD
                del acts
            print(f"  [decomp] {ck} T{ti}: {n} forwards ({time.time()-t0:.0f}s)", flush=True)
    _save(RAW, META, n, t0)


def transfer():
    """Step 1C: does the B->A / C->A instruction transplant redirect the causal transfer profile C_j (not just presence)?"""
    t0 = time.time(); tok, lm, ALL, run, ro, COLS, DEC, TID = _setup()
    LT = 36
    DONOR = {}
    for _ti, _tr in enumerate(TRIPLES):
        _nx = TRIPLES[(_ti + 1) % len(TRIPLES)]
        for _i, _w in enumerate(_tr):
            DONOR[_w] = _nx[_i]
    RAW, META = {}, {"cells": {}, "triples": [list(t) for t in TRIPLES], "columns": COLS, "carriers": CARRIERS,
                     "donor": DONOR, "tags": TAGS, "l_transplant": LT,
                     "decoys": [COLS[i] for i in range(len(COLS) - len(DECOYS), len(COLS))], "stage": STAGE}
    n = 0

    def record(tag, r, acts, logits):
        RAW[f"{tag}|z"] = ro.z(acts, r.interior, ALL_LAYERS).astype(np.float16)
        cs, ce = r.meta["carrier_start"], r.meta["carrier_end"]; nll, top1, _ = RO.carrier_damage(logits, r.ids, cs, ce)
        RAW[f"{tag}|nll"] = np.float32(nll); RAW[f"{tag}|top1"] = top1

    for ck in CARRIERS:
        for ti, tr in enumerate(TRIPLES):
            for rot in range(3):
                words = rotate(tr, rot); rr = {a: render_arm(tok, words, a, ck) for a in TAGS}
                tp = tag_position(rr["A"], rr["B"], rr["C"]); cs = rr["A"].meta["carrier_start"]
                instr = list(range(tp, cs)); RA = rr["A"]
                spans = {j: RA.spans[f"X{j}"]["full"] for j in range(3)}
                for j in range(3):
                    assert max(spans[j]) < tp, f"source span overlaps instruction region {ti} j={j}"
                base = f"T{ti}|{ck}|rot{rot}"; META["cells"][base] = {"words": list(words), "tag_pos": tp}
                acts = {}                                                # clean A/B/C: record noswap + keep for instruction states
                for a in TAGS:
                    ac, lg = run(rr[a].ids); n += 1
                    record(f"{base}|clean{a}|noswap", RA, ac, lg); acts[a] = ac
                donor_src = {}
                for j in range(3):
                    dw = list(words); dw[j] = DONOR[words[j]]
                    rd = render_arm(tok, tuple(dw), "A", ck)
                    assert len(rd) == len(RA) and rd.spans[f"X{j}"]["full"] == spans[j], f"donor geom {base} j={j}"
                    ad, _ = run(rd.ids); n += 1; donor_src[j] = {l: ad[l][0, spans[j], :].clone() for l in ALL}; del ad
                instrpatch = {"BtoA": {l: acts["B"][l][0, instr, :].clone() for l in ALL},
                              "CtoA": {l: acts["C"][l][0, instr, :].clone() for l in ALL}}
                conds = {"cleanA": (RA.ids, None), "cleanB": (rr["B"].ids, None), "cleanC": (rr["C"].ids, None),
                         "BtoA": (RA.ids, instrpatch["BtoA"]), "CtoA": (RA.ids, instrpatch["CtoA"])}
                for cname, (ids, ipatch) in conds.items():
                    ip = H.SpanWriter(lm.layers, [l for l in ALL if l >= LT], instr, ipatch) if ipatch is not None else None
                    if ipatch is not None:                               # transplant noswap baseline
                        ac, lg = run(ids, ip); n += 1; record(f"{base}|{cname}|noswap", RA, ac, lg)
                    for j in range(3):
                        sw = H.SpanWriter(lm.layers, [l for l in ALL if l >= LT], spans[j], donor_src[j])
                        ac, lg = run(ids, H.Both(ip, sw)); n += 1; record(f"{base}|{cname}|swap{j}", RA, ac, lg)
                del acts
            print(f"  [transfer] {ck} T{ti}: {n} forwards ({time.time()-t0:.0f}s)", flush=True)
    _save(RAW, META, n, t0)


def region_split():
    """Corrected Step 1B (Amendment 3): split the post-tag prefix into tag / instr_tail / user_carrier / gap / full."""
    t0 = time.time(); tok, lm, ALL, run, ro, COLS, DEC, TID = _setup()
    LREG = [36, 44]; REGS = ["tag", "instr_tail", "user_carrier", "gap", "full"]
    RAW, META = {}, {"cells": {}, "triples": [list(t) for t in TRIPLES], "columns": COLS, "carriers": CARRIERS,
                     "tags": TAGS, "l_reg": LREG, "regions": REGS,
                     "decoys": [COLS[i] for i in range(len(COLS) - len(DECOYS), len(COLS))], "stage": STAGE}
    n = 0

    def record(tag, r, acts, logits):
        RAW[f"{tag}|z"] = ro.z(acts, r.interior, ALL_LAYERS).astype(np.float16)
        cs, ce = r.meta["carrier_start"], r.meta["carrier_end"]; nll, top1, _ = RO.carrier_damage(logits, r.ids, cs, ce)
        RAW[f"{tag}|nll"] = np.float32(nll); RAW[f"{tag}|top1"] = top1

    for ck in CARRIERS:
        for ti, tr in enumerate(TRIPLES):
            for rot in range(3):
                words = rotate(tr, rot); rr = {a: render_arm(tok, words, a, ck) for a in TAGS}
                tp = tag_position(rr["A"], rr["B"], rr["C"]); cs = rr["A"].meta["carrier_start"]
                uc = rr["A"].spans["user_carrier"]
                regions = {"tag": [tp], "instr_tail": list(range(tp + 1, uc[0])), "user_carrier": list(range(uc[0], uc[1])),
                           "gap": list(range(uc[1], cs)), "full": list(range(tp, cs))}
                acts = {}
                for a in TAGS:
                    ac, lg = run(rr[a].ids); n += 1; record(f"T{ti}|{ck}|rot{rot}|clean{a}", rr[a], ac, lg); acts[a] = ac
                base = f"T{ti}|{ck}|rot{rot}"; META["cells"][base] = {"words": list(words), "tag_pos": tp, "carrier_start": cs,
                                                                     "user_carrier": list(uc), "region_sizes": {k: len(v) for k, v in regions.items()}}
                for D in ("B", "C"):
                    for rname, rpos in regions.items():
                        if not rpos:
                            continue
                        dstate = {l: acts[D][l][0, rpos, :].clone() for l in ALL}
                        for L in LREG:
                            aD, lD = run(rr["A"].ids, H.SpanWriter(lm.layers, [l for l in ALL if l >= L], rpos, dstate)); n += 1
                            record(f"{base}|{D}toA|{rname}|L{L}", rr["A"], aD, lD); del aD
                del acts
            print(f"  [region_split] {ck} T{ti}: {n} forwards ({time.time()-t0:.0f}s)", flush=True)
    _save(RAW, META, n, t0)


def random_control():
    """Amendment 4: norm-matched isotropic, position-shuffled and sign-flipped controls beside the B->A / C->A transplant.

    At boundary 36 over the full instruction region, each control writes h_A + delta at every layer >= 36, where delta
    is (rand) an isotropic direction scaled to ||h_D - h_A|| at that (layer, position), (shuff) the donor delta with region
    positions permuted, or (flip) minus the donor delta. Endpoint: carrier presence profile, as in ptr_transplant.
    """
    t0 = time.time(); tok, lm, ALL, run, ro, COLS, DEC, TID = _setup()
    LT = 36; SEEDS = [0, 1]
    RAW, META = {}, {"cells": {}, "triples": [list(t) for t in TRIPLES], "columns": COLS, "carriers": CARRIERS,
                     "tags": TAGS, "l_transplant": LT, "seeds": SEEDS,
                     "conds": ["cleanA", "cleanB", "cleanC", "BtoA", "CtoA"] + [f"rand{D}_s{s}" for D in "BC" for s in SEEDS] + [f"shuff{D}" for D in "BC"] + [f"flip{D}" for D in "BC"],
                     "decoys": [COLS[i] for i in range(len(COLS) - len(DECOYS), len(COLS))], "stage": STAGE}
    n = 0

    def record(tag, r, acts, logits):
        RAW[f"{tag}|z"] = ro.z(acts, r.interior, ALL_LAYERS).astype(np.float16)
        cs, ce = r.meta["carrier_start"], r.meta["carrier_end"]; nll, top1, _ = RO.carrier_damage(logits, r.ids, cs, ce)
        RAW[f"{tag}|nll"] = np.float32(nll); RAW[f"{tag}|top1"] = top1

    LGE = [l for l in ALL if l >= LT]
    for ck in CARRIERS:
        for ti, tr in enumerate(TRIPLES):
            for rot in range(3):
                words = rotate(tr, rot); rr = {a: render_arm(tok, words, a, ck) for a in TAGS}
                tp = tag_position(rr["A"], rr["B"], rr["C"]); cs = rr["A"].meta["carrier_start"]
                instr = list(range(tp, cs)); P = len(instr)
                base = f"T{ti}|{ck}|rot{rot}"; META["cells"][base] = {"words": list(words), "tag_pos": tp, "carrier_start": cs, "instr_len": P}
                acts = {}
                for a in TAGS:
                    ac, lg = run(rr[a].ids); n += 1; record(f"{base}|clean{a}", rr[a], ac, lg); acts[a] = ac
                hA = {l: acts["A"][l][0, instr, :].float() for l in LGE}
                states = {}
                cell_seed = (ti * 7919 + rot * 104729 + CARRIERS.index(ck) * 15485863) & 0x7fffffff
                for D in ("B", "C"):
                    hD = {l: acts[D][l][0, instr, :].float() for l in LGE}
                    delta = {l: hD[l] - hA[l] for l in LGE}
                    states[f"{D}toA"] = {l: hD[l].clone() for l in LGE}
                    for s in SEEDS:
                        g = torch.Generator(device="cpu").manual_seed(cell_seed + 1000 * s + (0 if D == "B" else 500))
                        st = {}
                        for l in LGE:
                            r = torch.randn(P, hA[l].shape[1], generator=g).to(hA[l].device)
                            r = r / r.norm(dim=1, keepdim=True) * delta[l].norm(dim=1, keepdim=True)
                            st[l] = hA[l] + r
                        states[f"rand{D}_s{s}"] = st
                    g = torch.Generator(device="cpu").manual_seed(cell_seed + 77 + (0 if D == "B" else 500))
                    perm = torch.randperm(P, generator=g).to(hA[LGE[0]].device)
                    states[f"shuff{D}"] = {l: hA[l] + delta[l][perm] for l in LGE}
                    states[f"flip{D}"] = {l: hA[l] - delta[l] for l in LGE}
                for cname, st in states.items():
                    src = {l: st[l].to(acts["A"][l].dtype) for l in LGE}
                    aD, lD = run(rr["A"].ids, H.SpanWriter(lm.layers, LGE, instr, src)); n += 1
                    record(f"{base}|{cname}", rr["A"], aD, lD); del aD
                del acts, states, hA
            print(f"  [random_control] {ck} T{ti}: {n} forwards ({time.time()-t0:.0f}s)", flush=True)
    _save(RAW, META, n, t0)


def _save(RAW, META, n, t0):
    META.update({"run_id": RUN_ID, "n_forwards": n, "elapsed_s": round(time.time() - t0, 1)})
    np.savez_compressed(os.path.join(OUT, f"raw_{STAGE}.npz"), **RAW)
    json.dump(META, open(os.path.join(OUT, f"meta_{STAGE}.json"), "w"), indent=1)
    man = R.manifest_block(); man.update({"run_id": RUN_ID, "stage": STAGE, "script": os.path.relpath(__file__, R.PROJECT),
                                          "design": "H1/design_specs/selection_localization.md",
                                          "raw_sha256": hashlib.sha256(open(os.path.join(OUT, f"raw_{STAGE}.npz"), "rb").read()).hexdigest()})
    json.dump(man, open(os.path.join(OUT, f"manifest_{STAGE}.json"), "w"), indent=1)
    print(f"[done {STAGE}] {n} forwards, {time.time()-t0:.0f}s -> {OUT}")


if __name__ == "__main__":
    {"smoke": smoke, "ptr_transplant": ptr_transplant, "decomp": decomp, "transfer": transfer, "region_split": region_split, "random_control": random_control}[STAGE]()
