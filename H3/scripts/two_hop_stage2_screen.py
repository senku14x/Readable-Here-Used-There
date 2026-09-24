"""Answer-smuggling screen (Amendment 7 §3): per relation family, a ridge affine map W_U[answer] ~ A W_U[intermediate] + b fitted in
the dual form on centred unembedding rows over all eligible (intermediate, answer) pairs of the family; leave-one-out residual
fraction at the best lambda in {0.01, 0.1, 1} x mean eigenvalue of the pair Gram matrix, beside a mismatched-pairs null (20
permutations of the intermediates). Unembedding rows only (lm_head.weight read from the checkpoint shard); no forward.
Writes H3/outputs/two_hop_organism/screen_stage2.json. Usage: two_hop_stage2_screen.py"""
import os, sys, json, itertools
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "..", "common", "scripts"))
import numpy as np, torch
import registry as R, rendering as Rn
sys.argv = [sys.argv[0]]; sys.path.insert(0, HERE)
from two_hop_items_stage2_build import FAMILIES   # the frozen entity tables (module-level; the builder writes the bank on import, deterministically)

tok = R.make_tokenizer(); single = lambda w: Rn.single_token_id(tok, w)
from huggingface_hub import snapshot_download
from safetensors import safe_open
snap = snapshot_download(R.MODEL, revision=R.REV, allow_patterns=["*.json"]); idx = json.load(open(os.path.join(snap, "model.safetensors.index.json")))
key = "lm_head.weight" if "lm_head.weight" in idx["weight_map"] else "model.embed_tokens.weight"; shard = idx["weight_map"][key]
shard_path = os.path.join(snapshot_download(R.MODEL, revision=R.REV, allow_patterns=[shard, "*.json"]), shard)
with safe_open(shard_path, "pt") as f: WU = f.get_tensor(key).float()
print(f"unembedding rows from {key} in {shard}: {tuple(WU.shape)}")
# the pilot families (released items) are screened on the pilot bank's pairs
pilot = json.load(open(os.path.join(R.PROJECT, "H3", "design_specs", "two_hop_items.json")))["pilot_items"]
fams = {f: [(i, a) for (_, i, a) in ents] for f, (_, ents) in FAMILIES.items()}
for it in pilot: fams.setdefault("pilot-" + it["category"], []).append((it["intermediate"], it["answer"]))
rng = np.random.default_rng(20260924); out = {}


def loo_resid(X, Y, lam_rel):
    """X, Y: [n, d] centred. Dual ridge: A = Y^T X (X X^T + lam I)^-1 in feature space == predictions via kernel K = X X^T.
    Leave-one-out: fit on n-1 pairs, predict the held-out answer row, residual fraction vs the centred answer norm."""
    n = X.shape[0]; res = []
    for i in range(n):
        m = np.ones(n, bool); m[i] = False; Xt, Yt = X[m], Y[m]; mu_x, mu_y = Xt.mean(0), Yt.mean(0)
        Xc, Yc = Xt - mu_x, Yt - mu_y; K = Xc @ Xc.T; lam = lam_rel * np.trace(K) / (n - 1)
        alpha = np.linalg.solve(K + lam * np.eye(n - 1), Xc @ (X[i] - mu_x))          # dual coefficients for the held-out input
        pred = mu_y + alpha @ Yc; res.append(float(((Y[i] - pred) ** 2).sum() / ((Y[i] - mu_y) ** 2).sum()))
    return float(np.mean(res))


for fam, pairs in fams.items():
    pairs = list(dict.fromkeys(p for p in pairs if single(p[0]) is not None and single(p[1]) is not None))
    if len(pairs) < 4: out[fam] = {"n_pairs": len(pairs), "note": "too few pairs"}; continue
    X = np.stack([WU[single(i)].numpy() for i, a in pairs]); Y = np.stack([WU[single(a)].numpy() for i, a in pairs])
    lams = {lr: loo_resid(X, Y, lr) for lr in (0.01, 0.1, 1.0)}; best = min(lams, key=lams.get)
    null = [loo_resid(X[rng.permutation(len(pairs))], Y, best) for _ in range(20)]
    out[fam] = {"n_pairs": len(pairs), "pairs": pairs, "loo_residual_fraction_by_lambda": lams, "best_lambda_rel": best, "loo_residual_fraction": lams[best],
                "null_mean": float(np.mean(null)), "null_p05": float(np.percentile(null, 5)), "flagged": bool(lams[best] <= 0.5 and lams[best] < np.percentile(null, 5))}
    print(f"{fam:24s} n={len(pairs):2d} LOO residual {lams[best]:.3f} (lambda_rel {best}; all {[round(v, 3) for v in lams.values()]}) | null mean {np.mean(null):.3f} p05 {np.percentile(null, 5):.3f} | {'FLAGGED' if out[fam]['flagged'] else 'not flagged'}")
json.dump(out, open(os.path.join(R.out_dir("H3", "outputs", "two_hop_organism"), "screen_stage2.json"), "w"), indent=1)
