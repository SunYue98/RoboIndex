#!/usr/bin/env python3
"""Infer relatedIds across public/data/*.json from existing fields.

Multi-pass:
  1. Manufacturer ↔ product: hardware entries' `company` -> 产业 entries by name.
  2. VC ↔ portfolio: 资本 entries' specs."Notable Portfolio" -> 产业 entries.
  3. Lab/org ↔ algorithm: software entries' `company` strings -> 实验室/产业 entries.
  4. Algorithm ↔ dataset: 基础模型 entries' specs.training_data text -> 数据集 entries.
  5. Lab ↔ research output: 实验室 entries' specs."Notable Projects" -> matching algorithms/datasets.
  6. 整机平台 ↔ flagship product on company entry: 产业 entries' specs."Key Products" -> hardware platform.

All edges become bidirectional. Capped at 15 relations per entity (sorted by category preference).
"""
import json
import re
import collections
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PUBLIC = ROOT / "public/data"

partitions = ["hardware", "software", "ecosystem", "players"]
data = {p: json.loads((PUBLIC / f"{p}.json").read_text(encoding="utf-8")) for p in partitions}
all_entries = []
id_to_entry = {}
for p, lst in data.items():
    for e in lst:
        e["_partition"] = p
        all_entries.append(e)
        id_to_entry[e["id"]] = e


def canon(s):
    if not s: return ""
    s = s.lower()
    s = re.sub(r"\s*\([^)]*\)", "", s)
    s = re.sub(r"[^\w一-鿿]+", "", s)
    return s.strip()


def split_affiliations(s):
    if not s: return []
    parts = re.split(r"\s*[/&,]\s*(?:and\s+)?", s)
    return [p.strip() for p in parts if len(p.strip()) >= 2]


# ---- Build alias index for "parent" categories ----
# alias_to_ids: canon_key -> {entity_id}
alias_to_ids = collections.defaultdict(set)


def register(eid, key):
    c = canon(key)
    if len(c) >= 3:
        alias_to_ids[c].add(eid)


# Register 产业/资本/实验室 by both name and company
for e in all_entries:
    if e["category"] in ("产业", "资本", "实验室"):
        register(e["id"], e["name"])
        register(e["id"], e.get("company", ""))


# Explicit aliases for common lab/company shorthand
EXPLICIT_ALIASES = {
    # Labs (only register if the id exists)
    "stanford": "lab-sail", "sail": "lab-sail", "stanfordai": "lab-sail",
    "ucberkeley": "lab-bair-autolab", "bair": "lab-bair-autolab", "berkeley": "lab-bair-autolab",
    "autolab": "lab-bair-autolab", "ucb": "lab-bair-autolab",
    "mit": "lab-mit-csail", "csail": "lab-mit-csail",
    "cmu": "lab-cmu-ri", "carnegiemellon": "lab-cmu-ri",
    "ethzurich": "lab-eth-rsl", "eth": "lab-eth-rsl", "rsl": "lab-eth-rsl", "roboticsystems": "lab-eth-rsl",
    "nyu": "lab-nyu-grail", "grail": "lab-nyu-grail",
    "mpi": "lab-mpi-is", "mpis": "lab-mpi-is", "maxplanck": "lab-mpi-is",
    "tokyo": "lab-utokyo-jsk", "utokyo": "lab-utokyo-jsk", "jsk": "lab-utokyo-jsk",
    "tsinghua": "lab-tsinghua-tea",
    "pku": "lab-pku-hyperplane", "peking": "lab-pku-hyperplane",
    "shanghaiailab": "lab-shanghai-ailab", "上海人工智能实验室": "lab-shanghai-ailab",
    "usc": "lab-usc-lira",
    "kaist": "lab-kaist-hubo",
    "gatech": "lab-gatech-irim", "georgia": "lab-gatech-irim", "georgiatech": "lab-gatech-irim",
    "iit": "lab-iit-icub",
    "jpl": "lab-jpl-robotics", "nasa": "lab-jpl-robotics",
    "imperial": "lab-imperial-prl", "imperialcollege": "lab-imperial-prl",
    "princeton": "lab-princeton-visualai",
    "upenn": "lab-upenn-grasp", "penn": "lab-upenn-grasp", "pennsylvania": "lab-upenn-grasp",
    "grasp": "lab-upenn-grasp",
    "epfl": "lab-epfl-biorob",
    # Industrial players
    "nvidia": "ind1",
    "googledeepmind": "ind-deepmind-robotics", "deepmind": "ind-deepmind-robotics", "google": "ind-deepmind-robotics",
    "tri": "ind-tri", "toyotaresearchinstitute": "ind-tri", "toyota": "ind-tri",
    "physicalintelligence": "ind-physical-intelligence", "pi": "ind-physical-intelligence",
    "skildai": "ind-skild", "skild": "ind-skild",
    "tesla": "ind-tesla-optimus",
    "figure": "ind-figure", "figureai": "ind-figure",
    "1x": "ind-1x", "1xtechnologies": "ind-1x",
    "sanctuary": "ind-sanctuary", "sanctuaryai": "ind-sanctuary",
    "bostondynamics": "ind-boston-dynamics", "波士顿动力": "ind-boston-dynamics",
    "apptronik": "ind-apptronik",
    "agility": "ind-agility", "agilityrobotics": "ind-agility",
    "unitree": "ind-unitree", "宇树": "ind-unitree", "unitreerobotics": "ind-unitree",
    "xpeng": "ind-xpeng-robotics", "小鹏": "ind-xpeng-robotics",
    "agibot": "ind-agibot", "智元": "ind-agibot", "智元机器人": "ind-agibot",
    "ubtech": "ind-ubtech", "优必选": "ind-ubtech",
    "fourier": "ind-fourier", "傅利叶": "ind-fourier", "傅利叶智能": "ind-fourier", "fourierintelligence": "ind-fourier",
    "robotera": "ind-robot-era", "星动纪元": "ind-robot-era",
    "galbot": "ind-galbot", "银河通用": "ind-galbot",
    "booster": "ind-booster", "boosterrobotics": "ind-booster",
    "limx": "ind-limx", "逐际动力": "ind-limx", "limxdynamics": "ind-limx",
    "engineeredarts": "ind-engineered-arts",
    "palrobotics": "ind-pal-robotics",
    "anybotics": "ind-anybotics",
    "dexterity": "ind-dexterity",
    "picklerobot": "ind-pickle",
    "hellorobot": "ind-hello-robot",
    # VCs
    "sequoia": "vc1", "sequoiacapital": "vc1",
    "a16z": "vc-a16z", "andreessenhorowitz": "vc-a16z",
    "khosla": "vc-khosla", "khoslaventures": "vc-khosla",
    "lux": "vc-lux", "luxcapital": "vc-lux",
    "foundersfund": "vc-founders-fund",
    "bessemer": "vc-bessemer", "bessemerventurepartners": "vc-bessemer",
    "gv": "vc-gv", "googleventures": "vc-gv",
    "innovationendeavors": "vc-innovation-endeavors",
    "tigerglobal": "vc-tiger-global",
    "ggv": "vc-ggv", "ggvcapital": "vc-ggv",
    "sinovation": "vc-sinovation", "创新工场": "vc-sinovation",
    "5y": "vc-5y", "5ycapital": "vc-5y", "五源": "vc-5y",
    "hillhouse": "vc-hillhouse", "高瓴": "vc-hillhouse",
    "hongshan": "vc-hongshan", "红杉": "vc-hongshan",
    "idg": "vc-idg", "idgcapital": "vc-idg",
    "sourcecode": "vc-source-code", "源码": "vc-source-code",
}

