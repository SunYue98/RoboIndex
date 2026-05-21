#!/usr/bin/env python3
"""Generate synthetic title-card placeholders for entries lacking imageUrl.

Per IMAGE_SPEC.md prototype B: a 1000×1000 PNG with category-colored gradient,
big entity name, company subtitle, year+category meta corner. Writes to
public/images/_synthetic/<entity-id>.png so EntityCard.tsx can fall back when
entity.imageUrl is empty.

Skips entities that already have:
  - a non-empty imageUrl in JSON, OR
  - an existing file at the synthetic output path
so manually-collected images and prior runs are never overwritten.

Usage:
  python3 research/_tools/generate_synthetic_cards.py [--force]
"""
import argparse
import json
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("FATAL: Pillow not installed. Run: pip install Pillow")
    raise SystemExit(1)

ROOT = Path(__file__).resolve().parents[2]
PUBLIC = ROOT / "public/data"
OUTPUT_DIR = ROOT / "public/images/_synthetic"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Category gradient color pairs (top-left → bottom-right) — RGB tuples
CATEGORY_GRADIENT = {
    # 硬件 — warm metal/industrial tones
    "整机平台":     ((58, 65, 80),   (118, 130, 150)),   # slate
    "灵巧手 & 夹爪": ((90, 70, 50),   (155, 130, 105)),   # bronze
    "机械臂":       ((50, 75, 100),  (110, 145, 175)),   # steel blue
    "关节模组":     ((75, 65, 90),   (140, 125, 165)),   # mauve
    "核心零部件":   ((65, 70, 75),   (130, 140, 150)),   # charcoal
    "传感器":       ((50, 95, 110),  (110, 165, 185)),   # teal
    "计算平台":     ((50, 85, 70),   (105, 155, 130)),   # sage
    "能源动力":     ((90, 80, 50),   (160, 145, 100)),   # amber
    "数采 & 遥操":   ((85, 60, 90),   (150, 115, 160)),   # plum
    # 软件 — vibrant, per IMAGE_SPEC
    "基础模型":     ((35, 50, 110),  (90, 60, 145)),     # deep blue → purple
    "算法框架":     ((30, 85, 75),   (60, 140, 130)),    # dark green → teal
    "控制算法":     ((130, 75, 45),  (175, 95, 70)),     # orange → red
    "仿真平台":     ((90, 45, 110),  (165, 90, 145)),    # deep purple → pink
    "数据集":       ((65, 70, 85),   (120, 130, 150)),   # gray → blue-gray
    "评测基准":     ((130, 105, 55), (170, 140, 85)),    # yellow → brown
    # 生态与应用
    "开发生态":     ((40, 95, 100),  (75, 150, 135)),    # cyan → green
    "应用场景":     ((75, 55, 45),   (140, 105, 85)),    # earth
    # 参与实体
    "产业":         ((45, 55, 75),   (95, 110, 140)),    # corporate slate
    "资本":         ((90, 75, 45),   (150, 125, 80)),    # gold (capital theme)
    "实验室":       ((55, 75, 95),   (105, 140, 170)),   # academic blue
    "人物":         ((75, 65, 90),   (145, 120, 165)),   # warm violet (people)
}
DEFAULT_GRADIENT = ((60, 60, 70), (130, 130, 140))

# Font discovery — prefer CJK-capable fonts for the many Chinese entity names
FONT_CANDIDATES = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Medium.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc",
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
]

def find_font():
    for p in FONT_CANDIDATES:
        if Path(p).exists():
            return p
    raise RuntimeError("No CJK font found; checked: " + ", ".join(FONT_CANDIDATES))

FONT_PATH = find_font()


def make_gradient(size, c1, c2):
    """Diagonal gradient from c1 (top-left) to c2 (bottom-right)."""
    base = Image.new("RGB", size, c1)
    top = Image.new("RGB", size, c2)
    # Linear gradient mask
    mask = Image.new("L", size)
    for y in range(size[1]):
        for x in range(size[0]):
            mask.putpixel((x, y), int(255 * (x + y) / (size[0] + size[1] - 2)))
    base.paste(top, (0, 0), mask)
    return base


def make_gradient_fast(size, c1, c2):
    """Vectorized version using numpy if available; falls back to make_gradient."""
    try:
        import numpy as np
        w, h = size
        xs = np.arange(w).reshape(1, w).repeat(h, axis=0)
        ys = np.arange(h).reshape(h, 1).repeat(w, axis=1)
        t = (xs + ys) / (w + h - 2)
        r = (c1[0] * (1 - t) + c2[0] * t).astype("uint8")
        g = (c1[1] * (1 - t) + c2[1] * t).astype("uint8")
        b = (c1[2] * (1 - t) + c2[2] * t).astype("uint8")
        arr = np.stack([r, g, b], axis=-1)
        return Image.fromarray(arr, "RGB")
    except ImportError:
        return make_gradient(size, c1, c2)


