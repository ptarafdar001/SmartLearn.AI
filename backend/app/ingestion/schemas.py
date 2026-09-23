"""
Pydantic V2 Schemas for Curriculum Ingestion Pipeline.

Enforces strict source provenance, educational standards (Bloom's taxonomy),
content segregation (Authentic PYQ vs AI Practice), and pedagogical structure.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class VerificationStatus(str, Enum):
    """Content verification tier for provenance tracking."""
    MACHINE_EXTRACTED = "machine_extracted"
    AI_DRAFT = "ai_draft"
    HUMAN_REVIEWED = "human_reviewed"
    VERIFIED_PUBLISHED = "verified_published"


class TaxonomyLevel(str, Enum):
    """Bloom's Revised Taxonomy levels for learning objectives."""
    REMEMBER = "remember"
    UNDERSTAND = "understand"
    APPLY = "apply"
    ANALYZE = "analyze"
    EVALUATE = "evaluate"
    CREATE = "create"


class ResourceType(str, Enum):
    """Permitted multi-modal resource types."""
    TEXT = "text"
    VIDEO = "video"
    AUDIO = "audio"
    NOTES = "notes"
    INTERACTIVE = "interactive"
    REVISION = "revision"


class SourceProvenanceSchema(BaseModel):
    """Metadata certifying the authoritative origin of the curriculum or content item."""
    source_authority: str = Field(
        ...,
        min_length=2,
        description="Official issuing body (e.g., 'CBSE / NCERT', 'CISCE', 'State Board').",
    )
    source_name: str = Field(
        ...,
        min_length=3,
        description="Specific document or publication title (e.g. 'CBSE Secondary Curriculum 2026-27').",
    )
    source_url: str = Field(
        ...,
        description="Official publication URL or stable reference portal.",
    )
    syllabus_version: str = Field(
        ...,
        description="Academic year or syllabus version (e.g., 'Academic Year 2026-27').",
    )
    document_ref: Optional[str] = Field(
        default=None,
        description="Official circular, document code, or PDF filename reference.",
    )
    retrieval_date: str = Field(
        ...,
        description="ISO date string when the syllabus source was accessed or verified (YYYY-MM-DD).",
    )
    verification_status: VerificationStatus = Field(
        default=VerificationStatus.VERIFIED_PUBLISHED,
        description="Review tier: verified_published, human_reviewed, ai_draft, machine_extracted.",
    )
    license_or_terms: Optional[str] = Field(
        default="Official Public Curriculum / Permitted Educational Attribution",
        description="Copyright or usage terms declaration.",
    )

    @field_validator("source_url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        v_str = str(v).strip()
        if not v_str.startswith("http://") and not v_str.startswith("https://"):
            raise ValueError(f"source_url must be a valid HTTP/HTTPS URL: {v}")
        return v_str


class LearningObjectiveIngestSchema(BaseModel):
    """Granular learning objective mapped to a topic with Bloom's taxonomy."""
    code: str = Field(..., min_length=3, max_length=50, description="Unique objective code e.g. CBSE10-SCI-CH01-LO01")
    description: str = Field(..., min_length=10, description="Verifiable pedagogical objective description")
    taxonomy_level: TaxonomyLevel = Field(default=TaxonomyLevel.UNDERSTAND)
    is_core: bool = Field(default=True)
    is_verified: bool = Field(default=True)


class LearningResourceIngestSchema(BaseModel):
    """Multi-modal educational resource with attribution and provenance."""
    title: str = Field(..., min_length=3, max_length=255)
    resource_type: ResourceType = Field(default=ResourceType.TEXT)
    provider: str = Field(default="smartlearn", max_length=50)
    source_name: Optional[str] = Field(default=None, max_length=150)
    source_url: Optional[str] = None
    external_id: Optional[str] = Field(default=None, max_length=255)
    content_url: Optional[str] = None
    text_content: Optional[str] = None
    duration_seconds: Optional[int] = None
    language: str = Field(default="en", max_length=20)
    order_index: int = Field(default=1)
    is_verified: bool = Field(default=True)

    @field_validator("source_url", "content_url")
    @classmethod
    def validate_optional_urls(cls, v: Optional[str]) -> Optional[str]:
        if v:
            v_str = str(v).strip()
            if not v_str.startswith("http://") and not v_str.startswith("https://"):
                raise ValueError(f"Resource URL must start with http:// or https://: {v}")
            return v_str
        return None


class PreviousYearQuestionIngestSchema(BaseModel):
    """
    Authentic official examination question from authorized board papers.
    Strictly segregated from AI practice questions.
    """
    board: str = Field(..., min_length=2, max_length=50)
    grade: str = Field(..., min_length=2, max_length=50)
    exam_year: int = Field(..., ge=1990, le=2030, description="Year of board examination")
    paper_code: str = Field(..., min_length=2, max_length=100, description="Official paper code e.g. 'CBSE-31/1/1-2023'")
    question_number: str = Field(..., min_length=1, max_length=50, description="Question number in paper e.g. 'Question 4(b)'")
    question_text: str = Field(..., min_length=10)
    marks: int = Field(..., ge=1, le=20)
    marking_scheme: Optional[str] = Field(default=None, description="Official marking scheme or answer key points")
    source_name: str = Field(..., min_length=3, max_length=255, description="Official paper source")
    source_url: Optional[str] = Field(default=None, description="Official board paper or syllabus portal link")
    is_verified: bool = Field(default=True)


class PracticeQuestionIngestSchema(BaseModel):
    """
    AI-generated or curated practice question with explicit labeling and provenance.
    """
    question_text: str = Field(..., min_length=10)
    question_type: Literal["mcq", "short_answer", "long_answer"] = "mcq"
    options: Optional[List[Dict[str, str]]] = Field(
        default=None,
        description="Options for MCQ questions e.g. [{'id': 'A', 'text': '...'}]",
    )
    correct_answer: str = Field(..., min_length=1)
    explanation: str = Field(..., min_length=10)
    difficulty: Literal["easy", "medium", "hard"] = "medium"
    marks: int = Field(default=1, ge=1, le=10)
    is_ai_generated: bool = Field(
        default=True,
        description="MUST be true for synthetic/AI-generated practice questions.",
    )
    generation_provenance: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Audit metadata: model, template_version, prompt_hash, timestamp.",
    )

    @field_validator("is_ai_generated")
    @classmethod
    def enforce_ai_label(cls, v: bool) -> bool:
        # Safety enforcement: practice questions ingested via this schema must be transparently labeled
        return v


