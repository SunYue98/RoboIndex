import React, { createContext, useContext, useState, ReactNode } from 'react';

type Lang = 'zh' | 'en';

interface LangContextProps {
  lang: Lang;
  setLang: (lang: Lang) => void;
  t: (key: string) => string;
}

const DICT: Record<Lang, Record<string, string>> = {
  zh: {
    'nav.architecture': '全景架构',
    'nav.timeline': '演进脉络',
    'nav.hardware': '硬件',
    'nav.software': '软件',
    'nav.eco': '生态与应用',
    'nav.players': '参与实体',
    'nav.language': '中',
    'nav.contact': '联系',
    'nav.submit': '提交',
    'title.main': 'Embodied AI Systems Architecture',
    'title.timeline': 'Embodied AI Timeline & Evolution',
    'contact.title': 'WeChat / 微信',
    'contact.desc': '扫描二维码或搜索ID联系我们',
    'submit.title': '提交收录 (Submit Entity)',
    'submit.desc': '提交新的机器人、组件、软件或应用。',
    'submit.success.title': '提交成功',
    'submit.success.desc': '您的提交已收到，审核后会更新在系统中。',
    'submit.form.name': '名称 (Entity Name) *',
    'submit.form.company': '所属机构 (Company/Org)',
    'submit.form.master': '领域 (Master Sector) *',
    'submit.form.category': '分类 (Category) *',
    'submit.form.link': '参考链接 (Reference Link)',
    'submit.form.specs': '简述与参数 (Description / Specs)',
    'submit.btn.submit': '提交审核 (Submit for Review)',
    'btn.compare': '同类比较',
    'empty.card': '选择一个项目进行查看',
    'empty.compare': '选择一个项目进行比较',
    'sys.sec1': '1. 理性具身 (Embodiment)',
    'sys.sec2': '2. 机电驱动 (Actuation)',
    'sys.sec3': '3. 智能核心 (Intelligence)',
    'sys.sec_entities': '4. 参与实体 (Ecosystem Players)',
    'desc.整机平台': '具备完整形态的基础系统',
    'desc.机械臂': '空间移动与精细操作核心',
    'desc.灵巧手 & 夹爪': '与物理环境交互的末端',
    'desc.关节模组': '提供动力的核心驱动单元',
    'desc.核心零部件': '构成电机与减速器等关键硬件',
    'desc.传感器': '赋予机器人多模态感知能力',
    'desc.能源动力': '为机器人提供并管理能量供给',
    'desc.数采 & 遥操': '获取真实数据与操作意图',
    'desc.计算平台': '承载算法运行与逻辑处理',
    'desc.基础模型': '提供通用认知与决策能力',
    'desc.算法框架': '支持动作与策略生成的软件库',
    'desc.控制算法': '实现机电协调与底层运动控制',
    'desc.仿真平台': '用于虚拟训练与物理测试环境',
    'desc.数据集': '推动模型训练的海量动捕与示教',
    'desc.评测基准': '衡量机器人性能与任务成功率的标准',
    'desc.开发生态': '涵盖中间件与开发调试工具',
    'desc.应用场景': '机器人落地并产生价值的实际场景',
    'desc.资本': '为产业发展提供资金与资源支持',
    'desc.产业': '推动硬件、软件及系统集成的核心企业',
    'desc.实验室': '探索前沿技术与基础研究的科研机构',
    'time.breakthroughs': '演进与突破',
    'timeline.focus': '当前聚焦范围：',
    'panel.related': '相关组件',
    'panel.evolution_timeline': '追踪演进脉络',
    'panel.system_link': '系统关联',
    'panel.visit': '访问官网',
    'panel.copy': '复制比对链接',
    'panel.sources': '出处 / Sources',
    'panel.no_sources': '出处待补 (Source needed)',
    'panel.source_type.official': '官方',
    'panel.source_type.paper': '论文',
    'panel.source_type.wiki': '百科',
    'panel.source_type.news': '新闻',
    'panel.source_type.datasheet': '资料表',
    'panel.series': '产品系列',
  },
  en: {
    'nav.architecture': 'Architecture',
    'nav.timeline': 'Timeline',
    'nav.hardware': 'Hardware',
    'nav.software': 'Software',
    'nav.eco': 'Ecosystem',
    'nav.players': 'Entities',
    'nav.language': 'EN',
    'nav.contact': 'Contact',
    'nav.submit': 'Submit',
    'title.main': 'Embodied AI Systems Architecture',
    'title.timeline': 'Embodied AI Timeline & Evolution',
    'contact.title': 'WeChat / 微信',
    'contact.desc': 'Scan the QR code or search ID to reach out',
    'submit.title': 'Submit Entity',
    'submit.desc': 'Propose a new robot, component, software, or application to be indexed.',
    'submit.success.title': 'Submitted Successfully',
    'submit.success.desc': 'Your submission has been warmly received. It will appear in the system after review.',
    'submit.form.name': 'Entity Name *',
    'submit.form.company': 'Company/Organization',
    'submit.form.master': 'Master Sector *',
    'submit.form.category': 'Category *',
    'submit.form.link': 'Reference Link',
    'submit.form.specs': 'Description / Specs',
    'submit.btn.submit': 'Submit for Review',
    'btn.compare': 'Compare in category',
    'empty.card': 'Select an item to view',
    'empty.compare': 'Select an item to compare',
    'sys.sec1': '1. Embodiment',
    'sys.sec2': '2. Actuation',
    'sys.sec3': '3. Intelligence',
    'sys.sec_entities': '4. Ecosystem Players',
    'desc.整机平台': 'Complete foundation systems with full form factor',
    'desc.机械臂': 'Core of spatial movement and fine manipulation',
    'desc.灵巧手 & 夹爪': 'End-effectors interacting with physical environments',
    'desc.关节模组': 'Core driving units providing articulation power',
    'desc.核心零部件': 'Critical hardware making up motors and reducers',
    'desc.传感器': 'Empowering robots with multi-modal perception',
    'desc.能源动力': 'Providing and managing energy supply for the robot',
    'desc.数采 & 遥操': 'Acquiring real-world data and operator intents',
    'desc.计算平台': 'Hosting algorithm execution and logic processing',
    'desc.基础模型': 'Supplying general cognitive and decision capabilities',
    'desc.算法框架': 'Software libraries supporting motion and policy generation',
    'desc.控制算法': 'Achieving electro-mechanical coordination and low-level control',
    'desc.仿真平台': 'Environments for virtual training and physics testing',
    'desc.数据集': 'Massive mocap and demonstration data for model training',
    'desc.评测基准': 'Standards to measure robot performance and task success rate',
    'desc.开发生态': 'Encompassing middlewares and development/debugging tools',
    'desc.应用场景': 'Real-world scenarios where robots deploy to create value',
    'desc.资本': 'Entities providing financial resources and backing',
    'desc.产业': 'Core companies driving hardware, software, and systems',
    'desc.实验室': 'Research institutions exploring bleeding-edge technology',
    'time.breakthroughs': 'Breakthroughs',
    'timeline.focus': 'Currently Focused On: ',
    'panel.related': 'Related Components',
    'panel.evolution_timeline': 'Trace Evolutionary Path',
    'panel.system_link': 'System Link',
    'panel.visit': 'Visit Website',
    'panel.copy': 'Copy comparison',
    'panel.sources': 'Sources',
    'panel.no_sources': 'Source needed',
    'panel.source_type.official': 'Official',
    'panel.source_type.paper': 'Paper',
    'panel.source_type.wiki': 'Wiki',
    'panel.source_type.news': 'News',
    'panel.source_type.datasheet': 'Datasheet',
    'panel.series': 'Series',
  }
};

