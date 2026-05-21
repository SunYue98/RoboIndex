#!/usr/bin/env python3
"""Phase 3 — Migrate key fields from free-form `specs` to typed `sourcedSpecs[Claim]`.

For each Entity, look in its `specs` field for keys that match the per-category
schema (mirrors src/data/categoryClaimSchema.ts), parse the values per the
declared `type`, wrap as Claim form, and write to `sourcedSpecs`.

  Claim shape:  { value, source?, asOf?, confidence?, notes? }

Per-claim source: best-effort, using the entity's first source URL. asOf:
the entity's year (where reasonable). Both can be refined manually later.

Old `specs` is preserved as-is — UI prefers `sourcedSpecs` when a key exists
in both. Nothing is destroyed.

Usage:
  python3 research/_tools/migrate_specs_to_claims.py
  python3 research/_tools/migrate_specs_to_claims.py --dry-run
"""
import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "public/data"
PARTITIONS = ["hardware", "software", "ecosystem", "players"]

# Mirror of src/data/categoryClaimSchema.ts — kept in sync manually.
# (TODO Phase 8: emit this file from TS to remove drift.)
CATEGORY_CLAIM_SCHEMA: dict[str, list[dict]] = {
    "整机平台": [
        {"key": "height_cm",         "type": "number", "aliases": ["Height", "height", "Height (cm)", "Body Height", "身高"]},
        {"key": "weight_kg",         "type": "number", "aliases": ["Weight", "Mass", "weight", "Body Weight", "体重", "重量"]},
        {"key": "dof",               "type": "number", "aliases": ["DoF", "DOF", "Degrees of Freedom", "DoFs", "dof", "自由度"]},
        {"key": "payload_kg",        "type": "number", "aliases": ["Payload", "Max Payload", "Payload Capacity", "payload", "Load Capacity", "carryPayload", "Carry Payload", "Lift Capacity", "负载"]},
        {"key": "battery_runtime_min", "type": "number", "aliases": ["Battery Life", "Runtime", "Battery Runtime", "Battery", "Operating Time", "续航"]},
        {"key": "top_speed_mps",     "type": "number", "aliases": ["Top Speed", "Max Speed", "Walking Speed", "Speed", "top_speed"]},
    ],
    "机械臂": [
        {"key": "dof",          "type": "number", "aliases": ["DoF", "DOF", "Axes", "Joints", "dof", "自由度", "轴数"]},
        {"key": "payload_kg",   "type": "number", "aliases": ["Payload", "Max Payload", "Payload Capacity", "负载"]},
        {"key": "reach_mm",     "type": "number", "aliases": ["Reach", "Working Radius", "Max Reach", "臂展", "工作半径"]},
        {"key": "weight_kg",    "type": "number", "aliases": ["Weight", "Mass", "重量"]},
        {"key": "repeatability_mm", "type": "number", "aliases": ["Repeatability", "Position Accuracy", "Pose Repeatability", "重复定位精度"]},
    ],
    "灵巧手 & 夹爪": [
        {"key": "dof",          "type": "number", "aliases": ["DoF", "DOF", "Active DoF", "dof", "自由度"]},
        {"key": "finger_count", "type": "number", "aliases": ["Fingers", "Finger Count", "Number of Fingers", "手指数"]},
        {"key": "payload_kg",   "type": "number", "aliases": ["Payload", "Grasp Force", "Max Grip", "Gripping Force", "负载"]},
        {"key": "weight_g",     "type": "number", "aliases": ["Weight", "Mass", "重量"]},
    ],
    "关节模组": [
        {"key": "torque_nm",      "type": "number", "aliases": ["Torque", "Rated Torque", "Nominal Torque", "额定扭矩"]},
        {"key": "peak_torque_nm", "type": "number", "aliases": ["Peak Torque", "Max Torque", "Stall Torque", "峰值扭矩"]},
        {"key": "weight_g",       "type": "number", "aliases": ["Weight", "Mass", "重量"]},
        {"key": "gear_ratio",     "type": "number", "aliases": ["Gear Ratio", "Reduction Ratio", "减速比"]},
    ],
    "核心零部件": [
        {"key": "torque_nm",  "type": "number", "aliases": ["Torque", "Rated Torque", "扭矩"]},
        {"key": "gear_ratio", "type": "number", "aliases": ["Gear Ratio", "Reduction Ratio", "减速比"]},
        {"key": "type",       "type": "string", "aliases": ["Type", "Mechanism", "类型"]},
    ],
    "传感器": [
        {"key": "range_m",         "type": "number", "aliases": ["Range", "Max Range", "Detection Range", "量程"]},
        {"key": "fov_deg",         "type": "number", "aliases": ["FoV", "Field of View", "FOV", "视场角"]},
        {"key": "resolution",      "type": "string", "aliases": ["Resolution", "Image Resolution", "分辨率"]},
        {"key": "frame_rate_hz",   "type": "number", "aliases": ["Frame Rate", "FPS", "Refresh Rate", "帧率"]},
    ],
    "能源动力": [
        {"key": "capacity_wh",  "type": "number", "aliases": ["Capacity", "Energy", "容量"]},
        {"key": "voltage_v",    "type": "number", "aliases": ["Voltage", "Nominal Voltage", "电压"]},
        {"key": "runtime_min",  "type": "number", "aliases": ["Runtime", "Battery Life", "续航"]},
    ],
    "数采 & 遥操": [
        {"key": "type", "type": "string", "aliases": ["Type", "类型"]},
        {"key": "dof",  "type": "number", "aliases": ["DoF", "DOF", "自由度"]},
    ],
    "计算平台": [
        {"key": "tops",       "type": "number", "aliases": ["TOPS", "AI Performance", "INT8 TOPS", "Compute", "算力"]},
        {"key": "power_w",    "type": "number", "aliases": ["Power", "Power Consumption", "TDP", "功耗"]},
        {"key": "ram_gb",     "type": "number", "aliases": ["Memory", "RAM", "Unified Memory", "内存"]},
        {"key": "price_usd",  "type": "number", "aliases": ["Price", "MSRP", "Cost", "价格"]},
    ],
    "基础模型": [
        {"key": "params_b",          "type": "number", "aliases": ["Parameters", "Params", "Model Size", "Parameter Count", "参数量"]},
        {"key": "release_date",      "type": "string", "aliases": ["Release Date", "Released", "Date", "release", "发布日期"]},
        {"key": "training_data_size", "type": "string", "aliases": ["Training Data", "Training Size", "Data Size"]},
    ],
    "算法框架": [
        {"key": "language",     "type": "string", "aliases": ["Language", "Primary Language", "语言"]},
        {"key": "license",      "type": "string", "aliases": ["License", "license", "许可"]},
        {"key": "github_stars", "type": "number", "aliases": ["GitHub Stars", "Stars", "GH Stars"]},
    ],
    "控制算法": [
        {"key": "language",  "type": "string", "aliases": ["Language"]},
        {"key": "license",   "type": "string", "aliases": ["License"]},
    ],
    "仿真平台": [
        {"key": "engine",  "type": "string", "aliases": ["Engine", "Physics Engine", "物理引擎"]},
        {"key": "license", "type": "string", "aliases": ["License", "许可"]},
    ],
    "数据集": [
        {"key": "episodes",  "type": "number", "aliases": ["Episodes", "Demonstrations", "Demos", "Trajectories", "轨迹数"]},
        {"key": "hours",     "type": "number", "aliases": ["Hours", "Duration", "Total Hours"]},
        {"key": "tasks",     "type": "number", "aliases": ["Tasks", "Task Count", "任务数"]},
    ],
    "评测基准": [
        {"key": "tasks",     "type": "number", "aliases": ["Tasks", "Task Count", "任务数"]},
        {"key": "episodes",  "type": "number", "aliases": ["Episodes", "Test Episodes"]},
    ],
    "开发生态": [
        {"key": "license",  "type": "string", "aliases": ["License"]},
        {"key": "language", "type": "string", "aliases": ["Language"]},
    ],
    "应用场景": [],
    "资本": [
        {"key": "aum_b",        "type": "number", "aliases": ["AUM", "Assets Under Management", "资产管理规模"]},
        {"key": "founded_year", "type": "number", "aliases": ["Founded", "Founding Year", "成立年份"]},
        {"key": "hq_country",   "type": "string", "aliases": ["HQ", "Headquarters", "Country", "总部"]},
    ],
    "产业": [
        {"key": "founded_year",   "type": "number", "aliases": ["Founded", "Founding Year", "成立年份"]},
        {"key": "hq_country",     "type": "string", "aliases": ["HQ", "Headquarters", "Country", "总部"]},
        {"key": "employee_count", "type": "number", "aliases": ["Employees", "Headcount", "Staff Count", "员工数"]},
    ],
    "实验室": [
        {"key": "founded_year", "type": "number", "aliases": ["Founded", "Founding Year", "成立年份"]},
        {"key": "university",   "type": "string", "aliases": ["University", "Affiliation", "Parent", "所属"]},
        {"key": "head",         "type": "string", "aliases": ["Head", "Director", "PI", "Lead", "负责人"]},
    ],
}


