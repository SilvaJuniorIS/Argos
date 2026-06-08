from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.mixins import TimestampMixin


class Institucional(Base, TimestampMixin):
    __tablename__ = "institucional"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome_orgao: Mapped[str] = mapped_column(String(220), nullable=False)
    nome_municipio: Mapped[str | None] = mapped_column(String(160), nullable=True)
    uf: Mapped[str | None] = mapped_column(String(2), nullable=True)
    cnpj: Mapped[str | None] = mapped_column(String(30), nullable=True)
    endereco: Mapped[str | None] = mapped_column(String(300), nullable=True)
    telefone: Mapped[str | None] = mapped_column(String(80), nullable=True)
    email: Mapped[str | None] = mapped_column(String(160), nullable=True)
    site: Mapped[str | None] = mapped_column(String(160), nullable=True)
    autoridade_nome: Mapped[str | None] = mapped_column(String(180), nullable=True)
    autoridade_cargo: Mapped[str | None] = mapped_column(String(120), nullable=True)
    responsavel_tecnico: Mapped[str | None] = mapped_column(String(180), nullable=True)
    rodape_documentos: Mapped[str | None] = mapped_column(Text, nullable=True)
    logo_base64: Mapped[str | None] = mapped_column(Text, nullable=True)
