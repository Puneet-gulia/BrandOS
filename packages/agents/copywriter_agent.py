"""
CopywriterAgent — generates high-converting ad variants.
"""
from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel

from packages.agents.base import BaseAgent
from packages.shared.errors import LLMError, OrchestrationError
from packages.shared.models.assets import AdVariant
from packages.shared.models.brand import BrandProfile
from packages.shared.models.campaign import CampaignStrategy


class CopywriterAgent(BaseAgent):
    """Generates ad variants across multiple platforms."""

    PROMPT_TEMPLATE = "creative/ad_copy"

    async def generate(
        self,
        brand_profile: BrandProfile,
        campaign_strategy: CampaignStrategy,
        **kwargs: Any,
    ) -> list[AdVariant]:
        """Generate ad copy variants.

        Args:
            brand_profile: The brand identity.
            campaign_strategy: The approved campaign strategy.

        Returns:
            A list of AdVariant objects.

        Raises:
            OrchestrationError: If the LLM fails to generate valid ad copy.
        """
        self._logger.info("Generating ad copy variants")

        try:
            prompt = self._prompt_loader.load(
                self.PROMPT_TEMPLATE,
                brand_profile=json.dumps(brand_profile.model_dump(mode="json"), indent=2),
                campaign_strategy=json.dumps(campaign_strategy.model_dump(mode="json"), indent=2),
            )
            return await self._llm_client.complete_structured_list(
                prompt=prompt,
                item_model=AdVariant,
                system_prompt="You are a professional copywriter. Respond only with valid JSON array.",
            )
        except LLMError as exc:
            detail_msg = f"{exc.message} ({exc.detail})" if exc.detail else exc.message
            raise OrchestrationError(
                "CopywriterAgent failed to generate ad variants",
                detail=detail_msg,
            ) from exc
        except Exception as exc:
            raise OrchestrationError(
                "CopywriterAgent failed to parse LLM output",
                detail=str(exc),
            ) from exc
