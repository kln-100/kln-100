"""Profile banner for kln-100: ASCII script "K1" + terminal-style title, matching the avatars."""
import random

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent

W, H = 2560, 640  # 2x of 1280x320, downscaled on save
MONO = str(HERE / "fonts/mono-bold.ttf")
MONO_REG = str(HERE / "fonts/mono-regular.ttf")
SCRIPT = str(HERE / "fonts/shape.ttf")
OUT = str(HERE / "assets/banner.png")

BG = (4, 4, 6)
RED = (225, 18, 45)
DEEP = (42, 6, 11)
WHITE = (255, 255, 255)
GREY = (150, 150, 158)
STEP = 22  # px per ASCII cell


def lerp(a, b, k):
    return tuple(int(x + (y - x) * k) for x, y in zip(a, b))


# K1 mask on the left third.
mask = Image.new("L", (W, H), 0)
md = ImageDraw.Draw(mask)
sfont = ImageFont.truetype(SCRIPT, int(H * 0.78))
l, t, r, b = md.textbbox((0, 0), "K1", font=sfont)
kx, ky = int(W * 0.17) - (r - l) // 2 - l, H // 2 - (b - t) // 2 - t
md.text((kx, ky), "K1", fill=255, font=sfont)
mask = mask.filter(ImageFilter.MaxFilter(11))
top, bottom = ky + t, ky + b
halo = mask.filter(ImageFilter.MaxFilter(41))

glow = mask.filter(ImageFilter.GaussianBlur(40)).point(lambda v: int(v * 0.5))
img = Image.composite(Image.new("RGB", (W, H), RED), Image.new("RGB", (W, H), BG), glow)
draw = ImageDraw.Draw(img)

rng = random.Random("kln-100/banner")
gfont = ImageFont.truetype(MONO, int(STEP * 1.15))
text_x = int(W * 0.36)  # binary rain fades out before the title column

for y in range(H // STEP):
    for x in range(W // STEP):
        cx, cy = (x + 0.5) * STEP, (y + 0.5) * STEP
        if mask.getpixel((int(cx), int(cy))) >= 128:
            k = min(max((cy - top) / (bottom - top), 0), 1) ** 2.2
            draw.text((cx, cy), rng.choice("@#%&$8B"), fill=lerp(WHITE, RED, k), font=gfont, anchor="mm")
        elif halo.getpixel((int(cx), int(cy))) < 128:
            # faint binary field, denser on the far left and right edges
            edge = max(1 - cx / text_x, (cx - W * 0.82) / (W * 0.18), 0)
            if rng.random() < 0.08 + 0.4 * edge:
                draw.text((cx, cy), rng.choice("01"), fill=lerp(BG, DEEP, 0.4 + 0.6 * edge), font=gfont, anchor="mm")

# Title block.
title = ImageFont.truetype(MONO, 150)
sub = ImageFont.truetype(MONO_REG, 54)
draw.text((text_x, H * 0.24), "~/", fill=RED, font=title)
tw = draw.textlength("~/", font=title)
draw.text((text_x + tw, H * 0.24), "k100", fill=WHITE, font=title)
cursor_x = text_x + tw + draw.textlength("k100", font=title) + 18
draw.rectangle((cursor_x, H * 0.24 + 30, cursor_x + 70, H * 0.24 + 180), fill=RED)

line_y = H * 0.62
draw.text((text_x, line_y), "$", fill=RED, font=sub)
draw.text((text_x + 60, line_y), "cloud security", fill=WHITE, font=sub)
x = text_x + 60 + draw.textlength("cloud security", font=sub)
for word in ("siem", "web dev"):
    draw.text((x, line_y), "  ·  ", fill=RED, font=sub)
    x += draw.textlength("  ·  ", font=sub)
    draw.text((x, line_y), word, fill=WHITE, font=sub)
    x += draw.textlength(word, font=sub)

# Thin red rule along the bottom.
draw.rectangle((0, H - 6, W, H), fill=RED)

img.resize((W // 2, H // 2), Image.LANCZOS).save(OUT, optimize=True)
