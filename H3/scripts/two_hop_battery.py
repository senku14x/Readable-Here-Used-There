"""H3 two_hop_organism — stages `full` and `noclue` (design H3/design_specs/two_hop_organism.md, Amendment 3).

Materials: anthropics/jacobian-lens @ 581d398 data/experiments/probe-swap.json, the 12 items with a released
length-matched donor clue (frozen in H3/design_specs/two_hop_items.json). Readout columns cover BOTH pairs —
the bridge entity (intermediate/swap_to) and the maintained answer (answer/swap_answer) — at the carrier interior
and at the question positions. Usage: two_hop_battery.py full|noclue|smoke
"""
import os, sys, json, time, hashlib, re
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "..", "common", "scripts"))
import numpy as np, torch
import registry as R, materials as M, rendering as Rn, readout as RO, hooks as H

STAGE = sys.argv[1] if len(sys.argv) > 1 else "smoke"
assert STAGE in ("smoke", "full", "noclue")
OUT = R.out_dir("H3", "outputs", "two_hop_organism")
RUN_ID = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()); SEED = 20260909
COPY = "copy the following text exactly, word for word"
CARRIERS = ["C0", "C1", "C2", "C3"]; LX = 36; QL = list(range(36, 63)); DECOYS = M.FIT_WORDS[:8]
ITEMS = json.load(open(os.path.join(R.PROJECT, "H3", "design_specs", "two_hop_items.json")))["pilot_items"]
STRIP = re.compile(r"\s+(is called a|is called the|is the|is a|are|is)\s*$")
QUESTION = "Complete the fact from the clue you were given, using one word."

clue_body = lambda p: STRIP.sub("", p.replace("Fact: ", "").strip())
utext = lambda body, car: f"Here is a clue: {body}. Keep the answer to the clue in mind while you {COPY}:\n\n" + car


def entity_diff(it):
    """The single word by which this item's clue differs from its donor clue, or None (paraphrase pair)."""
    a, b = clue_body(it["prompt"]).split(), clue_body(it["donor_prompt"]).split()
    d1 = [w for w in a if w not in b]; d2 = [w for w in b if w not in a]
    return (d1[0], d2[0]) if len(d1) == 1 and len(d2) == 1 else None


def forms(tok, w):
    out = []
    for f in (w, " " + w, w.capitalize(), " " + w.capitalize(), w.lower(), " " + w.lower()):
        ids = tok(f, add_special_tokens=False).input_ids
        if len(ids) == 1 and ids[0] not in out: out.append(ids[0])
    return out


def smoke():
    tok = R.make_tokenizer(); tl = lambda s: len(tok(s, add_special_tokens=False).input_ids)
    ent = {it["name"]: entity_diff(it) for it in ITEMS}
    print("entity-swap items:", sum(v is not None for v in ent.values()), "/", len(ITEMS),
          "| paraphrase items:", [k for k, v in ent.items() if v is None])
    words = sorted({w for it in ITEMS for w in (it["intermediate"], it["swap_to"], it["answer"], it["swap_answer"])})
    print(f"{len(words)} readout words, all single-token:", all(Rn.single_token_id(tok, w) is not None for w in words),
          "| collision with decoys:", set(words) & set(DECOYS))
    ok = 0
    for it in ITEMS:
        e = ent[it["name"]]
        for ck in CARRIERS:
            car = M.CARRIERS[ck]
            r = Rn.render(tok, utext(clue_body(it["prompt"]), car), car, sources=[("CLUE", clue_body(it["prompt"]), False)], extra_turns=[(QUESTION, "")])
            rd = Rn.render(tok, utext(clue_body(it["donor_prompt"]), car), car, sources=[("CLUE", clue_body(it["donor_prompt"]), False)], extra_turns=[(QUESTION, "")])
            good = len(rd) == len(r) and rd.spans["CLUE"]["full"] == r.spans["CLUE"]["full"]
            if e is not None:
                nb = clue_body(it["prompt"]).replace(e[0], "X")
                rn = Rn.render(tok, utext(nb, car), car, sources=[("CLUE", nb, False)], extra_turns=[(QUESTION, "")])
                good = good and len(rn) == len(r) and rn.spans["CLUE"]["full"] == r.spans["CLUE"]["full"]
            ok += good
    print(f"geometry (recipient/donor/placeholder aligned): {ok}/{len(ITEMS)*len(CARRIERS)}")
    print("SMOKE OK" if ok == len(ITEMS) * len(CARRIERS) else "SMOKE FAIL")


