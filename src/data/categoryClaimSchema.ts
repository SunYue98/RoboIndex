// Per-category "key claim" schema.
//
// For each category we define ~3-8 high-value fields that benefit from being
// stored as Claim<T> instead of free-form Specs[string]. These are the fields
// where users want apples-to-apples comparison or want to fact-check a number.
//
// Migration (research/_tools/migrate_specs_to_claims.py) walks each entity's
// legacy `specs` field, looks for keys matching the aliases below (case-
// insensitive, fuzzy on whitespace/punctuation), parses values per `type`,
// and writes the result into `entity.sourcedSpecs`.
//
// UI: SpecsList prefers sourcedSpecs over specs[key] when both exist for the
// same logical field. The free-form specs remains visible for everything
// else, so no data is hidden.

import type { Category, ClaimValue } from './entities';

export type ClaimDataType = 'number' | 'string' | 'boolean' | 'enum';

export interface ClaimKeySpec {
  /** Canonical key used in sourcedSpecs JSON. */
  key: string;
  /** Display label (Chinese; English fallback derived from key). */
  label: string;
  /** Optional unit for display (e.g. "kg", "cm", "TOPS"). */
  unit?: string;
  /** Expected value type — drives migration parsing. */
  type: ClaimDataType;
  /** Migration aliases — keys in legacy `specs` that map to this canonical key. */
  aliases: string[];
  /** Optional enum values when type === 'enum'. */
  enum?: string[];
}

/**
 * The full schema, keyed by Category.
 * Empty arrays mean we haven't picked key claims yet — UI just renders the
 * free-form specs for those categories.
 */
