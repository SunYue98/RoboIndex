import React from 'react';
import { Entity, PaperInfo, OrgInfo, Source, FundingRound, PortfolioInvestment } from '../data/entities';
import { ArrowUpRight } from 'lucide-react';
import { useLang } from '../i18n';

export function PaperInfoBlock({ paperInfo, name }: { paperInfo?: PaperInfo, name: string }) {
  if (!paperInfo) return null;
  return (
    <div className="mb-6 flex flex-col gap-2">
      <h4 className="text-[14px] font-bold text-zinc-900 leading-snug">{name}</h4>
      <p className="text-[12px] font-medium text-emerald-600/80 leading-snug">{paperInfo.authors}</p>
      <p className="text-[12px] text-zinc-500 leading-relaxed mt-2 text-justify line-clamp-6 hover:line-clamp-none transition-all duration-300 cursor-pointer" title="Click to expand/collapse abstract">{paperInfo.abstract}</p>
      
      <div className="flex gap-2 mt-3">
        {paperInfo.arxivUrl && (
          <a href={paperInfo.arxivUrl} target="_blank" rel="noreferrer" className="px-3 py-1.5 rounded-full bg-red-50 text-red-600 hover:bg-red-100 text-[11px] font-bold tracking-wide transition-colors">
            arXiv
          </a>
        )}
        {paperInfo.codeUrl && (
          <a href={paperInfo.codeUrl} target="_blank" rel="noreferrer" className="px-3 py-1.5 rounded-full bg-zinc-100 text-zinc-700 hover:bg-zinc-200 text-[11px] font-bold tracking-wide transition-colors">
            Code
          </a>
        )}
        {paperInfo.projectUrl && (
          <a href={paperInfo.projectUrl} target="_blank" rel="noreferrer" className="px-3 py-1.5 rounded-full bg-blue-50 text-blue-600 hover:bg-blue-100 text-[11px] font-bold tracking-wide transition-colors">
            Project
          </a>
        )}
      </div>
    </div>
  );
}

export function OrgInfoBlock({ orgInfo, name }: { orgInfo?: OrgInfo, name: string }) {
  if (!orgInfo) return null;
  return (
    <div className="mb-6 flex flex-col gap-3">
      <h4 className="text-[14px] font-bold text-zinc-900 leading-snug">{name}</h4>
      {orgInfo.description && (
        <p className="text-[12px] text-zinc-500 leading-relaxed text-justify">{orgInfo.description}</p>
      )}
      
      {orgInfo.location && (
        <div className="flex items-center gap-2 mt-1">
          <span className="text-[11px] font-[600] text-zinc-400 uppercase tracking-widest leading-none">Location</span>
          <span className="text-[12px] font-[500] text-zinc-700 leading-none">{orgInfo.location}</span>
        </div>
      )}
      
      <div className="flex gap-2 mt-2">
        {orgInfo.website && (
          <a href={orgInfo.website} target="_blank" rel="noreferrer" className="px-3 py-1.5 rounded-full bg-zinc-100 text-zinc-700 hover:bg-zinc-200 text-[11px] font-bold tracking-wide transition-colors flex items-center gap-1">
            Website <ArrowUpRight className="w-3 h-3" />
          </a>
        )}
      </div>
    </div>
  );
}

export function SpecsList({ specs }: { specs?: Record<string, any> }) {
  if (!specs || Object.keys(specs).length === 0) return null;
  
  const formatLabel = (key: string) => key.charAt(0).toUpperCase() + key.slice(1);

  return (
    <div className="flex flex-col border-b border-zinc-100 pb-4 mb-4">
      {Object.entries(specs).map(([key, val]) => (
         <div className="flex items-center w-full justify-between py-[12px]" key={key}>
           <div className="w-[80px] text-left text-[12px] font-[500] text-zinc-400 shrink-0">
             {formatLabel(key)}
           </div>
           <div className="flex-1 text-left text-[14px] font-[500] text-zinc-600 line-clamp-2">
             {Array.isArray(val) ? val.join(', ') : (val || '—')}
           </div>
         </div>
      ))}
    </div>
  );
}

export function TagsList({ tags }: { tags?: string[] }) {
  if (!tags || tags.length === 0) return null;
  return (
    <div className="flex flex-wrap gap-2 mb-2">
      {tags.map(tag => (
        <span key={tag} className="px-3 py-1.5 rounded-full border border-zinc-200 text-[12px] font-[500] text-zinc-500 tracking-tight">
          {tag}
        </span>
      ))}
    </div>
  );
}

