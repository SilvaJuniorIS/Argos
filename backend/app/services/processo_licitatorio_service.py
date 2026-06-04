from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.documento_gerado import DocumentoGerado
from app.models.processo_licitatorio import ProcessoLicitatorio, ProcessoLicitatorioItem
from app.schemas.processo_licitatorio import (
    ProcessoLicitatorioDashboard,
    ProcessoLicitatorioDashboardItem,
    ProcessoLicitatorioDashboardStatusTotal,
    ProcessoLicitatorioCreate,
    ProcessoLicitatorioUpdate,
)


def create_processo(
    db: Session,
    payload: ProcessoLicitatorioCreate,
) -> ProcessoLicitatorio:
    payload_data = payload.model_dump(exclude={"itens"})
    processo = ProcessoLicitatorio(**payload_data)
    processo.itens = _build_itens(payload)
    db.add(processo)
    db.commit()
    db.refresh(processo)
    return processo


def list_processos(db: Session) -> list[ProcessoLicitatorio]:
    statement = (
        select(ProcessoLicitatorio)
        .options(selectinload(ProcessoLicitatorio.itens))
        .order_by(ProcessoLicitatorio.created_at.desc())
    )
    return list(db.scalars(statement).all())


def get_processo(db: Session, processo_id: int) -> ProcessoLicitatorio | None:
    statement = (
        select(ProcessoLicitatorio)
        .options(selectinload(ProcessoLicitatorio.itens))
        .where(ProcessoLicitatorio.id == processo_id)
    )
    return db.scalar(statement)


def get_dashboard(db: Session, limit: int = 6) -> ProcessoLicitatorioDashboard:
    total_processos = db.scalar(select(func.count(ProcessoLicitatorio.id))) or 0
    total_documentos = db.scalar(select(func.count(DocumentoGerado.id))) or 0

    document_stats = _document_stats_by_processo(db)
    processos = list(
        db.scalars(
            select(ProcessoLicitatorio)
            .order_by(ProcessoLicitatorio.created_at.desc())
            .limit(limit)
        ).all()
    )

    status_totals = {"Rascunho": 0, "Gerado": 0, "Revisado": 0}
    for processo_id in db.scalars(select(ProcessoLicitatorio.id)).all():
        status = _status_processo(document_stats.get(processo_id))
        status_totals[status] += 1

    ultimos = [
        ProcessoLicitatorioDashboardItem(
            id=processo.id,
            objeto=processo.objeto,
            secretaria=processo.secretaria,
            tipo_documento=processo.tipo_documento,
            modalidade=processo.modalidade,
            created_at=processo.created_at,
            status=_status_processo(document_stats.get(processo.id)),
            total_documentos=document_stats.get(processo.id, {}).get("total", 0),
        )
        for processo in processos
    ]

    return ProcessoLicitatorioDashboard(
        total_processos=total_processos,
        total_documentos_gerados=total_documentos,
        total_rascunho=status_totals["Rascunho"],
        total_gerado=status_totals["Gerado"],
        total_revisado=status_totals["Revisado"],
        por_status=[
            ProcessoLicitatorioDashboardStatusTotal(status=status, total=total)
            for status, total in status_totals.items()
        ],
        ultimos_processos=ultimos,
    )


def update_processo(
    db: Session,
    processo: ProcessoLicitatorio,
    payload: ProcessoLicitatorioUpdate,
) -> ProcessoLicitatorio:
    update_data = payload.model_dump(exclude_unset=True, exclude={"itens"})
    for field, value in update_data.items():
        setattr(processo, field, value)
    if payload.itens is not None:
        processo.itens = [
            ProcessoLicitatorioItem(
                ordem=index,
                descricao=item.descricao,
                quantidade=item.quantidade,
                unidade_medida=item.unidade_medida,
                observacoes=item.observacoes,
            )
            for index, item in enumerate(payload.itens, start=1)
        ]
    db.add(processo)
    db.commit()
    db.refresh(processo)
    return processo


def delete_processo(db: Session, processo: ProcessoLicitatorio) -> None:
    db.delete(processo)
    db.commit()


def _document_stats_by_processo(db: Session) -> dict[int, dict[str, int]]:
    rows = db.execute(
        select(
            DocumentoGerado.processo_id,
            func.count(DocumentoGerado.id),
            func.count(DocumentoGerado.revisado_em),
        ).group_by(DocumentoGerado.processo_id)
    ).all()
    return {
        processo_id: {"total": int(total or 0), "revisados": int(revisados or 0)}
        for processo_id, total, revisados in rows
    }


def _status_processo(stats: dict[str, int] | None) -> str:
    if not stats or stats["total"] == 0:
        return "Rascunho"
    if stats["revisados"] > 0:
        return "Revisado"
    return "Gerado"


def _build_itens(payload: ProcessoLicitatorioCreate) -> list[ProcessoLicitatorioItem]:
    itens = payload.itens
    if not itens and payload.quantidade is not None and payload.unidade_medida:
        itens = [
            ProcessoLicitatorioItem(
                ordem=1,
                descricao=payload.objeto,
                quantidade=payload.quantidade,
                unidade_medida=payload.unidade_medida,
                observacoes=payload.observacoes,
            )
        ]
        return itens

    return [
        ProcessoLicitatorioItem(
            ordem=index,
            descricao=item.descricao,
            quantidade=item.quantidade,
            unidade_medida=item.unidade_medida,
            observacoes=item.observacoes,
        )
        for index, item in enumerate(itens, start=1)
    ]
