"""H3 recompute_cost_ladder (design H3/design_specs/recompute_cost_ladder.md, registered 2026-09-09).

Varies recompute cost inside one organism, with the block-36 boundary measured per tier, to separate
"the carrier copy is used more when recomputation is expensive" from "the two earlier organisms had
different boundaries". t1 and t3 share identical source strings and donors and differ only in the
instruction and the question. Usage: recompute_cost_ladder.py smoke|run
"""
import os, sys, json, time, hashlib
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "..", "common", "scripts"))
import numpy as np, torch
import registry as R, materials as M, rendering as Rn, readout as RO, hooks as H

STAGE = sys.argv[1] if len(sys.argv) > 1 else "smoke"
OUT = R.out_dir("H3", "outputs", "recompute_cost_ladder")
RUN_ID = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()); SEED = 20260909
COPY = "copy the following text exactly, word for word"; CARRIERS = ["C0", "C1", "C2", "C3"]
LX = 36; DECOYS = M.FIT_WORDS[:8]
NUM = {n: w for n, w in zip(range(2, 21), ["two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven",
                                           "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen",
                                           "nineteen", "twenty"])}
PAIRS = [(2, 2), (2, 3), (2, 4), (3, 4), (3, 5), (4, 5), (4, 6), (5, 5)]              # sums 4..10, doubles 8..20
TRIPLES = [(2, 2, 3), (2, 3, 3), (2, 3, 4), (3, 3, 4), (2, 4, 5), (3, 4, 5), (4, 4, 5), (4, 5, 5)]   # sums 7..14


def tiers():
    """{tier: [ {src, donor_src, latent, donor_latent, instr, question} ]} with donor = item (i+3) mod 8."""
    T = {}
    ps = [" and ".join(NUM[x] for x in p) for p in PAIRS]
    ts = [" and ".join(NUM[x] for x in t) for t in TRIPLES]
    T["t1_memorised"] = [dict(src=ps[i], donor_src=ps[(i + 3) % 8], latent=NUM[sum(PAIRS[i])], donor_latent=NUM[sum(PAIRS[(i + 3) % 8])],
                              instr="Keep their sum in mind", question="What is the sum of the pair? Answer with one word.", noun="pair") for i in range(8)]
    T["t3_chained"] = [dict(src=ps[i], donor_src=ps[(i + 3) % 8], latent=NUM[2 * sum(PAIRS[i])], donor_latent=NUM[2 * sum(PAIRS[(i + 3) % 8])],
                            instr="Keep double their sum in mind", question="What is double the sum of the pair? Answer with one word.", noun="pair") for i in range(8)]
    T["t2_composed"] = [dict(src=ts[i], donor_src=ts[(i + 3) % 8], latent=NUM[sum(TRIPLES[i])], donor_latent=NUM[sum(TRIPLES[(i + 3) % 8])],
                             instr="Keep their sum in mind", question="What is the sum of the triple? Answer with one word.", noun="triple") for i in range(8)]
    return T


def utext(it, src, car): return f'Here is the {it["noun"]} "{src}". {it["instr"]} while you {COPY}:\n\n' + car


def forms(tok, w):
    out = []
    for f in (w, " " + w, w.capitalize(), " " + w.capitalize()):
        ids = tok(f, add_special_tokens=False).input_ids
        if len(ids) == 1 and ids[0] not in out: out.append(ids[0])
    return out