export function SeriesChain({
  entity,
  allEntries,
  onNavigateToEntity,
}: {
  entity: Entity;
  allEntries: Entity[];
  onNavigateToEntity?: (id: string) => void;
}) {
  const { t } = useLang();
  if (!entity.seriesId) return null;

  // Find sibling members of the same series, sort by seriesOrder
  const members = allEntries
    .filter(e => e.seriesId === entity.seriesId)
    .sort((a, b) => (a.seriesOrder ?? 0) - (b.seriesOrder ?? 0));

  if (members.length < 2) return null; // single-member series — no chain to show

  return (
    <div className="flex flex-col gap-2 mb-5 pb-4 border-b border-zinc-100">
      <h4 className="text-[11px] font-bold text-zinc-400 uppercase tracking-widest mb-1">
        {t('panel.series')}
      </h4>
      <div className="flex flex-wrap gap-1.5 items-center">
        {members.map((m, idx) => {
          const isCurrent = m.id === entity.id;
          const label = m.seriesLabel || m.name;
          return (
            <React.Fragment key={m.id}>
              {idx > 0 && (
                <span className="text-zinc-300 text-[10px] select-none">→</span>
              )}
              <button
                onClick={() => !isCurrent && onNavigateToEntity?.(m.id)}
                disabled={isCurrent}
                title={`${m.name} (${m.category})`}
                className={
                  isCurrent
                    ? 'px-2.5 py-1 rounded-[8px] bg-zinc-900 text-white text-[11px] font-bold cursor-default'
                    : 'px-2.5 py-1 rounded-[8px] bg-zinc-50 border border-zinc-200 text-[11px] font-[500] text-zinc-600 hover:bg-white hover:border-zinc-300 hover:text-zinc-900 transition-colors'
                }
              >
                {label}
              </button>
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
}

/**
 * FundingBlock — renders either:
 *   - 投资人 view (entity is a company): list each funding round, its investors,
 *     and the source URL.
 *   - 投资组合 view (entity is a VC): list each investment this VC made, the
 *     company invested in, round details, and the source URL.
 *
 * Every row has a clickable source link (icon-only on the right) — that's the
 * fact-check entry point. Investor / company names that link to entities in
 * our DB become clickable buttons; otherwise plain text.
 */
export function FundingBlock({
  rounds,
  portfolio,
  allEntries,
  onNavigateToEntity,
}: {
  rounds?: FundingRound[];
  portfolio?: PortfolioInvestment[];
  allEntries: Entity[];
  onNavigateToEntity?: (id: string) => void;
}) {
  const { t } = useLang();
  if ((!rounds || rounds.length === 0) && (!portfolio || portfolio.length === 0)) return null;

  // 投资组合 view (for VCs)
  if (portfolio && portfolio.length > 0) {
    const sorted = [...portfolio].sort((a, b) => (b.year || '').localeCompare(a.year || ''));
    return (
      <div className="flex flex-col gap-2 mt-4 pt-4 border-t border-zinc-100">
        <h4 className="text-[11px] font-bold text-zinc-400 uppercase tracking-widest mb-1">
          {t('panel.portfolio')}
        </h4>
        <div className="flex flex-col gap-1.5">
          {sorted.map((inv, i) => (
            <div
              key={`${inv.companyId}-${inv.round || ''}-${i}`}
              className="flex items-center justify-between gap-2 px-3 py-2 rounded-[10px] bg-zinc-50 border border-zinc-100"
            >
              <div className="flex items-center gap-2 min-w-0 flex-1">
                <button
                  onClick={() => onNavigateToEntity?.(inv.companyId)}
                  className="text-[12px] font-bold text-zinc-700 hover:text-zinc-900 hover:underline truncate"
                  title={inv.companyName}
                >
                  {inv.companyName}
                </button>
                {inv.leadInvestor && (
                  <span className="shrink-0 px-1.5 py-0.5 rounded-[4px] bg-amber-100 text-amber-700 text-[9px] font-bold tracking-wider uppercase">
                    {t('panel.lead_investor')}
                  </span>
                )}
                <span className="text-[11px] text-zinc-400 truncate">
                  {[inv.round, inv.year, inv.amount].filter(Boolean).join(' · ')}
                </span>
              </div>
              <a
                href={inv.source.url}
                target="_blank"
                rel="noopener noreferrer"
                title={inv.source.title}
                className="shrink-0 text-zinc-400 hover:text-zinc-700"
              >
                <ArrowUpRight className="w-3.5 h-3.5" />
              </a>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // 投资人 view (for companies)
  if (rounds && rounds.length > 0) {
    const sorted = [...rounds].sort((a, b) => (b.year || '').localeCompare(a.year || ''));
    return (
      <div className="flex flex-col gap-2 mt-4 pt-4 border-t border-zinc-100">
        <h4 className="text-[11px] font-bold text-zinc-400 uppercase tracking-widest mb-1">
          {t('panel.investors')}
        </h4>
        <div className="flex flex-col gap-2">
          {sorted.map((round, idx) => {
            const headerLine = [round.round, round.year, round.amount].filter(Boolean).join(' · ');
            return (
              <div
                key={`${round.round || ''}-${round.year || ''}-${idx}`}
                className="px-3 py-2 rounded-[10px] bg-zinc-50 border border-zinc-100"
              >
                <div className="flex items-center justify-between gap-2 mb-1.5">
                  <div className="text-[11px] font-bold text-zinc-700 tracking-tight">
                    {headerLine || '(round)'}
                    {round.valuation && (
                      <span className="ml-1.5 text-[10px] font-[500] text-zinc-400">
                        @ {round.valuation}
                      </span>
                    )}
                  </div>
                  <a
                    href={round.source.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    title={round.source.title}
                    className="shrink-0 text-zinc-400 hover:text-zinc-700"
                  >
                    <ArrowUpRight className="w-3.5 h-3.5" />
                  </a>
                </div>
                <div className="flex flex-wrap gap-1">
                  {round.investors.map((inv, j) => {
                    const isLead = round.leadInvestor && round.leadInvestor === inv.name;
                    const cls = isLead
                      ? 'px-1.5 py-0.5 rounded-[4px] bg-amber-100 text-amber-800 text-[10px] font-bold'
                      : 'px-1.5 py-0.5 rounded-[4px] bg-white border border-zinc-200 text-[10px] font-[500] text-zinc-600';
                    return inv.id ? (
                      <button
                        key={`${inv.name}-${j}`}
                        onClick={() => onNavigateToEntity?.(inv.id!)}
                        className={cls + ' hover:border-zinc-400 hover:text-zinc-900 transition-colors'}
                        title={inv.name}
                      >
                        {inv.name}
                      </button>
                    ) : (
                      <span key={`${inv.name}-${j}`} className={cls}>
                        {inv.name}
                      </span>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  }

  return null;
}

export function SourcesBlock({ sources }: { sources?: Source[] }) {
  const { t } = useLang();
  const hasSources = sources && sources.length > 0;

  return (
    <div className="flex flex-col gap-2 mt-4 pt-4 border-t border-zinc-100">
      <h4 className="text-[11px] font-bold text-zinc-400 uppercase tracking-widest mb-1">
        {t('panel.sources')}
      </h4>
      {hasSources ? (
        <div className="flex flex-col gap-1.5">
          {sources!.map((s, i) => (
            <a
              key={`${s.url}-${i}`}
              href={s.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center justify-between gap-2 px-3 py-2 rounded-[10px] bg-zinc-50 border border-zinc-100 hover:bg-white hover:border-zinc-300 hover:shadow-sm transition-all group"
              title={s.url}
            >
              <div className="flex items-center gap-2 min-w-0 flex-1">
                {s.type && (
                  <span className="shrink-0 px-1.5 py-0.5 rounded-[4px] bg-zinc-200/70 text-[9px] font-bold tracking-wider text-zinc-600 uppercase">
                    {t(`panel.source_type.${s.type}`) || s.type}
                  </span>
                )}
                <span className="text-[12px] font-[500] text-zinc-700 group-hover:text-zinc-900 line-clamp-1 min-w-0">
                  {s.title}
                </span>
              </div>
              <ArrowUpRight className="w-3.5 h-3.5 text-zinc-400 group-hover:text-zinc-700 shrink-0" />
            </a>
          ))}
        </div>
      ) : (
        <div className="px-3 py-2 rounded-[10px] bg-amber-50/50 border border-amber-200/40 text-[11px] font-[500] text-amber-700/80">
          {t('panel.no_sources')}
        </div>
      )}
    </div>
  );
}

export function RelatedLinksList({
  relatedEntities, 
  onNavigateToEntity 
}: { 
  relatedEntities?: Entity[], 
  onNavigateToEntity?: (id: string) => void 
}) {
  const { t } = useLang();
  
  if (!relatedEntities || relatedEntities.length === 0) return null;
  
  return (
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
  );
}
