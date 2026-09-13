#!/usr/bin/env python3
"""Draw a labelled pixel grid over a chart so coordinates can be read off reliably.

Why: estimating "that bar is about 45" is the single biggest error source in
chart DI. Instead, overlay a grid, read the *pixel* y of two known gridlines and
of the mark you want, then convert with calibrate.py. Pixel positions are easy to
read off an image accurately; data values are not.

Usage:
  python overlay.py IMAGE [--step 50] [--out grid.png] [--scale 1]
  python overlay.py IMAGE --step 25 --box 0.1 0.0 1.0 0.8   # overlay a crop only
  python overlay.py IMAGE --step 50 --axis y                # horizontal lines only

Output: a copy with thin lines every --step pixels, labelled with their pixel
coordinate. Minor ticks every step/5 px are drawn unlabelled.

Do NOT use this on a geometry figure: those are not to scale.

Requires Pillow:  pip install pillow
"""
import argparse
import os
import sys

try:
    from PIL import Image, ImageDraw
except ImportError:
    sys.exit("Pillow is required: pip install pillow")

MAJOR = (255, 0, 0)
MINOR = (255, 208, 208)
LABEL_BG = (255, 255, 255)


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("image")
    p.add_argument("--step", type=int, default=50, help="major gridline spacing in px (default 50)")
    p.add_argument("--axis", choices=["x", "y", "both"], default="both",
                   help="which gridlines to draw (default both)")
    p.add_argument("--box", nargs=4, type=float, metavar=("L", "T", "R", "B"),
                   help="overlay only this region (pixels, or fractions if all <= 1)")
    p.add_argument("--scale", type=float, default=1.0,
                   help="upscale before overlaying; labels stay in ORIGINAL-crop pixels")
    p.add_argument("--minor", type=int, default=None,
                   help="minor tick spacing in px (default step/5; 0 disables)")
    p.add_argument("--out", help="output path (default <name>_grid.png)")
    a = p.parse_args()

    im = Image.open(a.image).convert("RGB")
    w0, h0 = im.size
    ox, oy = 0, 0
    if a.box:
        vals = a.box
        if all(v <= 1 for v in vals):
            box = (int(vals[0] * w0), int(vals[1] * h0), int(vals[2] * w0), int(vals[3] * h0))
        else:
            box = tuple(int(v) for v in vals)
        ox, oy = box[0], box[1]
        im = im.crop(box)

    cw, ch = im.size
    s = a.scale
    if s != 1:
        im = im.resize((int(cw * s), int(ch * s)), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    W, H = im.size

    step = a.step
    minor = a.minor if a.minor is not None else max(1, step // 5)

    def vlines():
        for x in (range(0, cw + 1, minor) if minor else ()):
            if x % step:
                d.line([(x * s, 0), (x * s, H)], fill=MINOR, width=1)
        for x in range(0, cw + 1, step):
            d.line([(x * s, 0), (x * s, H)], fill=MAJOR, width=1)
            t = str(x + ox)
            d.rectangle([x * s + 2, 2, x * s + 8 + 7 * len(t), 16], fill=LABEL_BG)
            d.text((x * s + 4, 4), t, fill=MAJOR)

    def hlines():
        for y in (range(0, ch + 1, minor) if minor else ()):
            if y % step:
                d.line([(0, y * s), (W, y * s)], fill=MINOR, width=1)
        for y in range(0, ch + 1, step):
            d.line([(0, y * s), (W, y * s)], fill=MAJOR, width=1)
            t = str(y + oy)
            d.rectangle([2, y * s + 2, 10 + 7 * len(t), y * s + 16], fill=LABEL_BG)
            d.text((4, y * s + 4), t, fill=MAJOR)

    if a.axis in ("x", "both"):
        vlines()
    if a.axis in ("y", "both"):
        hlines()

    out = a.out or os.path.splitext(a.image)[0] + "_grid.png"
    im.save(out)
    print(f"overlaid step={step}px (minor {minor}px) on {cw}x{ch} region "
          f"at offset ({ox},{oy}); saved: {out}")
    print("Read pixel coords off the labels, then run calibrate.py. "
          "Labels are in ORIGINAL image pixels.")


if __name__ == "__main__":
    main()
