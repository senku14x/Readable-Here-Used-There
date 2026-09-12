"""H1 tagged categories (design: H1/design_specs/tagged_categories.md).

Does the tagged instruction select category-associated content that is never a token in the prompt?
Stage `gate`  : the category organisms named-category maintain / mention / absent on the 8 eligible categories (member-instrument positive control).
Stage `select`: tagged triples of category labels, 3 rotations, arms {A, B, C, ctrl}, each label source replaced from block 36
                by the partner triple's label at the same slot; readout-only triples for the two geometry-unmatched categories.
Both stages fit the RESID_P member centroids (plain templates 1-8 fit, 9-12 validate) into resid_axis_categories.npz.

Usage: tagged_categories.py gate|select
Writes H1/outputs/tagged_categories/{raw_<stage>.npz, meta_<stage>.json, manifest_<stage>.json}.
"""
import os, sys, json, time, hashlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "common", "scripts"))
import numpy as np, torch
import registry as R, materials as M, rendering as Rn, readout as RO, hooks as H

STAGE = sys.argv[1] if len(sys.argv) > 1 else "gate"
assert STAGE in ("gate", "select")
OUT = os.path.join(R.PROJECT, "H1", "outputs", "tagged_categories"); os.makedirs(OUT, exist_ok=True)
RUN_ID = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()); L_X = 36; L_STATE = 35
TAGS = ["A", "B", "C"]; ARMS = ["A", "B", "C", "ctrl"]
CARRIERS = ["C0", "C1", "C3"]                                   # C2 contains "birds": excluded by textual rule for every category
GATE = json.load(open(os.path.join(R.PROJECT, "common", "configs", "instrument_gates_result.json")))["A"]["categories"]
ELIGIBLE = ["birds", "fish", "insects", "tools", "vehicles", "furniture", "mammals", "vegetables"]
MEMBERS = {c: GATE[c]["eligible_unshown_in_order"][:4] for c in ELIGIBLE}
PRIMARY = ["birds", "fish", "insects", "tools", "vehicles", "furniture"]   # quoted-label geometry 3 tokens each
READOUT_ONLY = ["mammals", "vegetables"]                                    # 5 and 4 tokens: no matched donor (flagged, readout rows only)
# partitions: P0 pure, P1-P3 diagonal mixed (design §3)
PARTITIONS = [(("birds", "fish", "insects"), ("tools", "vehicles", "furniture")),
              (("fish", "insects", "tools"), ("vehicles", "furniture", "birds")),
              (("birds", "insects", "vehicles"), ("tools", "furniture", "fish")),
              (("birds", "fish", "furniture"), ("tools", "vehicles", "insects"))]
TRIPLES = [t for p in PARTITIONS for t in p]                    # 8 triples; partner = other triple of the partition
PARTNER = {t: (p[1] if t == p[0] else p[0]) for p in PARTITIONS for t in p}
RO_TRIPLES = [("mammals", "vegetables", "tools"), ("mammals", "vegetables", "vehicles")]
DECOYS = M.FIT_WORDS[:8]
ALL_LAYERS = list(range(R.N_SRC)); RANK_LAYERS = list(range(24, 60))
COPY = "copy the following text exactly, word for word"


def user_text_tagged(cats, arm, carrier):
    head = f'Here are three categories: (A) "{cats[0]}", (B) "{cats[1]}", (C) "{cats[2]}"'
    tail = f". Keep the category tagged {arm} in mind while you {COPY}" if arm in TAGS else f". Those categories occur one time. Now {COPY}"
    return head + tail + ":\n\n" + carrier


def user_text_gate(cond, c, carrier):
    if cond == "absent": return Rn.ABSENT_HEAD + ":\n\n" + carrier
    return f'Here is the category "{c}"' + Rn.CATEGORY_TAILS[cond] + ":\n\n" + carrier


def rotate(tr, r): return tuple(tr[(i + r) % 3] for i in range(3))


