"""
PromptLoader — loads and renders Markdown prompt templates from disk.

All BrandOS prompts live in packages/prompts/ as .md files.
This class ensures:
- Zero prompts are ever hardcoded in Python
- Template variables are rendered safely with clear error messages
- Prompt files are cached after first read to avoid repeated disk I/O
"""
from __future__ import annotations

import logging
import re
from functools import lru_cache
from pathlib import Path
from string import Template

logger = logging.getLogger(__name__)

# Default path: the prompts package root, relative to the project root
_DEFAULT_PROMPTS_DIR = Path(__file__).resolve().parents[2] / "packages" / "prompts"


class PromptLoader:
    """
    Loads .md prompt template files and renders them with provided variables.
    
    Template syntax uses {{variable_name}} placeholders (double-brace style
    to avoid conflicts with Python's str.format or Jinja2 if introduced later).
    
    Example:
        loader = PromptLoader()
        prompt = loader.load("knowledge/brand_extraction", raw_content="...")
    """

    def __init__(self, prompts_dir: Path | None = None) -> None:
        self._prompts_dir = prompts_dir or _DEFAULT_PROMPTS_DIR
        if not self._prompts_dir.exists():
            raise FileNotFoundError(f"Prompts directory not found: {self._prompts_dir}")
        logger.debug("PromptLoader initialised with directory: %s", self._prompts_dir)

    def load(self, template_path: str, **variables: str) -> str:
        """
        Load a prompt template and render it with the given variables.
        
        Args:
            template_path: Relative path without extension, e.g. "knowledge/brand_extraction"
            **variables: Key-value pairs matching {{variable_name}} placeholders
            
        Returns:
            Rendered prompt string with all placeholders replaced.
            
        Raises:
            FileNotFoundError: If the template file does not exist.
            KeyError: If a required placeholder is missing from variables.
        """
        raw = self._read_template(template_path)
        return self._render(raw, template_path, variables)

    @lru_cache(maxsize=64)  # type: ignore[misc]
    def _read_template(self, template_path: str) -> str:
        """Read and cache a template file from disk."""
        file_path = self._prompts_dir / f"{template_path}.md"
        if not file_path.exists():
            raise FileNotFoundError(
                f"Prompt template not found: {file_path}. "
                f"Expected at: packages/prompts/{template_path}.md"
            )
        content = file_path.read_text(encoding="utf-8")
        logger.debug("Loaded prompt template: %s (%d chars)", template_path, len(content))
        return content

    @staticmethod
    def _render(template: str, template_path: str, variables: dict[str, str]) -> str:
        """Replace {{variable}} placeholders with provided values."""
        # Find all placeholders in the template
        placeholders = set(re.findall(r"\{\{(\w+)\}\}", template))
        missing = placeholders - variables.keys()
        if missing:
            raise KeyError(
                f"Prompt template '{template_path}' requires variables {missing} "
                f"that were not provided. Provided: {set(variables.keys())}"
            )
        result = template
        for key, value in variables.items():
            result = result.replace(f"{{{{{key}}}}}", value)
        return result
