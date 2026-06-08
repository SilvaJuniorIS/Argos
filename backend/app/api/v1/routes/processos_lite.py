from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.processo_lite import ProcessoLiteCreate, ProcessoLiteRead, ProcessoLiteUpdate
from app.services import processo_lite_service

router = APIRouter()


@router.get("/", response_model=list[ProcessoLiteRead])
def listar_processos(db: Annotated[Session, Depends(get_db)]):
    return processo_lite_service.list_processos(db)


@router.post("/", response_model=ProcessoLiteRead, status_code=status.HTTP_201_CREATED)
def criar_processo(payload: ProcessoLiteCreate, db: Annotated[Session, Depends(get_db)]):
    return processo_lite_service.create_processo(db, payload)


@router.get("/{processo_id}", response_model=ProcessoLiteRead)
def obter_processo(processo_id: int, db: Annotated[Session, Depends(get_db)]):
    processo = processo_lite_service.get_processo(db, processo_id)
    if processo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Processo nao encontrado",
        )
    return processo


@router.patch("/{processo_id}", response_model=ProcessoLiteRead)
def atualizar_processo(
    processo_id: int,
    payload: ProcessoLiteUpdate,
    db: Annotated[Session, Depends(get_db)],
):
    processo = processo_lite_service.get_processo(db, processo_id)
    if processo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Processo nao encontrado",
        )
    return processo_lite_service.update_processo(db, processo, payload)
