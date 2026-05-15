import { mockData, Entity } from '../data/entities';
import { motion } from 'motion/react';
import { Calendar } from 'lucide-react';
import { useLang } from '../i18n';

interface TimelineViewProps {
  onNavigateToEntity: (id: string) => void;
}

export function TimelineView({ onNavigateToEntity }: TimelineViewProps) {
  const { t } = useLang();
  // Group by year
  const grouped = mockData.reduce((acc, entity) => {
    if (!acc[entity.year]) acc[entity.year] = [];
    acc[entity.year].push(entity);
    return acc;
  }, {} as Record<string, Entity[]>);

  // Sort years descending
  const sortedYears = Object.keys(grouped).sort((a, b) => parseInt(b) - parseInt(a));

  return (
    <div className="w-full h-full flex flex-col items-center justify-start overflow-y-auto pt-8 pb-32">
      <div className="w-full max-w-[1000px] relative mt-10">
        <div className="absolute left-[50%] top-0 bottom-0 w-[2px] bg-zinc-100 -translate-x-[50%]"></div>
        
        {sortedYears.map((year) => (
          <div key={year} className="relative mb-24">
            {/* Year Badge */}
            <div className="flex justify-center mb-12 sticky top-4 z-20">
              <div className="bg-zinc-900/90 backdrop-blur-md text-white px-6 py-2.5 rounded-full font-bold text-[16px] shadow-lg flex items-center gap-2 border border-zinc-700/50">
                 <Calendar className="w-4 h-4 text-zinc-300" />
                 {year} {t('time.breakthroughs')}
              </div>
            </div>

            {/* Timeline Items */}
            <div className="flex flex-col gap-16">
              {grouped[year].map((entity, index) => {
                const isLeft = index % 2 === 0;
                return (
                  <div key={entity.id} className={`w-full flex ${isLeft ? 'justify-start' : 'justify-end'} relative`}>
                    
                    {/* Center Point */}
                     <div className="absolute left-[50%] top-[50%] -translate-x-[50%] -translate-y-[50%] z-10 flex items-center justify-center">
                        <div className="w-4 h-4 bg-white border-4 border-zinc-300 rounded-full shadow-sm" />
                     </div>

                     {/* Main Card */}
                     <div className={`w-[calc(50%-40px)] ${isLeft ? 'text-right' : 'text-left'}`}>
                       <motion.div 
                         initial={{ opacity: 0, y: 20 }}
                         animate={{ opacity: 1, y: 0 }}
                         transition={{ delay: index * 0.1, type: 'spring', stiffness: 300, damping: 30 }}
                         onClick={() => onNavigateToEntity(entity.id)}
                         className={`group flex items-center gap-6 bg-white/60 backdrop-blur-sm p-5 rounded-[24px] border border-zinc-200/80 shadow-sm hover:shadow-xl hover:bg-white cursor-pointer transition-all duration-300 hover:-translate-y-1 ${isLeft ? 'flex-row-reverse' : ''}`}
                       >
                         <div className="w-[140px] h-[140px] bg-zinc-100/50 rounded-[16px] overflow-hidden shrink-0 flex items-center justify-center p-2">
                            <img src={entity.imageUrl} alt={entity.name} className="w-full h-full object-contain mix-blend-multiply group-hover:scale-110 transition-transform duration-500 ease-out" />
                         </div>
                         <div className={`flex flex-col ${isLeft ? 'items-end text-right' : 'items-start text-left'}`}>
                            <div className="flex items-center gap-2 mb-2">
                               <span className="px-2 py-1 bg-zinc-100 text-zinc-500 text-[10px] font-bold uppercase tracking-widest rounded-[6px]">{entity.category}</span>
                               {entity.isNew && <span className="px-2 py-1 bg-blue-50 text-blue-600 text-[10px] font-bold rounded-[6px]">NEW</span>}
                            </div>
                            <span className="text-[22px] font-bold text-zinc-900 group-hover:text-amber-600 transition-colors leading-tight mb-1">{entity.name}</span>
                            <span className="text-[14px] font-[500] text-zinc-500">{entity.company}</span>
                            
                            {/* Short preview of specs */}
                            <div className={`mt-4 flex flex-col gap-1 ${isLeft ? 'items-end' : 'items-start'}`}>
                              {Object.entries(entity.specs).slice(0, 2).map(([k, v]) => (
                                <div key={k} className="text-[11px] text-zinc-400">
                                  <span className="uppercase tracking-wider font-bold opacity-70">{k}:</span> {v}
                                </div>
                              ))}
                            </div>
                         </div>
                       </motion.div>
                     </div>
                  </div>
                )
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
