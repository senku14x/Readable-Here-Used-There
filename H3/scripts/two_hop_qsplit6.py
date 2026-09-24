"""H3 two_hop_organism stage `qsplit6` (design: H3/design_specs/two_hop_organism.md, Amendment 6).

The question-turn ladder finished: the same-run Amendment-5 rows, the ANSWER naming plane, a k-sweep (k in {2, 8, 25, 64})
of nonnegative pursuit over the full-vocabulary J_NP dictionary with least-squares refits, the registered restricted-dictionary
NNLS row (`q_rem25`), a consumer clamp at the scoring position for every complement row (with a norm-matched random-k
control), norm- and rank-matched random-k removals, and a current-base complement whose plane is left free. Float32 residual
from block 35 on every forward; sequence-log-prob endpoint only (the single-token candidate scalars are recorded as a
secondary continuity column, never scored).

Stages:  smoke    tokenizer-only checks + a CPU unit test of the pursuit / NNLS machinery (no model)
         smoke1   one cell end to end (item 0, carrier C0): gates, every row, timings; writes raw_smoke1*.npz
         qsplit6  the 48 cells: Phase A clean/donor forwards -> Phase B pursuits per block (the registered `pursuit` pass,
                  saved as raw_pursuit_qsplit6.npz) -> Phase C rows
Usage: two_hop_qsplit6.py smoke|smoke1|qsplit6
"""
import os, sys, json, time, hashlib, re
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "..", "common", "scripts"))
import numpy as np, torch
import registry as R, materials as M, rendering as Rn, readout as RO, hooks as H
from hooks_fp32 import Fp32Residual

STAGE = sys.argv[1] if len(sys.argv) > 1 else "smoke"; assert STAGE in ("smoke", "smoke1", "qsplit6")
OUT = R.out_dir("H3", "outputs", "two_hop_organism")
RUN_ID = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()); SEED = 20260924; FP32_FROM = 35
COPY = "copy the following text exactly, word for word"; CARRIERS = ["C0", "C1", "C2", "C3"]; DECOYS = M.FIT_WORDS[:8]
SWAP_L = list(range(36, 63)); RB = list(range(51, 60)); KS = [2, 8, 25, 64]; KMAX = 64; KNN = 25; LZ = list(range(36, 63))
ITEMS = json.load(open(os.path.join(R.PROJECT, "H3", "design_specs", "two_hop_items.json")))["pilot_items"]
STRIP = re.compile(r"\s+(is called a|is called the|is the|is a|are|is)\s*$")
QUESTION = "Complete the fact from the clue you were given, using one word."
S_DONOR0_SEQ_BF16 = 23.87764283021291   # bridgeswap_seq ceiling (meta_bridgeswap_seq.json), quoted for context, not re-run
if STAGE == "smoke1": ITEMS, CARRIERS = ITEMS[:1], CARRIERS[:1]
WORD_RE = re.compile(r"^Ġ[A-Za-z]{3,}$")   # restricted dictionary: leading-space alphabetic word tokens of >= 3 letters
RIDGE = 1e-6                                # relative ridge on the Gram system of the LS refit (numerical guard only; recorded)

# Amendment 6 §1: frozen alias lists for the atom classification (answer class takes priority on a collision)
ANS_ALIASES = {"Madrid": ["madrid"], "Ottawa": ["ottawa"], "Paris": ["paris", "parisian"], "Rome": ["rome", "roman"], "Berlin": ["berlin"],
               "Tokyo": ["tokyo"], "Arabic": ["arabic", "arab"], "Russian": ["russian"], "Budapest": ["budapest"], "Warsaw": ["warsaw"],
               "Athens": ["athens", "athenian"], "cow": ["cow", "cows", "cattle"], "bee": ["bee", "bees"]}
INT_ALIASES = {"Spain": ["spain", "spanish", "spaniard"], "Canada": ["canada", "canadian"], "France": ["france", "french"],
               "Italy": ["italy", "italian"], "Germany": ["germany", "german"], "Japan": ["japan", "japanese"], "Egypt": ["egypt", "egyptian"],
               "Russia": ["russia", "russian"], "Hungary": ["hungary", "hungarian"], "Poland": ["poland", "polish"], "Greece": ["greece", "greek"],
               "butter": ["butter", "buttery"], "honey": ["honey", "honeyed"]}

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


def classify_atom(s, it):
    """Amendment 6 §1: answer-related (priority) / intermediate-related / other, from the decoded token string."""
    s = s.strip().lower()
    if not s: return "other"
    for w in (it["answer"], it["swap_answer"]):
        if s == w.lower() or s in ANS_ALIASES.get(w, []): return "answer"
    for w in (it["intermediate"], it["swap_to"]):
        wl = w.lower()
        if s == wl or s in INT_ALIASES.get(w, []): return "intermediate"
        if len(s) >= 3 and s.isalpha() and (wl.startswith(s) or s.startswith(wl)): return "intermediate"
    return "other"


# ----------------------------------------------------------------------------------------------------------------- pursuit
@torch.no_grad()
def ls_refit(A, X, alive=None):
    """Ordinary least squares c = argmin ||X - A^T c|| per vector via the Gram system, A [N, s, d], X [N, d].
    `alive` [N, s] float mask (1 = atom in the active set); dead atoms get coefficient 0 (rank-safe: their rows/cols of the
    Gram matrix are replaced by the identity). A relative ridge RIDGE * mean diag guards near-duplicate atoms."""
    N, s, _ = A.shape
    G = A @ A.transpose(1, 2); b = torch.einsum("nsd,nd->ns", A, X)
    if alive is not None:
        G = G * alive[:, :, None] * alive[:, None, :] + torch.diag_embed(1.0 - alive); b = b * alive
    G = G + RIDGE * torch.eye(s, device=A.device)[None] * (G.diagonal(dim1=1, dim2=2).mean(1)[:, None, None])
    return torch.linalg.solve(G, b[:, :, None])[:, :, 0]


