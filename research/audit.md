# Audit log — entries flagged for replacement or correction

Each row identifies an existing entry in `public/data/` that the staging pass intends to fix.
Seeded at Phase 0 from the placeholder-classification report; new rows are added as Phase 1–6 surface more issues.

The **Proposed action** column says what will replace or modify the entry. The actual replacement entries (when produced) live in `staging.json` keyed `stg-<original-id>-replacement`.

## Legend

| Issue tag | Meaning |
|---|---|
| `placeholder-image` | imageUrl is an Unsplash stock photo, not a product image |
| `placeholder-specs` | specs are templated (e.g. `status: "In Production"` with no model-specific numbers) |
| `wrong-year` | year does not match the product's actual release year |
| `broken-image-ref` | imageUrl points to a local file that doesn't exist on disk |
| `needs-investigation` | possibly hallucinated entry — verify the product exists at all |

---

## Confirmed placeholders — Phase 0 seed (14 entries)

| id | name | company | current year | actual year (est.) | issues | proposed action |
|---|---|---|---:|---:|---|---|
| `a1` | UR10e | Universal Robots | 2023 | 2018 | placeholder-image, placeholder-specs, wrong-year | replace with sourced entry `stg-a1-replacement` |
| `a2` | Panda | Franka Emika | 2024 | 2015 (FER3 refresh 2023) | placeholder-image, placeholder-specs, wrong-year | replace with sourced entry `stg-a2-replacement` (consider re-listing as "Franka Research 3" 2023) |
| `e1` | 2F-85 | Robotiq | 2023 | 2013 | placeholder-image, placeholder-specs, wrong-year | replace with sourced entry `stg-e1-replacement` |
| `e2` | Shadow Hand | Shadow Robot | 2024 | 2011 (Dexterous Hand original); current gen ~2022 | placeholder-image, placeholder-specs, wrong-year | replace with sourced entry `stg-e2-replacement` |
| `j1` | FSA Actuator | Fourier | 2024 | TBD | placeholder-image, placeholder-specs | replace with sourced entry `stg-j1-replacement` |
| `j2` | Dynamixel-P | Robotis | 2023 | TBD (Dynamixel-P series ~2018+) | placeholder-image, placeholder-specs | replace with sourced entry `stg-j2-replacement` |
| `c1` | Harmonic Drive | Harmonic Drive | 2023 | n/a (product line, not a year) | placeholder-image, placeholder-specs, wrong-year | replace with specific SKU (e.g. CSF-2UH or SHF-2SH-LW); `stg-c1-replacement` |
| `c2` | Frameless BLDC | Kollmorgen | 2022 | n/a (product family) | placeholder-image, placeholder-specs | replace with specific KBM family entry; `stg-c2-replacement` |
| `s1` | RealSense D455 | Intel | 2023 | 2020 (D455 launch) | placeholder-image, placeholder-specs, wrong-year | replace with sourced entry `stg-s1-replacement` (also note D435/D435i/L515 are separate products worth adding) |
| `s2` | Axia80 6-Axis | ATI Industrial | 2023 | TBD | placeholder-image, placeholder-specs | replace with sourced entry `stg-s2-replacement` |
| `en1` | High-Discharge LFP Pack | Ampere | 2024 | TBD | placeholder-image, placeholder-specs, needs-investigation (is "Ampere" a real battery vendor in this space?) | investigate; if not a real product line, remove and substitute a real entry |
| `d1` | HaptX Gloves | HaptX | 2024 | 2017 (HaptX Gloves DK1); G1 released 2021 | placeholder-image, placeholder-specs, wrong-year | replace with sourced entry `stg-d1-replacement` (likely HaptX Gloves G1) |
| `cp1` | Jetson AGX Orin | NVIDIA | 2024 | 2022 | placeholder-image, placeholder-specs, wrong-year | replace with sourced entry `stg-cp1-replacement` |
| `cp2` | MIC-733-AO | Advantech | 2025 | TBD | placeholder-image, placeholder-specs | verify model name; if real, replace with sourced entry |

## Broken local-image references — Phase 0 seed (3 entries)

