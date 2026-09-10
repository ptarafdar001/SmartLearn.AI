"""
Unit tests for SmartLearn.AI Learning Database Foundation Models (Issue #13).
Verifies:
- Subject -> Chapter -> Topic -> LearningResource canonical hierarchy
- User -> StudentProgress -> Topic learning telemetry
- Multi-modal resource types and provenance metadata (YouTube external_id, NCERT, etc.)
- Unique constraints and cascade deletion semantics
"""

from datetime import datetime, timezone
import pytest
from sqlalchemy.exc import IntegrityError

from app.db.session import SessionLocal
from app.models.learning import (
    Chapter,
    LearningResource,
    StudentProgress,
    Subject,
    Topic,
)
from app.models.users import User


@pytest.fixture
def db():
    """Provide an isolated database session rolled back after each test."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


def create_test_user(db, email: str = "learning_test_student@example.com") -> User:
    """Helper to create or get an isolated test student account."""
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        db.delete(existing)
        db.commit()

    user = User(
        email=email,
        hashed_password="test_hashed_password_123",
        full_name="Learning Test Student",
        role="student",
        is_active=True,
        is_onboarded=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def cleanup_subject(db, code: str):
    """Helper to cleanly delete a test subject and its cascade children."""
    existing = db.query(Subject).filter(Subject.code == code).first()
    if existing:
        db.delete(existing)
        db.commit()


def test_subject_chapter_topic_hierarchy(db):
    """Verify Subject -> Chapter -> Topic hierarchy and bidirectional navigation."""
    subject_code = "test-cbse-10-math-041"
    cleanup_subject(db, subject_code)

    try:
        subject = Subject(
            code=subject_code,
            name="Mathematics Standard",
            board="CBSE",
            grade="Class 10",
            academic_stream=None,
            category="core",
            description="Core Class 10 CBSE Mathematics syllabus",
            display_order=1,
            is_active=True,
        )
        db.add(subject)
        db.flush()

        assert subject.id is not None
        assert subject.created_at is not None

        chapter = Chapter(
            subject_id=subject.id,
            chapter_number=1,
            title="Real Numbers",
            description="Euclid's division lemma and fundamental theorem of arithmetic",
        )
        db.add(chapter)
        db.flush()

        assert chapter.id is not None
        assert chapter.subject.name == "Mathematics Standard"

        topic1 = Topic(
            chapter_id=chapter.id,
            topic_number=1,
            title="Fundamental Theorem of Arithmetic",
            description="Prime factorisation and applications",
            estimated_minutes=20,
        )
        topic2 = Topic(
            chapter_id=chapter.id,
            topic_number=2,
            title="Revisiting Irrational Numbers",
            description="Proofs of irrationality",
            estimated_minutes=15,
        )
        db.add_all([topic1, topic2])
        db.commit()

        # Verify query and ordering
        retrieved_subject = db.query(Subject).filter(Subject.id == subject.id).first()
        assert len(retrieved_subject.chapters) == 1
        assert retrieved_subject.chapters[0].title == "Real Numbers"
        assert len(retrieved_subject.chapters[0].topics) == 2
        assert retrieved_subject.chapters[0].topics[0].topic_number == 1
        assert retrieved_subject.chapters[0].topics[1].topic_number == 2
    finally:
        cleanup_subject(db, subject_code)


def test_learning_resource_modalities_and_provenance(db):
    """
    Verify LearningResource supports all 8 modalities and 6 providers,
    including YouTube external_id storage without media downloads, and provenance metadata.
    """
    subject_code = "test-cbse-10-sci-086"
    cleanup_subject(db, subject_code)

    try:
        subject = Subject(
            code=subject_code,
            name="Science",
            board="CBSE",
            grade="Class 10",
            category="core",
        )
        db.add(subject)
        db.flush()

        chapter = Chapter(subject_id=subject.id, chapter_number=1, title="Chemical Reactions")
        db.add(chapter)
        db.flush()

        topic = Topic(chapter_id=chapter.id, topic_number=1, title="Balancing Chemical Equations")
        db.add(topic)
        db.flush()

        now = datetime.now(timezone.utc)

        # 1. Text / Theory Lesson (SmartLearn native)
        res_text = LearningResource(
            topic_id=topic.id,
            title="Balancing Chemical Equations: Step-by-Step Guide",
            resource_type="text",
            provider="smartlearn",
            text_content="# Balancing Equations\nStep 1: Count atom numbers on LHS and RHS...",
            order_index=1,
            is_active=True,
            is_verified=True,
            verified_at=now,
        )

        # 2. Video Resource (YouTube metadata / embed ID - no video download)
        res_video = LearningResource(
            topic_id=topic.id,
            title="Visual Demonstration: Law of Conservation of Mass",
            resource_type="video",
            provider="youtube",
            source_name="NCERT Official Channel",
            source_url="https://youtube.com/watch?v=mockVideoId123",
            external_id="mockVideoId123",
            content_url="https://www.youtube-nocookie.com/embed/mockVideoId123",
            duration_seconds=480,
            order_index=2,
            is_active=True,
            is_verified=True,
            verified_at=now,
        )

        # 3. Audio Recap (NCERT Podcast / Audio)
        res_audio = LearningResource(
            topic_id=topic.id,
            title="Audio Recap: Chemical Reactions in Everyday Life",
            resource_type="audio",
            provider="ncert",
            source_name="CIET NCERT",
            source_url="https://ciet.nic.in/audio/chem_10_01.mp3",
            duration_seconds=300,
            order_index=3,
        )

        # 4. Notes / Cheat-sheet
        res_notes = LearningResource(
            topic_id=topic.id,
            title="Formula Cheat-Sheet & Common Reaction Types",
            resource_type="notes",
            provider="smartlearn",
            text_content="- Synthesis: A + B -> AB\n- Decomposition: AB -> A + B",
            order_index=4,
        )

        # 5. Quiz Resource
        res_quiz = LearningResource(
            topic_id=topic.id,
            title="5-Question Concept Check: Balancing Equations",
            resource_type="quiz",
            provider="smartlearn",
            order_index=5,
        )

        # 6. Practice Questions
        res_practice = LearningResource(
            topic_id=topic.id,
            title="Board Exam Practice Problems (2020-2025)",
            resource_type="practice",
            provider="cisce",
            source_name="Exemplar Bank",
            order_index=6,
        )

        # 7. Interactive Simulation
        res_interactive = LearningResource(
            topic_id=topic.id,
            title="Interactive Equation Balancer",
            resource_type="interactive",
            provider="diksha",
            source_name="DIKSHA Open Assets",
            content_url="https://diksha.gov.in/play/content/do_123",
            order_index=7,
        )

        # 8. Revision Flashcards
        res_revision = LearningResource(
            topic_id=topic.id,
            title="Rapid Revision Flashcards",
            resource_type="revision",
            provider="other",
            source_name="Open Educator",
            order_index=8,
        )

        db.add_all([
            res_text,
            res_video,
            res_audio,
            res_notes,
            res_quiz,
            res_practice,
            res_interactive,
            res_revision,
        ])
        db.commit()

        # Query and verify
        resources = (
            db.query(LearningResource)
            .filter(LearningResource.topic_id == topic.id)
            .order_by(LearningResource.order_index)
            .all()
        )
        assert len(resources) == 8

        # Verify YouTube metadata
        yt_res = next(r for r in resources if r.provider == "youtube")
        assert yt_res.resource_type == "video"
        assert yt_res.external_id == "mockVideoId123"
        assert yt_res.duration_seconds == 480
        assert yt_res.is_verified is True
        assert yt_res.source_name == "NCERT Official Channel"

        # Verify all 8 distinct modalities were stored and retrieved
        modalities = {r.resource_type for r in resources}
        assert modalities == {
            "text",
            "video",
            "audio",
            "notes",
            "quiz",
            "practice",
            "interactive",
            "revision",
        }
    finally:
        cleanup_subject(db, subject_code)


def test_student_progress_lifecycle(db):
    """Verify StudentProgress states, progress percentage, time tracking, and User relationship."""
    user = create_test_user(db, "progress_test_student@example.com")
    subject_code = "test-cbse-10-eng-184"
    cleanup_subject(db, subject_code)

    try:
        subject = Subject(
            code=subject_code,
            name="English Language & Literature",
            board="CBSE",
            grade="Class 10",
        )
        db.add(subject)
        db.flush()

        chapter = Chapter(subject_id=subject.id, chapter_number=1, title="A Letter to God")
        db.add(chapter)
        db.flush()

        topic = Topic(chapter_id=chapter.id, topic_number=1, title="Lencho's Faith")
        db.add(topic)
        db.flush()

        # 1. Initial creation (not_started)
        progress = StudentProgress(
            user_id=user.id,
            topic_id=topic.id,
            status="not_started",
            progress_percentage=0.0,
            time_spent_seconds=0,
        )
        db.add(progress)
        db.commit()

        assert progress.id is not None
        assert progress.status == "not_started"
        assert progress.progress_percentage == 0.0
        assert progress.completed_at is None

        # 2. Update to in_progress
        progress.status = "in_progress"
        progress.progress_percentage = 50.0
        progress.time_spent_seconds = 300
        db.commit()
        db.refresh(progress)
        assert progress.status == "in_progress"
        assert progress.progress_percentage == 50.0
        assert progress.time_spent_seconds == 300

        # 3. Complete topic
        now = datetime.now(timezone.utc)
        progress.status = "completed"
        progress.progress_percentage = 100.0
        progress.time_spent_seconds = 600
        progress.completed_at = now
        db.commit()
        db.refresh(progress)

        assert progress.status == "completed"
        assert progress.progress_percentage == 100.0
        assert progress.completed_at is not None

        # Verify User relationship navigation
        retrieved_user = db.query(User).filter(User.id == user.id).first()
        assert len(retrieved_user.student_progress_records) == 1
        assert retrieved_user.student_progress_records[0].topic_id == topic.id
    finally:
        cleanup_subject(db, subject_code)
        db.delete(user)
        db.commit()


def test_unique_constraints(db):
    """Verify unique constraints on Subject.code, (subject_id, chapter_number), (chapter_id, topic_number), and (user_id, topic_id)."""
    user = create_test_user(db, "unique_constraint_test@example.com")
    subject_code = "test-unique-code"
    cleanup_subject(db, subject_code)

    try:
        subj1 = Subject(code=subject_code, name="Subject A", board="CBSE", grade="Class 10")
        db.add(subj1)
        db.commit()

        # 1. Duplicate Subject.code
        subj2 = Subject(code=subject_code, name="Subject B", board="CBSE", grade="Class 10")
        db.add(subj2)
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()

        # 2. Duplicate (subject_id, chapter_number)
        subj = db.query(Subject).filter(Subject.code == subject_code).first()
        ch1 = Chapter(subject_id=subj.id, chapter_number=1, title="Chapter 1")
        db.add(ch1)
        db.commit()

        ch2 = Chapter(subject_id=subj.id, chapter_number=1, title="Duplicate Chapter 1")
        db.add(ch2)
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()

        # 3. Duplicate (chapter_id, topic_number)
        ch = db.query(Chapter).filter(Chapter.subject_id == subj.id, Chapter.chapter_number == 1).first()
        t1 = Topic(chapter_id=ch.id, topic_number=1, title="Topic 1")
        db.add(t1)
        db.commit()

        t2 = Topic(chapter_id=ch.id, topic_number=1, title="Duplicate Topic 1")
        db.add(t2)
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()

        # 4. Duplicate (user_id, topic_id) on StudentProgress
        t = db.query(Topic).filter(Topic.chapter_id == ch.id, Topic.topic_number == 1).first()
        p1 = StudentProgress(user_id=user.id, topic_id=t.id, status="in_progress", progress_percentage=25.0)
        db.add(p1)
        db.commit()

        p2 = StudentProgress(user_id=user.id, topic_id=t.id, status="completed", progress_percentage=100.0)
        db.add(p2)
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()
    finally:
        cleanup_subject(db, subject_code)
        db.delete(user)
        db.commit()


def test_cascade_deletion(db):
    """Verify cascade deletion from Subject -> Chapter -> Topic -> LearningResource & StudentProgress."""
    user = create_test_user(db, "cascade_test_student@example.com")
    subject_code = "test-cascade-subject"
    cleanup_subject(db, subject_code)

    try:
        subj = Subject(code=subject_code, name="Cascade Subj", board="CBSE", grade="Class 10")
        db.add(subj)
        db.flush()

        ch = Chapter(subject_id=subj.id, chapter_number=1, title="Cascade Chapter")
        db.add(ch)
        db.flush()

        t = Topic(chapter_id=ch.id, topic_number=1, title="Cascade Topic")
        db.add(t)
        db.flush()

        res = LearningResource(topic_id=t.id, title="Cascade Resource", resource_type="text")
        prog = StudentProgress(user_id=user.id, topic_id=t.id, status="completed", progress_percentage=100.0)
        db.add_all([res, prog])
        db.commit()

        subj_id = subj.id
        ch_id = ch.id
        t_id = t.id
        res_id = res.id
        prog_id = prog.id

        # Delete the Subject
        db.delete(subj)
        db.commit()

        # Verify everything cascaded
        assert db.query(Subject).filter(Subject.id == subj_id).first() is None
        assert db.query(Chapter).filter(Chapter.id == ch_id).first() is None
        assert db.query(Topic).filter(Topic.id == t_id).first() is None
        assert db.query(LearningResource).filter(LearningResource.id == res_id).first() is None
        assert db.query(StudentProgress).filter(StudentProgress.id == prog_id).first() is None

        # User remains intact
        assert db.query(User).filter(User.id == user.id).first() is not None
    finally:
        cleanup_subject(db, subject_code)
        db.delete(user)
        db.commit()
