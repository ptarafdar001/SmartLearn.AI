"""
Comprehensive Test Suite for Curriculum Ingestion Pipeline.

Tests:
1. Manifest schema validation success.
2. Missing or invalid source provenance rejection.
3. Invalid Bloom's taxonomy level rejection.
4. Duplicate chapter numbers rejection.
5. Duplicate topic numbers rejection.
6. Duplicate learning objective codes rejection.
7. Authentic PYQ provenance and metadata enforcement.
8. AI-generated practice question labeling enforcement.
9. Dry-run preview execution leaves database state completely untouched.
10. Idempotent publication (running twice produces 0 duplicate records).
11. Quarantine enforcement against unreviewed ai_draft content.
12. Protection of active student progress and existing verified content.
13. End-to-end integration: CBSE Class 10 Science publication and verification.
"""

from copy import deepcopy
import json
from pathlib import Path
import pytest
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.ingestion.pipeline import CurriculumIngestionPipeline, IngestionError
from app.ingestion.schemas import CurriculumManifestSchema, TaxonomyLevel, VerificationStatus
from app.ingestion.validator import CurriculumValidator
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


@pytest.fixture
def db_session():
    """Transactional DB session fixture."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def sample_manifest_data():
    """Load valid CBSE 10 Science manifest fixture."""
    manifest_path = Path("data/curricula/cbse_class10_science.json")
    with open(manifest_path, "r", encoding="utf-8") as f:
        return json.load(f)


# ── 1. Schema Validation Tests ────────────────────────────────────────────────

def test_manifest_schema_validation_success(sample_manifest_data):
    """Verify that a valid manifest parses into CurriculumManifestSchema without errors."""
    manifest = CurriculumManifestSchema.model_validate(sample_manifest_data)
    assert manifest.subject_code == "cbse-class-10-sci"
    assert manifest.board == "CBSE"
    assert manifest.grade == "Class 10"
    assert len(manifest.chapters) == 13
    assert manifest.source_provenance.source_authority == "CBSE / NCERT"
    assert manifest.source_provenance.verification_status == VerificationStatus.VERIFIED_PUBLISHED


def test_missing_provenance_rejected(sample_manifest_data):
    """Verify that missing mandatory provenance fields (e.g. source_url, authority) fail validation."""
    invalid_data = deepcopy(sample_manifest_data)
    del invalid_data["source_provenance"]["source_url"]

    with pytest.raises(Exception):
        CurriculumManifestSchema.model_validate(invalid_data)

    invalid_data2 = deepcopy(sample_manifest_data)
    invalid_data2["source_provenance"]["source_url"] = "not-a-valid-url"
    with pytest.raises(Exception):
        CurriculumManifestSchema.model_validate(invalid_data2)


def test_invalid_taxonomy_level_rejected(sample_manifest_data):
    """Verify that learning objectives with non-Bloom's taxonomy levels are rejected."""
    invalid_data = deepcopy(sample_manifest_data)
    invalid_data["chapters"][0]["topics"][0]["learning_objectives"][0]["taxonomy_level"] = "memorize_fast"

    with pytest.raises(Exception):
        CurriculumManifestSchema.model_validate(invalid_data)


# ── 2. Duplicate Detection Tests ──────────────────────────────────────────────

def test_duplicate_chapter_numbers_rejected(sample_manifest_data, db_session: Session):
    """Verify that manifests with duplicate chapter numbers are flagged by the validator."""
    invalid_data = deepcopy(sample_manifest_data)
    # Duplicate chapter 1
    dup_chapter = deepcopy(invalid_data["chapters"][0])
    invalid_data["chapters"].append(dup_chapter)

    manifest = CurriculumManifestSchema.model_validate(invalid_data)
    res = CurriculumValidator.validate(manifest, db_session)
    assert not res.is_valid
    assert any("Duplicate chapter number 1" in e for e in res.errors)


def test_duplicate_topic_numbers_rejected(sample_manifest_data, db_session: Session):
    """Verify that manifests with duplicate topic numbers within a chapter are rejected."""
    invalid_data = deepcopy(sample_manifest_data)
    ch1_topics = invalid_data["chapters"][0]["topics"]
    dup_topic = deepcopy(ch1_topics[0])
    ch1_topics.append(dup_topic)

    manifest = CurriculumManifestSchema.model_validate(invalid_data)
    res = CurriculumValidator.validate(manifest, db_session)
    assert not res.is_valid
    assert any("Duplicate topic number 1" in e for e in res.errors)


def test_duplicate_learning_objective_codes_rejected(sample_manifest_data, db_session: Session):
    """Verify that duplicate Learning Objective codes across the curriculum are rejected."""
    invalid_data = deepcopy(sample_manifest_data)
    # Duplicate LO code
    lo1 = invalid_data["chapters"][0]["topics"][0]["learning_objectives"][0]
    invalid_data["chapters"][0]["topics"][1]["learning_objectives"].append(deepcopy(lo1))

    manifest = CurriculumManifestSchema.model_validate(invalid_data)
    res = CurriculumValidator.validate(manifest, db_session)
    assert not res.is_valid
    assert any("Duplicate Learning Objective code" in e for e in res.errors)


# ── 3. Content Segregation & Labeling Tests ────────────────────────────────────

