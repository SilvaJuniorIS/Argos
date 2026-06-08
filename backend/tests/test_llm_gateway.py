from types import SimpleNamespace

import pytest

from app.services.llm_gateway.gateway import LLMGateway
from app.services.llm_gateway.providers import OpenAIProvider, OpenRouterProvider
from app.services.llm_gateway.types import (
    LLMConfigurationError,
    LLMResponse,
    LLMUnavailableError,
)


def test_openrouter_provider_normaliza_resposta(monkeypatch) -> None:
    provider = OpenRouterProvider()
    provider.api_key = "sk-or-test"
    provider.default_model = "openrouter/free"

    response = SimpleNamespace(
        model="openrouter/free",
        usage=SimpleNamespace(model_dump=lambda: {"total_tokens": 12}),
        choices=[SimpleNamespace(message=SimpleNamespace(content=" Texto gerado "))],
        model_dump=lambda: {"id": "chatcmpl-test"},
    )
    monkeypatch.setattr(
        provider,
        "_client",
        lambda: SimpleNamespace(
            chat=SimpleNamespace(
                completions=SimpleNamespace(create=lambda **kwargs: response)
            )
        ),
    )

    result = provider.generate_text(
        messages=[{"role": "user", "content": "Ola"}],
        model="google/gemini-2.5-flash",
    )

    assert result.content == "Texto gerado"
    assert result.model == "openrouter/free"
    assert result.provider == "openrouter"
    assert result.usage == {"total_tokens": 12}
    assert result.raw_response == {"id": "chatcmpl-test"}


def test_openai_provider_remove_prefixo_openai() -> None:
    provider = OpenAIProvider()

    assert provider._normalize_model("openai/gpt-4o-mini") == "gpt-4o-mini"


def test_gateway_usa_fallback_quando_principal_falha(monkeypatch) -> None:
    class PrimaryProvider:
        name = "openrouter"

        def generate_text(self, **kwargs):
            raise LLMUnavailableError("OpenRouter fora do ar")

    class FallbackProvider:
        name = "openai"

        def generate_text(self, **kwargs):
            return LLMResponse(
                content="Resposta via fallback",
                model=kwargs["model"].removeprefix("openai/"),
                provider=self.name,
                usage=None,
                raw_response={},
            )

    def fake_create_provider(name: str):
        if name == "openrouter":
            return PrimaryProvider()
        if name == "openai":
            return FallbackProvider()
        raise AssertionError(name)

    monkeypatch.setattr("app.services.llm_gateway.gateway.create_provider", fake_create_provider)

    gateway = LLMGateway(provider_name="openrouter", fallback_provider_name="openai")
    response = gateway.generate_text(messages=[{"role": "user", "content": "Gerar"}])

    assert response.content == "Resposta via fallback"
    assert response.provider == "openai"
    assert response.model == "gpt-4o-mini"


def test_gateway_com_openai_usa_modelo_compativel(monkeypatch) -> None:
    class OpenAIOnlyProvider:
        name = "openai"

        def generate_text(self, **kwargs):
            return LLMResponse(
                content="Resposta OpenAI",
                model=kwargs["model"].removeprefix("openai/"),
                provider=self.name,
                usage=None,
                raw_response={},
            )

    monkeypatch.setattr(
        "app.services.llm_gateway.gateway.create_provider",
        lambda name: OpenAIOnlyProvider(),
    )

    gateway = LLMGateway(provider_name="openai", fallback_provider_name="")
    response = gateway.generate_text(
        messages=[{"role": "user", "content": "Gerar"}],
        task="legal_draft",
    )

    assert response.provider == "openai"
    assert response.model == "gpt-4o-mini"


def test_gateway_sem_fallback_repassa_erro(monkeypatch) -> None:
    class BrokenProvider:
        name = "openrouter"

        def generate_text(self, **kwargs):
            raise LLMConfigurationError("sem chave")

    monkeypatch.setattr(
        "app.services.llm_gateway.gateway.create_provider",
        lambda name: BrokenProvider(),
    )

    gateway = LLMGateway(provider_name="openrouter", fallback_provider_name="openrouter")
    with pytest.raises(LLMConfigurationError):
        gateway.generate_text(messages=[{"role": "user", "content": "Gerar"}])
