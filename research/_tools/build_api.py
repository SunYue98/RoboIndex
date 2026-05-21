#!/usr/bin/env python3
"""Phase 6 — Build the consumable API layer.

Reads public/data/*.json and emits a set of static files under public/api/ that
external tools (LLMs, Jupyter, dashboards, scrapers) can consume without
knowing about our internal partitioning. Everything ships as part of the
GitHub Pages bundle at <base>/api/...

Outputs:
  entities.json         — all 667 entities, flat array
  relations.json        — all typed edges (source_id, role, target_id, isInverse)
  funding-rounds.json   — flat funding history with per-round source URLs
  summary.json          — high-level stats: counts, coverage, top-degree nodes
  by-category.json      — {category: [id, ...]}
  by-country.json       — {country: [id, ...]}  (derived from orgInfo.location)
  by-year.json          — {year: [id, ...]}
  entities.csv          — Excel/pandas-friendly entity table (key columns only)
  relations.csv         — Excel/pandas-friendly edge table
  narrative.md          — LLM-friendly running prose describing the catalog
  README.md             — consumer documentation

Run after any data change:
  python3 research/_tools/build_api.py
"""
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from datetime import date

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "public/data"
API = ROOT / "public/api"
API.mkdir(parents=True, exist_ok=True)
PARTITIONS = ["hardware", "software", "ecosystem", "players"]
TOP_LEVEL = {
    "硬件": ["整机平台", "机械臂", "灵巧手 & 夹爪", "关节模组", "核心零部件", "传感器",
            "能源动力", "数采 & 遥操", "计算平台"],
    "软件": ["基础模型", "算法框架", "控制算法", "仿真平台", "数据集", "评测基准"],
    "生态与应用": ["开发生态", "应用场景"],
    "参与实体": ["资本", "产业", "实验室", "人物"],
}


def load_all() -> list[dict]:
    out: list[dict] = []
    for p in PARTITIONS:
        for e in json.loads((DATA / f"{p}.json").read_text(encoding="utf-8")):
            e["_partition"] = p
            out.append(e)
    return out


def extract_country(entity: dict) -> str | None:
    """Best-effort country derivation from orgInfo.location."""
    loc = (entity.get("orgInfo") or {}).get("location") or ""
    if not loc:
        return None
    # location is usually "City, Country" or "City, State, USA" or just "Country"
    parts = [p.strip() for p in re.split(r"[,，;]", loc) if p.strip()]
    if not parts:
        return None
    # Heuristic: last token is the country in most templates we use
    last = parts[-1]
    # Normalize a few common aliases
    aliases = {
        "USA": "USA", "United States": "USA", "U.S.": "USA", "US": "USA", "America": "USA",
        "UK": "UK", "United Kingdom": "UK", "England": "UK",
        "China": "China", "中国": "China", "PRC": "China",
        "Korea": "South Korea", "South Korea": "South Korea", "ROK": "South Korea",
    }
    return aliases.get(last, last)


