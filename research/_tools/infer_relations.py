#!/usr/bin/env python3
"""Phase 2 — Migrate `relatedIds: string[]` → `relations: Relation[]` with inferred roles.

Strategy:
  - For each entity, iterate its relatedIds.
  - For each (this_category, target_category) pair, look up the canonical role
    in CATEGORY_PAIR_TO_ROLE.
  - If a specific rule fires → add typed Relation, remove tid from relatedIds.
  - If no rule fires (no entry, or fallback to 'related') → KEEP in relatedIds.
    These remain visible to the UI as "未分类关系" and surface as targets for
    manual review.

Authoring conventions ("which side authors the edge"):
  - Asymmetric edges are authored on the side where the fact is most natural:
    hardware authors its manufacturer; VC authors its investments; model
    authors its training data, etc. The other side gets a derived inverse
    view at UI render time (built from the reverse index).
  - Symmetric edges (affiliated-with, series-member, competitor, related) are
    authored on BOTH sides.

Same-category edges:
  - If both entities share a seriesId → 'series-member'
  - Otherwise → SAME_CAT_DEFAULT[category] (competitor for hardware/products,
    'related' for capital/lab where competition is less crisp)

Usage:
  python3 research/_tools/infer_relations.py             # do the migration
  python3 research/_tools/infer_relations.py --dry-run   # report only, no writes
"""
import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "public/data"
PARTITIONS = ["hardware", "software", "ecosystem", "players"]

# Hardware categories (so we can match wildcards below)
HARDWARE_CATS = [
    "整机平台", "机械臂", "灵巧手 & 夹爪", "关节模组",
    "核心零部件", "传感器", "能源动力", "数采 & 遥操", "计算平台",
]

# FORWARD_RULES — (this.category, target.category) → role
# These describe the CANONICAL authoring direction of the relation. The reverse
# direction will be auto-derived below as INVERSE_RULES (with isInverse=true).
FORWARD_RULES: dict[tuple[str, str], str] = {
    # Hardware → 产业 = "I am made by them"
    **{(hw, "产业"): "manufacturer" for hw in HARDWARE_CATS},
    # 资本 → 产业 = "I invested in them"
    ("资本", "产业"): "invested-in",
    # 基础模型 → 数据集 / 评测基准 = "I was trained on / evaluated on this"
    ("基础模型", "数据集"): "trained-on",
    ("基础模型", "评测基准"): "trained-on",
    # Software / algorithm → framework / simulator = "I depend on this"
    ("基础模型", "算法框架"): "tech-base",
    ("控制算法", "算法框架"): "tech-base",
    ("控制算法", "仿真平台"): "tech-base",
    ("基础模型", "仿真平台"): "tech-base",
    # Software → hardware = "I am deployed on this"
    ("基础模型", "整机平台"): "deployed-at",
    ("算法框架", "整机平台"): "deployed-at",
    ("控制算法", "整机平台"): "deployed-at",
    # Hardware integration: whole-body uses components
    ("整机平台", "机械臂"): "tech-base",
    ("整机平台", "灵巧手 & 夹爪"): "tech-base",
    ("整机平台", "关节模组"): "tech-base",
    ("整机平台", "核心零部件"): "tech-base",
    ("整机平台", "传感器"): "tech-base",
    ("整机平台", "计算平台"): "tech-base",
    ("整机平台", "能源动力"): "tech-base",
    # Arms / hands also depend on lower-level components
    ("机械臂", "关节模组"): "tech-base",
    ("机械臂", "核心零部件"): "tech-base",
    ("机械臂", "传感器"): "tech-base",
    ("灵巧手 & 夹爪", "关节模组"): "tech-base",
    ("灵巧手 & 夹爪", "核心零部件"): "tech-base",
    ("灵巧手 & 夹爪", "传感器"): "tech-base",
    # Hardware → application = "I am deployed in this scenario"
    **{(hw, "应用场景"): "deployed-at" for hw in HARDWARE_CATS},
    # 产业 → 应用场景 = "I (the company) operate in this scenario" — author on company side too
    ("产业", "应用场景"): "deployed-at",
    # Dev tools → framework / simulator
    ("开发生态", "算法框架"): "tech-base",
    ("开发生态", "仿真平台"): "tech-base",
    # Model ↔ producing org (lab or company): treat the org as the producer
    ("基础模型", "产业"): "manufacturer",       # company "made" this model
    ("数据集", "产业"): "manufacturer",         # company "released" this dataset
    ("仿真平台", "产业"): "manufacturer",
    ("算法框架", "产业"): "manufacturer",
    ("评测基准", "产业"): "manufacturer",
    ("控制算法", "产业"): "manufacturer",
}

# SYMMETRIC_RULES — both sides author the edge (no canonical side); no inverse marker.
SYMMETRIC_RULES: dict[tuple[str, str], str] = {
    # Lab affiliation
    ("实验室", "实验室"): "affiliated-with",
    ("实验室", "产业"): "affiliated-with",
    ("产业", "实验室"): "affiliated-with",
    ("实验室", "基础模型"): "affiliated-with",
    ("基础模型", "实验室"): "affiliated-with",
    ("实验室", "数据集"): "affiliated-with",
    ("数据集", "实验室"): "affiliated-with",
    ("实验室", "评测基准"): "affiliated-with",
    ("评测基准", "实验室"): "affiliated-with",
    ("实验室", "控制算法"): "affiliated-with",
    ("控制算法", "实验室"): "affiliated-with",
    ("实验室", "算法框架"): "affiliated-with",
    ("算法框架", "实验室"): "affiliated-with",
    ("实验室", "仿真平台"): "affiliated-with",
    ("仿真平台", "实验室"): "affiliated-with",
    # Framework ↔ benchmark / simulator (often paired)
    ("算法框架", "仿真平台"): "tech-base",
    ("仿真平台", "算法框架"): "tech-base",
    ("仿真平台", "评测基准"): "related",
    ("评测基准", "仿真平台"): "related",
}