def main():
    t0 = time.time(); tok = R.make_tokenizer()
    from jlens.hf import from_hf
    model = R.load_model(); lm = from_hf(model, tok, compile=False); ALL = list(range(R.N_BLOCKS)); run = H.make_run(model, lm, ALL); dev = lm.input_device
    LEN = R.load_lenses(("J_NP",))["J_NP"]
    ALLMEM = [w for c in ELIGIBLE for w in MEMBERS[c]]
    for c in ELIGIBLE:
        for w in MEMBERS[c]:
            assert w not in M.CATEGORIES[c][0], (c, w)                      # unshown
    assert not (set(ALLMEM) & set(DECOYS))
    for ck in CARRIERS:                                                       # no label or member in any carrier
        for s in ELIGIBLE + ALLMEM: assert not Rn.word_in_text(s, M.CARRIERS[ck]), (ck, s)
    TID = {w: Rn.single_token_id(tok, w) for w in ALLMEM + ELIGIBLE + DECOYS}; assert all(v is not None for v in TID.values()), TID
    COLS = ALLMEM + ELIGIBLE + DECOYS; CIX = {w: i for i, w in enumerate(COLS)}
    ro = RO.LensReadout(model, lm, LEN, [TID[w] for w in COLS])
    # ---------------- RESID_P member centroids (the plain-sentence axis: category centroid = mean of member-context means)
    axis_path = os.path.join(OUT, "resid_axis_categories.npz"); resid = {}
    if os.path.exists(axis_path):
        old = np.load(axis_path); resid = {k: old[k] for k in old.files}
    for w in ALLMEM:
        for split, tpls in (("fit", M.PLAIN_FIT), ("val", M.PLAIN_VAL)):
            if f"{w}|{split}" in resid: continue
            acc = []
            for tpl in tpls:
                s = tpl.format(m=w); enc = tok(s, add_special_tokens=False, return_offsets_mapping=True)
                c_end = tpl.index("{m}") + len(w) - 1                        # slot position (the "king"/"asking" lesson)
                p = next(i for i, (a, b) in enumerate(enc.offset_mapping) if a <= c_end < b)
                assert tok.decode(enc.input_ids[p]).strip().lower() in w.lower(), (s, tok.decode(enc.input_ids[p]))
                acts, _ = run(enc.input_ids); acc.append(torch.stack([acts[l][0, p, :].float() for l in ALL_LAYERS])); del acts
            resid[f"{w}|{split}"] = torch.stack(acc).mean(0).cpu().numpy().astype(np.float16)
    np.savez_compressed(axis_path, **resid)
    MUC = {c: torch.tensor(np.stack([resid[f"{w}|fit"] for w in MEMBERS[c]]).astype(np.float32).mean(0), device=dev) for c in ELIGIBLE}
    MUCV = {c: torch.tensor(np.stack([resid[f"{w}|val"] for w in MEMBERS[c]]).astype(np.float32).mean(0), device=dev) for c in ELIGIBLE}
    def pax(X, Y):
        v = MUC[Y] - MUC[X]; return v / v.norm(dim=-1, keepdim=True)
    axis_val = {}
    for X in ELIGIBLE:
        for Y in ELIGIBLE:
            if X != Y: axis_val[f"{X}->{Y}"] = float((((MUCV[Y] - MUCV[X]) * pax(X, Y)).sum(-1))[36:51].mean())   # held-out-context margin, L36-50
    print(f"[axis] member centroids fit; held-out margin min {min(axis_val.values()):.2f} ({time.time()-t0:.0f}s)", flush=True)
    G = np.load(os.path.join(R.PROJECT, "H1", "outputs", "task_state_modulation", "G.npz")); ghat = torch.tensor(G["ghat"], device=dev)
    F = np.load(os.path.join(R.PROJECT, "H1", "outputs", "tagged_selection", "fits_evaluate.npz")); dshw = torch.tensor(F["d_shared"], device=dev); dshw = dshw / dshw.norm()
    RAW, META = {}, {"cells": {}, "members": MEMBERS, "eligible": ELIGIBLE, "primary": PRIMARY, "readout_only": READOUT_ONLY, "triples": TRIPLES, "ro_triples": RO_TRIPLES,
                     "partner": {" ".join(k): list(v) for k, v in PARTNER.items()}, "columns": COLS, "carriers": CARRIERS, "arms": ARMS, "rank_layers": RANK_LAYERS,
                     "l_state": L_STATE, "l_x": L_X, "axis_heldout_margin_L36_50": axis_val, "stage": STAGE}
    n = 0

    def record(tag, r, acts, logits, cats, srcs, clean=False):
        inter = r.interior
        RAW[f"{tag}|z"] = ro.z(acts, inter, ALL_LAYERS).astype(np.float16)
        RAW[f"{tag}|lp"] = torch.log_softmax(logits[0, inter, :].float(), -1)[:, [TID[w] for w in COLS]].cpu().numpy().astype(np.float32)
        hs = torch.stack([acts[l][0, inter, :].float() for l in ALL_LAYERS])
        for j in srcs:
            X = cats[j]; Y = DONOR_OF(cats, j)
            RAW[f"{tag}|p_pair{j}"] = (hs * pax(X, Y)[:, None, :]).sum(-1).cpu().numpy().astype(np.float32)
        targets = [TID[c] for c in cats] + [TID[w] for c in cats for w in MEMBERS[c]]
        RAW[f"{tag}|rank"] = ro.full_vocab_ranks(acts, inter, RANK_LAYERS, targets).astype(np.int32)
        h35 = acts[L_STATE][0, inter, :].float()
        RAW[f"{tag}|g35"] = (h35 @ ghat).cpu().numpy().astype(np.float32); RAW[f"{tag}|dshw35"] = (h35 @ dshw).cpu().numpy().astype(np.float32)
        if clean: RAW[f"{tag}|h35mean"] = h35.mean(0).cpu().numpy().astype(np.float32)
        cs, ce = r.meta["carrier_start"], r.meta["carrier_end"]; nll, top1, _ = RO.carrier_damage(logits, r.ids, cs, ce)
        RAW[f"{tag}|nll"] = np.float32(nll); RAW[f"{tag}|top1"] = top1

    CUR = {}
    def DONOR_OF(cats, j):
        return CUR["donor"][j]

    if STAGE == "gate":
        for ck in CARRIERS:
            car = M.CARRIERS[ck]
            for c in ELIGIBLE:
                for cond in ("maintain", "mention", "absent"):
                    tag = f"gate|{ck}|{c}|{cond}"; ut = user_text_gate(cond, c, car)
                    for w in ALLMEM: assert not Rn.word_in_text(w, ut), (tag, w)
                    r = Rn.render(tok, ut, car, sources=([("X0", c, True)] if cond != "absent" else []), name=tag)
                    acts, lg = run(r.ids); n += 1; CUR["donor"] = {}
                    record(tag, r, acts, lg, (c,), [], clean=True); META["cells"][tag] = {"cats": [c], "cond": cond, "n_tokens": len(r), "interior_n": len(r.interior)}; del acts
            print(f"  [gate] {ck}: {n} forwards ({time.time()-t0:.0f}s)", flush=True)
    else:
        def cell(tag, cats, arm, ck, srcs, donor):
            nonlocal n
            car = M.CARRIERS[ck]; ut = user_text_tagged(cats, arm, car)
            for w in ALLMEM: assert not Rn.word_in_text(w, ut), (tag, w)
            r = Rn.render(tok, ut, car, sources=[(f"X{j}", cats[j], True) for j in range(3)], name=tag)
            acts, lg = run(r.ids); n += 1; CUR["donor"] = donor
            record(f"{tag}|clean", r, acts, lg, cats, srcs, clean=True)
            META["cells"][tag] = {"cats": list(cats), "arm": arm, "donor": {str(j): donor[j] for j in srcs}, "n_tokens": len(r), "interior_n": len(r.interior)}
            if not srcs: del acts; return
            spans = {j: r.spans[f"X{j}"]["full"] for j in srcs}
            own0 = {l: acts[l][0, spans[0], :].clone() for l in ALL}
            a_s, l_s = run(r.ids, H.SpanWriter(lm.layers, [l for l in ALL if l >= L_X], spans[0], own0)); n += 1
            assert torch.equal(l_s, lg) and all(torch.equal(a_s[l], acts[l]) for l in ALL), f"same-source != clean {tag}"; del a_s
            for j in srcs:
                dc = list(cats); dc[j] = donor[j]
                rd = Rn.render(tok, user_text_tagged(tuple(dc), arm, car), car, sources=[(f"X{i}", dc[i], True) for i in range(3)])
                assert len(rd) == len(r) and rd.spans[f"X{j}"]["full"] == spans[j], f"donor geometry {tag} j={j}"
                ad, _ = run(rd.ids); n += 1; dn = {l: ad[l][0, spans[j], :].clone() for l in ALL}; del ad
                a2, l2 = run(r.ids, H.SpanWriter(lm.layers, [l for l in ALL if l >= L_X], spans[j], dn)); n += 1
                for l in range(L_X): assert torch.equal(a2[l][0, r.interior, :], acts[l][0, r.interior, :]), f"layer<{L_X} identity {tag} j={j}"
                record(f"{tag}|swap{j}", r, a2, l2, cats, srcs); del a2
            del acts
        for ck in CARRIERS:
            for ti, tr in enumerate(TRIPLES):
                for rot in range(3):
                    cats = rotate(tr, rot); partner = rotate(PARTNER[tr], rot); donor = {j: partner[j] for j in range(3)}
                    for arm in ARMS: cell(f"sel|{ck}|T{ti}|rot{rot}|{arm}", cats, arm, ck, [0, 1, 2], donor)
                print(f"  [select] {ck} T{ti}: {n} forwards ({time.time()-t0:.0f}s)", flush=True)
            for ti, tr in enumerate(RO_TRIPLES):
                for rot in range(3):
                    cats = rotate(tr, rot)
                    for arm in ARMS: cell(f"ro|{ck}|R{ti}|rot{rot}|{arm}", cats, arm, ck, [], {})
            print(f"  [readout-only] {ck}: {n} forwards ({time.time()-t0:.0f}s)", flush=True)
    META.update({"run_id": RUN_ID, "n_forwards": n, "elapsed_s": round(time.time() - t0, 1), "token_ids": TID})
    np.savez_compressed(os.path.join(OUT, f"raw_{STAGE}.npz"), **RAW); json.dump(META, open(os.path.join(OUT, f"meta_{STAGE}.json"), "w"), indent=1)
    man = R.manifest_block(); man.update({"run_id": RUN_ID, "stage": STAGE, "script": os.path.relpath(__file__, R.PROJECT), "design": "H1/design_specs/tagged_categories.md",
                                          "raw_sha256": hashlib.sha256(open(os.path.join(OUT, f"raw_{STAGE}.npz"), "rb").read()).hexdigest()})
    json.dump(man, open(os.path.join(OUT, f"manifest_{STAGE}.json"), "w"), indent=1)
    print(f"[done {STAGE}] {n} forwards, {time.time()-t0:.0f}s -> {OUT}")


if __name__ == "__main__":
    main()
