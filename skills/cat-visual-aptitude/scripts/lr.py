#!/usr/bin/env python3
"""Solve CAT-style Logical Reasoning sets by exhaustive enumeration.

Do not reason the constraints out in prose -- encode every one as a named
predicate and let the machine intersect them. Dropping a constraint is the usual
failure mode, so every solver prints the constraint count back at you.

Copy the template for your set's shape, replace the ENTITIES / CONSTRAINTS
blocks, run it, then answer the sub-questions with evaluate_options().

Shapes provided:
  1. PERMUTATION    order people in seats / ranks / finishing positions
  2. CIRCULAR       round a table, with wrap-around adjacency and facing
  3. ASSIGNMENT     match each person to one attribute from each category
  4. SUBSET         choose which k of n items satisfy the conditions
  5. GRID           floors x flats, or any rows x columns placement
  6. PARTIAL ORDER  only pairwise "above/before" clues
  7. TOURNAMENT     round-robin results, then score the table
  8. CRYPTARITHM    letters standing for distinct digits
  9. BINARY LOGIC   truth-tellers and liars

Run all demos:   python lr.py
Run one:         python lr.py --shape circular
Self-test:       python lr.py --selftest
"""
from __future__ import annotations

import argparse
from itertools import permutations, product, combinations

# ===========================================================================
# ANSWERING HELPERS -- use these, not eyeballing the solution list
# ===========================================================================


def report(name, constraints, solutions, limit=20):
    print(f"\n=== {name} ===")
    print(f"constraints encoded: {len(constraints)}")
    for d, _ in constraints:
        print(f"  - {d}")
    print(f"solutions found: {len(solutions)}")
    for s in solutions[:limit]:
        print(f"  {s}")
    if len(solutions) > limit:
        print(f"  ... and {len(solutions) - limit} more")
    if not solutions:
        print("  NONE -- a constraint is mis-encoded, or you mis-read the set.")
        print("  Comment constraints out one at a time to find which kills it,")
        print("  fix the ENCODING, and put it back. Never delete a constraint.")
    elif len(solutions) > 1:
        print("  Multiple solutions: use evaluate_options(). 'Must be true' needs")
        print("  ALWAYS; 'could be true' needs SOMETIMES or ALWAYS.")
    return solutions


def evaluate_options(solutions, options):
    """Classify each option across ALL surviving solutions.

    options: {"A": lambda s: s["P"] == 3, ...}
    Prints ALWAYS / SOMETIMES / NEVER per option and returns the dict.

      must be true      -> the ALWAYS option
      could be true     -> a SOMETIMES (or ALWAYS) option
      cannot be true    -> the NEVER option
    """
    if not solutions:
        print("\nno solutions -- fix the constraints before answering options")
        return {}
    print(f"\noptions across {len(solutions)} solution(s):")
    out = {}
    for label, pred in options.items():
        hits = sum(1 for s in solutions if pred(s))
        verdict = "ALWAYS" if hits == len(solutions) else ("NEVER" if hits == 0 else "SOMETIMES")
        out[label] = verdict
        print(f"  ({label}) {verdict:<9} true in {hits}/{len(solutions)}")
    print("  must-be-true -> ALWAYS | could-be-true -> SOMETIMES/ALWAYS | "
          "cannot-be-true -> NEVER")
    return out


def determined(solutions, key):
    """The value of `key` if it is the same in every solution, else None."""
    vals = {s[key] for s in solutions}
    if len(vals) == 1:
        v = vals.pop()
        print(f"  {key} is determined: {v}")
        return v
    print(f"  {key} is NOT determined; possible values {sorted(vals)}")
    return None


def all_determined(solutions):
    """Report every key that is pinned down across all solutions."""
    if not solutions:
        return {}
    out = {}
    for k in solutions[0]:
        vals = {s[k] for s in solutions}
        if len(vals) == 1:
            out[k] = vals.pop()
    print(f"\ndetermined in every solution: {out}")
    undet = [k for k in solutions[0] if k not in out]
    if undet:
        print(f"still free: {undet}")
    return out


# ===========================================================================
# SHAPE 1: PERMUTATION
# "Five friends A-E sit in a row of 5 chairs numbered 1-5 (left to right)."
# ===========================================================================
ENTITIES = ["A", "B", "C", "D", "E"]