def main():
    if STAGE == "smoke":
        smoke(); return
    tok = R.make_tokenizer()
    from jlens.hf import from_hf
    model = R.load_model(); lm = from_hf(model, tok, compile=False)
    ALL = list(range(R.N_BLOCKS)); SRC = list(range(R.N_SRC)); run = H.make_run(model, lm, ALL); lge = [l for l in ALL if l >= LX]
    LEN = R.load_lenses(("J_NP",))["J_NP"]
    words = sorted({w for it in ITEMS for w in (it["intermediate"], it["swap_to"], it["answer"], it["swap_answer"])})
    COLS = words + [d for d in DECOYS if d not in words]
    TID = {w: Rn.single_token_id(tok, w) for w in COLS}; assert all(v is not None for v in TID.values()), TID
    ro = RO.LensReadout(model, lm, LEN, [TID[w] for w in COLS])
    RAW, META = {}, {"columns": COLS, "decoys": [d for d in DECOYS if d not in words], "carriers": CARRIERS, "lx": LX,
                     "q_layers": [QL[0], QL[-1]], "seed": SEED, "stage": STAGE, "cells": {}, "question": QUESTION,
                     "items": ITEMS, "entity_diff": {it["name"]: entity_diff(it) for it in ITEMS},
                     "materials": "anthropics/jacobian-lens@581d398 data/experiments/probe-swap.json"}
    t0 = time.time(); n = 0

    def rec(tag, r, logits, acts, it, Q):
        lp = torch.log_softmax(logits[0, -1].float(), -1)
        RAW[f"{tag}|s_answer"] = np.float32(float(torch.logsumexp(lp[forms(tok, it["answer"])], 0)))
        RAW[f"{tag}|s_swap"] = np.float32(float(torch.logsumexp(lp[forms(tok, it["swap_answer"])], 0)))
        RAW[f"{tag}|greedy"] = tok.decode(int(logits[0, -1].argmax())).strip()
        RAW[f"{tag}|z_carr"] = ro.z(acts, r.interior, SRC).astype(np.float16)
        RAW[f"{tag}|z_q"] = ro.z(acts, Q, SRC).astype(np.float16)
        cs, ce = r.meta["carrier_start"], r.meta["carrier_end"]; nll, _, _ = RO.carrier_damage(logits, r.ids, cs, ce)
        RAW[f"{tag}|nll"] = np.float32(nll)

    def wdiag(tag, src, acts_before, pos, acts_after, layers):
        RAW[f"{tag}|wnorm"] = np.float32(np.mean([(src[l].float() - acts_before[l][0, pos, :].float()).norm(dim=1).mean().item() for l in layers]))
        RAW[f"{tag}|rberr"] = np.float32(np.max([(acts_after[l][0, pos, :].float() - src[l].float()).abs().max().item() for l in layers]))

    for it in ITEMS:
        ent = entity_diff(it)
        if STAGE == "noclue" and ent is None:
            continue
        for ck in CARRIERS:
            car = M.CARRIERS[ck]; base = f"{it['name']}|{ck}"
            body, dbody = clue_body(it["prompt"]), clue_body(it["donor_prompt"])
            rO = Rn.render(tok, utext(body, car), car, sources=[("CLUE", body, False)], extra_turns=[(QUESTION, "")])
            rD = Rn.render(tok, utext(dbody, car), car, sources=[("CLUE", dbody, False)], extra_turns=[(QUESTION, "")])
            assert len(rD) == len(rO) and rD.spans["CLUE"]["full"] == rO.spans["CLUE"]["full"] and rD.meta["carrier_start"] == rO.meta["carrier_start"], f"geometry {base}"
            if STAGE == "noclue":
                nb = body.replace(ent[0], "X")
                r = Rn.render(tok, utext(nb, car), car, sources=[("CLUE", nb, False)], extra_turns=[(QUESTION, "")])
                assert len(r) == len(rO) and r.spans["CLUE"]["full"] == rO.spans["CLUE"]["full"] and r.meta["carrier_start"] == rO.meta["carrier_start"], f"placeholder geometry {base}"
            else:
                r = rO
            span = r.spans["CLUE"]["full"]; cs, ce = r.meta["carrier_start"], r.meta["carrier_end"]
            carr = list(range(cs, ce)); Q = list(range(ce, len(r))); pre = list(range(0, cs))
            META["cells"][base] = {"clue": r.strings.get("CLUE"), "own_clue": body, "donor_clue": dbody, "entity": ent,
                                   "intermediate": it["intermediate"], "swap_to": it["swap_to"], "answer": it["answer"],
                                   "swap_answer": it["swap_answer"], "span": [span[0], span[-1]], "carrier": [cs, ce],
                                   "Q": [ce, len(r)], "n_tokens": len(r)}
            ac, lg = run(r.ids); n += 1
            rec(f"{base}|" + ("clean_nc" if STAGE == "noclue" else "clean"), r, lg, ac, it, Q)
            aO, lgO = run(rO.ids); n += 1                       # own-entity source run (== clean in `full`)
            aD, lgD = run(rD.ids); n += 1
            if STAGE == "full":
                rec(f"{base}|donor_clean", rD, lgD, aD, it, Q)
            else:
                rec(f"{base}|own_clean", rO, lgO, aO, it, Q); rec(f"{base}|donor_clean", rD, lgD, aD, it, Q)
            g = torch.Generator(device="cpu").manual_seed(SEED + (hash(base) % 10007))
            if STAGE == "full":
                O36 = {l: aD[l][0, span, :].clone() for l in lge}; Oall = {l: aD[l][0, span, :].clone() for l in ALL}
                C36 = {l: aD[l][0, carr, :].clone() for l in lge}; Call = {l: aD[l][0, carr, :].clone() for l in ALL}
                own36 = {l: ac[l][0, carr, :].clone() for l in lge}; ownall = {l: ac[l][0, carr, :].clone() for l in ALL}
                Qsrc = {l: aD[l][0, Q, :].clone() for l in QL}; Qown = {l: ac[l][0, Q, :].clone() for l in QL}
                Crand = {}
                for l in lge:
                    hC = ac[l][0, carr, :].float(); dn = (C36[l].float() - hC).norm(dim=1, keepdim=True)
                    v = torch.randn(len(carr), hC.shape[1], generator=g).to(hC.device)
                    Crand[l] = (hC + v / v.norm(dim=1, keepdim=True) * dn).to(ac[l].dtype)
                conds = {
                    "S_donor0": (lambda: H.SpanWriter(lm.layers, ALL, span, Oall), "span"),
                    "S_donor": (lambda: H.SpanWriter(lm.layers, lge, span, O36), "span"),
                    "C_full": (lambda: H.SpanWriter(lm.layers, lge, carr, C36), "carr"),
                    "C_all": (lambda: H.SpanWriter(lm.layers, ALL, carr, Call), "carr"),
                    "C_rand": (lambda: H.SpanWriter(lm.layers, lge, carr, Crand), "carr"),
                    "NEC_all": (lambda: H.Both(H.SpanWriter(lm.layers, ALL, span, Oall), H.SpanWriter(lm.layers, ALL, carr, ownall)), "both"),
                    "NEC36": (lambda: H.Both(H.SpanWriter(lm.layers, lge, span, O36), H.SpanWriter(lm.layers, lge, carr, own36)), "both"),
                    "Q_donor": (lambda: H.SpanWriter(lm.layers, QL, Q, Qsrc), "Q"),
                    "Q_own": (lambda: H.SpanWriter(lm.layers, QL, Q, Qown), "Q"),
                }
            else:
                CE = {l: aO[l][0, carr, :].clone() for l in ALL}; CE2 = {l: aD[l][0, carr, :].clone() for l in ALL}
                QE = {l: aO[l][0, Q, :].clone() for l in QL}
                Crand = {}
                for l in ALL:
                    hC = ac[l][0, carr, :].float(); dn = (CE[l].float() - hC).norm(dim=1, keepdim=True)
                    v = torch.randn(len(carr), hC.shape[1], generator=g).to(hC.device)
                    Crand[l] = (hC + v / v.norm(dim=1, keepdim=True) * dn).to(ac[l].dtype)
                conds = {
                    "C_from_E": (lambda: H.SpanWriter(lm.layers, ALL, carr, CE), "carr"),
                    "C_from_E2": (lambda: H.SpanWriter(lm.layers, ALL, carr, CE2), "carr"),
                    "C_rand_nc": (lambda: H.SpanWriter(lm.layers, ALL, carr, Crand), "carr"),
                    "Q_from_E": (lambda: H.SpanWriter(lm.layers, QL, Q, QE), "Q"),
                }
            for cond, (mk, kind) in conds.items():
                ctx = mk(); a_, l_ = run(r.ids, ctx); n += 1; tag = f"{base}|{cond}"
                if kind in ("carr", "Q"):
                    assert all(torch.equal(a_[l][0, span, :], ac[l][0, span, :]) for l in ALL), f"clue span touched under {cond} {base}"
                if kind == "Q":
                    assert all(torch.equal(a_[l][0, pre, :], ac[l][0, pre, :]) for l in ALL), f"prefix touched under {cond} {base}"
                    if cond == "Q_own":
                        META["cells"][base]["Q_own_bitwise"] = bool(torch.equal(l_, lg) and all(torch.equal(a_[l], ac[l]) for l in ALL))
                rec(tag, r, l_, a_, it, Q)
                if cond in ("C_full", "C_all", "C_from_E", "C_from_E2"):
                    src = (C36 if cond == "C_full" else Call) if STAGE == "full" else (CE if cond == "C_from_E" else CE2)
                    wdiag(tag, src, ac, carr, a_, list(src))
                del a_
            del ac, aO, aD
        print(f"  [{STAGE}] {it['name']}: {n} forwards ({time.time()-t0:.0f}s)", flush=True)

    META.update({"run_id": RUN_ID, "n_forwards": n, "elapsed_s": round(time.time() - t0, 1)})
    np.savez_compressed(os.path.join(OUT, f"raw_{STAGE}.npz"), **RAW)
    json.dump(META, open(os.path.join(OUT, f"meta_{STAGE}.json"), "w"), indent=1, default=str)
    man = R.manifest_block(); man.update({"run_id": RUN_ID, "stage": STAGE, "script": os.path.relpath(__file__, R.PROJECT),
                                          "design": "H3/design_specs/two_hop_organism.md (Amendment 3)",
                                          "materials": META["materials"],
                                          "raw_sha256": hashlib.sha256(open(os.path.join(OUT, f"raw_{STAGE}.npz"), "rb").read()).hexdigest()})
    json.dump(man, open(os.path.join(OUT, f"manifest_{STAGE}.json"), "w"), indent=1)
    print(f"[done {STAGE}] {n} forwards, {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
