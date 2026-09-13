"""
Campaign router — Phase 2 implementation.

Endpoints:
- POST /api/campaigns/create  → create a campaign from brand profile + brief
- GET  /api/campaigns/{id}    → retrieve an existing campaign by ID

The router is deliberately thin. All business logic lives in PlanningService.
"""
from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from apps.api.dependencies import PlanningServiceDep
from packages.shared.models.brand import BrandProfile
from packages.shared.models.campaign import (
    CampaignBrief,
    CampaignPackage,
    MarketingChannel,
)
from packages.shared.errors import OrchestrationError
from packages.workflows.campaign_store import CampaignNotFoundError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/campaigns", tags=["campaigns"])


# ── Request / Response models ─────────────────────────────────────────────────


class CreateCampaignRequest(BaseModel):
    """Request body for POST /api/campaigns/create.

    The client supplies the full BrandProfile (returned from the knowledge
    extraction step) and the campaign brief. No separate "save brand profile"
    endpoint is needed — the profile is carried in the request and stored as
    part of the CampaignPackage.
    """

    brand_profile: BrandProfile
    objective: str
    target_audience: list[str]
    channels: list[MarketingChannel]
    budget_range: str | None = None
    timeline_weeks: int | None = None
    constraints: list[str] = []


class CampaignPackageResponse(BaseModel):
    """Response envelope for campaign endpoints."""

    campaign: CampaignPackage


# ── Endpoints ─────────────────────────────────────────────────────────────────


@router.post("/create", response_model=CampaignPackageResponse, status_code=201)
async def create_campaign(
    request: CreateCampaignRequest,
    service: PlanningServiceDep,
) -> CampaignPackageResponse:
    """Create a campaign and generate a strategy.

    Accepts a BrandProfile (from the knowledge extraction step) and campaign
    parameters, then runs the Planning Layer to produce a CampaignStrategy.

    Returns the full CampaignPackage with status='complete' on success.
    """
    # Build the CampaignBrief from the flat request fields
    brief = CampaignBrief(
        brand_profile_id=request.brand_profile.id,
        objective=request.objective,
        target_audience=request.target_audience,
        channels=request.channels,
        budget_range=request.budget_range,
        timeline_weeks=request.timeline_weeks,
        constraints=request.constraints,
    )

    try:
        package = await service.create_campaign(
            brand_profile=request.brand_profile,
            campaign_brief=brief,
        )
        return CampaignPackageResponse(campaign=package)

    except OrchestrationError as exc:
        logger.error("Campaign creation failed: %s", exc)
        raise HTTPException(
            status_code=422,
            detail={"error": "orchestration_error", "message": exc.message, "detail": exc.detail},
        ) from exc
    except Exception as exc:
        logger.exception("Unexpected error during campaign creation")
        raise HTTPException(
            status_code=500,
            detail={"error": "internal_error", "message": "An unexpected error occurred"},
        ) from exc


@router.get("/{campaign_id}", response_model=CampaignPackageResponse)
async def get_campaign(
    campaign_id: str,
    service: PlanningServiceDep,
) -> CampaignPackageResponse:
    """Retrieve an existing campaign by ID.

    Returns the CampaignPackage as it currently exists in the store.
    Status may be 'in_progress', 'complete', or 'failed'.
    """
    try:
        package = await service.get_campaign(campaign_id)
        return CampaignPackageResponse(campaign=package)
    except CampaignNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.message) from exc
    except Exception as exc:
        logger.exception("Unexpected error retrieving campaign %s", campaign_id)
        raise HTTPException(status_code=500, detail="Internal server error") from exc
