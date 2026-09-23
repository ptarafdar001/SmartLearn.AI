"""
API endpoints for Learning curriculum traversal, multi-modal resources, and progress tracking.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user
from app.db.session import get_db
from app.models.users import User
from app.schemas.dashboard import RecommendationsResponse
from app.schemas.learning import (
    ChapterSummaryResponse,
    ContinueLearningItem,
    LearningObjectiveResponse,
    PracticeQuestionAttemptRequest,
    PracticeQuestionAttemptResponse,
    PracticeQuestionResponse,
    PreviousYearQuestionResponse,
    ProgressUpdateRequest,
    SubjectDetailResponse,
    SubjectSummaryResponse,
    TopicDetailResponse,
    TopicNotesGenerateRequest,
    TopicProgressResponse,
    TopicStudyNotesResponse,
)
from app.services.dashboard_service import DashboardService
from app.services.learning_service import LearningService
from app.services.notes_service import NotesService
from app.services.practice_service import PracticeService

router = APIRouter(prefix="/learning", tags=["Learning"])


@router.get(
    "/subjects",
    response_model=List[SubjectSummaryResponse],
    summary="Get authenticated student's enrolled subjects",
)
def get_user_subjects(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> List[SubjectSummaryResponse]:
    """Retrieve subjects chosen by the student with calculated chapters, topics, and progress."""
    try:
        return LearningService.get_enrolled_subjects(db=db, user_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/subjects/{subject_id}",
    response_model=SubjectDetailResponse,
    summary="Get subject syllabus with chapters and topics",
)
def get_subject_detail(
    subject_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> SubjectDetailResponse:
    """Retrieve complete subject details, chapters, and progress for the authenticated student."""
    try:
        return LearningService.get_subject_detail(
            db=db, user_id=current_user.id, subject_id=subject_id
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/chapters/{chapter_id}",
    response_model=ChapterSummaryResponse,
    summary="Get chapter topics and completion status",
)
def get_chapter_detail(
    chapter_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> ChapterSummaryResponse:
    """Retrieve chapter details and ordered topics with progress."""
    try:
        return LearningService.get_chapter_detail(
            db=db, user_id=current_user.id, chapter_id=chapter_id
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/topics/{topic_id}",
    response_model=TopicDetailResponse,
    summary="Get topic details, breadcrumbs, and multi-modal resources",
)
def get_topic_detail(
    topic_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> TopicDetailResponse:
    """Retrieve topic lessons, syllabus hierarchy, and all multi-modal learning resources."""
    try:
        return LearningService.get_topic_detail(
            db=db, user_id=current_user.id, topic_id=topic_id
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/topics/{topic_id}/progress",
    response_model=TopicProgressResponse,
    summary="Record student progress on a topic",
)
def update_topic_progress(
    topic_id: int,
    data: ProgressUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> TopicProgressResponse:
    """
    Record or update student learning progress.
    User identity is securely derived from JWT authentication.
    """
    try:
        return LearningService.update_topic_progress(
            db=db, user_id=current_user.id, topic_id=topic_id, data=data
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/continue",
    response_model=Optional[ContinueLearningItem],
    summary="Get student's most recently accessed topic",
)
def get_continue_learning(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Optional[ContinueLearningItem]:
    """Retrieve the most recently active topic for the dashboard 'Continue Learning' banner."""
    try:
        return LearningService.get_continue_learning(db=db, user_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/recommendations",
    response_model=RecommendationsResponse,
    summary="Get tailored study recommendations",
)
def get_recommendations(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> RecommendationsResponse:
    """Retrieve rule-based recommendations tailored to the student's enrolled subjects and goals."""
    try:
        return DashboardService.get_recommendations(db=db, user_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ── Learning Objectives ───────────────────────────────────────────────────────
@router.get(
    "/topics/{topic_id}/objectives",
    response_model=List[LearningObjectiveResponse],
    summary="Get verified syllabus learning objectives for a topic",
)
def get_topic_objectives(
    topic_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> List[LearningObjectiveResponse]:
    """Retrieve verified Bloom's taxonomy objectives for curriculum alignment."""
    from app.repositories.learning_repository import LearningRepository
    objectives = LearningRepository.get_learning_objectives(db, topic_id=topic_id)
    return [LearningObjectiveResponse.model_validate(o) for o in objectives]


# ── Dynamic Study Notes ───────────────────────────────────────────────────────
@router.get(
    "/topics/{topic_id}/notes",
    response_model=TopicStudyNotesResponse,
    summary="Get 10-part pedagogical study notes for a topic",
)
def get_topic_notes(
    topic_id: int,
    type: str = "comprehensive",
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> TopicStudyNotesResponse:
    """Fetch cached verified study notes or synthesize them on demand."""
    try:
        return NotesService.get_or_generate_notes(
            db=db,
            user_id=current_user.id,
            topic_id=topic_id,
            notes_type=type,
            force_regenerate=False,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/topics/{topic_id}/notes/generate",
    response_model=TopicStudyNotesResponse,
    summary="Force regenerate 10-part study notes for a topic",
)
def regenerate_topic_notes(
    topic_id: int,
    req: TopicNotesGenerateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> TopicStudyNotesResponse:
    """Generate fresh study notes grounded in topic verified learning resources."""
    try:
        return NotesService.get_or_generate_notes(
            db=db,
            user_id=current_user.id,
            topic_id=topic_id,
            notes_type=req.notes_type,
            force_regenerate=True,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ── Authentic Previous-Year Questions (PYQs) ──────────────────────────────────
@router.get(
    "/topics/{topic_id}/pyqs",
    response_model=List[PreviousYearQuestionResponse],
    summary="Get authentic previous-year examination questions for a topic",
)
def get_topic_pyqs(
    topic_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> List[PreviousYearQuestionResponse]:
    """Retrieve official past-year board questions strictly segregated from AI practice."""
    return PracticeService.get_authentic_pyqs(db=db, topic_id=topic_id)


@router.get(
    "/subjects/{subject_id}/pyqs",
    response_model=List[PreviousYearQuestionResponse],
    summary="Get authentic previous-year examination questions for a subject",
)
def get_subject_pyqs(
    subject_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> List[PreviousYearQuestionResponse]:
    """Retrieve all authentic past-year questions for the subject."""
    return PracticeService.get_subject_pyqs(db=db, subject_id=subject_id)


# ── AI-Generated Practice Questions & Attempt Evaluation ──────────────────────
@router.get(
    "/topics/{topic_id}/practice-questions",
    response_model=List[PracticeQuestionResponse],
    summary="Get syllabus-aligned AI practice questions for a topic",
)
def get_practice_questions(
    topic_id: int,
    difficulty: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> List[PracticeQuestionResponse]:
    """Retrieve practice questions explicitly tagged as AI-generated practice."""
    return PracticeService.get_or_generate_practice_questions(
        db=db,
        user_id=current_user.id,
        topic_id=topic_id,
        difficulty=difficulty,
        force_generate=False,
    )


@router.post(
    "/topics/{topic_id}/practice-questions/generate",
    response_model=List[PracticeQuestionResponse],
    summary="Generate fresh AI practice questions grounded in verified syllabus",
)
def generate_practice_questions(
    topic_id: int,
    difficulty: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> List[PracticeQuestionResponse]:
    """Generate new curriculum-grounded practice questions."""
    return PracticeService.get_or_generate_practice_questions(
        db=db,
        user_id=current_user.id,
        topic_id=topic_id,
        difficulty=difficulty,
        force_generate=True,
    )


@router.post(
    "/practice-questions/{question_id}/attempt",
    response_model=PracticeQuestionAttemptResponse,
    summary="Submit student attempt for instant grading and pedagogical feedback",
)
def submit_practice_attempt(
    question_id: int,
    attempt_req: PracticeQuestionAttemptRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> PracticeQuestionAttemptResponse:
    """Grade student answer against official answer key and record attempt history."""
    try:
        return PracticeService.evaluate_and_record_attempt(
            db=db,
            user_id=current_user.id,
            question_id=question_id,
            attempt_req=attempt_req,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/practice-questions/my-attempts",
    summary="Get recent question attempts for the authenticated student",
)
def get_my_attempts(
    limit: int = 50,
    topic_id: Optional[int] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Retrieve history of student attempts with marks and feedback."""
    from app.repositories.learning_repository import LearningRepository
    attempts = LearningRepository.get_user_question_attempts(
        db, user_id=current_user.id, limit=limit, topic_id=topic_id
    )
    return [
        {
            "id": a.id,
            "question_type": a.question_type,
            "pyq_id": a.pyq_id,
            "practice_question_id": a.practice_question_id,
            "user_answer": a.user_answer,
            "is_correct": a.is_correct,
            "marks_obtained": a.marks_obtained,
            "feedback": a.feedback,
            "attempted_at": a.attempted_at.isoformat() if a.attempted_at else None,
        }
        for a in attempts
    ]

