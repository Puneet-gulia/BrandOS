"""
EvaluationService — public facade for the Evaluation Layer.

Mirrors the pattern established by KnowledgeService and PlanningService:
- All internal wiring hidden from callers
- Single public method: evaluate_campaign()
- Injects into routers via FastAPI's Depends() mechanism
"""
from __future__ import annotations

import logging

from packages.evaluations.evaluator import QualityEvaluator
from packages.shared.errors import OrchestrationError
from packages.shared.models.campaign import CampaignAssets, CampaignStrategy
from packages.shared.models.brand import BrandProfile
from packages.shared.models.evaluation import QualityReport
from packages.tools.llm_client import LLMClient
from packages.tools.prompt_loader import PromptLoader

logger = logging.getLogger(__name__)


class EvaluationService:
    """Facade for the Evaluation Layer.

    Wires QualityEvaluator with the shared LLM client and prompt loader.
    The API router calls only this class — never QualityEvaluator directly.

    Usage:
        service = EvaluationService()
        report = await service.evaluate_campaign(brand_profile, strategy, assets)
    """

    def __init__(self) -> None:
        llm_client = LLMClient()
        prompt_loader = PromptLoader()
        self._evaluator = QualityEvaluator(llm_client, prompt_loader)

    async def evaluate_campaign(
        self,
        brand_profile: BrandProfile,
        campaign_strategy: CampaignStrategy,
        campaign_assets: CampaignAssets,
    ) -> QualityReport:
        """Evaluate the quality of generated campaign assets.

        Args:
            brand_profile: The brand identity to evaluate against.
            campaign_strategy: The approved strategy the assets should fulfil.
            campaign_assets: The generated assets to evaluate.

        Returns:
            A QualityReport with scores for all 6 evaluation dimensions,
            plus overall_score and passed (computed fields on QualityReport).

        Raises:
            OrchestrationError: If the evaluation LLM call fails.
        """
        logger.info(
            "EvaluationService: evaluating campaign_assets_id=%s",
            campaign_assets.id[:8],
        )
        return await self._evaluator.evaluate(
            brand_profile=brand_profile,
            campaign_strategy=campaign_strategy,
            campaign_assets=campaign_assets,
        )
