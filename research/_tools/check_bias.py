#!/usr/bin/env python3
"""Phase 7 — Bias self-audit.

Surface distribution skews the project has unintentionally accumulated. We don't
control these (the world is what it is) but knowing them lets us:
  - Decide whether a gap is worth filling on purpose (e.g., Japanese / Korean
    robotics is under-covered in our data — should we go fix it?)
  - Disclose them honestly when this dataset is cited
  - Track over time whether new additions widen or narrow the skew

Dimensions:
  1. Region (which countries dominate)
  2. Era (founding-year buckets — are we drowning in 2024–2025 startups?)
  3. Company stage (Seed / Series A / B / C / Public — derived from funding rounds)
  4. Gender (best-effort heuristic on person first names — VERY rough, just to
     flag obvious imbalance for manual follow-up)
  5. Source-type mix (official vs wiki vs news)
  6. Language (Chinese vs English entries — does our 中文 coverage match our
     stated bilingual ambition?)

Outputs JSON to stdout; --markdown writes to research/_health_cache/bias.md.

Usage:
  python3 research/_tools/check_bias.py
  python3 research/_tools/check_bias.py --markdown
"""
import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "public/data"
CACHE_DIR = ROOT / "research/_health_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
PARTITIONS = ["hardware", "software", "ecosystem", "players"]

# Very rough gender heuristic. Strictly first-name-based; flags obvious skew but
# doesn't try to be authoritative. Names not in either list are reported as
# 'unknown'. This is documented in the output so consumers don't over-read.
COMMON_MALE_FIRST_NAMES = {
    # Anglo
    "brett", "jonathan", "jeff", "marc", "geordie", "bernt", "will", "ken",
    "pieter", "sergey", "karol", "russ", "andy", "stefan", "marco", "michael",
    "yann", "geoffrey", "geoff", "elon", "bob", "tom", "john", "david",
    # Chinese (pinyin first names; very rough)
    "xingxing", "zhihui", "jian", "cewu", "kai", "wei", "ming",
}
COMMON_FEMALE_FIRST_NAMES = {
    "chelsea", "daniela", "fei-fei", "feifei", "ruzena", "cynthia",
    "li", "jiajun",  # ambiguous in pinyin; we choose conservatively
}


def extract_country(entity: dict) -> str | None:
    loc = (entity.get("orgInfo") or {}).get("location") or ""
    if not loc:
        return None
    parts = [p.strip() for p in re.split(r"[,，;]", loc) if p.strip()]
    if not parts:
        return None
    last = parts[-1]
    aliases = {
        "USA": "USA", "United States": "USA", "U.S.": "USA", "US": "USA",
        "UK": "UK", "United Kingdom": "UK", "England": "UK",
        "China": "China", "中国": "China",
        "South Korea": "South Korea", "Korea": "South Korea",
        # US state abbreviations leaking through as "country" — flag as "USA"
        "CA": "USA", "WA": "USA", "NY": "USA", "MA": "USA", "TX": "USA",
        "Berkeley": "USA", "Cambridge": "USA",
    }
    return aliases.get(last, last)


def detect_chinese(text: str) -> bool:
    return any("一" <= c <= "鿿" for c in (text or ""))


def first_name(full_name: str) -> str:
    # Strip Chinese characters and parentheticals
    s = re.sub(r"[一-鿿（）()]+", " ", full_name or "")
    s = re.sub(r"\s+", " ", s).strip()
    if not s:
        return ""
    return s.split()[0].lower().rstrip(".")


