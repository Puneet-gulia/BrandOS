"""Knowledge Layer service facade."""
import logging
from typing import Optional

from packages.knowledge.extractor import BrandExtractor
from packages.knowledge.llm_extractor import LLMBrandExtractor
from packages.knowledge.scrapers.document_parser import DocumentParser
from packages.knowledge.scrapers.web_scraper import WebScraper
from packages.shared.config import Settings, get_settings
from packages.shared.models.brand import BrandInput, BrandInputType, BrandProfile
from packages.tools.llm_client import LLMClient
from packages.tools.prompt_loader import PromptLoader

logger = logging.getLogger(__name__)


class KnowledgeService:
    """Facade for all Knowledge Layer operations."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings or get_settings()
        self._llm_client = LLMClient()
        self._prompt_loader = PromptLoader()
        self._web_scraper = WebScraper()
        self._document_parser = DocumentParser()
        self._llm_extractor = LLMBrandExtractor(self._llm_client, self._prompt_loader)
        self._brand_extractor = BrandExtractor(
            self._web_scraper, self._document_parser, self._llm_extractor
        )

    async def extract_brand_profile(self, brand_input: BrandInput) -> BrandProfile:
        """Extract a brand profile from a generic BrandInput.
        
        Args:
            brand_input: The configuration for extraction.
            
        Returns:
            The extracted BrandProfile.
        """
        logger.info("Extracting brand profile for input type %s", brand_input.input_type)
        return await self._brand_extractor.extract(brand_input)

    async def extract_from_document(
        self, filename: str, content_bytes: bytes, extra_context: Optional[str] = None
    ) -> BrandProfile:
        """Extract a brand profile from a raw document upload.
        
        Args:
            filename: The name of the uploaded file.
            content_bytes: The raw file bytes.
            extra_context: Optional additional context to append to the extracted text.
            
        Returns:
            The extracted BrandProfile.
        """
        logger.info("Extracting brand profile from document: %s", filename)
        parsed_text = self._document_parser.parse(filename, content_bytes)
        
        if extra_context:
            parsed_text = f"{extra_context}\n\n{parsed_text}"
            
        brand_input = BrandInput(
            input_type=BrandInputType.DOCUMENT,
            document_filename=filename,
            document_content=parsed_text,
        )
        
        return await self._brand_extractor.extract(brand_input)
