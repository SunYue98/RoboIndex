#!/usr/bin/env python3
"""Image collection priority queue.

Scans all entities, scores them by "visibility × placeholder × novelty", and
outputs a ranked todo list of which images to collect next. Designed to be
re-run after each batch to surface the next highest-value 30 entries.

Score components:
  - relatedIds count (how often this entity is linked from other cards)
  - category weight (high-traffic categories score higher)
  - isNew bonus (recently launched products = users will look for these)
  - flagship boost (entities that anchor a series_id chain get extra)

Outputs:
  - Default: pretty markdown table written to research/IMAGE_QUEUE.md (top N)
  - --json: machine-readable for piping
  - --done: also show entities WITH real images (for verifying)
  - --partition <name>: filter to one partition

Usage:
  python3 research/_tools/audit_images.py            # write IMAGE_QUEUE.md (top 30)
  python3 research/_tools/audit_images.py --top 100  # top 100
  python3 research/_tools/audit_images.py --partition players
"""
import argparse
import json
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "public/data"
PARTITIONS = ["hardware", "software", "ecosystem", "players"]

# Categories whose synthetic title card IS the canonical visual (per IMAGE_SPEC.md
# prototype B). These should not be counted as "missing" — the synthetic IS the
# image. Mirrors SYNTHETIC_CANONICAL_CATEGORIES in src/data/entities.ts.
SYNTHETIC_CANONICAL_CATEGORIES = {
    "基础模型", "算法框架", "控制算法", "仿真平台", "数据集", "评测基准", "开发生态", "人物",
}

# Category weights (visibility heuristic) — higher = more user-facing
CATEGORY_WEIGHT = {
    "整机平台": 20,
    "基础模型": 18,
    "产业": 15,
    "应用场景": 15,
    "灵巧手 & 夹爪": 12,
    "机械臂": 12,
    "仿真平台": 10,
    "传感器": 10,
    "计算平台": 10,
    "数据集": 10,
    "实验室": 8,
    "资本": 8,
    "算法框架": 8,
    "控制算法": 7,
    "评测基准": 7,
    "开发生态": 7,
    "关节模组": 6,
    "核心零部件": 6,
    "能源动力": 5,
    "数采 & 遥操": 5,
}

# Hints for where to look — by prototype
COLLECTION_HINTS = {
    "整机平台": "厂商 press kit / 官网产品页 / IEEE Spectrum / Robot Report",
    "灵巧手 & 夹爪": "datasheet / 厂商产品页",
    "机械臂": "datasheet / 厂商产品页",
    "关节模组": "datasheet 首页",
    "核心零部件": "datasheet / 分销商网站",
    "传感器": "datasheet / 厂商产品页",
    "计算平台": "datasheet / 厂商产品页",
    "能源动力": "datasheet / 厂商产品页",
    "数采 & 遥操": "厂商产品页",
    "基础模型": "论文 figure / GitHub README hero",
    "算法框架": "GitHub README / 论文",
    "控制算法": "GitHub README / 论文",
    "仿真平台": "官网截图 / 论文",
    "数据集": "项目主页 sample / 论文",
    "评测基准": "leaderboard / 论文",
    "开发生态": "项目官网 logo / GitHub",
    "应用场景": "厂商客户案例页 / 媒体报道",
    "产业": "公司官网 press / Wikipedia infobox",
    "资本": "VC 官网 brand page / Crunchbase",
    "实验室": "Wikipedia / 大学官网 / GitHub org avatar",
}


def load_all():
    entities = []
    for p in PARTITIONS:
        for e in json.loads((DATA / f"{p}.json").read_text(encoding="utf-8")):
            e["_partition"] = p
            entities.append(e)
    return entities


def score(entity, series_anchors: set) -> int:
    s = 0
    s += len(entity.get("relatedIds", []) or [])
    s += CATEGORY_WEIGHT.get(entity.get("category", ""), 5)
    if entity.get("isNew"):
        s += 5
    if entity["id"] in series_anchors:
        s += 8  # first/last in a series gets a boost
    # Penalize entries that mostly carry placeholder-shaped specs
    specs = entity.get("specs") or {}
    if len(specs) <= 2:
        s -= 3
    return s


def detect_series_anchors(entities):
    """Identify head/tail of each evolution chain (most visible products)."""
    by_series = {}
    for e in entities:
        sid = e.get("seriesId")
        if not sid:
            continue
        by_series.setdefault(sid, []).append(e)
    anchors = set()
    for sid, members in by_series.items():
        members.sort(key=lambda x: x.get("seriesOrder", 0))
        if members:
            anchors.add(members[0]["id"])
            anchors.add(members[-1]["id"])
    return anchors


