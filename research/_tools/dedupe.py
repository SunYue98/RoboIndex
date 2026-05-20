#!/usr/bin/env python3
"""Dedupe public/data/*.json by merging known duplicate pairs.

For each (winner_id, loser_id) pair:
  - Take richer fields (specs, tags, paperInfo, orgInfo, year, imageUrl) from loser
    into winner where winner's value is missing / less specific.
  - Merge sources arrays (deduplicated by URL).
  - Update any other entries' relatedIds: loser_id -> winner_id.
  - Delete loser.

Also handles pure deletions (placeholder entries fully replaced).
"""
import json
import re
from pathlib import Path
from copy import deepcopy

ROOT = Path(__file__).resolve().parents[2]
PUBLIC = ROOT / "public/data"

# (winner_id, loser_id) — winner stays in live data, loser's richer fields merged in
MERGES = [
    # Hardware: original short-id + Phase 5 flagship duplicate
    ("f4", "flagship-optimus-gen2"),
    ("f24", "flagship-unitree-h2"),
    ("f29", "flagship-atlas-electric"),
    ("f38", "flagship-booster-t1"),
    ("f49", "flagship-agibot-a2"),
    ("f69", "flagship-walker-s2"),
    ("f73", "flagship-limx-oli"),
    ("f104", "flagship-figure-03"),
    ("f118", "flagship-phoenix-gen8"),
    # Hardware: f119 "MEMO 未知/概念" is fake; merge into real f1 Memo by Agility
    ("f1", "f119"),
    # Software: short-id + Phase 1 stg-derived duplicate
    ("sw1", "sw-openvla"),
    ("sw2", "sw-rtx"),
    ("sw3", "sw-isaac-lab"),
    ("sw5", "sw-isaac-sim"),
    ("sw6", "sw-mujoco"),
    ("sw7", "sw-open-x-embodiment"),
    # Software: cross-category duplicates (pick winner category)
    ("sw-ocs2", "sw-ocs2-framework"),     # OCS2 → 控制算法
    ("sw-drake", "sw-drake-framework"),   # Drake → 仿真平台
    ("sw-act", "sw-act-aloha"),           # ACT → 控制算法
    # Software: bm1 generic ManiSkill → use proper sw-maniskill3 as current version
    ("sw-maniskill3", "bm1"),
    # Ecosystem: short-id + stg-derived
    ("eco1", "eco-ros2"),
    ("eco2", "eco-foxglove"),
    # Players: short-id + stg-derived
    ("vc1", "vc-sequoia"),
    ("ind1", "ind-nvidia-robotics"),
]

# Pure deletions (no winner; entry is fully covered by other entries)
DELETIONS = [
    "ca1",  # generic "MIT Cheetah WBC" placeholder; covered by sw-convex-mpc-cheetah + sw-wbc-sentis
]


def merge_sources(winner_srcs, loser_srcs):
    """Merge two sources lists, deduplicating by URL."""
    seen_urls = set()
    out = []
    for s in (winner_srcs or []) + (loser_srcs or []):
        u = s.get("url", "").strip()
        if u and u in seen_urls:
            continue
        seen_urls.add(u)
        out.append(s)
    return out


def merge_specs(winner_specs, loser_specs):
    """Merge specs: prefer winner's value if present, else take loser's."""
    out = dict(winner_specs or {})
    for k, v in (loser_specs or {}).items():
        if k not in out or out[k] in (None, "", "—", "n/a"):
            out[k] = v
    return out


def is_richer(loser_val, winner_val):
    """Heuristic: is loser_val 'richer' than winner_val?"""
    if not winner_val:
        return bool(loser_val)
    if not loser_val:
        return False
    # If both are dicts, compare key count
    if isinstance(winner_val, dict) and isinstance(loser_val, dict):
        return len(loser_val) > len(winner_val)
    # If both are strings, prefer longer (usually more detailed)
    if isinstance(winner_val, str) and isinstance(loser_val, str):
        return len(loser_val.strip()) > len(winner_val.strip()) * 1.3
    return False


