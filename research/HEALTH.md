# RoboIndex Health Report

_Generated: 2026-05-21_

## TL;DR

| Metric | Value | Grade |
|---|---:|:---:|
| Schema errors | **0** | 🟢 |
| Source attribution coverage | 665/667 (99%) | 🟢 |
| Image coverage (real + synthetic-canonical) | 293+131/667 (63%) | 🟠 |
| Typed relations | 497/667 (74%) | 🟠 |
| sourcedSpecs (Claim form) | 418/667 (62%) | 🟠 |
| URL liveness (cached, 2026-05-21) | 1071/1142 alive (93%) | 🟡 |

## Migration progress

| Layer | Status | Last phase |
|---|---|---|
| Schema (typed Relation / Claim / per-category schemas) | ✅ complete | Phase 1+3+4 |
| relatedIds → typed Relation | ✅ 497 migrated, 12 legacy-only | Phase 2 |
| specs → sourcedSpecs Claim | 🟡 418 migrated, 197 legacy-only | Phase 3 |
| People as first-class entities | ✅ 20 seeded | Phase 5 |
| Public API layer (/api/*.json,.csv,.md) | ✅ 11 endpoints live | Phase 6 |

## Image coverage by category

| Category | Real | Synthetic (canonical) | Missing | Total | % covered |
|---|---:|---:|---:|---:|---:|
| 整机平台 | 121 | 0 | 3 | 124 | 97% |
| 资本 | 55 | 0 | 66 | 121 | 45% |
| 灵巧手 & 夹爪 | 52 | 0 | 2 | 54 | 96% |
| 产业 | 32 | 0 | 16 | 48 | 66% |
| 基础模型 † | 2 | 33 | 0 | 35 | 100% |
| 传感器 | 0 | 0 | 32 | 32 | 0% |
| 机械臂 | 3 | 0 | 28 | 31 | 9% |
| 实验室 | 17 | 0 | 12 | 29 | 58% |
| 关节模组 | 1 | 0 | 20 | 21 | 4% |
| 人物 † | 0 | 20 | 0 | 20 | 100% |
| 开发生态 † | 2 | 17 | 0 | 19 | 100% |
| 数采 & 遥操 | 1 | 0 | 16 | 17 | 5% |
| 核心零部件 | 0 | 0 | 16 | 16 | 0% |
| 评测基准 † | 0 | 16 | 0 | 16 | 100% |
| 应用场景 | 2 | 0 | 14 | 16 | 12% |
| 数据集 † | 1 | 14 | 0 | 15 | 100% |
| 计算平台 | 0 | 0 | 14 | 14 | 0% |
| 算法框架 † | 2 | 10 | 0 | 12 | 100% |
| 仿真平台 † | 2 | 10 | 0 | 12 | 100% |
| 控制算法 † | 0 | 11 | 0 | 11 | 100% |
| 能源动力 | 0 | 0 | 4 | 4 | 0% |

_† synthetic title card is the canonical visual per IMAGE_SPEC.md_

## Region distribution (where entities have a stated location)

| Country | Count | Share |
|---|---:|---:|
| China | 97 | 42% |
| USA | 89 | 39% |
| Canada | 10 | 4% |
| UK | 6 | 2% |
| Switzerland | 4 | 1% |
| Norway | 4 | 1% |
| Japan | 3 | 1% |
| Taiwan | 2 | 0% |
| Germany | 2 | 0% |
| Spain | 1 | 0% |
| USA / Singapore | 1 | 0% |
| South Korea | 1 | 0% |
| Italy | 1 | 0% |
| Hong Kong | 1 | 0% |
| Australia | 1 | 0% |
| *(and 3 more)* | 3 | |

_441 entities have no parseable location._

## Era distribution (founding / release year)

| Bucket | Count |
|---|---:|
| <2000 | 47 |
| 2000-2009 | 56 |
| 2010-2014 | 44 |
| 2015-2019 | 123 |
| 2020-2023 | 133 |
| ≥2024 | 261 |

## Relation roles in the graph

| Role | Edges |
|---|---:|
| `series-member` | 272 |
| `manufacturer` | 263 |
| `invested-in` | 255 |
| `deployed-at` | 237 |
| `competitor` | 121 |
| `related` | 120 |
| `affiliated-with` | 119 |
| `tech-base` | 73 |
| `employed-at` | 21 |
| `founder-of` | 17 |
| `trained-on` | 12 |
| `alumni-of` | 4 |

## Top 10 most-connected entities

| Rank | Entity | Category | Degree |
|:---:|---|---|---:|
| 1 | Stanford SAIL | 实验室 | 40 |
| 2 | UC Berkeley AUTOLab (BAIR) | 实验室 | 37 |
| 3 | Galbot (银河通用) | 产业 | 35 |
| 4 | NVIDIA Robotics | 产业 | 34 |
| 5 | Physical Intelligence (Pi) | 产业 | 34 |
| 6 | Google DeepMind Robotics | 产业 | 34 |
| 7 | Unitree Robotics (宇树科技) | 产业 | 31 |
| 8 | 1X Technologies | 产业 | 30 |
| 9 | AgiBot (智元机器人) | 产业 | 30 |
| 10 | Hospitality / Food Service | 应用场景 | 29 |

## Dead source URLs (71 found, sample of 10)

| URL | HTTP |
|---|---:|
| `https://www.crunchbase.com/organization/houxue-capital` | 403 |
| `https://hexagon.com/company/newsroom/press-releases/2025/hexagon-launches-aeo...` | 403 |
| `https://nai500.com/blog/2017/10/china-artificial-intelligence-firm-iflytek-pl...` | 403 |
| `https://x.com/QimingVC/status/1877183260318425443` | 403 |
| `https://www.serverobotics.com/uber-eats-partnership` | 404 |
| `https://www.robotshop.com/products/realman-robotic-arm-rm65-b-6-dof-5kg-paylo...` | 403 |
| `https://www.tesla.com/AI` | 403 |
| `https://www.kollmorgen.com/en-us/products/motors/direct-drive/kbm-series-fram...` | 403 |
| `https://www.ia.omron.com/products/family/3739/specification.html` | 403 |
| `https://muksrobotics.com/spaceo-pro-01/` | 404 |

_Run `check_url_liveness.py --markdown` for the full list + entity references._

## Known gaps / next-up targets

- **Image coverage long tail**: ~243 entities still need real product images
  (mostly per-SKU hardware: sensor / arm / joint / compute variants).
  Run `audit_images.py` to refresh the priority queue.
- **sourcedSpecs gaps**: only ~62% of entities have any sourced claim.
  Many 整机平台 entries have placeholder specs (status='In Production')
  with no real numbers — these don't migrate, won't migrate until
  the underlying data is improved.
- **Region skew**: China + USA dominate. Japanese (Toyota, Honda, Sony)
  and Korean (Samsung, LG, KAIST) ecosystems are under-represented
  relative to their actual robotics weight.
- **Era skew toward 2024–2025**: the recent humanoid wave is heavily
  represented; foundational work pre-2015 (PR2, Asimo, early Atlas)
  is thin.
- **People graph just seeded** (20 persons). Founder/CTO/PI coverage
  is sparse — most companies + labs don't yet have a person node.
- **Source URL liveness**: needs periodic re-check via
  `check_url_liveness.py`. Last check: 2026-05-21.

---
_Run `python3 research/_tools/health_report.py` to regenerate._
