"""Evaluation data models."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, computed_field


class EvaluationDimension(str, Enum):
    """Dimensions for evaluating creative assets."""
    BRAND_CONSISTENCY = "BRAND_CONSISTENCY"
    GRAMMAR = "GRAMMAR"
    COMPLETENESS = "COMPLETENESS"
    TONE = "TONE"
    READABILITY = "READABILITY"
    SEO = "SEO"


class QualityScore(BaseModel):
    """Score for a specific evaluation dimension."""
    dimension: EvaluationDimension
    score: float = Field(ge=0.0, le=1.0)
    passed: bool
    feedback: str
    suggestions: list[str] = Field(default_factory=list)


class QualityReport(BaseModel):
    """Complete quality evaluation report."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    campaign_assets_id: str
    scores: list[QualityScore]
    recommendations: list[str]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @computed_field
    def overall_score(self) -> float:
        """Average of all dimension scores."""
        if not self.scores:
            return 0.0
        return sum(s.score for s in self.scores) / len(self.scores)

    @computed_field
    def passed(self) -> bool:
        """True if overall score is passing."""
        return self.overall_score >= 0.7
