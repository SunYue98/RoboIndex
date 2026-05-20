#!/usr/bin/env python3
"""Apply hand-curated evolution series (seriesId + seriesOrder + seriesLabel)
to entities in public/data/*.json.

A "series" is a product family with a meaningful chronological order. Examples:
  - Tesla Optimus Gen 1 → Gen 2 → V2.5 (chronological generations)
  - UR3e + UR5e + UR10e + UR16e + UR20 + UR30 (parallel SKUs in same e-Series)

The seriesOrder is an integer for sorting within a series. Gaps allowed (so we
can insert a new entry without renumbering). The UI renders members of a series
as a horizontal chain navigator (← prev · current · next →).

Run as: python3 apply_evolution_chains.py
"""
import json
from pathlib import Path
import collections

ROOT = Path(__file__).resolve().parents[2]
PUBLIC = ROOT / "public/data"

# === SERIES MAP ===
# Each entry: id -> (seriesId, order, label)
# seriesId is a stable slug; order is for sorting; label is for UI display.
SERIES = {}

def chain(series_id, members):
    """Helper to register a chain. members = [(id, label), ...] in order."""
    for i, (eid, label) in enumerate(members, start=1):
        SERIES[eid] = (series_id, i, label)


# === HUMANOID PLATFORM SERIES ===
chain("tesla-optimus", [
    ("f8",  "Gen 1 (2022)"),
    ("f4",  "Gen 2 (2023)"),
    ("f98", "V2.5 (2024)"),
])
chain("figure-humanoid", [
    ("f9",   "Figure 01"),
    ("f139", "Figure 02"),
    ("f104", "Figure 03"),
])
chain("ubtech-walker", [
    ("f82",  "Walker C"),
    ("f135", "Walker S1"),
    ("f69",  "Walker S2"),
])
chain("1x-humanoid", [
    ("f21",  "EVE-3"),
    ("f122", "NEO Beta"),
    ("f34",  "NEO Gamma"),
])
chain("leju-kuavo", [
    ("f56",  "Roban 2"),
    ("f39",  "KUAVO-S"),
    ("f61",  "KUAVO-MY"),
    ("f123", "XTRON KUAVO-MY"),
])
chain("agibot", [
    ("f40", "X1 (open dev)"),
    ("f49", "A2"),
    ("f70", "A2 Max"),
    ("f78", "G2 Genie"),
])
chain("limx-dynamics", [
    ("f15",  "P1S"),
    ("f25",  "TRON"),
    ("f132", "CL"),
    ("f73",  "Oli"),
])
chain("unitree-humanoid", [
    ("f84", "H1"),
    ("f24", "H2"),
])
chain("pudu-d", [
    ("f120", "D7"),
    ("f127", "D9"),
])
chain("dobot-atom", [
    ("f80",  "Atom"),
    ("f129", "Atom Max"),
])
chain("xpeng-iron", [
    ("f128", "IRON"),
    ("flagship-xpeng-iron-nextgen", "Next-Gen IRON"),
])
chain("pndbotics-adam", [
    ("f12",  "Adam G0"),
    ("f124", "Adam Lite"),
])
chain("noetix", [
    ("f32", "Dora"),
    ("f77", "Hobbs"),
])
chain("mentee-bot", [
    ("f114", "MenteeBot v1"),
    ("f59",  "MenteeBot V3"),
])
chain("kepler", [
    ("f88", "K1 (legacy)"),
    ("f72", "K2"),
    ("f54", "K2 Bumblebee"),
])
chain("xhumanoid-tian-yi", [
    ("f41",  "Tian Yi 2.0"),
    ("f112", "Tian Yi 2.0 (YI-2)"),
])
chain("phybot", [
    ("f138", "C1"),
    ("f52",  "M1"),
])
chain("agility-bipedal", [
    ("f1",   "Memo"),
    ("f130", "Digit"),
])
chain("muks-spaceo", [
    ("f6",  "SPACEO M1"),
    ("f13", "SPACEO Pro"),
])
chain("matrix-robotics", [
    ("f22", "Matrix-1"),
    ("f96", "Matrix-4"),
])
chain("humanoid-uk", [
    ("f58",  "HMND 01"),
    ("f108", "HMND_01 Alpha"),
])
chain("robotera", [
    ("f105", "RobotEra L2"),
    ("flagship-robotera-l7", "L7"),
])
chain("apptronik-apollo", [
    ("f81", "Apollo"),
])  # single member but registered so flagship dedup chain is recognized

