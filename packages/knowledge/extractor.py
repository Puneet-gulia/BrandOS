"""Orchestrates brand profile extraction."""
import logging

from packages.knowledge.llm_extractor import LLMBrandExtractor
from packages.knowledge.scrapers.document_parser import DocumentParser
from packages.knowledge.scrapers.web_scraper import WebScraper
from packages.shared.errors import ExtractionError
from packages.shared.models.brand import BrandInput, BrandInputType, BrandProfile

logger = logging.getLogger(__name__)


class BrandExtractor:
    """Orchestrator for extracting brand profiles from various inputs."""

    def __init__(
        self,
        web_scraper: WebScraper,
        document_parser: DocumentParser,
        llm_extractor: LLMBrandExtractor,
    ) -> None:
        self.web_scraper = web_scraper
        self.document_parser = document_parser
        self.llm_extractor = llm_extractor

    async def extract(self, brand_input: BrandInput) -> BrandProfile:
        """Extract a brand profile based on the input type.
        
        Args:
            brand_input: The input configuration (URL, TEXT, or DOCUMENT).
            
        Returns:
            The extracted BrandProfile.
            
        Raises:
            ExtractionError: If extraction fails at any step.
        """
        raw_text = ""
        
        try:
            if brand_input.input_type == BrandInputType.URL:
                if not brand_input.url:
                    raise ExtractionError("URL is required for URL input type")
                raw_text = await self.web_scraper.scrape(brand_input.url)
                
            elif brand_input.input_type == BrandInputType.TEXT:
                if not brand_input.text:
                    raise ExtractionError("Text is required for TEXT input type")
                raw_text = brand_input.text
                
            elif brand_input.input_type == BrandInputType.DOCUMENT:
                if not brand_input.document_content:
                    raise ExtractionError("Document content is required for DOCUMENT input type")
                # In Phase 1, we expect document_content to hold the raw text for direct processing
                # Document bytes parsing is handled at the API/Service level before creating BrandInput
                raw_text = brand_input.document_content
                
            else:
                raise ExtractionError(f"Unsupported input type: {brand_input.input_type}")
                
            if not raw_text.strip():
                raise ExtractionError("Extracted text is empty")
                
            return await self.llm_extractor.extract(raw_text)
            
        except ExtractionError:
            raise
        except Exception as exc:
            raise ExtractionError("Unexpected error during brand extraction", detail=str(exc)) from exc
