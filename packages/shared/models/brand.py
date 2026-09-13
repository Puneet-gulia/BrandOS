"""Brand data models."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class BrandInputType(str, Enum):
    """Type of brand input provided."""
    URL = "URL"
    TEXT = "TEXT"
    DOCUMENT = "DOCUMENT"


class BrandInput(BaseModel):
    """Input for brand knowledge extraction."""
    input_type: BrandInputType
    url: Optional[str] = None
    text: Optional[str] = None
    document_filename: Optional[str] = None
    document_content: Optional[str] = None

    @model_validator(mode="after")
    def validate_input(self) -> BrandInput:
        if self.input_type == BrandInputType.URL and not self.url:
            raise ValueError("url must be provided when input_type is URL")
        if self.input_type == BrandInputType.TEXT and not self.text:
            raise ValueError("text must be provided when input_type is TEXT")
        if self.input_type == BrandInputType.DOCUMENT and not self.document_content:
            raise ValueError("document_content must be provided when input_type is DOCUMENT")
        return self


class BrandProfile(BaseModel):
    """Extracted brand profile."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    company_name: str
    tagline: Optional[str] = None
    brand_voice: list[str]
    writing_style: list[str]
    target_audience: list[str]
    industry: str
    keywords: list[str]
    core_values: list[str]
    unique_selling_proposition: str
    tone: str
    competitors: list[str] = Field(default_factory=list)
    raw_input_summary: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