const CATEGORY_TRANSLATIONS: Record<string, string> = {
  // Main Tabs
  '全景架构': 'Architecture',
  '演进脉络': 'Timeline',
  '硬件': 'Hardware',
  '软件': 'Software',
  '生态与应用': 'Ecosystem',
  '参与实体': 'Entities',
  // Top Level Groups
  '硬件平台': 'Hardware Platforms',
  '核心零部件': 'Core Components',
  '基础模型': 'Foundation Models',
  '中间件与操作系统': 'OS & Middleware',
  '仿真平台': 'Simulation',
  '生态应用与服务': 'Applications & Services',
  // Hardware
  '整机平台': 'Complete Robots',
  '计算单元': 'Compute Units',
  '传感器': 'Sensors',
  '执行器': 'Actuators',
  '动力与能源': 'Power & Energy',
  '机械臂': 'Robotic Arms',
  '灵巧手 & 夹爪': 'Dexterous Hands & Grippers',
  '关节模组': 'Joint Modules',
  '能源动力': 'Power & Energy',
  '数采 & 遥操': 'Data Acq & Teleoperation',
  '计算平台': 'Computing Platforms',
  // Software
  '大语言模型': 'Large Language Models (LLMs)',
  '多模态大模型': 'Multimodal Models (VLM/VLA)',
  '运动控制算法': 'Motion Control Algorithms',
  '机器人操作系统': 'Robot Operating Systems (ROS)',
  '算法框架': 'Algorithm Frameworks',
  '控制算法': 'Control Algorithms',
  '数据集': 'Datasets',
  '评测基准': 'Benchmarks',
  // Eco
  '开发生态': 'Development Ecosystem',
  '应用场景': 'Application Scenarios',
  '资本': 'Capital',
  '产业': 'Industry',
  '实验室': 'Laboratories',
  '工业制造': 'Industrial Manufacturing',
  '仓储物流': 'Warehousing & Logistics',
  '家庭服务': 'Home Services',
  '特种作业': 'Special Operations',
};

const LangContext = createContext<LangContextProps>({
  lang: 'zh',
  setLang: () => {},
  t: (key: string) => key,
});

export const LangProvider = ({ children }: { children: ReactNode }) => {
  const [lang, setLang] = useState<Lang>('zh');

  const t = (key: string) => {
    // If it's a category/group name
    if (CATEGORY_TRANSLATIONS[key]) {
      return lang === 'en' ? CATEGORY_TRANSLATIONS[key] : key;
    }
    // Fallback to dict
    return DICT[lang][key] || key;
  };

  return (
    <LangContext.Provider value={{ lang, setLang, t }}>
      {children}
    </LangContext.Provider>
  );
};

export const useLang = () => useContext(LangContext);
