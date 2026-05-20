#!/usr/bin/env python3
"""Extend relations: clean dangling refs + 2 more inference passes."""
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
        e["_partition"] = p
        all_entries.append(e)
        id_to_entry[e["id"]] = e
existing_ids = set(id_to_entry.keys())


def canon(s):
    if not s: return ""
    s = s.lower()
    s = re.sub(r"\s*\([^)]*\)", "", s)
    s = re.sub(r"[^\w一-鿿]+", "", s)
    return s.strip()


# ---- Pass A: Clean dangling relatedIds (pointing to deleted entries) ----
n_dangling = 0
for e in all_entries:
    rel = e.get("relatedIds") or []
    cleaned = [r for r in rel if r in existing_ids]
    removed = len(rel) - len(cleaned)
    if removed:
        e["relatedIds"] = cleaned
        n_dangling += removed
print(f"Pass A: cleaned {n_dangling} dangling relatedIds")


# ---- Build aliases for hardware platforms + simulators (for further passes) ----
hw_alias = {}      # canon_name -> hw id
sim_alias = {}     # canon_name -> sim id
for e in all_entries:
    cat = e["category"]
    name = e["name"]
    c = canon(name)
    if cat in ("整机平台", "机械臂", "灵巧手 & 夹爪"):
        hw_alias[c] = e["id"]
        # Strip parens-content prefix variants
        for part in re.split(r"\s*[/\-(]\s*", name):
            cp = canon(part)
            if len(cp) >= 4 and cp not in hw_alias:
                hw_alias[cp] = e["id"]
    elif cat == "仿真平台":
        sim_alias[c] = e["id"]

# Hand-add common platform aliases for known robot names
EXTRA_HW = {
    "frankapanda": "a2", "panda": "a2", "fer3": "a2", "frankaresearch3": "a2", "fr3": "a2",
    "ur5e": "a1",  # we have UR10e at a1, but UR5e too if exists
    "viperx300": "d2", "widowx250": "d2",  # ALOHA hardware (approx)
    "shadowhand": "e2", "shadowdexteroushand": "e2",
    "alohastationary": "d2",  # rough
}
EXTRA_SIM = {
    "mujoco": "sw6",
    "isaacsim": "sw5", "omniverse": "sw5",
    "isaaclab": "sw3", "isaacgym": "sw3",  # close enough
    "gazebo": "sw-gazebo",
    "pybullet": "sw-pybullet",
    "sapien": "sw-sapien",
    "genesis": "sw-genesis",
    "newton": "sw-newton",
    "drake": "sw-drake",
    "habitat": "sw-habitat2",
    "robosuite": "sw-robosuite",
    "robomimic": "sw4",
    "carla": None,  # not in our data
}
for k, v in EXTRA_HW.items():
    if v in existing_ids:
        hw_alias[k] = v
for k, v in EXTRA_SIM.items():
    if v in existing_ids:
        sim_alias[k] = v


# ---- Pass B: algorithm's specs (training_data / platform / simulator / embodiment / engine) ----
edges = collections.defaultdict(set)

def add_edge(a, b):
    if a == b or a not in existing_ids or b not in existing_ids:
        return
    edges[a].add(b)
    edges[b].add(a)

SPEC_FIELDS = ["training_data", "platform", "simulator", "embodiment", "engine",
               "benchmarks", "benchmark", "tasks", "envs", "supported_robots"]

n_p6 = 0
for e in all_entries:
    if e["_partition"] != "software":
        continue
    specs = e.get("specs") or {}
    for fld in SPEC_FIELDS:
        val = specs.get(fld)
        if not val:
            continue
        if isinstance(val, list):
            val = " ".join(str(v) for v in val)
        if not isinstance(val, str):
            continue
        text_canon = canon(val)
        # Scan for sim aliases
        for sim_canon, sim_id in sim_alias.items():
            if len(sim_canon) >= 4 and sim_canon in text_canon:
                add_edge(e["id"], sim_id)
                n_p6 += 1
        # Scan for hw aliases
        for hw_canon, hw_id in hw_alias.items():
            if len(hw_canon) >= 4 and hw_canon in text_canon:
                add_edge(e["id"], hw_id)
                n_p6 += 1
