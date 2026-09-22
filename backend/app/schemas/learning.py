"""
Pydantic schemas for the SmartLearn.AI Learning Service.
"""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
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
    curriculum_status: Optional[str] = "in_preparation"
    source_authority: Optional[str] = None
    source_url: Optional[str] = None
    syllabus_version: Optional[str] = None
    status_message: Optional[str] = None

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
    curriculum_status: Optional[str] = "in_preparation"
    source_authority: Optional[str] = None
    source_url: Optional[str] = None
    syllabus_version: Optional[str] = None
    status_message: Optional[str] = None
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


class LearningObjectiveResponse(BaseModel):
    """Granular syllabus objective benchmark."""
    id: int
    topic_id: int
    code: str
    description: str
    taxonomy_level: str
    is_core: bool
    is_verified: bool

    model_config = ConfigDict(from_attributes=True)


class PreviousYearQuestionResponse(BaseModel):
    """Authentic previous year exam question with verified provenance."""
    id: int
    subject_id: int
    topic_id: int
    board: str
    grade: str
    exam_year: int
    paper_code: str
    question_number: str
    question_text: str
    marks: int
    marking_scheme: Optional[str] = None
    source_name: str
    source_url: Optional[str] = None
    is_verified: bool
    verified_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class PracticeOption(BaseModel):
    """Option item for MCQ practice questions."""
    id: str
    text: str


class PracticeQuestionResponse(BaseModel):
    """Curriculum practice question strictly labeled as AI-generated."""
    id: int
    topic_id: int
    learning_objective_id: Optional[int] = None
    question_text: str
    question_type: str
    options: Optional[Any] = None
    correct_answer: str
    explanation: str
    difficulty: str
    marks: int
    is_ai_generated: bool
    generation_provenance: Optional[Any] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PracticeQuestionAttemptRequest(BaseModel):
    """Payload for student submitting an answer attempt."""
    user_answer: str = Field(..., min_length=1, max_length=2000)


class PracticeQuestionAttemptResponse(BaseModel):
    """Immediate evaluation and feedback on student practice submission."""
    id: int
    question_id: int
    question_type: str
    user_answer: str
    is_correct: bool
    marks_obtained: float
    max_marks: int
    feedback: str
    explanation: str
    attempted_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TopicStudyNotesResponse(BaseModel):
    """10-part pedagogical study notes model."""
    id: int
    topic_id: int
    notes_type: str
    title: str
    overview: str
    learning_objectives_json: Optional[Any] = None
    explanation_markdown: str
    key_terms_json: Optional[Any] = None
    formulas_and_dates_json: Optional[Any] = None
    diagrams_json: Optional[Any] = None
    common_misconceptions_json: Optional[Any] = None
    exam_points_json: Optional[Any] = None
    practice_questions_json: Optional[Any] = None
    source_references_json: Optional[Any] = None
    version: int
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TopicNotesGenerateRequest(BaseModel):
    """Request payload to request dynamic notes generation."""
    notes_type: Literal["comprehensive", "revision"] = "comprehensive"
    force_regenerate: bool = False

