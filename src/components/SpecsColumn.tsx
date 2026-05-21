import { Link2, Link as LinkIcon } from 'lucide-react';
import { Entity, Claim } from '../data/entities';
import { CATEGORY_CLAIM_SCHEMA, ClaimKeySpec } from '../data/categoryClaimSchema';
import { useLang } from '../i18n';

interface SpecsColumnProps {
  left?: Entity | null;
  right?: Entity | null;
}

function normalizeKey(s: string): string {
  return s.toLowerCase().replace(/[\s\-_/&（）()]/g, '');
}

function formatClaimValue(val: any, spec: ClaimKeySpec): string {
  if (val === null || val === undefined || val === '') return '—';
  if (typeof val === 'number') {
    const s = Number.isInteger(val) ? String(val) : val.toFixed(2).replace(/\.?0+$/, '');
    return spec.unit ? `${s} ${spec.unit}` : s;
  }
  const s = String(val);
  return spec.unit && !s.toLowerCase().endsWith(spec.unit.toLowerCase())
    ? `${s} ${spec.unit}`
    : s;
}

function formatLabel(key: string) {
  return key.charAt(0).toUpperCase() + key.slice(1);
}

export function SpecsColumn({ left, right }: SpecsColumnProps) {
  const { t } = useLang();

  // Pick the schema. If both sides share a category, use it; otherwise prefer
  // left's. (Cross-category comparison is rare in practice.)
  const category = left?.category || right?.category;
  const schema = (category && CATEGORY_CLAIM_SCHEMA[category as keyof typeof CATEGORY_CLAIM_SCHEMA]) || [];
  const aliasToCanon = new Map<string, string>();
  for (const spec of schema) {
    aliasToCanon.set(normalizeKey(spec.key), spec.key);
    for (const a of spec.aliases) aliasToCanon.set(normalizeKey(a), spec.key);
  }

  // === Build typed-claim rows in schema order ===
  type TypedRow = { spec: ClaimKeySpec; leftClaim?: Claim; rightClaim?: Claim };
  const typedRows: TypedRow[] = [];
  for (const spec of schema) {
    const leftClaim = left?.sourcedSpecs?.[spec.key];
    const rightClaim = right?.sourcedSpecs?.[spec.key];
    if (leftClaim || rightClaim) typedRows.push({ spec, leftClaim, rightClaim });
  }

  // === Build legacy-spec rows for keys NOT covered by typed schema ===
  const legacyKeys = new Set<string>();
  for (const e of [left, right]) {
    if (!e?.specs) continue;
    for (const k of Object.keys(e.specs)) {
      const canon = aliasToCanon.get(normalizeKey(k));
      if (canon && (left?.sourcedSpecs?.[canon] || right?.sourcedSpecs?.[canon])) continue;
      legacyKeys.add(k);
    }
  }
  const legacyKeyArr = Array.from(legacyKeys);

  // === Header rows: year + company (always show; help orient the compare) ===
  type HeaderRow = { label: string; leftVal: string; rightVal: string };
  const headerRows: HeaderRow[] = [];
  if (left?.year || right?.year) {
    headerRows.push({ label: 'Year', leftVal: left?.year || '—', rightVal: right?.year || '—' });
  }
  const leftCo = left?.company, rightCo = right?.company;
  if ((leftCo && leftCo !== left?.name) || (rightCo && rightCo !== right?.name)) {
    headerRows.push({
      label: 'Company',
      leftVal: leftCo || '—',
      rightVal: rightCo || '—',
    });
  }

  const totalRows = headerRows.length + typedRows.length + legacyKeyArr.length;

  // === Row renderer ===
  const renderHeader = (row: HeaderRow) => (
    <div className="flex items-center w-[240px] justify-between py-[10px]" key={`h-${row.label}`}>
      <div className="flex-1 text-left text-[14px] font-[500] text-zinc-600 line-clamp-1 tracking-tight">
        {row.leftVal}
      </div>
      <div className="w-[80px] text-center text-[10px] font-[600] text-zinc-400 uppercase tracking-[0.08em] shrink-0">
        {row.label}
      </div>
      <div className="flex-1 text-right text-[14px] font-[500] text-zinc-600 line-clamp-1 tracking-tight">
        {row.rightVal}
      </div>
    </div>
  );

  const renderTyped = (row: TypedRow) => {
    const leftStr = row.leftClaim ? formatClaimValue(row.leftClaim.value, row.spec) : '—';
    const rightStr = row.rightClaim ? formatClaimValue(row.rightClaim.value, row.spec) : '—';
    return (
      <div className="flex items-center w-[240px] justify-between py-[12px]" key={`t-${row.spec.key}`}>
        <div className="flex-1 text-left text-[14px] font-[500] text-zinc-700 flex items-center gap-1 tracking-tight">
          <span className="line-clamp-1">{leftStr}</span>
          {row.leftClaim?.source?.url && (
            <a
              href={row.leftClaim.source.url}
              target="_blank"
              rel="noreferrer"
              title={row.leftClaim.source.title}
              className="inline-flex w-3.5 h-3.5 items-center justify-center text-zinc-300 hover:text-zinc-600 transition-colors"
              aria-label="Left source"
            >
              <LinkIcon className="w-3 h-3" />
            </a>
          )}
        </div>
        <div className="w-[80px] text-center text-[11px] font-[600] text-zinc-500 tracking-tight shrink-0">
          {row.spec.label}
        </div>
        <div className="flex-1 text-right text-[14px] font-[500] text-zinc-700 flex items-center justify-end gap-1 tracking-tight">
          {row.rightClaim?.source?.url && (
            <a
              href={row.rightClaim.source.url}
              target="_blank"
              rel="noreferrer"
              title={row.rightClaim.source.title}
              className="inline-flex w-3.5 h-3.5 items-center justify-center text-zinc-300 hover:text-zinc-600 transition-colors"
              aria-label="Right source"
            >
              <LinkIcon className="w-3 h-3" />
            </a>
          )}
          <span className="line-clamp-1">{rightStr}</span>
        </div>
      </div>
    );
  };

  const renderLegacy = (key: string) => {
    const leftVal = left?.specs?.[key];
    const rightVal = right?.specs?.[key];
    const showDot = key === 'status';
    const leftStr = Array.isArray(leftVal) ? leftVal.join(', ') : (leftVal || '—');
    const rightStr = Array.isArray(rightVal) ? rightVal.join(', ') : (rightVal || '—');
    return (
      <div className="flex items-center w-[240px] justify-between py-[12px]" key={`l-${key}`}>
        <div className="flex-1 text-left text-[14px] font-[500] text-zinc-600 flex items-center gap-2 tracking-tight">
          {showDot && leftVal === 'In Production' && <div className="w-1.5 h-1.5 rounded-full bg-emerald-500" />}
          <span className="line-clamp-1">{leftStr}</span>
        </div>
        <div className="w-[80px] text-center text-[11px] font-[500] text-zinc-400 uppercase tracking-[0.08em] shrink-0">
          {formatLabel(key)}
        </div>
        <div className="flex-1 text-right text-[14px] font-[500] text-zinc-600 flex items-center justify-end gap-2 tracking-tight">
          <span className="line-clamp-1">{rightStr}</span>
          {showDot && rightVal === 'In Production' && <div className="w-1.5 h-1.5 rounded-full bg-emerald-500" />}
        </div>
      </div>
    );
  };

  return (
    <div className="flex flex-col mt-12 px-4">
      {headerRows.map(renderHeader)}
      {(headerRows.length > 0 && (typedRows.length > 0 || legacyKeyArr.length > 0)) && (
        <div className="h-px bg-zinc-100 my-2" />
      )}
      {typedRows.map(renderTyped)}
      {(typedRows.length > 0 && legacyKeyArr.length > 0) && (
        <div className="h-px bg-zinc-100 my-2" />
      )}
      {legacyKeyArr.map(renderLegacy)}

      {totalRows === 0 && (
        <div className="w-[240px] py-8 text-center text-[12px] font-medium text-zinc-400">
          {t('panel.no_compare') || '此两条目暂无可对比的字段'}
        </div>
      )}

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
