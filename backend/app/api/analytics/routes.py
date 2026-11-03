from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user
from app.db.session import get_db
from app.models.users import User
from app.schemas.dashboard import DashboardOverviewResponse
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get(
    "/overview",
    response_model=DashboardOverviewResponse,
    summary="Get authenticated student dashboard overview",
)
def get_analytics_overview(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> DashboardOverviewResponse:
    """
    Retrieve real dashboard overview metrics for the authenticated student.
    Unavailable tracking metrics (streaks, questions solved) return null rather than fake values.
    """
    try:
        return DashboardService.get_dashboard_overview(
            db=db, user_id=current_user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