def wrap_text(text, font, max_width, draw):
    """Break a long string into multiple lines that fit max_width."""
    if not text:
        return []
    # Try as one line first
    bbox = draw.textbbox((0, 0), text, font=font)
    if bbox[2] - bbox[0] <= max_width:
        return [text]
    # Greedy wrap by character (CJK-friendly)
    lines = []
    current = ""
    for ch in text:
        candidate = current + ch
        bbox = draw.textbbox((0, 0), candidate, font=font)
        if bbox[2] - bbox[0] > max_width and current:
            lines.append(current)
            current = ch
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def draw_centered_text(draw, lines, font, y_start, color, size_w, line_spacing=8):
    """Draw multiple lines centered horizontally, return y after last line."""
    y = y_start
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        x = (size_w - w) // 2
        # Subtle shadow for readability
        draw.text((x + 2, y + 2), line, font=font, fill=(0, 0, 0, 80))
        draw.text((x, y), line, font=font, fill=color)
        y += h + line_spacing
    return y


def render_card(entity, out_path):
    size = (1000, 1000)
    category = entity.get("category", "")
    gradient = CATEGORY_GRADIENT.get(category, DEFAULT_GRADIENT)

    img = make_gradient_fast(size, *gradient)
    draw = ImageDraw.Draw(img, "RGBA")

    title = entity.get("name", "Untitled")
    subtitle = entity.get("company", "")
    year = entity.get("year", "")
    meta_left = f"{year} · {category}" if year else category

    # Fonts — sized for 1000x1000
    title_font = ImageFont.truetype(FONT_PATH, 72)
    subtitle_font = ImageFont.truetype(FONT_PATH, 36)
    meta_font = ImageFont.truetype(FONT_PATH, 26)

    inner_w = 880  # 60px padding each side
    inner_x = (size[0] - inner_w) // 2

    # Title — wrap to up to 3 lines, shrink if needed
    title_lines = wrap_text(title, title_font, inner_w, draw)
    if len(title_lines) > 3:
        # Try smaller font
        title_font = ImageFont.truetype(FONT_PATH, 56)
        title_lines = wrap_text(title, title_font, inner_w, draw)
        title_lines = title_lines[:3]
        if len(title_lines) == 3 and len(title) > sum(len(l) for l in title_lines):
            title_lines[-1] = title_lines[-1][:-1] + "…"

    # Subtitle — wrap to 2 lines
    subtitle_lines = wrap_text(subtitle, subtitle_font, inner_w, draw)[:2]

    # Vertical centering: figure out total block height, place starting y
    title_h = sum(
        draw.textbbox((0, 0), l, font=title_font)[3] - draw.textbbox((0, 0), l, font=title_font)[1]
        for l in title_lines
    ) + 8 * (len(title_lines) - 1)
    subtitle_h = sum(
        draw.textbbox((0, 0), l, font=subtitle_font)[3] - draw.textbbox((0, 0), l, font=subtitle_font)[1]
        for l in subtitle_lines
    ) + 8 * (max(0, len(subtitle_lines) - 1))
    gap = 40 if subtitle_lines else 0
    block_h = title_h + gap + subtitle_h
    y0 = (size[1] - block_h) // 2 - 20  # nudge up to leave room for meta

    y = draw_centered_text(draw, title_lines, title_font, y0, (255, 255, 255), size[0])
    if subtitle_lines:
        y += gap - 8
        draw_centered_text(draw, subtitle_lines, subtitle_font, y, (255, 255, 255, 220), size[0])

    # Meta bottom-left
    draw.text((60 + 1, size[1] - 80 + 1), meta_left, font=meta_font, fill=(0, 0, 0, 100))
    draw.text((60, size[1] - 80), meta_left, font=meta_font, fill=(255, 255, 255, 230))

    img.save(out_path, "PNG", optimize=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true",
                    help="Regenerate even if synthetic file already exists")
    args = ap.parse_args()

    partitions = ["hardware", "software", "ecosystem", "players"]
    total_entities = 0
    needs_synthetic = 0
    generated = 0
    skipped_existing_file = 0
    skipped_has_imageUrl = 0

    for p in partitions:
        entries = json.loads((PUBLIC / f"{p}.json").read_text(encoding="utf-8"))
        for e in entries:
            total_entities += 1
            if e.get("imageUrl"):
                skipped_has_imageUrl += 1
                continue
            needs_synthetic += 1
            out = OUTPUT_DIR / f"{e['id']}.png"
            if out.exists() and not args.force:
                skipped_existing_file += 1
                continue
            try:
                render_card(e, out)
                generated += 1
            except Exception as exc:
                print(f"  FAILED {e['id']}: {exc}")

    print(f"=== generate_synthetic_cards.py ===")
    print(f"Total entities: {total_entities}")
    print(f"  Has real imageUrl, skipped: {skipped_has_imageUrl}")
    print(f"  Needs synthetic placeholder: {needs_synthetic}")
    print(f"    Already generated, skipped: {skipped_existing_file}")
    print(f"    Newly generated this run: {generated}")
    print(f"\nOutput: {OUTPUT_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
