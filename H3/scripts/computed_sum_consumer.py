"""H3 computed_sum_consumer (design: H3/design_specs/computed_sum_consumer.md).

Does the carrier's representation of a COMPUTED LATENT (the sum) control a codebook consumer, at a boundary
where the equivalent full donor on a re-readable WORD did not (selection_to_behavior: full source-donor @block36
flips 0/36)? The sum has no surface token to re-read, so re-reading is not a route to the answer.

Organism (H1 computed_sums): `Here is the pair "{a} and {b}". Keep their sum in mind while you copy: {carrier}`.
Consumer (turn 2): `Code: seven=.., .., fourteen=... Using the code, give the letter for the sum of the pair.`

Stages:
  competence : all 8 sums x C0/C1 x 3 query wordings, clean only -> does greedy == F(sum)? (gate)
  boundary   : calibration sums {seven, ten, thirteen} x C0/C1, L_x in {23,36}; full different-sum donor and
               same-sum sibling on the addend span -> does the greedy answer flip to F(sum_donor)?  (the H3.2
               positive control that failed for the word consumer; internal C_diff^sum recorded as anchor)
Usage: computed_sum_consumer.py smoke|competence|boundary|transport|robust
  robust     : Amendment 2 robustness battery (C0-C3, two donor maps, C_all / NEC / C_rand, RESID_P + LOGITS + answer-position distance)
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
assert STAGE in ("smoke", "competence", "sumreport", "calibrate", "boundary", "transport", "robust", "global")
OUT = R.out_dir("H3", "outputs", "computed_sum_consumer")
RUN_ID = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
LETTERS = ["B", "D", "F", "H", "K", "M", "Q", "V"]
SEED = 20260908
COPY = "copy the following text exactly, word for word"
SUMS = M.SUMS                                                # (sum_word, A_pair, same_sum_B_pair)
SUM_WORDS = [s[0] for s in SUMS]                             # seven..fourteen (the 8 codebook entries)
NUMS = ["two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen"]
DECOYS = M.FIT_WORDS[:8]
COLS = NUMS + DECOYS
CAL_SUMS = [0, 3, 6]                                         # seven, ten, thirteen
CAL_CARRIERS = ["C0", "C1"]
LX_SWEEP = [23, 36]
QUERIES = {
    "sum_pair": "Using the code, give the letter for the sum of the pair. Answer with the letter only.",
    "sum_two": "Using the code, give the letter for the sum of the two numbers. Answer with the letter only.",
    "total_pair": "Using the code, give the letter for the total of the pair. Answer with the letter only.",
}
FROZEN_QUERY = "sum_pair"                                    # boundary stage; competence may revise (recorded)


def pair_of(i, x): return SUMS[i][1] if x == "A" else SUMS[i][2]
def sum_of(i): return SUMS[i][0]
def diff_donor(i): return SUMS[(i + 3) % 8][1]
def diff_sum(i): return SUMS[(i + 3) % 8][0]
def same_donor(i): return SUMS[i][2]                        # recipient uses A-addends -> sibling = B-addends
def pstr(p): return f"{p[0]} and {p[1]}"


def codebook_text(rng):
    letters = list(LETTERS); rng.shuffle(letters)
    assign = {w: letters[k] for k, w in enumerate(SUM_WORDS)}
    order = list(SUM_WORDS); rng.shuffle(order)
    return "Code: " + ", ".join(f"{w} = {assign[w]}" for w in order) + ".", assign


def utext(pair, car):
    return f'Here is the pair "{pstr(pair)}". Keep their sum in mind while you {COPY}:\n\n' + car


SUMWORD_QUERY = "What is the sum of the pair? Answer with one word."


def render_cell(tok, pair, ck, codebook, query, consumer=True):
    car = M.CARRIERS[ck]
    turn = query if codebook is None else codebook + "\n" + query
    extra = [(turn, "")] if consumer else None
    return Rn.render(tok, utext(pair, car), car, sources=[("P", pstr(pair), True)],
                     extra_turns=extra, name=f"{pstr(pair)}|{ck}")


def sumword_ids(tok):
    """sum-word answer ids in the forms the model may emit: {'seven',' seven','Seven',' Seven'}."""
    return answer_ids(tok, SUM_WORDS)


def answer_ids(tok, words):
    """word -> [single-token ids for forms {w,' '+w,Cap,' '+Cap}], -1 where not single-token."""
    out = {}
    for w in words:
        forms = []
        for form in (w, " " + w, w.capitalize(), " " + w.capitalize()):
            ids = tok(form, add_special_tokens=False).input_ids
            forms.append(ids[0] if len(ids) == 1 else -1)
        out[w] = forms
    return out


def score_words(tok, logits, WID, words):
    """logsumexp-over-forms score per word at the answer token; returns (scores dict, greedy decode)."""
    lp = torch.log_softmax(logits[0, -1].float(), -1)
    sc = {w: float(torch.logsumexp(torch.tensor([lp[t] for t in WID[w] if t >= 0]), 0)) for w in words}
    return sc, tok.decode(int(logits[0, -1].argmax())).strip()


def sumval(i): return i + 7                                        # SUMS[0]=seven=7 ... SUMS[7]=fourteen=14


def letter_ids(tok):
    out = {}
    for L in LETTERS:
        forms = []
        for form in (L, " " + L):
            ids = tok(form, add_special_tokens=False).input_ids
            forms.append(ids[0] if len(ids) == 1 else -1)
        out[L] = forms
    assert all(out[L][0] >= 0 for L in LETTERS)
    return out


def smoke():
    tok = R.make_tokenizer(); letter_ids(tok)
    TID = {w: Rn.single_token_id(tok, w) for w in NUMS + DECOYS}
    miss = {k: v for k, v in TID.items() if v is None}
    print(f"number/decoy single-token: {len(TID)-len(miss)}/{len(TID)}" + (f"  MULTITOK={list(miss)}" if miss else ""))
    rng = np.random.default_rng(SEED)
    for i in CAL_SUMS:
        pair = pair_of(i, "A"); dpair = diff_donor(i); spair = same_donor(i)
        cb, assign = codebook_text(rng)
        r = render_cell(tok, pair, "C0", cb, QUERIES[FROZEN_QUERY])
        span = r.spans["P"]["full"]
        rd = render_cell(tok, dpair, "C0", cb, QUERIES[FROZEN_QUERY])
        rs = render_cell(tok, spair, "C0", cb, QUERIES[FROZEN_QUERY])
        geom = (len(rd) == len(r) and rd.spans["P"]["full"] == span, len(rs) == len(r) and rs.spans["P"]["full"] == span)
        print(f"sum={sum_of(i)}({assign[sum_of(i)]}) pair='{pstr(pair)}' span={span} len={len(r)} ans_pos={r.spans['answer']} "
              f"| diff='{pstr(dpair)}'({diff_sum(i)}={assign[diff_sum(i)]}) same='{pstr(spair)}' geom(diff,same)={geom}")
    # show one full rendered conversation so the strings can be eyeballed
    r = render_cell(tok, pair_of(0, "A"), "C0", *(lambda a: (a[0], QUERIES[FROZEN_QUERY]))(codebook_text(np.random.default_rng(1))))
    print("\n--- full rendered cell (sum=seven) ---\n" + r.meta["full"][:1200])
    print("SMOKE OK")


def llp_at_answer(tok, LID, logits):
    lp = torch.log_softmax(logits[0, -1].float(), -1)
    arr = np.full((len(LETTERS), 2), -1e30, np.float32)
    for k, L in enumerate(LETTERS):
        for f, tid in enumerate(LID[L]):
            if tid >= 0:
                arr[k, f] = float(lp[tid])
    return arr, tok.decode(int(logits[0, -1].argmax())).strip()


def main():
    if STAGE == "smoke":
        smoke(); return
    tok = R.make_tokenizer(); LID = letter_ids(tok)
    TID = {w: Rn.single_token_id(tok, w) for w in COLS}
    assert all(v is not None for v in TID.values()), {k: v for k, v in TID.items() if v is None}
    from jlens.hf import from_hf
    model = R.load_model(); lm = from_hf(model, tok, compile=False)
    ALL = list(range(R.N_BLOCKS)); SRC = list(range(R.N_SRC))
    run = H.make_run(model, lm, ALL)
    LEN = R.load_lenses(("J_NP",))["J_NP"]; ro = RO.LensReadout(model, lm, LEN, [TID[w] for w in COLS])
    RAW, META = {}, {"columns": COLS, "sum_words": SUM_WORDS, "letters": LETTERS, "letter_ids": LID,
                     "decoys": DECOYS, "seed": SEED, "stage": STAGE, "queries": QUERIES, "token_ids": TID}
    t0 = time.time(); n = 0

    def rec_answer(tag, logits):
        arr, top = llp_at_answer(tok, LID, logits); RAW[f"{tag}|llp"] = arr; RAW[f"{tag}|greedy"] = top

    def rec_internal(tag, r, acts):
        RAW[f"{tag}|z"] = ro.z(acts, r.interior, SRC).astype(np.float16)
        cs, ce = r.meta["carrier_start"], r.meta["carrier_end"]; nll, top1, _ = RO.carrier_damage(logits_holder[0], r.ids, cs, ce)
        RAW[f"{tag}|nll"] = np.float32(nll); RAW[f"{tag}|top1"] = top1
    logits_holder = [None]

    # -------------------- competence --------------------
    if STAGE == "competence":
        res = {}
        for ck in CAL_CARRIERS:
            for i in range(8):
                pair = pair_of(i, "A"); s = sum_of(i)
                rng = np.random.default_rng(SEED + 1000 * i + 10 * CAL_CARRIERS.index(ck))  # codebook fixed per (sum,carrier); wordings share it (controlled comparison)
                cb, assign = codebook_text(rng)
                for qname, query in QUERIES.items():
                    r = render_cell(tok, pair, ck, cb, query)
                    _, lg = run(r.ids); n += 1
                    arr, top = llp_at_answer(tok, LID, lg)
                    tag = f"{i}|{ck}|{qname}"
                    RAW[f"{tag}|llp"] = arr; RAW[f"{tag}|greedy"] = top
                    res[tag] = {"sum": s, "target_letter": assign[s], "greedy": top, "correct": top == assign[s],
                                "assign": assign, "pair": list(pair)}
            print(f"  [competence] {ck}: {n} forwards ({time.time()-t0:.0f}s)", flush=True)
        META["competence"] = res
        for q in QUERIES:
            cells = [v for k, v in res.items() if k.endswith(q)]
            acc = np.mean([c["correct"] for c in cells])
            print(f"   {q:12s} accuracy {acc:.3f} ({sum(c['correct'] for c in cells)}/{len(cells)})")

    # -------------------- sumreport (direct sum-word report; no codebook) --------------------
    elif STAGE == "sumreport":
        SWID = sumword_ids(tok); META["sumword_ids"] = SWID; res = {}
        allids = [tid for w in SUM_WORDS for tid in SWID[w] if tid >= 0]
        for ck in CAL_CARRIERS:
            for i in range(8):
                pair = pair_of(i, "A"); s = sum_of(i)
                r = render_cell(tok, pair, ck, None, SUMWORD_QUERY)
                _, lg = run(r.ids); n += 1
                lp = torch.log_softmax(lg[0, -1].float(), -1)
                sc = {w: float(torch.logsumexp(torch.tensor([lp[t] for t in SWID[w] if t >= 0]), 0)) for w in SUM_WORDS}
                top = tok.decode(int(lg[0, -1].argmax())).strip()
                pred = max(sc, key=sc.get)
                tag = f"{i}|{ck}"
                RAW[f"{tag}|scores"] = np.array([sc[w] for w in SUM_WORDS], np.float32); RAW[f"{tag}|greedy"] = top
                res[tag] = {"sum": s, "pair": list(pair), "greedy": top, "pred_sumword": pred,
                            "correct_greedy": top.lower() == s, "correct_scored": pred == s}
            print(f"  [sumreport] {ck}: {n} forwards ({time.time()-t0:.0f}s)", flush=True)
        META["sumreport"] = res
        accg = np.mean([v["correct_greedy"] for v in res.values()]); accs = np.mean([v["correct_scored"] for v in res.values()])
        print(f"   greedy==sumword accuracy {accg:.3f} ({sum(v['correct_greedy'] for v in res.values())}/{len(res)}); "
              f"argmax-over-8-sumwords accuracy {accs:.3f}")
        for k, v in res.items():
            if not v["correct_greedy"]:
                print(f"   MISS {k}: {v['pair']} sum={v['sum']} greedy={v['greedy']!r} scored={v['pred_sumword']}")

    # -------------------- calibrate: A explicit-vs-latent lookup, B >10, C parity (researcher review) --------------------
    elif STAGE == "calibrate":
        LID = letter_ids(tok); resA = {}
        LOOKUP_Q = "Using the code, give the letter for the sum of the pair. Answer with the letter only."
        for ck in CAL_CARRIERS:
            car = M.CARRIERS[ck]
            for i in range(8):
                pair = pair_of(i, "A"); s = sum_of(i)
                rng = np.random.default_rng(SEED + 1000 * i + 10 * CAL_CARRIERS.index(ck))
                cb, assign = codebook_text(rng)                       # SAME codebook for latent & explicit (matched control)
                for cond in ("latent", "explicit"):
                    turn = (f"The sum is {s}. " if cond == "explicit" else "") + cb + "\n" + LOOKUP_Q
                    r = Rn.render(tok, utext(pair, car), car, sources=[("P", pstr(pair), True)], extra_turns=[(turn, "")])
                    _, lg = run(r.ids); n += 1
                    arr, top = llp_at_answer(tok, LID, lg)
                    tag = f"A|{i}|{ck}|{cond}"; RAW[f"{tag}|llp"] = arr; RAW[f"{tag}|greedy"] = top
                    resA[tag] = {"sum": s, "cond": cond, "target": assign[s], "greedy": top, "correct": top == assign[s]}
        PRED = {"gt10": (["yes", "no"], "Is their sum greater than ten? Answer yes or no.", lambda i: "yes" if sumval(i) > 10 else "no"),
                "parity": (["even", "odd"], "Is their sum even or odd? Answer even or odd.", lambda i: "odd" if sumval(i) % 2 else "even")}
        resBC = {}
        for pname, (words, q, truth) in PRED.items():
            WID = answer_ids(tok, words)
            for ck in CAL_CARRIERS:
                car = M.CARRIERS[ck]
                for i in range(8):
                    pair = pair_of(i, "A")
                    r = Rn.render(tok, utext(pair, car), car, sources=[("P", pstr(pair), True)], extra_turns=[(q, "")])
                    _, lg = run(r.ids); n += 1
                    sc, top = score_words(tok, lg, WID, words); pred = max(sc, key=sc.get); t = truth(i)
                    tag = f"{pname}|{i}|{ck}"; RAW[f"{tag}|scores"] = np.array([sc[w] for w in words], np.float32); RAW[f"{tag}|greedy"] = top
                    resBC[tag] = {"sum": sum_of(i), "truth": t, "pred": pred, "greedy": top, "correct": pred == t}
        META["calibrate"] = {"A_lookup": resA, "BC_predicate": resBC}
        accAl = np.mean([v["correct"] for v in resA.values() if v["cond"] == "latent"])
        accAe = np.mean([v["correct"] for v in resA.values() if v["cond"] == "explicit"])
        print(f"   A lookup: explicit-sum {accAe:.3f}  vs  latent-sum {accAl:.3f}  (n=16 each)", flush=True)
        for pname in PRED:
            cells = [v for k, v in resBC.items() if k.startswith(pname + "|")]
            acc = np.mean([c["correct"] for c in cells])
            print(f"   {pname:7s} competence {acc:.3f} ({sum(c['correct'] for c in cells)}/{len(cells)})")
            for c in cells:
                if not c["correct"]:
                    print(f"      MISS sum={c['sum']} truth={c['truth']} pred={c['pred']} greedy={c['greedy']!r}")

    # -------------------- boundary: full-donor gate at L_x on COMPETENT consumers (parity primary, report secondary) --------------------
    # Amendment 1 (2026-09-08): codebook consumer failed competence; this gate uses parity (1.00) + direct sum-report,
    # multi-consumer on the SAME different-sum donor (which always flips parity), same-sum sibling as the matched control.
    elif STAGE == "boundary":
        META["lx_sweep"] = LX_SWEEP; META["carriers"] = CAL_CARRIERS; META["cells"] = {}
        PAR_WORDS = ["even", "odd"]
        CONSUMERS = {"parity": ("Is their sum even or odd? Answer even or odd.", PAR_WORDS, answer_ids(tok, PAR_WORDS)),
                     "report": ("What is the sum of the pair? Answer with one word.", SUM_WORDS, sumword_ids(tok))}
        parity_of = lambda sword: ("odd" if (SUM_WORDS.index(sword) + 7) % 2 else "even")

        def rec_bnd(tag, r, logits, acts, words, WID):
            sc, top = score_words(tok, logits, WID, words)
            RAW[f"{tag}|scores"] = np.array([sc[w] for w in words], np.float32); RAW[f"{tag}|greedy"] = top
            RAW[f"{tag}|z"] = ro.z(acts, r.interior, SRC).astype(np.float16)
            cs, ce = r.meta["carrier_start"], r.meta["carrier_end"]; nll, _, _ = RO.carrier_damage(logits, r.ids, cs, ce)
            RAW[f"{tag}|nll"] = np.float32(nll)

        for ck in CAL_CARRIERS:
            car = M.CARRIERS[ck]
            for i in range(8):
                pair = pair_of(i, "A"); dpair = diff_donor(i); spair = same_donor(i); base = f"S{i}|{ck}"
                META["cells"][base] = {"sum": sum_of(i), "diff_donor": list(dpair), "diff_sum": diff_sum(i),
                                       "same_donor": list(spair), "pair": list(pair),
                                       "own_parity": parity_of(sum_of(i)), "diff_parity": parity_of(diff_sum(i))}
                for cname, (q, words, WID) in CONSUMERS.items():
                    r = Rn.render(tok, utext(pair, car), car, sources=[("P", pstr(pair), True)], extra_turns=[(q, "")])
                    span = r.spans["P"]["full"]
                    ac, lg = run(r.ids); n += 1
                    rec_bnd(f"{base}|{cname}|clean", r, lg, ac, words, WID)
                    lge36 = [l for l in ALL if l >= 36]; own = {l: ac[l][0, span, :].clone() for l in lge36}
                    a_s, l_s = run(r.ids, H.SpanWriter(lm.layers, lge36, span, own)); n += 1
                    META["cells"][base][f"{cname}_selfpatch_bitwise"] = bool(torch.equal(l_s, lg) and all(torch.equal(a_s[l], ac[l]) for l in ALL)); del a_s
                    for dname, dpr in (("diff", dpair), ("same", spair)):
                        rd = Rn.render(tok, utext(dpr, car), car, sources=[("P", pstr(dpr), True)], extra_turns=[(q, "")])
                        assert len(rd) == len(r) and rd.spans["P"]["full"] == span, f"donor geom {base} {cname} {dname} ({pstr(pair)}->{pstr(dpr)})"
                        add, _ = run(rd.ids); n += 1; dsrc = {l: add[l][0, span, :].clone() for l in ALL}; del add
                        for lx in LX_SWEEP:
                            lge = [l for l in ALL if l >= lx]
                            a2, l2 = run(r.ids, H.SpanWriter(lm.layers, lge, span, {l: dsrc[l] for l in lge})); n += 1
                            for l in range(lx):
                                assert torch.equal(a2[l][0, r.interior, :], ac[l][0, r.interior, :]), f"<Lx {base} {cname} {dname} lx{lx}"
                            wn = float(np.mean([(dsrc[l].float() - ac[l][0, span, :].float()).norm(dim=1).mean().item() for l in lge]))
                            rb = float(np.max([(a2[l][0, span, :].float() - dsrc[l].float()).abs().max().item() for l in lge]))
                            tag = f"{base}|{cname}|{dname}swap|lx{lx}"
                            rec_bnd(tag, r, l2, a2, words, WID); RAW[f"{tag}|wnorm"] = np.float32(wn); RAW[f"{tag}|rberr"] = np.float32(rb)
                            del a2
                    del ac
            print(f"  [boundary] {ck}: {n} forwards ({time.time()-t0:.0f}s)", flush=True)

    # -------------------- transport vs recomputation: intervene at the CARRIER (has the sum-latent, no operands) --------------------
    # C_full (carrier<-donor carrier state, operands clean) tests whether the MAINTAINED carrier state is USED,
    # vs the answer re-reading the turn-1 operands and recomputing (O_donor reference flips; C_rand is the control).
    elif STAGE == "transport":
        LX = 36; META["lx"] = LX; META["cells"] = {}
        PAR_WORDS = ["even", "odd"]
        CONSUMERS = {"parity": ("Is their sum even or odd? Answer even or odd.", PAR_WORDS, answer_ids(tok, PAR_WORDS)),
                     "report": ("What is the sum of the pair? Answer with one word.", SUM_WORDS, sumword_ids(tok))}
        parity_of = lambda sword: ("odd" if (SUM_WORDS.index(sword) + 7) % 2 else "even")
        lge = [l for l in ALL if l >= LX]

        def rec_t(tag, r, logits, acts, words, WID):
            sc, top = score_words(tok, logits, WID, words)
            RAW[f"{tag}|scores"] = np.array([sc[w] for w in words], np.float32); RAW[f"{tag}|greedy"] = top
            RAW[f"{tag}|z"] = ro.z(acts, r.interior, SRC).astype(np.float16)
            cs, ce = r.meta["carrier_start"], r.meta["carrier_end"]; nll, _, _ = RO.carrier_damage(logits, r.ids, cs, ce)
            RAW[f"{tag}|nll"] = np.float32(nll)

        for ck in CAL_CARRIERS:
            car = M.CARRIERS[ck]
            for i in range(8):
                pair = pair_of(i, "A"); dpair = diff_donor(i); base = f"S{i}|{ck}"
                META["cells"][base] = {"sum": sum_of(i), "diff_donor": list(dpair), "diff_sum": diff_sum(i), "pair": list(pair),
                                       "own_parity": parity_of(sum_of(i)), "diff_parity": parity_of(diff_sum(i))}
                for cname, (q, words, WID) in CONSUMERS.items():
                    r = Rn.render(tok, utext(pair, car), car, sources=[("P", pstr(pair), True)], extra_turns=[(q, "")])
                    span = r.spans["P"]["full"]; carr = list(range(r.meta["carrier_start"], r.meta["carrier_end"]))
                    ac, lg = run(r.ids); n += 1; rec_t(f"{base}|{cname}|clean", r, lg, ac, words, WID)
                    rd = Rn.render(tok, utext(dpair, car), car, sources=[("P", pstr(dpair), True)], extra_turns=[(q, "")])
                    assert len(rd) == len(r) and rd.spans["P"]["full"] == span and rd.meta["carrier_start"] == r.meta["carrier_start"] and rd.meta["carrier_end"] == r.meta["carrier_end"], f"donor align {base} {cname}"
                    add, _ = run(rd.ids); n += 1
                    O_src = {l: add[l][0, span, :].clone() for l in ALL}          # donor operand-span states
                    C_src = {l: add[l][0, carr, :].clone() for l in ALL}          # donor carrier (copied-text) states
                    del add
                    # O_donor reference: operand span -> donor (carrier free-runs)
                    a1, l1 = run(r.ids, H.SpanWriter(lm.layers, lge, span, {l: O_src[l] for l in lge})); n += 1
                    rec_t(f"{base}|{cname}|O_donor", r, l1, a1, words, WID); del a1
                    # C_full: carrier -> donor carrier state, operand span CLEAN
                    a2, l2 = run(r.ids, H.SpanWriter(lm.layers, lge, carr, {l: C_src[l] for l in lge})); n += 1
                    assert all(torch.equal(a2[l][0, span, :], ac[l][0, span, :]) for l in ALL), f"operand touched under C_full {base} {cname}"
                    rec_t(f"{base}|{cname}|C_full", r, l2, a2, words, WID); del a2
                    # C_rand: carrier -> recipient + per-position norm-matched random, operand span CLEAN
                    g = torch.Generator(device="cpu").manual_seed(SEED + 11 * i + (0 if ck == "C0" else 1) + (0 if cname == "parity" else 5))
                    Crand = {}
                    for l in lge:
                        hC = ac[l][0, carr, :].float(); dn = (C_src[l].float() - hC).norm(dim=1, keepdim=True)
                        v = torch.randn(len(carr), hC.shape[1], generator=g).to(hC.device)
                        Crand[l] = (hC + v / v.norm(dim=1, keepdim=True) * dn).to(ac[l].dtype)
                    a3, l3 = run(r.ids, H.SpanWriter(lm.layers, lge, carr, Crand)); n += 1
                    rec_t(f"{base}|{cname}|C_rand", r, l3, a3, words, WID); del a3
                    del ac
            print(f"  [transport] {ck}: {n} forwards ({time.time()-t0:.0f}s)", flush=True)

    # -------------------- robust (Amendment 2): instrument-independent premise, full-depth carrier, consumer-position distance, necessity, materials --------------------
    elif STAGE == "robust":
        LX = 36; ROB_CARRIERS = ["C0", "C1", "C2", "C3"]; MAPS = {"off3": 3, "off1": 1}
        META.update({"lx": LX, "carriers": ROB_CARRIERS, "maps": MAPS, "cells": {}, "design": "Amendment 2"})
        PAR_WORDS = ["even", "odd"]
        CONSUMERS = {"parity": ("Is their sum even or odd? Answer even or odd.", PAR_WORDS, answer_ids(tok, PAR_WORDS)),
                     "report": ("What is the sum of the pair? Answer with one word.", SUM_WORDS, sumword_ids(tok))}
        parity_of = lambda sword: ("odd" if (SUM_WORDS.index(sword) + 7) % 2 else "even")
        lge = [l for l in ALL if l >= LX]
        # ---- RESID_P number axis (Appendix C number templates; fit 1-4, validate 5-6), fitted here, never from another run
        MU = {}
        for w in COLS:
            for split, tpls in (("fit", M.NUMBER_FIT), ("val", M.NUMBER_VAL)):
                acc = []
                for tpl in tpls:
                    s_ = tpl.format(m=w); enc = tok(s_, add_special_tokens=False, return_offsets_mapping=True)
                    c_end = tpl.index("{m}") + len(w) - 1
                    p = next(k for k, (a, b) in enumerate(enc.offset_mapping) if a <= c_end < b)
                    assert tok.decode(enc.input_ids[p]).strip().lower() in w.lower(), (s_, tok.decode(enc.input_ids[p]))
                    a_, _ = run(enc.input_ids); n += 1
                    acc.append(torch.stack([a_[l][0, p, :].float() for l in ALL])); del a_
                MU[(w, split)] = torch.stack(acc).mean(0)                                   # [64, d]
        np.savez_compressed(os.path.join(OUT, "resid_axis_numbers.npz"), **{f"{w}|{sp}": MU[(w, sp)].cpu().numpy().astype(np.float16) for (w, sp) in MU})
        dec_cent = torch.stack([MU[(d, "fit")] for d in DECOYS]).mean(0)
        PDIR = {w: (MU[(w, "fit")] - dec_cent) / (MU[(w, "fit")] - dec_cent).norm(dim=-1, keepdim=True) for w in SUM_WORDS}
        PCENT = {w: (PDIR[w] * dec_cent).sum(-1) for w in SUM_WORDS}
        dec_val = torch.stack([MU[(d, "val")] for d in DECOYS]).mean(0)
        META["resid_axis"] = {"fit_templates": M.NUMBER_FIT, "val_templates": M.NUMBER_VAL,
                              "heldout_presence_margin_L36_59": {w: float(((PDIR[w] * (MU[(w, "val")] - dec_val)).sum(-1))[36:60].mean()) for w in SUM_WORDS}}
        PAIR = {}                                                                          # (own_sum, donor_sum) -> unit axis [64, d]
        for i in range(8):
            for mk, off in MAPS.items():
                o, d = sum_of(i), SUMS[(i + off) % 8][0]
                v = MU[(d, "fit")] - MU[(o, "fit")]; PAIR[(o, d)] = v / v.norm(dim=-1, keepdim=True)
        META["resid_axis"]["heldout_pair_margin_L36_59"] = {f"{o}->{d}": float(((PAIR[(o, d)] * (MU[(d, "val")] - MU[(o, "val")])).sum(-1))[36:60].mean()) for (o, d) in PAIR}
        print(f"  [robust] number axis fitted ({n} forwards, {time.time()-t0:.0f}s): heldout pair margins "
              f"{ {k: round(v, 2) for k, v in META['resid_axis']['heldout_pair_margin_L36_59'].items()} }", flush=True)
        COLIDS = [TID[w] for w in COLS]

        def rec_rob(tag, r, logits, acts, words, WID, i, h_clean_ans):
            sc, top = score_words(tok, logits, WID, words)
            RAW[f"{tag}|scores"] = np.array([sc[w] for w in words], np.float32); RAW[f"{tag}|greedy"] = top
            RAW[f"{tag}|z"] = ro.z(acts, r.interior, SRC).astype(np.float16)
            hs = torch.stack([acts[l][0, r.interior, :].float() for l in ALL])              # [64, P, d]
            RAW[f"{tag}|p_pres"] = torch.stack([((hs * PDIR[w][:, None, :]).sum(-1) - PCENT[w][:, None]).mean(-1) for w in SUM_WORDS], 1).cpu().numpy().astype(np.float32)  # [64, 8]
            RAW[f"{tag}|p_pair"] = torch.stack([(hs * PAIR[(sum_of(i), SUMS[(i + off) % 8][0])][:, None, :]).sum(-1).mean(-1) for off in MAPS.values()], 1).cpu().numpy().astype(np.float32)  # [64, 2]
            lp = torch.log_softmax(logits[0, r.interior, :].float(), -1)
            RAW[f"{tag}|lp_cols"] = lp[:, COLIDS].mean(0).cpu().numpy().astype(np.float32)   # [21] LOGITS at interior
            cs, ce = r.meta["carrier_start"], r.meta["carrier_end"]; nll, _, _ = RO.carrier_damage(logits, r.ids, cs, ce)
            RAW[f"{tag}|nll"] = np.float32(nll)
            h_ans = torch.stack([acts[l][0, -1, :].float() for l in ALL])                   # [64, d] answer position
            RAW[f"{tag}|ans_dist"] = (h_ans - h_clean_ans).norm(dim=-1).cpu().numpy().astype(np.float32)
            RAW[f"{tag}|ans_norm"] = h_ans.norm(dim=-1).cpu().numpy().astype(np.float32)
            return h_ans

        for ck in ROB_CARRIERS:
            car = M.CARRIERS[ck]
            for i in range(8):
                pair = pair_of(i, "A"); base = f"S{i}|{ck}"
                META["cells"][base] = {"sum": sum_of(i), "pair": list(pair), "own_parity": parity_of(sum_of(i)),
                                       "maps": {mk: {"donor": list(SUMS[(i + off) % 8][1]), "sum": SUMS[(i + off) % 8][0], "parity": parity_of(SUMS[(i + off) % 8][0])} for mk, off in MAPS.items()}}
                for mk, off in MAPS.items():
                    assert parity_of(SUMS[(i + off) % 8][0]) != parity_of(sum_of(i)), f"map {mk} does not flip parity at {base}"
                for cname, (q, words, WID) in CONSUMERS.items():
                    r = Rn.render(tok, utext(pair, car), car, sources=[("P", pstr(pair), True)], extra_turns=[(q, "")])
                    span = r.spans["P"]["full"]; carr = list(range(r.meta["carrier_start"], r.meta["carrier_end"]))
                    ac, lg = run(r.ids); n += 1
                    h0 = rec_rob(f"{base}|{cname}|clean", r, lg, ac, words, WID, i, torch.zeros(len(ALL), R.D_MODEL, device=ac[0].device))
                    RAW[f"{base}|{cname}|clean|ans_dist"] = np.zeros(len(ALL), np.float32)
                    own36 = {l: ac[l][0, carr, :].clone() for l in lge}
                    a_o, l_o = run(r.ids, H.SpanWriter(lm.layers, lge, carr, own36)); n += 1
                    META["cells"][base][f"{cname}_C_own_bitwise"] = bool(torch.equal(l_o, lg) and all(torch.equal(a_o[l], ac[l]) for l in ALL)); del a_o
                    for mk, off in MAPS.items():
                        dpair = SUMS[(i + off) % 8][1]
                        rd = Rn.render(tok, utext(dpair, car), car, sources=[("P", pstr(dpair), True)], extra_turns=[(q, "")])
                        assert len(rd) == len(r) and rd.spans["P"]["full"] == span and rd.meta["carrier_start"] == r.meta["carrier_start"] and rd.meta["carrier_end"] == r.meta["carrier_end"], f"donor align {base} {cname} {mk}"
                        add, _ = run(rd.ids); n += 1
                        O_src = {l: add[l][0, span, :].clone() for l in ALL}; C_src = {l: add[l][0, carr, :].clone() for l in ALL}; del add
                        g = torch.Generator(device="cpu").manual_seed(SEED + 11 * i + ROB_CARRIERS.index(ck) + (0 if cname == "parity" else 5) + 100 * off)
                        Crand = {}
                        for l in lge:
                            hC = ac[l][0, carr, :].float(); dn = (C_src[l].float() - hC).norm(dim=1, keepdim=True)
                            v = torch.randn(len(carr), hC.shape[1], generator=g).to(hC.device)
                            Crand[l] = (hC + v / v.norm(dim=1, keepdim=True) * dn).to(ac[l].dtype)
                        conds = {"O_donor": (H.SpanWriter(lm.layers, lge, span, {l: O_src[l] for l in lge}), False),
                                 "C_full": (H.SpanWriter(lm.layers, lge, carr, {l: C_src[l] for l in lge}), True),
                                 "C_all": (H.SpanWriter(lm.layers, ALL, carr, C_src), True),
                                 "C_rand": (H.SpanWriter(lm.layers, lge, carr, Crand), True),
                                 "NEC": (H.Both(H.SpanWriter(lm.layers, lge, span, {l: O_src[l] for l in lge}), H.SpanWriter(lm.layers, lge, carr, own36)), False)}
                        for cond, (ctx, opd_clean) in conds.items():
                            a_, l_ = run(r.ids, ctx); n += 1
                            if opd_clean:
                                assert all(torch.equal(a_[l][0, span, :], ac[l][0, span, :]) for l in ALL), f"operand touched under {cond} {base} {cname} {mk}"
                            tag = f"{base}|{cname}|{mk}|{cond}"
                            rec_rob(tag, r, l_, a_, words, WID, i, h0)
                            if cond in ("C_full", "C_all"):
                                lw = lge if cond == "C_full" else ALL
                                RAW[f"{tag}|wnorm"] = np.float32(np.mean([(C_src[l].float() - ac[l][0, carr, :].float()).norm(dim=1).mean().item() for l in lw]))
                                RAW[f"{tag}|rberr"] = np.float32(np.max([(a_[l][0, carr, :].float() - C_src[l].float()).abs().max().item() for l in lw]))
                            if cond == "C_rand":
                                RAW[f"{tag}|wnorm"] = np.float32(np.mean([(Crand[l].float() - ac[l][0, carr, :].float()).norm(dim=1).mean().item() for l in lge]))
                            del a_
                    del ac
            print(f"  [robust] {ck}: {n} forwards ({time.time()-t0:.0f}s)", flush=True)

    # -------------------- global (Amendment 3): token-level operand control, consistent global clamp, paper-style coordinate swap,
    # decision-position band swap, first route-restriction pass (attention read block with leak capture) --------------------
    elif STAGE == "global":
        LX = 36; ROB_CARRIERS = ["C0", "C1", "C2", "C3"]; OFF = 3
        SMOKE = os.environ.get("TCSIF_SMOKE") == "1"
        if SMOKE: ROB_CARRIERS = ["C0"]
        META.update({"lx": LX, "carriers": ROB_CARRIERS, "map": OFF, "cells": {}, "design": "Amendment 3", "smoke": SMOKE})
        PAR_WORDS = ["even", "odd"]
        CONSUMERS = {"parity": ("Is their sum even or odd? Answer even or odd.", PAR_WORDS, answer_ids(tok, PAR_WORDS)),
                     "report": ("What is the sum of the pair? Answer with one word.", SUM_WORDS, sumword_ids(tok))}
        parity_of = lambda sword: ("odd" if (SUM_WORDS.index(sword) + 7) % 2 else "even")
        lge = [l for l in ALL if l >= LX]; SWAP_L = list(range(36, 63)); FULL_ATT = R.full_attention_layers(model)
        META["full_attention_layers"] = FULL_ATT; META["swap_layers"] = SWAP_L
        # RESID_P number axis (same construction as `robust`)
        MU = {}
        for w in COLS:
            for split, tpls in (("fit", M.NUMBER_FIT), ("val", M.NUMBER_VAL)):
                acc = []
                for tpl in tpls:
                    s_ = tpl.format(m=w); enc = tok(s_, add_special_tokens=False, return_offsets_mapping=True)
                    c_end = tpl.index("{m}") + len(w) - 1
                    p = next(k for k, (a, b) in enumerate(enc.offset_mapping) if a <= c_end < b)
                    a_, _ = run(enc.input_ids); n += 1
                    acc.append(torch.stack([a_[l][0, p, :].float() for l in ALL])); del a_
                MU[(w, split)] = torch.stack(acc).mean(0)
        dec_cent = torch.stack([MU[(d, "fit")] for d in DECOYS]).mean(0)
        PDIR = {w: (MU[(w, "fit")] - dec_cent) / (MU[(w, "fit")] - dec_cent).norm(dim=-1, keepdim=True) for w in SUM_WORDS}
        PCENT = {w: (PDIR[w] * dec_cent).sum(-1) for w in SUM_WORDS}
        PAIR = {}
        for i in range(8):
            o, d = sum_of(i), SUMS[(i + OFF) % 8][0]; v = MU[(d, "fit")] - MU[(o, "fit")]; PAIR[(o, d)] = v / v.norm(dim=-1, keepdim=True)
        COLIDS = [TID[w] for w in COLS]
        # lens naming directions per layer for the coordinate swap
        NAMING = {w: {l: ro.folded_direction(l, TID[w]) for l in SWAP_L} for w in SUM_WORDS}

        def rec_g(tag, r, logits, acts, words, WID, i, h_clean_ans):
            sc, top = score_words(tok, logits, WID, words)
            RAW[f"{tag}|scores"] = np.array([sc[w] for w in words], np.float32); RAW[f"{tag}|greedy"] = top
            RAW[f"{tag}|z"] = ro.z(acts, r.interior, SRC).astype(np.float16)
            hs = torch.stack([acts[l][0, r.interior, :].float() for l in ALL])
            RAW[f"{tag}|p_pres"] = torch.stack([((hs * PDIR[w][:, None, :]).sum(-1) - PCENT[w][:, None]).mean(-1) for w in SUM_WORDS], 1).cpu().numpy().astype(np.float32)
            RAW[f"{tag}|p_pair"] = (hs * PAIR[(sum_of(i), SUMS[(i + OFF) % 8][0])][:, None, :]).sum(-1).mean(-1).cpu().numpy().astype(np.float32)
            lp = torch.log_softmax(logits[0, r.interior, :].float(), -1)
            RAW[f"{tag}|lp_cols"] = lp[:, COLIDS].mean(0).cpu().numpy().astype(np.float32)
            cs, ce = r.meta["carrier_start"], r.meta["carrier_end"]; nll, _, _ = RO.carrier_damage(logits, r.ids, cs, ce)
            RAW[f"{tag}|nll"] = np.float32(nll)
            h_ans = torch.stack([acts[l][0, -1, :].float() for l in ALL])
            RAW[f"{tag}|ans_dist"] = (h_ans - h_clean_ans).norm(dim=-1).cpu().numpy().astype(np.float32)
            return h_ans

        for ck in ROB_CARRIERS:
            car = M.CARRIERS[ck]
            for i in (range(1) if SMOKE else range(8)):
                pair = pair_of(i, "A"); dpair = SUMS[(i + OFF) % 8][1]; base = f"S{i}|{ck}"
                META["cells"][base] = {"sum": sum_of(i), "pair": list(pair), "own_parity": parity_of(sum_of(i)),
                                       "donor": list(dpair), "diff_sum": SUMS[(i + OFF) % 8][0], "diff_parity": parity_of(SUMS[(i + OFF) % 8][0])}
                for cname, (q, words, WID) in CONSUMERS.items():
                    r = Rn.render(tok, utext(pair, car), car, sources=[("P", pstr(pair), True)], extra_turns=[(q, "")])
                    span = r.spans["P"]["full"]; cs, ce = r.meta["carrier_start"], r.meta["carrier_end"]
                    carr = list(range(cs, ce)); dec = list(range(ce, len(r))); tail = list(range(span[0], len(r)))
                    META["cells"][base][f"{cname}_positions"] = {"span": [span[0], span[-1]], "carrier": [cs, ce], "decision": [ce, len(r)]}
                    ac, lg = run(r.ids); n += 1
                    h0 = rec_g(f"{base}|{cname}|clean", r, lg, ac, words, WID, i, torch.zeros(len(ALL), R.D_MODEL, device=ac[0].device))
                    RAW[f"{base}|{cname}|clean|ans_dist"] = np.zeros(len(ALL), np.float32)
                    rd = Rn.render(tok, utext(dpair, car), car, sources=[("P", pstr(dpair), True)], extra_turns=[(q, "")])
                    assert len(rd) == len(r) and rd.spans["P"]["full"] == span and rd.meta["carrier_start"] == cs and rd.meta["carrier_end"] == ce, f"donor align {base} {cname}"
                    add, _ = run(rd.ids); n += 1
                    O_src = {l: add[l][0, span, :].clone() for l in ALL}; C_src = {l: add[l][0, carr, :].clone() for l in ALL}
                    D_src = {l: add[l][0, dec, :].clone() for l in ALL}; del add
                    own, dsw = sum_of(i), SUMS[(i + OFF) % 8][0]
                    dirs = {l: (NAMING[own][l], NAMING[dsw][l]) for l in SWAP_L}
                    conds = {
                        "O_donor36": (lambda: H.SpanWriter(lm.layers, lge, span, {l: O_src[l] for l in lge})),
                        "O_donor0": (lambda: H.SpanWriter(lm.layers, ALL, span, O_src)),
                        "C_full": (lambda: H.SpanWriter(lm.layers, lge, carr, {l: C_src[l] for l in lge})),
                        "G_full": (lambda: H.Both(H.SpanWriter(lm.layers, lge, span, {l: O_src[l] for l in lge}), H.SpanWriter(lm.layers, lge, carr, {l: C_src[l] for l in lge}))),
                        "G_swap_all": (lambda: H.CoordSwap(lm.layers, SWAP_L, tail, dirs)),
                        "G_swap_carrier": (lambda: H.CoordSwap(lm.layers, SWAP_L, carr, dirs)),
                        "D_band": (lambda: H.SpanWriter(lm.layers, list(range(36, 51)), dec, {l: D_src[l] for l in range(36, 51)})),
                        "D_band_early": (lambda: H.SpanWriter(lm.layers, list(range(36, 44)), dec, {l: D_src[l] for l in range(36, 44)})),
                        "mask_clean": (lambda: H.AttnReadBlock(lm.layers, FULL_ATT, dec, span)),
                        "mask_C_full": (lambda: H.Both(H.AttnReadBlock(lm.layers, FULL_ATT, dec, span), H.SpanWriter(lm.layers, lge, carr, {l: C_src[l] for l in lge}))),
                        "mask_O_donor36": (lambda: H.Both(H.AttnReadBlock(lm.layers, FULL_ATT, dec, span), H.SpanWriter(lm.layers, lge, span, {l: O_src[l] for l in lge}))),
                    }
                    for cond, mk in conds.items():
                        ctx = mk()
                        a_, l_ = run(r.ids, ctx); n += 1
                        tag = f"{base}|{cname}|{cond}"
                        rec_g(tag, r, l_, a_, words, WID, i, h0)
                        if cond in ("C_full", "mask_C_full", "G_swap_carrier"):
                            assert all(torch.equal(a_[l][0, span, :], ac[l][0, span, :]) for l in ALL), f"operand touched under {cond} {base} {cname}"
                        if cond.startswith("mask"):
                            blk = ctx if isinstance(ctx, H.AttnReadBlock) else ctx.c[0]
                            RAW[f"{tag}|leak"] = np.array([blk.leak.get(l, np.nan) for l in FULL_ATT], np.float32)
                            assert all(torch.equal(a_[l][0, :ce, :], ac[l][0, :ce, :]) for l in ALL) or cond != "mask_clean", f"mask changed pre-consumer states {base}"
                        if cond.startswith("G_swap"):
                            RAW[f"{tag}|swapnorm"] = np.array([ctx.realized.get(l, np.nan) for l in SWAP_L], np.float32)
                        if cond.startswith("D_band"):
                            assert all(torch.equal(a_[l][0, :ce, :], ac[l][0, :ce, :]) for l in ALL), f"decision write touched prefix {base}"
                        del a_
                    del ac
            print(f"  [global] {ck}: {n} forwards ({time.time()-t0:.0f}s)", flush=True)

    SFX = "_smoke" if os.environ.get("TCSIF_SMOKE") == "1" else ""
    np.savez_compressed(os.path.join(OUT, f"raw_{STAGE}{SFX}.npz"), **RAW)
    META.update({"run_id": RUN_ID, "n_forwards": n, "elapsed_s": round(time.time() - t0, 1)})
    json.dump(META, open(os.path.join(OUT, f"meta_{STAGE}{SFX}.json"), "w"), indent=1)
    man = R.manifest_block(); man.update({"run_id": RUN_ID, "stage": STAGE, "script": os.path.relpath(__file__, R.PROJECT),
                                          "design": "H3/design_specs/computed_sum_consumer.md",
                                          "raw_sha256": hashlib.sha256(open(os.path.join(OUT, f"raw_{STAGE}{SFX}.npz"), "rb").read()).hexdigest()})
    json.dump(man, open(os.path.join(OUT, f"manifest_{STAGE}{SFX}.json"), "w"), indent=1)
    print(f"[done {STAGE}] {n} forwards, {time.time()-t0:.0f}s -> {OUT}")


if __name__ == "__main__":
    main()
