"""
SQLAlchemy ORM models package.
All models are imported here for clean discovery by Alembic and application services.
"""

from app.db.base import Base
from app.models.learning import (
    Chapter,
    LearningObjective,
    LearningResource,
    PracticeQuestion,
    PreviousYearQuestion,
    StudentProgress,
    StudentQuestionAttempt,
    Subject,
    Topic,
    TopicStudyNotes,
)
from app.models.onboarding import (
    LearningPreference,
    StudentProfile,
    StudyGoal,
    StudySchedule,
    SubjectSelection,
)
from app.models.users import User

__all__ = [
    "Base",
    "User",
    "StudentProfile",
    "SubjectSelection",
    "LearningPreference",
    "StudyGoal",
    "StudySchedule",
    "Subject",
    "Chapter",
    "Topic",
    "LearningResource",
    "StudentProgress",
    "LearningObjective",
    "PreviousYearQuestion",
    "PracticeQuestion",
    "StudentQuestionAttempt",
    "TopicStudyNotes",
]
