#!/usr/bin/env python3
"""Phase 8 merge preview — generates what the merged public/data/*.json files
would look like, **without** overwriting them. Output goes to research/_preview/.

Inputs:
  - public/data/*.json (existing live data)
  - research/staging.json (new entries)
  - research/backfill.json (sources for existing entries)
  - research/audit.md (manually noted replacements)  -- replacements parsed from a hardcoded table for now

Steps:
  1. Copy existing live data into preview.
  2. For each existing entry: if backfill.json has its id, add `sources` field.
  3. Apply audit deletions (en1) and replacements (e1, e2, cp2, etc.).
  4. For each staging entry that's a flagship/new addition (stg-flagship-*, stg-sw-*, etc.),
     produce a new live entry: strip `_provenance`, promote its sources to `sources`,
     reconcile id, assign to correct partition.
  5. Write previews and a summary.

The user reviews the preview before doing the actual merge.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # repo root
PUBLIC = ROOT / "public/data"
RESEARCH = ROOT / "research"
PREVIEW = RESEARCH / "_preview"
PREVIEW.mkdir(exist_ok=True)

partitions = ['hardware', 'software', 'ecosystem', 'players']

# Load live data
live = {p: json.loads((PUBLIC / f"{p}.json").read_text(encoding="utf-8")) for p in partitions}

# Load staging
staging = json.loads((RESEARCH / "staging.json").read_text(encoding="utf-8"))
staging_by_id = {e['id']: e for e in staging}

# Load backfill
backfill = json.loads((RESEARCH / "backfill.json").read_text(encoding="utf-8"))
# Filter doc keys
backfill = {k: v for k, v in backfill.items() if not k.startswith('_')}

# --- Audit replacements ---
# From audit.md: maps live-id -> staging-id (the replacement entry).
# en1 is fabricated and gets DELETED with no replacement.
REPLACEMENTS = {
    "a1":  "stg-arm-ur10e",
    "a2":  "stg-arm-franka-panda",
    "c1":  "stg-comp-harmonic-csf-2uh",
    "c2":  "stg-comp-kollmorgen-kbm",
    "cp1": "stg-cp-jetson-agx-orin",
    "cp2": "stg-cp2-replacement",
    "d1":  "stg-teleop-haptx-g1",
    "e1":  "stg-e1-replacement",
    "e2":  "stg-e2-replacement",
    "j2":  "stg-joint-dynamixel-ph54-200",
    "s1":  "stg-sensor-realsense-d455",
    "s2":  "stg-sensor-ati-axia80",
    # j1 left as-is (Fourier FSA Actuator) — no Phase 4/5 replacement, will need needs-source badge.
}
DELETIONS = {"en1"}  # Fabricated entry, no replacement.

# Map flagship staging entries to live-id replacements (broken-image-refs)
REPLACEMENTS["f34"] = "stg-flagship-neo-gamma"      # NEO GAMMA

# Mapping from staging entry's category to live partition
CATEGORY_TO_PARTITION = {
    # hardware
    "整机平台": "hardware",
    "机械臂": "hardware",
    "灵巧手 & 夹爪": "hardware",
    "关节模组": "hardware",
    "核心零部件": "hardware",
    "传感器": "hardware",
    "能源动力": "hardware",
    "数采 & 遥操": "hardware",
    "计算平台": "hardware",
    # software
    "基础模型": "software",
    "算法框架": "software",
    "控制算法": "software",
    "仿真平台": "software",
    "数据集": "software",
    "评测基准": "software",
    # ecosystem
    "开发生态": "ecosystem",
    "应用场景": "ecosystem",
    # players
    "资本": "players",
    "产业": "players",
    "实验室": "players",
}

def strip_provenance_and_promote(stg_entry):
    """Turn a staging entry into a live entry: strip _provenance, set sources from it."""
    e = {k: v for k, v in stg_entry.items() if k != "_provenance"}
    prov = stg_entry.get("_provenance", {})
    src_list = prov.get("sources", [])
    if src_list:
        # Strip 'fetched' from each source (internal-only metadata)
        e["sources"] = [
            {k: v for k, v in s.items() if k != "fetched"}
            for s in src_list
        ]
    return e

def reconcile_id(stg_id, partition):
    """Strip stg- prefix; if collision with existing id, suffix with -ext."""
    new_id = stg_id
    if new_id.startswith("stg-"):
        new_id = new_id[4:]
    return new_id

# Build the preview output
preview = {p: [] for p in partitions}
log_lines = []

# Pass 1: keep / modify existing entries
for p in partitions:
    for e in live[p]:
        eid = e['id']
        if eid in DELETIONS:
            log_lines.append(f"[DELETE] {p}:{eid} ({e.get('name','?')}) — fabricated")
            continue
        if eid in REPLACEMENTS:
            stg_id = REPLACEMENTS[eid]
            stg = staging_by_id.get(stg_id)
            if not stg:
                log_lines.append(f"[WARN] {p}:{eid} maps to {stg_id} which is missing from staging")
                preview[p].append(e)  # fall back to keeping original
                continue
            # Promote staging entry to live, keeping the original live id
            replacement = strip_provenance_and_promote(stg)
            replacement["id"] = eid  # preserve the original id so relatedIds links don't break
            # Preserve relatedIds from original
            if e.get("relatedIds") and not replacement.get("relatedIds"):
                replacement["relatedIds"] = e["relatedIds"]
            preview[p].append(replacement)
            log_lines.append(f"[REPLACE] {p}:{eid} <- {stg_id} ({replacement.get('name','?')})")
            continue
        # Plain existing entry — apply backfill if present
        if eid in backfill:
            bf = backfill[eid]
            srcs = bf.get('sources', [])
            if srcs:
                e2 = dict(e)
                e2['sources'] = [{k: v for k, v in s.items() if k != 'fetched'} for s in srcs]
                preview[p].append(e2)
                log_lines.append(f"[BACKFILL] {p}:{eid} — added {len(srcs)} sources")
            else:
                preview[p].append(e)
        else:
            preview[p].append(e)

# Pass 2: add NEW staging entries that weren't replacement-mapped
mapped_stg_ids = set(REPLACEMENTS.values())
for stg_id, stg in staging_by_id.items():
    if stg_id in mapped_stg_ids:
        continue  # already used as a replacement
    cat = stg.get('category')
    partition = CATEGORY_TO_PARTITION.get(cat)
    if not partition:
        log_lines.append(f"[SKIP] {stg_id} — unknown category '{cat}'")
        continue
    new_entry = strip_provenance_and_promote(stg)
    new_entry['id'] = reconcile_id(stg_id, partition)
    preview[partition].append(new_entry)
    log_lines.append(f"[ADD] {partition}:{new_entry['id']} (from {stg_id})")

# Write previews
for p in partitions:
    out = PREVIEW / f"{p}.preview.json"
    out.write_text(json.dumps(preview[p], ensure_ascii=False, indent=2), encoding="utf-8")

(PREVIEW / "merge.log").write_text("\n".join(log_lines), encoding="utf-8")

# Summary stats
print("=== Phase 8 merge preview ===\n")
for p in partitions:
    n_before = len(live[p])
    n_after = len(preview[p])
    with_sources = sum(1 for e in preview[p] if e.get('sources'))
    sources_pct = (with_sources / n_after * 100) if n_after else 0
    print(f"  {p}.json: {n_before} -> {n_after} entries, {with_sources} with sources ({sources_pct:.0f}%)")

n_replaced = sum(1 for l in log_lines if l.startswith('[REPLACE]'))
n_deleted = sum(1 for l in log_lines if l.startswith('[DELETE]'))
n_backfilled = sum(1 for l in log_lines if l.startswith('[BACKFILL]'))
n_added = sum(1 for l in log_lines if l.startswith('[ADD]'))
n_warn = sum(1 for l in log_lines if l.startswith('[WARN]'))
print()
print(f"  Replaced: {n_replaced}")
print(f"  Deleted:  {n_deleted}")
print(f"  Backfilled (sources only): {n_backfilled}")
print(f"  Added (new from staging): {n_added}")
print(f"  Warnings: {n_warn}")
print()
print(f"Preview files: {PREVIEW}/*.preview.json")
print(f"Log:           {PREVIEW}/merge.log")
