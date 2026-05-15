export type TopLevelGroup = '硬件' | '软件' | '生态与应用';

export type Category = 
  | '整机平台' | '机械臂' | '灵巧手 & 夹爪'
  | '关节模组' | '核心零部件' | '传感器' | '能源动力'
  | '数采 & 遥操' | '计算平台'
  | '基础模型' | '算法框架' | '控制算法' | '仿真平台' | '数据集' | '评测基准'
  | '开发生态' | '应用场景';

export const CATEGORY_MAP: Record<TopLevelGroup, Category[]> = {
  '硬件': ['整机平台', '机械臂', '灵巧手 & 夹爪', '关节模组', '核心零部件', '传感器', '能源动力', '数采 & 遥操', '计算平台'],
  '软件': ['基础模型', '算法框架', '控制算法', '仿真平台', '数据集', '评测基准'],
  '生态与应用': ['开发生态', '应用场景']
};

export const TOP_LEVEL_GROUPS = Object.keys(CATEGORY_MAP) as TopLevelGroup[];

export interface Specs {
  [key: string]: any;
}

export interface Entity {
  id: string;
  name: string;
  company: string;
  category: Category;
  imageUrl: string;
  year: string;
  isNew: boolean;
  specs: Specs;
  relatedIds?: string[];
  tags?: string[];
}

