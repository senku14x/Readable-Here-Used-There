# Seaborn and plotly

## Seaborn

Seaborn is matplotlib underneath, so the mplstyle applies. Two rules:

1. Call `ip.setup()` after importing seaborn and never call `sns.set_theme()` / `sns.set_style()` (they overwrite rcParams with a grey grid and DejaVu Sans).
2. Pass palettes explicitly so seaborn's defaults don't win:

```python
import seaborn as sns
import iclrplot as ip
ip.setup()
fig, ax = ip.figure(width="wide")
sns.lineplot(data=df, x="step", y="acc", hue="method", errorbar=("ci", 95),
             palette=ip.palette("categorical", df.method.nunique()), ax=ax)
sns.despine(ax=ax)
ip.finish(fig, "fig_seaborn")
```

For ordered hues: `palette=dict(zip(levels, ip.palette("ordinal", len(levels))))`.
For heatmaps: `sns.heatmap(M, cmap=cmap, norm=norm, ...)` where `cmap, norm = ip.cmap_for(M)`.
`sns.catplot` / `relplot` create their own figure; pass `height=` and `aspect=` so that `height*aspect*ncols` equals the target width in inches (4.4 or 5.5).

## Plotly

No rcParams. Use this template and export via kaleido to PDF at the target width.

```python
import plotly.graph_objects as go, plotly.io as pio
pio.templates["iclr"] = go.layout.Template(layout=dict(
    font=dict(family="Times New Roman, TeX Gyre Termes, serif", size=9, color="#222"),
    paper_bgcolor="white", plot_bgcolor="white",
    colorway=["#0072B2","#D55E00","#009E73","#CC79A7","#E69F00","#56B4E9","#7A4FBF","#333333"],
    xaxis=dict(showline=True, linecolor="#404040", linewidth=0.6, gridcolor="#E0E0E0",
               ticks="outside", tickcolor="#404040", zeroline=False, mirror=False),
    yaxis=dict(showline=True, linecolor="#404040", linewidth=0.6, gridcolor="#E0E0E0",
               ticks="outside", tickcolor="#404040", zeroline=False, mirror=False),
    legend=dict(bgcolor="rgba(0,0,0,0)", borderwidth=0),
    margin=dict(l=40, r=10, t=10, b=35),
))
pio.templates.default = "iclr"
fig = go.Figure(...)
fig.write_image("fig.pdf", width=int(4.4*96), height=int(4.4*0.618*96), scale=1)
```

Sequential: `colorscale="Viridis"`. Diverging: `colorscale="RdBu"`, `zmid=0`. Plotly's interactive figures are for exploration; the paper figure should still be a static PDF.
