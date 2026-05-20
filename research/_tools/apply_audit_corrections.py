#!/usr/bin/env python3
"""Apply remaining audit.md corrections to live public/data/.

After prior phases applied year fixes, deletions, renames, and company
attributions, these final corrections remain:

1. DELETE f23 (AgileX LIMO) — wheeled education robot miscategorized as humanoid.
2. DELETE f113 (OWI RE-CO) — $35 children's STEM kit miscategorized as humanoid.
3. MERGE f41+f112 — both refer to X-Humanoid Tian Yi 2.0. Keep f41 (more sources).
4. MERGE f97+f137 — both refer to Topstar Xiao Tuo. Keep f137 (full name vs truncation).
5. RENAME f63 STAR1 → S1 — Astribot's actual flagship is S1, not STAR1.
6. UPDATE e2 Shadow Hand year 2024 → 2022 — current-gen E3M5R released ~2022.

Also cleans up any relatedIds that point to deleted entries.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PUBLIC = ROOT / "public/data"

partitions = ["hardware", "software", "ecosystem", "players"]
data = {p: json.loads((PUBLIC / f"{p}.json").read_text(encoding="utf-8")) for p in partitions}

# ---- 1-2: Outright deletions ----
TO_DELETE = {"f23", "f113", "f112", "f97"}

# ---- 3-4: Merge actions (keep source's relatedIds; nothing else to merge) ----
# f112 → f41 (keep f41 TIAN YI 2.0). f41 already references f112 in relatedIds; we'll remove that ref.
# f97 → f137 (keep f137 XIAO TUO).

# Before deleting, transfer any unique data we'd lose
# f112 has 1 source, f41 has 2 — check if f112's source is already in f41
f41 = next(e for e in data["hardware"] if e["id"] == "f41")
f112 = next(e for e in data["hardware"] if e["id"] == "f112")
f41_urls = {s["url"] for s in f41.get("sources", [])}
for s in f112.get("sources", []):
    if s["url"] not in f41_urls:
        f41.setdefault("sources", []).append(s)
        print(f"  Transferred f112 source to f41: {s.get('title','')[:50]}")

# f97 → f137: keep f137. f97 has 2 sources, f137 has 2; check overlap
f97 = next(e for e in data["hardware"] if e["id"] == "f97")
f137 = next(e for e in data["hardware"] if e["id"] == "f137")
f137_urls = {s["url"] for s in f137.get("sources", [])}
for s in f97.get("sources", []):
    if s["url"] not in f137_urls:
        f137.setdefault("sources", []).append(s)
        print(f"  Transferred f97 source to f137: {s.get('title','')[:50]}")

# ---- 5: Rename ----
f63 = next(e for e in data["hardware"] if e["id"] == "f63")
old_name = f63["name"]
f63["name"] = "S1"
print(f"  Renamed f63: {old_name!r} → 'S1'")

# ---- 6: Year fix ----
e2 = next(e for e in data["hardware"] if e["id"] == "e2")
old_year = e2["year"]
e2["year"] = "2022"
print(f"  Updated e2 Shadow Hand year: {old_year} → 2022")

# ---- Apply deletions ----
deleted_count = 0
for p in partitions:
    before = len(data[p])
    data[p] = [e for e in data[p] if e["id"] not in TO_DELETE]
    after = len(data[p])
    if before != after:
        print(f"  Deleted {before - after} entries from {p}.json")
        deleted_count += before - after

# ---- Clean up dangling relatedIds ----
all_ids = {e["id"] for lst in data.values() for e in lst}
dangling_count = 0
for lst in data.values():
    for e in lst:
        rels = e.get("relatedIds") or []
        kept = [r for r in rels if r in all_ids]
        if len(kept) != len(rels):
            dangling_count += len(rels) - len(kept)
            e["relatedIds"] = kept

print(f"\nCleaned up {dangling_count} dangling relatedIds")

# ---- Also clean up dangling investor IDs in fundingRounds ----
funding_dangling = 0
for lst in data.values():
    for e in lst:
        for r in e.get("fundingRounds") or []:
            for inv in r.get("investors", []) or []:
                inv_id = inv.get("id")
                if inv_id and inv_id not in all_ids:
                    del inv["id"]
                    funding_dangling += 1

print(f"Cleaned up {funding_dangling} dangling investor IDs in fundingRounds")

# ---- Write back ----
for p in partitions:
    (PUBLIC / f"{p}.json").write_text(
        json.dumps(data[p], ensure_ascii=False, indent=2), encoding="utf-8"
    )

print(f"\nDone. Total deletions: {deleted_count}")
print(f"New partition sizes: {', '.join(f'{p}={len(data[p])}' for p in partitions)}")
