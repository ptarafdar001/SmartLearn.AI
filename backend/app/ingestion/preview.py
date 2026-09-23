"""
Preview Report Generator for Ingestion Pipeline.

Generates pre-publication diffs and change audits comparing
an incoming curriculum manifest with active database state.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from app.ingestion.schemas import CurriculumManifestSchema
from app.models.learning import (
    Chapter,
    LearningObjective,
    LearningResource,
    PracticeQuestion,
    PreviousYearQuestion,
    StudentProgress,
    Subject,
    Topic,
    TopicStudyNotes,
)


@dataclass
class EntityDiff:
    """Track additions, modifications, and unchanged items."""
    to_create: int = 0
    to_update: int = 0
    unchanged: int = 0
    details: List[str] = field(default_factory=list)


@dataclass
class PreviewReport:
    """Complete pre-publication preview report."""
    subject_code: str
    subject_title: str
    board: str
    grade: str
    current_status: Optional[str]
    proposed_status: str
    source_authority: str
    syllabus_version: str
    chapters: EntityDiff = field(default_factory=EntityDiff)
    topics: EntityDiff = field(default_factory=EntityDiff)
    learning_objectives: EntityDiff = field(default_factory=EntityDiff)
    learning_resources: EntityDiff = field(default_factory=EntityDiff)
    previous_year_questions: EntityDiff = field(default_factory=EntityDiff)
    practice_questions: EntityDiff = field(default_factory=EntityDiff)
    study_notes: EntityDiff = field(default_factory=EntityDiff)
    warnings: List[str] = field(default_factory=list)

    def render_text(self) -> str:
        """Render a clean, human-readable terminal summary."""
        lines = [
            "=" * 70,
            f"CURRICULUM INGESTION PREVIEW: {self.subject_title} ({self.board} {self.grade})",
            f"Subject Code: {self.subject_code}",
            f"Status Change: '{self.current_status}' -> '{self.proposed_status}'",
            f"Source Authority: {self.source_authority} | Version: {self.syllabus_version}",
            "-" * 70,
            f"{'Content Category':<28} | {'Create':<8} | {'Update':<8} | {'Unchanged':<10}",
            "-" * 70,
            f"{'Chapters':<28} | {self.chapters.to_create:<8} | {self.chapters.to_update:<8} | {self.chapters.unchanged:<10}",
            f"{'Topics':<28} | {self.topics.to_create:<8} | {self.topics.to_update:<8} | {self.topics.unchanged:<10}",
            f"{'Learning Objectives':<28} | {self.learning_objectives.to_create:<8} | {self.learning_objectives.to_update:<8} | {self.learning_objectives.unchanged:<10}",
            f"{'Learning Resources':<28} | {self.learning_resources.to_create:<8} | {self.learning_resources.to_update:<8} | {self.learning_resources.unchanged:<10}",
            f"{'Previous Year Questions':<28} | {self.previous_year_questions.to_create:<8} | {self.previous_year_questions.to_update:<8} | {self.previous_year_questions.unchanged:<10}",
            f"{'Practice Questions (AI)':<28} | {self.practice_questions.to_create:<8} | {self.practice_questions.to_update:<8} | {self.practice_questions.unchanged:<10}",
            f"{'Topic Study Notes':<28} | {self.study_notes.to_create:<8} | {self.study_notes.to_update:<8} | {self.study_notes.unchanged:<10}",
            "-" * 70,
        ]
        if self.warnings:
            lines.append("Warnings / Preservations:")
            for w in self.warnings:
                lines.append(f"  [!] {w}")
            lines.append("-" * 70)
        lines.append("=" * 70)
        return "\n".join(lines)


class IngestionPreviewGenerator:
    """Inspects database state against manifest and computes entity diffs."""

    @classmethod
    def generate(
        cls,
        manifest: CurriculumManifestSchema,
        subject: Subject,
        db: Session,
    ) -> PreviewReport:
        report = PreviewReport(
            subject_code=subject.code,
            subject_title=subject.name,
            board=subject.board,
            grade=subject.grade,
            current_status=subject.curriculum_status,
            proposed_status=manifest.curriculum_status,
            source_authority=manifest.source_provenance.source_authority,
            syllabus_version=manifest.source_provenance.syllabus_version,
        )

        # Existing chapters mapping
        existing_chapters = {
            c.chapter_number: c
            for c in db.query(Chapter).filter(Chapter.subject_id == subject.id).all()
        }

        # Check chapters and topics diff
        for ch_manifest in manifest.chapters:
            if ch_manifest.chapter_number not in existing_chapters:
                report.chapters.to_create += 1
                report.chapters.details.append(f"+ Chapter {ch_manifest.chapter_number}: {ch_manifest.title}")
                # All topics in new chapter are to_create
                for top_m in ch_manifest.topics:
                    report.topics.to_create += 1
                    report.learning_objectives.to_create += len(top_m.learning_objectives)
                    report.learning_resources.to_create += len(top_m.resources)
                    report.previous_year_questions.to_create += len(top_m.pyqs)
                    report.practice_questions.to_create += len(top_m.practice_questions)
                    if top_m.study_notes:
                        report.study_notes.to_create += 1
            else:
                existing_ch = existing_chapters[ch_manifest.chapter_number]
                if existing_ch.title != ch_manifest.title or existing_ch.description != ch_manifest.description:
                    report.chapters.to_update += 1
                else:
                    report.chapters.unchanged += 1

                # Check topics within this existing chapter
                existing_topics = {
                    t.topic_number: t
                    for t in db.query(Topic).filter(Topic.chapter_id == existing_ch.id).all()
                }

                for top_m in ch_manifest.topics:
                    if top_m.topic_number not in existing_topics:
                        report.topics.to_create += 1
                        report.learning_objectives.to_create += len(top_m.learning_objectives)
                        report.learning_resources.to_create += len(top_m.resources)
                        report.previous_year_questions.to_create += len(top_m.pyqs)
                        report.practice_questions.to_create += len(top_m.practice_questions)
                        if top_m.study_notes:
                            report.study_notes.to_create += 1
                    else:
                        existing_top = existing_topics[top_m.topic_number]
                        if (
                            existing_top.title != top_m.title
                            or existing_top.description != top_m.description
                            or existing_top.estimated_minutes != top_m.estimated_minutes
                        ):
                            report.topics.to_update += 1
                        else:
                            report.topics.unchanged += 1

                        # Diff Learning Objectives
                        existing_los = {
                            lo.code: lo
                            for lo in db.query(LearningObjective)
                            .filter(LearningObjective.topic_id == existing_top.id)
                            .all()
                        }
                        for lo_m in top_m.learning_objectives:
                            if lo_m.code not in existing_los:
                                report.learning_objectives.to_create += 1
                            else:
                                report.learning_objectives.unchanged += 1

                        # Diff Resources
                        existing_res = {
                            r.order_index: r
                            for r in db.query(LearningResource)
                            .filter(LearningResource.topic_id == existing_top.id)
                            .all()
                        }
                        for res_m in top_m.resources:
                            if res_m.order_index not in existing_res:
                                report.learning_resources.to_create += 1
                            else:
                                report.learning_resources.to_update += 1

                        # Diff PYQs for this topic
                        existing_pyqs = {
                            (p.paper_code, p.question_number): p
                            for p in db.query(PreviousYearQuestion)
                            .filter(PreviousYearQuestion.topic_id == existing_top.id)
                            .all()
                        }
                        for pyq_m in top_m.pyqs:
                            key = (pyq_m.paper_code, pyq_m.question_number)
                            if key not in existing_pyqs:
                                report.previous_year_questions.to_create += 1
                            else:
                                report.previous_year_questions.unchanged += 1

                        # Diff Practice Questions
                        existing_pqs = (
                            db.query(PracticeQuestion)
                            .filter(PracticeQuestion.topic_id == existing_top.id)
                            .count()
                        )
                        if existing_pqs == 0:
                            report.practice_questions.to_create += len(top_m.practice_questions)
                        else:
                            report.practice_questions.unchanged += len(top_m.practice_questions)

                        # Diff Study Notes
                        existing_notes = (
                            db.query(TopicStudyNotes)
                            .filter(TopicStudyNotes.topic_id == existing_top.id)
                            .first()
                        )
                        if top_m.study_notes:
                            if not existing_notes:
                                report.study_notes.to_create += 1
                            else:
                                report.study_notes.to_update += 1

        # Check Subject-level PYQs
        existing_subject_pyqs = {
            (p.paper_code, p.question_number): p
            for p in db.query(PreviousYearQuestion)
            .filter(
                PreviousYearQuestion.subject_id == subject.id,
                PreviousYearQuestion.topic_id.is_(None),
            )
            .all()
        }
        for spyq_m in manifest.subject_pyqs:
            key = (spyq_m.paper_code, spyq_m.question_number)
            if key not in existing_subject_pyqs:
                report.previous_year_questions.to_create += 1
            else:
                report.previous_year_questions.unchanged += 1

        # Check for safety on existing student progress
        all_existing_topics = (
            db.query(Topic)
            .join(Chapter, Topic.chapter_id == Chapter.id)
            .filter(Chapter.subject_id == subject.id)
            .all()
        )
        for et in all_existing_topics:
            progress_count = db.query(StudentProgress).filter(StudentProgress.topic_id == et.id).count()
            if progress_count > 0:
                report.warnings.append(
                    f"Topic {et.id} ('{et.title}') has {progress_count} active student progress records. "
                    f"Protected from deletion."
                )

        return report
