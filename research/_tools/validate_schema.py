#!/usr/bin/env python3
"""Validate public/data/*.json against the Entity schema and report health.

Phase 1 of the infrastructure upgrade. Checks:
  - Structural integrity: required Entity fields present + correct shape
  - Referential integrity: every relatedIds + relations[].targetId resolves
  - Category validity: all categories are in the allowed enum
  - Source attribution coverage: per-entity, per-category, overall
  - Migration progress: how many entities use new typed Relation / sourcedSpecs
    (Phase 2/3 will fill these; this lets us track over time)
  - Duplicates: same id, same canonicalized name within a category
  - Dangling links: relations / relatedIds pointing to deleted entities
  - URL sanity: sources have an http(s) URL

Exit code:
  0 if no errors (warnings are OK)
  1 if any errors (broken refs, missing required fields, duplicate ids)

Usage:
  python3 research/_tools/validate_schema.py
  python3 research/_tools/validate_schema.py --json  # machine-readable output
  python3 research/_tools/validate_schema.py --strict  # treat warnings as errors
"""
import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "public/data"
PARTITIONS = ["hardware", "software", "ecosystem", "players"]

ALLOWED_CATEGORIES = {
    "整机平台", "机械臂", "灵巧手 & 夹爪", "关节模组", "核心零部件", "传感器",
    "能源动力", "数采 & 遥操", "计算平台",
    "基础模型", "算法框架", "控制算法", "仿真平台", "数据集", "评测基准",
    "开发生态", "应用场景",
    "资本", "产业", "实验室", "人物",
}
SYNTHETIC_CANONICAL = {
    "基础模型", "算法框架", "控制算法", "仿真平台", "数据集", "评测基准", "开发生态", "人物",
}
ALLOWED_RELATION_ROLES = {
    "manufacturer", "invested-in", "competitor", "customer-of", "supplier-to",
    "subsidiary-of", "affiliated-with", "series-member", "tech-base",
    "trained-on", "deployed-at", "related",
    "founder-of", "employed-at", "alumni-of", "advised-by",
}
ALLOWED_SOURCE_TYPES = {"official", "paper", "wiki", "news", "datasheet"}
ALLOWED_CLAIM_CONFIDENCE = {"verified", "reported", "estimated"}

REQUIRED_ENTITY_FIELDS = {"id", "name", "company", "category", "imageUrl", "year", "isNew", "specs"}


class Report:
    def __init__(self):
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.info: list[str] = []
        self.stats: dict = {}

    def err(self, msg: str):
        self.errors.append(msg)

    def warn(self, msg: str):
        self.warnings.append(msg)

    def has_errors(self) -> bool:
        return len(self.errors) > 0


