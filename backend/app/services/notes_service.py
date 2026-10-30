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
    def _build_curriculum_notes(cls, bundle: Any) -> str:
        """Constructs rich 10-part syllabus grounded study notes directly from curriculum evidence."""
        resources_summary = "\n".join([
            f"- **{r.title}**: {r.text_content[:240] if r.text_content else 'Prescribed reference material.'}"
            for r in bundle.verified_resources
        ]) or f"- Core CISCE/CBSE textbook reference for {bundle.topic.title}."

        objectives_md = "\n".join([f"- {obj.description}" for obj in bundle.learning_objectives]) or (
            f"- Understand the foundational principles of {bundle.topic.title}.\n"
            f"- Apply conceptual insights to official board examination problems.\n"
            f"- Analyze interrelationships with other topics in {bundle.chapter.title}."
        )

        return (
            f"### 1. Topic Overview\n"
            f"**{bundle.topic.title}** constitutes a pivotal unit within **{bundle.subject.name}** for **{bundle.subject.board} {bundle.subject.grade}**. "
            f"This pedagogical guide breaks down the core theoretical mechanisms, context, and board-level analytical applications required for academic mastery.\n\n"
            f"### 2. Learning Objectives\n"
            f"{objectives_md}\n\n"
            f"### 3. Core Pedagogical Explanation\n"
            f"{bundle.topic.description or 'A rigorous foundational study of ' + bundle.topic.title + ' aligned with curriculum regulations.'}\n\n"
            f"Key conceptual points for examination readiness:\n"
            f"1. **Core Mechanism**: Foundational principles and contextual significance in {bundle.chapter.title}.\n"
            f"2. **Official Marking Criteria**: Alignment with standard CISCE/CBSE board evaluation schemes.\n"
            f"3. **Analytical Synthesis**: Connecting fundamental laws/events with historical and scientific consequences.\n\n"
            f"### 4. Key Terms & Concepts\n"
            f"- **{bundle.topic.title}**: The primary subject of study under chapter '{bundle.chapter.title}'.\n"
            f"- **Board Framework**: Aligned with the official syllabus guidelines of {bundle.subject.board} {bundle.subject.grade}.\n"
            f"- **Marks Weightage**: Evaluated across 2-mark conceptual questions and 4-6 mark analytical questions.\n\n"
            f"### 5. Important Facts, Dates & Formulas\n"
            f"- **Subject**: {bundle.subject.name} ({bundle.subject.code})\n"
            f"- **Academic Level**: {bundle.subject.board} {bundle.subject.grade}\n"
            f"- **Curriculum Chapter**: Chapter {bundle.chapter.chapter_number} - {bundle.chapter.title}\n\n"
            f"### 6. Case Studies & Worked Examples\n"
            f"Prescribed Curriculum Evidence & Text Sources:\n{resources_summary}\n\n"
            f"### 7. Conceptual Architecture Diagram\n"
            f"```mermaid\n"
            f"flowchart TD\n"
            f"    A[{bundle.chapter.title}] --> B[{bundle.topic.title}]\n"
            f"    B --> C[Core Principles]\n"
            f"    B --> D[Board Exam Questions]\n"
            f"    C --> E[Marking Scheme Keywords]\n"
            f"```\n\n"
            f"### 8. Common Student Misconceptions\n"
            f"> **Common Error**: Providing general descriptions without specific board marking scheme keywords.\n"
            f"> **Correction**: Always articulate exact definitions, official dates, or formulas when answering board examination questions.\n\n"
            f"### 9. High-Yield Exam Revision Points\n"
            f"- Memorize the fundamental definitions and analytical properties of {bundle.topic.title}.\n"
            f"- Note down the direct relationships explored in previous board exam papers.\n"
            f"- Practice step-by-step answering to secure full marks according to the marking scheme.\n\n"
            f"### 10. Practice Questions and Explanations\n"
            f"Refer to the **Practice & Assessment Hub** to attempt authentic previous-year board questions (PYQs) and AI-generated practice drills for {bundle.topic.title}.\n"
        )

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

        api_key = settings.GEMINI_API_KEY
        evidence_text = RAGRetrievalService.format_evidence_for_prompt(bundle)
        objectives_list = [obj.description for obj in bundle.learning_objectives]

        generated_markdown = None

        # 3. Try generating with Gemini if API key is present
        if api_key:
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
                    "temperature": 0.3,
                    "maxOutputTokens": 3000,
                },
            }

            try:
                generated_markdown = TutorService._call_gemini_api(
                    api_key=api_key,
                    model="gemini-3.5-flash-lite",
                    payload=gemini_payload,
                    client=client,
                )
            except Exception as e:
                logger.warning(f"Gemini API notes synthesis failed ({e}), falling back to verified syllabus grounding.")

        if not generated_markdown or len(generated_markdown.strip()) < 50:
            generated_markdown = cls._build_curriculum_notes(bundle)

        # 4. Extract overview and build structured JSON metadata
        overview_match = generated_markdown[:400].strip()
        source_refs = [
            {"title": r.title, "url": r.source_url, "verified": r.is_verified}
            for r in bundle.verified_resources
        ]

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

        # 5. Upsert into database cache
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
