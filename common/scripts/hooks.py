"""Intervention primitives on block outputs.

All hooks act on the output of decoder block l (the residual stream after block l), batch size 1,
in float32 then cast back to the model dtype. Each returns the realized write so the requested vs
realized perturbation can be checked (rho = |delta_real|/|delta_req|, kappa = cos).
"""
import torch


class Both:
    def __init__(self, *c):
        self.c = [x for x in c if x is not None]

    def __enter__(self):
        for x in self.c:
            x.__enter__()
        return self

    def __exit__(self, *a):
        for x in reversed(self.c):
            x.__exit__(*a)


def _out(o):
    return o if torch.is_tensor(o) else o[0]


def _pack(o, h):
    return h if torch.is_tensor(o) else (h,) + tuple(o[1:])


class SpanWriter:
    """Sustained replacement: block outputs at `positions` <- source[l] ([P, d]) for every layer in `layers`."""
    def __init__(self, blocks, layers, positions, source):
        self.blocks, self.layers = blocks, sorted(layers)
        self.pos = torch.as_tensor(positions, dtype=torch.long)
        self.src, self._h = source, []

    def _mk(self, l):
        def f(m, i, o):
            if len(self.pos) == 0:
                return None  # empty patch: hook installed, nothing written
            h = _out(o).clone()
            h[0, self.pos, :] = self.src[l].to(h.dtype).to(h.device)
            return _pack(o, h)
        return f

    def __enter__(self):
        self._h = [self.blocks[l].register_forward_hook(self._mk(l)) for l in self.layers]
        return self

    def __exit__(self, *a):
        [x.remove() for x in self._h]


class StateMove:
    """Natural-coordinate move at one layer: h <- h + alpha_t * u_disp, alpha_t = level - u_meas . h (per position).

    With u_meas = u_disp = g_hat this is the H1.4 move; with u_disp = u_i it is the equal-dose
    control of H1.5 (same signed alpha_t along another unit direction). `alpha_fixed` overrides the
    clean-derived scalar with a precomputed per-position vector (convention: use the same clean-derived
    scalar in swap and no-swap conditions).
    """
    def __init__(self, blocks, layer, positions, u_meas, u_disp, level=None, scale=1.0, alpha_fixed=None):
        self.blocks, self.layer = blocks, layer
        self.pos = torch.as_tensor(positions, dtype=torch.long)
        self.um, self.ud, self.level, self.scale = u_meas, u_disp, level, float(scale)
        self.alpha_fixed, self.realized, self._h = alpha_fixed, None, []

    def _f(self, m, i, o):
        h = _out(o).clone()
        hp = h[0, self.pos, :].float()
        ud = self.ud.to(h.device)
        if self.alpha_fixed is not None:
            a = self.alpha_fixed.to(h.device)
        else:
            a = self.level - hp @ self.um.to(h.device)
        delta = self.scale * a[:, None] * ud[None, :]
        new = (hp + delta).to(h.dtype)
        self.realized = {"alpha": a.detach().cpu(), "delta_req": delta.detach().cpu(),
                         "delta_real": (new.float() - hp).detach().cpu()}
        h[0, self.pos, :] = new
        return _pack(o, h)

    def __enter__(self):
        self._h = [self.blocks[self.layer].register_forward_hook(self._f)]
        return self

    def __exit__(self, *a):
        [x.remove() for x in self._h]


class AddVector:
    """Additive steering h <- h +/- beta * r at one layer and positions (raw vector r, not unit)."""
    def __init__(self, blocks, layer, positions, vec):
        self.blocks, self.layer = blocks, layer
        self.pos = torch.as_tensor(positions, dtype=torch.long)
        self.vec, self.realized, self._h = vec, None, []

    def _f(self, m, i, o):
        h = _out(o).clone()
        hp = h[0, self.pos, :].float()
        new = (hp + self.vec.to(h.device)[None, :]).to(h.dtype)
        self.realized = {"delta_req": self.vec.detach().cpu()[None, :].expand(len(self.pos), -1),
                         "delta_real": (new.float() - hp).detach().cpu()}
        h[0, self.pos, :] = new
        return _pack(o, h)

    def __enter__(self):
        self._h = [self.blocks[self.layer].register_forward_hook(self._f)]
        return self

    def __exit__(self, *a):
        [x.remove() for x in self._h]


