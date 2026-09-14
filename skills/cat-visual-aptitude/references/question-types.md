# Question-type routing table

Identify the type from the visual, then follow its row. Anything not listed falls
back to the generic Phase 1–4 pipeline in `SKILL.md`.

**First check § H.** If the image contains only shapes and no numbers, it is a
non-verbal figure puzzle: skip every row below, skip the pipeline, and use the
fast path — [nonverbal.md](./nonverbal.md). No script is written for those.

## A. Data Interpretation — chart forms

| Visual | Read it as | Type-specific danger | Extra Phase-2 check |
| --- | --- | --- | --- |
| **Simple bar / column** | one value per category | axis origin ≠ 0; bar width is meaningless | — |
| **Grouped (clustered) bar** | series × category matrix | legend order ≠ bar order left-to-right; confirm by one labelled bar | every group has the same number of bars |
| **Stacked bar (absolute)** | segments + implied total | reading a segment top as its value instead of its height | segments sum to the total label |
| **100% stacked bar** | shares only | segments are shares of *that bar's* total, so cross-bar segment comparison needs the totals | each bar sums to 100 |
| **Line chart** | value per period | between-point interpolation is not data; a line does not imply continuity | endpoints match any stated start/end |
| **Dual-axis combo (bar + line)** | two series, two scales | reading the line against the bar axis. **This is the highest-frequency silent error.** Note both axis ranges explicitly in the transcription | pick one labelled point on each series and confirm it against its own axis |
| **Pie chart** | shares of one total | absolutes impossible without the total; two pies with different totals are not comparable percentage-wise | shares sum to 100, degrees to 360 |
| **Doughnut / nested pies** | inner = outer breakdown | inner ring is usually the *parent* total, not another series | inner sum = 100 and each outer group sums to its parent slice |
| **Area chart** | cumulative bands | in a stacked area the top line is the total, not the last series | band heights, not top values |
| **Cumulative / ogive / "less than" curve** | running total | reading a cumulative point as a period value. Period value = difference of consecutive points | monotone non-decreasing; last point = grand total |
| **Histogram** | frequency per bin | bins may be unequal width — then the *area*, not the height, is the frequency | frequencies sum to n |
| **Scatter plot** | (x, y) pairs | correlation ≠ causation and ≠ a fitted value; count points before answering "how many" | point count matches any stated n |
| **Bubble chart** | (x, y, size) | bubble *area* encodes the third variable, not its radius — a bubble twice as wide is 4× | — |
| **Radar / spider** | value per spoke | each spoke can have its own scale; enclosed area is not a meaningful total | one labelled spoke per series |
| **Waterfall** | signed deltas | a bar's height is a change; its position encodes the running total | start + Σ deltas = end |
| **Pareto** | bars + cumulative % line | the line is on the right axis and is cumulative | line ends at 100% |
| **Index series (base = 100)** | relative values | an index of 120 vs 110 is not "10% more" unless both share a base; absolutes need the base-year value | base period reads exactly 100 |
| **Chart of growth rates** | first differences, not levels | a falling positive rate still means levels are rising; levels fall only when the rate is negative. To get levels, compound from a stated base | — |
| **Box plot** | five-number summary | the box holds 50% of data; whiskers are not min/max if outliers are drawn separately | median inside the box |
| **Map / geographic shading** | binned categories | the legend bins are ranges, not values | — |
| **Gantt / timeline** | intervals | inclusive vs exclusive endpoints; overlap ≠ sum | — |
| **Network / route map** | weighted graph | "shortest" may mean cost, time or hops — check the stem; edges may be directed | every stated edge appears once |
| **Caselet (prose, no chart)** | build the table yourself | the table is implied; write it before solving, and mark which cells are given vs derived | derived cells reconcile |
| **Table with blanks** | constraint system | eyeballing a proportion. Solve as equations or enumerate | all row/col totals reconcile once filled |

## B. Logical Reasoning / DILR set shapes

Full recipes in [lr-shapes.md](./lr-shapes.md). Type → tool:

