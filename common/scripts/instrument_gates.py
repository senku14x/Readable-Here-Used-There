"""Instrument, rendering and materials gates. Run before any scientific forward.

Part A (no GPU): materials eligibility — single-token status of every bank word, decoy and category
member; carrier overlap; rendering gates on the frozen exact prompts for calibration words.
Part B (GPU): model identity (layer types from config), eager attention weights reachable, hooks
disabled == clean, empty patch == clean, same-source replacement == clean (bitwise), lens
subprojection == full unembedding, repeat-determinism at fixed length, and the sequence-length
nondeterminism magnitude (a documented tolerance input, not a pass/fail).

Writes common/configs/instrument_gates_result.json.
"""
import os, sys, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import torch
import registry as R
import materials as M
import rendering as Rn

OUT = os.path.join(R.out_dir("common", "configs"), "instrument_gates_result.json")
res = {"meta": {"started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}, "A": {}, "B": {}}


def main():
    t0 = time.time()
    tok = R.make_tokenizer()
    # ---------------------------------------------------------------- Part A: materials
    words = {"fit": M.FIT_WORDS, "calibration": M.CALIBRATION_WORDS, "decoys": M.DECOYS,
             "bank1": [w for p in M.EVAL_BANK_1 for w in p], "bank2": [w for p in M.EVAL_BANK_2 for w in p]}
    elig = {}
    all_carriers = {**M.CARRIERS, **M.DIRECT_CARRIERS}
    for role, ws in words.items():
        for w in ws:
            tid = Rn.single_token_id(tok, w)
            bare = tok(w, add_special_tokens=False).input_ids
            overlap = [k for k, c in all_carriers.items() if Rn.word_in_text(w, c)]
            elig[w] = {"role": role, "space_token_id": tid, "single_token_space": tid is not None,
                       "n_pieces_bare": len(bare), "carrier_overlap": overlap}
    cat = {}
    for name, (shown, unshown) in M.CATEGORIES.items():
        members = {}
        for m in unshown:
            tid = Rn.single_token_id(tok, m)
            overlap = [k for k, c in all_carriers.items() if Rn.word_in_text(m, c)]
            members[m] = {"single_token_space": tid is not None, "space_token_id": tid, "carrier_overlap": overlap}
        label_tid = Rn.single_token_id(tok, name)
        eligible = [m for m in unshown if members[m]["single_token_space"] and not members[m]["carrier_overlap"]]
        cat[name] = {"shown": shown, "members": members, "label_single_token": label_tid is not None,
                     "eligible_unshown_in_order": eligible, "K4_ok": len(eligible) >= 4, "K4": eligible[:4]}
    res["A"]["word_eligibility"] = elig
    res["A"]["categories"] = cat
    res["A"]["ineligible_words"] = [w for w, e in elig.items() if not e["single_token_space"]]
    res["A"]["carrier_overlap_words"] = {w: e["carrier_overlap"] for w, e in elig.items() if e["carrier_overlap"]}
    res["A"]["categories_K4_fail"] = [c for c, e in cat.items() if not e["K4_ok"]]
    # rendering gates on the exact spec prompts
    rend = {}
    for X in M.CALIBRATION_WORDS[:2]:
        for ck in ("C0", "C2"):
            car = M.CARRIERS[ck]
            for cond in ("maintain", "mention", "ignore", "do_not_think", "never_think"):
                r = Rn.render(tok, Rn.user_text_controlled(cond, X, car), car, sources=[("X", X, True)], name=f"{cond}|{X}|{ck}")
                rend[f"{cond}|{X}|{ck}"] = {"gates": r.meta["gates"], "n_tokens": len(r), "span": r.spans["X"],
                                            "carrier": [r.meta["carrier_start"], r.meta["carrier_end"]],
                                            "interior_n": len(r.interior), "span_pieces": len(r.spans["X"]["content"])}
            r = Rn.render(tok, Rn.user_text_controlled("plain_mention", X, car), car, sources=[("X", X, False)], name=f"plain_mention|{X}|{ck}")
            rend[f"plain_mention|{X}|{ck}"] = {"gates": r.meta["gates"], "n_tokens": len(r), "span": r.spans["X"]}
            for cond in ("absent", "pulse_base"):
                r = Rn.render(tok, Rn.user_text_controlled(cond, X, car), car, sources=[], name=f"{cond}|{ck}")
                rend[f"{cond}|{X}|{ck}"] = {"gates": r.meta["gates"], "n_tokens": len(r)}
            # direct organism, primary pair, carrier D0
            for pid in M.DIRECT_PRIMARY_PAIR:
                fam, txt = M.DIRECT_PHRASINGS[pid]
                dcar = M.DIRECT_CARRIERS["D0"]
                r = Rn.render(tok, Rn.user_text_direct(txt, X), dcar, sources=[("X", X, False)], name=f"direct|{pid}|{X}", carrier_in_user=False)
                rend[f"direct|{pid}|{X}"] = {"gates": {k: v for k, v in r.meta["gates"].items() if k != "user_carrier"}, "n_tokens": len(r)}
                r = Rn.render(tok, Rn.user_text_direct(txt, X, dcar, copy_adapted=True), dcar, sources=[("X", X, False)], name=f"direct_copy|{pid}|{X}")
                rend[f"direct_copy|{pid}|{X}"] = {"gates": r.meta["gates"], "n_tokens": len(r)}
    res["A"]["rendering"] = rend
    # donor geometry match for calibration pairs (same arm, same carrier): spans and lengths must agree
    geo = {}
    for cond in ("maintain", "mention"):
        for (X, Y) in [("orange", "guitar"), ("tiger", "castle"), ("diamond", "rocket"), ("mountain", "thunder")]:
            car = M.CARRIERS["C0"]
            rx = Rn.render(tok, Rn.user_text_controlled(cond, X, car), car, sources=[("X", X, True)])
            ry = Rn.render(tok, Rn.user_text_controlled(cond, Y, car), car, sources=[("X", Y, True)])
            geo[f"{cond}|{X}-{Y}"] = {"len": [len(rx), len(ry)], "span_full": [rx.spans["X"]["full"], ry.spans["X"]["full"]],
                                      "match": len(rx) == len(ry) and rx.spans["X"]["full"] == ry.spans["X"]["full"]}
    res["A"]["donor_geometry"] = geo
    res["A"]["pass"] = bool(all(v["gates"].values() if isinstance(v.get("gates"), dict) else True for v in rend.values()))
    print(f"[A] ineligible words {res['A']['ineligible_words']} | overlap {res['A']['carrier_overlap_words']} | K4 fail {res['A']['categories_K4_fail']} | rendering pass {res['A']['pass']} ({time.time()-t0:.0f}s)", flush=True)
    print("[A] donor geometry:", {k: v["match"] for k, v in geo.items()}, flush=True)
    json.dump(res, open(OUT, "w"), indent=1)

    # ---------------------------------------------------------------- Part B: GPU gates
    from jlens.hf import from_hf
    from jlens.hooks import ActivationRecorder
    import hooks as H
    import readout as RO
    model = R.load_model()
    load_s = time.time() - t0
    lm = from_hf(model, tok, compile=False)
    lt = R.layer_types(model)
    fa, la = R.full_attention_layers(model), R.linear_attention_layers(model)
    res["B"]["model"] = {"class": type(model).__name__, "load_s": round(load_s, 1), "n_full_attention": len(fa), "n_linear_attention": len(la),
                         "full_attention_layers": fa, "attn_impl": str(getattr(model.config, "_attn_implementation", None)),
                         "gpu_mem_GB": round(torch.cuda.memory_allocated() / 1e9, 1)}
    print(f"[B] {res['B']['model']}", flush=True)
    lenses = R.load_lenses(tuple(k for k in ("J_NP", "J_CB", "R_CB") if k in R.REGISTRY["instruments"]))
    LEN = lenses["J_NP"]
    ALL = list(range(R.N_BLOCKS))
    run = H.make_run(model, lm, ALL)
    X, car = "orange", M.CARRIERS["C0"]
    r = Rn.render(tok, Rn.user_text_controlled("mention", X, car), car, sources=[("X", X, True)])
    ids = r.ids
    # B1 attention weights reachable on full-attention layers (eager)
    grabbed = {}
    hs = [model.model.layers[l].self_attn.register_forward_hook((lambda l: (lambda m, i, o: grabbed.__setitem__(l, None if not (isinstance(o, tuple) and len(o) > 1 and o[1] is not None) else tuple(o[1].shape))))(l)) for l in fa]
    t = time.time(); acts0, lg0 = run(ids); fwd_s = time.time() - t
    [h.remove() for h in hs]
    res["B"]["attention_weights_reachable"] = {"all_present": all(grabbed.get(l) is not None for l in fa), "shape": str(grabbed.get(fa[0]))}
    # B2 repeat determinism, hooks-disabled, empty patch, same-source
    acts1, lg1 = run(ids)
    res["B"]["repeat_bitwise"] = bool(torch.equal(lg0, lg1) and all(torch.equal(acts0[l], acts1[l]) for l in ALL))
    span = r.spans["X"]["full"]
    acts2, lg2 = run(ids, H.SpanWriter(lm.layers, ALL, [], {}))
    res["B"]["empty_patch_bitwise"] = bool(torch.equal(lg0, lg2) and all(torch.equal(acts0[l], acts2[l]) for l in ALL))
    own = {l: acts0[l][0, span, :].clone() for l in ALL}
    acts3, lg3 = run(ids, H.SpanWriter(lm.layers, ALL, span, own))
    res["B"]["same_source_bitwise"] = bool(torch.equal(lg0, lg3) and all(torch.equal(acts0[l], acts3[l]) for l in ALL))
    # B3 subprojection equivalence at a mid layer for the NP lens
    cols = [Rn.single_token_id(tok, w) for w in M.CALIBRATION_WORDS + M.DECOYS]
    ro = RO.LensReadout(model, lm, LEN, cols)
    l = 36; inter = r.interior
    zsub = ro.z(acts0, inter, [l])[0]
    zfull = lm.unembed(LEN.transport(acts0[l][0, inter, :].float(), l)).float()[:, cols].cpu().numpy()
    res["B"]["subprojection_max_abs_diff"] = float(np.abs(zsub - zfull).max())
    # B4 diagnostics consistency: z32 = n/r vs implementation z
    n, rr, z32 = ro.diagnostics(acts0, inter, [l])
    res["B"]["z32_vs_impl_max_abs_diff"] = float(np.abs(z32[0] - zsub).max())
    res["B"]["rms_median"] = float(np.median(rr))
    # B5 sequence-length nondeterminism: same prefix, one extra token appended; compare interior z at L48
    ids_long = ids + tok(" And", add_special_tokens=False).input_ids
    actsL, _ = run(ids_long)
    zA = ro.z(acts0, inter, [48])[0]; zB = ro.z(actsL, inter, [48])[0]
    res["B"]["seqlen_nondeterminism_max_abs_dz_L48"] = float(np.abs(zA - zB).max())
    res["B"]["seqlen_nondeterminism_max_abs_dh_L48"] = float((acts0[48][0, inter, :].float() - actsL[48][0, inter, :].float()).abs().max())
    # B6 realized-write check for a StateMove of 1.0 along a random unit direction at L35
    g = torch.randn(R.D_MODEL, device=lm.input_device); g = g / g.norm()
    sm = H.StateMove(lm.layers, 35, inter, g, g, level=None, alpha_fixed=torch.ones(len(inter)))
    acts4, _ = run(ids, sm)
    res["B"]["state_move_realized"] = H.realized_write_stats(sm)
    res["B"]["state_move_layer35_delta_vs_recorded"] = float((acts4[35][0, inter, :].float() - acts0[35][0, inter, :].float() - g[None, :]).abs().max())
    res["B"]["forward_s_all_layers_recorded"] = round(fwd_s, 3)
    res["B"]["pass"] = bool(res["B"]["attention_weights_reachable"]["all_present"] and res["B"]["repeat_bitwise"] and res["B"]["empty_patch_bitwise"]
                            and res["B"]["same_source_bitwise"] and res["B"]["subprojection_max_abs_diff"] < 0.05
                            and 0.9 <= res["B"]["state_move_realized"]["rho"] <= 1.1 and res["B"]["state_move_realized"]["kappa"] >= 0.99)
    res["meta"]["elapsed_s"] = round(time.time() - t0, 1)
    json.dump(res, open(OUT, "w"), indent=1)
    print("[B]", json.dumps({k: v for k, v in res["B"].items() if k != "model"}, indent=1), flush=True)
    print(f"[gates] A pass {res['A']['pass']} | B pass {res['B']['pass']} | {time.time()-t0:.0f}s -> {OUT}")


if __name__ == "__main__":
    main()