@torch.no_grad()
def pursuit_ls(D, X, K, checkpoints):
    """Nonnegative greedy selection with least-squares refits (Amendment 6 §1).
    D: [V, d] fp16 unit atoms (GPU); X: [N, d] fp32 targets. Returns sel [N, K] long, stop_at [N] (K if never stopped),
    and {k: coef [N, k] fp32} at each checkpoint (LS coefficients on the first min(k, stop) selected atoms, zero after a stop)."""
    N, d = X.shape; V = D.shape[0]; dev = X.device
    R_ = X.clone(); sel = torch.zeros(N, K, dtype=torch.long, device=dev); stop = torch.full((N,), K, dtype=torch.long, device=dev)
    mask = torch.zeros(N, V, dtype=torch.bool, device=dev); ar = torch.arange(N, device=dev); coefs = {}
    for j in range(K):
        C = (R_.half() @ D.T).float()                               # [N, V] correlations (fp16 operands, fp32 accumulation)
        C[mask] = float("-inf")
        cmax, v = C.max(1)
        newly = (cmax <= 0) & (stop == K); stop[newly] = j        # nonnegative rule: no positive correlation left -> stopped at j
        sel[:, j] = v; mask[ar, v] = True
        A = D[sel[:, :j + 1]].float()                               # [N, j+1, d]
        alive = (torch.arange(j + 1, device=dev)[None, :] < stop[:, None]).float()
        c = ls_refit(A, X, alive)
        R_ = X - torch.einsum("nk,nkd->nd", c, A)
        if (j + 1) in checkpoints: coefs[j + 1] = c.clone()
        del C, A
    return sel, stop, coefs


@torch.no_grad()
def nnls_batched(A, X, iters=500):
    """Batched NNLS min ||X - A^T c||, c >= 0, by accelerated projected gradient (FISTA) on the Gram system.
    A: [N, s, d], X: [N, d]. Returns c [N, s]."""
    G = A @ A.transpose(1, 2); b = torch.einsum("nsd,nd->ns", A, X)
    L = torch.linalg.eigvalsh(G)[:, -1].clamp_min(1e-8)[:, None]
    c = torch.zeros_like(b); y = c.clone(); t = 1.0
    for _ in range(iters):
        g = torch.einsum("nst,nt->ns", G, y) - b
        cn = (y - g / L).clamp_min(0.0); t_new = 0.5 * (1 + (1 + 4 * t * t) ** 0.5)
        y = cn + ((t - 1) / t_new) * (cn - c); c, t = cn, t_new
    return c


@torch.no_grad()
def kkt_check(A, X, c):
    """Amendment 6 §1 KKT conditions at tolerance 1e-4 * ||X||: c >= 0; |g_i| <= tol where c_i > 0; g_i >= -tol where c_i = 0."""
    G = A @ A.transpose(1, 2); b = torch.einsum("nsd,nd->ns", A, X); g = torch.einsum("nst,nt->ns", G, c) - b
    tol = 1e-4 * X.norm(dim=1)[:, None]
    return (((c > 0) & (g.abs() <= tol)) | ((c == 0) & (g >= -tol))).all(1) & (c >= 0).all(1)


def nnls_scipy(A, X):
    from scipy.optimize import nnls
    return torch.tensor(np.stack([nnls(A[n].T.cpu().numpy().astype(np.float64), X[n].cpu().numpy().astype(np.float64))[0] for n in range(A.shape[0])]),
                        dtype=torch.float32, device=X.device)


@torch.no_grad()
def pursuit_nnls(D, X, K):
    """Greedy nonnegative selection with a true NNLS refit at every step (Amendment 6 §1, the registered q_rem25).
    Returns sel [N, K], coef [N, K] (nonnegative), kkt_pass [N] (after the scipy fallback at the final step), n_fallback."""
    N, d = X.shape; V = D.shape[0]; dev = X.device
    R_ = X.clone(); sel = torch.zeros(N, K, dtype=torch.long, device=dev); mask = torch.zeros(N, V, dtype=torch.bool, device=dev)
    ar = torch.arange(N, device=dev); c = None; nfb = 0
    for j in range(K):
        C = (R_.half() @ D.T).float(); C[mask] = float("-inf"); v = C.argmax(1); sel[:, j] = v; mask[ar, v] = True
        A = D[sel[:, :j + 1]].float(); c = nnls_batched(A, X); ok = kkt_check(A, X, c)
        if not bool(ok.all()):
            bad = (~ok).nonzero()[:, 0]; c[bad] = nnls_scipy(A[bad], X[bad])
            if j + 1 == K: nfb = int(len(bad))
        R_ = X - torch.einsum("nk,nkd->nd", c, A); del C
    ok = kkt_check(A, X, c)
    return sel, c, ok, nfb


def random_frame(d, k, g, dev):
    return torch.linalg.qr(torch.randn(d, k, generator=g))[0].to(dev)


def orth_against(Rr, U):
    """Orthogonalise the columns of Rr [d, k] against span(U) [d, m], then orthonormalise."""
    Rr = Rr - U @ (U.T @ Rr)
    return torch.linalg.qr(Rr)[0]


# ----------------------------------------------------------------------------------------------------------------- hooks
class SubspaceClampMatched:
    """Amendment 6 §3 consumer clamp: at block l and the scoring position s, hold the coordinates of h_s in span(U_l) at their
    clean values, h' = h - U U^T (h - h_ref); with `target` ({block: scalar norm}) the delta is rescaled to that norm (the
    norm-matched random-k control). Arithmetic in true float32 under the autocast; the post-cast realized write is recorded."""
    def __init__(self, blocks, layers, position, U, href, target=None):
        self.blocks, self.layers, self.pos = blocks, sorted(layers), int(position)
        self.U, self.href, self.target, self._h, self.post = U, href, target, [], {}

    def _mk(self, l):
        @torch.autocast("cuda", enabled=False)
        def f(m, i, o):
            h = H._out(o).clone(); hp = h[0, self.pos, :].float(); U = self.U[l].to(hp.device).float()
            delta = -U @ (U.T @ (hp - self.href[l].to(hp.device).float()))
            if self.target is not None:
                delta = delta * (float(self.target[l]) / delta.norm().clamp_min(1e-8))
            new = (hp + delta).to(h.dtype); real = new.float() - hp; dn = float(delta.norm())
            self.post[l] = {"req": dn, "real": float(real.norm()),
                            "kappa": float(torch.nn.functional.cosine_similarity(real[None], delta[None]).item()) if dn > 1e-8 else 1.0}
            h[0, self.pos, :] = new
            return H._pack(o, h)
        return f

    def __enter__(self):
        self._h = [self.blocks[l].register_forward_hook(self._mk(l)) for l in self.layers]; return self

    def __exit__(self, *a):
        [x.remove() for x in self._h]