# Each constraint is (english clue, predicate). pos is a dict: name -> seat number.
PERM_CONSTRAINTS = [
    ("A is not at either end",       lambda pos: pos["A"] not in (1, len(ENTITIES))),
    ("B sits immediately left of C", lambda pos: pos["C"] - pos["B"] == 1),
    ("D and E are not adjacent",     lambda pos: abs(pos["D"] - pos["E"]) != 1),
]


def solve_permutation(entities=ENTITIES, constraints=PERM_CONSTRAINTS):
    out = []
    for order in permutations(entities):
        pos = {name: i + 1 for i, name in enumerate(order)}
        if all(pred(pos) for _, pred in constraints):
            out.append(pos)
    return out


# ===========================================================================
# SHAPE 2: CIRCULAR
# "Six people sit around a circular table facing the centre."
# Fix one entity at seat 0 to kill rotational symmetry -- this loses no distinct
# arrangement. Do NOT also fix a second entity: mirror images are distinct when
# left/right matters.
# ===========================================================================
CIRC = ["P", "Q", "R", "S", "T", "U"]
N = len(CIRC)


def adj(pos, a, b, n=N):
    """Adjacent around the circle, wrap-around included."""
    return (pos[a] - pos[b]) % n in (1, n - 1)


def opposite(pos, a, b, n=N):
    """Directly across. Only exists for even n."""
    return n % 2 == 0 and (pos[a] - pos[b]) % n == n // 2


def immediate_left(pos, a, b, n=N, facing_centre=True):
    """`a` is immediately to the LEFT of `b`.

    Facing the centre, a person's left is the next seat clockwise in the seat
    numbering as drawn (seats numbered clockwise). Facing outward reverses it.
    If the set does not say which, run both and keep the reading that yields a
    consistent unique solution -- and say which you used.
    """
    step = 1 if facing_centre else -1
    return (pos[b] - pos[a]) % n == step % n


def gap(pos, a, b, k, n=N):
    """Exactly k people sit between a and b, measured the short way."""
    d = (pos[a] - pos[b]) % n
    return min(d, n - d) == k + 1


CIRC_CONSTRAINTS = [
    ("P and Q are adjacent",            lambda pos: adj(pos, "P", "Q")),
    ("R sits opposite S",               lambda pos: opposite(pos, "R", "S")),
    ("T is immediately left of U",      lambda pos: immediate_left(pos, "T", "U")),
    ("exactly one person between P, R", lambda pos: gap(pos, "P", "R", 1)),
]


def solve_circular(entities=CIRC, constraints=CIRC_CONSTRAINTS):
    pinned, rest = entities[0], entities[1:]
    out = []
    for order in permutations(rest):
        pos = {pinned: 0}
        for i, name in enumerate(order):
            pos[name] = i + 1
        if all(pred(pos) for _, pred in constraints):
            out.append(pos)
    return out


# ===========================================================================
# SHAPE 3: ASSIGNMENT
# "Four people each have a distinct city and a distinct drink."
# ===========================================================================
PEOPLE = ["P", "Q", "R", "S"]
CATEGORIES = {
    "city":  ["Delhi", "Mumbai", "Chennai", "Kolkata"],
    "drink": ["Tea", "Coffee", "Juice", "Water"],
}

ASSIGN_CONSTRAINTS = [
    ("P is not from Delhi",             lambda a: a["P"]["city"] != "Delhi"),
    ("The Mumbai person drinks Coffee", lambda a: all(v["drink"] == "Coffee"
                                                      for v in a.values()
                                                      if v["city"] == "Mumbai")),
    ("Q drinks Tea or Juice",           lambda a: a["Q"]["drink"] in ("Tea", "Juice")),
]


def solve_assignment(people=PEOPLE, categories=CATEGORIES,
                     constraints=ASSIGN_CONSTRAINTS):
    keys = list(categories)
    perms = [list(permutations(categories[k])) for k in keys]
    out = []
    for combo in product(*perms):
        a = {p: {k: combo[ki][pi] for ki, k in enumerate(keys)}
             for pi, p in enumerate(people)}
        if all(pred(a) for _, pred in constraints):
            out.append(a)
    return out


# ===========================================================================
# SHAPE 4: SUBSET  -- "Exactly 3 of 6 projects are approved."
# ===========================================================================
ITEMS = ["p1", "p2", "p3", "p4", "p5", "p6"]
PICK = 3

SUBSET_CONSTRAINTS = [
    ("If p1 is picked, p4 is not", lambda s: not ("p1" in s and "p4" in s)),
    ("At least one of p2, p3",     lambda s: bool({"p2", "p3"} & set(s))),
]


