from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.institucional import Institucional
from app.schemas.institucional import InstitucionalUpdate

DEFAULT_NOME_ORGAO = "Prefeitura Municipal"


def get_config(db: Session) -> Institucional:
    config = db.scalar(select(Institucional).order_by(Institucional.id.asc()).limit(1))
    if config is not None:
        return config

    config = Institucional(
        nome_orgao=DEFAULT_NOME_ORGAO,
        rodape_documentos=(
            "Documento gerado pelo ARGOS para apoio a elaboracao de minutas. "
            "Revise tecnicamente, juridicamente e administrativamente antes do uso oficial."
        ),
    )
    db.add(config)
    db.commit()
    db.refresh(config)
    return config


def update_config(db: Session, payload: InstitucionalUpdate) -> Institucional:
    config = get_config(db)
    for field, value in payload.model_dump().items():
        setattr(config, field, value)

    db.add(config)
    db.commit()
    db.refresh(config)
    return config
