"""H3 two_hop_organism stage `probe5` (design: H3/design_specs/two_hop_organism.md, Amendment 10 and its registration notes).
Part B (7 pairs): planes orthogonalised against the receiving question's answer plane. Parts A, C, D, E (35 admitted items x C0-C3):
A the fitted non-lens span Phi at the answer positions (+ baseline J25rem with the block-63 read cut, energy logging, optional Phi');
C the functional-row null (pursuit over J_l^T(gamma*u), u ~ N(0, Cov W_U)); D block-63 read cuts by position class + per-head attribution;
E the delivery-depth curve. Order: B, then A with references, then C/D/E; the raw file is saved after each stage.
Usage: two_hop_probe5.py smoke5|probe5
"""
import os, sys, json, time, hashlib, re
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "..", "common", "scripts"))
STAGE = sys.argv[1] if len(sys.argv) > 1 else "smoke5"; assert STAGE in ("smoke5", "probe5")
_argv = sys.argv; sys.argv = [_argv[0], "stage2"]; import two_hop_qsplit6 as Q
sys.argv = [_argv[0], "smoke4"]; import two_hop_probe4 as P4; sys.argv = _argv
import numpy as np, torch
import registry as R, materials as M, rendering as Rn, readout as RO, hooks as H
from hooks_fp32 import Fp32Residual

OUT = R.out_dir("H3", "outputs", "two_hop_organism"); RUN_ID = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()); SEED = 20260924; FP32_FROM = 35; LAST = 63
CARRIERS = ["C0", "C1", "C2", "C3"]; SWAP_L = list(range(36, 63)); LZ = list(range(36, 63)); KP = 25; DEPTHS = [50, 54, 58]
ADMITTED = json.load(open(os.path.join(OUT, "meta_admit.json")))["admitted"]; ITEMS_AB = [it for it in Q.ITEMS if it["name"] in ADMITTED]; assert len(ITEMS_AB) == 35
PAIR_ITEMS = ["ex-city-capital-Lyon-Naples", "ex-city-capital-Naples-Barcelona", "ex2-city-capital-Munich", "ex2-city-capital-Osaka", "s2-city-capital-Bergen-Kyoto", "s2-city-capital-Marseille-Aarhus", "s2-city-capital-Salzburg-Kyoto"]
LANG = P4.LANG; LANG_TEMPLATE = P4.LANG_TEMPLATE; CAR_AB, CAR_C = CARRIERS, CARRIERS
if STAGE == "smoke5": ITEMS_AB, CAR_AB, PAIR_ITEMS, CAR_C = [ITEMS_AB[0]], ["C0"], PAIR_ITEMS[:1], ["C0"]
IT = {it["name"]: it for it in Q.ITEMS}; cue_of = P4.cue_of
CLS = {"P": list(range(0, 5)), "W": list(range(5, 19)), "T": list(range(19, 27))}


class HeadCapture:
    """Block-63 capture at position s: the gated per-head attention output (pre-hook on o_proj) and the attention weights of s."""
    def __init__(self, block, s): self.b, self.s, self._h, self.x, self.w = block, int(s), [], None, None
    def __enter__(self):
        att = self.b.self_attn
        self._h.append(att.o_proj.register_forward_pre_hook(lambda m, a: setattr(self, "x", a[0][0, self.s, :].detach().float().clone())))
        self._h.append(att.register_forward_hook(lambda m, i, o: setattr(self, "w", o[1][0, :, self.s, :].detach().float().clone() if o[1] is not None else None)))
        return self
    def __exit__(self, *a): [x.remove() for x in self._h]


