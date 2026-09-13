"""
Assets router — POST /api/campaigns/{id}/assets

This endpoint triggers creative asset generation for an existing campaign
that already has a strategy (status='complete').

Separating asset generation from campaign creation allows the user to:
1. Review the strategy first
2. Decide if they want to proceed with asset generation
3. Regenerate assets without changing the strategy
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from apps.api.dependencies import CreativeServiceDep, PlanningServiceDep
from packages.shared.errors import OrchestrationError
from packages.shared.models.campaign import CampaignPackage
from packages.workflows.campaign_store import CampaignNotFoundError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/campaigns", tags=["assets"])


class AssetGenerationResponse(BaseModel):
    campaign: CampaignPackage


@router.post("/{campaign_id}/assets", response_model=AssetGenerationResponse)
async def generate_assets(
    campaign_id: str,
    planning_service: PlanningServiceDep,
    creative_service: CreativeServiceDep,
) -> AssetGenerationResponse:
    """Generate creative assets for an existing campaign.

    The campaign must already have a strategy (status='complete').
    Returns the updated CampaignPackage with populated campaign_assets.
    """
    # Retrieve campaign
    try:
        package = await planning_service.get_campaign(campaign_id)
    except CampaignNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.message) from exc

    # Validate state
    if package.status != "complete" or package.campaign_strategy is None:
        raise HTTPException(
            status_code=409,
            detail=f"Campaign must have a completed strategy before generating assets. Current status: {package.status}",
        )

    # Generate assets
    try:
        channels = package.campaign_brief.channels
        assets = await creative_service.generate_assets(
            brand_profile=package.brand_profile,
            campaign_strategy=package.campaign_strategy,
            channels=channels,
        )
    except OrchestrationError as exc:
        logger.error("Asset generation failed for campaign %s: %s", campaign_id, exc)
        raise HTTPException(
            status_code=422,
            detail={"error": "asset_generation_failed", "message": exc.message},
        ) from exc
    except Exception as exc:
        logger.exception("Unexpected error generating assets for campaign %s", campaign_id)
        raise HTTPException(status_code=500, detail="Internal server error during asset generation") from exc

    # Update the package with assets using the public service method
    from datetime import datetime, timezone
    updated_package = package.model_copy(
        update={"campaign_assets": assets, "updated_at": datetime.now(timezone.utc)}
    )
    await planning_service.update_campaign(updated_package)

    return AssetGenerationResponse(campaign=updated_package)
