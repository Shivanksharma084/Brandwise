"""
Brandwise API - Main application entry point
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import api_router
from app.core.config import settings
from app.db.session import init_db

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Modern FastAPI lifespan handler for startup and shutdown."""
    logger.info("Starting Brandwise API server")
    await init_db()
    logger.info("Database initialized")
    yield
    logger.info("Shutting down Brandwise API server")


def get_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(
        title="Brandwise API",
        description="AI Brand-Governance Platform - Review layer for brand content",
        version="0.1.0",
        openapi_url="/api/openapi.json",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        lifespan=lifespan,
    )

    # CORS middleware
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Include routers
    app.include_router(api_router, prefix=settings.API_V1_STR)

    return app


app = get_app()
