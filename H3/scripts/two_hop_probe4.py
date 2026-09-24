"""H3 two_hop_organism stage `probe4` (design: H3/design_specs/two_hop_organism.md, Amendment 9).

Part 1 (35 admitted items x C0-C3): the verified consumer clamp of Amendment 8 extended to every scored answer position A_j
(s and the continuation positions of spelling j; silly mistake 5), its rank- and norm-matched control, and the route split at the
final block (block 63, full attention): the block-63 read from A_j to q_pre cut (AttnReadBlock construction), the answer positions
held entirely at clean at blocks 36-62, and both. Same-run references reproduce probe3.
Part 2 (7 city pairs x C0-C3): the country plane and the cue-city plane of the transplanted delta, installed alone or removed,
in the language question (capital delta) and in the capital question (language delta), with random 2-plane controls.
Every row logs per-token log-probs (first token vs continuation). Float32 residual from block 35; sequence endpoint primary.
Usage: two_hop_probe4.py smoke4|probe4
"""
import os, sys, json, time, hashlib, re
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "..", "common", "scripts"))
STAGE = sys.argv[1] if len(sys.argv) > 1 else "smoke4"; assert STAGE in ("smoke4", "probe4")
_argv = sys.argv; sys.argv = [_argv[0], "stage2"]; import two_hop_qsplit6 as Q; sys.argv = _argv
import numpy as np, torch
import registry as R, materials as M, rendering as Rn, readout as RO, hooks as H
from hooks_fp32 import Fp32Residual

OUT = R.out_dir("H3", "outputs", "two_hop_organism")
RUN_ID = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()); SEED = 20260924; FP32_FROM = 35; LAST = 63
CARRIERS = ["C0", "C1", "C2", "C3"]; SWAP_L = list(range(36, 63)); RB = list(range(51, 60)); LZ = list(range(36, 63)); KP = 25
ADMITTED = json.load(open(os.path.join(OUT, "meta_admit.json")))["admitted"]
ITEMS_AB = [it for it in Q.ITEMS if it["name"] in ADMITTED]; assert len(ITEMS_AB) == 35
PAIR_ITEMS = ["ex-city-capital-Lyon-Naples", "ex-city-capital-Naples-Barcelona", "ex2-city-capital-Munich", "ex2-city-capital-Osaka",
              "s2-city-capital-Bergen-Kyoto", "s2-city-capital-Marseille-Aarhus", "s2-city-capital-Salzburg-Kyoto"]
LANG = {"France": "French", "Italy": "Italian", "Spain": "Spanish", "Germany": "German", "Japan": "Japanese", "Norway": "Norwegian", "Denmark": "Danish", "Austria": "German"}
LANG_TEMPLATE = "Fact: The language spoken in the country where {cue} is located is"
CAR_AB, CAR_C = CARRIERS, CARRIERS
if STAGE == "smoke4": ITEMS_AB, CAR_AB, PAIR_ITEMS, CAR_C = [ITEMS_AB[0]], ["C0"], PAIR_ITEMS[:1], ["C0"]
IT = {it["name"]: it for it in Q.ITEMS}
cue_of = lambda p: re.search(r"country where (.+?) is located", p).group(1)


class SubspaceClampMulti:
    """Amendment 9: hold the coordinates of h in span(U_l) at their clean values at several positions, h' = h - (h - h_ref) U U^T,
    per-position clean references href {l: [P, d]}; with `target` {l: [P]} each position's delta is rescaled to that norm.
    fp32 arithmetic under the autocast; the post-cast realized write is recorded per block and position."""
    def __init__(self, blocks, layers, positions, U, href, target=None):
        self.blocks, self.layers = blocks, sorted(layers); self.pos = torch.as_tensor(positions, dtype=torch.long)
        self.U, self.href, self.target, self._h, self.post = U, href, target, [], {}

    def _mk(self, l):
        @torch.autocast("cuda", enabled=False)
        def f(m, i, o):
            h = H._out(o).clone(); hp = h[0, self.pos, :].float(); U = self.U[l].to(hp.device).float()
            delta = -((hp - self.href[l].to(hp.device).float()) @ U) @ U.T
            if self.target is not None:
                delta = delta * (self.target[l].to(hp.device).float()[:, None] / delta.norm(dim=1, keepdim=True).clamp_min(1e-8))
            new = (hp + delta).to(h.dtype); real = new.float() - hp; dn = delta.norm(dim=1)
            self.post[l] = {"req": dn.detach().cpu(), "real": real.norm(dim=1).detach().cpu(), "kappa": torch.nn.functional.cosine_similarity(real, delta, dim=1).detach().cpu()}
            h[0, self.pos, :] = new
            return H._pack(o, h)
        return f

    def __enter__(self):
        self._h = [self.blocks[l].register_forward_hook(self._mk(l)) for l in self.layers]; return self

    def __exit__(self, *a):
        [x.remove() for x in self._h]


