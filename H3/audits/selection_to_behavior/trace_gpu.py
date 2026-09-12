"""GPU trace audit for one selection_to_behavior cell.

Non-destructive: writes only under H3/audits/selection_to_behavior/outputs/.
It intentionally does NOT import the H3 runner, so the audit is an independent execution path over
shared registry/rendering/hooks only.

Run from repo root on the same environment/GPU used for the experiment:
    python H3/audits/selection_to_behavior/trace_gpu.py

Cell traced: T0 / C0 / rot0.  Visible words cat,dress,snake; B->A donor is the clean-B
instruction-region state from the identical full consumer rendering.
"""
import os, sys, json, hashlib
import numpy as np
import torch

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "common", "scripts"))
import registry as R
import materials as M
import rendering as Rn
import hooks as H

OUT = os.path.join(HERE, "outputs")
os.makedirs(OUT, exist_ok=True)
LETTERS = ["B", "D", "F", "H", "K", "M", "Q", "V"]
QUERY = "Using the code, give the letter for the word you were instructed to keep in mind. Answer with the letter only."
COPY = "copy the following text exactly, word for word"
SEED = 20260907
LX = 36
WORDS = ("cat", "dress", "snake")
DONORS = ("turtle", "airport", "fish")
CK = "C0"


def codebook_details(words, donors, seed):
    rng = np.random.default_rng(seed)
    items = list(words) + list(donors)
    letters = list(LETTERS); rng.shuffle(letters)
    assign = {w: letters[i] for i, w in enumerate(items)}
    order = list(items); rng.shuffle(order)
    text = "Code: " + ", ".join(f"{w} = {assign[w]}" for w in order) + "."
    return text, assign, order


def user_text(words, tag):
    head = f'Here are three words: (A) "{words[0]}", (B) "{words[1]}", (C) "{words[2]}"'
    return head + f". Keep the word tagged {tag} in mind while you {COPY}"


def render_arm(tok, words, tag, cb, consumer=True):
    car = M.CARRIERS[CK]
    ut = user_text(words, tag) + ":\n\n" + car
    extra = [(cb + "\n" + QUERY, "")] if consumer else None
    return Rn.render(tok, ut, car, sources=[(f"X{j}", words[j], True) for j in range(3)],
                     extra_turns=extra, name=f"audit|{tag}|{'consumer' if consumer else 'no_consumer'}")


def letter_ids(tok):
    out = {}
    for L in LETTERS:
        ids = []
        for form in (L, " " + L):
            v = tok(form, add_special_tokens=False).input_ids
            if len(v) == 1:
                ids.append((form, int(v[0])))
        # deduplicate token ids while preserving the first surface label
        seen = set(); dedup = []
        for form, tid in ids:
            if tid not in seen:
                seen.add(tid); dedup.append((form, tid))
        out[L] = dedup
    assert all(out.values())
    return out


def tensor_sha(x):
    # float() upcast: numpy has no bf16 dtype; bf16->float32 is lossless so equal tensors hash equal.
    a = x.detach().float().cpu().contiguous().numpy()
    return hashlib.sha256(a.tobytes()).hexdigest()


def token_dump(tok, r, positions):
    return [{"pos": int(p), "id": int(r.ids[p]), "token": tok.convert_ids_to_tokens(int(r.ids[p])),
             "decoded": tok.decode([int(r.ids[p])])} for p in positions]


def run_direct(model, lm, ids_list, all_layers, ctx=None, explicit_mask=False):
    from jlens.hooks import ActivationRecorder
    ids = torch.tensor([ids_list], device=lm.input_device)
    mask = torch.ones_like(ids) if explicit_mask else None
    with (ctx if ctx is not None else H.Both()):
        with ActivationRecorder(lm.layers, at=all_layers) as rec:
            logits = model(ids, attention_mask=mask).logits
            acts = {l: rec.activations[l].detach() for l in all_layers}
    return acts, logits


def run_lm_reference(lm, ids_list, all_layers):
    """Available jlens wrapper path; failure is recorded rather than hidden."""
    from jlens.hooks import ActivationRecorder
    ids = torch.tensor([ids_list], device=lm.input_device)
    with ActivationRecorder(lm.layers, at=all_layers) as rec:
        out = lm.forward(ids)
        acts = {l: rec.activations[l].detach() for l in all_layers}
    return acts, out