def merge_entry(winner, loser):
    """Merge loser's data into winner where winner is missing or less specific.
    Winner keeps its id, category, relatedIds, imageUrl."""
    w = deepcopy(winner)
    # Sources — combine
    w["sources"] = merge_sources(w.get("sources"), loser.get("sources"))
    # Specs — combine (winner's values win)
    w["specs"] = merge_specs(w.get("specs", {}), loser.get("specs", {}))
    # Tags — combine, deduplicated
    w_tags = w.get("tags") or []
    l_tags = loser.get("tags") or []
    seen = set(w_tags)
    for t in l_tags:
        if t not in seen:
            w_tags.append(t)
            seen.add(t)
    if w_tags:
        w["tags"] = w_tags
    # paperInfo / orgInfo — take loser's if winner missing
    for field in ("paperInfo", "orgInfo"):
        if not w.get(field) and loser.get(field):
            w[field] = loser[field]
    # year / name / company — prefer loser if winner's looks like a placeholder
    if is_richer(loser.get("year", ""), w.get("year", "")):
        w["year"] = loser["year"]
    if is_richer(loser.get("name", ""), w.get("name", "")):
        # Only overwrite name if it's significantly more descriptive
        pass  # Keep winner's name for stability
    return w


def main():
    partitions = ["hardware", "software", "ecosystem", "players"]
    # Load all partitions, build a global id->entry index
    live = {p: json.loads((PUBLIC / f"{p}.json").read_text(encoding="utf-8")) for p in partitions}
    id_to_partition = {}
    for p, data in live.items():
        for e in data:
            id_to_partition[e["id"]] = p

    # Build remap: loser_id -> winner_id for relatedIds rewriting
    remap = {loser: winner for winner, loser in MERGES}
    for did in DELETIONS:
        remap[did] = None  # mark for removal in relatedIds

    # Phase 1: merge entries
    merge_log = []
    for winner_id, loser_id in MERGES:
        wp = id_to_partition.get(winner_id)
        lp = id_to_partition.get(loser_id)
        if not wp or not lp:
            merge_log.append(f"SKIP {winner_id} <- {loser_id}: missing partition")
            continue
        # Find entries
        w_idx = next((i for i, e in enumerate(live[wp]) if e["id"] == winner_id), None)
        l_idx = next((i for i, e in enumerate(live[lp]) if e["id"] == loser_id), None)
        if w_idx is None or l_idx is None:
            merge_log.append(f"SKIP {winner_id} <- {loser_id}: entry not found")
            continue
        winner = live[wp][w_idx]
        loser = live[lp][l_idx]
        merged = merge_entry(winner, loser)
        live[wp][w_idx] = merged
        merge_log.append(
            f"MERGE {wp}:{winner_id} <- {lp}:{loser_id}  "
            f"(+{len(loser.get('sources', []))} src, "
            f"+{len(set((loser.get('tags') or [])) - set(winner.get('tags') or []))} tags)"
        )

    # Phase 2: delete losers + DELETIONS from their partitions
    to_remove = {loser for _, loser in MERGES} | set(DELETIONS)
    for p in partitions:
        before = len(live[p])
        live[p] = [e for e in live[p] if e["id"] not in to_remove]
        removed = before - len(live[p])
        if removed:
            merge_log.append(f"REMOVED from {p}.json: {removed} entries")

    # Phase 3: rewrite relatedIds across all entries
    relatedIds_fixes = 0
    for p in partitions:
        for e in live[p]:
            rel = e.get("relatedIds")
            if not rel:
                continue
            new_rel = []
            for rid in rel:
                if rid in remap:
                    target = remap[rid]
                    if target is None:
                        # Deletion — drop the link
                        relatedIds_fixes += 1
                        continue
                    new_rel.append(target)
                    relatedIds_fixes += 1
                else:
                    new_rel.append(rid)
            # Dedupe within list
            seen = set()
            new_rel = [r for r in new_rel if not (r in seen or seen.add(r))]
            e["relatedIds"] = new_rel

    merge_log.append(f"relatedIds rewrites: {relatedIds_fixes}")

    # Phase 4: write back
    for p in partitions:
        (PUBLIC / f"{p}.json").write_text(
            json.dumps(live[p], ensure_ascii=False, indent=2), encoding="utf-8"
        )

    # Report
    print("=== dedupe.py report ===")
    for line in merge_log:
        print(f"  {line}")
    print()
    print("Per-partition counts after dedup:")
    for p in partitions:
        n = len(live[p])
        n_sources = sum(1 for e in live[p] if e.get("sources"))
        print(f"  {p:9s} {n:>4} entries, {n_sources} with sources ({n_sources*100//n if n else 0}%)")


if __name__ == "__main__":
    main()
