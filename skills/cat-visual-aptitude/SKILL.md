---
name: cat-visual-aptitude
description: >-
  Solves aptitude and competitive-exam questions supplied as screenshots, photos or images — bar/line/pie/stacked/dual-axis charts, caselet tables, Data Interpretation (DI), Logical Reasoning (LR/DILR) sets, Venn and set min-max problems, geometry figures, Data Sufficiency, and Quantitative Aptitude of the kind found in CAT, XAT, SNAP, NMAT, GMAT, GRE and campus placement tests. Also verifies a user's own attempted answer and diagnoses which mistake produced it, and explains the exam-speed method on request. Use this skill whenever the user pastes an image of an exam question, or mentions DI, LR, DILR, aptitude, CAT, XAT, GMAT, percentile, quant, mocks or sectionals, or asks "solve this", "which option" or "check my answer" alongside a chart, graph, table, figure or multiple-choice options — even if they do not name the skill. Optimizes for correctness first and speed second by transcribing the visual into data, validating it, and computing in Python instead of mental arithmetic.
---

# CAT / Aptitude Visual Question Solver

Wrong answers on these questions come from two places, almost never from weak
reasoning:

1. **Misreading the image** — a bar read as 42 when it is 45, a legend mapped to
   the wrong series, a percentage read as an absolute, a second y-axis ignored.
2. **Mental arithmetic on read-off numbers** — compounding, ratios and weighted
   averages done in-head drift.

Slow answers come from a third place: open-ended exploration. Do not search the
web, do not scan the workspace, do not write plan artifacts. This is a
self-contained task. Target: one image read, one script run, one answer.

## Step 0 — Classify the request, then the question

