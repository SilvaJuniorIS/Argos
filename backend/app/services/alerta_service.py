import re
from datetime import UTC, date, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.alerta import Alerta, AlertaStatus
from app.models.anexo import Anexo, AnexoTipo
from app.models.contract import Contract
from app.models.contrato import Contrato, ContratoStatus
from app.models.notification import Notification
from app.models.secretaria import Secretaria
from app.services import email_service

VENCIMENTO_WINDOWS = (180, 90, 60, 30, 15, 7, 1)
ACTIVE_STATUSES = {
    ContratoStatus.ativo.value,
    ContratoStatus.alerta.value,
    ContratoStatus.critico.value,
}
EMAIL_SPLIT_PATTERN = re.compile(r"[;,\s]+")


def _dias_para_termino(termino: date, referencia: date | None = None) -> int:
    return (termino - (referencia or date.today())).days


def _tipo_vencimento(dias: int) -> str:
    return f"vencimento_{dias}"


def _adicionar_um_ano(data: date) -> date:
    try:
        return data.replace(year=data.year + 1)
    except ValueError:
        return data.replace(year=data.year + 1, day=28)


def _alerta_existe(db: Session, contrato_id: int, tipo: str, data_referencia: date) -> bool:
    existing = db.scalar(
        select(Alerta.id).where(
            Alerta.contrato_id == contrato_id,
            Alerta.tipo == tipo,
            Alerta.data_referencia == data_referencia,
        )
    )
    return existing is not None


def _split_emails(value: str | None) -> list[str]:
    if not value:
        return []
    return [email.strip() for email in EMAIL_SPLIT_PATTERN.split(value) if email.strip()]


def _destinatarios_alerta(contrato: Contrato) -> list[str]:
    emails: list[str] = []
    for user in (contrato.fiscal_responsavel, contrato.gestor_responsavel):
        if user and user.email:
            emails.append(user.email)
    if contrato.secretaria:
        emails.extend(_split_emails(contrato.secretaria.email_alertas))

    seen: set[str] = set()
    unique: list[str] = []
    for email in emails:
        key = email.lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(email)
    return unique


def _assert_alerta_in_scope(alerta: Alerta, secretaria_ids: list[int] | None) -> None:
    if secretaria_ids is None:
        return
    contrato = alerta.contrato
    if contrato is None or contrato.secretaria_id not in secretaria_ids:
        raise PermissionError("Alerta fora do escopo da sua secretaria")


def verificar_vencimentos(db: Session, referencia: date | None = None) -> int:
    hoje = referencia or date.today()
    criados = 0
    contratos = db.scalars(select(Contrato).where(Contrato.status.in_(ACTIVE_STATUSES))).all()

    for contrato in contratos:
        if contrato.termino < hoje:
            continue
        dias = _dias_para_termino(contrato.termino, hoje)
        if dias not in VENCIMENTO_WINDOWS:
            continue
        tipo = _tipo_vencimento(dias)
        if _alerta_existe(db, contrato.id, tipo, contrato.termino):
            continue
        alerta = Alerta(
            contrato_id=contrato.id,
            tipo=tipo,
            titulo=f"Contrato {contrato.numero} vence em {dias} dias",
            mensagem=(
                f"O contrato {contrato.numero} vence em {dias} dias. "
                "Avalie renovacao, prorrogacao ou encerramento."
            ),
            data_referencia=contrato.termino,
            status=AlertaStatus.pendente.value,
        )
        db.add(alerta)
        db.flush()
        _notificar_alerta(alerta, contrato)
        criados += 1

    if criados:
        db.commit()
    return criados


