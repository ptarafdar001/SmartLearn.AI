"""
SmartLearn.AI Backend Application Entry Point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    openapi_tags=[
        {"name": "Root", "description": "Welcome and diagnostics"},
        {"name": "Health", "description": "Service health probes"},
        {"name": "Authentication", "description": "Registration, login, and token management"},
        {"name": "Users & Onboarding", "description": "4-step student onboarding and status"},
        {"name": "Learning", "description": "Enrolled subjects and study recommendations"},
        {"name": "Analytics", "description": "Student dashboard overview and progress metrics"},
    ],
)

# ── CORS Middleware ───────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=(
        settings.ALLOWED_ORIGINS
        if isinstance(settings.ALLOWED_ORIGINS, list)
        else [settings.ALLOWED_ORIGINS]
    ),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Core Root Routes ──────────────────────────────────────────────────────────
@app.get("/", tags=["Root"])
def root() -> dict:
    """Welcome / root endpoint."""
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
def health() -> dict:
    """Service liveness probe."""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
    }


# ── API v1 Router Registration ────────────────────────────────────────────────
app.include_router(api_router, prefix=settings.API_V1_STR)
