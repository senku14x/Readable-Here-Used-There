"""H1.8 competition series and mid-carrier cue on the tagged organism (design: tagged_selection.md, amendment 2).

Usage: competition_and_cue.py evaluate
Writes H1/outputs/competition_and_cue/{raw.npz, meta.json, manifest.json}.
"""
import os, sys, json, time, hashlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "common", "scripts"))
import numpy as np, torch
import registry as R, materials as M, rendering as Rn, readout as RO, hooks as H

OUT = os.path.join(R.PROJECT, "H1", "outputs", "competition_and_cue"); os.makedirs(OUT, exist_ok=True)
RUN_ID = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()); L_X = 36; L_STATE = 35
TAGS = ["A", "B", "C", "D", "E", "F"]; KS = [1, 2, 3, 4, 6]; CARRIERS = M.EVAL_CARRIERS
_bank = [w for p in M.EVAL_BANK_1 + M.EVAL_BANK_2 for w in p]
TRIPLES = [tuple(_bank[3 * i:3 * i + 3]) for i in range(8)]
SETS = [TRIPLES[2 * i] + TRIPLES[2 * i + 1] for i in range(4)]
DECOYS = M.FIT_WORDS[:8]; ALL_LAYERS = list(range(R.N_SRC)); RANK_LAYERS = list(range(24, 60))
COPY = "copy the following text exactly, word for word"
NUM = {1: "one", 2: "two", 3: "three", 4: "four", 6: "six"}
CUE = " Actually, keep the word tagged {T} in mind instead."


def head(words):
    k = len(words); lst = ", ".join(f'({TAGS[i]}) "{w}"' for i, w in enumerate(words))
    return f"Here {'is' if k == 1 else 'are'} {NUM[k]} word{'' if k == 1 else 's'}: {lst}"


def user_text(words, arm, carrier):
    tail = f". Keep the word tagged {arm} in mind while you {COPY}" if arm in TAGS else f". {'That word occurs' if len(words) == 1 else 'Those words occur'} one time. Now {COPY}"
    return head(words) + tail + ":\n\n" + carrier


def split_carrier(car):
    ws = car.split(" "); mid = len(ws) // 2
    return " ".join(ws[:mid]), " ".join(ws[mid:])


