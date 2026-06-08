from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class DocumentoGerado(Base):
    __tablename__ = "documentos_gerados"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    processo_id: Mapped[int] = mapped_column(
        ForeignKey("processos_licitatorios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    tipo_documento: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    modelo: Mapped[str] = mapped_column(String(80), nullable=False)
    conteudo: Mapped[str] = mapped_column(Text, nullable=False)
    prompt_utilizado: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    revisado_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    processo = relationship("ProcessoLicitatorio")
