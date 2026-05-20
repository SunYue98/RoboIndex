#!/usr/bin/env python3
"""Phase 2 relation builder — adds 4 new passes on top of Phase 1's basic relations.

Pass G (same-vendor SKU sibling): Within a category, products from the same
  company are likely "related variants" (UR3e/5e/10e; Robstride 01-06).

Pass F (cross-category same-vendor integration): Across categories, same-company
  products are likely "integrated" (Unitree humanoid uses Unitree actuator).

Pass A (component composition): Scan 整机 specs.compute/sensing/hands/vision/
  endEffectors/battery text for known compute/sensor/hand entry names.

Pass H (deployment scenario reverse-scan): Each 应用场景 entry's
  specs.'Notable Deployments' lists are strings like "Figure 02 at BMW";
  reverse-scan to link the scenario to the product/company entries it mentions.

All edges bidirectional. Final cap: 15 per entity. When capping, prefer category
diversity over same-category sibling spam.
"""
import json, re, collections
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
existing_ids = set(id_to_entry.keys())


def canon_co(s):
    if not s: return ""
    s = re.sub(r"\([^)]*\)", "", s.lower())
    return re.sub(r"[^\w一-鿿]+", "", s)


# Companies that aren't real companies — Pass G/F MUST NOT treat these as same-vendor
GENERIC_COMPANIES = {
    "various", "opensource", "academic", "未知概念",
    "multiinstitution", "industrialacademic",
}

def is_generic_company(s):
    c = canon_co(s)
    return c in GENERIC_COMPANIES or "various" in c or "concept" in c or "未知" in c


def text_tokens(s):
    """Tokenize a free-text spec string; lowercase, drop punctuation."""
    if not s: return ""
    return re.sub(r"[^\w\s一-鿿]+", " ", s.lower())


# Edges accumulator. Bidirectional via add_edge.
edges = collections.defaultdict(set)
edge_source = collections.defaultdict(set)  # for diagnostic / priority

def add_edge(a, b, src=""):
    if a == b or a not in existing_ids or b not in existing_ids:
        return False
    if b not in edges[a]:
        edges[a].add(b)
        edges[b].add(a)
        edge_source[(a, b)].add(src)
        edge_source[(b, a)].add(src)
        return True
    return False


# ==============================================================
# Pass G (same-category, same-company SKU siblings)
# ==============================================================
g_count = 0
by_cat_co = collections.defaultdict(list)
for e in all_entries:
    if is_generic_company(e.get("company", "")):
        continue
    co = canon_co(e.get("company", ""))
    if not co:
        continue
    by_cat_co[(e["category"], co)].append(e["id"])

for (cat, co), ids in by_cat_co.items():
    if len(ids) < 2:
        continue
    # Cap family size linking to avoid quadratic blow-up for big families (Jetson 6)
    # Each entry links to at most 4 of its siblings (the cap pass will trim more later)
    for i, src_id in enumerate(ids):
        # Pick up to 4 siblings (round-robin from full list)
        siblings = [x for x in ids if x != src_id][:4]
        for tgt_id in siblings:
            if add_edge(src_id, tgt_id, "G:sku-sibling"):
                g_count += 1

print(f"Pass G (same-vendor SKU siblings within category): {g_count} edges added")


# ==============================================================
# Pass F (cross-category, same-company integration)
# ==============================================================
f_count = 0
co_to_entries = collections.defaultdict(list)  # canon_co -> [(id, category)]
for e in all_entries:
    if is_generic_company(e.get("company", "")):
        continue
    co = canon_co(e.get("company", ""))
    if not co:
        continue
    if e["_p"] != "hardware":
        continue  # Cross-category integration only meaningful for hardware
    co_to_entries[co].append((e["id"], e["category"]))

for co, items in co_to_entries.items():
    cats_present = set(c for _, c in items)
    if len(cats_present) < 2:
        continue  # all in same category — handled by Pass G
    # For each entry, link to entries in DIFFERENT categories from same company
    for src_id, src_cat in items:
        for tgt_id, tgt_cat in items:
            if src_cat == tgt_cat:
                continue
            if add_edge(src_id, tgt_id, "F:cross-cat"):
                f_count += 1

print(f"Pass F (cross-category same-vendor integration): {f_count} edges added")


# ==============================================================
# Pass A (整机 specs scan → cp/sensor/hand entries)
# ==============================================================
# Build aliases for compute/sensor/hand entries (longer, more specific names)
compute_alias = {}   # alias_canon → cp_id
sensor_alias = {}
hand_alias = {}
sim_alias = {}