**Request mode** (from the user's words; default `solve`):

| Mode | Trigger | What changes |
| --- | --- | --- |
| `solve` | default | Full pipeline below. |
| `verify` | "is (C) right?", "check my answer", "I got 37.5" | Solve independently **first**, without letting their answer anchor you. Then compare, and if it differs, name the specific mistake that produces their value — see `references/traps.md` § Distractor forensics. |
| `teach` | "explain", "how do I do this in 60s", "method" | Still compute exactly, but lead with the exam-speed route: approximation, elimination, what to eyeball vs calculate. Give the time budget. |
| `set` | 4–6 questions on one data set | Transcribe once, one script, answer all in a single response, led by an answer table. |

**Question type** — pick the playbook. The full routing table, covering every
chart and set type and the traps unique to each, is in
[references/question-types.md](./references/question-types.md). Read that file
whenever the question is anything other than a plain bar/line/pie/table DI.
Common escalations: dual-axis combo chart, cumulative/ogive, index-to-100 series,
a chart of growth *rates*, radar/scatter/bubble/waterfall, route-network and
games-and-tournaments sets, Data Sufficiency, geometry figures ("not to scale"),
cryptarithms, binary logic, para-jumbles and other VARC.

## Mandatory pipeline

Never skip a phase. Never merge Phase 1 into Phase 3.

### Phase 1 — Transcribe (do NOT solve yet)

Look at the image and write out, in the response, a compact transcription:

- **Question stem, verbatim.** Including any "which of the following", "at
  most", "cannot be determined", "approximately" wording. These words decide the
  answer.
- **All answer options, verbatim**, with their labels. Note whether it is MCQ or
  TITA (type-in-the-answer, no options).
- **A data table.** One row per data point. Columns: category / series / value.
- **Units and base.** Absolute, percentages, indices, ₹ crore, '000s? Is there a
  "Total = X" note anywhere? Pie charts are usually shares of an unstated total —
  record that fact explicitly.
- **Confidence marks.** Tag every value `exact` (printed data label, or a mark
  landing on a gridline) or `approx` (estimated between gridlines).

Value-source priority — always take the highest available:

1. A printed data label on the mark.
2. A value derivable from a stated total or the other series (e.g. the last stack
   segment = total − others). Derive rather than read.
3. A mark landing exactly on a gridline.
4. Pixel calibration — `scripts/overlay.py` then `scripts/calibrate.py`. Use this
   instead of eyeballing whenever an unlabelled mark sits between gridlines and
   the options are close together.
5. Eyeballed interpolation — last resort, always tagged `approx`.

Rules while transcribing:

- **Read the axis before reading any mark.** Minimum, maximum, gridline interval,
  and whether there are two y-axes. A y-axis starting at 20 instead of 0 is the
  single most common trap in bar-chart DI.
- Map legend colours/patterns to series names before reading a stacked or grouped
  chart, and state the mapping in the transcription.
- If any label, tick or legend entry is unreadable, crop and upscale it with
  `scripts/crop.py` rather than guessing.
- If the image holds more than one question sharing one data set, transcribe the
  data **once** and reuse it. Do not re-read the image per sub-question.
- Indian digit grouping: `12,34,567` is 1234567, not 1234.567. `1 lakh` = 1e5,
  `1 crore` = 1e7. See [references/visual-reading.md](./references/visual-reading.md)
  for this plus multi-image, rotated-photo and clipped-option handling.
- If a solution or answer key is visible in the screenshot, **ignore it until
  Phase 4.** It is often the key for a different question. Solve independently,
  then reconcile.

### Phase 2 — Validate the transcription

Run these checks before computing. They catch most misreads for free.
`scripts/di.py` implements each as a one-line call.

| Chart type | Check |
| --- | --- |
| Pie chart | Sector percentages sum to 100 (±1 rounding); degrees sum to 360 |
| Stacked bar | Segments sum to the printed segment total or the axis height |
| Table with totals | Row totals and column totals reconcile to the grand total |
| Stated total or average | Recomputed mean/total matches the stated one |
| Index series | The base year reads exactly 100 |
| Cumulative / ogive | Series is monotonically non-decreasing; final point = total |
| Two pies / two periods | Each pie sums to 100 *separately*; the totals differ |
| Any chart | Every legend series appears in the table, and vice versa |

If a check fails by more than rounding, **go back to the image and re-read the
offending values.** Do not proceed with an inconsistent table, and do not
"adjust" a number to make it fit.

If the question is a missing-data DI puzzle (blank cells to be deduced from
constraints), treat blanks as unknowns and solve them in Phase 3 with equations
or enumeration — never by eyeballing a proportion.

### Phase 3 — Compute in Python, always

Write one short script and run it. Never do the arithmetic in prose, even when it
looks trivial — a two-step percentage change done in-head is exactly where these
answers go wrong.

The script must:

- Hardcode the transcribed table as a literal at the top, so the numbers are
  auditable.
- Print intermediate values, not just the final one.
- Print the final value in the unit and rounding the options use.
- Batch every sub-question of a set into this one script.

Helpers (run with `--help`; do not read the source unless a run fails):

- `scripts/di.py` — percentage change vs percentage point, CAGR, successive
  change, weighted mean, index conversion, the Phase-2 validators,
  `match_option()` and `sensitivity()`.
- `scripts/lr.py` — exhaustive enumeration templates for LR sets, plus
  `evaluate_options()`, which classifies each option as always / sometimes /
  never true across all surviving arrangements.
- `scripts/sets.py` — Venn region solver and feasible min/max for "exactly two",
  "at least one", "maximum possible" set questions.

For **LR sets** (seating, ranking, scheduling, distribution, tournaments, Venn,
grid/matching, routes): **do not reason your way through the constraints.**
Enumerate with `itertools` and filter by each constraint as a *named* predicate,
then read off what survives. This is faster and near-immune to the error mode
where one constraint gets silently dropped. `scripts/lr.py` covers permutation,
circular (fix one entity to kill rotational symmetry), assignment, subset, grid,
partial-order and cryptarithm shapes; `references/lr-shapes.md` maps set types to
recipes. If the space exceeds a few million, filter on the most restrictive
constraint first.

For **quant with clean options**, back-solving (substitute each option into the
original condition) is often the fastest reliable route. Do it in the script.

**Sensitivity, not point estimates.** If any value is tagged `approx` and the
options are within ~10% of each other, do not answer from the single best read.
Call `di.sensitivity()` with a plausible low/high for each `approx` value; it
reports whether every corner lands on the same option. If they do, the answer is
robust — say so and drop the caveat. If they do not, go back and pixel-calibrate
the offending mark. This replaces hedging with a decision.

### Phase 4 — Match against the options

- If the computed value equals an option, answer it.
- If it is *near* an option but not equal, **do not snap to the nearest.** A
  near-miss means an assumption is wrong. Re-check, in this order: the percentage
  base (of what?), percentage vs percentage-point, absolute vs share, the axis
  origin, a second y-axis, and whether the question asked about a subset of
  years/categories rather than all of them.
- **Distractor forensics.** Options are built so each wrong one is the product of
  a specific mistake. If your value matches no option, work out which mistake
  yields each option — that usually names your own error immediately. Catalogue in
  `references/traps.md`.
- **Second route.** Before finalising, re-derive the answer by one independent
  route (a different formula, a bound, or a magnitude check). Two routes agreeing
  is the cheapest correctness insurance there is.
- If TITA, give the answer in the exact format asked (integer, two decimals, no
  units unless requested).
- Answer "cannot be determined" only if that is an option or the stem invites it.
  Otherwise the transcription is incomplete — re-read the image.

## Trap checklist

Scan before finalising. Each has produced a wrong answer on a real paper.
Per-type traps live in `references/traps.md`; these are the universal ones.

- Y-axis not starting at zero; log scale; broken axis; **two y-axes at different
  scales**.
- Percentage **point** difference vs percentage **change**.
- Percentage-change base = the earlier value, not the later one, not the total.
- Pie shares are meaningless as absolutes unless a total is given; two pies with
  different totals cannot have their percentages compared directly.
- "Growth rate" vs "growth" vs "CAGR" — CAGR is `(end/start)**(1/n) - 1` where
  `n` is the number of *intervals*, not of data points.
- A chart **of growth rates** is not a chart of values: a falling but still
  positive growth rate means the value is still rising.
- Averages of percentages ≠ percentage of the totals; weight by the bases.
- Ratios asked "A : B" — check the order.
- "Approximately" means the options are far apart and heavy exact computation is
  wasted effort; "exactly" or "must be" means the opposite.
- LR wording: "only if", "unless", "at least one", "exactly two", "no two
  adjacent" — translate each into a predicate, and count the constraints in the
  script comments to confirm none was dropped.
- Units switching mid-question (lakh vs crore, kg vs tonne, % vs fraction, ₹ vs
  ₹'000).
- Geometry figures are **not to scale** — never measure pixels on them. Use only
  marked lengths, tick marks, right-angle squares and stated congruences.

## Output format

Keep it tight. The user wants the answer, then the ability to audit it.

```
**Answer: (C) 37.5%**

Read from chart (y-axis 0–200, interval 20; all values printed labels):
| Year | Revenue | Cost |
|------|---------|------|
| 2019 | 120     | 80   |
...
Checks: column totals match stated 480 ✓ · legend 2/2 mapped ✓

Working:
1. Profit 2021 = 180 − 120 = 60
2. Profit 2019 = 120 − 80  = 40
3. Change = 20/40 = 50%              [3 lines max]

Second route: 60/40 = 1.5× → +50% ✓
Confidence: high
```

- Add a **Flagged** line only when a value is `approx` *and* `sensitivity()` shows
  the option can change; then say which alternative read gives which option.
- `Confidence: high` when every value is `exact` and two routes agree; `medium`
  when a robust `approx` is involved; `low` when the read is genuinely ambiguous —
  and then say what would resolve it (a clearer crop of which region).
- For a `set`, lead with a one-line answer table, then one compact working block
  per sub-question.

## Speed rules

- No web search. No workspace scanning. No implementation-plan artifact.
- One image pass in Phase 1. Re-read only when a validation check fails, a label
  is illegible, or sensitivity is inconclusive.
- One script for the whole set.
- Do not restate the question back to the user before solving.
- Budget: ≈90 s of tool work for a single DI question, ≈3 min for a 4-question
  set, ≈4 min for an LR set. On a `verify` where you agree with the user, say so
  in one line and stop.
