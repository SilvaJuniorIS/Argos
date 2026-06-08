from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.institucional import InstitucionalRead, InstitucionalUpdate
from app.services import institucional_service

router = APIRouter()


@router.get("", response_model=InstitucionalRead)
def get_institucional(db: Annotated[Session, Depends(get_db)]):
    return institucional_service.get_config(db)


@router.put("", response_model=InstitucionalRead)
def update_institucional(
    payload: InstitucionalUpdate,
    db: Annotated[Session, Depends(get_db)],
):
    return institucional_service.update_config(db, payload)