def canon_name(s: str) -> str:
    s = (s or "").lower()
    s = re.sub(r"\([^)]*\)", "", s)
    s = re.sub(r"[^\w一-鿿]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def is_url(u: str) -> bool:
    return isinstance(u, str) and (u.startswith("http://") or u.startswith("https://"))


def validate_source(src: dict, where: str, r: Report):
    if not isinstance(src, dict):
        r.err(f"{where}: source is not an object")
        return
    if "url" not in src or not is_url(src["url"]):
        r.err(f"{where}: source missing or invalid URL ({src.get('url')!r})")
    if "title" not in src or not src["title"]:
        r.warn(f"{where}: source has no title")
    t = src.get("type")
    if t and t not in ALLOWED_SOURCE_TYPES:
        r.warn(f"{where}: source.type={t!r} not in {sorted(ALLOWED_SOURCE_TYPES)}")


def validate_claim(c: dict, where: str, r: Report):
    if not isinstance(c, dict):
        r.err(f"{where}: claim is not an object")
        return
    if "value" not in c:
        r.err(f"{where}: claim missing 'value'")
    if "source" in c and c["source"] is not None:
        validate_source(c["source"], f"{where}.source", r)
    conf = c.get("confidence")
    if conf and conf not in ALLOWED_CLAIM_CONFIDENCE:
        r.warn(f"{where}: claim.confidence={conf!r} not in {sorted(ALLOWED_CLAIM_CONFIDENCE)}")


def validate_relation(rel: dict, where: str, all_ids: set, r: Report):
    if not isinstance(rel, dict):
        r.err(f"{where}: relation is not an object")
        return
    tid = rel.get("targetId")
    if not tid:
        r.err(f"{where}: relation missing targetId")
    elif tid not in all_ids:
        r.err(f"{where}: relation.targetId={tid!r} doesn't exist")
    role = rel.get("role")
    if not role:
        r.err(f"{where}: relation missing role")
    elif role not in ALLOWED_RELATION_ROLES:
        r.err(f"{where}: relation.role={role!r} not in allowed set")
    if "source" in rel and rel["source"] is not None:
        validate_source(rel["source"], f"{where}.source", r)


def validate_entity(e: dict, partition: str, all_ids: set, r: Report):
    eid = e.get("id", "<no-id>")
    where = f"{partition}.json[{eid}]"

    # Required fields
    for f in REQUIRED_ENTITY_FIELDS:
        if f not in e:
            r.err(f"{where}: missing required field '{f}'")

    # Category check
    cat = e.get("category")
    if cat and cat not in ALLOWED_CATEGORIES:
        r.err(f"{where}: category={cat!r} not in allowed enum")

    # ID format
    if eid and not re.match(r"^[a-zA-Z0-9_-]+$", eid):
        r.warn(f"{where}: id contains unusual characters")

    # relatedIds
    for rel_id in e.get("relatedIds") or []:
        if rel_id not in all_ids:
            r.err(f"{where}: relatedIds entry {rel_id!r} doesn't exist")

    # Typed relations (Phase 2 fills these)
    for i, rel in enumerate(e.get("relations") or []):
        validate_relation(rel, f"{where}.relations[{i}]", all_ids, r)

    # sourcedSpecs (Phase 3 fills these)
    for key, claim in (e.get("sourcedSpecs") or {}).items():
        validate_claim(claim, f"{where}.sourcedSpecs[{key}]", r)

    # Top-level sources
    for i, src in enumerate(e.get("sources") or []):
        validate_source(src, f"{where}.sources[{i}]", r)

    # Funding rounds — every round MUST have source
    for i, fr in enumerate(e.get("fundingRounds") or []):
        if not isinstance(fr, dict):
            r.err(f"{where}.fundingRounds[{i}]: not an object")
            continue
        src = fr.get("source")
        if not src:
            r.err(f"{where}.fundingRounds[{i}]: missing source")
        else:
            validate_source(src, f"{where}.fundingRounds[{i}].source", r)

    # Year format sanity
    yr = e.get("year")
    if yr and not re.match(r"^\d{4}(-\d{2})?$", str(yr)):
        r.warn(f"{where}: year={yr!r} not in YYYY or YYYY-MM format")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true", help="Output JSON report")
    ap.add_argument("--strict", action="store_true", help="Warnings → errors")
    args = ap.parse_args()

    r = Report()

    # Load all partitions
    all_entities = []  # list of (partition, entity)
    all_ids = set()
    id_counter = Counter()
    for p in PARTITIONS:
        path = DATA / f"{p}.json"
        if not path.exists():
            r.err(f"Missing partition file: {path}")
            continue
        try:
            arr = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            r.err(f"{p}.json: invalid JSON — {e}")
            continue
        if not isinstance(arr, list):
            r.err(f"{p}.json: top-level is not a list")
            continue
        for e in arr:
            eid = e.get("id")
            if eid:
                id_counter[eid] += 1
                all_ids.add(eid)
            all_entities.append((p, e))

    # Duplicate id check
    for eid, n in id_counter.items():
        if n > 1:
            r.err(f"Duplicate id across partitions: {eid!r} appears {n}×")

    # Duplicate name within a category
    name_to_ids = defaultdict(list)
    for _, e in all_entities:
        key = (e.get("category"), canon_name(e.get("name", "")))
        if key[1]:
            name_to_ids[key].append(e.get("id"))
    for (cat, name), ids in name_to_ids.items():
        if len(ids) > 1:
            r.warn(f"Duplicate name in {cat}: {name!r} → {ids}")

    # Validate each entity
    for p, e in all_entities:
        validate_entity(e, p, all_ids, r)

    # ---- Compute stats ----
    s = r.stats
    s["total_entities"] = len(all_entities)
    s["by_partition"] = dict(Counter(p for p, _ in all_entities))
    s["by_category"] = dict(Counter(e.get("category", "?") for _, e in all_entities))

    # Source attribution coverage
    with_sources = sum(1 for _, e in all_entities if e.get("sources"))
    s["source_coverage"] = {
        "with_sources": with_sources,
        "total": len(all_entities),
        "pct": with_sources * 100 // max(1, len(all_entities)),
    }

    # Image coverage (real + synthetic-canonical)
    real_img = synth_canon = neither = 0
    for _, e in all_entities:
        if e.get("imageUrl"):
            real_img += 1
        elif e.get("category") in SYNTHETIC_CANONICAL:
            synth_canon += 1
        else:
            neither += 1
    s["image_coverage"] = {
        "real": real_img,
        "synthetic_canonical": synth_canon,
        "missing": neither,
        "total": len(all_entities),
    }

    # Migration progress: new schema fields
    using_typed_relations = sum(1 for _, e in all_entities if e.get("relations"))
    using_legacy_related = sum(1 for _, e in all_entities if e.get("relatedIds") and not e.get("relations"))
    using_sourced_specs = sum(1 for _, e in all_entities if e.get("sourcedSpecs"))
    using_legacy_specs_only = sum(
        1 for _, e in all_entities
        if e.get("specs") and not e.get("sourcedSpecs")
    )
    s["migration_progress"] = {
        "typed_relations": using_typed_relations,
        "legacy_relatedIds_only": using_legacy_related,
        "sourcedSpecs": using_sourced_specs,
        "legacy_specs_only": using_legacy_specs_only,
    }

    # Funding rounds coverage (already at Claim-like maturity)
    with_funding = sum(1 for _, e in all_entities if e.get("fundingRounds"))
    s["funding_rounds_authored_on"] = with_funding

    # Cross-link density (avg relations + relatedIds per entity)
    total_rel = sum(len(e.get("relatedIds") or []) + len(e.get("relations") or []) for _, e in all_entities)
    s["avg_relations_per_entity"] = round(total_rel / max(1, len(all_entities)), 2)

    # Top problematic categories by source-coverage gap
    cat_sources = defaultdict(lambda: [0, 0])  # [with_sources, total]
    for _, e in all_entities:
        c = e.get("category", "?")
        cat_sources[c][1] += 1
        if e.get("sources"):
            cat_sources[c][0] += 1
    cat_coverage = {
        c: (w, t, w * 100 // max(1, t))
        for c, (w, t) in cat_sources.items()
    }
    s["category_source_coverage"] = cat_coverage

    # ---- Emit ----
    if args.json:
        out = {
            "errors": r.errors,
            "warnings": r.warnings,
            "stats": s,
            "ok": not r.has_errors(),
        }
        print(json.dumps(out, ensure_ascii=False, indent=2))
        sys.exit(0 if not r.has_errors() else 1)

    # Human-readable
    print("=" * 60)
    print("RoboIndex schema validation")
    print("=" * 60)
    print(f"\nTotal entities: {s['total_entities']}")
    print(f"By partition: {s['by_partition']}")

    print(f"\nSource attribution:")
    sc = s["source_coverage"]
    print(f"  {sc['with_sources']}/{sc['total']} entities have ≥1 source ({sc['pct']}%)")

    print(f"\nImage coverage:")
    ic = s["image_coverage"]
    print(f"  Real:      {ic['real']:4d} / {ic['total']}")
    print(f"  Synthetic-canonical: {ic['synthetic_canonical']:4d} (software/dev-tool default)")
    print(f"  Still missing:       {ic['missing']:4d}")

    print(f"\nMigration progress (Phase 2/3 targets):")
    mp = s["migration_progress"]
    print(f"  Using typed relations:        {mp['typed_relations']}  ← Phase 2 target")
    print(f"  Legacy relatedIds (untyped):  {mp['legacy_relatedIds_only']}")
    print(f"  Using sourcedSpecs (Claim):   {mp['sourcedSpecs']}  ← Phase 3 target")
    print(f"  Legacy specs only:            {mp['legacy_specs_only']}")
    print(f"  Funding rounds authored on:   {s['funding_rounds_authored_on']}  (already Claim-like)")

    print(f"\nAvg relations per entity: {s['avg_relations_per_entity']}")

    print(f"\nSource coverage by category (worst-first):")
    sorted_cats = sorted(cat_coverage.items(), key=lambda kv: kv[1][2])
    for c, (w, t, pct) in sorted_cats:
        bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
        print(f"  {c:12s} [{bar}]  {w:3d}/{t:3d}  ({pct}%)")

    # Errors and warnings
    if r.errors:
        print(f"\n❌ {len(r.errors)} ERROR(S):")
        for e in r.errors[:50]:
            print(f"  - {e}")
        if len(r.errors) > 50:
            print(f"  ... and {len(r.errors) - 50} more")

    if r.warnings:
        print(f"\n⚠️  {len(r.warnings)} WARNING(S):")
        shown = 20
        for w in r.warnings[:shown]:
            print(f"  - {w}")
        if len(r.warnings) > shown:
            print(f"  ... and {len(r.warnings) - shown} more")

    if not r.errors and not r.warnings:
        print("\n✅ No errors, no warnings.")
    elif not r.errors:
        print(f"\n✅ No errors. ({len(r.warnings)} warnings.)")
    else:
        print(f"\n❌ {len(r.errors)} errors. Fix before next migration phase.")

    fail = r.has_errors() or (args.strict and r.warnings)
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