def derive_stage(entity: dict) -> str:
    """Best-effort: latest funding round → stage. 'public' overrides if listed."""
    rounds = entity.get("fundingRounds") or []
    status = (entity.get("specs") or {}).get("status", "").lower()
    if "public" in status or "ipo" in status or "listed" in status:
        return "Public"
    if not rounds:
        return "Unknown / no-round"
    # Pick the latest round by year
    rounds_with_year = [(r.get("round") or "", r.get("year") or "") for r in rounds]
    rounds_with_year.sort(key=lambda x: x[1], reverse=True)
    latest = rounds_with_year[0][0].strip()
    if not latest:
        return "Unknown"
    # Normalize
    l = latest.lower()
    for tag in ["seed", "angel", "pre-a", "series a", "series b", "series c",
               "series d", "series e", "series f", "series g", "strategic",
               "pre-ipo", "ipo"]:
        if tag in l:
            return tag.title()
    return latest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--markdown", action="store_true", help="Write markdown to research/_health_cache/bias.md")
    args = ap.parse_args()

    entities = []
    for p in PARTITIONS:
        for e in json.loads((DATA / f"{p}.json").read_text(encoding="utf-8")):
            entities.append(e)

    # 1. Region
    region = Counter()
    region_by_cat = defaultdict(Counter)
    for e in entities:
        c = extract_country(e)
        if c:
            region[c] += 1
            region_by_cat[e["category"]][c] += 1

    # 2. Era (founding year buckets)
    era = Counter()
    for e in entities:
        y_str = (e.get("year") or "")[:4]
        if re.match(r"^\d{4}$", y_str):
            y = int(y_str)
            if y < 2000:
                era["<2000"] += 1
            elif y < 2010:
                era["2000–2009"] += 1
            elif y < 2015:
                era["2010–2014"] += 1
            elif y < 2020:
                era["2015–2019"] += 1
            elif y < 2024:
                era["2020–2023"] += 1
            else:
                era[f"≥2024"] += 1
        else:
            era["(no year)"] += 1

    # 3. Stage (companies only)
    stage = Counter()
    for e in entities:
        if e.get("category") != "产业":
            continue
        stage[derive_stage(e)] += 1

    # 4. Gender (persons only — very rough)
    gender = Counter()
    persons_unknown = []
    for e in entities:
        if e.get("category") != "人物":
            continue
        fn = first_name(e.get("name", ""))
        if fn in COMMON_MALE_FIRST_NAMES:
            gender["male"] += 1
        elif fn in COMMON_FEMALE_FIRST_NAMES:
            gender["female"] += 1
        else:
            gender["unknown / not-in-list"] += 1
            persons_unknown.append(e.get("name", ""))

    # 5. Source-type mix
    source_types = Counter()
    for e in entities:
        for s in e.get("sources") or []:
            source_types[s.get("type") or "(untyped)"] += 1

    # 6. Language / bilingual coverage
    bilingual = Counter()  # zh_only, en_only, bilingual, neither
    for e in entities:
        has_zh = detect_chinese(e.get("name", "")) or detect_chinese(e.get("company", ""))
        # crude: if name has both ASCII letters and CJK, call it bilingual
        has_en = bool(re.search(r"[A-Za-z]{2,}", e.get("name", "") + " " + e.get("company", "")))
        if has_zh and has_en:
            bilingual["bilingual"] += 1
        elif has_zh:
            bilingual["zh_only"] += 1
        elif has_en:
            bilingual["en_only"] += 1
        else:
            bilingual["other"] += 1

    result = {
        "region": dict(region.most_common()),
        "region_by_category": {c: dict(d.most_common(5)) for c, d in region_by_cat.items()},
        "era": dict(era),
        "stage": dict(stage),
        "gender": dict(gender),
        "gender_unknown_names": sorted(persons_unknown),
        "source_types": dict(source_types),
        "name_language": dict(bilingual),
        "totals": {"entities": len(entities)},
    }

    if args.markdown:
        out = ["# Bias self-audit", "",
               f"Auto-generated. Total entities: {len(entities)}.",
               "",
               "## Region", ""]
        out.append("| Country | Count |\n|---|---:|")
        for c, n in region.most_common(15):
            out.append(f"| {c} | {n} |")
        if len(region) > 15:
            out.append(f"| *(and {len(region)-15} more countries)* | |")
        out.append("")
        out.append("## Era (by founding/release year)\n")
        out.append("| Bucket | Count |\n|---|---:|")
        for bucket in ["<2000", "2000–2009", "2010–2014", "2015–2019", "2020–2023", "≥2024", "(no year)"]:
            out.append(f"| {bucket} | {era.get(bucket, 0)} |")
        out.append("")
        out.append("## Company stage (产业 only)\n")
        out.append("| Stage | Count |\n|---|---:|")
        for s, n in stage.most_common():
            out.append(f"| {s} | {n} |")
        out.append("")
        out.append("## Gender (人物 only — best-effort heuristic on first names)\n")
        out.append("| Gender | Count |\n|---|---:|")
        for g, n in gender.most_common():
            out.append(f"| {g} | {n} |")
        if persons_unknown:
            out.append(f"\n*Unrecognized first names (review for accuracy):* "
                       f"{', '.join(persons_unknown)}")
        out.append("")
        out.append("## Source-type mix\n")
        out.append("| Type | Count |\n|---|---:|")
        for t, n in source_types.most_common():
            out.append(f"| {t} | {n} |")
        out.append("")
        out.append("## Name language\n")
        out.append("| Mix | Count |\n|---|---:|")
        for k in ["bilingual", "zh_only", "en_only", "other"]:
            out.append(f"| {k} | {bilingual.get(k, 0)} |")

        (CACHE_DIR / "bias.md").write_text("\n".join(out) + "\n", encoding="utf-8")
        print(f"Wrote {CACHE_DIR / 'bias.md'}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
