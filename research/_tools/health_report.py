#!/usr/bin/env python3
"""Phase 7 — Generate `research/HEALTH.md`, the omnibus health dashboard.

Aggregates output from:
  - research/_tools/validate_schema.py    (schema errors, source coverage)
  - research/_tools/check_bias.py         (region / era / stage / gender)
  - research/_tools/check_url_liveness.py (dead links — uses cache, does NOT
                                          make network calls)
  - research/_tools/audit_images.py       (image coverage)
  - public/api/summary.json               (degree, top nodes, rel-role mix)

Re-run anytime to refresh:
  python3 research/_tools/health_report.py
"""
import json
import re
import subprocess
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "public/data"
API = ROOT / "public/api"
CACHE_DIR = ROOT / "research/_health_cache"
HEALTH_MD = ROOT / "research/HEALTH.md"
PARTITIONS = ["hardware", "software", "ecosystem", "players"]

SYNTHETIC_CANONICAL = {
    "基础模型", "算法框架", "控制算法", "仿真平台", "数据集", "评测基准", "开发生态", "人物",
}


def run_validate() -> dict:
    """Run validate_schema.py in JSON mode and parse."""
    try:
        proc = subprocess.run(
            ["python3", str(ROOT / "research/_tools/validate_schema.py"), "--json"],
            capture_output=True, text=True, timeout=60,
        )
        return json.loads(proc.stdout)
    except Exception as e:
        return {"errors": [str(e)], "warnings": [], "stats": {}, "ok": False}


def load_summary() -> dict:
    if (API / "summary.json").exists():
        return json.loads((API / "summary.json").read_text(encoding="utf-8"))
    return {}


