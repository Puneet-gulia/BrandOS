"""BrandOS Knowledge Layer.

Responsible for understanding the brand. This layer:
- Accepts raw brand input (URL, text, or document)
- Scrapes or parses the content
- Uses an LLM to extract structured brand information
- Returns a BrandProfile

This layer NEVER generates marketing content.
"""

from packages.knowledge.service import KnowledgeService

__all__ = ["KnowledgeService"]
