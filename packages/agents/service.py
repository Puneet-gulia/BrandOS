"""
CreativeService — public facade for the Creative Layer.

Orchestrates all creative agents to produce a complete CampaignAssets bundle.
This is the ONLY class the API router calls for creative generation.

Channel routing logic:
- SOCIAL_MEDIA → SocialMediaAgent
- PAID_ADS     → CopywriterAgent (ad copy)
- EMAIL        → EmailSpecialistAgent
- LANDING_PAGE → LandingPageAgent
- Always run  → ImagePromptAgent (visual prompts useful for all campaigns)
"""
from __future__ import annotations

import logging
from typing import Optional

from packages.agents.base import BaseAgent
from packages.agents.copywriter_agent import CopywriterAgent
from packages.agents.email_specialist_agent import EmailSpecialistAgent
from packages.agents.image_prompt_agent import ImagePromptAgent
from packages.agents.landing_page_agent import LandingPageAgent
from packages.agents.social_media_agent import SocialMediaAgent
from packages.shared.config import get_settings
from packages.shared.models.assets import (
    AdVariant, EmailCampaign, ImagePromptItem, LandingPageCopy, SocialMediaPost
)
from packages.shared.models.brand import BrandProfile
from packages.shared.models.campaign import CampaignAssets, CampaignStrategy, MarketingChannel
from packages.tools.llm_client import LLMClient
from packages.tools.prompt_loader import PromptLoader

logger = logging.getLogger(__name__)

# Map channel enum values to social platform names for the SocialMediaAgent
_SOCIAL_PLATFORM_MAP = {
    MarketingChannel.SOCIAL_MEDIA: ["Instagram", "LinkedIn", "Facebook"],
}


class CreativeService:
    """Facade for the Creative Layer.

    Wires all creative agents and runs them based on the channels
    requested in the campaign strategy.
    """

    def __init__(self) -> None:
        settings = get_settings()
        llm_client = LLMClient()
        prompt_loader = PromptLoader()
        self._social_media_agent = SocialMediaAgent(llm_client, prompt_loader)
        self._copywriter_agent = CopywriterAgent(llm_client, prompt_loader)
        self._email_agent = EmailSpecialistAgent(llm_client, prompt_loader)
        self._landing_page_agent = LandingPageAgent(llm_client, prompt_loader)
        self._image_prompt_agent = ImagePromptAgent(llm_client, prompt_loader)

    async def generate_assets(
        self,
        brand_profile: BrandProfile,
        campaign_strategy: CampaignStrategy,
        channels: list[MarketingChannel],
    ) -> CampaignAssets:
        """Generate all creative assets for the campaign.

        Runs each agent whose channel is requested. Always runs
        the ImagePromptAgent regardless of channels.

        Args:
            brand_profile: The extracted brand identity.
            campaign_strategy: The approved campaign strategy.
            channels: The marketing channels requested in the brief.

        Returns:
            A populated CampaignAssets with all generated content.
        """
        logger.info(
            "Generating creative assets for strategy=%s channels=%s",
            campaign_strategy.id[:8],
            [c.value for c in channels],
        )

        social_posts: list[SocialMediaPost] = []
        ad_copy: list[AdVariant] = []
        emails: list[EmailCampaign] = []
        landing_page: Optional[LandingPageCopy] = None
        image_prompts: list[ImagePromptItem] = []

        # Channel-routed agents
        if MarketingChannel.SOCIAL_MEDIA in channels:
            social_posts = await self._social_media_agent.generate(
                brand_profile, campaign_strategy, platforms=["Instagram", "LinkedIn", "Facebook"]
            )
            logger.info("Generated %d social media posts", len(social_posts))

        if MarketingChannel.PAID_ADS in channels:
            ad_copy = await self._copywriter_agent.generate(brand_profile, campaign_strategy)
            logger.info("Generated %d ad variants", len(ad_copy))

        if MarketingChannel.EMAIL in channels:
            emails = await self._email_agent.generate(brand_profile, campaign_strategy)
            logger.info("Generated %d email campaigns", len(emails))

        if MarketingChannel.LANDING_PAGE in channels:
            landing_page = await self._landing_page_agent.generate(brand_profile, campaign_strategy)
            logger.info("Generated landing page copy")

        # Always generate image prompts
        image_prompts = await self._image_prompt_agent.generate(brand_profile, campaign_strategy)
        logger.info("Generated %d image prompts", len(image_prompts))

        return CampaignAssets(
            campaign_strategy_id=campaign_strategy.id,
            social_media_posts=social_posts,
            ad_copy=ad_copy,
            email_campaigns=emails,
            landing_page_copy=landing_page,
            image_prompts=image_prompts,
        )
