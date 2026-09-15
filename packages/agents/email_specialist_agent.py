"""
EmailSpecialistAgent — generates email marketing campaigns.
"""
from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel

from packages.agents.base import BaseAgent
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
                item_model=EmailCampaign,
                system_prompt="You are a professional email specialist. Respond only with valid JSON array.",
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
