"""Stage `bridgeswap_seq`: the same 11 conditions as `bridgeswap`, rescored with sequence log-probabilities of the two
full answer words (the behavioural-endpoint convention (sequence log-probs for multi-token answers; damage metrics): multi-token answers use explicitly defined sequence log-probs). For each cell and condition,
each candidate (as written, and capitalised; with and without a leading space) is appended after the assistant start and
teacher-forced; the score is logsumexp over spellings of the summed token log-probs. Interventions act on the original
positions only (the appended tokens lie beyond them), so every condition is bitwise the same intervention as `bridgeswap`."""
import os, sys, json, time, hashlib, re
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "..", "common", "scripts"))
import numpy as np, torch
import registry as R, materials as M, rendering as Rn, readout as RO, hooks as H

OUT = os.path.join(R.OUT_ROOT, "H3", "outputs", "two_hop_organism"); os.makedirs(OUT, exist_ok=True)
RUN_ID = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()); SEED = 20260909
COPY = "copy the following text exactly, word for word"; CARRIERS = ["C0", "C1", "C2", "C3"]; LX = 36; DECOYS = M.FIT_WORDS[:8]
SWAP_L = list(range(36, 63)); STAGE = "bridgeswap_seq"
ITEMS = json.load(open(os.path.join(R.PROJECT, "H3", "design_specs", "two_hop_items.json")))["pilot_items"]
STRIP = re.compile(r"\s+(is called a|is called the|is the|is a|are|is)\s*$")


def clue_body(prompt): return STRIP.sub("", prompt.replace("Fact: ", "").strip())
def utext(body, car): return f"Here is a clue: {body}. Keep the answer to the clue in mind while you {COPY}:\n\n" + car
def question(prompt): return "Complete the fact from the clue you were given, using one word."


def spellings(tok, w):
    out = []
    for f in dict.fromkeys([w, w.capitalize(), " " + w, " " + w.capitalize()]):
        ids = tuple(tok(f, add_special_tokens=False).input_ids)
        if ids not in out: out.append(ids)
    return out


