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
    "baidu": [],
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
    # Chinese VCs added in batch_p11
    "tencent": ["stg-vc-tencent"],
    "tencent investment": ["stg-vc-tencent"],
    "tencent holdings": ["stg-vc-tencent"],
    "alibaba": ["stg-vc-alibaba"],
    "alibaba group": ["stg-vc-alibaba"],
    "ant group": ["stg-vc-alibaba"],  # Ant Group is Alibaba-affiliated; closest match
    "meituan": ["stg-vc-meituan"],
    "meituan strategy": ["stg-vc-meituan"],
    "meituan strategic": ["stg-vc-meituan"],
    "catl": ["stg-vc-catl"],
    "contemporary amperex": ["stg-vc-catl"],
    "geely": ["stg-vc-geely"],
    "geely capital": ["stg-vc-geely"],
    "geely holding": ["stg-vc-geely"],
    "zhenfund": ["stg-vc-zhenfund"],
    "真格基金": ["stg-vc-zhenfund"],
    "qiming": ["stg-vc-qiming"],
    "qiming venture": ["stg-vc-qiming"],
    "启明创投": ["stg-vc-qiming"],
    "bluerun": ["stg-vc-bluerun"],
    "bluerun ventures": ["stg-vc-bluerun"],
    "lanchi": ["stg-vc-bluerun"],
    "lanchi ventures": ["stg-vc-bluerun"],
    "蓝驰创投": ["stg-vc-bluerun"],
    "shunwei": ["stg-vc-shunwei"],
    "shunwei capital": ["stg-vc-shunwei"],
    "顺为资本": ["stg-vc-shunwei"],
    "matrix partners china": ["stg-vc-matrix-china"],
    "经纬创投": ["stg-vc-matrix-china"],
    "mpc": ["stg-vc-matrix-china"],
    "beijing robot": ["stg-vc-bj-robot-fund"],
    "beijing robot industry": ["stg-vc-bj-robot-fund"],
    "shenzhen capital group": ["stg-vc-scg"],
    "scgc": ["stg-vc-scg"],
    "深圳市创新投资集团": ["stg-vc-scg"],
    # batch_p12 (Tier A global VCs) — name mismatches / canon-stripped cases
    "microsoft": ["stg-vc-msft"],
    "openai": ["stg-vc-openai-corp"],
    "intel": ["stg-vc-intel-capital"],
    "intel capital": ["stg-vc-intel-capital"],
    "ark invest": ["stg-vc-ark-invest"],
    "salesforce": ["stg-vc-salesforce-ventures"],
    "salesforce ventures": ["stg-vc-salesforce-ventures"],
    "macquarie capital": ["stg-vc-macquarie-capital"],
    "brookfield asset management": ["stg-vc-brookfield"],
    "jeff bezos": ["stg-vc-bezos-expeditions"],
    "bezos expeditions": ["stg-vc-bezos-expeditions"],
    "samsung": ["stg-vc-samsung-next"],
    "samsung electronics": ["stg-vc-samsung-next"],
    "sk telecom": [],  # no entity
    "softbank": ["stg-vc-softbank"],
    "softbank group": ["stg-vc-softbank"],
    "qualcomm ventures": ["stg-vc-qualcomm-ventures"],
    "alphabet": ["stg-vc-capitalg"],
    "redpoint": ["stg-vc-redpoint"],
    "lightspeed": ["stg-vc-lightspeed"],
    "lightspeed venture": ["stg-vc-lightspeed"],
    "coatue": ["stg-vc-coatue"],
    "felicis": ["stg-vc-felicis"],
    "menlo": ["stg-vc-menlo-ventures"],
    "crv": ["stg-vc-crv"],
    "charles river": ["stg-vc-crv"],
    "alexa fund": ["stg-vc-alexa-fund"],
    "amazon alexa fund": ["stg-vc-alexa-fund"],
    "amazon industrial innovation": ["stg-vc-amazon-industrial-innovation"],
    "amazon industrial innovation fund": ["stg-vc-amazon-industrial-innovation"],
    "bdc": ["stg-vc-bdc-capital"],
    "bdc capital": ["stg-vc-bdc-capital"],
    "business development bank of canada": ["stg-vc-bdc-capital"],
    "edc": ["stg-vc-edc"],
    "export development canada": ["stg-vc-edc"],
    "magna international": ["stg-vc-magna"],
    "verizon": ["stg-vc-verizon-ventures"],
    "verizon ventures": ["stg-vc-verizon-ventures"],
    "workday": ["stg-vc-workday-ventures"],
    "workday ventures": ["stg-vc-workday-ventures"],
    "mercedes benz": ["stg-vc-mercedes-benz"],
    "at t": ["stg-vc-att-ventures"],
    "at t ventures": ["stg-vc-att-ventures"],
    "att ventures": ["stg-vc-att-ventures"],
    "b": ["stg-vc-b-capital"],
    "deere": ["stg-vc-john-deere"],
    "deere company": ["stg-vc-john-deere"],
    "skagerak": ["stg-vc-skagerak-capital"],
    "nistad": ["stg-vc-nistad-group"],
    "factory": ["stg-vc-capital-factory"],
    "capital factory": ["stg-vc-capital-factory"],
    # batch_p13 (Tier B Chinese funds + strategics) — aliases for name mismatches
    "dcvc": ["stg-vc-dcvc"],
    "data collective": ["stg-vc-dcvc"],
    "playground": ["stg-vc-playground-global"],
    "playground global": ["stg-vc-playground-global"],
    "mfv": ["stg-vc-mfv-partners"],
    "itic": ["stg-vc-itic"],
    "industrial technology investment corporation": ["stg-vc-itic"],
    "robotics hub": ["stg-vc-robotics-hub"],
    "coal hill": ["stg-vc-robotics-hub"],
    "coal hill ventures": ["stg-vc-robotics-hub"],
    "safar": ["stg-vc-safar-partners"],
    "safar partners": ["stg-vc-safar-partners"],
    "sony innovation": ["stg-vc-sony-innovation-fund"],
    "sony innovation fund": ["stg-vc-sony-innovation-fund"],
    "sony group": ["stg-vc-sony-innovation-fund"],
    "tdk": ["stg-vc-tdk-ventures"],
    "tdk ventures": ["stg-vc-tdk-ventures"],
    "brv": ["stg-vc-bluerun"],
    "brv partners": ["stg-vc-bluerun"],
    "longqi technology": ["stg-vc-longcheer"],
    "shanghai longcheer": ["stg-vc-longcheer"],
    "longcheer": ["stg-vc-longcheer"],
    "wolong electric": ["stg-vc-wolong"],
    "wolong": ["stg-vc-wolong"],
    "huafa group": ["stg-vc-huafa"],
    "huafa": ["stg-vc-huafa"],
    "china mobile": ["stg-vc-china-mobile"],
    "jinqiu": ["stg-vc-jinqiu"],
    "china development bank": ["stg-vc-cdb-capital"],
    "cdb": ["stg-vc-cdb-capital"],
    "cdb capital": ["stg-vc-cdb-capital"],
    "cdb sci-tech innovation fund": ["stg-vc-cdb-capital"],
    "国开金融": ["stg-vc-cdb-capital"],
    "beijing robotics industry": ["stg-vc-bj-robot-fund"],
    "beijing robot industry development": ["stg-vc-bj-robot-fund"],
    "beijing robotics industry fund": ["stg-vc-bj-robot-fund"],
    "beijing robot industry development fund": ["stg-vc-bj-robot-fund"],
    "beijing ai industry": ["stg-vc-beijing-ai-fund"],
    "beijing ai industry investment": ["stg-vc-beijing-ai-fund"],
    "beijing artificial intelligence industry": ["stg-vc-beijing-ai-fund"],
    "beijing artificial intelligence industry investment": ["stg-vc-beijing-ai-fund"],
    "granite asia": ["vc-ggv"],
    "ggv asia": ["vc-ggv"],
    "baic": ["stg-vc-baic-capital"],
    "baic capital": ["stg-vc-baic-capital"],
    "baic industrial": ["stg-vc-baic-capital"],
    "baic industrial investment": ["stg-vc-baic-capital"],
    "beijing automotive group industrial investment": ["stg-vc-baic-capital"],
    "sensetime guoxiang": ["stg-vc-sense-capital"],
    "sense capital": ["stg-vc-sense-capital"],
    "商汤国香资本": ["stg-vc-sense-capital"],
    "iflytek": ["stg-vc-iflytek-fund"],
    "iflytek fund": ["stg-vc-iflytek-fund"],
    "iflytek industry fund": ["stg-vc-iflytek-fund"],
    "lighthouse": ["stg-vc-lighthouse-capital"],
    "lighthouse capital": ["stg-vc-lighthouse-capital"],
    "光源资本": ["stg-vc-lighthouse-capital"],
    "cdh": ["stg-vc-cdh"],
    "cdh investments": ["stg-vc-cdh"],
    "鼎晖投资": ["stg-vc-cdh"],
    "haier": ["stg-vc-haier-capital"],
    "haier capital": ["stg-vc-haier-capital"],
    "海尔资本": ["stg-vc-haier-capital"],
    "houxue": ["stg-vc-houxue"],
    "houxue capital": ["stg-vc-houxue"],
    "厚雪资本": ["stg-vc-houxue"],
    "meridian": ["stg-vc-meridian-china"],
    "meridian capital": ["stg-vc-meridian-china"],
    "meridian capital china": ["stg-vc-meridian-china"],
    "xianghe": ["stg-vc-xianghe"],
    "xianghe capital": ["stg-vc-xianghe"],
    "襄禾资本": ["stg-vc-xianghe"],
    "zhejiang fore intelligent": ["stg-vc-fore-intelligent"],
    "zhejiang fore intelligent technology": ["stg-vc-fore-intelligent"],
    "zhejiang fore": ["stg-vc-fore-intelligent"],
    "fore intelligent": ["stg-vc-fore-intelligent"],
    "crystal stream": ["stg-vc-crystal-stream"],
    "crystal stream capital": ["stg-vc-crystal-stream"],
    "清流资本": ["stg-vc-crystal-stream"],
    "晶流资本": ["stg-vc-crystal-stream"],  # known typo from source data
    "tsinghua": ["stg-vc-tsinghua-holdings"],
    "tsinghua tiancheng": ["stg-vc-tsinghua-holdings"],
    "qingkong tiancheng": ["stg-vc-tsinghua-holdings"],
    "tsinghua tiancheng ventures": ["stg-vc-tsinghua-holdings"],
    "清华控股": ["stg-vc-tsinghua-holdings"],
    "清控天诚": ["stg-vc-tsinghua-holdings"],
    "clearvue": ["stg-vc-clearvue"],
    "clearvue partners": ["stg-vc-clearvue"],
    "凯辉资本": ["stg-vc-clearvue"],
    "visionplus": ["stg-vc-visionplus"],
    "visionplus capital": ["stg-vc-visionplus"],
    "yuanjing": ["stg-vc-visionplus"],  # likely typo for 元璟资本 per agent
    "yuanjing capital": ["stg-vc-visionplus"],
    "元景资本": ["stg-vc-visionplus"],  # known typo from source data
    "元璟资本": ["stg-vc-visionplus"],
    "orinno": ["stg-vc-orinno"],
    "orinno capital": ["stg-vc-orinno"],
    "langmafeng": ["stg-vc-orinno"],
    "朗玛峰创投": ["stg-vc-orinno"],
    "lenovo": ["stg-vc-lenovo-capital"],
    "lenovo capital": ["stg-vc-lenovo-capital"],
    "lenovo ventures": ["stg-vc-lenovo-capital"],
    "联想创投": ["stg-vc-lenovo-capital"],
    "century golden resources": ["stg-vc-century-golden-resources"],
    "世纪金源": ["stg-vc-century-golden-resources"],
    "stone": ["stg-vc-stone-venture"],
    "stone venture": ["stg-vc-stone-venture"],
    "oriental fortune": ["stg-vc-oriental-fortune"],
    "oriental fortune capital": ["stg-vc-oriental-fortune"],
    "东方富海": ["stg-vc-oriental-fortune"],
    "costone": ["stg-vc-costone"],
    "costone capital": ["stg-vc-costone"],
    "shenzhen co stone": ["stg-vc-costone"],
    "shenzhen co stone asset": ["stg-vc-costone"],
    "shenzhen co-stone": ["stg-vc-costone"],
    "深圳基石资产": ["stg-vc-costone"],
    "基石资本": ["stg-vc-costone"],
    "jd": ["stg-vc-jd"],
    "jd com": ["stg-vc-jd"],
    "京东": ["stg-vc-jd"],
    "zhongding": ["stg-vc-zhongding"],
    "zhongding sealing": ["stg-vc-zhongding"],
    "中鼎股份": ["stg-vc-zhongding"],
    "nrb": ["stg-vc-nrb"],
    "nrb corp": ["stg-vc-nrb"],
    "changzhou nrb": ["stg-vc-nrb"],
    "kyland": ["stg-vc-kyland"],
    "kyland technology": ["stg-vc-kyland"],
    "东土科技": ["stg-vc-kyland"],
    "innoangel": ["stg-vc-innoangel"],
    "innoangel fund": ["stg-vc-innoangel"],
    "英诺天使基金": ["stg-vc-innoangel"],
    "jinding": ["stg-vc-jinding"],
    "jinding capital": ["stg-vc-jinding"],
    "金鼎资本": ["stg-vc-jinding"],
    # Carnegie Mellon University as Skild AI tech-transfer investor → existing lab entity
    "carnegie mellon university": ["lab-cmu-ri"],
    "carnegie mellon": ["lab-cmu-ri"],
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
