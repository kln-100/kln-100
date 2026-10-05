"""ASCII avatar for kln-100: "K1" in a script font drawn with glyphs, red→white gradient on black."""
import random
import sys

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent

SIZE = 920  # 2x GitHub's 460px avatar, downscaled on save for crisp glyphs
GLYPH_FONT = str(HERE / "fonts/mono-bold.ttf")
SHAPE_FONT = sys.argv[1] if len(sys.argv) > 1 else str(HERE / "fonts/shape.ttf")
OUT = sys.argv[2] if len(sys.argv) > 2 else str(HERE / "avatar.png")

COLS = 86  # ASCII characters per side
TEXT = "K1"
TEXT_SCALE = 0.55
BG = (0, 0, 0)
RED = (225, 18, 45)
WHITE = (255, 255, 255)

# Mask: render TEXT large in the shape font, then sample it once per character cell.
mask = Image.new("L", (SIZE, SIZE), 0)
mdraw = ImageDraw.Draw(mask)
mfont = ImageFont.truetype(SHAPE_FONT, int(SIZE * TEXT_SCALE))
l, t, r, b = mdraw.textbbox((0, 0), TEXT, font=mfont)
mdraw.text(((SIZE - (r - l)) / 2 - l, (SIZE - (b - t)) / 2 - t), TEXT, fill=255, font=mfont)

# Soft red glow behind the letters.
glow = mask.filter(ImageFilter.GaussianBlur(SIZE * 0.035)).point(lambda v: int(v * 0.35))
img = Image.composite(Image.new("RGB", (SIZE, SIZE), RED), Image.new("RGB", (SIZE, SIZE), BG), glow)

rng = random.Random("kln-100")
step = SIZE / COLS
font = ImageFont.truetype(GLYPH_FONT, int(step * 1.15))
draw = ImageDraw.Draw(img)
dense = "@#%&$8B"
top, bottom = (SIZE - (b - t)) / 2, (SIZE + (b - t)) / 2

for y in range(COLS):
    for x in range(COLS):
        cx, cy = (x + 0.5) * step, (y + 0.5) * step
        if mask.getpixel((int(cx), int(cy))) < 128:
            continue
        k = min(max((cy - top) / (bottom - top), 0), 1)  # 0 = top (red), 1 = bottom (white)
        k = k ** 1.6  # keep most of the letters red, whiten toward the base
        color = tuple(int(a + (z - a) * k) for a, z in zip(RED, WHITE))
        draw.text((cx, cy), rng.choice(dense), fill=color, font=font, anchor="mm")

img.resize((460, 460), Image.LANCZOS).save(OUT, optimize=True)
