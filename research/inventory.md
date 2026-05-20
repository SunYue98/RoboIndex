# RoboIndex Data Inventory — frozen 2026-05-19

Snapshot of `public/data/` taken before staging collection begins. This file is
not updated as collection progresses — it's the baseline we measure against.

## Top-level counts

| Partition | Entries | Categories represented |
|---|---:|---|
| `hardware.json` | 218 | 传感器, 关节模组, 数采 & 遥操, 整机平台, 机械臂, 核心零部件, 灵巧手 & 夹爪, 能源动力, 计算平台 |
| `software.json` | 9 | 仿真平台, 基础模型, 控制算法, 数据集, 算法框架, 评测基准 |
| `ecosystem.json` | 4 | 应用场景, 开发生态 |
| `players.json` | 3 | 产业, 实验室, 资本 |

## Per-category breakdown

| Partition | Category | Count | Has tags | Has paperInfo | Has orgInfo | Local img | Unsplash img |
|---|---|---:|---:|---:|---:|---:|---:|
| hardware | 传感器 | 2 | 2 | 0 | 0 | 0 | 2 |
| hardware | 关节模组 | 2 | 2 | 0 | 0 | 0 | 2 |
| hardware | 数采 & 遥操 | 2 | 2 | 0 | 0 | 0 | 2 |
| hardware | 整机平台 | 145 | 145 | 0 | 120 | 145 | 0 |
| hardware | 机械臂 | 8 | 8 | 0 | 4 | 6 | 2 |
| hardware | 核心零部件 | 2 | 2 | 0 | 0 | 0 | 2 |
| hardware | 灵巧手 & 夹爪 | 54 | 2 | 0 | 52 | 52 | 2 |
| hardware | 能源动力 | 1 | 1 | 0 | 0 | 0 | 1 |
| hardware | 计算平台 | 2 | 2 | 0 | 0 | 0 | 2 |
| software | 仿真平台 | 2 | 2 | 0 | 0 | 0 | 2 |
| software | 基础模型 | 2 | 2 | 2 | 0 | 0 | 2 |
| software | 控制算法 | 1 | 1 | 0 | 0 | 0 | 1 |
| software | 数据集 | 1 | 1 | 0 | 0 | 0 | 1 |
| software | 算法框架 | 2 | 2 | 0 | 0 | 0 | 2 |
| software | 评测基准 | 1 | 1 | 0 | 0 | 0 | 1 |
| ecosystem | 应用场景 | 2 | 2 | 0 | 0 | 0 | 2 |
| ecosystem | 开发生态 | 2 | 2 | 0 | 0 | 0 | 2 |
| players | 产业 | 1 | 1 | 0 | 1 | 0 | 1 |
| players | 实验室 | 1 | 1 | 0 | 1 | 0 | 1 |
| players | 资本 | 1 | 1 | 0 | 1 | 0 | 1 |

## Image-asset reality check

- `public/images/hardware/`: **198 files**
- `public/images/software/`: **does not exist** → entries in this partition have no local images
- `public/images/ecosystem/`: **does not exist** → entries in this partition have no local images
- `public/images/players/`: **does not exist** → entries in this partition have no local images

## Confirmed placeholder entries (Phase 0 audit seed)

All 14 below use Unsplash stock images, templated `status` specs, and likely-fabricated years.
Tracked individually in `audit.md`.

| id | partition | category | name | company | year (current) |
|---|---|---|---|---|---|
| `a1` | hardware | 机械臂 | UR10e | Universal Robots | 2023 |
| `a2` | hardware | 机械臂 | Panda | Franka Emika | 2024 |
| `e1` | hardware | 灵巧手 & 夹爪 | 2F-85 | Robotiq | 2023 |
| `e2` | hardware | 灵巧手 & 夹爪 | Shadow Hand | Shadow Robot | 2024 |
| `j1` | hardware | 关节模组 | FSA Actuator | Fourier | 2024 |
| `j2` | hardware | 关节模组 | Dynamixel-P | Robotis | 2023 |
| `c1` | hardware | 核心零部件 | Harmonic Drive | Harmonic Drive | 2023 |
| `c2` | hardware | 核心零部件 | Frameless BLDC | Kollmorgen | 2022 |
| `s1` | hardware | 传感器 | RealSense D455 | Intel | 2023 |
| `s2` | hardware | 传感器 | Axia80 6-Axis | ATI Industrial | 2023 |
| `en1` | hardware | 能源动力 | High-Discharge LFP Pack | Ampere | 2024 |
| `d1` | hardware | 数采 & 遥操 | HaptX Gloves | HaptX | 2024 |
| `cp1` | hardware | 计算平台 | Jetson AGX Orin | NVIDIA | 2024 |
| `cp2` | hardware | 计算平台 | MIC-733-AO | Advantech | 2025 |

## Broken local-image references (Phase 0 audit seed)

These entries reference a local `images/hardware/<slug>.jpg` that does not exist on disk.
Tracked in `audit.md`.

| id | name | company | imageUrl |
|---|---|---|---|
| `f34` | NEO GAMMA | 1X Technologies | `images/hardware/neo-gamma.jpg` |
| `f39` | KUAVO-S | Leju Robotics (乐聚机器人) | `images/hardware/kuavo-s.jpg` |
| `f108` | HMND_01 ALPHA | Humanoid (英国) | `images/hardware/hmnd-01-alpha.jpg` |

## Coverage gaps (targets in plan)

| Partition | Current | Target after Phase 1–5 | Gap |
|---|---:|---:|---:|
| hardware | 218 | ~318 | +100 |
| software | 9 | ~89 | +80 |
| ecosystem | 4 | ~34 | +30 |
| players | 3 | ~63 | +60 |

Plus: backfill `sources` field on **all** existing entries (~234) in Phase 6.
