"""Implementation audit for H3 selection_to_behavior. Writes H3/outputs/audit/ ; does not touch existing results.

Checks (GPU): 1 prefix/leakage with an equal-length different-content suffix control; 2 patch read-back and
untouched-layer verification; 4 answer-scoring by hand (position, ids, raw logits, max vs logsumexp);
5 realized write norms for randA vs the transplant.
Usage: audit_selection_to_behavior.py
"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "common", "scripts"))
import numpy as np, torch
import registry as R, materials as M, rendering as Rn, readout as RO, hooks as H

OUT = os.path.join(R.PROJECT, "H3", "outputs", "audit"); os.makedirs(OUT, exist_ok=True)
COPY = "copy the following text exactly, word for word"
LETTERS = ["B", "D", "F", "H", "K", "M", "Q", "V"]
QUERY = "Using the code, give the letter for the word you were instructed to keep in mind. Answer with the letter only."
LX = 36
res = {}


def ut(w, t):
    return f'Here are three words: (A) "{w[0]}", (B) "{w[1]}", (C) "{w[2]}". Keep the word tagged {t} in mind while you {COPY}'


def main():
    tok = R.make_tokenizer()
    from jlens.hf import from_hf
    model = R.load_model(); lm = from_hf(model, tok, compile=False)
    ALL = list(range(R.N_BLOCKS)); LGE = [l for l in ALL if l >= LX]
    run = H.make_run(model, lm, ALL)
    words = ("cat", "dress", "snake"); ck = "C0"; car = M.CARRIERS[ck]
    asg = {"cat": "Q", "dress": "V", "snake": "F", "turtle": "B", "airport": "H", "fish": "M"}
    order = list(asg)
    cb = "Code: " + ", ".join(f"{x} = {asg[x]}" for x in order) + "."
    # equal-length, different-content suffix: same words, permuted letters + permuted order
    asg2 = {"cat": "K", "dress": "M", "snake": "D", "turtle": "V", "airport": "Q", "fish": "B"}
    cb2 = "Code: " + ", ".join(f"{x} = {asg2[x]}" for x in reversed(order)) + "."

    def rend(tag, consumer=None):
        extra = [(consumer + "\n" + QUERY, "")] if consumer else None
        return Rn.render(tok, ut(words, tag) + ":\n\n" + car, car,
                         sources=[(f"X{j}", words[j], True) for j in range(3)], extra_turns=extra, name=tag)

    rA, rB = rend("A", cb), rend("B", cb)
    rA2 = rend("A", cb2)                      # same length? assert below
    rAnc = rend("A", None)
    cs = rA.meta["carrier_start"]; tp = [i for i in range(len(rA.ids)) if rA.ids[i] != rB.ids[i]][0]
    instr = list(range(tp, cs)); interior = rA.interior

    # ---------------- CHECK 1
    c1 = {"len_with": len(rA), "len_with_alt": len(rA2), "len_without": len(rAnc),
          "equal_length_alt": len(rA) == len(rA2),
          "prefix_ids_identical_alt": rA.ids[:cs] == rA2.ids[:cs],
          "prefix_ids_identical_nc": rA.ids[:cs] == rAnc.ids[:cs],
          "carrier_ids_identical_alt": rA.ids[cs:rA.spans['assistant_carrier'][1]] == rA2.ids[cs:rA2.spans['assistant_carrier'][1]]}
    aA, _ = run(rA.ids); aA2, _ = run(rA2.ids); aNC, _ = run(rAnc.ids)
    per_layer_alt, per_layer_nc = [], []
    first_div_alt, first_div_nc = None, None
    for l in ALL:
        x = aA[l][0, interior, :].float(); y = aA2[l][0, interior, :].float(); z = aNC[l][0, rAnc.interior, :].float()
        da = float((x - y).abs().max()); dn = float((x - z).abs().max())
        per_layer_alt.append(da); per_layer_nc.append(dn)
        if first_div_alt is None and da > 0: first_div_alt = l
        if first_div_nc is None and dn > 0: first_div_nc = l
    c1.update({"first_divergent_block_equal_length_alt": first_div_alt, "first_divergent_block_without_consumer": first_div_nc,
               "max_abs_resid_diff_alt": max(per_layer_alt), "max_abs_resid_diff_nc": max(per_layer_nc),
               "per_layer_alt_first8": per_layer_alt[:8], "per_layer_nc_first8": per_layer_nc[:8],
               "per_layer_nc_last8": per_layer_nc[-8:]})
    res["check1_prefix_leakage"] = c1

    # ---------------- CHECK 2 read-back
    Bsrc = {l: aA[l][0, instr, :].clone() for l in LGE}          # placeholder replaced below with real B states
    aB, _ = run(rB.ids)
    Bsrc = {l: aB[l][0, instr, :].clone() for l in LGE}
    aBA, lgBA = run(rA.ids, H.SpanWriter(lm.layers, LGE, instr, Bsrc))
    rb_patched = max(float((aBA[l][0, instr, :].float() - Bsrc[l].float()).abs().max()) for l in LGE)
    rb_below = max(float((aBA[l][0, instr, :].float() - aA[l][0, instr, :].float()).abs().max()) for l in ALL if l < LX)
    rb_sources_untouched = max(float((aBA[l][0, sum([rA.spans[f'X{j}']['full'] for j in range(3)], []), :].float()
                                      - aA[l][0, sum([rA.spans[f'X{j}']['full'] for j in range(3)], []), :].float()).abs().max()) for l in ALL if l < LX)
    res["check2_readback"] = {"hook_site": "register_forward_hook on block -> patches BLOCK OUTPUT",
                              "max_abs_diff_patched_positions_vs_donor(should be 0)": rb_patched,
                              "max_abs_diff_below_Lx_at_instr_vs_cleanA(should be 0)": rb_below,
                              "max_abs_diff_below_Lx_at_source_spans(should be 0)": rb_sources_untouched,
                              "instr_positions": [instr[0], instr[-1]], "n_instr": len(instr),
                              "instr_decoded": tok.decode(rA.ids[tp:cs]),
                              "instr_disjoint_from_sources": len(set(instr) & set(sum([rA.spans[f'X{j}']['full'] for j in range(3)], []))) == 0,
                              "instr_max_lt_answer_pos": max(instr) < rA.spans["answer"]}

    # ---------------- CHECK 4 answer scoring by hand
    LID = {L: sorted({tok(f, add_special_tokens=False).input_ids[0]
                      for f in (L, " " + L) if len(tok(f, add_special_tokens=False).input_ids) == 1}) for L in LETTERS}
    def scores(logits):
        lp = torch.log_softmax(logits[0, -1].float(), -1)
        mx = {L: max(float(lp[i]) for i in LID[L]) for L in LETTERS}
        lse = {L: float(torch.logsumexp(torch.tensor([float(lp[i]) for i in LID[L]]), 0)) for L in LETTERS}
        return mx, lse, lp
    _, lgA = run(rA.ids)
    mxA, lseA, lpA = scores(lgA); mxBA, lseBA, lpBA = scores(lgBA)
    res["check4_scoring"] = {
        "answer_position_index": int(rA.spans["answer"]), "seq_len": len(rA.ids),
        "scored_position_is_last": int(rA.spans["answer"]) == len(rA.ids) - 1,
        "last_5_tokens": [tok.decode([i]) for i in rA.ids[-5:]],
        "letter_ids": LID, "n_ids_per_letter": {k: len(v) for k, v in LID.items()},
        "greedy_cleanA": tok.decode(int(lgA[0, -1].argmax())), "greedy_BtoA": tok.decode(int(lgBA[0, -1].argmax())),
        "raw_logit_at_scored_pos_cleanA": {L: [float(lgA[0, -1, i]) for i in LID[L]] for L in LETTERS},
        "E_B_max_rule": (mxBA[asg["dress"]] - mxBA[asg["cat"]]) - (mxA[asg["dress"]] - mxA[asg["cat"]]),
        "E_B_logsumexp_rule": (lseBA[asg["dress"]] - lseBA[asg["cat"]]) - (lseA[asg["dress"]] - lseA[asg["cat"]]),
        "offby_one_probe_E_B_at_pos_minus_1": None}
    # off-by-one probe: score at position -2 instead of -1
    lp2 = torch.log_softmax(lgA[0, -2].float(), -1); lp2b = torch.log_softmax(lgBA[0, -2].float(), -1)
    m2 = lambda lp: {L: max(float(lp[i]) for i in LID[L]) for L in LETTERS}
    a2, b2 = m2(lp2), m2(lp2b)
    res["check4_scoring"]["offby_one_probe_E_B_at_pos_minus_1"] = (b2[asg["dress"]] - b2[asg["cat"]]) - (a2[asg["dress"]] - a2[asg["cat"]])

    # ---------------- CHECK 5 realized write norms
    aC, _ = run(rend("C", cb).ids)
    Csrc = {l: aC[l][0, instr, :].clone() for l in LGE}
    g = torch.Generator(device="cpu").manual_seed(0)
    randsrc, nb, nc, nr = {}, [], [], []
    for l in LGE:
        hA = aA[l][0, instr, :].float(); hB = aB[l][0, instr, :].float(); hC = aC[l][0, instr, :].float()
        dn = (hB - hA).norm(dim=1, keepdim=True)
        rr_ = torch.randn(len(instr), hA.shape[1], generator=g).to(hA.device)
        rr_ = rr_ / rr_.norm(dim=1, keepdim=True) * dn
        randsrc[l] = (hA + rr_).to(aA[l].dtype)
        nb.append(float((hB - hA).norm(dim=1).mean())); nc.append(float((hC - hA).norm(dim=1).mean()))
        nr.append(float((randsrc[l].float() - hA).norm(dim=1).mean()))
    res["check5_random_control"] = {
        "mean_write_norm_BtoA_per_layer_first5": nb[:5], "mean_write_norm_CtoA_per_layer_first5": nc[:5],
        "mean_write_norm_randA_per_layer_first5": nr[:5],
        "randA_matches_BtoA_ratio": float(np.mean(nr) / np.mean(nb)), "randA_matches_CtoA_ratio": float(np.mean(nr) / np.mean(nc)),
        "CtoA_vs_BtoA_norm_ratio": float(np.mean(nc) / np.mean(nb)),
        "note": "SpanWriter OVERWRITES; realized==requested by construction (verified in check2 read-back). The battery's stored randA rho=1.0 was a hardcoded placeholder, not a measurement."}

    json.dump(res, open(os.path.join(OUT, "audit_results.json"), "w"), indent=1, default=float)
    print(json.dumps(res, indent=1, default=float)[:4000])


if __name__ == "__main__":
    main()
