from fastapi import APIRouter

from app.api.analytics.routes import router as analytics_router
from app.api.auth.routes import router as auth_router
from app.api.learning.routes import router as learning_router
from app.api.tutor.routes import router as tutor_router
from app.api.users.routes import router as users_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(learning_router)
api_router.include_router(analytics_router)
api_router.include_router(tutor_router)

__all__ = ["api_router"]