def load_url_cache() -> dict:
    cache = CACHE_DIR / "url_status.json"
    if cache.exists():
        try:
            return json.loads(cache.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def extract_country(entity: dict) -> str | None:
    loc = (entity.get("orgInfo") or {}).get("location") or ""
    parts = [p.strip() for p in re.split(r"[,，;]", loc) if p.strip()]
    if not parts:
        return None
    last = parts[-1]
    aliases = {
        "USA": "USA", "United States": "USA", "US": "USA",
        "UK": "UK", "United Kingdom": "UK",
        "China": "China", "中国": "China",
        "CA": "USA", "WA": "USA", "NY": "USA", "MA": "USA", "TX": "USA",
    }
    return aliases.get(last, last)


def load_all_entities() -> list[dict]:
    out = []
    for p in PARTITIONS:
        out.extend(json.loads((DATA / f"{p}.json").read_text(encoding="utf-8")))
    return out


def compute_bias_buckets(entities: list[dict]) -> dict:
    region = Counter()
    era = Counter()
    for e in entities:
        c = extract_country(e)
        if c:
            region[c] += 1
        y_str = (e.get("year") or "")[:4]
        if re.match(r"^\d{4}$", y_str):
            y = int(y_str)
            if y < 2000:
                era["<2000"] += 1
            elif y < 2010:
                era["2000-2009"] += 1
            elif y < 2015:
                era["2010-2014"] += 1
            elif y < 2020:
                era["2015-2019"] += 1
            elif y < 2024:
                era["2020-2023"] += 1
            else:
                era["≥2024"] += 1
    return {"region": region, "era": era}


def compute_image_coverage(entities: list[dict]) -> dict:
    real = synth = neither = 0
    by_cat = defaultdict(lambda: {"real": 0, "synth": 0, "missing": 0, "total": 0})
    for e in entities:
        cat = e.get("category", "?")
        by_cat[cat]["total"] += 1
        if e.get("imageUrl"):
            real += 1
            by_cat[cat]["real"] += 1
        elif cat in SYNTHETIC_CANONICAL:
            synth += 1
            by_cat[cat]["synth"] += 1
        else:
            neither += 1
            by_cat[cat]["missing"] += 1
    return {"real": real, "synth": synth, "missing": neither, "by_cat": dict(by_cat)}


def grade(pct: int) -> str:
    if pct >= 95: return "🟢"
    if pct >= 80: return "🟡"
    if pct >= 50: return "🟠"
    return "🔴"


def main():
    validate = run_validate()
    stats = validate.get("stats", {})
    summary = load_summary()
    url_cache = load_url_cache()
    entities = load_all_entities()
    bias = compute_bias_buckets(entities)
    img = compute_image_coverage(entities)

    n_total = stats.get("total_entities", len(entities))
    n_err = len(validate.get("errors", []))
    n_warn = len(validate.get("warnings", []))

    # URL liveness summary
    url_cats = Counter()
    for u, info in url_cache.items():
        url_cats[info.get("category", "unchecked")] += 1
    url_total = sum(url_cats.values())
    dead_urls = url_cats.get("client_error", 0)
    url_check_dates = sorted(set(c.get("checked_at", "?") for c in url_cache.values()))
    last_url_check = url_check_dates[-1] if url_check_dates else "never"

    # Compose markdown
    out = [
        f"# RoboIndex Health Report",
        "",
        f"_Generated: {date.today()}_",
        "",
        "## TL;DR",
        "",
        f"| Metric | Value | Grade |",
        f"|---|---:|:---:|",
    ]

    # Source coverage
    sc = stats.get("source_coverage", {})
    src_pct = sc.get("pct", 0)
    out.append(f"| Schema errors | **{n_err}** | {'🟢' if n_err == 0 else '🔴'} |")
    out.append(f"| Source attribution coverage | {sc.get('with_sources',0)}/{n_total} ({src_pct}%) | {grade(src_pct)} |")
    real_pct = (img['real'] + img['synth']) * 100 // max(1, n_total)
    out.append(f"| Image coverage (real + synthetic-canonical) | {img['real']}+{img['synth']}/{n_total} ({real_pct}%) | {grade(real_pct)} |")
    mp = stats.get("migration_progress", {})
    typed_rel = mp.get("typed_relations", 0)
    typed_pct = typed_rel * 100 // max(1, n_total)
    out.append(f"| Typed relations | {typed_rel}/{n_total} ({typed_pct}%) | {grade(typed_pct)} |")
    sourced = mp.get("sourcedSpecs", 0)
    sourced_pct = sourced * 100 // max(1, n_total)
    out.append(f"| sourcedSpecs (Claim form) | {sourced}/{n_total} ({sourced_pct}%) | {grade(sourced_pct)} |")
    if url_total:
        dead_pct = (url_total - dead_urls) * 100 // url_total
        out.append(f"| URL liveness (cached, {last_url_check}) | {url_total - dead_urls}/{url_total} alive ({dead_pct}%) | {grade(dead_pct)} |")
    else:
        out.append(f"| URL liveness | **never checked** — run `check_url_liveness.py` | 🔴 |")

    out.append("")

    # Migration progress
    out.append("## Migration progress")
    out.append("")
    out.append("| Layer | Status | Last phase |")
    out.append("|---|---|---|")
    out.append(f"| Schema (typed Relation / Claim / per-category schemas) | ✅ complete | Phase 1+3+4 |")
    out.append(f"| relatedIds → typed Relation | ✅ {typed_rel} migrated, {mp.get('legacy_relatedIds_only',0)} legacy-only | Phase 2 |")
    out.append(f"| specs → sourcedSpecs Claim | 🟡 {sourced} migrated, {mp.get('legacy_specs_only',0)} legacy-only | Phase 3 |")
    out.append(f"| People as first-class entities | ✅ 20 seeded | Phase 5 |")
    out.append(f"| Public API layer (/api/*.json,.csv,.md) | ✅ 11 endpoints live | Phase 6 |")
    out.append("")

    # Image coverage by category
    out.append("## Image coverage by category")
    out.append("")
    out.append("| Category | Real | Synthetic (canonical) | Missing | Total | % covered |")
    out.append("|---|---:|---:|---:|---:|---:|")
    for cat in sorted(img["by_cat"].keys(), key=lambda c: -img["by_cat"][c]["total"]):
        d = img["by_cat"][cat]
        covered = d["real"] + d["synth"]
        pct = covered * 100 // max(1, d["total"])
        tag = " †" if cat in SYNTHETIC_CANONICAL else ""
        out.append(f"| {cat}{tag} | {d['real']} | {d['synth']} | {d['missing']} | {d['total']} | {pct}% |")
    out.append("")
    out.append("_† synthetic title card is the canonical visual per IMAGE_SPEC.md_")
    out.append("")

    # Region distribution
    out.append("## Region distribution (where entities have a stated location)")
    out.append("")
    out.append("| Country | Count | Share |")
    out.append("|---|---:|---:|")
    region_total = sum(bias["region"].values())
    for country, n in bias["region"].most_common(15):
        share = n * 100 // max(1, region_total)
        out.append(f"| {country} | {n} | {share}% |")
    if len(bias["region"]) > 15:
        rest = sum(n for _, n in bias["region"].most_common()[15:])
        out.append(f"| *(and {len(bias['region']) - 15} more)* | {rest} | |")
    out.append("")
    out.append(f"_{n_total - region_total} entities have no parseable location._")
    out.append("")

    # Era distribution
    out.append("## Era distribution (founding / release year)")
    out.append("")
    out.append("| Bucket | Count |")
    out.append("|---|---:|")
    for bucket in ["<2000", "2000-2009", "2010-2014", "2015-2019", "2020-2023", "≥2024"]:
        out.append(f"| {bucket} | {bias['era'].get(bucket, 0)} |")
    out.append("")

    # Relation-role distribution (from API summary)
    if summary.get("relation_role_counts"):
        out.append("## Relation roles in the graph")
        out.append("")
        out.append("| Role | Edges |")
        out.append("|---|---:|")
        for role, n in sorted(summary["relation_role_counts"].items(), key=lambda x: -x[1]):
            out.append(f"| `{role}` | {n} |")
        out.append("")

    # Top connected nodes (from API summary)
    if summary.get("top_connected_entities"):
        out.append("## Top 10 most-connected entities")
        out.append("")
        out.append("| Rank | Entity | Category | Degree |")
        out.append("|:---:|---|---|---:|")
        for i, e in enumerate(summary["top_connected_entities"][:10], 1):
            out.append(f"| {i} | {e['name']} | {e['category']} | {e['degree']} |")
        out.append("")

    # Dead URLs (top 10)
    if url_cache:
        dead = [(u, info) for u, info in url_cache.items() if info.get("category") == "client_error"]
        if dead:
            out.append(f"## Dead source URLs ({len(dead)} found, sample of 10)")
            out.append("")
            out.append("| URL | HTTP |")
            out.append("|---|---:|")
            for u, info in dead[:10]:
                u_short = u if len(u) <= 80 else u[:77] + "..."
                out.append(f"| `{u_short}` | {info.get('status', '?')} |")
            out.append("")
            out.append("_Run `check_url_liveness.py --markdown` for the full list + entity references._")
            out.append("")

    # Validation errors / warnings
    if n_err:
        out.append(f"## Schema errors ({n_err}) — must fix")
        out.append("")
        for e in validate["errors"][:20]:
            out.append(f"- {e}")
        out.append("")

    if n_warn and n_warn > 0:
        out.append(f"## Schema warnings ({n_warn})")
        out.append("")
        for w in validate.get("warnings", [])[:10]:
            out.append(f"- {w}")
        if n_warn > 10:
            out.append(f"- *(and {n_warn - 10} more)*")
        out.append("")

    # Self-reflection — known gaps
    out.append("## Known gaps / next-up targets")
    out.append("")
    out.append("- **Image coverage long tail**: ~243 entities still need real product images")
    out.append("  (mostly per-SKU hardware: sensor / arm / joint / compute variants).")
    out.append("  Run `audit_images.py` to refresh the priority queue.")
    out.append("- **sourcedSpecs gaps**: only ~62% of entities have any sourced claim.")
    out.append("  Many 整机平台 entries have placeholder specs (status='In Production')")
    out.append("  with no real numbers — these don't migrate, won't migrate until")
    out.append("  the underlying data is improved.")
    out.append("- **Region skew**: China + USA dominate. Japanese (Toyota, Honda, Sony)")
    out.append("  and Korean (Samsung, LG, KAIST) ecosystems are under-represented")
    out.append("  relative to their actual robotics weight.")
    out.append("- **Era skew toward 2024–2025**: the recent humanoid wave is heavily")
    out.append("  represented; foundational work pre-2015 (PR2, Asimo, early Atlas)")
    out.append("  is thin.")
    out.append("- **People graph just seeded** (20 persons). Founder/CTO/PI coverage")
    out.append("  is sparse — most companies + labs don't yet have a person node.")
    out.append("- **Source URL liveness**: needs periodic re-check via")
    out.append("  `check_url_liveness.py`. Last check: " + last_url_check + ".")
    out.append("")

    out.append("---")
    out.append(f"_Run `python3 research/_tools/health_report.py` to regenerate._")

    HEALTH_MD.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"Wrote {HEALTH_MD.relative_to(ROOT)}")
    print(f"  Schema errors: {n_err}")
    print(f"  Source coverage: {src_pct}%")
    print(f"  Image covered (real+synth): {real_pct}%")
    if url_total:
        dead_pct_msg = f"({dead_urls} dead of {url_total} checked)"
    else:
        dead_pct_msg = "(URL liveness never run — `check_url_liveness.py`)"
    print(f"  URL liveness: {dead_pct_msg}")


if __name__ == "__main__":
    main()