def solve_subset(items=ITEMS, pick=PICK, constraints=SUBSET_CONSTRAINTS):
    return [s for s in combinations(items, pick)
            if all(pred(s) for _, pred in constraints)]


# ===========================================================================
# SHAPE 5: GRID -- "Six people live in a building: 3 floors x 2 flats."
# Enumerate as a permutation over the flattened cells (floor, flat).
# ===========================================================================
GRID_PEOPLE = ["A", "B", "C", "D", "E", "F"]
FLOORS, FLATS = 3, 2
CELLS = [(f, t) for f in range(1, FLOORS + 1) for t in range(1, FLATS + 1)]

GRID_CONSTRAINTS = [
    ("A lives on the top floor",       lambda g: g["A"][0] == FLOORS),
    ("B and C live on the same floor",  lambda g: g["B"][0] == g["C"][0]),
    ("D lives immediately above E",     lambda g: g["D"][0] - g["E"][0] == 1),
    ("F lives in flat 1",               lambda g: g["F"][1] == 1),
]


def solve_grid(people=GRID_PEOPLE, cells=CELLS, constraints=GRID_CONSTRAINTS):
    out = []
    for arrangement in permutations(cells, len(people)):
        g = dict(zip(people, arrangement))
        if all(pred(g) for _, pred in constraints):
            out.append(g)
    return out


# ===========================================================================
# SHAPE 6: PARTIAL ORDER -- only pairwise clues, several orders may survive.
# ===========================================================================
RUNNERS = ["V", "W", "X", "Y"]
ABOVE = [("V", "W"), ("W", "X")]          # V finished before W, W before X
ORDER_CONSTRAINTS = [
    (f"{a} finished before {b}", (lambda a=a, b=b: lambda pos: pos[a] < pos[b])())
    for a, b in ABOVE
] + [
    ("Y did not finish last", lambda pos: pos["Y"] != len(RUNNERS)),
]


def solve_partial_order(entities=RUNNERS, constraints=ORDER_CONSTRAINTS):
    return solve_permutation(entities, constraints)


# ===========================================================================
# SHAPE 7: TOURNAMENT -- round robin, enumerate every match result, then score.
# ===========================================================================
TEAMS = ["T1", "T2", "T3"]
MATCHES = list(combinations(TEAMS, 2))
POINTS = {"W": 3, "D": 1, "L": 0}


def score_table(results):
    """results: {(home, away): 'W'|'L'|'D'} from the home team's perspective."""
    pts = {t: 0 for t in TEAMS}
    for (h, a), r in results.items():
        if r == "W":
            pts[h] += POINTS["W"]
        elif r == "L":
            pts[a] += POINTS["W"]
        else:
            pts[h] += POINTS["D"]
            pts[a] += POINTS["D"]
    return pts


TOURNEY_CONSTRAINTS = [
    ("T1 finished with 6 points",  lambda pts: pts["T1"] == 6),
    ("No team finished on 0",      lambda pts: all(v > 0 for v in pts.values())),
]


def solve_tournament(matches=MATCHES, constraints=TOURNEY_CONSTRAINTS):
    out = []
    for combo in product("WLD", repeat=len(matches)):
        results = dict(zip(matches, combo))
        pts = score_table(results)
        if all(pred(pts) for _, pred in constraints):
            out.append({"results": results, **pts})
    return out


# ===========================================================================
# SHAPE 8: CRYPTARITHM -- distinct digits for distinct letters.
#   Solves column sums like  AB + CB = CDA.
# ===========================================================================
def solve_cryptarithm(words, result, base=10, allow_leading_zero=False):
    letters = sorted(set("".join(words) + result))
    if len(letters) > base:
        raise ValueError(f"{len(letters)} letters cannot fit {base} digits")
    leading = {w[0] for w in list(words) + [result] if len(w) > 1}
    out = []
    for digits in permutations(range(base), len(letters)):
        m = dict(zip(letters, digits))
        if not allow_leading_zero and any(m[c] == 0 for c in leading):
            continue
        val = lambda w: sum(m[c] * base ** i for i, c in enumerate(reversed(w)))
        if sum(val(w) for w in words) == val(result):
            out.append(m)
    return out


# ===========================================================================
# SHAPE 9: BINARY LOGIC -- who is telling the truth.
# Each statement is (speaker, claim). `claim(truth)` reads the truth assignment.
# A speaker who is truthful must make a true claim; a liar a false one.
# ===========================================================================
SPEAKERS = ["A", "B", "C"]
STATEMENTS = [
    ("A", "B is lying",           lambda t: not t["B"]),
    ("B", "C is telling truth",   lambda t: t["C"]),
    ("C", "A and I both lie",     lambda t: (not t["A"]) and (not t["C"])),
]
NUM_TRUTHFUL = 1          # set to None if the count is not given


