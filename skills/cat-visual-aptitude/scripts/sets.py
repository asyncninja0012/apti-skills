#!/usr/bin/env python3
"""Venn / set-cardinality solver: exact regions when determined, feasible min and
max when not.

These questions ("at least how many liked all three?", "what is the maximum
possible number who liked exactly one?") are where hand reasoning quietly picks an
infeasible corner. This script searches the region values under every stated
constraint, so any min or max it reports is actually attainable, and it prints a
witness assignment to prove it.

Region naming for three sets A, B, C:
    a, b, c        = in ONLY that set
    ab, bc, ca     = in exactly those two
    abc            = in all three
    none           = in none of them

Derived quantities, all available as constraints or as optimisation targets:
    A, B, C            set sizes            (A = a + ab + ca + abc)
    AB, BC, CA         pairwise overlaps, INCLUDING abc
    ABC                = abc
    total, none
    exactly_one        a + b + c
    exactly_two        ab + bc + ca
    at_least_one       total - none
    at_least_two       exactly_two + abc

Library use:

    import sets
    sets.venn3(total=100, A=50, B=40, C=30, AB=15, BC=10, CA=12, ABC=5)
    sets.venn3(total=60, A=30, B=25, C=20, none=0, maximise="exactly_one")
    sets.overlap_bounds(100, [80, 70, 60])       # at least how many in all three

CLI:
  python sets.py --total 100 --A 50 --B 40 --C 30 --AB 15 --BC 10 --CA 12 --ABC 5
  python sets.py --total 60 --A 30 --B 25 --C 20 --none 0 --max exactly_one
  python sets.py --total 100 --overlap 80 70 60
  python sets.py --selftest

No third-party dependencies.
"""
from __future__ import annotations

import argparse

REGIONS = ("abc", "ab", "bc", "ca", "a", "b", "c", "none")

# Every constrainable quantity as a sum of regions.
SUMS = {
    "A":            ("a", "ab", "ca", "abc"),
    "B":            ("b", "ab", "bc", "abc"),
    "C":            ("c", "bc", "ca", "abc"),
    "AB":           ("ab", "abc"),
    "BC":           ("bc", "abc"),
    "CA":           ("ca", "abc"),
    "ABC":          ("abc",),
    "none":         ("none",),
    "total":        REGIONS,
    "exactly_one":  ("a", "b", "c"),
    "exactly_two":  ("ab", "bc", "ca"),
    "at_least_one": ("a", "b", "c", "ab", "bc", "ca", "abc"),
    "at_least_two": ("ab", "bc", "ca", "abc"),
}


def derived(r):
    return {k: sum(r[m] for m in members) for k, members in SUMS.items()}


def _search(stated, cap, node_budget):
    """DFS over the regions with interval propagation from the stated sums.

    Assign regions in order; at each step the pending constraints give an exact
    upper bound, and a constraint whose other members are all assigned forces the
    value outright. That prunes hard enough for any realistic question.
    """
    cons = [(SUMS[k], v) for k, v in stated.items()]
    order = list(REGIONS)
    assigned = {}
    sols = []
    nodes = [0]
    overflow = [False]

    def rec(i):
        nodes[0] += 1
        if nodes[0] > node_budget:
            overflow[0] = True
            return
        if i == len(order):
            sols.append(dict(assigned))
            return
        v = order[i]
        lo, hi = 0, cap
        for members, target in cons:
            if v not in members:
                continue
            rem = target - sum(assigned[m] for m in members if m in assigned)
            if rem < 0:
                return
            hi = min(hi, rem)
            if all(m in assigned or m == v for m in members):
                lo = max(lo, rem)
        if lo > hi:
            return
        for val in range(lo, hi + 1):
            assigned[v] = val
            # early check: any constraint now fully assigned must match
            ok = True
            for members, target in cons:
                if all(m in assigned for m in members):
                    if sum(assigned[m] for m in members) != target:
                        ok = False
                        break
            if ok:
                rec(i + 1)
            del assigned[v]

    rec(0)
    return sols, nodes[0], overflow[0]


