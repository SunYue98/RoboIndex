import { ArrowUpRight, History } from 'lucide-react';
import { Entity } from '../data/entities';
import { motion } from 'motion/react';
import { useLang } from '../i18n';
import { PaperInfoBlock, OrgInfoBlock, SpecsList, TagsList, RelatedLinksList, SourcesBlock, SeriesChain, FundingBlock } from './EntityDetailBlocks';

interface SingleSpecsPanelProps {
  entity: Entity;
  mockData: Entity[];
  onNavigateToEntity?: (entityId: string) => void;
  onViewEvolution?: () => void;
}

export function SingleSpecsPanel({ entity, mockData, onNavigateToEntity, onViewEvolution }: SingleSpecsPanelProps) {
  const { t } = useLang();

  return (
    <motion.div 
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      transition={{ duration: 0.5, type: 'spring', bounce: 0.2 }}
      className={`flex flex-col ml-8 h-[600px] overflow-y-auto no-scrollbar pt-12 ${entity.paperInfo || entity.orgInfo ? 'w-[320px] pr-2' : 'w-[240px]'}`}
    >
      <div className="flex flex-col mb-4">
        <SeriesChain entity={entity} allEntries={mockData} onNavigateToEntity={onNavigateToEntity} />
        {entity.paperInfo && <PaperInfoBlock paperInfo={entity.paperInfo} name={entity.name} />}
        {entity.orgInfo && <OrgInfoBlock orgInfo={entity.orgInfo} name={entity.name} />}
        
        <div className="flex flex-col gap-3 mb-6">
          {onViewEvolution && (
            <button 
              onClick={onViewEvolution}
              className="flex items-center w-full px-4 py-3 bg-amber-50 border border-amber-200/50 justify-center rounded-[16px] text-[13px] font-bold tracking-tight text-amber-700 hover:border-amber-300 hover:bg-amber-100 transition-all focus:outline-none focus:ring-2 focus:ring-amber-200 group"
            >
              <div className="flex items-center gap-2">
                <History className="w-4 h-4" />
                <span>{t('panel.evolution_timeline') || '追踪演进脉络'}</span>
              </div>
            </button>
          )}
          
          {entity.websiteUrl && (
            <a
              href={entity.websiteUrl}
              target="_blank"
              rel="noreferrer"
              className="flex items-center justify-between w-full px-4 py-3 bg-zinc-900 border border-zinc-900 rounded-full text-[13px] font-[500] tracking-tight text-white hover:bg-zinc-800 transition-all focus:outline-none focus:ring-2 focus:ring-zinc-900 group"
            >
              <span>{t('panel.visit')}</span>
              <div className="w-6 h-6 rounded-full bg-white/20 flex items-center justify-center text-white group-hover:bg-white/30 transition-colors">
                <ArrowUpRight className="w-3 h-3" />
              </div>
            </a>
          )}
        </div>

        <SpecsList specs={entity.specs} sourcedSpecs={entity.sourcedSpecs} category={entity.category} />
      </div>

      <div className="flex flex-col gap-3 mb-auto">
        <TagsList tags={entity.tags} />
        <FundingBlock
          rounds={entity.fundingRounds}
          portfolio={entity.portfolio}
          allEntries={mockData}
          onNavigateToEntity={onNavigateToEntity}
        />
        <RelatedLinksList entity={entity} mockData={mockData} onNavigateToEntity={onNavigateToEntity} />
        <SourcesBlock sources={entity.sources} />
      </div>
    </motion.div>
  );
}
