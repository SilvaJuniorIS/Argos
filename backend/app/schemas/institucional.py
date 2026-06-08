from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class InstitucionalBase(BaseModel):
    nome_orgao: str = Field(max_length=220)
    nome_municipio: str | None = Field(default=None, max_length=160)
    uf: str | None = Field(default=None, min_length=2, max_length=2)
    cnpj: str | None = Field(default=None, max_length=30)
    endereco: str | None = Field(default=None, max_length=300)
    telefone: str | None = Field(default=None, max_length=80)
    email: str | None = Field(default=None, max_length=160)
    site: str | None = Field(default=None, max_length=160)
    autoridade_nome: str | None = Field(default=None, max_length=180)
    autoridade_cargo: str | None = Field(default=None, max_length=120)
    responsavel_tecnico: str | None = Field(default=None, max_length=180)
    rodape_documentos: str | None = Field(default=None, max_length=1200)
    logo_base64: str | None = Field(default=None, max_length=500_000)


class InstitucionalUpdate(InstitucionalBase):
    pass


class InstitucionalRead(InstitucionalBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
