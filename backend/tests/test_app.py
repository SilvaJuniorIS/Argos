from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app

client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": settings.app_name}


def test_dashboard_page_loads() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "ARGOS Dashboard" in response.text
    assert "/api/v1/dashboard" in response.text


def test_dashboard_endpoint_returns_cards_without_database() -> None:
    response = client.get("/api/v1/dashboard")

    assert response.status_code == 200
    payload = response.json()
    assert "cards" in payload
    assert "total_contratos" in payload["cards"]


def test_run_seed_indisponivel_em_producao(monkeypatch) -> None:
    monkeypatch.setattr(settings, "environment", "production")

    response = client.get("/run-seed")

    assert response.status_code == 404
    assert response.json()["detail"] == "Endpoint indisponivel em producao"