# Hand-built aliases — must be substrings that DON'T appear in generic text
COMPUTE_ALIASES = {
    "jetson agx thor": "cp-jetson-agx-thor",
    "jetson thor": "cp-jetson-agx-thor",
    "agx thor": "cp-jetson-agx-thor",
    "jetson agx orin": "cp1",
    "agx orin": "cp1",
    "jetson orin nx": "cp-jetson-orin-nx",
    "orin nx": "cp-jetson-orin-nx",
    "jetson orin nano": "cp-jetson-orin-nano",
    "orin nano": "cp-jetson-orin-nano",
    "jetson nano": "cp-jetson-nano",
    "jetson xavier": "cp-jetson-agx-xavier",
    "agx xavier": "cp-jetson-agx-xavier",
    "intel nuc": "cp-intel-nuc-13-pro",
    "mac mini": "cp-apple-mac-mini-m4",
    "rk3588": "cp-radxa-rock-5b",
    "radxa rock": "cp-radxa-rock-5b",
    "hailo-8": "cp-hailo-8",
    "hailo 8": "cp-hailo-8",
    "hailo-10": "cp-hailo-10h",
    "hailo 10": "cp-hailo-10h",
    "coral dev": "cp-coral-dev-board",
    "edge tpu": "cp-coral-dev-board",
    "qualcomm robotics": "cp-qualcomm-robotics-rb5",
    "robotics rb5": "cp-qualcomm-robotics-rb5",
    "qrb5165": "cp-qualcomm-robotics-rb5",
}

SENSOR_ALIASES = {
    "realsense d455": "s1",
    "realsense d435": "sensor-realsense-d435i",
    "realsense d457": "sensor-realsense-d457",
    "realsense l515": "sensor-realsense-l515",
    "azure kinect": "sensor-azure-kinect-dk",
    "femto bolt": "sensor-orbbec-femto-bolt",
    "femto mega": "sensor-orbbec-femto-mega",
    "gemini 335": "sensor-orbbec-gemini-335",
    "mech-eye pro": "sensor-mech-mind-pro-m",
    "mech-eye lsr": "sensor-mech-mind-lsr-s",
    "zivid": "sensor-zivid-two-m70",
    "phoxi": "sensor-photoneo-phoxi-m",
    "motioncam": "sensor-photoneo-motioncam-3d",
    "zed 2i": "sensor-stereolabs-zed2i",
    "zed x": "sensor-stereolabs-zed-x",
    "axia80": "s2",
    "ati mini40": "sensor-ati-mini40",
    "mini40": "sensor-ati-mini40",
    "hex-e": "sensor-onrobot-hex-e",
    "gelsight": "sensor-gelsight-mini",
    "vlp-16": "sensor-velodyne-vlp16",
    "alpha prime": "sensor-velodyne-alpha-prime",
    "vls-128": "sensor-velodyne-alpha-prime",
    "ouster os1": "sensor-ouster-os1",
    "hesai at128": "sensor-hesai-at128",
    "pandar": "sensor-hesai-xt16",
    "livox mid-360": "sensor-livox-mid360",
    "livox mid360": "sensor-livox-mid360",
    "livox mid-40": "sensor-livox-mid40",
    "livox hap": "sensor-livox-hap",
    "vectornav vn-100": "sensor-vectornav-vn100",
    "vn-100": "sensor-vectornav-vn100",
    "bmi270": "sensor-bosch-bmi270",
    "xsens mti": "sensor-xsens-mti300",
}

HAND_ALIASES = {
    "shadow hand": "e2",
    "shadow dexterous": "e2",
    "robotiq 2f-85": "e1",
    "robotiq 2f": "e1",
    "inspire rh56": "h25",
    "inspire rh50": "h5",
    "rh56e2": "h25",
    "dg-3f": "h3",
    "dg-5f": "h39",
    "psyonic ability": "h9",
    "ability hand": "h9",
    "allegro hand": "h12",
    "covvi": "h13",
    "gmh18": "h21",
    "wuji hand": "h22",
    "revo 2": "h23",
    "dex5-1": "h26",
    "unitree dex5": "h26",
    "mia hand": "h42",
    "azzurra": "h27",
    "bionicsofthand": "h43",
    "softhand": "h48",
    "orca hand": "h35",
    "dexhand": "h36",
    "dg-5f-m": "h39",
    "magichand": "h47",
    "xhand": "h40",
    "x-hand": "h40",
    "dexh5": "h30",
    "dexh13": "h41",
    "tora-one": "f109",  # actually a humanoid, but PaXini's hand is in tora
}

