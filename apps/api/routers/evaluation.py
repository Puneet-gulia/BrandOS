"""
Evaluation router — POST /api/campaigns/{id}/evaluate

Triggers quality evaluation for a campaign that has already generated assets.
Separating evaluation from asset generation lets users:
1. Review assets first
2. Trigger a quality pass explicitly
3. Re-evaluate after manual edits (future)
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from apps.api.dependencies import EvaluationServiceDep, PlanningServiceDep
from packages.shared.errors import OrchestrationError
from packages.shared.models.campaign import CampaignPackage
from packages.workflows.campaign_store import CampaignNotFoundError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/campaigns", tags=["evaluation"])


class EvaluationResponse(BaseModel):
    campaign: CampaignPackage


@router.post("/{campaign_id}/evaluate", response_model=EvaluationResponse)
async def evaluate_campaign(
    campaign_id: str,
    planning_service: PlanningServiceDep,
    evaluation_service: EvaluationServiceDep,
) -> EvaluationResponse:
    """Run quality evaluation on a campaign's generated assets.

    Requires:
    - Campaign status = 'complete'
    - campaign_strategy is populated
    - campaign_assets is populated

    Returns the updated CampaignPackage with quality_report attached.
    """
    # Retrieve campaign
    try:
        package = await planning_service.get_campaign(campaign_id)
    except CampaignNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.message) from exc

    # Validate preconditions
    if package.campaign_strategy is None:
        raise HTTPException(
            status_code=409,
            detail="Campaign must have a strategy before evaluation. Run POST /create first.",
        )
    if package.campaign_assets is None:
        raise HTTPException(
            status_code=409,
            detail="Campaign must have generated assets before evaluation. Run POST /{id}/assets first.",
        )

    # Run evaluation
    try:
        report = await evaluation_service.evaluate_campaign(
            brand_profile=package.brand_profile,
            campaign_strategy=package.campaign_strategy,
            campaign_assets=package.campaign_assets,
        )
    except OrchestrationError as exc:
        logger.error("Evaluation failed for campaign %s: %s", campaign_id, exc)
        raise HTTPException(
            status_code=422,
            detail={"error": "evaluation_failed", "message": exc.message},
        ) from exc
    except Exception as exc:
        logger.exception("Unexpected error evaluating campaign %s", campaign_id)
        raise HTTPException(status_code=500, detail="Internal server error during evaluation") from exc

    # Attach report and persist
    updated_package = package.model_copy(
        update={
            "quality_report": report,
            "updated_at": datetime.now(timezone.utc),
        }
    )
    await planning_service.update_campaign(updated_package)
    logger.info(
        "Evaluation complete for campaign %s: overall_score=%.2f passed=%s",
        campaign_id,
        report.overall_score,
        report.passed,
    )

    return EvaluationResponse(campaign=updated_package)