def solve_binary_logic(speakers=SPEAKERS, statements=STATEMENTS,
                       num_truthful=NUM_TRUTHFUL):
    out = []
    for combo in product([True, False], repeat=len(speakers)):
        t = dict(zip(speakers, combo))
        if num_truthful is not None and sum(combo) != num_truthful:
            continue
        if all(claim(t) == t[who] for who, _, claim in statements):
            out.append(t)
    return out


# ===========================================================================

DEMOS = {
    "permutation": lambda: report("permutation", PERM_CONSTRAINTS, solve_permutation()),
    "circular":    lambda: report("circular (P pinned at seat 0)", CIRC_CONSTRAINTS,
                                  solve_circular()),
    "assignment":  lambda: report("assignment", ASSIGN_CONSTRAINTS, solve_assignment()),
    "subset":      lambda: report("subset", SUBSET_CONSTRAINTS, solve_subset()),
    "grid":        lambda: report("grid (floors x flats)", GRID_CONSTRAINTS, solve_grid()),
    "order":       lambda: report("partial order", ORDER_CONSTRAINTS,
                                  solve_partial_order()),
    "tournament":  lambda: report("tournament", TOURNEY_CONSTRAINTS, solve_tournament()),
    "cryptarithm": lambda: _crypt_demo(),
    "logic":       lambda: report("binary logic", [(s, c) for _, s, c in STATEMENTS],
                                  solve_binary_logic()),
}


def _crypt_demo():
    sols = solve_cryptarithm(["TO", "GO"], "OUT")
    print("\n=== cryptarithm TO + GO = OUT ===")
    print(f"solutions found: {len(sols)}")
    for m in sols[:10]:
        print("  " + ", ".join(f"{k}={v}" for k, v in sorted(m.items())))
    return sols


def _selftest():
    perm = solve_permutation()
    assert perm, "permutation demo should have solutions"
    assert all(1 < s["A"] < 5 and s["C"] - s["B"] == 1 for s in perm)

    circ = solve_circular()
    assert all(adj(s, "P", "Q") and opposite(s, "R", "S") for s in circ)
    assert all(s["P"] == 0 for s in circ), "P must stay pinned"

    assign = solve_assignment()
    assert all(a["P"]["city"] != "Delhi" for a in assign)

    sub = solve_subset()
    assert all(len(s) == 3 for s in sub)
    assert not any("p1" in s and "p4" in s for s in sub)

    grid = solve_grid()
    assert all(g["A"][0] == FLOORS and g["F"][1] == 1 for g in grid)
    assert all(len(set(g.values())) == len(g) for g in grid), "cells must be unique"

    order = solve_partial_order()
    assert all(s["V"] < s["W"] < s["X"] and s["Y"] != 4 for s in order)

    tour = solve_tournament()
    assert all(t["T1"] == 6 for t in tour)

    crypt = solve_cryptarithm(["TO", "GO"], "OUT")
    assert crypt, "TO + GO = OUT should have at least one solution"
    for m in crypt:
        to = m["T"] * 10 + m["O"]
        go = m["G"] * 10 + m["O"]
        out = m["O"] * 100 + m["U"] * 10 + m["T"]
        assert to + go == out
        assert m["T"] and m["G"] and m["O"]

    logic = solve_binary_logic()
    assert all(sum(t.values()) == 1 for t in logic)

    v = evaluate_options(perm, {
        "A": lambda s: s["A"] != 1,
        "B": lambda s: s["B"] == 1,
        "C": lambda s: s["A"] == 1,
    })
    assert v["A"] == "ALWAYS" and v["C"] == "NEVER"

    assert determined(circ, "P") == 0
    all_determined(perm)
    print("\nall self-tests passed")


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--shape", choices=sorted(DEMOS), help="run one demo shape")
    p.add_argument("--selftest", action="store_true")
    a = p.parse_args()

    if a.selftest:
        _selftest()
    elif a.shape:
        DEMOS[a.shape]()
    else:
        for fn in DEMOS.values():
            fn()
        print("\nCopy the shape you need, replace the ENTITIES / CONSTRAINTS "
              "blocks, then answer with evaluate_options().")


if __name__ == "__main__":
    main()
