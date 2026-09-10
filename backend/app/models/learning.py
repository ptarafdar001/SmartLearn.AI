"""
Learning Foundation ORM Models for SmartLearn.AI.

Defines the canonical curriculum hierarchy:
    Subject -> Chapter -> Topic -> LearningResource
and student learning state tracking:
    User -> StudentProgress -> Topic
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Subject(Base):
    """Canonical catalog of educational subjects by board, grade, and optional stream."""

    __tablename__ = "subjects"
    __table_args__ = (
        Index("ix_subjects_board_grade_stream", "board", "grade", "academic_stream"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    board: Mapped[str] = mapped_column(String(100), nullable=False)
    grade: Mapped[str] = mapped_column(String(50), nullable=False)
    academic_stream: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    category: Mapped[str] = mapped_column(
        String(50), default="core", nullable=False
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
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
    chapters: Mapped[List["Chapter"]] = relationship(
        "Chapter",
        back_populates="subject",
        cascade="all, delete-orphan",
        order_by="Chapter.chapter_number",
    )

    def __repr__(self) -> str:
        return f"<Subject id={self.id} code={self.code!r} name={self.name!r} board={self.board!r} grade={self.grade!r}>"


class Chapter(Base):
    """Sequential unit/chapter within a curriculum subject."""

    __tablename__ = "chapters"
    __table_args__ = (
        UniqueConstraint(
            "subject_id", "chapter_number", name="uq_subject_chapter_number"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    subject_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("subjects.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    chapter_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
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
    subject: Mapped["Subject"] = relationship("Subject", back_populates="chapters")
    topics: Mapped[List["Topic"]] = relationship(
        "Topic",
        back_populates="chapter",
        cascade="all, delete-orphan",
        order_by="Topic.topic_number",
    )

    def __repr__(self) -> str:
        return f"<Chapter id={self.id} subject_id={self.subject_id} number={self.chapter_number} title={self.title!r}>"


class Topic(Base):
    """Atomic concept or lesson unit within a chapter."""

    __tablename__ = "topics"
    __table_args__ = (
        UniqueConstraint(
            "chapter_id", "topic_number", name="uq_chapter_topic_number"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chapter_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("chapters.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    topic_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    estimated_minutes: Mapped[int] = mapped_column(
        Integer, default=15, nullable=False
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
    chapter: Mapped["Chapter"] = relationship("Chapter", back_populates="topics")
    learning_resources: Mapped[List["LearningResource"]] = relationship(
        "LearningResource",
        back_populates="topic",
        cascade="all, delete-orphan",
        order_by="LearningResource.order_index",
    )
    student_progress_records: Mapped[List["StudentProgress"]] = relationship(
        "StudentProgress",
        back_populates="topic",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Topic id={self.id} chapter_id={self.chapter_id} number={self.topic_number} title={self.title!r}>"


class LearningResource(Base):
    """
    Multi-modal learning resource associated with a topic.
    Supports modalities: text, video, audio, notes, quiz, practice, interactive, revision.
    Includes explicit provenance and source tracking metadata.
    """

    __tablename__ = "learning_resources"
    __table_args__ = (
        Index("ix_resources_topic_type", "topic_id", "resource_type"),
        Index("ix_resources_provider", "provider"),
        Index("ix_resources_external_id", "external_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topic_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("topics.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False)
    provider: Mapped[str] = mapped_column(
        String(50), default="smartlearn", nullable=False
    )
    source_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    external_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    content_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    text_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    language: Mapped[str] = mapped_column(String(20), default="en", nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    verified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
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
    topic: Mapped["Topic"] = relationship("Topic", back_populates="learning_resources")

    def __repr__(self) -> str:
        return f"<LearningResource id={self.id} topic_id={self.topic_id} type={self.resource_type!r} provider={self.provider!r}>"


class StudentProgress(Base):
    """
    Tracks per-topic learning state, duration, and completion for an individual student.
    Enforces a unique constraint on (user_id, topic_id).
    """

    __tablename__ = "student_progress"
    __table_args__ = (
        UniqueConstraint("user_id", "topic_id", name="uq_user_topic_progress"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    topic_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("topics.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(50), default="not_started", nullable=False
    )
    progress_percentage: Mapped[float] = mapped_column(
        Float, default=0.0, nullable=False
    )
    time_spent_seconds: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    last_accessed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
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
    user: Mapped["User"] = relationship(  # type: ignore[name-defined]
        "User", back_populates="student_progress_records"
    )
    topic: Mapped["Topic"] = relationship(
        "Topic", back_populates="student_progress_records"
    )

    def __repr__(self) -> str:
        return f"<StudentProgress id={self.id} user_id={self.user_id} topic_id={self.topic_id} status={self.status!r} progress={self.progress_percentage}%>"
