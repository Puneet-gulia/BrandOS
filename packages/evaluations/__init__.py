"""BrandOS Evaluation Layer — Phase 4.

Scores generated assets against the BrandProfile across 6 dimensions:
- BRAND_CONSISTENCY — does the copy match the brand voice and values?
- GRAMMAR           — correct spelling, punctuation, sentence structure?
- COMPLETENESS      — all requested asset types present and developed?
- TONE              — matches the intended emotional register?
- READABILITY       — appropriate for the target audience?
- SEO               — keywords present and headlines optimised?

All scores are 0.0–1.0. Pass threshold is 0.70.
This layer NEVER generates content — it only evaluates.
"""

from packages.evaluations.evaluator import QualityEvaluator
from packages.evaluations.service import EvaluationService

__all__ = ["QualityEvaluator", "EvaluationService"]

