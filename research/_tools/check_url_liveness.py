#!/usr/bin/env python3
"""Phase 7 — Source URL liveness check.

Walks every `sources[*].url`, every `fundingRounds[*].source.url`, and every
`sourcedSpecs[*].source.url` in the dataset. HEADs each URL via curl with a
generous timeout, classifies HTTP status, caches the result so the next run
re-checks only URLs older than --stale-days.

Cache: research/_health_cache/url_status.json
       { "<url>": { "status": int, "checked_at": "YYYY-MM-DD", "category": "..." } }

Categories:
  "ok"            — 2xx or 3xx
  "client_error"  — 4xx (likely dead)
  "server_error"  — 5xx (could be temporary)
  "timeout"       — couldn't reach in time
  "error"         — other (DNS / TLS / etc.)

Usage:
  python3 research/_tools/check_url_liveness.py            # incremental
  python3 research/_tools/check_url_liveness.py --full     # re-check everything
  python3 research/_tools/check_url_liveness.py --sample 50 # random N urls
  python3 research/_tools/check_url_liveness.py --report   # just print the cached report
"""
import argparse
import json
import random
import subprocess
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "public/data"
CACHE_DIR = ROOT / "research/_health_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
CACHE = CACHE_DIR / "url_status.json"
PARTITIONS = ["hardware", "software", "ecosystem", "players"]

UA = "Mozilla/5.0 (compatible; RoboIndexLinkCheck/1.0)"


def collect_urls() -> dict[str, list[tuple[str, str]]]:
    """Return {url: [(entity_id, field_path), ...]} so we can blame failures."""
    urls: dict[str, list[tuple[str, str]]] = {}
    for p in PARTITIONS:
        for e in json.loads((DATA / f"{p}.json").read_text(encoding="utf-8")):
            eid = e["id"]
            for i, s in enumerate(e.get("sources") or []):
                u = (s or {}).get("url")
                if u:
                    urls.setdefault(u, []).append((eid, f"sources[{i}]"))
            for i, fr in enumerate(e.get("fundingRounds") or []):
                u = ((fr or {}).get("source") or {}).get("url")
                if u:
                    urls.setdefault(u, []).append((eid, f"fundingRounds[{i}].source"))
            for k, claim in (e.get("sourcedSpecs") or {}).items():
                u = ((claim or {}).get("source") or {}).get("url")
                if u:
                    urls.setdefault(u, []).append((eid, f"sourcedSpecs.{k}.source"))
            # entity-level website (Phase 5 fixed this)
            if e.get("websiteUrl"):
                urls.setdefault(e["websiteUrl"], []).append((eid, "websiteUrl"))
            ow = (e.get("orgInfo") or {}).get("website")
            if ow:
                urls.setdefault(ow, []).append((eid, "orgInfo.website"))
    return urls


def classify(code: int) -> str:
    if code == 0:
        return "error"
    if 200 <= code < 400:
        return "ok"
    if 400 <= code < 500:
        return "client_error"
    if 500 <= code < 600:
        return "server_error"
    return "error"


def head_url(url: str, timeout: int = 12) -> dict:
    """HEAD with fallback to GET if HEAD is rejected (some CDNs 405 HEAD)."""
    try:
        proc = subprocess.run(
            ["curl", "-sILA", UA, "--max-time", str(timeout),
             "-w", "%{http_code}\n", "-o", "/dev/null", url],
            capture_output=True, text=True, timeout=timeout + 5,
        )
        # Last token of stdout is the final HTTP code after redirects
        last_line = proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else "0"
        try:
            code = int(last_line.split("\t")[0])
        except ValueError:
            code = 0
        if code == 405:  # HEAD not allowed → try GET
            proc2 = subprocess.run(
                ["curl", "-sL", "-A", UA, "--max-time", str(timeout),
                 "-o", "/dev/null", "-w", "%{http_code}", url],
                capture_output=True, text=True, timeout=timeout + 5,
            )
            try:
                code = int(proc2.stdout.strip())
            except ValueError:
                code = 0
    except subprocess.TimeoutExpired:
        code = 0
        return {"status": 0, "category": "timeout", "checked_at": str(date.today())}
    except Exception:
        code = 0
    return {"status": code, "category": classify(code), "checked_at": str(date.today())}


