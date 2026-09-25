from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class EnrolledSubjectSummary(BaseModel):
    """Subject enrolled by the student."""
    id: int
    subject_name: str
    progress_percentage: Optional[float] = None  # None until syllabus progress module is implemented

    model_config = ConfigDict(from_attributes=True)


class StudyTargetSummary(BaseModel):
    """Study targets derived from the student's onboarding schedule."""
    daily_target_hours: float
    preferred_slot: str
    available_days: List[str]


class DashboardOverviewResponse(BaseModel):
    """
    Dashboard overview data.
    Metrics that require future tracking modules (streaks, questions solved, syllabus progress)
    are explicitly None rather than fabricated with fake values.
    """
    user_id: int
    full_name: str
    board: Optional[str] = None
    grade: Optional[str] = None
    academic_stream: Optional[str] = None
    preferred_learning_style: Optional[str] = None
    study_target: Optional[StudyTargetSummary] = None
    goals: List[str] = []
    enrolled_subjects: List[str] = []
    total_enrolled_subjects: int = 0

    # Metrics requiring future modules (quiz_attempts, study_sessions, chapter_progress)
    study_streak_days: Optional[int] = None
    questions_solved: Optional[int] = None
    overall_progress_percentage: Optional[float] = None


class RecommendationItem(BaseModel):
    """A deterministic, data-driven study recommendation derived from the student's profile."""
    id: str
    title: str
    description: str
    subject: str
    learning_style: Optional[str] = None
    recommendation_type: str


class RecommendationsResponse(BaseModel):
    """List of tailored recommendations for the student."""
    user_id: int
    recommendations: List[RecommendationItem]
    total_count: int
