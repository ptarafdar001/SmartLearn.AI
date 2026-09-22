"""
Domain business logic service for the SmartLearn.AI Learning Foundation.
"""

from datetime import datetime, timezone
import logging
from typing import List, Optional
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.learning import Chapter, Subject, Topic
from app.models.onboarding import SubjectSelection
from app.repositories.learning_repository import LearningRepository
from app.repositories.onboarding_repository import OnboardingRepository
from app.schemas.learning import (
    ChapterSummaryResponse,
    ContinueLearningItem,
    LearningResourceResponse,
    ProgressUpdateRequest,
    SubjectDetailResponse,
    SubjectSummaryResponse,
    TopicDetailResponse,
    TopicProgressResponse,
    TopicProgressSummary,
    TopicSummaryResponse,
)

logger = logging.getLogger("smartlearn.learning")


class LearningService:
    """Orchestrates learning workflows, curriculum traversal, and student progress telemetry."""

    @staticmethod
    def get_enrolled_subjects(db: Session, user_id: int) -> List[SubjectSummaryResponse]:
        """
        Retrieve curriculum subjects aligned with the student's board, grade, and onboarding selections,
        including live chapter counts and calculated topic progress.
        """
        profile = OnboardingRepository.get_student_profile(db, user_id)
        selections = OnboardingRepository.get_subject_selections(db, user_id)
        selected_names = {s.subject_name.strip().lower() for s in selections}

        if profile:
            candidate_subjects = LearningRepository.get_subjects_by_board_grade(
                db,
                board=profile.board,
                grade=profile.grade,
                academic_stream=profile.academic_stream,
            )
        else:
            candidate_subjects = LearningRepository.get_all_active_subjects(db)

        # Filter to subjects the student enrolled in during onboarding (or all matching if no filter)
        if selected_names:
            matched_subjects = []
            for sel in selected_names:
                # 1. Exact match against candidate subject name
                exact = next(
                    (s for s in candidate_subjects if s.name.strip().lower() == sel),
                    None,
                )
                if exact and exact not in matched_subjects:
                    matched_subjects.append(exact)
                    continue

                # 2. Normalized fallback only if no exact match found
                fallback = next(
                    (
                        s
                        for s in candidate_subjects
                        if sel in s.name.strip().lower() or s.name.strip().lower() in sel
                    ),
                    None,
                )
                if fallback and fallback not in matched_subjects:
                    matched_subjects.append(fallback)

            subjects = matched_subjects if matched_subjects else candidate_subjects
        else:
            subjects = candidate_subjects

        results: List[SubjectSummaryResponse] = []
        covered_names = set()

        for s in subjects:
            covered_names.add(s.name.strip().lower())
            chapters = LearningRepository.get_chapters_by_subject_id(db, s.id)
            all_topics: List[Topic] = []
            for ch in chapters:
                all_topics.extend(LearningRepository.get_topics_by_chapter_id(db, ch.id))

            topic_ids = [t.id for t in all_topics]
            progress_map = LearningRepository.get_user_progress_for_topics(db, user_id, topic_ids)

            total_chapters = len(chapters)
            total_topics = len(all_topics)
            completed_topics = sum(
                1 for t in all_topics if progress_map.get(t.id) and progress_map[t.id].status == "completed"
            )
            progress_sum = sum(
                progress_map[t.id].progress_percentage for t in all_topics if progress_map.get(t.id)
            )
            overall_pct = round(progress_sum / total_topics, 1) if (total_topics > 0 and progress_map) else None

            results.append(
                SubjectSummaryResponse(
                    id=s.id,
                    code=s.code,
                    name=s.name,
                    subject_name=s.name,
                    board=s.board,
                    grade=s.grade,
                    academic_stream=s.academic_stream,
                    category=s.category,
                    description=s.description,
                    total_chapters=total_chapters,
                    total_topics=total_topics,
                    chapter_count=total_chapters,
                    topic_count=total_topics,
                    completed_topics=completed_topics,
                    progress_percentage=overall_pct,
                    curriculum_status=s.curriculum_status or "in_preparation",
                    source_authority=s.source_authority,
                    source_url=s.source_url,
                    syllabus_version=s.syllabus_version,
                )
            )

        # For any enrolled selection that has not been seeded as a canonical Subject yet,
        # provide a graceful placeholder summary so existing onboarding workflows & tests work seamlessly
        for sel in selections:
            if sel.subject_name.strip().lower() not in covered_names:
                results.append(
                    SubjectSummaryResponse(
                        id=sel.id,
                        code=f"enrolled-{sel.id}",
                        name=sel.subject_name,
                        subject_name=sel.subject_name,
                        board=profile.board if profile else "CBSE",
                        grade=profile.grade if profile else "Class 11",
                        academic_stream=profile.academic_stream if profile else None,
                        category="core",
                        description=f"Enrolled subject: {sel.subject_name}",
                        total_chapters=0,
                        total_topics=0,
                        chapter_count=0,
                        topic_count=0,
                        completed_topics=0,
                        progress_percentage=None,
                        curriculum_status="in_preparation",
                        status_message=f"Enrollment recorded for {sel.subject_name}. Subject syllabus is being prepared.",
                    )
                )

        return results

    @staticmethod
    def get_subject_detail(db: Session, user_id: int, subject_id: int) -> SubjectDetailResponse:
        """Retrieve complete subject details with chapter accordions and student progress status."""
        subject = LearningRepository.get_subject_by_id(db, subject_id)
        if not subject:
            # Fallback in case subject_id was passed as an enrolled selection id
            sel = (
                db.query(SubjectSelection)
                .filter(SubjectSelection.id == subject_id, SubjectSelection.user_id == user_id)
                .first()
            )
            if sel:
                profile = OnboardingRepository.get_student_profile(db, user_id)
                if profile:
                    candidate_subjects = LearningRepository.get_subjects_by_board_grade(
                        db,
                        board=profile.board,
                        grade=profile.grade,
                        academic_stream=profile.academic_stream,
                    )
                    sel_clean = sel.subject_name.strip().lower()
                    for cand in candidate_subjects:
                        cand_clean = cand.name.strip().lower()
                        if cand_clean == sel_clean or cand_clean in sel_clean or sel_clean in cand_clean:
                            subject = cand
                            break

        if not subject:
            raise ValueError("Subject not found or inactive")

        chapters = LearningRepository.get_chapters_by_subject_id(db, subject.id)

        # If subject has no chapters yet, return an explicit, honest in-preparation response
        if not chapters:
            status_msg = (
                f"Curriculum framework registered for {subject.board} {subject.grade} {subject.name}. "
                f"Syllabus structures and learning modules are actively being curated from {subject.source_authority or 'authoritative educational'} sources."
            )
            return SubjectDetailResponse(
                id=subject.id,
                code=subject.code,
                name=subject.name,
                board=subject.board,
                grade=subject.grade,
                academic_stream=subject.academic_stream,
                category=subject.category,
                description=subject.description,
                total_chapters=0,
                total_topics=0,
                completed_topics=0,
                progress_percentage=0.0,
                curriculum_status=subject.curriculum_status or "in_preparation",
                source_authority=subject.source_authority,
                source_url=subject.source_url,
                syllabus_version=subject.syllabus_version,
                status_message=status_msg,
                chapters=[],
            )

        all_topics: List[Topic] = []
        for ch in chapters:
            all_topics.extend(LearningRepository.get_topics_by_chapter_id(db, ch.id))

        topic_ids = [t.id for t in all_topics]
        progress_map = LearningRepository.get_user_progress_for_topics(db, user_id, topic_ids)

        chapter_responses: List[ChapterSummaryResponse] = []
        for ch in chapters:
            ch_topics = [t for t in all_topics if t.chapter_id == ch.id]
            topic_summaries: List[TopicSummaryResponse] = []
            for t in ch_topics:
                prog = progress_map.get(t.id)
                prog_summary = None
                if prog:
                    prog_summary = TopicProgressSummary(
                        status=prog.status,
                        progress_percentage=prog.progress_percentage,
                        time_spent_seconds=prog.time_spent_seconds,
                        last_accessed_at=prog.last_accessed_at,
                        completed_at=prog.completed_at,
                    )
                topic_summaries.append(
                    TopicSummaryResponse(
                        id=t.id,
                        chapter_id=t.chapter_id,
                        topic_number=t.topic_number,
                        title=t.title,
                        description=t.description,
                        estimated_minutes=t.estimated_minutes,
                        progress=prog_summary,
                    )
                )

            total_ch_topics = len(ch_topics)
            completed_ch_topics = sum(
                1 for t in ch_topics if progress_map.get(t.id) and progress_map[t.id].status == "completed"
            )
            ch_progress_sum = sum(
                progress_map[t.id].progress_percentage for t in ch_topics if progress_map.get(t.id)
            )
            ch_pct = round(ch_progress_sum / total_ch_topics, 1) if total_ch_topics > 0 else 0.0

            chapter_responses.append(
                ChapterSummaryResponse(
                    id=ch.id,
                    subject_id=ch.subject_id,
                    chapter_number=ch.chapter_number,
                    title=ch.title,
                    description=ch.description,
                    total_topics=total_ch_topics,
                    completed_topics=completed_ch_topics,
                    progress_percentage=ch_pct,
                    topics=topic_summaries,
                )
            )

        total_subject_topics = len(all_topics)
        total_completed = sum(
            1 for t in all_topics if progress_map.get(t.id) and progress_map[t.id].status == "completed"
        )
        total_sum = sum(
            progress_map[t.id].progress_percentage for t in all_topics if progress_map.get(t.id)
        )
        overall_pct = round(total_sum / total_subject_topics, 1) if total_subject_topics > 0 else 0.0

        return SubjectDetailResponse(
            id=subject.id,
            code=subject.code,
            name=subject.name,
            board=subject.board,
            grade=subject.grade,
            academic_stream=subject.academic_stream,
            category=subject.category,
            description=subject.description,
            total_chapters=len(chapters),
            total_topics=total_subject_topics,
            completed_topics=total_completed,
            progress_percentage=overall_pct,
            curriculum_status=subject.curriculum_status or "curriculum_verified",
            source_authority=subject.source_authority,
            source_url=subject.source_url,
            syllabus_version=subject.syllabus_version,
            status_message=None,
            chapters=chapter_responses,
        )

    @staticmethod
    def get_chapter_detail(db: Session, user_id: int, chapter_id: int) -> ChapterSummaryResponse:
        """Retrieve chapter details and ordered topics with student progress."""
        chapter = LearningRepository.get_chapter_by_id(db, chapter_id)
        if not chapter:
            raise ValueError("Chapter not found")

        topics = LearningRepository.get_topics_by_chapter_id(db, chapter.id)
        topic_ids = [t.id for t in topics]
        progress_map = LearningRepository.get_user_progress_for_topics(db, user_id, topic_ids)

        topic_summaries: List[TopicSummaryResponse] = []
        for t in topics:
            prog = progress_map.get(t.id)
            prog_summary = None
            if prog:
                prog_summary = TopicProgressSummary(
                    status=prog.status,
                    progress_percentage=prog.progress_percentage,
                    time_spent_seconds=prog.time_spent_seconds,
                    last_accessed_at=prog.last_accessed_at,
                    completed_at=prog.completed_at,
                )
            topic_summaries.append(
                TopicSummaryResponse(
                    id=t.id,
                    chapter_id=t.chapter_id,
                    topic_number=t.topic_number,
                    title=t.title,
                    description=t.description,
                    estimated_minutes=t.estimated_minutes,
                    progress=prog_summary,
                )
            )

        total_topics = len(topics)
        completed_topics = sum(
            1 for t in topics if progress_map.get(t.id) and progress_map[t.id].status == "completed"
        )
        progress_sum = sum(
            progress_map[t.id].progress_percentage for t in topics if progress_map.get(t.id)
        )
        pct = round(progress_sum / total_topics, 1) if total_topics > 0 else 0.0

        return ChapterSummaryResponse(
            id=chapter.id,
            subject_id=chapter.subject_id,
            chapter_number=chapter.chapter_number,
            title=chapter.title,
            description=chapter.description,
            total_topics=total_topics,
            completed_topics=completed_topics,
            progress_percentage=pct,
            topics=topic_summaries,
        )

    @staticmethod
    def get_topic_detail(db: Session, user_id: int, topic_id: int) -> TopicDetailResponse:
        """Retrieve topic content, parent syllabus breadcrumb info, and all multi-modal resources."""
        topic = LearningRepository.get_topic_by_id(db, topic_id)
        if not topic:
            raise ValueError("Topic not found")

        chapter = LearningRepository.get_chapter_by_id(db, topic.chapter_id)
        subject = LearningRepository.get_subject_by_id(db, chapter.subject_id) if chapter else None

        resources = LearningRepository.get_resources_by_topic_id(db, topic.id, only_active=True)
        resource_responses = [
            LearningResourceResponse(
                id=r.id,
                topic_id=r.topic_id,
                title=r.title,
                resource_type=r.resource_type,
                provider=r.provider,
                source_name=r.source_name,
                source_url=r.source_url,
                external_id=r.external_id,
                content_url=r.content_url,
                text_content=r.text_content,
                duration_seconds=r.duration_seconds,
                language=r.language,
                order_index=r.order_index,
                is_active=r.is_active,
                is_verified=r.is_verified,
                verified_at=r.verified_at,
            )
            for r in resources
        ]

        prog = LearningRepository.get_student_progress(db, user_id, topic.id)
        prog_summary = None
        if prog:
            prog_summary = TopicProgressSummary(
                status=prog.status,
                progress_percentage=prog.progress_percentage,
                time_spent_seconds=prog.time_spent_seconds,
                last_accessed_at=prog.last_accessed_at,
                completed_at=prog.completed_at,
            )

        return TopicDetailResponse(
            id=topic.id,
            chapter_id=topic.chapter_id,
            chapter_title=chapter.title if chapter else "Chapter",
            chapter_number=chapter.chapter_number if chapter else 1,
            subject_id=subject.id if subject else 0,
            subject_name=subject.name if subject else "Subject",
            topic_number=topic.topic_number,
            title=topic.title,
            description=topic.description,
            estimated_minutes=topic.estimated_minutes,
            progress=prog_summary,
            user_progress=prog_summary,
            resources=resource_responses,
        )

    @staticmethod
    def update_topic_progress(
        db: Session, user_id: int, topic_id: int, data: ProgressUpdateRequest
    ) -> TopicProgressResponse:
        """
        Record or advance student progress for a topic.
        Enforces user ownership, bounds checking, and server-controlled completion timestamp.
        """
        topic = LearningRepository.get_topic_by_id(db, topic_id)
        if not topic:
            raise ValueError("Topic not found")

        # Auto-promote status if progress is 100%
        status = data.status
        if data.progress_percentage >= 100.0:
            status = "completed"

        completed_at = datetime.now(timezone.utc) if status == "completed" else None

        record = LearningRepository.upsert_student_progress(
            db=db,
            user_id=user_id,
            topic_id=topic.id,
            status=status,
            progress_percentage=data.progress_percentage,
            time_spent_seconds=data.time_spent_seconds,
            completed_at=completed_at,
        )

        return TopicProgressResponse(
            id=record.id,
            user_id=record.user_id,
            topic_id=record.topic_id,
            status=record.status,
            progress_percentage=record.progress_percentage,
            time_spent_seconds=record.time_spent_seconds,
            last_accessed_at=record.last_accessed_at,
            completed_at=record.completed_at,
        )

    @staticmethod
    def get_continue_learning(db: Session, user_id: int) -> Optional[ContinueLearningItem]:
        """
        Find the student's most recently accessed topic to power the dashboard 'Continue Learning' card.
        """
        recent_records = LearningRepository.get_recent_progress_for_user(db, user_id, limit=1)
        if not recent_records:
            return None

        recent = recent_records[0]
        topic = LearningRepository.get_topic_by_id(db, recent.topic_id)
        if not topic:
            return None

        chapter = LearningRepository.get_chapter_by_id(db, topic.chapter_id)
        subject = LearningRepository.get_subject_by_id(db, chapter.subject_id) if chapter else None

        return ContinueLearningItem(
            topic_id=topic.id,
            topic_title=topic.title,
            topic_number=topic.topic_number,
            chapter_id=chapter.id if chapter else 0,
            chapter_title=chapter.title if chapter else "Chapter",
            chapter_number=chapter.chapter_number if chapter else 1,
            subject_id=subject.id if subject else 0,
            subject_name=subject.name if subject else "Subject",
            status=recent.status,
            progress_percentage=recent.progress_percentage,
            time_spent_seconds=recent.time_spent_seconds,
            last_accessed_at=recent.last_accessed_at,
        )