def venn3(total=None, A=None, B=None, C=None, AB=None, BC=None, CA=None,
          ABC=None, none=None, exactly_one=None, exactly_two=None,
          at_least_one=None, at_least_two=None, maximise=None, minimise=None,
          verbose=True, node_budget=4_000_000):
    """Find every feasible region assignment consistent with the givens.

    Returns (solutions, summary); summary maps each quantity to (min, max) over
    the feasible set. A quantity with min == max is determined by the givens.
    """
    given = dict(total=total, A=A, B=B, C=C, AB=AB, BC=BC, CA=CA, ABC=ABC,
                 none=none, exactly_one=exactly_one, exactly_two=exactly_two,
                 at_least_one=at_least_one, at_least_two=at_least_two)
    stated = {k: v for k, v in given.items() if v is not None}
    if not stated:
        raise ValueError("supply at least one quantity")
    bad = [k for k, v in stated.items() if v < 0]
    if bad:
        raise ValueError(f"negative given(s): {bad}")

    cap = max(stated.values())
    sols, nodes, overflow = _search(stated, cap, node_budget)

    if verbose:
        print(f"given: {stated}")
        print(f"visited {nodes:,} nodes; feasible assignments: {len(sols)}"
              + ("  (SEARCH TRUNCATED)" if overflow else ""))
    if overflow:
        print("  the search hit its node budget -- supply more givens (ABC, none "
              "and the pairwise overlaps prune hardest) before trusting a min/max")

    if not sols:
        if verbose:
            print("INFEASIBLE -- the givens contradict each other. Check whether "
                  "the question's pairwise figure INCLUDES the triple overlap "
                  "(AB does) or excludes it (exactly_two does).")
        return [], {}

    summary = {}
    for k in list(SUMS) + list(REGIONS):
        vals = [(derived(s)[k] if k in SUMS else s[k]) for s in sols]
        summary[k] = (min(vals), max(vals))

    if verbose:
        if len(sols) == 1:
            print(f"\nuniquely determined: "
                  + ", ".join(f"{k}={sols[0][k]}" for k in REGIONS))
        print("\nquantity            min      max   status")
        for k in list(REGIONS) + list(SUMS):
            lo, hi = summary[k]
            print(f"  {k:<16} {lo:>6} {hi:>8}   "
                  f"{'determined' if lo == hi else 'range'}")
        for target, want_max in ((maximise, True), (minimise, False)):
            if target:
                if target not in summary:
                    print(f"\nunknown target {target!r}; "
                          f"pick one of {sorted(summary)}")
                    continue
                lo, hi = summary[target]
                word = "MAXIMUM" if want_max else "MINIMUM"
                print(f"\n{word} {target} = {hi if want_max else lo}")
                print(f"  witness: {_witness(sols, target, want_max)}")
    return sols, summary


def _witness(sols, key, want_max):
    def val(s):
        return derived(s)[key] if key in SUMS else s[key]
    best = max(sols, key=val) if want_max else min(sols, key=val)
    return ", ".join(f"{k}={best[k]}" for k in REGIONS)


def venn2(total=None, A=None, B=None, AB=None, none=None, verbose=True):
    """Two sets: |A u B| = A + B - AB, and total = |A u B| + none."""
    if verbose:
        shown = {k: v for k, v in
                 dict(total=total, A=A, B=B, AB=AB, none=none).items()
                 if v is not None}
        print(f"given: {shown}")
    out = {}
    if A is not None and B is not None and AB is not None:
        out["at_least_one"] = A + B - AB
        out["exactly_one"] = A + B - 2 * AB
        out["only_A"] = A - AB
        out["only_B"] = B - AB
        if total is not None:
            out["none"] = total - out["at_least_one"]
    elif A is not None and B is not None and total is not None:
        n = none or 0
        out["at_least_one"] = total - n
        out["AB"] = A + B - out["at_least_one"]
        out["exactly_one"] = out["at_least_one"] - out["AB"]
        out["only_A"] = A - out["AB"]
        out["only_B"] = B - out["AB"]
        if none is None:
            out["note"] = "assumed none = 0; with none > 0 the overlap is larger"
    else:
        print("  need (A, B, AB) or (A, B, total)")
        return out
    if verbose:
        for k, v in out.items():
            print(f"  {k:<14} {v}")
        if any(isinstance(v, int) and v < 0 for v in out.values()):
            print("  NEGATIVE region -- the givens are inconsistent, re-read them")
    return out


