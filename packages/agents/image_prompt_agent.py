"""
ImagePromptAgent — generates visual image prompts for AI generation.
"""
from __future__ import annotations

import json
from typing import Any

from packages.agents.base import BaseAgent
from packages.shared.errors import LLMError, OrchestrationError
from packages.shared.models.assets import ImagePromptItem
from packages.shared.models.brand import BrandProfile
from packages.shared.models.campaign import CampaignStrategy


class ImagePromptAgent(BaseAgent):
    """Generates visual image prompts."""

    PROMPT_TEMPLATE = "creative/image_prompts"

    async def generate(
        self,
        brand_profile: BrandProfile,
        campaign_strategy: CampaignStrategy,
        **kwargs: Any,
    ) -> list[ImagePromptItem]:
        """Generate image prompt items.

        Args:
            brand_profile: The brand identity.
            campaign_strategy: The approved campaign strategy.

        Returns:
            A list of ImagePromptItem objects.

        Raises:
            OrchestrationError: If the LLM fails to generate valid image prompts.
        """
        self._logger.info("Generating image prompts")

        constraints = kwargs.get("constraints", [])
        constraints_str = "\n".join(constraints) if isinstance(constraints, list) and constraints else "None"

        try:
            prompt = self._prompt_loader.load(
                self.PROMPT_TEMPLATE,
                brand_profile=json.dumps(brand_profile.model_dump(mode="json"), indent=2),
                campaign_strategy=json.dumps(campaign_strategy.model_dump(mode="json"), indent=2),
                constraints=constraints_str,
            )
            return await self._llm_client.complete_structured_list(
                prompt=prompt,
                item_model=ImagePromptItem,
                system_prompt="You are a professional creative director. Respond only with valid JSON array.",
            )
        except LLMError as exc:
            detail_msg = f"{exc.message} ({exc.detail})" if exc.detail else exc.message
            raise OrchestrationError(
                "ImagePromptAgent failed to generate image prompts",
                detail=detail_msg,
            ) from exc
        except Exception as exc:
            raise OrchestrationError(
                "ImagePromptAgent failed to parse LLM output",
                detail=str(exc),
            ) from exc
