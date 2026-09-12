# Palettes

## Categorical (default cycle)

Vivid but colorblind-safe (derived from Okabe-Ito, reordered so the first four are maximally distinct and the first is a strong blue, which reads as "primary"):

| Idx | Hex | Name | Typical role |
|---|---|---|---|
| 0 | #0072B2 | blue | Ours / primary |
| 1 | #D55E00 | vermilion | main baseline / highlight |
| 2 | #009E73 | green | second baseline |
| 3 | #CC79A7 | pink | third |
| 4 | #E69F00 | orange | |
| 5 | #56B4E9 | sky blue | |
| 6 | #7A4FBF | purple | |
| 7 | #333333 | near-black | "no intervention" / control |

Extended set (idx 8-12) is from tab10 and is only for >8 groups; prefer restructuring the figure.

Greys: `NEUTRAL = #7F7F7F` for secondary annotations, `BASELINE = #8A8A8A` dashed for chance/random lines.

## Sequential (ordered, non-negative)

- `viridis` (default): perceptually uniform, prints in greyscale, white-background safe.
- `magma` ("warm"): when viridis clashes with a categorical series in the same figure.
- `cividis` ("cool"): strongest colorblind safety.
- `Blues` ("single"): single-hue; use when the ramp has few levels (3-4) and you want it to look calm.

For *lines* that are ordered (layers, sizes), `palette("ordinal", n)` samples viridis from 0.78 down to 0, so the smallest value is green (still visible on white, never yellow) and the largest is dark purple. Dark = larger value by convention; state the mapping in the legend.

## Diverging (signed, zero is meaningful)

- `RdBu_r` (default): red positive, blue negative, white at zero. Norm is `TwoSlopeNorm(0, -lim, +lim)` with symmetric limits so white means exactly zero.
- `coolwarm`: softer, for slides.
- `PRGn`: if red/blue already mean something else in the figure.

Never use a diverging map on non-negative data; the midpoint would lie.

## Checks

- Greyscale: `matplotlib.colors.rgb_to_hsv` luminance should differ by >0.15 between adjacent categorical colors in the order used. The default cycle passes.
- Deuteranopia: avoid pairing #009E73 (green) with #D55E00 (vermilion) as the *only* distinguishing feature; add markers.
