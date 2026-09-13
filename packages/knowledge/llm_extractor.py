"""LLM-based brand profile extraction."""
import logging
from typing import Optional

from pydantic import BaseModel

from packages.shared.errors import ExtractionError, LLMError
from packages.shared.models.brand import BrandProfile
from packages.tools.llm_client import LLMClient
from packages.tools.prompt_loader import PromptLoader

logger = logging.getLogger(__name__)


class BrandProfileLLMOutput(BaseModel):
    """Pydantic model matching the LLM output schema for brand extraction."""
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
    competitors: list[str] = []
    raw_input_summary: str


class LLMBrandExtractor:
    """Uses LLM to extract a BrandProfile from raw text."""

    def __init__(self, llm_client: LLMClient, prompt_loader: PromptLoader) -> None:
        self.llm_client = llm_client
        self.prompt_loader = prompt_loader

    async def extract(self, raw_content: str, company_hint: Optional[str] = None) -> BrandProfile:
        """Extract brand profile from raw text.
        
        Args:
            raw_content: The text to analyze.
            company_hint: Optional hint about the company name.
            
        Returns:
            A complete BrandProfile.
            
        Raises:
            ExtractionError: If the LLM extraction fails.
        """
        try:
            prompt = self.prompt_loader.load("knowledge/brand_extraction", raw_content=raw_content)
            
            output = await self.llm_client.complete_structured(
                prompt=prompt,
                response_model=BrandProfileLLMOutput,
            )
            
            # Map to the final BrandProfile (generates ID and created_at)
            return BrandProfile(
                company_name=output.company_name,
                tagline=output.tagline,
                brand_voice=output.brand_voice,
                writing_style=output.writing_style,
                target_audience=output.target_audience,
                industry=output.industry,
                keywords=output.keywords,
                core_values=output.core_values,
                unique_selling_proposition=output.unique_selling_proposition,
                tone=output.tone,
                competitors=output.competitors,
                raw_input_summary=output.raw_input_summary,
            )
        except LLMError as exc:
            raise ExtractionError("Failed to extract brand profile using LLM", detail=str(exc)) from exc