class AttnReadBlockFrom(H.AttnReadBlock):
    """H.AttnReadBlock with the query positions set at call time to every position from q_from to the end of the sequence
    (the scored answer positions of whichever spelling is being scored)."""
    def __init__(self, blocks, layers, q_from, k_positions):
        super().__init__(blocks, layers, [q_from], k_positions); self.q_from = int(q_from)

    def _pre(self, l):
        base = super()._pre(l)
        def f(m, args, kwargs):
            hs = kwargs.get("hidden_states", args[0] if args else None); self.q = torch.arange(self.q_from, hs.shape[1], dtype=torch.long)
            return base(m, args, kwargs)
        return f


def main():
    tok = R.make_tokenizer()
    from jlens.hf import from_hf
    model = R.load_model(); lm = from_hf(model, tok, compile=False)
    ALL = list(range(R.N_BLOCKS)); run = H.make_run(model, lm, ALL); dev = lm.input_device
    LEN = R.load_lenses(("J_NP",))["J_NP"]
    render = lambda prompt, car: Rn.render(tok, Q.utext(Q.clue_body(prompt), car), car, sources=[("CLUE", Q.clue_body(prompt), False)], extra_turns=[(Q.QUESTION, "")])
    assert type(lm.layers[LAST].self_attn).__name__.lower().find("attention") >= 0 and hasattr(lm.layers[LAST], "self_attn"), "block 63 must be a full-attention layer"

    # ---------------------------------------------------------------- words, columns, directions
    words = set()
    for it in ITEMS_AB: words |= {it[k] for k in ("intermediate", "swap_to", "answer", "swap_answer")}
    pairs = []
    for nm in PAIR_ITEMS:
        it = IT[nm]; p = {"name": nm, "it": it, "A": cue_of(it["prompt"]), "B": cue_of(it["donor_prompt"]), "own_country": it["intermediate"], "donor_country": it["swap_to"],
                          "own_cap": it["answer"], "donor_cap": it["swap_answer"], "own_lang": LANG[it["intermediate"]], "donor_lang": LANG[it["swap_to"]]}
        pairs.append(p); words |= {p[k] for k in ("A", "B", "own_country", "donor_country", "own_cap", "donor_cap", "own_lang", "donor_lang")}
    decoys = [w for w in Q.DECOYS if w not in words]; COLS = sorted(words) + decoys
    TID = {w: Rn.single_token_id(tok, w) for w in COLS}; assert all(v is not None for v in TID.values()), TID
    ro = RO.LensReadout(model, lm, LEN, [TID[w] for w in COLS])
    gamma = ro.gamma.to(dev); WU = ro.Wu; d = WU.shape[1]; V = len(tok)
    NAMING = {w: {l: ro.folded_direction(l, TID[w]) for l in SWAP_L} for w in words}
    fp = lambda: Fp32Residual(lm.layers, FP32_FROM)
    zc_ab = lambda it: [COLS.index(w) for w in (it["intermediate"], it["swap_to"], it["answer"], it["swap_answer"])] + [COLS.index(x) for x in decoys]
    zc_c = lambda p: [COLS.index(p[k]) for k in ("own_country", "donor_country", "A", "B", "own_lang", "donor_lang", "own_cap", "donor_cap")] + [COLS.index(x) for x in decoys]

    def atom_dirs(l, ids):
        J = LEN.jacobians[l].to(dev).float(); a = (WU[torch.as_tensor(np.asarray(ids, dtype=np.int64), device=dev)].float() * gamma) @ J
        return (a / a.norm(dim=1, keepdim=True).clamp_min(1e-12)).half().float()

    def score_word(ids, cands, mk, capture=None):
        """Sequence score of one word: one forward per spelling under mk(j, sp); returns logsumexp, per-spelling totals, per-spelling
        first-token log-probs, and the first forward's (acts, logits, ctx) plus every ctx. capture[j] <- states at A_j, blocks 36-62."""
        vals, firsts, first, ctxs = [], [], None, []
        for j, sp in enumerate(cands):
            full = ids + list(sp); ctx = mk(j, sp); a_, lg = run(full, ctx); ctxs.append(ctx)
            lp = torch.log_softmax(lg[0, len(ids) - 1: len(full) - 1].float(), -1); tl = [float(lp[k, sp[k]]) for k in range(len(sp))]
            vals.append(sum(tl)); firsts.append(tl[0])
            if capture is not None: capture[j] = {l: a_[l][0, len(ids) - 1: len(full) - 1, :].float().clone() for l in SWAP_L}
            if first is None: first = (a_, lg)
            else: del a_
        return float(torch.logsumexp(torch.tensor(vals), 0)), vals, firsts, first, ctxs

    # ---------------------------------------------------------------- translation atoms (Amendment 8 rule)
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

    RAW, RAWZ = {}, {}
    META = {"stage": STAGE, "design": "H3/design_specs/two_hop_organism.md (Amendment 9)", "columns": COLS, "decoys": decoys, "carriers_ab": CAR_AB, "carriers_c": CAR_C,
            "swap_layers": [SWAP_L[0], SWAP_L[-1]], "readout_band": [RB[0], RB[-1]], "zq_layers": [LZ[0], LZ[-1]], "fp32_from": FP32_FROM, "seed": SEED, "last_block": LAST,
            "items_ab": [it["name"] for it in ITEMS_AB], "pairs": [{k: v for k, v in p.items() if k != "it"} for p in pairs], "language_template": LANG_TEMPLATE,
            "seeds": {"ccsr_frames": "SEED + 350000 + cell (Amendment 8)", "x_rand2": "SEED + 500000 + pair cell", "m_rand2": "SEED + 550000 + pair cell"},
            "cells_ab": {}, "cells_c": {}, "leak": {}, "clamp_stats": {}}
    n = 0

    # ---------------------------------------------------------------- Part 1
    P3 = dict(np.load(os.path.join(OUT, "raw_pursuit_probe3.npz"), allow_pickle=True)); b3 = list(P3["bases"]); nq3 = int(P3["n_qpre"])
    bases = [f"{it['name']}|{ck}" for it in ITEMS_AB for ck in CAR_AB]; assert all(b in b3 for b in bases), "cells missing from probe3's pursuit"
    ROWS_AB = ["q_full_pre", "q_J25rem_pre", "q_J25rem_pre_ccs", "q_J25rem_pre_ccsA", "q_J25rem_pre_ccsrA", "clean_m63A", "q_full_pre_m63A", "q_J25rem_pre_ccsA_m63A",
               "q_full_pre_sfullA", "q_J25rem_pre_sfullA", "q_J25rem_pre_sfullA_m63A"]
    META["rows_ab"] = ROWS_AB
    for bi, b in enumerate(bases):
        it = IT[b.split("|")[0]]; ck = b.split("|")[1]; car = M.CARRIERS[ck]; tc = time.time(); j3 = b3.index(b)
        r = render(it["prompt"], car); rd = render(it["donor_prompt"], car)
        assert len(rd) == len(r) and rd.spans["CLUE"]["full"] == r.spans["CLUE"]["full"] and rd.meta["carrier_end"] == r.meta["carrier_end"], f"geometry {b}"
        ce = r.meta["carrier_end"]; Qp_ = list(range(ce, len(r))); qpre = Qp_[:-1]; s = Qp_[-1]; nq = len(qpre); assert nq == nq3 and s == len(r) - 1
        assert list(r.ids[Qp_[0]:]) == list(rd.ids[Qp_[0]:]), f"q-turn {b}"
        ids = list(r.ids); SPW = {"answer": Q.spellings(tok, it["answer"]), "swap": Q.spellings(tok, it["swap_answer"])}
        CLEAN_A = {}; sc = {}
        for w in ("answer", "swap"):
            cap = {}; sc[w] = score_word(ids, SPW[w], lambda j, sp: fp(), capture=cap); n += len(SPW[w])
            for j in cap: CLEAN_A[(w, j)] = cap[j]
        ac = sc["answer"][3][0]; RAW[f"{b}|clean|seq_answer"], RAW[f"{b}|clean|seq_swap"] = np.float32(sc["answer"][0]), np.float32(sc["swap"][0])
        RAW[f"{b}|clean|lpf_answer_all"], RAW[f"{b}|clean|lpf_swap_all"] = np.array(sc["answer"][2], np.float32), np.array(sc["swap"][2], np.float32)
        RAW[f"{b}|clean|seq_answer_all"], RAW[f"{b}|clean|seq_swap_all"] = np.array(sc["answer"][1], np.float32), np.array(sc["swap"][1], np.float32)
        RAWZ[f"{b}|clean|zq"] = ro.z(ac, Qp_, LZ)[:, :, zc_ab(it)].astype(np.float16)
        dA = score_word(list(rd.ids), SPW["answer"], lambda j, sp: fp()); dB = score_word(list(rd.ids), SPW["swap"], lambda j, sp: fp()); n += len(SPW["answer"]) + len(SPW["swap"])
        RAW[f"{b}|donor|seq_answer"], RAW[f"{b}|donor|seq_swap"] = np.float32(dA[0]), np.float32(dB[0]); ad = dA[3][0]
        hq = {l: ac[l][0, Qp_, :].float() for l in SWAP_L}; hqY = {l: ad[l][0, Qp_, :].float() for l in SWAP_L}; del ad, dA, dB
        META["cells_ab"][b] = {"intermediate": it["intermediate"], "swap_to": it["swap_to"], "answer": it["answer"], "swap_answer": it["swap_answer"], "category": it.get("category"), "scoring": s,
                               "spellings_answer": [list(x) for x in SPW["answer"]], "spellings_swap": [list(x) for x in SPW["swap"]], "zq_columns": [COLS[i] for i in zc_ab(it)]}
        # targets and pinned spans (Amendment 8 construction from the stored pursuit)
        gr = torch.Generator().manual_seed(SEED + 350000 + bi)
        Fids = sorted(set(sum([forms_all(it[k]) for k in ("intermediate", "swap_to", "answer", "swap_answer")], []))); Xids = translation_ids(it)
        T = {"q_full_pre": {}, "q_J25rem_pre": {}}; PIN, PINR = {}, {}
        for l in SWAP_L:
            h = hq[l][:-1]; dh = hqY[l][:-1] - h; T["q_full_pre"][l] = hqY[l][:-1].clone()
            sel = P3[f"L{l}|sel"][j3 * nq3:(j3 + 1) * nq3, :KP]; c = torch.as_tensor(P3[f"L{l}|coef{KP}"][j3 * nq3:(j3 + 1) * nq3], device=dev)
            A25 = atom_dirs(l, sel.reshape(-1)).reshape(nq, KP, d); T["q_J25rem_pre"][l] = h + dh - torch.einsum("nk,nkd->nd", c, A25); del A25
            si = len(b3) * nq3 + j3; ks = min(KP, max(int(P3[f"L{l}|stop"][si]), 1)); Ps = atom_dirs(l, P3[f"L{l}|sel"][si, :ks])
            Mx = torch.cat([atom_dirs(l, Fids), Ps] + ([atom_dirs(l, Xids)] if Xids else []), 0).T
            Us, Ss, _ = torch.linalg.svd(Mx, full_matrices=False); U = Us[:, Ss > 1e-3 * Ss[0]]; PIN[l] = U; PINR[l] = Q.orth_against(Q.random_frame(d, U.shape[1], gr, dev), U)
        hclean_s = {l: hq[l][-1] for l in SWAP_L}; CCT = {}; stats = {}

        def mk_row(row, w):
            def mk(j, sp):
                A_j = list(range(s, s + len(sp))); cref = CLEAN_A[(w, j)]; parts = [fp()]
                base = "q_full_pre" if row.startswith("q_full_pre") else ("q_J25rem_pre" if row.startswith("q_J25rem_pre") else None)
                if "sfullA" in row: parts.append(H.SpanWriter(lm.layers, SWAP_L, qpre + A_j, {l: torch.cat([T[base][l], cref[l]], 0) for l in SWAP_L}))
                elif base is not None: parts.append(H.SpanWriter(lm.layers, SWAP_L, qpre, T[base]))
                if row == "q_J25rem_pre_ccs": parts.append(Q.SubspaceClampMatched(lm.layers, SWAP_L, s, PIN, hclean_s))
                if row in ("q_J25rem_pre_ccsA", "q_J25rem_pre_ccsA_m63A"): parts.append(SubspaceClampMulti(lm.layers, SWAP_L, A_j, PIN, cref))
                if row == "q_J25rem_pre_ccsrA": parts.append(SubspaceClampMulti(lm.layers, SWAP_L, A_j, PINR, cref, target=CCT[(w, j)]))
                if row.endswith("m63A"): parts.append(AttnReadBlockFrom(lm.layers, [LAST], s, qpre))
                return H.Both(*parts)
            return mk
        for row in ROWS_AB:
            tag = f"{b}|{row}"; out = {}
            for w in ("answer", "swap"):
                out[w] = score_word(ids, SPW[w], mk_row(row, w)); n += len(SPW[w])
                for j, ctx in enumerate(out[w][4]):
                    for x in ctx.c:
                        if isinstance(x, SubspaceClampMulti):
                            stt = stats.setdefault(row, {"rho": [], "kappa": [], "normdev": []})
                            for l in SWAP_L:
                                pst = x.post[l]; ok = pst["req"] > 1e-6
                                if ok.any(): stt["rho"] += (pst["real"][ok] / pst["req"][ok]).tolist(); stt["kappa"] += pst["kappa"][ok].tolist()
                                if row == "q_J25rem_pre_ccsA": CCT.setdefault((w, j), {})[l] = pst["real"].clone()
                                if row == "q_J25rem_pre_ccsrA":
                                    ref = CCT[(w, j)][l]; okr = ref > 1e-6
                                    if okr.any(): stt["normdev"] += (torch.abs(pst["real"][okr] - ref[okr]) / ref[okr]).tolist()
                        if isinstance(x, AttnReadBlockFrom): META["leak"][tag] = max(META["leak"].get(tag, 0.0), float(x.leak.get(LAST, float("nan"))))
            RAW[f"{tag}|seq_answer"], RAW[f"{tag}|seq_swap"] = np.float32(out["answer"][0]), np.float32(out["swap"][0])
            RAW[f"{tag}|seq_answer_all"], RAW[f"{tag}|seq_swap_all"] = np.array(out["answer"][1], np.float32), np.array(out["swap"][1], np.float32)
            RAW[f"{tag}|lpf_answer_all"], RAW[f"{tag}|lpf_swap_all"] = np.array(out["answer"][2], np.float32), np.array(out["swap"][2], np.float32)
            a_, l_ = out["answer"][3]
            assert all(torch.equal(a_[l][0, :qpre[0], :], ac[l][0, :qpre[0], :]) for l in ALL), f"prefix touched {tag}"
            if row not in ("clean_m63A",):
                base = "q_full_pre" if row.startswith("q_full_pre") else "q_J25rem_pre"
                req = torch.stack([(T[base][l] - ac[l][0, qpre, :].float()).flatten() for l in SWAP_L]); real = torch.stack([(a_[l][0, qpre, :].float() - ac[l][0, qpre, :].float()).flatten() for l in SWAP_L])
                RAW[f"{tag}|rho"] = np.float32(float((real.norm(dim=1) / req.norm(dim=1).clamp_min(1e-8)).mean())); RAW[f"{tag}|kappa"] = np.float32(float(torch.nn.functional.cosine_similarity(real, req, dim=1).mean()))
                RAW[f"{tag}|rberr"] = np.float32(max(float((a_[l][0, qpre, :].float() - T[base][l]).abs().max()) for l in SWAP_L))
            RAWZ[f"{tag}|zq"] = ro.z(a_, Qp_, LZ)[:, :, zc_ab(it)].astype(np.float16); RAW[f"{tag}|greedy"] = tok.decode(int(l_[0, len(ids) - 1].argmax())).strip()
            del a_, l_, out
        for row, st_ in stats.items():
            cs_ = META["clamp_stats"].setdefault(row, {"rho_min": 9.0, "rho_max": -9.0, "kappa_min": 9.0, "normdev_max": 0.0})
            if st_["rho"]: cs_["rho_min"] = min(cs_["rho_min"], min(st_["rho"])); cs_["rho_max"] = max(cs_["rho_max"], max(st_["rho"])); cs_["kappa_min"] = min(cs_["kappa_min"], min(st_["kappa"]))
            if st_["normdev"]: cs_["normdev_max"] = max(cs_["normdev_max"], max(st_["normdev"]))
        del ac, hq, hqY, CLEAN_A, sc; torch.cuda.empty_cache()
        mgn = lambda rr, cl="clean": float((RAW[f"{b}|{rr}|seq_swap"] - RAW[f"{b}|{rr}|seq_answer"]) - (RAW[f"{b}|{cl}|seq_swap"] - RAW[f"{b}|{cl}|seq_answer"]))
        full = mgn("q_full_pre")
        print(f"  [C] {b}: {n} forwards ({time.time()-tc:.0f}s) | shares ccs {mgn('q_J25rem_pre_ccs')/full:+.2f} ccsA {mgn('q_J25rem_pre_ccsA')/full:+.2f} ccsrA {mgn('q_J25rem_pre_ccsrA')/full:+.2f} | "
              f"ccsA_m63A {mgn('q_J25rem_pre_ccsA_m63A', 'clean_m63A')/full:+.2f} J25_sfullA {mgn('q_J25rem_pre_sfullA')/full:+.2f} both-cut {mgn('q_J25rem_pre_sfullA_m63A', 'clean_m63A')/full:+.3f} | "
              f"full_m63A {mgn('q_full_pre_m63A', 'clean_m63A')/full:+.2f} full_sfullA {mgn('q_full_pre_sfullA')/full:+.2f} | leak max {max(v for k, v in META['leak'].items() if k.startswith(b)):.1e}", flush=True)

    # ---------------------------------------------------------------- Part 2: country or city
    ROWS_C = ["q_xfer", "q_native_lang", "x_ctry", "x_city", "x_noctry", "x_nocity", "x_rand2", "q_mirror", "q_native_cap", "m_ctry", "m_city", "m_noctry", "m_nocity", "m_rand2"]
    META["rows_c"] = ROWS_C
    for pi, p in enumerate(pairs):
        for ck in CAR_C:
            car = M.CARRIERS[ck]; b = f"{p['name']}|{ck}"; ci_ = pi * len(CAR_C) + CAR_C.index(ck); tc = time.time()
            rc = {"A": render(p["it"]["prompt"], car), "B": render(p["it"]["donor_prompt"], car)}; rl = {"A": render(LANG_TEMPLATE.format(cue=p["A"]), car), "B": render(LANG_TEMPLATE.format(cue=p["B"]), car)}
            for rr in (rc, rl):
                assert len(rr["A"]) == len(rr["B"]) and rr["A"].spans["CLUE"]["full"] == rr["B"].spans["CLUE"]["full"] and rr["A"].meta["carrier_end"] == rr["B"].meta["carrier_end"], f"geometry {b}"
            qt = [list(x.ids[x.meta["carrier_end"]:]) for x in (rc["A"], rc["B"], rl["A"], rl["B"])]; assert all(q == qt[0] for q in qt), f"q-turn ids {b}"
            SP = {k: Q.spellings(tok, p[k]) for k in ("own_lang", "donor_lang", "own_cap", "donor_cap")}

            def score4(ids, mk):
                out, firsts, first = {}, {}, None
                for k in SP:
                    v, _, fl, fr, _c = score_word(ids, SP[k], lambda j, sp: mk()); out[k] = v; firsts[k] = fl
                    if first is None: first = fr
                    else: del fr
                return out, firsts, first
            st, geo = {}, {}
            for tmpl, rr in (("cap", rc), ("lang", rl)):
                ce = rr["A"].meta["carrier_end"]; Qp_ = list(range(ce, len(rr["A"]))); geo[tmpl] = {"Q": Qp_, "qpre": Qp_[:-1], "ids": list(rr["A"].ids)}
                for side in ("A", "B"):
                    sc4, fl4, (acts, lgx) = score4(list(rr[side].ids), fp); n += sum(len(v) for v in SP.values()); tag = f"{b}|{tmpl}_{'clean' if side == 'A' else 'donor'}"
                    for k, v in sc4.items(): RAW[f"{tag}|{k}"] = np.float32(v); RAW[f"{tag}|lpf_{k}"] = np.array(fl4[k], np.float32)
                    RAWZ[f"{tag}|zq"] = ro.z(acts, Qp_, LZ)[:, :, zc_c(p)].astype(np.float16); RAW[f"{tag}|greedy"] = tok.decode(int(lgx[0, len(rr[side].ids) - 1].argmax())).strip()
                    st[(tmpl, side)] = {l: acts[l][0, Qp_[:-1], :].float().clone() for l in SWAP_L}
                    if side == "A": st[(tmpl, "acts")] = acts
                    else: del acts
            dcap = {l: st[("cap", "B")][l] - st[("cap", "A")][l] for l in SWAP_L}; dlang = {l: st[("lang", "B")][l] - st[("lang", "A")][l] for l in SWAP_L}
            g1 = torch.Generator().manual_seed(SEED + 500000 + ci_); g2 = torch.Generator().manual_seed(SEED + 550000 + ci_); proj = {}; cosCY = []
            for l in SWAP_L:
                Qc = torch.linalg.qr(torch.stack([NAMING[p["own_country"]][l], NAMING[p["donor_country"]][l]], 1).float())[0]; Qy = torch.linalg.qr(torch.stack([NAMING[p["A"]][l], NAMING[p["B"]][l]], 1).float())[0]
                cosCY.append(float(torch.linalg.svdvals(Qc.T @ Qy).max()))
                for nmD, D_, g in (("cap", dcap, g1), ("lang", dlang, g2)):
                    vc = (D_[l] @ Qc) @ Qc.T; vy = (D_[l] @ Qy) @ Qy.T; R2 = Q.random_frame(d, 2, g, dev); vr = (D_[l] @ R2) @ R2.T; vr = vr * (vc.norm(dim=1, keepdim=True) / vr.norm(dim=1, keepdim=True).clamp_min(1e-12))
                    assert torch.allclose(vr.norm(dim=1), vc.norm(dim=1), rtol=1e-4, atol=1e-6)
                    proj[(nmD, l)] = {"ctry": vc, "city": vy, "noctry": D_[l] - vc, "nocity": D_[l] - vy, "rand2": vr, "full": D_[l]}
            rowspec = {"q_xfer": ("lang", "cap", "full"), "q_native_lang": ("lang", "lang", "full"), "x_ctry": ("lang", "cap", "ctry"), "x_city": ("lang", "cap", "city"),
                       "x_noctry": ("lang", "cap", "noctry"), "x_nocity": ("lang", "cap", "nocity"), "x_rand2": ("lang", "cap", "rand2"),
                       "q_mirror": ("cap", "lang", "full"), "q_native_cap": ("cap", "cap", "full"), "m_ctry": ("cap", "lang", "ctry"), "m_city": ("cap", "lang", "city"),
                       "m_noctry": ("cap", "lang", "noctry"), "m_nocity": ("cap", "lang", "nocity"), "m_rand2": ("cap", "lang", "rand2")}
            for cond, (tmpl, src, part) in rowspec.items():
                g_ = geo[tmpl]; base = st[(tmpl, "A")]; Tt = {l: base[l] + proj[(src, l)][part] for l in SWAP_L}; clean_acts = st[(tmpl, "acts")]
                sc4, fl4, (a_, l_) = score4(g_["ids"], lambda Tt=Tt, g_=g_: H.Both(fp(), H.SpanWriter(lm.layers, SWAP_L, g_["qpre"], Tt))); n += sum(len(v) for v in SP.values()); tag = f"{b}|{cond}"
                for k, v in sc4.items(): RAW[f"{tag}|{k}"] = np.float32(v); RAW[f"{tag}|lpf_{k}"] = np.array(fl4[k], np.float32)
                assert all(torch.equal(a_[l][0, :g_["qpre"][0], :], clean_acts[l][0, :g_["qpre"][0], :]) for l in ALL), f"prefix touched {tag}"
                req = torch.stack([(Tt[l] - base[l]).flatten() for l in SWAP_L]); real = torch.stack([(a_[l][0, g_["qpre"], :].float() - base[l]).flatten() for l in SWAP_L])
                RAW[f"{tag}|rho"] = np.float32(float((real.norm(dim=1) / req.norm(dim=1).clamp_min(1e-8)).mean())); RAW[f"{tag}|kappa"] = np.float32(float(torch.nn.functional.cosine_similarity(real, req, dim=1).mean()))
                RAWZ[f"{tag}|zq"] = ro.z(a_, g_["Q"], LZ)[:, :, zc_c(p)].astype(np.float16); RAW[f"{tag}|greedy"] = tok.decode(int(l_[0, len(g_["ids"]) - 1].argmax())).strip(); del a_
            META["cells_c"][b] = {**{k: v for k, v in p.items() if k != "it"}, "zq_columns": [COLS[i] for i in zc_c(p)], "max_principal_cos_country_city_planes_L51_59": float(np.mean(cosCY[15:24]))}
            del st; torch.cuda.empty_cache()
            m = lambda c, tm, basec: float((RAW[f"{b}|{c}|donor_{tm}"] - RAW[f"{b}|{c}|own_{tm}"]) - (RAW[f"{b}|{basec}|donor_{tm}"] - RAW[f"{b}|{basec}|own_{tm}"]))
            print(f"  [X] {b}: {n} forwards ({time.time()-tc:.0f}s) | language q., push to donor language: xfer {m('q_xfer', 'lang', 'lang_clean'):+.2f} ctry {m('x_ctry', 'lang', 'lang_clean'):+.2f} city {m('x_city', 'lang', 'lang_clean'):+.2f} "
                  f"noctry {m('x_noctry', 'lang', 'lang_clean'):+.2f} nocity {m('x_nocity', 'lang', 'lang_clean'):+.2f} rand2 {m('x_rand2', 'lang', 'lang_clean'):+.2f}", flush=True)
    bc = list(META["cells_c"])
    META["competence_c"] = {"cap_clean": float(np.mean([RAW[f"{b}|cap_clean|own_cap"] > RAW[f"{b}|cap_clean|donor_cap"] for b in bc])), "cap_donor": float(np.mean([RAW[f"{b}|cap_donor|donor_cap"] > RAW[f"{b}|cap_donor|own_cap"] for b in bc])),
                            "lang_clean": float(np.mean([RAW[f"{b}|lang_clean|own_lang"] > RAW[f"{b}|lang_clean|donor_lang"] for b in bc])), "lang_donor": float(np.mean([RAW[f"{b}|lang_donor|donor_lang"] > RAW[f"{b}|lang_donor|own_lang"] for b in bc]))}
    META["competence_ab"] = {"clean": float(np.mean([RAW[f"{b}|clean|seq_answer"] > RAW[f"{b}|clean|seq_swap"] for b in bases])), "donor": float(np.mean([RAW[f"{b}|donor|seq_swap"] > RAW[f"{b}|donor|seq_answer"] for b in bases]))}
    META.update({"run_id": RUN_ID, "n_forwards": n, "elapsed_s": round(time.time() - t0, 1)})
    np.savez_compressed(os.path.join(OUT, f"raw_{STAGE}.npz"), **RAW); np.savez_compressed(os.path.join(OUT, f"raw_{STAGE}_zq.npz"), **RAWZ)
    json.dump(META, open(os.path.join(OUT, f"meta_{STAGE}.json"), "w"), indent=1, default=str)
    sha = lambda f: hashlib.sha256(open(os.path.join(OUT, f), "rb").read()).hexdigest()
    man = R.manifest_block(); man.update({"run_id": RUN_ID, "stage": STAGE, "script": os.path.relpath(__file__, R.PROJECT), "design": META["design"], "raw_sha256": sha(f"raw_{STAGE}.npz"), "raw_zq_sha256": sha(f"raw_{STAGE}_zq.npz")})
    json.dump(man, open(os.path.join(OUT, f"manifest_{STAGE}.json"), "w"), indent=1)
    print(f"[done {STAGE}] {n} forwards, {time.time()-t0:.0f}s | competence ab {META['competence_ab']} c {META['competence_c']} | clamp stats {META['clamp_stats']} | leak max {max(META['leak'].values()) if META['leak'] else float('nan'):.1e}")


if __name__ == "__main__":
    main()