def emit_markdown(rows, total_missing, total_entities):
    lines = []
    lines.append("# 图片收集优先级队列")
    lines.append("")
    lines.append(f"自动生成 by `research/_tools/audit_images.py`。共 {total_entities} 条 entity，{total_missing} 条缺真图（{total_missing*100//total_entities}%）。")
    lines.append("")
    lines.append("评分逻辑：`relatedIds 数 + 类别权重 + isNew + 系列首/尾 boost`。每完成一批后重跑本脚本会刷新清单。")
    lines.append("")
    lines.append("## 待办（按优先级排序）")
    lines.append("")
    lines.append("| ✓ | 优先级 | ID | 名称 | 公司 | 类别 | 关联数 | 收集来源建议 |")
    lines.append("|---|---:|---|---|---|---|---:|---|")
    for r in rows:
        hint = COLLECTION_HINTS.get(r["category"], "")
        name = r["name"].replace("|", "\\|")[:30]
        company = (r["company"] or "")[:25].replace("|", "\\|")
        lines.append(
            f"| ☐ | {r['score']} | `{r['id']}` | {name} | {company} | {r['category']} | {r['n_related']} | {hint} |"
        )
    lines.append("")
    lines.append("## 处理工作流提醒")
    lines.append("")
    lines.append("1. 收原图到 `raw_images/<id>.{jpg|png}`（这个目录已 gitignore）")
    lines.append("2. 跑 `python3 research/_tools/process_image.py raw_images/<id>.jpg --entity <id> [--remove-bg] [--format png]`")
    lines.append("3. 把生成的相对路径写进 `public/data/<partition>.json` 的 `imageUrl` 字段")
    lines.append("4. `npm run dev` 视觉过一遍")
    lines.append("5. 一批 30 张后 commit 一次，然后重跑本脚本刷新优先级队列")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--top", type=int, default=30, help="Top N entries to list (default: 30)")
    ap.add_argument("--partition", choices=PARTITIONS, help="Restrict to one partition")
    ap.add_argument("--json", action="store_true", help="Emit JSON instead of writing markdown")
    ap.add_argument("--done", action="store_true", help="Also show entries WITH real images")
    ap.add_argument("--out", default="research/IMAGE_QUEUE.md", help="Output path for markdown")
    args = ap.parse_args()

    entities = load_all()
    if args.partition:
        entities = [e for e in entities if e["_partition"] == args.partition]

    series_anchors = detect_series_anchors(entities)

    missing = []
    for e in entities:
        has_real = bool(e.get("imageUrl"))
        # Software / dev-tool categories: synthetic IS canonical, skip from queue
        if not has_real and e.get("category") in SYNTHETIC_CANONICAL_CATEGORIES and not args.done:
            continue
        if has_real and not args.done:
            continue
        sc = score(e, series_anchors)
        missing.append({
            "id": e["id"],
            "name": e["name"],
            "company": e.get("company", ""),
            "category": e.get("category", ""),
            "partition": e["_partition"],
            "score": sc,
            "n_related": len(e.get("relatedIds", []) or []),
            "has_real_image": has_real,
            "isNew": bool(e.get("isNew")),
        })

    missing.sort(key=lambda x: (-x["score"], x["partition"], x["id"]))
    rows = missing[: args.top]

    # "missing" = needs a real image. Synthetic-canonical categories are spec-compliant
    # without a real imageUrl so they're not counted as missing.
    total_missing = sum(
        1 for e in entities
        if not e.get("imageUrl") and e.get("category") not in SYNTHETIC_CANONICAL_CATEGORIES
    )
    total = len(entities)

    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return

    out_path = ROOT / args.out
    md = emit_markdown(rows, total_missing, total)
    out_path.write_text(md, encoding="utf-8")
    print(f"=== audit_images.py ===")
    print(f"Total entities: {total}")
    print(f"Missing real image: {total_missing} ({total_missing*100//total}%)")
    print(f"Written top {args.top} to {out_path.relative_to(ROOT)}")

    # Print top-5 inline as a teaser
    print("\nTop 5 right now:")
    for r in rows[:5]:
        print(f"  {r['score']:3d}  [{r['category']:8s}]  {r['id']:25s}  {r['name'][:35]}")

    # Coverage breakdown by category — synthetic-canonical categories count as 100%
    by_cat = Counter()
    real_by_cat = Counter()
    for e in entities:
        c = e.get("category", "?")
        by_cat[c] += 1
        if e.get("imageUrl") or c in SYNTHETIC_CANONICAL_CATEGORIES:
            real_by_cat[c] += 1
    print("\nCoverage by category (synthetic-canonical categories shown with †):")
    for cat, total_in_cat in sorted(by_cat.items(), key=lambda x: -x[1]):
        real = real_by_cat[cat]
        pct = real * 100 // total_in_cat
        bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
        tag = "†" if cat in SYNTHETIC_CANONICAL_CATEGORIES else " "
        print(f"  {cat:12s} {tag} [{bar}]  {real:3d}/{total_in_cat:3d}  ({pct}%)")


if __name__ == "__main__":
    main()
