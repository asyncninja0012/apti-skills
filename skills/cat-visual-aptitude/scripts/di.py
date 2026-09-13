#!/usr/bin/env python3
"""DI toolkit: transcription validators, percentage/growth maths, option matching
and sensitivity analysis over uncertain chart reads.

Import it from your solve script (same directory, or add the dir to sys.path):

    import di

    tbl = {"2019": {"rev": 120, "cost": 80}, "2021": {"rev": 180, "cost": 120}}
    di.check_totals(tbl, grand=500)
    p = di.pct_change(di.profit(tbl["2019"]), di.profit(tbl["2021"]))
    di.match_option(p, {"A": 25, "B": 40, "C": 50, "D": 60}, unit="%")

Self-test everything:  python di.py --selftest
Quick one-off maths:   python di.py --pct-change 40 60
                       python di.py --cagr 100 200 5
                       python di.py --successive 10 -10

No third-party dependencies.
"""
from __future__ import annotations

import argparse
import itertools
import math

# --------------------------------------------------------------------------
# percentages and growth
# --------------------------------------------------------------------------


def pct_change(old, new):
    """Percentage change from old to new. Base is ALWAYS the earlier value."""
    if old == 0:
        raise ValueError("percentage change from zero is undefined")
    return (new - old) / old * 100.0


def pct_point(a_pct, b_pct):
    """Percentage-POINT difference. Not a percentage change."""
    return b_pct - a_pct


def reverse_pct(after, pct):
    """Value before a pct% change produced `after`."""
    return after / (1 + pct / 100.0)


def successive(*pcts):
    """Net percentage after applying each change in turn. +10 then -10 -> -1.0."""
    f = 1.0
    for p in pcts:
        f *= (1 + p / 100.0)
    return (f - 1) * 100.0


def cagr(start, end, intervals):
    """Compound annual growth rate in %. `intervals` = periods, i.e. years-1 for
    a series from 2015 to 2020 -> 5."""
    if start <= 0 or intervals <= 0:
        raise ValueError("cagr needs start > 0 and intervals > 0")
    return ((end / start) ** (1.0 / intervals) - 1) * 100.0


def avg_growth(start, end, intervals):
    """Absolute average growth per interval (not a rate)."""
    return (end - start) / intervals


def share(part, whole):
    return part / whole * 100.0


def of(pct, whole):
    """pct% of whole."""
    return pct / 100.0 * whole


def index_value(value, base_value):
    return value / base_value * 100.0


def from_index(idx, base_value):
    return idx / 100.0 * base_value


def weighted_mean(values, weights):
    tw = sum(weights)
    if tw == 0:
        raise ValueError("weights sum to zero")
    return sum(v * w for v, w in zip(values, weights)) / tw


def ratio(a, b, as_int=True):
    """Simplified 'a : b' string. Order matters -- check the stem."""
    if as_int and float(a).is_integer() and float(b).is_integer():
        g = math.gcd(int(a), int(b)) or 1
        return f"{int(a) // g} : {int(b) // g}"
    return f"{a / b:.4f} : 1"


def levels_from_growth(base, rates):
    """Turn a chart OF GROWTH RATES into levels. rates in %, applied in order."""
    out, v = [base], base
    for r in rates:
        v = v * (1 + r / 100.0)
        out.append(v)
    return out


def profit(row, rev="rev", cost="cost"):
    return row[rev] - row[cost]


def margin(row, rev="rev", cost="cost"):
    return (row[rev] - row[cost]) / row[rev] * 100.0


# --------------------------------------------------------------------------
# Phase-2 transcription validators. Each prints PASS/FAIL and returns a bool.
# --------------------------------------------------------------------------


def _verdict(name, ok, detail):
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}: {detail}")
    if not ok:
        print("         -> re-read the image. Do NOT adjust a number to fit.")
    return ok


def check_pie(shares, tol=1.0, degrees=False):
    """Pie sector shares sum to 100 (or degrees to 360)."""
    vals = list(shares.values()) if isinstance(shares, dict) else list(shares)
    target = 360.0 if degrees else 100.0
    s = sum(vals)
    return _verdict("pie sums", abs(s - target) <= tol,
                    f"sum={s:g} target={target:g} tol=+/-{tol:g}")


