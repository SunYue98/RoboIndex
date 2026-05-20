#!/usr/bin/env python3
"""Apply funding round data to companies + derive VC portfolio mirror.

Input: research/funding_rounds.json (produced by the funding research agent)
  Shape: { "ind-figure": [ {round, year, amount, leadInvestor, investors:[{name, id?}], valuation?, source}, ... ], ... }

Output: updates public/data/players.json
  - For each 产业 (company) entry in the input map: write its fundingRounds list
  - For each 资本 (VC) entry in our data: derive a portfolio list by reverse-scanning
    all companies' fundingRounds for occurrences of this VC

Validation:
  - Every round must have a non-empty source.url
  - Drops entries that fail validation; reports them
"""
import json
import re
import collections
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PUBLIC = ROOT / "public/data"
INPUT = ROOT / "research/funding_rounds.json"

if not INPUT.exists():
    print(f"FATAL: {INPUT} does not exist yet. Wait for the agent to finish, save its output there, then re-run.")
    exit(1)

input_data = json.loads(INPUT.read_text(encoding="utf-8"))

# Load live data
partitions = ["hardware", "software", "ecosystem", "players"]
data = {p: json.loads((PUBLIC / f"{p}.json").read_text(encoding="utf-8")) for p in partitions}
id_to_entry = {}
for p, lst in data.items():
    for e in lst:
        id_to_entry[e["id"]] = e

