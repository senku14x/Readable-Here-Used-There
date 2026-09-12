"""H3 two_hop_organism stage `bridgeswap` (design: H3/design_specs/two_hop_organism.md, Amendment 4).
The paper's lens-coordinate swap on the two-hop intermediate (and, as the paper's own confound check, on the answer),
decomposed by position: tail (all positions from the clue on) / clue / carrier / question. Reference ceiling: S_donor0."""
import os, sys, json, time, hashlib, re
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "..", "common", "scripts"))
import numpy as np, torch
import registry as R, materials as M, rendering as Rn, readout as RO, hooks as H

OUT = os.path.join(R.OUT_ROOT, "H3", "outputs", "two_hop_organism"); os.makedirs(OUT, exist_ok=True)
RUN_ID = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()); SEED = 20260909
COPY = "copy the following text exactly, word for word"; CARRIERS = ["C0", "C1", "C2", "C3"]; LX = 36; DECOYS = M.FIT_WORDS[:8]
SWAP_L = list(range(36, 63))
ITEMS = json.load(open(os.path.join(R.PROJECT, "H3", "design_specs", "two_hop_items.json")))["pilot_items"]
STRIP = re.compile(r"\s+(is called a|is called the|is the|is a|are|is)\s*$")
STAGE = "bridgeswap"


def clue_body(prompt): return STRIP.sub("", prompt.replace("Fact: ", "").strip())
def utext(body, car): return f"Here is a clue: {body}. Keep the answer to the clue in mind while you {COPY}:\n\n" + car
def question(prompt): return "Complete the fact from the clue you were given, using one word."


def forms(tok, w):
    out = []
    for f in (w, " " + w, w.capitalize(), " " + w.capitalize(), w.lower(), " " + w.lower()):
        ids = tok(f, add_special_tokens=False).input_ids
        if len(ids) == 1 and ids[0] not in out: out.append(ids[0])
    return out


