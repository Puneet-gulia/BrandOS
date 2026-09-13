"""
LandingPageAgent — generates full landing page copy.
"""
from __future__ import annotations

import json
from typing import Any

from packages.agents.base import BaseAgent
from packages.shared.errors import LLMError, OrchestrationError
from packages.shared.models.assets import LandingPageCopy
from packages.shared.models.brand import BrandProfile
from packages.shared.models.campaign import CampaignStrategy


class LandingPageAgent(BaseAgent):
    """Generates complete landing page copy."""

    PROMPT_TEMPLATE = "creative/landing_page"

    async def generate(
        self,
        brand_profile: BrandProfile,
        campaign_strategy: CampaignStrategy,
        **kwargs: Any,
    ) -> LandingPageCopy:
        """Generate landing page copy.

        Args:
            brand_profile: The brand identity.
            campaign_strategy: The approved campaign strategy.

        Returns:
            A single LandingPageCopy object.

        Raises:
            OrchestrationError: If the LLM fails to generate valid landing page copy.
        """
        self._logger.info("Generating landing page copy")

        try:
            prompt = self._prompt_loader.load(
                self.PROMPT_TEMPLATE,
                brand_profile=json.dumps(brand_profile.model_dump(mode="json"), indent=2),
                campaign_strategy=json.dumps(campaign_strategy.model_dump(mode="json"), indent=2),
            )
            
            result = await self._llm_client.complete_structured(
                prompt=prompt,
                response_model=LandingPageCopy,
                system_prompt="You are a professional landing page copywriter. Respond only with valid JSON.",
            )
            return result
        except LLMError as exc:
            raise OrchestrationError(
                "LandingPageAgent failed to generate landing page copy",
                detail=str(exc),
            ) from exc
        except Exception as exc:
            raise OrchestrationError(
                "LandingPageAgent failed to parse LLM output",
                detail=str(exc),
            ) from exc
