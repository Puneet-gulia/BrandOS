/**
 * BrandOS API Client
 *
 * Typed wrapper around all FastAPI backend endpoints.
 * All functions throw an Error with a user-friendly message on failure.
 */

import type {
  BrandProfile,
  CampaignPackage,
  CreateCampaignRequest,
  HealthResponse,
  KnowledgeExtractRequest,
  QualityReport,
  RunCampaignRequest,
} from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

/** Internal wrapper matching the Python BrandProfileResponse envelope. */
interface BrandProfileResponse {
  profile: BrandProfile;
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${path}`;
  const response = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({ message: response.statusText }));
    let msg = `Request failed: ${response.status}`;
    if (typeof body.detail === 'object' && body.detail !== null) {
      msg = body.detail.message || body.detail.detail || body.detail.error || JSON.stringify(body.detail);
    } else if (typeof body.message === 'string' && body.message) {
      msg = body.message;
    } else if (typeof body.detail === 'string' && body.detail) {
      msg = body.detail;
    }
    throw new Error(msg);
  }
  return response.json() as Promise<T>;
}

export const api = {
  health: {
    check: () => request<HealthResponse>('/api/health'),
  },
  knowledge: {
    /**
     * Extract a brand profile from URL, text, or document content string.
     * Unwraps the server-side BrandProfileResponse envelope automatically.
     */
    extract: async (data: KnowledgeExtractRequest): Promise<BrandProfile> => {
      const res = await request<BrandProfileResponse>('/api/knowledge/extract', {
        method: 'POST',
        body: JSON.stringify(data),
      });
      return res.profile;
    },
    /**
     * Extract a brand profile from an uploaded file (multipart/form-data).
     * The browser sets the Content-Type boundary automatically when headers is omitted.
     */
    extractFile: async (file: File, extraContext?: string): Promise<BrandProfile> => {
      const form = new FormData();
      form.append('file', file);
      if (extraContext) form.append('extra_context', extraContext);
      const res = await request<BrandProfileResponse>('/api/knowledge/extract-file', {
        method: 'POST',
        // Deliberately omit Content-Type so the browser sets multipart/form-data + boundary
        headers: {},
        body: form,
      });
      return res.profile;
    },
  },
  campaigns: {
    /**
     * Create a campaign with a brand profile and brief.
     * The server returns { campaign: CampaignPackage }, which we unwrap.
     */
    create: async (data: CreateCampaignRequest): Promise<CampaignPackage> => {
      const res = await request<{ campaign: CampaignPackage }>('/api/campaigns/create', {
        method: 'POST',
        body: JSON.stringify(data),
      });
      return res.campaign;
    },
    /** Run the full BrandOS pipeline: Planning → Creative → Evaluation */
    run: async (data: RunCampaignRequest): Promise<CampaignPackage> => {
      const res = await request<{ campaign: CampaignPackage }>('/api/campaigns/run', {
        method: 'POST',
        body: JSON.stringify(data),
      });
      return res.campaign;
    },
    /** Retrieve an existing campaign by ID. */
    get: async (id: string): Promise<CampaignPackage> => {
      const res = await request<{ campaign: CampaignPackage }>(`/api/campaigns/${id}`);
      return res.campaign;
    },
    generateAssets: async (campaignId: string): Promise<CampaignPackage> => {
      const res = await request<{ campaign: CampaignPackage }>(`/api/campaigns/${campaignId}/assets`, {
        method: 'POST',
      });
      return res.campaign;
    },
    /** Run quality evaluation on a campaign that has assets. */
    evaluate: async (campaignId: string): Promise<CampaignPackage> => {
      const res = await request<{ campaign: CampaignPackage }>(`/api/campaigns/${campaignId}/evaluate`, {
        method: 'POST',
      });
      return res.campaign;
    },
  },
};

