"""Custom exception hierarchy for BrandOS.

All exceptions inherit from BrandOSError so callers can catch at any level
of specificity without importing multiple exception types.
"""
from __future__ import annotations


class BrandOSError(Exception):
    """Base exception for all BrandOS errors."""

    def __init__(self, message: str, detail: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.detail = detail

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message={self.message!r}, detail={self.detail!r})"


class ExtractionError(BrandOSError):
    """Raised when the Knowledge Layer fails to extract brand information.

    This covers scraping failures, parsing failures, and LLM extraction failures.
    """


class LLMError(BrandOSError):
    """Raised when an LLM call fails.

    Includes API errors, timeout errors, malformed response errors,
    and structured output parsing failures.
    """

    def __init__(self, message: str, detail: str | None = None, status_code: int | None = None) -> None:
        super().__init__(message, detail)
        self.status_code = status_code


class OrchestrationError(BrandOSError):
    """Raised when the Orchestration Layer encounters a workflow failure.

    This is raised when agent coordination breaks down, e.g. an agent
    returns an unexpected type or the workflow reaches an invalid state.
    """


class ValidationError(BrandOSError):  # noqa: A001
    """Raised when a data model fails validation.

    Distinct from Pydantic's ValidationError — this wraps it for the
    BrandOS error hierarchy.
    """
