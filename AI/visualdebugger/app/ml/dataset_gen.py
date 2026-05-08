"""
Synthetic dataset generator.
Creates "buggy" and "clean" UI screenshots using Pillow.
Saves to ml_experiments/data/raw/{buggy|clean}/

Usage:
    python -m app.ml.dataset_gen --n 500 --out ml_experiments/data/raw
"""
import os
import random
import argparse
import uuid
from PIL import Image, ImageDraw, ImageFont

# ── Color palettes ────────────────────────────────────────────────────────────
CLEAN_BG  = [(245, 247, 250), (255, 255, 255), (240, 242, 245)]
CLEAN_ACC = [(63, 131, 248), (16, 185, 129), (139, 92, 246)]
BUG_COLORS = [(255, 0, 0), (255, 165, 0), (200, 0, 200)]


def _draw_clean_ui(draw: ImageDraw.Draw, w: int, h: int):
    """Render a well-structured UI layout."""
    # Header
    header_col = random.choice([(30, 41, 59), (17, 24, 39)])
    draw.rectangle([0, 0, w, 60], fill=header_col)
    # Nav items
    for i in range(4):
        draw.rectangle([20 + i * 120, 20, 110 + i * 120, 45], fill=(255, 255, 255, 80))
    # Card grid
    card_col = random.choice([(255, 255, 255), (248, 250, 252)])
    for row in range(3):
        for col in range(3):
            x0 = 20 + col * 200
            y0 = 80 + row * 160
            draw.rounded_rectangle([x0, y0, x0 + 180, y0 + 140], radius=10, fill=card_col,
                                    outline=(226, 232, 240), width=1)
    # Footer
    draw.rectangle([0, h - 60, w, h], fill=header_col)


def _draw_buggy_ui(draw: ImageDraw.Draw, w: int, h: int, bug_type: str):
    """Render a UI with a specific visual bug."""
    _draw_clean_ui(draw, w, h)  # base layout

    if bug_type == "overlap":
        # Two overlapping elements
        draw.rectangle([100, 150, 350, 300], fill=(255, 200, 200))
        draw.rectangle([180, 200, 420, 350], fill=(200, 200, 255))

    elif bug_type == "layout":
        # Element outside its container
        draw.rectangle([w - 50, 90, w + 100, 200], fill=(255, 100, 100))

    elif bug_type == "color":
        # Low contrast text (light gray on white)
        draw.rectangle([20, 90, 200, 130], fill=(245, 245, 245))
        draw.text((30, 100), "Invisible text", fill=(220, 220, 220))

    elif bug_type == "missing":
        # Blank expected area
        draw.rectangle([20, 90, 200, 220], fill=(230, 230, 230))
        draw.line([20, 90, 200, 220], fill=(200, 200, 200), width=2)
        draw.line([200, 90, 20, 220], fill=(200, 200, 200), width=2)

    elif bug_type == "alignment":
        # Randomly shifted elements
        for i in range(4):
            offset = random.randint(5, 40)
            draw.rectangle([20 + i * 120 + offset, 20, 110 + i * 120 + offset, 45],
                           fill=(150, 200, 255))

    elif bug_type == "contrast":
        # Yellow text on white — bad contrast
        draw.rectangle([20, 90, 400, 170], fill=(255, 255, 255))
        draw.text((30, 110), "Poor contrast heading", fill=(200, 200, 50))


def generate_dataset(n_per_class: int, output_dir: str):
    """Generate clean and buggy UI images."""
    BUG_TYPES = ["overlap", "layout", "color", "missing", "alignment", "contrast"]
    W, H = 640, 480

    clean_dir = os.path.join(output_dir, "clean")
    os.makedirs(clean_dir, exist_ok=True)

    print(f"Generating {n_per_class} clean images…")
    for _ in range(n_per_class):
        img = Image.new("RGB", (W, H), color=random.choice(CLEAN_BG))
        draw = ImageDraw.Draw(img)
        _draw_clean_ui(draw, W, H)
        img.save(os.path.join(clean_dir, f"clean_{uuid.uuid4().hex[:8]}.png"))

    for bug_type in BUG_TYPES:
        bug_dir = os.path.join(output_dir, bug_type)
        os.makedirs(bug_dir, exist_ok=True)
        print(f"Generating {n_per_class} {bug_type} images…")
        for _ in range(n_per_class):
            img = Image.new("RGB", (W, H), color=random.choice(CLEAN_BG))
            draw = ImageDraw.Draw(img)
            _draw_buggy_ui(draw, W, H, bug_type)
            img.save(os.path.join(bug_dir, f"{bug_type}_{uuid.uuid4().hex[:8]}.png"))

    print(f"✓ Dataset generated at {output_dir}")
    print(f"  Classes: clean + {', '.join(BUG_TYPES)}")
    print(f"  Total images: {n_per_class * (len(BUG_TYPES) + 1)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate synthetic UI bug dataset")
    parser.add_argument("--n",   type=int, default=200, help="Images per class")
    parser.add_argument("--out", default="ml_experiments/data/raw", help="Output directory")
    args = parser.parse_args()
    generate_dataset(args.n, args.out)
