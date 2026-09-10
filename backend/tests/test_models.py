import pytest
from sqlalchemy.exc import IntegrityError
from app.db.session import SessionLocal
from app.models.users import User
from app.models.onboarding import (
    StudentProfile,
    SubjectSelection,
    LearningPreference,
    StudyGoal,
    StudySchedule,
)


@pytest.fixture
def db_session():
    """Provide a transactional database session for tests and roll back changes."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


def test_create_user_and_relationships(db_session):
    """Verify creating a user and associated onboarding models in PostgreSQL."""
    test_email = "test_student_phase2@example.com"
    # Clean up if exists from previous run
    existing = db_session.query(User).filter(User.email == test_email).first()
    if existing:
        db_session.delete(existing)
        db_session.commit()

    user = User(
        email=test_email,
        hashed_password="hashed_secret_placeholder",
        full_name="Phase2 Test Student",
        role="student",
        is_active=True,
        is_onboarded=False,
    )
    db_session.add(user)
    db_session.flush()

    assert user.id is not None
    assert user.created_at is not None

    # Step 1: StudentProfile
    profile = StudentProfile(
        user_id=user.id,
        board="CBSE",
        grade="Class 12",
        academic_stream="Science",
    )
    db_session.add(profile)

    # Step 2: SubjectSelection
    sub1 = SubjectSelection(user_id=user.id, subject_name="Physics")
    sub2 = SubjectSelection(user_id=user.id, subject_name="Mathematics")
    db_session.add_all([sub1, sub2])

    # Step 3: LearningPreference and StudyGoal
    pref = LearningPreference(user_id=user.id, preferred_style="Visual")
    goal = StudyGoal(
        user_id=user.id,
        goal_text="Score 95% in Board Exams",
        target_score="95%",
        target_exam="CBSE Board",
    )
    db_session.add_all([pref, goal])

    # Step 4: StudySchedule
    sched = StudySchedule(
        user_id=user.id,
        daily_target_hours=3.5,
        preferred_slot="evening",
        available_days=["Monday", "Wednesday", "Friday"],
    )
    db_session.add(sched)
    db_session.commit()

    # Re-query and verify relationships
    retrieved = db_session.query(User).filter(User.id == user.id).first()
    assert retrieved is not None
    assert retrieved.student_profile is not None
    assert retrieved.student_profile.board == "CBSE"
    assert len(retrieved.subject_selections) == 2
    assert [s.subject_name for s in retrieved.subject_selections] == ["Physics", "Mathematics"]
    assert retrieved.learning_preference.preferred_style == "Visual"
    assert retrieved.study_goals[0].goal_text == "Score 95% in Board Exams"
    assert retrieved.study_schedule.daily_target_hours == 3.5
    assert "Monday" in retrieved.study_schedule.available_days

    # Test cascade delete
    db_session.delete(retrieved)
    db_session.commit()

    assert db_session.query(StudentProfile).filter(StudentProfile.user_id == user.id).first() is None
    assert db_session.query(SubjectSelection).filter(SubjectSelection.user_id == user.id).count() == 0
    assert db_session.query(LearningPreference).filter(LearningPreference.user_id == user.id).first() is None
    assert db_session.query(StudyGoal).filter(StudyGoal.user_id == user.id).count() == 0
    assert db_session.query(StudySchedule).filter(StudySchedule.user_id == user.id).first() is None


def test_unique_email_constraint(db_session):
    """Verify unique constraint on user email raises IntegrityError."""
    u1 = User(
        email="duplicate_check@example.com",
        hashed_password="hash",
        full_name="User One",
    )
    db_session.add(u1)
    db_session.commit()

    u2 = User(
        email="duplicate_check@example.com",
        hashed_password="hash2",
        full_name="User Two",
    )
    db_session.add(u2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

    # Cleanup
    db_session.delete(u1)
    db_session.commit()
