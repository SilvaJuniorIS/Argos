from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


TipoDocumento = Literal["ETP", "TR"]
StatusDashboard = Literal["Rascunho", "Gerado", "Revisado"]


class ProcessoLicitatorioItemBase(BaseModel):
    descricao: str = Field(..., min_length=3, max_length=500)
    quantidade: Decimal = Field(..., ge=0)
    unidade_medida: str = Field(..., min_length=1, max_length=60)
    observacoes: str | None = Field(default=None, max_length=1000)


class ProcessoLicitatorioItemCreate(ProcessoLicitatorioItemBase):
    pass


class ProcessoLicitatorioItemRead(ProcessoLicitatorioItemBase):
    id: int
    ordem: int

    model_config = ConfigDict(from_attributes=True)


class ProcessoLicitatorioBase(BaseModel):
    objeto: str = Field(..., min_length=3, max_length=2000)
    secretaria: str = Field(..., min_length=2, max_length=160)
    justificativa: str = Field(..., min_length=3, max_length=4000)
    quantidade: Decimal | None = Field(default=None, ge=0)
    unidade_medida: str | None = Field(default=None, max_length=60)
    modalidade: str | None = Field(default=None, max_length=120)
    prazo_execucao: str | None = Field(default=None, max_length=120)
    observacoes: str | None = Field(default=None, max_length=4000)
    tipo_documento: TipoDocumento


class ProcessoLicitatorioCreate(ProcessoLicitatorioBase):
    itens: list[ProcessoLicitatorioItemCreate] = Field(default_factory=list, max_length=100)


class ProcessoLicitatorioUpdate(BaseModel):
    objeto: str | None = Field(default=None, min_length=3)
    secretaria: str | None = Field(default=None, min_length=2, max_length=160)
    justificativa: str | None = Field(default=None, min_length=3)
    quantidade: Decimal | None = Field(default=None, ge=0)
    unidade_medida: str | None = Field(default=None, max_length=60)
    modalidade: str | None = Field(default=None, max_length=120)
    prazo_execucao: str | None = Field(default=None, max_length=120)
    observacoes: str | None = None
    tipo_documento: TipoDocumento | None = None
    itens: list[ProcessoLicitatorioItemCreate] | None = Field(default=None, max_length=100)


class ProcessoLicitatorioRead(ProcessoLicitatorioBase):
    id: int
    itens: list[ProcessoLicitatorioItemRead] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProcessoLicitatorioDashboardItem(BaseModel):
    id: int
    objeto: str
    secretaria: str
    tipo_documento: TipoDocumento
    modalidade: str | None = None
    created_at: datetime
    status: StatusDashboard
    total_documentos: int = 0


class ProcessoLicitatorioDashboardStatusTotal(BaseModel):
    status: StatusDashboard
    total: int


class ProcessoLicitatorioDashboard(BaseModel):
    total_processos: int
    total_documentos_gerados: int
    total_rascunho: int
    total_gerado: int
    total_revisado: int
    por_status: list[ProcessoLicitatorioDashboardStatusTotal]
    ultimos_processos: list[ProcessoLicitatorioDashboardItem]