def main():
    tok = R.make_tokenizer()
    from jlens.hf import from_hf
    model = R.load_model(); lm = from_hf(model, tok, compile=False)
    ALL = list(range(R.N_BLOCKS)); SRC = list(range(R.N_SRC)); run = H.make_run(model, lm, ALL)
    LEN = R.load_lenses(("J_NP",))["J_NP"]
    words = sorted({it["intermediate"] for it in ITEMS} | {it["swap_to"] for it in ITEMS}); COLS = words + DECOYS
    ans_words = sorted({it["answer"] for it in ITEMS} | {it["swap_answer"] for it in ITEMS})
    TID = {w: Rn.single_token_id(tok, w) for w in COLS + ans_words}; assert all(v is not None for v in TID.values()), TID
    ro = RO.LensReadout(model, lm, LEN, [TID[w] for w in COLS])
    NAMING = {w: {l: ro.folded_direction(l, TID[w]) for l in SWAP_L} for w in COLS + ans_words}
    RAW, META = {}, {"columns": COLS, "decoys": DECOYS, "carriers": CARRIERS, "lx": LX, "swap_layers": [SWAP_L[0], SWAP_L[-1]], "seed": SEED, "cells": {}, "items": ITEMS}
    t0 = time.time(); n = 0

    def score(logits, a, b):
        lp = torch.log_softmax(logits[0, -1].float(), -1)
        sa = float(torch.logsumexp(lp[forms(tok, a)], 0)); sb = float(torch.logsumexp(lp[forms(tok, b)], 0))
        return sa, sb, tok.decode(int(logits[0, -1].argmax())).strip()

    def rec(tag, r, logits, acts, it, Q):
        sa, sb, g = score(logits, it["answer"], it["swap_answer"])
        RAW[f"{tag}|s_answer"] = np.float32(sa); RAW[f"{tag}|s_swap"] = np.float32(sb); RAW[f"{tag}|greedy"] = g
        RAW[f"{tag}|z"] = ro.z(acts, r.interior, SRC).astype(np.float16)
        RAW[f"{tag}|zq"] = ro.z(acts, Q, SRC).astype(np.float16)
        cs, ce = r.meta["carrier_start"], r.meta["carrier_end"]; nll, _, _ = RO.carrier_damage(logits, r.ids, cs, ce); RAW[f"{tag}|nll"] = np.float32(nll)

    rend = {}
    for it in ITEMS:
        for ck in CARRIERS:
            car = M.CARRIERS[ck]; base = f"{it['name']}|{ck}"
            body, dbody = clue_body(it["prompt"]), clue_body(it["donor_prompt"])
            r = Rn.render(tok, utext(body, car), car, sources=[("CLUE", body, False)], extra_turns=[(question(it["prompt"]), "")])
            rd = Rn.render(tok, utext(dbody, car), car, sources=[("CLUE", dbody, False)], extra_turns=[(question(it["donor_prompt"]), "")])
            assert len(rd) == len(r) and rd.spans["CLUE"]["full"] == r.spans["CLUE"]["full"] and rd.meta["carrier_start"] == r.meta["carrier_start"] and rd.meta["carrier_end"] == r.meta["carrier_end"], f"G3 donor geometry {base}"
            span = r.spans["CLUE"]["full"]; cs, ce = r.meta["carrier_start"], r.meta["carrier_end"]
            carr = list(range(cs, ce)); Q = list(range(ce, len(r))); tail = list(range(span[0], len(r)))
            META["cells"][base] = {"clue": body, "donor_clue": dbody, "intermediate": it["intermediate"], "swap_to": it["swap_to"], "answer": it["answer"], "swap_answer": it["swap_answer"],
                                   "span": [span[0], span[-1]], "carrier": [cs, ce], "q": [Q[0], Q[-1]], "n_tokens": len(r)}
            ac, lg = run(r.ids); n += 1; rec(f"{base}|clean", r, lg, ac, it, Q)
            add, lgd = run(rd.ids); n += 1; rec(f"{base}|donor_clean", rd, lgd, add, it, Q)
            O_all = {l: add[l][0, span, :].clone() for l in ALL}
            a_, l_ = run(r.ids, H.SpanWriter(lm.layers, ALL, span, O_all)); n += 1; rec(f"{base}|S_donor0", r, l_, a_, it, Q); del a_
            pairs = {"int": (it["intermediate"], it["swap_to"]), "ans": (it["answer"], it["swap_answer"]), "rand": (DECOYS[0], DECOYS[1])}
            posets = {"tail": tail, "clue": span, "carr": carr, "q": Q}
            conds = [(f"{p}_{s}", p, s) for p in ("int", "ans") for s in posets] + [("rand_tail", "rand", "tail")]
            for cond, p, s in conds:
                w1, w2 = pairs[p]; dirs = {l: (NAMING[w1][l], NAMING[w2][l]) for l in SWAP_L}
                ctx = H.CoordSwap(lm.layers, SWAP_L, posets[s], dirs)
                a_, l_ = run(r.ids, ctx); n += 1
                if s in ("carr", "q"): assert all(torch.equal(a_[l][0, span, :], ac[l][0, span, :]) for l in ALL), f"clue span touched {base} {cond}"
                rec(f"{base}|{cond}", r, l_, a_, it, Q); RAW[f"{base}|{cond}|realized"] = np.float32(np.mean(list(ctx.realized.values()))); del a_
            rend[base] = it
            if n % 60 < 12: print(f"  {base}: {n} forwards ({time.time()-t0:.0f}s)", flush=True)
            del ac, add

    dec = [COLS.index(d) for d in DECOYS]
    def pres(tag, w, key="z"): z = RAW[f"{tag}|{key}"][51:60].astype(np.float32).mean(axis=(0, 1)); return float(z[COLS.index(w)] - z[dec].mean())
    def ci(v):
        from scipy import stats as st; v = np.asarray(v); m = v.mean(); h = st.t.ppf(0.975, len(v) - 1) * v.std(ddof=1) / np.sqrt(len(v)); return [float(m), float(m - h), float(m + h), int((v > 0).sum()), len(v)]
    names = list(dict.fromkeys(b.split("|")[0] for b in rend))
    byitem = lambda vals: [np.mean([v for b, v in zip(rend, vals) if b.startswith(nm + "|")]) for nm in names]
    comp = np.mean([RAW[f"{b}|clean|s_answer"] > RAW[f"{b}|clean|s_swap"] for b in rend]); META["G1"] = {"scored_pairwise": float(comp)}
    rows = []; ceil = None
    for cond in ["S_donor0"] + [f"{p}_{s}" for p in ("int", "ans") for s in ("tail", "clue", "carr", "q")] + ["rand_tail"]:
        marg = byitem([(RAW[f"{b}|{cond}|s_swap"] - RAW[f"{b}|{cond}|s_answer"]) - (RAW[f"{b}|clean|s_swap"] - RAW[f"{b}|clean|s_answer"]) for b in rend])
        if cond == "S_donor0": ceil = float(np.mean(marg))
        flips = sum(int(RAW[f"{b}|{cond}|s_swap"] > RAW[f"{b}|{cond}|s_answer"]) for b in rend)
        zsh = byitem([(pres(f"{b}|{cond}", rend[b]["swap_to"]) - pres(f"{b}|{cond}", rend[b]["intermediate"])) - (pres(f"{b}|clean", rend[b]["swap_to"]) - pres(f"{b}|clean", rend[b]["intermediate"])) for b in rend])
        zq = byitem([(pres(f"{b}|{cond}", rend[b]["swap_to"], "zq") - pres(f"{b}|{cond}", rend[b]["intermediate"], "zq")) - (pres(f"{b}|clean", rend[b]["swap_to"], "zq") - pres(f"{b}|clean", rend[b]["intermediate"], "zq")) for b in rend])
        dn = max(float(RAW[f"{b}|{cond}|nll"] - RAW[f"{b}|clean|nll"]) for b in rend)
        rl = float(np.mean([RAW[f"{b}|{cond}|realized"] for b in rend])) if cond not in ("S_donor0",) else None
        rows.append({"cond": cond, "margin": ci(marg), "share_of_ceiling": float(np.mean(marg) / ceil), "flips": flips, "n": len(rend),
                     "carrier_latent_shift_J": ci(zsh), "question_latent_shift_J": ci(zq), "dNLL_max": dn, "realized_norm": rl})
        print(f"  [{cond:9s}] margin {rows[-1]['margin'][0]:+6.2f} [{rows[-1]['margin'][1]:+6.2f},{rows[-1]['margin'][2]:+6.2f}] ({rows[-1]['margin'][3]}/{rows[-1]['margin'][4]}>0) share {rows[-1]['share_of_ceiling']:+.2f} flips {flips}/{len(rend)} | latent shift carrier {rows[-1]['carrier_latent_shift_J'][0]:+.2f} question {rows[-1]['question_latent_shift_J'][0]:+.2f} | dNLL max {dn:+.4f} | realized {rl}", flush=True)
    META["rows"] = rows; META["ceiling_margin"] = ceil
    META.update({"run_id": RUN_ID, "n_forwards": n, "elapsed_s": round(time.time() - t0, 1)})
    np.savez_compressed(os.path.join(OUT, f"raw_{STAGE}.npz"), **RAW); json.dump(META, open(os.path.join(OUT, f"meta_{STAGE}.json"), "w"), indent=1, default=str)
    man = R.manifest_block(); man.update({"run_id": RUN_ID, "stage": STAGE, "script": os.path.relpath(__file__, R.PROJECT), "design": "H3/design_specs/two_hop_organism.md (Amendment 4)",
                                          "materials": "anthropics/jacobian-lens@581d398 data/experiments/probe-swap.json", "raw_sha256": hashlib.sha256(open(os.path.join(OUT, f"raw_{STAGE}.npz"), "rb").read()).hexdigest()})
    json.dump(man, open(os.path.join(OUT, f"manifest_{STAGE}.json"), "w"), indent=1)
    print(f"[done {STAGE}] {n} forwards, {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
