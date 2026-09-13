"""Main FastAPI application module."""
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from apps.api.routers import campaigns, health, knowledge, assets, evaluation, orchestration
from packages.shared.errors import BrandOSError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan events for the application."""
    logger.info("BrandOS API started")
    yield
    logger.info("BrandOS API stopping")


app = FastAPI(
    title="BrandOS API",
    description="BrandOS - AI-powered Creative Operating System",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(BrandOSError)
async def brandos_error_handler(request: Request, exc: BrandOSError) -> JSONResponse:
    """Global handler for BrandOS exceptions."""
    logger.error("BrandOSError occurred: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"error": exc.__class__.__name__, "message": exc.message, "detail": exc.detail},
    )


# Mount routers
# Orchestration router mounted before campaigns so /run is not consumed by /{id}
app.include_router(health.router)
app.include_router(knowledge.router)
app.include_router(orchestration.router)
app.include_router(campaigns.router)
app.include_router(assets.router)
app.include_router(evaluation.router)