| id | name | company | imageUrl (missing) | proposed action |
|---|---|---|---|---|
| `f34` | NEO GAMMA | 1X Technologies | `images/hardware/neo-gamma.jpg` | verify product exists (NEO Gamma was announced by 1X Feb 2025); if real, plan to source image and re-add to image-todo list |
| `f39` | KUAVO-S | Leju Robotics (乐聚机器人) | `images/hardware/kuavo-s.jpg` | verify (KUAVO is the Leju humanoid line); confirm S variant exists, then plan image |
| `f108` | HMND_01 ALPHA | Humanoid (英国) | `images/hardware/hmnd-01-alpha.jpg` | verify Humanoid Ltd. (UK) and HMND_01 Alpha announcement; if real, plan image |

## New findings (Phase 1+ additions go here)

### Phase 5 verdicts on the audit-seed entries

Phase 5 agent investigated all 4 outstanding items (en1, f34, f39, f108, cp2) plus added 15 missing flagships. Verdicts:

| Entry | Verdict | Action |
|---|---|---|
| `en1` Ampere LFP Pack | **FAKE** — No robot-battery vendor "Ampere" exists in this space. The EV brand "Ampere" by Renault makes cars, not robot batteries. The placeholder specs even mix "LFP" with "Solid State" (different chemistries). | Remove. The 4 real entries in 能源动力 (Spot, Unitree H1, Inspired Energy NL2020, BB-2590/U) already cover the category honestly. |
| `f34` 1X NEO Gamma | **REAL** — Verified via 1x.tech, TechCrunch, IEEE/Dezeen. 1.65 m, ~30 kg, 22-DoF hands, Jetson Thor compute. | Replace with `stg-flagship-neo-gamma` at merge time. Still needs image download. |
| `f39` Leju KUAVO-S | **REAL-BUT-SKU-UNCERTAIN** — Leju Robotics (乐聚机器人) is real and the KUAVO line exists. The specific "KUAVO-S" SKU does NOT appear on Leju's English site; current public SKUs are KUAVO 4Pro, KUAVO 5/5-W, KUAVO-MY. "KUAVO-S" may be Chinese-market naming for a sized variant. | Investigate Chinese-market product page; if SKU resolves, source. If not, rename to canonical SKU. |
| `f108` HMND_01 ALPHA | **REAL** — Humanoid Ltd. UK is verified; HMND 01 ALPHA Bipedal launched late 2025. 179 cm / 90 kg / 29 DoF / 15 kg dual-handed payload / NVIDIA-powered VLA. | Add sources, plan image download. Entry data is correct. |
| `cp2` Advantech MIC-733-AO | **REAL** — Verified via advantech.com + Mouser datasheet. Jetson AGX Orin 32/64 GB, up to 275 TOPS, fanless AMR/AGV IPC. | Replace with `stg-cp2-replacement` at merge time. |

### Phase 5 placeholder replacements written

| Original id | Replacement entry | Status |
|---|---|---|
| `a1` UR10e | `stg-arm-ur10e` (Phase 4) | Phase 4 covered this; reuse at merge. |
| `a2` Franka Panda | `stg-arm-franka-panda` (Phase 4) | Phase 4 covered. |
| `c1` Harmonic Drive | `stg-comp-harmonic-csf-2uh` or `stg-comp-harmonic-csf-2up` (Phase 4) | Phase 4 covered (pick by specific SKU). |
| `c2` Frameless BLDC | `stg-comp-kollmorgen-kbm` (Phase 4) | Phase 4 covered. |
| `cp1` Jetson AGX Orin | `stg-cp-jetson-agx-orin` (Phase 4) | Phase 4 covered. |
| `cp2` Advantech MIC-733-AO | `stg-cp2-replacement` (Phase 5) | Phase 5 wrote new entry. |
| `d1` HaptX Gloves | `stg-teleop-haptx-g1` (Phase 4) | Phase 4 covered. |
| `e1` Robotiq 2F-85 | `stg-e1-replacement` (Phase 5) | Phase 5 wrote new entry. |
| `e2` Shadow Hand | `stg-e2-replacement` (Phase 5) | Phase 5 wrote new entry. |
| `en1` Ampere LFP Pack | **REMOVE — fabricated** | Delete at merge. |
| `j1` Fourier FSA Actuator | (none) | Fourier's FSA actuator was not independently sourceable; skip or flag needs-source. |
| `j2` Robotis Dynamixel-P | `stg-joint-dynamixel-ph42-020` / `stg-joint-dynamixel-ph54-200` (Phase 4) | Phase 4 covered (pick by specific SKU). |
| `s1` Intel RealSense D455 | `stg-sensor-realsense-d455` (Phase 4) | Phase 4 covered. |
| `s2` ATI Axia80 | `stg-sensor-ati-axia80` (Phase 4) | Phase 4 covered. |

