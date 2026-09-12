"""H1 source transfer: does sustained replacement of the source span from layer L_x onward move the later
readout toward the donor, and from which L_x? (Package 1, H1.2 source intervention; calibration of L_x.)

Testing category-independent word-source transfer under the controlled copy scaffold. For each
geometry-matched calibration pair (X, Y), both directions, both arms (maintain, mention), fitting carriers:
clean X, clean Y (donor cache), same-source replacement at L_x=36 (bitwise gate), and swaps at each L_x in
the sweep with a layers-<L_x identity assert. Readouts at every lens layer at interior carrier positions.

Usage: source_transfer.py [pilot]
Writes H1/outputs/source_transfer/{raw.npz, meta.json, manifest.json}.
"""
import os, sys, json, time, hashlib, itertools
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "common", "scripts"))
import numpy as np
import torch
import registry as R
import materials as M
import rendering as Rn
import readout as RO
import hooks as H

OUT = R.out_dir("H1", "outputs", "source_transfer")
os.makedirs(OUT, exist_ok=True)
RUN_ID = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
LX_SWEEP = [23, 28, 32, 36, 40, 44]
LX_GATE = 36
ARMS = ["maintain", "mention"]
CARRIERS = M.FIT_CARRIERS
WORDS = M.CALIBRATION_WORDS
DECOYS = M.DECOYS
ALL_LAYERS = list(range(R.N_SRC))


def matched_pairs(tok):
    """Greedy disjoint pairing of calibration words whose quoted-span geometry matches under both arms and carriers."""
    ok = {}
    for a, b in itertools.combinations(WORDS, 2):
        good = True
        for arm in ARMS:
            for ck in CARRIERS:
                car = M.CARRIERS[ck]
                ra = Rn.render(tok, Rn.user_text_controlled(arm, a, car), car, sources=[("X", a, True)])
                rb = Rn.render(tok, Rn.user_text_controlled(arm, b, car), car, sources=[("X", b, True)])
                good &= (len(ra) == len(rb) and ra.spans["X"]["full"] == rb.spans["X"]["full"])
        ok[(a, b)] = good
    used, pairs = set(), []
    for (a, b), g in ok.items():
        if g and a not in used and b not in used:
            pairs.append((a, b)); used.update((a, b))
    return pairs, {f"{a}-{b}": g for (a, b), g in ok.items()}


