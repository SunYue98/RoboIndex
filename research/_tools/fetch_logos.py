#!/usr/bin/env python3
"""Bulk-fetch candidate logos for 产业/资本/实验室 entities missing imageUrl.

Per-entity strategy (first hit wins):
  1. Wikipedia infobox (English) — usually the canonical clean logo
  2. Wikipedia infobox (Chinese fallback)
  3. Official website apple-touch-icon-precomposed.png
  4. Official website apple-touch-icon.png
  5. Official website favicon-512x512.png / favicon-192x192.png
  6. Official website /logo.png, /logo.svg

Output: raw_images/<entity-id>.{png|svg} — then user runs process_image.py to standardize.

Skips entities that already have imageUrl set, or already have a raw file ready.

Reports successes / failures so you know what still needs manual collection.
"""
import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "public/data"
RAW = ROOT / "raw_images"
RAW.mkdir(parents=True, exist_ok=True)

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
TARGET_CATEGORIES = {"产业", "资本", "实验室"}
MIN_BYTES = 1500  # skip suspiciously small files (likely SPA fallback HTML)


def curl_head(url: str, timeout: int = 10) -> tuple[int, int]:
    """Return (http_code, content_length)."""
    try:
        out = subprocess.run(
            ["curl", "-sIL", "-A", UA, "--max-time", str(timeout), "-w", "%{http_code}\t%{size_download}\n", "-o", "/dev/null", url],
            capture_output=True, text=True, timeout=timeout + 5,
        ).stdout.strip().splitlines()
        if not out:
            return (0, 0)
        last = out[-1]
        parts = last.split("\t")
        return (int(parts[0]), int(parts[1]) if len(parts) > 1 else 0)
    except Exception:
        return (0, 0)


def curl_download(url: str, dest: Path, timeout: int = 20) -> bool:
    """Download with curl, return True if non-empty file written."""
    try:
        subprocess.run(
            ["curl", "-sL", "-A", UA, "--max-time", str(timeout), "-o", str(dest), url],
            timeout=timeout + 5, check=False,
        )
        if dest.exists() and dest.stat().st_size > MIN_BYTES:
            # Check it's not an HTML error page
            head = dest.read_bytes()[:100].lower()
            if b"<html" in head or b"<!doctype" in head:
                dest.unlink()
                return False
            return True
        if dest.exists():
            dest.unlink()
        return False
    except Exception:
        return False


def grep_wikipedia_logo(html: str) -> str | None:
    """Find the infobox logo image URL in Wikipedia article HTML.

    STRICT: only matches the canonical infobox-image class. The earlier loose
    fallback (any img with "logo" in URL) was grabbing Wikipedia's own chrome
    icons (Wiktionary-logo, Wikibooks-logo, etc.), so it's been removed.
    """
    m = re.search(r'<td[^>]*class="[^"]*infobox-image[^"]*"[^>]*>.*?<img[^>]+src="([^"]+)"', html, re.DOTALL)
    if not m:
        return None
    url = m.group(1)
    if url.startswith("//"):
        url = "https:" + url
    # Replace thumb URL with full-res original (path before /<NNN>px-...)
    full = re.sub(r'/thumb(/[a-z0-9]/[a-z0-9]{2}/[^/]+)/\d+px-[^"]+$', r'\1', url)
    return full


def try_wikipedia(entity: dict) -> str | None:
    """Return raw image URL from Wikipedia infobox, or None."""
    candidates = []
    name = entity.get("name", "")
    company = entity.get("company", "")
    # Strip parenthetical Chinese / annotations
    for raw in (name, company):
        clean = re.sub(r"\s*[\(（].*?[\)）]\s*", " ", raw).strip()
        clean = re.sub(r"\s+", "_", clean)
        if clean and clean not in candidates:
            candidates.append(clean)
        # Also try with " " not " "
        clean2 = re.sub(r"\s+", "_", raw.split(" ")[0]) if " " in raw else None
        if clean2 and clean2 != clean and clean2 not in candidates:
            candidates.append(clean2)

    for cand in candidates[:3]:  # cap per-entity attempts
        for lang in ("en", "zh"):
            url = f"https://{lang}.wikipedia.org/wiki/{quote(cand, safe='_')}"
            try:
                res = subprocess.run(
                    ["curl", "-sL", "-A", UA, "--max-time", "12", url],
                    capture_output=True, text=True, timeout=15,
                ).stdout
            except Exception:
                continue
            if not res or "Wikipedia does not have an article" in res:
                continue
            img = grep_wikipedia_logo(res)
            if img:
                return img
    return None


