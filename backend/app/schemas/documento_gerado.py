from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

TipoDocumento = Literal["ETP", "TR", "EDITAL"]


class DocumentoGerarRequest(BaseModel):
    processo_id: int = Field(..., gt=0)
    tipo_documento: TipoDocumento | None = None


class DocumentoGeradoRead(BaseModel):
    id: int
    processo_id: int
    tipo_documento: str
    modelo: str
    conteudo: str
    created_at: datetime
    revisado_em: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class DocumentoGeradoUpdate(BaseModel):
    conteudo: str = Field(..., min_length=1, max_length=120000)
