import os

base = "/Users/puneetgulia/.gemini/antigravity/scratch/BrandOS"

def write_file(path, content):
    full_path = os.path.join(base, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w") as f:
        f.write(content)

def read_file(path):
    with open(os.path.join(base, path), "r") as f:
        return f.read()

write_file("packages/shared/models/assets.py", '''"""
Typed models for BrandOS creative assets.

Each model represents the structured output of one creative agent.
Using typed models instead of dict[str, Any] gives us validation,
autocompletion, and serialization guarantees throughout the system.
"""
from __future__ import annotations
from pydantic import BaseModel, Field


class SocialMediaPost(BaseModel):
    """A single social media post."""
    platform: str  # e.g. "Instagram", "LinkedIn", "Twitter/X", "Facebook"
    post_type: str = "feed"  # feed, story, reel, thread, carousel
    content: str
    hashtags: list[str] = Field(default_factory=list)
    call_to_action: str
    notes: str = ""  # creative direction notes for the designer


class AdVariant(BaseModel):
    """A single ad creative variant."""
    platform: str  # "Google Ads", "Meta Ads", "LinkedIn Ads", etc.
    format: str = "standard"  # standard, carousel, video_script
    headline: str
    body: str
    call_to_action: str
    target_audience_note: str = ""  # specific audience this variant targets


class EmailCampaign(BaseModel):
    """A single email campaign."""
    name: str  # e.g. "Welcome", "Nurture - Week 1", "Conversion"
    subject_line: str
    preview_text: str
    body: str  # markdown-formatted email body
    call_to_action_text: str
    send_timing: str = ""  # e.g. "Day 1", "Day 3", "Day 7"


class LandingPageCopy(BaseModel):
    """Complete landing page copy."""
    hero_headline: str
    hero_subheadline: str
    hero_cta: str
    value_propositions: list[str]  # 3-4 bullet benefits
    social_proof_statement: str
    feature_sections: list[dict]  # [{"title": str, "body": str}]
    faq: list[dict]  # [{"question": str, "answer": str}]
    closing_headline: str
    closing_cta: str


class ImagePromptItem(BaseModel):
    """A single image generation prompt."""
    use_case: str  # e.g. "Hero Banner", "Instagram Post", "Ad Creative"
    platform: str  # where this image will be used
    prompt: str  # the full image generation prompt
    style: str  # e.g. "photorealistic", "illustration", "minimalist"
    mood: str  # e.g. "energetic", "calm", "professional"
    aspect_ratio: str = "16:9"
''')


c_content = read_file("packages/shared/models/campaign.py")
if "from packages.shared.models.assets" not in c_content:
    imports = """from packages.shared.models.assets import (
    SocialMediaPost, AdVariant, EmailCampaign, LandingPageCopy, ImagePromptItem
)
"""
    c_content = c_content.replace("from pydantic import BaseModel, Field", "from pydantic import BaseModel, Field\n\n" + imports)
    
    old_ca = """class CampaignAssets(BaseModel):
    \"\"\"AI-generated creative assets.\"\"\"
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    campaign_strategy_id: str
    social_media_posts: list[dict[str, Any]] = Field(default_factory=list)
    ad_copy: list[dict[str, Any]] = Field(default_factory=list)
    email_campaigns: list[dict[str, Any]] = Field(default_factory=list)
    landing_page_copy: Optional[dict[str, Any]] = None
    blog_posts: list[dict[str, Any]] = Field(default_factory=list)
    image_prompts: list[str] = Field(default_factory=list)
    video_storyboards: list[dict[str, Any]] = Field(default_factory=list)
    poster_concepts: list[dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))"""
    
    new_ca = """class CampaignAssets(BaseModel):
    \"\"\"AI-generated creative assets for a campaign.\"\"\"
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    campaign_strategy_id: str
    social_media_posts: list[SocialMediaPost] = Field(default_factory=list)
    ad_copy: list[AdVariant] = Field(default_factory=list)
    email_campaigns: list[EmailCampaign] = Field(default_factory=list)
    landing_page_copy: Optional[LandingPageCopy] = None
    blog_posts: list[dict[str, Any]] = Field(default_factory=list)  # Phase 5
    image_prompts: list[ImagePromptItem] = Field(default_factory=list)
    video_storyboards: list[dict[str, Any]] = Field(default_factory=list)  # Phase 5
    poster_concepts: list[dict[str, Any]] = Field(default_factory=list)  # Phase 5
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))"""

    c_content = c_content.replace(old_ca, new_ca)
    write_file("packages/shared/models/campaign.py", c_content)

i_content = read_file("packages/shared/models/__init__.py")
if "from packages.shared.models.assets" not in i_content:
    assets_import = """from packages.shared.models.assets import (
    AdVariant,
    EmailCampaign,
    ImagePromptItem,
    LandingPageCopy,
    SocialMediaPost,
)
"""
    i_content = i_content.replace("from packages.shared.models.brand", assets_import + "\nfrom packages.shared.models.brand")
    i_content = i_content.replace('    "BrandInput",', '    "AdVariant",\n    "EmailCampaign",\n    "ImagePromptItem",\n    "LandingPageCopy",\n    "SocialMediaPost",\n    "BrandInput",')
    write_file("packages/shared/models/__init__.py", i_content)

write_file("packages/prompts/creative/social_media.md", '''# Social Media Content Prompt

You are the Social Media Specialist for BrandOS, an AI Creative Operating System.

Your role is to create platform-native social media posts that feel authentic to the brand and drive the campaign objective. You understand the nuances of each platform's format, tone, and audience expectations.

## Brand Profile

```json
{{brand_profile}}
```

## Campaign Strategy

```json
{{campaign_strategy}}
```

## Requested Platforms

{{platforms}}

## Your Task

Create 3 social media posts for EACH requested platform. Each post must:

1. Match the platform's native format and character limits
2. Use the brand's exact voice, tone, and writing style
3. Reinforce one or more of the campaign's messaging pillars
4. Include relevant hashtags (5–10 per post, platform-appropriate)
5. End with a clear, compelling call to action

## Platform Guidelines

- **Instagram**: Visual-first, emoji-friendly, up to 2,200 chars. Use strong opening hook.
- **LinkedIn**: Professional, thought-leadership tone, up to 3,000 chars. Use line breaks for readability.
- **Twitter/X**: Punchy, max 280 chars for main tweet. Can include thread continuation notes.
- **Facebook**: Conversational, community-focused, up to 63,206 chars but optimal 40–80 words.

## Output Format

Respond ONLY with valid JSON. No other text.

```json
[
  {
    "platform": "Instagram",
    "post_type": "feed",
    "content": "string",
    "hashtags": ["hashtag1", "hashtag2"],
    "call_to_action": "string",
    "notes": "Creative direction: show product in use"
  }
]
```
''')

write_file("packages/prompts/creative/ad_copy.md", '''# Ad Copy Prompt

You are the Copywriter for BrandOS, an AI Creative Operating System.

Your role is to write high-converting advertisement copy. You understand direct response principles, persuasion psychology, and platform-specific ad formats. Every word is chosen intentionally.

## Brand Profile

```json
{{brand_profile}}
```

## Campaign Strategy

```json
{{campaign_strategy}}
```

## Your Task

Create 5 distinct ad variants across the following formats:
- 2× Google Search Ads (headline 30 chars max, description 90 chars max)
- 2× Meta/Social Display Ads (headline 40 chars, body 125 chars, CTA button text)
- 1× LinkedIn Sponsored Content (headline 70 chars, introductory text 150 chars)

Each variant must:
1. Lead with the single strongest benefit or hook for the target audience
2. Use the brand's tone and voice (do not use a generic corporate voice)
3. Align with one or more messaging pillars from the campaign strategy
4. Include a clear, action-oriented CTA
5. Be different enough from the other variants to genuinely test different angles

## Output Format

Respond ONLY with valid JSON. No other text.

```json
[
  {
    "platform": "Google Ads",
    "format": "search",
    "headline": "string (max 30 chars)",
    "body": "string (max 90 chars)",
    "call_to_action": "string",
    "target_audience_note": "string"
  }
]
```
''')

write_file("packages/prompts/creative/email_specialist.md", '''# Email Campaign Prompt

You are the Email Specialist for BrandOS, an AI Creative Operating System.

Your role is to write a sequence of marketing emails that move the reader from awareness to action. You understand email deliverability, open rate optimization, and persuasive email structure.

## Brand Profile

```json
{{brand_profile}}
```

## Campaign Strategy

```json
{{campaign_strategy}}
```

## Your Task

Create a 3-email campaign sequence:

1. **Awareness Email** — Introduces the campaign concept. No hard sell. Builds curiosity and brand affinity.
2. **Value Email** — Delivers concrete value (tips, insights, or a compelling story). Positions the brand as the solution.
3. **Conversion Email** — Direct call to action. Urgency if appropriate. Clear offer.

For each email:
- Write a subject line that earns the open (avoid spam triggers)
- Write preview text that complements (not repeats) the subject
- Write the full email body in markdown (use **bold**, bullet points, short paragraphs)
- End with a single, prominent CTA
- Specify optimal send timing

## Output Format

Respond ONLY with valid JSON. No other text.

```json
[
  {
    "name": "Awareness",
    "subject_line": "string",
    "preview_text": "string",
    "body": "markdown string",
    "call_to_action_text": "string",
    "send_timing": "Day 1"
  }
]
```
''')

write_file("packages/prompts/creative/landing_page.md", '''# Landing Page Copy Prompt

You are the Copywriter (Landing Page Specialist) for BrandOS, an AI Creative Operating System.

Your role is to write a complete, high-converting landing page for this campaign. You understand above-the-fold impact, the F-pattern reading behavior, and conversion rate optimization principles.

## Brand Profile

```json
{{brand_profile}}
```

## Campaign Strategy

```json
{{campaign_strategy}}
```

## Your Task

Write complete landing page copy with these sections:

1. **Hero Section** — A powerful headline (max 10 words), supporting subheadline (max 20 words), and primary CTA button text
2. **Value Propositions** — 4 concise benefit statements (not features), each max 15 words
3. **Social Proof** — One compelling social proof statement (could be a stat, testimonial format, or trust signal)
4. **Feature Sections** — 3 content sections, each with a title and 2-3 sentence description
5. **FAQ** — 4 frequently asked questions with answers (2-3 sentences each)
6. **Closing Section** — Final headline and CTA to capture hesitant visitors

## Copywriting Rules

- Hero headline: lead with transformation or outcome, not product name
- Use "you" language throughout, not "we" or "our product"
- Benefits before features
- Active voice
- No jargon unless the brand uses it

## Output Format

Respond ONLY with valid JSON. No other text.

```json
{
  "hero_headline": "string",
  "hero_subheadline": "string",
  "hero_cta": "string",
  "value_propositions": ["string"],
  "social_proof_statement": "string",
  "feature_sections": [{"title": "string", "body": "string"}],
  "faq": [{"question": "string", "answer": "string"}],
  "closing_headline": "string",
  "closing_cta": "string"
}
```
''')

write_file("packages/prompts/creative/image_prompts.md", '''# Image Prompt Generation Prompt

You are the Creative Director (Visual) for BrandOS, an AI Creative Operating System.

Your role is to write detailed prompts for AI image generation tools (Midjourney, DALL-E, Stable Diffusion). Each prompt should produce a campaign-consistent visual that a marketing team can use directly.

## Brand Profile

```json
{{brand_profile}}
```

## Campaign Strategy

```json
{{campaign_strategy}}
```

## Your Task

Create 6 distinct image generation prompts for this campaign:

1. Hero Banner (16:9) — Main campaign visual
2. Social Media Square (1:1) — Instagram/Facebook feed image
3. Social Story (9:16) — Instagram/TikTok story visual
4. Ad Creative (4:3) — Display ad image
5. Email Header (2:1) — Top of email banner
6. LinkedIn Banner (4:1) — LinkedIn post image

For each prompt:
- Be specific about subject matter, setting, lighting, and composition
- Specify the visual style that matches the brand
- Include mood/atmosphere keywords
- End with technical quality modifiers (e.g., "professional photography, 4K, sharp focus")
- Do NOT include any text or logos in the image prompts

## Output Format

Respond ONLY with valid JSON. No other text.

```json
[
  {
    "use_case": "Hero Banner",
    "platform": "Website / All Channels",
    "prompt": "full image generation prompt string",
    "style": "photorealistic",
    "mood": "energetic and optimistic",
    "aspect_ratio": "16:9"
  }
]
```
''')

write_file("packages/agents/base.py", '''"""
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
''')

write_file("packages/agents/social_media_agent.py", '''"""
SocialMediaAgent — generates platform-native social media posts.

Single responsibility: receive BrandProfile + CampaignStrategy + platforms list,
return a list of SocialMediaPost objects.
"""
from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel

from packages.agents.base import BaseAgent
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

        try:
            prompt = self._prompt_loader.load(
                self.PROMPT_TEMPLATE,
                brand_profile=json.dumps(brand_profile.model_dump(mode="json"), indent=2),
                campaign_strategy=json.dumps(campaign_strategy.model_dump(mode="json"), indent=2),
                platforms=platforms_str,
            )
            # Wrap in an object so complete_structured can parse the list
            raw = await self._llm_client.complete(
                prompt=prompt,
                system_prompt="You are a professional social media copywriter. Respond only with valid JSON array.",
            )
            # Parse the raw JSON array
            cleaned = raw.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\\n", 1)[1].rsplit("```", 1)[0].strip()
            import json as _json
            items = _json.loads(cleaned)
            return [SocialMediaPost.model_validate(item) for item in items]
        except LLMError as exc:
            raise OrchestrationError(
                "SocialMediaAgent failed to generate posts",
                detail=str(exc),
            ) from exc
        except Exception as exc:
            raise OrchestrationError(
                "SocialMediaAgent failed to parse LLM output",
                detail=str(exc),
            ) from exc
''')

write_file("packages/agents/copywriter_agent.py", '''"""
CopywriterAgent — generates high-converting ad variants.
"""
from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel

from packages.agents.base import BaseAgent
from packages.shared.errors import LLMError, OrchestrationError
from packages.shared.models.assets import AdVariant
from packages.shared.models.brand import BrandProfile
from packages.shared.models.campaign import CampaignStrategy


class CopywriterAgent(BaseAgent):
    """Generates ad variants across multiple platforms."""

    PROMPT_TEMPLATE = "creative/ad_copy"

    async def generate(
        self,
        brand_profile: BrandProfile,
        campaign_strategy: CampaignStrategy,
        **kwargs: Any,
    ) -> list[AdVariant]:
        """Generate ad copy variants.

        Args:
            brand_profile: The brand identity.
            campaign_strategy: The approved campaign strategy.

        Returns:
            A list of AdVariant objects.

        Raises:
            OrchestrationError: If the LLM fails to generate valid ad copy.
        """
        self._logger.info("Generating ad copy variants")

        try:
            prompt = self._prompt_loader.load(
                self.PROMPT_TEMPLATE,
                brand_profile=json.dumps(brand_profile.model_dump(mode="json"), indent=2),
                campaign_strategy=json.dumps(campaign_strategy.model_dump(mode="json"), indent=2),
            )
            raw = await self._llm_client.complete(
                prompt=prompt,
                system_prompt="You are a professional copywriter. Respond only with valid JSON array.",
            )
            cleaned = raw.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\\n", 1)[1].rsplit("```", 1)[0].strip()
            import json as _json
            items = _json.loads(cleaned)
            return [AdVariant.model_validate(item) for item in items]
        except LLMError as exc:
            raise OrchestrationError(
                "CopywriterAgent failed to generate ad variants",
                detail=str(exc),
            ) from exc
        except Exception as exc:
            raise OrchestrationError(
                "CopywriterAgent failed to parse LLM output",
                detail=str(exc),
            ) from exc
''')

write_file("packages/agents/email_specialist_agent.py", '''"""
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
                cleaned = cleaned.split("\\n", 1)[1].rsplit("```", 1)[0].strip()
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
''')

write_file("packages/agents/landing_page_agent.py", '''"""
LandingPageAgent — generates full landing page copy.
"""
from __future__ import annotations

import json
from typing import Any

from packages.agents.base import BaseAgent
from packages.shared.errors import LLMError, OrchestrationError
from packages.shared.models.assets import LandingPageCopy
from packages.shared.models.brand import BrandProfile
from packages.shared.models.campaign import CampaignStrategy


class LandingPageAgent(BaseAgent):
    """Generates complete landing page copy."""

    PROMPT_TEMPLATE = "creative/landing_page"

    async def generate(
        self,
        brand_profile: BrandProfile,
        campaign_strategy: CampaignStrategy,
        **kwargs: Any,
    ) -> LandingPageCopy:
        """Generate landing page copy.

        Args:
            brand_profile: The brand identity.
            campaign_strategy: The approved campaign strategy.

        Returns:
            A single LandingPageCopy object.

        Raises:
            OrchestrationError: If the LLM fails to generate valid landing page copy.
        """
        self._logger.info("Generating landing page copy")

        try:
            prompt = self._prompt_loader.load(
                self.PROMPT_TEMPLATE,
                brand_profile=json.dumps(brand_profile.model_dump(mode="json"), indent=2),
                campaign_strategy=json.dumps(campaign_strategy.model_dump(mode="json"), indent=2),
            )
            
            result = await self._llm_client.complete_structured(
                prompt=prompt,
                response_model=LandingPageCopy,
                system_prompt="You are a professional landing page copywriter. Respond only with valid JSON.",
            )
            return result
        except LLMError as exc:
            raise OrchestrationError(
                "LandingPageAgent failed to generate landing page copy",
                detail=str(exc),
            ) from exc
        except Exception as exc:
            raise OrchestrationError(
                "LandingPageAgent failed to parse LLM output",
                detail=str(exc),
            ) from exc
''')

write_file("packages/agents/image_prompt_agent.py", '''"""
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
                cleaned = cleaned.split("\\n", 1)[1].rsplit("```", 1)[0].strip()
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
''')

write_file("packages/agents/service.py", '''"""
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
''')

write_file("packages/agents/__init__.py", '''"""BrandOS Creative Agents — Phase 3.

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
''')

write_file("apps/api/routers/assets.py", '''"""
Assets router — POST /api/campaigns/{id}/assets

This endpoint triggers creative asset generation for an existing campaign
that already has a strategy (status='complete').

Separating asset generation from campaign creation allows the user to:
1. Review the strategy first
2. Decide if they want to proceed with asset generation
3. Regenerate assets without changing the strategy
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from apps.api.dependencies import CreativeServiceDep, PlanningServiceDep
from packages.shared.errors import OrchestrationError
from packages.shared.models.campaign import CampaignPackage
from packages.workflows.campaign_store import CampaignNotFoundError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/campaigns", tags=["assets"])


class AssetGenerationResponse(BaseModel):
    campaign: CampaignPackage


@router.post("/{campaign_id}/assets", response_model=AssetGenerationResponse)
async def generate_assets(
    campaign_id: str,
    planning_service: PlanningServiceDep,
    creative_service: CreativeServiceDep,
) -> AssetGenerationResponse:
    """Generate creative assets for an existing campaign.

    The campaign must already have a strategy (status='complete').
    Returns the updated CampaignPackage with populated campaign_assets.
    """
    # Retrieve campaign
    try:
        package = await planning_service.get_campaign(campaign_id)
    except CampaignNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.message) from exc

    # Validate state
    if package.status != "complete" or package.campaign_strategy is None:
        raise HTTPException(
            status_code=409,
            detail=f"Campaign must have a completed strategy before generating assets. Current status: {package.status}",
        )

    # Generate assets
    try:
        channels = package.campaign_brief.channels
        assets = await creative_service.generate_assets(
            brand_profile=package.brand_profile,
            campaign_strategy=package.campaign_strategy,
            channels=channels,
        )
    except OrchestrationError as exc:
        logger.error("Asset generation failed for campaign %s: %s", campaign_id, exc)
        raise HTTPException(
            status_code=422,
            detail={"error": "asset_generation_failed", "message": exc.message},
        ) from exc
    except Exception as exc:
        logger.exception("Unexpected error generating assets for campaign %s", campaign_id)
        raise HTTPException(status_code=500, detail="Internal server error during asset generation") from exc

    # Update the package with assets
    from datetime import datetime, timezone
    updated_package = package.model_copy(
        update={"campaign_assets": assets, "updated_at": datetime.now(timezone.utc)}
    )
    await planning_service._store.save(updated_package)

    return AssetGenerationResponse(campaign=updated_package)
''')

d_content = read_file("apps/api/dependencies.py")
if "CreativeService" not in d_content:
    new_dep = """
# ── CreativeService ───────────────────────────────────────────────────────────
from packages.agents.service import CreativeService

@lru_cache(maxsize=1)
def _get_creative_service_singleton() -> CreativeService:
    return CreativeService()

def get_creative_service() -> CreativeService:
    \"\"\"Dependency provider for CreativeService.\"\"\"
    return _get_creative_service_singleton()

CreativeServiceDep = Annotated[CreativeService, Depends(get_creative_service)]
"""
    d_content += new_dep
    write_file("apps/api/dependencies.py", d_content)

m_content = read_file("apps/api/main.py")
if "assets" not in m_content:
    m_content = m_content.replace("from apps.api.routers import campaigns, health, knowledge", "from apps.api.routers import campaigns, health, knowledge, assets")
    m_content = m_content.replace("app.include_router(campaigns.router)", "app.include_router(campaigns.router)\napp.include_router(assets.router)")
    write_file("apps/api/main.py", m_content)

