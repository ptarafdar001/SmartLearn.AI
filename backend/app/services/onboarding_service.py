from typing import Any, Dict, List
from sqlalchemy.orm import Session

from app.repositories.onboarding_repository import OnboardingRepository
from app.repositories.user_repository import UserRepository
from app.schemas.onboarding import (
    LearningPreferenceResponse,
    OnboardingStatusResponse,
    Step1BoardClass,
    Step2StreamSubjects,
    Step3PreferencesGoals,
    Step4Schedule,
    StudentProfileResponse,
    StudyGoalResponse,
    StudyScheduleResponse,
    SubjectSelectionResponse,
)


class OnboardingService:
    """Business logic service managing the 4-step student onboarding workflow."""

    @staticmethod
    def save_step1_board_class(
        db: Session, user_id: int, data: Step1BoardClass
    ) -> StudentProfileResponse:
        """Step 1: Save or update student board, grade, and academic stream."""
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            raise ValueError("User not found")

        profile = OnboardingRepository.upsert_student_profile(
            db=db,
            user_id=user_id,
            board=data.board,
            grade=data.grade,
            academic_stream=data.academic_stream,
        )
        return StudentProfileResponse.model_validate(profile)

    @staticmethod
    def save_step2_stream_subjects(
        db: Session, user_id: int, data: Step2StreamSubjects
    ) -> List[SubjectSelectionResponse]:
        """Step 2: Save or replace enrolled subjects and optionally update stream."""
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            raise ValueError("User not found")

        # Update stream on student profile if provided
        if data.academic_stream:
            profile = OnboardingRepository.get_student_profile(db, user_id)
            if profile:
                OnboardingRepository.upsert_student_profile(
                    db=db,
                    user_id=user_id,
                    board=profile.board,
                    grade=profile.grade,
                    academic_stream=data.academic_stream,
                )

        subjects = OnboardingRepository.replace_subject_selections(
            db=db, user_id=user_id, subjects=data.subjects
        )
        return [SubjectSelectionResponse.model_validate(s) for s in subjects]

    @staticmethod
    def save_step3_preferences_goals(
        db: Session, user_id: int, data: Step3PreferencesGoals
    ) -> Dict[str, Any]:
        """Step 3: Save learning style preference and study goals."""
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            raise ValueError("User not found")

        pref = OnboardingRepository.upsert_learning_preference(
            db=db, user_id=user_id, preferred_style=data.preferred_style
        )
        goals = OnboardingRepository.replace_study_goals(
            db=db,
            user_id=user_id,
            goals=data.goals,
            target_score=data.target_score,
            target_exam=data.target_exam,
        )
        return {
            "learning_preference": LearningPreferenceResponse.model_validate(pref),
            "study_goals": [StudyGoalResponse.model_validate(g) for g in goals],
        }

    @staticmethod
    def save_step4_schedule(
        db: Session, user_id: int, data: Step4Schedule
    ) -> StudyScheduleResponse:
        """
        Step 4: Save study schedule and finalize onboarding.
        Marks users.is_onboarded = True upon successful Step 4 completion.
        """
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            raise ValueError("User not found")

        schedule = OnboardingRepository.upsert_study_schedule(
            db=db,
            user_id=user_id,
            daily_target_hours=data.daily_target_hours,
            preferred_slot=data.preferred_slot,
            available_days=data.available_days,
        )

        # Mark user as fully onboarded only after Step 4 completes
        UserRepository.update_onboarding_status(db, user_id=user_id, is_onboarded=True)

        return StudyScheduleResponse.model_validate(schedule)

    @staticmethod
    def get_onboarding_status(db: Session, user_id: int) -> OnboardingStatusResponse:
        """Determine step-by-step onboarding progress for the authenticated user."""
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            raise ValueError("User not found")

        profile = OnboardingRepository.get_student_profile(db, user_id)
        subjects = OnboardingRepository.get_subject_selections(db, user_id)
        preference = OnboardingRepository.get_learning_preference(db, user_id)
        schedule = OnboardingRepository.get_study_schedule(db, user_id)

        step1_done = profile is not None
        step2_done = len(subjects) > 0
        step3_done = preference is not None
        step4_done = schedule is not None

        if not step1_done:
            current = 1
        elif not step2_done:
            current = 2
        elif not step3_done:
            current = 3
        elif not step4_done:
            current = 4
        else:
            current = 5  # All completed

        return OnboardingStatusResponse(
            is_onboarded=user.is_onboarded and step4_done,
            step1_completed=step1_done,
            step2_completed=step2_done,
            step3_completed=step3_done,
            step4_completed=step4_done,
            current_step=current,
        )
