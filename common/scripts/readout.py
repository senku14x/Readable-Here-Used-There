"""Lens and residual readouts.

For a block-output residual h at layer l and a Jacobian lens with transport J_l:
    t   = J_l h                                  (transported residual, final-block coordinates)
    r   = sqrt(mean(t^2) + eps)                  (the RMS denominator of the model's final norm)
    n_v = w_v . (gamma * t)                      (numerator for vocabulary row v)
    z_v = n_v / r                                (the normalized lens logit; what the model's own
                                                  final norm + unembedding would produce from t)
Implementation-precision scores follow the model's own path (transport -> bf16 -> final_norm -> W);
float32 diagnostics (n, r) are computed separately so the ordered decomposition of a score change
can be reported (§4.5).
"""
import numpy as np
import torch


class LensReadout:
    def __init__(self, model, lm, lens, columns_ids, eps=None):
        """columns_ids: list of vocabulary ids read as columns (targets, decoys, donors...)."""
        self.model, self.lm, self.lens = model, lm, lens
        self.norm = lm._final_norm
        # Qwen3_5RMSNorm computes norm(x) * (1 + weight) with a zero-initialised weight; the effective gain is
        # gamma = 1 + weight. Verified against the transformers 5.15.0 source in common/configs/instrument_gates.log.
        w = self.norm.weight.detach().float()
        self.gamma = (1.0 + w) if type(self.norm).__name__ == "Qwen3_5RMSNorm" else w
        self.gamma_note = "1+weight (Qwen3_5RMSNorm)" if type(self.norm).__name__ == "Qwen3_5RMSNorm" else "weight"
        self.eps = float(getattr(self.norm, "variance_epsilon", getattr(self.norm, "eps", 1e-6))) if eps is None else eps
        self.Wu = model.lm_head.weight.detach()
        self.set_columns(columns_ids)

    def set_columns(self, columns_ids):
        self.cols = list(columns_ids)
        self.W_sub = self.Wu[self.cols]
        self.W_subF = self.W_sub.float()

    @torch.no_grad()
    def z(self, acts, positions, layers):
        """Implementation-precision z over `layers` -> [L, P, ncols] float32 (model's own norm path)."""
        out = torch.empty(len(layers), len(positions), len(self.cols))
        for i, l in enumerate(layers):
            h = acts[int(l)][0, positions, :].float()
            t = self.lens.transport(h, int(l)).to(torch.bfloat16)
            out[i] = (self.norm(t) @ self.W_sub.T).float().cpu()
        return out.numpy()

    @torch.no_grad()
    def diagnostics(self, acts, positions, layers):
        """float32 numerator n [L,P,ncols], RMS r [L,P], and z32 = n/r."""
        n = torch.empty(len(layers), len(positions), len(self.cols)); r = torch.empty(len(layers), len(positions))
        for i, l in enumerate(layers):
            h = acts[int(l)][0, positions, :].float()
            t = self.lens.transport(h, int(l)).float()
            r[i] = torch.sqrt((t * t).mean(-1) + self.eps).cpu()
            n[i] = ((t * self.gamma) @ self.W_subF.T).cpu()
        return n.numpy(), r.numpy(), (n / r[..., None]).numpy()

    @torch.no_grad()
    def full_vocab_ranks(self, acts, positions, layers, target_ids):
        """Rank (1 = top) of each target id in the full-vocabulary lens readout -> [L, P, n_targets] int32."""
        R = np.empty((len(layers), len(positions), len(target_ids)), np.int32)
        tids = torch.tensor(target_ids, device=self.Wu.device)
        for i, l in enumerate(layers):
            h = acts[int(l)][0, positions, :].float()
            zf = self.lm.unembed(self.lens.transport(h, int(l))).float()
            zt = zf[:, tids]
            R[i] = ((zf[:, :, None] > zt[:, None, :]).sum(1) + 1).cpu().numpy()
        return R

    @torch.no_grad()
    def topk(self, acts, positions, layers, k=10):
        ids = np.empty((len(layers), len(positions), k), np.int32); vals = np.empty((len(layers), len(positions), k), np.float16)
        for i, l in enumerate(layers):
            h = acts[int(l)][0, positions, :].float()
            zf = self.lm.unembed(self.lens.transport(h, int(l))).float()
            v, j = zf.topk(k, dim=-1)
            ids[i], vals[i] = j.cpu().numpy(), v.cpu().numpy()
        return ids, vals

    def folded_direction(self, l, tid, unit=True):
        """a_{v,l} = J_l^T (gamma * w_v): the naming direction for token v at layer l."""
        w = self.Wu[tid].float() * self.gamma
        u = self.lens.jacobians[int(l)].float().T @ w
        return u / u.norm() if unit else u


def presence(z, target_col, decoy_cols):
    """s_J(X) = z_X - mean(z_decoys), averaged over positions then layers -> scalar."""
    return float((z[:, :, target_col] - z[:, :, decoy_cols].mean(-1)).mean())


def pair_margin(z, X_col, Y_col):
    """m^{X->Y} = E[z_Y - z_X] over (layer, position)."""
    return float((z[:, :, Y_col] - z[:, :, X_col]).mean())


@torch.no_grad()
def output_logits_margin(logits, positions, X_id, Y_id):
    """Model-native output logit margin lp(Y) - lp(X) at `positions`."""
    lp = torch.log_softmax(logits[0, positions, :].float(), -1)
    return float((lp[:, Y_id] - lp[:, X_id]).mean())


@torch.no_grad()
def carrier_damage(logits, ids, carrier_start, carrier_end, clean_top1=None):
    """Delta-NLL inputs and top-1 retention on the teacher-forced carrier."""
    lp = torch.log_softmax(logits[0, carrier_start - 1:carrier_end - 1, :].float(), -1)
    tgt = torch.tensor(ids[carrier_start:carrier_end], device=lp.device)
    nll = -float(lp.gather(1, tgt[:, None]).mean())
    top1 = lp.argmax(-1).cpu().numpy().astype(np.int32)
    ret = float((top1 == clean_top1).mean()) if clean_top1 is not None else 1.0
    return nll, top1, ret
