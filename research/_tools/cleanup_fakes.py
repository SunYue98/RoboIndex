#!/usr/bin/env python3
"""Delete the 22 audit-flagged fake/hallucinated entries + clean dangling refs + apply known name corrections."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PUBLIC = ROOT / "public/data"

# Fake / hallucinated entries from audit.md
DELETIONS = {
    # 16 "未知/概念" placeholder concepts (no real product exists)
    "f5", "f11", "f14", "f16", "f17", "f18", "f20", "f27", "f57",
    "f90", "f92", "f94", "f95", "f99", "f116",  # f119 already merged into f1
    # 4 wrong-company / non-existent products
    "f28",   # Ascento RUFUS — Ascento makes Guard quadruped, not a humanoid
    "f102",  # MagicBot 2 — MagicLab doesn't have this version
    "f117",  # Raion LION — Raion makes Raibo quadruped, not humanoid
    "f126",  # CasiVision CASIVIDOT — CasiVision is AOI, not robotics
    # 3 unverifiable arms
    "a3",  # KINO X2 — no such product
    "a5",  # PANDEL — no such arm
    "a7",  # Pudu FLASHBOT ARM — Pudu has FlashBot delivery, not arm
}

# Known name/company corrections from audit.md
CORRECTIONS = {
    # id: {"name": new_name, "company": new_company}
    "h23": {"company": "BrainCo"},  # was AUTODISCOVERY
    "h28": {"company": "WIRobotics"},  # was NXROBOTICS
    "h47": {"company": "MagicLab"},  # was 逐际动力 (which is LimX)
    "h7":  {"name": "PL-WitHand"},  # was PL-METHAND typo
    "h21": {"name": "GMH18"},  # was GM18B typo
    "f6":  {"name": "SPACEO M1"},  # was SPACED M1 typo
    "f13": {"name": "SPACEO Pro"},  # was SPACED P1 typo
    "f19": {"name": "HIVA Haiwa", "company": "Haier"},  # was HAWO HANXI garbled
    "f106": {"name": "SE01"},  # was SEO1 typo
    "f93": {"name": "Mercury X1"},  # was ROBOTART X1
    "f101": {"name": "VersaBot VB-1"},  # was VC-1 typo
    "f109": {"name": "TORA-ONE"},  # was TORA_DOUBLEONE
    "f142": {"name": "Onero H1", "company": "SwitchBot (Wonderlabs)"},  # was OMERO H1 / Ecovacs
    "a4":  {"name": "JAKA K1"},  # was JAKA Zu 5 (bootstrap pointed wrong)
    "a6":  {"name": "ultraArm P340"},  # was PB-340 name-mangling
    "f31": {"name": "AstroDroid AD-01", "company": "INFIFORCE"},  # was Galbot ASTROBO
}

partitions = ["hardware", "software", "ecosystem", "players"]
data = {p: json.loads((PUBLIC / f"{p}.json").read_text(encoding="utf-8")) for p in partitions}

# Phase 1: delete fakes
removed_count = {}
for p in partitions:
    before = len(data[p])
    data[p] = [e for e in data[p] if e["id"] not in DELETIONS]
    removed_count[p] = before - len(data[p])

# Phase 2: apply corrections
n_corrected = 0
for p in partitions:
    for e in data[p]:
        if e["id"] in CORRECTIONS:
            for k, v in CORRECTIONS[e["id"]].items():
                e[k] = v
            n_corrected += 1

# Phase 3: clean dangling relatedIds (point to deleted entries)
existing_ids = set()
for p in partitions:
    for e in data[p]:
        existing_ids.add(e["id"])

n_dangling = 0
for p in partitions:
    for e in data[p]:
        rel = e.get("relatedIds") or []
        cleaned = [r for r in rel if r in existing_ids]
        removed = len(rel) - len(cleaned)
        if removed:
            n_dangling += removed
            e["relatedIds"] = cleaned

# Write back
for p in partitions:
    (PUBLIC / f"{p}.json").write_text(
        json.dumps(data[p], ensure_ascii=False, indent=2), encoding="utf-8"
    )

# Report
print("=== Cleanup report ===\n")
print("Removed fake/hallucinated entries:")
for p, n in removed_count.items():
    if n:
        print(f"  {p}.json: -{n}")
print(f"Applied name/company corrections: {n_corrected}")
print(f"Cleaned dangling relatedIds: {n_dangling}\n")

print("Per-partition counts after cleanup:")
for p in partitions:
    n = len(data[p])
    with_rel = sum(1 for e in data[p] if e.get("relatedIds"))
    print(f"  {p:9s} {n:>4} entries, {with_rel} with relations ({with_rel*100//n if n else 0}%)")
