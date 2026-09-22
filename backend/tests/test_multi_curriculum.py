"""
Comprehensive Test Suite for Batch 1 Multi-Board, Multi-Subject Curriculum Architecture.

Verifies:
1. Existing ISC Class 11 History data (ID 43) remains 100% intact.
2. Canonical resolution for multiple boards (CBSE, ICSE, ISC, State Board).
3. Authoritative exemplar syllabi (CBSE 10 Science, CBSE 10 Math, CBSE 12 Physics, ICSE 10 HCG).
4. Duplicate / repeated seeding idempotency without duplication.
5. Registered unpopulated subjects return honest 'in_preparation' empty states (HTTP 200, chapters=[]), no 404, no fake content.
6. Student onboarding selections map correctly to canonical subjects.
7. Alembic migration upgrade and downgrade safety.
"""

import subprocess
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.seed_curriculum import seed_curriculum, seed_isc_history_curriculum
from app.db.session import SessionLocal
from app.main import app
from app.models.learning import Chapter, LearningObjective, LearningResource, PreviousYearQuestion, Subject, Topic
from app.models.onboarding import StudentProfile, SubjectSelection
from app.models.users import User
from app.services.learning_service import LearningService


@pytest.fixture(scope="module")
def client():
    """FastAPI TestClient fixture."""
    return TestClient(app)


@pytest.fixture
def db_session():
    """Transactional database test session."""
    session = SessionLocal()
    try:
        seed_curriculum(session)
        yield session
    finally:
        session.rollback()
        session.close()


def test_existing_isc_history_data_remains_intact(db_session: Session):
    """
    CRITICAL: Verify that the existing CISCE ISC Class 11 History slice (ID=43)
    is completely preserved with all 5 chapters, 12 topics, 22 resources, and 3 PYQs.
    """
    subject = db_session.query(Subject).filter(Subject.code == "isc-11-hist").first()
    assert subject is not None, "ISC Class 11 History subject not found"
    assert subject.id == 43, f"Expected subject ID 43, got {subject.id}"
    assert subject.name == "History"
    assert subject.board == "ISC"
    assert subject.grade == "Class 11"
    assert subject.academic_stream == "Humanities / Arts"
    assert subject.curriculum_status == "content_available"
    assert subject.source_authority == "CISCE"
    assert subject.syllabus_version == "Examination Year 2027"

    # Verify chapters (1, 2, 3, 4, 7)
    chapters = (
        db_session.query(Chapter)
        .filter(Chapter.subject_id == subject.id)
        .order_by(Chapter.chapter_number)
        .all()
    )
    assert len(chapters) == 5, f"Expected 5 chapters for ISC History, got {len(chapters)}"
    ch_nums = [c.chapter_number for c in chapters]
    assert ch_nums == [1, 2, 3, 4, 7], f"Expected chapter numbers [1, 2, 3, 4, 7], got {ch_nums}"

    # Verify topics count
    ch_ids = [c.id for c in chapters]
    topics = db_session.query(Topic).filter(Topic.chapter_id.in_(ch_ids)).all()
    assert len(topics) == 12, f"Expected 12 topics for ISC History, got {len(topics)}"

    # Verify learning resources
    t_ids = [t.id for t in topics]
    resources = db_session.query(LearningResource).filter(LearningResource.topic_id.in_(t_ids)).all()
    assert len(resources) == 22, f"Expected 22 learning resources, got {len(resources)}"

    # Verify authentic PYQs
    pyqs = db_session.query(PreviousYearQuestion).filter(PreviousYearQuestion.subject_id == subject.id).all()
    assert len(pyqs) == 3, f"Expected 3 PYQs, got {len(pyqs)}"
    for pyq in pyqs:
        assert pyq.paper_code.startswith("ISC-")
        assert pyq.is_verified is True


