---
name: iclr-plots
description: Make publication-quality figures in the ICLR conference style (Times font, 5.5in single column, white background, centered, 9pt captions) with matplotlib, seaborn, or plotly. Colors, colormaps, and layout are chosen from what is being plotted - categorical vs ordered vs signed data, single vs multi-panel. Use this skill whenever the user asks for a plot, figure, chart, or visualization for a paper, submission, workshop, arXiv preprint, or slides derived from one, and whenever they mention ICLR, NeurIPS, ICML, "paper figure", "publication quality", "camera-ready", or want an existing plot to "look like a paper figure". Trigger even if they just paste numbers or a results dict and say "plot this" in a research context.
---

# ICLR-style plots

Produce figures that drop straight into an `iclr20xx_conference` LaTeX document without rescaling, look like they belong on the page, and encode the data honestly and legibly.

## Quick start (matplotlib)

```python
import sys; sys.path.insert(0, "<skill-path>/scripts")
import iclrplot as ip

ip.setup()                                   # loads assets/iclr.mplstyle
fig, ax = ip.figure(width="wide")            # 0.8\linewidth = 4.4in, golden aspect
cols = ip.palette("categorical", 3)
ip.line_ci(ax, steps, mean, lo, hi, label="Ours", color=cols[0])
ip.reference_line(ax, y=0.5, label="Chance")
ax.set(xlabel="Training steps", ylabel="Accuracy")
ax.legend()
ip.finish(fig, "fig_accuracy")               # fig_accuracy.pdf + .png
```

Always save PDF for LaTeX plus PNG for the chat preview, and show the PNG to the user. Then give the `\begin{figure}` snippet (see `references/latex.md`).

## The three decisions the skill makes for you

### 1. Size from placement

The ICLR style sets `\textwidth` to 5.5in, single column. Build the figure at the exact width it will be displayed at, so 9pt text stays 9pt on the page:

| Use in LaTeX | `ip.figure(width=...)` | Inches |
|---|---|---|
| `width=\linewidth` | `"full"` | 5.5 |
| `width=0.8\linewidth` (template default) | `"wide"` | 4.4 |
| two subfigures side by side | `"half"` | 2.64 |
| three side by side | `"third"` | 1.7 |

Default to `"wide"` for one panel, `"full"` for 2+ panels. Never build at 10in and let `\includegraphics` shrink it; that is how 4pt tick labels happen.

### 2. Color from data type

Ask what the series or cells *are*, not how many there are:

| Data | Palette | Helper |
|---|---|---|
| Unrelated groups (methods, datasets, ablations) | vivid categorical, colorblind-safe | `ip.palette("categorical", n)` |
| Ordered magnitudes (layer index, model size, epoch, temperature) | one ramp, dark = large | `ip.palette("ordinal", n)` or `series_palette(labels)` |
| Non-negative intensities (attention, loss, counts) | sequential colormap | `ip.heatmap(...)` picks viridis |
| Signed quantities (deltas, correlations, log-ratios) | diverging, white at zero | `ip.heatmap(...)` / `ip.cmap_for(...)` picks RdBu_r centered at 0 |
| The method being proposed vs baselines | "Ours" gets the strongest hue (`ip.HIGHLIGHT` or first categorical), baselines get the rest; chance/random lines are dashed grey (`ip.reference_line`) | |

`ip.series_palette(labels)` infers this: labels like `["1B", "7B", "70B"]` or `["layer 4", "layer 12"]` get an ordinal ramp, `["SFT", "DPO", "Ours"]` get categorical. Use it when the series names are in hand.

Add a second channel when a figure might be read in greyscale: `ip.markers(n)` and `ip.linestyles(n)` give distinct shapes/dashes to pair with colors.

Do not use rainbow/jet, red-green pairs, or more than ~8 categorical colors. If there are more than 8 groups, the figure is asking to be split or aggregated.

### 3. Layout from panel count

- **One panel**: `width="wide"`, legend inside (`ax.legend()`), or `loc="best"`. Golden-ratio aspect unless the data wants square (heatmaps, scatter with equal axes).
- **2-4 panels in a row**: `width="full"`, `ncols=n`, `sharey=True` when the y-quantity is the same. One shared legend above via `ip.legend_outside(fig, "top")`. Label panels with `ip.label_panels(axes, titles=[...])`, which renders **(a)** Title on one line, and refer to (a), (b) in the caption.
- **Grid (2x2, 2x3)**: `width="full"`, `nrows`, `ncols`, share both axes where meaningful, single legend, panel labels.
- **Many small multiples (>6)**: consider whether a heatmap or a single overlaid plot says the same thing. If not, use `aspect=1` panels and drop inner tick labels.

Grouped bars: legend goes above the axes (`ip.legend_outside(fig, "top", title=...)`) so it never sits on the tallest bar.

Heatmaps: `square=True`, annotate cells only when the grid is at most ~10x10, put the colorbar label on the colorbar not in the caption.

## Rules of the house

- White background, no figure border, top/right spines off, light grey gridlines behind the data. The mplstyle handles all of this; do not override with `sns.set_theme()` or `plt.style.use("ggplot")`.
- Axis labels with units where relevant ("Wall-clock time (s)", "KL to base (nats)"). Sentence case, no trailing period.
- No title inside the figure. The caption is the title in ICLR papers.
- Error bars or bands whenever multiple seeds exist; say what they are in the caption (std, 95% CI, min-max) and how many seeds.
- Log scale when the x range spans more than ~2 orders of magnitude (model size, learning rate, steps).
- Legend labels are what a reader would say aloud, not variable names: "Random baseline", not `rand_bl`.
- Tick counts: 4-6 per axis. Use `ax.yaxis.set_major_locator(MaxNLocator(5))` if matplotlib overcrowds.
- Text in the PDF must be real text (the style sets `pdf.fonttype: 42`), so reviewers can search and zoom.

## Other libraries

The style file is matplotlib rcParams, so seaborn inherits it if you call `ip.setup()` *after* any seaborn import and pass palettes explicitly. Plotly needs its own template. See `references/other-libs.md`.

## Files

- `assets/iclr.mplstyle` - rcParams matching the ICLR .sty (fonts, sizes, spines, cycle).
- `scripts/iclrplot.py` - sizing, palettes, `line_ci`, `bars_grouped`, `heatmap`, `scatter`, `legend_outside`, `label_panels`, `finish`.
- `references/palettes.md` - hex values, when to use each ramp, colorblind notes.
- `references/latex.md` - `\begin{figure}` and `subfigure` snippets that match the sizes above.
- `references/other-libs.md` - seaborn and plotly equivalents.

## Before handing the figure over

Look at the PNG. Check: nothing clipped, legend does not cover data, the proposed method is visually first, the y-axis starts at a defensible place (0 for bars; not necessarily for lines), fonts are not bigger than the paper body text. If the user gave real results, do not invent smoothing, extra seeds, or error bars they did not provide.
