#!/usr/bin/env python3
"""Crop, rotate, upscale and sharpen a region of a question screenshot.

Usage:
  python crop.py IMAGE --info
  python crop.py IMAGE --box LEFT TOP RIGHT BOTTOM [--scale 3] [--enhance]
  python crop.py IMAGE --grid 3x3 --cell 2,1 [--scale 3]
  python crop.py IMAGE --rotate 90 [--out rotated.png]
  python crop.py IMAGE --strips 4 --axis y        # write 4 horizontal slices

Coordinates may be pixels (120 340 480 600) or fractions of width/height
(0.0 0.5 0.4 1.0). Fractions are detected when every value is <= 1.

--grid splits the image into an RxC grid and crops one cell (1-indexed,
"col,row"), handy when you only know the label is "bottom left".

--strips writes every slice at once, so one call surfaces the whole axis or
legend column without guessing coordinates.

--enhance sharpens, boosts contrast and greyscales, which usually rescues small
grey axis labels and compression-blurred legends.

Requires Pillow:  pip install pillow
"""
import argparse
import os
import sys

try:
    from PIL import Image, ImageEnhance, ImageOps, ImageFilter
except ImportError:
    sys.exit("Pillow is required: pip install pillow")


def parse_box(vals, w, h):
    if all(v <= 1 for v in vals):
        l, t, r, b = vals
        return (int(l * w), int(t * h), int(r * w), int(b * h))
    return tuple(int(v) for v in vals)


def enhance(im):
    im = ImageOps.grayscale(im)
    im = ImageOps.autocontrast(im, cutoff=1)
    im = ImageEnhance.Contrast(im).enhance(1.6)
    return im.filter(ImageFilter.UnsharpMask(radius=2, percent=160, threshold=2))


def save(crop, path, scale, do_enhance):
    if scale != 1:
        crop = crop.resize(
            (max(1, int(crop.width * scale)), max(1, int(crop.height * scale))),
            Image.LANCZOS,
        )
    if do_enhance:
        crop = enhance(crop)
    crop.save(path)
    return crop


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("image")
    p.add_argument("--box", nargs=4, type=float, metavar=("L", "T", "R", "B"),
                   help="crop box in pixels or fractions of the image size")
    p.add_argument("--grid", help="split into a grid, e.g. 3x3 (COLSxROWS)")
    p.add_argument("--cell", help="which grid cell to crop, 1-indexed 'col,row'")
    p.add_argument("--strips", type=int,
                   help="write N equal slices of the whole image")
    p.add_argument("--axis", choices=["x", "y"], default="y",
                   help="slice direction for --strips (y = horizontal bands)")
    p.add_argument("--rotate", type=float, default=0,
                   help="rotate this many degrees counter-clockwise before cropping")
    p.add_argument("--scale", type=float, default=3.0,
                   help="upscale factor after cropping (default 3)")
    p.add_argument("--enhance", action="store_true",
                   help="greyscale + autocontrast + unsharp mask")
    p.add_argument("--out", help="output path (default: <name>_crop.png next to input)")
    p.add_argument("--info", action="store_true", help="print image size and exit")
    a = p.parse_args()

    im = Image.open(a.image)
    if im.mode not in ("RGB", "L"):
        im = im.convert("RGB")
    if a.rotate:
        im = im.rotate(a.rotate, expand=True, resample=Image.BICUBIC)
    w, h = im.size

    stem = os.path.splitext(a.image)[0]
    print(f"{a.image}: {w} x {h} px, mode={im.mode}")
    if a.info:
        return

    if a.strips:
        n = a.strips
        for i in range(n):
            if a.axis == "y":
                box = (0, int(i * h / n), w, int((i + 1) * h / n))
            else:
                box = (int(i * w / n), 0, int((i + 1) * w / n), h)
            out = f"{stem}_strip{i + 1}.png"
            c = save(im.crop(box), out, a.scale, a.enhance)
            print(f"strip {i + 1}/{n} {box} -> {c.width}x{c.height}  saved: {out}")
        return

    if a.grid:
        cols, rows = (int(x) for x in a.grid.lower().split("x"))
        c, r = (int(x) for x in (a.cell or "1,1").split(","))
        cw, ch = w / cols, h / rows
        box = (int((c - 1) * cw), int((r - 1) * ch), int(c * cw), int(r * ch))
    elif a.box:
        box = parse_box(a.box, w, h)
    elif a.rotate:
        box = (0, 0, w, h)
    else:
        print("nothing to do: pass --box, --grid, --strips or --rotate")
        return

    out = a.out or stem + "_crop.png"
    crop = save(im.crop(box), out, a.scale, a.enhance)
    print(f"cropped {box} -> {crop.width}x{crop.height}  saved: {out}")


if __name__ == "__main__":
    main()
