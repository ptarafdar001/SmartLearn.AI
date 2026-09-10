from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user
from app.db.session import get_db
from app.models.users import User
from app.schemas.dashboard import EnrolledSubjectSummary, RecommendationsResponse
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/learning", tags=["Learning"])


@router.get(
    "/subjects",
    response_model=List[EnrolledSubjectSummary],
    summary="Get authenticated student enrolled subjects",
)
def get_user_subjects(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> List[EnrolledSubjectSummary]:
    """Retrieve subjects chosen by the authenticated student."""
    try:
        return DashboardService.get_enrolled_subjects(
            db=db, user_id=current_user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/recommendations",
    response_model=RecommendationsResponse,
    summary="Get tailored study recommendations",
)
def get_recommendations(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> RecommendationsResponse:
    """
    Retrieve study recommendations tailored strictly to the authenticated student's
    enrolled subjects, board, grade, and preferred learning style.
    """
    try:
        return DashboardService.get_recommendations(
            db=db, user_id=current_user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
