"""Campaign data models."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Any, Optional

from pydantic import BaseModel, Field

from packages.shared.models.assets import (
    SocialMediaPost, AdVariant, EmailCampaign, LandingPageCopy, ImagePromptItem
)

if TYPE_CHECKING:
    from packages.shared.models.evaluation import QualityReport


from packages.shared.models.brand import BrandProfile


class MarketingChannel(str, Enum):
    """Marketing channels for a campaign."""
    SOCIAL_MEDIA = "SOCIAL_MEDIA"
    EMAIL = "EMAIL"
    PAID_ADS = "PAID_ADS"
    LANDING_PAGE = "LANDING_PAGE"
    BLOG = "BLOG"
    VIDEO = "VIDEO"
    PRINT = "PRINT"


class CampaignBrief(BaseModel):
    """User-provided brief for a new campaign."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    brand_profile_id: str
    objective: str
    target_audience: list[str]
    channels: list[MarketingChannel]
    budget_range: Optional[str] = None
    timeline_weeks: Optional[int] = None
    constraints: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CampaignStrategy(BaseModel):
    """AI-generated strategy based on the brief."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    campaign_brief_id: str
    campaign_name: str
    positioning_statement: str
    messaging_pillars: list[str]
    key_themes: list[str]
    channel_strategy: dict[str, str]
    content_calendar_weeks: int
    success_metrics: list[str]
    rationale: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CampaignAssets(BaseModel):
    """AI-generated creative assets for a campaign."""
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
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CampaignPackage(BaseModel):
    """The complete generated campaign."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    brand_profile: BrandProfile
    campaign_brief: CampaignBrief
    campaign_strategy: Optional[CampaignStrategy] = None
    campaign_assets: Optional[CampaignAssets] = None
    quality_report: Optional[QualityReport] = None  # type: ignore[name-defined]
    status: str = "draft"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
