#!/usr/bin/env python3
"""Phase 5 — Seed the initial set of person entities.

Adds 20 high-signal people to public/data/players.json:
- Humanoid company founders/CEOs (10)
- Major embodied-AI researchers / lab PIs (10)

Each person gets:
- A 'people' partition entry with category='人物'
- founder-of / employed-at relations to existing company/lab entities
- A sources list (Wikipedia + official bio where available)

Idempotent: skips entries whose id already exists in players.json.

Usage:
  python3 research/_tools/seed_persons.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLAYERS = ROOT / "public/data/players.json"

# Helpers
def src(title: str, url: str, type_: str = "wiki") -> dict:
    return {"title": title, "url": url, "type": type_}


def person(
    pid: str,
    name: str,
    company: str,
    year: str,
    role: str,
    expertise: str,
    description: str,
    location: str,
    sources: list[dict],
    relations: list[dict],
    birth_year: int | None = None,
    highest_degree: str | None = None,
    nationality: str | None = None,
) -> dict:
    specs: dict = {"role": role, "expertise": expertise}
    sourced: dict = {
        "role": {"value": role, "source": sources[0] if sources else None, "confidence": "reported"},
        "expertise": {"value": expertise, "source": sources[0] if sources else None, "confidence": "reported"},
    }
    if birth_year:
        sourced["birth_year"] = {"value": birth_year, "source": sources[0] if sources else None}
    if highest_degree:
        specs["highest_degree"] = highest_degree
        sourced["highest_degree"] = {"value": highest_degree, "source": sources[0] if sources else None}
    if nationality:
        sourced["nationality"] = {"value": nationality, "source": sources[0] if sources else None}
    return {
        "id": pid,
        "name": name,
        "company": company,
        "category": "人物",
        "imageUrl": "",
        "year": year,
        "isNew": False,
        "specs": specs,
        "orgInfo": {"description": description, "location": location},
        "tags": ["人物"],
        "sources": sources,
        "relations": relations,
        "sourcedSpecs": sourced,
    }


# === 20 person seed entries ===
PERSONS = [
    # ----- Humanoid company founders / CEOs -----
    person(
        pid="person-brett-adcock",
        name="Brett Adcock",
        company="Figure AI",
        year="2022",
        role="Founder & CEO",
        expertise="Humanoid robotics, serial entrepreneur",
        description="Founder and CEO of Figure AI (humanoid robotics, 2022). Previously co-founded Archer Aviation (eVTOL, NYSE:ACHR) and Vettery (enterprise hiring, acquired by Adecco).",
        location="Sunnyvale, CA, USA",
        sources=[
            src("Brett Adcock - Wikipedia", "https://en.wikipedia.org/wiki/Brett_Adcock", "wiki"),
            src("Figure AI - About", "https://www.figure.ai/about", "official"),
        ],
        relations=[
            {"targetId": "ind-figure", "role": "founder-of"},
            {"targetId": "ind-figure", "role": "employed-at"},
        ],
        nationality="USA",
    ),
    person(
        pid="person-bernt-bornich",
        name="Bernt Børnich",
        company="1X Technologies",
        year="2014",
        role="Founder & CEO",
        expertise="Humanoid robotics, soft-bodied actuation",
        description="Norwegian engineer who co-founded 1X Technologies (formerly Halodi Robotics) in 2014. Led the development of NEO and EVE humanoid platforms.",
        location="Moss, Norway",
        sources=[
            src("1X Technologies - Wikipedia", "https://en.wikipedia.org/wiki/1X_Technologies", "wiki"),
            src("1X - Team", "https://www.1x.tech/", "official"),
        ],
        relations=[
            {"targetId": "ind-1x", "role": "founder-of"},
            {"targetId": "ind-1x", "role": "employed-at"},
        ],
        nationality="Norway",
    ),
    person(
        pid="person-geordie-rose",
        name="Geordie Rose",
        company="Sanctuary AI",
        year="2018",
        role="Co-founder & CTO",
        expertise="Quantum computing, general-purpose AI, humanoid robotics",
        description="Co-founded Sanctuary AI (humanoid robotics, 2018) and previously D-Wave Systems (quantum computing, 1999) and Kindred AI (acquired by Ocado).",
        location="Vancouver, BC, Canada",
        sources=[
            src("Geordie Rose - Wikipedia", "https://en.wikipedia.org/wiki/Geordie_Rose", "wiki"),
        ],
        relations=[
            {"targetId": "ind-sanctuary", "role": "founder-of"},
            {"targetId": "ind-sanctuary", "role": "employed-at"},
        ],
        highest_degree="PhD (Physics, UBC)",
        nationality="Canada",
    ),
    person(
        pid="person-jonathan-hurst",
        name="Jonathan Hurst",
        company="Agility Robotics",
        year="2015",
        role="Co-founder & CTO",
        expertise="Bipedal locomotion, dynamic walking",
        description="Co-founder and CTO of Agility Robotics (2015). Professor at Oregon State University. Created Cassie and Digit bipedal robots.",
        location="Tangent, OR, USA",
        sources=[
            src("Jonathan Hurst - OSU", "https://research.engr.oregonstate.edu/dynamic/people/jonathan-hurst", "official"),
            src("Agility Robotics - Wikipedia", "https://en.wikipedia.org/wiki/Agility_Robotics", "wiki"),
        ],
        relations=[
            {"targetId": "ind-agility", "role": "founder-of"},
            {"targetId": "ind-agility", "role": "employed-at"},
        ],
        highest_degree="PhD (Robotics, CMU)",
        nationality="USA",
    ),
    person(
        pid="person-jeff-cardenas",
        name="Jeff Cardenas",
        company="Apptronik",
        year="2016",
        role="Co-founder & CEO",
        expertise="Humanoid robotics, exoskeletons, commercial robotics",
        description="Co-founder and CEO of Apptronik (2016), a humanoid robotics company based in Austin. Apollo humanoid is deployed at Mercedes-Benz and GXO.",
        location="Austin, TX, USA",
        sources=[
            src("Apptronik - Wikipedia", "https://en.wikipedia.org/wiki/Apptronik", "wiki"),
            src("Apptronik - Team", "https://apptronik.com/about", "official"),
        ],
        relations=[
            {"targetId": "ind-apptronik", "role": "founder-of"},
            {"targetId": "ind-apptronik", "role": "employed-at"},
        ],
        nationality="USA",
    ),
    person(
        pid="person-marc-raibert",
        name="Marc Raibert",
        company="Boston Dynamics",
        year="1992",
        role="Founder; Executive Director, Boston Dynamics AI Institute",
        expertise="Legged robotics, dynamic balance, hopping & running machines",
        description="Founded Boston Dynamics in 1992 (spun out of MIT Leg Lab). Stepped back from BD CEO role in 2019. In 2022 launched the Boston Dynamics AI Institute (now The AI Institute).",
        location="Cambridge, MA, USA",
        sources=[
            src("Marc Raibert - Wikipedia", "https://en.wikipedia.org/wiki/Marc_Raibert", "wiki"),
        ],
        relations=[
            {"targetId": "ind4", "role": "founder-of"},
            {"targetId": "ind4", "role": "employed-at"},
        ],
        birth_year=1949,
        highest_degree="PhD (MIT)",
        nationality="USA",
    ),
    person(
        pid="person-wang-xingxing",
        name="Wang Xingxing 王兴兴",
        company="Unitree Robotics 宇树科技",
        year="2016",
        role="Founder & CEO",
        expertise="Quadruped & humanoid robotics, low-cost actuation",
        description="Founded Unitree in 2016 in Hangzhou. Designed the XDog quadruped during his MSc; Unitree has since shipped Go1/Go2 quadrupeds and H1/G1 humanoids and is one of China's largest legged-robot makers by units.",
        location="Hangzhou, China",
        sources=[
            src("Unitree - Wikipedia", "https://en.wikipedia.org/wiki/Unitree_Robotics", "wiki"),
            src("Unitree - About", "https://www.unitree.com/about", "official"),
        ],
        relations=[
            {"targetId": "ind-unitree", "role": "founder-of"},
            {"targetId": "ind-unitree", "role": "employed-at"},
        ],
        highest_degree="MSc (Robotics, Shanghai University)",
        nationality="China",
    ),
    person(
        pid="person-peng-zhihui",
        name="Peng Zhihui 彭志辉 (稚晖君)",
        company="AgiBot 智元机器人",
        year="2023",
        role="Co-founder & CTO (and prominent maker / vlogger)",
        expertise="Embedded AI, humanoid robotics, electronics",
        description="Co-founded AgiBot in 2023 with Yan Weixing. Previously a 'genius youth' hire at Huawei (2020 cohort) and a popular Chinese maker vlogger under the alias 稚晖君.",
        location="Shanghai, China",
        sources=[
            src("AgiBot - Caixin profile", "https://www.caixinglobal.com/2024-04-30/", "news"),
            src("彭志辉 - 百度百科", "https://baike.baidu.com/item/%E5%BD%AD%E5%BF%97%E8%BE%89", "wiki"),
        ],
        relations=[
            {"targetId": "ind-agibot", "role": "founder-of"},
            {"targetId": "ind-agibot", "role": "employed-at"},
        ],
        nationality="China",
    ),
    person(
        pid="person-zhou-jian",
        name="Zhou Jian 周剑",
        company="UBTech 优必选",
        year="2012",
        role="Founder & CEO",
        expertise="Humanoid robotics, consumer & education robots, IPO leadership",
        description="Founded UBTech in 2012 in Shenzhen. Took the company public on HKEX in December 2023 — first humanoid-robot listed company in China.",
        location="Shenzhen, China",
        sources=[
            src("UBTech - Wikipedia", "https://en.wikipedia.org/wiki/UBTECH_Robotics", "wiki"),
        ],
        relations=[
            {"targetId": "ind-ubtech", "role": "founder-of"},
            {"targetId": "ind-ubtech", "role": "employed-at"},
        ],
        nationality="China",
    ),
    person(
        pid="person-will-jackson",
        name="Will Jackson",
        company="Engineered Arts",
        year="2004",
        role="Founder & CEO",
        expertise="Animatronic & humanoid robotics, expressive faces",
        description="Founded Engineered Arts in 2004 in Cornwall, UK. Creator of RoboThespian, Mesmer and Ameca — expressive humanoids known for highly articulated faces.",
        location="Penryn, Cornwall, UK",
        sources=[
            src("Engineered Arts - Wikipedia", "https://en.wikipedia.org/wiki/Engineered_Arts", "wiki"),
            src("Engineered Arts - About", "https://www.engineeredarts.co.uk/about/", "official"),
        ],
        relations=[
            {"targetId": "ind-engineered-arts", "role": "founder-of"},
            {"targetId": "ind-engineered-arts", "role": "employed-at"},
        ],
        nationality="UK",
    ),

    # ----- Embodied-AI researchers / lab PIs -----
    person(
        pid="person-sergey-levine",
        name="Sergey Levine",
        company="UC Berkeley",
        year="2009",
        role="Associate Professor (UC Berkeley); Co-founder, Physical Intelligence",
        expertise="Deep reinforcement learning, robot learning, foundation models for robotics",
        description="UC Berkeley EECS professor (since 2016). Co-founded Physical Intelligence (Pi, 2024) to build foundation models for robots. Prolific author on RL, imitation learning, and VLA models.",
        location="Berkeley, CA, USA",
        sources=[
            src("Sergey Levine - UC Berkeley", "https://people.eecs.berkeley.edu/~svlevine/", "official"),
            src("Sergey Levine - Wikipedia", "https://en.wikipedia.org/wiki/Sergey_Levine", "wiki"),
        ],
        relations=[
            {"targetId": "ind-physical-intelligence", "role": "founder-of"},
            {"targetId": "lab-bair-autolab", "role": "employed-at"},
            {"targetId": "lab-sail", "role": "alumni-of"},
        ],
        highest_degree="PhD (Stanford, 2014)",
        nationality="USA",
    ),
    person(
        pid="person-chelsea-finn",
        name="Chelsea Finn",
        company="Stanford University",
        year="2018",
        role="Assistant Professor (Stanford); Co-founder, Physical Intelligence",
        expertise="Meta-learning, imitation learning, robot learning",
        description="Stanford CS faculty and co-founder of Physical Intelligence. Known for MAML (Model-Agnostic Meta-Learning), ALOHA bimanual teleoperation, and OpenVLA contributions.",
        location="Stanford, CA, USA",
        sources=[
            src("Chelsea Finn - Stanford", "https://ai.stanford.edu/~cbfinn/", "official"),
            src("Chelsea Finn - Wikipedia", "https://en.wikipedia.org/wiki/Chelsea_Finn", "wiki"),
        ],
        relations=[
            {"targetId": "ind-physical-intelligence", "role": "founder-of"},
            {"targetId": "lab-sail", "role": "employed-at"},
            {"targetId": "lab-bair-autolab", "role": "alumni-of"},
        ],
        highest_degree="PhD (UC Berkeley, 2018)",
        nationality="USA",
    ),
    person(
        pid="person-karol-hausman",
        name="Karol Hausman",
        company="Physical Intelligence",
        year="2024",
        role="Co-founder & CEO",
        expertise="Robot learning, foundation models, large-scale data",
        description="Co-founder and CEO of Physical Intelligence (Pi). Previously senior researcher at Google DeepMind / Google Brain working on RT-1, RT-2, and Open X-Embodiment.",
        location="San Francisco, CA, USA",
        sources=[
            src("Physical Intelligence - Team", "https://www.physicalintelligence.company/", "official"),
            src("Karol Hausman - Google Scholar", "https://scholar.google.com/citations?user=yy0UFOwAAAAJ", "official"),
        ],
        relations=[
            {"targetId": "ind-physical-intelligence", "role": "founder-of"},
            {"targetId": "ind-physical-intelligence", "role": "employed-at"},
        ],
        highest_degree="PhD (USC, 2018)",
    ),
    person(
        pid="person-daniela-rus",
        name="Daniela Rus",
        company="MIT CSAIL",
        year="2003",
        role="Andrew (1956) and Erna Viterbi Professor; Director, MIT CSAIL",
        expertise="Distributed robotics, soft robotics, autonomous vehicles, AI",
        description="Director of MIT CSAIL since 2012. Awarded MacArthur Fellowship (2002). Pioneer in modular self-reconfiguring robotics and soft robots.",
        location="Cambridge, MA, USA",
        sources=[
            src("Daniela Rus - MIT CSAIL", "https://danielarus.csail.mit.edu/", "official"),
            src("Daniela Rus - Wikipedia", "https://en.wikipedia.org/wiki/Daniela_Rus", "wiki"),
        ],
        relations=[
            {"targetId": "lab-mit-csail", "role": "employed-at"},
            {"targetId": "lab-cmu-ri", "role": "alumni-of"},
        ],
        highest_degree="PhD (Cornell, 1992)",
        nationality="USA / Romania",
    ),
    person(
        pid="person-ken-goldberg",
        name="Ken Goldberg",
        company="UC Berkeley",
        year="1995",
        role="William S. Floyd Jr. Distinguished Chair (UC Berkeley); Director, AUTOLab",
        expertise="Robust robot grasping, surgical robotics, manipulation",
        description="UC Berkeley IEOR / EECS professor; founder of the AUTOLab. Inventor of Dex-Net (deep grasp planning), early pioneer of cloud robotics and surgical autonomy.",
        location="Berkeley, CA, USA",
        sources=[
            src("Ken Goldberg - Wikipedia", "https://en.wikipedia.org/wiki/Ken_Goldberg", "wiki"),
            src("AUTOLab", "https://autolab.berkeley.edu/", "official"),
        ],
        relations=[
            {"targetId": "lab-bair-autolab", "role": "founder-of"},
            {"targetId": "lab-bair-autolab", "role": "employed-at"},
        ],
        highest_degree="PhD (CMU, 1990)",
        nationality="USA",
    ),
    person(
        pid="person-pieter-abbeel",
        name="Pieter Abbeel",
        company="UC Berkeley",
        year="2008",
        role="Professor (UC Berkeley); Co-founder, Covariant",
        expertise="Reinforcement learning, imitation learning, robot manipulation",
        description="UC Berkeley professor; ran Berkeley AI Research's robotics group. Co-founded Covariant (industrial AI for grasping, 2017) — Amazon hired Covariant's founders in 2024.",
        location="Berkeley, CA, USA",
        sources=[
            src("Pieter Abbeel - UC Berkeley", "https://people.eecs.berkeley.edu/~pabbeel/", "official"),
            src("Pieter Abbeel - Wikipedia", "https://en.wikipedia.org/wiki/Pieter_Abbeel", "wiki"),
        ],
        relations=[
            {"targetId": "lab-bair-autolab", "role": "employed-at"},
            {"targetId": "lab-sail", "role": "alumni-of"},
        ],
        highest_degree="PhD (Stanford, 2008)",
        nationality="Belgium / USA",
    ),
    person(
        pid="person-marco-hutter",
        name="Marco Hutter",
        company="ETH Zurich",
        year="2014",
        role="Professor (ETH); Director, Robotic Systems Lab (RSL)",
        expertise="Legged robotics, locomotion, learning-based control",
        description="ETH Zurich faculty leading the Robotic Systems Lab. Created ANYmal (quadruped, spun out as ANYbotics) and the Swiss-Mile humanoid-quadruped hybrid.",
        location="Zurich, Switzerland",
        sources=[
            src("Marco Hutter - ETH RSL", "https://rsl.ethz.ch/the-lab/people/person-detail.MTIxOTEx.TGlzdC8yNDQxLC0xNDY1OTM1NDc4.html", "official"),
            src("ANYbotics - Wikipedia", "https://en.wikipedia.org/wiki/ANYbotics", "wiki"),
        ],
        relations=[
            {"targetId": "lab-eth-rsl", "role": "founder-of"},
            {"targetId": "lab-eth-rsl", "role": "employed-at"},
            {"targetId": "ind-anybotics", "role": "founder-of"},
        ],
        highest_degree="PhD (ETH Zurich, 2013)",
        nationality="Switzerland",
    ),
    person(
        pid="person-russ-tedrake",
        name="Russ Tedrake",
        company="MIT CSAIL",
        year="2004",
        role="Toyota Professor (MIT); VP of Robotics Research, Toyota Research Institute",
        expertise="Underactuated robotics, optimization-based control, manipulation",
        description="MIT professor leading the Robot Locomotion Group; VP of Robotics Research at Toyota Research Institute. Author of Drake (open-source robotics simulator & toolbox).",
        location="Cambridge, MA, USA",
        sources=[
            src("Russ Tedrake - MIT", "https://locomotion.csail.mit.edu/russt.html", "official"),
        ],
        relations=[
            {"targetId": "lab-mit-csail", "role": "employed-at"},
            {"targetId": "ind-tri", "role": "employed-at"},
        ],
        highest_degree="PhD (MIT, 2004)",
        nationality="USA",
    ),
    person(
        pid="person-fei-fei-li",
        name="Fei-Fei Li 李飞飞",
        company="Stanford University",
        year="2009",
        role="Sequoia Professor (Stanford); Co-Director, Stanford HAI; Co-founder & CEO, World Labs",
        expertise="Computer vision, ImageNet, spatial intelligence",
        description="Stanford CS faculty; created ImageNet (2009). Co-directs the Human-Centered AI institute. In 2024 founded World Labs to build large world models for spatial intelligence.",
        location="Stanford, CA, USA",
        sources=[
            src("Fei-Fei Li - Stanford", "https://profiles.stanford.edu/fei-fei-li", "official"),
            src("Fei-Fei Li - Wikipedia", "https://en.wikipedia.org/wiki/Fei-Fei_Li", "wiki"),
        ],
        relations=[
            {"targetId": "lab-sail", "role": "employed-at"},
        ],
        highest_degree="PhD (Caltech, 2005)",
        nationality="USA / China",
    ),
    person(
        pid="person-cewu-lu",
        name="Cewu Lu 卢策吾",
        company="Shanghai Jiao Tong University & Galbot",
        year="2014",
        role="Professor (SJTU); Co-founder, Galbot",
        expertise="Robot learning, dexterous manipulation, embodied AI datasets",
        description="SJTU Qing Yuan Research Institute professor. Co-founder of Galbot (humanoid robotics, 2023). Created RH20T and RH20T-P large-scale manipulation datasets; AlphaPose human-pose estimator.",
        location="Shanghai, China",
        sources=[
            src("Cewu Lu - SJTU Qing Yuan", "http://www.qingyuan.sjtu.edu.cn/a/Cewu-Lu.html", "official"),
            src("Galbot - Team", "https://www.galbot.com/", "official"),
        ],
        relations=[
            {"targetId": "stg-lab-sjtu", "role": "employed-at"},
            {"targetId": "ind-galbot", "role": "founder-of"},
        ],
        nationality="China",
    ),
]


def main():
    arr = json.loads(PLAYERS.read_text(encoding="utf-8"))
    existing_ids = {e["id"] for e in arr}
    added = 0
    skipped = 0
    for p in PERSONS:
        if p["id"] in existing_ids:
            skipped += 1
            continue
        arr.append(p)
        added += 1
    PLAYERS.write_text(json.dumps(arr, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Added {added} person entities (skipped {skipped} already present)")
    print(f"players.json now contains {len(arr)} entities")


if __name__ == "__main__":
    main()
