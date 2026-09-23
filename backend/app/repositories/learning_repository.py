"""
Repository for learning entities and student progress data access.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

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


class LearningRepository:
    """Encapsulates all PostgreSQL queries for subjects, chapters, topics, resources, and progress."""

    # ── Subjects ──────────────────────────────────────────────────────────────
    @staticmethod
    def get_subject_by_id(db: Session, subject_id: int) -> Optional[Subject]:
        """Fetch subject by primary key."""
        return db.query(Subject).filter(Subject.id == subject_id, Subject.is_active == True).first()

    @staticmethod
    def get_subject_by_code(db: Session, code: str) -> Optional[Subject]:
        """Fetch subject by unique canonical code."""
        return db.query(Subject).filter(Subject.code == code, Subject.is_active == True).first()

    @staticmethod
    def get_subjects_by_board_grade(
        db: Session,
        board: str,
        grade: str,
        academic_stream: Optional[str] = None,
    ) -> List[Subject]:
        """Fetch active subjects matching board, grade, and optional stream."""
        query = db.query(Subject).filter(
            Subject.board == board,
            Subject.grade == grade,
            Subject.is_active == True,
        )
        if academic_stream:
            # Match exact, substring (e.g. 'Humanities' in 'Humanities / Arts'), or stream-independent subjects
            query = query.filter(
                (Subject.academic_stream == academic_stream)
                | (Subject.academic_stream.ilike(f"%{academic_stream}%"))
                | (Subject.academic_stream.is_(None))
            )
        return query.order_by(Subject.display_order, Subject.id).all()

    @staticmethod
    def get_all_active_subjects(db: Session) -> List[Subject]:
        """Fetch all active subjects."""
        return db.query(Subject).filter(Subject.is_active == True).order_by(Subject.display_order).all()

    # ── Chapters ──────────────────────────────────────────────────────────────
    @staticmethod
    def get_chapter_by_id(db: Session, chapter_id: int) -> Optional[Chapter]:
        """Fetch chapter by primary key."""
        return db.query(Chapter).filter(Chapter.id == chapter_id).first()

    @staticmethod
    def get_chapters_by_subject_id(db: Session, subject_id: int) -> List[Chapter]:
        """Fetch ordered chapters belonging to a subject."""
        return (
            db.query(Chapter)
            .filter(Chapter.subject_id == subject_id)
            .order_by(Chapter.chapter_number)
            .all()
        )

    # ── Topics ────────────────────────────────────────────────────────────────
    @staticmethod
    def get_topic_by_id(db: Session, topic_id: int) -> Optional[Topic]:
        """Fetch topic by primary key."""
        return db.query(Topic).filter(Topic.id == topic_id).first()

    @staticmethod
    def get_topics_by_chapter_id(db: Session, chapter_id: int) -> List[Topic]:
        """Fetch ordered topics belonging to a chapter."""
        return (
            db.query(Topic)
            .filter(Topic.chapter_id == chapter_id)
            .order_by(Topic.topic_number)
            .all()
        )

    # ── Learning Resources ────────────────────────────────────────────────────
    @staticmethod
    def get_resources_by_topic_id(
        db: Session, topic_id: int, only_active: bool = True
    ) -> List[LearningResource]:
        """Fetch learning resources for a topic ordered by order_index."""
        query = db.query(LearningResource).filter(LearningResource.topic_id == topic_id)
        if only_active:
            query = query.filter(LearningResource.is_active == True)
        return query.order_by(LearningResource.order_index).all()

    # ── Student Progress ──────────────────────────────────────────────────────
    @staticmethod
    def get_student_progress(
        db: Session, user_id: int, topic_id: int
    ) -> Optional[StudentProgress]:
        """Fetch student progress on a specific topic."""
        return (
            db.query(StudentProgress)
            .filter(
                StudentProgress.user_id == user_id,
                StudentProgress.topic_id == topic_id,
            )
            .first()
        )

    @staticmethod
    def get_user_progress_for_topics(
        db: Session, user_id: int, topic_ids: List[int]
    ) -> Dict[int, StudentProgress]:
        """Batch fetch student progress records indexed by topic_id."""
        if not topic_ids:
            return {}
        records = (
            db.query(StudentProgress)
            .filter(
                StudentProgress.user_id == user_id,
                StudentProgress.topic_id.in_(topic_ids),
            )
            .all()
        )
        return {r.topic_id: r for r in records}

    @staticmethod
    def get_all_progress_for_user(db: Session, user_id: int) -> List[StudentProgress]:
        """Fetch all progress records for a user."""
        return db.query(StudentProgress).filter(StudentProgress.user_id == user_id).all()

    @staticmethod
    def get_recent_progress_for_user(
        db: Session, user_id: int, limit: int = 5
    ) -> List[StudentProgress]:
        """Fetch the most recently accessed topic progress records."""
        return (
            db.query(StudentProgress)
            .filter(StudentProgress.user_id == user_id)
            .order_by(StudentProgress.last_accessed_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def upsert_student_progress(
        db: Session,
        user_id: int,
        topic_id: int,
        status: str,
        progress_percentage: float,
        time_spent_seconds: int,
        completed_at: Optional[datetime] = None,
    ) -> StudentProgress:
        """Create or update a student's topic progress record."""
        now = datetime.now(timezone.utc)
        record = (
            db.query(StudentProgress)
            .filter(
                StudentProgress.user_id == user_id,
                StudentProgress.topic_id == topic_id,
            )
            .first()
        )
        if record:
            record.status = status
            record.progress_percentage = progress_percentage
            record.time_spent_seconds = time_spent_seconds
            record.last_accessed_at = now
            if completed_at is not None:
                record.completed_at = completed_at
            elif status == "completed" and record.completed_at is None:
                record.completed_at = now
            elif status != "completed":
                record.completed_at = None
        else:
            final_completed = completed_at or (now if status == "completed" else None)
            record = StudentProgress(
                user_id=user_id,
                topic_id=topic_id,
                status=status,
                progress_percentage=progress_percentage,
                time_spent_seconds=time_spent_seconds,
                last_accessed_at=now,
                completed_at=final_completed,
            )
            db.add(record)

        db.commit()
        db.refresh(record)
        return record

    # ── Learning Objectives ───────────────────────────────────────────────────
    @staticmethod
    def get_learning_objectives(
        db: Session, topic_id: int, only_verified: bool = True
    ) -> List[LearningObjective]:
        """Fetch curriculum learning objectives for a topic."""
        query = db.query(LearningObjective).filter(LearningObjective.topic_id == topic_id)
        if only_verified:
            query = query.filter(LearningObjective.is_verified == True)
        return query.order_by(LearningObjective.code).all()

    # ── Previous Year Questions (PYQs) ────────────────────────────────────────
    @staticmethod
    def get_pyqs_by_topic_id(
        db: Session, topic_id: int, only_verified: bool = True
    ) -> List[PreviousYearQuestion]:
        """Fetch authentic previous-year exam questions for a topic."""
        query = db.query(PreviousYearQuestion).filter(PreviousYearQuestion.topic_id == topic_id)
        if only_verified:
            query = query.filter(PreviousYearQuestion.is_verified == True)
        return query.order_by(PreviousYearQuestion.exam_year.desc()).all()

    @staticmethod
    def get_pyqs_by_subject_id(
        db: Session, subject_id: int, only_verified: bool = True
    ) -> List[PreviousYearQuestion]:
        """Fetch authentic previous-year exam questions for an entire subject."""
        query = db.query(PreviousYearQuestion).filter(PreviousYearQuestion.subject_id == subject_id)
        if only_verified:
            query = query.filter(PreviousYearQuestion.is_verified == True)
        return query.order_by(PreviousYearQuestion.exam_year.desc()).all()

    @staticmethod
    def get_pyq_by_id(db: Session, pyq_id: int) -> Optional[PreviousYearQuestion]:
        """Fetch a single authentic PYQ by primary key."""
        return db.query(PreviousYearQuestion).filter(PreviousYearQuestion.id == pyq_id).first()

    # ── Practice Questions (AI-Generated & Curated) ───────────────────────────
    @staticmethod
    def get_practice_questions(
        db: Session, topic_id: int, difficulty: Optional[str] = None
    ) -> List[PracticeQuestion]:
        """Fetch practice questions for a topic, optionally filtered by difficulty."""
        query = db.query(PracticeQuestion).filter(PracticeQuestion.topic_id == topic_id)
        if difficulty:
            query = query.filter(PracticeQuestion.difficulty == difficulty)
        return query.order_by(PracticeQuestion.id).all()

    @staticmethod
    def get_practice_question_by_id(
        db: Session, question_id: int
    ) -> Optional[PracticeQuestion]:
        """Fetch a single practice question by primary key."""
        return db.query(PracticeQuestion).filter(PracticeQuestion.id == question_id).first()

    # ── Student Question Attempts ─────────────────────────────────────────────
    @staticmethod
    def record_question_attempt(
        db: Session,
        user_id: int,
        question_type: str,
        user_answer: str,
        is_correct: Optional[bool] = None,
        marks_obtained: Optional[float] = None,
        feedback: Optional[str] = None,
        pyq_id: Optional[int] = None,
        practice_question_id: Optional[int] = None,
    ) -> StudentQuestionAttempt:
        """Persist a student attempt on a PYQ or practice question."""
        now = datetime.now(timezone.utc)
        attempt = StudentQuestionAttempt(
            user_id=user_id,
            question_type=question_type,
            user_answer=user_answer,
            is_correct=is_correct,
            marks_obtained=marks_obtained,
            feedback=feedback,
            pyq_id=pyq_id,
            practice_question_id=practice_question_id,
            attempted_at=now,
        )
        db.add(attempt)
        db.commit()
        db.refresh(attempt)
        return attempt

    @staticmethod
    def get_user_question_attempts(
        db: Session, user_id: int, limit: int = 50, topic_id: Optional[int] = None
    ) -> List[StudentQuestionAttempt]:
        """Fetch recent attempts for a student, optionally filtered by topic."""
        query = db.query(StudentQuestionAttempt).filter(StudentQuestionAttempt.user_id == user_id)
        if topic_id is not None:
            query = query.outerjoin(
                PracticeQuestion, StudentQuestionAttempt.practice_question_id == PracticeQuestion.id
            ).outerjoin(
                PreviousYearQuestion, StudentQuestionAttempt.pyq_id == PreviousYearQuestion.id
            ).filter(
                (PracticeQuestion.topic_id == topic_id) | (PreviousYearQuestion.topic_id == topic_id)
            )
        return (
            query.order_by(StudentQuestionAttempt.attempted_at.desc())
            .limit(limit)
            .all()
        )

    # ── Topic Study Notes ─────────────────────────────────────────────────────
    @staticmethod
    def get_topic_study_notes(
        db: Session, topic_id: int, notes_type: str = "comprehensive"
    ) -> Optional[TopicStudyNotes]:
        """Fetch cached study notes for a topic."""
        return (
            db.query(TopicStudyNotes)
            .filter(
                TopicStudyNotes.topic_id == topic_id,
                TopicStudyNotes.notes_type == notes_type,
            )
            .first()
        )

    @staticmethod
    def upsert_topic_study_notes(
        db: Session,
        topic_id: int,
        notes_type: str,
        title: str,
        overview: str,
        explanation_markdown: str,
        learning_objectives_json: Optional[Any] = None,
        key_terms_json: Optional[Any] = None,
        formulas_and_dates_json: Optional[Any] = None,
        diagrams_json: Optional[Any] = None,
        common_misconceptions_json: Optional[Any] = None,
        exam_points_json: Optional[Any] = None,
        practice_questions_json: Optional[Any] = None,
        source_references_json: Optional[Any] = None,
        is_verified: bool = True,
    ) -> TopicStudyNotes:
        """Create or update cached study notes for a topic."""
        now = datetime.now(timezone.utc)
        record = (
            db.query(TopicStudyNotes)
            .filter(
                TopicStudyNotes.topic_id == topic_id,
                TopicStudyNotes.notes_type == notes_type,
            )
            .first()
        )
        if record:
            record.title = title
            record.overview = overview
            record.explanation_markdown = explanation_markdown
            record.learning_objectives_json = learning_objectives_json
            record.key_terms_json = key_terms_json
            record.formulas_and_dates_json = formulas_and_dates_json
            record.diagrams_json = diagrams_json
            record.common_misconceptions_json = common_misconceptions_json
            record.exam_points_json = exam_points_json
            record.practice_questions_json = practice_questions_json
            record.source_references_json = source_references_json
            record.version += 1
            record.is_verified = is_verified
            record.updated_at = now
        else:
            record = TopicStudyNotes(
                topic_id=topic_id,
                notes_type=notes_type,
                title=title,
                overview=overview,
                explanation_markdown=explanation_markdown,
                learning_objectives_json=learning_objectives_json,
                key_terms_json=key_terms_json,
                formulas_and_dates_json=formulas_and_dates_json,
                diagrams_json=diagrams_json,
                common_misconceptions_json=common_misconceptions_json,
                exam_points_json=exam_points_json,
                practice_questions_json=practice_questions_json,
                source_references_json=source_references_json,
                version=1,
                is_verified=is_verified,
                created_at=now,
                updated_at=now,
            )
            db.add(record)

        db.commit()
        db.refresh(record)
        return record

