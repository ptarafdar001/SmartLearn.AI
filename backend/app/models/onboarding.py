from datetime import datetime
from typing import Any, List, Optional
from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class StudentProfile(Base):
    """Step 1 Onboarding: Academic board, grade/class, and optional stream."""

    __tablename__ = "student_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    board: Mapped[str] = mapped_column(String(100), nullable=False)
    grade: Mapped[str] = mapped_column(String(50), nullable=False)
    academic_stream: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user: Mapped["User"] = relationship("User", back_populates="student_profile")

    def __repr__(self) -> str:
        return f"<StudentProfile id={self.id} user_id={self.user_id} board={self.board!r} grade={self.grade!r}>"


class SubjectSelection(Base):
    """Step 2 Onboarding: Subjects enrolled/chosen by the student."""

    __tablename__ = "subject_selections"
    __table_args__ = (
        UniqueConstraint("user_id", "subject_name", name="uq_user_subject"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    subject_name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="subject_selections")

    def __repr__(self) -> str:
        return f"<SubjectSelection id={self.id} user_id={self.user_id} subject={self.subject_name!r}>"


class LearningPreference(Base):
    """Step 3 Onboarding: Preferred learning style (visual, auditory, hands-on, reading)."""

    __tablename__ = "learning_preferences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    preferred_style: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="learning_preference")

    def __repr__(self) -> str:
        return f"<LearningPreference id={self.id} user_id={self.user_id} style={self.preferred_style!r}>"


class StudyGoal(Base):
    """Step 3 Onboarding: Specific study targets, competitive exams, or score ambitions."""

    __tablename__ = "study_goals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    goal_text: Mapped[str] = mapped_column(String(255), nullable=False)
    target_score: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    target_exam: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="study_goals")

    def __repr__(self) -> str:
        return f"<StudyGoal id={self.id} user_id={self.user_id} goal={self.goal_text!r}>"


class StudySchedule(Base):
    """Step 4 Onboarding: Daily targets, preferred study slots, and weekly day availability."""

    __tablename__ = "study_schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    daily_target_hours: Mapped[float] = mapped_column(Float, nullable=False)
    preferred_slot: Mapped[str] = mapped_column(String(100), nullable=False)
    available_days: Mapped[List[str]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="study_schedule")

    def __repr__(self) -> str:
        return f"<StudySchedule id={self.id} user_id={self.user_id} target_hours={self.daily_target_hours}>"
