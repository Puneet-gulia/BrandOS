"""Canonical data models for BrandOS.

All inter-layer communication uses these models. No layer should define
its own data structures for shared concepts.
"""

from packages.shared.models.assets import (
    AdVariant,
    EmailCampaign,
    ImagePromptItem,
    LandingPageCopy,
    SocialMediaPost,
)

from packages.shared.models.brand import BrandInput, BrandInputType, BrandProfile
from packages.shared.models.campaign import (
    CampaignAssets,
    CampaignBrief,
    CampaignPackage,
    CampaignStrategy,
    MarketingChannel,
)
from packages.shared.models.evaluation import EvaluationDimension, QualityReport, QualityScore

__all__ = [
    "AdVariant",
    "EmailCampaign",
    "ImagePromptItem",
    "LandingPageCopy",
    "SocialMediaPost",
    "BrandInput",
    "BrandInputType",
    "BrandProfile",
    "CampaignBrief",
    "CampaignStrategy",
    "CampaignAssets",
    "CampaignPackage",
    "MarketingChannel",
    "QualityScore",
    "QualityReport",
    "EvaluationDimension",
]
