import { memo } from 'react';
import { Minus } from 'lucide-react';
import { motion } from 'motion/react';

export interface EntityCardData {
  id: string;
  title: string;
  subtitle: string;
  badge?: string | null;
  image: string;
  metaText?: string;
  avatarText?: string;
}

interface EntityCardProps {
  data?: EntityCardData | null;
  align?: 'left' | 'right';
  onRemove?: () => void;
  size?: 'normal' | 'large';
  emptyText?: string;
}

export const EntityCard = memo(function EntityCard({ 
  data, 
  align = 'left', 
  onRemove, 
  size = 'normal',
  emptyText = 'Select an item' 
}: EntityCardProps) {
  const isLarge = size === 'large';
  
  if (!data) {
    return (
      <motion.div 
        layout
        className={`${isLarge ? 'w-[440px] h-[640px]' : 'w-[340px] h-[520px]'} transition-all duration-500 border border-dashed border-zinc-200 rounded-[28px] flex flex-col items-center justify-center text-zinc-400 bg-zinc-50/50`}
        role="region"
        aria-label="Empty Slot"
      >
         <span className="text-sm font-medium">{emptyText}</span>
      </motion.div>
    );
  }

  return (
    <motion.div 
      layout
      transition={{ type: 'spring', bounce: 0.2, duration: 0.8 }}
      className={`flex flex-col ${isLarge ? 'w-[440px]' : 'w-[340px]'} origin-center group/card transition-all duration-500 hover:scale-[1.03] cursor-pointer focus:outline-none focus-visible:ring-2 focus-visible:ring-zinc-400 focus-visible:ring-offset-8 rounded-[32px]`}
      role="article"
      aria-labelledby={`entity-name-${data.id}`}
      tabIndex={0}
      onKeyDown={(e) => {
         if (e.key === ' ' || e.key === 'Enter') {
           e.preventDefault();
         }
      }}
    >
       {/* Header Area */}
       <motion.div layout className="flex items-start justify-between mb-4 px-2 h-[40px]">
         <div className="flex items-center gap-3">
           {data.avatarText && (
             <div className={`bg-black text-white flex items-center justify-center rounded-[8px] ${isLarge ? 'w-10 h-10' : 'w-8 h-8'} shadow-sm`} aria-hidden="true">
               <span className={`font-bold uppercase leading-none ${isLarge ? 'text-[16px]' : 'text-[12px]'}`}>{data.avatarText}</span>
             </div>
           )}
           <div className="flex flex-col">
             <div className="flex items-baseline gap-2 leading-none mb-1">
                <span id={`entity-name-${data.id}`} className={`font-bold text-zinc-900 ${isLarge ? 'text-[22px]' : 'text-[17px]'}`}>{data.title}</span>
                {data.metaText && (
                  <span className={`text-zinc-400 font-bold ${isLarge ? 'text-[14px]' : 'text-[12px]'}`} aria-label={data.metaText}>{data.metaText}</span>
                )}
             </div>
             <span className={`font-medium text-zinc-500 leading-none ${isLarge ? 'text-[16px]' : 'text-[14px]'}`}>{data.subtitle}</span>
           </div>
         </div>
         {align === 'right' && onRemove && (
           <button 
             onClick={onRemove}
             className="w-8 h-8 rounded-full bg-zinc-100 flex items-center justify-center text-zinc-400 hover:text-zinc-600 hover:bg-zinc-200 transition-colors focus:outline-none focus:ring-2 focus:ring-zinc-400"
             aria-label={`Remove ${data.title}`}
             onKeyDown={(e) => e.stopPropagation()}
           >
              <Minus className="w-4 h-4" aria-hidden="true" />
           </button>
         )}
       </motion.div>

       {/* Image Area */}
       <motion.div 
          layout 
          className={`relative w-full ${isLarge ? 'h-[560px]' : 'h-[420px]'} bg-gradient-to-br from-zinc-50 via-zinc-100/50 to-zinc-100 border border-black/[0.03] rounded-[32px] p-6 group flex items-center justify-center overflow-hidden transition-all duration-700 group-hover/card:shadow-[0_40px_80px_-20px_rgba(0,0,0,0.12)] group-hover/card:-translate-y-2`}
        >
         {/* Subtle inner reflection */}
         <div className="absolute inset-0 rounded-[32px] ring-1 ring-inset ring-white/60 pointer-events-none"></div>
         
         {data.badge && (
           <div 
             className={`absolute top-5 left-5 bg-zinc-900/90 backdrop-blur-md text-white font-bold px-4 py-1.5 rounded-full z-10 shadow-lg leading-none tracking-wide ${isLarge ? 'text-[12px]' : 'text-[10px]'}`}
             aria-label={data.badge}
           >
             {data.badge}
           </div>
         )}
         <motion.img
           layout
           src={data.image}
           alt={data.title}
           className="w-full h-full object-contain mix-blend-multiply drop-shadow-2xl transition-all duration-700 ease-out group-hover:scale-110 group-hover:-rotate-2"
           draggable="false"
         />
       </motion.div>
    </motion.div>
  );
});