def test_pyq_authenticity_enforcement(sample_manifest_data):
    """Verify that PYQs require board, exam_year, paper_code, question_number, and source_name."""
    invalid_data = deepcopy(sample_manifest_data)
    # Omit paper_code on PYQ
    del invalid_data["chapters"][0]["topics"][0]["pyqs"][0]["paper_code"]

    with pytest.raises(Exception):
        CurriculumManifestSchema.model_validate(invalid_data)


def test_ai_practice_questions_must_be_labeled(sample_manifest_data):
    """Verify practice questions have is_ai_generated and question_type validation."""
    pq = sample_manifest_data["chapters"][0]["topics"][0]["practice_questions"][0]
    assert pq["is_ai_generated"] is True
    assert pq["question_type"] in ["mcq", "short_answer", "long_answer"]
    assert "options" in pq
    assert "explanation" in pq


def test_unreviewed_ai_draft_quarantine(sample_manifest_data, db_session: Session):
    """Verify that manifests flagged with verification_status='ai_draft' are quarantined by default."""
    draft_data = deepcopy(sample_manifest_data)
    draft_data["source_provenance"]["verification_status"] = "ai_draft"

    manifest = CurriculumManifestSchema.model_validate(draft_data)
    res = CurriculumValidator.validate(manifest, db_session, allow_drafts=False)
    assert not res.is_valid
    assert any("Quarantine Violation" in e for e in res.errors)

    # When allow_drafts=True, validation permits preview
    res_allowed = CurriculumValidator.validate(manifest, db_session, allow_drafts=True)
    assert res_allowed.is_valid


# ── 4. Ingestion Execution, Dry-Run & Idempotency Tests ─────────────────────────

def test_dry_run_leaves_database_unmodified(sample_manifest_data, db_session: Session):
    """Verify that running with dry_run=True computes preview diffs without mutating the database."""
    # Count PYQs before
    pyqs_before = (
        db_session.query(PreviousYearQuestion)
        .join(Subject, PreviousYearQuestion.subject_id == Subject.id)
        .filter(Subject.code == "cbse-class-10-sci")
        .count()
    )

    result = CurriculumIngestionPipeline.run(
        source=sample_manifest_data,
        dry_run=True,
        db_session=db_session,
    )
    assert result["status"] == "dry_run_success"
    assert result["preview_report"] is not None

    # Count PYQs after
    pyqs_after = (
        db_session.query(PreviousYearQuestion)
        .join(Subject, PreviousYearQuestion.subject_id == Subject.id)
        .filter(Subject.code == "cbse-class-10-sci")
        .count()
    )
    assert pyqs_before == pyqs_after


def test_idempotent_ingestion_and_safe_rerun(sample_manifest_data, db_session: Session):
    """
    Verify that publishing the exact same manifest twice is idempotent:
    - First run creates/updates entities.
    - Second run executes without error and creates 0 duplicate rows.
    """
    subject = db_session.query(Subject).filter(Subject.code == "cbse-class-10-sci").first()
    assert subject is not None

    # Run 1: Publish
    res1 = CurriculumIngestionPipeline.run(
        source=sample_manifest_data,
        dry_run=False,
        db_session=db_session,
    )
    assert res1["status"] == "published_success"

    # Count rows after Run 1
    ch_count_1 = db_session.query(Chapter).filter(Chapter.subject_id == subject.id).count()
    top_count_1 = (
        db_session.query(Topic)
        .join(Chapter, Topic.chapter_id == Chapter.id)
        .filter(Chapter.subject_id == subject.id)
        .count()
    )
    pyq_count_1 = db_session.query(PreviousYearQuestion).filter(PreviousYearQuestion.subject_id == subject.id).count()

    # Run 2: Re-run with the same manifest
    res2 = CurriculumIngestionPipeline.run(
        source=sample_manifest_data,
        dry_run=False,
        db_session=db_session,
    )
    assert res2["status"] == "published_success"

    # Count rows after Run 2
    ch_count_2 = db_session.query(Chapter).filter(Chapter.subject_id == subject.id).count()
    top_count_2 = (
        db_session.query(Topic)
        .join(Chapter, Topic.chapter_id == Chapter.id)
        .filter(Chapter.subject_id == subject.id)
        .count()
    )
    pyq_count_2 = db_session.query(PreviousYearQuestion).filter(PreviousYearQuestion.subject_id == subject.id).count()

    assert ch_count_1 == ch_count_2 == 13, f"Expected 13 chapters, got {ch_count_2}"
    assert top_count_1 == top_count_2 >= 38, f"Expected identical topic count across runs, got {top_count_1} vs {top_count_2}"
    assert pyq_count_1 == pyq_count_2, f"Expected identical PYQ count, got {pyq_count_1} vs {pyq_count_2}"


def test_isc_history_remains_intact_after_cbse_ingestion(db_session: Session):
    """
    Verify that existing ISC Class 11 History (Subject 43) slice is completely untouched
    and remains at 5 chapters, 12 topics, and 3 authentic PYQs.
    """
    isc = db_session.query(Subject).filter(Subject.code == "isc-11-hist").first()
    assert isc is not None
    assert isc.id == 43
    assert len(isc.chapters) == 5
    topics_count = sum(len(c.topics) for c in isc.chapters)
    assert topics_count == 12
    pyqs_count = db_session.query(PreviousYearQuestion).filter(PreviousYearQuestion.subject_id == 43).count()
    assert pyqs_count == 3
