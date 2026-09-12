"""H3 two_hop_organism pilot (design: H3/design_specs/two_hop_organism.md). Materials: anthropics/jacobian-lens probe-swap.json,
filtered per the design; pilot = 12 items with a released, length-matched donor clue. Stage `pilot` runs the gates on the clean
forwards first and the three interventions only if G1 passes."""
import os, sys, json, time, hashlib, re
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "..", "common", "scripts"))
import numpy as np, torch
import registry as R, materials as M, rendering as Rn, readout as RO, hooks as H

OUT = os.path.join(R.PROJECT, "H3", "outputs", "two_hop_organism"); os.makedirs(OUT, exist_ok=True)
RUN_ID = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()); SEED = 20260909
COPY = "copy the following text exactly, word for word"; CARRIERS = ["C0", "C1"]; LX = 36; DECOYS = M.FIT_WORDS[:8]
ITEMS = json.load(open(os.path.join(R.PROJECT, "H3", "design_specs", "two_hop_items.json")))["pilot_items"]
STRIP = re.compile(r"\s+(is called a|is called the|is the|is a|are|is)\s*$")


def clue_body(prompt): return STRIP.sub("", prompt.replace("Fact: ", "").strip())
def utext(body, car): return f"Here is a clue: {body}. Keep the answer to the clue in mind while you {COPY}:\n\n" + car
def question(prompt): return "Complete the fact from the clue you were given, using one word."   # Amendment 2: never restates the clue


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
    ALL = list(range(R.N_BLOCKS)); SRC = list(range(R.N_SRC)); run = H.make_run(model, lm, ALL); lge = [l for l in ALL if l >= LX]
    LEN = R.load_lenses(("J_NP",))["J_NP"]
    words = sorted({it["intermediate"] for it in ITEMS} | {it["swap_to"] for it in ITEMS}); COLS = words + DECOYS
    TID = {w: Rn.single_token_id(tok, w) for w in COLS}; assert all(v is not None for v in TID.values()), TID
    ro = RO.LensReadout(model, lm, LEN, [TID[w] for w in COLS])
    RAW, META = {}, {"columns": COLS, "decoys": DECOYS, "carriers": CARRIERS, "lx": LX, "seed": SEED, "cells": {}, "items": ITEMS}
    t0 = time.time(); n = 0

    def score(logits, a, b):
        lp = torch.log_softmax(logits[0, -1].float(), -1)
        sa = float(torch.logsumexp(lp[forms(tok, a)], 0)); sb = float(torch.logsumexp(lp[forms(tok, b)], 0))
        return sa, sb, tok.decode(int(logits[0, -1].argmax())).strip()

    def rec(tag, r, logits, acts, it):
        sa, sb, g = score(logits, it["answer"], it["swap_answer"])
        RAW[f"{tag}|s_answer"] = np.float32(sa); RAW[f"{tag}|s_swap"] = np.float32(sb); RAW[f"{tag}|greedy"] = g
        RAW[f"{tag}|z"] = ro.z(acts, r.interior, SRC).astype(np.float16)
        cs, ce = r.meta["carrier_start"], r.meta["carrier_end"]; nll, _, _ = RO.carrier_damage(logits, r.ids, cs, ce); RAW[f"{tag}|nll"] = np.float32(nll)

    # ---- G1 first: clean competence on every cell
    rend = {}
    for it in ITEMS:
        for ck in CARRIERS:
            car = M.CARRIERS[ck]; base = f"{it['name']}|{ck}"
            body, dbody = clue_body(it["prompt"]), clue_body(it["donor_prompt"])
            r = Rn.render(tok, utext(body, car), car, sources=[("CLUE", body, False)], extra_turns=[(question(it["prompt"]), "")])
            rd = Rn.render(tok, utext(dbody, car), car, sources=[("CLUE", dbody, False)], extra_turns=[(question(it["donor_prompt"]), "")])
            rh = Rn.render(tok, f"Here is a clue (hidden). Keep the answer to the clue in mind while you {COPY}:\n\n" + car, car, sources=[], extra_turns=[(question(it["prompt"]), "")])
            assert len(rd) == len(r) and rd.spans["CLUE"]["full"] == r.spans["CLUE"]["full"] and rd.meta["carrier_start"] == r.meta["carrier_start"] and rd.meta["carrier_end"] == r.meta["carrier_end"], f"G3 donor geometry {base}"
            rend[base] = (r, rd, rh, it)
            META["cells"][base] = {"clue": body, "donor_clue": dbody, "intermediate": it["intermediate"], "swap_to": it["swap_to"], "answer": it["answer"], "swap_answer": it["swap_answer"],
                                   "span": [r.spans["CLUE"]["full"][0], r.spans["CLUE"]["full"][-1]], "carrier": [r.meta["carrier_start"], r.meta["carrier_end"]], "n_tokens": len(r)}
            ac, lg = run(r.ids); n += 1; rec(f"{base}|clean", r, lg, ac, it); META["cells"][base]["acts_clean"] = True
            rend[base] = (r, rd, rh, it, ac)
    comp_scored = np.mean([RAW[f"{b}|clean|s_answer"] > RAW[f"{b}|clean|s_swap"] for b in rend])
    comp_greedy = np.mean([str(RAW[f"{b}|clean|greedy"]).lower() == rend[b][3]["answer"].lower() for b in rend])
    META["G1"] = {"scored_pairwise": float(comp_scored), "greedy_exact": float(comp_greedy), "pass": bool(comp_scored >= 0.9)}
    print(f"  [G1] clean competence: scored (answer > swap_answer) {comp_scored:.3f}, greedy == answer {comp_greedy:.3f} -> {'PASS' if META['G1']['pass'] else 'FAIL'}", flush=True)
    # ---- G2 readability + donor/hidden forwards (needed for G2 regardless)
    for base, (r, rd, rh, it, ac) in rend.items():
        add, lgd = run(rd.ids); n += 1; rec(f"{base}|donor_clean", rd, lgd, add, it)
        ah, lgh = run(rh.ids); n += 1; rec(f"{base}|hidden", rh, lgh, ah, it); del ah
        rend[base] = (r, rd, rh, it, ac, add)
    dec = [COLS.index(d) for d in DECOYS]
    def pres(tag, w): z = RAW[f"{tag}|z"][51:60].astype(np.float32).mean(axis=(0, 1)); return float(z[COLS.index(w)] - z[dec].mean())
    g2 = [pres(f"{b}|clean", rend[b][3]["intermediate"]) - pres(f"{b}|donor_clean", rend[b][3]["intermediate"]) for b in rend]
    g2h = [pres(f"{b}|clean", rend[b][3]["intermediate"]) - pres(f"{b}|hidden", rend[b][3]["intermediate"]) for b in rend]
    def ci(v):
        from scipy import stats as st; v = np.asarray(v); m = v.mean(); h = st.t.ppf(0.975, len(v) - 1) * v.std(ddof=1) / np.sqrt(len(v)); return [float(m), float(m - h), float(m + h), int((v > 0).sum()), len(v)]
    # cluster by item (carriers averaged)
    byitem = lambda vals: [np.mean([v for b, v in zip(rend, vals) if b.startswith(nm + "|")]) for nm in dict.fromkeys(b.split("|")[0] for b in rend)]
    META["G2"] = {"own_minus_donor_clue": ci(byitem(g2)), "own_minus_hidden": ci(byitem(g2h))}
    META["G2"]["pass"] = bool(META["G2"]["own_minus_donor_clue"][1] > 0)
    print(f"  [G2] intermediate presence L51-59, own clue − donor clue: {META['G2']['own_minus_donor_clue']} ; own − hidden: {META['G2']['own_minus_hidden']} -> {'PASS' if META['G2']['pass'] else 'FAIL'}", flush=True)
    if not META["G1"]["pass"]:
        print("  G1 failed: interventions not run (design §2)."); META["interventions_run"] = False
    else:
        META["interventions_run"] = True
        for base, (r, rd, rh, it, ac, add) in rend.items():
            span = r.spans["CLUE"]["full"]; carr = list(range(r.meta["carrier_start"], r.meta["carrier_end"]))
            O_src = {l: add[l][0, span, :].clone() for l in lge}; C_src = {l: add[l][0, carr, :].clone() for l in lge}
            O_all = {l: add[l][0, span, :].clone() for l in ALL}; C_allsrc = {l: add[l][0, carr, :].clone() for l in ALL}
            g = torch.Generator(device="cpu").manual_seed(SEED + hash(base) % 10007); Crand = {}
            for l in lge:
                hC = ac[l][0, carr, :].float(); dn = (C_src[l].float() - hC).norm(dim=1, keepdim=True)
                v = torch.randn(len(carr), hC.shape[1], generator=g).to(hC.device); Crand[l] = (hC + v / v.norm(dim=1, keepdim=True) * dn).to(ac[l].dtype)
            for cond, ctx in (("S_donor", H.SpanWriter(lm.layers, lge, span, O_src)), ("C_full", H.SpanWriter(lm.layers, lge, carr, C_src)), ("C_rand", H.SpanWriter(lm.layers, lge, carr, Crand)),
                              ("S_donor0", H.SpanWriter(lm.layers, ALL, span, O_all)), ("C_all", H.SpanWriter(lm.layers, ALL, carr, C_allsrc))):
                a_, l_ = run(r.ids, ctx); n += 1
                if not cond.startswith("S_donor"): assert all(torch.equal(a_[l][0, span, :], ac[l][0, span, :]) for l in ALL), f"clue span touched {base} {cond}"
                rec(f"{base}|{cond}", r, l_, a_, it); del a_
        # summary
        rows = []
        for cond in ("S_donor", "S_donor0", "C_full", "C_all", "C_rand"):
            marg = byitem([(RAW[f"{b}|{cond}|s_swap"] - RAW[f"{b}|{cond}|s_answer"]) - (RAW[f"{b}|clean|s_swap"] - RAW[f"{b}|clean|s_answer"]) for b in rend])
            flips = sum(int(RAW[f"{b}|{cond}|s_swap"] > RAW[f"{b}|{cond}|s_answer"]) for b in rend)
            zsh = byitem([(pres(f"{b}|{cond}", rend[b][3]["swap_to"]) - pres(f"{b}|{cond}", rend[b][3]["intermediate"])) - (pres(f"{b}|clean", rend[b][3]["swap_to"]) - pres(f"{b}|clean", rend[b][3]["intermediate"])) for b in rend])
            dn = max(float(RAW[f"{b}|{cond}|nll"] - RAW[f"{b}|clean|nll"]) for b in rend)
            rows.append({"cond": cond, "margin": ci(marg), "flips": flips, "n": len(rend), "carrier_latent_shift_J": ci(zsh), "dNLL_max": dn})
            print(f"  [{cond:8s}] answer margin toward swap_answer {rows[-1]['margin'][:3]} ({rows[-1]['margin'][3]}/{rows[-1]['margin'][4]} items >0), flips {flips}/{len(rend)}, carrier latent shift (J_NP L51-59) {rows[-1]['carrier_latent_shift_J'][:3]}, dNLL max {dn:+.4f}", flush=True)
        META["pilot"] = rows
    META.update({"run_id": RUN_ID, "n_forwards": n, "elapsed_s": round(time.time() - t0, 1)})
    np.savez_compressed(os.path.join(OUT, "raw_pilot_a2.npz"), **RAW); json.dump(META, open(os.path.join(OUT, "meta_pilot_a2.json"), "w"), indent=1, default=str)
    man = R.manifest_block(); man.update({"run_id": RUN_ID, "stage": "pilot", "script": os.path.relpath(__file__, R.PROJECT), "design": "H3/design_specs/two_hop_organism.md",
                                          "materials": "anthropics/jacobian-lens@581d398 data/experiments/probe-swap.json", "raw_sha256": hashlib.sha256(open(os.path.join(OUT, "raw_pilot_a2.npz"), "rb").read()).hexdigest()})
    json.dump(man, open(os.path.join(OUT, "manifest_pilot_a2.json"), "w"), indent=1)
    print(f"[done pilot] {n} forwards, {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
