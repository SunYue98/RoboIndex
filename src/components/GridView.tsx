import { motion, AnimatePresence } from 'motion/react';
import { Entity } from '../data/entities';
import { X, Search } from 'lucide-react';
import { useState, useMemo } from 'react';
import { useLang } from '../i18n';

interface GridViewProps {
  isOpen: boolean;
  onClose: () => void;
  items: Entity[];
  onSelect: (id: string) => void;
  title: string;
}

export function GridView({ isOpen, onClose, items, onSelect, title }: GridViewProps) {
  const { t } = useLang();
  const [search, setSearch] = useState('');

  const filteredItems = useMemo(() => {
    return items.filter(item => 
      item.name.toLowerCase().includes(search.toLowerCase()) || 
      item.company.toLowerCase().includes(search.toLowerCase())
    );
  }, [items, search]);

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 30 }}
          transition={{ type: 'spring', damping: 25, stiffness: 200 }}
          className="absolute inset-0 z-[60] bg-zinc-50/95 backdrop-blur-xl flex flex-col items-center pt-24 pb-12 px-10 overflow-hidden"
        >
          <div className="absolute top-8 right-10">
             <button onClick={onClose} className="p-3 bg-white border border-zinc-200 rounded-full hover:bg-zinc-100 transition-colors shadow-sm text-zinc-500 hover:text-zinc-900">
                <X className="w-5 h-5" />
             </button>
          </div>

          <div className="w-full max-w-6xl flex flex-col h-full">
            <div className="flex items-center justify-between mb-8 shrink-0">
               <div>
                  <h2 className="text-[28px] font-bold text-zinc-900 tracking-tight">{title}</h2>
                  <p className="text-zinc-500 font-medium mt-1">{filteredItems.length} {t('items') || 'items'} available</p>
               </div>
               
               <div className="flex items-center gap-3 bg-white px-4 py-2.5 rounded-full border border-zinc-200 shadow-sm w-[300px]">
                  <Search className="w-4 h-4 text-zinc-400" />
                  <input 
                    type="text" 
                    placeholder={t('search.placeholder') || "Search..."}
                    value={search}
                    onChange={e => setSearch(e.target.value)}
                    className="w-full bg-transparent border-none outline-none text-[14px] text-zinc-800 placeholder-zinc-400 font-medium"
                  />
               </div>
            </div>

            <div className="w-full flex-1 overflow-y-auto pr-4 pb-10 grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6 content-start custom-scrollbar">
               {filteredItems.map(item => (
                 <motion.div
                   key={item.id}
                   whileHover={{ y: -4 }}
                   onClick={() => {
                     onSelect(item.id);
                     onClose();
                   }}
                   className="flex flex-col bg-white border border-zinc-200/80 rounded-[24px] p-4 cursor-pointer hover:shadow-xl hover:border-zinc-300 transition-all duration-300 group"
                 >
                    <div className="w-full aspect-square bg-gradient-to-br from-zinc-50 to-zinc-100 rounded-[16px] mb-4 flex items-center justify-center p-4 overflow-hidden mix-blend-multiply relative shadow-inner">
                       <img src={item.imageUrl} alt={item.name} className="w-full h-full object-contain group-hover:scale-110 transition-transform duration-500 ease-out" />
                       {item.isNew && (
                         <div className="absolute top-2 left-2 px-2 py-0.5 bg-blue-100 text-blue-700 text-[9px] font-bold uppercase rounded-full">New</div>
                       )}
                    </div>
                    <div className="flex flex-col px-1">
                       <span className="text-[15px] font-bold text-zinc-900 leading-tight group-hover:text-amber-600 transition-colors">{item.name}</span>
                       <span className="text-[12px] font-medium text-zinc-500 mt-1 line-clamp-1">{item.company}</span>
                    </div>
                 </motion.div>
               ))}
               {filteredItems.length === 0 && (
                 <div className="col-span-full py-20 flex flex-col items-center justify-center text-zinc-400">
                    <Search className="w-8 h-8 mb-4 opacity-50" />
                    <p className="font-medium text-[15px]">No results found for "{search}"</p>
                 </div>
               )}
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
