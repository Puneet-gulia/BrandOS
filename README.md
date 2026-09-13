# BrandOS — Your AI Creative Team

**BrandOS** is an AI-powered Creative Operating System that orchestrates specialized AI agents to generate complete, brand-consistent marketing campaigns from a single brief.

Unlike simple prompt wrappers, BrandOS simulates a multi-agent creative team where specialized agents handle brand extraction, strategy planning, creative asset generation across multiple channels, and quality evaluation.

---

## 🌟 Key Features

- **Knowledge Layer**: Multi-modal brand identity extraction from website URLs, raw text, or document uploads (`.txt`, `.pdf`).
- **Planning Layer**: Generates internal positioning statements, messaging pillars, key themes, channel strategies, and measurable KPIs.
- **Creative Layer**: 5 specialized agents generating platform-native assets:
  - **Social Media Specialist**: Instagram, LinkedIn, X, Facebook posts with native formatting, CTAs, & hashtags.
  - **Copywriter (Ad Specialist)**: Google Search, Meta Display, and LinkedIn Sponsored ad variants with character budget tracking.
  - **Email Specialist**: 3-part email sequences (Awareness, Value, Conversion) formatted in markdown with timing & preview text.
  - **Landing Page Specialist**: Complete landing page copy (Hero, Value Props, Social Proof, Features, FAQ, & Closing CTA).
  - **Visual Creative Director**: Midjourney/DALL-E 3 image generation prompts with aspect ratios, mood, and style directives.
- **Evaluation Layer**: Evaluates generated assets against 6 quality dimensions (**Brand Consistency, Grammar, Completeness, Tone, Readability, SEO**) with scoring, feedback, and recommendations.
- **Orchestration Layer**: Top-level workflow runner that executes the full pipeline end-to-end in a single request or step-by-step.

---

## 🏗️ Monorepo Structure

```text
BrandOS/
├── apps/
│   ├── api/                  # FastAPI backend app & routers
│   │   └── routers/          # health, knowledge, campaigns, assets, evaluation, orchestration
│   └── web/                  # Next.js 14 (App Router) + TailwindCSS + shadcn/ui frontend
├── packages/
│   ├── shared/               # Canonical Pydantic models (brand, campaign, assets, evaluation)
│   ├── knowledge/            # Knowledge Layer (web scraper, document parser, brand extractor)
│   ├── workflows/            # Planning Layer & CampaignOrchestrator
│   ├── agents/               # Creative Layer (SocialMedia, Copywriter, Email, LandingPage, ImagePrompt)
│   ├── evaluations/          # Evaluation Layer (QualityEvaluator & 6-dimension scoring engine)
│   ├── prompts/              # All LLM prompt templates (.md files — 0 hardcoded prompts in Python)
│   └── tools/                # Shared utilities (LLMClient with retries, PromptLoader)
└── pyproject.toml
```

---

## 🚦 Development Status

| Phase | Module | Status |
|-------|--------|--------|
| **1** | Project Foundation + Knowledge Layer | ✅ Complete |
| **2** | Planning Layer (`CampaignPlanner` & `CampaignStore`) | ✅ Complete |
| **3** | Creative Layer (5 Specialized Creative Agents) | ✅ Complete |
| **4** | Evaluation Layer (`QualityEvaluator` & 6-Dimension Engine) | ✅ Complete |
| **5** | Orchestration Layer (`CampaignOrchestrator` & Full UI) | ✅ Complete |

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.11+
- Node.js 18+ & npm
- OpenRouter API Key (or OpenAI API Key)

### 2. Backend Setup
```bash
# From the root directory
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

# Configure environment variables
cp .env.example .env
# Edit .env and set OPENROUTER_API_KEY=your_key_here

# Start FastAPI server
uvicorn apps.api.main:app --reload
# API available at http://localhost:8000
# Interactive Swagger docs at http://localhost:8000/docs
```

### 3. Frontend Setup
```bash
# In a new terminal window
cd apps/web
npm install

# Configure environment variables
cp .env.local.example .env.local

# Start Next.js dev server
npm run dev
# Frontend available at http://localhost:3000
```

---

## 📡 API Endpoints

- `GET  /api/health` — Health check
- `POST /api/knowledge/extract` — Extract brand profile from URL, text, or file
- `POST /api/campaigns/create` — Step 1: Create campaign brief & generate strategy
- `POST /api/campaigns/{id}/assets` — Step 2: Generate creative assets for campaign channels
- `POST /api/campaigns/{id}/evaluate` — Step 3: Run 6-dimension quality evaluation on generated assets
- `POST /api/campaigns/run` — **One-Shot Orchestrated Pipeline** (runs strategy → assets → evaluation end-to-end)
- `GET  /api/campaigns/{id}` — Retrieve full campaign package by ID

---

## 📄 License

MIT License.
