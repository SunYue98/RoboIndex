#!/usr/bin/env python3
"""Process raw collected images into the IMAGE_SPEC.md standard.

Pipeline per image:
  1. (optional) Background removal via rembg → solid white or transparent
  2. Crop to 1:1 around the subject's bounding box (uses alpha if available, else center)
  3. Resize to 1000×1000 (LANCZOS)
  4. Save as JPG (≤200KB) or PNG (≤400KB) by compressing iteratively

Output destination: public/images/<partition>/<entity-id>.{jpg|png}
The partition is resolved from public/data/*.json by entity id.

Usage:
  # Single image, entity ID supplied → resolves output path automatically
  python3 research/_tools/process_image.py raw.jpg --entity ind-figure

  # With background removal (requires `pip install rembg`)
  python3 research/_tools/process_image.py raw.jpg --entity ind-figure --remove-bg

  # Force PNG (for logos with transparency)
  python3 research/_tools/process_image.py raw.png --entity stg-vc-msft --format png --remove-bg

  # Batch a folder where each filename matches an entity ID
  python3 research/_tools/process_image.py raw_dir/ --batch

  # Explicit output path override
  python3 research/_tools/process_image.py raw.jpg --out public/images/hardware/custom.jpg
"""
import argparse
import json
import sys
from pathlib import Path
from typing import Optional, Tuple

try:
    from PIL import Image
except ImportError:
    print("FATAL: Pillow not installed. Run: pip install Pillow")
    sys.exit(1)

ROOT = Path(__file__).resolve().parents[2]
PUBLIC = ROOT / "public"
DATA = PUBLIC / "data"
PARTITIONS = ["hardware", "software", "ecosystem", "players"]

# JPG size cap (KB), PNG size cap (KB) — from IMAGE_SPEC.md
JPG_CAP_KB = 200
PNG_CAP_KB = 400
TARGET_SIZE = 1000


def load_entity_index() -> dict:
    """Build entity_id → partition mapping."""
    index = {}
    for p in PARTITIONS:
        for e in json.loads((DATA / f"{p}.json").read_text(encoding="utf-8")):
            index[e["id"]] = p
    return index


def remove_bg(img: Image.Image) -> Image.Image:
    """Run rembg to get RGBA with alpha; return RGBA."""
    try:
        from rembg import remove
    except ImportError:
        raise RuntimeError(
            "rembg not installed. Run: pip install rembg\n"
            "(first run will download ~170MB U2Net model)"
        )
    img_rgba = remove(img)  # rembg returns PIL.Image RGBA
    return img_rgba.convert("RGBA")


def alpha_bbox(img: Image.Image) -> Optional[Tuple[int, int, int, int]]:
    """Tight bbox of non-transparent pixels, or None if no alpha."""
    if img.mode != "RGBA":
        return None
    alpha = img.split()[3]
    return alpha.getbbox()


def crop_to_square(img: Image.Image, padding_ratio: float = 0.08) -> Image.Image:
    """Crop image to 1:1.

    If alpha-aware bbox is available, center on subject with padding.
    Otherwise, center-crop on the image's middle.
    """
    bbox = alpha_bbox(img) if img.mode == "RGBA" else None
    w, h = img.size

    if bbox:
        # Center on subject bbox
        bx, by, bx2, by2 = bbox
        cx, cy = (bx + bx2) // 2, (by + by2) // 2
        bw, bh = bx2 - bx, by2 - by
        # Side of square = longest subject dim + padding
        side = int(max(bw, bh) * (1 + 2 * padding_ratio))
        side = max(side, 200)  # don't go absurdly small
        side = min(side, min(w, h))  # don't exceed image
    else:
        # Center crop
        side = min(w, h)
        cx, cy = w // 2, h // 2

    half = side // 2
    left = max(0, cx - half)
    top = max(0, cy - half)
    right = left + side
    bottom = top + side
    # Push back into image bounds
    if right > w:
        left -= right - w
        right = w
    if bottom > h:
        top -= bottom - h
        bottom = h
    left = max(0, left)
    top = max(0, top)
    return img.crop((left, top, right, bottom))


def composite_white_bg(img: Image.Image) -> Image.Image:
    """Flatten RGBA onto white background (for JPG output of rembg result)."""
    if img.mode != "RGBA":
        return img.convert("RGB")
    bg = Image.new("RGB", img.size, (255, 255, 255))
    bg.paste(img, mask=img.split()[3])
    return bg