def test_multiple_boards_classes_subjects_resolve_correctly(db_session: Session):
    """
    Verify authoritative exemplar subjects across multiple boards and grades resolve
    with their verified syllabus hierarchies:
    - CBSE Class 10 Science: 13 official NCERT chapters + verified learning objectives
    - CBSE Class 10 Math Standard: 14 official NCERT chapters
    - CBSE Class 12 Physics: 14 official NCERT chapters
    - ICSE Class 10 HCG: 12 official CISCE chapters
    """
    # 1. CBSE Class 10 Science
    cbse_sci = (
        db_session.query(Subject)
        .filter(Subject.board == "CBSE", Subject.grade == "Class 10", Subject.name == "Science")
        .first()
    )
    assert cbse_sci is not None
    assert cbse_sci.curriculum_status == "content_available"
    assert cbse_sci.source_authority == "CBSE / NCERT"
    sci_detail = LearningService.get_subject_detail(db_session, user_id=1, subject_id=cbse_sci.id)
    assert sci_detail.total_chapters == 13, f"Expected 13 chapters for CBSE 10 Science, got {sci_detail.total_chapters}"
    assert sci_detail.chapters[0].title == "Chemical Reactions and Equations"
    assert sci_detail.chapters[12].title == "Our Environment"

    # Verify CBSE 10 Science verified learning objectives
    ch1 = (
        db_session.query(Chapter)
        .filter(Chapter.subject_id == cbse_sci.id, Chapter.chapter_number == 1)
        .first()
    )
    t1 = db_session.query(Topic).filter(Topic.chapter_id == ch1.id, Topic.topic_number == 1).first()
    objs = db_session.query(LearningObjective).filter(LearningObjective.topic_id == t1.id).all()
    assert len(objs) == 2
    lo_codes = {o.code for o in objs}
    assert "CBSE10-SCI-CH01-LO01" in lo_codes
    assert "CBSE10-SCI-CH01-LO02" in lo_codes

    # 2. CBSE Class 10 Math Standard
    cbse_math = (
        db_session.query(Subject)
        .filter(
            Subject.board == "CBSE",
            Subject.grade == "Class 10",
            Subject.name == "Mathematics Standard",
        )
        .first()
    )
    assert cbse_math is not None
    math_detail = LearningService.get_subject_detail(db_session, user_id=1, subject_id=cbse_math.id)
    assert math_detail.total_chapters == 14, f"Expected 14 chapters for CBSE 10 Math, got {math_detail.total_chapters}"
    assert math_detail.chapters[0].title == "Real Numbers"
    assert math_detail.chapters[13].title == "Probability"

    # 3. CBSE Class 12 Physics
    cbse_phy = (
        db_session.query(Subject)
        .filter(
            Subject.board == "CBSE",
            Subject.grade == "Class 12",
            Subject.academic_stream == "Science",
            Subject.name == "Physics",
        )
        .first()
    )
    assert cbse_phy is not None
    phy_detail = LearningService.get_subject_detail(db_session, user_id=1, subject_id=cbse_phy.id)
    assert phy_detail.total_chapters == 14, f"Expected 14 chapters for CBSE 12 Physics, got {phy_detail.total_chapters}"
    assert phy_detail.chapters[0].title == "Electric Charges and Fields"

    # 4. ICSE Class 10 History, Civics and Geography
    icse_hcg = (
        db_session.query(Subject)
        .filter(
            Subject.board == "ICSE",
            Subject.grade == "Class 10",
            Subject.name == "History, Civics and Geography",
        )
        .first()
    )
    assert icse_hcg is not None
    hcg_detail = LearningService.get_subject_detail(db_session, user_id=1, subject_id=icse_hcg.id)
    assert hcg_detail.total_chapters == 12, f"Expected 12 chapters for ICSE 10 HCG, got {hcg_detail.total_chapters}"
    assert hcg_detail.chapters[0].title == "The Union Parliament"


