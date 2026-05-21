#!/usr/bin/env python3
"""Phase 8 — Compute the dataset version stamp and write it into summary.json.

Versioning model:
  schema_version  — semver-major. Bumped only when an Entity / Relation /
                    Claim shape changes in a way that breaks external
                    consumers. Currently 1 (post-Phase-7 stable schema).
  dataset_version — date-based: "YYYY.MM.DD.N" where N is the count of
                    same-day data changes (0-indexed). Lets consumers
                    pin to a specific snapshot.
  snapshot_sha    — git HEAD short SHA at the time build_api.py last ran.
                    Lets consumers diff between snapshots.
  generated_at    — ISO date.
  entity_count, edge_count — sanity-check numbers for consumers.

Usage:
  python3 research/_tools/version_bump.py
This rewrites public/api/summary.json with the version block at the top.
"""
import json
import re
import subprocess
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
API = ROOT / "public/api"
SUMMARY = API / "summary.json"

SCHEMA_VERSION = 1  # bump when Entity / Relation / Claim shape changes


def git_short_sha() -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, cwd=ROOT, timeout=5,
        )
        return out.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def compute_dataset_version(prev: str | None, today: str) -> str:
    """Returns YYYY.MM.DD.N where N increments for same-day changes."""
    if prev and prev.startswith(today + "."):
        try:
            n = int(prev.rsplit(".", 1)[-1])
            return f"{today}.{n + 1}"
        except ValueError:
            pass
    return f"{today}.0"


def main():
    if not SUMMARY.exists():
        print("FATAL: public/api/summary.json missing. Run build_api.py first.")
        raise SystemExit(1)

    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    today = date.today().isoformat().replace("-", ".")
    prev_dataset_version = summary.get("dataset_version")
    new_dataset_version = compute_dataset_version(prev_dataset_version, today)

    version_block = {
        "schema_version": SCHEMA_VERSION,
        "dataset_version": new_dataset_version,
        "snapshot_sha": git_short_sha(),
        "generated_at": str(date.today()),
        "entity_count": summary.get("totals", {}).get("entities"),
        "edge_count": summary.get("totals", {}).get("edges"),
    }

    # Put the version block at the top of summary.json for easy discovery
    new_summary = {**version_block, **{k: v for k, v in summary.items()
                                       if k not in version_block}}
    SUMMARY.write_text(
        json.dumps(new_summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"Updated {SUMMARY.relative_to(ROOT)}:")
    print(f"  schema_version:  {SCHEMA_VERSION}")
    print(f"  dataset_version: {new_dataset_version}")
    print(f"  snapshot_sha:    {version_block['snapshot_sha']}")
    print(f"  entity_count:    {version_block['entity_count']}")
    print(f"  edge_count:      {version_block['edge_count']}")


if __name__ == "__main__":
    main()
