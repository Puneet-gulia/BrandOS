"""
BaseAgent — abstract base class for all BrandOS creative agents.

All creative agents inherit from this class. This ensures:
- Consistent constructor signature (LLMClient + PromptLoader)
- A single, well-defined generate() method per agent
- Consistent logging pattern
- No agent holds state between generate() calls (stateless design)
"""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any

from packages.tools.llm_client import LLMClient
from packages.tools.prompt_loader import PromptLoader
from packages.shared.models.brand import BrandProfile
from packages.shared.models.campaign import CampaignStrategy


class BaseAgent(ABC):
    """Abstract base for BrandOS creative agents.

    Each concrete agent:
    - Has ONE responsibility (one type of creative output)
    - Has ONE corresponding prompt template (.md file)
    - Has ONE structured output type
    - Is stateless — all inputs come via generate(), no instance state

    Args:
        llm_client: Shared LLM client instance
        prompt_loader: Shared prompt loader instance
    """

    def __init__(self, llm_client: LLMClient, prompt_loader: PromptLoader) -> None:
        self._llm_client = llm_client
        self._prompt_loader = prompt_loader
        self._logger = logging.getLogger(self.__class__.__module__ + "." + self.__class__.__name__)

    @abstractmethod
    async def generate(
        self,
        brand_profile: BrandProfile,
        campaign_strategy: CampaignStrategy,
        **kwargs: Any,
    ) -> Any:
        """Generate creative assets.

        Args:
            brand_profile: The extracted brand identity
            campaign_strategy: The approved campaign strategy
            **kwargs: Agent-specific additional inputs (e.g. platforms list)

        Returns:
            Agent-specific structured output (always a Pydantic model or list of them)
        """
        ...
