# Reading the image accurately

Everything here exists to replace guessing with measurement.

## 1. Axis calibration before anything else

Write down, in this order, before reading a single mark:

1. y-axis minimum and maximum, and the gridline interval.
2. Whether the axis starts at zero. If not, **every visual comparison of bar
   heights is invalid** — only the numeric values are.
3. Whether the scale is linear or logarithmic. On a log axis, equal pixel steps
   are equal *ratios*. A log axis is recognisable from tick labels like
   1, 10, 100 or 1, 2, 5, 10.
4. Whether there is a **second y-axis** on the right. If yes, write which series
   belongs to which axis and never mix them.
5. The x-axis: are categories evenly spaced but unevenly valued (e.g. years
   2010, 2011, 2015)? Then slopes are not comparable.

## 2. Pixel calibration — the precise way to read an unlabelled mark

Use when a mark sits between gridlines and the options are close together. Two
steps, both scripted:

```
python scripts/overlay.py question.png --step 50 --out grid.png
```

This writes a copy with a labelled pixel grid drawn over it. Look at `grid.png`
and read off pixel y-coordinates: two reference gridlines whose data values you
know, and the top of each mark you need.

```
python scripts/calibrate.py --p1 480 0 --p2 120 200 --read 245 310 --read 198 400
```

`--p1 PIXEL VALUE` and `--p2 PIXEL VALUE` are the two references; each `--read`
takes the pixel y of a mark (and an optional label). The script maps pixels to
values linearly, or logarithmically with `--log`. It also prints the value of one
pixel, so you can state your own read precision honestly — if one pixel is worth
0.8 units, a ±3 px reading uncertainty is ±2.4 units, and that is the interval to
feed into `di.sensitivity()`.

Never pixel-calibrate a geometry figure. Those are not to scale.

## 3. When something is illegible

```
python scripts/crop.py question.png --info                  # get the dimensions
python scripts/crop.py question.png --box 0.0 0.7 0.45 1.0  # fractions of w/h
python scripts/crop.py question.png --grid 3x3 --cell 1,3   # bottom-left cell
python scripts/crop.py question.png --box 0 300 400 500 --scale 4 --enhance
```

`--enhance` sharpens and raises contrast, which usually rescues small grey axis
labels and compression-blurred legends. Crop tightly: a 4× upscale of a small
region beats a 2× upscale of half the page.

Escalation when a value is still unreadable:

1. Can it be **derived** instead (total minus the others, a stated average times
   n, a ratio given elsewhere)? Derive it — a derived value is `exact`.
2. Can it be **bounded** well enough that the option is determined regardless?
   Then say so and answer.
3. Otherwise state precisely what is illegible and ask for a tighter screenshot
   of that region. Do not answer on a guess and do not silently pick a value.

## 4. Number formats that bite

| Seen | Means |
| --- | --- |
| `12,34,567` (Indian grouping) | 1 234 567 — **not** 1234.567 |
| `1,234,567` (Western grouping) | 1 234 567 |
| `1,5` in a European-styled paper | 1.5 |
| `1 lakh` / `1 L` | 1e5 |
| `1 crore` / `1 Cr` | 1e7 |
| `₹ in '000s` / `₹ '000` | multiply the plotted number by 1 000 |
| `₹ in crore` | the axis number is already crore — do not scale it again |
| `bn`, `mn`, `k` | 1e9, 1e6, 1e3 |
| `%` on a bar in an otherwise absolute chart | a share, plotted on a secondary axis |
| `p.a.` | per annum — check whether the period in the question is a year |
| A trailing `*` or `#` on a label | there is a footnote; find and read it |

If the axis caption and the data labels disagree about scale, the **data label
wins** and the caption is usually a leftover from another chart.

## 5. Awkward inputs

- **Photograph of a screen or page** — expect keystone distortion and glare.
  Values on gridlines are still safe; pixel calibration is not, because the axis
  is not parallel to the image edge. Prefer printed labels; if there are none,
  say the photo is unsuitable for a precise read and ask for a screenshot.
- **Rotated or sideways image** — rotate before reading:
  `python scripts/crop.py img.png --rotate 90`.
- **Dark mode / inverted screenshot** — colours in a legend may be hard to match.
  Match by *position in the legend* against *order in the stack* on a bar where
  one segment is labelled, and say you did.
- **Two screenshots, data in one and questions in the other** — transcribe both,
  then state which image each piece came from.
- **A whole page with several unrelated questions** — answer each, numbered, and
  keep each block short. Ask before doing more than about eight in one response.
- **Handwritten question** — transcribe the stem verbatim and flag any character
  you are unsure of (1 vs 7, 0 vs 6, x vs ×).
- **Low resolution below roughly 600 px wide** — say so up front; misread digits
  are the dominant risk and a better capture is cheaper than a wrong answer.

## 6. Colour and legend mapping

1. Read the legend order top-to-bottom (or left-to-right).
2. Find one bar/segment with a printed value, and check that value against the
   series you *think* it is, using another part of the chart (a total, another
   series). If it fails, your mapping is reversed.
3. In a stacked bar, the legend order usually matches bottom-to-top, but not
   always — verify once, then reuse.
4. Note the mapping in the transcription so the user can audit it. Most
   "the reasoning was right but the answer was wrong" cases are a swapped legend.
