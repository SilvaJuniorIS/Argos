import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette import status
from starlette.requests import Request

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.init_db import init_lite_db

from scripts.seed import seed

logger = logging.getLogger("argos")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    init_lite_db()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        description="Backend do ARGOS para inteligencia documental, processos, ETP e TR.",
        version="0.1.0",
        lifespan=lifespan,
    )

    cors_origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=sorted(set([settings.frontend_url, *cors_origins])),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix=settings.api_v1_prefix)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        logger.warning(
            "Erro de validacao na requisicao %s %s: %s",
            request.method,
            request.url.path,
            exc.errors(),
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": jsonable_encoder(exc.errors())},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception(
            "Erro inesperado ao processar %s %s",
            request.method,
            request.url.path,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Erro interno no servidor"},
        )

    @app.get("/", include_in_schema=False)
    def root():
        return {
            "service": settings.app_name,
            "description": "ARGOS - inteligencia documental para compras publicas",
            "docs": "/docs",
            "health": "/health",
        }

    @app.get("/health")
    def health_check():
        return {"status": "ok", "service": settings.app_name}

    @app.get("/run-seed")
    def run_seed():
        if settings.environment.lower() == "production":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Endpoint indisponivel em producao",
            )
        seed()
        return {"status": "seed executado"}

    return app


app = create_app()
