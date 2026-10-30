from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user
from app.db.session import get_db
from app.models.users import User
from app.schemas.dashboard import DashboardOverviewResponse
from app.services.analytics_service import AnalyticsService
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
    """Retrieve overview metrics for the authenticated student."""
    try:
        return DashboardService.get_dashboard_overview(
            db=db, user_id=current_user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/detailed",
    summary="Get real-world child routine and practice analytics",
)
def get_detailed_analytics(
    period: str = "week",
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Retrieve real-world analytics derived strictly from student question attempts, progress, and study schedule."""
    return AnalyticsService.get_detailed_student_analytics(
        db=db, user=current_user, period=period
    )


@router.post(
    "/alerts/trigger-missed-slot",
    summary="Dispatch missed routine study slot email alert to the student",
)
def send_missed_slot_alert(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Trigger an email notification alerting the student about missing their scheduled routine study slot."""
    return AnalyticsService.trigger_missed_slot_email_alert(
        db=db, user=current_user
    )
