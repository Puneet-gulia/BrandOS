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

from packages.shared.config import get_settings
from packages.tools.llm_client import LLMClient
from packages.tools.prompt_loader import PromptLoader
from packages.shared.models.brand import BrandProfile
from packages.shared.models.campaign import CampaignBrief, CampaignStrategy

HOUSE_STYLE_TEMPLATE = "creative/_house_style"

# Creative writing benefits from some variety; parsing/strategy calls keep the provider default.
CREATIVE_TEMPERATURE = 0.8


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
        settings = get_settings()
        self._model = settings.openrouter_creative_model or None

    def _build_prompt(
        self,
        template: str,
        brand_profile: BrandProfile,
        campaign_strategy: CampaignStrategy,
        campaign_brief: CampaignBrief | None = None,
        constraints: list[str] | None = None,
        **extra: str,
    ) -> str:
        """Render an agent template with the shared creative brief and house style."""
        return self._prompt_loader.load(
            template,
            creative_brief=render_creative_brief(brand_profile, campaign_strategy, campaign_brief, constraints),
            house_style=self._prompt_loader.load(HOUSE_STYLE_TEMPLATE),
            **extra,
        )

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


def _bullets(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items if item) or "- (none given)"


def render_creative_brief(
    brand_profile: BrandProfile,
    campaign_strategy: CampaignStrategy,
    campaign_brief: CampaignBrief | None = None,
    constraints: list[str] | None = None,
) -> str:
    """Turn the brand profile, brief and strategy into a readable creative brief.

    Models write noticeably better from a human-style brief than from raw JSON
    dumps full of ids and timestamps, and it keeps the voice samples prominent.
    """
    bp = brand_profile
    cs = campaign_strategy
    directives = constraints if constraints is not None else (campaign_brief.constraints if campaign_brief else [])

    sections = [
        f"### Brand: {bp.company_name}",
        f"Industry: {bp.industry}",
    ]
    if bp.tagline:
        sections.append(f"Tagline: {bp.tagline}")
    sections += [
        f"What makes them different: {bp.unique_selling_proposition}",
        f"Tone: {bp.tone}",
        f"Voice: {', '.join(bp.brand_voice)}",
        f"Writing style: {', '.join(bp.writing_style)}",
        f"Core values: {', '.join(bp.core_values)}",
        f"Words and topics they own: {', '.join(bp.keywords)}",
    ]
    if bp.competitors:
        sections.append(f"Competitors: {', '.join(bp.competitors)}")
    sections.append(f"Background: {bp.raw_input_summary}")

    if bp.voice_samples:
        sections += [
            "",
            "### Voice samples (the brand's own words — match this voice)",
            "\n".join(f"> {sample}" for sample in bp.voice_samples),
        ]

    sections += ["", "### Campaign"]
    if campaign_brief:
        sections.append(f"Objective: {campaign_brief.objective}")
    sections += [
        f"Campaign name (internal): {cs.campaign_name}",
        f"Positioning: {cs.positioning_statement}",
        "Target audience:",
        _bullets(campaign_brief.target_audience if campaign_brief else bp.target_audience),
        "Messaging pillars:",
        _bullets(cs.messaging_pillars),
        "Themes:",
        _bullets(cs.key_themes),
        "Channel plan:",
        _bullets([f"{channel}: {plan}" for channel, plan in cs.channel_strategy.items()]),
        "",
        "### Directives from the user (must follow)",
        _bullets(directives) if directives else "- None",
    ]
    return "\n".join(sections)