class EraseToReference:
    """H2.4: h <- h + q (q.mu0 - q.h) at layers/positions, unit q per layer, reference level mu0 per layer."""
    def __init__(self, blocks, layers, positions, q, ref_level):
        self.blocks, self.layers = blocks, sorted(layers)
        self.pos = torch.as_tensor(positions, dtype=torch.long)
        self.q, self.ref, self._h = q, ref_level, []

    def _mk(self, l):
        def f(m, i, o):
            h = _out(o).clone(); hp = h[0, self.pos, :].float(); q = self.q[l].to(h.device)
            hp = hp + (self.ref[l] - hp @ q)[:, None] * q[None, :]
            h[0, self.pos, :] = hp.to(h.dtype)
            return _pack(o, h)
        return f

    def __enter__(self):
        self._h = [self.blocks[l].register_forward_hook(self._mk(l)) for l in self.layers]
        return self

    def __exit__(self, *a):
        [x.remove() for x in self._h]


def realized_write_stats(hook):
    """rho and kappa of a StateMove/AddVector realized write (cell-level)."""
    r = hook.realized
    dreq, dreal = r["delta_req"].flatten(), r["delta_real"].flatten()
    nreq = float(dreq.norm()); nreal = float(dreal.norm())
    rho = nreal / (nreq + 1e-12)
    kappa = float((dreq @ dreal) / (nreq * nreal + 1e-12)) if nreq > 0 and nreal > 0 else float("nan")
    return {"rho": rho, "kappa": kappa, "req_norm": nreq, "real_norm": nreal}


def make_run(model, lm, all_layers):
    """Forward with block-output recording. Returns (acts dict layer->[1,T,d] bf16, logits)."""
    from jlens.hooks import ActivationRecorder

    @torch.no_grad()
    def run(ids_list, ctx=None):
        ids = torch.tensor([ids_list], device=lm.input_device)
        with (ctx if ctx is not None else Both()):
            with ActivationRecorder(lm.layers, at=all_layers) as r:
                logits = model(ids, attention_mask=None).logits
                acts = {i: r.activations[i].detach() for i in all_layers}
        return acts, logits
    return run


class CoordSwap:
    """Paper-style coordinate swap on block outputs: V=[v_s v_t] (unit columns), c = V^+ h, h <- h + V(sigma(c) - c),
    sigma swaps the two coordinates. Applied at `positions` for every layer in `layers` (directions per layer)."""
    def __init__(self, blocks, layers, positions, dirs):
        """dirs: {layer: (v_s [d], v_t [d])} float tensors on device."""
        self.blocks, self.layers = blocks, sorted(layers)
        self.pos = torch.as_tensor(positions, dtype=torch.long)
        self.dirs, self._h, self.realized = dirs, [], {}

    def _mk(self, l):
        def f(m, i, o):
            h = _out(o).clone()
            hp = h[0, self.pos, :].float()
            vs, vt = self.dirs[l]
            V = torch.stack([vs, vt], 1).to(hp.device)                       # [d, 2]
            pinv = torch.linalg.pinv(V)                                       # [2, d]
            c = hp @ pinv.T                                                   # [P, 2]
            delta = (c[:, [1, 0]] - c) @ V.T                                  # [P, d]
            new = (hp + delta).to(h.dtype)
            self.realized[l] = float(delta.norm(dim=1).mean())
            h[0, self.pos, :] = new
            return _pack(o, h)
        return f

    def __enter__(self):
        self._h = [self.blocks[l].register_forward_hook(self._mk(l)) for l in self.layers]
        return self

    def __exit__(self, *a):
        [x.remove() for x in self._h]