existing_ids = set(id_to_entry.keys())
for alias, target_id in EXPLICIT_ALIASES.items():
    if target_id in existing_ids:
        alias_to_ids[canon(alias)].add(target_id)


# ---- Index datasets/models by canon name ----
dataset_alias = {}  # canon_name -> dataset id
model_alias = {}    # canon_name -> model id
hardware_alias = {}  # canon_name -> hw id

for e in all_entries:
    cat = e["category"]
    name = e["name"]
    c = canon(name)
    # Sub-name (strip parens etc.)
    if cat == "数据集":
        dataset_alias[c] = e["id"]
        # Also register name parts (e.g., "Open X-Embodiment (RT-X Dataset)" -> register both)
        for part in split_affiliations(name):
            cp = canon(part)
            if len(cp) >= 4 and cp not in dataset_alias:
                dataset_alias[cp] = e["id"]
    elif cat == "基础模型":
        model_alias[c] = e["id"]
    elif cat == "整机平台":
        hardware_alias[c] = e["id"]


# ---- Edge accumulator ----
edges = collections.defaultdict(set)  # entity_id -> {related_id}


def add_edge(a_id, b_id):
    if a_id == b_id:
        return
    if a_id not in existing_ids or b_id not in existing_ids:
        return
    edges[a_id].add(b_id)
    edges[b_id].add(a_id)


# ---- Pass 1: Manufacturer ↔ product (hardware company -> 产业) ----
n_p1 = 0
for e in all_entries:
    if e["_partition"] != "hardware":
        continue
    comp = e.get("company", "")
    if not comp:
        continue
    # Try alias map
    c = canon(comp)
    if c in alias_to_ids:
        for parent in alias_to_ids[c]:
            add_edge(e["id"], parent)
            n_p1 += 1
print(f"Pass 1 (manufacturer ↔ hardware): {n_p1} edges added")


# ---- Pass 2: VC ↔ portfolio ----
n_p2 = 0
for e in all_entries:
    if e["category"] != "资本":
        continue
    portfolio = e.get("specs", {}).get("Notable Portfolio", [])
    if not isinstance(portfolio, list):
        continue
    for company_name in portfolio:
        c = canon(company_name)
        if c in alias_to_ids:
            for target in alias_to_ids[c]:
                add_edge(e["id"], target)
                n_p2 += 1
print(f"Pass 2 (VC ↔ portfolio): {n_p2} edges added")


