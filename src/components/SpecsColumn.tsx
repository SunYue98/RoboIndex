import { Link2 } from 'lucide-react';
import { Entity } from '../data/entities';
import { useLang } from '../i18n';

interface SpecsColumnProps {
  left?: Entity | null;
  right?: Entity | null;
}

export function SpecsColumn({ left, right }: SpecsColumnProps) {
  const { t } = useLang();
  // Get all unique spec keys from both left and right entities
  const allKeys = new Set<string>();
  if (left?.specs) Object.keys(left.specs).forEach(k => allKeys.add(k));
  if (right?.specs) Object.keys(right.specs).forEach(k => allKeys.add(k));
  
  const specKeys = Array.from(allKeys);

  const formatLabel = (key: string) => {
    return key.charAt(0).toUpperCase() + key.slice(1);
  };

  const renderRow = (key: string) => {
    const leftVal = left?.specs[key];
    const rightVal = right?.specs[key];
    const showDot = key === 'status'; // Add green dot for status

    return (
      <div className="flex items-center w-[240px] justify-between py-[12px]" key={key}>
        <div className="flex-1 text-left text-[14px] font-[500] text-zinc-600 flex items-center gap-2 tracking-tight">
          {showDot && leftVal === 'In Production' && <div className="w-1.5 h-1.5 rounded-full bg-emerald-500" />}
          <span className="line-clamp-1">{leftVal || '—'}</span>
        </div>
        <div className="w-[80px] text-center text-[11px] font-[500] text-zinc-400 uppercase tracking-[0.08em] shrink-0">
          {formatLabel(key)}
        </div>
        <div className="flex-1 text-right text-[14px] font-[500] text-zinc-600 flex items-center justify-end gap-2 tracking-tight">
          <span className="line-clamp-1">{rightVal || '—'}</span>
          {showDot && rightVal === 'In Production' && <div className="w-1.5 h-1.5 rounded-full bg-emerald-500" />}
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col mt-20 px-4">
       {/* List of Specs */}
       {specKeys.map(key => renderRow(key))}

       {/* Copy Action */}
       <div className="mt-[60px] flex justify-center">
         <button className="flex items-center gap-3 pl-4 pr-1 py-1 bg-white border border-zinc-200 rounded-full text-[13px] font-[500] tracking-tight text-zinc-600 hover:border-zinc-300 hover:bg-zinc-50 hover:shadow-sm transition-all focus:outline-none focus:ring-2 focus:ring-zinc-200">
           {t('panel.copy')}
           <div className="w-7 h-7 rounded-full bg-zinc-100 flex items-center justify-center text-zinc-500">
             <Link2 className="w-3.5 h-3.5" />
           </div>
         </button>
       </div>
    </div>
  );
}
