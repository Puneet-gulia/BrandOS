"""BrandOS Creative Agents — Phase 3.

Specialized AI agents, each with a single responsibility:
- SocialMediaAgent  → list[SocialMediaPost]
- CopywriterAgent   → list[AdVariant]
- EmailSpecialistAgent → list[EmailCampaign]
- LandingPageAgent  → LandingPageCopy
- ImagePromptAgent  → list[ImagePromptItem]

All agents are coordinated by CreativeService (the public facade).
No agent is called directly from outside this package.
"""

from packages.agents.service import CreativeService
from packages.agents.social_media_agent import SocialMediaAgent
from packages.agents.copywriter_agent import CopywriterAgent
from packages.agents.email_specialist_agent import EmailSpecialistAgent
from packages.agents.landing_page_agent import LandingPageAgent
from packages.agents.image_prompt_agent import ImagePromptAgent

__all__ = [
    "CreativeService",
    "SocialMediaAgent",
    "CopywriterAgent",
    "EmailSpecialistAgent",
    "LandingPageAgent",
    "ImagePromptAgent",
]