def smoke():
    tok = R.make_tokenizer(); T = tiers(); ok = bad = 0
    for tn, items in T.items():
        for i, it in enumerate(items):
            assert it["latent"] != it["donor_latent"], (tn, i, it)
            for ck in CARRIERS:
                car = M.CARRIERS[ck]
                r = Rn.render(tok, utext(it, it["src"], car), car, sources=[("P", it["src"], True)], extra_turns=[(it["question"], "")])
                rd = Rn.render(tok, utext(it, it["donor_src"], car), car, sources=[("P", it["donor_src"], True)], extra_turns=[(it["question"], "")])
                good = len(rd) == len(r) and rd.spans["P"]["full"] == r.spans["P"]["full"] and rd.meta["carrier_start"] == r.meta["carrier_start"]
                ok += good; bad += (not good)
    t1, t3 = T["t1_memorised"], T["t3_chained"]
    print(f"geometry ok {ok}, bad {bad}; t1/t3 source strings identical: {[a['src'] for a in t1] == [b['src'] for b in t3]}")
    print("latents  t1:", [a["latent"] for a in t1], "\n         t3:", [a["latent"] for a in t3], "\n         t2:", [a["latent"] for a in T["t2_composed"]])
    print("all latents single-token:", all(Rn.single_token_id(tok, a["latent"]) is not None and Rn.single_token_id(tok, a["donor_latent"]) is not None for v in T.values() for a in v))
    r = Rn.render(tok, utext(t3[0], t3[0]["src"], M.CARRIERS["C0"]), M.CARRIERS["C0"], sources=[("P", t3[0]["src"], True)], extra_turns=[(t3[0]["question"], "")])
    print("\nexample t3 cell:\n" + r.meta["full"][:330].replace("\n", " | "))
    print("SMOKE OK" if bad == 0 else "SMOKE FAIL")


