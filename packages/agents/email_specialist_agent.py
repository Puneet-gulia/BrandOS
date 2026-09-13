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

        try:
            prompt = self._prompt_loader.load(
                self.PROMPT_TEMPLATE,
                brand_profile=json.dumps(brand_profile.model_dump(mode="json"), indent=2),
                campaign_strategy=json.dumps(campaign_strategy.model_dump(mode="json"), indent=2),
            )
            raw = await self._llm_client.complete(
                prompt=prompt,
                system_prompt="You are a professional email specialist. Respond only with valid JSON array.",
            )
            cleaned = raw.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1].rsplit("```", 1)[0].strip()
            import json as _json
            items = _json.loads(cleaned)
            return [EmailCampaign.model_validate(item) for item in items]
        except LLMError as exc:
            raise OrchestrationError(
                "EmailSpecialistAgent failed to generate email campaigns",
                detail=str(exc),
            ) from exc
        except Exception as exc:
            raise OrchestrationError(
                "EmailSpecialistAgent failed to parse LLM output",
                detail=str(exc),
            ) from exc
