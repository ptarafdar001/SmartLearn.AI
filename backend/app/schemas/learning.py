"""
Pydantic schemas for the SmartLearn.AI Learning Service.
"""

from datetime import datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field


class TopicProgressSummary(BaseModel):
    """Summary of student progress on a topic."""
    status: str
    progress_percentage: float
    time_spent_seconds: int
    last_accessed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class LearningResourceResponse(BaseModel):
    """Multi-modal learning resource contract with provenance metadata."""
    id: int
    topic_id: int
    title: str
    resource_type: str
    provider: str
    source_name: Optional[str] = None
    source_url: Optional[str] = None
    external_id: Optional[str] = None
    content_url: Optional[str] = None
    text_content: Optional[str] = None
    duration_seconds: Optional[int] = None
    language: str
    order_index: int
    is_active: bool
    is_verified: bool
    verified_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class TopicSummaryResponse(BaseModel):
    """Concise topic information for chapter syllabus lists."""
    id: int
    chapter_id: int
    topic_number: int
    title: str
    description: Optional[str] = None
    estimated_minutes: int
    progress: Optional[TopicProgressSummary] = None

    model_config = ConfigDict(from_attributes=True)


class ChapterSummaryResponse(BaseModel):
    """Chapter information with its ordered topics and aggregate progress."""
    id: int
    subject_id: int
    chapter_number: int
    title: str
    description: Optional[str] = None
    total_topics: int
    completed_topics: int
    progress_percentage: float
    topics: List[TopicSummaryResponse] = []

    model_config = ConfigDict(from_attributes=True)


class SubjectSummaryResponse(BaseModel):
    """High-level subject card for the student dashboard."""
    id: int
    code: str
    name: str
    subject_name: str  # Backward-compatible alias matching name
    board: str
    grade: str
    academic_stream: Optional[str] = None
    category: str
    description: Optional[str] = None
    total_chapters: int
    total_topics: int
    chapter_count: Optional[int] = None
    topic_count: Optional[int] = None
    completed_topics: int
    progress_percentage: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class SubjectDetailResponse(BaseModel):
    """Detailed subject view with full chapter and topic syllabus hierarchy."""
    id: int
    code: str
    name: str
    board: str
    grade: str
    academic_stream: Optional[str] = None
    category: str
    description: Optional[str] = None
    total_chapters: int
    total_topics: int
    completed_topics: int
    progress_percentage: float
    chapters: List[ChapterSummaryResponse] = []

    model_config = ConfigDict(from_attributes=True)


class TopicDetailResponse(BaseModel):
    """Comprehensive topic page payload including resources and student progress."""
    id: int
    chapter_id: int
    chapter_title: str
    chapter_number: int
    subject_id: int
    subject_name: str
    topic_number: int
    title: str
    description: Optional[str] = None
    estimated_minutes: int
    progress: Optional[TopicProgressSummary] = None
    user_progress: Optional[TopicProgressSummary] = None
    resources: List[LearningResourceResponse] = []

    model_config = ConfigDict(from_attributes=True)


class ProgressUpdateRequest(BaseModel):
    """Validation schema for recording student topic progress."""
    status: Literal["not_started", "in_progress", "completed"]
    progress_percentage: float = Field(..., ge=0.0, le=100.0, description="Completion percentage between 0 and 100")
    time_spent_seconds: int = Field(0, ge=0, description="Non-negative time duration spent studying")


class TopicProgressResponse(BaseModel):
    """Response returned after progress persistence."""
    id: int
    user_id: int
    topic_id: int
    status: str
    progress_percentage: float
    time_spent_seconds: int
    last_accessed_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ContinueLearningItem(BaseModel):
    """Dashboard widget item indicating the most recently engaged topic."""
    topic_id: int
    topic_title: str
    topic_number: int
    chapter_id: int
    chapter_title: str
    chapter_number: int
    subject_id: int
    subject_name: str
    status: str
    progress_percentage: float
    time_spent_seconds: int
    last_accessed_at: datetime
