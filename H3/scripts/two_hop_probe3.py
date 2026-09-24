"""H3 two_hop_organism stage `probe3` (design: H3/design_specs/two_hop_organism.md, Amendment 8 and its run registration).

(a) q_bothrem_pre: joint removal of the intermediate and answer naming planes on q_pre, with a norm-matched random 4-frame control;
(b) q_J25rem_pre_ccs: the J25 complement on q_pre plus a stronger consumer clamp at the scoring position s pinning the span of the
    four words and their aliases (every single-token form), the 25 pursuit atoms of the donor's delta at s and the translation atoms,
    verified by the readouts at s, with a rank- and norm-matched random control (_ccsr);
(c) relation transfer: a capital item's question-turn delta written into the language question for the same city (q_xfer) and the
    mirror (q_mirror), with native references and norm-matched random controls.
Same-run references (Amendment 6 rows) reproduce Stage 2. Float32 residual from block 35; sequence-log-prob endpoint only.
Stages: smoke3 (one admitted cell + one pair cell, carrier C0) | probe3 (140 admitted cells + 28 pair cells).
Usage: two_hop_probe3.py smoke3|probe3
"""
import os, sys, json, time, hashlib, re
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "..", "common", "scripts"))
STAGE = sys.argv[1] if len(sys.argv) > 1 else "smoke3"; assert STAGE in ("smoke3", "probe3")
_argv = sys.argv; sys.argv = [_argv[0], "stage2"]; import two_hop_qsplit6 as Q; sys.argv = _argv   # shared helpers, the 42-item bank, the frozen alias lists
import numpy as np, torch
import registry as R, materials as M, rendering as Rn, readout as RO, hooks as H
from hooks_fp32 import Fp32Residual

OUT = R.out_dir("H3", "outputs", "two_hop_organism")
RUN_ID = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()); SEED = 20260924; FP32_FROM = 35
CARRIERS = ["C0", "C1", "C2", "C3"]; SWAP_L = list(range(36, 63)); RB = list(range(51, 60)); LZ = list(range(36, 63)); KP = 25
ADMITTED = json.load(open(os.path.join(OUT, "meta_admit.json")))["admitted"]
ITEMS_AB = [it for it in Q.ITEMS if it["name"] in ADMITTED]; assert len(ITEMS_AB) == 35, len(ITEMS_AB)
PAIR_ITEMS = ["ex-city-capital-Lyon-Naples", "ex-city-capital-Naples-Barcelona", "ex2-city-capital-Munich", "ex2-city-capital-Osaka",
              "s2-city-capital-Bergen-Kyoto", "s2-city-capital-Marseille-Aarhus", "s2-city-capital-Salzburg-Kyoto"]
LANG = {"France": "French", "Italy": "Italian", "Spain": "Spanish", "Germany": "German", "Japan": "Japanese", "Norway": "Norwegian", "Denmark": "Danish", "Austria": "German"}
LANG_TEMPLATE = "Fact: The language spoken in the country where {cue} is located is"
CAR_AB, CAR_C = CARRIERS, CARRIERS
if STAGE == "smoke3": ITEMS_AB, CAR_AB, PAIR_ITEMS, CAR_C = [ITEMS_AB[0]], ["C0"], PAIR_ITEMS[:1], ["C0"]
IT = {it["name"]: it for it in Q.ITEMS}
cue_of = lambda p: re.search(r"country where (.+?) is located", p).group(1)
REF_ROWS = ["q_full_pre", "q_rem_pre", "q_ansrem_pre", "q_J25rem_pre", "q_J25rem_pre_cc"]


def unit(v): return v / v.norm()


