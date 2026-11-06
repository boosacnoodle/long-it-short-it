#!/usr/bin/env python3
"""Build free promo assets for REKTcity - Long It Short It.

ffmpeg here has no drawtext filter, so all type is rendered with PIL into frame
images, then ffmpeg cuts them together with a crossfade and the master audio.

Outputs (in assets/):
  rektcity-vertical-15s.mp4   1080x1920, 15s, crossfaded beats, loudest part of master
  card-1-still-rekt.jpg       1080x1080 hook cards for X / IG
  card-2-down-bad.jpg
  card-3-the-trade.jpg
"""
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

D = Path(__file__).parent
ART = D / "art.jpg"
MASTER = Path.home() / "Downloads/Long It Short (Remix) (Remastered).wav"
FONT = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
INK = (245, 244, 241)
RED = (255, 46, 46)
DIM = (150, 154, 162)
BG = (7, 7, 8)

W, H = 1080, 1920


def font(size):
    return ImageFont.truetype(FONT, size)


def backdrop(w, h, art):
    """Blurred, darkened album art filling the frame."""
    im = art.copy()
    scale = max(w / im.width, h / im.height)
    im = im.resize((int(im.width * scale) + 1, int(im.height * scale) + 1), Image.Resampling.LANCZOS)
    left = (im.width - w) // 2
    top = (im.height - h) // 2
    im = im.crop((left, top, left + w, top + h))
    im = im.filter(ImageFilter.GaussianBlur(38))
    im = ImageEnhance.Brightness(im).enhance(0.42)
    im = ImageEnhance.Color(im).enhance(1.25)
    return im


def centre(draw, text, y, f, fill, tracking=0, box_w=W):
    if tracking:
        widths = [draw.textlength(c, font=f) for c in text]
        total = sum(widths) + tracking * (len(text) - 1)
        x = (box_w - total) / 2
        for c, cw in zip(text, widths):
            draw.text((x, y), c, font=f, fill=fill)
            x += cw + tracking
    else:
        tw = draw.textlength(text, font=f)
        draw.text(((box_w - tw) / 2, y), text, font=f, fill=fill)


def vertical_frame(art, label, head, sub, head_colour=INK, sub_colour=DIM, head_size=90):
    im = backdrop(W, H, art)
    card = art.resize((780, 780), Image.Resampling.LANCZOS)
    im.paste(card, (150, 470))
    d = ImageDraw.Draw(im)

    centre(d, label.upper(), 330, font(34), DIM, tracking=8)

    lines = head.split("\n")
    fs = head_size if max(len(l) for l in lines) <= 12 else int(head_size * 0.82)
    y = 1330 - (len(lines) - 1) * 40
    for line in lines:
        centre(d, line, y, font(fs), head_colour)
        y += fs + 16

    if sub:
        centre(d, sub, y + 18, font(40), DIM)
    return im


def square_frame(art, label, head, sub, head_size=150):
    S = 1080
    im = backdrop(S, S, art)
    card = art.resize((560, 560), Image.Resampling.LANCZOS)
    im.paste(card, (260, 70))
    d = ImageDraw.Draw(im)

    centre(d, label.upper(), 30, font(26), DIM, tracking=9, box_w=S)

    lines = head.split("\n")
    fs = head_size if max(len(l) for l in lines) <= 12 else int(head_size * 0.8)
    y = 700 - (len(lines) - 1) * 48
    for line in lines:
        centre(d, line, y, font(fs), INK, box_w=S)
        y += fs + 14

    centre(d, sub.upper(), 1000, font(30), RED, tracking=4, box_w=S)
    return im


def main():
    art = Image.open(ART).convert("RGB")

    beats = [
        ("rektcity", "BTC -5.4%\nETH -7.5%", "your portfolio: -100%"),
        ("rektcity", "Long it.\nShort it.", "either way you're paying"),
        ("rektcity", "Still rekt.", "long it short it - out now"),
    ]
    paths = []
    for i, (label, head, sub) in enumerate(beats, 1):
        col = RED if i == 1 else (INK if i == 2 else INK)
        p = D / f"beat{i}.png"
        vertical_frame(art, label, head, sub, head_colour=col).save(p, quality=95)
        paths.append(p)

    cmd = ["ffmpeg", "-y", "-v", "error"]
    for p in paths:
        cmd += ["-loop", "1", "-t", "5.4", "-i", str(p)]
    cmd += ["-ss", "80", "-t", "15", "-i", str(MASTER)]
    cmd += [
        "-filter_complex",
        "[0:v][1:v]xfade=transition=fade:duration=0.4:offset=5.0[a];"
        "[a][2:v]xfade=transition=fade:duration=0.4:offset=10.0[v];"
        "[v]format=yuv420p[vout];[3:a]afade=t=out:st=13.6:d=0.9[aout]",
        "-map", "[vout]", "-map", "[aout]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-r", "30",
        "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart",
        str(D / "rektcity-vertical-15s.mp4"),
    ]
    subprocess.run(cmd, check=True)
    print("video  ", (D / "rektcity-vertical-15s.mp4").stat().st_size // 1024, "KB")

    stills = [
        ("card-1-still-rekt.jpg", "rektcity", "Still rekt.", "long it short it - out now"),
        ("card-2-down-bad.jpg", "rektcity", "Down bad?", "same. put this on."),
        ("card-3-the-trade.jpg", "rektcity", "Long it.\nShort it.", "out now on spotify"),
    ]
    for name, label, head, sub in stills:
        square_frame(art, label, head, sub).save(D / name, quality=94)
        print("still  ", name)


if __name__ == "__main__":
    main()
