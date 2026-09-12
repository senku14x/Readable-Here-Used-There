r"""
iclrplot: helpers for ICLR-style figures with matplotlib.

Usage
-----
    import sys; sys.path.insert(0, "<skill>/scripts")
    import iclrplot as ip
    ip.setup()                                  # apply iclr.mplstyle
    fig, ax = ip.figure(width="wide")           # 0.8\linewidth, one panel
    ip.line_ci(ax, x, mean, lo, hi, label="ours", color=ip.palette("categorical", 3)[0])
    ip.finish(fig, "fig_main")                  # writes fig_main.pdf + fig_main.png

Design goals
- Figure width equals the physical width it will occupy in the PDF, so fonts are
  never rescaled by \\includegraphics.
- Palette choice is driven by the data: categories -> vivid categorical,
  ordered magnitudes -> sequential, signed quantities -> diverging.
- Layout is driven by panel count: shared axes, panel labels, one legend.
"""

from __future__ import annotations

import os
from typing import Iterable, Sequence

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
STYLE = os.path.join(_HERE, "..", "assets", "iclr.mplstyle")

# ICLR 2019-2027 conference style: \textwidth 5.5in, single column.
TEXTWIDTH_IN = 5.5
WIDTHS = {
    "full": TEXTWIDTH_IN,          # \includegraphics[width=\linewidth]
    "wide": 0.8 * TEXTWIDTH_IN,    # template default, 0.8\linewidth
    "half": 0.48 * TEXTWIDTH_IN,   # two side-by-side subfigures
    "third": 0.31 * TEXTWIDTH_IN,  # three side-by-side subfigures
}
GOLDEN = 0.618

# ---------------------------------------------------------------------------
# Palettes (see references/palettes.md for rationale)
# ---------------------------------------------------------------------------

CATEGORICAL = [  # vivid, colorblind-safe, ordered so first 4 are maximally distinct
    "#0072B2", "#D55E00", "#009E73", "#CC79A7",
    "#E69F00", "#56B4E9", "#7A4FBF", "#333333",
]
CATEGORICAL_EXTENDED = CATEGORICAL + [
    "#8C564B", "#17BECF", "#BCBD22", "#E377C2", "#7F7F7F",
]
SEQUENTIAL_CMAPS = {"default": "viridis", "warm": "magma", "cool": "cividis", "single": "Blues"}
DIVERGING_CMAPS = {"default": "RdBu_r", "warm-cool": "coolwarm", "green-purple": "PRGn"}
NEUTRAL = "#7F7F7F"
BASELINE = "#8A8A8A"   # for "baseline" / "random" reference lines
HIGHLIGHT = "#D55E00"  # for "ours" when it must pop against several baselines


def palette(kind: str = "categorical", n: int | None = None, variant: str = "default",
            lo: float = 0.15, hi: float = 0.9) -> list:
    """Return a list of n colors.

    kind: "categorical" | "sequential" | "diverging" | "ordinal"
      - categorical: distinct hues for unrelated groups (methods, datasets)
      - sequential : one ordered ramp for monotone quantities (layer, model size, epoch)
      - diverging  : signed ramp centered on zero (deltas, correlations)
      - ordinal    : like sequential but samples a hue-varying cmap so lines stay
                     distinguishable in a legend (good for 3-8 ordered series)
    """
    if kind == "categorical":
        n = n or len(CATEGORICAL)
        src = CATEGORICAL if n <= len(CATEGORICAL) else CATEGORICAL_EXTENDED
        return [src[i % len(src)] for i in range(n)]
    n = n or 6
    if kind == "sequential":
        cmap = plt.get_cmap(SEQUENTIAL_CMAPS.get(variant, variant))
        return [cmap(v) for v in np.linspace(lo, hi, n)]
    if kind == "ordinal":
        # Largest value -> darkest color. Range stops at 0.78 so the lightest
        # series is still green rather than a yellow that disappears on white.
        cmap = plt.get_cmap("viridis" if variant == "default" else variant)
        return [cmap(v) for v in np.linspace(0.78, 0.0, n)]
    if kind == "diverging":
        cmap = plt.get_cmap(DIVERGING_CMAPS.get(variant, variant))
        return [cmap(v) for v in np.linspace(0.05, 0.95, n)]
    raise ValueError(f"unknown palette kind {kind!r}")


def cmap_for(values, signed: bool | None = None, variant: str = "default"):
    """Pick a colormap and norm from the data.

    Signed data (min<0<max) -> diverging map centered on 0.
    Non-negative or all-negative -> sequential map.
    Returns (cmap, norm).
    """
    a = np.asarray(values, dtype=float)
    a = a[np.isfinite(a)]
    vmin, vmax = float(a.min()), float(a.max())
    if signed is None:
        signed = vmin < 0 < vmax
    if signed:
        lim = max(abs(vmin), abs(vmax))
        return plt.get_cmap(DIVERGING_CMAPS.get(variant, variant)), mpl.colors.TwoSlopeNorm(0, -lim, lim)
    return plt.get_cmap(SEQUENTIAL_CMAPS.get(variant, variant)), mpl.colors.Normalize(vmin, vmax)