def compare_prefix(a, b, positions):
    rows = []
    first_exact = None
    for l in a:
        x = a[l][0, positions, :].float(); y = b[l][0, positions, :].float()
        mad = float((x-y).abs().max())
        same = bool(torch.equal(a[l][0, positions, :], b[l][0, positions, :]))
        if not same and first_exact is None:
            first_exact = int(l)
        rows.append({"layer": int(l), "bitwise_equal": same, "max_abs": mad,
                     "rms": float(torch.sqrt(torch.mean((x-y)**2)))})
    return {"first_non_bitwise_layer": first_exact, "per_layer": rows}


class TraceAbsoluteWriter:
    """Absolute block-output replacement with pre/write/post diagnostics."""
    def __init__(self, blocks, layers, positions, source):
        self.blocks, self.layers = blocks, list(layers)
        self.pos = torch.as_tensor(positions, dtype=torch.long)
        self.src = source; self.handles = []; self.stats = {}
    def _mk(self, l):
        def f(m, i, o):
            is_t = torch.is_tensor(o); h = (o if is_t else o[0]).clone()
            pre = h[0, self.pos, :].float().clone()
            tgt = self.src[l].to(h.device).float()
            new = tgt.to(h.dtype)
            post = new.float()
            d = post-pre
            self.stats[l] = {"pre_sha": tensor_sha(pre), "target_sha": tensor_sha(tgt), "post_sha": tensor_sha(post),
                             "target_post_max_abs": float((post-tgt).abs().max()),
                             "write_norm_per_pos": d.norm(dim=1).detach().cpu().tolist()}
            h[0, self.pos, :] = new
            return h if is_t else (h,) + tuple(o[1:])
        return f
    def __enter__(self):
        self.before_counts = [len(self.blocks[l]._forward_hooks) for l in self.layers]
        self.handles = [self.blocks[l].register_forward_hook(self._mk(l)) for l in self.layers]
        return self
    def __exit__(self, *a):
        for h in self.handles: h.remove()
        self.after_counts = [len(self.blocks[l]._forward_hooks) for l in self.layers]


def score_letters(tok, logits, lids):
    lp = torch.log_softmax(logits[0, -1].float(), -1)
    out = {}
    for L, forms in lids.items():
        ids = [tid for _, tid in forms]
        vals = torch.stack([lp[tid] for tid in ids])
        out[L] = {"forms": [{"surface": f, "id": tid, "raw_logit": float(logits[0,-1,tid]), "logprob": float(lp[tid])}
                            for f, tid in forms],
                  "old_max_logprob": float(vals.max()),
                  "dedup_logsumexp_logprob": float(torch.logsumexp(vals, 0))}
    topid = int(logits[0,-1].argmax())
    return out, {"id": topid, "token": tok.convert_ids_to_tokens(topid), "decoded": tok.decode([topid])}


