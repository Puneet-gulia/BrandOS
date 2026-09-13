"""
CampaignPlanner — Planning Layer agent.

Single responsibility: receive a BrandProfile and CampaignBrief,
call the LLM with the campaign strategy prompt, and return a
structured CampaignStrategy.

This agent:
- Knows nothing about web scraping, creativity, or evaluation
- Never calls the LLM directly — always through LLMClient
- Never has prompts hardcoded — always through PromptLoader
"""
from __future__ import annotations

import json
import logging
from typing import Optional

from pydantic import BaseModel

from packages.shared.errors import LLMError, OrchestrationError
from packages.shared.models.brand import BrandProfile
from packages.shared.models.campaign import CampaignBrief, CampaignStrategy
from packages.tools.llm_client import LLMClient
from packages.tools.prompt_loader import PromptLoader

logger = logging.getLogger(__name__)


class CampaignStrategyLLMOutput(BaseModel):
    """Pydantic model matching the LLM output schema for campaign strategy.

    This is the intermediate model between the raw LLM JSON response and the
    full CampaignStrategy model (which adds system-generated fields like id,
    campaign_brief_id, and created_at).
    """

    campaign_name: str
    positioning_statement: str
    messaging_pillars: list[str]
    key_themes: list[str]
    channel_strategy: dict[str, str]
    content_calendar_weeks: int
    success_metrics: list[str]
    rationale: str


class CampaignPlanner:
    """Planning Layer agent.

    Transforms a BrandProfile + CampaignBrief into a CampaignStrategy.

    The planner is stateless — it holds no campaign data itself. Each call
    to plan() is fully independent.

    Args:
        llm_client: The shared LLM client for making API calls.
        prompt_loader: The prompt loader for loading strategy templates.
    """

    def __init__(self, llm_client: LLMClient, prompt_loader: PromptLoader) -> None:
        self._llm_client = llm_client
        self._prompt_loader = prompt_loader

    async def plan(
        self,
        brand_profile: BrandProfile,
        campaign_brief: CampaignBrief,
    ) -> CampaignStrategy:
        """Generate a CampaignStrategy from a BrandProfile and CampaignBrief.

        Args:
            brand_profile: The extracted brand identity.
            campaign_brief: The user's campaign objectives and constraints.

        Returns:
            A structured CampaignStrategy ready for use by the Creative Layer.

        Raises:
            OrchestrationError: If the LLM fails or returns an invalid strategy.
        """
        logger.info(
            "Planning campaign for brand=%r, objective=%r",
            brand_profile.company_name,
            campaign_brief.objective[:80],
        )

        # Serialize inputs for the prompt template.
        # We use model_dump with mode='json' to ensure all types (datetime, enum)
        # are serialized to JSON-safe primitives.
        brand_json = json.dumps(
            brand_profile.model_dump(mode="json"),
            indent=2,
        )
        brief_json = json.dumps(
            campaign_brief.model_dump(mode="json"),
            indent=2,
        )

        try:
            prompt = self._prompt_loader.load(
                "planning/campaign_strategy",
                brand_profile=brand_json,
                campaign_brief=brief_json,
            )

            llm_output = await self._llm_client.complete_structured(
                prompt=prompt,
                response_model=CampaignStrategyLLMOutput,
                system_prompt=(
                    "You are a senior marketing strategist. "
                    "Respond only with valid JSON. No commentary."
                ),
            )
        except LLMError as exc:
            raise OrchestrationError(
                message="Campaign planning failed — LLM returned an error",
                detail=str(exc),
            ) from exc

        # Validate the strategy makes sense before returning it
        self._validate_strategy(llm_output, campaign_brief)

        return CampaignStrategy(
            campaign_brief_id=campaign_brief.id,
            campaign_name=llm_output.campaign_name,
            positioning_statement=llm_output.positioning_statement,
            messaging_pillars=llm_output.messaging_pillars,
            key_themes=llm_output.key_themes,
            channel_strategy=llm_output.channel_strategy,
            content_calendar_weeks=llm_output.content_calendar_weeks,
            success_metrics=llm_output.success_metrics,
            rationale=llm_output.rationale,
        )

    @staticmethod
    def _validate_strategy(
        strategy: CampaignStrategyLLMOutput,
        brief: CampaignBrief,
    ) -> None:
        """Lightweight sanity checks on the LLM output.

        We validate that the strategy is non-trivially complete. We do NOT
        enforce strict channel matching because the LLM may map channel enum
        values to human-readable names (e.g. 'SOCIAL_MEDIA' → 'Social Media').

        Raises:
            OrchestrationError: If the strategy fails a critical validation.
        """
        if not strategy.campaign_name.strip():
            raise OrchestrationError("LLM returned an empty campaign name")
        if len(strategy.messaging_pillars) < 1:
            raise OrchestrationError("LLM returned no messaging pillars")
        if len(strategy.success_metrics) < 1:
            raise OrchestrationError("LLM returned no success metrics")
        if strategy.content_calendar_weeks < 1:
            raise OrchestrationError("LLM returned invalid content calendar weeks")
