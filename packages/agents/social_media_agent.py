"""
SocialMediaAgent — generates platform-native social media posts.

Single responsibility: receive BrandProfile + CampaignStrategy + platforms list,
return a list of SocialMediaPost objects.
"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from packages.agents.base import CREATIVE_TEMPERATURE, BaseAgent
from packages.shared.errors import LLMError, OrchestrationError
from packages.shared.models.assets import SocialMediaPost
from packages.shared.models.brand import BrandProfile
from packages.shared.models.campaign import CampaignStrategy


class SocialMediaPostsOutput(BaseModel):
    """Wrapper so we can use complete_structured() with a list."""
    posts: list[SocialMediaPost]


class SocialMediaAgent(BaseAgent):
    """Generates platform-native social media posts."""

    PROMPT_TEMPLATE = "creative/social_media"

    async def generate(
        self,
        brand_profile: BrandProfile,
        campaign_strategy: CampaignStrategy,
        platforms: list[str] | None = None,
        **kwargs: Any,
    ) -> list[SocialMediaPost]:
        """Generate social media posts for the specified platforms.

        Args:
            brand_profile: The brand identity.
            campaign_strategy: The approved campaign strategy.
            platforms: List of platform names. Defaults to ["Instagram", "LinkedIn"].

        Returns:
            A list of SocialMediaPost objects.

        Raises:
            OrchestrationError: If the LLM fails to generate valid posts.
        """
        requested_platforms = platforms or ["Instagram", "LinkedIn"]
        platforms_str = ", ".join(requested_platforms)

        self._logger.info("Generating social media posts for platforms: %s", platforms_str)

        constraints = kwargs.get("constraints")

        try:
            prompt = self._build_prompt(
                self.PROMPT_TEMPLATE,
                brand_profile,
                campaign_strategy,
                campaign_brief=kwargs.get("campaign_brief"),
                constraints=constraints,
                platforms=platforms_str,
            )
            # Wrap in an object so complete_structured can parse the list
            return await self._llm_client.complete_structured_list(
                prompt=prompt,
                item_model=SocialMediaPost,
                system_prompt="You are a professional social media copywriter. Respond only with valid JSON array.",
                model=self._model,
                temperature=CREATIVE_TEMPERATURE,
            )
        except LLMError as exc:
            detail_msg = f"{exc.message} ({exc.detail})" if exc.detail else exc.message
            raise OrchestrationError(
                "SocialMediaAgent failed to generate posts",
                detail=detail_msg,
            ) from exc
        except Exception as exc:
            raise OrchestrationError(
                "SocialMediaAgent failed to parse LLM output",
                detail=str(exc),
            ) from exc
