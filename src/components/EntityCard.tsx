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
        className={`${isLarge ? 'w-[480px] h-[720px]' : 'w-[360px] h-[600px]'} transition-all duration-500 border border-dashed border-zinc-200 rounded-[28px] flex flex-col items-center justify-center text-zinc-400 bg-zinc-50/50`}
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
      className={`flex flex-col ${isLarge ? 'w-[480px]' : 'w-[360px]'} origin-center group/card transition-all duration-500 hover:scale-[1.02] cursor-pointer focus:outline-none focus-visible:ring-2 focus-visible:ring-zinc-400 focus-visible:ring-offset-8 rounded-[28px]`}
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
             <div className={`bg-black text-white flex items-center justify-center rounded-[4px] ${isLarge ? 'w-8 h-8' : 'w-6 h-6'}`} aria-hidden="true">
               <span className={`font-bold uppercase leading-none ${isLarge ? 'text-[14px]' : 'text-[10px]'}`}>{data.avatarText}</span>
             </div>
           )}
           <div className="flex flex-col">
             <div className="flex items-baseline gap-2 leading-none mb-1">
                <span id={`entity-name-${data.id}`} className={`font-bold text-zinc-900 ${isLarge ? 'text-[20px]' : 'text-[15px]'}`}>{data.title}</span>
                {data.metaText && (
                  <span className={`text-zinc-400 ${isLarge ? 'text-[14px]' : 'text-[12px]'}`} aria-label={data.metaText}>{data.metaText}</span>
                )}
             </div>
             <span className={`font-medium text-zinc-400 leading-none ${isLarge ? 'text-[15px]' : 'text-[13px]'}`}>{data.subtitle}</span>
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
          className={`relative w-full ${isLarge ? 'h-[720px]' : 'h-[540px]'} bg-zinc-100/70 rounded-[28px] p-6 group flex items-center justify-center overflow-hidden transition-all duration-500 group-hover/card:shadow-[0_20px_40px_-15px_rgba(0,0,0,0.1)] group-hover/card:bg-zinc-100/90`}
        >
         {data.badge && (
           <div 
             className={`absolute top-4 left-4 bg-zinc-400/90 backdrop-blur-md text-white font-bold px-3 py-1 rounded-full z-10 shadow-sm leading-none ${isLarge ? 'text-[13px]' : 'text-[11px]'}`}
             aria-label={data.badge}
           >
             {data.badge}
           </div>
         )}
         <motion.img
           layout
           src={data.image}
           alt={data.title}
           className="w-full h-full object-contain mix-blend-multiply drop-shadow-2xl transition-transform duration-700 ease-out group-hover:scale-105"
           draggable="false"
         />
       </motion.div>
    </motion.div>
  );
});