# === SOFTWARE: BASE MODEL SERIES ===
chain("google-rt", [
    ("sw-rt1", "RT-1 (2022)"),
    ("sw-rt2", "RT-2 (2023)"),
    ("sw2",    "RT-X (2023)"),
])
chain("physical-intelligence-pi", [
    ("sw-pi0",      "π0 (2024)"),
    ("sw-pi0-fast", "π0-FAST (2025)"),
    ("sw-pi05",     "π0.5 (2025)"),
])
chain("bytedance-gr", [
    ("sw-gr1", "GR-1 (2023)"),
    ("sw-gr2", "GR-2 (2024)"),
])
chain("nvidia-groot", [
    ("sw-groot-n1",   "GR00T N1 (Mar 2025)"),
    ("sw-groot-n1-5", "GR00T N1.5 (Jun 2025)"),
])
chain("deepmind-genie", [
    ("sw-genie-2", "Genie 2 (Dec 2024)"),
    ("sw-genie-3", "Genie 3 (Aug 2025)"),
])
chain("nvidia-cosmos", [  # parallel-variant family, not strict generations
    ("sw-cosmos-predict",  "Cosmos Predict"),
    ("sw-cosmos-reason",   "Cosmos Reason"),
    ("sw-cosmos-transfer", "Cosmos Transfer"),
])
chain("aloha", [
    ("sw-act",          "ACT / ALOHA (2023)"),
    ("sw-mobile-aloha", "Mobile ALOHA (2024)"),
])
chain("dreamer", [
    ("sw-dreamerv3",  "DreamerV3 (2023)"),
    ("sw-daydreamer", "DayDreamer (2022 robot deploy)"),
])

# === BENCHMARKS / DATASETS ===
chain("maniskill", [
    ("sw-maniskill2", "ManiSkill2 (2023)"),
    ("sw-maniskill3", "ManiSkill3 (2024)"),
])

# === COMPUTE PLATFORMS ===
chain("nvidia-jetson", [
    ("cp-jetson-nano",        "Nano (2019)"),
    ("cp-jetson-agx-xavier",  "AGX Xavier (2018)"),
    ("cp1",                   "AGX Orin (2022)"),
    ("cp-jetson-orin-nx",     "Orin NX (2023)"),
    ("cp-jetson-orin-nano",   "Orin Nano (2023)"),
    ("cp-jetson-agx-thor",    "AGX Thor (2025)"),
])
chain("hailo", [
    ("cp-hailo-8",   "Hailo-8 (2021)"),
    ("cp-hailo-10h", "Hailo-10H (2024)"),
])

# === SENSORS ===
chain("intel-realsense-stereo", [
    ("sensor-realsense-d435i", "D435i (2019)"),
    ("s1",                     "D455 (2020)"),
    ("sensor-realsense-d457",  "D457 (2022)"),
])
chain("orbbec-femto", [
    ("sensor-orbbec-femto-bolt", "Femto Bolt"),
    ("sensor-orbbec-femto-mega", "Femto Mega"),
])
chain("orbbec-gemini", [
    ("sensor-orbbec-gemini-335",   "Gemini 335"),
    ("sensor-orbbec-gemini-335le", "Gemini 335Le"),
])
chain("livox", [
    ("sensor-livox-mid40",  "Mid-40 (2019)"),
    ("sensor-livox-mid360", "Mid-360 (2023)"),
    ("sensor-livox-hap",    "HAP (2022 auto)"),
])
chain("velodyne", [
    ("sensor-velodyne-vlp16",       "VLP-16 (2014)"),
    ("sensor-velodyne-alpha-prime", "Alpha Prime VLS-128 (2018)"),
])
chain("hesai-pandar", [
    ("sensor-hesai-xt16",  "PandarXT-16 (2020)"),
    ("sensor-hesai-at128", "AT128 (2021)"),
])
chain("ati-ft", [
    ("sensor-ati-mini40", "Mini40"),
    ("s2",                "Axia80"),
])

# === ROBOT ARMS ===
chain("ur-eseries", [
    ("arm-ur3e",  "UR3e (2018)"),
    ("arm-ur5e",  "UR5e (2018)"),
    ("a1",        "UR10e (2018)"),
    ("arm-ur16e", "UR16e (2019)"),
    ("arm-ur20",  "UR20 (2022)"),
    ("arm-ur30",  "UR30 (2023)"),
])
chain("franka", [
    ("a2",      "Panda (2017)"),
    ("arm-fr3", "Research 3 (2022)"),
])
chain("kinova-gen3", [
    ("arm-kinova-gen3-lite", "Gen3 lite (2020)"),
    ("arm-kinova-gen3",      "Gen3 7-DOF (2019)"),
])
chain("kuka-iiwa", [
    ("arm-kuka-iiwa-7-r800",  "iiwa 7 R800"),
    ("arm-kuka-iiwa-14-r820", "iiwa 14 R820"),
])
chain("aubo-i", [
    ("arm-aubo-i5",  "i5"),
    ("arm-aubo-i10", "i10"),
])
chain("doosan-m-h", [
    ("arm-doosan-m0609", "M0609"),
    ("arm-doosan-m1013", "M1013"),
    ("arm-doosan-h2017", "H2017"),
])
chain("jaka-cobot", [
    ("arm-jaka-zu5",      "Zu 5"),
    ("arm-jaka-minicobo", "MiniCobo"),
])
chain("techman-tm", [
    ("arm-techman-tm5-900", "TM5-900"),
    ("arm-techman-tm12",    "TM12"),
])
chain("realman-rm", [
    ("arm-realman-rm65", "RM65"),
    ("arm-realman-rm75", "RM75"),
])
chain("elite-cobot", [
    ("arm-elite-ec66", "EC66"),
    ("arm-elite-cs66", "CS66"),
])
chain("abb-cobot", [
    ("arm-abb-yumi-irb14000", "YuMi IRB 14000 (2015)"),
    ("arm-abb-gofa-5",        "GoFa CRB 15000-5 (2021)"),
])

