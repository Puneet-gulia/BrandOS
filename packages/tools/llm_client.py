"""
LLMClient — thin, resilient wrapper around the OpenAI-compatible API.

All agents in BrandOS use this single client. Centralising here ensures:
- Consistent retry logic and error handling across all agents
- A single place to swap AI providers (OpenRouter → OpenAI → Anthropic)
- Structured output parsing with type safety
- Configurable timeouts and retry behaviour
"""
from __future__ import annotations

import json
import logging
from typing import Any, Type, TypeVar

import httpx
from openai import AsyncOpenAI, APIConnectionError, APIStatusError, RateLimitError
from pydantic import BaseModel
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
    before_sleep_log,
)

from packages.shared.config import get_settings
from packages.shared.errors import LLMError

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class LLMClient:
    """
    Async LLM client for BrandOS.
    
    Wraps the OpenAI SDK (OpenRouter-compatible) and provides:
    - `complete(prompt, model)` → raw string response
    - `complete_structured(prompt, response_model, model)` → Pydantic model instance
    
    The client uses exponential backoff on transient errors (rate limits,
    connection failures) and raises `LLMError` for all failures.
    """

    def __init__(self, api_key: str | None = None, base_url: str | None = None, model: str | None = None) -> None:
        settings = get_settings()
        self._model = model or settings.openrouter_default_model
        self._client = AsyncOpenAI(
            api_key=api_key or settings.openrouter_api_key,
            base_url=base_url or settings.openrouter_base_url,
            timeout=httpx.Timeout(settings.llm_timeout_seconds),
            max_retries=0,  # We handle retries ourselves via tenacity
        )
        self._max_retries = settings.llm_max_retries

    async def complete(self, prompt: str, model: str | None = None, system_prompt: str | None = None) -> str:
        """Send a prompt and return the raw text response."""
        return await self._call_with_retry(prompt=prompt, model=model, system_prompt=system_prompt)

    async def complete_structured(self, prompt: str, response_model: Type[T], model: str | None = None, system_prompt: str | None = None) -> T:
        """Send a prompt and parse the response into a Pydantic model.
        
        The LLM is instructed to respond with valid JSON matching the model schema.
        Raises LLMError if parsing fails.
        """
        schema_instruction = (
            f"You MUST respond with valid JSON only. No markdown, no explanation. "
            f"The JSON must conform to this schema:\n{json.dumps(response_model.model_json_schema(), indent=2)}"
        )
        full_system = f"{system_prompt}\n\n{schema_instruction}" if system_prompt else schema_instruction
        raw = await self._call_with_retry(prompt=prompt, model=model, system_prompt=full_system)
        try:
            # Strip markdown code fences if present
            cleaned = raw.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1].rsplit("```", 1)[0].strip()
            data = json.loads(cleaned)
            return response_model.model_validate(data)
        except (json.JSONDecodeError, Exception) as exc:
            raise LLMError(
                message="Failed to parse structured LLM response",
                detail=f"Raw response: {raw[:500]}",
            ) from exc

    async def _call_with_retry(self, prompt: str, model: str | None = None, system_prompt: str | None = None) -> str:
        """Internal call with tenacity retry logic."""
        selected_model = model or self._model
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        @retry(
            retry=retry_if_exception_type((RateLimitError, APIConnectionError)),
            stop=stop_after_attempt(self._max_retries),
            wait=wait_exponential(multiplier=1, min=2, max=30),
            before_sleep=before_sleep_log(logger, logging.WARNING),
            reraise=False,
        )
        async def _attempt() -> str:
            try:
                response = await self._client.chat.completions.create(
                    model=selected_model,
                    messages=messages,  # type: ignore[arg-type]
                )
                content = response.choices[0].message.content
                if content is None:
                    raise LLMError("LLM returned empty content")
                return content
            except RateLimitError as exc:
                logger.warning("Rate limited by LLM API, will retry: %s", exc)
                raise
            except APIConnectionError as exc:
                logger.warning("LLM API connection error, will retry: %s", exc)
                raise
            except APIStatusError as exc:
                raise LLMError(
                    message=f"LLM API returned error status {exc.status_code}",
                    detail=str(exc.message),
                    status_code=exc.status_code,
                ) from exc

        try:
            return await _attempt()
        except (RateLimitError, APIConnectionError) as exc:
            raise LLMError(
                message="LLM call failed after maximum retries",
                detail=str(exc),
            ) from exc