print(f"Pass B (algorithm specs -> platform/sim): {n_p6} edges added")


# ---- Pass C: paperInfo authors -> labs (loose) ----
# For each algorithm entry with paperInfo.authors, look up author surnames -> known PIs
LAB_PI_NAMES = {
    "chelseafinn": "lab-sail", "feifeili": "lab-sail", "dorsasadigh": "lab-sail",
    "marcopavone": "lab-sail",
    "sergeylevine": "lab-bair-autolab", "kengoldberg": "lab-bair-autolab",
    "pieterabbeel": "lab-bair-autolab",
    "russtedrake": "lab-mit-csail", "danielarus": "lab-mit-csail", "pulkitagrawal": "lab-mit-csail",
    "deepakpathak": "lab-cmu-ri", "abhinavgupta": "lab-cmu-ri",
    "marcohutter": "lab-eth-rsl",
    "lerrelpinto": "lab-nyu-grail",
    "haohuang": "lab-tsinghua-tea", "huazhexu": "lab-tsinghua-tea",
    "haodong": "lab-pku-hyperplane", "wanghe": "lab-pku-hyperplane",
    "vijaykumar": "lab-upenn-grasp", "pratikchaudhari": "lab-upenn-grasp",
}
n_p7 = 0
for e in all_entries:
    pi = e.get("paperInfo") or {}
    authors = pi.get("authors", "")
    if not authors:
        continue
    text = canon(authors)
    for name_canon, lab_id in LAB_PI_NAMES.items():
        if lab_id in existing_ids and name_canon in text:
            add_edge(e["id"], lab_id)
            n_p7 += 1
print(f"Pass C (paper authors -> PI's lab): {n_p7} edges added")


# Merge new edges into existing relatedIds
CATEGORY_PREF = {
    "产业": 0, "资本": 1, "实验室": 2,
    "基础模型": 3, "数据集": 4, "整机平台": 5,
    "算法框架": 6, "评测基准": 7, "控制算法": 8,
    "仿真平台": 9, "灵巧手 & 夹爪": 10, "机械臂": 11,
    "传感器": 12, "核心零部件": 13, "关节模组": 14,
    "计算平台": 15, "数采 & 遥操": 16, "能源动力": 17,
    "开发生态": 18, "应用场景": 19,
}
CAP = 15
for e in all_entries:
    eid = e["id"]
    existing = set(e.get("relatedIds") or [])
    new = edges.get(eid, set())
    combined = existing | new
    if len(combined) > CAP:
        combined = set(sorted(combined, key=lambda r: (
            CATEGORY_PREF.get(id_to_entry.get(r, {}).get("category", ""), 99),
            r
        ))[:CAP])
    if combined:
        e["relatedIds"] = sorted(combined, key=lambda r: (
            CATEGORY_PREF.get(id_to_entry.get(r, {}).get("category", ""), 99),
            r
        ))


# Write back
for p in partitions:
    out = data[p]
    for e in out:
        e.pop("_partition", None)
    (PUBLIC / f"{p}.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
    )


# Report
print("\n=== Final relatedIds density (after extend) ===")
for p in partitions:
    n = len(data[p])
    with_rel = sum(1 for e in data[p] if e.get("relatedIds"))
    total_rel = sum(len(e.get("relatedIds") or []) for e in data[p])
    avg = total_rel / n if n else 0
    print(f"  {p:9s} {n:>4} entries, {with_rel} with relations ({with_rel*100//n}%), avg {avg:.1f} per entry")

# Sample interesting entries
print("\n=== Sample (post-extend) ===")
for sid in ["sw-pi0", "sw-helix", "sw-mobile-aloha", "sw-droid", "sw-galaxea-g0", "lab-bair-autolab", "ind-tesla-optimus"]:
    e = id_to_entry.get(sid)
    if not e: continue
    rel = e.get("relatedIds") or []
    print(f"  {sid:25s} {e['name'][:30]:30s} ({len(rel)} relations)")
    for r in rel[:6]:
        re_entry = id_to_entry.get(r, {})
        print(f"    -> {r:25s} {re_entry.get('name','?')[:32]:32s} [{re_entry.get('category','?')}]")
