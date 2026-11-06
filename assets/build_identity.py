#!/usr/bin/env python3
"""REKTcity brand kit: avatars + platform banners rendered from the album art.

Sizes follow each platform's current spec:
  avatar       1000x1000 (works scaled to 400 / 320 / 200 everywhere)
  x banner     1500x500
  youtube      2560x1440 with the 1546x423 safe area respected
  ig story     1080x1920 (profile card / first post)
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

D = Path(__file__).parent
ART = D / "art.jpg"
FONT = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
INK = (245, 244, 241)
RED = (255, 46, 46)
DIM = (150, 154, 162)


def f(size):
    return ImageFont.truetype(FONT, size)


def cover(im, w, h):
    s = max(w / im.width, h / im.height)
    im = im.resize((int(im.width * s) + 1, int(im.height * s) + 1), Image.Resampling.LANCZOS)
    l = (im.width - w) // 2
    t = (im.height - h) // 2
    return im.crop((l, t, l + w, t + h))


def backdrop(art, w, h, blur=40, bright=0.42):
    im = cover(art, w, h).filter(ImageFilter.GaussianBlur(blur))
    im = ImageEnhance.Brightness(im).enhance(bright)
    return ImageEnhance.Color(im).enhance(1.25)


def centre(d, text, y, font, fill, tracking=0, box_w=1000):
    if tracking:
        ws = [d.textlength(c, font=font) for c in text]
        total = sum(ws) + tracking * (len(text) - 1)
        x = (box_w - total) / 2
        for c, w in zip(text, ws):
            d.text((x, y), c, font=font, fill=fill)
            x += w + tracking
    else:
        d.text(((box_w - d.textlength(text, font=font)) / 2, y), text, font=font, fill=fill)


def avatar(art):
    im = cover(art, 1000, 1000)
    # subtle vignette so it reads as a logo at 40px
    mask = Image.new("L", (1000, 1000), 0)
    md = ImageDraw.Draw(mask)
    md.ellipse((-140, -140, 1140, 1140), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(60))
    dark = ImageEnhance.Brightness(im).enhance(0.35)
    im = Image.composite(im, dark, mask)
    return im


def x_banner(art):
    W, H = 1500, 500
    im = backdrop(art, W, H, blur=44, bright=0.34)
    # album art on the right: the avatar sits bottom-left on profile pages
    card = art.resize((380, 380), Image.Resampling.LANCZOS)
    im.paste(card, (1050, 60))
    d = ImageDraw.Draw(im)
    d.text((96, 148), "REKTCITY", font=f(88), fill=INK)
    d.text((100, 258), "LONG IT SHORT IT  -  OUT NOW", font=f(30), fill=RED)
    d.text((100, 312), "long it. short it. still rekt.", font=f(26), fill=DIM)
    return im


def youtube_banner(art):
    W, H = 2560, 1440
    im = backdrop(art, W, H, blur=60, bright=0.32)
    d = ImageDraw.Draw(im)
    # keep type inside the 1546x423 centre safe area
    centre(d, "REKTCITY", 600, f(120), INK, tracking=16, box_w=W)
    centre(d, "LONG IT SHORT IT  —  OUT NOW", 760, f(44), RED, tracking=8, box_w=W)
    return im


def story(art):
    W, H = 1080, 1920
    im = backdrop(art, W, H, blur=42, bright=0.4)
    card = art.resize((860, 860), Image.Resampling.LANCZOS)
    im.paste(card, (110, 430))
    d = ImageDraw.Draw(im)
    centre(d, "REKTCITY", 300, f(46), INK, tracking=12, box_w=W)
    centre(d, "LONG IT SHORT IT", 1360, f(74), INK, box_w=W)
    centre(d, "OUT NOW ON SPOTIFY", 1470, f(32), RED, tracking=6, box_w=W)
    return im


def main():
    art = Image.open(ART).convert("RGB")
    out = {
        "avatar-1000.png": avatar(art),
        "banner-x-1500x500.png": x_banner(art),
        "banner-youtube-2560x1440.png": youtube_banner(art),
        "story-1080x1920.png": story(art),
    }
    for name, im in out.items():
        im.save(D / name)
        print(f"  {name}  {im.size[0]}x{im.size[1]}  {(D / name).stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
