from datetime import datetime
from typing import List, Optional
from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    """User database model representing authenticated system accounts."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        String(50), default="student", nullable=False, index=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_onboarded: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    student_profile: Mapped[Optional["StudentProfile"]] = relationship(
        "StudentProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    subject_selections: Mapped[List["SubjectSelection"]] = relationship(
        "SubjectSelection",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="SubjectSelection.id",
    )
    learning_preference: Mapped[Optional["LearningPreference"]] = relationship(
        "LearningPreference",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    study_goals: Mapped[List["StudyGoal"]] = relationship(
        "StudyGoal",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="StudyGoal.id",
    )
    study_schedule: Mapped[Optional["StudySchedule"]] = relationship(
        "StudySchedule",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    student_progress_records: Mapped[List["StudentProgress"]] = relationship(
        "StudentProgress",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r} role={self.role!r} is_onboarded={self.is_onboarded}>"
