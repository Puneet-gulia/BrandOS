"""
QualityEvaluator — Evaluation Layer agent.

Single responsibility: receive CampaignAssets + BrandProfile + CampaignStrategy,
evaluate the assets across 6 quality dimensions, and return a QualityReport.

This agent NEVER generates marketing content.
It ONLY evaluates content that has already been generated.

Design notes:
- Sends a representative *sample* of the assets rather than all content.
  This keeps the context window manageable while covering all asset types.
- The sample is constructed deterministically (first N items per category).
- All 6 EvaluationDimension values are always evaluated, even if some asset
  types are empty (those dimensions will score lower as a result).
"""
from __future__ import annotations

import json
import logging
from typing import Optional

from pydantic import BaseModel, Field

from packages.shared.errors import LLMError, OrchestrationError
from packages.shared.models.brand import BrandProfile
from packages.shared.models.campaign import CampaignAssets, CampaignStrategy
from packages.shared.models.evaluation import EvaluationDimension, QualityReport, QualityScore
from packages.tools.llm_client import LLMClient
from packages.tools.prompt_loader import PromptLoader

logger = logging.getLogger(__name__)

# Maximum characters of asset content to include in the evaluation sample.
# Keeps the prompt under typical context window limits.
_MAX_SAMPLE_CHARS = 6000


class _QualityScoreLLMOutput(BaseModel):
    """Matches the per-score object returned by the LLM."""

    dimension: str
    score: float = Field(ge=0.0, le=1.0)
    passed: bool
    feedback: str
    suggestions: list[str] = Field(default_factory=list)


class _QualityReportLLMOutput(BaseModel):
    """Top-level shape of the LLM JSON response for evaluation."""

    scores: list[_QualityScoreLLMOutput]
    recommendations: list[str]


class QualityEvaluator:
    """Evaluation Layer agent.

    Evaluates a complete CampaignAssets bundle against the brand profile
    and campaign strategy. Returns a structured QualityReport with
    per-dimension scores, feedback, and recommendations.

    Args:
        llm_client: The shared LLM client.
        prompt_loader: The prompt loader for evaluation templates.
    """

    PROMPT_TEMPLATE = "evaluation/quality_evaluator"

    def __init__(self, llm_client: LLMClient, prompt_loader: PromptLoader) -> None:
        self._llm_client = llm_client
        self._prompt_loader = prompt_loader

    async def evaluate(
        self,
        brand_profile: BrandProfile,
        campaign_strategy: CampaignStrategy,
        campaign_assets: CampaignAssets,
    ) -> QualityReport:
        """Evaluate the quality of generated campaign assets.

        Args:
            brand_profile: The brand identity to evaluate against.
            campaign_strategy: The strategic intent to evaluate against.
            campaign_assets: The generated assets to evaluate.

        Returns:
            A QualityReport with per-dimension scores and recommendations.

        Raises:
            OrchestrationError: If the LLM fails to return a valid evaluation.
        """
        logger.info(
            "Evaluating assets for strategy=%s assets=%s",
            campaign_strategy.id[:8],
            campaign_assets.id[:8],
        )

        assets_sample = self._build_assets_sample(campaign_assets)
        brand_json = json.dumps(brand_profile.model_dump(mode="json"), indent=2)
        strategy_json = json.dumps(campaign_strategy.model_dump(mode="json"), indent=2)

        try:
            prompt = self._prompt_loader.load(
                self.PROMPT_TEMPLATE,
                brand_profile=brand_json,
                campaign_strategy=strategy_json,
                assets_sample=assets_sample,
            )

            llm_output = await self._llm_client.complete_structured(
                prompt=prompt,
                response_model=_QualityReportLLMOutput,
                system_prompt=(
                    "You are a senior brand editor and quality evaluator. "
                    "Respond only with valid JSON. Be specific and evidence-based in all feedback."
                ),
            )
        except LLMError as exc:
            raise OrchestrationError(
                "QualityEvaluator failed — LLM returned an error",
                detail=str(exc),
            ) from exc

        return self._build_quality_report(llm_output, campaign_assets.id)

    # ── Private helpers ────────────────────────────────────────────────────────

    @staticmethod
    def _build_assets_sample(assets: CampaignAssets) -> str:
        """Build a JSON summary of the assets for the evaluation prompt.

        Takes a representative sample from each populated asset type to keep
        the prompt within context window limits while covering all dimensions.
        """
        sample: dict = {
            "social_media_posts": [],
            "ad_copy": [],
            "email_campaigns": [],
            "landing_page_copy": None,
            "image_prompts": [],
        }

        # Take up to 2 items from each list type (enough to evaluate quality)
        if assets.social_media_posts:
            sample["social_media_posts"] = [
                p.model_dump(mode="json") for p in assets.social_media_posts[:2]
            ]

        if assets.ad_copy:
            sample["ad_copy"] = [
                a.model_dump(mode="json") for a in assets.ad_copy[:2]
            ]

        if assets.email_campaigns:
            sample["email_campaigns"] = [
                e.model_dump(mode="json") for e in assets.email_campaigns[:2]
            ]

        if assets.landing_page_copy:
            # For the LP, include hero + value props + first feature section
            lp = assets.landing_page_copy
            sample["landing_page_copy"] = {
                "hero_headline": lp.hero_headline,
                "hero_subheadline": lp.hero_subheadline,
                "hero_cta": lp.hero_cta,
                "value_propositions": lp.value_propositions,
                "social_proof_statement": lp.social_proof_statement,
                "feature_sections": lp.feature_sections[:2],
                "faq": lp.faq[:2],
                "closing_headline": lp.closing_headline,
            }

        if assets.image_prompts:
            sample["image_prompts"] = [
                p.model_dump(mode="json") for p in assets.image_prompts[:2]
            ]

        sample_json = json.dumps(sample, indent=2)

        # Truncate if over the character limit
        if len(sample_json) > _MAX_SAMPLE_CHARS:
            sample_json = sample_json[:_MAX_SAMPLE_CHARS] + "\n... [truncated for context]\n}"

        return sample_json

    @staticmethod
    def _build_quality_report(
        llm_output: _QualityReportLLMOutput,
        campaign_assets_id: str,
    ) -> QualityReport:
        """Map the LLM output to the canonical QualityReport model."""
        scores: list[QualityScore] = []

        # Track which dimensions the LLM covered
        covered_dimensions: set[str] = set()

        for raw_score in llm_output.scores:
            try:
                dimension = EvaluationDimension(raw_score.dimension)
            except ValueError:
                logger.warning(
                    "LLM returned unknown dimension %r — skipping", raw_score.dimension
                )
                continue

            covered_dimensions.add(raw_score.dimension)
            scores.append(
                QualityScore(
                    dimension=dimension,
                    score=raw_score.score,
                    # Recompute 'passed' from score rather than trusting the LLM
                    passed=raw_score.score >= 0.70,
                    feedback=raw_score.feedback,
                    suggestions=raw_score.suggestions,
                )
            )

        # If the LLM missed any dimensions, add a neutral placeholder score
        all_dimensions = {d.value for d in EvaluationDimension}
        for missing in all_dimensions - covered_dimensions:
            logger.warning("LLM did not score dimension %r — adding neutral score", missing)
            scores.append(
                QualityScore(
                    dimension=EvaluationDimension(missing),
                    score=0.5,
                    passed=False,
                    feedback="This dimension was not evaluated by the LLM.",
                    suggestions=["Re-run evaluation to score this dimension."],
                )
            )

        return QualityReport(
            campaign_assets_id=campaign_assets_id,
            scores=scores,
            recommendations=llm_output.recommendations,
        )
