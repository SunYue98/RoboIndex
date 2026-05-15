import React from 'react';
import { Category, CATEGORY_MAP } from '../data/entities';
import { motion } from 'motion/react';
import { Bot, Armchair, Hand, Cable, CircuitBoard, Eye, Radio, Server, Fingerprint, Activity, Box, Database, Sparkles, BatteryCharging, Wrench, Factory, Cpu, Target } from 'lucide-react';
import { useLang } from '../i18n';

interface SystemOverviewProps {
  onSelectCategory: (cat: Category) => void;
}

const iconMap: Record<Category, React.ElementType> = {
  // Hardware
  '整机平台': Bot,
  '机械臂': Armchair,
  '灵巧手 & 夹爪': Hand,
  '关节模组': Cable,
  '核心零部件': CircuitBoard,
  '传感器': Eye,
  '能源动力': BatteryCharging,
  '数采 & 遥操': Radio,
  '计算平台': Server,
  // Software
  '基础模型': BrainIcon,
  '算法框架': Activity,
  '控制算法': Cpu,
  '仿真平台': Box,
  '数据集': Database,
  '评测基准': Target,
  // Ecosystem
  '开发生态': Wrench,
  '应用场景': Factory,
};

const descMap: Record<Category, string> = {
  // Hardware
  '整机平台': '具备完整形态的基础系统',
  '机械臂': '空间移动与精细操作核心',
  '灵巧手 & 夹爪': '与物理环境交互的末端',
  '关节模组': '提供动力的核心驱动单元',
  '核心零部件': '构成电机与减速器等关键硬件',
  '传感器': '赋予机器人多模态感知能力',
  '能源动力': '为机器人提供并管理能量供给',
  '数采 & 遥操': '获取真实数据与操作意图',
  '计算平台': '承载算法运行与逻辑处理',
  // Software
  '基础模型': '提供通用认知与决策能力',
  '算法框架': '支持动作与策略生成的软件库',
  '控制算法': '实现机电协调与底层运动控制',
  '仿真平台': '用于虚拟训练与物理测试环境',
  '数据集': '推动模型训练的海量动捕与示教',
  '评测基准': '衡量机器人性能与任务成功率的标准',
  // Ecosystem
  '开发生态': '涵盖中间件与开发调试工具',
  '应用场景': '机器人落地并产生价值的实际场景',
};

function BrainIcon(props: any) {
  return <Sparkles {...props} />;
}

export function SystemOverview({ onSelectCategory }: SystemOverviewProps) {
  const { t } = useLang();
  
  const renderCard = (cat: Category, colorClass: string = "bg-zinc-50 border-zinc-200 hover:bg-zinc-100") => {
    const Icon = iconMap[cat];
    return (
      <div 
        key={cat}
        onClick={() => onSelectCategory(cat)}
        className={`group relative flex flex-col items-start justify-between p-5 rounded-[24px] border transition-all duration-300 cursor-pointer hover:shadow-sm hover:scale-[1.02] ${colorClass}`}
      >
        <div className="w-10 h-10 rounded-full bg-white/80 border border-zinc-900/5 flex items-center justify-center text-zinc-700 shadow-sm transition-transform group-hover:scale-110">
          <Icon className="w-5 h-5" />
        </div>
        <div className="mt-4">
          <h3 className="font-bold text-[15px] text-zinc-900 tracking-tight">{t(cat)}</h3>
          <p className="text-[12px] text-zinc-500 font-medium mt-1 leading-relaxed">{t(`desc.${cat}`)}</p>
        </div>
      </div>
    );
  };

  return (
    <div className="w-full h-full flex flex-col items-center overflow-y-auto pb-10">
      
      <div className="w-full max-w-[1400px] relative opacity-90 px-8 py-10">
         <div className="grid grid-cols-12 gap-8 w-full">
           
           {/* Section 1: Embodiment */}
           <div className="col-span-12 lg:col-span-4 flex flex-col gap-6">
              <div className="text-[12px] font-bold text-zinc-400 tracking-[0.1em] uppercase mb-[-12px] pl-2 border-l-2 border-zinc-200">{t('sys.sec1')}</div>
              {renderCard('整机平台', 'bg-gradient-to-br from-zinc-50 to-zinc-100 border-zinc-200 shadow-sm')}
              
              <div className="grid grid-cols-2 gap-4 mt-2">
                {renderCard('机械臂')}
                {renderCard('灵巧手 & 夹爪')}
                {renderCard('应用场景', 'bg-amber-50/50 border-amber-100/60 hover:bg-amber-50')}
              </div>
           </div>

           {/* Section 2: Under the Hood */}
           <div className="col-span-12 lg:col-span-4 flex flex-col gap-6">
              <div className="text-[12px] font-bold text-zinc-400 tracking-[0.1em] uppercase mb-[-12px] pl-2 border-l-2 border-zinc-200">{t('sys.sec2')}</div>
              <div className="grid grid-cols-2 gap-4">
                 {renderCard('关节模组')}
                 {renderCard('核心零部件')}
                 {renderCard('传感器')}
                 {renderCard('计算平台')}
                 {renderCard('数采 & 遥操')}
                 {renderCard('能源动力', 'bg-emerald-50/50 border-emerald-100/60 hover:bg-emerald-50')}
              </div>
           </div>

           {/* Section 3: The Brains and Software */}
           <div className="col-span-12 lg:col-span-4 flex flex-col gap-6">
              <div className="text-[12px] font-bold text-zinc-400 tracking-[0.1em] uppercase mb-[-12px] pl-2 border-l-2 border-blue-200">{t('sys.sec3')}</div>
              
              <div className="flex flex-col gap-4 h-full">
                {renderCard('基础模型', 'bg-blue-50/50 border-blue-100 hover:bg-blue-50 flex-1')}
                <div className="grid grid-cols-2 gap-4 flex-1 mt-2">
                  {renderCard('仿真平台')}
                  {renderCard('算法框架')}
                  {renderCard('控制算法')}
                  {renderCard('数据集')}
                  {renderCard('评测基准', 'bg-rose-50/50 border-rose-100/60 hover:bg-rose-50')}
                  {renderCard('开发生态', 'bg-indigo-50/50 border-indigo-100/60 hover:bg-indigo-50')}
                </div>
              </div>
           </div>

         </div>
      </div>
    </div>
  );
}
