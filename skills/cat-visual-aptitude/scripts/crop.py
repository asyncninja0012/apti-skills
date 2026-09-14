#!/usr/bin/env python3
"""Crop, rotate, upscale and sharpen a region of a question screenshot.

Usage:
  python crop.py IMAGE --info
  python crop.py IMAGE --box LEFT TOP RIGHT BOTTOM [--scale 3] [--enhance]
  python crop.py IMAGE --grid 3x3 --cell 2,1 [--scale 3]
  python crop.py IMAGE --rotate 90 [--out rotated.png]
  python crop.py IMAGE --strips 4 --axis y        # write 4 horizontal slices
  python crop.py IMAGE --boxes 100 35 795 195  100 260 795 410   # many at once
  python crop.py IMAGE --panels --sheet           # every cell, tiled into one image
  python crop.py IMAGE --panels                   # auto-split the figure cells

Coordinates may be pixels (120 340 480 600) or fractions of width/height
(0.0 0.5 0.4 1.0). Fractions are detected when every value is <= 1.

--grid splits the image into an RxC grid and crops one cell (1-indexed,
"col,row"), handy when you only know the label is "bottom left".

--strips writes every slice at once, so one call surfaces the whole axis or
legend column without guessing coordinates.

--boxes takes any number of 4-value groups and writes them all in one call.
Use it instead of several --box runs: one round-trip, one set of outputs.

--panels is the non-verbal-figure workhorse. It finds the bordered cells of a
"which set does this figure belong to" / figure-series layout automatically:
horizontal bands of content are detected first, then the full-height vertical
rule lines inside each band, so adjacent panels sharing a border are still
split. Every panel is written upscaled, named <stem>_r<band>c<col>.png. Pass
--panels-min to drop thin bands of question text. Add --sheet to get all the
cells tiled into a single labelled image instead of N files - one crop call and
one look covers the whole question. This is the call to make
whenever the answer depends on *counting* strokes, sides, dots or intersections
in thin line art -- counts are unreliable at screenshot scale.

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


def dark_mask(im, thresh=160):
    """Rows/cols of dark-pixel counts, for finding panel borders."""
    g = ImageOps.grayscale(im)
    w, h = g.size
    px = g.load()
    rows = [0] * h
    cols = [0] * w
    for y in range(h):
        for x in range(w):
            if px[x, y] < thresh:
                rows[y] += 1
                cols[x] += 1
    return rows, cols


def runs(flags):
    """Maximal runs of True as (start, end_exclusive)."""
    out, start = [], None
    for i, f in enumerate(flags):
        if f and start is None:
            start = i
        elif not f and start is not None:
            out.append((start, i))
            start = None
    if start is not None:
        out.append((start, len(flags)))
    return out


def trim_margins(im):
    """Drop full-height / full-width dark margins (screenshot sidebars).

    A black chrome strip down one edge otherwise makes every row look like
    content and defeats band detection.
    """
    w, h = im.size
    rows, cols = dark_mask(im)
    left, right, top, bottom = 0, w, 0, h
    while left < right and cols[left] >= 0.9 * h:
        left += 1
    while right > left and cols[right - 1] >= 0.9 * h:
        right -= 1
    while top < bottom and rows[top] >= 0.9 * w:
        top += 1
    while bottom > top and rows[bottom - 1] >= 0.9 * w:
        bottom -= 1
    return (left, top, right, bottom)


def find_panels(im, min_h, pad=2):
    """Return [(box, band_index, col_index)] for the bordered cells.

    Bands of content are found first (horizontal rows of figures), then the
    full-height vertical rule lines inside each band, so panels that share a
    border are still separated.
    """
    ox, oy, ex, ey = trim_margins(im)
    work = im.crop((ox, oy, ex, ey))
    w, h = work.size
    rows, _ = dark_mask(work)
    bands = [(a, b) for a, b in runs([c > 0 for c in rows]) if b - a >= min_h]

    panels = []
    for bi, (top, bot) in enumerate(bands, 1):
        bh = bot - top
        _, cols = dark_mask(work.crop((0, top, w, bot)))
        # a vertical rule spans (almost) the whole band height
        rule_runs = runs([c >= 0.75 * bh for c in cols])
        if len(rule_runs) < 2:
            panels.append(((ox, oy + top, ox + w, oy + bot), bi, 1))
            continue
        edges = [(a + b) // 2 for a, b in rule_runs]
        for ci, (l, r) in enumerate(zip(edges, edges[1:]), 1):
            if r - l < 8:
                continue
            box = (ox + max(0, l - pad), oy + max(0, top - pad),
                   ox + min(w, r + pad), oy + min(h, bot + pad))
            panels.append((box, bi, ci))
    return panels


def contact_sheet(im, panels, scale, gap=14, label_h=20):
    """Tile every panel into one labelled image, so the whole set reads in one look."""
    from PIL import ImageDraw
    tiles = []
    for box, bi, ci in panels:
        c = im.crop(box)
        c = c.resize((max(1, int(c.width * scale)), max(1, int(c.height * scale))),
                     Image.LANCZOS)
        tiles.append((c, f"r{bi}c{ci}"))

    bands = {}
    for (c, name), (_, bi, _) in zip(tiles, panels):
        bands.setdefault(bi, []).append((c, name))

    row_w = [sum(c.width for c, _ in v) + gap * (len(v) + 1) for v in bands.values()]
    row_h = [max(c.height for c, _ in v) + gap + label_h for v in bands.values()]
    sheet = Image.new("RGB", (max(row_w), sum(row_h) + gap), "white")
    d = ImageDraw.Draw(sheet)
    y = gap
    for bi in sorted(bands):
        x = gap
        rh = max(c.height for c, _ in bands[bi])
        for c, name in bands[bi]:
            sheet.paste(c, (x, y))
            d.text((x + 2, y + rh + 3), name, fill="black")
            x += c.width + gap
        y += rh + gap + label_h
    return sheet


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


def selftest():
    """Synthesise a two-row figure-set sheet and check --panels recovers it."""
    from PIL import ImageDraw
    W, H = 900, 640
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    # a black screenshot sidebar down the right edge - the case that used to
    # collapse band detection into one full-image panel
    d.rectangle([W - 60, 0, W - 1, H - 1], fill="black")
    cells = []
    for row, top in enumerate([40, 250], start=1):
        for col in range(5):
            l = 60 + col * 140
            d.rectangle([l, top, l + 140, top + 140], outline="black")
            cells.append((row, col + 1))
    d.rectangle([60, 460, 200, 600], outline="black")   # the target figure
    d.text((60, 615), "Q3 Which set does the Figure belong to?", fill="black")

    found = find_panels(im, 40)
    assert len(found) == 11, f"expected 11 panels, got {len(found)}"
    bands = sorted({bi for _, bi, _ in found})
    assert bands == [1, 2, 3], bands
    per_band = [sum(1 for _, bi, _ in found if bi == b) for b in bands]
    assert per_band == [5, 5, 1], per_band
    for box, bi, ci in found:
        assert box[2] <= W - 60, f"panel r{bi}c{ci} bled into the sidebar: {box}"
        assert box[2] - box[0] > 20 and box[3] - box[1] > 20, box
    print(f"selftest OK: {len(found)} panels, {per_band} per band, sidebar trimmed")


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("image", nargs="?")
    p.add_argument("--box", nargs=4, type=float, metavar=("L", "T", "R", "B"),
                   help="crop box in pixels or fractions of the image size")
    p.add_argument("--boxes", nargs="+", type=float, metavar="V",
                   help="several crop boxes at once: L T R B L T R B ...")
    p.add_argument("--panels", action="store_true",
                   help="auto-detect and write every bordered figure cell")
    p.add_argument("--sheet", action="store_true",
                   help="with --panels: tile every cell into ONE labelled image "
                        "(one crop call + one look instead of N files)")
    p.add_argument("--panels-min", type=int, default=40,
                   help="ignore content bands thinner than this (default 40 px)")
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
    p.add_argument("--out-dir", help="write outputs here instead of beside the input; "
                                     "use it when the image sits in a read-only cache")
    p.add_argument("--info", action="store_true", help="print image size and exit")
    p.add_argument("--selftest", action="store_true",
                   help="check panel detection on a synthetic sheet and exit")
    a = p.parse_args()

    if a.selftest:
        selftest()
        return
    if not a.image:
        p.error("an image is required (or pass --selftest)")

    im = Image.open(a.image)
    if im.mode not in ("RGB", "L"):
        im = im.convert("RGB")
    if a.rotate:
        im = im.rotate(a.rotate, expand=True, resample=Image.BICUBIC)
    w, h = im.size

    stem = os.path.splitext(a.image)[0]
    if a.out_dir:
        os.makedirs(a.out_dir, exist_ok=True)
        stem = os.path.join(a.out_dir, os.path.basename(stem))
    print(f"{a.image}: {w} x {h} px, mode={im.mode}")
    if a.info:
        return

    if a.panels:
        found = find_panels(im, a.panels_min)
        if not found:
            print("no panels found - try --panels-min lower, or use --boxes")
            return
        if a.sheet:
            sheet = contact_sheet(im, found, a.scale)
            if a.enhance:
                sheet = enhance(sheet)
            out = a.out or f"{stem}_sheet.png"
            sheet.save(out)
            bands = sorted({bi for _, bi, _ in found})
            per = [sum(1 for _, bi, _ in found if bi == b) for b in bands]
            print(f"{len(found)} panels in {len(bands)} bands {per} -> "
                  f"{sheet.width}x{sheet.height}  saved: {out}")
            print("Read this one file, then count strokes on it - not on the original.")
            return
        for box, bi, ci in found:
            out = f"{stem}_r{bi}c{ci}.png"
            c = save(im.crop(box), out, a.scale, a.enhance)
            print(f"panel r{bi}c{ci} {box} -> {c.width}x{c.height}  saved: {out}")
        print(f"{len(found)} panels written. Count strokes on these, not the original.")
        return

    if a.boxes:
        vals = a.boxes
        if len(vals) % 4:
            sys.exit("--boxes needs a multiple of 4 values (L T R B per box)")
        for i in range(0, len(vals), 4):
            box = parse_box(vals[i:i + 4], w, h)
            out = f"{stem}_box{i // 4 + 1}.png"
            c = save(im.crop(box), out, a.scale, a.enhance)
            print(f"box {i // 4 + 1} {box} -> {c.width}x{c.height}  saved: {out}")
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
        print("nothing to do: pass --box, --boxes, --panels, --grid, "
              "--strips or --rotate")
        return

    out = a.out or stem + "_crop.png"
    crop = save(im.crop(box), out, a.scale, a.enhance)
    print(f"cropped {box} -> {crop.width}x{crop.height}  saved: {out}")


if __name__ == "__main__":
    main()
