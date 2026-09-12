"""Copy of H3/scripts/query_local_workspace.py with one added stage, `clampfix32` (Amendment 4, this folder: AMENDMENT_4.md).
The shipped script is untouched; outputs land in this folder. Original header follows.

H3 query_local_workspace (design: H3/design_specs/query_local_workspace.md, registered 2026-09-09).

Is the sum reconstructed into a consumer-local representation at the question positions, and does the answer
depend on it? Plus: is the carrier copy consumable when the operands are absent from the prompt entirely?

Stages: smoke | queryread | querycausal | nosource
Parity is the primary consumer for every coordinate-level intervention (report emits the swapped tokens).
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
import hooks_fp32 as H32

STAGE = sys.argv[1] if len(sys.argv) > 1 else "smoke"
assert STAGE == "clampfix32", "this copy runs only the Amendment 4 stage"
FP32 = True                          # Amendment 4: clampfix conditions under the float32 residual regime from block 35 on
OUT = R.out_dir("H3", "outputs", "query_local_workspace")
RUN_ID = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
SEED = 20260909
COPY = "copy the following text exactly, word for word"
SUMS = M.SUMS; SUM_WORDS = [s[0] for s in SUMS]
NUMS = ["two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen"]
DECOYS = M.FIT_WORDS[:8]; COLS = NUMS + DECOYS
CARRIERS = ["C0", "C1", "C2", "C3"]; OFF = 3
LX = 36; QL = list(range(36, 63))                       # question-site intervention band (36-62)
PAR_WORDS = ["even", "odd"]

pair_of = lambda i: SUMS[i][1]
sum_of = lambda i: SUMS[i][0]
donor_pair = lambda i: SUMS[(i + OFF) % 8][1]
donor_sum = lambda i: SUMS[(i + OFF) % 8][0]
pstr = lambda p: f"{p[0]} and {p[1]}"
parity_of = lambda w: ("odd" if (SUM_WORDS.index(w) + 7) % 2 else "even")
utext = lambda pair, car: f'Here is the pair "{pstr(pair)}". Keep their sum in mind while you {COPY}:\n\n' + car
# absent-source recipient: no operand tokens anywhere (length matched mechanically, see smoke/gate 3)
NS_TEXT = lambda car, filler: f'Here is the pair "{filler}". Keep their sum in mind while you {COPY}:\n\n' + car


def answer_ids(tok, words):
    out = {}
    for w in words:
        forms = []
        for form in (w, " " + w, w.capitalize(), " " + w.capitalize()):
            ids = tok(form, add_special_tokens=False).input_ids
            forms.append(ids[0] if len(ids) == 1 else -1)
        out[w] = forms
    return out


def score_words(tok, logits, WID, words):
    lp = torch.log_softmax(logits[0, -1].float(), -1)
    sc = {w: float(torch.logsumexp(torch.tensor([lp[t] for t in WID[w] if t >= 0]), 0)) for w in words}
    return sc, tok.decode(int(logits[0, -1].argmax())).strip()


def ns_filler(tok, pair_str):
    """A filler for the absent-source rendering with the same token count as the operand string and no number words."""
    cands = ["a and b", "one thing and another", "the first and the second", "this one and that one",
             "something and something else", "an item and an item", "x and y", "the pair and the pair"]
    tgt = len(tok(pair_str, add_special_tokens=False).input_ids)
    for c in cands:
        if len(tok(c, add_special_tokens=False).input_ids) == tgt and not any(nw in c for nw in NUMS):
            return c
    return None


def smoke():
    tok = R.make_tokenizer()
    q = "Is their sum even or odd? Answer even or odd."
    ok = 0; miss = []
    for ck in CARRIERS:
        car = M.CARRIERS[ck]
        for i in range(8):
            p, d = pair_of(i), donor_pair(i)
            r = Rn.render(tok, utext(p, car), car, sources=[("P", pstr(p), True)], extra_turns=[(q, "")])
            rd = Rn.render(tok, utext(d, car), car, sources=[("P", pstr(d), True)], extra_turns=[(q, "")])
            f = ns_filler(tok, pstr(p))
            if f is None:
                miss.append((sum_of(i), pstr(p))); continue
            rn = Rn.render(tok, NS_TEXT(car, f), car, sources=[("P", f, True)], extra_turns=[(q, "")])
            ok += int(len(rd) == len(r) == len(rn) and rd.meta["carrier_start"] == r.meta["carrier_start"] == rn.meta["carrier_start"]
                      and rd.meta["carrier_end"] == r.meta["carrier_end"] == rn.meta["carrier_end"])
    print(f"length/span match (recipient, donor, absent-source): {ok}/32; no filler for: {miss}")
    r = Rn.render(tok, NS_TEXT(M.CARRIERS['C0'], ns_filler(tok, pstr(pair_of(0)))), M.CARRIERS['C0'],
                  sources=[("P", ns_filler(tok, pstr(pair_of(0))), True)], extra_turns=[(q, "")])
    print("absent-source rendering:\n" + r.meta["full"][:420].replace("\n", " | "))
    print("SMOKE OK" if ok == 32 else "SMOKE FAIL")


def nosource(tok, run, lm, ro, ALL, SRC, QL, CONSUMERS, PDIR, PCENT, PAIR, COLIDS, RAW, META, t0):
    """Absent-source recipient: no operand tokens anywhere. Carrier (all 64 blocks) or question positions (36-62) are
    installed from a real run with sum S (own) or S2 (donor); the endpoint is whether the answer becomes S / S2."""
    n = 0
    for ck in CARRIERS:
        car = M.CARRIERS[ck]
        for i in range(8):
            pair, dpair = pair_of(i), donor_pair(i); base = f"S{i}|{ck}"
            filler = ns_filler(tok, pstr(pair)); assert filler is not None
            META["cells"][base] = {"sum": sum_of(i), "donor_sum": donor_sum(i), "pair": list(pair), "donor": list(dpair), "filler": filler,
                                   "own_parity": parity_of(sum_of(i)), "donor_parity": parity_of(donor_sum(i))}
            for cname, (q, words, WID) in CONSUMERS.items():
                if STAGE == "nosource2":
                    rn = Rn.render(tok, f"Here is a pair of numbers (hidden). Keep their sum in mind while you {COPY}:\n\n" + car, car, sources=[], extra_turns=[(q, "")])
                else:
                    rn = Rn.render(tok, NS_TEXT(car, filler), car, sources=[("P", filler, True)], extra_turns=[(q, "")])
                rS = Rn.render(tok, utext(pair, car), car, sources=[("P", pstr(pair), True)], extra_turns=[(q, "")])
                rS2 = Rn.render(tok, utext(dpair, car), car, sources=[("P", pstr(dpair), True)], extra_turns=[(q, "")])
                cs, ce = rn.meta["carrier_start"], rn.meta["carrier_end"]
                assert len(rn) == len(rS) == len(rS2) and rS.meta["carrier_start"] == rS2.meta["carrier_start"] == cs and rS.meta["carrier_end"] == rS2.meta["carrier_end"] == ce, f"nosource length {base} {cname}"
                carr = list(range(cs, ce)); Q = list(range(ce, len(rn)))
                ac, lg = run(rn.ids); n += 1
                z0 = torch.zeros(len(ALL), R.D_MODEL, device=ac[0].device)
                # record helper (same fields as rec, inline to keep this stage self-contained)
                def recn(tag, logits, acts, h_clean):
                    sc, top = score_words(tok, logits, WID, words)
                    RAW[f"{tag}|scores"] = np.array([sc[w] for w in words], np.float32); RAW[f"{tag}|greedy"] = top
                    for site, pos in (("carr", rn.interior), ("q", Q)):
                        RAW[f"{tag}|z_{site}"] = ro.z(acts, pos, SRC).astype(np.float16)
                        hs = torch.stack([acts[l][0, pos, :].float() for l in ALL])
                        RAW[f"{tag}|ppres_{site}"] = torch.stack([((hs * PDIR[w][:, None, :]).sum(-1) - PCENT[w][:, None]).mean(-1) for w in SUM_WORDS], 1).cpu().numpy().astype(np.float32)
                        RAW[f"{tag}|ppair_{site}"] = (hs * PAIR[(sum_of(i), donor_sum(i))][:, None, :]).sum(-1).mean(-1).cpu().numpy().astype(np.float32)
                        lp = torch.log_softmax(logits[0, pos, :].float(), -1)
                        RAW[f"{tag}|lp_{site}"] = lp[:, COLIDS].mean(0).cpu().numpy().astype(np.float32)
                    nll, _, _ = RO.carrier_damage(logits, rn.ids, cs, ce); RAW[f"{tag}|nll"] = np.float32(nll)
                    h_ans = torch.stack([acts[l][0, -1, :].float() for l in ALL])
                    RAW[f"{tag}|ans_dist"] = (h_ans - h_clean).norm(dim=-1).cpu().numpy().astype(np.float32)
                    return h_ans
                h0 = recn(f"{base}|{cname}|clean_ns", lg, ac, z0); RAW[f"{base}|{cname}|clean_ns|ans_dist"] = np.zeros(len(ALL), np.float32)
                aS, _ = run(rS.ids); n += 1; CS = {l: aS[l][0, carr, :].clone() for l in ALL}; QS = {l: aS[l][0, Q, :].clone() for l in QL}; del aS
                aS2, _ = run(rS2.ids); n += 1; CS2 = {l: aS2[l][0, carr, :].clone() for l in ALL}; del aS2
                g = torch.Generator(device="cpu").manual_seed(SEED + 17 * i + CARRIERS.index(ck) + (0 if cname == "parity" else 5))
                Crand = {}
                for l in ALL:
                    hC = ac[l][0, carr, :].float(); dn = (CS[l].float() - hC).norm(dim=1, keepdim=True)
                    v = torch.randn(len(carr), hC.shape[1], generator=g).to(hC.device)
                    Crand[l] = (hC + v / v.norm(dim=1, keepdim=True) * dn).to(ac[l].dtype)
                conds = {"C_from_S": lambda: H.SpanWriter(lm.layers, ALL, carr, CS),
                         "C_from_S2": lambda: H.SpanWriter(lm.layers, ALL, carr, CS2),
                         "C_rand_ns": lambda: H.SpanWriter(lm.layers, ALL, carr, Crand),
                         "Q_from_S": lambda: H.SpanWriter(lm.layers, QL, Q, QS)}
                pre = list(range(0, cs))
                for cond, mk in conds.items():
                    a_, l_ = run(rn.ids, mk()); n += 1
                    assert all(torch.equal(a_[l][0, pre, :], ac[l][0, pre, :]) for l in ALL), f"prefix touched {base} {cname} {cond}"
                    recn(f"{base}|{cname}|{cond}", l_, a_, h0); del a_
                del ac
        print(f"  [nosource] {ck}: {n} forwards ({time.time()-t0:.0f}s)", flush=True)
    META["n_forwards"] = n


def main():
    if STAGE == "smoke":
        smoke(); return
    tok = R.make_tokenizer()
    TID = {w: Rn.single_token_id(tok, w) for w in COLS}
    assert all(v is not None for v in TID.values())
    from jlens.hf import from_hf
    model = R.load_model(); lm = from_hf(model, tok, compile=False)
    ALL = list(range(R.N_BLOCKS)); SRC = list(range(R.N_SRC)); run0 = H.make_run(model, lm, ALL)
    run = lambda ids, ctx=None: run0(ids, H.Both(H32.Fp32Residual(lm.layers, LX - 1), ctx))   # every forward in the regime
    LEN = R.load_lenses(("J_NP",))["J_NP"]; ro = RO.LensReadout(model, lm, LEN, [TID[w] for w in COLS])
    lge = [l for l in ALL if l >= LX]
    CONSUMERS = {"parity": ("Is their sum even or odd? Answer even or odd.", PAR_WORDS, answer_ids(tok, PAR_WORDS)),
                 "report": ("What is the sum of the pair? Answer with one word.", SUM_WORDS, answer_ids(tok, SUM_WORDS))}
    RAW, META = {}, {"columns": COLS, "sum_words": SUM_WORDS, "decoys": DECOYS, "seed": SEED, "stage": STAGE,
                     "carriers": CARRIERS, "map": OFF, "lx": LX, "q_layers": [QL[0], QL[-1]], "cells": {},
                     "token_ids": TID, "primary_consumer": "parity (report is steering-susceptible for coordinate writes)",
                     "regime": ("float32 residual from block %d on, bf16 autocast (Amendment 4)" % (LX - 1)) if FP32 else "bf16"}
    t0 = time.time(); n = 0
    # RESID_P number axis (same construction as computed_sum_consumer robust/global)
    MU = {}
    for w in COLS:
        for split, tpls in (("fit", M.NUMBER_FIT), ("val", M.NUMBER_VAL)):
            acc = []
            for tpl in tpls:
                s_ = tpl.format(m=w); enc = tok(s_, add_special_tokens=False, return_offsets_mapping=True)
                ce_ = tpl.index("{m}") + len(w) - 1
                p_ = next(k for k, (a, b) in enumerate(enc.offset_mapping) if a <= ce_ < b)
                a_, _ = run(enc.input_ids); n += 1
                acc.append(torch.stack([a_[l][0, p_, :].float() for l in ALL])); del a_
            MU[(w, split)] = torch.stack(acc).mean(0)
    dec_cent = torch.stack([MU[(d, "fit")] for d in DECOYS]).mean(0)
    PDIR = {w: (MU[(w, "fit")] - dec_cent) / (MU[(w, "fit")] - dec_cent).norm(dim=-1, keepdim=True) for w in SUM_WORDS}
    PCENT = {w: (PDIR[w] * dec_cent).sum(-1) for w in SUM_WORDS}
    PAIR = {}
    for i in range(8):
        o, d = sum_of(i), donor_sum(i); v = MU[(d, "fit")] - MU[(o, "fit")]; PAIR[(o, d)] = v / v.norm(dim=-1, keepdim=True)
    NAMING = {w: {l: ro.folded_direction(l, TID[w]) for l in QL} for w in SUM_WORDS}
    COLIDS = [TID[w] for w in COLS]
    print(f"  [{STAGE}] axis fitted ({n} forwards, {time.time()-t0:.0f}s)", flush=True)

    def rec(tag, r, logits, acts, words, WID, i, qpos, h_clean_ans):
        """Record at BOTH the carrier interior and the question positions."""
        sc, top = score_words(tok, logits, WID, words)
        RAW[f"{tag}|scores"] = np.array([sc[w] for w in words], np.float32); RAW[f"{tag}|greedy"] = top
        for site, pos in (("carr", r.interior), ("q", qpos)):
            RAW[f"{tag}|z_{site}"] = ro.z(acts, pos, SRC).astype(np.float16)
            hs = torch.stack([acts[l][0, pos, :].float() for l in ALL])
            RAW[f"{tag}|ppres_{site}"] = torch.stack([((hs * PDIR[w][:, None, :]).sum(-1) - PCENT[w][:, None]).mean(-1) for w in SUM_WORDS], 1).cpu().numpy().astype(np.float32)
            RAW[f"{tag}|ppair_{site}"] = (hs * PAIR[(sum_of(i), donor_sum(i))][:, None, :]).sum(-1).mean(-1).cpu().numpy().astype(np.float32)
            lp = torch.log_softmax(logits[0, pos, :].float(), -1)
            RAW[f"{tag}|lp_{site}"] = lp[:, COLIDS].mean(0).cpu().numpy().astype(np.float32)
        cs, ce = r.meta["carrier_start"], r.meta["carrier_end"]; nll, _, _ = RO.carrier_damage(logits, r.ids, cs, ce)
        RAW[f"{tag}|nll"] = np.float32(nll)
        h_ans = torch.stack([acts[l][0, -1, :].float() for l in ALL])
        RAW[f"{tag}|ans_dist"] = (h_ans - h_clean_ans).norm(dim=-1).cpu().numpy().astype(np.float32)
        return h_ans

    if STAGE in ("nosource", "nosource2"):
        nosource(tok, run, lm, ro, ALL, SRC, QL, CONSUMERS, PDIR, PCENT, PAIR, COLIDS, RAW, META, t0)
        n += META["n_forwards"]
    for ck in (CARRIERS if STAGE not in ("nosource", "nosource2") else []):
        car = M.CARRIERS[ck]
        for i in range(8):
            pair, dpair = pair_of(i), donor_pair(i); base = f"S{i}|{ck}"
            META["cells"][base] = {"sum": sum_of(i), "donor_sum": donor_sum(i), "pair": list(pair), "donor": list(dpair),
                                   "own_parity": parity_of(sum_of(i)), "donor_parity": parity_of(donor_sum(i))}
            assert parity_of(donor_sum(i)) != parity_of(sum_of(i))
            for cname, (q, words, WID) in CONSUMERS.items():
                r = Rn.render(tok, utext(pair, car), car, sources=[("P", pstr(pair), True)], extra_turns=[(q, "")])
                span = r.spans["P"]["full"]; cs, ce = r.meta["carrier_start"], r.meta["carrier_end"]
                carr = list(range(cs, ce)); Q = list(range(ce, len(r)))
                META["cells"][base][f"{cname}_pos"] = {"span": [span[0], span[-1]], "carrier": [cs, ce], "Q": [ce, len(r)]}
                ac, lg = run(r.ids); n += 1
                z0 = torch.zeros(len(ALL), R.D_MODEL, device=ac[0].device)
                h0 = rec(f"{base}|{cname}|clean", r, lg, ac, words, WID, i, Q, z0)
                RAW[f"{base}|{cname}|clean|ans_dist"] = np.zeros(len(ALL), np.float32)
                rd = Rn.render(tok, utext(dpair, car), car, sources=[("P", pstr(dpair), True)], extra_turns=[(q, "")])
                assert len(rd) == len(r) and rd.spans["P"]["full"] == span and rd.meta["carrier_start"] == cs and rd.meta["carrier_end"] == ce
                add, _ = run(rd.ids); n += 1
                O_src = {l: add[l][0, span, :].clone() for l in ALL}
                C_src = {l: add[l][0, carr, :].clone() for l in ALL}
                Q_src = {l: add[l][0, Q, :].clone() for l in ALL}
                own_carr = {l: ac[l][0, carr, :].clone() for l in lge}
                dirs = {l: (NAMING[sum_of(i)][l], NAMING[donor_sum(i)][l]) for l in QL}
                cref = H.plane_coords(ac, Q, QL, dirs)                       # clean coordinates at Q

                if STAGE == "queryread":
                    conds = {"O_donor": lambda: H.SpanWriter(lm.layers, lge, span, {l: O_src[l] for l in lge}),
                             "C_full": lambda: H.SpanWriter(lm.layers, lge, carr, {l: C_src[l] for l in lge}),
                             "NEC": lambda: H.Both(H.SpanWriter(lm.layers, lge, span, {l: O_src[l] for l in lge}),
                                                   H.SpanWriter(lm.layers, lge, carr, own_carr))}
                elif STAGE == "clampsplit":
                    Qna, Qans = Q[:-1], Q[-1:]
                    cref_na = H.plane_coords(ac, Qna, QL, dirs); cref_an = H.plane_coords(ac, Qans, QL, dirs)
                    conds = {
                        "NEC": lambda: H.Both(H.SpanWriter(lm.layers, lge, span, {l: O_src[l] for l in lge}), H.SpanWriter(lm.layers, lge, carr, own_carr)),
                        "NEC_Qclamp_noans": lambda: H.Both(H.SpanWriter(lm.layers, lge, span, {l: O_src[l] for l in lge}), H.SpanWriter(lm.layers, lge, carr, own_carr),
                                                           H.CoordClamp(lm.layers, QL, Qna, dirs, cref_na)),
                        "NEC_Qclamp_ansonly": lambda: H.Both(H.SpanWriter(lm.layers, lge, span, {l: O_src[l] for l in lge}), H.SpanWriter(lm.layers, lge, carr, own_carr),
                                                             H.CoordClamp(lm.layers, QL, Qans, dirs, cref_an)),
                    }
                elif STAGE in ("clampfix", "clampfix32"):   # Amendment 3: norm-matched orthogonal controls + realized post-cast write; Amendment 4: same in float32
                    g = torch.Generator(device="cpu").manual_seed(SEED + 11 * i + CARRIERS.index(ck) + (0 if cname == "parity" else 5))
                    pdirs = {}
                    for l in QL:
                        v0, v1 = dirs[l]; B = torch.stack([v0, v1], 1)
                        Rr = torch.randn(B.shape[0], 2, generator=g).to(B.device).to(B.dtype)
                        Rr = Rr - B @ (torch.linalg.pinv(B) @ Rr)
                        Rr = Rr / Rr.norm(dim=0, keepdim=True)
                        pdirs[l] = (Rr[:, 0], Rr[:, 1])
                    Qna, Qans = Q[:-1], Q[-1:]
                    CR = {"all": (Q, H.plane_coords(ac, Q, QL, dirs), H.plane_coords(ac, Q, QL, pdirs)),
                          "noans": (Qna, H.plane_coords(ac, Qna, QL, dirs), H.plane_coords(ac, Qna, QL, pdirs)),
                          "ansonly": (Qans, H.plane_coords(ac, Qans, QL, dirs), H.plane_coords(ac, Qans, QL, pdirs))}
                    NECw = lambda: (H.SpanWriter(lm.layers, lge, span, {l: O_src[l] for l in lge}), H.SpanWriter(lm.layers, lge, carr, own_carr))
                    TARGET = {}
                    def mk_clamp(which, perp):
                        pos, cn, cp = CR[which]
                        if not perp: return H.Both(*NECw(), H32.CoordClampMatched(lm.layers, QL, pos, dirs, cn))
                        return H.Both(*NECw(), H32.CoordClampMatched(lm.layers, QL, pos, pdirs, cp, target=TARGET[which]))
                    conds = {"NEC": lambda: H.Both(*NECw())}
                    for which, nm in (("all", "NEC_Qclamp"), ("noans", "NEC_Qclamp_noans"), ("ansonly", "NEC_Qclamp_ansonly")):
                        conds[nm] = (lambda w=which: mk_clamp(w, False)); conds[nm + "_perpm"] = (lambda w=which: mk_clamp(w, True))
                else:   # querycausal
                    g = torch.Generator(device="cpu").manual_seed(SEED + 11 * i + CARRIERS.index(ck) + (0 if cname == "parity" else 5))
                    Qrand = {}
                    for l in QL:
                        hQ = ac[l][0, Q, :].float(); dn = (Q_src[l].float() - hQ).norm(dim=1, keepdim=True)
                        v = torch.randn(len(Q), hQ.shape[1], generator=g).to(hQ.device)
                        Qrand[l] = (hQ + v / v.norm(dim=1, keepdim=True) * dn).to(ac[l].dtype)
                    # matched control plane: random 2-plane orthogonalised against the naming plane
                    pdirs = {}
                    for l in QL:
                        v0, v1 = dirs[l]; B = torch.stack([v0, v1], 1)
                        Rr = torch.randn(B.shape[0], 2, generator=g).to(B.device).to(B.dtype)
                        Rr = Rr - B @ (torch.linalg.pinv(B) @ Rr)
                        Rr = Rr / Rr.norm(dim=0, keepdim=True)
                        pdirs[l] = (Rr[:, 0], Rr[:, 1])
                    pref = H.plane_coords(ac, Q, QL, pdirs)
                    conds = {
                        "Q_own": lambda: H.SpanWriter(lm.layers, QL, Q, {l: ac[l][0, Q, :].clone() for l in QL}),
                        "Q_donor_50": lambda: H.SpanWriter(lm.layers, list(range(36, 51)), Q, {l: Q_src[l] for l in range(36, 51)}),
                        "Q_donor_62": lambda: H.SpanWriter(lm.layers, QL, Q, {l: Q_src[l] for l in QL}),
                        "Q_rand": lambda: H.SpanWriter(lm.layers, QL, Q, Qrand),
                        "Q_swap": lambda: H.CoordSwap(lm.layers, QL, Q, dirs),
                        "NEC_Qclamp": lambda: H.Both(H.SpanWriter(lm.layers, lge, span, {l: O_src[l] for l in lge}),
                                                     H.SpanWriter(lm.layers, lge, carr, own_carr),
                                                     H.CoordClamp(lm.layers, QL, Q, dirs, cref)),
                        "NEC_Qclamp_perp": lambda: H.Both(H.SpanWriter(lm.layers, lge, span, {l: O_src[l] for l in lge}),
                                                          H.SpanWriter(lm.layers, lge, carr, own_carr),
                                                          H.CoordClamp(lm.layers, QL, Q, pdirs, pref)),
                        "NEC": lambda: H.Both(H.SpanWriter(lm.layers, lge, span, {l: O_src[l] for l in lge}),
                                              H.SpanWriter(lm.layers, lge, carr, own_carr)),
                    }
                for cond, mk in conds.items():
                    ctx = mk(); a_, l_ = run(r.ids, ctx); n += 1
                    tag = f"{base}|{cname}|{cond}"
                    rec(tag, r, l_, a_, words, WID, i, Q, h0)
                    if cond == "Q_own":
                        META["cells"][base][f"{cname}_Qown_bitwise"] = bool(torch.equal(l_, lg) and all(torch.equal(a_[l], ac[l]) for l in ALL))
                    if cond.startswith("Q_") or cond.endswith("clamp") or cond.endswith("perp"):
                        assert all(torch.equal(a_[l][0, :ce, :], ac[l][0, :ce, :]) for l in ALL) or not cond.startswith("Q_"), f"Q write touched prefix {tag}"
                    if STAGE in ("clampfix", "clampfix32") and "clamp" in cond:
                        cl = [x for x in ctx.c if isinstance(x, H32.CoordClampMatched)][0]
                        which = "all" if cond.startswith("NEC_Qclamp_perpm") or cond == "NEC_Qclamp" else ("noans" if "noans" in cond else "ansonly")
                        if not cond.endswith("_perpm"): TARGET[which] = {l: cl.post[l]["norms_req"] for l in QL}
                        RAW[f"{tag}|clampnorm"] = np.array([cl.realized[l] for l in QL], np.float32)
                        RAW[f"{tag}|rho"] = np.array([cl.post[l]["rho"] for l in QL], np.float32)
                        RAW[f"{tag}|kappa"] = np.array([cl.post[l]["kappa"] for l in QL], np.float32)
                        RAW[f"{tag}|realnorm"] = np.array([float(cl.post[l]["norms_real"].mean()) for l in QL], np.float32)
                        pos_, cn_, cp_ = CR[which]; ref_ = cp_ if cond.endswith("_perpm") else cn_
                        if not cond.endswith("_perpm"):
                            got = H.plane_coords(a_, pos_, QL, dirs)
                            RAW[f"{tag}|clamperr"] = np.float32(max(float((got[l] - cn_[l].to(got[l].device)).abs().max()) for l in QL))
                    if cond in ("NEC_Qclamp", "NEC_Qclamp_perp") and STAGE not in ("clampfix", "clampfix32"):
                        cl = [x for x in ctx.c if isinstance(x, H.CoordClamp)][0]
                        RAW[f"{tag}|clampnorm"] = np.array([cl.realized.get(l, np.nan) for l in QL], np.float32)
                        got = H.plane_coords(a_, Q, QL, dirs if cond == "NEC_Qclamp" else pdirs)
                        RAW[f"{tag}|clamperr"] = np.float32(max(float((got[l] - (cref if cond == "NEC_Qclamp" else pref)[l].to(got[l].device)).abs().max()) for l in QL))
                    del a_
                del ac
        print(f"  [{STAGE}] {ck}: {n} forwards ({time.time()-t0:.0f}s)", flush=True)

    META.update({"run_id": RUN_ID, "n_forwards": n, "elapsed_s": round(time.time() - t0, 1)})
    np.savez_compressed(os.path.join(OUT, f"raw_{STAGE}.npz"), **RAW)
    json.dump(META, open(os.path.join(OUT, f"meta_{STAGE}.json"), "w"), indent=1)
    man = R.manifest_block(); man.update({"run_id": RUN_ID, "stage": STAGE, "script": os.path.relpath(__file__, R.PROJECT),
                                          "design": "H3/design_specs/query_local_workspace.md (Amendment 4)",
                                          "raw_sha256": hashlib.sha256(open(os.path.join(OUT, f"raw_{STAGE}.npz"), "rb").read()).hexdigest()})
    json.dump(man, open(os.path.join(OUT, f"manifest_{STAGE}.json"), "w"), indent=1)
    print(f"[done {STAGE}] {n} forwards, {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
