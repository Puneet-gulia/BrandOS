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

        try:
            prompt = self._prompt_loader.load(
                self.PROMPT_TEMPLATE,
                brand_profile=json.dumps(brand_profile.model_dump(mode="json"), indent=2),
                campaign_strategy=json.dumps(campaign_strategy.model_dump(mode="json"), indent=2),
            )
            raw = await self._llm_client.complete(
                prompt=prompt,
                system_prompt="You are a professional creative director. Respond only with valid JSON array.",
            )
            cleaned = raw.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1].rsplit("```", 1)[0].strip()
            import json as _json
            items = _json.loads(cleaned)
            return [ImagePromptItem.model_validate(item) for item in items]
        except LLMError as exc:
            raise OrchestrationError(
                "ImagePromptAgent failed to generate image prompts",
                detail=str(exc),
            ) from exc
        except Exception as exc:
            raise OrchestrationError(
                "ImagePromptAgent failed to parse LLM output",
                detail=str(exc),
            ) from exc
