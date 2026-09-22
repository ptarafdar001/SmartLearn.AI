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
    ProgressUpdateRequest,
    SubjectDetailResponse,
    SubjectSummaryResponse,
    TopicDetailResponse,
    TopicProgressResponse,
)
from app.services.dashboard_service import DashboardService
from app.services.learning_service import LearningService

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