def save_compressed(img: Image.Image, out_path: Path, fmt: str):
    """Save with iterative quality reduction to hit size cap."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if fmt.lower() == "jpg":
        cap_bytes = JPG_CAP_KB * 1024
        # Try qualities 90, 85, 80, ... down to 60
        for q in [92, 88, 84, 80, 76, 72, 68, 64, 60]:
            img.save(out_path, "JPEG", quality=q, optimize=True, progressive=True)
            if out_path.stat().st_size <= cap_bytes:
                return q
        return 60
    elif fmt.lower() == "png":
        img.save(out_path, "PNG", optimize=True)
        # PNG has fewer quality knobs; the optimize flag does most of it
        sz = out_path.stat().st_size
        if sz > PNG_CAP_KB * 1024:
            print(f"  WARN: {out_path.name} is {sz//1024}KB (cap {PNG_CAP_KB}KB) — consider running through oxipng")
        return None
    else:
        raise ValueError(f"Unknown format: {fmt}")


def process_one(
    in_path: Path,
    out_path: Path,
    fmt: str,
    do_remove_bg: bool,
) -> dict:
    """Process a single image; return summary dict."""
    img = Image.open(in_path)
    # Always work in RGB(A) — drop palette / CMYK
    if img.mode == "P":
        img = img.convert("RGBA" if "transparency" in img.info else "RGB")
    elif img.mode == "CMYK":
        img = img.convert("RGB")

    bg_removed = False
    if do_remove_bg:
        img = remove_bg(img)
        bg_removed = True

    img = crop_to_square(img)
    img = img.resize((TARGET_SIZE, TARGET_SIZE), Image.LANCZOS)

    # If output is JPG, flatten any alpha onto white
    if fmt.lower() == "jpg":
        img = composite_white_bg(img)

    quality = save_compressed(img, out_path, fmt)
    return {
        "in": str(in_path),
        "out": str(out_path),
        "format": fmt,
        "bg_removed": bg_removed,
        "size_kb": out_path.stat().st_size // 1024,
        "quality": quality,
    }


def resolve_output(entity_id: str, fmt: str, entity_index: dict) -> Path:
    partition = entity_index.get(entity_id)
    if not partition:
        raise ValueError(
            f"Entity id {entity_id!r} not found in any partition. "
            f"Known partitions: {PARTITIONS}"
        )
    return PUBLIC / "images" / partition / f"{entity_id}.{fmt}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", help="Path to raw image file, or directory if --batch")
    ap.add_argument("--entity", help="Entity ID (resolves output partition automatically)")
    ap.add_argument("--out", help="Explicit output path (overrides --entity resolution)")
    ap.add_argument("--format", default="jpg", choices=["jpg", "png"], help="Output format (default: jpg)")
    ap.add_argument("--remove-bg", action="store_true", help="Run rembg to isolate the subject")
    ap.add_argument("--batch", action="store_true",
                    help="Treat input as directory; each file's stem must match an entity ID")
    ap.add_argument("--force", action="store_true", help="Overwrite existing output")
    args = ap.parse_args()

    in_path = Path(args.input)
    if not in_path.exists():
        print(f"FATAL: {in_path} does not exist")
        sys.exit(1)

    entity_index = load_entity_index()

    # Build list of (in_path, out_path) jobs
    jobs = []
    if args.batch:
        if not in_path.is_dir():
            print(f"FATAL: --batch requires a directory; got {in_path}")
            sys.exit(1)
        for f in sorted(in_path.iterdir()):
            if f.suffix.lower() not in (".jpg", ".jpeg", ".png", ".webp", ".gif"):
                continue
            eid = f.stem
            if eid not in entity_index:
                print(f"  SKIP {f.name}: stem {eid!r} not in any partition")
                continue
            out = resolve_output(eid, args.format, entity_index)
            jobs.append((f, out, eid))
    else:
        if args.out:
            out = Path(args.out)
            eid = None
        elif args.entity:
            out = resolve_output(args.entity, args.format, entity_index)
            eid = args.entity
        else:
            print("FATAL: must supply --entity or --out (or use --batch)")
            sys.exit(1)
        jobs.append((in_path, out, eid))

    # Process
    results = []
    skipped = 0
    for src, dst, eid in jobs:
        if dst.exists() and not args.force:
            print(f"  SKIP {dst.relative_to(ROOT)} (exists; use --force to overwrite)")
            skipped += 1
            continue
        try:
            r = process_one(src, dst, args.format, args.remove_bg)
            results.append(r)
            tag = f" [bg removed]" if r["bg_removed"] else ""
            q = f" q={r['quality']}" if r["quality"] is not None else ""
            print(f"  ✓ {src.name} → {dst.relative_to(ROOT)} ({r['size_kb']}KB{q}{tag})")
            if eid:
                # Synthetic placeholder no longer needed — flag for cleanup
                synth = PUBLIC / "images" / "_synthetic" / f"{eid}.png"
                if synth.exists():
                    print(f"    (placeholder still at {synth.relative_to(ROOT)}; EntityCard now prefers the real image once JSON imageUrl is set)")
        except Exception as exc:
            print(f"  FAIL {src.name}: {exc}")

    # Summary + reminder about JSON imageUrl
    print(f"\nProcessed {len(results)} images, skipped {skipped}")
    if results:
        print("\nNext step — update each entity's imageUrl field in public/data/<partition>.json:")
        for r in results:
            out_p = Path(r["out"])
            try:
                rel = out_p.relative_to(PUBLIC).as_posix()
                print(f'  "imageUrl": "{rel}",')
            except ValueError:
                # --out pointed outside public/; show as-is for reference
                print(f'  (output: {out_p}; copy into public/images/ to use)')


if __name__ == "__main__":
    main()