def main():
    if STAGE == "smoke":
        smoke(); return
    tok = R.make_tokenizer()
    from jlens.hf import from_hf
    model = R.load_model(); lm = from_hf(model, tok, compile=False)
    ALL = list(range(R.N_BLOCKS)); SRC = list(range(R.N_SRC)); run = H.make_run(model, lm, ALL); lge = [l for l in ALL if l >= LX]
    LEN = R.load_lenses(("J_NP",))["J_NP"]
    COLS = [NUM[n] for n in sorted(NUM)] + [d for d in DECOYS if d not in NUM.values()]
    TID = {w: Rn.single_token_id(tok, w) for w in COLS}; assert all(v is not None for v in TID.values())
    ro = RO.LensReadout(model, lm, LEN, [TID[w] for w in COLS])
    T = tiers()
    RAW, META = {}, {"columns": COLS, "decoys": [d for d in DECOYS if d not in NUM.values()], "carriers": CARRIERS, "lx": LX,
                     "seed": SEED, "cells": {}, "tiers": {k: v for k, v in T.items()}, "answer_set": [NUM[n] for n in sorted(NUM)]}
    t0 = time.time(); n = 0
    AID = {w: forms(tok, w) for w in [NUM[k] for k in sorted(NUM)]}

    def rec(tag, r, logits, acts, it, Q):
        lp = torch.log_softmax(logits[0, -1].float(), -1)
        sc = {w: float(torch.logsumexp(lp[AID[w]], 0)) for w in AID}
        RAW[f"{tag}|scores"] = np.array([sc[w] for w in AID], np.float32)
        RAW[f"{tag}|greedy"] = tok.decode(int(logits[0, -1].argmax())).strip()
        RAW[f"{tag}|z_carr"] = ro.z(acts, r.interior, SRC).astype(np.float16)
        RAW[f"{tag}|z_q"] = ro.z(acts, Q, SRC).astype(np.float16)
        cs, ce = r.meta["carrier_start"], r.meta["carrier_end"]; nll, _, _ = RO.carrier_damage(logits, r.ids, cs, ce)
        RAW[f"{tag}|nll"] = np.float32(nll)

    META["answer_order"] = list(AID)
    for tn, items in T.items():
        for i, it in enumerate(items):
            for ck in CARRIERS:
                car = M.CARRIERS[ck]; base = f"{tn}|i{i}|{ck}"
                r = Rn.render(tok, utext(it, it["src"], car), car, sources=[("P", it["src"], True)], extra_turns=[(it["question"], "")])
                rd = Rn.render(tok, utext(it, it["donor_src"], car), car, sources=[("P", it["donor_src"], True)], extra_turns=[(it["question"], "")])
                span = r.spans["P"]["full"]; cs, ce = r.meta["carrier_start"], r.meta["carrier_end"]
                assert len(rd) == len(r) and rd.spans["P"]["full"] == span and rd.meta["carrier_start"] == cs, f"geometry {base}"
                carr = list(range(cs, ce)); Q = list(range(ce, len(r)))
                META["cells"][base] = {"tier": tn, "item": i, "src": it["src"], "donor_src": it["donor_src"], "latent": it["latent"],
                                       "donor_latent": it["donor_latent"], "span": [span[0], span[-1]], "carrier": [cs, ce], "Q": [ce, len(r)]}
                ac, lg = run(r.ids); n += 1; rec(f"{base}|clean", r, lg, ac, it, Q)
                ad, lgd = run(rd.ids); n += 1; rec(f"{base}|donor_clean", rd, lgd, ad, it, Q)
                O36 = {l: ad[l][0, span, :].clone() for l in lge}; Oall = {l: ad[l][0, span, :].clone() for l in ALL}
                C36 = {l: ad[l][0, carr, :].clone() for l in lge}; Call = {l: ad[l][0, carr, :].clone() for l in ALL}
                ownall = {l: ac[l][0, carr, :].clone() for l in ALL}
                g = torch.Generator(device="cpu").manual_seed(SEED + 7 * i + CARRIERS.index(ck) + hash(tn) % 997)
                Crand = {}
                for l in lge:
                    hC = ac[l][0, carr, :].float(); dn = (C36[l].float() - hC).norm(dim=1, keepdim=True)
                    v = torch.randn(len(carr), hC.shape[1], generator=g).to(hC.device)
                    Crand[l] = (hC + v / v.norm(dim=1, keepdim=True) * dn).to(ac[l].dtype)
                conds = {"S_donor0": (lambda: H.SpanWriter(lm.layers, ALL, span, Oall), False),
                         "S_donor": (lambda: H.SpanWriter(lm.layers, lge, span, O36), False),
                         "C_full": (lambda: H.SpanWriter(lm.layers, lge, carr, C36), True),
                         "C_all": (lambda: H.SpanWriter(lm.layers, ALL, carr, Call), True),
                         "C_rand": (lambda: H.SpanWriter(lm.layers, lge, carr, Crand), True),
                         "NEC_all": (lambda: H.Both(H.SpanWriter(lm.layers, ALL, span, Oall), H.SpanWriter(lm.layers, ALL, carr, ownall)), False)}
                for cond, (mk, clean_span) in conds.items():
                    a_, l_ = run(r.ids, mk()); n += 1
                    if clean_span:
                        assert all(torch.equal(a_[l][0, span, :], ac[l][0, span, :]) for l in ALL), f"source touched under {cond} {base}"
                    rec(f"{base}|{cond}", r, l_, a_, it, Q); del a_
                del ac, ad
        print(f"  [{tn}] {n} forwards ({time.time()-t0:.0f}s)", flush=True)
    META.update({"run_id": RUN_ID, "n_forwards": n, "elapsed_s": round(time.time() - t0, 1)})
    np.savez_compressed(os.path.join(OUT, "raw_run.npz"), **RAW)
    json.dump(META, open(os.path.join(OUT, "meta_run.json"), "w"), indent=1, default=str)
    man = R.manifest_block(); man.update({"run_id": RUN_ID, "stage": "run", "script": os.path.relpath(__file__, R.PROJECT),
                                          "design": "H3/design_specs/recompute_cost_ladder.md",
                                          "raw_sha256": hashlib.sha256(open(os.path.join(OUT, "raw_run.npz"), "rb").read()).hexdigest()})
    json.dump(man, open(os.path.join(OUT, "manifest_run.json"), "w"), indent=1)
    print(f"[done] {n} forwards, {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
