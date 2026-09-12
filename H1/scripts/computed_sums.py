"""H1 computed_sums (design: H1/design_specs/computed_sums.md).

Does a computed value (the sum) transfer, or only its addends? Organism: `Here is the pair "{a} and {b}". Keep their sum in
mind while you copy: {carrier}`. A different-sum donor should move the sum readout; a same-sum sibling donor (different
addends, same sum) should leave the sum readout invariant while moving the addend readout.

Stages: `arithmetic` (competence gate, greedy) · `natural` (sum-word readability gate) · `transfer` (the contrast).
Usage: computed_sums.py arithmetic|natural|transfer
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

STAGE = sys.argv[1] if len(sys.argv) > 1 else "arithmetic"
assert STAGE in ("arithmetic", "natural", "transfer")
OUT = os.path.join(R.PROJECT, "H1", "outputs", "computed_sums"); os.makedirs(OUT, exist_ok=True)
RUN_ID = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()); L_X = 36
SUMS = M.SUMS                                                      # (sum_word, A_addends, same_sum_B_addends)
ROWS = [(i, x) for x in ("A", "B") for i in range(8)]             # 16 source rows
SUM_WORDS = [s[0] for s in SUMS]
NUMS = ["two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen"]
DECOYS = M.FIT_WORDS[:8]
CARRIERS = M.EVAL_CARRIERS
ALL_LAYERS = list(range(R.N_SRC)); RANK_LAYERS = list(range(24, 60))
COPY = "copy the following text exactly, word for word"; COPY_NOW = "Now " + COPY


def pair_of(i, x): return SUMS[i][1] if x == "A" else SUMS[i][2]
def sum_of(i): return SUMS[i][0]
def same_donor(i, x): return SUMS[i][2] if x == "A" else SUMS[i][1]      # other pair, same sum
def diff_donor(i): return SUMS[(i + 3) % 8][1]                            # A-addends of a different sum
def diff_sum(i): return SUMS[(i + 3) % 8][0]
def pstr(p): return f"{p[0]} and {p[1]}"


def ut(kind, pair, carrier):
    head = f'Here is the pair "{pstr(pair)}"'
    if kind == "maintain": return head + f". Keep their sum in mind while you {COPY}:\n\n" + carrier
    if kind == "control":  return head + f". That pair occurs one time. {COPY_NOW}:\n\n" + carrier
    if kind == "absent":   return Rn.ABSENT_HEAD + ":\n\n" + carrier
    if kind == "arith":    return head + ". Keep their sum in mind. What is their sum? Answer with one word."
    raise ValueError(kind)


def main():
    t0 = time.time(); tok = R.make_tokenizer()
    from jlens.hf import from_hf
    model = R.load_model(); lm = from_hf(model, tok, compile=False); ALL = list(range(R.N_BLOCKS))
    run = H.make_run(model, lm, ALL); dev = lm.input_device
    TID = {w: Rn.single_token_id(tok, w) for w in NUMS + DECOYS}
    assert all(v is not None for v in TID.values()), {k: v for k, v in TID.items() if v is None}
    COLS = NUMS + DECOYS; CIX = {w: i for i, w in enumerate(COLS)}
    META = {"rows": ROWS, "sums": SUMS, "columns": COLS, "sum_words": SUM_WORDS, "decoys": DECOYS,
            "carriers": CARRIERS, "rank_layers": RANK_LAYERS, "l_x": L_X, "stage": STAGE}
    RAW = {}; n = 0

    # ---------------- arithmetic competence gate ----------------
    if STAGE == "arithmetic":
        res = {}
        for i, x in ROWS:
            pair = pair_of(i, x); s = sum_of(i)
            enc = tok(tok.apply_chat_template([{"role": "user", "content": ut("arith", pair, None)}], tokenize=False, add_generation_prompt=True, enable_thinking=False), add_special_tokens=False).input_ids
            ids = list(enc)
            for _ in range(3):
                lg = run(ids)[1]; ids.append(int(lg[0, -1].argmax())); n += 1
            ans = tok.decode(ids[len(enc):]).strip()
            res[f"{i}{x}"] = {"pair": list(pair), "sum": s, "answer": ans, "correct": s in ans.lower() or str(_word2num(s)) in ans}
        acc = np.mean([r["correct"] for r in res.values()])
        META["arithmetic"] = res; META["accuracy"] = float(acc)
        print(f"[arithmetic] accuracy {acc:.3f} ({sum(r['correct'] for r in res.values())}/16)", flush=True)
        for k, r in res.items():
            if not r["correct"]: print(f"   MISS {k}: {r['pair']} -> {r['answer']!r} (want {r['sum']})")

    else:
        LEN = R.load_lenses(("J_NP",))["J_NP"]; ro = RO.LensReadout(model, lm, LEN, [TID[w] for w in COLS])
        SUMCOL = [CIX[w] for w in SUM_WORDS]; DECCOL = [CIX[w] for w in DECOYS]

        def record(tag, r, acts, logits):
            inter = r.interior
            RAW[f"{tag}|z"] = ro.z(acts, inter, ALL_LAYERS).astype(np.float16)
            lp = torch.log_softmax(logits[0, inter, :].float(), -1)
            RAW[f"{tag}|lp"] = lp[:, [TID[w] for w in COLS]].cpu().numpy().astype(np.float32)
            cs, ce = r.meta["carrier_start"], r.meta["carrier_end"]; nll, top1, _ = RO.carrier_damage(logits, r.ids, cs, ce)
            RAW[f"{tag}|nll"] = np.float32(nll); RAW[f"{tag}|top1"] = top1

        # ---------------- natural readability gate ----------------
        if STAGE == "natural":
            for ck in CARRIERS:
                car = M.CARRIERS[ck]
                for i, x in ROWS:
                    pair = pair_of(i, x)
                    for cond in ("maintain", "control", "absent"):
                        tag = f"{i}{x}|{ck}|{cond}"
                        srcs = [] if cond == "absent" else [("P", pstr(pair), True)]
                        r = Rn.render(tok, ut(cond, pair, car), car, sources=srcs, name=tag)
                        acts, lg = run(r.ids); n += 1; record(tag, r, acts, lg); del acts
                        META.setdefault("cells", {})[tag] = {"pair": list(pair), "sum": sum_of(i), "cond": cond}
                print(f"  [natural] {ck}: {n} forwards ({time.time()-t0:.0f}s)", flush=True)

        # ---------------- transfer ----------------
        else:
            for ck in CARRIERS:
                car = M.CARRIERS[ck]
                for i, x in ROWS:
                    pair = pair_of(i, x); dpair = diff_donor(i); spair = same_donor(i, x)
                    for arm in ("maintain", "control"):
                        tag = f"{i}{x}|{ck}|{arm}"
                        r = Rn.render(tok, ut(arm, pair, car), car, sources=[("P", pstr(pair), True)], name=tag)
                        span = r.spans["P"]["full"]
                        acts, lg = run(r.ids); n += 1; record(f"{tag}|clean", r, acts, lg)
                        META.setdefault("cells", {})[tag] = {"pair": list(pair), "sum": sum_of(i), "diff_donor": list(dpair),
                                                             "diff_sum": diff_sum(i), "same_donor": list(spair), "arm": arm}
                        # same-source gate
                        own = {l: acts[l][0, span, :].clone() for l in ALL}
                        a_s, l_s = run(r.ids, H.SpanWriter(lm.layers, [l for l in ALL if l >= L_X], span, own)); n += 1
                        assert torch.equal(l_s, lg) and all(torch.equal(a_s[l], acts[l]) for l in ALL), f"same-source {tag}"; del a_s
                        for dname, dpr in (("diff", dpair), ("same", spair)):
                            rd = Rn.render(tok, ut(arm, dpr, car), car, sources=[("P", pstr(dpr), True)])
                            assert len(rd) == len(r) and rd.spans["P"]["full"] == span, f"donor geometry {tag} {dname} ({pstr(pair)}->{pstr(dpr)})"
                            ad, _ = run(rd.ids); n += 1; dn = {l: ad[l][0, span, :].clone() for l in ALL}; del ad
                            a2, l2 = run(r.ids, H.SpanWriter(lm.layers, [l for l in ALL if l >= L_X], span, dn)); n += 1
                            for l in range(L_X):
                                assert torch.equal(a2[l][0, r.interior, :], acts[l][0, r.interior, :]), f"<Lx {tag} {dname}"
                            record(f"{tag}|{dname}swap", r, a2, l2); del a2
                        del acts
                    print(f"  [transfer] {ck} row {i}{x}: {n} forwards ({time.time()-t0:.0f}s)", flush=True)

    if STAGE != "arithmetic":
        np.savez_compressed(os.path.join(OUT, f"raw_{STAGE}.npz"), **RAW)
    META.update({"run_id": RUN_ID, "n_forwards": n, "elapsed_s": round(time.time() - t0, 1), "token_ids": TID})
    json.dump(META, open(os.path.join(OUT, f"meta_{STAGE}.json"), "w"), indent=1)
    man = R.manifest_block(); man.update({"run_id": RUN_ID, "stage": STAGE, "script": os.path.relpath(__file__, R.PROJECT), "design": "H1/design_specs/computed_sums.md"})
    if STAGE != "arithmetic":
        man["raw_sha256"] = hashlib.sha256(open(os.path.join(OUT, f"raw_{STAGE}.npz"), "rb").read()).hexdigest()
    json.dump(man, open(os.path.join(OUT, f"manifest_{STAGE}.json"), "w"), indent=1)
    print(f"[done {STAGE}] {n} forwards, {time.time()-t0:.0f}s -> {OUT}")


_W2N = {"seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14}
def _word2num(s): return _W2N.get(s, s)


if __name__ == "__main__":
    main()