def normalize_key(s: str) -> str:
    return re.sub(r"[\s\-_/&（）()]", "", s.lower())


def build_alias_index() -> dict[str, dict[str, dict]]:
    idx: dict[str, dict[str, dict]] = {}
    for cat, specs in CATEGORY_CLAIM_SCHEMA.items():
        m: dict[str, dict] = {}
        for spec in specs:
            m[normalize_key(spec["key"])] = spec
            for a in spec["aliases"]:
                m[normalize_key(a)] = spec
        idx[cat] = m
    return idx


# Plausibility ranges per canonical claim key. Parsed values outside these are
# rejected as "looks-like-wrong-unit-or-relative-claim" cases.
PLAUSIBLE_RANGES: dict[str, tuple[float, float]] = {
    "height_cm":            (30, 250),
    "weight_kg":            (0.5, 500),
    "weight_g":             (10, 50000),
    "dof":                  (1, 200),
    "finger_count":         (2, 10),
    "payload_kg":           (0.05, 2000),
    "reach_mm":             (50, 5000),
    "repeatability_mm":     (0.001, 50),
    "battery_runtime_min":  (1, 1440),
    "top_speed_mps":        (0.05, 30),
    "torque_nm":            (0.01, 10000),
    "peak_torque_nm":       (0.01, 20000),
    "gear_ratio":           (1, 1000),
    "range_m":              (0.05, 1000),
    "fov_deg":              (1, 360),
    "frame_rate_hz":        (1, 5000),
    "capacity_wh":          (1, 100000),
    "voltage_v":            (1, 1000),
    "runtime_min":          (1, 1440),
    "tops":                 (0.1, 10000),
    "power_w":              (0.1, 2000),
    "ram_gb":               (0.5, 1024),
    "price_usd":            (10, 10_000_000),
    "params_b":             (0.001, 10000),
    "founded_year":         (1800, 2030),
    "aum_b":                (0.001, 5000),
    "employee_count":       (1, 1_000_000),
    "github_stars":         (1, 10_000_000),
    "tasks":                (1, 100000),
    "episodes":             (1, 100_000_000),
    "hours":                (0.1, 1_000_000),
}

