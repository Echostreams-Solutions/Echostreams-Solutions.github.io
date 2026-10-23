"""Create 1200x630 share images (assets/img/og/<product-slug>.jpg) from each product's first image.

The product PNGs are up to ~6 MB, too large for social previews (Twitter/X limit 5 MB), so previews use these
small JPEGs instead. Run before scripts/import_products.py:  python scripts/make_og_images.py   (needs Pillow)
"""
import json, re
from pathlib import Path
from PIL import Image

SITE = Path(__file__).resolve().parent.parent
OUT = SITE / "assets" / "img" / "og"
OUT.mkdir(parents=True, exist_ok=True)
W, H, PAD = 1200, 630, 60
made = 0
for f in sorted((SITE / "_products").glob("*.md")):
    t = f.read_text(encoding="utf-8")
    m = re.search(r'^image: (".*")$', t, re.M)
    if not m or f.name.startswith("example"):
        continue
    src = SITE / json.loads(m.group(1)).lstrip("/")
    if src.suffix.lower() not in (".png", ".jpg", ".jpeg", ".webp") or not src.exists():
        continue
    im = Image.open(src).convert("RGBA")
    bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
    im = Image.alpha_composite(bg, im).convert("RGB")
    im.thumbnail((W - 2 * PAD, H - 2 * PAD), Image.LANCZOS)
    canvas = Image.new("RGB", (W, H), (255, 255, 255))
    canvas.paste(im, ((W - im.width) // 2, (H - im.height) // 2))
    canvas.save(OUT / (f.stem + ".jpg"), "JPEG", quality=84, optimize=True)
    made += 1
print(f"wrote {made} share images to {OUT}")