def main():
    entities = load_all()
    id_to_e = {e["id"]: e for e in entities}

    # === entities.json — strip internal "_partition" before export ===
    entities_out = []
    for e in entities:
        eo = {k: v for k, v in e.items() if k != "_partition"}
        # add partition as visible field (useful for consumers)
        eo["partition"] = e["_partition"]
        entities_out.append(eo)
    (API / "entities.json").write_text(
        json.dumps(entities_out, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # === relations.json — flat edge list ===
    edges = []
    for e in entities:
        for rel in e.get("relations") or []:
            edges.append({
                "source_id": e["id"],
                "source_name": e["name"],
                "source_category": e["category"],
                "target_id": rel["targetId"],
                "target_name": id_to_e.get(rel["targetId"], {}).get("name", ""),
                "target_category": id_to_e.get(rel["targetId"], {}).get("category", ""),
                "role": rel["role"],
                "isInverse": bool(rel.get("isInverse")),
            })
        # Include legacy relatedIds as role='related' for forward-compat consumers
        for tid in e.get("relatedIds") or []:
            t = id_to_e.get(tid)
            if not t:
                continue
            edges.append({
                "source_id": e["id"],
                "source_name": e["name"],
                "source_category": e["category"],
                "target_id": tid,
                "target_name": t["name"],
                "target_category": t["category"],
                "role": "related",
                "isInverse": False,
                "_legacy": True,
            })
    (API / "relations.json").write_text(
        json.dumps(edges, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # === funding-rounds.json — flat with per-round source ===
    rounds = []
    for e in entities:
        for fr in e.get("fundingRounds") or []:
            rounds.append({
                "company_id": e["id"],
                "company_name": e["name"],
                **{k: v for k, v in fr.items()},
            })
    (API / "funding-rounds.json").write_text(
        json.dumps(rounds, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # === by-category.json ===
    by_cat: dict[str, list[str]] = defaultdict(list)
    for e in entities:
        by_cat[e["category"]].append(e["id"])
    (API / "by-category.json").write_text(
        json.dumps(dict(by_cat), ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # === by-country.json ===
    by_country: dict[str, list[str]] = defaultdict(list)
    for e in entities:
        c = extract_country(e)
        if c:
            by_country[c].append(e["id"])
    (API / "by-country.json").write_text(
        json.dumps(dict(sorted(by_country.items())), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # === by-year.json ===
    by_year: dict[str, list[str]] = defaultdict(list)
    for e in entities:
        y = (e.get("year") or "")[:4]
        if re.match(r"^\d{4}$", y):
            by_year[y].append(e["id"])
    (API / "by-year.json").write_text(
        json.dumps(dict(sorted(by_year.items())), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # === summary.json ===
    out_edges_per = Counter(e["source_id"] for e in edges)
    in_edges_per = Counter(e["target_id"] for e in edges if not e.get("isInverse"))
    top_degree = sorted(
        ((eid, out_edges_per.get(eid, 0) + in_edges_per.get(eid, 0)) for eid in id_to_e),
        key=lambda x: -x[1],
    )[:30]
    summary = {
        "generated_at": str(date.today()),
        "version": "phase-6",
        "totals": {
            "entities": len(entities),
            "edges": len(edges),
            "funding_rounds": len(rounds),
        },
        "by_partition": dict(Counter(e["_partition"] for e in entities)),
        "by_category": {c: len(ids) for c, ids in by_cat.items()},
        "by_top_level": {
            tl: sum(len(by_cat.get(c, [])) for c in cats)
            for tl, cats in TOP_LEVEL.items()
        },
        "coverage": {
            "with_sources": sum(1 for e in entities if e.get("sources")),
            "with_image": sum(1 for e in entities if e.get("imageUrl")),
            "with_relations": sum(1 for e in entities if e.get("relations")),
            "with_sourcedSpecs": sum(1 for e in entities if e.get("sourcedSpecs")),
            "with_fundingRounds": sum(1 for e in entities if e.get("fundingRounds")),
        },
        "relation_role_counts": dict(Counter(e["role"] for e in edges)),
        "top_connected_entities": [
            {"id": eid, "name": id_to_e[eid]["name"], "category": id_to_e[eid]["category"], "degree": d}
            for eid, d in top_degree
        ],
    }
    (API / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # === entities.csv — key columns ===
    with (API / "entities.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "name", "company", "category", "partition", "year", "country",
                    "is_new", "n_sources", "n_relations", "n_sourced_specs", "imageUrl", "website"])
        for e in entities:
            w.writerow([
                e["id"], e["name"], e.get("company", ""), e["category"], e["_partition"],
                e.get("year", ""), extract_country(e) or "",
                int(bool(e.get("isNew"))),
                len(e.get("sources") or []),
                len(e.get("relations") or []),
                len(e.get("sourcedSpecs") or {}),
                e.get("imageUrl", ""),
                e.get("websiteUrl") or (e.get("orgInfo") or {}).get("website", ""),
            ])

    # === relations.csv ===
    with (API / "relations.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["source_id", "source_name", "source_category", "role",
                    "target_id", "target_name", "target_category", "is_inverse"])
        for e in edges:
            w.writerow([
                e["source_id"], e["source_name"], e["source_category"], e["role"],
                e["target_id"], e["target_name"], e["target_category"],
                int(bool(e.get("isInverse"))),
            ])

    # === narrative.md — running prose, LLM-friendly ===
    lines = ["# RoboIndex Catalog (LLM-readable snapshot)", "",
             f"Auto-generated by `research/_tools/build_api.py` on {date.today()}.",
             f"Total entities: {len(entities)}. Total edges: {len(edges)}.",
             "",
             "This snapshot describes the entire RoboIndex knowledge graph in prose, "
             "intended for ingestion by language models that can't (or don't want to) "
             "load the JSON. Per-entity claims with `source` fields are described as "
             "'(per <source URL>)' so you can trace back. Edges with role=`related` "
             "are unclassified legacy and weaker signal than typed edges.",
             ""]

    for tl, cats in TOP_LEVEL.items():
        lines.append(f"## {tl}")
        for cat in cats:
            ids = by_cat.get(cat, [])
            lines.append(f"### {cat} ({len(ids)} entities)")
            # List top 10 by degree within this category
            in_cat = sorted(
                ((eid, out_edges_per.get(eid, 0) + in_edges_per.get(eid, 0)) for eid in ids),
                key=lambda x: -x[1],
            )[:10]
            for eid, deg in in_cat:
                e = id_to_e[eid]
                company = f" — {e.get('company')}" if e.get("company") and e.get("company") != e["name"] else ""
                year = f" ({e['year']})" if e.get("year") else ""
                lines.append(f"- **{e['name']}**{company}{year}, degree={deg}")
            if len(ids) > 10:
                lines.append(f"  *(and {len(ids) - 10} more)*")
        lines.append("")

    lines.append("## Top 30 most-connected entities")
    for entry in summary["top_connected_entities"]:
        lines.append(f"- {entry['name']} ({entry['category']}, deg={entry['degree']}, id=`{entry['id']}`)")
    lines.append("")

    lines.append("## Relation role distribution")
    for role, n in sorted(summary["relation_role_counts"].items(), key=lambda x: -x[1]):
        lines.append(f"- `{role}`: {n}")
    lines.append("")

    (API / "narrative.md").write_text("\n".join(lines), encoding="utf-8")

    # === README.md — consumer documentation ===
    readme = f"""# RoboIndex Public API

Static JSON / CSV / Markdown files at `<site>/api/...`. Deployed alongside the
live site to GitHub Pages — fetchable from any tool that can hit a public URL.

Generated by `research/_tools/build_api.py` on {date.today()}.
Snapshot version: `phase-6`.

## Endpoints

| File | What it is |
|------|------------|
| `entities.json`        | Flat array of all {len(entities)} entities, full data |
| `relations.json`       | Flat list of all {len(edges)} typed edges (source, role, target) |
| `funding-rounds.json`  | Flat funding history, each round with per-round source URL |
| `summary.json`         | Counts, coverage stats, top-degree entities, role distribution |
| `by-category.json`     | `{{category: [id, …]}}` — fast category filter |
| `by-country.json`      | `{{country: [id, …]}}` — derived from `orgInfo.location` |
| `by-year.json`         | `{{year: [id, …]}}` — derived from `entity.year` |
| `entities.csv`         | Excel/pandas-friendly entity table (key columns) |
| `relations.csv`        | Excel/pandas-friendly edge table |
| `narrative.md`         | Running prose summary — feed to an LLM that can't read JSON |
| `README.md`            | This file |

## Quick examples

```python
import urllib.request, json
base = "https://sunyue.github.io/RoboIndex/api"
ents = json.loads(urllib.request.urlopen(f"{{base}}/entities.json").read())
print(f"Loaded {{len(ents)}} entities")
```

```python
# pandas one-liner
import pandas as pd
df = pd.read_csv("https://sunyue.github.io/RoboIndex/api/entities.csv")
df.query("category == '产业' and country == 'China'")
```

```python
# Graph analysis with networkx
import networkx as nx, urllib.request, json
edges = json.loads(urllib.request.urlopen(f"{{base}}/relations.json").read())
G = nx.DiGraph()
for e in edges:
    G.add_edge(e["source_id"], e["target_id"], role=e["role"])
print(f"Most-connected: {{sorted(G.degree, key=lambda x: -x[1])[:5]}}")
```

```
# Curl for shell pipelines
curl -s https://sunyue.github.io/RoboIndex/api/by-country.json | jq 'keys'
```

## Data model recap

- **Entity** = a node in the graph. Each has `id` (stable), `category`
  (one of 20+), `partition` (hardware/software/ecosystem/players),
  `name`, `company`, `year`, plus optional `specs`, `sourcedSpecs`,
  `relations`, `sources`, `fundingRounds`, etc. See `entities.json`.

- **Relation** = a typed directed edge. Roles include `manufacturer`,
  `invested-in`, `founder-of`, `tech-base`, etc. See `relations.json`.
  `isInverse=true` means this edge was authored on the OTHER side and is
  presented here for convenience.

- **Claim** = a single fact-checkable value in `sourcedSpecs[key]`. Shape:
  `{{ value, source?: {{ url, title, type }}, asOf?, confidence?, notes? }}`.

- **Source** is mandatory on every public-facing fact (per project
  convention "出处第一公民"). Every funding round and most `sourcedSpecs`
  entries carry a clickable source URL.

## Refresh cadence

Re-run after any data change:
```
python3 research/_tools/build_api.py
```
Commit the resulting `public/api/*` files alongside the data changes that
produced them so external consumers always see a consistent snapshot.
"""
    (API / "README.md").write_text(readme, encoding="utf-8")

    # === Report ===
    print(f"=== build_api.py ===")
    print(f"Wrote {len(list(API.glob('*')))} files to {API.relative_to(ROOT)}/")
    print(f"  entities.json:        {len(entities_out)} entities")
    print(f"  relations.json:       {len(edges)} edges")
    print(f"  funding-rounds.json:  {len(rounds)} rounds")
    print(f"  by-category.json:     {len(by_cat)} categories")
    print(f"  by-country.json:      {len(by_country)} countries")
    print(f"  by-year.json:         {len(by_year)} distinct years")
    print(f"  summary.json:         top-degree node = {summary['top_connected_entities'][0]['name']}")
    print(f"  entities.csv + relations.csv + narrative.md + README.md")


if __name__ == "__main__":
    main()