# Phrases that mean "this is a relative or qualitative claim, not an absolute number".
# We refuse to parse a single number out of these.
RELATIVE_BLOCKERS = [
    "faster than", "slower than", "lighter than", "heavier than",
    "% faster", "% slower", "% more", "% less", "× faster", "x faster",
    "compared to", "vs.", " vs ",
    "approximately " "as ",  # "as much as X"
    "tbd", "n/a", "to be determined", "未公布", "待发布",
]


def looks_relative(s: str) -> bool:
    low = s.lower()
    return any(b in low for b in RELATIVE_BLOCKERS)


def parse_imperial_height(s: str) -> float | None:
    """Convert 5'11" / 5'11 / 5 ft 11 in → cm. Return None if not this format."""
    m = re.match(r"^\s*(\d+)\s*[ '′ʹ]\s*(\d+)?\s*[\"″ʺ]?\s*$", s.strip())
    if m and m.group(2) is not None:
        feet = int(m.group(1))
        inches = int(m.group(2))
        return round((feet * 12 + inches) * 2.54, 1)
    return None


def parse_value(raw, expected_type: str, canonical_key: str):
    """Best-effort parser. Returns (parsed_value, ok)."""
    if raw is None:
        return None, False
    if isinstance(raw, bool):
        return raw, expected_type == "string"
    if isinstance(raw, (int, float)):
        if expected_type == "number":
            return float(raw), True
        return raw, True
    if not isinstance(raw, str):
        return raw, False

    s = raw.strip()
    if not s or looks_relative(s):
        return raw, False

    if expected_type == "string":
        return s, True

    # === number path ===
    low = s.lower()

    # 1) Imperial feet+inches → cm (only for height_cm)
    if canonical_key == "height_cm":
        ft_cm = parse_imperial_height(s)
        if ft_cm is not None and PLAUSIBLE_RANGES["height_cm"][0] <= ft_cm <= PLAUSIBLE_RANGES["height_cm"][1]:
            return ft_cm, True

    # 2) Unit detection — if a unit is present in the string, ensure it matches
    # the canonical key's expected unit. Otherwise be conservative and skip.
    expected_units_by_key = {
        "height_cm":           {"cm", "centimeters", "centimetres", "m ", "m)", "metres", "meter"},
        "weight_kg":           {"kg", "kilogram", "kilograms", "lb", "lbs", "pound", "pounds"},
        "weight_g":            {"g ", "g)", "grams", "gram", "g/"},
        "payload_kg":          {"kg", "kilogram", "kilograms", "lb", "lbs", "pound", "pounds"},
        "reach_mm":            {"mm", "millimeter", "millimetres"},
        "repeatability_mm":    {"mm", "μm", "um", "micron"},
        "battery_runtime_min": {"min", "hr", "hour", "minutes", "minute"},
        "top_speed_mps":       {"m/s", "mps", "km/h", "kph", "mph"},
        "torque_nm":           {"nm", "n·m", "n.m", "n-m"},
        "peak_torque_nm":      {"nm", "n·m", "n.m", "n-m"},
        "gear_ratio":          {":1", "ratio", "reduction"},
        "range_m":             {" m ", " m)", "meter", "metres"},
        "fov_deg":             {"°", "deg", "degree"},
        "frame_rate_hz":       {"hz", "fps"},
        "capacity_wh":         {"wh", "watt-hour", "ah", "mah"},
        "voltage_v":           {"v ", "volt", "v)", "vdc", "vac"},
        "runtime_min":         {"min", "hr", "hour"},
        "tops":                {"tops"},
        "power_w":             {" w ", " w)", "watt", "tdp"},
        "ram_gb":              {"gb", "gib", "lpddr", "ddr"},
        "price_usd":           {"$", "usd", "yuan", "rmb", "eur"},
        "params_b":            {"b ", " b ", " b)", "billion", "m ", "million", "trillion"},
    }
    units = expected_units_by_key.get(canonical_key)
    if units:
        # Loose check: any of the unit strings should appear in the lowercased value.
        has_unit = any(u in low for u in units) or any(u.strip() in low for u in units)
        if not has_unit:
            # No unit detected and the value is a bare number — accept if it's plausible.
            if not re.match(r"^\s*-?\d+(?:\.\d+)?\s*$", s):
                # String has non-numeric content but no expected unit → suspect, skip
                return raw, False

    # 3) Extract first numeric token
    clean = re.sub(r",", "", s)
    m = re.search(r"(-?\d+(?:\.\d+)?)", clean)
    if not m:
        return raw, False
    v = float(m.group(1))

    # 4) Convert imperial / non-canonical units to canonical
    if canonical_key in ("weight_kg", "payload_kg") and ("lb" in low or "pound" in low):
        v = v * 0.4536  # kg
    if canonical_key == "top_speed_mps":
        if "km/h" in low or "kph" in low:
            v = v / 3.6
        elif "mph" in low:
            v = v * 0.44704
    if canonical_key == "height_cm":
        # "X m" where X is small float → metres → cm
        if re.search(r"\b\d+(?:\.\d+)?\s*m\b", low) and v < 10:
            v = v * 100
    if canonical_key == "weight_kg" and re.search(r"\b\d+(?:\.\d+)?\s*g\b", low) and v < 5000 and "kg" not in low:
        # bare grams → kg
        v = v / 1000
    if canonical_key == "torque_nm" and ("mnm" in low or "mn·m" in low):
        v = v / 1000
    if canonical_key == "battery_runtime_min" and ("hr" in low or "hour" in low):
        v = v * 60
    if canonical_key == "runtime_min" and ("hr" in low or "hour" in low):
        v = v * 60
    if canonical_key == "params_b":
        if "trillion" in low or "t " in low or " t)" in low:
            v = v * 1000
        elif "m " in low or "million" in low:
            v = v / 1000

    # 5) Plausibility check — refuse if outside known range for the canonical key
    rng = PLAUSIBLE_RANGES.get(canonical_key)
    if rng and not (rng[0] <= v <= rng[1]):
        return raw, False

    return round(v, 4), True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    alias_idx = build_alias_index()

    coverage_per_cat = defaultdict(lambda: defaultdict(int))  # category → key → count
    entities_per_cat = Counter()
    entities_with_claims = 0
    total_claims = 0

    for p in PARTITIONS:
        arr = json.loads((DATA / f"{p}.json").read_text(encoding="utf-8"))
        for e in arr:
            cat = e.get("category")
            entities_per_cat[cat] += 1
            if not cat or cat not in alias_idx:
                continue
            cat_idx = alias_idx[cat]
            if not cat_idx:
                continue

            specs = e.get("specs") or {}
            if not isinstance(specs, dict):
                continue

            sourced = dict(e.get("sourcedSpecs") or {})  # preserve any prior
            entity_sources = e.get("sources") or []
            default_source = entity_sources[0] if entity_sources else None
            asOf = e.get("year") or None

            for spec_key, raw_val in specs.items():
                norm = normalize_key(str(spec_key))
                spec_meta = cat_idx.get(norm)
                if not spec_meta:
                    continue
                key = spec_meta["key"]
                if key in sourced:
                    # Already migrated; skip
                    continue
                parsed, ok = parse_value(raw_val, spec_meta["type"], key)
                if not ok and spec_meta["type"] == "number":
                    # Number expected but we couldn't parse — skip
                    continue
                claim = {"value": parsed}
                if default_source:
                    claim["source"] = {
                        "title": default_source.get("title", ""),
                        "url": default_source.get("url", ""),
                    }
                    if default_source.get("type"):
                        claim["source"]["type"] = default_source["type"]
                if asOf:
                    claim["asOf"] = str(asOf)
                claim["confidence"] = "reported"
                sourced[key] = claim
                coverage_per_cat[cat][key] += 1
                total_claims += 1

            if sourced:
                if not args.dry_run:
                    e["sourcedSpecs"] = sourced
                entities_with_claims += 1

        if not args.dry_run:
            (DATA / f"{p}.json").write_text(
                json.dumps(arr, ensure_ascii=False, indent=2), encoding="utf-8"
            )

    # Report
    print(f"=== migrate_specs_to_claims.py {'(dry-run)' if args.dry_run else ''} ===\n")
    print(f"Total claims written: {total_claims}")
    print(f"Entities with ≥1 sourced claim: {entities_with_claims}")
    print(f"\nPer-category claim coverage (cells = entities with key filled):")
    cats = sorted(coverage_per_cat.keys(), key=lambda c: -entities_per_cat[c])
    for cat in cats:
        total = entities_per_cat[cat]
        schema_keys = [s["key"] for s in CATEGORY_CLAIM_SCHEMA.get(cat, [])]
        if not schema_keys:
            continue
        parts = []
        for key in schema_keys:
            n = coverage_per_cat[cat].get(key, 0)
            parts.append(f"{key}={n}")
        print(f"  {cat:12s} ({total} entities)  {', '.join(parts)}")

    # Categories with schema but no claims migrated (data drift signal)
    empty_cats = [
        c for c, specs in CATEGORY_CLAIM_SCHEMA.items()
        if specs and not coverage_per_cat.get(c)
    ]
    if empty_cats:
        print(f"\nCategories with schema but zero claims migrated (legacy specs don't match aliases):")
        for c in empty_cats:
            print(f"  - {c}")


if __name__ == "__main__":
    main()
