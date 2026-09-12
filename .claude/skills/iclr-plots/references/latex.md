# LaTeX snippets matching the figure sizes

The ICLR style: `\textwidth 5.5in`, single column, `\parindent 0pt`, figures centered, caption below in `\footnotesize` (9pt), lower case except first word and proper nouns.

## One figure (built with width="wide")

```latex
\begin{figure}[t]
\begin{center}
\includegraphics[width=0.8\linewidth]{figures/fig_accuracy.pdf}
\end{center}
\caption{Validation accuracy over training. Shaded bands are $\pm 1$ std over 5 seeds.}
\label{fig:accuracy}
\end{figure}
```

Built with width="full": use `width=\linewidth`.

## Side-by-side subfigures (built with width="half" each)

```latex
\usepackage{subcaption}  % preamble

\begin{figure}[t]
\centering
\begin{subfigure}[b]{0.48\linewidth}
  \includegraphics[width=\linewidth]{figures/fig_left.pdf}
  \caption{Probe AUROC by layer.}
  \label{fig:left}
\end{subfigure}\hfill
\begin{subfigure}[b]{0.48\linewidth}
  \includegraphics[width=\linewidth]{figures/fig_right.pdf}
  \caption{Steering effect size.}
  \label{fig:right}
\end{subfigure}
\caption{Readout versus control. (a) ...; (b) ...}
\label{fig:readout-control}
\end{figure}
```

## Multi-panel single PDF (built with nrows/ncols and label_panels)

Prefer this over subfigures when panels share a legend: one PDF, one `\includegraphics[width=\linewidth]`, and the caption walks through (a), (b), (c).

## Placement

`[t]` for most figures, `[h]` only if the text really needs it adjacent, `[p]` for a full-page appendix figure. The template says leave a line before the caption and one after; the `figure` environment does that already.