def verificar_reajustes(db: Session, referencia: date | None = None) -> int:
    hoje = referencia or date.today()
    criados = 0
    contratos = db.scalars(select(Contrato).where(Contrato.status.in_(ACTIVE_STATUSES))).all()

    for contrato in contratos:
        aniversario = _adicionar_um_ano(contrato.inicio)
        if aniversario >= hoje:
            continue
        tem_aditivo = db.scalar(
            select(Anexo.id).where(
                Anexo.contrato_id == contrato.id,
                Anexo.tipo == AnexoTipo.aditivo.value,
            )
        )
        if tem_aditivo:
            continue
        tipo = "reajuste_anual"
        if _alerta_existe(db, contrato.id, tipo, aniversario):
            continue
        alerta = Alerta(
            contrato_id=contrato.id,
            tipo=tipo,
            titulo=f"Reajuste anual pendente - contrato {contrato.numero}",
            mensagem="Contrato elegivel a reajuste anual sem aditivo registrado.",
            data_referencia=aniversario,
            status=AlertaStatus.pendente.value,
        )
        db.add(alerta)
        db.flush()
        _notificar_alerta(alerta, contrato)
        criados += 1

    if criados:
        db.commit()
    return criados


def gerar_alertas_operacionais(db: Session, referencia: date | None = None) -> dict[str, int]:
    vencimentos = verificar_vencimentos(db, referencia=referencia)
    reajustes = verificar_reajustes(db, referencia=referencia)
    return {
        "vencimentos": vencimentos,
        "reajustes": reajustes,
        "total": vencimentos + reajustes,
    }


def _notificar_alerta(alerta: Alerta, contrato: Contrato) -> int:
    enviados = 0
    for email in _destinatarios_alerta(contrato):
        if email_service.send_alert_email(email, alerta, contrato):
            enviados += 1
    if enviados:
        alerta.status = AlertaStatus.enviado.value
        alerta.enviado_em = datetime.now(UTC)
    return enviados


def marcar_como_lido(
    db: Session,
    alerta_id: int,
    user_id: int,
    secretaria_ids: list[int] | None = None,
) -> Alerta:
    alerta = db.get(Alerta, alerta_id)
    if alerta is None:
        raise ValueError("Alerta nao encontrado")
    _assert_alerta_in_scope(alerta, secretaria_ids)
    alerta.status = AlertaStatus.lido.value
    db.add(alerta)
    db.commit()
    db.refresh(alerta)
    return alerta


def resolver_alerta(
    db: Session,
    alerta_id: int,
    user_id: int,
    secretaria_ids: list[int] | None = None,
) -> Alerta:
    alerta = db.get(Alerta, alerta_id)
    if alerta is None:
        raise ValueError("Alerta nao encontrado")
    _assert_alerta_in_scope(alerta, secretaria_ids)
    alerta.status = AlertaStatus.resolvido.value
    alerta.enviado_em = alerta.enviado_em or datetime.now(UTC)
    db.add(alerta)
    db.commit()
    db.refresh(alerta)
    return alerta


