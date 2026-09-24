export type Question = {
  id: string;
  text: string;
  type?: "single_choice" | "multi_select" | "likert";
  options?: { v: string; l: string }[];
  max?: number;
};

export type TopSignal = {
  key: string;
  score: number;
  confidence: number;
};

export type Barrier = {
  type: string;
  level: "hard" | "soft";
  path?: string;
};

export type CareerItem = {
  career_id: string;
  career_uz: string;
  cluster_uz: string;
  fit: number;
  readiness: number;
  coverage: number;
  learning_months?: number;
  barriers: Barrier[];
  has_hard_barrier: boolean;
  has_roadmap?: boolean;
};

export type TeaserResponse = {
  stage1_result_id: number;
  top_2_signals: TopSignal[];
  top_2_careers: CareerItem[];
  locked_count: number;
  confidence: string;
};

export type AIExplanation = {
  source: "ai" | "fallback";
  summary: string;
  why_this_fits: string[];
  risks: string[];
  next_step_emphasis: string;
};

export type RoadmapItem = {
  career_id: string;
  career_uz: string;
  why_this_path: string;
  gaps: string[];
  phases: { period: string; goal: string; actions: string[] }[];
  first_3_actions: string[];
  barrier_resolutions: { barrier_type: string; level: string; action: string }[];
  milestones: string[];
  risks: string[];
  resources: { name: string; url: string }[];
  projects: string[];
  is_placeholder?: boolean;
};

export type ReportCareer = {
  career: {
    id: string;
    uz: string;
    cluster: string;
    cluster_uz: string;
    pathway_type?: string;
    learning_months?: number;
  };
  fit: number;
  readiness: number;
  coverage: number;
  barriers: Barrier[];
  has_hard_barrier: boolean;
  roadmap: RoadmapItem;
};

export type FullReport = {
  id: number;
  stage: string;
  profile: any;
  roadmap: { careers: ReportCareer[] };
  ai: AIExplanation | null;
  versions: Record<string, string>;
  created_at: string;
};


export type SalaryRange = {
  min: number;
  median: number;
  max: number;
};

export type SalaryData = {
  junior: SalaryRange;
  mid: SalaryRange;
  senior: SalaryRange;
  remote_usd: { junior: number; mid: number; senior: number };
};