# Only keep aliases pointing to ids that actually exist
COMPUTE_ALIASES = {k: v for k, v in COMPUTE_ALIASES.items() if v in existing_ids}
SENSOR_ALIASES = {k: v for k, v in SENSOR_ALIASES.items() if v in existing_ids}
HAND_ALIASES = {k: v for k, v in HAND_ALIASES.items() if v in existing_ids}

print(f"\nAliases loaded: compute={len(COMPUTE_ALIASES)}, sensor={len(SENSOR_ALIASES)}, hand={len(HAND_ALIASES)}")

# Scan 整机 (and 机械臂, 数采&遥操) specs
a_count = 0
SPEC_FIELDS_TO_SCAN = ["compute", "sensing", "hands", "vision", "endEffectors", "sensor",
                        "endeffector", "ai", "compute_unit", "brain", "perception"]
for e in all_entries:
    if e["_p"] != "hardware":
        continue
    if e["category"] not in ("整机平台", "机械臂", "数采 & 遥操"):
        continue
    specs = e.get("specs") or {}
    text_blobs = []
    for fld in SPEC_FIELDS_TO_SCAN:
        v = specs.get(fld)
        if v:
            if isinstance(v, list):
                v = " ".join(str(x) for x in v)
            text_blobs.append(str(v))
    if not text_blobs:
        continue
    blob = " ".join(text_blobs).lower()
    # Match each alias as a token sub-sequence (allow it to appear anywhere)
    for alias, tgt_id in COMPUTE_ALIASES.items():
        if alias in blob:
            if add_edge(e["id"], tgt_id, "A:compute"):
                a_count += 1
    for alias, tgt_id in SENSOR_ALIASES.items():
        if alias in blob:
            if add_edge(e["id"], tgt_id, "A:sensor"):
                a_count += 1
    for alias, tgt_id in HAND_ALIASES.items():
        if alias in blob:
            if add_edge(e["id"], tgt_id, "A:hand"):
                a_count += 1

print(f"Pass A (整机/机械臂 specs → component entries): {a_count} edges added")


# ==============================================================
# Pass H (应用场景 reverse-scan deployments → product/company mentions)
# ==============================================================
# Build name aliases for all hardware platforms + industry players
name_alias_to_id = {}
for e in all_entries:
    cat = e["category"]
    if cat not in ("整机平台", "产业", "机械臂"):
        continue
    name = e["name"]
    # Lowercase, alphanumeric-only canon
    base = re.sub(r"\([^)]*\)", "", name).strip().lower()
    base = re.sub(r"[^\w\s]+", " ", base)
    base = re.sub(r"\s+", " ", base).strip()
    if len(base) >= 4:
        name_alias_to_id.setdefault(base, []).append(e["id"])
    # Sub-tokens for short product names (e.g., "Apollo" → ind-apptronik)
    for tok in base.split():
        if len(tok) >= 4:
            name_alias_to_id.setdefault(tok, []).append(e["id"])

# Hand-add some common shortcuts (deployment strings often use these)
EXTRA_NAME_ALIAS = {
    "figure 02": ["f139"],
    "figure 03": ["f104"],
    "figure": ["ind-figure"],
    "apollo": ["f81"],  # Apptronik Apollo robot
    "apptronik": ["ind-apptronik"],
    "spot": [],  # not in our data as a product
    "atlas": ["f29"],
    "boston dynamics": ["ind-boston-dynamics"],
    "anymal": [],  # ANYbotics' product not in data
    "anybotics": ["ind-anybotics"],
    "neo": ["f34", "f122"],
    "1x": ["ind-1x"],
    "digit": ["f130"],
    "agility": ["ind-agility"],
    "stretch": [],
    "starship": [],
    "moxi": [],
    "amazon": [],
    "carbon robotics": [],
    "laserweeder": [],
    "amr": [],
    "locus": [],
    "symbotic": [],
    "mercedes-benz": [],
    "bmw": [],
    "hyundai": [],
    "walker s2": ["f69"],
    "walker s1": ["f135"],
}
for k, v in EXTRA_NAME_ALIAS.items():
    real = [i for i in v if i in existing_ids]
    if real:
        name_alias_to_id.setdefault(k, []).extend(real)

