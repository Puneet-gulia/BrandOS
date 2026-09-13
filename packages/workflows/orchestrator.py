"""
CampaignOrchestrator — the top-level layer of BrandOS.

Chains all four layers in the correct sequence:
  Knowledge → Planning → Creative → Evaluation

This is the ONLY place in the codebase where the four services are
composed together. Each service remains independently testable and
deployable — the orchestrator only handles sequencing and data flow.

Design principles:
- The orchestrator has NO business logic of its own
- Each step is a pure delegation to the correct service
- Failure at any step is surfaced as an OrchestrationError with
  enough context to know which layer failed
- The package is saved after each step so GET /api/campaigns/{id}
  always reflects the current progress
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from packages.agents.service import CreativeService
from packages.evaluations.service import EvaluationService
from packages.knowledge.service import KnowledgeService
from packages.shared.errors import OrchestrationError
from packages.shared.models.brand import BrandProfile
from packages.shared.models.campaign import (
    CampaignBrief,
    CampaignPackage,
    MarketingChannel,
)
from packages.workflows.service import PlanningService

logger = logging.getLogger(__name__)


class CampaignOrchestrator:
    """Top-level campaign orchestrator.

    Wires together the four BrandOS service layers and exposes a single
    run() method that accepts a BrandProfile + brief parameters and
    returns a fully populated CampaignPackage.

    The brand extraction step is intentionally NOT part of the orchestrator
    because the user has already extracted (and verified) their BrandProfile
    in step 1 of the UI. Re-extracting would waste LLM tokens.

    Args:
        knowledge_service: KnowledgeService — used only for reference, not run()
        planning_service: PlanningService — creates campaign + strategy
        creative_service: CreativeService — generates all creative assets
        evaluation_service: EvaluationService — evaluates asset quality
    """

    def __init__(
        self,
        planning_service: PlanningService,
        creative_service: CreativeService,
        evaluation_service: EvaluationService,
    ) -> None:
        self._planning = planning_service
        self._creative = creative_service
        self._evaluation = evaluation_service

    async def run(
        self,
        brand_profile: BrandProfile,
        objective: str,
        target_audience: list[str],
        channels: list[MarketingChannel],
        budget_range: str | None = None,
        timeline_weeks: int | None = None,
        constraints: list[str] | None = None,
    ) -> CampaignPackage:
        """Execute the full campaign generation pipeline.

        Pipeline:
        1. PlanningService.create_campaign()   → CampaignPackage (strategy)
        2. CreativeService.generate_assets()   → CampaignAssets
        3. EvaluationService.evaluate_campaign() → QualityReport

        The package is persisted after each step so callers can
        poll GET /api/campaigns/{id} to observe progress.

        Args:
            brand_profile: The pre-extracted brand identity.
            objective: The campaign objective (from the brief).
            target_audience: Target audience segments.
            channels: Marketing channels to activate.
            budget_range: Optional budget range string.
            timeline_weeks: Optional campaign duration.
            constraints: Optional list of creative constraints.

        Returns:
            A fully populated CampaignPackage with status='complete',
            campaign_strategy, campaign_assets, and quality_report.

        Raises:
            OrchestrationError: If any layer fails.
        """
        if constraints is None:
            constraints = []

        logger.info(
            "Orchestrator.run: brand=%r objective=%r channels=%s",
            brand_profile.company_name,
            objective[:60],
            [c.value for c in channels],
        )

        brief = CampaignBrief(
            brand_profile_id=brand_profile.id,
            objective=objective,
            target_audience=target_audience,
            channels=channels,
            budget_range=budget_range,
            timeline_weeks=timeline_weeks,
            constraints=constraints,
        )

        # ── Step 1: Planning ──────────────────────────────────────────────────
        logger.info("[1/3] Planning: generating campaign strategy")
        try:
            package = await self._planning.create_campaign(
                brand_profile=brand_profile,
                campaign_brief=brief,
            )
        except Exception as exc:
            raise OrchestrationError(
                "Orchestration failed at Planning step",
                detail=str(exc),
            ) from exc

        if package.campaign_strategy is None:
            raise OrchestrationError(
                "Planning step completed but returned no strategy",
                detail="CampaignPackage.campaign_strategy is None",
            )

        strategy = package.campaign_strategy
        logger.info("[1/3] Planning complete: campaign=%r", strategy.campaign_name)

        # ── Step 2: Creative ──────────────────────────────────────────────────
        logger.info("[2/3] Creative: generating assets for %d channels", len(channels))
        try:
            assets = await self._creative.generate_assets(
                brand_profile=brand_profile,
                campaign_strategy=strategy,
                channels=channels,
            )
        except Exception as exc:
            raise OrchestrationError(
                "Orchestration failed at Creative step",
                detail=str(exc),
            ) from exc

        # Persist assets immediately
        now = datetime.now(timezone.utc)
        package = package.model_copy(
            update={"campaign_assets": assets, "updated_at": now}
        )
        await self._planning.update_campaign(package)
        logger.info(
            "[2/3] Creative complete: posts=%d ads=%d emails=%d lp=%s images=%d",
            len(assets.social_media_posts),
            len(assets.ad_copy),
            len(assets.email_campaigns),
            "yes" if assets.landing_page_copy else "no",
            len(assets.image_prompts),
        )

        # ── Step 3: Evaluation ────────────────────────────────────────────────
        logger.info("[3/3] Evaluation: scoring all 6 dimensions")
        try:
            report = await self._evaluation.evaluate_campaign(
                brand_profile=brand_profile,
                campaign_strategy=strategy,
                campaign_assets=assets,
            )
        except Exception as exc:
            raise OrchestrationError(
                "Orchestration failed at Evaluation step",
                detail=str(exc),
            ) from exc

        # Persist the final complete package
        package = package.model_copy(
            update={
                "quality_report": report,
                "status": "complete",
                "updated_at": datetime.now(timezone.utc),
            }
        )
        await self._planning.update_campaign(package)

        logger.info(
            "[3/3] Evaluation complete: overall_score=%.2f passed=%s",
            report.overall_score,
            report.passed,
        )
        logger.info(
            "Orchestration DONE: campaign_id=%s brand=%r",
            package.id,
            brand_profile.company_name,
        )

        return package
