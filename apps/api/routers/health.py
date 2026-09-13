"""Health check endpoint."""
from fastapi import APIRouter
from pydantic import BaseModel
import time

router = APIRouter(prefix="/api", tags=["health"])

_START_TIME = time.time()

class HealthResponse(BaseModel):
    status: str
    version: str
    uptime_seconds: float

@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Liveness check. Returns 200 if the API is running."""
    return HealthResponse(
        status="ok",
        version="0.1.0",
        uptime_seconds=round(time.time() - _START_TIME, 2),
    )
