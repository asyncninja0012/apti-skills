# Non-verbal / abstract reasoning — FIG route

No solver script. No pixel calibration. These questions are decided by naming
what is in each figure precisely, then testing a short list of known rules. The
whole cost is in *describing accurately*; the rule then falls out in seconds.

The one tool that earns its place is `scripts/crop.py --panels --sheet`, which enlarges
every cell in a single call — see § 0. Reach for it before describing whenever a
count could decide the answer.

## 0. Describe before you theorise

One line per figure, fixed vocabulary, no adjectives:

- **Shape names**: circle, triangle, square, rectangle, pentagon, hexagon,
  heptagon, octagon, star (say 5- or 6-pointed if it matters), arrow, line, dot,
  cross, arc.
- **Fill**: `black` (solid) or `white` (outline only). Nothing else.
- **Nesting**: `⊃` means "contains". `black star ⊃ white pentagon`.
- **Independent elements** of one cell separated by `|`.
- **Orientation** only when the puzzle has rotation in it: add `@90°` or
  `points-up`.

```
A1: white square ⊃ black circle | black hexagon
A5: white circle ⊃ black triangle | black triangle ⊃ white star
```

Count the elements per cell as you write. A miscount here is the only way these
questions go wrong — every wrong answer traces back to a shape named wrong, a
fill read backwards, or a nesting missed, never to faulty logic.

### Crop first when the answer is a count

Run `python scripts/crop.py IMAGE --panels --sheet --out-dir <scratch>` **before**
describing, whenever either of these is true:

1. **The rule might be a count.** Line-art puzzles — polylines, zigzags,
   staircases, dot patterns, matchstick figures — are usually separated by the
   *number* of strokes, sides, vertices, dots or intersections. At screenshot
   scale a 5-stroke zigzag and a 4-stroke zigzag look identical, and the wrong
   count is not a wrong *rule*, it is a confidently wrong answer. Counting is the
   one FIG operation the eye cannot be trusted on unzoomed.
2. **A shape is ambiguous.** A 5-sided blob is a pentagon, a 6-sided one a
   hexagon, and at small sizes they look alike.

`--panels` finds the bordered cells automatically (both set rows plus the target
figure) and `--sheet` tiles them, labelled `r<band>c<col>`, into **one** enlarged
image. So the whole question costs one crop call and one look, about a second of
compute. It trims screenshot sidebars first, so a black chrome strip down the
edge does not defeat it. Drop `--sheet` only if you need one cell very large.
Then count on the sheet, never on the original.

This is the one tool call the FIG path budgets for. It is not the script the
route forbids: it produces a *better image*, not a restatement of what you
already read.

## 1. Classification / grouping — "which set does this figure belong to?"

The two sets are built from **complementary** rules: whatever is true of every
figure in Set A is false of every figure in Set B. So you are looking for one
binary attribute, not a description.

Test in this order. Stop at the first that separates the sets cleanly.

| # | Candidate rule | What to compute per figure |
| --- | --- | --- |
| 1 | **Shape identity across elements** | Are the two black shapes the same? The two white shapes? The outer shapes? The inner shapes? *(the most common rule in this family)* |
| 2 | **Nesting chain direction** | Does the small/outlined element's inner shape equal the large/black element's outer shape, or the reverse? |
| 3 | **Fill pattern** | Count black shapes; count white shapes; is the outermost shape black or white; do fills alternate black/white going inward? |
| 4 | **Element / shape count** | Total shapes per cell; number of distinct shapes; nesting depth (2 vs 3 levels) |
| 5 | **Side count arithmetic** | Sum of sides of all shapes odd/even; inner sides > outer sides; sides differ by a constant; sides increase inward |
| 6 | **Curved vs straight** | Exactly one curved (circle/arc) shape per figure vs none vs two |
| 7 | **Symmetry** | Each figure has a vertical axis of symmetry vs not; rotational symmetry order |
| 8 | **Position / orientation** | Which element is upper-left vs lower-right; all figures point the same way; one element rotated relative to the other |
| 9 | **Size relation** | Larger element black vs white; size order matches nesting order |
| 10 | **Line/intersection count** | Number of line segments, intersections, enclosed regions, or free ends — **count on a cropped panel, never on the original** |

Procedure:

1. Write the one-line description of all set figures plus the target.
2. Take rule 1: compute its value for each Set A figure. If all agree and no Set
   B figure shares that value, you are done.
3. Otherwise move to rule 2. Do **not** revisit a rule with a patched exception —
   "Set A means X, except figure 3" is a misread description, so go back and
   re-read figure 3 rather than weakening the rule.
4. Apply the winning rule to the target figure. State the rule for *both* sets
   and say explicitly why the target fails the other one. If it fails both,
   answer "neither" — that option exists precisely because it is sometimes right.

A figure whose description is *identical in structure* to one set member (same
nesting, same fills, one shape swapped) is a strong tell — check the rule anyway,
but expect it to confirm.