def main():
    tok = R.make_tokenizer(); lids = letter_ids(tok)
    cb, assign, order = codebook_details(WORDS, DONORS, SEED)
    rA = render_arm(tok, WORDS, "A", cb, True); rB = render_arm(tok, WORDS, "B", cb, True); rC = render_arm(tok, WORDS, "C", cb, True)
    rN = render_arm(tok, WORDS, "A", cb, False)
    diffs = [i for i,(a,b,c) in enumerate(zip(rA.ids,rB.ids,rC.ids)) if not (a==b==c)]
    assert len(diffs)==1
    tp = diffs[0]; cs = rA.meta["carrier_start"]; instr = list(range(tp,cs))
    src_spans = {str(j): rA.spans[f"X{j}"]["full"] for j in range(3)}

    # Equal-length, different-content suffix: keep words/order/query fixed, cyclically rotate assigned letters.
    alt_assign = dict(assign); used = [assign[w] for w in order]; rot_letters = used[1:]+used[:1]
    for w,L in zip(order,rot_letters): alt_assign[w]=L
    alt_cb = "Code: " + ", ".join(f"{w} = {alt_assign[w]}" for w in order) + "."
    rAlt = render_arm(tok, WORDS, "A", alt_cb, True)

    report = {"cell": "T0|C0|rot0", "words": WORDS, "donors": DONORS, "codebook": cb, "assign": assign, "order": order,
              "tag_pos": tp, "carrier_start": cs, "assistant_carrier": list(rA.spans["assistant_carrier"]),
              "answer_prediction_pos": int(rA.spans["answer"]), "n_tokens": {"consumer": len(rA), "no_consumer": len(rN), "alt_suffix": len(rAlt)},
              "token_alignment": {"arm_diff_positions": diffs,
                  "ids_equal_before_carrier": rA.ids[:cs] == rN.ids[:cs],
                  "interior_positions_equal": rA.interior == rN.interior,
                  "interior_ids_equal": [rA.ids[p] for p in rA.interior] == [rN.ids[p] for p in rN.interior] if rA.interior==rN.interior else False,
                  "same_length_alt": len(rAlt)==len(rA),
                  "alt_prefix_ids_equal_through_carrier_end": rAlt.ids[:rA.meta["carrier_end"]] == rA.ids[:rA.meta["carrier_end"]]},
              "patched_region": {"positions": instr, "decoded": tok.decode([rA.ids[p] for p in instr]),
                                 "tokens": token_dump(tok,rA,instr), "source_spans": src_spans,
                                 "source_tokens": {j: token_dump(tok,rA,ps) for j,ps in src_spans.items()},
                                 "user_carrier": list(rA.spans["user_carrier"]),
                                 "assistant_carrier": list(rA.spans["assistant_carrier"])},
              "answer_input_tail": token_dump(tok,rA,list(range(max(0,len(rA)-16),len(rA)))),
              "letter_ids": lids}

    model = R.load_model(); from jlens.hf import from_hf
    lm = from_hf(model,tok,compile=False); ALL=list(range(R.N_BLOCKS)); LGE=[l for l in ALL if l>=LX]
    # Clean same-rendering paths.
    aA,lgA = run_direct(model,lm,rA.ids,ALL); aB,lgB = run_direct(model,lm,rB.ids,ALL)
    aN,lgN = run_direct(model,lm,rN.ids,ALL); aAlt,lgAlt = run_direct(model,lm,rAlt.ids,ALL)
    shared_positions = rA.interior if rA.interior==rN.interior else sorted(set(rA.interior)&set(rN.interior))
    report["prefix_activation_compare"] = {
        "consumer_vs_no_consumer": compare_prefix(aA,aN,shared_positions),
        "consumer_vs_equal_length_different_suffix": compare_prefix(aA,aAlt,rA.interior)}
    # Explicit all-ones mask reference on consumer rendering.
    aMask,lgMask = run_direct(model,lm,rA.ids,ALL,explicit_mask=True)
    report["explicit_ones_mask_vs_none"] = compare_prefix(aA,aMask,rA.interior)
    # jlens wrapper reference path when available.
    try:
        aRef,_ = run_lm_reference(lm,rA.ids,ALL)
        report["lm_forward_reference_vs_model"] = compare_prefix(aA,aRef,rA.interior)
    except Exception as e:
        report["lm_forward_reference_error"] = repr(e)

    # B->A absolute patch and exact write trace.
    Bsrc={l:aB[l][0,instr,:].clone() for l in LGE}
    donor_sha_before={str(l):tensor_sha(Bsrc[l]) for l in LGE}
    hook_counts_before={str(l):len(lm.layers[l]._forward_hooks) for l in LGE}
    wB=TraceAbsoluteWriter(lm.layers,LGE,instr,Bsrc)
    aBA,lgBA=run_direct(model,lm,rA.ids,ALL,wB)
    hook_counts_after={str(l):len(lm.layers[l]._forward_hooks) for l in LGE}
    donor_sha_after={str(l):tensor_sha(Bsrc[l]) for l in LGE}
    report["BtoA_patch"]={"hook_kind":"forward hook on decoder-block OUTPUT", "layers":LGE,
                          "donor_immutable":donor_sha_before==donor_sha_after,
                          "hook_counts_restored":hook_counts_before==hook_counts_after,
                          "write_stats":{str(l):v for l,v in wB.stats.items()}}

    # C->A actual sustained write, needed to assess whether one B-matched random is adequate for C.
    aC,lgC=run_direct(model,lm,rC.ids,ALL); Csrc={l:aC[l][0,instr,:].clone() for l in LGE}
    wC=TraceAbsoluteWriter(lm.layers,LGE,instr,Csrc); aCA,lgCA=run_direct(model,lm,rA.ids,ALL,wC)

    # Reconstruct CURRENT randA exactly: clean B-A endpoint norm, absolute target hA + random delta.
    g=torch.Generator(device="cpu").manual_seed(SEED+7)  # ti=rot=carrier_index=0
    randsrc={}
    for l in LGE:
        hA=aA[l][0,instr,:].float(); hB=aB[l][0,instr,:].float(); dn=(hB-hA).norm(dim=1,keepdim=True)
        rv=torch.randn(len(instr),hA.shape[1],generator=g).to(hA.device); rv=rv/rv.norm(dim=1,keepdim=True)*dn
        randsrc[l]=(hA+rv).to(aA[l].dtype)
    wR=TraceAbsoluteWriter(lm.layers,LGE,instr,randsrc); aR,lgR=run_direct(model,lm,rA.ids,ALL,wR)
    ratiosB=[]; ratiosC=[]
    for l in LGE:
        rb=np.array(wB.stats[l]["write_norm_per_pos"]); rc=np.array(wC.stats[l]["write_norm_per_pos"]); rr=np.array(wR.stats[l]["write_norm_per_pos"])
        ratiosB.extend((rr/(rb+1e-12)).tolist()); ratiosC.extend((rr/(rc+1e-12)).tolist())
    report["current_randA_audit"]={"construction":"absolute clean-A target plus isotropic vector scaled to clean ||hB-hA||, not realized sustained BtoA write",
                                  "rand_to_actual_B_write_ratio":{"median":float(np.median(ratiosB)),"p10":float(np.percentile(ratiosB,10)),"p90":float(np.percentile(ratiosB,90))},
                                  "rand_to_actual_C_write_ratio":{"median":float(np.median(ratiosC)),"p10":float(np.percentile(ratiosC,10)),"p90":float(np.percentile(ratiosC,90))},
                                  "separate_C_matched_random_present_in_original":False}

    # Hand answer scoring: old max versus requested deduplicated probability mass.
    scoresA,greedyA=score_letters(tok,lgA,lids); scoresB,greedyB=score_letters(tok,lgB,lids); scoresBA,greedyBA=score_letters(tok,lgBA,lids)
    def q_from(scores,target,base,kind): return scores[assign[target]][kind]-scores[assign[base]][kind]
    report["answer_scoring"]={"cleanA":{"scores":scoresA,"greedy":greedyA},"cleanB":{"scores":scoresB,"greedy":greedyB},"BtoA":{"scores":scoresBA,"greedy":greedyBA},
                              "E_B_old_max":q_from(scoresBA,WORDS[1],WORDS[0],"old_max_logprob")-q_from(scoresA,WORDS[1],WORDS[0],"old_max_logprob"),
                              "E_B_dedup_logsumexp":q_from(scoresBA,WORDS[1],WORDS[0],"dedup_logsumexp_logprob")-q_from(scoresA,WORDS[1],WORDS[0],"dedup_logsumexp_logprob")}
    # Saved pilot comparison uses aggregate eight-letter max scores; check exact current max E for this cell against saved lsc.
    try:
        raw=np.load(os.path.join(ROOT,"H3","outputs","selection_to_behavior","raw_pilot.npz"),allow_pickle=False)
        LIX={L:i for i,L in enumerate(LETTERS)}
        base="T0|C0|rot0"
        asg=assign
        def saved_q(tag,target,baseword):
            v=raw[f"{tag}|lsc"].astype(np.float64)
            return float(v[LIX[asg[target]]]-v[LIX[asg[baseword]]])
        saved_E=saved_q(f"{base}|BtoA|noswap",WORDS[1],WORDS[0])-saved_q(f"{base}|cleanA|noswap",WORDS[1],WORDS[0])
        report["answer_scoring"]["saved_E_B_current_max"] = saved_E
        report["answer_scoring"]["rerun_minus_saved_E_B"] = report["answer_scoring"]["E_B_old_max"]-saved_E
    except Exception as e:
        report["answer_scoring"]["saved_compare_error"] = repr(e)

    # Cache/recurrent semantics of the actual runner.
    report["state_semantics"]={"past_key_values_supplied":False,"attention_mask_argument":"None in original runner",
        "interpretation":"single full-sequence forward; block-output patch does not overwrite within-block attention/GatedDeltaNet state already computed in that same block. Patched outputs feed subsequent blocks, whose attention/recurrent computations are recomputed from the modified residual trajectory. No cache object is transplanted between runs."}

    path=os.path.join(OUT,"trace_T0_C0_rot0.json")
    json.dump(report,open(path,"w"),indent=1)
    print(json.dumps(report,indent=1))
    print(f"\nWrote {path}")

if __name__=="__main__": main()
