#!/usr/bin/env python3
"""Phase 2 dedup pass: catches dupes that earlier dedup_script missed because
of canon-name mismatches.

Newly found pairs:
  - f81 APPTRONIK APOLLO  +  flagship-apptronik-apollo Apollo
    (Apptronik's actual Apollo product; both refer to same robot)

Strategy: same as research/_tools/dedupe.py — keep winner id (shorter / older),
absorb richer fields from loser, rewrite relatedIds.
"""
import json, re
from pathlib import Path
from copy import deepcopy

ROOT = Path(__file__).resolve().parents[2]
PUBLIC = ROOT / "public/data"

MERGES = [
    ("f81", "flagship-apptronik-apollo"),  # both = Apptronik Apollo humanoid
]

partitions = ["hardware", "software", "ecosystem", "players"]
data = {p: json.loads((PUBLIC / f"{p}.json").read_text(encoding="utf-8")) for p in partitions}
id_to_part = {}
for p, lst in data.items():
    for e in lst:
        id_to_part[e["id"]] = p


def merge_sources(a, b):
    seen = set()
    out = []
    for s in (a or []) + (b or []):
        u = s.get("url", "").strip()
        if u and u in seen: continue
        if u: seen.add(u)
        out.append(s)
    return out


def merge_specs(a, b):
    out = dict(a or {})
    for k, v in (b or {}).items():
        if k not in out or out[k] in (None, "", "—", "n/a"):
            out[k] = v
    return out


merged_count = 0
for winner_id, loser_id in MERGES:
    wp = id_to_part.get(winner_id)
    lp = id_to_part.get(loser_id)
    if not wp or not lp:
        print(f"  SKIP {winner_id}/{loser_id} — missing")
        continue
    w_idx = next((i for i, e in enumerate(data[wp]) if e["id"] == winner_id), None)
    l_idx = next((i for i, e in enumerate(data[lp]) if e["id"] == loser_id), None)
    if w_idx is None or l_idx is None:
        print(f"  SKIP {winner_id}/{loser_id} — not found")
        continue
    winner = data[wp][w_idx]
    loser = data[lp][l_idx]
    # Merge richer fields into winner
    w = deepcopy(winner)
    w["sources"] = merge_sources(w.get("sources"), loser.get("sources"))
    w["specs"] = merge_specs(w.get("specs", {}), loser.get("specs", {}))
    w_tags = list(w.get("tags") or [])
    seen = set(w_tags)
    for t in (loser.get("tags") or []):
        if t not in seen:
            w_tags.append(t); seen.add(t)
    if w_tags:
        w["tags"] = w_tags
    for fld in ("paperInfo", "orgInfo"):
        if not w.get(fld) and loser.get(fld):
            w[fld] = loser[fld]
    data[wp][w_idx] = w
    print(f"  MERGE {wp}:{winner_id} <- {lp}:{loser_id}  (+{len(loser.get('sources') or [])} src)")
    merged_count += 1

# Phase 2: delete losers + rewrite relatedIds (loser_id -> winner_id)
remap = {loser: winner for winner, loser in MERGES}
losers = set(remap.keys())
for p in partitions:
    data[p] = [e for e in data[p] if e["id"] not in losers]

# Rewrite relatedIds
relmaps = 0
for p in partitions:
    for e in data[p]:
        rel = e.get("relatedIds") or []
        new = []
        seen = set()
        for r in rel:
            r2 = remap.get(r, r)
            if r2 not in seen and r2 != e["id"]:
                new.append(r2)
                seen.add(r2)
                if r2 != r: relmaps += 1
        e["relatedIds"] = new

# Write
for p in partitions:
    (PUBLIC / f"{p}.json").write_text(
        json.dumps(data[p], ensure_ascii=False, indent=2), encoding="utf-8"
    )

print(f"\nTotal merges: {merged_count}")
print(f"relatedIds rewrites: {relmaps}")
print()
for p in partitions:
    print(f"  {p:9s} {len(data[p]):>4} entries")