def test_empty_curricula_return_honest_empty_states(db_session: Session):
    """
    CRITICAL: A registered unpopulated subject must return an honest in-preparation response:
    - HTTP 200 equivalent (no 404, no ValueError)
    - total_chapters == 0
    - chapters == []
    - curriculum_status == 'in_preparation'
    - status_message explicitly explaining compilation status
    - Never fabricates fake chapters or placeholder items!
    """
    # Pick a registered unpopulated subject (e.g. CBSE Class 7 Mathematics)
    unseeded_subject = (
        db_session.query(Subject)
        .filter(
            Subject.board == "CBSE",
            Subject.grade == "Class 7",
            Subject.name == "Mathematics",
        )
        .first()
    )
    assert unseeded_subject is not None
    assert unseeded_subject.curriculum_status == "in_preparation"

    # Call get_subject_detail
    detail = LearningService.get_subject_detail(db_session, user_id=1, subject_id=unseeded_subject.id)
    assert detail.id == unseeded_subject.id
    assert detail.name == "Mathematics"
    assert detail.board == "CBSE"
    assert detail.grade == "Class 7"
    assert detail.total_chapters == 0
    assert detail.total_topics == 0
    assert detail.completed_topics == 0
    assert detail.progress_percentage == 0.0
    assert detail.curriculum_status == "in_preparation"
    assert detail.chapters == []
    assert detail.status_message is not None
    assert "Curriculum framework registered" in detail.status_message
    assert "actively being curated" in detail.status_message


def test_duplicate_seeding_is_safe_and_idempotent(db_session: Session):
    """
    Verify that executing seed_curriculum multiple times does not create duplicate
    subjects, duplicate chapters, duplicate topics, or orphan records.
    """
    initial_subjects = db_session.query(Subject).count()
    initial_chapters = db_session.query(Chapter).count()
    initial_topics = db_session.query(Topic).count()
    initial_resources = db_session.query(LearningResource).count()

    # Re-run the seed script
    seed_curriculum(db_session)

    assert db_session.query(Subject).count() == initial_subjects
    assert db_session.query(Chapter).count() == initial_chapters
    assert db_session.query(Topic).count() == initial_topics
    assert db_session.query(LearningResource).count() == initial_resources


def test_student_selections_map_to_canonical_subjects(db_session: Session):
    """
    Verify that when a student completes onboarding selections (e.g. CBSE Class 10 Science + Math),
    LearningService.get_enrolled_subjects maps those selections directly to canonical Subject records
    with full metadata, correct IDs, and active curriculum status.
    """
    # Create test user
    test_user = User(
        email="cbse_student_test@example.com",
        full_name="CBSE Test Student",
        hashed_password="hashed_pw_test",
        is_active=True,
    )
    db_session.add(test_user)
    db_session.flush()

    # Create profile
    profile = StudentProfile(
        user_id=test_user.id,
        board="CBSE",
        grade="Class 10",
        academic_stream=None,
    )
    db_session.add(profile)

    # Create selections for Science and Mathematics Standard
    sel1 = SubjectSelection(user_id=test_user.id, subject_name="Science")
    sel2 = SubjectSelection(user_id=test_user.id, subject_name="Mathematics Standard")
    db_session.add_all([sel1, sel2])
    db_session.flush()

    # Query enrolled subjects
    enrolled = LearningService.get_enrolled_subjects(db_session, user_id=test_user.id)
    assert len(enrolled) == 2

    enrolled_names = {s.name for s in enrolled}
    assert "Science" in enrolled_names
    assert "Mathematics Standard" in enrolled_names

    for s in enrolled:
        assert s.board == "CBSE"
        assert s.grade == "Class 10"
        if s.name == "Science":
            assert s.total_chapters == 13
            assert s.curriculum_status in ("content_available", "curriculum_verified")
            assert s.source_authority == "CBSE / NCERT"
        elif s.name == "Mathematics Standard":
            assert s.total_chapters == 14
            assert s.curriculum_status in ("curriculum_verified", "content_available")
            assert s.source_authority == "CBSE / NCERT"


def test_alembic_migrations_upgrade_and_downgrade_safely():
    """
    Verify Alembic migration c1a2e3f4b5d6 upgrades and downgrades without DDL errors.
    """
    import os
    from alembic.config import Config
    from alembic import command

    alembic_ini_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "alembic.ini"))
    alembic_cfg = Config(alembic_ini_path)

    # Downgrade 1 revision (reverts c1a2e3f4b5d6)
    command.downgrade(alembic_cfg, "-1")

    # Upgrade back to head (re-applies c1a2e3f4b5d6)
    command.upgrade(alembic_cfg, "head")
