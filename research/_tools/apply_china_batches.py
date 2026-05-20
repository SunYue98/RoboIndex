#!/usr/bin/env python3
"""Apply Chinese coverage batches (industry + labs/VCs) to players.json.

Pattern:
  - Read both batch files
  - For each entry: strip _provenance, promote _provenance.sources → entity.sources (url/title/type only)
  - Check id collision with existing players.json (skip with warning)
  - Check name collision (canon-name comparison) — skip with warning
  - Append survivors to players.json

Does NOT touch hardware/software/ecosystem — these new entries are all 产业/实验室/资本.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PUBLIC = ROOT / "public/data"
BATCHES = ROOT / "research/_batches"

BATCH_FILES = [
    BATCHES / "batch_p10_china_industry.json",
    BATCHES / "batch_p11_china_labs_vcs.json",
]

def canon(s):
    s = (s or "").lower()
    s = re.sub(r"\([^)]*\)", "", s)
    s = re.sub(r"[^\w一-鿿]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

players = json.loads((PUBLIC / "players.json").read_text(encoding="utf-8"))
existing_ids = {e["id"] for e in players}
existing_canons = {canon(e.get("name", "")): e["id"] for e in players if e.get("name")}

new_entries = []
skipped = []

for bf in BATCH_FILES:
    batch = json.loads(bf.read_text(encoding="utf-8"))
    for entry in batch:
        eid = entry["id"]
        ename = entry.get("name", "")
        ecanon = canon(ename)
        if eid in existing_ids:
            skipped.append(f"  ID conflict: {eid} ({ename}) — already in players.json as same id")
            continue
        if ecanon in existing_canons:
            skipped.append(f"  NAME conflict: {eid} ({ename}) ≈ existing {existing_canons[ecanon]}")
            continue

        # Strip _provenance, promote sources
        prov = entry.pop("_provenance", {})
        sources = []
        for s in prov.get("sources", []) or []:
            clean = {"url": s.get("url", ""), "title": s.get("title", "")}
            if s.get("type"):
                clean["type"] = s["type"]
            if clean["url"]:
                sources.append(clean)
        if sources:
            entry["sources"] = sources

        # Ensure relatedIds list exists (empty for now; relations passes will fill it)
        entry.setdefault("relatedIds", [])

        new_entries.append(entry)
        existing_ids.add(eid)
        existing_canons[ecanon] = eid

players.extend(new_entries)

# Write back
(PUBLIC / "players.json").write_text(
    json.dumps(players, ensure_ascii=False, indent=2), encoding="utf-8"
)

# Report
print(f"=== apply_china_batches.py ===\n")
print(f"Appended {len(new_entries)} entries to players.json")
print(f"  产业: {sum(1 for e in new_entries if e['category'] == '产业')}")
print(f"  实验室: {sum(1 for e in new_entries if e['category'] == '实验室')}")
print(f"  资本: {sum(1 for e in new_entries if e['category'] == '资本')}")
print(f"\nplayers.json total: {len(players)}")
if skipped:
    print(f"\nSkipped ({len(skipped)}):")
    for s in skipped:
        print(s)
