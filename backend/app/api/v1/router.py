from fastapi import APIRouter

from app.api.v1.routes import (
    auditoria,
    auth,
    documentos,
    fornecedores,
    institucional,
    processos_licitatorios,
    processos_lite,
    secretarias,
    users,
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(secretarias.router, prefix="/secretarias", tags=["secretarias"])
api_router.include_router(fornecedores.router, prefix="/fornecedores", tags=["fornecedores"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(documentos.router, tags=["documentos"])
api_router.include_router(auditoria.router, prefix="/auditoria", tags=["auditoria"])
api_router.include_router(institucional.router, prefix="/institucional", tags=["institucional"])
api_router.include_router(
    processos_licitatorios.router,
    prefix="/processos-licitatorios",
    tags=["processos-licitatorios"],
)
api_router.include_router(processos_lite.router, prefix="/processos-lite", tags=["processos-lite"])
