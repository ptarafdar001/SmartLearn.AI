"""
API endpoints for the Curriculum-Aware AI Tutor.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user
from app.db.session import get_db
from app.models.users import User
from app.schemas.tutor import TutorChatRequest, TutorChatResponse
from app.services.tutor_service import TutorService

router = APIRouter(prefix="/tutor", tags=["AI Tutor"])


@router.post(
    "/chat",
    response_model=TutorChatResponse,
    summary="Chat with Curriculum-Aware AI Tutor",
)
def chat_with_tutor(
    data: TutorChatRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> TutorChatResponse:
    """
    Interact with the curriculum-aware AI tutor.
    Grounded in student profile, board, grade, chapter, topic, and verified learning resources.
    Supports multimodal visual doubt solving via optional base64 image.
    """
    try:
        return TutorService.generate_tutor_reply(
            db=db, user_id=current_user.id, request=data
        )
    except ValueError as e:
        msg = str(e)
        if "not found" in msg.lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)
