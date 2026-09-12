"""Float32-residual regime and an exact-write clamp (query_local_workspace Amendment 4). Kept separate from hooks.py: the shipped
bf16 hooks are unchanged; these are the float32-regime variants used by the clampfix32 and qsplit stages."""
import os, sys
import torch
import hooks as H


class Fp32Residual:
    """Float32 residual from block `from_layer` onward.

    A forward hook on block `from_layer` upcasts its output to float32; every later block then receives a float32
    residual. The forward runs under bf16 autocast, so matmuls, attention and the linear-attention kernels see the same
    bf16 operands as before (the norms already compute in float32); only the residual additions and the hooked writes
    are carried in float32, so coordinate-level writes of norm 0.2-0.5 are no longer lost to bf16 rounding. Enter this
    context before any writer so its hook fires first (writers hook blocks > from_layer in this stage anyway).
    """
    def __init__(self, blocks, from_layer):
        self.blocks, self.layer, self._h, self._ac = blocks, int(from_layer), None, None

    @staticmethod
    def _f(m, i, o):
        h = H._out(o)
        return H._pack(o, h.float()) if h.dtype != torch.float32 else None

    def __enter__(self):
        self._h = self.blocks[self.layer].register_forward_hook(self._f)
        self._ac = torch.autocast("cuda", dtype=torch.bfloat16); self._ac.__enter__()
        return self

    def __exit__(self, *a):
        self._ac.__exit__(*a); self._h.remove()


class CoordClampMatched(H.CoordClampMatched):
    """H.CoordClampMatched with the coordinate/delta arithmetic forced to true float32 under the autocast."""
    def _mk(self, l):
        @torch.autocast("cuda", enabled=False)
        def f(m, i, o):
            h = H._out(o).clone()
            hp = h[0, self.pos, :].float()
            v0, v1 = self.dirs[l]
            V = torch.stack([v0, v1], 1).to(hp.device).float()
            c = hp @ torch.linalg.pinv(V).T
            delta = (self.cref[l].to(hp.device).float() - c) @ V.T
            if self.target is not None:
                t = self.target[l].to(hp.device).float()[:, None]
                delta = delta * (t / delta.norm(dim=1, keepdim=True).clamp_min(1e-8))
            new = (hp + delta).to(h.dtype)
            real = new.float() - hp
            dn = delta.norm(dim=1)
            self.realized[l] = float(dn.mean())
            self.post[l] = {"norms_req": dn.detach().cpu(), "norms_real": real.norm(dim=1).detach().cpu(),
                            "rho": float((real.norm(dim=1) / dn.clamp_min(1e-8)).mean()),
                            "kappa": float(torch.nn.functional.cosine_similarity(real, delta, dim=1).mean())}
            h[0, self.pos, :] = new
            return H._pack(o, h)
        return f
