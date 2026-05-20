export type TopLevelGroup = '硬件' | '软件' | '生态与应用' | '参与实体';

export type Category = 
  | '整机平台' | '机械臂' | '灵巧手 & 夹爪'
  | '关节模组' | '核心零部件' | '传感器' | '能源动力'
  | '数采 & 遥操' | '计算平台'
  | '基础模型' | '算法框架' | '控制算法' | '仿真平台' | '数据集' | '评测基准'
  | '开发生态' | '应用场景'
  | '资本' | '产业' | '实验室';

export const CATEGORY_MAP: Record<TopLevelGroup, Category[]> = {
  '硬件': ['整机平台', '机械臂', '灵巧手 & 夹爪', '关节模组', '核心零部件', '传感器', '能源动力', '数采 & 遥操', '计算平台'],
  '软件': ['基础模型', '算法框架', '控制算法', '仿真平台', '数据集', '评测基准'],
  '生态与应用': ['开发生态', '应用场景'],
  '参与实体': ['资本', '产业', '实验室']
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
  relatedIds?: string[];
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

export const entityImageInfo = (entity: Pick<Entity, 'id' | 'imageUrl'>): { url: string; isPlaceholder: boolean } => {
  if (entity.imageUrl) return { url: entity.imageUrl, isPlaceholder: false };
  return { url: `images/_synthetic/${entity.id}.png`, isPlaceholder: true };
};

