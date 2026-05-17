import { useState, useMemo, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Dices, Plus, Network, Globe, MessageSquare, Send, Github, LayoutGrid, Loader2 } from 'lucide-react';
import { Entity, Category, CATEGORY_MAP, TopLevelGroup, loadEntities } from './data/entities';
import { EntityCard, EntityCardData } from './components/EntityCard';
import { SpecsColumn } from './components/SpecsColumn';
import { WheelSelector } from './components/WheelSelector';
import { HorizontalWheelSelector } from './components/HorizontalWheelSelector';
import { SingleSpecsPanel } from './components/SingleSpecsPanel';
import { SystemOverview } from './components/SystemOverview';
import { TimelineView } from './components/TimelineView';
import { GridView } from './components/GridView';
import { ContactModal, SubmitModal } from './components/Modals';
import { useLang } from './i18n';

export type MainTab = '全景架构' | '演进脉络' | '硬件' | '软件' | '生态与应用' | '参与实体';

export default function App() {
  const [mockData, setMockData] = useState<Entity[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadEntities().then(data => {
      setMockData(data);
      if (data.length > 0) {
        setLeftId(data.find(d => d.category === '整机平台')?.id || data[0].id);
      }
      setIsLoading(false);
    });
  }, []);

  const [mainTab, setMainTab] = useState<MainTab>('全景架构');
  const [hardwareCat, setHardwareCat] = useState<Category>('整机平台');
  const [softwareCat, setSoftwareCat] = useState<Category>('基础模型');
  const [ecoCat, setEcoCat] = useState<Category>('开发生态');
  const [playersCat, setPlayersCat] = useState<Category>('产业');
  const [timelineFocusId, setTimelineFocusId] = useState<string | null>(null);

  const { lang, setLang, t } = useLang();
  const [contactOpen, setContactOpen] = useState(false);
  const [submitOpen, setSubmitOpen] = useState(false);
  const [showGridView, setShowGridView] = useState(false);

  const activeCategory = mainTab === '硬件' ? hardwareCat : (mainTab === '软件' ? softwareCat : (mainTab === '生态与应用' ? ecoCat : playersCat));

  const list = useMemo(() => {
    return mockData.filter(d => d.category === activeCategory);
  }, [mainTab, activeCategory, mockData]);

  const [leftId, setLeftId] = useState<string | null>(null);
  const [rightId, setRightId] = useState<string | null>(null);
  const [isComparing, setIsComparing] = useState(false);

  // When changing tabs, handle selections gracefully
  useEffect(() => {
    if (isLoading) return;
    const initial = list[0]?.id || null;
    setLeftId(initial);
    setIsComparing(false);
    setRightId(null);
  }, [mainTab, activeCategory, list, isLoading]);

  const leftEntity = mockData.find(l => l.id === leftId) || null;
  const rightEntity = mockData.find(l => l.id === rightId) || null;

  const mapEntityToCardData = (entity: typeof leftEntity): EntityCardData | null => {
    if (!entity) return null;
    return {
      id: entity.id,
      title: entity.name,
      subtitle: entity.company,
      badge: entity.isNew ? 'New Release' : undefined,
      image: entity.imageUrl,
      metaText: entity.year,
      avatarText: entity.company ? entity.company.charAt(0).toUpperCase() : undefined,
    };
  };

  const leftCardData = useMemo(() => mapEntityToCardData(leftEntity), [leftEntity]);
  const rightCardData = useMemo(() => mapEntityToCardData(rightEntity), [rightEntity]);

  const setCategory = (cat: Category) => {
    if (CATEGORY_MAP['硬件'].includes(cat)) {
      setHardwareCat(cat);
      setMainTab('硬件');
    } else if (CATEGORY_MAP['软件'].includes(cat)) {
      setSoftwareCat(cat);
      setMainTab('软件');
    } else if (CATEGORY_MAP['生态与应用'].includes(cat)) {
      setEcoCat(cat);
      setMainTab('生态与应用');
    } else if (CATEGORY_MAP['参与实体'] && CATEGORY_MAP['参与实体'].includes(cat)) {
      setPlayersCat(cat);
      setMainTab('参与实体');
    }
  };

  const handleNavigateToEntity = (entityId: string) => {
    const entity = mockData.find(e => e.id === entityId);
    if (!entity) return;
    
    const isHardware = CATEGORY_MAP['硬件'].includes(entity.category);
    const isSoftware = CATEGORY_MAP['软件'].includes(entity.category);
    const isEco = CATEGORY_MAP['生态与应用'].includes(entity.category);
    
    if (isHardware) {
      setMainTab('硬件');
      setHardwareCat(entity.category);
    } else if (isSoftware) {
      setMainTab('软件');
      setSoftwareCat(entity.category);
    } else if (isEco) {
      setMainTab('生态与应用');
      setEcoCat(entity.category);
    } else {
      setMainTab('参与实体');
      setPlayersCat(entity.category);
    }
    setLeftId(entityId);
    setIsComparing(false);
    setRightId(null);
  };

  // Option to randomize selections
  const randomize = () => {
     if (list.length < 1) return;
     let a = Math.floor(Math.random() * list.length);
     setLeftId(list[a].id);

     if (isComparing && list.length > 1) {
       let b = Math.floor(Math.random() * list.length);
       while (b === a) {
         b = Math.floor(Math.random() * list.length);
       }
       setRightId(list[b].id);
     }
  };
  
  const handleStartCompare = () => {
    setIsComparing(true);
    setRightId(list.find(l => l.id !== leftId)?.id || list[0]?.id || null);
  };

  if (isLoading) {
    return (
      <div className="h-screen w-screen flex items-center justify-center bg-white text-zinc-900">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="w-8 h-8 animate-spin text-zinc-400" />
          <p className="text-zinc-500 text-sm font-medium tracking-wide">Loading Data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen w-screen overflow-hidden bg-white text-zinc-900 font-sans flex flex-col relative selection:bg-zinc-200">
      <div className="min-w-[1280px] w-full h-full flex flex-col relative">
        
        {/* Header */}
        <header className="relative w-full px-10 pt-6 pb-2 flex flex-col z-50 gap-4 bg-zinc-50/80 backdrop-blur-md border-b border-zinc-200/50 shadow-sm shrink-0">
           <div className="flex items-center w-full justify-between">
             {/* Left Actions + Logo */}
             <div className="flex items-center gap-6 shrink-0">
               <div className="flex items-center gap-2 bg-zinc-100/80 p-1.5 rounded-full border border-zinc-200/50 shadow-sm">
                 <button 
                   onClick={() => setLang(l => l === 'zh' ? 'en' : 'zh')}
                   className="flex items-center gap-1.5 px-3 py-1.5 rounded-full hover:bg-white text-zinc-600 hover:text-zinc-900 transition-colors text-[12px] font-bold tracking-wide"
                 >
                   <Globe className="w-3.5 h-3.5" />
                   {lang === 'zh' ? 'EN' : '中'}
                 </button>
                 <a 
                   href="https://github.com/SunYue98/RoboIndex"
                   target="_blank"
                   rel="noopener noreferrer"
                   className="flex items-center gap-1.5 px-3 py-1.5 rounded-full hover:bg-white text-zinc-600 hover:text-zinc-900 transition-colors text-[12px] font-bold tracking-wide"
                 >
                   <Github className="w-3.5 h-3.5" />
                   GitHub
                 </a>
                 <button 
                   onClick={() => setContactOpen(true)}
                   className="flex items-center gap-1.5 px-3 py-1.5 rounded-full hover:bg-white text-zinc-600 hover:text-zinc-900 transition-colors text-[12px] font-bold tracking-wide"
                 >
                   <MessageSquare className="w-3.5 h-3.5" />
                   {lang === 'zh' ? '联系' : 'Contact'}
                 </button>
                 <button 
                   onClick={() => setSubmitOpen(true)}
                   className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-zinc-900 text-white hover:bg-zinc-800 transition-colors text-[12px] font-bold tracking-wide shadow-sm"
                 >
                   <Send className="w-3.5 h-3.5" />
                   {lang === 'zh' ? '提交' : 'Submit'}
                 </button>
               </div>

               <div className="w-[1px] h-6 bg-zinc-300 rounded-full mx-2 hidden lg:block" />

               <div className="flex items-center gap-2 cursor-pointer shrink-0" onClick={() => setMainTab('全景架构')}>
                 <div className="w-8 h-8 bg-zinc-900 text-white flex items-center justify-center rounded-[8px]">
                    <Network className="w-4 h-4" />
                 </div>
                 <div className="text-[17px] font-bold tracking-tight text-zinc-900 whitespace-nowrap">
                   RoboIndex
                 </div>
               </div>
             </div>
               
             {/* Main Top Navigation */}
             <div className="flex items-center gap-1 bg-zinc-100/80 p-1 rounded-full border border-zinc-200/50 shadow-sm shrink-0">
                  {(['全景架构', '演进脉络', '硬件', '软件', '生态与应用', '参与实体'] as MainTab[]).map(tab => (
                    <button 
                      key={tab}
                      onClick={() => {
                        setMainTab(tab);
                        if (tab !== '演进脉络') setTimelineFocusId(null);
                      }}
                      className={`px-4 sm:px-5 py-1.5 rounded-full text-[13px] font-[600] transition-all duration-300 focus:outline-none whitespace-nowrap ${
                        mainTab === tab 
                          ? 'text-zinc-900 shadow-[0_2px_10px_-2px_rgba(0,0,0,0.1)] border border-black/5 bg-gradient-to-b from-white to-zinc-50' 
                          : 'text-zinc-500 hover:text-zinc-800 hover:bg-black/5 hover:shadow-sm border border-transparent'
                      }`}
                    >
                      {t(tab)}
                    </button>
                  ))}
               </div>

             {/* Right Addons */}
             <div className="flex items-center gap-2 shrink-0 justify-end w-[90px]">
                {(mainTab !== '全景架构' && mainTab !== '演进脉络') && (
                  <>
                    <button title="View Grid" onClick={() => setShowGridView(true)} className="p-2 text-zinc-400 hover:text-zinc-800 transition-colors focus:outline-none focus:ring-2 focus:ring-zinc-200 rounded-full bg-zinc-50 border border-zinc-100 hover:bg-zinc-100">
                      <LayoutGrid className="w-5 h-5" />
                    </button>
                    <button title="Randomize" onClick={randomize} className="p-2 text-zinc-400 hover:text-zinc-800 transition-colors focus:outline-none focus:ring-2 focus:ring-zinc-200 rounded-full bg-zinc-50 border border-zinc-100 hover:bg-zinc-100">
                      <Dices className="w-5 h-5" />
                    </button>
                  </>
                )}
             </div>
           </div>

           {/* Sub Categories or Compare Label */}
           <div className="flex w-full justify-center h-10 items-center">
             {(mainTab !== '全景架构' && mainTab !== '演进脉络') ? (
               <HorizontalWheelSelector 
                  items={CATEGORY_MAP[mainTab as TopLevelGroup]}
                  selectedItem={activeCategory as string}
                  onSelect={(item) => setCategory(item as Category)}
               />
             ) : mainTab === '演进脉络' ? (
               <div className="flex items-center text-[13px] font-[600] text-zinc-400 tracking-wide whitespace-nowrap">
                 {t('title.timeline')}
               </div>
             ) : (
                <div className="flex items-center text-[13px] font-[600] text-zinc-400 tracking-wide whitespace-nowrap">
                 {t('title.main')}
               </div>
             )}
           </div>
        </header>

        {/* Main Workspace */}
        <div className="flex-1 flex justify-center items-start w-full max-w-[1600px] mx-auto px-6 overflow-hidden pt-8 pb-10">
          <AnimatePresence mode="wait">
            {mainTab === '全景架构' ? (
               <motion.div
                 key="overview"
                 initial={{ opacity: 0, y: 20 }}
                 animate={{ opacity: 1, y: 0 }}
                 exit={{ opacity: 0, y: -20 }}
                 transition={{ duration: 0.4 }}
                 className="w-full h-full flex items-center justify-center pt-8"
               >
                 <SystemOverview onSelectCategory={setCategory} />
               </motion.div>
            ) : mainTab === '演进脉络' ? (
               <motion.div
                 key="timeline"
                 initial={{ opacity: 0, y: 20 }}
                 animate={{ opacity: 1, y: 0 }}
                 exit={{ opacity: 0, y: -20 }}
                 transition={{ duration: 0.4 }}
                 className="w-full h-full flex items-start justify-center pt-4"
               >
                 <TimelineView 
                   onNavigateToEntity={handleNavigateToEntity} 
                   mockData={mockData} 
                   focusEntityId={timelineFocusId}
                   onClearFocus={() => setTimelineFocusId(null)}
                 />
               </motion.div>
            ) : (
               <motion.div
                 key="wheels"
                 initial={{ opacity: 0 }}
                 animate={{ opacity: 1 }}
                 exit={{ opacity: 0 }}
                 className="flex-1 flex justify-center items-start w-full h-full relative py-8"
               >
                 {/* Left Wheel Context */}
                 <div className="flex-[0.8] flex items-start pt-[60px] justify-end pr-8">
                   <WheelSelector items={list} selectedId={leftId} onSelect={setLeftId} align="left" />
                 </div>

                 {/* Primary Context */}
                 <motion.div layout className="flex shrink-0 items-start justify-center gap-10 pt-[20px]">
                    <EntityCard data={leftCardData} align="left" size={isComparing ? 'normal' : 'large'} emptyText={t('empty.card')} />
                    
                    <AnimatePresence mode="popLayout">
                      {!isComparing && leftEntity && (
                        <motion.div
                          key="single-specs"
                          initial={{ opacity: 0, scale: 0.9, width: 0 }} 
                          animate={{ opacity: 1, scale: 1, width: 'auto' }} 
                          exit={{ opacity: 0, scale: 0.9, width: 0 }}
                          transition={{ type: 'spring', bounce: 0.2, duration: 0.8 }}
                          className="overflow-hidden"
                        >
                          <SingleSpecsPanel 
                            entity={leftEntity} 
                            mockData={mockData} 
                            onFindRelated={() => setMainTab('全景架构')} 
                            onNavigateToEntity={handleNavigateToEntity} 
                            onViewEvolution={() => {
                              setTimelineFocusId(leftEntity.id);
                              setMainTab('演进脉络');
                            }}
                          />
                        </motion.div>
                      )}

                      {isComparing && (
                        <motion.div 
                          key="specs"
                          initial={{ opacity: 0, scale: 0.9, width: 0 }} 
                          animate={{ opacity: 1, scale: 1, width: 'auto' }} 
                          exit={{ opacity: 0, scale: 0.9, width: 0 }}
                          transition={{ type: 'spring', bounce: 0.2, duration: 0.8 }}
                          className="overflow-hidden"
                        >
                          <div className="min-w-[240px]">
                            <SpecsColumn left={leftEntity} right={rightEntity} />
                          </div>
                        </motion.div>
                      )}
                      
                      {isComparing && (
                        <motion.div 
                          key="right-card"
                          initial={{ opacity: 0, x: 20 }} 
                          animate={{ opacity: 1, x: 0 }} 
                          exit={{ opacity: 0, x: 20 }}
                          transition={{ type: 'spring', bounce: 0.2, duration: 0.8 }}
                        >
                           <EntityCard data={rightCardData} align="right" onRemove={() => setIsComparing(false)} size="normal" emptyText={t('empty.compare')} />
                        </motion.div>
                      )}
                    </AnimatePresence>
                 </motion.div>

                 {/* Right Wheel Context */}
                 <div className="flex-[0.8] flex items-start pt-[60px] justify-start pl-8 relative">
                   <AnimatePresence mode="popLayout">
                     {isComparing ? (
                       <motion.div
                         key="right-wheel"
                         initial={{ opacity: 0, x: 20 }}
                         animate={{ opacity: 1, x: 0 }}
                         exit={{ opacity: 0, x: 20 }}
                         transition={{ duration: 0.3 }}
                       >
                         <WheelSelector items={list} selectedId={rightId} onSelect={setRightId} align="right" />
                       </motion.div>
                     ) : (
                       <motion.div
                         key="compare-btn"
                         initial={{ opacity: 0, scale: 0.8 }}
                         animate={{ opacity: 1, scale: 1 }}
                         exit={{ opacity: 0, scale: 0.8 }}
                         transition={{ duration: 0.3 }}
                         className="absolute left-10 flex flex-col items-center gap-3 mt-10"
                       >
                         <button 
                           onClick={handleStartCompare}
                           className="w-12 h-12 flex flex-col items-center justify-center rounded-full bg-zinc-100 text-zinc-500 hover:text-zinc-700 hover:bg-zinc-200 transition-colors focus:ring-2 focus:ring-zinc-200 focus:outline-none shadow-sm"
                         >
                           <Plus className="w-5 h-5" />
                         </button>
                         <span className="text-[12px] font-[500] text-zinc-400">{t('btn.compare')}</span>
                       </motion.div>
                     )}
                   </AnimatePresence>
                 </div>
               </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Footer */}
        <footer className="h-[40px] px-10 flex items-center justify-between shrink-0 text-[11px] font-[500] text-zinc-400 tracking-wide border-t border-zinc-100/50 bg-white z-50">
           <div>Roy Jad © 2026</div>
           <a href="https://github.com/google/gemini" target="_blank" rel="noreferrer" className="hover:text-zinc-800 transition-colors">Powered by system engineering</a>
        </footer>
      </div>
      
      <GridView 
        isOpen={showGridView} 
        onClose={() => setShowGridView(false)} 
        items={list} 
        onSelect={(id) => {
          setLeftId(id);
          setIsComparing(false);
          setRightId(null);
        }} 
        title={t(activeCategory as string) || activeCategory as string}
      />
      <ContactModal isOpen={contactOpen} onClose={() => setContactOpen(false)} />
      <SubmitModal isOpen={submitOpen} onClose={() => setSubmitOpen(false)} />
    </div>
  );
}
