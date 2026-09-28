"""
EmailSpecialistAgent — generates email marketing campaigns.
"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from packages.agents.base import CREATIVE_TEMPERATURE, BaseAgent
from packages.shared.errors import LLMError, OrchestrationError
from packages.shared.models.assets import EmailCampaign
from packages.shared.models.brand import BrandProfile
from packages.shared.models.campaign import CampaignStrategy


class EmailSpecialistAgent(BaseAgent):
    """Generates email campaigns."""

    PROMPT_TEMPLATE = "creative/email_specialist"

    async def generate(
        self,
        brand_profile: BrandProfile,
        campaign_strategy: CampaignStrategy,
        **kwargs: Any,
    ) -> list[EmailCampaign]:
        """Generate email campaigns.

        Args:
            brand_profile: The brand identity.
            campaign_strategy: The approved campaign strategy.

        Returns:
            A list of EmailCampaign objects.

        Raises:
            OrchestrationError: If the LLM fails to generate valid email campaigns.
        """
        self._logger.info("Generating email campaigns")

        constraints = kwargs.get("constraints")

        try:
            prompt = self._build_prompt(
                self.PROMPT_TEMPLATE,
                brand_profile,
                campaign_strategy,
                campaign_brief=kwargs.get("campaign_brief"),
                constraints=constraints,
            )
            return await self._llm_client.complete_structured_list(
                prompt=prompt,
                item_model=EmailCampaign,
                system_prompt="You are a professional email specialist. Respond only with valid JSON array.",
                model=self._model,
                temperature=CREATIVE_TEMPERATURE,
            )
        except LLMError as exc:
            detail_msg = f"{exc.message} ({exc.detail})" if exc.detail else exc.message
            raise OrchestrationError(
                "EmailSpecialistAgent failed to generate email campaigns",
                detail=detail_msg,
            ) from exc
        except Exception as exc:
            raise OrchestrationError(
                "EmailSpecialistAgent failed to parse LLM output",
                detail=str(exc),
            ) from exc
