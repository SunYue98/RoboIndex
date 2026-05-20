# 最终阶段状态 — 2026-05-20

## 进度总览

| 阶段 | 状态 | 结果 |
|---|---|---|
| 0 — 搭骨架 | ✅ 完成 | `research/` 五个文件就位 |
| 1 — 软件类 | ✅ 完成 | **88 条**（基础模型 23、算法框架 13、控制算法 11、仿真平台 10、数据集 15、评测基准 16） |
| 2 — 参与实体 | ✅ 完成 | **63 条**（产业 27、资本 16、实验室 20） |
| 3 — 生态与应用 | ✅ 完成 | **33 条**（开发生态 19、应用场景 14） |
| 4 — 硬件长尾 | ✅ 完成 | **129 条**（机械臂 28、关节模组 20、核心零部件 16、传感器 32、能源动力 4、数采&遥操 16、计算平台 13） |
| 5 — 硬件长头 + 占位替换 | ✅ 完成 | **17 条**（3 个占位替换 + 14 个旗舰）；`en1` 判定为伪造，建议删除 |
| 6 — 给现有 234 条补 sources | ✅ **完成** | 207 条已补来源 + 11 条标为 needs-source；4 个智能体（p6a/b/c/e）跑完 + p6d + 公司名引导脚本 |
| 7 — Schema + UI 扩展 | ✅ 完成 | `Entity.sources?` 上线，`SingleSpecsPanel` 渲染 SourcesBlock + 出处待补 fallback |
| 8 — 合并进 public/data | 🟡 **预览就绪，未应用** | `research/_preview/*.preview.json` 已生成；等你批准后用 4 个 cp 命令上线 |

## 最终数字

- **新增条目：330 条**（A 级 261，B 级 69，全部 A/B 级来源验证）
- **现有 234 条中 207 条已补 sources**（88%）
- **合并预览后的最终规模：**
  - hardware.json：218 → 350 条，**93% 有 sources**
  - software.json：9 → 97 条，**100% 有 sources**
  - ecosystem.json：4 → 37 条，**100% 有 sources**
  - players.json：3 → 66 条，**100% 有 sources**
  - **总计 234 → 550 条**
- 操作明细：替换 13 条、删除 1 条、为 194 条补 sources、新增 317 条

## Phase 6 智能体发现的现有数据问题

详见 `research/audit.md`。简要清单：

**伪造 / 幻觉条目（建议删除，共 ~22 条）：**
- 概念占位类：JIE-1、TULL GET 1、PICHI MAN 1.0、CYBEO、BIANMU、DECO、RAISE M1、GOLDEN BOY 2.0、HAVAI-T3、ROBO、ONE1、E-S10、BHI A2、TOLL ONE、MR2、MEMO（共 16 条 "未知/概念"）
- 公司错配类：`f28` RUFUS（Ascento 没这个产品）、`f102` MagicBot 2（不存在）、`f117` Raion LION（Raion 做的是四足 Raibo）、`f126` CasiVision CASIVIDOT（CasiVision 是 AOI 公司，不是机器人厂）
- 占位电池：`en1` Ampere LFP Pack
- 其他无法验证：`a3` KINO X2、`a5` PANDEL、`a7` Pudu FLASHBOT ARM

**误分类（建议改类目，2 条）：**
- `f23` AgileX LIMO —— 是带轮/履带的教育机器人，不是人形
- `f113` OWI RE/CO —— 是 $35 STEM 玩具套件，更不是人形

