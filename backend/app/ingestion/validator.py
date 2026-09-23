"""
Validation Engine for Curriculum Ingestion.

Enforces:
- Schema conformance and non-empty source provenance.
- Duplicate detection across chapters, topics, learning objectives, and PYQs.
- Segregation and quarantine of unreviewed/synthetic content.
- Preservation of existing verified content against regressions.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
from sqlalchemy.orm import Session

from app.ingestion.schemas import (
    CurriculumManifestSchema,
    VerificationStatus,
)
from app.models.learning import Chapter, LearningObjective, PreviousYearQuestion, Subject, Topic


@dataclass
class ValidationResult:
    """Detailed outcome of manifest validation."""
    is_valid: bool
    subject_id: Optional[int] = None
    canonical_subject: Optional[Subject] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    stats: Dict[str, int] = field(default_factory=dict)

    def add_error(self, msg: str) -> None:
        self.errors.append(msg)
        self.is_valid = False

    def add_warning(self, msg: str) -> None:
        self.warnings.append(msg)


class CurriculumValidator:
    """Validates curriculum manifests against database state and integrity rules."""

    @classmethod
    def validate(
        cls,
        manifest: CurriculumManifestSchema,
        db: Session,
        allow_drafts: bool = False,
    ) -> ValidationResult:
        result = ValidationResult(is_valid=True)

        # 1. Resolve Canonical Subject in DB
        subject = db.query(Subject).filter(Subject.code == manifest.subject_code).first()
        if not subject:
            # Fallback search by board, grade, name
            query = db.query(Subject).filter(
                Subject.board == manifest.board,
                Subject.grade == manifest.grade,
                Subject.name == manifest.subject_name,
            )
            if manifest.academic_stream:
                query = query.filter(Subject.academic_stream == manifest.academic_stream)
            subject = query.first()

        if not subject:
            result.add_error(
                f"Subject not found in canonical catalog for code '{manifest.subject_code}' "
                f"or tuple ({manifest.board}, {manifest.grade}, {manifest.subject_name}). "
                f"Ensure canonical subject exists in catalog before ingesting syllabus."
            )
        else:
            result.subject_id = subject.id
            result.canonical_subject = subject

        # 2. Check Provenance Tier & Quarantine Unreviewed Drafts
        prov = manifest.source_provenance
        if prov.verification_status == VerificationStatus.AI_DRAFT and not allow_drafts:
            result.add_error(
                f"Quarantine Violation: Manifest '{manifest.subject_code}' is marked as 'ai_draft'. "
                f"Unreviewed AI-generated curriculum cannot be published to the authoritative database."
            )

        # 3. Duplicate Chapter Detection
        seen_chapters: Set[int] = set()
        total_topics = 0
        total_objectives = 0
        total_resources = 0
        total_pyqs = len(manifest.subject_pyqs)
        total_practice_qs = 0
        total_notes = 0

        all_objective_codes: Set[str] = set()
        seen_pyq_keys: Set[Tuple[str, str]] = set()

        # Check subject-level PYQs
        for spyq in manifest.subject_pyqs:
            key = (spyq.paper_code.strip(), spyq.question_number.strip())
            if key in seen_pyq_keys:
                result.add_error(f"Duplicate subject-level PYQ detected: paper '{key[0]}', number '{key[1]}'")
            seen_pyq_keys.add(key)

        for ch in manifest.chapters:
            if ch.chapter_number in seen_chapters:
                result.add_error(f"Duplicate chapter number {ch.chapter_number} detected: '{ch.title}'")
            seen_chapters.add(ch.chapter_number)

            seen_topics: Set[int] = set()
            for top in ch.topics:
                total_topics += 1
                if top.topic_number in seen_topics:
                    result.add_error(
                        f"Duplicate topic number {top.topic_number} in Chapter {ch.chapter_number}: '{top.title}'"
                    )
                seen_topics.add(top.topic_number)

                # Validate Learning Objectives
                for lo in top.learning_objectives:
                    total_objectives += 1
                    lo_code = lo.code.strip()
                    if lo_code in all_objective_codes:
                        result.add_error(f"Duplicate Learning Objective code '{lo_code}' in topic '{top.title}'")
                    all_objective_codes.add(lo_code)

                # Validate Resources
                for res in top.resources:
                    total_resources += 1
                    if not res.source_name and not res.source_url:
                        result.add_warning(
                            f"Resource '{res.title}' in Topic {top.topic_number} has no explicit source attribution."
                        )

                # Validate Topic PYQs
                for pyq in top.pyqs:
                    total_pyqs += 1
                    key = (pyq.paper_code.strip(), pyq.question_number.strip())
                    if key in seen_pyq_keys:
                        result.add_error(
                            f"Duplicate PYQ key (paper '{key[0]}', number '{key[1]}') in Topic '{top.title}'"
                        )
                    seen_pyq_keys.add(key)

                    # Provenance enforcement on PYQs: reject without verifiable board paper reference
                    if not pyq.source_name:
                        result.add_error(f"PYQ '{key[0]} {key[1]}' lacks mandatory source_name attribution.")

                # Validate Practice Questions
                for pq in top.practice_questions:
                    total_practice_qs += 1
                    if not pq.is_ai_generated:
                        result.add_warning(
                            f"Practice question in Topic '{top.title}' is marked is_ai_generated=False. "
                            f"Ensure authentic past questions are categorized as PYQs instead."
                        )

                # Validate Study Notes
                if top.study_notes:
                    total_notes += 1
                    notes = top.study_notes
                    if not notes.overview or len(notes.overview) < 20:
                        result.add_error(f"Study note for topic '{top.title}' has insufficient overview.")
                    if not notes.explanation_markdown or len(notes.explanation_markdown) < 50:
                        result.add_error(f"Study note for topic '{top.title}' has insufficient explanation text.")

        # 4. Protection of Verified Content in Existing DB
        if subject:
            # If the database already has verified content, ensure manifest does not attempt to drop verified chapters
            existing_chapters = db.query(Chapter).filter(Chapter.subject_id == subject.id).all()
            if existing_chapters and subject.curriculum_status == "content_available":
                manifest_ch_nums = {c.chapter_number for c in manifest.chapters}
                for ech in existing_chapters:
                    if ech.chapter_number not in manifest_ch_nums:
                        result.add_warning(
                            f"Existing verified Chapter {ech.chapter_number} ('{ech.title}') is absent from manifest. "
                            f"It will be preserved and not deleted silently."
                        )

        # Populate summary stats
        result.stats = {
            "chapters": len(manifest.chapters),
            "topics": total_topics,
            "learning_objectives": total_objectives,
            "resources": total_resources,
            "pyqs": total_pyqs,
            "practice_questions": total_practice_qs,
            "study_notes": total_notes,
        }

        return result
