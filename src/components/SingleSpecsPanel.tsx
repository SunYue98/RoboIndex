import { ArrowUpRight, Network } from 'lucide-react';
import { Entity, mockData } from '../data/entities';
import { motion } from 'motion/react';
import { useLang } from '../i18n';

interface SingleSpecsPanelProps {
  entity: Entity;
  onFindRelated?: () => void;
  onNavigateToEntity?: (entityId: string) => void;
}

export function SingleSpecsPanel({ entity, onFindRelated, onNavigateToEntity }: SingleSpecsPanelProps) {
  const { t } = useLang();
  const tags = entity.tags || [];

  const relatedEntities = (entity.relatedIds || [])
    .map(id => mockData.find(e => e.id === id))
    .filter((e): e is Entity => e !== undefined);

  // Capitalize first letter of spec keys
  const formatLabel = (key: string) => {
    return key.charAt(0).toUpperCase() + key.slice(1);
  };

  return (
    <motion.div 
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      transition={{ duration: 0.5, type: 'spring', bounce: 0.2 }}
      className="flex flex-col ml-8 w-[240px] h-[720px] pt-16"
    >
      <div className="flex flex-col border-b border-zinc-100 pb-4 mb-4">
        {Object.entries(entity.specs).map(([key, val]) => (
           <div className="flex items-center w-full justify-between py-[12px]" key={key}>
             <div className="w-[80px] text-left text-[12px] font-[500] text-zinc-400 shrink-0">
               {formatLabel(key)}
             </div>
             <div className="flex-1 text-left text-[14px] font-[500] text-zinc-600 line-clamp-1">
               {val || '—'}
             </div>
           </div>
        ))}
      </div>

      <div className="flex flex-col gap-3 mb-auto">
        {tags.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {tags.map(tag => (
              <span key={tag} className="px-3 py-1.5 rounded-full border border-zinc-200 text-[12px] font-[500] text-zinc-500 tracking-tight">
                {tag}
              </span>
            ))}
          </div>
        )}

        {relatedEntities.length > 0 && (
          <div className="flex flex-col gap-2 mt-2">
            <h4 className="text-[11px] font-bold text-zinc-400 uppercase tracking-widest mb-1">{t('panel.related')}</h4>
            <div className="flex flex-wrap gap-2">
              {relatedEntities.map(rel => (
                <button 
                  key={rel.id} 
                  onClick={() => onNavigateToEntity?.(rel.id)}
                  className="group flex flex-col items-start px-3 py-2 rounded-[12px] bg-white border border-zinc-200 shadow-sm hover:border-zinc-300 hover:shadow-md transition-all focus:outline-none focus:ring-2 focus:ring-zinc-400 active:scale-[0.98] w-full"
                >
                   <div className="flex items-center gap-1.5 w-full">
                     <span className="w-1.5 h-1.5 rounded-full bg-zinc-400 group-hover:bg-zinc-600 transition-colors"></span>
                     <span className="text-[10px] font-bold text-zinc-400 uppercase tracking-wider">{t(rel.category)}</span>
                   </div>
                   <span className="text-[13px] font-[600] text-zinc-700 mt-1">{rel.name}</span>
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="flex flex-col gap-3">
        {onFindRelated && (
          <button 
            onClick={onFindRelated}
            className="flex items-center justify-between w-full px-4 py-3 bg-zinc-50 border border-zinc-200 rounded-[16px] text-[13px] font-[500] tracking-tight text-zinc-600 hover:border-zinc-300 hover:bg-zinc-100 transition-all focus:outline-none focus:ring-2 focus:ring-zinc-200 group mt-4"
          >
            <div className="flex items-center gap-2">
              <Network className="w-4 h-4 text-zinc-400 group-hover:text-zinc-600 transition-colors" />
              <span>{t('panel.system_link')}</span>
            </div>
          </button>
        )}
        
        <button className="flex items-center justify-between w-full px-4 py-3 bg-zinc-900 border border-zinc-900 rounded-full text-[13px] font-[500] tracking-tight text-white hover:bg-zinc-800 transition-all focus:outline-none focus:ring-2 focus:ring-zinc-900 group">
          <span>{t('panel.visit')}</span>
          <div className="w-6 h-6 rounded-full bg-white/20 flex items-center justify-center text-white group-hover:bg-white/30 transition-colors">
            <ArrowUpRight className="w-3 h-3" />
          </div>
        </button>
      </div>
    </motion.div>
  );
}