def check_stack(segments, total, tol=1.0):
    """Stacked-bar segments sum to the printed total."""
    vals = list(segments.values()) if isinstance(segments, dict) else list(segments)
    s = sum(vals)
    return _verdict("stack sums", abs(s - total) <= tol,
                    f"segments={s:g} printed total={total:g}")


def check_totals(table, row_totals=None, col_totals=None, grand=None, tol=1.0):
    """Reconcile a dict-of-dicts table against stated row/column/grand totals."""
    ok = True
    cols = sorted({c for r in table.values() for c in r})
    if row_totals:
        for k, stated in row_totals.items():
            got = sum(table[k].values())
            ok &= _verdict(f"row total {k}", abs(got - stated) <= tol,
                           f"computed={got:g} stated={stated:g}")
    if col_totals:
        for c, stated in col_totals.items():
            got = sum(r.get(c, 0) for r in table.values())
            ok &= _verdict(f"col total {c}", abs(got - stated) <= tol,
                           f"computed={got:g} stated={stated:g}")
    if grand is not None:
        got = sum(sum(r.values()) for r in table.values())
        ok &= _verdict("grand total", abs(got - grand) <= tol,
                       f"computed={got:g} stated={grand:g}")
    if not (row_totals or col_totals or grand is not None):
        print(f"  [INFO] table has {len(table)} rows, columns {cols}; "
              "no stated totals given to check against")
    return ok


def check_mean(values, stated, tol=0.05):
    got = sum(values) / len(values)
    return _verdict("stated average", abs(got - stated) <= tol,
                    f"computed={got:.4g} stated={stated:g}")


def check_index_base(series, base_key, tol=0.01):
    v = series[base_key]
    return _verdict(f"index base {base_key}", abs(v - 100) <= tol, f"reads {v:g}, expected 100")


def check_cumulative(series, total=None, tol=1.0):
    """Ogive / cumulative series: non-decreasing, and ends at the total."""
    vals = list(series.values()) if isinstance(series, dict) else list(series)
    mono = all(b >= a - tol for a, b in zip(vals, vals[1:]))
    ok = _verdict("cumulative monotone", mono, f"series={vals}")
    if total is not None:
        ok &= _verdict("cumulative endpoint", abs(vals[-1] - total) <= tol,
                       f"last={vals[-1]:g} stated total={total:g}")
    return ok


def periods_from_cumulative(series):
    """Per-period values from a cumulative series. The usual ogive mistake is to
    read a cumulative point as a period value."""
    keys = list(series)
    vals = [series[k] for k in keys]
    out = {keys[0]: vals[0]}
    for k, a, b in zip(keys[1:], vals, vals[1:]):
        out[k] = b - a
    return out


def check_legend(legend, table_series):
    a, b = set(legend), set(table_series)
    return _verdict("legend mapping", a == b,
                    f"legend={sorted(a)} table={sorted(b)}"
                    + ("" if a == b else f" missing={sorted(a ^ b)}"))


# --------------------------------------------------------------------------
# option matching and sensitivity
# --------------------------------------------------------------------------


def match_option(value, options, tol=0.05, unit=""):
    """Match a computed value against the options.

    options: {"A": 25, "B": 40, ...} -- numeric values only.
    Prints the gap to every option and refuses to snap to a near miss.
    Returns the matching label, or None.
    """
    print(f"\ncomputed = {value:.6g}{unit}")
    rows = []
    for label, opt in options.items():
        gap = value - opt
        rel = abs(gap) / abs(opt) * 100 if opt else float("inf")
        rows.append((abs(gap), label, opt, gap, rel))
    rows.sort()
    for _, label, opt, gap, rel in rows:
        print(f"  ({label}) {opt:<12g} gap {gap:+.6g}  ({rel:.3g}% off)")
    best_gap, best, opt, _, rel = rows[0]
    if best_gap <= tol or rel <= 0.5:
        print(f"MATCH: ({best}) {opt:g}{unit}")
        return best
    print(f"NO MATCH. Nearest is ({best}) at {rel:.3g}% off -- do NOT snap to it.")
    print("Check, in order: percentage base / percentage vs percentage-point / "
          "absolute vs share / axis origin / second y-axis / subset of periods.")
    print("Then run distractor forensics: which mistake would produce each option?")
    return None