| Set shape | Enumeration strategy |
| --- | --- |
| Linear seating / ranking / order | `permutations` over positions |
| Circular seating | fix one entity at seat 1 (kills rotational symmetry); note facing in/out reverses left/right |
| Two-row / facing-each-other | positions 1..n and n+1..2n, with an explicit "opposite" map |
| Floors & flats, grid/matrix | `product` over cells, or `permutations` per column |
| Attribute matching (person × city × drink) | `product` of `permutations`, one per attribute |
| Selection / committee | `combinations` over the pick size |
| Scheduling with days/slots | assignment, plus a capacity predicate |
| Partial order ("A finished above B") | enumerate permutations, filter by each pair |
| Tournament / points table | enumerate match results in `product({W,L,D})`, score them |
| Venn / set cardinality, min-max | `scripts/sets.py` |
| Route / network / flow | build the graph, use `itertools` paths or Dijkstra by hand |
| Cryptarithm / alphametic | `permutations` of digits over distinct letters, leading digit ≠ 0 |
| Binary logic (truth-tellers and liars) | `product([True, False], repeat=n)` over who is truthful |
| Distribution with quantities | `product` over integer splits summing to the total |
| Quant-in-LR (e.g. "maximum possible score") | enumerate, then `max()` — never argue it |

After enumeration, always answer sub-questions with
`lr.evaluate_options(solutions, options)`:

- exactly one surviving solution → read the answer off directly;
- several → "must be true" holds in **all**, "could be true" in **at least one**,
  "cannot be true" in **none**. Never answer a "must be true" from one solution.
- zero surviving solutions → a constraint is mis-encoded. Re-read the set; do not
  loosen a constraint to make solutions appear.

## C. Quantitative Aptitude

Formula sheet: [formulas.md](./formulas.md). Routing:

| Stem smells like | Do this |
| --- | --- |
| Clean numeric options, messy algebra | back-solve: substitute each option into the original condition |
| "Find the number of integer solutions/ordered pairs" | enumerate over a proven bound; state the bound |
| Max/min of an expression | enumerate a grid, or AM–GM / derivative — verify with enumeration |
| Time–speed–distance, work, mixtures | set up with a unitary/LCM base so the arithmetic stays integral |
| Simple vs compound interest | never approximate; compute both if the stem is ambiguous, and say which reading you used |
| Permutations/combinations | count in Python (`itertools`) on a small analogue to validate the formula before scaling |
| Probability | enumerate the sample space when it is under ~1e6 |
| Progressions, functions, logs, inequalities | symbolic if `sympy` is importable, else careful numeric plus a second route |
| Number theory (remainders, factors, digits) | brute-force over the modulus or a bounded range; patterns are verified, not assumed |
| Geometry with a figure | see § D |
| Mensuration | write the formula, then substitute in the script — never in prose |

## D. Geometry and figure-based questions

This section is for *measured* geometry — labelled lengths, angles, areas. A
figure made only of unlabelled shapes with no measurement asked is § H, not this.

The figure is a *schematic*. **"Figures are not to scale" applies even when it is
not printed.**

1. Transcribe only what is *marked*: labelled lengths, tick marks (equal
   segments), arcs (equal angles), right-angle squares, parallel arrows,
   collinearity, tangency, centre labels.
2. Do **not** measure pixels, do **not** infer that an angle "looks" right, and do
   **not** assume a triangle is isosceles because it is drawn that way.
3. Re-draw as a coordinate system when it helps: place one vertex at the origin
   and one side along the x-axis, then compute with coordinates in the script.
4. If the answer depends on a configuration the figure does not pin down (point
   inside vs outside, which of two intersection points), enumerate both cases and
   check which is consistent with the stem.
5. Sanity-bound every answer: triangle inequality, an angle sum, an area smaller
   than a bounding rectangle.

Coordinate-geometry plots, number lines and inequality shadings *are* to scale —
read them like charts, but confirm whether endpoints are open (hollow) or closed
(filled) circles.

## E. Data Sufficiency (GMAT / XAT style)

Answer options are fixed:
A — (1) alone sufficient, (2) not · B — (2) alone, (1) not · C — both together
only · D — each alone · E — neither, even together. **Confirm the option wording
in the image; some papers permute it.**

Procedure, in this order, and never skip a step:

1. Restate what exactly must be determined — a unique value, or just a yes/no.
2. Evaluate statement (1) **alone**, deliberately forgetting (2).
3. Evaluate statement (2) **alone**, deliberately forgetting (1) — this is where
   carry-over from (1) causes most errors.
