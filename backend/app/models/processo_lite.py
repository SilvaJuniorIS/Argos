from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class ProcessoLite(Base):
    __tablename__ = "lite_processos"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    numero: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    objeto: Mapped[str] = mapped_column(Text, nullable=False)
    area_requisitante: Mapped[str | None] = mapped_column(String(160))
    tipo_documento: Mapped[str] = mapped_column(String(20), default="ETP", nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="rascunho", nullable=False)
    documento_gerado: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
