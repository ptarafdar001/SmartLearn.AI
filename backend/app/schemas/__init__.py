"""Pydantic request and response schemas."""

from app.schemas.auth import (
    Token,
    TokenPayload,
    UserBase,
    UserCreate,
    UserLogin,
    UserResponse,
)
from app.schemas.dashboard import (
    DashboardOverviewResponse,
    EnrolledSubjectSummary,
    RecommendationItem,
    RecommendationsResponse,
    StudyTargetSummary,
)
from app.schemas.onboarding import (
    LearningPreferenceResponse,
    OnboardingStatusResponse,
    Step1BoardClass,
    Step2StreamSubjects,
    Step3PreferencesGoals,
    Step4Schedule,
    StudentProfileResponse,
    StudyGoalResponse,
    StudyScheduleResponse,
    SubjectSelectionResponse,
)

__all__ = [
    "UserBase",
    "UserCreate",
    "UserLogin",
    "Token",
    "TokenPayload",
    "UserResponse",
    "Step1BoardClass",
    "StudentProfileResponse",
    "Step2StreamSubjects",
    "SubjectSelectionResponse",
    "Step3PreferencesGoals",
    "LearningPreferenceResponse",
    "StudyGoalResponse",
    "Step4Schedule",
    "StudyScheduleResponse",
    "OnboardingStatusResponse",
    "DashboardOverviewResponse",
    "EnrolledSubjectSummary",
    "RecommendationItem",
    "RecommendationsResponse",
    "StudyTargetSummary",
]
