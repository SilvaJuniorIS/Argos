from datetime import date, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.contrato import Contrato, ContratoStatus
from app.models.fornecedor import Fornecedor
from app.models.secretaria import Secretaria
from app.models.user import User, UserRole
from app.services import alerta_service
from tests.conftest import TEST_PASSWORD


def _auth(client: TestClient, email: str) -> dict[str, str]:
    r = client.post("/api/v1/auth/login", data={"username": email, "password": TEST_PASSWORD})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def _seed(db: Session) -> tuple[Contrato, User]:
    sec = Secretaria(nome="Saude", sigla="SMS", is_active=True)
    forn = Fornecedor(razao_social="F", cnpj="11.222.333/0001-81", is_active=True)
    db.add_all([sec, forn])
    db.flush()
    admin = User(
        nome="Admin",
        email="admin-alertas@example.com",
        hashed_password=hash_password(TEST_PASSWORD),
        role=UserRole.admin.value,
        is_active=True,
    )
    db.add(admin)
    db.flush()
    hoje = date.today()
    contrato = Contrato(
        numero="ALERT/01",
        orgao="Pref",
        objeto="Teste",
        valor=1000,
        inicio=hoje - timedelta(days=30),
        termino=hoje + timedelta(days=25),
        status=ContratoStatus.ativo.value,
        secretaria_id=sec.id,
        fornecedor_id=forn.id,
        gestor_responsavel_id=admin.id,
    )
    db.add(contrato)
    db.commit()
    db.refresh(contrato)
    return contrato, admin


def test_gera_alerta_contrato_25_dias(client: TestClient, db_session: Session) -> None:
    contrato, _ = _seed(db_session)
    alerta = alerta_service.gerar_para_contrato_em_dias(db_session, contrato, 25)
    assert alerta is not None
    assert "25 dias" in alerta.titulo


def test_nao_duplica_alerta(client: TestClient, db_session: Session) -> None:
    contrato, _ = _seed(db_session)
    first = alerta_service.gerar_para_contrato_em_dias(db_session, contrato, 30)
    second = alerta_service.gerar_para_contrato_em_dias(db_session, contrato, 30)
    assert first is not None
    assert second is None


def test_marcar_alerta_como_lido(client: TestClient, db_session: Session) -> None:
    contrato, admin = _seed(db_session)
    alerta = alerta_service.gerar_para_contrato_em_dias(db_session, contrato, 30)
    assert alerta is not None
    headers = _auth(client, admin.email)
    response = client.put(f"/api/v1/alertas/{alerta.id}/lido", headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "lido"


def test_gerar_alertas_operacionais_endpoint(client: TestClient, db_session: Session) -> None:
    contrato, admin = _seed(db_session)
    hoje = date.today()
    contrato.inicio = hoje - timedelta(days=400)
    contrato.termino = hoje + timedelta(days=30)
    db_session.add(contrato)
    db_session.commit()
    headers = _auth(client, admin.email)

    response = client.post("/api/v1/alertas/gerar", headers=headers)

    assert response.status_code == 200
    assert response.json() == {
        "vencimentos": 1,
        "reajustes": 1,
        "contratos_importados": 0,
        "total": 2,
    }


def test_gera_alerta_vencimento_15_dias(client: TestClient, db_session: Session) -> None:
    contrato, _ = _seed(db_session)
    hoje = date.today()
    contrato.termino = hoje + timedelta(days=15)
    db_session.add(contrato)
    db_session.commit()

    criados = alerta_service.verificar_vencimentos(db_session, referencia=hoje)

    assert criados == 1
    alerta = alerta_service.list_alertas(
        db_session,
        secretaria_ids=None,
        limit=10,
        offset=0,
    )[0]
    assert alerta.tipo == "vencimento_15"


def test_envia_alerta_para_responsaveis_e_secretaria(
    client: TestClient,
    db_session: Session,
    monkeypatch,
) -> None:
    contrato, admin = _seed(db_session)
    contrato.termino = date.today() + timedelta(days=15)
    contrato.secretaria.email_alertas = f"central@example.com; {admin.email}"
    db_session.add(contrato)
    db_session.commit()
    enviados: list[str] = []

    def fake_send_alert_email(email, alerta, contrato):
        enviados.append(email)
        return True

    monkeypatch.setattr(alerta_service.email_service, "send_alert_email", fake_send_alert_email)

    criados = alerta_service.verificar_vencimentos(db_session)

    assert criados == 1
    assert enviados == [admin.email, "central@example.com"]
    alerta = alerta_service.list_alertas(
        db_session,
        secretaria_ids=None,
        limit=10,
        offset=0,
    )[0]
    assert alerta.status == "enviado"
    assert alerta.enviado_em is not None


def test_reajuste_ignora_inicio_em_29_fevereiro(client: TestClient, db_session: Session) -> None:
    contrato, _ = _seed(db_session)
    contrato.inicio = date(2024, 2, 29)
    contrato.termino = date(2026, 12, 31)
    db_session.add(contrato)
    db_session.commit()

    criados = alerta_service.verificar_reajustes(db_session, referencia=date(2025, 3, 1))

    assert criados == 1
    alerta = alerta_service.list_alertas(
        db_session,
        secretaria_ids=None,
        limit=10,
        offset=0,
    )[0]
    assert alerta.data_referencia == date(2025, 2, 28)


def test_usuario_nao_altera_alerta_de_outra_secretaria(
    client: TestClient,
    db_session: Session,
) -> None:
    contrato, _ = _seed(db_session)
    alerta = alerta_service.gerar_para_contrato_em_dias(db_session, contrato, 30)
    assert alerta is not None

    outra_secretaria = Secretaria(nome="Educacao", sigla="SME", is_active=True)
    db_session.add(outra_secretaria)
    db_session.flush()
    fiscal = User(
        nome="Fiscal",
        email="fiscal-alertas@example.com",
        hashed_password=hash_password(TEST_PASSWORD),
        role=UserRole.fiscal.value,
        secretaria_id=outra_secretaria.id,
        is_active=True,
    )
    db_session.add(fiscal)
    db_session.commit()
    headers = _auth(client, fiscal.email)

    response = client.put(f"/api/v1/alertas/{alerta.id}/lido", headers=headers)

    assert response.status_code == 403