def list_alertas(
    db: Session,
    *,
    secretaria_ids: list[int] | None,
    lido: bool | None = None,
    resolvido: bool | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[Alerta]:
    stmt = (
        select(Alerta)
        .join(Contrato, Contrato.id == Alerta.contrato_id)
        .order_by(Alerta.data_referencia.asc())
        .limit(limit)
        .offset(offset)
    )
    if secretaria_ids is not None:
        stmt = stmt.where(Contrato.secretaria_id.in_(secretaria_ids))
    if lido is True:
        stmt = stmt.where(Alerta.status == AlertaStatus.lido.value)
    elif lido is False:
        stmt = stmt.where(
            Alerta.status.not_in([AlertaStatus.lido.value, AlertaStatus.resolvido.value])
        )
    if resolvido is True:
        stmt = stmt.where(Alerta.status == AlertaStatus.resolvido.value)
    elif resolvido is False:
        stmt = stmt.where(Alerta.status != AlertaStatus.resolvido.value)
    return list(db.scalars(stmt))


def _secretarias_escopo(db: Session, secretaria_ids: list[int] | None) -> set[str] | None:
    if secretaria_ids is None:
        return None
    return set(
        db.scalars(select(Secretaria.nome).where(Secretaria.id.in_(secretaria_ids))).all()
    )


def _list_notifications(
    db: Session,
    *,
    secretaria_ids: list[int] | None,
    lido: bool | None = None,
    resolvido: bool | None = None,
) -> list[dict]:
    if lido is True or resolvido is True:
        return []

    stmt = (
        select(Notification, Contract)
        .join(Contract, Contract.id == Notification.contract_id)
        .order_by(Contract.fim_vigencia.asc().nulls_last(), Notification.created_at.asc())
    )
    secretaria_names = _secretarias_escopo(db, secretaria_ids)
    if secretaria_names is not None:
        stmt = stmt.where(Contract.secretaria.in_(secretaria_names))

    rows = db.execute(stmt).all()
    return [
        {
            "id": notification.id,
            "contrato_id": str(notification.contract_id),
            "tipo": notification.tipo,
            "titulo": notification.titulo,
            "mensagem": notification.mensagem,
            "data_referencia": contract.fim_vigencia or notification.created_at.date(),
            "status": "pendente",
            "enviado_em": None,
            "created_at": notification.created_at,
            "updated_at": notification.created_at,
            "origem": "notification",
        }
        for notification, contract in rows
    ]


def list_alertas_api(
    db: Session,
    *,
    secretaria_ids: list[int] | None,
    lido: bool | None = None,
    resolvido: bool | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[dict]:
    alertas = [
        {
            "id": alerta.id,
            "contrato_id": alerta.contrato_id,
            "tipo": alerta.tipo,
            "titulo": alerta.titulo,
            "mensagem": alerta.mensagem,
            "data_referencia": alerta.data_referencia,
            "status": alerta.status,
            "enviado_em": alerta.enviado_em,
            "created_at": alerta.created_at,
            "updated_at": alerta.updated_at,
            "origem": "alerta",
        }
        for alerta in list_alertas(
            db,
            secretaria_ids=secretaria_ids,
            lido=lido,
            resolvido=resolvido,
            limit=10_000,
            offset=0,
        )
    ]
    notifications = _list_notifications(
        db,
        secretaria_ids=secretaria_ids,
        lido=lido,
        resolvido=resolvido,
    )
    items = sorted(
        [*alertas, *notifications],
        key=lambda item: (item["data_referencia"], item["created_at"]),
    )
    return items[offset : offset + limit]


def resumo_alertas(db: Session, secretaria_ids: list[int] | None) -> dict[str, int]:
    alertas = list_alertas_api(db, secretaria_ids=secretaria_ids, limit=10_000, offset=0)
    urgentes = atencao = info = 0
    nao_lidos = 0
    for alerta in alertas:
        if alerta["status"] in {AlertaStatus.lido.value, AlertaStatus.resolvido.value}:
            continue
        nao_lidos += 1
        if alerta["tipo"] in {
            "contract_expiration",
            "vencimento_30",
            "vencimento_60",
        } or "critico" in alerta["titulo"].lower():
            urgentes += 1
        elif alerta["tipo"] in {"vencimento_90", "reajuste_anual"}:
            atencao += 1
        else:
            info += 1
    return {"urgentes": urgentes, "atencao": atencao, "info": info, "total_nao_lidos": nao_lidos}


def gerar_para_contrato_em_dias(db: Session, contrato: Contrato, dias: int) -> Alerta | None:
    """Gera alerta de vencimento para contrato com N dias restantes (uso em testes/jobs)."""
    tipo = _tipo_vencimento(dias) if dias in VENCIMENTO_WINDOWS else f"vencimento_{dias}"
    if _alerta_existe(db, contrato.id, tipo, contrato.termino):
        return None
    alerta = Alerta(
        contrato_id=contrato.id,
        tipo=tipo,
        titulo=f"Contrato {contrato.numero} vence em {dias} dias",
        mensagem=f"Contrato vence em {dias} dias.",
        data_referencia=contrato.termino,
        status=AlertaStatus.pendente.value,
    )
    db.add(alerta)
    db.commit()
    db.refresh(alerta)
    return alerta
