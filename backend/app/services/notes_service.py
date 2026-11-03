"""
Dynamic Study Notes Service for SmartLearn.AI.
Generates, caches, versions, and serves curriculum-grounded 10-part study notes.
"""

from datetime import datetime, timezone
import json
import logging
from typing import Any, Dict, List, Optional
import httpx
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.learning import TopicStudyNotes
from app.repositories.learning_repository import LearningRepository
from app.schemas.learning import TopicStudyNotesResponse
from app.services.rag_service import RAGRetrievalService
from app.services.tutor_service import TutorService

logger = logging.getLogger("smartlearn.notes")
settings = get_settings()


class NotesService:
    """Orchestrates 10-part pedagogical study notes retrieval and generation."""

    @classmethod
    def get_or_generate_notes(
        cls,
        db: Session,
        user_id: int,
        topic_id: int,
        notes_type: str = "comprehensive",
        force_regenerate: bool = False,
        client: Optional[httpx.Client] = None,
    ) -> TopicStudyNotesResponse:
        """
        Fetch cached verified notes or generate dynamically from verified topic resources.
        Prevents redundant re-generation through database caching.
        """
        # 1. Check database cache
        if not force_regenerate:
            cached = LearningRepository.get_topic_study_notes(
                db, topic_id=topic_id, notes_type=notes_type
            )
            if cached:
                return TopicStudyNotesResponse.model_validate(cached)

        # 2. Retrieve verified evidence bundle
        bundle = RAGRetrievalService.validate_and_retrieve_context(
            db=db, user_id=user_id, topic_id=topic_id
        )

        # 3. If API key not configured or fallback needed, check existing or generate structured template
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            # Fall back to existing cached or construct direct verified syllabus notes
            cached = LearningRepository.get_topic_study_notes(db, topic_id=topic_id, notes_type=notes_type)
            if cached:
                return TopicStudyNotesResponse.model_validate(cached)
            raise ValueError("AI Notes generation requires GEMINI_API_KEY to be configured.")

        # 4. Generate structured notes using Gemini grounded in verified resources
        evidence_text = RAGRetrievalService.format_evidence_for_prompt(bundle)
        objectives_list = [obj.description for obj in bundle.learning_objectives]

        prompt = (
            f"Generate a professional, pedagogical, 10-part study note for the topic:\n"
            f"Subject: {bundle.subject.name} ({bundle.subject.board} {bundle.subject.grade})\n"
            f"Chapter {bundle.chapter.chapter_number}: {bundle.chapter.title}\n"
            f"Topic {bundle.topic.topic_number}: {bundle.topic.title}\n\n"
            f"VERIFIED EVIDENCE AND SYLLABUS CONTEXT:\n{evidence_text}\n\n"
            f"Structure your response strictly with these 10 distinct Markdown headings:\n"
            f"### 1. Topic Overview\n"
            f"### 2. Learning Objectives\n"
            f"### 3. Core Pedagogical Explanation\n"
            f"### 4. Key Terms & Concepts\n"
            f"### 5. Important Facts, Dates & Formulas\n"
            f"### 6. Case Studies & Worked Examples\n"
            f"### 7. Conceptual Architecture Diagram (Include a safe ```mermaid flowchart TD``` code block)\n"
            f"### 8. Common Student Misconceptions (Use > callouts)\n"
            f"### 9. High-Yield Exam Revision Points\n"
            f"### 10. Practice Questions and Explanations\n\n"
            f"Do not use emojis. Ground all statements in the verified syllabus evidence."
        )

        system_instruction = (
            f"You are the senior curriculum developer for SmartLearn.AI. "
            f"You create rigorous, beautiful, syllabus-aligned study notes for {bundle.subject.board} {bundle.subject.grade}."
        )

        gemini_payload = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "system_instruction": {"parts": [{"text": system_instruction}]},
            "generationConfig": {
                "temperature": 0.4,
                "maxOutputTokens": 3000,
            },
        }

        generated_markdown = TutorService._call_gemini_api(
            api_key=api_key,
            model=settings.AI_TUTOR_MODEL,
            payload=gemini_payload,
            client=client,
        )

        # 5. Extract overview and build structured JSON metadata
        overview_match = generated_markdown[:400].strip()
        source_refs = [
            {"title": r.title, "url": r.source_url, "verified": r.is_verified}
            for r in bundle.verified_resources
        ]

        # Extract Mermaid diagram code if present
        diagrams_json = []
        if "```mermaid" in generated_markdown:
            try:
                mermaid_block = generated_markdown.split("```mermaid")[1].split("```")[0].strip()
                diagrams_json.append({
                    "title": f"Process Diagram for {bundle.topic.title}",
                    "diagram_type": "mermaid",
                    "code": mermaid_block,
                    "description": "Visual conceptual map of topic relationships",
                })
            except Exception as e:
                logger.warning(f"Could not parse mermaid block: {e}")

        # 6. Upsert into database cache
        notes_record = LearningRepository.upsert_topic_study_notes(
            db=db,
            topic_id=bundle.topic.id,
            notes_type=notes_type,
            title=f"{bundle.subject.name} - {bundle.topic.title}",
            overview=f"Comprehensive {bundle.subject.board} {bundle.subject.grade} study notes for {bundle.topic.title}.",
            explanation_markdown=generated_markdown,
            learning_objectives_json=objectives_list,
            diagrams_json=diagrams_json,
            source_references_json=source_refs,
            is_verified=True,
        )

        return TopicStudyNotesResponse.model_validate(notes_record)
