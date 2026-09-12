"""Cluster-level inference."""
import numpy as np
from scipy import stats as st


def cluster_t(values, conf=0.95):
    """Mean and Student-t interval over clusters; sign count; per-cluster values."""
    v = np.asarray(values, float)
    n = len(v)
    m = float(v.mean())
    if n < 2:
        return {"mean": m, "ci": [float("nan"), float("nan")], "n": n, "signs": int((v > 0).sum()), "per_cluster": v.tolist()}
    h = st.t.ppf(0.5 + conf / 2, n - 1) * float(v.std(ddof=1)) / np.sqrt(n)
    return {"mean": m, "ci": [m - h, m + h], "n": n, "signs_pos": int((v > 0).sum()), "signs_neg": int((v < 0).sum()),
            "sd": float(v.std(ddof=1)), "per_cluster": v.tolist()}


def equivalence(values, eps, conf=0.90):
    """Two one-sided tests: the (conf) interval lies entirely within [-eps, +eps]."""
    r = cluster_t(values, conf)
    r["eps"] = eps
    r["equivalent"] = bool(r["ci"][0] > -eps and r["ci"][1] < eps)
    return r


def ratio_of_means(num, den, B=2000, seed=20260907):
    """Ratio of cluster means with a paired cluster bootstrap interval."""
    num, den = np.asarray(num, float), np.asarray(den, float)
    n = len(num)
    if n == 0 or not (np.isfinite(num).all() and np.isfinite(den).all()):
        return {"ratio": float("nan"), "ci": [float("nan"), float("nan")], "numerator_mean": float("nan"), "denominator_mean": float("nan"), "n": n, "B": B}
    rng = np.random.default_rng(seed)
    point = float(num.mean() / den.mean())
    bs = []
    for _ in range(B):
        idx = rng.integers(0, n, n)
        d = den[idx].mean()
        bs.append(num[idx].mean() / d if d != 0 else np.nan)
    bs = np.array(bs); bs = bs[np.isfinite(bs)]
    return {"ratio": point, "ci": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))],
            "numerator_mean": float(num.mean()), "denominator_mean": float(den.mean()), "n": n, "B": B}


def holm(pvals):
    """Holm step-down adjusted p-values."""
    p = np.asarray(pvals, float); m = len(p); order = np.argsort(p)
    adj = np.empty(m)
    running = 0.0
    for rank, i in enumerate(order):
        val = min(1.0, (m - rank) * p[i]); running = max(running, val); adj[i] = running
    return adj.tolist()


def paired_p(values):
    v = np.asarray(values, float)
    return float(st.ttest_1samp(v, 0.0).pvalue) if len(v) > 1 else float("nan")