def overlap_bounds(total, sizes, verbose=True):
    """Min and max possible size of the intersection of ALL the given sets.

        max = min(sizes)
        min = max(0, sum(sizes) - (k-1) * total)

    The workhorse for "at least how many people liked all three?".
    """
    k = len(sizes)
    lo = max(0, sum(sizes) - (k - 1) * total)
    hi = min(sizes)
    if verbose:
        print(f"{k} sets of sizes {sizes} inside a universe of {total}:")
        print(f"  the intersection of all of them is between {lo} and {hi}")
        print(f"  min = sum - (k-1)*total = {sum(sizes)} - {k - 1}*{total} "
              f"= {sum(sizes) - (k - 1) * total}, floored at 0")
        print("  (this assumes everyone is inside the universe; if some are in "
              "none of the sets, use that smaller effective universe)")
    return lo, hi


def _selftest():
    print("-- fully determined three-set case")
    sols, s = venn3(total=100, A=50, B=40, C=30, AB=15, BC=10, CA=12, ABC=5)
    assert len(sols) == 1, len(sols)
    assert sols[0] == {"abc": 5, "ab": 10, "bc": 5, "ca": 7,
                       "a": 28, "b": 20, "c": 13, "none": 12}, sols[0]
    assert s["exactly_one"] == (61, 61) and s["exactly_two"] == (22, 22)
    assert s["at_least_one"] == (88, 88)

    print("\n-- under-determined: maximise exactly_one")
    sols, s = venn3(total=60, A=30, B=25, C=20, none=0,
                    maximise="exactly_one", minimise="abc")
    # Sizes sum to 75 in a universe of 60 with nobody outside, so
    # (ab+bc+ca) + 2*abc = 15 and exactly_one = 45 + abc. abc can reach 7
    # (leaving one person in exactly two), giving exactly_one = 52 and
    # at_least_two = 15 - abc, i.e. 8..15. Hand-derived "45" is the trap here:
    # it silently assumes abc = 0.
    assert s["exactly_one"] == (45, 52), s["exactly_one"]
    assert s["abc"] == (0, 7), s["abc"]
    assert s["at_least_two"] == (8, 15), s["at_least_two"]

    print("\n-- 'exactly two' given instead of pairwise overlaps")
    sols, s = venn3(total=100, A=50, B=40, C=30, exactly_two=20, none=10)
    assert sols, "should be feasible"
    for x in sols:
        d = derived(x)
        assert d["total"] == 100 and d["exactly_two"] == 20 and d["none"] == 10

    print("\n-- infeasible givens are reported, not silently solved")
    sols, _ = venn3(total=10, A=8, B=8, C=8, ABC=0, none=0)
    assert sols == []

    print("\n-- two-set")
    out = venn2(total=100, A=60, B=50, AB=30)
    assert out["at_least_one"] == 80 and out["exactly_one"] == 50 and out["none"] == 20

    print("\n-- overlap bounds")
    assert overlap_bounds(100, [80, 70, 60]) == (10, 60)
    assert overlap_bounds(100, [50, 40]) == (0, 40)

    print("\nall self-tests passed")


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    for k in ("total", "A", "B", "C", "AB", "BC", "CA", "ABC", "none"):
        p.add_argument(f"--{k}", type=int)
    p.add_argument("--exactly-one", type=int)
    p.add_argument("--exactly-two", type=int)
    p.add_argument("--at-least-one", type=int)
    p.add_argument("--at-least-two", type=int)
    p.add_argument("--max", dest="maximise", help="quantity or region to maximise")
    p.add_argument("--min", dest="minimise", help="quantity or region to minimise")
    p.add_argument("--two-set", action="store_true", help="use the two-set solver")
    p.add_argument("--overlap", nargs="+", type=int, metavar="SIZE",
                   help="min/max overlap of these set sizes (needs --total)")
    p.add_argument("--selftest", action="store_true")
    a = p.parse_args()

    if a.selftest:
        _selftest()
    elif a.overlap:
        if a.total is None:
            p.error("--overlap needs --total")
        overlap_bounds(a.total, a.overlap)
    elif a.two_set:
        venn2(total=a.total, A=a.A, B=a.B, AB=a.AB, none=a.none)
    elif any(v is not None for v in (a.total, a.A, a.B, a.C, a.AB, a.BC, a.CA)):
        venn3(total=a.total, A=a.A, B=a.B, C=a.C, AB=a.AB, BC=a.BC, CA=a.CA,
              ABC=a.ABC, none=a.none, exactly_one=a.exactly_one,
              exactly_two=a.exactly_two, at_least_one=a.at_least_one,
              at_least_two=a.at_least_two, maximise=a.maximise,
              minimise=a.minimise)
    else:
        p.print_help()


if __name__ == "__main__":
    main()
