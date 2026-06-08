from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app

client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": settings.app_name}


def test_root_returns_argos_metadata() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["service"] == settings.app_name
    assert "inteligencia documental" in response.json()["description"]


def test_run_seed_indisponivel_em_producao(monkeypatch) -> None:
    monkeypatch.setattr(settings, "environment", "production")

    response = client.get("/run-seed")

    assert response.status_code == 404
    assert response.json()["detail"] == "Endpoint indisponivel em producao"