def main():
    t0 = time.time()
    tok = R.make_tokenizer()
    TID = {w: Rn.single_token_id(tok, w) for w in WORDS + DECOYS}
    COLS = WORDS + DECOYS
    pairs, table = matched_pairs(tok)
    print(f"[pairs] {pairs}", flush=True)
    from jlens.hf import from_hf
    model = R.load_model()
    lm = from_hf(model, tok, compile=False)
    lenses = R.load_lenses(("J_NP",))
    ro = RO.LensReadout(model, lm, lenses["J_NP"], [TID[w] for w in COLS])
    ALL = list(range(R.N_BLOCKS))
    run = H.make_run(model, lm, ALL)
    # plain-sentence axis from the natural_modulation run (independent instrument; fitted on templates 1-8)
    ra = np.load(os.path.join(R.PROJECT, "H1", "outputs", "natural_modulation", "resid_axis.npz"))
    MU = {w: torch.tensor(ra[f"{w}|fit"].astype(np.float32), device=lm.input_device) for w in COLS}
    def pair_axis(X, Y):
        v = MU[Y] - MU[X]; return v / v.norm(dim=-1, keepdim=True)        # [L, d]
    RAW, META = {}, {"cells": {}, "pairs": pairs, "pair_table": table, "columns": COLS, "layers": ALL_LAYERS, "lx_sweep": LX_SWEEP}
    n = 0

    def record(tag, r, acts, logits, X, Y):
        inter = r.interior
        RAW[f"{tag}|z"] = ro.z(acts, inter, ALL_LAYERS).astype(np.float16)
        nn, rr, z32 = ro.diagnostics(acts, inter, ALL_LAYERS)
        RAW[f"{tag}|z32"] = z32.astype(np.float32); RAW[f"{tag}|r"] = rr.astype(np.float32)
        hs = torch.stack([acts[l][0, inter, :].float() for l in ALL_LAYERS])
        RAW[f"{tag}|p_pair"] = (hs * pair_axis(X, Y)[:, None, :]).sum(-1).cpu().numpy().astype(np.float32)
        RAW[f"{tag}|rank"] = ro.full_vocab_ranks(acts, inter, ALL_LAYERS, [TID[X], TID[Y]]).astype(np.int32)
        lp = torch.log_softmax(logits[0, inter, :].float(), -1)
        RAW[f"{tag}|lp_margin"] = (lp[:, TID[Y]] - lp[:, TID[X]]).cpu().numpy().astype(np.float32)
        cs, ce = r.meta["carrier_start"], r.meta["carrier_end"]
        nll, top1, _ = RO.carrier_damage(logits, r.ids, cs, ce)
        RAW[f"{tag}|nll"] = np.float32(nll); RAW[f"{tag}|top1"] = top1
        META["cells"][tag] = {"n_tokens": len(r), "interior": inter, "span_full": r.spans["X"]["full"]}

    for ck in CARRIERS:
        car = M.CARRIERS[ck]
        for (a, b) in pairs:
            for arm in ARMS:
                rend = {w: Rn.render(tok, Rn.user_text_controlled(arm, w, car), car, sources=[("X", w, True)], name=f"{arm}|{w}|{ck}") for w in (a, b)}
                cache, clean = {}, {}
                for w in (a, b):
                    acts, logits = run(rend[w].ids); n += 1
                    cache[w] = {l: acts[l][0, rend[w].spans["X"]["full"], :].clone() for l in ALL}
                    clean[w] = (acts, logits)
                for X, Y in ((a, b), (b, a)):
                    r = rend[X]; span = r.spans["X"]["full"]; inter = r.interior
                    tag = f"{ck}|{arm}|{X}->{Y}"
                    acts0, lg0 = clean[X]
                    record(f"{tag}|clean", r, acts0, lg0, X, Y)
                    # natural donor level: the clean Y run read with the same (X, Y) columns
                    record(f"{tag}|donor_clean", rend[Y], clean[Y][0], clean[Y][1], X, Y)
                    # same-source gate at L_x = 36
                    acts_s, lg_s = run(r.ids, H.SpanWriter(lm.layers, [l for l in ALL if l >= LX_GATE], span, cache[X])); n += 1
                    assert torch.equal(lg_s, lg0) and all(torch.equal(acts_s[l], acts0[l]) for l in ALL), f"same-source != clean at {tag}"
                    del acts_s
                    for lx in LX_SWEEP:
                        acts, logits = run(r.ids, H.SpanWriter(lm.layers, [l for l in ALL if l >= lx], span, cache[Y])); n += 1
                        for l in range(lx):
                            assert torch.equal(acts[l][0, inter, :], acts0[l][0, inter, :]), f"layer<{lx} identity broken at L{l} {tag}"
                        record(f"{tag}|swap{lx}", r, acts, logits, X, Y); del acts
                del clean, cache; torch.cuda.empty_cache()
            print(f"  {ck} {a}-{b}: {n} forwards ({time.time()-t0:.0f}s)", flush=True)
    META.update({"run_id": RUN_ID, "n_forwards": n, "elapsed_s": round(time.time() - t0, 1), "arms": ARMS, "carriers": CARRIERS,
                 "token_ids": TID, "lx_gate": LX_GATE})
    np.savez_compressed(os.path.join(OUT, "raw.npz"), **RAW)
    json.dump(META, open(os.path.join(OUT, "meta.json"), "w"), indent=1)
    man = R.manifest_block(); man.update({"run_id": RUN_ID, "script": os.path.relpath(__file__, R.PROJECT),
                                          "raw_sha256": hashlib.sha256(open(os.path.join(OUT, "raw.npz"), "rb").read()).hexdigest()})
    json.dump(man, open(os.path.join(OUT, "manifest.json"), "w"), indent=1)
    print(f"[done] {n} forwards, {time.time()-t0:.0f}s -> {OUT}")


if __name__ == "__main__":
    main()