4. Only if both fail alone, evaluate them together.
5. Sufficiency means *a unique answer*, not a *nice* answer, and not that you can
   find one example. To prove **insufficient**, exhibit two cases satisfying the
   statement that give different answers. Do that in the script.
6. Traps: a yes/no question is sufficient even when the answer is "no"; a
   statement that merely restates the stem adds nothing; integer/positivity
   constraints are easy to forget; `x² = 9` gives two roots unless positivity is
   stated.

## F. Verbal (VARC) screenshots

No Python. Quote textual evidence instead of computing.

| Type | Method |
| --- | --- |
| Reading comprehension | Locate the supporting sentence and quote it with its line/paragraph position. Reject options that are true-but-not-stated, overly absolute, or partly right. |
| Para-jumble | Find the opener (no dangling reference), then chain by pronouns, connectives and repeated nouns. State the chain, e.g. 4–2–1–3, and justify each link by a specific linking word. |
| Para-summary | Prefer the option preserving the author's main claim *and* its qualifiers; reject ones that add detail, flip emphasis or drop the conclusion. |
| Odd sentence out | Build the theme from the majority, then remove the one that does not fit that chain. |
| Critical reasoning / assumption | Name premise and conclusion explicitly, then test each option by negation: if negating it destroys the argument, it is the assumption. |
| Fill in the blanks / vocab | Use collocation and register, not just meaning. |

## G. Non-question images

- **No question visible** (only a chart, or only options): say exactly what is
  missing and ask for the stem — do not invent it.
- **Options clipped at the image edge**: solve, state the value, and say which
  option letter it matches *if* that option is legible; otherwise report the value
  and note the clipping.
- **Multi-image input**: assume all images belong to one set. State which image
  supplied which part of the transcription.
- **Answer key visible**: solve independently first (see `SKILL.md` Phase 1). If
  you disagree with a visible key, say so plainly and show why — printed keys are
  wrong often enough to matter, and are frequently misaligned by one question.

## H. Non-verbal / abstract reasoning (FIG route — no Python)

Shapes only, no numbers. Full playbook: [nonverbal.md](./nonverbal.md).

| Type | Answer by |
| --- | --- |
| **Figure classification** ("which set does this figure belong to?", "group the figures") | Find the one binary attribute separating the sets. Start with: are the two black shapes in a cell identical? the two white ones? Then nesting-chain direction, fill counts, shape counts, side counts. For line-art cells, count strokes on a `--panels --sheet` crop — the target is drawn to mimic the *wrong* set's silhouette. |
| **Figure series** ("what comes next") | Track rotation, movement, count, fill and size as independent series; extend each; combine. |
| **Figure analogy** (A : B :: C : ?) | Name the single A→B transformation, apply verbatim to C. Beware reflection-vs-rotation options. |
| **Odd one out** | The attribute shared by all but one — usually four are rotations of each other and one is their mirror. |
| **Mirror / water image** | Mirror flips left–right and reverses character order; water flips up–down and does not. Eliminate using a symmetric character. |
| **Paper folding / punching** | Unfold one fold at a time, mirroring; check hole *count* first (n × 2^k). |
| **Cubes, dice, nets** | Opposite faces never co-appear; on a net, opposite = separated by one face. Painted-cube counts are arithmetic → NUM. |
| **Embedded / hidden figure** | Match angles and proportions, not overall silhouette. |
| **Counting figures** (triangles, rectangles) | Count by size class; grid rectangles = C(m+1,2)·C(n+1,2) — arithmetic, so script that one. |
| **Matrix / 3×3 pattern** | Rows, then columns, then diagonals; test superposition and the common-elements-cancel rule. |

Do **not** write a script that hardcodes shape names and prints them back. It
checks nothing the description did not already fix, and it is the main source of
slow answers on this route. `overlay.py` and `calibrate.py` never apply — there
is no axis.

`crop.py --panels --sheet` *is* expected here: it auto-splits every bordered
cell and tiles them, upscaled, into one labelled image. Use it before describing whenever the rule could be a
count — strokes, sides, vertices, dots, intersections — which is most line-art
sets. Miscounting strokes on an unzoomed figure is the main source of *wrong*
answers on this route.
