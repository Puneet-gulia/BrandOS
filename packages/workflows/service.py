"""
PlanningService — public facade for the Planning Layer.

This is the only class the API router calls when working with campaign
planning. It wires together CampaignPlanner + CampaignStore and is
injected into routers via FastAPI's dependency system.

Design note: PlanningService intentionally mirrors KnowledgeService in
structure — a facade that hides all internal wiring. This consistency
makes the codebase predictable as new layers are added.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from packages.shared.config import Settings, get_settings
from packages.shared.models.brand import BrandProfile
from packages.shared.models.campaign import CampaignBrief, CampaignPackage
from packages.tools.llm_client import LLMClient
from packages.tools.prompt_loader import PromptLoader
from packages.workflows.campaign_store import CampaignStore
from packages.workflows.planner import CampaignPlanner

logger = logging.getLogger(__name__)


class PlanningService:
    """Facade for all Planning Layer operations.

    Exposes two high-level methods:
    - create_campaign: creates a CampaignPackage, generates a strategy, saves it
    - get_campaign: retrieves an existing CampaignPackage by ID

    All internal wiring (LLMClient, PromptLoader, CampaignPlanner, CampaignStore)
    is constructed here and hidden from callers.
    """

    def __init__(
        self,
        settings: Settings | None = None,
        store: CampaignStore | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._llm_client = LLMClient()
        self._prompt_loader = PromptLoader()
        self._planner = CampaignPlanner(self._llm_client, self._prompt_loader)
        # Allow injecting a custom store (useful for testing)
        self._store = store or CampaignStore()

    async def create_campaign(
        self,
        brand_profile: BrandProfile,
        campaign_brief: CampaignBrief,
    ) -> CampaignPackage:
        """Create a campaign package and generate a strategy.

        Workflow:
        1. Assemble an initial CampaignPackage with status='in_progress'
        2. Call CampaignPlanner to generate a CampaignStrategy
        3. Attach the strategy, update status to 'complete', save and return

        If planning fails, the package is saved with status='failed' and the
        error is re-raised so the API layer can return an appropriate response.

        Args:
            brand_profile: The extracted brand profile.
            campaign_brief: The user's campaign brief.

        Returns:
            A CampaignPackage with status='complete' and a populated strategy.

        Raises:
            OrchestrationError: If the planning step fails.
        """
        # Ensure the brief is linked to the brand profile
        brief_with_link = campaign_brief.model_copy(
            update={"brand_profile_id": brand_profile.id}
        )

        # Start the package in 'in_progress' state and persist it immediately
        # so GET requests can observe progress in future streaming scenarios
        package = CampaignPackage(
            brand_profile=brand_profile,
            campaign_brief=brief_with_link,
            status="in_progress",
        )
        await self._store.save(package)

        logger.info(
            "Creating campaign id=%s for brand=%r",
            package.id,
            brand_profile.company_name,
        )

        try:
            strategy = await self._planner.plan(brand_profile, brief_with_link)

            completed_package = package.model_copy(
                update={
                    "campaign_strategy": strategy,
                    "status": "complete",
                    "updated_at": datetime.now(timezone.utc),
                }
            )
            await self._store.save(completed_package)
            logger.info("Campaign id=%s completed successfully", package.id)
            return completed_package

        except Exception as exc:
            failed_package = package.model_copy(
                update={
                    "status": "failed",
                    "updated_at": datetime.now(timezone.utc),
                }
            )
            await self._store.save(failed_package)
            logger.error("Campaign id=%s failed: %s", package.id, exc)
            raise

    async def update_campaign(self, package: CampaignPackage) -> CampaignPackage:
        """Persist an updated CampaignPackage.

        Use this to update a package after assets or evaluation have been attached.
        This is the public replacement for directly calling store.save().

        Args:
            package: The updated campaign package.

        Returns:
            The saved package.
        """
        return await self._store.save(package)

    async def get_campaign(self, campaign_id: str) -> CampaignPackage:
        """Retrieve a CampaignPackage by ID.

        Args:
            campaign_id: The UUID of the campaign.

        Returns:
            The matching CampaignPackage.

        Raises:
            CampaignNotFoundError: If the campaign does not exist.
        """
        return await self._store.get(campaign_id)
