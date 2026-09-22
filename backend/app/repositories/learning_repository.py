"""
Repository for learning entities and student progress data access.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional
from sqlalchemy.orm import Session

from app.models.learning import Chapter, LearningResource, StudentProgress, Subject, Topic


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
