from __future__ import annotations

import logging
from collections.abc import Iterator
from typing import Any

from app.core.config import settings
from app.services.llm_gateway.types import (
    LLMAuthenticationError,
    LLMConfigurationError,
    LLMError,
    LLMRateLimitError,
    LLMResponse,
    LLMTimeoutError,
    LLMUnavailableError,
    Message,
)

logger = logging.getLogger("argos.llm")


class BaseOpenAICompatibleProvider:
    name = "base"

    def __init__(
        self,
        api_key: str,
        default_model: str,
        timeout: float,
        base_url: str | None = None,
        default_headers: dict[str, str] | None = None,
    ) -> None:
        self.api_key = api_key
        self.default_model = default_model
        self.timeout = timeout
        self.base_url = base_url
        self.default_headers = default_headers or {}

    def generate_text(
        self,
        messages: list[Message],
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        self._ensure_configured()
        request_model = self._normalize_model(model or self.default_model)
        client = self._client()
        kwargs: dict[str, Any] = {
            "model": request_model,
            "messages": messages,
            "temperature": temperature,
        }
        if max_tokens is not None:
            kwargs["max_tokens"] = max_tokens

        try:
            response = client.chat.completions.create(**kwargs)
        except Exception as exc:
            self._raise_normalized_error(exc)

        content = self._extract_content(response)
        if not content:
            raise LLMUnavailableError(f"{self.name} nao retornou conteudo de texto")
        return self._normalize_response(response, content, request_model)

    def generate_json(
        self,
        messages: list[Message],
        schema: dict[str, Any] | None = None,
        model: str | None = None,
    ) -> LLMResponse:
        self._ensure_configured()
        request_model = self._normalize_model(model or self.default_model)
        client = self._client()
        response_format: dict[str, Any] = {"type": "json_object"}
        if schema:
            response_format = {
                "type": "json_schema",
                "json_schema": {
                    "name": "argos_response",
                    "schema": schema,
                    "strict": True,
                },
            }
        try:
            response = client.chat.completions.create(
                model=request_model,
                messages=messages,
                temperature=0,
                response_format=response_format,
            )
        except Exception as exc:
            self._raise_normalized_error(exc)

        content = self._extract_content(response)
        if not content:
            raise LLMUnavailableError(f"{self.name} nao retornou JSON")
        return self._normalize_response(response, content, request_model)

    def stream_text(self, messages: list[Message], model: str | None = None) -> Iterator[str]:
        response = self.generate_text(messages=messages, model=model)
        yield response.content

    def _client(self):
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise LLMConfigurationError("Biblioteca openai nao instalada no backend") from exc

        kwargs: dict[str, Any] = {"api_key": self.api_key, "timeout": self.timeout}
        if self.base_url:
            kwargs["base_url"] = self.base_url
        if self.default_headers:
            kwargs["default_headers"] = self.default_headers
        return OpenAI(**kwargs)

    def _ensure_configured(self) -> None:
        if not self.api_key:
            raise LLMConfigurationError(f"Chave de API nao configurada para {self.name}")

    def _normalize_model(self, model: str) -> str:
        return model

    def _normalize_response(self, response: Any, content: str, request_model: str) -> LLMResponse:
        raw = response.model_dump() if hasattr(response, "model_dump") else response
        usage = getattr(response, "usage", None)
        if hasattr(usage, "model_dump"):
            usage = usage.model_dump()
        response_model = getattr(response, "model", None) or request_model
        return LLMResponse(
            content=content.strip(),
            model=response_model,
            provider=self.name,
            usage=usage,
            raw_response=raw,
        )

    def _extract_content(self, response: Any) -> str:
        choices = getattr(response, "choices", None) or []
        if not choices:
            return ""
        message = getattr(choices[0], "message", None)
        return (getattr(message, "content", None) or "").strip()

    def _raise_normalized_error(self, exc: Exception) -> None:
        try:
            from openai import APIConnectionError, APIStatusError, APITimeoutError, RateLimitError
        except ImportError:
            raise LLMUnavailableError(f"Erro ao chamar {self.name}") from exc

        if isinstance(exc, APITimeoutError):
            raise LLMTimeoutError(f"Tempo excedido ao chamar {self.name}") from exc
        if isinstance(exc, RateLimitError):
            raise LLMRateLimitError(f"Limite de uso atingido em {self.name}") from exc
        if isinstance(exc, APIStatusError):
            status_code = getattr(exc, "status_code", None)
            if status_code in {401, 403}:
                raise LLMAuthenticationError(f"Autenticacao recusada por {self.name}") from exc
            if status_code == 429:
                raise LLMRateLimitError(f"Limite de uso atingido em {self.name}") from exc
            if status_code and status_code >= 500:
                raise LLMUnavailableError(f"{self.name} indisponivel no momento") from exc
            raise LLMError(f"{self.name} retornou erro {status_code}") from exc
        if isinstance(exc, APIConnectionError):
            raise LLMUnavailableError(f"Nao foi possivel conectar a {self.name}") from exc
        logger.exception("Erro inesperado no provedor LLM %s", self.name)
        raise LLMError(f"Erro inesperado ao chamar {self.name}") from exc


class OpenRouterProvider(BaseOpenAICompatibleProvider):
    name = "openrouter"

    def __init__(self) -> None:
        headers = {}
        if settings.openrouter_http_referer:
            headers["HTTP-Referer"] = settings.openrouter_http_referer
        if settings.openrouter_x_title:
            headers["X-Title"] = settings.openrouter_x_title
        super().__init__(
            api_key=settings.openrouter_api_key,
            default_model=settings.openrouter_default_model,
            timeout=settings.llm_timeout_seconds,
            base_url=settings.openrouter_base_url,
            default_headers=headers,
        )


class OpenAIProvider(BaseOpenAICompatibleProvider):
    name = "openai"

    def __init__(self) -> None:
        default_model = settings.openai_default_model
        if default_model == "gpt-4o-mini" and settings.openai_model != "gpt-4o-mini":
            default_model = settings.openai_model
        super().__init__(
            api_key=settings.openai_api_key,
            default_model=default_model,
            timeout=settings.openai_timeout_seconds or settings.llm_timeout_seconds,
        )

    def _normalize_model(self, model: str) -> str:
        return model.removeprefix("openai/")


def create_provider(name: str):
    provider_name = name.strip().lower()
    if provider_name == "openrouter":
        return OpenRouterProvider()
    if provider_name == "openai":
        return OpenAIProvider()
    raise LLMConfigurationError(f"Provedor LLM nao suportado: {name}")