def main():
    tok = R.make_tokenizer()
    from jlens.hf import from_hf
    model = R.load_model(); lm = from_hf(model, tok, compile=False)
    ALL = list(range(R.N_BLOCKS)); run = H.make_run(model, lm, ALL); dev = lm.input_device
    LEN = R.load_lenses(("J_NP",))["J_NP"]
    render = lambda prompt, car: Rn.render(tok, Q.utext(Q.clue_body(prompt), car), car, sources=[("CLUE", Q.clue_body(prompt), False)], extra_turns=[(Q.QUESTION, "")])

    # ---------------------------------------------------------------- words, columns, directions
    words = set()
    for it in ITEMS_AB: words |= {it[k] for k in ("intermediate", "swap_to", "answer", "swap_answer")}
    pairs = []
    for nm in PAIR_ITEMS:
        it = IT[nm]; p = {"name": nm, "it": it, "A": cue_of(it["prompt"]), "B": cue_of(it["donor_prompt"]), "own_country": it["intermediate"], "donor_country": it["swap_to"],
                          "own_cap": it["answer"], "donor_cap": it["swap_answer"], "own_lang": LANG[it["intermediate"]], "donor_lang": LANG[it["swap_to"]]}
        pairs.append(p); words |= {p[k] for k in ("own_country", "donor_country", "own_cap", "donor_cap", "own_lang", "donor_lang")}
    decoys = [w for w in Q.DECOYS if w not in words]; COLS = sorted(words) + decoys
    TID = {w: Rn.single_token_id(tok, w) for w in COLS}; assert all(v is not None for v in TID.values()), TID
    ro = RO.LensReadout(model, lm, LEN, [TID[w] for w in COLS])
    gamma = ro.gamma.to(dev); WU = ro.Wu; d = WU.shape[1]; V = len(tok)
    NAMING = {w: {l: ro.folded_direction(l, TID[w]) for l in SWAP_L} for w in words}
    NAMING63 = {w: unit(WU[TID[w]].float() * gamma) for w in words}
    fp = lambda: Fp32Residual(lm.layers, FP32_FROM)
    zc_ab = lambda it: [COLS.index(w) for w in (it["intermediate"], it["swap_to"], it["answer"], it["swap_answer"])] + [COLS.index(x) for x in decoys]
    zc_c = lambda p: [COLS.index(p[k]) for k in ("own_country", "donor_country", "own_lang", "donor_lang", "own_cap", "donor_cap")] + [COLS.index(x) for x in decoys]

    def build_dict(l):
        J = LEN.jacobians[l].to(dev).float(); out = torch.empty(WU.shape[0], d, dtype=torch.float16, device=dev)
        for a in range(0, WU.shape[0], 32768):
            blk = (WU[a:a + 32768].float() * gamma) @ J; out[a:a + 32768] = (blk / blk.norm(dim=1, keepdim=True).clamp_min(1e-12)).half(); del blk
        return out

    def atom_dirs(l, ids):
        J = LEN.jacobians[l].to(dev).float(); a = (WU[torch.as_tensor(np.asarray(ids, dtype=np.int64), device=dev)].float() * gamma) @ J
        return (a / a.norm(dim=1, keepdim=True).clamp_min(1e-12)).half().float()

    def seqscore(ids, mk, cands):
        vals, first = [], None
        for sp in cands:
            full = ids + list(sp); a_, lg = run(full, mk())
            lp = torch.log_softmax(lg[0, len(ids) - 1: len(full) - 1].float(), -1)
            vals.append(float(sum(lp[k, sp[k]] for k in range(len(sp)))))
            if first is None: first = (a_, lg)
            else: del a_
        return float(torch.logsumexp(torch.tensor(vals), 0)), vals, first

    # ---------------------------------------------------------------- translation atoms (tokenizer + W_U only)
    t0 = time.time()
    dec = [tok.decode([i]) for i in range(V)]; latin = torch.tensor([bool(re.search(r"[A-Za-z]", s)) for s in dec])
    Wn = torch.empty(V, d, dtype=torch.float16, device=dev)
    for a in range(0, V, 32768): w_ = WU[a:min(a + 32768, V)].float(); Wn[a:a + len(w_)] = (w_ / w_.norm(dim=1, keepdim=True).clamp_min(1e-6)).half()
    lat_idx = latin.nonzero()[:, 0].to(dev); non_idx = (~latin).nonzero()[:, 0].to(dev); WL = Wn[lat_idx]; nn = torch.empty(len(non_idx), dtype=torch.long, device=dev)
    for a in range(0, len(non_idx), 8192): nn[a:a + 8192] = lat_idx[(Wn[non_idx[a:a + 8192]] @ WL.T).argmax(1)]
    nnword = [dec[j].strip().lower() for j in nn.tolist()]; non_list = non_idx.tolist(); del Wn, WL; torch.cuda.empty_cache()
    alias = lambda w: {w.lower()} | set(Q.ANS_ALIASES.get(w, [])) | set(Q.INT_ALIASES.get(w, []))

    def forms_all(w):
        ids = []
        for a in sorted(alias(w)):
            for f in (a.lower(), a.capitalize(), " " + a.lower(), " " + a.capitalize()):
                t = tok(f, add_special_tokens=False).input_ids
                if len(t) == 1 and t[0] not in ids: ids.append(t[0])
        return ids

    def translation_ids(it):
        S = set().union(*[alias(it[k]) for k in ("intermediate", "swap_to", "answer", "swap_answer")])
        return [non_list[i] for i, w in enumerate(nnword) if w in S]
    print(f"  [X] translation-atom pass: {len(non_list)} non-Latin entries, {time.time()-t0:.0f}s", flush=True)

    RAW, RAWZ = {}, {}
    META = {"stage": STAGE, "design": "H3/design_specs/two_hop_organism.md (Amendment 8, run registration)", "columns": COLS, "decoys": decoys, "carriers_ab": CAR_AB, "carriers_c": CAR_C,
            "swap_layers": [SWAP_L[0], SWAP_L[-1]], "readout_band": [RB[0], RB[-1]], "zq_layers": [LZ[0], LZ[-1]], "fp32_from": FP32_FROM, "seed": SEED, "k_pursuit": KP,
            "items_ab": [it["name"] for it in ITEMS_AB], "pairs": [{k: v for k, v in p.items() if k != "it"} for p in pairs], "question": Q.QUESTION, "language_template": LANG_TEMPLATE,
            "seeds": {"rand4": "SEED + 300000 + cell", "ccsr": "SEED + 350000 + cell", "xfer_rand": "SEED + 400000 + pair cell", "mirror_rand": "SEED + 450000 + pair cell"},
            "cells_ab": {}, "cells_c": {}, "clamp_sets": {}}
    n = 0; t0 = time.time()

    # ---------------------------------------------------------------- Phase A (rows a, b): clean and donor forwards
    cellinfo = {}
    for it in ITEMS_AB:
        for ck in CAR_AB:
            car = M.CARRIERS[ck]; b = f"{it['name']}|{ck}"
            r = render(it["prompt"], car); rd = render(it["donor_prompt"], car)
            assert len(rd) == len(r) and rd.spans["CLUE"]["full"] == r.spans["CLUE"]["full"] and rd.meta["carrier_start"] == r.meta["carrier_start"] and rd.meta["carrier_end"] == r.meta["carrier_end"], f"geometry {b}"
            cs, ce = r.meta["carrier_start"], r.meta["carrier_end"]; Qp_ = list(range(ce, len(r))); qpre = Qp_[:-1]; s = Qp_[-1]
            assert s == len(r) - 1 == r.spans["answer"] and list(r.ids[Qp_[0]:]) == list(rd.ids[Qp_[0]:]), f"q-turn {b}"
            ids = list(r.ids); cA, cB = Q.spellings(tok, it["answer"]), Q.spellings(tok, it["swap_answer"])
            sA, _, (ac, lg) = seqscore(ids, fp, cA); sB, _, _ = seqscore(ids, fp, cB); dA, _, (ad, lgd) = seqscore(list(rd.ids), fp, cA); dB, _, _ = seqscore(list(rd.ids), fp, cB); n += 2 * (len(cA) + len(cB))
            RAW[f"{b}|clean|seq_answer"], RAW[f"{b}|clean|seq_swap"], RAW[f"{b}|donor|seq_answer"], RAW[f"{b}|donor|seq_swap"] = map(np.float32, (sA, sB, dA, dB))
            for tag, acts, lgx in ((f"{b}|clean", ac, lg), (f"{b}|donor", ad, lgd)):
                RAWZ[f"{tag}|zq"] = ro.z(acts, Qp_, LZ)[:, :, zc_ab(it)].astype(np.float16); RAW[f"{tag}|greedy"] = tok.decode(int(lgx[0, len(ids) - 1].argmax())).strip()
                for pr, (w1, w2) in (("int", (it["intermediate"], it["swap_to"])), ("ans", (it["answer"], it["swap_answer"]))):
                    RAW[f"{tag}|c63s_{pr}"] = (acts[63][0, s, :].float() @ torch.stack([NAMING63[w1], NAMING63[w2]], 1)).cpu().numpy().astype(np.float32)
            cellinfo[b] = {"it": it, "ids": ids, "cA": cA, "cB": cB, "Q": Qp_, "qpre": qpre, "s": s, "cs": cs, "ce": ce,
                           "hq": {l: ac[l][0, Qp_, :].float().cpu().clone() for l in SWAP_L}, "hqY": {l: ad[l][0, Qp_, :].float().cpu().clone() for l in SWAP_L}}
            META["cells_ab"][b] = {"intermediate": it["intermediate"], "swap_to": it["swap_to"], "answer": it["answer"], "swap_answer": it["swap_answer"], "category": it.get("category"),
                                   "q": [Qp_[0], Qp_[-1]], "scoring": s, "n_tokens": len(r), "zq_columns": [COLS[i] for i in zc_ab(it)]}
            del ac, ad, lg, lgd
        print(f"  [A] {it['name']}: {n} forwards ({time.time()-t0:.0f}s)", flush=True)
    bases = list(cellinfo); nq = len(cellinfo[bases[0]]["qpre"]); assert all(len(cellinfo[b]["qpre"]) == nq for b in bases)
    META["competence_ab"] = {"clean": float(np.mean([RAW[f"{b}|clean|seq_answer"] > RAW[f"{b}|clean|seq_swap"] for b in bases])), "donor": float(np.mean([RAW[f"{b}|donor|seq_swap"] > RAW[f"{b}|donor|seq_answer"] for b in bases]))}
    print(f"  [gate 2 ab] competence {META['competence_ab']}", flush=True)

    # ---------------------------------------------------------------- Phase B: the full-dictionary pursuit to k = 25 (q_pre vectors, then the s vectors)
    PUR = {}
    for l in SWAP_L:
        Xq = torch.stack([cellinfo[b]["hqY"][l][:-1] - cellinfo[b]["hq"][l][:-1] for b in bases]).reshape(-1, d); Xs = torch.stack([cellinfo[b]["hqY"][l][-1] - cellinfo[b]["hq"][l][-1] for b in bases])
        X = torch.cat([Xq, Xs], 0).to(dev); D = build_dict(l); sel, stop, coefs = Q.pursuit_ls(D, X, KP, [KP]); del D, X; torch.cuda.empty_cache()
        PUR[l] = {"sel": sel.cpu().numpy().astype(np.int32), "stop": stop.cpu().numpy().astype(np.int32), "coef": coefs[KP].cpu().numpy().astype(np.float32)}
    P2 = np.load(os.path.join(OUT, "raw_pursuit_stage2.npz"), allow_pickle=True); b2 = list(P2["bases"]); nq2 = int(P2["n_qpre"]); agq, ags = [], []
    for l in SWAP_L:
        s2 = P2[f"L{l}|sel"]
        for bi, b in enumerate(bases):
            j = b2.index(b); agq.append(float((PUR[l]["sel"][bi * nq:(bi + 1) * nq, :KP] == s2[j * nq2:(j + 1) * nq2, :KP]).all(1).mean())); ags.append(bool((PUR[l]["sel"][len(bases) * nq + bi, :KP] == s2[len(b2) * nq2 + j, :KP]).all()))
    META["pursuit_agreement_with_stage2"] = {"qpre_vectors_identical_first25": float(np.mean(agq)), "s_vectors_identical_first25": float(np.mean(ags))}
    PR = {"bases": np.array(bases), "n_qpre": np.int32(nq)}
    for l in SWAP_L: PR[f"L{l}|sel"], PR[f"L{l}|stop"], PR[f"L{l}|coef{KP}"] = PUR[l]["sel"], PUR[l]["stop"], PUR[l]["coef"]
    np.savez_compressed(os.path.join(OUT, f"raw_pursuit_{STAGE}.npz"), **PR)
    print(f"  [B] pursuit to k = {KP} done ({time.time()-t0:.0f}s); agreement with Stage 2 selections {META['pursuit_agreement_with_stage2']}", flush=True)

    # ---------------------------------------------------------------- Phase C (rows a, b)
    def record(tag, b, acts, logits, info, it):
        L = len(info["ids"]); RAW[f"{tag}|greedy"] = tok.decode(int(logits[0, L - 1].argmax())).strip()
        RAWZ[f"{tag}|zq"] = ro.z(acts, info["Q"], LZ)[:, :, zc_ab(it)].astype(np.float16)
        for pr, (w1, w2) in (("int", (it["intermediate"], it["swap_to"])), ("ans", (it["answer"], it["swap_answer"]))):
            RAW[f"{tag}|c63s_{pr}"] = (acts[63][0, info["s"], :].float() @ torch.stack([NAMING63[w1], NAMING63[w2]], 1)).cpu().numpy().astype(np.float32)

    ROWS_AB = None
    for bi, b in enumerate(bases):
        info = cellinfo[b]; it = info["it"]; ids, cA, cB, qpre, s, Qp_ = info["ids"], info["cA"], info["cB"], info["qpre"], info["s"], info["Q"]; tc = time.time()
        sA0, _, (ac, _lg) = seqscore(ids, fp, cA); n += len(cA)
        assert all(torch.equal(ac[l][0, Qp_, :].float().cpu(), info["hq"][l]) for l in SWAP_L) and abs(sA0 - float(RAW[f"{b}|clean|seq_answer"])) < 1e-6, f"Phase A/C determinism {b}"
        q0 = bi * nq; si = len(bases) * nq + bi
        g4 = torch.Generator().manual_seed(SEED + 300000 + bi); gr = torch.Generator().manual_seed(SEED + 350000 + bi)
        Fids = sorted(set(sum([forms_all(it[k]) for k in ("intermediate", "swap_to", "answer", "swap_answer")], []))); Xids = translation_ids(it)
        T = {k: {} for k in ("q_full_pre", "q_rem_pre", "q_ansrem_pre", "q_bothrem_pre", "q_rand4rem_pre", "q_J25rem_pre")}; PIN_cc, PIN_ccs, PIN_ccsr, rank, cos4 = {}, {}, {}, {}, {}
        for l in SWAP_L:
            h = info["hq"][l][:-1].to(dev); hY = info["hqY"][l][:-1].to(dev); dh = hY - h
            a_i, a_t, a_a, a_b = (NAMING[it[k]][l].float() for k in ("intermediate", "swap_to", "answer", "swap_answer"))
            Qp = torch.linalg.qr(torch.stack([a_i, a_t], 1))[0]; Qa = torch.linalg.qr(torch.stack([a_a, a_b], 1))[0]; Q4 = torch.linalg.qr(torch.stack([a_i, a_t, a_a, a_b], 1))[0]
            cos4[l] = [float(a_i @ a_a), float(a_t @ a_b)]
            v4 = (dh @ Q4) @ Q4.T; R4 = Q.random_frame(d, 4, g4, dev); vR4 = (dh @ R4) @ R4.T; vR4 = vR4 * (v4.norm(dim=1, keepdim=True) / vR4.norm(dim=1, keepdim=True).clamp_min(1e-12))
            assert torch.allclose(vR4.norm(dim=1), v4.norm(dim=1), rtol=1e-4, atol=1e-6), f"rand4 norm match {b} {l}"
            T["q_full_pre"][l] = hY.clone(); T["q_rem_pre"][l] = h + dh - (dh @ Qp) @ Qp.T; T["q_ansrem_pre"][l] = h + dh - (dh @ Qa) @ Qa.T
            T["q_bothrem_pre"][l] = h + dh - v4; T["q_rand4rem_pre"][l] = h + dh - vR4
            sel = PUR[l]["sel"][q0:q0 + nq, :KP]; c = torch.as_tensor(PUR[l]["coef"][q0:q0 + nq], device=dev)
            A25 = atom_dirs(l, sel.reshape(-1)).reshape(nq, KP, d); T["q_J25rem_pre"][l] = h + dh - torch.einsum("nk,nkd->nd", c, A25); del A25
            ks = min(KP, max(int(PUR[l]["stop"][si]), 1)); Ps = atom_dirs(l, PUR[l]["sel"][si, :ks]); PIN_cc[l] = torch.linalg.qr(Ps.T)[0]
            Mx = torch.cat([atom_dirs(l, Fids), Ps] + ([atom_dirs(l, Xids)] if Xids else []), 0).T
            Us, Ss, _ = torch.linalg.svd(Mx, full_matrices=False); U = Us[:, Ss > 1e-3 * Ss[0]]; PIN_ccs[l] = U; rank[l] = int(U.shape[1])
            PIN_ccsr[l] = Q.orth_against(Q.random_frame(d, rank[l], gr, dev), U)
        META["clamp_sets"][it["name"]] = {"F": len(Fids), "X": len(Xids), "X_examples": [dec[x] for x in Xids[:24]], "rank_min": min(rank.values()), "rank_max": max(rank.values()),
                                          "cos_int_ans_folded_L51_59": float(np.mean([cos4[l][0] for l in RB])), "cos_swap_swapans_folded_L51_59": float(np.mean([cos4[l][1] for l in RB]))}
        hclean_s = {l: info["hq"][l][-1] for l in SWAP_L}; CCT = {}
        conds = {k: (lambda k=k: H.Both(fp(), H.SpanWriter(lm.layers, SWAP_L, qpre, T[k]))) for k in T}
        conds["q_J25rem_pre_cc"] = lambda: H.Both(fp(), H.SpanWriter(lm.layers, SWAP_L, qpre, T["q_J25rem_pre"]), Q.SubspaceClampMatched(lm.layers, SWAP_L, s, PIN_cc, hclean_s))
        conds["q_J25rem_pre_ccs"] = lambda: H.Both(fp(), H.SpanWriter(lm.layers, SWAP_L, qpre, T["q_J25rem_pre"]), Q.SubspaceClampMatched(lm.layers, SWAP_L, s, PIN_ccs, hclean_s))
        conds["q_J25rem_pre_ccsr"] = lambda: H.Both(fp(), H.SpanWriter(lm.layers, SWAP_L, qpre, T["q_J25rem_pre"]), Q.SubspaceClampMatched(lm.layers, SWAP_L, s, PIN_ccsr, hclean_s, target=CCT))
        ROWS_AB = list(conds)
        for cond, mk in conds.items():
            ctx = mk(); sA, vA, (a_, l_) = seqscore(ids, lambda: ctx, cA); sB, vB, _ = seqscore(ids, lambda: ctx, cB); n += len(cA) + len(cB); tag = f"{b}|{cond}"
            RAW[f"{tag}|seq_answer"], RAW[f"{tag}|seq_swap"] = np.float32(sA), np.float32(sB); RAW[f"{tag}|seq_answer_all"], RAW[f"{tag}|seq_swap_all"] = np.array(vA, np.float32), np.array(vB, np.float32)
            assert all(torch.equal(a_[l][0, :qpre[0], :], ac[l][0, :qpre[0], :]) for l in ALL), f"prefix touched {tag}"
            tgt = T[cond] if cond in T else T["q_J25rem_pre"]
            req = torch.stack([(tgt[l] - ac[l][0, qpre, :].float()).flatten() for l in SWAP_L]); real = torch.stack([(a_[l][0, qpre, :].float() - ac[l][0, qpre, :].float()).flatten() for l in SWAP_L])
            nr, nq_ = real.norm(dim=1), req.norm(dim=1); ok = nq_ > 1e-8
            RAW[f"{tag}|rho"] = np.float32(float((nr[ok] / nq_[ok]).mean())); RAW[f"{tag}|kappa"] = np.float32(float(torch.nn.functional.cosine_similarity(real[ok], req[ok], dim=1).mean()))
            RAW[f"{tag}|rberr"] = np.float32(max(float((a_[l][0, qpre, :].float() - tgt[l]).abs().max()) for l in SWAP_L))
            if cond.endswith("_cc") or cond.endswith("_ccs") or cond.endswith("_ccsr"):
                cl = [x for x in ctx.c if isinstance(x, Q.SubspaceClampMatched)][0]
                RAW[f"{tag}|clamp_req"] = np.array([cl.post[l]["req"] for l in SWAP_L], np.float32); RAW[f"{tag}|clamp_real"] = np.array([cl.post[l]["real"] for l in SWAP_L], np.float32)
                RAW[f"{tag}|clamp_kappa"] = np.array([cl.post[l]["kappa"] for l in SWAP_L], np.float32); RAW[f"{tag}|clamp_dim"] = np.array([cl.U[l].shape[1] for l in SWAP_L], np.int32)
                if cond.endswith("_ccs"): CCT.update({l: cl.post[l]["real"] for l in SWAP_L})
            record(tag, b, a_, l_, info, it); del a_, ctx
        z = lambda c: RAWZ[f"{b}|{c}|zq"].astype(np.float32)[RB[0] - LZ[0]: RB[-1] + 1 - LZ[0], -1, :]   # [9 blocks (L51-59), cols] at s
        zs = {c: z(c) for c in ("clean", "q_J25rem_pre", "q_J25rem_pre_ccs")}; sh = lambda c, i, j: float((zs[c][:, j] - zs[c][:, i]).mean() - (zs["clean"][:, j] - zs["clean"][:, i]).mean())
        del ac; torch.cuda.empty_cache()
        print(f"  [C] {b}: {n} forwards ({time.time()-tc:.0f}s cell, {time.time()-t0:.0f}s total) | |F| {len(Fids)} |X| {len(Xids)} rank {min(rank.values())}-{max(rank.values())} | readout at s int/ans: "
              f"J25rem {sh('q_J25rem_pre', 0, 1):+.2f}/{sh('q_J25rem_pre', 2, 3):+.2f} -> ccs {sh('q_J25rem_pre_ccs', 0, 1):+.2f}/{sh('q_J25rem_pre_ccs', 2, 3):+.2f}", flush=True)

    # ---------------------------------------------------------------- rows c: relation transfer and mirror
    ROWS_C = None
    for pi, p in enumerate(pairs):
        for ck in CAR_C:
            car = M.CARRIERS[ck]; b = f"{p['name']}|{ck}"; ci_ = pi * len(CAR_C) + CAR_C.index(ck); tc = time.time()
            rc = {"A": render(p["it"]["prompt"], car), "B": render(p["it"]["donor_prompt"], car)}; rl = {"A": render(LANG_TEMPLATE.format(cue=p["A"]), car), "B": render(LANG_TEMPLATE.format(cue=p["B"]), car)}
            for rr in (rc, rl):
                assert len(rr["A"]) == len(rr["B"]) and rr["A"].spans["CLUE"]["full"] == rr["B"].spans["CLUE"]["full"] and rr["A"].meta["carrier_end"] == rr["B"].meta["carrier_end"], f"geometry {b}"
            qt = [list(x.ids[x.meta["carrier_end"]:]) for x in (rc["A"], rc["B"], rl["A"], rl["B"])]; assert all(q == qt[0] for q in qt), f"q-turn ids {b}"
            SP = {k: Q.spellings(tok, p[k]) for k in ("own_lang", "donor_lang", "own_cap", "donor_cap")}

            def score4(ids, mk):
                out, first = {}, None
                for k in SP:
                    v, _, fr = seqscore(ids, mk, SP[k]); out[k] = v
                    if first is None: first = fr
                    else: del fr
                return out, first
            st, geo = {}, {}
            for tmpl, rr in (("cap", rc), ("lang", rl)):
                ce = rr["A"].meta["carrier_end"]; Qp_ = list(range(ce, len(rr["A"]))); geo[tmpl] = {"Q": Qp_, "qpre": Qp_[:-1], "s": Qp_[-1], "ids": list(rr["A"].ids)}
                for side in ("A", "B"):
                    sc, (acts, lgx) = score4(list(rr[side].ids), fp); n += sum(len(v) for v in SP.values()); tag = f"{b}|{tmpl}_{'clean' if side == 'A' else 'donor'}"
                    for k, v in sc.items(): RAW[f"{tag}|{k}"] = np.float32(v)
                    RAWZ[f"{tag}|zq"] = ro.z(acts, Qp_, LZ)[:, :, zc_c(p)].astype(np.float16); RAW[f"{tag}|greedy"] = tok.decode(int(lgx[0, len(rr[side].ids) - 1].argmax())).strip()
                    st[(tmpl, side)] = {l: acts[l][0, Qp_[:-1], :].float().clone() for l in SWAP_L}
                    if side == "A": st[(tmpl, "acts")] = acts
                    else: del acts
            dcap = {l: st[("cap", "B")][l] - st[("cap", "A")][l] for l in SWAP_L}; dlang = {l: st[("lang", "B")][l] - st[("lang", "A")][l] for l in SWAP_L}
            g1 = torch.Generator().manual_seed(SEED + 400000 + ci_); g2 = torch.Generator().manual_seed(SEED + 450000 + ci_)

            def randlike(dh, g):
                r_ = torch.randn(dh.shape[0], dh.shape[1], generator=g).to(dh.device); r_ = r_ / r_.norm(dim=1, keepdim=True) * dh.norm(dim=1, keepdim=True)
                assert torch.allclose(r_.norm(dim=1), dh.norm(dim=1), rtol=1e-4, atol=1e-6); return r_
            rcap = {l: randlike(dcap[l], g1) for l in SWAP_L}; rlang = {l: randlike(dlang[l], g2) for l in SWAP_L}
            rowspec = {"q_xfer": ("lang", dcap), "q_native_lang": ("lang", dlang), "q_xfer_rand": ("lang", rcap),
                       "q_mirror": ("cap", dlang), "q_native_cap": ("cap", dcap), "q_mirror_rand": ("cap", rlang)}
            ROWS_C = list(rowspec)
            for cond, (tmpl, delta) in rowspec.items():
                g_ = geo[tmpl]; base = st[(tmpl, "A")]; Tt = {l: base[l] + delta[l] for l in SWAP_L}; clean_acts = st[(tmpl, "acts")]
                mk = lambda Tt=Tt, g_=g_: H.Both(fp(), H.SpanWriter(lm.layers, SWAP_L, g_["qpre"], Tt))
                sc, (a_, l_) = score4(g_["ids"], mk); n += sum(len(v) for v in SP.values()); tag = f"{b}|{cond}"
                for k, v in sc.items(): RAW[f"{tag}|{k}"] = np.float32(v)
                assert all(torch.equal(a_[l][0, :g_["qpre"][0], :], clean_acts[l][0, :g_["qpre"][0], :]) for l in ALL), f"prefix touched {tag}"
                req = torch.stack([(Tt[l] - base[l]).flatten() for l in SWAP_L]); real = torch.stack([(a_[l][0, g_["qpre"], :].float() - base[l]).flatten() for l in SWAP_L])
                RAW[f"{tag}|rho"] = np.float32(float((real.norm(dim=1) / req.norm(dim=1).clamp_min(1e-8)).mean())); RAW[f"{tag}|kappa"] = np.float32(float(torch.nn.functional.cosine_similarity(real, req, dim=1).mean()))
                RAW[f"{tag}|rberr"] = np.float32(max(float((a_[l][0, g_["qpre"], :].float() - Tt[l]).abs().max()) for l in SWAP_L))
                RAWZ[f"{tag}|zq"] = ro.z(a_, g_["Q"], LZ)[:, :, zc_c(p)].astype(np.float16); RAW[f"{tag}|greedy"] = tok.decode(int(l_[0, len(g_["ids"]) - 1].argmax())).strip(); del a_
            META["cells_c"][b] = {**{k: v for k, v in p.items() if k != "it"}, "n_tokens_cap": len(rc["A"]), "n_tokens_lang": len(rl["A"]), "zq_columns": [COLS[i] for i in zc_c(p)]}
            del st; torch.cuda.empty_cache()
            m = lambda c, tm: float((RAW[f"{b}|{c}|donor_{tm}"] - RAW[f"{b}|{c}|own_{tm}"]) - (RAW[f"{b}|{'lang' if c in ('q_xfer', 'q_native_lang', 'q_xfer_rand') else 'cap'}_clean|donor_{tm}"] - RAW[f"{b}|{'lang' if c in ('q_xfer', 'q_native_lang', 'q_xfer_rand') else 'cap'}_clean|own_{tm}"]))
            print(f"  [X] {b}: {n} forwards ({time.time()-tc:.0f}s) | language question: m_lang xfer {m('q_xfer', 'lang'):+.2f} native {m('q_native_lang', 'lang'):+.2f} rand {m('q_xfer_rand', 'lang'):+.2f}; m_cap xfer {m('q_xfer', 'cap'):+.2f} | "
                  f"capital question: m_cap mirror {m('q_mirror', 'cap'):+.2f} native {m('q_native_cap', 'cap'):+.2f} rand {m('q_mirror_rand', 'cap'):+.2f}; m_lang mirror {m('q_mirror', 'lang'):+.2f}", flush=True)
    bc = list(META["cells_c"])
    META["competence_c"] = {"cap_clean": float(np.mean([RAW[f"{b}|cap_clean|own_cap"] > RAW[f"{b}|cap_clean|donor_cap"] for b in bc])), "cap_donor": float(np.mean([RAW[f"{b}|cap_donor|donor_cap"] > RAW[f"{b}|cap_donor|own_cap"] for b in bc])),
                            "lang_clean": float(np.mean([RAW[f"{b}|lang_clean|own_lang"] > RAW[f"{b}|lang_clean|donor_lang"] for b in bc])), "lang_donor": float(np.mean([RAW[f"{b}|lang_donor|donor_lang"] > RAW[f"{b}|lang_donor|own_lang"] for b in bc]))}

    META.update({"run_id": RUN_ID, "n_forwards": n, "elapsed_s": round(time.time() - t0, 1), "rows_ab": ROWS_AB, "rows_c": ROWS_C, "n_qpre": nq})
    np.savez_compressed(os.path.join(OUT, f"raw_{STAGE}.npz"), **RAW); np.savez_compressed(os.path.join(OUT, f"raw_{STAGE}_zq.npz"), **RAWZ)
    json.dump(META, open(os.path.join(OUT, f"meta_{STAGE}.json"), "w"), indent=1, default=str)
    sha = lambda f: hashlib.sha256(open(os.path.join(OUT, f), "rb").read()).hexdigest()
    man = R.manifest_block(); man.update({"run_id": RUN_ID, "stage": STAGE, "script": os.path.relpath(__file__, R.PROJECT), "design": META["design"],
                                          "raw_sha256": sha(f"raw_{STAGE}.npz"), "raw_zq_sha256": sha(f"raw_{STAGE}_zq.npz"), "raw_pursuit_sha256": sha(f"raw_pursuit_{STAGE}.npz")})
    json.dump(man, open(os.path.join(OUT, f"manifest_{STAGE}.json"), "w"), indent=1)
    print(f"[done {STAGE}] {n} forwards, {time.time()-t0:.0f}s | competence ab {META['competence_ab']} c {META['competence_c']} | pursuit agreement {META['pursuit_agreement_with_stage2']}")


if __name__ == "__main__":
    main()
