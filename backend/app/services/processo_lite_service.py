from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.processo_lite import ProcessoLite
from app.schemas.processo_lite import ProcessoLiteCreate, ProcessoLiteUpdate


def list_processos(db: Session) -> list[ProcessoLite]:
    return list(db.scalars(select(ProcessoLite).order_by(ProcessoLite.created_at.desc())).all())


def get_processo(db: Session, processo_id: int) -> ProcessoLite | None:
    return db.get(ProcessoLite, processo_id)


def create_processo(db: Session, payload: ProcessoLiteCreate) -> ProcessoLite:
    processo = ProcessoLite(**payload.model_dump())
    db.add(processo)
    db.commit()
    db.refresh(processo)
    return processo


def update_processo(
    db: Session,
    processo: ProcessoLite,
    payload: ProcessoLiteUpdate,
) -> ProcessoLite:
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(processo, field, value)
    db.add(processo)
    db.commit()
    db.refresh(processo)
    return processo
