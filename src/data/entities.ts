export type TopLevelGroup = '硬件' | '软件' | '生态与应用' | '参与实体';

export type Category =
  | '整机平台' | '机械臂' | '灵巧手 & 夹爪'
  | '关节模组' | '核心零部件' | '传感器' | '能源动力'
  | '数采 & 遥操' | '计算平台'
  | '基础模型' | '算法框架' | '控制算法' | '仿真平台' | '数据集' | '评测基准'
  | '开发生态' | '应用场景'
  | '资本' | '产业' | '实验室' | '人物';

export const CATEGORY_MAP: Record<TopLevelGroup, Category[]> = {
  '硬件': ['整机平台', '机械臂', '灵巧手 & 夹爪', '关节模组', '核心零部件', '传感器', '能源动力', '数采 & 遥操', '计算平台'],
  '软件': ['基础模型', '算法框架', '控制算法', '仿真平台', '数据集', '评测基准'],
  '生态与应用': ['开发生态', '应用场景'],
  '参与实体': ['资本', '产业', '实验室', '人物']
};

export const TOP_LEVEL_GROUPS = Object.keys(CATEGORY_MAP) as TopLevelGroup[];

export interface Specs {
  [key: string]: any;
}

export interface PaperInfo {
  abstract?: string;
  authors?: string;
  arxivUrl?: string;
  codeUrl?: string;
  projectUrl?: string;
}

export interface OrgInfo {
  description?: string;
  location?: string;
  website?: string;
}

export type SourceType = 'official' | 'paper' | 'wiki' | 'news' | 'datasheet';

export interface Source {
  title: string;
  url: string;
  type?: SourceType;
}

/**
 * A single claim — a value that can be sourced and dated.
 *
 * Use Claim wherever a fact in an Entity should be independently fact-checkable.
 * In Phase 3 we'll migrate the most important Specs entries to Claim form; for now
 * Claim is also the building block for any new sourced metric we add.
 *
 * Example: { value: 50_000_000_000, source: {...}, asOf: "2025-Q3", confidence: "reported" }
 */
export type ClaimValue = string | number | boolean;
export type ClaimConfidence = 'verified' | 'reported' | 'estimated';

export interface Claim<T extends ClaimValue = ClaimValue> {
  value: T;
  source?: Source;     // where the claim comes from
  asOf?: string;       // when the claim was reported / measured (ISO date, "YYYY", or "YYYY-Qx")
  confidence?: ClaimConfidence;
  notes?: string;
}

/**
 * A typed edge from this entity to another entity.
 *
 * Phase 2 will migrate the existing `relatedIds: string[]` into typed Relation[]
 * with inferred roles. Until then both fields coexist; UI prefers `relations`
 * when present and falls back to `relatedIds` for entities not yet migrated.
 *
 * Roles are intentionally limited to what we can backfill from current data;
 * person-specific roles (founder-of, employed-at, alumni-of) wait for Phase 5.
 */
export type RelationRole =
  | 'manufacturer'      // this entity is made by → targetId (e.g. Optimus → Tesla)
  | 'invested-in'       // this entity invested in → targetId (set on 资本 entities)
  | 'competitor'        // this entity competes with → targetId
  | 'customer-of'       // this entity is a customer of → targetId
  | 'supplier-to'       // this entity supplies → targetId
  | 'subsidiary-of'     // this entity is a subsidiary of → targetId
  | 'affiliated-with'   // this entity is affiliated with → targetId (lab ↔ university, etc.)
  | 'series-member'     // this entity is in the same product series as → targetId
  | 'tech-base'         // this entity is built on top of → targetId (model/framework dependency)
  | 'trained-on'        // this entity (a model) was trained on → targetId (a dataset)
  | 'deployed-at'       // this entity is deployed at → targetId (product → application scenario)
  // Person-specific roles (Phase 5)
  | 'founder-of'        // this person founded → targetId (a company / lab)
  | 'employed-at'       // this person is currently / was employed at → targetId
  | 'alumni-of'         // this person attended / graduated from → targetId (institution / lab)
  | 'advised-by'        // this person was advised by → targetId (another person)
  | 'related';          // fallback / not yet classified — to be refined in Phase 2

export interface Relation {
  targetId: string;
  role: RelationRole;
  source?: Source;     // the source of THIS relation (separate from the entity's own sources)
  asOf?: string;       // when this relation was established/observed
  notes?: string;
  /** Set when this edge was auto-derived from a reciprocal edge on the target.
   *  Helps UI distinguish authored vs derived relations. */
  isInverse?: boolean;
}

/**
 * One funding round, attached to a company (Entity in 产业 category).
 * Investors are listed as named text + optional link to our VC entity if present.
 * Every round must carry a source URL so a user can fact-check the claim.
 */