### Phase 5 missing-flagship additions

15 flagship platform entries added in `batch_p5_placeholders_flagships.json`:
Optimus Gen 2, Atlas (electric), Figure 03, NEO Gamma, Unitree H2, Apptronik Apollo, AgiBot A2, RobotEra L7, Walker S2, XPENG Next-Gen IRON, Galbot G1, Booster T1, LimX Oli, Sanctuary Phoenix Gen 8.

Skipped (could not verify A/B source yet): Tesla Optimus Gen 3 (Musk Q1 2026 said "to be unveiled closer to production"); Apptronik Apollo Gen 2 (rolled into unified Apollo entry); KUAVO-S (SKU disambiguation pending).

### Phase 6 needs-source finds — likely vapor/concept entries

The p6a backfill agent ran through every existing humanoid entry from top companies looking for A/B-tier sources. 16 entries were unsourceable — they don't match any product in vendor catalogues, robotics databases, or news. Most are listed in the live data under `company: "未知 / 概念"`. Recommended action: **remove** unless someone can verify them.

| Live id | Name | Recommendation |
|---|---|---|
| `f5` | JIE-1 | Remove — no match anywhere |
| `f11` | TULL GET 1 | Remove |
| `f14` | PICHI MAN 1.0 | Remove |
| `f16` | CYBEO | Remove |
| `f17` | BIANMU | Remove |
| `f18` | DECO | Remove |
| `f20` | RAISE M1 | Remove |
| `f27` | GOLDEN BOY 2.0 | Remove |
| `f57` | HAVAI-T3 | Remove |
| `f90` | ROBO | Remove (too generic) |
| `f92` | ONE1 | Remove |
| `f94` | E-S10 | Remove |
| `f95` | BHI A2 | Remove |
| `f99` | TOLL ONE | Remove |
| `f116` | MR2 | Remove |
| `f119` | MEMO | Remove (likely duplicate of f1 Agility 'Memo') |

### Phase 6 name-corrections surfaced

**From p6a (humanoid platforms):**
| Live id | Current name | Likely correct |
|---|---|---|
| `f6`/`f13` | SPACED M1 / SPACED P1 (Muks Robotics) | "SPACEO M1" / "SPACEO Pro" — typo |
| `f106` | SEO1 (EngineAI) | "SE01" — typo |
| `f31` | "ASTROBO AD-01" attributed to Galbot | Actually "AstroDroid AD-01" by INFIFORCE, not Galbot |

**From p6c (dexterous hands) — company attribution fixes:**
| Live id | Current company / name | Should be |
|---|---|---|
| `h23` | 探索科技 (AUTODISCOVERY) / REVO 2 | **BrainCo** / REVO 2 (PR Newswire confirmed) |
| `h28` | NXROBOTICS / ALLEX | **WIRobotics (Korea)** / ALLEX — founded by ex-Samsung Robotics engineers, 2021 |
| `h47` | 逐际动力 (MAGICLAB) / MAGICAND S01 | **MagicLab** / MagicHand S01 — MagicLab and 逐际动力/LimX are separate companies |
| `h7` | PL-METHAND | "PL-WitHand" — typo |
| `h21` | GM18B | "GMH18" (PaXini) — typo |

**From p6c — Inspire Robots SKU mismatches:**
| Live id | Listed as | Reality |
|---|---|---|
| `h5` | RH50G2 | Not in current Inspire catalog. Lineup: RH56E2 / RH56DFX / RH56BFX / RH56F1 + EG2 series. Likely legacy designation. |
| `h20` | RH50 SERIES | Same — RH50 family is not on current product pages. |

