import { mockData, Entity, Category, CATEGORY_MAP, TOP_LEVEL_GROUPS } from '../data/entities';
import { motion, AnimatePresence } from 'motion/react';
import { Calendar, Search, Filter, X, ChevronRight, Hash } from 'lucide-react';
import { useLang } from '../i18n';
import { useRef, useState, useEffect, useMemo } from 'react';

interface TimelineViewProps {
  onNavigateToEntity: (id: string) => void;
}

export function TimelineView({ onNavigateToEntity }: TimelineViewProps) {
  const { t } = useLang();
  const scrollRef = useRef<HTMLDivElement>(null);

  // States for search and filter
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<Category | 'All'>('All');
  const [showFilters, setShowFilters] = useState(false);

  // Derive all available categories from the data for the filter
  const availableCategories = useMemo(() => {
    const cats = new Set<Category>();
    mockData.forEach(item => cats.add(item.category));
    return Array.from(cats);
  }, []);

  // Filter Data
  const filteredData = useMemo(() => {
    return mockData.filter(entity => {
      const matchesSearch = entity.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
                            entity.company.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesCat = selectedCategory === 'All' || entity.category === selectedCategory;
      return matchesSearch && matchesCat;
    });
  }, [searchQuery, selectedCategory]);

  // Group by year
  const grouped = useMemo(() => {
    return filteredData.reduce((acc, entity) => {
      if (!acc[entity.year]) acc[entity.year] = [];
      acc[entity.year].push(entity);
      return acc;
    }, {} as Record<string, Entity[]>);
  }, [filteredData]);

  // Sort years ascending for horizontal sequence
  const sortedYears = useMemo(() => Object.keys(grouped).sort((a, b) => parseInt(a) - parseInt(b)), [grouped]);

  // Handle Wheel Scroll
  useEffect(() => {
    const el = scrollRef.current;
    if (!el) return;

    const handleWheel = (e: WheelEvent) => {
      // If we're scrolling vertically, translate it to horizontal
      if (Math.abs(e.deltaY) > Math.abs(e.deltaX) && !e.shiftKey) {
        e.preventDefault();
        el.scrollLeft += e.deltaY;
      }
    };

    el.addEventListener('wheel', handleWheel, { passive: false });
    return () => el.removeEventListener('wheel', handleWheel);
  }, []);

  // Minimap Navigation
  const scrollToYear = (yearIndex: number) => {
    if (!scrollRef.current) return;
    
    // Calculate approximate position. 
    // Initial offset + (yearIndex * space per year) + some padding
    // We can also find the DOM element and scroll into view, but computing is smoother.
    const yearElements = document.querySelectorAll('[data-year-container]');
    if (yearElements[yearIndex]) {
      yearElements[yearIndex].scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
    }
  };

  return (
    <div className="w-full h-full flex flex-col items-center justify-start overflow-hidden relative">
      
      {/* Search & Filter Top Bar */}
      <div className="w-full max-w-5xl px-8 pt-8 pb-4 z-40 relative flex flex-col gap-4">
        <div className="flex items-center gap-4 bg-white/80 backdrop-blur-md p-2 rounded-[20px] shadow-sm border border-zinc-200/60">
           <div className="flex-1 flex items-center gap-3 px-4">
             <Search className="w-5 h-5 text-zinc-400" />
             <input 
               type="text" 
               placeholder={t('search.placeholder') || "Search entities, companies..."}
               className="w-full bg-transparent border-none outline-none text-[15px] font-medium text-zinc-800 placeholder-zinc-400"
               value={searchQuery}
               onChange={e => setSearchQuery(e.target.value)}
             />
             {searchQuery && (
               <button onClick={() => setSearchQuery('')} className="p-1 hover:bg-zinc-100 rounded-full text-zinc-400 transition-colors">
                 <X className="w-4 h-4" />
               </button>
             )}
           </div>
           <div className="h-8 w-[1px] bg-zinc-200"></div>
           <button 
             onClick={() => setShowFilters(!showFilters)}
             className={`flex items-center gap-2 px-6 py-2.5 rounded-[14px] font-bold text-[14px] transition-all ${
               showFilters || selectedCategory !== 'All' 
                 ? 'bg-zinc-900 text-white shadow-md' 
                 : 'bg-zinc-100 text-zinc-600 hover:bg-zinc-200'
             }`}
           >
             <Filter className="w-4 h-4" />
             {selectedCategory === 'All' ? t('nav.filter') || 'Filter' : selectedCategory}
           </button>
        </div>

        {/* Filter Drawer */}
        <AnimatePresence>
          {showFilters && (
            <motion.div 
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="overflow-hidden bg-white/90 backdrop-blur-xl border border-zinc-200/80 shadow-lg rounded-[24px]"
            >
              <div className="p-6 flex flex-wrap gap-2">
                <button
                  onClick={() => setSelectedCategory('All')}
                  className={`px-4 py-2 rounded-full text-[13px] font-bold transition-all ${
                    selectedCategory === 'All' ? 'bg-amber-100 text-amber-700 ring-2 ring-amber-400/50' : 'bg-zinc-100 text-zinc-600 hover:bg-zinc-200'
                  }`}
                >
                  All Categories
                </button>
                {availableCategories.map(cat => (
                  <button
                    key={cat}
                    onClick={() => setSelectedCategory(cat)}
                    className={`px-4 py-2 rounded-full text-[13px] font-bold transition-all flex items-center gap-1.5 ${
                      selectedCategory === cat ? 'bg-amber-100 text-amber-700 ring-2 ring-amber-400/50' : 'bg-zinc-50 border border-zinc-200 text-zinc-600 hover:bg-zinc-100'
                    }`}
                  >
                    <Hash className="w-3 h-3 opacity-50" />
                    {cat}
                  </button>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Main Timeline Scrollable Area */}
      <div 
        ref={scrollRef}
        className={`w-full flex-1 flex flex-col items-start justify-center overflow-x-auto overflow-y-hidden px-10 sm:px-[10vw] cursor-auto no-scrollbar selection:bg-transparent transition-opacity duration-300 ${filteredData.length === 0 ? 'opacity-0' : 'opacity-100'}`}
      >
        <div className="flex relative items-center min-w-max h-full pb-32 pointer-events-none">
          
          {/* Main Horizontal Timeline Track */}
          <div className="absolute top-[50%] left-0 right-0 h-[4px] bg-gradient-to-r from-transparent via-zinc-200 to-transparent -translate-y-[50%] z-0 pointer-events-none rounded-full"></div>

          {/* Start Genesis Node */}
          <div className="relative flex items-center h-full mr-20 shrink-0">
             <div className="absolute top-[50%] left-0 -translate-y-[50%] z-20 flex flex-col items-center">
                <div className="w-8 h-8 rounded-full bg-zinc-100 border-4 border-zinc-200 flex items-center justify-center shadow-inner">
                   <div className="w-3 h-3 bg-zinc-300 rounded-full" />
                </div>
                <span className="absolute top-12 text-[12px] font-bold text-zinc-400 tracking-[0.2em] uppercase whitespace-nowrap">Origin</span>
             </div>
          </div>

          {sortedYears.map((year, yearIndex) => (
            <div key={year} data-year-container className="relative flex items-center h-[500px] mt-[100px] mr-12 sm:mr-32 shrink-0 pointer-events-auto">
              
              {/* Year Marker Node */}
              <div className="relative z-20 flex flex-col items-center shrink-0 w-[60px] mr-8">
                 <div className="absolute top-[50%] -translate-y-[calc(50%+50px)] bg-black/90 backdrop-blur-md text-white px-5 py-2 rounded-full font-bold text-[16px] shadow-xl flex items-center gap-2 border border-zinc-700/50 mb-2 whitespace-nowrap">
                    <Calendar className="w-4 h-4 text-amber-400" />
                    {year}
                 </div>
                 <div className="absolute top-[50%] -translate-y-[50%] w-4 h-4 bg-amber-400 border-[4px] border-white rounded-full shadow-md ring-4 ring-amber-50" />
              </div>

              {/* Entities in this year */}
              <div className="flex items-center gap-8 sm:gap-16 shrink-0 h-full relative pl-8">
                {grouped[year].map((entity, index) => {
                  const isAbove = index % 2 === 0;
                  const isImportant = entity.importance === 'high';
                  
                  return (
                    <motion.div 
                      key={entity.id}
                      initial={{ opacity: 0, scale: 0.8, y: isAbove ? 20 : -20 }}
                      animate={{ opacity: 1, scale: 1, y: 0 }}
                      transition={{ delay: (yearIndex * 0.1) + (index * 0.05), type: 'spring', stiffness: 300, damping: 25 }}
                      className={`relative flex items-center justify-center shrink-0 h-full ${isImportant ? 'w-[280px] sm:w-[320px]' : 'w-[220px] sm:w-[260px]'}`}
                    >
                       {/* Connection to track */}
                       <div className="absolute top-[50%] left-[50%] -translate-x-[50%] -translate-y-[50%] z-10 w-2.5 h-2.5 bg-zinc-400 rounded-full border-2 border-white shadow-sm" />
                       <div className={`absolute left-[50%] w-[2px] bg-gradient-to-b ${isAbove ? 'from-zinc-200 to-transparent bottom-[50%] h-[90px]' : 'from-transparent to-zinc-200 top-[50%] h-[90px]'} -translate-x-[50%]`}></div>

                       {/* Entity Card */}
                       <div
                         onClick={() => onNavigateToEntity(entity.id)}
                         className={`absolute left-[50%] -translate-x-[50%] ${isAbove ? 'bottom-[calc(50%+90px)]' : 'top-[calc(50%+90px)]'} 
                           group flex flex-col gap-3 bg-white/80 backdrop-blur-xl p-5 rounded-[24px] border shadow-sm hover:shadow-2xl hover:bg-white transition-all duration-400 
                           z-20 cursor-pointer w-full 
                           ${isImportant ? 'border-amber-200/60 ring-1 ring-amber-100' : 'border-zinc-200/80'}
                           ${isAbove ? 'hover:-translate-y-3' : 'hover:translate-y-3'}
                         `}
                       >
                         <div className="flex items-start gap-4">
                           <div className={`rounded-[16px] overflow-hidden shrink-0 flex items-center justify-center p-2 bg-gradient-to-br from-zinc-50 to-zinc-100 shadow-inner
                             ${isImportant ? 'w-20 h-20' : 'w-16 h-16'}
                           `}>
                              <img src={entity.imageUrl} alt={entity.name} className="w-full h-full object-contain mix-blend-multiply group-hover:scale-110 group-hover:-rotate-3 transition-all duration-500 ease-out pointer-events-none" />
                           </div>
                           <div className="flex flex-col items-start gap-1.5 flex-1">
                              <div className="flex flex-wrap gap-1.5">
                                 {isImportant && (
                                   <span className="px-2 py-0.5 bg-amber-100 text-amber-700 text-[9px] font-bold uppercase tracking-widest rounded-[6px]">Notable</span>
                                 )}
                                 <span className="px-2 py-0.5 bg-zinc-100 text-zinc-500 text-[9px] font-bold uppercase tracking-widest rounded-[6px]">{entity.category}</span>
                              </div>
                              <span className={`font-bold text-zinc-900 group-hover:text-amber-600 transition-colors leading-tight ${isImportant ? 'text-[18px]' : 'text-[15px]'}`}>{entity.name}</span>
                              <span className="text-[12px] font-[600] text-zinc-400 line-clamp-1">{entity.company}</span>
                           </div>
                         </div>
                       </div>
                    </motion.div>
                  )
                })}
              </div>

            </div>
          ))}

          {/* Future Endpoint Marker */}
          <div className="relative flex items-center h-full ml-12 pointer-events-none">
             <div className="absolute top-[50%] left-0 -translate-y-[50%] z-20 flex items-center gap-3 opacity-50">
                <div className="w-2.5 h-2.5 bg-zinc-300 rounded-full" />
                <div className="w-2 h-2 bg-zinc-200 rounded-full" />
                <div className="w-1.5 h-1.5 bg-zinc-100 rounded-full" />
                <ChevronRight className="w-5 h-5 text-zinc-300" />
             </div>
          </div>

        </div>
      </div>

      {/* Empty State */}
      {filteredData.length === 0 && (
         <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
            <div className="w-16 h-16 bg-zinc-100 rounded-full flex items-center justify-center mb-4">
               <Search className="w-8 h-8 text-zinc-300" />
            </div>
            <h3 className="text-[18px] font-bold text-zinc-800">No results found</h3>
            <p className="text-[14px] font-medium text-zinc-500 mt-1">Try adjusting your search or filters.</p>
         </div>
      )}

      {/* Minimap Widget */}
      {sortedYears.length > 0 && (
        <div className="absolute bottom-6 left-[50%] -translate-x-[50%] z-50">
          <div className="bg-white/90 backdrop-blur-xl border border-zinc-200/80 shadow-[0_8px_30px_rgb(0,0,0,0.08)] rounded-full px-6 py-3 flex items-center gap-3">
             <span className="text-[10px] font-bold text-zinc-400 uppercase tracking-widest mr-2">Timeline</span>
             {sortedYears.map((year, i) => (
               <div key={year} className="flex items-center">
                 <button 
                   onClick={() => scrollToYear(i)}
                   className="w-10 h-10 rounded-full flex items-center justify-center text-[12px] font-bold text-zinc-600 hover:text-white hover:bg-zinc-900 transition-all hover:scale-110 active:scale-95"
                 >
                   {year}
                 </button>
                 {i < sortedYears.length - 1 && (
                   <div className="w-4 h-[2px] bg-zinc-100 mx-1 rounded-full"></div>
                 )}
               </div>
             ))}
          </div>
        </div>
      )}

    </div>
  )
}