export const mockData: Entity[] = [
  // ---------- 硬件 : 整机平台 ----------
  { id: 'f1', name: 'Memo', company: 'Agility Robotics', category: '整机平台', imageUrl: 'https://images.unsplash.com/photo-1546776310-eef45dd6d63c?auto=format&fit=crop&q=80&w=600', year: '2024', isNew: false, specs: { height: '5\'9"', weight: '160 lb', dof: 40, status: 'In Production' }, relatedIds: ['e1', 'j1', 'sw1', 'en1'], tags: ['Bipedal', 'Commercial', 'USA'] },
  { id: 'f2', name: 'Oli', company: 'LimX Dynamics', category: '整机平台', imageUrl: 'https://images.unsplash.com/photo-1485827404703-89b55fcc595e?auto=format&fit=crop&q=80&w=600', year: '2025', isNew: true, specs: { height: '5\'5"', weight: '121 lb', dof: 31, status: 'In Production' }, relatedIds: ['sw5', 'sw7', 'c1', 'ca1'], tags: ['Bipedal', 'Prototype', 'China'] },
  { id: 'f4', name: 'Optimus Gen 2', company: 'Tesla', category: '整机平台', imageUrl: 'https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&q=80&w=600', year: '2024', isNew: false, specs: { height: '5\'11"', weight: '160 lb', dof: 28, status: 'In Development' }, relatedIds: ['e2', 's1', 'cp1', 'en1'], tags: ['Electric', 'Highly Hyped', 'USA'] },

  // ---------- 硬件 : 机械臂 ----------
  { id: 'a1', name: 'UR10e', company: 'Universal Robots', category: '机械臂', imageUrl: 'https://images.unsplash.com/photo-1581092160562-40aa08e78837?auto=format&fit=crop&q=80&w=600', year: '2023', isNew: false, specs: { payload: '12.5 kg', reach: '1300 mm', weight: '73.9 lb', dof: 6, status: 'In Production' }, relatedIds: ['c1', 's2'], tags: ['Collaborative', 'Industrial', 'Denmark'] },
  { id: 'a2', name: 'Panda', company: 'Franka Emika', category: '机械臂', imageUrl: 'https://images.unsplash.com/photo-1581092335878-2d9fd86aecf3?auto=format&fit=crop&q=80&w=600', year: '2024', isNew: false, specs: { payload: '3 kg', reach: '855 mm', weight: '39.6 lb', dof: 7, status: 'In Production' }, relatedIds: ['c1'], tags: ['Collaborative', 'Research', 'Germany'] },

  // ---------- 硬件 : 灵巧手 & 夹爪 ----------
  { id: 'e1', name: '2F-85', company: 'Robotiq', category: '灵巧手 & 夹爪', imageUrl: 'https://images.unsplash.com/photo-1616423640778-28d1b53229bd?auto=format&fit=crop&q=80&w=600', year: '2023', isNew: false, specs: { payload: '5 kg', gripForce: '20-235 N', weight: '2 lb', status: 'In Production' }, relatedIds: ['f1'], tags: ['Gripper', 'Industrial'] },
  { id: 'e2', name: 'Shadow Hand', company: 'Shadow Robot', category: '灵巧手 & 夹爪', imageUrl: 'https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&q=80&w=600', year: '2024', isNew: true, specs: { sensors: '129 tactile', weight: '9.4 lb', dof: 24, status: 'In Production' }, relatedIds: ['d1', 'f4'], tags: ['Dexterous', 'Research'] },

  // ---------- 硬件 : 关节模组 ----------
  { id: 'j1', name: 'FSA Actuator', company: 'Fourier', category: '关节模组', imageUrl: 'https://images.unsplash.com/photo-1589254065878-42c9da997008?auto=format&fit=crop&q=80&w=600', year: '2024', isNew: true, specs: { torque: '100 Nm', weight: '1.2 kg', speed: '120 rpm', status: 'In Production' }, relatedIds: ['f1', 'c2'], tags: ['Integrated', 'High Torque'] },
  { id: 'j2', name: 'Dynamixel-P', company: 'Robotis', category: '关节模组', imageUrl: 'https://images.unsplash.com/photo-1535378917042-10a22c95931a?auto=format&fit=crop&q=80&w=600', year: '2023', isNew: false, specs: { torque: '44.7 Nm', weight: '0.8 kg', speed: '29 rpm', status: 'In Production' }, relatedIds: ['f2'], tags: ['Standardized', 'South Korea'] },

  // ---------- 硬件 : 核心零部件 ----------
  { id: 'c1', name: 'Harmonic Drive', company: 'Harmonic Drive', category: '核心零部件', imageUrl: 'https://images.unsplash.com/photo-1664448007559-0dbf88ee9dff?auto=format&fit=crop&q=80&w=600', year: '2023', isNew: false, specs: { ratio: '1:100', torque: 'High', type: 'Strain Wave', status: 'In Production' }, relatedIds: ['a1', 'a2', 'f2'], tags: ['Reducer', 'Zero Backlash'] },
  { id: 'c2', name: 'Frameless BLDC', company: 'Kollmorgen', category: '核心零部件', imageUrl: 'https://images.unsplash.com/photo-1546776310-eef45dd6d63c?auto=format&fit=crop&q=80&w=600', year: '2022', isNew: false, specs: { power: '500 W', type: 'TBM2G', status: 'In Production' }, relatedIds: ['j1'], tags: ['Motor', 'USA'] },

  // ---------- 硬件 : 传感器 ----------
  { id: 's1', name: 'RealSense D455', company: 'Intel', category: '传感器', imageUrl: 'https://images.unsplash.com/photo-1581092160562-40aa08e78837?auto=format&fit=crop&q=80&w=600', year: '2023', isNew: false, specs: { range: '0.6-6 m', type: 'Depth Camera', status: 'In Production' }, relatedIds: ['f4'], tags: ['Vision', 'Stereo'] },
  { id: 's2', name: 'Axia80 6-Axis', company: 'ATI Industrial', category: '传感器', imageUrl: 'https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?auto=format&fit=crop&q=80&w=600', year: '2023', isNew: false, specs: { force: '150 N', torque: '8 Nm', type: 'F/T Sensor', status: 'In Production' }, relatedIds: ['a1'], tags: ['Force/Torque', 'Industrial'] },

  // ---------- 硬件 : 能源动力 ----------
  { id: 'en1', name: 'High-Discharge LFP Pack', company: 'Ampere', category: '能源动力', imageUrl: 'https://images.unsplash.com/photo-1620021644783-6cc5ba5f0732?auto=format&fit=crop&q=80&w=600', year: '2024', isNew: true, specs: { capacity: '2.5 kWh', voltage: '48V', type: 'Solid State', status: 'In Production' }, relatedIds: ['f4'], tags: ['Battery', 'Solid State'] },

  // ---------- 硬件 : 数采 & 遥操 ----------
  { id: 'd1', name: 'HaptX Gloves', company: 'HaptX', category: '数采 & 遥操', imageUrl: 'https://images.unsplash.com/photo-1535223289827-42f1e9919769?auto=format&fit=crop&q=80&w=600', year: '2024', isNew: true, specs: { feedback: 'Force & Tactile', weight: '3 lb', dof: 130, status: 'In Production' }, relatedIds: ['e2'], tags: ['Teleoperation', 'Haptics'] },
  { id: 'd2', name: 'GELLO Arm', company: 'Open Source', category: '数采 & 遥操', imageUrl: 'https://images.unsplash.com/photo-1622979135225-d2ba269cf1ac?auto=format&fit=crop&q=80&w=600', year: '2024', isNew: true, specs: { type: 'Teleop Master', cost: '~$300 (DIY)', status: 'Open Source' }, relatedIds: ['sw4'], tags: ['Open Source', 'Low Cost'] },

  // ---------- 硬件 : 计算平台 ----------
  { id: 'cp1', name: 'Jetson AGX Orin', company: 'NVIDIA', category: '计算平台', imageUrl: 'https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&q=80&w=600', year: '2024', isNew: false, specs: { TOPS: 275, memory: '64 GB', power: '15-60W', status: 'In Production' }, relatedIds: ['f4', 'sw3'], tags: ['Edge Compute', 'GPU'] },
  { id: 'cp2', name: 'MIC-733-AO', company: 'Advantech', category: '计算平台', imageUrl: 'https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&q=80&w=600', year: '2025', isNew: true, specs: { type: 'IPC Based on Orin', memory: '32 GB', status: 'In Production' }, relatedIds: ['cp1'], tags: ['Industrial PC'] },

  // ---------- 软件 : 基础模型 ----------
  { id: 'sw1', name: 'OpenVLA', company: 'Open Source', category: '基础模型', imageUrl: 'https://images.unsplash.com/photo-1535378917042-10a22c95931a?auto=format&fit=crop&q=80&w=600', year: '2024', isNew: true, specs: { parameters: '7B', architecture: 'Transformer', paradigm: 'VLA', status: 'Available' }, relatedIds: ['sw7', 'f1'], tags: ['Vision-Language', 'Open Source'] },
  { id: 'sw2', name: 'RT-X', company: 'Google DeepMind', category: '基础模型', imageUrl: 'https://images.unsplash.com/photo-1546776310-eef45dd6d63c?auto=format&fit=crop&q=80&w=600', year: '2023', isNew: false, specs: { parameters: 'Unknown', paradigm: 'VLA', scale: 'Cross-Embodiment', status: 'Open Source' }, relatedIds: ['sw7'], tags: ['Cross-Embodiment', 'Research'] },

  // ---------- 软件 : 算法框架 ----------
  { id: 'sw3', name: 'Isaac Lab', company: 'NVIDIA', category: '算法框架', imageUrl: 'https://images.unsplash.com/photo-1616423640778-28d1b53229bd?auto=format&fit=crop&q=80&w=600', year: '2024', isNew: true, specs: { type: 'RL Environment', engine: 'Omniverse', status: 'Active' }, relatedIds: ['sw5', 'cp1'], tags: ['Simulation', 'RL'] },
  { id: 'sw4', name: 'RoboMimic', company: 'Stanford', category: '算法框架', imageUrl: 'https://images.unsplash.com/photo-1664448007559-0dbf88ee9dff?auto=format&fit=crop&q=80&w=600', year: '2022', isNew: false, specs: { type: 'Imitation Learning', language: 'Python/PyTorch', status: 'Active' }, relatedIds: ['d2'], tags: ['Imitation Learning', 'Open Source'] },

  // ---------- 软件 : 控制算法 ----------
  { id: 'ca1', name: 'MIT Cheetah WBC', company: 'MIT BIOMIMETICS', category: '控制算法', imageUrl: 'https://images.unsplash.com/photo-1664448007559-0dbf88ee9dff?auto=format&fit=crop&q=80&w=600', year: '2019', isNew: false, specs: { type: 'Whole Body Control', theory: 'Dynamical Optimization', status: 'Open Source' }, relatedIds: ['f2'], tags: ['WBC', 'Legged Locomotion'] },

  // ---------- 软件 : 仿真平台 ----------
  { id: 'sw5', name: 'Isaac Sim', company: 'NVIDIA', category: '仿真平台', imageUrl: 'https://images.unsplash.com/photo-1589254065878-42c9da997008?auto=format&fit=crop&q=80&w=600', year: '2023', isNew: false, specs: { rendering: 'RTX', physics: 'PhysX 5', status: 'Production' }, relatedIds: ['sw3', 'f2'], tags: ['PhysX', 'Raytracing'] },
  { id: 'sw6', name: 'MuJoCo', company: 'Google DeepMind', category: '仿真平台', imageUrl: 'https://images.unsplash.com/photo-1546776310-eef45dd6d63c?auto=format&fit=crop&q=80&w=600', year: '2022', isNew: false, specs: { physics: 'Fast Contacts', type: 'Open Source', status: 'Active' }, relatedIds: [], tags: ['Open Source', 'Physics Engine'] },

  // ---------- 软件 : 数据集 ----------
  { id: 'sw7', name: 'Open X-Embodiment', company: 'Google DeepMind', category: '数据集', imageUrl: 'https://images.unsplash.com/photo-1534438327276-14e5300c3a48?auto=format&fit=crop&q=80&w=600', year: '2023', isNew: false, specs: { size: '1M+ trajectories', robots: '22 embodiments', status: 'Publicly Available' }, relatedIds: ['sw1', 'sw2', 'f2'], tags: ['Dataset', 'Large-scale'] },

  // ---------- 软件 : 评测基准 ----------
  { id: 'bm1', name: 'ManiSkill', company: 'UCSD', category: '评测基准', imageUrl: 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&q=80&w=600', year: '2024', isNew: true, specs: { type: 'Manipulation Benchmark', envs: '120+ Tasks', status: 'Active' }, relatedIds: ['sw1'], tags: ['Benchmark', 'Manipulation'] },

  // ---------- 生态与应用 : 开发生态 ----------
  { id: 'eco1', name: 'ROS 2', company: 'OSRF', category: '开发生态', imageUrl: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&q=80&w=600', year: '2022', isNew: false, specs: { type: 'Middleware', language: 'C++/Python', status: 'Standard' }, relatedIds: ['f1', 'f2'], tags: ['Middleware', 'Standard'] },
  { id: 'eco2', name: 'Foxglove Studio', company: 'Foxglove', category: '开发生态', imageUrl: 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&q=80&w=600', year: '2024', isNew: false, specs: { type: 'Visualization Tool', integration: 'ROS/ROS2/WebSocket', status: 'Active' }, relatedIds: ['eco1'], tags: ['Visualization', 'Debugging'] },

  // ---------- 生态与应用 : 应用场景 ----------
  { id: 'app1', name: 'Smart Factory', company: 'Various', category: '应用场景', imageUrl: 'https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&q=80&w=600', year: '2025', isNew: true, specs: { type: 'B2B', environment: 'Structured', ROI: 'High', status: 'Deploying' }, relatedIds: ['f4', 'a1'], tags: ['B2B', 'Manufacturing'] },
  { id: 'app2', name: 'Logistics Warehouse', company: 'Various', category: '应用场景', imageUrl: 'https://images.unsplash.com/photo-1586528116311-ad8ed7c50a6f?auto=format&fit=crop&q=80&w=600', year: '2024', isNew: false, specs: { type: 'B2B', environment: 'Semi-structured', status: 'Scaling' }, relatedIds: ['f1'], tags: ['Logistics', 'Warehouse'] },
];
