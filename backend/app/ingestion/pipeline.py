"""
Curriculum Ingestion Pipeline Orchestrator.

Provides transactional, schema-validated, and idempotent ingestion
for multi-modal curriculum manifests.
"""

from datetime import datetime, timezone
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.ingestion.preview import IngestionPreviewGenerator, PreviewReport
from app.ingestion.schemas import CurriculumManifestSchema
from app.ingestion.validator import CurriculumValidator, ValidationResult
from app.models.learning import (
    Chapter,
    LearningObjective,
    LearningResource,
    PracticeQuestion,
    PreviousYearQuestion,
    Subject,
    Topic,
    TopicStudyNotes,
)

logger = logging.getLogger("smartlearn.ingestion")


class IngestionError(Exception):
    """Raised when curriculum ingestion fails validation or database execution."""
    def __init__(self, message: str, errors: Optional[list] = None):
        super().__init__(message)
        self.errors = errors or []


class CurriculumIngestionPipeline:
    """Executes validated, repeatable, idempotent curriculum ingestion."""

    @classmethod
    def load_manifest(cls, source: Union[str, Path, Dict[str, Any]]) -> CurriculumManifestSchema:
        """Parse and schema-validate a manifest from file path or dictionary."""
        if isinstance(source, (str, Path)):
            path = Path(source)
            if not path.is_file():
                raise IngestionError(f"Manifest file not found: {path}")
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = source

        try:
            return CurriculumManifestSchema.model_validate(data)
        except Exception as e:
            raise IngestionError(f"Schema validation failed: {e}")

    @classmethod
    def run(
        cls,
        source: Union[str, Path, Dict[str, Any]],
        dry_run: bool = True,
        allow_drafts: bool = False,
        db_session: Optional[Session] = None,
    ) -> Dict[str, Any]:
        """
        Execute the curriculum ingestion workflow.
        Returns preview report and execution status dictionary.
        """
        manifest = cls.load_manifest(source)

        owns_session = False
        db = db_session
        if db is None:
            db = SessionLocal()
            owns_session = True

        try:
            # 1. Validate against integrity rules
            validation_res: ValidationResult = CurriculumValidator.validate(
                manifest=manifest,
                db=db,
                allow_drafts=allow_drafts,
            )

            if not validation_res.is_valid:
                error_summary = "; ".join(validation_res.errors)
                raise IngestionError(
                    f"Curriculum validation rejected manifest '{manifest.subject_code}': {error_summary}",
                    errors=validation_res.errors,
                )

            subject = validation_res.canonical_subject
            assert subject is not None

            # 2. Generate Dry-run Preview
            preview_report: PreviewReport = IngestionPreviewGenerator.generate(
                manifest=manifest,
                subject=subject,
                db=db,
            )

            if dry_run:
                logger.info(f"Dry-run completed successfully for {manifest.subject_code}.")
                return {
                    "status": "dry_run_success",
                    "subject_id": subject.id,
                    "subject_code": subject.code,
                    "preview_report": preview_report,
                    "rendered_preview": preview_report.render_text(),
                    "warnings": validation_res.warnings,
                }

            # 3. Publish to Database (Idempotent Upsert)
            now = datetime.now(timezone.utc)

            # Update Subject metadata & provenance
            subject.curriculum_status = manifest.curriculum_status
            subject.source_authority = manifest.source_provenance.source_authority
            subject.source_url = manifest.source_provenance.source_url
            subject.syllabus_version = manifest.source_provenance.syllabus_version
            subject.last_verified_at = now
            db.flush()

            # Process Chapters
            for ch_data in manifest.chapters:
                chapter = (
                    db.query(Chapter)
                    .filter(
                        Chapter.subject_id == subject.id,
                        Chapter.chapter_number == ch_data.chapter_number,
                    )
                    .first()
                )
                if not chapter:
                    chapter = Chapter(
                        subject_id=subject.id,
                        chapter_number=ch_data.chapter_number,
                        title=ch_data.title,
                        description=ch_data.description,
                    )
                    db.add(chapter)
                    db.flush()
                else:
                    chapter.title = ch_data.title
                    chapter.description = ch_data.description
                    db.flush()

                # Process Topics
                for top_data in ch_data.topics:
                    topic = (
                        db.query(Topic)
                        .filter(
                            Topic.chapter_id == chapter.id,
                            Topic.topic_number == top_data.topic_number,
                        )
                        .first()
                    )
                    if not topic:
                        topic = Topic(
                            chapter_id=chapter.id,
                            topic_number=top_data.topic_number,
                            title=top_data.title,
                            description=top_data.description,
                            estimated_minutes=top_data.estimated_minutes,
                        )
                        db.add(topic)
                        db.flush()
                    else:
                        topic.title = top_data.title
                        topic.description = top_data.description
                        topic.estimated_minutes = top_data.estimated_minutes
                        db.flush()

                    # Process Learning Objectives
                    for lo_data in top_data.learning_objectives:
                        lo = (
                            db.query(LearningObjective)
                            .filter(
                                LearningObjective.topic_id == topic.id,
                                LearningObjective.code == lo_data.code,
                            )
                            .first()
                        )
                        if not lo:
                            lo = LearningObjective(
                                topic_id=topic.id,
                                code=lo_data.code,
                                description=lo_data.description,
                                taxonomy_level=lo_data.taxonomy_level.value,
                                is_core=lo_data.is_core,
                                is_verified=lo_data.is_verified,
                            )
                            db.add(lo)
                        else:
                            lo.description = lo_data.description
                            lo.taxonomy_level = lo_data.taxonomy_level.value
                            lo.is_core = lo_data.is_core
                            lo.is_verified = lo_data.is_verified

                    # Process Learning Resources
                    for res_data in top_data.resources:
                        res = (
                            db.query(LearningResource)
                            .filter(
                                LearningResource.topic_id == topic.id,
                                LearningResource.order_index == res_data.order_index,
                            )
                            .first()
                        )
                        if not res:
                            res = LearningResource(
                                topic_id=topic.id,
                                title=res_data.title,
                                resource_type=res_data.resource_type.value,
                                provider=res_data.provider,
                                source_name=res_data.source_name,
                                source_url=res_data.source_url,
                                external_id=res_data.external_id,
                                content_url=res_data.content_url,
                                text_content=res_data.text_content,
                                duration_seconds=res_data.duration_seconds,
                                language=res_data.language,
                                order_index=res_data.order_index,
                                is_active=True,
                                is_verified=res_data.is_verified,
                                verified_at=now if res_data.is_verified else None,
                            )
                            db.add(res)
                        else:
                            res.title = res_data.title
                            res.resource_type = res_data.resource_type.value
                            res.provider = res_data.provider
                            res.source_name = res_data.source_name
                            res.source_url = res_data.source_url
                            res.external_id = res_data.external_id
                            res.content_url = res_data.content_url
                            res.text_content = res_data.text_content
                            res.duration_seconds = res_data.duration_seconds
                            res.language = res_data.language
                            res.is_verified = res_data.is_verified

                    # Process Topic-level Authentic PYQs
                    for pyq_data in top_data.pyqs:
                        pyq = (
                            db.query(PreviousYearQuestion)
                            .filter(
                                PreviousYearQuestion.topic_id == topic.id,
                                PreviousYearQuestion.paper_code == pyq_data.paper_code,
                                PreviousYearQuestion.question_number == pyq_data.question_number,
                            )
                            .first()
                        )
                        if not pyq:
                            pyq = PreviousYearQuestion(
                                subject_id=subject.id,
                                topic_id=topic.id,
                                board=pyq_data.board,
                                grade=pyq_data.grade,
                                exam_year=pyq_data.exam_year,
                                paper_code=pyq_data.paper_code,
                                question_number=pyq_data.question_number,
                                question_text=pyq_data.question_text,
                                marks=pyq_data.marks,
                                marking_scheme=pyq_data.marking_scheme,
                                source_name=pyq_data.source_name,
                                source_url=pyq_data.source_url,
                                is_verified=pyq_data.is_verified,
                                verified_at=now if pyq_data.is_verified else None,
                            )
                            db.add(pyq)
                        else:
                            pyq.question_text = pyq_data.question_text
                            pyq.marks = pyq_data.marks
                            pyq.marking_scheme = pyq_data.marking_scheme
                            pyq.source_name = pyq_data.source_name
                            pyq.source_url = pyq_data.source_url
                            pyq.is_verified = pyq_data.is_verified

                    # Process Practice Questions (Labeled AI practice)
                    for pq_data in top_data.practice_questions:
                        pq = (
                            db.query(PracticeQuestion)
                            .filter(
                                PracticeQuestion.topic_id == topic.id,
                                PracticeQuestion.question_text == pq_data.question_text,
                            )
                            .first()
                        )
                        if not pq:
                            pq = PracticeQuestion(
                                topic_id=topic.id,
                                question_text=pq_data.question_text,
                                question_type=pq_data.question_type,
                                options=pq_data.options,
                                correct_answer=pq_data.correct_answer,
                                explanation=pq_data.explanation,
                                difficulty=pq_data.difficulty,
                                marks=pq_data.marks,
                                is_ai_generated=pq_data.is_ai_generated,
                                generation_provenance=pq_data.generation_provenance or {
                                    "model": "smartlearn-verified-curator",
                                    "timestamp": now.isoformat(),
                                },
                            )
                            db.add(pq)

                    # Process Topic Study Notes
                    if top_data.study_notes:
                        sn_data = top_data.study_notes
                        sn = (
                            db.query(TopicStudyNotes)
                            .filter(
                                TopicStudyNotes.topic_id == topic.id,
                                TopicStudyNotes.notes_type == sn_data.notes_type,
                            )
                            .first()
                        )
                        if not sn:
                            sn = TopicStudyNotes(
                                topic_id=topic.id,
                                notes_type=sn_data.notes_type,
                                title=sn_data.title,
                                overview=sn_data.overview,
                                learning_objectives_json=sn_data.learning_objectives,
                                explanation_markdown=sn_data.explanation_markdown,
                                key_terms_json=sn_data.key_terms,
                                formulas_and_dates_json=sn_data.formulas_and_dates,
                                diagrams_json=sn_data.diagrams,
                                common_misconceptions_json=sn_data.common_misconceptions,
                                exam_points_json=sn_data.exam_points,
                                practice_questions_json=sn_data.practice_questions,
                                source_references_json=sn_data.source_references,
                                version=sn_data.version,
                                is_verified=sn_data.is_verified,
                            )
                            db.add(sn)
                        else:
                            sn.title = sn_data.title
                            sn.overview = sn_data.overview
                            sn.learning_objectives_json = sn_data.learning_objectives
                            sn.explanation_markdown = sn_data.explanation_markdown
                            sn.key_terms_json = sn_data.key_terms
                            sn.formulas_and_dates_json = sn_data.formulas_and_dates
                            sn.diagrams_json = sn_data.diagrams
                            sn.common_misconceptions_json = sn_data.common_misconceptions
                            sn.exam_points_json = sn_data.exam_points
                            sn.practice_questions_json = sn_data.practice_questions
                            sn.source_references_json = sn_data.source_references
                            sn.version = sn.version + 1
                            sn.is_verified = sn_data.is_verified

            # Process Subject-level PYQs
            for spyq_data in manifest.subject_pyqs:
                spyq = (
                    db.query(PreviousYearQuestion)
                    .filter(
                        PreviousYearQuestion.subject_id == subject.id,
                        PreviousYearQuestion.topic_id.is_(None),
                        PreviousYearQuestion.paper_code == spyq_data.paper_code,
                        PreviousYearQuestion.question_number == spyq_data.question_number,
                    )
                    .first()
                )
                if not spyq:
                    spyq = PreviousYearQuestion(
                        subject_id=subject.id,
                        topic_id=None,
                        board=spyq_data.board,
                        grade=spyq_data.grade,
                        exam_year=spyq_data.exam_year,
                        paper_code=spyq_data.paper_code,
                        question_number=spyq_data.question_number,
                        question_text=spyq_data.question_text,
                        marks=spyq_data.marks,
                        marking_scheme=spyq_data.marking_scheme,
                        source_name=spyq_data.source_name,
                        source_url=spyq_data.source_url,
                        is_verified=spyq_data.is_verified,
                        verified_at=now if spyq_data.is_verified else None,
                    )
                    db.add(spyq)

            db.commit()
            logger.info(f"Successfully published curriculum manifest for {manifest.subject_code}.")

            return {
                "status": "published_success",
                "subject_id": subject.id,
                "subject_code": subject.code,
                "preview_report": preview_report,
                "rendered_preview": preview_report.render_text(),
                "warnings": validation_res.warnings,
            }

        except Exception as e:
            if not dry_run and db:
                db.rollback()
            raise e
        finally:
            if owns_session and db:
                db.close()