These are SKU/name/company errors in the live data. None require entry deletion — they need a string update at merge time. Documented here for the maintainer to apply during Phase 8 merge.

**From p6e:**
| Live id | Issue |
|---|---|
| `a3` KINO X2 | Unverifiable; not a Kinova SKU. Likely scraping artifact. Recommend remove. |
| `a5` PANDEL | Unverifiable arm. Recommend remove. |
| `a7` FLASHBOT ARM (Pudu) | Pudu has "FlashBot" delivery robot but no "FlashBot Arm". Recommend remove or rename. |
| `a4` JAKA K1 | Real but bootstrap entry pointed to wrong SKU (JAKA Zu 5); now corrected to JAKA K1 in backfill. |
| `a6` PB-340 (Elephant Robotics) | Likely name-mangling of "ultraArm P340". Recommend rename. |
| `a8` KINISI 01 | Real product (Kinisi Robotics KR1 / Kinisi 01, NYC + Bristol). |

**From p6b (humanoid long tail) — major data quality issues:**

Miscategorized (not humanoids; should NOT be in 整机平台):
| Live id | Issue |
|---|---|
| `f23` AgileX LIMO | Wheeled/tracked mobile education robot (322×220×251mm, 4.2kg). Not a humanoid. Recategorize as 数采&遥操 or remove. |
| `f113` OWI RE/CO | $35 children's STEM kit with tank tracks. Not a humanoid. Recategorize or remove. |

Hallucinated / wrong-name entries (no such product exists):
| Live id | Listed | Reality |
|---|---|---|
| `f19` HAWO HANXI (Haier) | Garbled name | Haier's actual humanoid is **HIVA Haiwa** (Jul 2025, 165cm, 44 DoF) |
| `f28` RUFUS (Ascento) | Doesn't exist | Ascento makes **Ascento Guard** — a two-wheeled jumping quadruped, not a humanoid |
| `f102` MagicBot 2 (MagicLab) | Doesn't exist | MagicLab's lineup is MagicBot Gen1 + MagicBot Z1; no "Gen 2" announced |
| `f117` LION (Raion Robotics) | Doesn't exist | Raion makes **Raibo** quadruped (KAIST spinoff); no humanoid LION |
| `f126` CASIVIDOT (CasiVision) | Wrong company entirely | CasiVision is an AOI/machine-vision company. Likely intended **CASBOT 01** by 中科慧灵 |

Name typos in p6b (sourceable but field needs update):
| Live id | Listed | Should be |
|---|---|---|
| `f63` STAR1 (Astribot) | Astribot's product is **S1**; "STAR1" belongs to RobotEra. May be conflated entries. |
| `f93` ROBOTART X1 (Elephant Robotics) | Actual product is **Mercury X1** |
| `f101` VersaBot VC-1 (Lanxin) | Actual model is **VB-1** |
| `f109` TORA_DOUBLEONE (PaXini) | Actual model is **TORA-ONE** (2nd-gen variant) |
| `f142` OMERO H1 / Ecovacs | Actual name is **Onero H1**; company is **SwitchBot/Wonderlabs**, NOT Ecovacs |

Duplicate entries (same product listed twice in hardware.json):
| Live ids | Product | Recommendation |
|---|---|---|
| `f41` + `f112` | Both Tian Yi 2.0 (X-Humanoid) | Merge — keep one |
| `f97` + `f137` | Both Xiao Tuo (Topstar) | Merge — keep one |

Total recommended deletions if user accepts all audit findings:
- 14 placeholder originals (`a1, a2, c1, c2, cp1, cp2, d1, e1, e2, en1, j1, j2, s1, s2`) — most replaced by Phase 4/5 staging entries, `en1` deleted as fabricated, `j1` Fourier FSA kept with company-level source
- ~16 hallucinated/concept entries from p6a + ~5 from p6b
- 2 miscategorizations to relocate (f23, f113)
- 2 duplicates to merge (f41/f112, f97/f137)

So after a full audit, the live hardware.json would shrink from 218 → ~190 entries (then grow back via Phase 5 flagship additions).

