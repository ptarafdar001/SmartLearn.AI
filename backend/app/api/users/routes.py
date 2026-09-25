from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user
from app.db.session import get_db
from app.models.users import User
from app.schemas.onboarding import (
    OnboardingStatusResponse,
    Step1BoardClass,
    Step2StreamSubjects,
    Step3PreferencesGoals,
    Step4Schedule,
    StudentProfileResponse,
    StudyScheduleResponse,
    SubjectSelectionResponse,
)
from app.services.onboarding_service import OnboardingService

router = APIRouter(prefix="/users", tags=["Users & Onboarding"])


@router.post(
    "/onboarding/step1",
    response_model=StudentProfileResponse,
    summary="Step 1: Board and Class selection",
)
def submit_step1(
    data: Step1BoardClass,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> StudentProfileResponse:
    """Save or update academic board, grade, and optional stream for the authenticated user."""
    try:
        return OnboardingService.save_step1_board_class(
            db=db, user_id=current_user.id, data=data
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/onboarding/step2",
    response_model=List[SubjectSelectionResponse],
    summary="Step 2: Stream and Subjects selection",
)
def submit_step2(
    data: Step2StreamSubjects,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> List[SubjectSelectionResponse]:
    """Save or replace enrolled subjects for the authenticated user."""
    try:
        return OnboardingService.save_step2_stream_subjects(
            db=db, user_id=current_user.id, data=data
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/onboarding/step3",
    response_model=Dict[str, Any],
    summary="Step 3: Learning Preferences and Goals",
)
def submit_step3(
    data: Step3PreferencesGoals,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Save learning style preference and study goals for the authenticated user."""
    try:
        return OnboardingService.save_step3_preferences_goals(
            db=db, user_id=current_user.id, data=data
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/onboarding/step4",
    response_model=StudyScheduleResponse,
    summary="Step 4: Study Schedule and Finalize Onboarding",
)
def submit_step4(
    data: Step4Schedule,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> StudyScheduleResponse:
    """
    Save study schedule and complete onboarding.
    Only this step marks the user as fully onboarded (is_onboarded = True).
    """
    try:
        return OnboardingService.save_step4_schedule(
            db=db, user_id=current_user.id, data=data
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/onboarding/status",
    response_model=OnboardingStatusResponse,
    summary="Get 4-step onboarding progress",
)
def get_onboarding_status(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> OnboardingStatusResponse:
    """Retrieve completion status for each onboarding step and current active step."""
    try:
        return OnboardingService.get_onboarding_status(
            db=db, user_id=current_user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