# ---- Pass 3: Software entries' company -> labs/companies ----
n_p3 = 0
for e in all_entries:
    if e["_partition"] != "software":
        continue
    comp = e.get("company", "")
    if not comp:
        continue
    for part in split_affiliations(comp):
        c = canon(part)
        if c in alias_to_ids:
            for target in alias_to_ids[c]:
                add_edge(e["id"], target)
                n_p3 += 1
print(f"Pass 3 (algorithm ↔ lab/org): {n_p3} edges added")


# ---- Pass 4: Algorithm ↔ training dataset ----
n_p4 = 0
for e in all_entries:
    if e["category"] != "基础模型":
        continue
    train = e.get("specs", {}).get("training_data", "")
    if not train:
        continue
    train_canon = canon(train)
    # Look for known dataset names as substrings of canon(training_data)
    for ds_canon, ds_id in dataset_alias.items():
        if len(ds_canon) >= 5 and ds_canon in train_canon:
            add_edge(e["id"], ds_id)
            n_p4 += 1
print(f"Pass 4 (model ↔ training dataset): {n_p4} edges added")


# ---- Pass 5: Lab/Industry "Notable Projects" / "Key Products" -> products ----
n_p5 = 0
for e in all_entries:
    if e["category"] not in ("实验室", "产业"):
        continue
    specs = e.get("specs", {})
    project_lists = []
    for key in ("Notable Projects", "Key Products"):
        if isinstance(specs.get(key), list):
            project_lists.extend(specs[key])
    for proj_name in project_lists:
        c = canon(proj_name)
        # Try to match models, hardware, datasets
        for amap in (model_alias, hardware_alias, dataset_alias):
            if c in amap:
                add_edge(e["id"], amap[c])
                n_p5 += 1
                break
        else:
            # Try partial: any model/hw whose canon name contains this one (or vice versa)
            if len(c) >= 4:
                for amap in (model_alias, hardware_alias):
                    for target_canon, target_id in amap.items():
                        if c == target_canon:
                            add_edge(e["id"], target_id)
                            n_p5 += 1
                            break
print(f"Pass 5 (lab/industry ↔ key products): {n_p5} edges added")


# ---- Cap: limit each entity to 15 relatedIds, prefer cross-category ----
CATEGORY_PREF = {
    # Categories listed earlier get higher priority when capping
    "产业": 0, "资本": 1, "实验室": 2,
    "基础模型": 3, "数据集": 4, "整机平台": 5,
    "算法框架": 6, "评测基准": 7, "控制算法": 8,
    "仿真平台": 9, "灵巧手 & 夹爪": 10, "机械臂": 11,
    "传感器": 12, "核心零部件": 13, "关节模组": 14,
    "计算平台": 15, "数采 & 遥操": 16, "能源动力": 17,
    "开发生态": 18, "应用场景": 19,
}

CAP = 15
n_pre = sum(len(v) for v in edges.values())
for eid, rels in edges.items():
    if len(rels) <= CAP:
        continue
    # Sort by category preference, then alphabetically for stability
    sorted_rels = sorted(rels, key=lambda r: (
        CATEGORY_PREF.get(id_to_entry.get(r, {}).get("category", ""), 99),
        r
    ))
    edges[eid] = set(sorted_rels[:CAP])

n_post = sum(len(v) for v in edges.values())
print(f"\nCap pass: trimmed {n_pre - n_post} edges (now {n_post} total directed edges)")


# ---- Merge edges into entities' relatedIds (preserve existing, add new, dedupe) ----
for e in all_entries:
    eid = e["id"]
    existing = set(e.get("relatedIds") or [])
    new = edges.get(eid, set())
    merged = sorted(existing | new, key=lambda r: (
        CATEGORY_PREF.get(id_to_entry.get(r, {}).get("category", ""), 99),
        r
    ))
    if merged:
        e["relatedIds"] = merged
    # Strip our internal field
    e.pop("_partition", None)


# ---- Write back ----
for p in partitions:
    out = data[p]
    for e in out:
        e.pop("_partition", None)
    (PUBLIC / f"{p}.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
    )


# ---- Report ----
print("\n=== Final relatedIds density ===")
for p in partitions:
    n = len(data[p])
    with_rel = sum(1 for e in data[p] if e.get("relatedIds"))
    avg = sum(len(e.get("relatedIds") or []) for e in data[p]) / n if n else 0
    print(f"  {p:9s} {n:>4} entries, {with_rel} with relations ({with_rel*100//n}%), avg {avg:.1f} per entry")

# Sample some entities to verify
print("\n=== Sample relations ===")
sample_ids = ["ind1", "vc1", "lab-sail", "sw1", "f4", "sw-cosmos-predict", "vc-khosla"]
for sid in sample_ids:
    e = id_to_entry.get(sid)
    if not e:
        continue
    rels = e.get("relatedIds") or []
    print(f"  {sid:25s} {e['name'][:30]:30s} ({len(rels)} relations)")
    for r in rels[:8]:
        re_entry = id_to_entry.get(r, {})
        print(f"    -> {r:25s} {re_entry.get('name','?')[:30]:30s} [{re_entry.get('category','?')}]")
