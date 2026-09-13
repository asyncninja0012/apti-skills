#!/usr/bin/env python3
"""Convert pixel positions on a chart into data values by two-point calibration.

Workflow:
  1. python overlay.py chart.png --step 50      -> chart_grid.png
  2. Look at chart_grid.png. Note the pixel coordinate of two gridlines whose
     data values you know, and the pixel coordinate of each mark you need.
  3. Run this script.

Usage:
  # y-axis: pixel 480 is value 0, pixel 120 is value 200
  python calibrate.py --p1 480 0 --p2 120 200 --read 245 --read 310 Cost2021

  # logarithmic axis
  python calibrate.py --p1 500 1 --p2 100 1000 --log --read 300

  # go the other way: what pixel does value 150 sit at?
  python calibrate.py --p1 480 0 --p2 120 200 --invert 150

Each --read takes a pixel coordinate and an optional label. Output includes the
value-per-pixel, so a plus/minus 2 px reading error converts into an explicit
value interval -- feed that interval straight into di.sensitivity().

No dependencies. Never use on a geometry figure (not to scale).
"""
import argparse
import math
import sys


def build(p1, v1, p2, v2, log):
    if p1 == p2:
        sys.exit("the two calibration pixels must differ")
    if log:
        if v1 <= 0 or v2 <= 0:
            sys.exit("--log needs strictly positive calibration values")
        l1, l2 = math.log10(v1), math.log10(v2)
        slope = (l2 - l1) / (p2 - p1)
        fwd = lambda px: 10 ** (l1 + (px - p1) * slope)
        inv = lambda v: p1 + (math.log10(v) - l1) / slope
    else:
        slope = (v2 - v1) / (p2 - p1)
        fwd = lambda px: v1 + (px - p1) * slope
        inv = lambda v: p1 + (v - v1) / slope
    return fwd, inv, slope


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--p1", nargs=2, type=float, required=True, metavar=("PIXEL", "VALUE"))
    p.add_argument("--p2", nargs=2, type=float, required=True, metavar=("PIXEL", "VALUE"))
    p.add_argument("--read", nargs="+", action="append", default=[],
                   metavar="PIXEL [LABEL]", help="a mark to convert; repeatable")
    p.add_argument("--invert", nargs="+", type=float, default=[],
                   metavar="VALUE", help="value -> pixel, repeatable")
    p.add_argument("--log", action="store_true", help="the axis is logarithmic")
    p.add_argument("--err", type=float, default=2.0,
                   help="assumed reading error in pixels (default 2)")
    p.add_argument("--round", type=int, default=2, help="decimals in output")
    a = p.parse_args()

    (p1, v1), (p2, v2) = a.p1, a.p2
    fwd, inv, slope = build(p1, v1, p2, v2, a.log)

    kind = "log10" if a.log else "linear"
    print(f"calibration: {kind}; pixel {p1:g} = {v1:g}, pixel {p2:g} = {v2:g}")
    if not a.log:
        print(f"1 px = {abs(slope):.4g} value units  "
              f"(a +/-{a.err:g} px read error is +/-{abs(slope) * a.err:.4g})")
    else:
        print(f"1 px = x{10 ** abs(slope):.5g} ratio")

    r = a.round
    if a.read:
        print("\npixel -> value")
        for item in a.read:
            px = float(item[0])
            label = " ".join(item[1:]) if len(item) > 1 else ""
            val = fwd(px)
            lo, hi = sorted((fwd(px - a.err), fwd(px + a.err)))
            print(f"  {px:7g}  ->  {val:.{r}f}   "
                  f"[{lo:.{r}f}, {hi:.{r}f}] at +/-{a.err:g}px   {label}")
        print("\nFeed the [low, high] intervals into di.sensitivity() when the "
              "options are close together.")

    if a.invert:
        print("\nvalue -> pixel")
        for v in a.invert:
            print(f"  {v:7g}  ->  {inv(v):.1f} px")

    if not a.read and not a.invert:
        print("\n(no --read or --invert given; calibration only)")


if __name__ == "__main__":
    main()