def main():
    t0 = time.time(); tok = R.make_tokenizer()
    from jlens.hf import from_hf
    model = R.load_model(); lm = from_hf(model, tok, compile=False); ALL = list(range(R.N_BLOCKS)); run = H.make_run(model, lm, ALL); dev = lm.input_device
    LEN = R.load_lenses(("J_NP",))["J_NP"]
    SRC = sorted({w for s in SETS for w in s}); DONOR = {}
    for ti, tr in enumerate(TRIPLES):
        nxt = TRIPLES[(ti + 1) % 8]
        for i, w in enumerate(tr): DONOR[w] = nxt[i]
    TID = {w: Rn.single_token_id(tok, w) for w in SRC + DECOYS}; assert all(v is not None for v in TID.values())
    COLS = SRC + DECOYS; ro = RO.LensReadout(model, lm, LEN, [TID[w] for w in COLS])
    ra = np.load(os.path.join(R.PROJECT, "H1", "outputs", "natural_modulation", "resid_axis.npz"))
    MU = {w: torch.tensor(ra[f"{w}|fit"].astype(np.float32), device=dev) for w in SRC}
    def pax(X, Y):
        v = MU[Y] - MU[X]; return v / v.norm(dim=-1, keepdim=True)
    F = np.load(os.path.join(R.PROJECT, "H1", "outputs", "tagged_selection", "fits_evaluate.npz"))
    ghat = torch.tensor(F["ghat"], device=dev); dsh = torch.tensor(F["d_shared"], device=dev); dsh = dsh / dsh.norm()
    RAW, META = {}, {"cells": {}, "sets": SETS, "triples": TRIPLES, "donor": DONOR, "columns": COLS, "ks": KS, "carriers": CARRIERS}
    n = 0

    def record(tag, r, acts, logits, words, positions, srcs):
        RAW[f"{tag}|z"] = ro.z(acts, positions, ALL_LAYERS).astype(np.float16)
        hs = torch.stack([acts[l][0, positions, :].float() for l in ALL_LAYERS]); lp = torch.log_softmax(logits[0, positions, :].float(), -1)
        for j in srcs:
            X = words[j]; Y = DONOR[X]
            RAW[f"{tag}|p_pair{j}"] = (hs * pax(X, Y)[:, None, :]).sum(-1).cpu().numpy().astype(np.float32)
            RAW[f"{tag}|lp_margin{j}"] = (lp[:, TID[Y]] - lp[:, TID[X]]).cpu().numpy().astype(np.float32)
        RAW[f"{tag}|rank"] = ro.full_vocab_ranks(acts, positions, RANK_LAYERS, [TID[words[j]] for j in srcs]).astype(np.int32)
        h35 = acts[L_STATE][0, positions, :].float()
        RAW[f"{tag}|g35"] = (h35 @ ghat).cpu().numpy().astype(np.float32); RAW[f"{tag}|dsh35"] = (h35 @ dsh).cpu().numpy().astype(np.float32)
        cs, ce = r.meta["carrier_start"], r.meta["carrier_end"]; nll, top1, _ = RO.carrier_damage(logits, r.ids, cs, ce)
        RAW[f"{tag}|nll"] = np.float32(nll); RAW[f"{tag}|top1"] = top1

    def cell(tag, words, arm, car, srcs, positions_fn):
        nonlocal n
        r = Rn.render(tok, user_text(words, arm, car), car, sources=[(f"X{j}", words[j], True) for j in range(len(words))], name=tag)
        acts, lg = run(r.ids); n += 1; pos = positions_fn(r)
        record(f"{tag}|clean", r, acts, lg, words, pos, srcs)
        META["cells"][tag] = {"words": list(words), "n_tokens": len(r), "n_positions": len(pos)}
        spans = {j: r.spans[f"X{j}"]["full"] for j in srcs}
        own0 = {l: acts[l][0, spans[srcs[0]], :].clone() for l in ALL}
        a_s, l_s = run(r.ids, H.SpanWriter(lm.layers, [l for l in ALL if l >= L_X], spans[srcs[0]], own0)); n += 1
        assert torch.equal(l_s, lg) and all(torch.equal(a_s[l], acts[l]) for l in ALL), f"same-source != clean {tag}"; del a_s
        for j in srcs:
            dw = list(words); dw[j] = DONOR[words[j]]
            rd = Rn.render(tok, user_text(tuple(dw), arm, car), car, sources=[(f"X{i}", dw[i], True) for i in range(len(dw))])
            assert len(rd) == len(r) and rd.spans[f"X{j}"]["full"] == spans[j], f"donor geometry {tag} j={j}"
            ad, _ = run(rd.ids); n += 1; donor = {l: ad[l][0, spans[j], :].clone() for l in ALL}; del ad
            a2, l2 = run(r.ids, H.SpanWriter(lm.layers, [l for l in ALL if l >= L_X], spans[j], donor)); n += 1
            for l in range(L_X): assert torch.equal(a2[l][0, pos, :], acts[l][0, pos, :]), f"layer<{L_X} identity {tag}"
            record(f"{tag}|swap{j}", r, a2, l2, words, pos, srcs); del a2
        del acts

    # ---------------- competition
    for ck in CARRIERS:
        car = M.CARRIERS[ck]
        for si, s6 in enumerate(SETS):
            for fi, focal in enumerate((s6[0], s6[3])):
                distract = [w for w in s6 if w != focal]
                for k in KS:
                    for place in ("first", "last"):
                        if k == 1 and place == "last": continue
                        words = tuple([focal] + distract[:k - 1]) if place == "first" else tuple(distract[:k - 1] + [focal])
                        fj = 0 if place == "first" else k - 1
                        srcs = [fj] + ([0 if fj != 0 else 1] if k >= 2 else [])
                        for arm in (TAGS[fj], "ctrl"):
                            cell(f"comp|{ck}|S{si}|F{fi}|k{k}|{place}|{arm}", words, arm, car, srcs, lambda r: r.interior)
                            META["cells"][f"comp|{ck}|S{si}|F{fi}|k{k}|{place}|{arm}"].update({"focal_j": fj, "srcs": srcs})
            print(f"  [comp] {ck} S{si}: {n} forwards ({time.time()-t0:.0f}s)", flush=True)
    # ---------------- mid-carrier cue (k = 3, rotation 0, pointed A)
    for ck in CARRIERS:
        c1, c2 = split_carrier(M.CARRIERS[ck])
        for ti, tr in enumerate(TRIPLES):
            for cue in ("switchB", "sameA", "none"):
                car = M.CARRIERS[ck] if cue == "none" else c1 + CUE.format(T="B" if cue == "switchB" else "A") + " " + c2
                def pos_fn(r, c1=c1):
                    cs, ce = r.meta["carrier_start"], r.meta["carrier_end"]
                    full = r.meta["full"]; a_start = full.rindex(r.strings["assistant_carrier"])
                    if cue == "none":
                        cut_char = a_start + len(c1)
                    else:
                        cut_char = full.index("instead.", a_start) + len("instead.")
                    enc = tok(full, add_special_tokens=False, return_offsets_mapping=True)
                    first_after = next(i for i, (a, b) in enumerate(enc.offset_mapping) if a >= cut_char)
                    return [p for p in range(first_after, ce)][1:-2]
                cell(f"cue|{ck}|T{ti}|{cue}", tr, "A", car, [0, 1], pos_fn)
            print(f"  [cue] {ck} T{ti}: {n} forwards ({time.time()-t0:.0f}s)", flush=True)
    META.update({"run_id": RUN_ID, "n_forwards": n, "elapsed_s": round(time.time() - t0, 1), "token_ids": TID})
    np.savez_compressed(os.path.join(OUT, "raw.npz"), **RAW); json.dump(META, open(os.path.join(OUT, "meta.json"), "w"), indent=1)
    man = R.manifest_block(); man.update({"run_id": RUN_ID, "script": os.path.relpath(__file__, R.PROJECT), "design": "H1/design_specs/tagged_selection.md#amendment-2",
                                          "raw_sha256": hashlib.sha256(open(os.path.join(OUT, "raw.npz"), "rb").read()).hexdigest()})
    json.dump(man, open(os.path.join(OUT, "manifest.json"), "w"), indent=1)
    print(f"[done] {n} forwards, {time.time()-t0:.0f}s -> {OUT}")


if __name__ == "__main__":
    main()
