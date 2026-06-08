from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


TipoDocumento = Literal["ETP", "TR"]


class ProcessoLiteBase(BaseModel):
    numero: str = Field(..., min_length=1, max_length=80)
    objeto: str = Field(..., min_length=3)
    area_requisitante: str | None = Field(default=None, max_length=160)
    tipo_documento: TipoDocumento = "ETP"


class ProcessoLiteCreate(ProcessoLiteBase):
    pass


class ProcessoLiteUpdate(BaseModel):
    numero: str | None = Field(default=None, min_length=1, max_length=80)
    objeto: str | None = Field(default=None, min_length=3)
    area_requisitante: str | None = Field(default=None, max_length=160)
    tipo_documento: TipoDocumento | None = None
    status: str | None = Field(default=None, max_length=40)
    documento_gerado: str | None = None


class ProcessoLiteRead(ProcessoLiteBase):
    id: int
    status: str
    documento_gerado: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