h_count = 0
for e in all_entries:
    if e["category"] != "应用场景":
        continue
    specs = e.get("specs") or {}
    deployments = specs.get("Notable Deployments", [])
    if not isinstance(deployments, list):
        continue
    for dep_str in deployments:
        dep_lower = dep_str.lower()
        # Scan for each known alias
        for alias, tgt_ids in name_alias_to_id.items():
            if alias in dep_lower:
                for tgt_id in tgt_ids:
                    if add_edge(e["id"], tgt_id, "H:deployment"):
                        h_count += 1

print(f"Pass H (应用场景 Notable Deployments → product/company): {h_count} edges added")


# ==============================================================
# MERGE with existing relatedIds + smart cap at 15
# ==============================================================
CATEGORY_PREF = {
    # Cross-category links (most informative) come first
    "产业": 0, "资本": 1, "实验室": 2,
    "基础模型": 3, "数据集": 4, "整机平台": 5,
    "算法框架": 6, "评测基准": 7, "控制算法": 8,
    "仿真平台": 9, "灵巧手 & 夹爪": 10, "机械臂": 11,
    "传感器": 12, "核心零部件": 13, "关节模组": 14,
    "计算平台": 15, "数采 & 遥操": 16, "能源动力": 17,
    "开发生态": 18, "应用场景": 19,
}

# Smart cap: prefer category diversity (max 4 per same category)
CAP_TOTAL = 15
CAP_PER_CAT = 4

stats_per_cat = collections.Counter()
for e in all_entries:
    eid = e["id"]
    existing = list(e.get("relatedIds") or [])
    new = [r for r in edges.get(eid, set()) if r not in existing]
    combined = existing + new

    # Apply per-category cap
    if len(combined) > CAP_TOTAL:
        per_cat_count = collections.Counter()
        result = []
        # Sort candidates by category preference; preserve existing entries' priority
        sorted_combined = sorted(
            combined,
            key=lambda r: (
                0 if r in existing else 1,  # existing entries first
                CATEGORY_PREF.get(id_to_entry.get(r, {}).get("category", ""), 99),
                r
            )
        )
        for rid in sorted_combined:
            r_cat = id_to_entry.get(rid, {}).get("category", "")
            if per_cat_count[r_cat] >= CAP_PER_CAT:
                continue
            result.append(rid)
            per_cat_count[r_cat] += 1
            if len(result) >= CAP_TOTAL:
                break
        # Re-sort by category preference for stable output
        result = sorted(
            result,
            key=lambda r: (CATEGORY_PREF.get(id_to_entry.get(r, {}).get("category", ""), 99), r),
        )
        e["relatedIds"] = result
    elif combined:
        # No need to cap; just sort
        e["relatedIds"] = sorted(
            set(combined),
            key=lambda r: (CATEGORY_PREF.get(id_to_entry.get(r, {}).get("category", ""), 99), r),
        )

    e.pop("_p", None)


# ==============================================================
# WRITE BACK
# ==============================================================
for p in partitions:
    (PUBLIC / f"{p}.json").write_text(
        json.dumps(data[p], ensure_ascii=False, indent=2), encoding="utf-8"
    )


# ==============================================================
# REPORT
# ==============================================================
print("\n=== Final relatedIds density ===")
for p in partitions:
    n = len(data[p])
    with_rel = sum(1 for e in data[p] if e.get("relatedIds"))
    total_rel = sum(len(e.get("relatedIds") or []) for e in data[p])
    avg = total_rel / n if n else 0
    print(f"  {p:9s} {n:>4} entries, {with_rel} with relations ({with_rel*100//n}%), avg {avg:.1f}, total edges {total_rel}")

print("\n=== Sample entries (Phase 2 enrichment) ===")
samples = [
    "ind-unitree",        # Unitree industry
    "f24",                # Unitree H2
    "joint-unitree-a1",   # Unitree A1 actuator (cross-cat link to f24/f140 expected)
    "f69",                # Walker S2 (compute spec mentions Jetson)
    "f34",                # NEO Gamma (compute mentions Jetson Thor)
    "ind-figure",         # Figure AI
    "stg-app-warehouse",  # if exists
    "app1",               # original warehouse app
    "app2",               # original logistics
    "cp1",                # Jetson AGX Orin
    "a1",                 # UR10e (siblings: UR3e/5e/16e/20/30)
]
for sid in samples:
    e = id_to_entry.get(sid)
    if not e:
        continue
    rel = e.get("relatedIds") or []
    print(f"\n  {sid:30s} {e['name'][:30]:30s}  ({len(rel)} relations)")
    for r in rel[:10]:
        re_e = id_to_entry.get(r, {})
        print(f"    → {r:30s} {re_e.get('name','?')[:32]:32s} [{re_e.get('category','?')}]")
