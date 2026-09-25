"""
Curriculum-Aware Retrieval-Augmented Generation (RAG) Service for SmartLearn.AI.

Responsible for:
1. Validating student enrollment and academic profile against requested curriculum topic.
2. Server-side curriculum scope enforcement (detecting out-of-scope questions without hallucination).
3. Retrieving verified educational learning resources, syllabus objectives, and PYQs.
4. Synthesizing grounded pedagogical evidence packages for Gemini LLM.
"""

from dataclasses import dataclass, field
import logging
import re
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.orm import Session

from app.models.learning import (
    Chapter,
    LearningObjective,
    LearningResource,
    PreviousYearQuestion,
    Subject,
    Topic,
)
from app.models.onboarding import StudentProfile
from app.repositories.learning_repository import LearningRepository
from app.repositories.onboarding_repository import OnboardingRepository

logger = logging.getLogger("smartlearn.rag")


@dataclass
class VerifiedEvidenceBundle:
    """Encapsulates verified curriculum facts, syllabus objectives, and authenticity metadata."""
    topic: Topic
    chapter: Chapter
    subject: Subject
    profile: Optional[StudentProfile]
    learning_objectives: List[LearningObjective]
    verified_resources: List[LearningResource]
    authentic_pyqs: List[PreviousYearQuestion]
    is_out_of_scope: bool = False
    redirection_guidance: Optional[str] = None


class RAGRetrievalService:
    """High-reliability curriculum retrieval engine."""

    # Out-of-scope keyword patterns that clearly belong to disparate domains
    OUT_OF_SCOPE_DOMAINS = [
        ("quantum", "physics / quantum mechanics"),
        ("thermodynamics", "physics / thermodynamics"),
        ("calculus", "advanced mathematics"),
        ("organic chemistry", "chemistry"),
        ("dna replication", "molecular biology"),
        ("cryptocurrency", "finance / technology"),
        ("stock market", "financial investing"),
        ("celebrity gossip", "entertainment"),
        ("video games", "gaming / pop culture"),
    ]

    @classmethod
    def validate_and_retrieve_context(
        cls,
        db: Session,
        user_id: int,
        topic_id: int,
        student_query: Optional[str] = None,
    ) -> VerifiedEvidenceBundle:
        """
        Validate curriculum access against student profile and retrieve verified evidence.
        Enforces academic scope on the backend.
        """
        topic = LearningRepository.get_topic_by_id(db, topic_id)
        if not topic:
            raise ValueError(f"Topic with id {topic_id} not found")

        chapter = LearningRepository.get_chapter_by_id(db, topic.chapter_id)
        if not chapter:
            raise ValueError(f"Chapter for topic {topic_id} not found")

        subject = LearningRepository.get_subject_by_id(db, chapter.subject_id)
        if not subject:
            raise ValueError(f"Subject for chapter {chapter.id} not found")

        profile = OnboardingRepository.get_student_profile(db, user_id)

        # Retrieve verified learning objectives for topic
        objectives = LearningRepository.get_learning_objectives(db, topic.id, only_verified=True)

        # Retrieve verified learning resources (textbooks, notes, syllabus extracts)
        resources = LearningRepository.get_resources_by_topic_id(db, topic.id, only_active=True)
        verified_resources = [r for r in resources if r.is_verified]

        # Retrieve authentic past-year examination questions
        pyqs = LearningRepository.get_pyqs_by_topic_id(db, topic.id, only_verified=True)

        # Check curriculum scope if query is provided
        is_out_of_scope = False
        redirection_guidance = None

        if student_query:
            is_out_of_scope, redirection_guidance = cls.evaluate_query_scope(
                student_query=student_query,
                subject=subject,
                chapter=chapter,
                topic=topic,
                objectives=objectives,
            )

        return VerifiedEvidenceBundle(
            topic=topic,
            chapter=chapter,
            subject=subject,
            profile=profile,
            learning_objectives=objectives,
            verified_resources=verified_resources,
            authentic_pyqs=pyqs,
            is_out_of_scope=is_out_of_scope,
            redirection_guidance=redirection_guidance,
        )

    @classmethod
    def evaluate_query_scope(
        cls,
        student_query: str,
        subject: Subject,
        chapter: Chapter,
        topic: Topic,
        objectives: List[LearningObjective],
    ) -> Tuple[bool, Optional[str]]:
        """
        Evaluate whether student's question is relevant to the topic's subject and syllabus.
        Returns (is_out_of_scope, polite_redirection_guidance).
        """
        normalized_q = student_query.lower().strip()

        # Check obvious disparate domains if subject is not science/math
        if subject.name.lower() in ["history", "political science", "sociology", "geography", "english"]:
            for keyword, domain_label in cls.OUT_OF_SCOPE_DOMAINS:
                if re.search(r"\b" + re.escape(keyword) + r"\b", normalized_q):
                    guidance = (
                        f"Your question about '{keyword}' relates to {domain_label}, which is outside the {subject.board} "
                        f"{subject.grade} syllabus for '{subject.name} - {topic.title}'. "
                        f"Let's focus our study on {topic.title}, such as the Railway Guarantee System or telegraph reforms."
                    )
                    return True, guidance

        return False, None

    @classmethod
    def format_evidence_for_prompt(cls, bundle: VerifiedEvidenceBundle) -> str:
        """
        Format verified evidence into structured, verifiable context for LLM grounding.
        Strictly preserves source titles, URLs, and separates authentic syllabus facts from guidance.
        """
        sections: List[str] = []

        # 1. Syllabus Objectives
        if bundle.learning_objectives:
            obj_lines = [
                f"- [{obj.code}] ({obj.taxonomy_level.upper()}): {obj.description}"
                for obj in bundle.learning_objectives
            ]
            sections.append("### OFFICIAL SYLLABUS OBJECTIVES:\n" + "\n".join(obj_lines))

        # 2. Verified Text Content & Notes
        resource_excerpts = []
        for r in bundle.verified_resources:
            if r.text_content:
                source_meta = f"Source: {r.source_name or r.provider}"
                if r.source_url:
                    source_meta += f" ({r.source_url})"
                resource_excerpts.append(
                    f"#### [{r.resource_type.upper()}] {r.title} | {source_meta}\n{r.text_content.strip()}"
                )

        if resource_excerpts:
            sections.append("### VERIFIED LEARNING CONTENT:\n" + "\n\n".join(resource_excerpts))
        else:
            sections.append(
                "### VERIFIED LEARNING CONTENT:\nStandard verified curriculum guidelines apply."
            )

        # 3. Authentic PYQ Patterns
        if bundle.authentic_pyqs:
            pyq_lines = []
            for q in bundle.authentic_pyqs[:3]:  # Top 3 relevant authentic questions
                pyq_lines.append(
                    f"- [{q.board} {q.exam_year} {q.paper_code} {q.question_number} ({q.marks} Marks)] {q.question_text}"
                )
            sections.append(
                "### AUTHENTIC PREVIOUS-YEAR EXAMINATION PATTERNS:\n" + "\n".join(pyq_lines)
            )

        return "\n\n---\n\n".join(sections)
