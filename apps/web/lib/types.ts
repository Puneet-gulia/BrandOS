// Brand types
export type BrandInputType = 'url' | 'text' | 'document';

export interface BrandInput {
  input_type: BrandInputType;
  url?: string;
  text?: string;
  document_filename?: string;
  document_content?: string;
}

export interface BrandProfile {
  id: string;
  company_name: string;
  tagline?: string;
  brand_voice: string[];
  writing_style: string[];
  target_audience: string[];
  industry: string;
  keywords: string[];
  core_values: string[];
  unique_selling_proposition: string;
  tone: string;
  competitors: string[];
  raw_input_summary: string;
  created_at: string;
}

// Campaign types
// Values match the Python MarketingChannel enum (uppercase)
export type MarketingChannel =
  | 'SOCIAL_MEDIA'
  | 'EMAIL'
  | 'PAID_ADS'
  | 'LANDING_PAGE'
  | 'BLOG'
  | 'VIDEO'
  | 'PRINT';

export const MARKETING_CHANNEL_LABELS: Record<MarketingChannel, string> = {
  SOCIAL_MEDIA: 'Social Media',
  EMAIL: 'Email',
  PAID_ADS: 'Paid Ads',
  LANDING_PAGE: 'Landing Page',
  BLOG: 'Blog',
  VIDEO: 'Video',
  PRINT: 'Print',
};

export interface CampaignBrief {
  id: string;
  brand_profile_id: string;
  objective: string;
  target_audience: string[];
  channels: MarketingChannel[];
  budget_range?: string;
  timeline_weeks?: number;
  constraints: string[];
  created_at: string;
}

export interface CampaignStrategy {
  id: string;
  campaign_brief_id: string;
  campaign_name: string;
  positioning_statement: string;
  messaging_pillars: string[];
  key_themes: string[];
  channel_strategy: Record<string, string>;
  content_calendar_weeks: number;
  success_metrics: string[];
  rationale: string;
  created_at: string;
}

export interface CampaignPackage {
  id: string;
  brand_profile: BrandProfile;
  campaign_brief: CampaignBrief;
  campaign_strategy?: CampaignStrategy;
  campaign_assets?: CampaignAssets;
  quality_report?: QualityReport;
  status: 'draft' | 'in_progress' | 'complete' | 'failed';
  created_at: string;
  updated_at: string;
}

// Creative asset types
export interface SocialMediaPost {
  platform: string;
  post_type: string;
  content: string;
  hashtags: string[];
  call_to_action: string;
  notes: string;
}

export interface AdVariant {
  platform: string;
  format: string;
  headline: string;
  body: string;
  call_to_action: string;
  target_audience_note: string;
}

export interface EmailCampaign {
  name: string;
  subject_line: string;
  preview_text: string;
  body: string;
  call_to_action_text: string;
  send_timing: string;
}

export interface LandingPageCopy {
  hero_headline: string;
  hero_subheadline: string;
  hero_cta: string;
  value_propositions: string[];
  social_proof_statement: string;
  feature_sections: Array<{ title: string; body: string }>;
  faq: Array<{ question: string; answer: string }>;
  closing_headline: string;
  closing_cta: string;
}

export interface ImagePromptItem {
  use_case: string;
  platform: string;
  prompt: string;
  style: string;
  mood: string;
  aspect_ratio: string;
}

export interface CampaignAssets {
  id: string;
  campaign_strategy_id: string;
  social_media_posts: SocialMediaPost[];
  ad_copy: AdVariant[];
  email_campaigns: EmailCampaign[];
  landing_page_copy: LandingPageCopy | null;
  blog_posts: unknown[];
  image_prompts: ImagePromptItem[];
  video_storyboards: unknown[];
  poster_concepts: unknown[];
  created_at: string;
}

// API request/response types
export interface KnowledgeExtractRequest {
  input_type: BrandInputType;
  url?: string;
  text?: string;
  document_filename?: string;
  document_content?: string;
}

/** Matches CreateCampaignRequest on the Python side */
export interface CreateCampaignRequest {
  brand_profile: BrandProfile;
  objective: string;
  target_audience: string[];
  channels: MarketingChannel[];
  budget_range?: string;
  timeline_weeks?: number;
  constraints: string[];
}

/** Request body for POST /api/campaigns/run */
export interface RunCampaignRequest {
  brand_profile: BrandProfile;
  objective: string;
  target_audience: string[];
  channels: MarketingChannel[];
  budget_range?: string;
  timeline_weeks?: number;
  constraints: string[];
}

export interface APIError {
  error: string;
  message: string;
  detail?: string;
}

export interface HealthResponse {
  status: string;
  version: string;
  uptime_seconds: number;
}

// Evaluation types
export type EvaluationDimension =
  | 'BRAND_CONSISTENCY'
  | 'GRAMMAR'
  | 'COMPLETENESS'
  | 'TONE'
  | 'READABILITY'
  | 'SEO';

export const DIMENSION_LABELS: Record<EvaluationDimension, string> = {
  BRAND_CONSISTENCY: 'Brand Consistency',
  GRAMMAR: 'Grammar',
  COMPLETENESS: 'Completeness',
  TONE: 'Tone',
  READABILITY: 'Readability',
  SEO: 'SEO',
};

export const DIMENSION_DESCRIPTIONS: Record<EvaluationDimension, string> = {
  BRAND_CONSISTENCY: 'Alignment with brand voice, values, and identity',
  GRAMMAR: 'Spelling, punctuation, and sentence structure',
  COMPLETENESS: 'All requested asset types present and fully developed',
  TONE: 'Emotional register matches the brand intent',
  READABILITY: 'Clear and appropriate for the target audience',
  SEO: 'Keywords present, headlines optimised for discoverability',
};

export interface QualityScore {
  dimension: EvaluationDimension;
  score: number; // 0.0 - 1.0
  passed: boolean;
  feedback: string;
  suggestions: string[];
}

export interface QualityReport {
  id: string;
  campaign_assets_id: string;
  scores: QualityScore[];
  recommendations: string[];
  overall_score: number; // computed field from Python
  passed: boolean; // computed field from Python
  created_at: string;
}


