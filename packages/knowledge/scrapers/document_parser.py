"""Document parser for extracting text from files."""
import io
import logging

import pdfplumber

from packages.shared.errors import ExtractionError

logger = logging.getLogger(__name__)


class DocumentParser:
    """Parses text from various document formats."""

    def parse(self, filename: str, content_bytes: bytes) -> str:
        """Parse text from a document.
        
        Args:
            filename: Name of the file, used to determine format.
            content_bytes: Raw bytes of the file.
            
        Returns:
            Extracted text.
            
        Raises:
            ExtractionError: If format is unsupported or parsing fails.
        """
        lower_name = filename.lower()
        if lower_name.endswith(".txt"):
            return self._parse_txt(content_bytes)
        elif lower_name.endswith(".pdf"):
            return self._parse_pdf(content_bytes)
        else:
            raise ExtractionError(f"Unsupported document format: {filename}")

    def _parse_txt(self, content_bytes: bytes) -> str:
        try:
            return content_bytes.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ExtractionError("Failed to decode text file as UTF-8", detail=str(exc)) from exc

    def _parse_pdf(self, content_bytes: bytes) -> str:
        try:
            text_parts = []
            with pdfplumber.open(io.BytesIO(content_bytes)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
            return "\n\n".join(text_parts)[:4000]
        except Exception as exc:
            raise ExtractionError("Failed to parse PDF document", detail=str(exc)) from exc