class CurrentBaseAdd:
    """Amendment 6 row q_rem_cb_pre: h' = h_evolving + delta_l at `positions` for every block in `layers`; the plane is free.
    Records the realized post-cast write (rho, kappa vs the evolving base) and the plane coordinates Q_l^T (h' - h_clean)."""
    def __init__(self, blocks, layers, positions, delta, Q, hclean):
        self.blocks, self.layers = blocks, sorted(layers); self.pos = torch.as_tensor(positions, dtype=torch.long)
        self.delta, self.Q, self.hclean, self._h, self.post, self.plane = delta, Q, hclean, [], {}, {}

    def _mk(self, l):
        @torch.autocast("cuda", enabled=False)
        def f(m, i, o):
            h = H._out(o).clone(); hp = h[0, self.pos, :].float(); dl = self.delta[l].to(hp.device).float()
            new = (hp + dl).to(h.dtype); real = new.float() - hp
            self.post[l] = {"rho": float(real.norm() / dl.norm().clamp_min(1e-8)),
                            "kappa": float(torch.nn.functional.cosine_similarity(real.flatten()[None], dl.flatten()[None]).item())}
            self.plane[l] = ((new.float() - self.hclean[l].to(hp.device).float()) @ self.Q[l].to(hp.device).float()).detach().cpu()   # [P, 2]
            h[0, self.pos, :] = new
            return H._pack(o, h)
        return f

    def __enter__(self):
        self._h = [self.blocks[l].register_forward_hook(self._mk(l)) for l in self.layers]; return self

    def __exit__(self, *a):
        [x.remove() for x in self._h]


# ----------------------------------------------------------------------------------------------------------------- smoke (no model)
def smoke():
    tok = R.make_tokenizer()
    words_int = sorted({it["intermediate"] for it in ITEMS} | {it["swap_to"] for it in ITEMS}); words_ans = sorted({it["answer"] for it in ITEMS} | {it["swap_answer"] for it in ITEMS})
    ok_int = all(Rn.single_token_id(tok, w) is not None for w in words_int); ok_ans = all(Rn.single_token_id(tok, w) is not None for w in words_ans)
    print(f"intermediate words ({len(words_int)}) single-token in leading-space form: {ok_int} | answer words ({len(words_ans)}): {ok_ans}")
    print("collisions int/ans:", sorted(set(words_int) & set(words_ans)), "| with decoys:", sorted((set(words_int) | set(words_ans)) & set(DECOYS)))
    V = len(tok); toks = tok.convert_ids_to_tokens(list(range(V))); wmask = np.array([bool(WORD_RE.match(t or "")) for t in toks])
    print(f"tokenizer vocab {V}; restricted word-like dictionary {int(wmask.sum())} entries (e.g. {[toks[i] for i in np.flatnonzero(wmask)[:5]]})")
    for it in ITEMS[:3]:
        print(" spellings", it["answer"], [tok.decode(list(s)) for s in spellings(tok, it["answer"])], "|", it["swap_answer"], [tok.decode(list(s)) for s in spellings(tok, it["swap_answer"])])
    it = ITEMS[0]; print(f" classify ({it['name']}):", {s: classify_atom(s, it) for s in [" Spain", " Spanish", " Madrid", " Canada", " Ottawa", " span", " the", " Spa", " Can"]})
    col = [it for it in ITEMS if it["answer"] == "Russian" or it["swap_answer"] == "Russian"]
    for it in col: print(f" collision item ({it['name']}):", {s: classify_atom(s, it) for s in [" Russian", " Russia", " Arabic", " Egypt", " Egyptian"]})
    # CPU unit test of the pursuit machinery on synthetic data
    g = torch.Generator().manual_seed(0); d, V_, N = 64, 500, 6
    D = torch.randn(V_, d, generator=g); D = (D / D.norm(dim=1, keepdim=True)).half()
    true_sel = torch.stack([torch.randperm(V_, generator=g)[:3] for _ in range(N)]); coef = torch.rand(N, 3, generator=g) + 0.5
    X = torch.einsum("nk,nkd->nd", coef, D[true_sel].float()) + 0.01 * torch.randn(N, d, generator=g)
    sel, stop, coefs = pursuit_ls(D, X, 8, [2, 3, 8])
    rec_ = float((torch.stack([torch.isin(true_sel[n], sel[n, :3]).float().mean() for n in range(N)])).mean())
    resid3 = float((X - torch.einsum("nk,nkd->nd", coefs[3], D[sel[:, :3]].float())).norm(dim=1).mean() / X.norm(dim=1).mean())
    print(f" pursuit_ls unit test: planted atoms recovered in the first 3 picks {rec_:.2f} (expect 1.00); relative residual at k=3 {resid3:.3f} (noise floor ~0.05); stops {stop.tolist()}")
    A3 = D[sel[:, :3]].float(); c_plain = torch.linalg.lstsq(A3.transpose(1, 2), X[:, :, None]).solution[:, :, 0]
    print(f" ls_refit vs torch.linalg.lstsq max abs diff {float((coefs[3] - c_plain).abs().max()):.2e} (ridge {RIDGE})")
    seln, cn, ok, nfb = pursuit_nnls(D, X, 3)
    recn = float((torch.stack([torch.isin(true_sel[n], seln[n]).float().mean() for n in range(N)])).mean())
    print(f" pursuit_nnls unit test: recovered {recn:.2f}, coefficients nonneg {bool((cn >= 0).all())}, KKT pass {int(ok.sum())}/{N}, fallbacks {nfb}")
    X2 = D[true_sel[:, 0]].float() - 0.7 * D[true_sel[:, 1]].float()
    A2 = D[true_sel[:, :2]].float(); c2 = nnls_batched(A2, X2); ok2 = kkt_check(A2, X2, c2); c2s = nnls_scipy(A2, X2)
    print(f" nnls with a negative component: batched c {[round(x, 4) for x in c2[0].tolist()]} kkt {ok2.tolist()} | scipy c {[round(x, 4) for x in c2s[0].tolist()]} kkt {kkt_check(A2, X2, c2s).tolist()}")
    print("SMOKE OK")


