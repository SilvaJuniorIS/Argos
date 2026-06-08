from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.documento_gerado import (
    DocumentoGeradoRead,
    DocumentoGeradoUpdate,
    DocumentoGerarRequest,
)
from app.services import documento_gerado_service
from app.services.documento_gerado_service import (
    DocumentoGeracaoError,
    LLMDocumentoConfigurationError,
    LLMDocumentoTimeoutError,
)

router = APIRouter()


@router.post("/documentos/gerar", response_model=DocumentoGeradoRead)
def gerar_documento(
    payload: DocumentoGerarRequest,
    db: Annotated[Session, Depends(get_db)],
) -> DocumentoGeradoRead:
    try:
        return documento_gerado_service.gerar_documento(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except LLMDocumentoConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except LLMDocumentoTimeoutError as exc:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=str(exc),
        ) from exc
    except DocumentoGeracaoError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc


@router.get("/documentos/gerados/{documento_id}", response_model=DocumentoGeradoRead)
def obter_documento_gerado(
    documento_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> DocumentoGeradoRead:
    documento = documento_gerado_service.get_documento(db, documento_id)
    if documento is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento gerado nao encontrado",
        )
    return documento


@router.patch("/documentos/gerados/{documento_id}", response_model=DocumentoGeradoRead)
def atualizar_documento_gerado(
    documento_id: int,
    payload: DocumentoGeradoUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> DocumentoGeradoRead:
    documento = documento_gerado_service.get_documento(db, documento_id)
    if documento is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento gerado nao encontrado",
        )
    if not payload.conteudo.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Conteudo do documento nao pode ficar vazio",
        )
    return documento_gerado_service.atualizar_documento(db, documento, payload.conteudo)


@router.get("/documentos/gerados/{documento_id}/exportar-docx")
def exportar_documento_gerado_docx(
    documento_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> StreamingResponse:
    documento = documento_gerado_service.get_documento(db, documento_id)
    if documento is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento gerado nao encontrado",
        )
    try:
        buffer, filename = documento_gerado_service.exportar_docx(documento)
    except DocumentoGeracaoError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

