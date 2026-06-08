from sqlalchemy import inspect, text

from app.core.config import settings
from app.db.session import engine
from app.models.documento_gerado import DocumentoGerado
from app.models.processo_licitatorio import ProcessoLicitatorio, ProcessoLicitatorioItem
from app.models.processo_lite import ProcessoLite


def init_lite_db() -> None:
    if settings.auto_create_lite_tables:
        ProcessoLicitatorio.__table__.create(bind=engine, checkfirst=True)
        ProcessoLicitatorioItem.__table__.create(bind=engine, checkfirst=True)
        DocumentoGerado.__table__.create(bind=engine, checkfirst=True)
        ProcessoLite.__table__.create(bind=engine, checkfirst=True)
        _ensure_lite_columns()


def _ensure_lite_columns() -> None:
    inspector = inspect(engine)
    if "documentos_gerados" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("documentos_gerados")}
    if "revisado_em" in columns:
        return
    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE documentos_gerados ADD COLUMN revisado_em DATETIME"))
