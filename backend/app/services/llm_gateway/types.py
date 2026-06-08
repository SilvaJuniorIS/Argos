from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any, Protocol


Message = dict[str, str]


@dataclass(slots=True)
class LLMResponse:
    content: str
    model: str
    provider: str
    usage: dict[str, Any] | None
    raw_response: Any


class LLMError(RuntimeError):
    pass


class LLMConfigurationError(LLMError):
    pass


class LLMAuthenticationError(LLMError):
    pass


class LLMRateLimitError(LLMError):
    pass


class LLMTimeoutError(LLMError):
    pass


class LLMUnavailableError(LLMError):
    pass


class LLMProvider(Protocol):
    name: str

    def generate_text(
        self,
        messages: list[Message],
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        ...

    def generate_json(
        self,
        messages: list[Message],
        schema: dict[str, Any] | None = None,
        model: str | None = None,
    ) -> LLMResponse:
        ...

    def stream_text(
        self,
        messages: list[Message],
        model: str | None = None,
    ) -> Iterator[str]:
        ...
