# LR set shapes → enumeration recipes

The rule: **never reason the constraints out in prose.** Encode every constraint
as a named predicate, intersect them by brute force, then answer the
sub-questions from the surviving set with `lr.evaluate_options()`.

`scripts/lr.py` ships runnable templates for each shape below. Copy the relevant
block, replace the entities and constraints, run it.

## Choosing the shape

| The set says | Shape | Space |
| --- | --- | --- |
| "sit in a row", "ranked 1st to nth", "finished in order" | permutation | n! |
| "sit around a circular table" | circular — fix one entity | (n−1)! |
| "n on each side of a rectangular table, facing each other" | two-row with an opposite map | (2n)! / symmetry |
| "live on n floors, one each" | permutation over floors | n! |
| "n floors × m flats" | grid assignment | see below |
| "each has one car and one city" | multi-attribute assignment | (n!)^k |
| "k of the n are selected" | subset | C(n,k) |
| "each of n people gets one of m tasks (repeats allowed)" | product | m^n |
| "distribute 20 coins among 4 people" | integer compositions | manageable with a bound |
| "each plays each other once" | round-robin results | 3^(matches) |
| "some like tea, some coffee…" with counts | Venn — use `scripts/sets.py` | — |
| "cities connected by roads with distances" | graph | paths / Dijkstra |
| letters standing for digits in a sum | cryptarithm | P(10, distinct letters) |
| "exactly one of them is lying" | binary logic | 2^n |

## Space management

Enumerate directly while the space is under a few million. Above that:

1. Apply the most restrictive constraint **inside** the generator, not as a
   post-filter — e.g. build permutations of the remaining entities after pinning
   the one whose position is given.
2. Decompose: solve the sub-puzzle that the constraints over-determine first
   (often one category), then extend.
3. For grids, iterate over columns as independent permutations and filter
   row-wise, instead of over all cells.
4. `10!` = 3.6e6 is fine. `12!` is not — decompose.

## Circular tables, carefully

- Fix one entity at seat 1. This removes rotational symmetry without losing
  solutions. Mention that you did it.
- Do **not** also fix a second entity unless the set gives a reflection-breaking
  clue; mirror images are genuinely distinct when left/right matters.
- Adjacency must wrap: use `(i - j) % n in (1, n - 1)`.
- "To the immediate left of X" with everyone **facing the centre** means the
  next seat **clockwise** from the observer's point of view is on their left — so
  left/right is the reverse of the outward-facing case. If the set does not say
  which, enumerate both and keep the reading that yields a consistent unique
  solution.
- Seats "opposite" each other exist only for even n: `(i + n // 2) % n`.

## Answering from the surviving set

```python
solutions = [s for s in candidates if all(p(s) for _, p in CONSTRAINTS)]
lr.report("seating", CONSTRAINTS, solutions)
lr.evaluate_options(solutions, {
    "A": lambda s: s["P"] == 3,
    "B": lambda s: abs(s["Q"] - s["R"]) == 1,
})
```

`evaluate_options` prints, for each option, `ALWAYS` / `SOMETIMES` / `NEVER`,
which maps directly onto the question wording:

| Stem asks | Pick the option that is |
| --- | --- |
| must be true / is definitely true | `ALWAYS` |
| could be true / is possible | `SOMETIMES` or `ALWAYS` |
| cannot be true / is definitely false | `NEVER` |
| is definitely false for all | `NEVER` |
| what is X's position | `lr.determined(solutions, "X")` — a value only if it is the same across all |
| how many arrangements are possible | `len(solutions)` |

Sanity rules:

- **Zero solutions** → a constraint is mis-encoded. Re-read the set; comment out
  constraints one at a time to find which one kills it, fix the encoding, and put
  it back. Never delete a constraint to get an answer.
- **Unexpectedly many solutions** → a constraint was dropped. Compare the printed
  constraint count with the number of numbered clues in the set.
- Exactly one solution is the common design for a CAT set with four
  sub-questions. If you have one solution, all four should fall out directly.

## Clue translation table

| English | Predicate |
| --- | --- |
| A is immediately left of B (row) | `pos[B] - pos[A] == 1` |
| A is to the left of B | `pos[A] < pos[B]` |
| A and B are adjacent (row) | `abs(pos[A] - pos[B]) == 1` |
| A and B are adjacent (circle of n) | `(pos[A] - pos[B]) % n in (1, n - 1)` |
| Exactly two people sit between A and B | `abs(pos[A] - pos[B]) == 3` |
| A is at an end | `pos[A] in (1, n)` |
| A is not at an end | `1 < pos[A] < n` |
| A sits opposite B (circle, even n) | `(pos[A] - pos[B]) % n == n // 2` |
| A is somewhere above B (floors) | `floor[A] > floor[B]` |
| A is immediately above B | `floor[A] - floor[B] == 1` |
| Unless A, B | `B or A` |
| A only if B | `(not A) or B` |
| If A then B | `(not A) or B` |
| Either A or B (exclusive) | `A != B` |
| At least one of A, B, C | `A or B or C` |
| Exactly two of A, B, C | `sum([A, B, C]) == 2` |
| Neither A nor B | `not A and not B` |
| A and B are not in the same group | `grp[A] != grp[B]` |
| No two of S are adjacent | `all(abs(pos[x] - pos[y]) != 1 for x, y in combinations(S, 2))` |

Write the English clue as the predicate's description string, verbatim. The
printed list of descriptions is what lets you audit that nothing was dropped.
