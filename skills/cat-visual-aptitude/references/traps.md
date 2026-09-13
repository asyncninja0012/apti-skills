# Trap catalogue and distractor forensics

## Distractor forensics

Option sets on real papers are not random. Each wrong option is the output of one
specific mistake. When your computed value matches no option, do not re-read the
chart at random — compute what each option *would* require, and the mismatch names
your error.

Standard distractor generators, in rough order of frequency:

| Distractor equals | Mistake it encodes |
| --- | --- |
| Your value with the base swapped (new instead of old) | percentage change computed on the wrong base |
| Your value × or ÷ by the total | share confused with absolute |
| The difference of two percentages | percentage points reported as percentage change |
| Your value with the sign flipped | direction of change reversed, or "decrease by" read as "decrease to" |
| Your value ÷ n where n is the count | simple average used where a weighted average is needed |
| Your value using n data points instead of n−1 intervals | CAGR / average-growth period count |
| Your value for the adjacent year/category | off-by-one on the x-axis |
| Your value from the other series | legend swapped |
| The reciprocal of your ratio | "A : B" read as "B : A" |
| Your value × 100 or ÷ 100 | fraction vs percentage |
| Your value using the whole range where the stem said a subset | "between 2018 and 2021" read as all years |
| A suspiciously round number like 50%, 100%, 25% | the trap answer for someone who eyeballed |
| The answer to the *previous* sub-question | the set was solved out of order |

Two corollaries worth stating:

- If your value matches an option **and** that option is also the output of a
  known mistake, check which reading the stem actually asks for. Matching an
  option is not proof.
- If two options are reciprocals, or differ by exactly 100×, the question is
  testing that specific confusion. Read the stem again, slowly.

## Universal traps

- **Axis origin not zero.** Visual comparison is then meaningless; only numbers
  count.
- **Log axis.** Equal pixel steps are equal ratios, not equal differences.
- **Broken axis** (a zigzag in the axis line). Bar heights are not proportional.
- **Second y-axis.** The commonest silent error in combo charts.
- **Percentage point vs percentage change.** 20% → 25% is +5 percentage points
  and +25%.
- **"Increased by 20%" vs "increased to 120%".**
- **Successive percentage changes do not add.** +10% then −10% is −1%, not 0.
- **Percentage change of a percentage.** Be explicit about which is the base.
- **Reverse percentage.** If a value after a 20% rise is 120, the original is 100,
  not 96.
- **Averages of percentages** are not the percentage of the totals unless the
  bases are equal.
- **Average of ratios ≠ ratio of averages.** Common in "average profit margin"
  questions.
- **"Approximately"** means the options are far apart; approximate freely.
  **"Exactly", "must", "always"** mean the opposite.
- **"At most / at least / no more than"** change an equality into an inequality —
  and often turn the question into an optimisation.
- **"Cannot be determined"** is a real answer, but only when a genuine degree of
  freedom remains. If you reach it, first re-check that you used every given.
- **Units switching mid-question** (lakh↔crore, kg↔tonne, ₹↔₹'000, %↔fraction).
- **Fiscal years.** FY21 may mean Apr 2020–Mar 2021. If the stem mixes FY and
  calendar labels, say which reading you used.
- **Inclusive counting.** "From 2010 to 2015" is 6 years but 5 intervals. Growth
  uses intervals; counting uses years.

## Chart-specific traps

**Pie**
- Shares only; absolutes need a stated total.
- Two pies for two years: percentages are not comparable unless the totals are
  given, and a *rising share* can coexist with a *falling absolute*.
- A degree value is a share: 90° = 25%.
- Exploded slices distort perceived size; only the label matters.

**Stacked bar**
- A segment's value is its *height*, not the y-value of its top edge.
- In a 100% stacked chart, a shrinking segment can still be growing in absolute
  terms.

**Line**
- Points, not a continuum: a value between two years is not readable.
- Steepness is not comparable if the x-axis spacing is uneven or the y-axis is
  log.
- A chart of **growth rates**: the level keeps rising while the rate falls, as
  long as the rate stays positive. Levels drop only where the rate is negative.
  The *lowest* level is at the end of the last negative stretch, not at the lowest
  point of the rate curve.

**Cumulative / ogive**
- Period value = difference of consecutive cumulative points.
- "Less than" and "more than" ogives read in opposite directions; the median is
  where they cross.

**Histogram**
- Unequal bin widths mean frequency is the *area*, so the y-axis is density.
- Bin boundaries: is 20 in "10–20" or "20–30"? Look for "10–20" vs "10 ≤ x < 20".

**Index series**
- Base = 100 by definition; an index says nothing about absolute size.
- Two indices with different base years cannot be compared directly.
- Index growth from 100 to 120 is +20%; from 120 to 150 is +25%, not +30.

**Scatter / bubble**
- Bubble *area* encodes the third variable — double the diameter is 4× the value.
- Count the points before answering "how many lie above…"; overlapping points
  hide.

**Table**
- Row and column totals are given as a *check*, so use them.
- A "Total" row may exclude an "Others" row, or include it — reconcile.
- Ranks are not values: a rank-2 item can be far below rank 1.

## LR-specific traps

- "**Unless** A, B" means `B or A` — i.e. `not A implies B`.
- "A **only if** B" means `A implies B`, not `B implies A`.
- "**Either** A **or** B" is usually exclusive in Indian papers, but check whether
  the set later allows both; if ambiguous, enumerate under both readings and see
  which yields a unique solution — the intended reading is nearly always the one
  that does.
- "**At least one**" vs "**exactly one**" vs "**only**".
- "**No two** X are adjacent" applies to *every* pair, not just the named ones.
- "Immediately left of" is direction-sensitive; in a circle it also depends on
  whether people face the centre. Facing outward reverses left and right.
- In a circle, `abs(pos[a] - pos[b]) == 1` is wrong at the wrap-around — use a
  modular distance.
- "Between A and B" usually means strictly between, and does not fix which of A
  and B is on the left.
- Distinctness: are two entities allowed the same value? Assume yes unless the
  set says "distinct" — and then say which reading you used.
- A "must be true" answer needs *every* surviving arrangement to satisfy it. With
  more than one solution, never answer from the first one found.
- Zero solutions means you mis-encoded a constraint, not that the set is broken.

## Geometry traps

- Figures are not to scale; only marked information counts.
- A point drawn inside may be required outside (and vice versa) — enumerate the
  configurations.
- "Diameter" vs "radius" in a stated length.
- Angles in the same segment, cyclic quadrilaterals, and the alternate-segment
  theorem rely on a configuration you must verify, not assume.
- An answer must satisfy the triangle inequality and an angle sum; check it.
- Area ratios of similar figures scale as the *square* of the length ratio,
  volumes as the cube.

## Data Sufficiency traps

- A yes/no question is sufficient even when the answer is "no".
- Statement (2) must be judged with (1) fully forgotten.
- One confirming example never proves sufficiency; two conflicting examples do
  prove insufficiency.
- `x² = 9` leaves two roots; `x² > 9` leaves two intervals.
- Integer, positive and non-zero constraints are frequently the whole question.
- A statement that only restates the stem is insufficient by itself.