def main():
    tok = R.make_tokenizer()
    from jlens.hf import from_hf
    model = R.load_model(); lm = from_hf(model, tok, compile=False); ALL = list(range(R.N_BLOCKS)); run = H.make_run(model, lm, ALL); dev = lm.input_device
    LEN = R.load_lenses(("J_NP",))["J_NP"]; t0 = time.time(); n = 0
    render = lambda prompt, car: Rn.render(tok, Q.utext(Q.clue_body(prompt), car), car, sources=[("CLUE", Q.clue_body(prompt), False)], extra_turns=[(Q.QUESTION, "")])
    words = set()
    for it in ITEMS_AB: words |= {it[k] for k in ("intermediate", "swap_to", "answer", "swap_answer")}
    pairs = []
    for nm in PAIR_ITEMS:
        it = IT[nm]; p = {"name": nm, "it": it, "A": cue_of(it["prompt"]), "B": cue_of(it["donor_prompt"]), "own_country": it["intermediate"], "donor_country": it["swap_to"], "own_cap": it["answer"],
                          "donor_cap": it["swap_answer"], "own_lang": LANG[it["intermediate"]], "donor_lang": LANG[it["swap_to"]]}
        pairs.append(p); words |= {p[k] for k in ("own_country", "donor_country", "own_cap", "donor_cap", "own_lang", "donor_lang")}
    decoys = [w for w in Q.DECOYS if w not in words]; COLS = sorted(words) + decoys; TID = {w: Rn.single_token_id(tok, w) for w in COLS}; assert all(v is not None for v in TID.values())
    ro = RO.LensReadout(model, lm, LEN, [TID[w] for w in COLS]); gamma = ro.gamma.to(dev); WU = ro.Wu; d = WU.shape[1]; V = len(tok); NW = WU.shape[0]
    NAMING = {w: {l: ro.folded_direction(l, TID[w]) for l in SWAP_L} for w in words}; fp = lambda: Fp32Residual(lm.layers, FP32_FROM)
    zc_ab = lambda it: [COLS.index(w) for w in (it["intermediate"], it["swap_to"], it["answer"], it["swap_answer"])] + [COLS.index(x) for x in decoys]
    zc_c = lambda p: [COLS.index(p[k]) for k in ("own_country", "donor_country", "own_lang", "donor_lang", "own_cap", "donor_cap")] + [COLS.index(x) for x in decoys]
    RAW, RAWZ = {}, {}; META = {"stage": STAGE, "design": "H3/design_specs/two_hop_organism.md (Amendment 10)", "columns": COLS, "decoys": decoys, "carriers_ab": CAR_AB, "carriers_c": CAR_C, "depths": DEPTHS,
                                "items_ab": [it["name"] for it in ITEMS_AB], "pairs": [{k: v for k, v in p.items() if k != "it"} for p in pairs], "classes_qpre": CLS, "seed": SEED, "cells_ab": {}, "cells_c": {}, "leak": {}, "stops": {}}

    def atom_dirs(l, ids):
        J = LEN.jacobians[l].to(dev).float(); a = (WU[torch.as_tensor(np.asarray(ids, dtype=np.int64), device=dev)].float() * gamma) @ J
        return (a / a.norm(dim=1, keepdim=True).clamp_min(1e-12)).half().float()

    def score_word(ids, cands, mk, capture=None):
        vals, firsts, first, ctxs = [], [], None, []
        for j, sp in enumerate(cands):
            full = ids + list(sp); ctx = mk(j, sp); a_, lg = run(full, ctx); ctxs.append(ctx)
            lp = torch.log_softmax(lg[0, len(ids) - 1: len(full) - 1].float(), -1); tl = [float(lp[k, sp[k]]) for k in range(len(sp))]; vals.append(sum(tl)); firsts.append(tl[0])
            if capture is not None: capture[j] = {l: a_[l][0, len(ids) - 1: len(full) - 1, :].float().clone() for l in SWAP_L}
            if first is None: first = (a_, lg)
            else: del a_
        return float(torch.logsumexp(torch.tensor(vals), 0)), vals, firsts, first, ctxs

    def save(tag):
        np.savez_compressed(os.path.join(OUT, f"raw_{STAGE}.npz"), **RAW); np.savez_compressed(os.path.join(OUT, f"raw_{STAGE}_zq.npz"), **RAWZ)
        META.update({"run_id": RUN_ID, "n_forwards": n, "elapsed_s": round(time.time() - t0, 1), "saved_after": tag}); json.dump(META, open(os.path.join(OUT, f"meta_{STAGE}.json"), "w"), indent=1, default=str)
        print(f"  [save] after {tag}: {n} forwards ({time.time()-t0:.0f}s)", flush=True)

    # ============================================================ Part B: orthogonalised planes, 7 pairs
    ROWS_C = ["q_xfer", "x_ctry", "x_lang", "x_ctry_perp", "x_lang_perp", "x_rand2b", "q_mirror", "m_ctry", "m_cap", "m_ctry_perp", "m_cap_perp", "m_rand2b"]; META["rows_c"] = ROWS_C
    for pi, p in enumerate(pairs):
        for ck in CAR_C:
            car = M.CARRIERS[ck]; b = f"{p['name']}|{ck}"; ci_ = pi * len(CAR_C) + CAR_C.index(ck); tc = time.time()
            rc = {"A": render(p["it"]["prompt"], car), "B": render(p["it"]["donor_prompt"], car)}; rl = {"A": render(LANG_TEMPLATE.format(cue=p["A"]), car), "B": render(LANG_TEMPLATE.format(cue=p["B"]), car)}
            for rr in (rc, rl): assert len(rr["A"]) == len(rr["B"]) and rr["A"].meta["carrier_end"] == rr["B"].meta["carrier_end"], f"geometry {b}"
            qt = [list(x.ids[x.meta["carrier_end"]:]) for x in (rc["A"], rc["B"], rl["A"], rl["B"])]; assert all(q == qt[0] for q in qt), f"q-turn ids {b}"
            SP = {k: Q.spellings(tok, p[k]) for k in ("own_lang", "donor_lang", "own_cap", "donor_cap")}

            def score4(ids, mk):
                out, first = {}, None
                for k in SP:
                    v, _, _, fr, _c = score_word(ids, SP[k], lambda j, sp: mk()); out[k] = v
                    if first is None: first = fr
                    else: del fr
                return out, first
            st, geo = {}, {}
            for tmpl, rr in (("cap", rc), ("lang", rl)):
                ce = rr["A"].meta["carrier_end"]; Qp_ = list(range(ce, len(rr["A"]))); geo[tmpl] = {"Q": Qp_, "qpre": Qp_[:-1], "ids": list(rr["A"].ids)}
                for side in ("A", "B"):
                    sc4, (acts, lgx) = score4(list(rr[side].ids), fp); n += sum(len(v) for v in SP.values()); tag = f"{b}|{tmpl}_{'clean' if side == 'A' else 'donor'}"
                    for k, v in sc4.items(): RAW[f"{tag}|{k}"] = np.float32(v)
                    RAWZ[f"{tag}|zq"] = ro.z(acts, Qp_, LZ)[:, :, zc_c(p)].astype(np.float16); st[(tmpl, side)] = {l: acts[l][0, Qp_[:-1], :].float().clone() for l in SWAP_L}
                    if side == "A": st[(tmpl, "acts")] = acts
                    else: del acts
            dcap = {l: st[("cap", "B")][l] - st[("cap", "A")][l] for l in SWAP_L}; dlang = {l: st[("lang", "B")][l] - st[("lang", "A")][l] for l in SWAP_L}
            g1 = torch.Generator().manual_seed(SEED + 650000 + ci_); g2 = torch.Generator().manual_seed(SEED + 700000 + ci_); proj = {}; cos = {"cL": [], "cK": []}
            orth = lambda A_, B_: torch.linalg.qr(A_ - B_ @ (B_.T @ A_))[0]
            for l in SWAP_L:
                qr2 = lambda w1, w2: torch.linalg.qr(torch.stack([NAMING[w1][l], NAMING[w2][l]], 1).float())[0]
                Qc, QL, QK = qr2(p["own_country"], p["donor_country"]), qr2(p["own_lang"], p["donor_lang"]), qr2(p["own_cap"], p["donor_cap"])
                cos["cL"].append(torch.linalg.svdvals(Qc.T @ QL).tolist()); cos["cK"].append(torch.linalg.svdvals(Qc.T @ QK).tolist())
                for nmD, D_, g, Qa in (("cap", dcap, g1, QL), ("lang", dlang, g2, QK)):
                    P = lambda U: (D_[l] @ U) @ U.T; Qcp, Qap = orth(Qc, Qa), orth(Qa, Qc); vcp = P(Qcp); R2 = Q.random_frame(d, 2, g, dev); vr = P(R2); vr = vr * (vcp.norm(dim=1, keepdim=True) / vr.norm(dim=1, keepdim=True).clamp_min(1e-12))
                    proj[(nmD, l)] = {"full": D_[l], "ctry": P(Qc), "ans": P(Qa), "ctry_perp": vcp, "ans_perp": P(Qap), "rand2b": vr}
            rowspec = {"q_xfer": ("lang", "cap", "full"), "x_ctry": ("lang", "cap", "ctry"), "x_lang": ("lang", "cap", "ans"), "x_ctry_perp": ("lang", "cap", "ctry_perp"), "x_lang_perp": ("lang", "cap", "ans_perp"),
                       "x_rand2b": ("lang", "cap", "rand2b"), "q_mirror": ("cap", "lang", "full"), "m_ctry": ("cap", "lang", "ctry"), "m_cap": ("cap", "lang", "ans"), "m_ctry_perp": ("cap", "lang", "ctry_perp"),
                       "m_cap_perp": ("cap", "lang", "ans_perp"), "m_rand2b": ("cap", "lang", "rand2b")}
            for cond, (tmpl, src, part) in rowspec.items():
                g_ = geo[tmpl]; base = st[(tmpl, "A")]; Tt = {l: base[l] + proj[(src, l)][part] for l in SWAP_L}
                sc4, (a_, l_) = score4(g_["ids"], lambda Tt=Tt, g_=g_: H.Both(fp(), H.SpanWriter(lm.layers, SWAP_L, g_["qpre"], Tt))); n += sum(len(v) for v in SP.values()); tag = f"{b}|{cond}"
                for k, v in sc4.items(): RAW[f"{tag}|{k}"] = np.float32(v)
                real = torch.stack([(a_[l][0, g_["qpre"], :].float() - base[l]).flatten() for l in SWAP_L]); req = torch.stack([(Tt[l] - base[l]).flatten() for l in SWAP_L])
                RAW[f"{tag}|rho"] = np.float32(float((real.norm(dim=1) / req.norm(dim=1).clamp_min(1e-8)).mean())); RAW[f"{tag}|kappa"] = np.float32(float(torch.nn.functional.cosine_similarity(real, req, dim=1).mean()))
                RAWZ[f"{tag}|zq"] = ro.z(a_, g_["Q"], LZ)[:, :, zc_c(p)].astype(np.float16); del a_
            META["cells_c"][b] = {**{k: v for k, v in p.items() if k != "it"}, "principal_cos_ctry_lang": cos["cL"], "principal_cos_ctry_cap": cos["cK"], "zq_columns": [COLS[i] for i in zc_c(p)]}
            del st; torch.cuda.empty_cache()
            m = lambda c, tm, bs: float((RAW[f"{b}|{c}|donor_{tm}"] - RAW[f"{b}|{c}|own_{tm}"]) - (RAW[f"{b}|{bs}|donor_{tm}"] - RAW[f"{b}|{bs}|own_{tm}"]))
            print(f"  [B] {b}: {n} fw ({time.time()-tc:.0f}s) | lang q.: xfer {m('q_xfer','lang','lang_clean'):+.2f} ctry {m('x_ctry','lang','lang_clean'):+.2f} lang {m('x_lang','lang','lang_clean'):+.2f} "
                  f"ctry_perp {m('x_ctry_perp','lang','lang_clean'):+.2f} lang_perp {m('x_lang_perp','lang','lang_clean'):+.2f} rand {m('x_rand2b','lang','lang_clean'):+.2f}", flush=True)
    save("part B")

    # ============================================================ Phase A (items): clean/donor, answer-position clean states, covariance samples
    P3 = dict(np.load(os.path.join(OUT, "raw_pursuit_probe3.npz"), allow_pickle=True)); b3 = list(P3["bases"]); nq3 = int(P3["n_qpre"])
    dec = [tok.decode([i]) for i in range(V)]; latin = torch.tensor([bool(re.search(r"[A-Za-z]", s)) for s in dec]); Wn = torch.empty(V, d, dtype=torch.float16, device=dev)
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
    im_end = tok.convert_tokens_to_ids("<|im_end|>")
    bases = [f"{it['name']}|{ck}" for it in ITEMS_AB for ck in CAR_AB]; info = {}; COVS = {l: [] for l in SWAP_L}
    for b in bases:
        it = IT[b.split("|")[0]]; car = M.CARRIERS[b.split("|")[1]]; r = render(it["prompt"], car); rd = render(it["donor_prompt"], car)
        ce = r.meta["carrier_end"]; Qp_ = list(range(ce, len(r))); qpre = Qp_[:-1]; s = Qp_[-1]; ids = list(r.ids); assert len(qpre) == nq3 == 27 and list(rd.ids[ce:]) == ids[ce:]
        assert ids[ce] == im_end and ids[ce + 19] == im_end and tok.decode(ids[ce + 5: ce + 19]).strip() == Q.QUESTION and "user" in tok.decode(ids[ce + 1: ce + 5]), f"position classes {b}"
        SPW = {"answer": Q.spellings(tok, it["answer"]), "swap": Q.spellings(tok, it["swap_answer"])}; CA = {}; sc = {}
        for w in ("answer", "swap"):
            cap = {}; sc[w] = score_word(ids, SPW[w], lambda j, sp: fp(), capture=cap); n += len(SPW[w])
            for j in cap: CA[(w, j)] = cap[j]
        ac = sc["answer"][3][0]; RAW[f"{b}|clean|seq_answer"], RAW[f"{b}|clean|seq_swap"] = np.float32(sc["answer"][0]), np.float32(sc["swap"][0])
        RAW[f"{b}|clean|lpf_answer_all"], RAW[f"{b}|clean|lpf_swap_all"] = np.array(sc["answer"][2], np.float32), np.array(sc["swap"][2], np.float32); RAWZ[f"{b}|clean|zq"] = ro.z(ac, Qp_, LZ)[:, :, zc_ab(it)].astype(np.float16)
        dA = score_word(list(rd.ids), SPW["answer"], lambda j, sp: fp()); dB = score_word(list(rd.ids), SPW["swap"], lambda j, sp: fp()); n += len(SPW["answer"]) + len(SPW["swap"])
        RAW[f"{b}|donor|seq_answer"], RAW[f"{b}|donor|seq_swap"] = np.float32(dA[0]), np.float32(dB[0]); ad = dA[3][0]
        for l in SWAP_L: COVS[l].append(ac[l][0, 4:len(ids), :].half().cpu())
        info[b] = {"it": it, "ids": ids, "SPW": SPW, "CA": CA, "Q": Qp_, "qpre": qpre, "s": s, "j3": b3.index(b), "hq": {l: ac[l][0, Qp_, :].float().cpu() for l in SWAP_L}, "hqY": {l: ad[l][0, Qp_, :].float().cpu() for l in SWAP_L},
                   "hfin": ac[LAST][0, s, :].float().clone(), "tok_first": (SPW["answer"][0][0], SPW["swap"][0][0])}
        META["cells_ab"][b] = {"category": it.get("category"), "scoring": s, "zq_columns": [COLS[i] for i in zc_ab(it)]}; del ac, ad, dA, dB, sc
    print(f"  [A] {len(bases)} cells: {n} fw ({time.time()-t0:.0f}s)", flush=True)

    # ============================================================ Phase B: J25 parts, pinned spans, Phi (Sigma-Gaussian pursuit on dh_s), functional pursuit on q_pre
    nb = len(bases); UJ, UF, CAPS, VJ, VF = {}, {}, {}, {}, {}
    WUc = WU[:NW].float(); mu = WUc.mean(0); CW = torch.zeros(d, d, device=dev)
    for a in range(0, NW, 32768): x_ = WUc[a:a + 32768] - mu; CW += x_.T @ x_
    CW /= NW; LW = torch.linalg.cholesky(CW + 1e-6 * torch.trace(CW) / d * torch.eye(d, device=dev)); del WUc, CW
    def gauss_dict(Lc, seed, l_fold=None):
        g = torch.Generator(device=dev).manual_seed(seed); out = torch.empty(NW, d, dtype=torch.float16, device=dev); J = LEN.jacobians[l_fold].to(dev).float() if l_fold is not None else None
        for a in range(0, NW, 32768):
            z = torch.randn(min(32768, NW - a), d, generator=g, device=dev) @ Lc.T
            if J is not None: z = (z * gamma) @ J
            out[a:a + len(z)] = (z / z.norm(dim=1, keepdim=True).clamp_min(1e-12)).half()
        return out
    def gauss_dict_samples(Xc, seed):
        """unit atoms u = X_c^T xi / sqrt(n), xi ~ N(0, I_n): exact draws from N(0, Sigma_hat) (Amendment 6 section 1 construction; no factorisation)."""
        g = torch.Generator(device=dev).manual_seed(seed); ns = Xc.shape[0]; out = torch.empty(NW, d, dtype=torch.float16, device=dev)
        for a in range(0, NW, 16384):
            z = torch.randn(min(16384, NW - a), ns, generator=g, device=dev) @ Xc / ns ** 0.5; out[a:a + len(z)] = (z / z.norm(dim=1, keepdim=True).clamp_min(1e-12)).half(); del z
        return out
    def pursuit_curve(D, X, K):
        N = X.shape[0]; R_ = X.clone(); sel = torch.zeros(N, K, dtype=torch.long, device=dev); mask = torch.zeros(N, D.shape[0], dtype=torch.bool, device=dev); ar = torch.arange(N, device=dev)
        cap = torch.zeros(N, K, device=dev); xn = (X ** 2).sum(1); nstop = 0
        for j in range(K):
            C = (R_.half() @ D.T).float(); C[mask] = float("-inf"); cm, v = C.max(1); nstop += int((cm <= 0).sum()); sel[:, j] = v; mask[ar, v] = True; del C
            A = D[sel[:, :j + 1]].float(); c = Q.ls_refit(A, X); R_ = X - torch.einsum("nk,nkd->nd", c, A); cap[:, j] = 1 - (R_ ** 2).sum(1) / xn; del A
        return sel, cap, nstop
    Fids = {it["name"]: sorted(set(sum([forms_all(it[k]) for k in ("intermediate", "swap_to", "answer", "swap_answer")], []))) for it in ITEMS_AB}
    Xids = {it["name"]: [non_list[i] for i, w in enumerate(nnword) if w in set().union(*[alias(it[k]) for k in ("intermediate", "swap_to", "answer", "swap_answer")])] for it in ITEMS_AB}
    capJ_s, capF_s = np.zeros((nb, len(SWAP_L))), np.zeros((nb, len(SWAP_L))); eJ, eF = [], []
    for li, l in enumerate(SWAP_L):
        tb = time.time(); Xs = torch.stack([info[b]["hqY"][l][-1] - info[b]["hq"][l][-1] for b in bases]).to(dev); Xq = torch.stack([info[b]["hqY"][l][:-1] - info[b]["hq"][l][:-1] for b in bases]).reshape(-1, d).to(dev)
        ranks = []
        for bi, b in enumerate(bases):
            j3 = info[b]["j3"]; nm = b.split("|")[0]; si = len(b3) * nq3 + j3; ks = min(KP, max(int(P3[f"L{l}|stop"][si]), 1)); Ps = atom_dirs(l, P3[f"L{l}|sel"][si, :ks])
            Mx = torch.cat([atom_dirs(l, Fids[nm]), Ps] + ([atom_dirs(l, Xids[nm])] if Xids[nm] else []), 0).T; Us, Ss, _ = torch.linalg.svd(Mx, full_matrices=False); U = Us[:, Ss > 1e-3 * Ss[0]]
            UJ[(b, l)] = U.cpu(); ranks.append(U.shape[1]); capJ_s[bi, li] = float(((Xs[bi] @ U) ** 2).sum() / (Xs[bi] ** 2).sum())
            sel = P3[f"L{l}|sel"][j3 * nq3:(j3 + 1) * nq3, :KP]; c = torch.as_tensor(P3[f"L{l}|coef{KP}"][j3 * nq3:(j3 + 1) * nq3], device=dev)
            VJ[(b, l)] = torch.einsum("nk,nkd->nd", c, atom_dirs(l, sel.reshape(-1)).reshape(nq3, KP, d)).cpu()
        eJ.append(float(np.mean([((VJ[(b, l)] ** 2).sum(1) / (info[b]["hqY"][l][:-1] - info[b]["hq"][l][:-1]).pow(2).sum(1)).mean() for b in bases])))
        Xc = torch.cat(COVS[l], 0).to(dev).float(); Xc -= Xc.mean(0, keepdim=True)
        D = gauss_dict_samples(Xc, SEED + 600000 + l); del Xc; Kmax = max(ranks); selP, capP, stP = pursuit_curve(D, Xs, Kmax)
        for bi, b in enumerate(bases):
            r_ = ranks[bi]; A_ = D[selP[bi, :r_]].float(); U = torch.linalg.qr(A_.T)[0]; UF[(b, l)] = U.cpu(); CAPS[(b, l)] = capP[bi].cpu().numpy(); capF_s[bi, li] = float(capP[bi, r_ - 1])
        del D; Dfn = gauss_dict(LW, SEED + 750000 + l, l_fold=l); selF, stopF, coefF = Q.pursuit_ls(Dfn, Xq, KP, [KP])
        vf = torch.einsum("nk,nkd->nd", coefF[KP], Dfn[selF].float()); META["stops"][str(l)] = {"phi": stP, "functional": int((stopF < KP).sum())}
        for bi, b in enumerate(bases): VF[(b, l)] = vf[bi * nq3:(bi + 1) * nq3].cpu()
        eF.append(float(((vf ** 2).sum(1) / (Xq ** 2).sum(1)).mean())); del Dfn, vf, selF, coefF, Xq, Xs; torch.cuda.empty_cache()
        print(f"  [PB] block {l}: rank {min(ranks)}-{max(ranks)} | capture of dh_s J {capJ_s[:, li].mean():.3f} Phi {capF_s[:, li].mean():.3f} | energy q_pre J25 {eJ[-1]:.3f} F25 {eF[-1]:.3f} ({time.time()-tb:.0f}s)", flush=True)
    ratio = float(capF_s.mean() / max(capJ_s.mean(), 1e-9)); TRIG = ratio > 1.5
    META.update({"capture_dh_s_J": capJ_s.tolist(), "capture_dh_s_phi": capF_s.tolist(), "phi_over_J_capture": ratio, "phi_prime_triggered": TRIG, "energy_qpre_J25": eJ, "energy_qpre_F25": eF})
    UF2 = {}
    if TRIG:
        for bi, b in enumerate(bases):
            for li, l in enumerate(SWAP_L):
                cv = CAPS[(b, l)]; rp = int(np.argmax(cv >= capJ_s[bi, li])) + 1 if (cv >= capJ_s[bi, li]).any() else UF[(b, l)].shape[1]; UF2[(b, l)] = UF[(b, l)][:, :min(rp, UF[(b, l)].shape[1])]
    print(f"  [PB] done ({time.time()-t0:.0f}s): Phi/J capture ratio {ratio:.2f} -> Phi' {'triggered' if TRIG else 'not triggered'}", flush=True)

    # ============================================================ Phase C: rows per cell (pass 1: refs + Part A; pass 2: Parts C, D, E)
    def cell_targets(b):
        I = info[b]; T = {"full": {}, "J25rem": {}, "F25": {}, "F25rem": {}, "R25rem": {}}; g = torch.Generator().manual_seed(SEED + 760000 + bases.index(b))
        for l in SWAP_L:
            h = I["hq"][l][:-1].to(dev); dh = I["hqY"][l][:-1].to(dev) - h; vj = VJ[(b, l)].to(dev); vf = VF[(b, l)].to(dev)
            T["full"][l] = h + dh; T["J25rem"][l] = h + dh - vj; T["F25"][l] = h + vf; T["F25rem"][l] = h + dh - vf
            Rk = Q.random_frame(d, KP, g, dev); vr = (dh @ Rk) @ Rk.T; vr = vr * (vf.norm(dim=1, keepdim=True) / vr.norm(dim=1, keepdim=True).clamp_min(1e-12)); T["R25rem"][l] = h + dh - vr
        return T
    def rows_for(b, T, rows):
        I = info[b]; ids, qpre, s, CA, SPW = I["ids"], I["qpre"], I["s"], I["CA"], I["SPW"]; UJd = {l: UJ[(b, l)].float() for l in SWAP_L}; UFd = {l: UF[(b, l)].float() for l in SWAP_L}
        UF2d = {l: UF2[(b, l)].float() for l in SWAP_L} if TRIG else None; Q0 = I["Q"][0]
        def mk_row(row, w):
            def mk(j, sp):
                A_j = list(range(s, s + len(sp))); cref = CA[(w, j)]; parts = [fp()]; base = row.split(":")[0]; mods = row.split(":")[1:] if ":" in row else []
                if base != "clean":
                    tgt = T[base]
                    if "sfullA" in mods: parts.append(H.SpanWriter(lm.layers, SWAP_L, qpre + A_j, {l: torch.cat([tgt[l], cref[l]], 0) for l in SWAP_L}))
                    else: parts.append(H.SpanWriter(lm.layers, SWAP_L, qpre, tgt))
                    for B_ in DEPTHS:
                        if f"sfull{B_}" in mods: parts.append(H.SpanWriter(lm.layers, list(range(36, B_ + 1)), A_j, {l: cref[l] for l in range(36, B_ + 1)}))
                for key, Ud in (("ccsA", UJd), ("ccfA", UFd), ("ccf2A", UF2d)):
                    if key in mods: parts.append(P4.SubspaceClampMulti(lm.layers, SWAP_L, A_j, Ud, cref))
                if "m63A" in mods: parts.append(P4.AttnReadBlockFrom(lm.layers, [LAST], s, qpre))
                for X_ in "TWP":
                    if f"cut{X_}" in mods: parts.append(P4.AttnReadBlockFrom(lm.layers, [LAST], s, [Q0 + i for i in CLS[X_]]))
                return H.Both(*parts)
            return mk
        for row in rows:
            tag = f"{b}|{row}"; out = {}
            for w in ("answer", "swap"):
                out[w] = score_word(ids, SPW[w], mk_row(row, w)); n_add = len(SPW[w]); globals()["_n"] = n_add
                for ctx in out[w][4]:
                    for x in ctx.c:
                        if isinstance(x, P4.AttnReadBlockFrom): META["leak"][tag] = max(META["leak"].get(tag, 0.0), float(x.leak.get(LAST, float("nan"))))
            RAW[f"{tag}|seq_answer"], RAW[f"{tag}|seq_swap"] = np.float32(out["answer"][0]), np.float32(out["swap"][0])
            RAW[f"{tag}|lpf_answer_all"], RAW[f"{tag}|lpf_swap_all"] = np.array(out["answer"][2], np.float32), np.array(out["swap"][2], np.float32)
            a_, l_ = out["answer"][3]; RAWZ[f"{tag}|zq"] = ro.z(a_, I["Q"], LZ)[:, :, zc_ab(I["it"])].astype(np.float16)
            if row == "J25rem":   # energy capture of the un-clamped row's change at the answer positions (answer word, first spelling)
                cref = CA[("answer", 0)]; P_ = len(SPW["answer"][0])
                ch = {l: a_[l][0, s:s + P_, :].float() - cref[l].to(dev) for l in SWAP_L}
                RAW[f"{b}|capture_rowchange_J"] = np.array([[(float(((ch[l][p] @ UJd[l].to(dev)) ** 2).sum() / (ch[l][p] ** 2).sum().clamp_min(1e-12))) for p in range(P_)] for l in SWAP_L], np.float32)
                RAW[f"{b}|capture_rowchange_phi"] = np.array([[(float(((ch[l][p] @ UFd[l].to(dev)) ** 2).sum() / (ch[l][p] ** 2).sum().clamp_min(1e-12))) for p in range(P_)] for l in SWAP_L], np.float32)
            del a_, l_, out
        return sum(2 * 0 for _ in rows)
    ROWS1 = ["full", "J25rem", "J25rem:ccsA", "J25rem:ccsA:m63A", "clean:m63A", "full:sfullA", "J25rem:m63A", "J25rem:ccfA", "J25rem:ccfA:m63A"] + (["J25rem:ccf2A", "J25rem:ccf2A:m63A"] if TRIG else [])
    ROWS2 = ["F25", "F25rem", "R25rem", "clean:cutT", "clean:cutW", "clean:cutP", "full:sfullA:cutT", "full:sfullA:cutW", "full:sfullA:cutP"] + [f"full:sfull{B_}" for B_ in DEPTHS]
    META["rows_pass1"], META["rows_pass2"] = ROWS1, ROWS2
    nf = lambda b, rows: sum(len(info[b]["SPW"]["answer"]) + len(info[b]["SPW"]["swap"]) for _ in rows)
    for b in bases:
        tc = time.time(); T = cell_targets(b); rows_for(b, T, ROWS1); n += nf(b, ROWS1); del T
        mg = lambda r_, base="clean": float((RAW[f"{b}|{r_}|seq_swap"] - RAW[f"{b}|{r_}|seq_answer"]) - (RAW[f"{b}|{base}|seq_swap"] - RAW[f"{b}|{base}|seq_answer"])); fl = mg("full")
        print(f"  [C1] {b}: {n} fw ({time.time()-tc:.0f}s) | ccsA {mg('J25rem:ccsA')/fl:+.2f} ccsA_m63 {mg('J25rem:ccsA:m63A','clean:m63A')/fl:+.2f} R0 {mg('J25rem:m63A','clean:m63A')/fl:+.2f} "
              f"ccfA {mg('J25rem:ccfA')/fl:+.2f} ccfA_m63 {mg('J25rem:ccfA:m63A','clean:m63A')/fl:+.2f}", flush=True)
    save("pass 1 (refs + Part A)")
    ATT = {}
    for b in bases:
        tc = time.time(); I = info[b]; T = cell_targets(b); rows_for(b, T, ROWS2); n += nf(b, ROWS2)
        # per-head attribution: one forward under full:sfullA and one clean (answer word, first spelling)
        sp0 = I["SPW"]["answer"][0]; A0 = list(range(I["s"], I["s"] + len(sp0))); cref = I["CA"][("answer", 0)]; full_ids = I["ids"] + list(sp0); cap = {}
        for tagc, ctx in (("clean", H.Both(fp())), ("sfullA", H.Both(fp(), H.SpanWriter(lm.layers, SWAP_L, I["qpre"] + A0, {l: torch.cat([T["full"][l], cref[l]], 0) for l in SWAP_L})))):
            hc = HeadCapture(lm.layers[LAST], I["s"]); a_, lg = run(full_ids, H.Both(ctx, hc)); n += 1; cap[tagc] = (hc.x, hc.w); del a_, lg
        Wo = lm.layers[LAST].self_attn.o_proj.weight.float(); nh = Wo.shape[1] // 256
        c_h = {k: torch.stack([Wo[:, h * 256:(h + 1) * 256] @ v[0][h * 256:(h + 1) * 256] for h in range(nh)]) for k, v in cap.items()}
        hf = I["hfin"]; eps = float(getattr(ro.norm, "variance_epsilon", 1e-6)); rms = torch.sqrt((hf ** 2).mean() + eps); w = (WU[I["tok_first"][1]].float() - WU[I["tok_first"][0]].float()) * gamma
        dC = c_h["sfullA"] - c_h["clean"]; DE = (dC @ w) / rms - (w @ hf) * (dC @ hf) / (d * rms ** 3)
        Q0 = I["Q"][0]; att = cap["sfullA"][1]
        RAW[f"{b}|head_DE"] = DE.cpu().numpy().astype(np.float32); RAW[f"{b}|head_mass"] = np.stack([att[:, [Q0 + i for i in CLS[X_]]].sum(1).cpu().numpy() for X_ in "TWP"], 1).astype(np.float32)
        del T; torch.cuda.empty_cache()
        mg = lambda r_, base="clean": float((RAW[f"{b}|{r_}|seq_swap"] - RAW[f"{b}|{r_}|seq_answer"]) - (RAW[f"{b}|{base}|seq_swap"] - RAW[f"{b}|{base}|seq_answer"])); fl = mg("full")
        print(f"  [C2] {b}: {n} fw ({time.time()-tc:.0f}s) | F25 {mg('F25')/fl:+.2f} F25rem {mg('F25rem')/fl:+.2f} R25rem {mg('R25rem')/fl:+.2f} | sfA {mg('full:sfullA')/fl:+.2f} "
              f"cutT {mg('full:sfullA:cutT','clean:cutT')/fl:+.2f} cutW {mg('full:sfullA:cutW','clean:cutW')/fl:+.2f} cutP {mg('full:sfullA:cutP','clean:cutP')/fl:+.2f} | "
              + " ".join(f"d{B_} {mg(f'full:sfull{B_}')/fl:+.2f}" for B_ in DEPTHS) + f" | head DE sum {float(DE.sum()):+.2f}", flush=True)
    save("pass 2 (Parts C, D, E)")
    sha = lambda f: hashlib.sha256(open(os.path.join(OUT, f), "rb").read()).hexdigest()
    man = R.manifest_block(); man.update({"run_id": RUN_ID, "stage": STAGE, "script": os.path.relpath(__file__, R.PROJECT), "design": META["design"], "raw_sha256": sha(f"raw_{STAGE}.npz"), "raw_zq_sha256": sha(f"raw_{STAGE}_zq.npz")})
    json.dump(man, open(os.path.join(OUT, f"manifest_{STAGE}.json"), "w"), indent=1)
    print(f"[done {STAGE}] {n} forwards, {time.time()-t0:.0f}s | leak max {max(META['leak'].values()) if META['leak'] else float('nan'):.1e} | Phi' {'triggered' if TRIG else 'not triggered'}")


if __name__ == "__main__":
    main()