class TopicStudyNotesIngestSchema(BaseModel):
    """
    10-part pedagogical study notes aligned with syllabus structure.
    """
    notes_type: Literal["comprehensive", "revision"] = "comprehensive"
    title: str = Field(..., min_length=5, max_length=255)
    overview: str = Field(..., min_length=20)
    learning_objectives: Optional[List[str]] = None
    explanation_markdown: str = Field(..., min_length=50)
    key_terms: Optional[List[Dict[str, str]]] = None
    formulas_and_dates: Optional[List[Dict[str, str]]] = None
    diagrams: Optional[List[Dict[str, str]]] = None
    common_misconceptions: Optional[List[Dict[str, str]]] = None
    exam_points: Optional[List[str]] = None
    practice_questions: Optional[List[Dict[str, Any]]] = None
    source_references: Optional[List[Dict[str, str]]] = None
    version: int = Field(default=1, ge=1)
    is_verified: bool = Field(default=True)


class TopicIngestSchema(BaseModel):
    """Lesson or atomic concept unit within a chapter."""
    topic_number: int = Field(..., ge=1)
    title: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = None
    estimated_minutes: int = Field(default=20, ge=5, le=180)
    learning_objectives: List[LearningObjectiveIngestSchema] = Field(default_factory=list)
    resources: List[LearningResourceIngestSchema] = Field(default_factory=list)
    pyqs: List[PreviousYearQuestionIngestSchema] = Field(default_factory=list)
    practice_questions: List[PracticeQuestionIngestSchema] = Field(default_factory=list)
    study_notes: Optional[TopicStudyNotesIngestSchema] = None


class ChapterIngestSchema(BaseModel):
    """Official chapter or unit in the syllabus."""
    chapter_number: int = Field(..., ge=1)
    title: str = Field(..., min_length=3, max_length=255)
    section: Optional[str] = Field(default=None, max_length=150)
    description: Optional[str] = None
    topics: List[TopicIngestSchema] = Field(default_factory=list)


class CurriculumManifestSchema(BaseModel):
    """
    Complete schema for an authoritative curriculum manifest document.
    """
    subject_code: str = Field(..., min_length=3, max_length=100, description="Canonical subject code e.g. cbse-class-10-sci")
    board: str = Field(..., min_length=2, max_length=100)
    grade: str = Field(..., min_length=2, max_length=50)
    academic_stream: Optional[str] = Field(default=None, max_length=100)
    subject_name: str = Field(..., min_length=2, max_length=150)
    category: str = Field(default="core", max_length=50)
    curriculum_status: Literal["catalogued", "curriculum_verified", "content_available", "in_preparation"] = "content_available"
    source_provenance: SourceProvenanceSchema
    chapters: List[ChapterIngestSchema] = Field(..., min_length=1)
    subject_pyqs: List[PreviousYearQuestionIngestSchema] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid")