def series_palette(labels: Sequence) -> list:
    """Infer a palette from the series labels themselves.

    Numeric or numeric-with-suffix labels ("1", "7B", "layer 12", "0.1") are
    treated as ordered -> ordinal ramp. Anything else -> categorical.
    """
    def _num(s):
        import re
        m = re.search(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", str(s))
        return float(m.group()) if m else None
    nums = [_num(l) for l in labels]
    if len(labels) >= 3 and all(v is not None for v in nums) and len(set(nums)) == len(nums):
        order = np.argsort(nums)
        ramp = palette("ordinal", len(labels))
        out = [None] * len(labels)
        for rank, idx in enumerate(order):
            out[idx] = ramp[rank]
        return out
    return palette("categorical", len(labels))


# ---------------------------------------------------------------------------
# Figure creation and finishing
# ---------------------------------------------------------------------------

def setup():
    """Apply the ICLR style. Call once at the top of a plotting script."""
    plt.style.use(STYLE)


def figure(width: str | float = "wide", aspect: float = GOLDEN, nrows: int = 1, ncols: int = 1,
           sharex=False, sharey=False, height: float | None = None, **kw):
    """Create a figure sized for the ICLR column.

    width : "full" | "wide" | "half" | "third" | inches
    aspect: height/width of a single panel (ignored if height given)
    """
    w = WIDTHS.get(width, width) if isinstance(width, str) else float(width)
    if height is None:
        panel_w = w / ncols
        height = panel_w * aspect * nrows
        height = min(height, 0.8 * w) if nrows == 1 else height
    fig, axes = plt.subplots(nrows, ncols, figsize=(w, height), sharex=sharex, sharey=sharey,
                             constrained_layout=True, **kw)
    return fig, axes


def finish(fig, path: str, formats: Iterable[str] = ("pdf", "png"), dpi: int = 300):
    """Save in vector + raster form and return the paths."""
    root, ext = os.path.splitext(path)
    if ext:
        formats = (ext.lstrip("."),)
    out = []
    for f in formats:
        p = f"{root}.{f}"
        fig.savefig(p, dpi=dpi)
        out.append(p)
    return out


def label_panels(axes, labels: Sequence[str] | None = None, titles: Sequence[str] | None = None,
                 x: float = -0.12, y: float = 1.02):
    """Put bold (a), (b), ... on each panel.

    With titles: renders "(a) Title" as a left-aligned panel title, which is the
    compact form used in most ML papers (one line, no stacked label + title).
    Without titles: places the label just outside the top-left corner.
    """
    axes = np.atleast_1d(axes).ravel()
    labels = labels or [f"({chr(97 + i)})" for i in range(len(axes))]
    for i, (ax, lab) in enumerate(zip(axes, labels)):
        bold = r"$\mathbf{" + lab + "}$"
        if titles is not None:
            ax.set_title(f"{bold} {titles[i]}", loc="left", fontsize=8.5, pad=4)
        else:
            ax.text(x, y, bold, transform=ax.transAxes, fontsize=9, va="bottom", ha="left")


def legend_outside(fig_or_ax, where: str = "top", ncol: int | None = None, title: str | None = None, **kw):
    """Single shared legend outside the plot area. where: "top" | "right" | "bottom".

    Use for any multi-panel figure, and for grouped bars where an inside legend
    would collide with the tallest bars.
    """
    fig = fig_or_ax if isinstance(fig_or_ax, mpl.figure.Figure) else fig_or_ax.figure
    handles, labels = [], []
    for ax in fig.axes:
        h, l = ax.get_legend_handles_labels()
        for hh, ll in zip(h, l):
            if ll not in labels:
                handles.append(hh); labels.append(ll)
    ncol = ncol or (len(labels) if where in ("top", "bottom") else 1)
    loc = {"top": ("lower center", (0.5, 1.0)), "bottom": ("upper center", (0.5, 0.0)),
           "right": ("center left", (1.0, 0.5))}[where]
    return fig.legend(handles, labels, loc=loc[0], bbox_to_anchor=loc[1], ncol=ncol, title=title, **kw)


def despine(ax, left: bool = False, bottom: bool = False):
    for side, hide in (("top", True), ("right", True), ("left", left), ("bottom", bottom)):
        ax.spines[side].set_visible(not hide)


# ---------------------------------------------------------------------------
# Plot recipes
# ---------------------------------------------------------------------------

def line_ci(ax, x, mean, lo=None, hi=None, label=None, color=None, marker="o", alpha_band=0.18, **kw):
    """Mean line with optional shaded confidence band."""
    (ln,) = ax.plot(x, mean, label=label, color=color, marker=marker, **kw)
    if lo is not None and hi is not None:
        ax.fill_between(x, lo, hi, color=ln.get_color(), alpha=alpha_band, linewidth=0)
    return ln


def bars_grouped(ax, categories: Sequence[str], series: dict, errors: dict | None = None,
                 colors: Sequence | None = None, width: float = 0.8, annotate: bool = False,
                 fmt: str = "{:.2f}"):
    """Grouped bar chart. series = {series_name: [value per category]}."""
    names = list(series)
    colors = colors or series_palette(names)
    n, m = len(categories), len(names)
    bw = width / m
    x = np.arange(n)
    for i, name in enumerate(names):
        vals = np.asarray(series[name], dtype=float)
        err = None if errors is None else errors.get(name)
        pos = x - width / 2 + bw * (i + 0.5)
        bars = ax.bar(pos, vals, bw, label=name, color=colors[i], yerr=err,
                      error_kw=dict(elinewidth=0.6, capsize=1.5, ecolor="0.3"))
        if annotate:
            for b, v in zip(bars, vals):
                ax.annotate(fmt.format(v), (b.get_x() + b.get_width() / 2, b.get_height()),
                            xytext=(0, 1.5), textcoords="offset points", ha="center", va="bottom",
                            fontsize=6.5)
    ax.set_xticks(x, categories)
    ax.grid(axis="x", visible=False)
    return ax


def heatmap(ax, data, xlabels=None, ylabels=None, signed: bool | None = None, variant: str = "default",
            annotate: bool = False, fmt: str = "{:.2f}", cbar: bool = True, cbar_label: str | None = None,
            square: bool = False):
    """Heatmap with a data-aware colormap (diverging if signed, sequential otherwise)."""
    data = np.asarray(data, dtype=float)
    cmap, norm = cmap_for(data, signed=signed, variant=variant)
    im = ax.imshow(data, cmap=cmap, norm=norm, aspect="equal" if square else "auto")
    ax.grid(False)
    for s in ax.spines.values():
        s.set_visible(False)
    if xlabels is not None:
        ax.set_xticks(range(data.shape[1]), xlabels)
    if ylabels is not None:
        ax.set_yticks(range(data.shape[0]), ylabels)
    ax.tick_params(length=0)
    if annotate:
        thr = (norm.vmin + norm.vmax) / 2 if not isinstance(norm, mpl.colors.TwoSlopeNorm) else None
        for i in range(data.shape[0]):
            for j in range(data.shape[1]):
                v = data[i, j]
                rgba = cmap(norm(v))
                lum = 0.299 * rgba[0] + 0.587 * rgba[1] + 0.114 * rgba[2]
                ax.text(j, i, fmt.format(v), ha="center", va="center", fontsize=6.5,
                        color="white" if lum < 0.5 else "black")
    if cbar:
        cb = ax.figure.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
        cb.outline.set_linewidth(0.4)
        cb.ax.tick_params(length=2, width=0.4)
        if cbar_label:
            cb.set_label(cbar_label)
    return im


def reference_line(ax, y=None, x=None, label=None, color=BASELINE, ls="--", lw=0.9):
    """Dashed grey reference (chance level, baseline, threshold)."""
    if y is not None:
        return ax.axhline(y, color=color, ls=ls, lw=lw, label=label, zorder=0.5)
    return ax.axvline(x, color=color, ls=ls, lw=lw, label=label, zorder=0.5)


def scatter(ax, x, y, c=None, label=None, signed: bool | None = None, s: float = 10, **kw):
    """Scatter; if c is numeric, colormap is chosen from the data."""
    if c is not None and np.issubdtype(np.asarray(c).dtype, np.number):
        cmap, norm = cmap_for(c, signed=signed)
        return ax.scatter(x, y, c=c, cmap=cmap, norm=norm, s=s, label=label, edgecolor="white",
                          linewidth=0.3, **kw)
    return ax.scatter(x, y, color=c, s=s, label=label, edgecolor="white", linewidth=0.3, **kw)


def markers(n: int) -> list:
    """Distinct marker shapes, for redundancy with color (print-safe)."""
    base = ["o", "s", "^", "D", "v", "P", "X", "*", "<", ">"]
    return [base[i % len(base)] for i in range(n)]


def linestyles(n: int) -> list:
    base = ["-", "--", "-.", ":", (0, (5, 1)), (0, (3, 1, 1, 1))]
    return [base[i % len(base)] for i in range(n)]
