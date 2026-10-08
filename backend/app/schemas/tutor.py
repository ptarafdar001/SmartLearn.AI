"""
Pydantic schemas for the SmartLearn.AI Curriculum-Aware AI Tutor Service.
"""

from typing import List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field


class TutorChatMessage(BaseModel):
    """A single turn in the AI Tutor conversation."""
    role: Literal["student", "tutor", "user", "model"]
    content: str = Field(..., max_length=10000)

    model_config = ConfigDict(from_attributes=True)


class TutorChatRequest(BaseModel):
    """Request payload for interacting with the AI Tutor."""
    topic_id: int = Field(..., description="ID of the curriculum topic currently being studied")
    message: str = Field(..., min_length=1, max_length=3000, description="Student's doubt or question")
    conversation_history: List[TutorChatMessage] = Field(
        default=[], max_length=20, description="Recent conversation turns in the current session"
    )
    image_base64: Optional[str] = Field(
        default=None,
        description="Optional base64 image string (data URI or raw base64) for visual doubt solving",
    )


class GroundedSourceItem(BaseModel):
    """Verified curriculum source citation."""
    title: str
    source_name: Optional[str] = None
    source_url: Optional[str] = None
    is_verified: bool = True
    resource_type: Optional[str] = None


class TutorChatResponse(BaseModel):
    """Response returned by the AI Tutor service."""
    reply: str
    topic_id: int
    topic_title: str
    subject_name: str
    board: str
    grade: str
    grounded_resource_titles: List[str] = []
    grounded_sources: List[GroundedSourceItem] = []
    learning_objectives: List[str] = []
    is_out_of_scope: bool = False
    scope_redirection_guidance: Optional[str] = None
    diagram_code: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class VoiceSessionRequest(BaseModel):
    """Payload to initiate a real-time conversational voice session."""
    topic_id: int = Field(..., description="Topic ID for curriculum grounding")


class VoiceSessionResponse(BaseModel):
    """Ephemeral session token and WebSocket connection details."""
    session_id: str
    session_token: str
    ws_endpoint: str
    topic_id: int
    topic_title: str
    subject_name: str
    board: str
    grade: str
    expires_in_seconds: int

    model_config = ConfigDict(from_attributes=True)

