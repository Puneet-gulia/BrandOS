"""
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