# Build investor-name → id index (VCs + industrial-strategic investors)
def canon(s):
    if not s: return ""
    s = s.lower()
    s = re.sub(r"\([^)]*\)", "", s)
    # Drop common VC suffixes for matching: "Sequoia Capital" ≈ "Sequoia"
    s = re.sub(r"\b(capital|ventures|partners|management|fund|funds|llc|inc\.?|llp|holdings?)\b", " ", s)
    s = re.sub(r"[^\w\s一-鿿]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

investor_name_to_id = {}
for eid, e in id_to_entry.items():
    if e["category"] not in ("资本", "产业"):
        continue
    name = e.get("name", "")
    company = e.get("company", "")
    for s in (name, company):
        c = canon(s)
        if len(c) >= 3:
            investor_name_to_id.setdefault(c, []).append(eid)
            # Also register without "robotics" / common suffix
            stripped = re.sub(r"\b(robotics|robot|tech|technology|technologies)\b", "", c).strip()
            if stripped and stripped != c and len(stripped) >= 3:
                investor_name_to_id.setdefault(stripped, []).append(eid)

# Manual aliases for tricky investor names
EXTRA_INVESTOR_ALIASES = {
    "microsoft": [],  # no entity for Microsoft Corp
    "openai": [],
    "openai startup fund": [],
    "amazon": [],
    "intel capital": [],  # different from intel sensors
    "intel": [],
    "ark invest": [],
    "salesforce ventures": [],
    "macquarie capital": [],
    "brookfield asset management": [],
    "jeff bezos": [],
    "samsung": [],
    "samsung electronics": [],
    "sk telecom": [],
    "softbank": [],
    "qualcomm ventures": [],
    "tencent": [],
    "alibaba": [],
    "baidu": [],
    "meituan": [],
    "hyundai": [],
    "honda": [],
    "lg electronics": [],
    "bond": [],
    # Real matches (verify these ids exist)
    "nvidia": ["ind1"],
    "sequoia": ["vc1"],
    "sequoia china": ["vc-hongshan"],
    "hongshan": ["vc-hongshan"],
    "andreessen horowitz": ["vc-a16z"],
    "a16z": ["vc-a16z"],
    "khosla": ["vc-khosla"],
    "lux": ["vc-lux"],
    "founders fund": ["vc-founders-fund"],
    "bessemer": ["vc-bessemer"],
    "google ventures": ["vc-gv"],
    "gv": ["vc-gv"],
    "innovation endeavors": ["vc-innovation-endeavors"],
    "tiger global": ["vc-tiger-global"],
    "ggv": ["vc-ggv"],
    "sinovation": ["vc-sinovation"],
    "5y": ["vc-5y"],
    "5y capital": ["vc-5y"],
    "morningside": ["vc-5y"],  # 5Y was Morningside
    "hillhouse": ["vc-hillhouse"],
    "idg": ["vc-idg"],
    "idg capital": ["vc-idg"],
    "source code": ["vc-source-code"],
    "deepmind": ["ind-deepmind-robotics"],
    "google deepmind": ["ind-deepmind-robotics"],
    "google": ["ind-deepmind-robotics"],
}
for k, v in EXTRA_INVESTOR_ALIASES.items():
    real_v = [x for x in v if x in id_to_entry]
    if real_v:
        investor_name_to_id.setdefault(canon(k), []).extend(real_v)

# Apply fundingRounds to each company
valid_count = 0
skipped = []
mapped_investor_count = 0
total_investors = 0

for company_id, rounds in input_data.items():
    if company_id.startswith("_"):
        continue
    if not isinstance(rounds, list):
        continue
    if company_id not in id_to_entry:
        skipped.append(f"  missing company id: {company_id}")
        continue

    cleaned_rounds = []
    for r in rounds:
        # Validate source
        src = r.get("source")
        if not src or not src.get("url"):
            skipped.append(f"  {company_id}: round has no source URL — DROPPED")
            continue
        # Coerce: investors should be list of {name, id?}
        raw_investors = r.get("investors", [])
        if not isinstance(raw_investors, list):
            raw_investors = []
        normalized_investors = []
        for inv in raw_investors:
            if isinstance(inv, str):
                inv_name = inv
                inv_id = None
            elif isinstance(inv, dict):
                inv_name = inv.get("name", "")
                inv_id = inv.get("id")
            else:
                continue
            if not inv_name:
                continue
            total_investors += 1
            # If id not provided, try to match via alias
            if not inv_id:
                c = canon(inv_name)
                matches = investor_name_to_id.get(c) or []
                if matches:
                    inv_id = matches[0]
                    mapped_investor_count += 1
            else:
                if inv_id not in id_to_entry:
                    inv_id = None  # stale id — drop
            normalized_investors.append({"name": inv_name, **({"id": inv_id} if inv_id else {})})

        cleaned = {
            **{k: v for k, v in r.items() if k != "investors"},
            "investors": normalized_investors,
        }
        cleaned_rounds.append(cleaned)
        valid_count += 1

    if cleaned_rounds:
        id_to_entry[company_id]["fundingRounds"] = cleaned_rounds


# Build VC portfolio (reverse mirror)
vc_portfolio = collections.defaultdict(list)
for company_id, rounds in input_data.items():
    if company_id.startswith("_"):
        continue
    if company_id not in id_to_entry:
        continue
    company_name = id_to_entry[company_id]["name"]
    for r in id_to_entry[company_id].get("fundingRounds", []) or []:
        src = r["source"]
        lead_name = r.get("leadInvestor")
        for inv in r.get("investors", []):
            inv_id = inv.get("id")
            if not inv_id:
                continue  # only mirror to VCs/companies in our DB
            is_lead = (lead_name and lead_name == inv["name"])
            vc_portfolio[inv_id].append({
                "companyName": company_name,
                "companyId": company_id,
                "round": r.get("round"),
                "year": r.get("year"),
                "amount": r.get("amount"),
                "leadInvestor": bool(is_lead),
                "source": src,
            })

# Write portfolio to each VC entity
for vc_id, portfolio in vc_portfolio.items():
    if vc_id in id_to_entry:
        # De-dup (a VC could appear twice in the same round if data is messy)
        seen = set()
        deduped = []
        for p in portfolio:
            key = (p["companyId"], p["round"] or "", p["year"] or "")
            if key in seen: continue
            seen.add(key)
            deduped.append(p)
        # Sort newest-first
        deduped.sort(key=lambda x: (x["year"] or "", x["companyId"]), reverse=True)
        id_to_entry[vc_id]["portfolio"] = deduped


# Also update relatedIds bidirectionally: company ↔ investor entity
n_new_rels = 0
for company_id, rounds in input_data.items():
    if company_id.startswith("_"):
        continue
    if company_id not in id_to_entry:
        continue
    for r in id_to_entry[company_id].get("fundingRounds", []) or []:
        for inv in r.get("investors", []):
            inv_id = inv.get("id")
            if not inv_id:
                continue
            # Add bidirectional link
            for src_id, tgt_id in [(company_id, inv_id), (inv_id, company_id)]:
                e = id_to_entry[src_id]
                rel = e.get("relatedIds") or []
                if tgt_id not in rel:
                    rel.append(tgt_id)
                    e["relatedIds"] = rel
                    n_new_rels += 1


# Cap relatedIds at 15 with per-category preference (re-using the rule from build_phase2)
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
for e in id_to_entry.values():
    rel = e.get("relatedIds") or []
    if len(rel) <= CAP:
        if rel:
            e["relatedIds"] = sorted(
                set(rel),
                key=lambda r: (CATEGORY_PREF.get(id_to_entry.get(r, {}).get("category", ""), 99), r),
            )
        continue
    sorted_rels = sorted(
        set(rel),
        key=lambda r: (CATEGORY_PREF.get(id_to_entry.get(r, {}).get("category", ""), 99), r),
    )
    e["relatedIds"] = sorted_rels[:CAP]


# Write all 4 partitions
for p in partitions:
    (PUBLIC / f"{p}.json").write_text(
        json.dumps(data[p], ensure_ascii=False, indent=2), encoding="utf-8"
    )


# ---- Report ----
print(f"=== apply_funding_rounds.py ===\n")
print(f"Valid funding rounds applied: {valid_count}")
print(f"Investors total: {total_investors}, mapped to entities: {mapped_investor_count} ({mapped_investor_count*100//total_investors if total_investors else 0}%)")
print(f"VC portfolio mirror: {sum(len(p) for p in vc_portfolio.values())} entries across {len(vc_portfolio)} VCs")
print(f"New bidirectional relatedIds: {n_new_rels}")
if skipped:
    print(f"\nSkipped (drops):")
    for s in skipped[:20]:
        print(s)

print("\nPer-company funding round count:")
for cid, e in id_to_entry.items():
    fr = e.get("fundingRounds") or []
    if fr:
        print(f"  {cid:30s} {e['name'][:25]:25s} — {len(fr)} rounds")

print("\nPer-VC portfolio size:")
for vid, e in id_to_entry.items():
    pf = e.get("portfolio") or []
    if pf:
        print(f"  {vid:30s} {e['name'][:25]:25s} — {len(pf)} investments")
