"""
Typed models for BrandOS creative assets.

Each model represents the structured output of one creative agent.
Using typed models instead of dict[str, Any] gives us validation,
autocompletion, and serialization guarantees throughout the system.
"""
from __future__ import annotations
from typing import Any
from pydantic import BaseModel, Field, model_validator


class SocialMediaPost(BaseModel):
    """A single social media post."""
    platform: str = "Social Media"
    post_type: str = "feed"
    content: str = ""
    hashtags: list[str] = Field(default_factory=list)
    call_to_action: str = ""
    notes: str = ""

    @model_validator(mode="before")
    @classmethod
    def normalize_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Normalize common LLM key aliases
            if "text" in data and not data.get("content"):
                data["content"] = data["text"]
            if "post" in data and not data.get("content"):
                data["content"] = data["post"]
            if "cta" in data and not data.get("call_to_action"):
                data["call_to_action"] = data["cta"]
        return data


class AdVariant(BaseModel):
    """A single ad creative variant."""
    platform: str = "Google Ads"
    format: str = "standard"
    headline: str = ""
    body: str = ""
    call_to_action: str = ""
    target_audience_note: str = ""

    @model_validator(mode="before")
    @classmethod
    def normalize_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Normalize common LLM key aliases for body text
            for alias in ["description", "text", "introductory_text", "copy", "main_text"]:
                if alias in data and not data.get("body"):
                    data["body"] = str(data[alias])
            if "title" in data and not data.get("headline"):
                data["headline"] = str(data["title"])
            if "cta" in data and not data.get("call_to_action"):
                data["call_to_action"] = str(data["cta"])
        return data


class EmailCampaign(BaseModel):
    """A single email campaign."""
    name: str = "Campaign"
    subject_line: str = ""
    preview_text: str = ""
    body: str = ""
    call_to_action_text: str = ""
    send_timing: str = ""

    @model_validator(mode="before")
    @classmethod
    def normalize_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "subject" in data and not data.get("subject_line"):
                data["subject_line"] = str(data["subject"])
            if "content" in data and not data.get("body"):
                data["body"] = str(data["content"])
            if "cta" in data and not data.get("call_to_action_text"):
                data["call_to_action_text"] = str(data["cta"])
        return data


class LandingPageCopy(BaseModel):
    """Complete landing page copy."""
    hero_headline: str = ""
    hero_subheadline: str = ""
    hero_cta: str = ""
    value_propositions: list[str] = Field(default_factory=list)
    social_proof_statement: str = ""
    feature_sections: list[dict[str, Any]] = Field(default_factory=list)
    faq: list[dict[str, Any]] = Field(default_factory=list)
    closing_headline: str = ""
    closing_cta: str = ""


class ImagePromptItem(BaseModel):
    """A single image generation prompt."""
    use_case: str = "General"
    platform: str = "All Channels"
    prompt: str = ""
    style: str = "photorealistic"
    mood: str = "professional"
    aspect_ratio: str = "16:9"
