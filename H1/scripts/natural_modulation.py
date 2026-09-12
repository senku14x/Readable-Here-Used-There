"""H1 natural modulation: readout of the introduced word under prompt conditions (Package 1, H1.2 natural endpoint).

Testing whether the maintain instruction raises the lens readability of the introduced word at the copied
sentence, against the project's mention control, plain mention and an absent-source baseline, on the
controlled copy organism and the direct directed-modulation organism (both renderings, never pooled).
Also fits the plain-sentence residual axis (RESID_P) used as the independent presence instrument.

Usage: natural_modulation.py [pilot|full]
  pilot : 8 calibration words × 7 conditions × carriers C0,C1 (controlled); primary direct pair × D0,D3.
Writes H1/outputs/natural_modulation/{raw.npz, resid_axis.npz, meta.json, manifest.json}.
No analysis here; see natural_modulation_analysis.py.
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

STAGE = sys.argv[1] if len(sys.argv) > 1 else "pilot"
OUT = R.out_dir("H1", "outputs", "natural_modulation")
os.makedirs(OUT, exist_ok=True)
RUN_ID = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())

CONDITIONS = ["maintain", "mention", "plain_mention", "ignore", "do_not_think", "never_think", "absent"]
WORDS = M.CALIBRATION_WORDS if STAGE == "pilot" else [w for p in M.EVAL_BANK_1 + M.EVAL_BANK_2 for w in p]
DECOYS = M.DECOYS
CARRIERS = M.FIT_CARRIERS if STAGE == "pilot" else M.EVAL_CARRIERS
DIRECT_CARRIERS = ["D0", "D3"] if STAGE == "pilot" else ["D11", "D14"]
ALL_LAYERS = list(range(R.N_SRC))            # lens source layers 0..62
TOPK_CELLS = ([("maintain", "orange", "C0"), ("mention", "orange", "C0"), ("plain_mention", "orange", "C0"),
               ("absent", "orange", "C0"), ("maintain", "castle", "C1"), ("mention", "castle", "C1")] if STAGE == "pilot" else
              [("maintain", "cat", "C2"), ("mention", "cat", "C2"), ("plain_mention", "cat", "C2"), ("absent", "cat", "C2"), ("maintain", "lake", "C3"), ("mention", "lake", "C3")])
QUAL_SEED = 20260907


def main():
    t0 = time.time()
    tok = R.make_tokenizer()
    TID = {w: Rn.single_token_id(tok, w) for w in WORDS + DECOYS}
    assert all(v is not None for v in TID.values()), TID
    COLS = WORDS + DECOYS
    from jlens.hf import from_hf
    model = R.load_model()
    lm = from_hf(model, tok, compile=False)
    lenses = R.load_lenses(tuple(k for k in ("J_NP", "J_CB", "R_CB") if k in R.REGISTRY["instruments"]))
    ro = {k: RO.LensReadout(model, lm, L, [TID[w] for w in COLS]) for k, L in lenses.items()}
    ALL = list(range(R.N_BLOCKS))
    run = H.make_run(model, lm, ALL)
    print(f"[setup] {time.time()-t0:.0f}s", flush=True)

    # ------------------------------------------------------------ RESID_P fit: plain-sentence means at the target token
    MU = {}    # (word, split) -> [n_layers, d] float16 mean over templates
    for w in COLS:
        for split, tpls in (("fit", M.PLAIN_FIT), ("val", M.PLAIN_VAL)):
            acc = []
            for tpl in tpls:
                s = tpl.format(m=w)
                enc = tok(s, add_special_tokens=False, return_offsets_mapping=True)
                c_end = tpl.index("{m}") + len(w) - 1          # slot position, not first substring match ("king" in "asking")
                p = next(i for i, (a, b) in enumerate(enc.offset_mapping) if a <= c_end < b)
                assert tok.decode(enc.input_ids[p]).strip().lower() in w.lower(), (s, tok.decode(enc.input_ids[p]))
                acts, _ = run(enc.input_ids)
                acc.append(torch.stack([acts[l][0, p, :].float() for l in ALL_LAYERS]))
                del acts
            MU[(w, split)] = torch.stack(acc).mean(0)
    resid = {f"{w}|{split}": MU[(w, split)].cpu().numpy().astype(np.float16) for (w, split) in MU}
    axis_path = os.path.join(OUT, "resid_axis.npz")
    if os.path.exists(axis_path):
        old = np.load(axis_path); resid = {**{k: old[k] for k in old.files}, **resid}
    np.savez_compressed(axis_path, **resid)
    # one-vs-decoy centroid presence direction per word, per layer, with the centering constant
    dec_cent = torch.stack([MU[(d, "fit")] for d in DECOYS]).mean(0)          # [L, d]
    PDIR, PCENT = {}, {}
    for w in WORDS:
        v = MU[(w, "fit")] - dec_cent
        v = v / v.norm(dim=-1, keepdim=True)
        PDIR[w] = v
        PCENT[w] = (v * dec_cent).sum(-1)                                        # [L]
    # validation of the axis on held-out contexts: sign of p_w.(mu_w_val - mu_decoy_val_centroid)
    dec_cent_val = torch.stack([MU[(d, "val")] for d in DECOYS]).mean(0)
    val_margin = {w: float(((PDIR[w] * (MU[(w, "val")] - dec_cent_val)).sum(-1))[36:51].mean()) for w in WORDS}
    print(f"[resid axis] held-out margins at L36-50: {json.dumps({k: round(v, 3) for k, v in val_margin.items()})} ({time.time()-t0:.0f}s)", flush=True)

    # ------------------------------------------------------------ battery
    RAW, META = {}, {"cells": {}, "columns": COLS, "layers": ALL_LAYERS}
    rng = np.random.default_rng(QUAL_SEED)
    n = 0

    def record(tag, r, acts, logits, X):
        inter = r.interior
        for k, ro_k in ro.items():
            RAW[f"{tag}|z|{k}"] = ro_k.z(acts, inter, ALL_LAYERS).astype(np.float16)
        nn, rr, z32 = ro["J_NP"].diagnostics(acts, inter, ALL_LAYERS)
        RAW[f"{tag}|n|J_NP"] = nn.astype(np.float32); RAW[f"{tag}|r|J_NP"] = rr.astype(np.float32); RAW[f"{tag}|z32|J_NP"] = z32.astype(np.float32)
        if X is not None:
            RAW[f"{tag}|rank_X"] = ro["J_NP"].full_vocab_ranks(acts, inter, ALL_LAYERS, [TID[X]])[:, :, 0].astype(np.int32)
            hs = torch.stack([acts[l][0, inter, :].float() for l in ALL_LAYERS])           # [L, P, d]
            RAW[f"{tag}|p_pres"] = ((hs * PDIR[X][:, None, :]).sum(-1) - PCENT[X][:, None]).cpu().numpy().astype(np.float32)
            lp = torch.log_softmax(logits[0, inter, :].float(), -1)
            RAW[f"{tag}|lp_X"] = lp[:, TID[X]].cpu().numpy().astype(np.float32)
            RAW[f"{tag}|lp_decoys"] = lp[:, [TID[d] for d in DECOYS]].mean(-1).cpu().numpy().astype(np.float32)
        cs, ce = r.meta["carrier_start"], r.meta["carrier_end"]
        nll, top1, _ = RO.carrier_damage(logits, r.ids, cs, ce)
        RAW[f"{tag}|nll"] = np.float32(nll); RAW[f"{tag}|top1"] = top1
        META["cells"][tag] = {"n_tokens": len(r), "interior": inter, "carrier": [cs, ce],
                              "span": r.spans.get("X"), "user_text": r.meta["user_text"], "gates": r.meta["gates"]}

    # controlled organism
    for ck in CARRIERS:
        car = M.CARRIERS[ck]
        for cond in CONDITIONS:
            for X in WORDS:
                if cond == "absent" and X != WORDS[0]:
                    continue   # absent source is word-independent; rendered once per carrier, scored against every word below
                src = [] if cond == "absent" else [("X", X, cond not in ("plain_mention",))]
                r = Rn.render(tok, Rn.user_text_controlled(cond, X, car), car, sources=src, name=f"{cond}|{X}|{ck}")
                acts, logits = run(r.ids); n += 1
                tag = f"controlled|{cond}|{X if cond != 'absent' else 'NONE'}|{ck}"
                record(tag, r, acts, logits, None if cond == "absent" else X)
                if cond == "absent":
                    inter = r.interior
                    hs = torch.stack([acts[l][0, inter, :].float() for l in ALL_LAYERS])
                    for w in WORDS:   # presence of every word under the absent-source baseline
                        RAW[f"{tag}|p_pres|{w}"] = ((hs * PDIR[w][:, None, :]).sum(-1) - PCENT[w][:, None]).cpu().numpy().astype(np.float32)
                        RAW[f"{tag}|rank_X|{w}"] = ro["J_NP"].full_vocab_ranks(acts, inter, ALL_LAYERS, [TID[w]])[:, :, 0].astype(np.int32)
                if (cond, X, ck) in TOPK_CELLS:
                    ids10, vals10 = ro["J_NP"].topk(acts, r.interior, ALL_LAYERS, 10)
                    RAW[f"{tag}|top10_ids"] = ids10; RAW[f"{tag}|top10_vals"] = vals10
                del acts
            print(f"  controlled {ck} {cond}: {n} forwards ({time.time()-t0:.0f}s)", flush=True)
    # direct organism: primary pair, direct rendering and copy-adapted rendering
    for dk in DIRECT_CARRIERS:
        car = M.DIRECT_CARRIERS[dk]
        for pid in M.DIRECT_PRIMARY_PAIR:
            fam, txt = M.DIRECT_PHRASINGS[pid]
            for X in WORDS:
                for rend in ("direct", "copy_adapted"):
                    u = Rn.user_text_direct(txt, X, car, copy_adapted=(rend == "copy_adapted"))
                    r = Rn.render(tok, u, car, sources=[("X", X, False)], name=f"{rend}|{pid}|{X}|{dk}", carrier_in_user=(rend == "copy_adapted"))
                    acts, logits = run(r.ids); n += 1
                    record(f"{rend}|{pid}|{X}|{dk}", r, acts, logits, X); del acts
            print(f"  direct {dk} {pid}: {n} forwards ({time.time()-t0:.0f}s)", flush=True)
    # seeded random qualitative sample: 6 cells, top-10 at all layers
    keys = [k for k in META["cells"] if k.startswith("controlled") and "|NONE|" not in k]
    for k in rng.choice(keys, size=min(6, len(keys)), replace=False):
        cond, X, ck = k.split("|")[1:]
        r = Rn.render(tok, Rn.user_text_controlled(cond, X, M.CARRIERS[ck]), M.CARRIERS[ck],
                      sources=[("X", X, cond != "plain_mention")])
        acts, _ = run(r.ids); n += 1
        ids10, vals10 = ro["J_NP"].topk(acts, r.interior, ALL_LAYERS, 10)
        RAW[f"{k}|qual_top10_ids"] = ids10; RAW[f"{k}|qual_top10_vals"] = vals10; del acts
    META["qual_random_cells"] = [k for k in keys if f"{k}|qual_top10_ids" in RAW]
    META.update({"run_id": RUN_ID, "stage": STAGE, "n_forwards": n, "elapsed_s": round(time.time() - t0, 1),
                 "words": WORDS, "decoys": DECOYS, "carriers": CARRIERS, "direct_carriers": DIRECT_CARRIERS,
                 "conditions": CONDITIONS, "direct_pair": list(M.DIRECT_PRIMARY_PAIR), "token_ids": TID,
                 "resid_axis": {"fit_templates": M.PLAIN_FIT, "val_templates": M.PLAIN_VAL, "heldout_margin_L36_50": val_margin,
                                "construction": "unit(mu_X^fit - centroid(mu_decoys^fit)) per layer; presence = p.h - p.centroid"},
                 "topk_cells": [list(c) for c in TOPK_CELLS], "qual_seed": QUAL_SEED})
    np.savez_compressed(os.path.join(OUT, f"raw_{STAGE}.npz"), **RAW)
    json.dump(META, open(os.path.join(OUT, f"meta_{STAGE}.json"), "w"), indent=1)
    man = R.manifest_block(); man.update({"run_id": RUN_ID, "stage": STAGE, "script": os.path.relpath(__file__, R.PROJECT),
                                          "raw_sha256": hashlib.sha256(open(os.path.join(OUT, f"raw_{STAGE}.npz"), "rb").read()).hexdigest(),
                                          "gates_result": "common/configs/instrument_gates_result.json"})
    json.dump(man, open(os.path.join(OUT, f"manifest_{STAGE}.json"), "w"), indent=1)
    print(f"[done] {n} forwards, {time.time()-t0:.0f}s -> {OUT}")


if __name__ == "__main__":
    main()