**The silhouette trap.** On line-art sets the target is deliberately drawn in the
same *idiom* as a member of the wrong set — same zigzag, same circle placement —
and differs only by one stroke. Matching the overall look gives the wrong set
every time. Count, then match.

## 2. Figure series — "what comes next?"

Track each attribute independently across the frames, as a separate series:

- **Rotation**: degrees per step, and direction. Check whether the whole figure
  rotates or only one element. A 45°/step element and a 90°/step element in the
  same frame is the standard construction.
- **Movement**: an element stepping around positions (clockwise one corner per
  frame), or along a path, possibly bouncing at the end.
- **Count**: elements added or removed by a fixed number, or by 1, 2, 3 …
- **Fill**: alternating black/white, or the black filling spreading one region
  per step.
- **Size**: growing/shrinking monotonically.
- **Reflection**: alternate frames are mirrored.

Write the per-attribute series as numbers (`rot: 0, 45, 90, 135 → 180`) and read
the next term off each, then combine. Check the answer options for the trap where
two options match every attribute but one.

## 3. Figure analogy — A : B :: C : ?

Name the *single* transformation A→B, then apply it verbatim to C. Candidates,
in frequency order: rotation by a fixed angle; reflection about a named axis;
fill inversion; adding/removing an element; shrinking one element and enlarging
another; replacing each shape by one with one more/fewer side; the inner and
outer shapes swapping places.

The classic trap: the transformation is a **reflection**, and a rotation option
is also present — they differ only for a chiral figure, so check an asymmetric
detail (a notch, a dot, the direction an arrow points).

## 4. Odd one out

Find the attribute shared by all-but-one. Test in order: shape count · side count
(often one figure has an even count when the rest are odd) · symmetry · curved vs
straight-only · rotational relationship (four of the five are rotations of each
other, one is a *mirror* of them — the most frequent construction) · fill ·
nesting depth · number of enclosed regions.

## 5. Mirror and water images

- **Mirror (vertical line to the right/left)**: left↔right flips, up/down
  unchanged. Letters/digits: reverse the *order* of the characters as well as
  each character's shape.
- **Water (horizontal line below)**: up↔down flips, left/right unchanged.
  Character order does **not** reverse.
- Symmetric characters give the fastest check: A H I M O T U V W X Y and 0 8 are
  mirror-invariant; B C D E H I K O X and 0 3 8 are water-invariant. Find one in
  the string, see which options preserve it, and eliminate.
- The spacing and slant of the whole string flips too — reject options that only
  flipped the glyphs.

## 6. Paper folding and punching

- **Unfolding**: each fold doubles the holes, reflected about that fold line, in
  reverse order of folding. Count holes first: n punches with k folds gives
  n × 2^k holes unless a punch sits on a fold line (then fewer).
- Work backwards one fold at a time, mirroring the copies, and check the *count*
  of the answer options before checking positions — it usually kills three of
  them.
- **Folding into a shape / dot-position**: the dot's distance from the fold edge
  is preserved.

## 7. Cubes, dice and nets

- On a die, opposite faces never appear together in one view. From two views
  sharing a common face, rotate mentally about that face to fix the rest.
- Standard dice: opposite faces sum to 7 — but only say so if the figure is
  stated to be a standard die.
- On a net, faces **opposite** each other are separated by exactly one face in a
  row or column, or lie at the two ends of an L. Adjacent-in-the-net faces are
  adjacent on the cube.
- For painted-cube counting, the formulas are arithmetic — that is a NUM
  question: 3 faces painted = 8 corners, 2 faces = 12(n−2), 1 face = 6(n−2)²,
  0 faces = (n−2)³. Verify with a one-line script if n is large.

## 8. Embedded / hidden figures and counting figures

- **Embedded**: check the target's distinctive *angles and proportions*, not its
  overall look; the target appears without rotation in most papers, but confirm.
- **Counting triangles/squares/rectangles**: label every vertex or cell, then
  count systematically by size class (1-cell, 2-cell, …) and sum. For a grid of
  m×n cells, rectangles = C(m+1,2)·C(n+1,2) — this is arithmetic, so compute it
  in a script rather than counting by eye.

## 9. Matrix / grid pattern (3×3 with one blank)

Read rows first, then columns, then the diagonals. The rule is usually one of:
an attribute increments along the row; the third cell is the *superposition* of
the first two; the third is the first minus the shared parts of the second
(elements common to both cancel); or each row contains the same three shapes in
a different order (a Latin square). Check the cancellation rule explicitly — it
is the one most often missed.

## 10. Answering

State the rule for the whole group in one sentence, apply it to the target, and
name why each rejected option fails. `Confidence: high` when the rule holds for
every figure in the group with no exception and the contrast group violates it
uniformly; `medium` when one figure's description was uncertain; `low` when no
rule separates cleanly — and then say which cell you could not resolve.
