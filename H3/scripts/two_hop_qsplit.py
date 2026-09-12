"""H3 two_hop_organism stage `qsplit` (design: H3/design_specs/two_hop_organism.md, Amendment 5).

The H3.3 ladder at the question-turn cut (scoring position excluded), float32 residual regime, sequence endpoint:
full residual donor vs the intermediate's two-token naming-plane component vs its complement, with norm-matched
random-plane controls. Every row is a fixed per-block target T_l = h_l^clean + M_l (h_l^donor - h_l^clean) written
with SpanWriter at blocks 36-62 on the `q_pre` positions. Usage: two_hop_qsplit.py smoke|qsplit
"""
import os, sys, json, time, hashlib, re
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "..", "common", "scripts"))
import numpy as np, torch
import registry as R, materials as M, rendering as Rn, readout as RO, hooks as H
from hooks_fp32 import Fp32Residual

STAGE = sys.argv[1] if len(sys.argv) > 1 else "smoke"; assert STAGE in ("smoke", "qsplit")
OUT = R.out_dir("H3", "outputs", "two_hop_organism")
RUN_ID = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()); SEED = 20260911; FP32_FROM = 35
COPY = "copy the following text exactly, word for word"; CARRIERS = ["C0", "C1", "C2", "C3"]; DECOYS = M.FIT_WORDS[:8]
SWAP_L = list(range(36, 63)); RB = list(range(51, 60))
ITEMS = json.load(open(os.path.join(R.PROJECT, "H3", "design_specs", "two_hop_items.json")))["pilot_items"]
STRIP = re.compile(r"\s+(is called a|is called the|is the|is a|are|is)\s*$")
QUESTION = "Complete the fact from the clue you were given, using one word."
S_DONOR0_SEQ_BF16 = 23.87764283021291   # bridgeswap_seq ceiling, quoted for context (meta_bridgeswap_seq.json), not re-run
if STAGE == "smoke": ITEMS, CARRIERS = ITEMS[:1], CARRIERS[:1]

clue_body = lambda p: STRIP.sub("", p.replace("Fact: ", "").strip())
utext = lambda body, car: f"Here is a clue: {body}. Keep the answer to the clue in mind while you {COPY}:\n\n" + car


def spellings(tok, w):
    out = []
    for f in dict.fromkeys([w, w.capitalize(), " " + w, " " + w.capitalize()]):
        ids = tuple(tok(f, add_special_tokens=False).input_ids)
        if ids not in out: out.append(ids)
    return out


def forms(tok, w):
    out = []
    for f in (w, " " + w, w.capitalize(), " " + w.capitalize(), w.lower(), " " + w.lower()):
        ids = tok(f, add_special_tokens=False).input_ids
        if len(ids) == 1 and ids[0] not in out: out.append(ids[0])
    return out


class CoordSwap32(H.CoordSwap):
    """H.CoordSwap with the coordinate arithmetic forced to true float32 under the bf16 autocast."""
    def _mk(self, l):
        @torch.autocast("cuda", enabled=False)
        def f(m, i, o):
            h = H._out(o).clone(); hp = h[0, self.pos, :].float(); vs, vt = self.dirs[l]
            V = torch.stack([vs, vt], 1).to(hp.device).float(); pinv = torch.linalg.pinv(V)
            c = hp @ pinv.T; delta = (c[:, [1, 0]] - c) @ V.T
            self.realized[l] = float(delta.norm(dim=1).mean()); h[0, self.pos, :] = (hp + delta).to(h.dtype)
            return H._pack(o, h)
        return f


