# BrandOS — Your AI Creative Team

BrandOS is an AI-powered Creative Operating System that orchestrates specialized AI agents to generate complete marketing campaigns.

## Monorepo Structure

```
BrandOS/
├── apps/
│   ├── api/          # FastAPI backend
│   └── web/          # Next.js frontend
├── packages/
│   ├── shared/       # Canonical Pydantic models & errors
│   ├── knowledge/    # Knowledge Layer (brand extraction)
│   ├── agents/       # Creative agents (Phase 3)
│   ├── workflows/    # Orchestration & Planning (Phase 2)
│   ├── prompts/      # Prompt templates (.md files)
│   ├── tools/        # Shared utilities (LLM client, prompt loader)
│   └── evaluations/  # Evaluation Layer (Phase 4)
└── docs/
```

## Quick Start

### Backend
```bash
cd BrandOS
python -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
# Edit .env with your API keys
uvicorn apps.api.main:app --reload
```

### Frontend
```bash
cd apps/web
npm install
npm run dev
```

## Architecture

See [docs/architecture.md](docs/architecture.md) for the full system design.

## Development Phases

| Phase | Feature | Status |
|-------|---------|--------|
| 1 | Project Foundation + Knowledge Layer | ✅ Complete |
| 2 | Planning Layer | 🔜 Planned |
| 3 | Creative Layer (Agents) | 🔜 Planned |
| 4 | Evaluation Layer | 🔜 Planned |
| 5 | Campaign Assembly + Results UI | 🔜 Planned |
