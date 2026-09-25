"""
Learning Foundation ORM Models for SmartLearn.AI.

Defines the canonical curriculum hierarchy:
    Subject -> Chapter -> Topic -> LearningResource
and student learning state tracking:
    User -> StudentProgress -> Topic
"""

from datetime import datetime
from typing import Any, List, Optional
from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
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
    previous_year_questions: Mapped[List["PreviousYearQuestion"]] = relationship(
        "PreviousYearQuestion",
        back_populates="subject",
        cascade="all, delete-orphan",
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
    learning_objectives: Mapped[List["LearningObjective"]] = relationship(
        "LearningObjective",
        back_populates="topic",
        cascade="all, delete-orphan",
        order_by="LearningObjective.code",
    )
    previous_year_questions: Mapped[List["PreviousYearQuestion"]] = relationship(
        "PreviousYearQuestion",
        back_populates="topic",
        cascade="all, delete-orphan",
        order_by="PreviousYearQuestion.exam_year.desc()",
    )
    practice_questions: Mapped[List["PracticeQuestion"]] = relationship(
        "PracticeQuestion",
        back_populates="topic",
        cascade="all, delete-orphan",
    )
    study_notes: Mapped[List["TopicStudyNotes"]] = relationship(
        "TopicStudyNotes",
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


class LearningObjective(Base):
    """
    Granular syllabus learning objective mapped to a curriculum topic.
    Provides verifiable pedagogical benchmarks (Bloom's taxonomy level).
    """

    __tablename__ = "learning_objectives"
    __table_args__ = (
        Index("ix_learning_objectives_topic", "topic_id"),
        UniqueConstraint("topic_id", "code", name="uq_topic_objective_code"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topic_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("topics.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    taxonomy_level: Mapped[str] = mapped_column(
        String(50), default="understand", nullable=False
    )
    is_core: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
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
    topic: Mapped["Topic"] = relationship("Topic", back_populates="learning_objectives")
    practice_questions: Mapped[List["PracticeQuestion"]] = relationship(
        "PracticeQuestion", back_populates="learning_objective"
    )

    def __repr__(self) -> str:
        return f"<LearningObjective id={self.id} topic_id={self.topic_id} code={self.code!r} level={self.taxonomy_level!r}>"


class PreviousYearQuestion(Base):
    """
    Authentic official examination questions from authorized board papers.
    Strictly segregated from AI-generated practice questions.
    Preserves exact board, year, paper code, question number, marks, and verified source provenance.
    """

    __tablename__ = "previous_year_questions"
    __table_args__ = (
        Index("ix_pyqs_subject_topic", "subject_id", "topic_id"),
        Index("ix_pyqs_board_year", "board", "exam_year"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    subject_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("subjects.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    topic_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("topics.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    board: Mapped[str] = mapped_column(String(50), nullable=False)
    grade: Mapped[str] = mapped_column(String(50), nullable=False)
    exam_year: Mapped[int] = mapped_column(Integer, nullable=False)
    paper_code: Mapped[str] = mapped_column(String(100), nullable=False)
    question_number: Mapped[str] = mapped_column(String(50), nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    marks: Mapped[int] = mapped_column(Integer, nullable=False)
    marking_scheme: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
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
    subject: Mapped["Subject"] = relationship("Subject", back_populates="previous_year_questions")
    topic: Mapped["Topic"] = relationship("Topic", back_populates="previous_year_questions")

    def __repr__(self) -> str:
        return f"<PreviousYearQuestion id={self.id} {self.board} {self.exam_year} {self.paper_code} {self.question_number}>"


class PracticeQuestion(Base):
    """
    AI-generated or curated practice questions explicitly labeled and distinguished from authentic PYQs.
    Maintains generation provenance and full answer keys.
    """

    __tablename__ = "practice_questions"
    __table_args__ = (
        Index("ix_practice_questions_topic", "topic_id"),
        Index("ix_practice_questions_difficulty", "difficulty"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topic_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("topics.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    learning_objective_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("learning_objectives.id", ondelete="SET NULL"),
        nullable=True,
    )
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[str] = mapped_column(
        String(50), default="mcq", nullable=False
    )  # mcq, short_answer, long_answer
    options: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)  # List[{"id": "A", "text": "..."}]
    correct_answer: Mapped[str] = mapped_column(Text, nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty: Mapped[str] = mapped_column(
        String(50), default="medium", nullable=False
    )  # easy, medium, hard
    marks: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_ai_generated: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    generation_provenance: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
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
    topic: Mapped["Topic"] = relationship("Topic", back_populates="practice_questions")
    learning_objective: Mapped[Optional["LearningObjective"]] = relationship(
        "LearningObjective", back_populates="practice_questions"
    )

    def __repr__(self) -> str:
        return f"<PracticeQuestion id={self.id} topic_id={self.topic_id} difficulty={self.difficulty!r}>"


class StudentQuestionAttempt(Base):
    """
    Records student submissions, answer correctness, marks awarded, and pedagogical feedback.
    Can be linked to either an authentic PYQ or an AI practice question.
    """

    __tablename__ = "student_question_attempts"
    __table_args__ = (
        Index("ix_attempts_user_topic", "user_id"),
        Index("ix_attempts_pyq", "pyq_id"),
        Index("ix_attempts_practice", "practice_question_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    question_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # "pyq" or "practice"
    pyq_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("previous_year_questions.id", ondelete="CASCADE"),
        nullable=True,
    )
    practice_question_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("practice_questions.id", ondelete="CASCADE"),
        nullable=True,
    )
    user_answer: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    marks_obtained: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    attempted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    user: Mapped["User"] = relationship("User")  # type: ignore[name-defined]

    def __repr__(self) -> str:
        return f"<StudentQuestionAttempt id={self.id} user_id={self.user_id} correct={self.is_correct}>"


class TopicStudyNotes(Base):
    """
    Curriculum-grounded 10-part dynamic study notes for a topic.
    Caches verified structured notes (comprehensive vs concise revision) to prevent redundant generation.
    """

    __tablename__ = "topic_study_notes"
    __table_args__ = (
        UniqueConstraint("topic_id", "notes_type", name="uq_topic_notes_type"),
        Index("ix_topic_notes_type", "topic_id", "notes_type"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topic_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("topics.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    notes_type: Mapped[str] = mapped_column(
        String(50), default="comprehensive", nullable=False
    )  # "comprehensive" or "revision"
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    overview: Mapped[str] = mapped_column(Text, nullable=False)
    learning_objectives_json: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    explanation_markdown: Mapped[str] = mapped_column(Text, nullable=False)
    key_terms_json: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    formulas_and_dates_json: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    diagrams_json: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    common_misconceptions_json: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    exam_points_json: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    practice_questions_json: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    source_references_json: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
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
    topic: Mapped["Topic"] = relationship("Topic", back_populates="study_notes")

    def __repr__(self) -> str:
        return f"<TopicStudyNotes id={self.id} topic_id={self.topic_id} type={self.notes_type!r} version={self.version}>"

