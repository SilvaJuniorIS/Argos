import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_rejeita_segredos_padrao_em_producao() -> None:
    with pytest.raises(ValidationError, match="Configuracao insegura"):
        Settings(
            environment="production",
            secret_key="change-me-in-production",
            admin_password="argos123",
            _env_file=None,
        )


def test_aceita_segredos_fortes_em_producao() -> None:
    settings = Settings(
        environment="production",
        secret_key="secret-key-forte-para-producao",
        admin_password="senha-forte-para-producao",
        _env_file=None,
    )

    assert settings.environment == "production"
