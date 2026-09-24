"""Run 2026-09-24 after the qsplit6 battery; output in H3/outputs/two_hop_organism/cbdiag_qsplit6.txt. Usage: two_hop_qsplit6_cbdiag.py"""
"""Construction diagnostic for the registered `q_rem_cb_pre` row (Amendment 6): per block, the norm of the deviation of the
current-base state from clean at q_pre, ||h'_l - h_l||, against the fixed-target complement's ||Delta_l - P Delta_l|| and the
donor's ||Delta_l||. Two cells, 5 forwards each. Not a scored row; a verification of the write construction."""
import sys, os, numpy as np, torch
sys.argv = ["x", "smoke1"]; HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "..", "common", "scripts"))
import two_hop_qsplit6 as Q, registry as R, materials as M, rendering as Rn, readout as RO, hooks as H
from hooks_fp32 import Fp32Residual
from jlens.hf import from_hf
tok = R.make_tokenizer(); model = R.load_model(); lm = from_hf(model, tok, compile=False); ALL = list(range(R.N_BLOCKS)); run = H.make_run(model, lm, ALL); dev = lm.input_device
LEN = R.load_lenses(("J_NP",))["J_NP"]; SWAP_L = Q.SWAP_L
items = {it["name"]: it for it in __import__("json").load(open(os.path.join(R.PROJECT, "H3", "design_specs", "two_hop_items.json")))["pilot_items"]}
fp = lambda: Fp32Residual(lm.layers, Q.FP32_FROM)
for name, ck in (("ex-city-capital-Barcelona-Toronto", "C0"), ("food-animal-butter", "C0")):
    it = items[name]; car = M.CARRIERS[ck]; body, dbody = Q.clue_body(it["prompt"]), Q.clue_body(it["donor_prompt"])
    r = Rn.render(tok, Q.utext(body, car), car, sources=[("CLUE", body, False)], extra_turns=[(Q.QUESTION, "")]); rd = Rn.render(tok, Q.utext(dbody, car), car, sources=[("CLUE", dbody, False)], extra_turns=[(Q.QUESTION, "")])
    ce = r.meta["carrier_end"]; Q_ = list(range(ce, len(r))); qpre = Q_[:-1]; ids = list(r.ids); cA = Q.spellings(tok, it["answer"])
    full = ids + list(cA[0]); ac, _ = run(full, fp()); ad, _ = run(list(rd.ids) + list(cA[0]), fp())
    TID = {w: Rn.single_token_id(tok, w) for w in (it["intermediate"], it["swap_to"])}; ro = RO.LensReadout(model, lm, LEN, list(TID.values()))
    Qp, CB, T = {}, {}, {}
    for l in SWAP_L:
        h = ac[l][0, qpre, :].float(); hY = ad[l][0, qpre, :].float(); dh = hY - h
        Qp[l] = torch.linalg.qr(torch.stack([ro.folded_direction(l, TID[it["intermediate"]]), ro.folded_direction(l, TID[it["swap_to"]])], 1).float())[0]
        vJ = (dh @ Qp[l]) @ Qp[l].T; CB[l] = (dh - vJ).clone(); T[l] = h + dh - vJ
    hcl = {l: ac[l][0, qpre, :].float() for l in SWAP_L}
    a_cb, _ = run(full, H.Both(fp(), Q.CurrentBaseAdd(lm.layers, SWAP_L, qpre, CB, Qp, hcl)))
    a_ft, _ = run(full, H.Both(fp(), H.SpanWriter(lm.layers, SWAP_L, qpre, T)))
    print(f"\n{name}|{ck}: per block  ||h'_cb - h||  /  ||Delta^perp|| (= fixed-target deviation)  /  ||Delta||  (means over q_pre positions)")
    for l in SWAP_L:
        d_cb = (a_cb[l][0, qpre, :].float() - hcl[l]).norm(dim=1).mean(); d_ft = (a_ft[l][0, qpre, :].float() - hcl[l]).norm(dim=1).mean(); d_full = (ad[l][0, qpre, :].float() - hcl[l]).norm(dim=1).mean()
        print(f"  L{l}: {d_cb:7.2f} / {d_ft:7.2f} / {d_full:7.2f}   ratio cb/full {d_cb/d_full:5.2f}")
    d63 = (a_cb[63][0, qpre, :].float() - ac[63][0, qpre, :].float()).norm(dim=1).mean(); f63 = (ad[63][0, qpre, :].float() - ac[63][0, qpre, :].float()).norm(dim=1).mean()
    print(f"  L63 (free): cb {d63:.2f} vs donor {f63:.2f}")