export const CATEGORY_CLAIM_SCHEMA: Record<Category, ClaimKeySpec[]> = {
  // === 硬件 ===
  '整机平台': [
    { key: 'height_cm',         label: '身高',     unit: 'cm',   type: 'number', aliases: ['Height', 'height', 'Height (cm)', 'Body Height', '身高'] },
    { key: 'weight_kg',         label: '体重',     unit: 'kg',   type: 'number', aliases: ['Weight', 'Mass', 'weight', 'Body Weight', '体重', '重量'] },
    { key: 'dof',               label: '自由度',   unit: 'DoF',  type: 'number', aliases: ['DoF', 'DOF', 'Degrees of Freedom', 'DoFs', 'dof', '自由度'] },
    { key: 'payload_kg',        label: '负载',     unit: 'kg',   type: 'number', aliases: ['Payload', 'Max Payload', 'Payload Capacity', 'payload', 'Load Capacity', '负载'] },
    { key: 'battery_runtime_min', label: '续航',  unit: 'min', type: 'number', aliases: ['Battery Life', 'Runtime', 'Battery Runtime', 'Battery', 'Operating Time', '续航'] },
    { key: 'top_speed_mps',     label: '最高速度', unit: 'm/s',  type: 'number', aliases: ['Top Speed', 'Max Speed', 'Walking Speed', 'Speed', 'top_speed'] },
  ],
  '机械臂': [
    { key: 'dof',          label: '自由度', unit: 'DoF',  type: 'number', aliases: ['DoF', 'DOF', 'Axes', 'Joints', 'dof', '自由度', '轴数'] },
    { key: 'payload_kg',   label: '负载',   unit: 'kg',   type: 'number', aliases: ['Payload', 'Max Payload', 'Payload Capacity', '负载'] },
    { key: 'reach_mm',     label: '臂展',   unit: 'mm',   type: 'number', aliases: ['Reach', 'Working Radius', 'Max Reach', '臂展', '工作半径'] },
    { key: 'weight_kg',    label: '重量',   unit: 'kg',   type: 'number', aliases: ['Weight', 'Mass', '重量'] },
    { key: 'repeatability_mm', label: '重复定位精度', unit: 'mm', type: 'number', aliases: ['Repeatability', 'Position Accuracy', 'Pose Repeatability', '重复定位精度'] },
  ],
  '灵巧手 & 夹爪': [
    { key: 'dof',          label: '自由度', unit: 'DoF',  type: 'number', aliases: ['DoF', 'DOF', 'Active DoF', 'dof', '自由度'] },
    { key: 'finger_count', label: '手指数', unit: '',     type: 'number', aliases: ['Fingers', 'Finger Count', 'Number of Fingers', '手指数'] },
    { key: 'payload_kg',   label: '抓取负载', unit: 'kg', type: 'number', aliases: ['Payload', 'Grasp Force', 'Max Grip', 'Gripping Force', '负载'] },
    { key: 'weight_g',     label: '重量',   unit: 'g',    type: 'number', aliases: ['Weight', 'Mass', '重量'] },
  ],
  '关节模组': [
    { key: 'torque_nm',      label: '额定扭矩', unit: 'N·m', type: 'number', aliases: ['Torque', 'Rated Torque', 'Nominal Torque', '额定扭矩'] },
    { key: 'peak_torque_nm', label: '峰值扭矩', unit: 'N·m', type: 'number', aliases: ['Peak Torque', 'Max Torque', 'Stall Torque', '峰值扭矩'] },
    { key: 'weight_g',       label: '重量',     unit: 'g',   type: 'number', aliases: ['Weight', 'Mass', '重量'] },
    { key: 'gear_ratio',     label: '减速比',   unit: ':1',  type: 'number', aliases: ['Gear Ratio', 'Reduction Ratio', '减速比'] },
  ],
  '核心零部件': [
    { key: 'torque_nm',  label: '扭矩',   unit: 'N·m', type: 'number', aliases: ['Torque', 'Rated Torque', '扭矩'] },
    { key: 'gear_ratio', label: '减速比', unit: ':1',  type: 'number', aliases: ['Gear Ratio', 'Reduction Ratio', '减速比'] },
    { key: 'type',       label: '类型',   type: 'string', aliases: ['Type', 'Mechanism', '类型'] },
  ],
  '传感器': [
    { key: 'range_m',         label: '量程',   unit: 'm',  type: 'number', aliases: ['Range', 'Max Range', 'Detection Range', '量程'] },
    { key: 'fov_deg',         label: 'FoV',    unit: '°',  type: 'number', aliases: ['FoV', 'Field of View', 'FOV', '视场角'] },
    { key: 'resolution',      label: '分辨率', type: 'string', aliases: ['Resolution', 'Image Resolution', '分辨率'] },
    { key: 'frame_rate_hz',   label: '帧率',   unit: 'Hz', type: 'number', aliases: ['Frame Rate', 'FPS', 'Refresh Rate', '帧率'] },
  ],
  '能源动力': [
    { key: 'capacity_wh',  label: '容量',     unit: 'Wh', type: 'number', aliases: ['Capacity', 'Energy', '容量'] },
    { key: 'voltage_v',    label: '电压',     unit: 'V',  type: 'number', aliases: ['Voltage', 'Nominal Voltage', '电压'] },
    { key: 'runtime_min',  label: '续航',     unit: 'min', type: 'number', aliases: ['Runtime', 'Battery Life', '续航'] },
  ],
  '数采 & 遥操': [
    { key: 'type',  label: '类型',   type: 'string', aliases: ['Type', '类型'] },
    { key: 'dof',   label: '自由度', unit: 'DoF',  type: 'number', aliases: ['DoF', 'DOF', '自由度'] },
  ],
  '计算平台': [
    { key: 'tops',       label: '算力',   unit: 'TOPS', type: 'number', aliases: ['TOPS', 'AI Performance', 'INT8 TOPS', 'Compute', '算力'] },
    { key: 'power_w',    label: '功耗',   unit: 'W',    type: 'number', aliases: ['Power', 'Power Consumption', 'TDP', '功耗'] },
    { key: 'ram_gb',     label: '内存',   unit: 'GB',   type: 'number', aliases: ['Memory', 'RAM', 'Unified Memory', '内存'] },
    { key: 'price_usd',  label: '价格',   unit: 'USD',  type: 'number', aliases: ['Price', 'MSRP', 'Cost', '价格'] },
  ],

  // === 软件 ===
  '基础模型': [
    { key: 'params_b',          label: '参数量', unit: 'B', type: 'number', aliases: ['Parameters', 'Params', 'Model Size', 'Parameter Count', '参数量'] },
    { key: 'release_date',      label: '发布',   type: 'string', aliases: ['Release Date', 'Released', 'Date', 'release', '发布日期'] },
    { key: 'training_data_size', label: '训练数据规模', type: 'string', aliases: ['Training Data', 'Training Size', 'Data Size'] },
  ],
  '算法框架': [
    { key: 'language',     label: '语言',  type: 'string', aliases: ['Language', 'Primary Language', '语言'] },
    { key: 'license',      label: '许可',  type: 'string', aliases: ['License', 'license', '许可'] },
    { key: 'github_stars', label: 'GitHub Stars', type: 'number', aliases: ['GitHub Stars', 'Stars', 'GH Stars'] },
  ],
  '控制算法': [
    { key: 'language',  label: '语言', type: 'string', aliases: ['Language'] },
    { key: 'license',   label: '许可', type: 'string', aliases: ['License'] },
  ],
  '仿真平台': [
    { key: 'engine',  label: '物理引擎', type: 'string', aliases: ['Engine', 'Physics Engine', '物理引擎'] },
    { key: 'license', label: '许可',     type: 'string', aliases: ['License', '许可'] },
  ],
  '数据集': [
    { key: 'episodes',  label: '轨迹数',   type: 'number', aliases: ['Episodes', 'Demonstrations', 'Demos', 'Trajectories', '轨迹数'] },
    { key: 'hours',     label: '时长',     unit: 'h', type: 'number', aliases: ['Hours', 'Duration', 'Total Hours'] },
    { key: 'tasks',     label: '任务数',   type: 'number', aliases: ['Tasks', 'Task Count', '任务数'] },
  ],
  '评测基准': [
    { key: 'tasks',     label: '任务数',    type: 'number', aliases: ['Tasks', 'Task Count', '任务数'] },
    { key: 'episodes',  label: '测试轨迹',  type: 'number', aliases: ['Episodes', 'Test Episodes'] },
  ],

  // === 生态 ===
  '开发生态': [
    { key: 'license',   label: '许可',  type: 'string', aliases: ['License'] },
    { key: 'language',  label: '语言',  type: 'string', aliases: ['Language'] },
  ],
  '应用场景': [],  // descriptive only; no quantitative claims

  // === 参与实体 ===
  '资本': [
    { key: 'aum_b',           label: 'AUM',   unit: 'B USD', type: 'number', aliases: ['AUM', 'Assets Under Management', '资产管理规模'] },
    { key: 'founded_year',    label: '成立',  type: 'number', aliases: ['Founded', 'Founding Year', '成立年份'] },
    { key: 'hq_country',      label: '总部',  type: 'string', aliases: ['HQ', 'Headquarters', 'Country', '总部'] },
  ],
  '产业': [
    { key: 'founded_year',     label: '成立',    type: 'number', aliases: ['Founded', 'Founding Year', '成立年份'] },
    { key: 'hq_country',       label: '总部',    type: 'string', aliases: ['HQ', 'Headquarters', 'Country', '总部'] },
    { key: 'employee_count',   label: '员工',    type: 'number', aliases: ['Employees', 'Headcount', 'Staff Count', '员工数'] },
  ],
  '实验室': [
    { key: 'founded_year',  label: '成立',  type: 'number', aliases: ['Founded', 'Founding Year', '成立年份'] },
    { key: 'university',    label: '所属',  type: 'string', aliases: ['University', 'Affiliation', 'Parent', '所属'] },
    { key: 'head',          label: '负责人', type: 'string', aliases: ['Head', 'Director', 'PI', 'Lead', '负责人'] },
  ],
};

/** Inverted alias index for fast migration lookup. Built once. */
export type AliasIndex = Map<string, Map<string, ClaimKeySpec>>; // category → (alias_lower → spec)

export function buildAliasIndex(): AliasIndex {
  const idx: AliasIndex = new Map();
  for (const [cat, specs] of Object.entries(CATEGORY_CLAIM_SCHEMA) as [Category, ClaimKeySpec[]][]) {
    const m = new Map<string, ClaimKeySpec>();
    for (const spec of specs) {
      m.set(spec.key.toLowerCase(), spec);  // canonical key is also a valid alias
      for (const a of spec.aliases) {
        m.set(a.toLowerCase(), spec);
      }
    }
    idx.set(cat, m);
  }
  return idx;
}

/** Re-export the ClaimValue type for convenience. */
export type { ClaimValue };