# ----------------------------------------------------------------------------------------------------------------- main
def main():
    if STAGE == "smoke":
        smoke(); return
    tok = R.make_tokenizer()
    from jlens.hf import from_hf
    model = R.load_model(); lm = from_hf(model, tok, compile=False)
    ALL = list(range(R.N_BLOCKS)); run = H.make_run(model, lm, ALL); dev = lm.input_device
    LEN = R.load_lenses(("J_NP",))["J_NP"]
    words_int = sorted({it["intermediate"] for it in ITEMS} | {it["swap_to"] for it in ITEMS}); words_ans = sorted({it["answer"] for it in ITEMS} | {it["swap_answer"] for it in ITEMS})
    COLS = words_int + [w for w in words_ans if w not in words_int] + [d_ for d_ in DECOYS if d_ not in words_int + words_ans]
    TID = {w: Rn.single_token_id(tok, w) for w in COLS}; assert all(v is not None for v in TID.values()), TID       # gate 1: single-token forms
    ro = RO.LensReadout(model, lm, LEN, [TID[w] for w in COLS])
    gamma = ro.gamma.to(dev); WU = ro.Wu; V = WU.shape[0]; d = WU.shape[1]
    toks = tok.convert_ids_to_tokens(list(range(V))); wmask = torch.tensor([bool(WORD_RE.match(t or "")) for t in toks], device=dev); widx = wmask.nonzero()[:, 0]
    NAMING = {w: {l: ro.folded_direction(l, TID[w]) for l in SWAP_L} for w in words_int + words_ans}
    NAMING63 = {w: (WU[TID[w]].float() * gamma) / (WU[TID[w]].float() * gamma).norm() for w in words_int + words_ans}
    fp = lambda: Fp32Residual(lm.layers, FP32_FROM)

    def build_dict(l, restrict=False):
        """Unit folded directions a_v = J_l^T (gamma * w_v) for every vocabulary entry (or the restricted set) -> [V', d] fp16."""
        J = LEN.jacobians[l].to(dev).float(); src = WU[widx] if restrict else WU
        out = torch.empty(src.shape[0], d, dtype=torch.float16, device=dev)
        for a in range(0, src.shape[0], 32768):
            blk = (src[a:a + 32768].float() * gamma) @ J
            out[a:a + 32768] = (blk / blk.norm(dim=1, keepdim=True).clamp_min(1e-12)).half(); del blk
        return out

    def atom_dirs(l, ids):
        """The unit folded directions of the given vocabulary ids at block l -> [n, d] fp32 (bitwise the rows of build_dict)."""
        J = LEN.jacobians[l].to(dev).float(); a = (WU[ids].float() * gamma) @ J
        return (a / a.norm(dim=1, keepdim=True).clamp_min(1e-12)).half().float()

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

    RAW, RAWZ = {}, {}
    META = {"columns": COLS, "n_int_words": len(words_int), "n_ans_words": len(words_ans), "decoys": [d_ for d_ in DECOYS if d_ not in words_int + words_ans],
            "carriers": CARRIERS, "swap_layers": [SWAP_L[0], SWAP_L[-1]], "fp32_from": FP32_FROM, "seed": SEED, "stage": STAGE, "cells": {}, "items": ITEMS,
            "question": QUESTION, "s_donor0_seq_bf16_quoted": S_DONOR0_SEQ_BF16, "readout_band": [RB[0], RB[-1]], "zq_layers": [LZ[0], LZ[-1]], "ks": KS, "k_nnls": KNN, "kmax": KMAX,
            "restricted_dictionary_size": int(len(widx)), "vocab_size": int(V), "ridge_rel": RIDGE, "materials": "anthropics/jacobian-lens@581d398 data/experiments/probe-swap.json",
            "design": "H3/design_specs/two_hop_organism.md (Amendment 6)",
            "seeds": {"random_2plane": "SEED + cell", "random_k_removal": "SEED + 100000 + cell", "ccr_frames": "SEED + 200000 + cell", "energy_reference": "SEED + 777"}}
    t0 = time.time(); n = 0

    # ------------------------------------------------------------------ Phase A: clean and donor forwards, cell geometry, states at Q
    cellinfo = {}; Xacc = {l: [] for l in SWAP_L}
    for it in ITEMS:
        for ck in CARRIERS:
            car = M.CARRIERS[ck]; base = f"{it['name']}|{ck}"
            body, dbody = clue_body(it["prompt"]), clue_body(it["donor_prompt"])
            r = Rn.render(tok, utext(body, car), car, sources=[("CLUE", body, False)], extra_turns=[(QUESTION, "")])
            rd = Rn.render(tok, utext(dbody, car), car, sources=[("CLUE", dbody, False)], extra_turns=[(QUESTION, "")])
            assert len(rd) == len(r) and rd.spans["CLUE"]["full"] == r.spans["CLUE"]["full"] and rd.meta["carrier_start"] == r.meta["carrier_start"] and rd.meta["carrier_end"] == r.meta["carrier_end"], f"G3 donor geometry {base}"
            span = r.spans["CLUE"]["full"]; cs, ce = r.meta["carrier_start"], r.meta["carrier_end"]
            Q = list(range(ce, len(r))); qpre = Q[:-1]; s = Q[-1]
            assert s == len(r) - 1 == r.spans["answer"] and s not in qpre, f"scoring position {base}"
            assert list(r.ids[Q[0]:]) == list(rd.ids[Q[0]:]), f"gate 1: q span token ids differ between recipient and donor {base}"
            ids = list(r.ids); cA, cB = spellings(tok, it["answer"]), spellings(tok, it["swap_answer"])
            sA, vA, (ac, lg) = seqscore(ids, fp, cA); sB, vB, _ = seqscore(ids, fp, cB); n += len(cA) + len(cB)
            dA, _, (ad, lgd) = seqscore(list(rd.ids), fp, cA); dB, _, _ = seqscore(list(rd.ids), fp, cB); n += len(cA) + len(cB)
            RAW[f"{base}|clean|seq_answer"], RAW[f"{base}|clean|seq_swap"] = np.float32(sA), np.float32(sB)
            RAW[f"{base}|donor|seq_answer"], RAW[f"{base}|donor|seq_swap"] = np.float32(dA), np.float32(dB)
            hq = {l: ac[l][0, Q, :].float().cpu().clone() for l in SWAP_L}; hqY = {l: ad[l][0, Q, :].float().cpu().clone() for l in SWAP_L}
            for l in SWAP_L: Xacc[l].append(ac[l][0, 4:, :].half().cpu())
            cos = {l: float(NAMING[it["intermediate"]][l] @ NAMING[it["swap_to"]][l]) for l in SWAP_L}; cosa = {l: float(NAMING[it["answer"]][l] @ NAMING[it["swap_answer"]][l]) for l in SWAP_L}
            cellinfo[base] = {"it": it, "r": r, "rd": rd, "ids": ids, "cA": cA, "cB": cB, "Q": Q, "qpre": qpre, "s": s, "span": span, "cs": cs, "ce": ce, "hq": hq, "hqY": hqY}
            META["cells"][base] = {"intermediate": it["intermediate"], "swap_to": it["swap_to"], "answer": it["answer"], "swap_answer": it["swap_answer"],
                                   "span": [span[0], span[-1]], "carrier": [cs, ce], "q": [Q[0], Q[-1]], "q_pre": [qpre[0], qpre[-1]], "scoring": s, "n_tokens": len(r),
                                   "cos_int_swap_max_abs": float(max(abs(v) for v in cos.values())), "cos_ans_swap_max_abs": float(max(abs(v) for v in cosa.values())),
                                   "spellings_answer": [list(x) for x in cA], "spellings_swap": [list(x) for x in cB]}
            for tag, rr, acts, lgx in ((f"{base}|clean", r, ac, lg), (f"{base}|donor", rd, ad, lgd)):
                RAWZ[f"{tag}|zq"] = ro.z(acts, Q, LZ).astype(np.float16)
                RAW[f"{tag}|nll"] = np.float32(RO.carrier_damage(lgx[:, :len(ids)], list(rr.ids), cs, ce)[0]); RAW[f"{tag}|greedy"] = tok.decode(int(lgx[0, len(ids) - 1].argmax())).strip()
                lp = torch.log_softmax(lgx[0, len(ids) - 1].float(), -1)
                RAW[f"{tag}|s_answer"] = np.float32(float(torch.logsumexp(lp[forms(tok, it["answer"])], 0))); RAW[f"{tag}|s_swap"] = np.float32(float(torch.logsumexp(lp[forms(tok, it["swap_answer"])], 0)))
                Q63 = torch.stack([NAMING63[it["intermediate"]], NAMING63[it["swap_to"]]], 1)
                RAW[f"{tag}|c63"] = (acts[63][0, qpre, :].float() @ Q63).cpu().numpy().astype(np.float32); RAW[f"{tag}|c63s"] = (acts[63][0, s, :].float() @ Q63).cpu().numpy().astype(np.float32)
            del ac, ad, lg, lgd
        print(f"  [A] {it['name']}: {n} forwards ({time.time()-t0:.0f}s)", flush=True)
    bases = list(cellinfo)
    comp_c = np.mean([RAW[f"{b}|clean|seq_answer"] > RAW[f"{b}|clean|seq_swap"] for b in bases]); comp_d = np.mean([RAW[f"{b}|donor|seq_swap"] > RAW[f"{b}|donor|seq_answer"] for b in bases])
    META["gate2"] = {"competence_clean32_seq": float(comp_c), "competence_donor32_seq": float(comp_d), "pass": bool(comp_c >= 0.9 and comp_d >= 0.9)}
    print(f"  [gate 2] competence clean {comp_c:.3f} donor {comp_d:.3f} -> {'PASS' if META['gate2']['pass'] else 'FAIL'}", flush=True)
    if not META["gate2"]["pass"] and STAGE == "qsplit6":
        json.dump(META, open(os.path.join(OUT, f"meta_{STAGE}_gatefail.json"), "w"), indent=1, default=str); print("gate 2 failed: stopping per Amendment 6 §4"); return

    # ------------------------------------------------------------------ Phase B: pursuits per block (q_pre positions and the scoring position), energy reference
    nq = len(cellinfo[bases[0]]["qpre"]); assert all(len(cellinfo[b]["qpre"]) == nq for b in bases), "q_pre length differs across cells"
    PUR, ENERGY = {}, {}; g_e = torch.Generator().manual_seed(SEED + 777)
    for l in SWAP_L:
        tb = time.time()
        Xq = torch.stack([cellinfo[b]["hqY"][l][:-1] - cellinfo[b]["hq"][l][:-1] for b in bases]).reshape(-1, d).to(dev)    # [n_cells*nq, d]
        Xs = torch.stack([cellinfo[b]["hqY"][l][-1] - cellinfo[b]["hq"][l][-1] for b in bases]).to(dev)                     # [n_cells, d]
        X = torch.cat([Xq, Xs], 0); nqall = Xq.shape[0]
        D = build_dict(l); sel, stop, coefs = pursuit_ls(D, X, KMAX, KS)
        Dw = build_dict(l, restrict=True); seln, cn, kkt, nfb = pursuit_nnls(Dw, X, KNN); seln_v = widx[seln]; del Dw
        PUR[l] = {"sel": sel.cpu().numpy().astype(np.int32), "stop": stop.cpu().numpy().astype(np.int32), "coef": {k: coefs[k].cpu().numpy().astype(np.float32) for k in KS},
                  "sel_nn": seln_v.cpu().numpy().astype(np.int32), "coef_nn": cn.cpu().numpy().astype(np.float32), "kkt": kkt.cpu().numpy(), "n_fallback": int(nfb)}
        # energy fractions on q_pre: J_k part vs k directions drawn from N(0, Sigma_l) vs k/d
        Xc = torch.cat(Xacc[l], 0).float().to(dev); Xc = Xc - Xc.mean(0, keepdim=True); ns = Xc.shape[0]
        e_rand = {k: [] for k in KS}
        for _ in range(5):
            xi = torch.randn(ns, KMAX, generator=g_e).to(dev); U = torch.linalg.qr(Xc.T @ xi / ns ** 0.5)[0]
            for k in KS: e_rand[k].append(float((((Xq @ U[:, :k]) ** 2).sum(1) / (Xq ** 2).sum(1)).mean()))
        e_J = {}
        for k in KS:
            A = D[sel[:nqall, :k]].float(); vJ = torch.einsum("nk,nkd->nd", coefs[k][:nqall], A); e_J[k] = float(((vJ ** 2).sum(1) / (Xq ** 2).sum(1)).mean()); del A, vJ
        ENERGY[l] = {"e_J": e_J, "e_rand_sigma": {k: float(np.mean(v)) for k, v in e_rand.items()}, "k_over_d": {k: k / d for k in KS}, "n_cov_samples": int(ns)}
        del D, Xc, X, Xq, Xs; torch.cuda.empty_cache()
        print(f"  [B] block {l}: pursuits done ({time.time()-tb:.0f}s); e_J {[round(e_J[k], 3) for k in KS]} e_rand(Sigma) {[round(ENERGY[l]['e_rand_sigma'][k], 3) for k in KS]}; "
              f"stops {int((stop < KMAX).sum())}; NNLS kkt {int(kkt.sum())}/{len(kkt)} fallback {nfb}", flush=True)
    META["energy"] = {str(l): ENERGY[l] for l in SWAP_L}
    PR = {"bases": np.array(bases), "n_qpre": np.int32(nq), "layout": np.array([f"rows 0..{len(bases)*nq-1}: cell-major q_pre positions ({nq} per cell); rows {len(bases)*nq}..: scoring position per cell"])}
    for l in SWAP_L:
        for key in ("sel", "stop", "sel_nn", "coef_nn", "kkt"): PR[f"L{l}|{key}"] = PUR[l][key]
        for k in KS: PR[f"L{l}|coef{k}"] = PUR[l]["coef"][k]
    np.savez_compressed(os.path.join(OUT, f"raw_pursuit_{STAGE}.npz"), **PR)
    print(f"  [B] saved raw_pursuit_{STAGE}.npz ({time.time()-t0:.0f}s)", flush=True)

    # ------------------------------------------------------------------ Phase C: rows per cell
    def targets_for(bi, b):
        """Fixed per-block targets on q_pre for every fixed-target row of this cell, the pinned spans at s (+ random controls),
        the current-base deltas, the planes, the norm diagnostics and the selected atoms with their classes."""
        info = cellinfo[b]; it = info["it"]; q0 = bi * nq; si = len(bases) * nq + bi
        T = {k: {} for k in ("q_full_pre", "q_plane_pre", "q_rem_pre", "q_ansplane_pre", "q_ansrem_pre", "q_J25nn_pre", "q_rem25nn_pre", "q_rem25ans_pre", "q_rem25int_pre", "q_rand_pre", "q_rem_rand_pre")}
        for k in KS: T[f"q_J{k}_pre"] = {}; T[f"q_J{k}rem_pre"] = {}; T[f"q_rand{k}rem_pre"] = {}
        PIN = {"q_rem_pre": {}, "q_rem25nn_pre": {}}; PINR = {"q_rem_pre": {}, "q_rem25nn_pre": {}}
        for k in KS: PIN[f"q_J{k}rem_pre"] = {}; PINR[f"q_J{k}rem_pre"] = {}
        CB, Qp, Qa, norms = {}, {}, {}, []; atoms = {"sel": {}, "sel_s": {}, "stop": {}, "stop_s": {}, "cls": {}, "cls_s": {}, "sel_nn": {}, "cls_nn": {}, "sel_nn_s": {}}
        g = torch.Generator().manual_seed(SEED + bi); gk = torch.Generator().manual_seed(SEED + 100000 + bi); g2 = torch.Generator().manual_seed(SEED + 200000 + bi)
        for l in SWAP_L:
            h = info["hq"][l][:-1].to(dev); hY = info["hqY"][l][:-1].to(dev); dh = hY - h
            Qp[l] = torch.linalg.qr(torch.stack([NAMING[it["intermediate"]][l], NAMING[it["swap_to"]][l]], 1).float())[0]
            Qa[l] = torch.linalg.qr(torch.stack([NAMING[it["answer"]][l], NAMING[it["swap_answer"]][l]], 1).float())[0]
            Rp = random_frame(d, 2, g, dev)
            vJ = (dh @ Qp[l]) @ Qp[l].T; vA = (dh @ Qa[l]) @ Qa[l].T; vRr = (dh @ Rp) @ Rp.T
            vR = vRr * (vJ.norm(dim=1, keepdim=True) / vRr.norm(dim=1, keepdim=True).clamp_min(1e-12)); assert torch.allclose(vR.norm(dim=1), vJ.norm(dim=1), rtol=1e-4, atol=1e-6), f"gate 3 norm match {b} {l}"
            T["q_full_pre"][l] = hY.clone(); T["q_plane_pre"][l] = h + vJ; T["q_rem_pre"][l] = h + dh - vJ
            T["q_ansplane_pre"][l] = h + vA; T["q_ansrem_pre"][l] = h + dh - vA; T["q_rand_pre"][l] = h + vR; T["q_rem_rand_pre"][l] = h + dh - vR
            CB[l] = (dh - vJ).clone()
            PIN["q_rem_pre"][l] = Qp[l]; PINR["q_rem_pre"][l] = orth_against(random_frame(d, 2, g2, dev), Qp[l])
            # J_k rows from the stored pursuits (LS coefficients on the selected atoms, directions recomputed)
            sel = torch.as_tensor(PUR[l]["sel"][q0:q0 + nq], device=dev); sel_s = torch.as_tensor(PUR[l]["sel"][si], device=dev); stop_s = int(PUR[l]["stop"][si])
            cls_all = np.array([[classify_atom(tok.decode([int(v)]), it) for v in row] for row in sel.cpu().numpy()])          # [nq, KMAX]
            cls_s_all = np.array([classify_atom(tok.decode([int(v)]), it) for v in sel_s.cpu().numpy()])                       # [KMAX]
            rowd = {"dh": float(dh.norm(dim=1).mean()), "vJ2": float(vJ.norm(dim=1).mean()), "vA2": float(vA.norm(dim=1).mean())}
            for k in KS:
                A = atom_dirs(l, sel[:, :k].reshape(-1)).reshape(nq, k, d); c = torch.as_tensor(PUR[l]["coef"][k][q0:q0 + nq], device=dev)
                vk = torch.einsum("nk,nkd->nd", c, A); T[f"q_J{k}_pre"][l] = h + vk; T[f"q_J{k}rem_pre"][l] = h + dh - vk
                Rk = random_frame(d, k, gk, dev); vRk = (dh @ Rk) @ Rk.T; vRk = vRk * (vk.norm(dim=1, keepdim=True) / vRk.norm(dim=1, keepdim=True).clamp_min(1e-12))
                assert torch.allclose(vRk.norm(dim=1), vk.norm(dim=1), rtol=1e-4, atol=1e-6), f"gate 3 norm match k={k} {b} {l}"; T[f"q_rand{k}rem_pre"][l] = h + dh - vRk
                rowd[f"vJ{k}"] = float(vk.norm(dim=1).mean())
                # atom-type norm shares ||v_C|| / ||v_Jk|| per position (answer, intermediate, other), on q_pre and at s
                sh = [(torch.einsum("nk,nkd->nd", c * torch.as_tensor(cls_all[:, :k] == which, device=dev).float(), A).norm(dim=1) / vk.norm(dim=1).clamp_min(1e-12)).cpu().numpy() for which in ("answer", "intermediate", "other")]
                atoms.setdefault(f"clsshare{k}", {})[l] = np.stack(sh, 1).astype(np.float32)                                      # [nq, 3]
                ks = min(k, max(stop_s, 1)); As = atom_dirs(l, sel_s[:ks]); cs_ = torch.as_tensor(PUR[l]["coef"][k][si][:ks], device=dev); vs = cs_ @ As
                sh_s = [float(((cs_ * torch.as_tensor(cls_s_all[:ks] == which, device=dev).float()) @ As).norm() / vs.norm().clamp_min(1e-12)) for which in ("answer", "intermediate", "other")]
                atoms.setdefault(f"clsshare{k}_s", {})[l] = np.array(sh_s, np.float32)                                            # [3]
                U = torch.linalg.qr(As.T)[0]                                                                                     # pinned span at s: the k atoms of the pursuit on the donor's dh_s
                PIN[f"q_J{k}rem_pre"][l] = U; PINR[f"q_J{k}rem_pre"][l] = orth_against(random_frame(d, ks, g2, dev), U)
                if k == 25:
                    cls = cls_all[:, :25]
                    for which, name in (("answer", "q_rem25ans_pre"), ("intermediate", "q_rem25int_pre")):
                        tgt = (h + dh).clone()
                        for p in range(nq):
                            m_ = torch.as_tensor(cls[p] == which, device=dev)
                            if m_.any(): Up = torch.linalg.qr(A[p][m_].T)[0]; tgt[p] = tgt[p] - Up @ (Up.T @ dh[p])
                        T[name][l] = tgt
                del A
            # NNLS restricted-dictionary row and its pinned support at s
            seln = torch.as_tensor(PUR[l]["sel_nn"][q0:q0 + nq], device=dev); cnn = torch.as_tensor(PUR[l]["coef_nn"][q0:q0 + nq], device=dev)
            An = atom_dirs(l, seln.reshape(-1)).reshape(nq, KNN, d); vnn = torch.einsum("nk,nkd->nd", cnn, An)
            T["q_J25nn_pre"][l] = h + vnn; T["q_rem25nn_pre"][l] = h + dh - vnn; rowd["vJ25nn"] = float(vnn.norm(dim=1).mean())
            cls_nn = np.array([[classify_atom(tok.decode([int(v)]), it) for v in row] for row in seln.cpu().numpy()])
            sh = [(torch.einsum("nk,nkd->nd", cnn * torch.as_tensor(cls_nn == which, device=dev).float(), An).norm(dim=1) / vnn.norm(dim=1).clamp_min(1e-12)).cpu().numpy() for which in ("answer", "intermediate", "other")]
            atoms.setdefault("clsshare_nn", {})[l] = np.stack(sh, 1).astype(np.float32); del An
            seln_s = torch.as_tensor(PUR[l]["sel_nn"][si], device=dev); cnn_s = torch.as_tensor(PUR[l]["coef_nn"][si], device=dev)
            supp = seln_s[cnn_s > 0]; supp = supp if len(supp) > 0 else seln_s[:1]
            Un = torch.linalg.qr(atom_dirs(l, supp).T)[0]; PIN["q_rem25nn_pre"][l] = Un; PINR["q_rem25nn_pre"][l] = orth_against(random_frame(d, Un.shape[1], g2, dev), Un)
            norms.append([rowd["dh"], rowd["vJ2"], rowd["vA2"]] + [rowd[f"vJ{k}"] for k in KS] + [rowd["vJ25nn"]])
            atoms["sel"][l] = sel.cpu().numpy(); atoms["sel_s"][l] = sel_s.cpu().numpy(); atoms["stop"][l] = PUR[l]["stop"][q0:q0 + nq]; atoms["stop_s"][l] = stop_s
            atoms["cls"][l] = cls_all; atoms["cls_s"][l] = cls_s_all; atoms["cls_nn"][l] = cls_nn
            atoms["sel_nn"][l] = seln.cpu().numpy(); atoms["sel_nn_s"][l] = seln_s.cpu().numpy()
        return T, PIN, PINR, CB, Qp, Qa, np.array(norms, np.float32), atoms

    def rec(tag, b, acts, logits):
        info = cellinfo[b]; it = info["it"]; L = len(info["ids"]); Q = info["Q"]; qpre = info["qpre"]
        lp = torch.log_softmax(logits[0, L - 1].float(), -1)
        RAW[f"{tag}|s_answer"] = np.float32(float(torch.logsumexp(lp[forms(tok, it["answer"])], 0))); RAW[f"{tag}|s_swap"] = np.float32(float(torch.logsumexp(lp[forms(tok, it["swap_answer"])], 0)))
        RAW[f"{tag}|greedy"] = tok.decode(int(logits[0, L - 1].argmax())).strip()
        RAWZ[f"{tag}|zq"] = ro.z(acts, Q, LZ).astype(np.float16)
        RAW[f"{tag}|nll"] = np.float32(RO.carrier_damage(logits[:, :L], info["ids"], info["cs"], info["ce"])[0])
        Q63 = torch.stack([NAMING63[it["intermediate"]], NAMING63[it["swap_to"]]], 1)
        RAW[f"{tag}|c63"] = (acts[63][0, qpre, :].float() @ Q63).cpu().numpy().astype(np.float32)      # [P, 2] projections on the raw unit naming directions at block 63
        RAW[f"{tag}|c63s"] = (acts[63][0, info["s"], :].float() @ Q63).cpu().numpy().astype(np.float32)

    ROWS = None
    for bi, b in enumerate(bases):
        info = cellinfo[b]; it = info["it"]; ids = info["ids"]; cA, cB = info["cA"], info["cB"]; qpre, s, Q = info["qpre"], info["s"], info["Q"]
        tc = time.time()
        sA0, _, (ac, lg) = seqscore(ids, fp, cA); n += len(cA)          # same forward as Phase A: bitwise determinism gate
        assert all(torch.equal(ac[l][0, Q, :].float().cpu(), info["hq"][l]) for l in SWAP_L), f"Phase A/C clean determinism {b}"
        assert abs(sA0 - float(RAW[f"{b}|clean|seq_answer"])) < 1e-6, f"clean seq_answer differs between phases {b}"
        T, PIN, PINR, CB, Qp, Qa, norms, atoms = targets_for(bi, b)
        RAW[f"{b}|normdiag"] = norms                                          # per block: |dh|, |vJ2|, |vA2|, |vJ_k| for k in KS, |vJ25nn|  (means over q_pre positions)
        for l in SWAP_L:
            RAW[f"{b}|L{l}|atoms_qpre"] = atoms["sel"][l].astype(np.int32); RAW[f"{b}|L{l}|atoms_s"] = atoms["sel_s"][l].astype(np.int32); RAW[f"{b}|L{l}|stop_qpre"] = atoms["stop"][l].astype(np.int32)
            RAW[f"{b}|L{l}|stop_s"] = np.int32(atoms["stop_s"][l]); RAW[f"{b}|L{l}|cls_qpre"] = atoms["cls"][l]; RAW[f"{b}|L{l}|cls_s"] = atoms["cls_s"][l]
            RAW[f"{b}|L{l}|atoms_nn"] = atoms["sel_nn"][l].astype(np.int32); RAW[f"{b}|L{l}|atoms_nn_s"] = atoms["sel_nn_s"][l].astype(np.int32); RAW[f"{b}|L{l}|cls_nn"] = atoms["cls_nn"][l]
            RAW[f"{b}|L{l}|plane_coord_full"] = ((T["q_full_pre"][l] - info["hq"][l][:-1].to(dev)) @ Qp[l]).cpu().numpy().astype(np.float32)     # [P, 2] the full donor's plane coordinate
            for k in KS: RAW[f"{b}|L{l}|clsshare{k}"] = atoms[f"clsshare{k}"][l]; RAW[f"{b}|L{l}|clsshare{k}_s"] = atoms[f"clsshare{k}_s"][l]        # [P, 3] / [3]: answer, intermediate, other
            RAW[f"{b}|L{l}|clsshare_nn"] = atoms["clsshare_nn"][l]
        hclean_s = {l: info["hq"][l][-1] for l in SWAP_L}; hclean_q = {l: info["hq"][l][:-1] for l in SWAP_L}
        conds = {k: (lambda k=k: H.Both(fp(), H.SpanWriter(lm.layers, SWAP_L, qpre, T[k]))) for k in T}
        conds["q_rem_cb_pre"] = lambda: H.Both(fp(), CurrentBaseAdd(lm.layers, SWAP_L, qpre, CB, Qp, hclean_q))
        cc_rows = ["q_rem_pre", "q_rem25nn_pre"] + [f"q_J{k}rem_pre" for k in KS]; CCT = {}
        for row in cc_rows:
            conds[f"{row}_cc"] = (lambda row=row: H.Both(fp(), H.SpanWriter(lm.layers, SWAP_L, qpre, T[row]), SubspaceClampMatched(lm.layers, SWAP_L, s, PIN[row], hclean_s)))
        for row in cc_rows:   # the matched controls come after their _cc rows so CCT[row] exists
            conds[f"{row}_ccr"] = (lambda row=row: H.Both(fp(), H.SpanWriter(lm.layers, SWAP_L, qpre, T[row]), SubspaceClampMatched(lm.layers, SWAP_L, s, PINR[row], hclean_s, target=CCT[row])))
        ROWS = list(conds)
        for cond, mk in conds.items():
            ctx = mk(); sA, vA, (a_, l_) = seqscore(ids, lambda: ctx, cA); sB, vB, _ = seqscore(ids, lambda: ctx, cB); n += len(cA) + len(cB); tag = f"{b}|{cond}"
            RAW[f"{tag}|seq_answer"], RAW[f"{tag}|seq_swap"] = np.float32(sA), np.float32(sB)
            RAW[f"{tag}|seq_answer_all"], RAW[f"{tag}|seq_swap_all"] = np.array(vA, np.float32), np.array(vB, np.float32)
            assert all(torch.equal(a_[l][0, :qpre[0], :], ac[l][0, :qpre[0], :]) for l in ALL), f"prefix touched {tag}"
            base_row = cond[:-3] if cond.endswith("_cc") else (cond[:-4] if cond.endswith("_ccr") else cond)
            if base_row in T:   # fixed-target rows (and their clamped variants): realized write on q_pre vs the clean base, read-back vs the fixed target
                req = torch.stack([(T[base_row][l] - ac[l][0, qpre, :].float()).flatten() for l in SWAP_L]); real = torch.stack([(a_[l][0, qpre, :].float() - ac[l][0, qpre, :].float()).flatten() for l in SWAP_L])
                nr, nq_ = real.norm(dim=1), req.norm(dim=1); ok = nq_ > 1e-8
                RAW[f"{tag}|rho"] = np.float32(float((nr[ok] / nq_[ok]).mean())) if ok.any() else np.float32(np.nan)
                RAW[f"{tag}|kappa"] = np.float32(float(torch.nn.functional.cosine_similarity(real[ok], req[ok], dim=1).mean())) if ok.any() else np.float32(np.nan)
                RAW[f"{tag}|rberr"] = np.float32(max(float((a_[l][0, qpre, :].float() - T[base_row][l]).abs().max()) for l in SWAP_L))
                RAW[f"{tag}|plane_dev"] = np.float32(np.mean([float(((a_[l][0, qpre, :].float() - T[base_row][l]) @ Qp[l]).abs().max()) for l in SWAP_L]))
            if cond.endswith("_cc") or cond.endswith("_ccr"):
                cl = [x for x in ctx.c if isinstance(x, SubspaceClampMatched)][0]
                RAW[f"{tag}|clamp_req"] = np.array([cl.post[l]["req"] for l in SWAP_L], np.float32); RAW[f"{tag}|clamp_real"] = np.array([cl.post[l]["real"] for l in SWAP_L], np.float32)
                RAW[f"{tag}|clamp_kappa"] = np.array([cl.post[l]["kappa"] for l in SWAP_L], np.float32); RAW[f"{tag}|clamp_dim"] = np.array([PIN[base_row][l].shape[1] for l in SWAP_L], np.int32)
                if cond.endswith("_cc"): CCT[base_row] = {l: cl.post[l]["real"] for l in SWAP_L}
            if cond == "q_rem_cb_pre":
                cb = [x for x in ctx.c if isinstance(x, CurrentBaseAdd)][0]
                RAW[f"{tag}|rho"] = np.float32(np.mean([cb.post[l]["rho"] for l in SWAP_L])); RAW[f"{tag}|kappa"] = np.float32(np.mean([cb.post[l]["kappa"] for l in SWAP_L]))
                RAW[f"{tag}|plane_band"] = np.stack([cb.plane[l].numpy() for l in SWAP_L]).astype(np.float32)       # [27, P, 2]: Q_l^T (h' - h_clean) per block, position
            rec(tag, b, a_, l_); del a_, ctx
        del ac; torch.cuda.empty_cache()
        print(f"  [C] {b}: {n} forwards, {len(conds)} rows ({time.time()-tc:.0f}s cell, {time.time()-t0:.0f}s total) | |dh| {norms[-1][0]:.1f} |vJ2| {norms[-1][1]:.2f} |vJ25| {norms[-1][5]:.2f} |vJ64| {norms[-1][6]:.2f} at L62", flush=True)

    META.update({"run_id": RUN_ID, "n_forwards": n, "elapsed_s": round(time.time() - t0, 1), "rows": ROWS, "n_qpre": nq})
    np.savez_compressed(os.path.join(OUT, f"raw_{STAGE}.npz"), **RAW); np.savez_compressed(os.path.join(OUT, f"raw_{STAGE}_zq.npz"), **RAWZ)
    json.dump(META, open(os.path.join(OUT, f"meta_{STAGE}.json"), "w"), indent=1, default=str)
    sha = lambda f: hashlib.sha256(open(os.path.join(OUT, f), "rb").read()).hexdigest()
    man = R.manifest_block(); man.update({"run_id": RUN_ID, "stage": STAGE, "script": os.path.relpath(__file__, R.PROJECT), "design": "H3/design_specs/two_hop_organism.md (Amendment 6)",
                                          "materials": META["materials"], "raw_sha256": sha(f"raw_{STAGE}.npz"), "raw_zq_sha256": sha(f"raw_{STAGE}_zq.npz"), "raw_pursuit_sha256": sha(f"raw_pursuit_{STAGE}.npz")})
    json.dump(man, open(os.path.join(OUT, f"manifest_{STAGE}.json"), "w"), indent=1)
    print(f"[done {STAGE}] {n} forwards, {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
