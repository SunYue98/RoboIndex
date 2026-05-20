# 图片收集优先级队列

自动生成 by `research/_tools/audit_images.py`。共 647 条 entity，455 条缺真图（70%）。

评分逻辑：`relatedIds 数 + 类别权重 + isNew + 系列首/尾 boost`。每完成一批后重跑本脚本会刷新清单。

## 待办（按优先级排序）

| ✓ | 优先级 | ID | 名称 | 公司 | 类别 | 关联数 | 收集来源建议 |
|---|---:|---|---|---|---|---:|---|
| ☐ | 36 | `sw-genie-2` | Genie 2 | Google DeepMind | 基础模型 | 5 | 论文 figure / GitHub README hero |
| ☐ | 36 | `sw-genie-3` | Genie 3 | Google DeepMind | 基础模型 | 5 | 论文 figure / GitHub README hero |
| ☐ | 36 | `sw-groot-n1` | GR00T N1 | NVIDIA | 基础模型 | 5 | 论文 figure / GitHub README hero |
| ☐ | 36 | `sw-groot-n1-5` | GR00T N1.5 | NVIDIA | 基础模型 | 5 | 论文 figure / GitHub README hero |
| ☐ | 36 | `sw-pi0` | π0 (Pi-Zero) | Physical Intelligence | 基础模型 | 5 | 论文 figure / GitHub README hero |
| ☐ | 35 | `flagship-robotera-l7` | L7 | Robot Era (星动纪元) | 整机平台 | 2 | 厂商 press kit / 官网产品页 / IEEE Spectrum / Robot Report |
| ☐ | 35 | `flagship-xpeng-iron-nextgen` | Next-Gen IRON | XPENG Robotics (小鹏机器人) | 整机平台 | 2 | 厂商 press kit / 官网产品页 / IEEE Spectrum / Robot Report |
| ☐ | 35 | `ind-booster` | Booster Robotics | Booster Robotics | 产业 | 15 | 公司官网 press / Wikipedia infobox |
| ☐ | 35 | `ind-galbot` | Galbot (银河通用) | Galbot (银河通用) | 产业 | 15 | 公司官网 press / Wikipedia infobox |
| ☐ | 35 | `ind-limx` | LimX Dynamics | LimX Dynamics | 产业 | 15 | 公司官网 press / Wikipedia infobox |
| ☐ | 35 | `ind-physical-intelligence` | Physical Intelligence (Pi) | Physical Intelligence (Pi | 产业 | 15 | 公司官网 press / Wikipedia infobox |
| ☐ | 35 | `sw-cosmos-predict` | Cosmos Predict (World Foundati | NVIDIA | 基础模型 | 4 | 论文 figure / GitHub README hero |
| ☐ | 34 | `ind-agibot` | AgiBot (智元机器人) | AgiBot (智元机器人) | 产业 | 14 | 公司官网 press / Wikipedia infobox |
| ☐ | 34 | `ind-skild` | Skild AI | Skild AI | 产业 | 14 | 公司官网 press / Wikipedia infobox |
| ☐ | 34 | `sw-pi05` | π0.5 | Physical Intelligence | 基础模型 | 3 | 论文 figure / GitHub README hero |
| ☐ | 33 | `ind-deepmind-robotics` | Google DeepMind Robotics | Google DeepMind Robotics | 产业 | 13 | 公司官网 press / Wikipedia infobox |
| ☐ | 32 | `cp-jetson-agx-thor` | Jetson AGX Thor (T5000) | NVIDIA | 计算平台 | 9 | datasheet / 厂商产品页 |
| ☐ | 32 | `sw-gr2` | GR-2 | ByteDance Research | 基础模型 | 1 | 论文 figure / GitHub README hero |
| ☐ | 31 | `app-cleaning` | Commercial Cleaning | Various | 应用场景 | 11 | 厂商客户案例页 / 媒体报道 |
| ☐ | 30 | `ind-1x` | 1X Technologies | 1X Technologies | 产业 | 15 | 公司官网 press / Wikipedia infobox |
| ☐ | 30 | `ind-xpeng-robotics` | XPENG Robotics (Iron) | XPENG Robotics (Iron) | 产业 | 10 | 公司官网 press / Wikipedia infobox |
| ☐ | 29 | `app-hospitality` | Hospitality / Food Service | Various | 应用场景 | 9 | 厂商客户案例页 / 媒体报道 |
| ☐ | 29 | `ind-unitree` | Unitree Robotics (宇树科技) | Unitree Robotics (宇树科技) | 产业 | 14 | 公司官网 press / Wikipedia infobox |
| ☐ | 29 | `stg-ind-lumos` | Lumos Robotics (光魔机器人) | Lumos Robotics (光魔机器人) | 产业 | 9 | 公司官网 press / Wikipedia infobox |
| ☐ | 29 | `stg-ind-matrix` | Matrix Robotics (矩阵超智) | Matrix Robotics (矩阵超智) | 产业 | 9 | 公司官网 press / Wikipedia infobox |
| ☐ | 29 | `stg-ind-noetix` | Noetix Robotics (松延动力) | Noetix Robotics (松延动力) | 产业 | 9 | 公司官网 press / Wikipedia infobox |
| ☐ | 28 | `e2` | Shadow Dexterous Hand (E3M5R) | Shadow Robot Company | 灵巧手 & 夹爪 | 3 | datasheet / 厂商产品页 |
| ☐ | 28 | `flagship-galbot-g1` | Galbot G1 | Galbot (银河通用) | 整机平台 | 3 | 厂商 press kit / 官网产品页 / IEEE Spectrum / Robot Report |
| ☐ | 28 | `ind-robot-era` | Robot Era (星动纪元) | Robot Era (星动纪元) | 产业 | 8 | 公司官网 press / Wikipedia infobox |
| ☐ | 28 | `sw-dreamerv3` | DreamerV3 | Google DeepMind / Univers | 基础模型 | 2 | 论文 figure / GitHub README hero |

## 处理工作流提醒

1. 收原图到 `raw_images/<id>.{jpg|png}`（这个目录已 gitignore）
2. 跑 `python3 research/_tools/process_image.py raw_images/<id>.jpg --entity <id> [--remove-bg] [--format png]`
3. 把生成的相对路径写进 `public/data/<partition>.json` 的 `imageUrl` 字段
4. `npm run dev` 视觉过一遍
5. 一批 30 张后 commit 一次，然后重跑本脚本刷新优先级队列
