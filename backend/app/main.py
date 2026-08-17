"""
app/main.py – Application entry point.

Start the server with:
    uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings

settings = get_settings()

# ── App factory ───────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# ── Middleware ────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Core routes ──────────────────────────────────────────────────────────────
@app.get("/", tags=["Root"])
async def root() -> dict:
    """Health-check / welcome endpoint."""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    """Lightweight liveness probe."""
    return {"status": "ok"}


# ── Router registration (add feature routers here) ───────────────────────────
# from app.api.v1 import users, courses
# app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
# app.include_router(courses.router, prefix="/api/v1/courses", tags=["Courses"])
