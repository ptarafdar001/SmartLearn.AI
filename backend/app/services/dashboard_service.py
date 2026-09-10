from typing import List
from sqlalchemy.orm import Session

from app.repositories.onboarding_repository import OnboardingRepository
from app.repositories.user_repository import UserRepository
from app.schemas.dashboard import (
    DashboardOverviewResponse,
    EnrolledSubjectSummary,
    RecommendationItem,
    RecommendationsResponse,
    StudyTargetSummary,
)


class DashboardService:
    """
    Business logic service for student dashboard overview, enrolled subjects, and recommendations.
    All data is strictly derived from verified PostgreSQL entities.
    Metrics that require future modules (study sessions, quiz attempts) are set to None.
    """

    @staticmethod
    def get_dashboard_overview(db: Session, user_id: int) -> DashboardOverviewResponse:
        """
        Assemble dashboard overview metrics strictly from persisted student records.
        """
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            raise ValueError("User not found")

        profile = OnboardingRepository.get_student_profile(db, user_id)
        subjects = OnboardingRepository.get_subject_selections(db, user_id)
        pref = OnboardingRepository.get_learning_preference(db, user_id)
        goals = OnboardingRepository.get_study_goals(db, user_id)
        schedule = OnboardingRepository.get_study_schedule(db, user_id)

        study_target = None
        if schedule:
            study_target = StudyTargetSummary(
                daily_target_hours=schedule.daily_target_hours,
                preferred_slot=schedule.preferred_slot,
                available_days=schedule.available_days,
            )

        subject_names = [s.subject_name for s in subjects]
        goal_texts = [g.goal_text for g in goals]

        return DashboardOverviewResponse(
            user_id=user.id,
            full_name=user.full_name,
            board=profile.board if profile else None,
            grade=profile.grade if profile else None,
            academic_stream=profile.academic_stream if profile else None,
            preferred_learning_style=pref.preferred_style if pref else None,
            study_target=study_target,
            goals=goal_texts,
            enrolled_subjects=subject_names,
            total_enrolled_subjects=len(subject_names),
            # Explicitly None until activity and assessment tracking tables are implemented
            study_streak_days=None,
            questions_solved=None,
            overall_progress_percentage=None,
        )

    @staticmethod
    def get_enrolled_subjects(
        db: Session, user_id: int
    ) -> List[EnrolledSubjectSummary]:
        """Return the authentic enrolled subjects for the authenticated user."""
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            raise ValueError("User not found")

        records = OnboardingRepository.get_subject_selections(db, user_id)
        return [
            EnrolledSubjectSummary(
                id=s.id,
                subject_name=s.subject_name,
                progress_percentage=None,
            )
            for s in records
        ]

    @staticmethod
    def get_recommendations(db: Session, user_id: int) -> RecommendationsResponse:
        """
        Generate deterministic study recommendations directly based on the user's
        enrolled subjects, grade, board, and learning preference.
        """
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            raise ValueError("User not found")

        profile = OnboardingRepository.get_student_profile(db, user_id)
        subjects = OnboardingRepository.get_subject_selections(db, user_id)
        pref = OnboardingRepository.get_learning_preference(db, user_id)
        goals = OnboardingRepository.get_study_goals(db, user_id)

        recommendations: List[RecommendationItem] = []

        style = pref.preferred_style if pref else "Interactive"
        board = profile.board if profile else "Curriculum"
        grade = profile.grade if profile else "Current Level"

        # Generate subject starter recommendations
        for s in subjects:
            rec_id = f"rec-subj-{s.id}"
            title = f"{s.subject_name}: Foundation & Concept Mapping"
            description = (
                f"Begin your {grade} ({board}) studies in {s.subject_name} using "
                f"{style.lower()} study techniques."
            )
            recommendations.append(
                RecommendationItem(
                    id=rec_id,
                    title=title,
                    description=description,
                    subject=s.subject_name,
                    learning_style=pref.preferred_style if pref else None,
                    recommendation_type="starter_guide",
                )
            )

        # Generate goal-oriented recommendations
        for g in goals:
            rec_id = f"rec-goal-{g.id}"
            exam_info = f" for {g.target_exam}" if g.target_exam else ""
            title = f"Goal Plan: {g.goal_text}"
            description = f"Structure your study sessions towards target: {g.goal_text}{exam_info}."
            recommendations.append(
                RecommendationItem(
                    id=rec_id,
                    title=title,
                    description=description,
                    subject="General Preparation",
                    learning_style=pref.preferred_style if pref else None,
                    recommendation_type="goal_milestone",
                )
            )

        return RecommendationsResponse(
            user_id=user.id,
            recommendations=recommendations,
            total_count=len(recommendations),
        )