def main():
    tok = R.make_tokenizer()
    from jlens.hf import from_hf
    model = R.load_model(); lm = from_hf(model, tok, compile=False)
    ALL = list(range(R.N_BLOCKS)); SRC = list(range(R.N_SRC)); run = H.make_run(model, lm, ALL)
    LEN = R.load_lenses(("J_NP",))["J_NP"]
    words = sorted({it["intermediate"] for it in ITEMS} | {it["swap_to"] for it in ITEMS}); COLS = words + [d for d in DECOYS if d not in words]
    ans_words = sorted({it["answer"] for it in ITEMS} | {it["swap_answer"] for it in ITEMS})
    TID = {w: Rn.single_token_id(tok, w) for w in COLS + ans_words}; assert all(v is not None for v in TID.values()), TID
    ro = RO.LensReadout(model, lm, LEN, [TID[w] for w in COLS])
    NAMING = {w: {l: ro.folded_direction(l, TID[w]) for l in SWAP_L} for w in words}
    def unit(v): return v / v.norm()
    NAMING63 = {w: unit(ro.Wu[TID[w]].float() * ro.gamma) for w in words}   # identity transport at the final block (no J_63)
    RAW, META = {}, {"columns": COLS, "decoys": [d for d in DECOYS if d not in words], "carriers": CARRIERS, "swap_layers": [SWAP_L[0], SWAP_L[-1]],
                     "fp32_from": FP32_FROM, "seed": SEED, "stage": STAGE, "cells": {}, "items": ITEMS, "question": QUESTION,
                     "s_donor0_seq_bf16_quoted": S_DONOR0_SEQ_BF16, "readout_band": [RB[0], RB[-1]],
                     "materials": "anthropics/jacobian-lens@581d398 data/experiments/probe-swap.json"}
    t0 = time.time(); n = 0
    fp = lambda: Fp32Residual(lm.layers, FP32_FROM)

    def seqscore(ids, mk, cands):
        """logsumexp over spellings of the summed token log-probs; one forward per spelling under mk(). Returns also the
        first forward's acts/logits (the original positions are unchanged by the appended tokens: causal)."""
        vals, first = [], None
        for sp in cands:
            full = ids + list(sp); a_, lg = run(full, mk())
            lp = torch.log_softmax(lg[0, len(ids) - 1: len(full) - 1].float(), -1)
            vals.append(float(sum(lp[k, sp[k]] for k in range(len(sp)))))
            if first is None: first = (a_, lg)
            else: del a_
        return float(torch.logsumexp(torch.tensor(vals), 0)), vals, first

    def rec(tag, r, it, acts, logits, Q, qpre, Qp63):
        L = len(r.ids); lp = torch.log_softmax(logits[0, L - 1].float(), -1)
        RAW[f"{tag}|s_answer"] = np.float32(float(torch.logsumexp(lp[forms(tok, it["answer"])], 0)))
        RAW[f"{tag}|s_swap"] = np.float32(float(torch.logsumexp(lp[forms(tok, it["swap_answer"])], 0)))
        RAW[f"{tag}|greedy"] = tok.decode(int(logits[0, L - 1].argmax())).strip()
        RAW[f"{tag}|zq"] = ro.z(acts, Q, SRC).astype(np.float16)                     # J_NP at the q positions, all lens layers
        RAW[f"{tag}|zq_pre"] = ro.z(acts, qpre, SRC).astype(np.float16)
        cs, ce = r.meta["carrier_start"], r.meta["carrier_end"]; nll, _, _ = RO.carrier_damage(logits[:, :L], r.ids, cs, ce); RAW[f"{tag}|nll"] = np.float32(nll)
        h63 = acts[63][0, qpre, :].float(); RAW[f"{tag}|c63"] = (h63 @ Qp63).cpu().numpy().astype(np.float32)   # [P,2] projections on the raw unit directions (a_int, a_swap) at block 63; sign-safe

    cell_idx = 0
    for it in ITEMS:
        for ck in CARRIERS:
            car = M.CARRIERS[ck]; base = f"{it['name']}|{ck}"
            body, dbody = clue_body(it["prompt"]), clue_body(it["donor_prompt"])
            r = Rn.render(tok, utext(body, car), car, sources=[("CLUE", body, False)], extra_turns=[(QUESTION, "")])
            rd = Rn.render(tok, utext(dbody, car), car, sources=[("CLUE", dbody, False)], extra_turns=[(QUESTION, "")])
            assert len(rd) == len(r) and rd.spans["CLUE"]["full"] == r.spans["CLUE"]["full"] and rd.meta["carrier_start"] == r.meta["carrier_start"] and rd.meta["carrier_end"] == r.meta["carrier_end"], f"G3 donor geometry {base}"
            span = r.spans["CLUE"]["full"]; cs, ce = r.meta["carrier_start"], r.meta["carrier_end"]
            Q = list(range(ce, len(r))); qpre = Q[:-1]; scoring = Q[-1]
            assert scoring == len(r) - 1 == r.spans["answer"] and scoring not in qpre, f"scoring position {base}"
            assert list(r.ids[Q[0]:]) == list(rd.ids[Q[0]:]), f"gate 1: q span token ids differ between recipient and donor {base}"
            ids = list(r.ids); cA, cB = spellings(tok, it["answer"]), spellings(tok, it["swap_answer"])
            # directions and planes
            cos = {l: float(NAMING[it["intermediate"]][l] @ NAMING[it["swap_to"]][l]) for l in SWAP_L}
            Qp = {l: torch.linalg.qr(torch.stack([NAMING[it["intermediate"]][l], NAMING[it["swap_to"]][l]], 1).float())[0] for l in SWAP_L}
            Qp63 = torch.stack([NAMING63[it["intermediate"]], NAMING63[it["swap_to"]]], 1)   # raw unit directions, not orthogonalized (QR column signs are arbitrary)
            g = torch.Generator(device="cpu").manual_seed(SEED + cell_idx)
            Rp = {l: torch.linalg.qr(torch.randn(R.D_MODEL, 2, generator=g))[0].to(Qp[l].device) for l in SWAP_L}
            META["cells"][base] = {"intermediate": it["intermediate"], "swap_to": it["swap_to"], "answer": it["answer"], "swap_answer": it["swap_answer"],
                                   "span": [span[0], span[-1]], "carrier": [cs, ce], "q": [Q[0], Q[-1]], "q_pre": [qpre[0], qpre[-1]], "scoring": scoring,
                                   "n_tokens": len(r), "cos_int_swap_max_abs": float(max(abs(v) for v in cos.values())), "cos_int_swap": cos,
                                   "plane_degenerate": bool(max(abs(v) for v in cos.values()) > 0.9), "random_seed": SEED + cell_idx,
                                   "spellings_answer": [list(x) for x in cA], "spellings_swap": [list(x) for x in cB]}
            # clean32 and donor32 (fp32 regime), with the sequence endpoint
            sA, vA, (ac, lg) = seqscore(ids, fp, cA); sB, vB, _ = seqscore(ids, fp, cB); n += len(cA) + len(cB)
            RAW[f"{base}|clean|seq_answer"], RAW[f"{base}|clean|seq_swap"] = np.float32(sA), np.float32(sB); rec(f"{base}|clean", r, it, ac, lg, Q, qpre, Qp63)
            dA, _, (ad, lgd) = seqscore(list(rd.ids), fp, cA); dB, _, _ = seqscore(list(rd.ids), fp, cB); n += len(cA) + len(cB)
            RAW[f"{base}|donor|seq_answer"], RAW[f"{base}|donor|seq_swap"] = np.float32(dA), np.float32(dB); rec(f"{base}|donor", rd, it, ad, lgd, Q, qpre, Qp63)
            # fixed targets per block on q_pre
            T = {k: {} for k in ("q_full_pre", "q_plane_pre", "q_rem_pre", "q_rand_pre", "q_rem_rand_pre")}; normdiag = []
            for l in SWAP_L:
                h = ac[l][0, qpre, :].float(); hY = ad[l][0, qpre, :].float(); d = hY - h
                vJ = (d @ Qp[l]) @ Qp[l].T; vRr = (d @ Rp[l]) @ Rp[l].T
                s = vJ.norm(dim=1, keepdim=True) / vRr.norm(dim=1, keepdim=True).clamp_min(1e-12); vR = s * vRr
                assert torch.allclose(vR.norm(dim=1), vJ.norm(dim=1), rtol=1e-4, atol=1e-6), f"gate 3 norm match {base} {l}"
                T["q_full_pre"][l] = hY.clone(); T["q_plane_pre"][l] = h + vJ; T["q_rem_pre"][l] = h + d - vJ
                T["q_rand_pre"][l] = h + vR; T["q_rem_rand_pre"][l] = h + d - vR
                normdiag.append([float(d.norm(dim=1).mean()), float(vJ.norm(dim=1).mean()), float(vR.norm(dim=1).mean())])
            RAW[f"{base}|normdiag"] = np.array(normdiag, np.float32)          # per block: |dh|, |vJ|, |vR| (mean over q_pre positions)
            conds = {k: (lambda k=k: H.Both(fp(), H.SpanWriter(lm.layers, SWAP_L, qpre, T[k]))) for k in T}
            conds["int_q32"] = lambda: H.Both(fp(), CoordSwap32(lm.layers, SWAP_L, qpre, {l: (NAMING[it["intermediate"]][l], NAMING[it["swap_to"]][l]) for l in SWAP_L}))
            for cond, mk in conds.items():
                sA, vA, (a_, l_) = seqscore(ids, mk, cA); sB, vB, _ = seqscore(ids, mk, cB); n += len(cA) + len(cB); tag = f"{base}|{cond}"
                RAW[f"{tag}|seq_answer"], RAW[f"{tag}|seq_swap"] = np.float32(sA), np.float32(sB)
                RAW[f"{tag}|seq_answer_all"], RAW[f"{tag}|seq_swap_all"] = np.array(vA, np.float32), np.array(vB, np.float32)
                assert all(torch.equal(a_[l][0, :qpre[0], :], ac[l][0, :qpre[0], :]) for l in ALL), f"prefix touched {tag}"
                if cond in T:   # realized write vs the clean base, and read-back against the fixed target
                    req = torch.stack([(T[cond][l] - ac[l][0, qpre, :].float()).flatten() for l in SWAP_L]); real = torch.stack([(a_[l][0, qpre, :].float() - ac[l][0, qpre, :].float()).flatten() for l in SWAP_L])
                    nr, nq = real.norm(dim=1), req.norm(dim=1); ok = nq > 1e-8
                    RAW[f"{tag}|rho"] = np.float32(float((nr[ok] / nq[ok]).mean())) if ok.any() else np.float32(np.nan)
                    RAW[f"{tag}|kappa"] = np.float32(float(torch.nn.functional.cosine_similarity(real[ok], req[ok], dim=1).mean())) if ok.any() else np.float32(np.nan)
                    RAW[f"{tag}|rberr"] = np.float32(max(float((a_[l][0, qpre, :].float() - T[cond][l]).abs().max()) for l in SWAP_L))
                    # naming-plane coordinates inside the band (construction check): mean |Q^T h' - Q^T target| over blocks
                    RAW[f"{tag}|plane_dev"] = np.float32(np.mean([float(((a_[l][0, qpre, :].float() - T[cond][l]) @ Qp[l]).abs().max()) for l in SWAP_L]))
                else:   # int_q32: continuity row only (no fixed target; realized norm not recorded)
                    RAW[f"{tag}|realized"] = np.float32(np.nan)
                rec(tag, r, it, a_, l_, Q, qpre, Qp63); del a_
            del ac, ad; cell_idx += 1
            print(f"  [{STAGE}] {base}: {n} forwards ({time.time()-t0:.0f}s) | cos max {META['cells'][base]['cos_int_swap_max_abs']:.2f} | |dh| {normdiag[-1][0]:.1f} |vJ| {normdiag[-1][1]:.2f} at L62", flush=True)

    META.update({"run_id": RUN_ID, "n_forwards": n, "elapsed_s": round(time.time() - t0, 1)})
    np.savez_compressed(os.path.join(OUT, f"raw_{STAGE}.npz"), **RAW); json.dump(META, open(os.path.join(OUT, f"meta_{STAGE}.json"), "w"), indent=1, default=str)
    man = R.manifest_block(); man.update({"run_id": RUN_ID, "stage": STAGE, "script": os.path.relpath(__file__, R.PROJECT), "design": "H3/design_specs/two_hop_organism.md (Amendment 5)",
                                          "materials": META["materials"], "raw_sha256": hashlib.sha256(open(os.path.join(OUT, f"raw_{STAGE}.npz"), "rb").read()).hexdigest()})
    json.dump(man, open(os.path.join(OUT, f"manifest_{STAGE}.json"), "w"), indent=1)
    print(f"[done {STAGE}] {n} forwards, {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