export interface FundingRound {
  round?: string;          // e.g. "Series A" / "Seed" / "IPO" / "Strategic"
  year?: string;           // "YYYY-MM" preferred, "YYYY" acceptable
  amount?: string;         // as-stated in the source, e.g. "$675M" or "RMB 1B"
  leadInvestor?: string | null;
  investors: Array<{ name: string; id?: string }>;
  valuation?: string;      // post-money valuation if explicitly stated
  source: Source;          // mandatory; users will click through to verify
}

/**
 * Mirror view from a VC's perspective: one investment by this VC into a company.
 * Derived (not authored) — built by reverse-scanning all companies' fundingRounds.
 */
export interface PortfolioInvestment {
  companyName: string;     // human-readable
  companyId: string;       // entity id (产业 category)
  round?: string;
  year?: string;
  amount?: string;         // size of the round, not the VC's specific cheque
  leadInvestor?: boolean;  // did this VC lead the round?
  source: Source;          // same source as the underlying FundingRound
}

export interface Entity {
  id: string;
  name: string;
  company: string;
  category: Category;
  imageUrl: string;
  websiteUrl?: string;
  year: string;
  isNew: boolean;
  specs: Specs;
  /** Untyped relations — legacy. Phase 2 migrates these into `relations` below. */
  relatedIds?: string[];
  /** Typed relations with explicit roles. Coexists with relatedIds during migration. */
  relations?: Relation[];
  /** Claim-shaped specs with per-field sources. Coexists with `specs` during migration. */
  sourcedSpecs?: Record<string, Claim>;
  tags?: string[];
  paperInfo?: PaperInfo;
  orgInfo?: OrgInfo;
  importance?: 'high' | 'medium' | 'low';
  sources?: Source[];
  // Evolution-chain membership. Members of the same series sort by seriesOrder
  // and render as a horizontal chain navigator in the UI (← prev · current · next →).
  seriesId?: string;
  seriesOrder?: number;
  seriesLabel?: string;
  // Funding history. fundingRounds = "who invested in me" (set on company entries).
  // portfolio = "who I invested in" (set on VC entries, derived from companies' rounds).
  // Both kinds carry mandatory per-edge source URLs for fact-checkability.
  fundingRounds?: FundingRound[];
  portfolio?: PortfolioInvestment[];
}

// Modular Data Loading Strategy
// We use a decoupled data loading strategy where an index file points to various
// module data chunks. This prevents a single data.json from becoming bloated,
// allows caching strategy per module, and supports parallel loading.

let cachedData: Entity[] | null = null;
let fetchPromise: Promise<Entity[]> | null = null;

interface DataIndex {
  partitions: {
    id: string;
    url: string;
    categories: string[];
  }[];
}

export const loadEntities = async (): Promise<Entity[]> => {
  if (cachedData) return cachedData;
  if (fetchPromise) return fetchPromise;
  
  fetchPromise = (async () => {
    try {
      // 1. Fetch the data index to discover available modules
      const indexRes = await fetch(import.meta.env.BASE_URL + 'data/index.json');
      if (!indexRes.ok) throw new Error('Failed to load data index');
      const index: DataIndex = await indexRes.json();

      // 2. Fetch all partitions in parallel
      const partitionPromises = index.partitions.map(async (partition) => {
        const res = await fetch(import.meta.env.BASE_URL + partition.url.replace(/^\//, ''));
        if (!res.ok) return [];
        return await res.json() as Entity[];
      });

      const results = await Promise.all(partitionPromises);
      
      // 3. Combine into a single entity registry
      cachedData = results.flat();
      return cachedData;
    } catch (err) {
      console.error('Data Loading Error:', err);
      return [];
    }
  })();
    
  return fetchPromise;
};

export const resolveImageUrl = (url: string): string => {
  if (url.startsWith('http')) return url;
  return import.meta.env.BASE_URL + url.replace(/^\//, '');
};

// Categories whose canonical visual is the synthetic title card (not a placeholder).
// Per IMAGE_SPEC.md prototype B — for these, the synthetic card IS the standard
// and should not show a "待补图" badge. 人物 (Phase 5) also uses synthetic cards
// because portrait sourcing has attribution complexity.
const SYNTHETIC_CANONICAL_CATEGORIES = new Set<string>([
  '基础模型', '算法框架', '控制算法', '仿真平台', '数据集', '评测基准', '开发生态', '人物',
]);

export const entityImageInfo = (entity: Pick<Entity, 'id' | 'imageUrl' | 'category'>): { url: string; isPlaceholder: boolean } => {
  if (entity.imageUrl) return { url: entity.imageUrl, isPlaceholder: false };
  const synthIsCanonical = SYNTHETIC_CANONICAL_CATEGORIES.has(entity.category as string);
  return { url: `images/_synthetic/${entity.id}.png`, isPlaceholder: !synthIsCanonical };
};

