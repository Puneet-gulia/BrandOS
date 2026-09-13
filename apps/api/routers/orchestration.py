"""
Orchestration router — POST /api/campaigns/run

The "one-shot" endpoint. Accepts a pre-extracted BrandProfile + brief
parameters and runs the full 3-step pipeline (Planning → Creative →
Evaluation) via CampaignOrchestrator.

This is the primary endpoint for the BrandOS frontend — users get a
complete CampaignPackage in a single request after the brand extraction step.

The step-by-step endpoints (/api/campaigns/create, /{id}/assets, /{id}/evaluate)
remain available for tooling, testing, and future API consumers who want
finer-grained control.
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from apps.api.dependencies import OrchestratorDep
from packages.shared.errors import OrchestrationError
from packages.shared.models.brand import BrandProfile
from packages.shared.models.campaign import CampaignPackage, MarketingChannel

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/campaigns", tags=["orchestration"])


# ── Request / Response models ─────────────────────────────────────────────────


class RunCampaignRequest(BaseModel):
    """Request body for POST /api/campaigns/run.

    The brand_profile is passed directly (already extracted by the
    /api/knowledge/extract step) to avoid duplicate LLM calls.
    All brief parameters are inlined for a flat, ergonomic request shape.
    """

    brand_profile: BrandProfile
    objective: str
    target_audience: list[str]
    channels: list[MarketingChannel]
    budget_range: str | None = None
    timeline_weeks: int | None = None
    constraints: list[str] = []


class RunCampaignResponse(BaseModel):
    """Response envelope for the full orchestration run."""

    campaign: CampaignPackage


# ── Endpoint ──────────────────────────────────────────────────────────────────


@router.post("/run", response_model=RunCampaignResponse, status_code=201)
async def run_campaign(
    request: RunCampaignRequest,
    orchestrator: OrchestratorDep,
) -> RunCampaignResponse:
    """Run the complete BrandOS pipeline in a single request.

    Chains:
      Planning (strategy generation)
      → Creative (asset generation for all requested channels)
      → Evaluation (quality scoring across 6 dimensions)

    Returns a fully populated CampaignPackage with:
    - campaign_strategy
    - campaign_assets (social posts, ads, emails, landing page, image prompts)
    - quality_report (6-dimension evaluation)

    This endpoint may take 60–120 seconds for a full campaign with
    multiple channels. A future version will support streaming progress.
    """
    logger.info(
        "POST /api/campaigns/run brand=%r channels=%s",
        request.brand_profile.company_name,
        [c.value for c in request.channels],
    )

    try:
        package = await orchestrator.run(
            brand_profile=request.brand_profile,
            objective=request.objective,
            target_audience=request.target_audience,
            channels=request.channels,
            budget_range=request.budget_range,
            timeline_weeks=request.timeline_weeks,
            constraints=request.constraints,
        )
        return RunCampaignResponse(campaign=package)

    except OrchestrationError as exc:
        logger.error("Campaign run failed: %s (detail: %s)", exc.message, exc.detail)
        raise HTTPException(
            status_code=422,
            detail={
                "error": "orchestration_error",
                "message": exc.message,
                "detail": exc.detail,
            },
        ) from exc
    except Exception as exc:
        logger.exception("Unexpected error during campaign run")
        raise HTTPException(
            status_code=500,
            detail={"error": "internal_error", "message": "An unexpected error occurred"},
        ) from exc
