#!/usr/bin/env python3
"""Remove noise edges introduced when Pass G/F treated generic company strings
(e.g. 'Various', 'Open Source', '未知 / 概念', 'Multi-institution') as if they
were single companies — this caused all 应用场景 entries to cross-link.

Also generally cleans:
  - relatedIds pointing to non-existent ids (shouldn't happen, defensive)
  - self-references
  - duplicates within a single entry's relatedIds list
"""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PUBLIC = ROOT / "public/data"

partitions = ["hardware", "software", "ecosystem", "players"]
data = {p: json.loads((PUBLIC / f"{p}.json").read_text(encoding="utf-8")) for p in partitions}
all_entries = []
id_to_entry = {}
for p, lst in data.items():
    for e in lst:
        e["_p"] = p
        all_entries.append(e)
        id_to_entry[e["id"]] = e
existing = set(id_to_entry.keys())


def canon_co(s):
    if not s: return ""
    return re.sub(r"[^\w一-鿿]+", "", re.sub(r"\([^)]*\)", "", s.lower()))


# Companies that aren't real companies — entries with these strings shouldn't be
# treated as "same vendor" for sibling linking
GENERIC_COMPANIES = {
    "various", "openSource", "opensource", "academic", "未知概念",
    "multiinstitution", "various",
    "industrialacademic",  # MPC entry
}

# Identify noise edges to remove: edges between two entries from same category +
# both have generic company.
def is_generic_company(s):
    c = canon_co(s)
    return c in GENERIC_COMPANIES or "various" in c or "concept" in c or "未知" in c

# Build a list of "groups" where Pass G/F would have linked entries via generic companies
groups_noise = []  # list of {category, generic, ids}
import collections
by_cat_co = collections.defaultdict(list)
for e in all_entries:
    if is_generic_company(e.get("company", "")):
        by_cat_co[(e["category"], canon_co(e.get("company", "")))].append(e["id"])
for (cat, co), ids in by_cat_co.items():
    if len(ids) >= 2:
        groups_noise.append((cat, co, set(ids)))

# Remove pairwise edges among entries in these noise groups
n_removed = 0
for cat, co, ids in groups_noise:
    for src_id in ids:
        e = id_to_entry.get(src_id)
        if not e:
            continue
        rel = e.get("relatedIds") or []
        cleaned = [r for r in rel if r not in ids or r == src_id]
        removed_here = len(rel) - len(cleaned)
        if removed_here:
            n_removed += removed_here
            e["relatedIds"] = cleaned

# General defensive cleanup
for e in all_entries:
    rel = e.get("relatedIds") or []
    if not rel:
        continue
    # Drop self-refs, missing ids, dupes
    seen = set()
    cleaned = []
    for r in rel:
        if r == e["id"] or r not in existing or r in seen:
            continue
        cleaned.append(r)
        seen.add(r)
    if len(cleaned) != len(rel):
        e["relatedIds"] = cleaned

# Write back
for p in partitions:
    for e in data[p]:
        e.pop("_p", None)
    (PUBLIC / f"{p}.json").write_text(
        json.dumps(data[p], ensure_ascii=False, indent=2), encoding="utf-8"
    )

print(f"=== fix_noise_edges report ===")
print(f"  Noise groups identified (generic company + same category, ≥2 entries):")
for cat, co, ids in groups_noise:
    print(f"    [{cat}] '{co}' — {len(ids)} entries")
print(f"\n  Pairwise edges removed: {n_removed}")
print()
for p in partitions:
    n = len(data[p])
    with_rel = sum(1 for e in data[p] if e.get("relatedIds"))
    total = sum(len(e.get("relatedIds") or []) for e in data[p])
    print(f"  {p:9s} {n:>4} entries, {with_rel} with relations ({with_rel*100//n}%), total edges {total}")
