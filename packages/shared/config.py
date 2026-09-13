"""Shared configuration used across all BrandOS packages.

Packages import from here rather than from apps/api/config.py to avoid
creating a dependency on the API application layer.
"""
from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application-wide settings loaded from environment variables.

    Pydantic-Settings reads values from the environment automatically.
    Required values without defaults will raise an error at startup if missing.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # AI Provider
    openrouter_api_key: str = Field(..., description="OpenRouter API key")
    openrouter_base_url: str = Field(
        default="https://openrouter.ai/api/v1",
        description="OpenRouter-compatible base URL",
    )
    openrouter_default_model: str = Field(
        default="openai/gpt-4o-mini",
        description="Default LLM model identifier",
    )

    # API Server
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    api_debug: bool = Field(default=False)

    # Limits
    llm_max_retries: int = Field(default=3, description="Max retry attempts for LLM calls")
    llm_timeout_seconds: float = Field(default=60.0, description="LLM call timeout")
    scraper_timeout_seconds: float = Field(default=20.0, description="Web scraper timeout")
    max_upload_size_bytes: int = Field(default=10 * 1024 * 1024, description="10 MB")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached singleton Settings instance.

    Using lru_cache ensures settings are parsed from the environment only once
    per process, which avoids redundant I/O and validation on every request.
    """
    return Settings()  # type: ignore[call-arg]
