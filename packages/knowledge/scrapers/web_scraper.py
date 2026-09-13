"""Web scraper for extracting text from URLs."""
import logging

import httpx
from bs4 import BeautifulSoup

from packages.shared.config import get_settings
from packages.shared.errors import ExtractionError

logger = logging.getLogger(__name__)


class WebScraper:
    """Scrapes and extracts readable text from web pages."""

    def __init__(self) -> None:
        self.settings = get_settings()

    async def scrape(self, url: str) -> str:
        """Fetch URL and extract meaningful text.
        
        Args:
            url: The URL to scrape.
            
        Returns:
            Clean text extracted from the page.
            
        Raises:
            ExtractionError: If the request fails or parsing fails.
        """
        try:
            async with httpx.AsyncClient(timeout=self.settings.scraper_timeout_seconds) as client:
                response = await client.get(url, follow_redirects=True)
                response.raise_for_status()
                html = response.text
        except Exception as exc:
            raise ExtractionError(f"Failed to fetch URL {url}", detail=str(exc)) from exc

        try:
            soup = BeautifulSoup(html, "html.parser")
            
            # Remove unwanted tags
            for element in soup(["script", "style", "nav", "footer", "header", "noscript", "aside"]):
                element.decompose()
                
            parts = []
            
            if soup.title and soup.title.string:
                parts.append(soup.title.string)
                
            meta_desc = soup.find("meta", attrs={"name": "description"})
            if meta_desc and meta_desc.get("content"):
                parts.append(str(meta_desc.get("content")))
                
            for heading in soup.find_all(["h1", "h2", "h3"]):
                if heading.get_text(strip=True):
                    parts.append(heading.get_text(strip=True))
                    
            for p in soup.find_all("p"):
                if p.get_text(strip=True):
                    parts.append(p.get_text(strip=True))
                    
            # Combine and limit length
            full_text = "\n\n".join(parts)
            return full_text[:4000]
        except Exception as exc:
            raise ExtractionError(f"Failed to parse HTML from {url}", detail=str(exc)) from exc
