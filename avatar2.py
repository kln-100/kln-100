"""ASCII avatar v2 for kln-100: a security shield of glyphs with a script "K1" at its core."""
import math
import random
import sys

from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent

SIZE = 920  # 2x GitHub's 460px avatar, downscaled on save for crisp glyphs
GLYPH_FONT = str(HERE / "fonts/mono-bold.ttf")
SHAPE_FONT = str(HERE / "fonts/shape.ttf")
SHIELD = "--no-shield" not in sys.argv
OUT = str(HERE / "avatar2.png") if SHIELD else str(HERE / "avatar3.png")

COLS = 80
BG = (4, 4, 6)
RED = (225, 18, 45)
DEEP = (48, 6, 12)
WHITE = (255, 255, 255)


def shield_points(cx, cy, w, h, n=120):
    """Classic heater shield: flat-ish top with a soft dip, sides curving to a point."""
    pts = []
    top = cy - h / 2
    # flat top edge
    for i in range(n + 1):
        pts.append((cx - w / 2 + w * i / n, top))
    # right side: straight for the upper third, then curving in to the point
    side = []
    for i in range(1, n + 1):
        u = i / n
        s = max(0.0, (u - 0.3) / 0.7)
        side.append((cx + (w / 2) * (1 - s ** 1.7), top + h * u))
    pts += side
    pts += [(2 * cx - x, y) for x, y in reversed(side[:-1])]
    return pts


def mask_from(draw_fn):
    m = Image.new("L", (SIZE, SIZE), 0)
    draw_fn(ImageDraw.Draw(m))
    return m


shield = mask_from(lambda d: d.polygon(shield_points(SIZE / 2, SIZE / 2 + 10, SIZE * 0.58, SIZE * 0.68), fill=255))
inner = shield.filter(ImageFilter.MinFilter(35))  # erode → border band = shield - inner
border = ImageChops.subtract(shield, inner)
if not SHIELD:
    shield = inner = border = Image.new("L", (SIZE, SIZE), 0)

tfont = ImageFont.truetype(SHAPE_FONT, int(SIZE * 0.38))
def draw_text(d):
    l, t, r, b = d.textbbox((0, 0), "K1", font=tfont)
    d.text((SIZE / 2 - (r - l) / 2 - l, SIZE / 2 - (20 if SHIELD else 0) - (b - t) / 2 - t), "K1", fill=255, font=tfont)
text = mask_from(draw_text).filter(ImageFilter.MaxFilter(9))  # thicken thin script strokes
halo = text.filter(ImageFilter.MaxFilter(31))

# Glow behind border and text.
glow = ImageChops.lighter(border, text).filter(ImageFilter.GaussianBlur(SIZE * 0.03)).point(lambda v: int(v * 0.45))
img = Image.composite(Image.new("RGB", (SIZE, SIZE), RED), Image.new("RGB", (SIZE, SIZE), BG), glow)
draw = ImageDraw.Draw(img)

rng = random.Random("kln-100/v2")
step = SIZE / COLS
font = ImageFont.truetype(GLYPH_FONT, int(step * 1.15))
sy0, sy1 = SIZE / 2 + 10 - SIZE * 0.34, SIZE / 2 + 10 + SIZE * 0.34


def lerp(a, b, k):
    return tuple(int(x + (y - x) * k) for x, y in zip(a, b))


for y in range(COLS):
    for x in range(COLS):
        cx, cy = (x + 0.5) * step, (y + 0.5) * step
        p = (int(cx), int(cy))
        if text.getpixel(p) >= 128:
            k = min(max((cy - SIZE * 0.3) / (SIZE * 0.3), 0), 1) ** 2.2
            draw.text((cx, cy), rng.choice("@#%&$8B"), fill=lerp(WHITE, RED, k), font=font, anchor="mm")
        elif border.getpixel(p) >= 128:
            k = min(max((cy - sy0) / (sy1 - sy0), 0), 1) ** 1.5
            draw.text((cx, cy), rng.choice("#%&@"), fill=lerp(RED, DEEP, k * 0.5), font=font, anchor="mm")
        elif inner.getpixel(p) >= 128 and halo.getpixel(p) < 128 and rng.random() < 0.45:
            draw.text((cx, cy), rng.choice("01"), fill=DEEP, font=font, anchor="mm")

img.resize((460, 460), Image.LANCZOS).save(OUT, optimize=True)
