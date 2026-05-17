import React from 'react';
import { Category, CATEGORY_MAP } from '../data/entities';
import { Bot, Armchair, Hand, Cable, CircuitBoard, Eye, Radio, Server, Fingerprint, Activity, Box, Database, Sparkles, BatteryCharging, Wrench, Factory, Cpu, Target, ArrowRightLeft, Link, Landmark, Building2, FlaskConical } from 'lucide-react';
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
  // Entities
  '资本': Landmark,
  '产业': Building2,
  '实验室': FlaskConical,
};

function BrainIcon(props: any) {
  return <Sparkles {...props} />;
}

export function SystemOverview({ onSelectCategory }: SystemOverviewProps) {
  const { t } = useLang();
  
  const renderCard = (cat: Category, className: string = "", layout: 'vertical' | 'horizontal' = 'vertical') => {
    const Icon = iconMap[cat];
    return (
      <div 
        key={cat}
        onClick={() => onSelectCategory(cat)}
        className={`group relative p-3 xl:p-4 rounded-[20px] border transition-all duration-300 cursor-pointer shadow-sm hover:shadow-xl hover:-translate-y-1 bg-white/70 backdrop-blur-md ${layout === 'horizontal' ? 'flex flex-row items-center gap-4' : 'flex flex-col items-start justify-between'} ${className}`}
      >
        <div className={`shrink-0 rounded-[14px] bg-white border border-zinc-100 flex items-center justify-center text-zinc-600 shadow-sm transition-all duration-300 group-hover:scale-105 group-hover:text-amber-600 group-hover:border-amber-200 group-hover:bg-amber-50 group-hover:shadow-md ${layout === 'horizontal' ? 'w-10 h-10 xl:w-12 xl:h-12' : 'w-10 h-10 mb-2'}`}>
          <Icon className="w-5 h-5 group-hover:animate-pulse" />
        </div>
        <div className={`flex flex-col ${layout === 'horizontal' ? 'flex-1' : ''}`}>
          <h3 className="font-bold text-[13px] xl:text-[14px] text-zinc-900 tracking-tight group-hover:text-amber-600 transition-colors uppercase tracking-wider">{t(cat) || cat}</h3>
          <p className="text-[10px] xl:text-[11px] text-zinc-400 font-medium mt-0.5 leading-snug opacity-80 group-hover:opacity-100 transition-opacity line-clamp-1 group-hover:text-amber-700/60">{t(`desc.${cat}`)}</p>
        </div>
      </div>
    );
  };

  return (
    <div className="w-full h-full flex flex-col items-center overflow-hidden pb-4 bg-zinc-50/30">
      
      <div className="w-full max-w-[1240px] h-full relative px-6 py-6 xl:py-10 flex flex-col justify-center">
         {/* Background decorative lines representing connections */}
         <div className="absolute inset-x-12 top-24 bottom-24 overflow-hidden pointer-events-none z-0 hidden lg:block opacity-40">
           <svg className="w-full h-full text-zinc-200" style={{ strokeDasharray: '4 4' }}>
             <path d="M 0 150 Q 200 150 400 300 T 800 150" fill="none" stroke="currentColor" strokeWidth="2" />
             <path d="M 0 450 Q 400 450 600 300 T 1200 450" fill="none" stroke="currentColor" strokeWidth="2" />
             <path d="M 400 0 V 600" fill="none" stroke="currentColor" strokeWidth="1" />
             <path d="M 800 0 V 600" fill="none" stroke="currentColor" strokeWidth="1" />
           </svg>
           <div className="absolute top-[296px] left-[396px] w-2 h-2 bg-zinc-300 rounded-full" />
           <div className="absolute top-[296px] left-[596px] w-2 h-2 bg-zinc-300 rounded-full" />
         </div>

         <div className="relative z-10 grid grid-cols-1 md:grid-cols-12 gap-4 lg:gap-6">
           
           {/* Section 1: Embodiment (Physical Structure) */}
           <div className="md:col-span-6 lg:col-span-4 relative bg-zinc-100/50 rounded-[32px] p-2 border border-zinc-200/80 flex flex-col hover:border-zinc-300 transition-colors group/sec">
              <div className="px-4 py-3 pb-2 text-[10px] font-bold text-zinc-400 tracking-[0.2em] uppercase flex items-center justify-between">
                <span>{t('sys.sec1') || 'Embodiment'}</span>
                <Link className="w-3 h-3 opacity-0 group-hover/sec:opacity-100 transition-opacity" />
              </div>
              <div className="flex flex-col gap-2 xl:gap-3 pb-2 px-2 flex-1">
                {renderCard('整机平台', 'bg-gradient-to-br from-white to-zinc-50 border-zinc-200 shadow-sm', 'horizontal')}
                <div className="grid grid-cols-2 gap-2 xl:gap-3 flex-1">
                  {renderCard('机械臂', 'border-zinc-200/60', 'vertical')}
                  {renderCard('灵巧手 & 夹爪', 'border-zinc-200/60', 'vertical')}
                </div>
              </div>
           </div>

           {/* Section 2: Hardware Architecture (Under the hood) */}
           <div className="md:col-span-6 lg:col-span-4 relative bg-zinc-100/50 rounded-[32px] p-2 border border-zinc-200/80 flex flex-col hover:border-zinc-300 transition-colors group/sec">
              <div className="px-4 py-3 pb-2 text-[10px] font-bold text-zinc-400 tracking-[0.2em] uppercase flex items-center justify-between">
                <span>{t('sys.sec2') || 'Hardware Architecture'}</span>
                <Link className="w-3 h-3 opacity-0 group-hover/sec:opacity-100 transition-opacity" />
              </div>
              <div className="flex flex-col gap-2 xl:gap-3 pb-2 px-2 flex-1">
                 {renderCard('计算平台', 'border-zinc-200/60', 'horizontal')}
                 <div className="grid grid-cols-2 gap-2 xl:gap-3 flex-1">
                   {renderCard('关节模组', 'border-zinc-200/60', 'vertical')}
                   {renderCard('核心零部件', 'border-zinc-200/60', 'vertical')}
                 </div>
              </div>
           </div>

           {/* Section 3: Cognitive Engine (Brain) */}
           <div className="md:col-span-6 lg:col-span-4 relative bg-blue-50/40 rounded-[32px] p-2 border border-blue-100/60 flex flex-col hover:border-blue-200/80 transition-colors group/sec">
              <div className="px-4 py-3 pb-2 text-[10px] font-bold text-blue-400/80 tracking-[0.2em] uppercase flex items-center justify-between">
                <span>{t('sys.sec3') || 'Cognitive Engine'}</span>
                <Link className="w-3 h-3 opacity-0 group-hover/sec:opacity-100 transition-opacity text-blue-400" />
              </div>
              <div className="flex flex-col gap-2 xl:gap-3 pb-2 px-2 flex-1">
                {renderCard('基础模型', 'bg-gradient-to-br from-blue-50 to-white border-blue-200/60 shadow-sm ring-1 ring-blue-50', 'horizontal')}
                <div className="grid grid-cols-2 gap-2 xl:gap-3 flex-1">
                  {renderCard('算法框架', 'border-blue-100/50', 'vertical')}
                  {renderCard('控制算法', 'border-blue-100/50', 'vertical')}
                </div>
              </div>
           </div>

           {/* Section 4: Middle Row Components */}
           <div className="md:col-span-6 lg:col-span-4 flex flex-col gap-4">
             {renderCard('传感器', 'border-zinc-200/80 flex-1', 'horizontal')}
             {renderCard('能源动力', 'bg-emerald-50/40 border-emerald-100/60 hover:bg-emerald-50 flex-1', 'horizontal')}
           </div>

           {/* Section 5: Ecosystem */}
           <div className="md:col-span-6 lg:col-span-4 relative bg-indigo-50/30 rounded-[32px] p-2 border border-indigo-100/50 flex flex-col hover:border-indigo-200 transition-colors group/sec">
              <div className="px-4 py-3 pb-2 text-[10px] font-bold text-indigo-400/80 tracking-[0.2em] uppercase flex items-center justify-between">
                <span>Ecosystem & Applications</span>
                <Link className="w-3 h-3 opacity-0 group-hover/sec:opacity-100 transition-opacity text-indigo-400" />
              </div>
              <div className="flex flex-col gap-2 xl:gap-3 pb-2 px-2 flex-1">
                 <div className="grid grid-cols-2 gap-2 xl:gap-3 flex-1">
                   {renderCard('仿真平台', 'border-indigo-100/60', 'vertical')}
                   {renderCard('数据集', 'border-indigo-100/60', 'vertical')}
                 </div>
                 {renderCard('开发生态', 'border-indigo-100/60', 'horizontal')}
              </div>
           </div>

           {/* Section 6: Bottom Row Extensions */}
           <div className="md:col-span-6 lg:col-span-4 flex flex-col gap-4">
             {renderCard('数采 & 遥操', 'border-zinc-200/80 flex-1', 'horizontal')}
             <div className="grid grid-cols-2 gap-4 flex-1">
               {renderCard('评测基准', 'bg-rose-50/30 border-rose-100/60 hover:bg-rose-50/80', 'vertical')}
               {renderCard('应用场景', 'bg-amber-50/30 border-amber-100/60 hover:bg-amber-50/80', 'vertical')}
             </div>
           </div>

           {/* Section 7: Participants (Entities) */}
           <div className="md:col-span-12 lg:col-span-12 relative bg-purple-50/30 rounded-[32px] p-2 border border-purple-100/50 flex flex-col hover:border-purple-200 transition-colors group/sec">
              <div className="px-4 py-3 pb-2 text-[10px] font-bold text-purple-400/80 tracking-[0.2em] uppercase flex items-center justify-between">
                <span>{t('sys.sec_entities') || 'Participants'}</span>
                <Link className="w-3 h-3 opacity-0 group-hover/sec:opacity-100 transition-opacity text-purple-400" />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pb-2 px-2 flex-1">
                 {renderCard('资本', 'bg-gradient-to-br from-white to-purple-50/50 border-purple-100/60 shadow-sm', 'horizontal')}
                 {renderCard('产业', 'bg-gradient-to-br from-white to-purple-50/50 border-purple-100/60 shadow-sm', 'horizontal')}
                 {renderCard('实验室', 'bg-gradient-to-br from-white to-purple-50/50 border-purple-100/60 shadow-sm', 'horizontal')}
              </div>
           </div>

         </div>
      </div>
    </div>
  );
}