class AttnReadBlock:
    """Route restriction at full-attention blocks: queries at `q_positions` cannot attend keys in `k_positions`.
    Adds finfo.min to the additive attention mask (building the causal mask if the layer received None) and
    captures the maximum post-softmax weight from q_positions to k_positions per layer (the leak)."""
    def __init__(self, blocks, layers, q_positions, k_positions):
        self.blocks, self.layers = blocks, sorted(layers)
        self.q = torch.as_tensor(q_positions, dtype=torch.long); self.k = torch.as_tensor(k_positions, dtype=torch.long)
        self._h, self.leak = [], {}

    def _pre(self, l):
        def f(m, args, kwargs):
            hs = kwargs.get("hidden_states", args[0] if args else None)
            T = hs.shape[1]; dt = hs.dtype; dev = hs.device
            am = kwargs.get("attention_mask", None)
            if am is None:
                am = torch.full((T, T), torch.finfo(dt).min, dtype=dt, device=dev).triu(1)[None, None]
            else:
                am = am.clone()
            am[:, :, self.q.to(dev)[:, None], self.k.to(dev)[None, :]] = torch.finfo(dt).min
            kwargs["attention_mask"] = am
            return args, kwargs
        return f

    def _post(self, l):
        def f(m, i, o):
            w = o[1]
            if w is not None:
                self.leak[l] = float(w[0][:, self.q.to(w.device)][:, :, self.k.to(w.device)].max())
        return f

    def __enter__(self):
        for l in self.layers:
            att = self.blocks[l].self_attn
            self._h.append(att.register_forward_pre_hook(self._pre(l), with_kwargs=True))
            self._h.append(att.register_forward_hook(self._post(l)))
        return self

    def __exit__(self, *a):
        [x.remove() for x in self._h]


class CoordClamp:
    """Clamp the coordinates of h in a 2-plane V=[v0 v1] to reference values, leaving the complement untouched:
    h <- h + V(c_ref - V^+ h). With c_ref taken from a clean run this pins the plane to its clean value."""
    def __init__(self, blocks, layers, positions, dirs, cref):
        """dirs: {layer: (v0 [d], v1 [d])}; cref: {layer: [P, 2] clean coordinates}."""
        self.blocks, self.layers = blocks, sorted(layers)
        self.pos = torch.as_tensor(positions, dtype=torch.long)
        self.dirs, self.cref, self._h, self.realized = dirs, cref, [], {}

    def _mk(self, l):
        def f(m, i, o):
            h = _out(o).clone()
            hp = h[0, self.pos, :].float()
            v0, v1 = self.dirs[l]
            V = torch.stack([v0, v1], 1).to(hp.device)
            c = hp @ torch.linalg.pinv(V).T
            delta = (self.cref[l].to(hp.device) - c) @ V.T
            self.realized[l] = float(delta.norm(dim=1).mean())
            h[0, self.pos, :] = (hp + delta).to(h.dtype)
            return _pack(o, h)
        return f

    def __enter__(self):
        self._h = [self.blocks[l].register_forward_hook(self._mk(l)) for l in self.layers]
        return self

    def __exit__(self, *a):
        [x.remove() for x in self._h]


def plane_coords(acts, positions, layers, dirs):
    """Coordinates of block outputs in the 2-plane per layer -> {layer: [P, 2] float32 cpu}."""
    out = {}
    for l in layers:
        hp = acts[int(l)][0, positions, :].float()
        v0, v1 = dirs[l]
        V = torch.stack([v0, v1], 1).to(hp.device)
        out[l] = (hp @ torch.linalg.pinv(V).T).detach()
    return out


class CoordClampMatched(CoordClamp):
    """CoordClamp that (a) optionally rescales each position's delta to a target norm (norm-matched control: the perp-plane
    clamp receives exactly the naming-plane clamp's per-position write size) and (b) records the realized post-cast write
    (rho, kappa, per-position norms), repairing the mislabelled `realized` of CoordClamp/CoordSwap (query_local_workspace
    Amendment 3)."""
    def __init__(self, blocks, layers, positions, dirs, cref, target=None):
        super().__init__(blocks, layers, positions, dirs, cref)
        self.target, self.post = target, {}

    def _mk(self, l):
        def f(m, i, o):
            h = _out(o).clone()
            hp = h[0, self.pos, :].float()
            v0, v1 = self.dirs[l]
            V = torch.stack([v0, v1], 1).to(hp.device)
            c = hp @ torch.linalg.pinv(V).T
            delta = (self.cref[l].to(hp.device) - c) @ V.T
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
            return _pack(o, h)
        return f