**公司名 / SKU 错误（建议改字段，~10 条）：**
- `h23` REVO 2 → 公司应为 **BrainCo**（不是 AUTODISCOVERY）
- `h28` ALLEX → 公司应为 **WIRobotics**（不是 NXROBOTICS）
- `h47` MAGICAND S01 → 公司应为 **MagicLab**（不是 LimX 逐际动力）
- `f19` HAWO HANXI → 海尔的产品其实叫 **HIVA Haiwa**
- `f63` Astribot STAR1 → 实际产品是 **S1**（STAR1 是 RobotEra 的）
- `f93` Elephant Robotics ROBOTART X1 → 实际是 **Mercury X1**
- `f101` Lanxin VersaBot VC-1 → 实际是 **VB-1**
- `f109` PaXini TORA_DOUBLEONE → 实际是 **TORA-ONE**
- `f142` Ecovacs OMERO H1 → 实际是 **SwitchBot/Wonderlabs Onero H1**（公司和名字都错）
- `f6/f13` Muks SPACED → 实际是 **SPACEO**
- `f106` EngineAI SEO1 → 实际是 **SE01**
- `f31` Galbot ASTROBO AD-01 → 实际是 **AstroDroid AD-01**，公司是 INFIFORCE，不是 Galbot
- `a4` JAKA Zu 5 → 应是 **JAKA K1**
- `a6` Elephant PB-340 → 应是 **ultraArm P340**

**重复条目（建议合并，2 对）：**
- `f41` 和 `f112` 都是 X-Humanoid Tian Yi 2.0
- `f97` 和 `f137` 都是 Topstar Xiao Tuo

**Inspire Robots SKU 名校对：**
- `h5` RH50G2 和 `h20` RH50 SERIES —— 当前 Inspire 官方目录里没有 RH50 系列，只有 RH56-series 和 EG2-series。可能是历史型号或内部命名。

## 现在可以做什么

### 选项 A：直接合并（推荐）
```bash
for p in hardware software ecosystem players; do
  cp research/_preview/$p.preview.json public/data/$p.json
done
npm run dev   # 本地预览
```
**效果**：上线 550 条数据，硬件 93% 带来源（约 26 条会显示"出处待补"徽章——多数是已经标记为伪造的概念条目，本来就该删）。

### 选项 B：先做一轮 audit cleanup 再合并
按 `audit.md` 把以下事项做完：
1. 删除 ~22 条伪造/幻觉条目
2. 合并 2 对重复
3. 改 ~15 处公司名 / SKU 字段错误
4. 把 f23 / f113 重新分类

做完之后再合并，hardware.json 会更干净（~325 条 vs ~350 条），覆盖率接近 100%。

### 选项 C：仅做最关键的几项 audit 再合并
如果 22 条全删太激进，可以只删 `en1`（已确认伪造）和 16 条 "未知/概念"，保留有疑问但可能是真品的（比如 `f23` 重新分类而不是删），其余字段错误后续慢慢改。

## Phase 8 合并脚本逻辑（已经实现，在 `_tools/build_merge_preview.py`）

1. **保留** 现有 234 条，给其中 207 条加 `sources` 字段
2. **替换** 13 条占位（a1/a2/c1/c2/cp1/cp2/d1/e1/e2/j2/s1/s2/f34）为对应的 Phase 4/5 条目
3. **删除** 1 条（en1，伪造）
4. **新增** 317 条（来自 staging 里所有未用作替换的条目）
5. 把每条 staging 的 `_provenance.sources`（去掉 `fetched` 字段）提升为公开的 `sources` 字段

合并脚本已经跑过预览，输出在 `research/_preview/{hardware,software,ecosystem,players}.preview.json`。

## 关键文件清单

| 文件 | 用途 |
|---|---|
| `research/staging.json` | 330 条新增条目，带完整 `_provenance` |
| `research/sources.md` | 按 id 索引的来源列表 |
| `research/backfill.json` | 207 条现有条目的来源映射 + 11 条 needs-source |
| `research/audit.md` | 所有数据质量问题清单 + 处理建议 |
| `research/_preview/*.preview.json` | Phase 8 合并预演输出 |
| `research/_tools/merge_batches.py` | 把 `_batches/*.json` 装配成 staging.json |
| `research/_tools/build_merge_preview.py` | 生成 Phase 8 预览 |
| `src/data/entities.ts` | 加了 `Source` 接口和 `Entity.sources?` |
| `src/components/EntityDetailBlocks.tsx` | 新增 `SourcesBlock` 组件 |
| `src/components/SingleSpecsPanel.tsx` | 渲染 `SourcesBlock` |
| `src/i18n.tsx` | 新增"出处 / Sources / 出处待补"等翻译 |

## 未触碰的文件

- `public/data/*.json` —— 现场数据保持原样，Phase 8 由你按需触发