# === JOINT MODULES ===
chain("robstride", [
    ("joint-robstride-01", "01"),
    ("joint-robstride-02", "02"),
    ("joint-robstride-03", "03"),
    ("joint-robstride-04", "04"),
    ("joint-robstride-06", "06"),
])
chain("cubemars-ak", [
    ("joint-cubemars-ak60-6", "AK60-6"),
    ("joint-cubemars-ak70-10","AK70-10"),
    ("joint-cubemars-ak80-9", "AK80-9"),
])
chain("dynamixel-x", [
    ("joint-dynamixel-xm430-w350", "XM430-W350"),
    ("joint-dynamixel-xh540-w270", "XH540-W270"),
])
chain("dynamixel-p", [
    ("joint-dynamixel-ph42-020", "PH42-020"),
    ("j2",                       "PH54-200"),
])
chain("steadywin-gim", [
    ("joint-steadywin-gim6010-8", "GIM6010-8"),
    ("joint-steadywin-gim8108-8", "GIM8108-8"),
    ("joint-steadywin-gim8115-6", "GIM8115-6"),
])
chain("hebi-x", [
    ("joint-hebi-x5-9",  "X5-9"),
    ("joint-hebi-x8-16", "X8-16"),
])
chain("unitree-motor", [
    ("joint-unitree-a1",         "A1 Motor"),
    ("joint-unitree-go-m8010-6", "GO-M8010-6"),
])

# === CORE COMPONENTS ===
chain("harmonic-csf", [
    ("c1",                    "CSF-2UH"),
    ("comp-harmonic-csf-2up", "CSF-2UP Ultra-Flat"),
])
chain("nabtesco-rv", [
    ("comp-nabtesco-rv-n", "RV-N"),
    ("comp-nabtesco-rv-c", "RV-C Hollow-Shaft"),
])

# === DEXTEROUS HANDS ===
chain("inspire-rh", [
    ("h20", "RH50 Series"),
    ("h5",  "RH50G2"),
    ("h25", "RH56E2"),
])
chain("paxini-dex", [
    ("h30", "DexH5"),
    ("h21", "GMH18"),
    ("h41", "DexH13"),
])
chain("tesollo-dg", [
    ("h3",  "DG-3F"),
    ("h39", "DG-5F"),
])
chain("agibot-omnihand", [
    ("h17", "OmniHand"),
    ("h11", "OmniHand Pro 2025"),
])
chain("shadow-dexterous", [
    ("e2",  "Dexterous Hand (E3M5R)"),
    ("h29", "Dexterous Hand (legacy)"),
    ("h24", "DEX-EE (smaller)"),
])
chain("prensilia", [
    ("h27", "IH2 Azzurra"),
    ("h42", "Mia Hand R&D"),
])

# === Apply ===
partitions = ["hardware", "software", "ecosystem", "players"]
data = {p: json.loads((PUBLIC / f"{p}.json").read_text(encoding="utf-8")) for p in partitions}
all_ids = set()
for p, lst in data.items():
    for e in lst:
        all_ids.add(e["id"])

applied = 0
missing = []
for eid, (sid, order, label) in SERIES.items():
    if eid not in all_ids:
        missing.append(eid)
        continue

for p in partitions:
    for e in data[p]:
        if e["id"] in SERIES:
            sid, order, label = SERIES[e["id"]]
            e["seriesId"] = sid
            e["seriesOrder"] = order
            e["seriesLabel"] = label
            applied += 1

# Write back
for p in partitions:
    (PUBLIC / f"{p}.json").write_text(
        json.dumps(data[p], ensure_ascii=False, indent=2), encoding="utf-8"
    )

# Report
print(f"=== apply_evolution_chains.py ===\n")
print(f"Applied series fields to {applied} entries.")
if missing:
    print(f"\n⚠️  {len(missing)} mapped ids missing from live data (typos?):")
    for mid in missing[:20]:
        print(f"    {mid}")

print("\nPer-series coverage:")
by_series = collections.defaultdict(list)
for eid, (sid, order, label) in SERIES.items():
    by_series[sid].append((order, eid, label))
for sid, members in sorted(by_series.items()):
    print(f"\n  '{sid}' ({len(members)} members):")
    for order, eid, label in sorted(members):
        present = "✓" if eid in all_ids else "✗"
        print(f"    {present} {order}. {eid:35s} {label}")