def load_cache() -> dict:
    if CACHE.exists():
        try:
            return json.loads(CACHE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_cache(cache: dict):
    CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stale-days", type=int, default=30, help="Re-check URLs cached older than N days (default 30)")
    ap.add_argument("--full", action="store_true", help="Re-check every URL regardless of cache")
    ap.add_argument("--sample", type=int, help="Only check N random URLs (for fast iteration)")
    ap.add_argument("--workers", type=int, default=8, help="Parallel HEAD requests")
    ap.add_argument("--report", action="store_true", help="Print report only; don't make any HTTP requests")
    ap.add_argument("--markdown", action="store_true", help="Write report to research/_health_cache/url_liveness.md")
    args = ap.parse_args()

    urls = collect_urls()
    cache = load_cache()
    print(f"Total unique source URLs in corpus: {len(urls)}")
    print(f"URLs in cache: {len(cache)}")

    if not args.report:
        cutoff = datetime.today() - timedelta(days=args.stale_days)
        to_check = []
        for u in urls.keys():
            entry = cache.get(u)
            if args.full or not entry:
                to_check.append(u)
            else:
                try:
                    checked = datetime.fromisoformat(entry["checked_at"])
                    if checked < cutoff:
                        to_check.append(u)
                except Exception:
                    to_check.append(u)

        if args.sample and len(to_check) > args.sample:
            to_check = random.sample(to_check, args.sample)

        print(f"Will check {len(to_check)} URLs (workers={args.workers})")
        n_done = 0
        with ThreadPoolExecutor(max_workers=args.workers) as ex:
            futures = {ex.submit(head_url, u): u for u in to_check}
            for f in as_completed(futures):
                u = futures[f]
                cache[u] = f.result()
                n_done += 1
                if n_done % 25 == 0:
                    print(f"  ...{n_done}/{len(to_check)} checked", file=sys.stderr)
                    save_cache(cache)
        save_cache(cache)

    # Report
    cats = Counter(cache.get(u, {}).get("category", "unchecked") for u in urls)
    print(f"\n=== URL liveness report ===")
    for c in ["ok", "client_error", "server_error", "timeout", "error", "unchecked"]:
        if cats.get(c):
            print(f"  {c:14s} {cats[c]:5d}")

    # List dead links (client_error)
    dead = [(u, cache[u], urls[u]) for u in urls if cache.get(u, {}).get("category") == "client_error"]
    if dead:
        print(f"\nDEAD LINKS ({len(dead)}):")
        for u, status, refs in dead[:30]:
            refs_s = "; ".join(f"{eid}:{path}" for eid, path in refs[:3])
            print(f"  HTTP {status['status']}  {u}")
            print(f"      ← {refs_s}")

    if args.markdown:
        lines = ["# Source URL liveness", "",
                 f"Total unique URLs: {len(urls)}",
                 f"Last check date(s) in cache: {sorted(set(c.get('checked_at','?') for c in cache.values()))[-3:]}",
                 ""]
        lines.append("## Category breakdown\n")
        lines.append("| Category | Count |\n|---|---:|")
        for c in ["ok", "client_error", "server_error", "timeout", "error", "unchecked"]:
            if cats.get(c):
                lines.append(f"| {c} | {cats[c]} |")
        if dead:
            lines.append(f"\n## Dead links ({len(dead)})\n")
            for u, status, refs in dead:
                refs_s = "; ".join(f"`{eid}`/{path}" for eid, path in refs[:5])
                lines.append(f"- HTTP {status['status']}  `{u}`")
                lines.append(f"  - referenced by: {refs_s}")
        (CACHE_DIR / "url_liveness.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"\nWrote {CACHE_DIR / 'url_liveness.md'}")


if __name__ == "__main__":
    main()