def _nearest_label(val, options, tol=0.05):
    """Which option does `val` land on? '?' when it sits ambiguously between two.

    Ambiguous means the gap to the nearest option is more than a quarter of the
    gap to the runner-up -- i.e. the value is not clearly in one option's basin.
    """
    gaps = sorted((abs(val - o), l) for l, o in options.items())
    if gaps[0][0] <= tol:
        return gaps[0][1]
    if len(gaps) > 1 and gaps[0][0] > 0.25 * gaps[1][0]:
        return "?"
    return gaps[0][1]


def sensitivity(fn, uncertain, options=None, tol=0.05, unit=""):
    """Is the answer robust to the uncertainty in the chart reads?

    fn:        callable taking **kwargs and returning the answer value.
    uncertain: {"cost2020": (95, 100), "rev2019": (118, 122)} -- low/high per
               approx-tagged read. A single number means it is exact.
    options:   optional {"A": 25, ...} to report which option each corner gives.

    Evaluates fn at every corner of the box. Prints ROBUST when all corners give
    the same option (or the same rounded value), SENSITIVE otherwise -- in which
    case go back and pixel-calibrate the offending mark instead of hedging.
    """
    names = list(uncertain)
    grids = []
    for n in names:
        v = uncertain[n]
        grids.append(sorted(set(v)) if isinstance(v, (tuple, list)) else [v])

    results = []
    for combo in itertools.product(*grids):
        kw = dict(zip(names, combo))
        val = fn(**kw)
        lab = _nearest_label(val, options, tol) if options else None
        results.append((kw, val, lab))

    print(f"\nsensitivity over {len(results)} corners of "
          f"{len(names)} uncertain read(s): {names}")
    vals = [r[1] for r in results]
    print(f"  value range: {min(vals):.6g} .. {max(vals):.6g}{unit}")
    for kw, val, lab in results:
        shown = ", ".join(f"{k}={v:g}" for k, v in kw.items())
        print(f"    {shown:<40} -> {val:.6g}{unit}" + (f"  option {lab}" if lab else ""))

    if options:
        labs = {r[2] for r in results}
        if len(labs) == 1 and "?" not in labs:
            print(f"  ROBUST: every corner lands on option {labs.pop()}. "
                  "Answer it, and drop the caveat.")
            return True
        print(f"  SENSITIVE: corners land on {sorted(labs)}. Pixel-calibrate the "
              "read with overlay.py + calibrate.py before answering.")
        return False

    spread = max(vals) - min(vals)
    print(f"  spread {spread:.6g}{unit}; no options supplied -- judge against the "
          "precision the stem asks for.")
    return None


def back_solve(options, condition, unit=""):
    """Substitute each option into the original condition. condition(x) -> bool."""
    print("\nback-solving:")
    hits = []
    for label, val in options.items():
        try:
            ok = bool(condition(val))
        except Exception as e:  # a failing option is informative, not fatal
            ok, val_note = False, f" (raised {type(e).__name__})"
        else:
            val_note = ""
        print(f"  ({label}) x={val:g}{unit}: {'SATISFIES' if ok else 'no'}{val_note}")
        if ok:
            hits.append(label)
    if len(hits) == 1:
        print(f"unique solution: ({hits[0]})")
    elif not hits:
        print("no option satisfies the condition -- the condition is mis-transcribed")
    else:
        print(f"several options satisfy it: {hits} -- the condition is under-specified")
    return hits


# --------------------------------------------------------------------------


