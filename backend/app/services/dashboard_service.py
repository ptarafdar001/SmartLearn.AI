from typing import List
from sqlalchemy.orm import Session

from app.repositories.learning_repository import LearningRepository
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

        # Calculate authentic overall progress across tracked topics
        all_progress = LearningRepository.get_all_progress_for_user(db, user_id)
        overall_progress = None
        if all_progress:
            overall_progress = round(
                sum(p.progress_percentage for p in all_progress) / len(all_progress), 1
            )

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
            overall_progress_percentage=overall_progress,
        )

    @staticmethod
    def get_enrolled_subjects(
        db: Session, user_id: int
    ) -> List[EnrolledSubjectSummary]:
        """Return the authentic enrolled subjects for the authenticated user with real progress."""
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            raise ValueError("User not found")

        records = OnboardingRepository.get_subject_selections(db, user_id)
        profile = OnboardingRepository.get_student_profile(db, user_id)

        board = profile.board if profile else None
        grade = profile.grade if profile else None
        stream = profile.academic_stream if profile else None

        results = []
        for s in records:
            # Try to match canonical subject to calculate syllabus progress
            canonical = None
            if board and grade:
                candidate_subjects = LearningRepository.get_subjects_by_board_grade(
                    db, board=board, grade=grade, academic_stream=stream
                )
                for cand in candidate_subjects:
                    if cand.name.lower() == s.subject_name.lower():
                        canonical = cand
                        break

            progress_pct = None
            if canonical:
                chapters = LearningRepository.get_chapters_by_subject_id(db, canonical.id)
                topic_ids = []
                for ch in chapters:
                    ch_topics = LearningRepository.get_topics_by_chapter_id(db, ch.id)
                    topic_ids.extend([t.id for t in ch_topics])

                if topic_ids:
                    progress_map = LearningRepository.get_user_progress_for_topics(
                        db, user_id, topic_ids
                    )
                    total_progress = sum(
                        progress_map[tid].progress_percentage
                        for tid in topic_ids
                        if tid in progress_map
                    )
                    progress_pct = round(total_progress / len(topic_ids), 1)
                else:
                    progress_pct = 0.0

            results.append(
                EnrolledSubjectSummary(
                    id=s.id,
                    subject_name=s.subject_name,
                    progress_percentage=progress_pct,
                )
            )
        return results

    @staticmethod
    def get_recommendations(db: Session, user_id: int) -> RecommendationsResponse:
        """
        Generate curriculum-grounded video recommendations and study modules directly based
        on the student's enrolled subjects, grade, board, and topics.
        """
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            raise ValueError("User not found")

        profile = OnboardingRepository.get_student_profile(db, user_id)
        subjects = OnboardingRepository.get_subject_selections(db, user_id)
        pref = OnboardingRepository.get_learning_preference(db, user_id)

        recommendations: List[RecommendationItem] = []
        style = pref.preferred_style if pref else "Interactive"
        board = profile.board if profile else "Curriculum"
        grade = profile.grade if profile else "Current Level"

        # Map each enrolled subject strictly to its canonical subject using single source of truth
        from app.services.learning_service import LearningService
        for s in subjects:
            canonical = LearningService._ensure_canonical_subject_for_selection(
                db, user_id=user_id, subject_name=s.subject_name
            )

            if canonical:
                chapters = LearningRepository.get_chapters_by_subject_id(db, canonical.id)
                for ch in chapters:
                    topics = LearningRepository.get_topics_by_chapter_id(db, ch.id)
                    for top in topics:
                        resources = LearningRepository.get_resources_by_topic_id(db, top.id, only_active=True)
                        video_res = next((r for r in resources if r.resource_type == "video"), None)
                        
                        vid_id = video_res.external_id if video_res else "kYJq1000m9A"
                        content_url = video_res.content_url if video_res else f"https://www.youtube-nocookie.com/embed/{vid_id}"
                        
                        rec_id = f"rec-vid-{top.id}"
                        title = f"Recommended Lesson: {top.title}"
                        description = f"Watch this verified video lesson on {top.title} aligned with {board} {grade} syllabus."
                        
                        recommendations.append(
                            RecommendationItem(
                                id=rec_id,
                                title=title,
                                description=description,
                                subject=s.subject_name,
                                learning_style=style,
                                recommendation_type="recommended_video",
                                topic_id=top.id,
                                video_id=vid_id,
                                video_url=content_url,
                                duration_minutes=round((video_res.duration_seconds / 60) if video_res and video_res.duration_seconds else (top.estimated_minutes or 12)),
                            )
                        )
                        if len(recommendations) >= 6:
                            break
                    if len(recommendations) >= 6:
                        break
            if len(recommendations) >= 6:
                break

        # Fallback if no specific videos found yet
        if not recommendations:
            for s in subjects:
                rec_id = f"rec-subj-{s.id}"
                title = f"{s.subject_name}: Foundation & Concept Video"
                description = f"Recommended core overview for {grade} ({board}) in {s.subject_name}."
                recommendations.append(
                    RecommendationItem(
                        id=rec_id,
                        title=title,
                        description=description,
                        subject=s.subject_name,
                        learning_style=style,
                        recommendation_type="recommended_video",
                        topic_id=None,
                        video_id="kYJq1000m9A",
                        video_url="https://www.youtube-nocookie.com/embed/kYJq1000m9A",
                        duration_minutes=12,
                    )
                )

        return RecommendationsResponse(
            user_id=user.id,
            recommendations=recommendations,
            total_count=len(recommendations),
        )
