import logging
from collections.abc import Iterator
from functools import lru_cache
from typing import Any

from app.core.config import settings
from app.services.llm_gateway.llm_config import DEFAULT_TEMPERATURES, LLM_TASK_MODELS
from app.services.llm_gateway.providers import create_provider
from app.services.llm_gateway.types import LLMError, LLMResponse, Message

logger = logging.getLogger("argos.llm")


class LLMGateway:
    def __init__(self, provider_name: str, fallback_provider_name: str | None = None) -> None:
        self.provider_name = provider_name
        self.fallback_provider_name = fallback_provider_name

    def generate_text(
        self,
        messages: list[Message],
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        task: str = "chat",
    ) -> LLMResponse:
        selected_model = model or self._model_for_task(task, self.provider_name)
        selected_temperature = temperature
        if selected_temperature is None:
            selected_temperature = DEFAULT_TEMPERATURES.get(task, 0.3)
        return self._call_with_fallback(
            method="generate_text",
            messages=messages,
            model=selected_model,
            temperature=selected_temperature,
            max_tokens=max_tokens,
            task=task,
        )

    def generate_json(
        self,
        messages: list[Message],
        schema: dict[str, Any] | None = None,
        model: str | None = None,
        task: str = "chat",
    ) -> LLMResponse:
        selected_model = model or self._model_for_task(task, self.provider_name)
        return self._call_with_fallback(
            method="generate_json",
            messages=messages,
            schema=schema,
            model=selected_model,
            task=task,
        )

    def stream_text(
        self,
        messages: list[Message],
        model: str | None = None,
        task: str = "chat",
    ) -> Iterator[str]:
        response = self.generate_text(messages=messages, model=model, task=task)
        yield response.content

    def _call_with_fallback(self, method: str, **kwargs) -> LLMResponse:
        primary = create_provider(self.provider_name)
        try:
            response = getattr(primary, method)(**self._provider_kwargs(kwargs))
            self._log_success(response, kwargs.get("task", "chat"), fallback=False)
            return response
        except LLMError as exc:
            logger.warning(
                "Falha no provedor principal de IA provider=%s task=%s erro=%s",
                self.provider_name,
                kwargs.get("task", "chat"),
                exc,
            )
            if not self._can_use_fallback():
                raise

        fallback = create_provider(self.fallback_provider_name or "")
        fallback_kwargs = self._fallback_kwargs(kwargs)
        response = getattr(fallback, method)(**self._provider_kwargs(fallback_kwargs))
        self._log_success(response, fallback_kwargs.get("task", "fallback"), fallback=True)
        return response

    def _provider_kwargs(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        return {key: value for key, value in kwargs.items() if key != "task"}

    def _fallback_kwargs(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        fallback_kwargs = dict(kwargs)
        fallback_kwargs["task"] = "fallback"
        fallback_kwargs["model"] = self._model_for_task(
            fallback_kwargs.get("task", "fallback"),
            self.fallback_provider_name or "",
        )
        return fallback_kwargs

    def _can_use_fallback(self) -> bool:
        return bool(
            self.fallback_provider_name
            and self.fallback_provider_name.strip().lower() != self.provider_name.strip().lower()
        )

    def _model_for_task(self, task: str, provider_name: str) -> str:
        if provider_name.strip().lower() == "openai":
            return LLM_TASK_MODELS["fallback"]
        return LLM_TASK_MODELS.get(task, LLM_TASK_MODELS["chat"])

    def _log_success(self, response: LLMResponse, task: str, fallback: bool) -> None:
        logger.info(
            "Chamada LLM concluida provider=%s model=%s task=%s fallback=%s",
            response.provider,
            response.model,
            task,
            fallback,
        )


@lru_cache
def get_llm_gateway() -> LLMGateway:
    return LLMGateway(
        provider_name=settings.llm_provider,
        fallback_provider_name=settings.llm_fallback_provider,
    )