def _selftest():
    print("percentages")
    assert abs(pct_change(40, 60) - 50) < 1e-9
    assert abs(pct_change(60, 40) + 33.3333333) < 1e-6
    assert abs(pct_point(20, 25) - 5) < 1e-9
    assert abs(reverse_pct(120, 20) - 100) < 1e-9
    assert abs(successive(10, -10) - -1.0) < 1e-9
    assert abs(cagr(100, 200, 5) - 14.8698) < 1e-3
    assert abs(weighted_mean([10, 20], [1, 3]) - 17.5) < 1e-9
    assert ratio(120, 80) == "3 : 2"
    assert abs(levels_from_growth(100, [10, 10])[-1] - 121) < 1e-9
    assert abs(margin({"rev": 200, "cost": 150}) - 25) < 1e-9
    print("  ok")

    print("validators")
    assert check_pie({"a": 40, "b": 35, "c": 25})
    assert not check_pie({"a": 40, "b": 35, "c": 20})
    assert check_pie({"a": 144, "b": 216}, degrees=True)
    assert check_stack([10, 20, 30], 60)
    tbl = {"2019": {"rev": 120, "cost": 80}, "2021": {"rev": 180, "cost": 120}}
    assert check_totals(tbl, row_totals={"2019": 200, "2021": 300},
                        col_totals={"rev": 300, "cost": 200}, grand=500)
    assert check_mean([10, 20, 30], 20)
    assert check_index_base({"2015": 100, "2016": 112}, "2015")
    assert check_cumulative({"a": 10, "b": 30, "c": 60}, total=60)
    assert not check_cumulative({"a": 10, "b": 5, "c": 60})
    assert periods_from_cumulative({"a": 10, "b": 30, "c": 60}) == {"a": 10, "b": 20, "c": 30}
    assert check_legend(["rev", "cost"], ["cost", "rev"])
    assert not check_legend(["rev", "cost"], ["rev"])
    print("  ok")

    print("option matching")
    assert match_option(50.0, {"A": 25, "B": 40, "C": 50, "D": 60}, unit="%") == "C"
    assert match_option(47.3, {"A": 25, "B": 40, "C": 50, "D": 60}) is None
    print("  ok")

    print("sensitivity")
    opts = {"A": 25, "B": 40, "C": 50, "D": 60}
    r = sensitivity(lambda c2020: pct_change(40, 180 - c2020),
                    {"c2020": (118, 122)}, opts)
    assert r is False
    r = sensitivity(lambda c2020: pct_change(40, 180 - c2020),
                    {"c2020": (129.9, 130.1)}, opts)
    assert r is True
    print("  ok")

    print("back-solve")
    assert back_solve({"A": 2, "B": 3, "C": 4}, lambda x: x * x == 9) == ["B"]
    print("  ok")

    print("\nall self-tests passed")


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--selftest", action="store_true")
    p.add_argument("--pct-change", nargs=2, type=float, metavar=("OLD", "NEW"))
    p.add_argument("--cagr", nargs=3, type=float, metavar=("START", "END", "INTERVALS"))
    p.add_argument("--successive", nargs="+", type=float, metavar="PCT")
    p.add_argument("--reverse", nargs=2, type=float, metavar=("AFTER", "PCT"))
    p.add_argument("--weighted", nargs="+", type=float,
                   metavar="V1 V2 .. W1 W2 ..", help="values then weights, equal counts")
    a = p.parse_args()

    did = False
    if a.selftest:
        _selftest()
        did = True
    if a.pct_change:
        print(f"pct_change = {pct_change(*a.pct_change):.6g}%")
        did = True
    if a.cagr:
        s, e, n = a.cagr
        print(f"cagr = {cagr(s, e, int(n)):.6g}% over {int(n)} intervals")
        did = True
    if a.successive:
        print(f"net = {successive(*a.successive):.6g}%")
        did = True
    if a.reverse:
        print(f"original = {reverse_pct(*a.reverse):.6g}")
        did = True
    if a.weighted:
        n = len(a.weighted) // 2
        print(f"weighted mean = {weighted_mean(a.weighted[:n], a.weighted[n:]):.6g}")
        did = True
    if not did:
        p.print_help()


if __name__ == "__main__":
    main()
