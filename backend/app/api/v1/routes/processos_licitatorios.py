from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.processo_licitatorio import (
    ProcessoLicitatorioDashboard,
    ProcessoLicitatorioCreate,
    ProcessoLicitatorioRead,
    ProcessoLicitatorioUpdate,
)
from app.services import processo_licitatorio_service

router = APIRouter()


@router.post("/", response_model=ProcessoLicitatorioRead, status_code=status.HTTP_201_CREATED)
def criar_processo_licitatorio(
    payload: ProcessoLicitatorioCreate,
    db: Annotated[Session, Depends(get_db)],
):
    return processo_licitatorio_service.create_processo(db, payload)


@router.get("/", response_model=list[ProcessoLicitatorioRead])
def listar_processos_licitatorios(db: Annotated[Session, Depends(get_db)]):
    return processo_licitatorio_service.list_processos(db)


@router.get("/dashboard", response_model=ProcessoLicitatorioDashboard)
def dashboard_processos_licitatorios(db: Annotated[Session, Depends(get_db)]):
    return processo_licitatorio_service.get_dashboard(db)


@router.get("/{processo_id}", response_model=ProcessoLicitatorioRead)
def buscar_processo_licitatorio_por_id(
    processo_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    processo = processo_licitatorio_service.get_processo(db, processo_id)
    if processo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Processo licitatorio nao encontrado",
        )
    return processo


@router.patch("/{processo_id}", response_model=ProcessoLicitatorioRead)
def atualizar_processo_licitatorio(
    processo_id: int,
    payload: ProcessoLicitatorioUpdate,
    db: Annotated[Session, Depends(get_db)],
):
    processo = processo_licitatorio_service.get_processo(db, processo_id)
    if processo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Processo licitatorio nao encontrado",
        )
    return processo_licitatorio_service.update_processo(db, processo, payload)