def main():
    tok = R.make_tokenizer()
    from jlens.hf import from_hf
    model = R.load_model(); lm = from_hf(model, tok, compile=False)
    ALL = list(range(R.N_BLOCKS)); run = H.make_run(model, lm, ALL)
    LEN = R.load_lenses(("J_NP",))["J_NP"]
    words = sorted({it["intermediate"] for it in ITEMS} | {it["swap_to"] for it in ITEMS}); COLS = words + DECOYS
    ans_words = sorted({it["answer"] for it in ITEMS} | {it["swap_answer"] for it in ITEMS})
    TID = {w: Rn.single_token_id(tok, w) for w in COLS + ans_words}; assert all(v is not None for v in TID.values()), TID
    ro = RO.LensReadout(model, lm, LEN, [TID[w] for w in COLS])
    NAMING = {w: {l: ro.folded_direction(l, TID[w]) for l in SWAP_L} for w in COLS + ans_words}
    RAW, META = {}, {"carriers": CARRIERS, "lx": LX, "swap_layers": [SWAP_L[0], SWAP_L[-1]], "seed": SEED, "cells": {}, "items": ITEMS}
    t0 = time.time(); n = 0

    def seqscore(ids, ctx, cands):
        """sum log p of each candidate spelling appended after `ids`; returns logsumexp over spellings. One forward per spelling."""
        vals = []
        for sp in cands:
            full = ids + list(sp)
            _, lg = run(full, ctx) if ctx is not None else run(full)
            lp = torch.log_softmax(lg[0, len(ids) - 1: len(full) - 1].float(), -1)
            vals.append(float(sum(lp[k, sp[k]] for k in range(len(sp)))))
        return float(torch.logsumexp(torch.tensor(vals), 0)), vals

    for it in ITEMS:
        for ck in CARRIERS:
            car = M.CARRIERS[ck]; base = f"{it['name']}|{ck}"
            body, dbody = clue_body(it["prompt"]), clue_body(it["donor_prompt"])
            r = Rn.render(tok, utext(body, car), car, sources=[("CLUE", body, False)], extra_turns=[(question(it["prompt"]), "")])
            rd = Rn.render(tok, utext(dbody, car), car, sources=[("CLUE", dbody, False)], extra_turns=[(question(it["donor_prompt"]), "")])
            assert len(rd) == len(r) and rd.spans["CLUE"]["full"] == r.spans["CLUE"]["full"] and rd.meta["carrier_start"] == r.meta["carrier_start"] and rd.meta["carrier_end"] == r.meta["carrier_end"], f"G3 donor geometry {base}"
            span = r.spans["CLUE"]["full"]; cs, ce = r.meta["carrier_start"], r.meta["carrier_end"]
            carr = list(range(cs, ce)); Q = list(range(ce, len(r))); tail = list(range(span[0], len(r)))
            ids = list(r.ids); cA, cB = spellings(tok, it["answer"]), spellings(tok, it["swap_answer"])
            META["cells"][base] = {"answer": it["answer"], "swap_answer": it["swap_answer"], "intermediate": it["intermediate"], "swap_to": it["swap_to"],
                                   "n_tokens": len(r), "spellings_answer": [list(x) for x in cA], "spellings_swap": [list(x) for x in cB]}
            add, _ = run(rd.ids); n += 1
            O_all = {l: add[l][0, span, :].clone() for l in ALL}
            pairs = {"int": (it["intermediate"], it["swap_to"]), "ans": (it["answer"], it["swap_answer"]), "rand": (DECOYS[0], DECOYS[1])}
            posets = {"tail": tail, "clue": span, "carr": carr, "q": Q}
            conds = {"clean": lambda: None, "S_donor0": lambda: H.SpanWriter(lm.layers, ALL, span, O_all)}
            for p in ("int", "ans"):
                for s in posets:
                    conds[f"{p}_{s}"] = (lambda p=p, s=s: H.CoordSwap(lm.layers, SWAP_L, posets[s], {l: (NAMING[pairs[p][0]][l], NAMING[pairs[p][1]][l]) for l in SWAP_L}))
            conds["rand_tail"] = lambda: H.CoordSwap(lm.layers, SWAP_L, tail, {l: (NAMING[DECOYS[0]][l], NAMING[DECOYS[1]][l]) for l in SWAP_L})
            for cond, mk in conds.items():
                sA, vA = seqscore(ids, mk(), cA); sB, vB = seqscore(ids, mk(), cB); n += len(cA) + len(cB)
                RAW[f"{base}|{cond}|seq_answer"] = np.float32(sA); RAW[f"{base}|{cond}|seq_swap"] = np.float32(sB)
                RAW[f"{base}|{cond}|seq_answer_all"] = np.array(vA, np.float32); RAW[f"{base}|{cond}|seq_swap_all"] = np.array(vB, np.float32)
            del add
            print(f"  {base}: {n} forwards ({time.time()-t0:.0f}s)", flush=True)

    names = list(dict.fromkeys(b.split("|")[0] for b in META["cells"])); cells = META["cells"]
    def ci(v):
        from scipy import stats as st; v = np.asarray(v); m = v.mean(); h = st.t.ppf(0.975, len(v) - 1) * v.std(ddof=1) / np.sqrt(len(v)); return [float(m), float(m - h), float(m + h), int((v > 0).sum()), len(v)]
    byitem = lambda vals: [np.mean([v for b, v in zip(cells, vals) if b.startswith(nm + "|")]) for nm in names]
    mg = lambda b, c: float((RAW[f"{b}|{c}|seq_swap"] - RAW[f"{b}|{c}|seq_answer"]) - (RAW[f"{b}|clean|seq_swap"] - RAW[f"{b}|clean|seq_answer"]))
    META["competence_seq"] = float(np.mean([RAW[f"{b}|clean|seq_answer"] > RAW[f"{b}|clean|seq_swap"] for b in cells]))
    rows = []; ceil = None
    for cond in ["S_donor0"] + [f"{p}_{s}" for p in ("int", "ans") for s in ("tail", "clue", "carr", "q")] + ["rand_tail"]:
        marg = byitem([mg(b, cond) for b in cells])
        if cond == "S_donor0": ceil = float(np.mean(marg))
        flips = sum(int(RAW[f"{b}|{cond}|seq_swap"] > RAW[f"{b}|{cond}|seq_answer"]) for b in cells)
        rows.append({"cond": cond, "margin_seq": ci(marg), "share_of_ceiling": float(np.mean(marg) / ceil), "flips_seq": flips, "n": len(cells)})
        print(f"  [{cond:9s}] seq margin {rows[-1]['margin_seq'][0]:+6.2f} [{rows[-1]['margin_seq'][1]:+6.2f},{rows[-1]['margin_seq'][2]:+6.2f}] ({rows[-1]['margin_seq'][3]}/{rows[-1]['margin_seq'][4]}>0) share {rows[-1]['share_of_ceiling']:+.2f} flips {flips}/{len(cells)}", flush=True)
    META["rows"] = rows; META["ceiling_margin_seq"] = ceil
    META.update({"run_id": RUN_ID, "n_forwards": n, "elapsed_s": round(time.time() - t0, 1)})
    np.savez_compressed(os.path.join(OUT, f"raw_{STAGE}.npz"), **RAW); json.dump(META, open(os.path.join(OUT, f"meta_{STAGE}.json"), "w"), indent=1, default=str)
    man = R.manifest_block(); man.update({"run_id": RUN_ID, "stage": STAGE, "script": os.path.relpath(__file__, R.PROJECT), "design": "H3/design_specs/two_hop_organism.md (Amendment 4, sequence endpoint)",
                                          "raw_sha256": hashlib.sha256(open(os.path.join(OUT, f"raw_{STAGE}.npz"), "rb").read()).hexdigest()})
    json.dump(man, open(os.path.join(OUT, f"manifest_{STAGE}.json"), "w"), indent=1)
    print(f"[done {STAGE}] {n} forwards, {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