# Build INVERSE_RULES automatically from FORWARD_RULES.
# These mark relations on the non-canonical side with isInverse=true.
INVERSE_RULES: dict[tuple[str, str], str] = {
    (c2, c1): role for (c1, c2), role in FORWARD_RULES.items()
}

# Same-category default role. Series-member always wins if both have same seriesId.
SAME_CAT_DEFAULT: dict[str, str] = {
    "整机平台": "competitor",
    "机械臂": "competitor",
    "灵巧手 & 夹爪": "competitor",
    "关节模组": "competitor",
    "核心零部件": "competitor",
    "传感器": "competitor",
    "能源动力": "competitor",
    "数采 & 遥操": "competitor",
    "计算平台": "competitor",
    "基础模型": "competitor",
    "算法框架": "competitor",
    "控制算法": "competitor",
    "仿真平台": "competitor",
    "数据集": "related",          # datasets don't compete
    "评测基准": "related",         # benchmarks don't compete (they're complementary)
    "开发生态": "related",
    "应用场景": "related",
    "产业": "competitor",
    "资本": "related",            # VCs don't compete in our framing
    "实验室": "affiliated-with",  # labs are peers
}


def infer_role(this_entity: dict, target_entity: dict) -> tuple[str, bool] | None:
    """Return (role, isInverse) for this→target, or None if not inferable."""
    c1 = this_entity.get("category")
    c2 = target_entity.get("category")
    if not c1 or not c2:
        return None
    pair = (c1, c2)

    # Same-category: series first, then default
    if c1 == c2:
        s1 = this_entity.get("seriesId")
        s2 = target_entity.get("seriesId")
        if s1 and s1 == s2:
            return ("series-member", False)
        d = SAME_CAT_DEFAULT.get(c1)
        return (d, False) if d else None

    # Symmetric → no inverse marker
    if pair in SYMMETRIC_RULES:
        return (SYMMETRIC_RULES[pair], False)
    # Forward canonical
    if pair in FORWARD_RULES:
        return (FORWARD_RULES[pair], False)
    # Inverse canonical
    if pair in INVERSE_RULES:
        return (INVERSE_RULES[pair], True)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="Report classifications without writing JSON")
    args = ap.parse_args()

    data = {p: json.loads((DATA / f"{p}.json").read_text(encoding="utf-8")) for p in PARTITIONS}
    id_to_entity = {e["id"]: e for arr in data.values() for e in arr}

    by_role = Counter()
    unclassified_pairs = Counter()   # for refinement
    entities_with_relations = 0
    edges_migrated = 0
    edges_kept = 0
    new_relations_total = 0

    for arr in data.values():
        for e in arr:
            related = e.get("relatedIds") or []
            if not related:
                continue
            new_relations = list(e.get("relations") or [])
            kept_related = []
            existing_targets = {r.get("targetId") for r in new_relations}

            for tid in related:
                target = id_to_entity.get(tid)
                if not target:
                    continue
                inferred = infer_role(e, target)
                if inferred:
                    role, is_inv = inferred
                    if tid not in existing_targets:
                        rel = {"targetId": tid, "role": role}
                        if is_inv:
                            rel["isInverse"] = True
                        new_relations.append(rel)
                        existing_targets.add(tid)
                        new_relations_total += 1
                    by_role[role + (" (inverse)" if is_inv else "")] += 1
                    edges_migrated += 1
                else:
                    kept_related.append(tid)
                    edges_kept += 1
                    unclassified_pairs[(e.get("category"), target.get("category"))] += 1

            if new_relations:
                if not args.dry_run:
                    e["relations"] = new_relations
                entities_with_relations += 1
            if kept_related:
                if not args.dry_run:
                    e["relatedIds"] = kept_related
            else:
                if not args.dry_run:
                    e.pop("relatedIds", None)

    # Write
    if not args.dry_run:
        for p in PARTITIONS:
            (DATA / f"{p}.json").write_text(
                json.dumps(data[p], ensure_ascii=False, indent=2), encoding="utf-8"
            )

    # Report
    print(f"=== infer_relations.py {'(dry-run)' if args.dry_run else ''} ===\n")
    print(f"Edges migrated:        {edges_migrated}")
    print(f"Edges kept in relatedIds (unclassified): {edges_kept}")
    print(f"New typed relations written: {new_relations_total}")
    print(f"Entities with at least one typed relation: {entities_with_relations}")
    print(f"\nBy role:")
    for role, n in sorted(by_role.items(), key=lambda x: -x[1]):
        print(f"  {role:20s} {n}")

    if unclassified_pairs:
        print(f"\nUnclassified category pairs (top 20):")
        for (c1, c2), n in unclassified_pairs.most_common(20):
            print(f"  {n:4d}  {c1!s:14s} → {c2!s}")


if __name__ == "__main__":
    main()
