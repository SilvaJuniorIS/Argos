from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class ProcessoLicitatorio(Base):
    __tablename__ = "processos_licitatorios"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    objeto: Mapped[str] = mapped_column(Text, nullable=False)
    secretaria: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    justificativa: Mapped[str] = mapped_column(Text, nullable=False)
    quantidade: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    unidade_medida: Mapped[str | None] = mapped_column(String(60))
    modalidade: Mapped[str | None] = mapped_column(String(120))
    prazo_execucao: Mapped[str | None] = mapped_column(String(120))
    observacoes: Mapped[str | None] = mapped_column(Text)
    tipo_documento: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    itens: Mapped[list["ProcessoLicitatorioItem"]] = relationship(
        back_populates="processo",
        cascade="all, delete-orphan",
        order_by="ProcessoLicitatorioItem.ordem",
    )


class ProcessoLicitatorioItem(Base):
    __tablename__ = "processos_licitatorios_itens"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    processo_id: Mapped[int] = mapped_column(
        ForeignKey("processos_licitatorios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    ordem: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    quantidade: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    unidade_medida: Mapped[str] = mapped_column(String(60), nullable=False)
    observacoes: Mapped[str | None] = mapped_column(Text)

    processo: Mapped[ProcessoLicitatorio] = relationship(back_populates="itens")
