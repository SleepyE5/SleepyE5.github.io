#!/usr/bin/env python3
"""Build the social preview card for sleepye5.github.io.

1200x630 is the Open Graph size. The card is composed from the page's own type
system rather than a new design: Georgia for anything you read, the system sans
for anything you operate, Menlo for anything that is a fact, on the same #0f1113
with the same dot grid and the same brass. The picture is a real capture from
the current build, the same file the portfolio links.

Run:  python3 tools/og-image.py
"""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "og-image.png")

W, H = 1200, 630
PAD = 64

BG = (15, 17, 19)
DOT = (27, 29, 31)
FG = (232, 230, 225)
FG2 = (180, 177, 170)
FG3 = (143, 149, 155)
BRASS = (217, 164, 65)
LINE = (40, 45, 51)
LINE2 = (59, 66, 73)
BG2 = (21, 24, 27)

SERIF = "/System/Library/Fonts/Supplemental/Georgia.ttf"
SERIF_B = "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"
SERIF_I = "/System/Library/Fonts/Supplemental/Georgia Italic.ttf"
SANS = "/System/Library/Fonts/SFNS.ttf"
SANS_B = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
MONO = "/System/Library/Fonts/Menlo.ttc"


def tracked(draw, xy, text, font, fill, tracking=0):
    """Draw with letter-spacing, since Pillow has no tracking."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + tracking
    return x


def rich_paragraph(d, xy, parts, fonts, fills, maxw, lead):
    """Wrap a run of (text, style_index) segments, keeping each word's style.
    The page sets Fablerift in italic; flattening it to roman would make the
    card read as a different document."""
    x0, y0 = xy
    x = x0
    line, line_w, y = [], 0.0, y0
    space = d.textlength(" ", font=fonts[0])

    def flush():
        nonlocal x, y, line, line_w
        x = x0
        for word, si in line:
            d.text((x, y), word, font=fonts[si], fill=fills[si])
            x += d.textlength(word, font=fonts[si]) + space
        y += lead
        line, line_w = [], 0.0

    for text, si in parts:
        for word in text.split():
            ww = d.textlength(word, font=fonts[si])
            if line and line_w + space + ww > maxw:
                flush()
            line.append((word, si))
            line_w += (space if line_w else 0.0) + ww
    if line:
        flush()
    return y


def main():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # the dot grid, fading out toward the right so it never competes with text
    for y in range(0, H, 26):
        for x in range(0, W, 26):
            d.point((x, y), fill=DOT)

    name_b = ImageFont.truetype(SERIF_B, 78)
    name_r = ImageFont.truetype(SERIF, 78)
    label = ImageFont.truetype(SANS_B, 19)
    pitch = ImageFont.truetype(SERIF, 25)
    pitch_i = ImageFont.truetype(SERIF_I, 25)
    mono = ImageFont.truetype(MONO, 17)
    mono_s = ImageFont.truetype(MONO, 15)
    cap = ImageFont.truetype(SANS, 15)

    left = PAD
    right_w = 440
    text_w = W - 2 * PAD - right_w - 44

    # --- name, split over two lines the way the masthead wraps on a phone ---
    y = 96
    d.text((left, y), "Enrico", font=name_b, fill=FG)
    y += 84
    d.text((left, y), "Sgiarovello", font=name_r, fill=FG)
    y += 96

    tracked(d, (left, y), "SOLO DEVELOPER  ·  C# / .NET  ·  UNITY", label, BRASS, tracking=2)
    y += 44

    parts = [
        ("I write the server, the clients, the launcher and the installer.", 1),
        ("Fablerift", 0),
        ("is the proof: a MUD you can start playing in about a minute.", 1),
    ]
    y = rich_paragraph(d, (left, y), parts,
                       fonts=(pitch_i, pitch), fills=(FG, FG2),
                       maxw=text_w, lead=38) + 30

    # --- the one line that tells a visitor where the rest lives ---
    rule_y = y
    d.line([(left, rule_y), (left + text_w, rule_y)], fill=LINE, width=1)
    y += 20
    # the repo list is 644px at 17px mono and the column only has 626, so the
    # detail line goes one size down rather than running under the plate
    bits = [
        ("Fablerift", "play.fablerift.net", mono),
        ("five repos", "linkcheck · tinysite · uptime · pr-guard · slidelimit", mono_s),
    ]
    for k, v, f in bits:
        d.text((left, y), k, font=f, fill=BRASS)
        x = left + d.textlength(k, font=f) + 14
        d.text((x, y), v, font=f, fill=FG3)
        y += 30

    # --- the capture, inset the way a plate is on the page ---
    shot_path = os.path.join(ROOT, "assets", "02-exploration.png")
    shot = Image.open(shot_path).convert("RGB")
    inner_w, inner_h = right_w - 22, 360
    scale = min(inner_w / shot.width, inner_h / shot.height)
    shot = shot.resize((round(shot.width * scale), round(shot.height * scale)), Image.LANCZOS)
    px = W - PAD - right_w + (right_w - shot.width) // 2
    py = 120 + (inner_h - shot.height) // 2
    box = (px - 11, py - 11, px + shot.width + 11, py + shot.height + 13)
    d.rectangle(box, fill=BG2, outline=LINE2, width=1)
    img.paste(shot, (px, py))
    d.text((box[0] + 1, box[3] + 12), "exploration · pinewood vale", font=cap, fill=FG3)

    # --- bottom rail ---
    d.line([(PAD, H - 74), (W - PAD, H - 74)], fill=LINE, width=1)
    d.text((PAD, H - 58), "sleepye5.github.io", font=mono, fill=FG3)
    tail = "updated 18 nov 2026"
    d.text((W - PAD - d.textlength(tail, font=mono), H - 58), tail, font=mono, fill=FG3)

    img.save(OUT, "PNG", optimize=True)
    print(f"wrote {OUT}  {os.path.getsize(OUT):,} bytes  {img.size}")


if __name__ == "__main__":
    main()