def try_website_favicon(entity: dict) -> str | None:
    """Try standard logo paths on the entity's website."""
    site = (entity.get("orgInfo") or {}).get("website", "")
    if not site:
        return None
    # Normalize
    site = site.rstrip("/")
    if not site.startswith("http"):
        site = "https://" + site

    paths = [
        "apple-touch-icon-precomposed.png",
        "apple-touch-icon.png",
        "favicon-512x512.png",
        "favicon-192x192.png",
        "favicon-256x256.png",
        "logo.png",
        "images/logo.png",
        "assets/logo.png",
        "static/logo.png",
    ]
    for path in paths:
        url = f"{site}/{path}"
        code, _ = curl_head(url)
        if code == 200:
            # Verify it's actually an image (HEAD doesn't always reveal SPA fallbacks)
            return url
    return None


def fetch_one(entity: dict) -> dict:
    """Try multiple sources for one entity, save first hit, return summary."""
    eid = entity["id"]
    # Try Wikipedia first
    img_url = try_wikipedia(entity)
    source_type = "wikipedia"
    if not img_url:
        img_url = try_website_favicon(entity)
        source_type = "website"

    if not img_url:
        return {"id": eid, "name": entity.get("name", ""), "status": "no-source", "url": None}

    # Pick extension from URL
    ext = "png"
    low = img_url.lower()
    if low.endswith(".svg"):
        ext = "svg"
    elif low.endswith(".jpg") or low.endswith(".jpeg"):
        ext = "jpg"
    dest = RAW / f"{eid}.{ext}"
    ok = curl_download(img_url, dest)
    if not ok:
        return {"id": eid, "name": entity.get("name", ""), "status": "download-failed", "url": img_url}

    # Validate dimensions: reject < 200px (likely a small chrome icon, not a real logo)
    if ext != "svg":
        try:
            from PIL import Image
            w, h = Image.open(dest).size
            if max(w, h) < 200:
                dest.unlink()
                return {"id": eid, "name": entity.get("name", ""), "status": f"too-small ({w}x{h})", "url": img_url}
        except Exception:
            pass

    return {
        "id": eid, "name": entity.get("name", ""), "status": "ok",
        "url": img_url, "source": source_type, "ext": ext,
        "size_kb": dest.stat().st_size // 1024,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--categories", default="产业,资本,实验室", help="Comma-separated categories (default: 产业,资本,实验室)")
    ap.add_argument("--limit", type=int, default=80, help="Max entities to try")
    ap.add_argument("--workers", type=int, default=4, help="Parallel fetches")
    ap.add_argument("--force", action="store_true", help="Re-download even if raw file already exists")
    args = ap.parse_args()

    cats = set(args.categories.split(","))

    # Load entities
    targets = []
    for p in ["hardware", "software", "ecosystem", "players"]:
        for e in json.loads((DATA / f"{p}.json").read_text(encoding="utf-8")):
            if e.get("imageUrl"):
                continue
            if e.get("category") not in cats:
                continue
            if not args.force and any((RAW / f"{e['id']}.{ext}").exists() for ext in ("png","svg","jpg")):
                continue
            targets.append(e)
        if len(targets) >= args.limit:
            break
    targets = targets[: args.limit]

    print(f"Fetching logos for {len(targets)} entities across categories {cats}...")
    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = {ex.submit(fetch_one, e): e for e in targets}
        for f in as_completed(futures):
            r = f.result()
            results.append(r)
            mark = "✓" if r["status"] == "ok" else "✗"
            extra = f" via {r.get('source','?')} ({r.get('size_kb','?')}KB)" if r["status"] == "ok" else f" [{r['status']}]"
            print(f"  {mark} {r['id']:30s} {r['name'][:35]:35s}{extra}")

    ok = [r for r in results if r["status"] == "ok"]
    no_src = [r for r in results if r["status"] == "no-source"]
    dl_fail = [r for r in results if r["status"] == "download-failed"]
    print(f"\nResults: {len(ok)} got, {len(no_src)} no-source, {len(dl_fail)} download-failed")
    print(f"\nNext: visually inspect raw_images/, then run:")
    print(f"  python3 research/_tools/process_image.py raw_images/ --batch --format png --pad")


if __name__ == "__main__":
    main()
