from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.onboarding import (
    LearningPreference,
    StudentProfile,
    StudyGoal,
    StudySchedule,
    SubjectSelection,
)


class OnboardingRepository:
    """Data access repository for all student onboarding entities."""

    # ── Step 1: Student Profile ───────────────────────────────────────────────
    @staticmethod
    def upsert_student_profile(
        db: Session,
        user_id: int,
        board: str,
        grade: str,
        academic_stream: Optional[str] = None,
    ) -> StudentProfile:
        """Create or update student academic profile (Step 1)."""
        profile = db.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()
        if profile:
            profile.board = board
            profile.grade = grade
            profile.academic_stream = academic_stream
        else:
            profile = StudentProfile(
                user_id=user_id,
                board=board,
                grade=grade,
                academic_stream=academic_stream,
            )
            db.add(profile)
        db.commit()
        db.refresh(profile)
        return profile

    @staticmethod
    def get_student_profile(db: Session, user_id: int) -> Optional[StudentProfile]:
        """Fetch student profile by user ID."""
        return db.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()

    # ── Step 2: Subject Selections ────────────────────────────────────────────
    @staticmethod
    def replace_subject_selections(
        db: Session,
        user_id: int,
        subjects: List[str],
    ) -> List[SubjectSelection]:
        """Replace user's enrolled subjects transactionally (Step 2)."""
        # Delete existing selections for this user
        db.query(SubjectSelection).filter(SubjectSelection.user_id == user_id).delete(
            synchronize_session="fetch"
        )
        new_records = [
            SubjectSelection(user_id=user_id, subject_name=s)
            for s in subjects
        ]
        db.add_all(new_records)
        db.commit()
        return (
            db.query(SubjectSelection)
            .filter(SubjectSelection.user_id == user_id)
            .order_by(SubjectSelection.id)
            .all()
        )

    @staticmethod
    def get_subject_selections(db: Session, user_id: int) -> List[SubjectSelection]:
        """Fetch all enrolled subjects for a user."""
        return (
            db.query(SubjectSelection)
            .filter(SubjectSelection.user_id == user_id)
            .order_by(SubjectSelection.id)
            .all()
        )

    # ── Step 3: Learning Preferences & Study Goals ────────────────────────────
    @staticmethod
    def upsert_learning_preference(
        db: Session,
        user_id: int,
        preferred_style: str,
    ) -> LearningPreference:
        """Create or update student learning style preference (Step 3)."""
        pref = (
            db.query(LearningPreference)
            .filter(LearningPreference.user_id == user_id)
            .first()
        )
        if pref:
            pref.preferred_style = preferred_style
        else:
            pref = LearningPreference(
                user_id=user_id,
                preferred_style=preferred_style,
            )
            db.add(pref)
        db.commit()
        db.refresh(pref)
        return pref

    @staticmethod
    def get_learning_preference(
        db: Session, user_id: int
    ) -> Optional[LearningPreference]:
        """Fetch learning preference by user ID."""
        return (
            db.query(LearningPreference)
            .filter(LearningPreference.user_id == user_id)
            .first()
        )

    @staticmethod
    def replace_study_goals(
        db: Session,
        user_id: int,
        goals: List[str],
        target_score: Optional[str] = None,
        target_exam: Optional[str] = None,
    ) -> List[StudyGoal]:
        """Replace student study goals transactionally (Step 3)."""
        db.query(StudyGoal).filter(StudyGoal.user_id == user_id).delete(
            synchronize_session="fetch"
        )
        new_goals = [
            StudyGoal(
                user_id=user_id,
                goal_text=g,
                target_score=target_score,
                target_exam=target_exam,
            )
            for g in goals
        ]
        db.add_all(new_goals)
        db.commit()
        return (
            db.query(StudyGoal)
            .filter(StudyGoal.user_id == user_id)
            .order_by(StudyGoal.id)
            .all()
        )

    @staticmethod
    def get_study_goals(db: Session, user_id: int) -> List[StudyGoal]:
        """Fetch all study goals for a user."""
        return (
            db.query(StudyGoal)
            .filter(StudyGoal.user_id == user_id)
            .order_by(StudyGoal.id)
            .all()
        )

    # ── Step 4: Study Schedule ────────────────────────────────────────────────
    @staticmethod
    def upsert_study_schedule(
        db: Session,
        user_id: int,
        daily_target_hours: float,
        preferred_slot: str,
        available_days: List[str],
    ) -> StudySchedule:
        """Create or update student study schedule (Step 4)."""
        sched = (
            db.query(StudySchedule)
            .filter(StudySchedule.user_id == user_id)
            .first()
        )
        if sched:
            sched.daily_target_hours = daily_target_hours
            sched.preferred_slot = preferred_slot
            sched.available_days = available_days
        else:
            sched = StudySchedule(
                user_id=user_id,
                daily_target_hours=daily_target_hours,
                preferred_slot=preferred_slot,
                available_days=available_days,
            )
            db.add(sched)
        db.commit()
        db.refresh(sched)
        return sched

    @staticmethod
    def get_study_schedule(
        db: Session, user_id: int
    ) -> Optional[StudySchedule]:
        """Fetch study schedule by user ID."""
        return (
            db.query(StudySchedule)
            .filter(StudySchedule.user_id == user_id)
            .first()
        )
