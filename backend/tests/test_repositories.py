from datetime import timedelta
import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.security import create_access_token, get_password_hash
from app.db.session import SessionLocal
from app.models.users import User
from app.repositories.onboarding_repository import OnboardingRepository
from app.repositories.user_repository import UserRepository


@pytest.fixture
def db_session():
    """Transactional test session."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


# ── User Repository Tests ─────────────────────────────────────────────────────
def test_user_repository_crud(db_session: Session):
    test_email = "repo_test_user@example.com"
    # Cleanup if exists
    existing = UserRepository.get_by_email(db_session, test_email)
    if existing:
        UserRepository.delete(db_session, existing.id)

    hashed = get_password_hash("Password123!")
    user = UserRepository.create(
        db_session,
        email=test_email,
        hashed_password=hashed,
        full_name="Repository Tester",
        role="student",
    )

    assert user.id is not None
    assert user.email == test_email
    assert user.is_onboarded is False

    # Get by ID
    by_id = UserRepository.get_by_id(db_session, user.id)
    assert by_id is not None
    assert by_id.id == user.id

    # Get by Email (case-insensitive)
    by_email = UserRepository.get_by_email(db_session, "REPO_TEST_USER@EXAMPLE.COM")
    assert by_email is not None
    assert by_email.id == user.id

    # Update onboarding status
    updated = UserRepository.update_onboarding_status(db_session, user.id, is_onboarded=True)
    assert updated.is_onboarded is True

    # Delete
    deleted = UserRepository.delete(db_session, user.id)
    assert deleted is True
    assert UserRepository.get_by_id(db_session, user.id) is None


# ── Onboarding Repository & User Isolation Tests ──────────────────────────────
def test_onboarding_repository_and_user_isolation(db_session: Session):
    # Pre-test cleanup for deterministic isolation
    for email in ["isolation_user_a@example.com", "isolation_user_b@example.com"]:
        existing = UserRepository.get_by_email(db_session, email)
        if existing:
            UserRepository.delete(db_session, existing.id)

    # Create User A and User B
    user_a = UserRepository.create(
        db_session,
        email="isolation_user_a@example.com",
        hashed_password=get_password_hash("PassA123!"),
        full_name="Student Alpha",
    )
    user_b = UserRepository.create(
        db_session,
        email="isolation_user_b@example.com",
        hashed_password=get_password_hash("PassB123!"),
        full_name="Student Beta",
    )

    # Step 1: Profiles
    OnboardingRepository.upsert_student_profile(
        db_session, user_id=user_a.id, board="CBSE", grade="Class 11", academic_stream="Science"
    )
    OnboardingRepository.upsert_student_profile(
        db_session, user_id=user_b.id, board="ICSE", grade="Class 10", academic_stream=None
    )

    # Step 2: Subjects
    OnboardingRepository.replace_subject_selections(
        db_session, user_id=user_a.id, subjects=["Physics", "Mathematics"]
    )
    OnboardingRepository.replace_subject_selections(
        db_session, user_id=user_b.id, subjects=["History", "Geography", "English"]
    )

    # Step 3: Preferences & Goals
    OnboardingRepository.upsert_learning_preference(
        db_session, user_id=user_a.id, preferred_style="Visual"
    )
    OnboardingRepository.upsert_learning_preference(
        db_session, user_id=user_b.id, preferred_style="Reading"
    )
    OnboardingRepository.replace_study_goals(
        db_session, user_id=user_a.id, goals=["JEE Advanced"]
    )
    OnboardingRepository.replace_study_goals(
        db_session, user_id=user_b.id, goals=["Board Exam 90%"]
    )

    # Step 4: Schedule
    OnboardingRepository.upsert_study_schedule(
        db_session, user_id=user_a.id, daily_target_hours=4.0, preferred_slot="night", available_days=["Monday", "Tuesday"]
    )
    OnboardingRepository.upsert_study_schedule(
        db_session, user_id=user_b.id, daily_target_hours=2.0, preferred_slot="morning", available_days=["Saturday", "Sunday"]
    )

    # Verify User Isolation
    profile_a = OnboardingRepository.get_student_profile(db_session, user_a.id)
    profile_b = OnboardingRepository.get_student_profile(db_session, user_b.id)
    assert profile_a.board == "CBSE"
    assert profile_b.board == "ICSE"

    subjects_a = [s.subject_name for s in OnboardingRepository.get_subject_selections(db_session, user_a.id)]
    subjects_b = [s.subject_name for s in OnboardingRepository.get_subject_selections(db_session, user_b.id)]
    assert subjects_a == ["Physics", "Mathematics"]
    assert subjects_b == ["History", "Geography", "English"]
    assert not set(subjects_a).intersection(set(subjects_b))

    pref_a = OnboardingRepository.get_learning_preference(db_session, user_a.id)
    pref_b = OnboardingRepository.get_learning_preference(db_session, user_b.id)
    assert pref_a.preferred_style == "Visual"
    assert pref_b.preferred_style == "Reading"

    sched_a = OnboardingRepository.get_study_schedule(db_session, user_a.id)
    sched_b = OnboardingRepository.get_study_schedule(db_session, user_b.id)
    assert sched_a.daily_target_hours == 4.0
    assert sched_b.daily_target_hours == 2.0

    # Cleanup
    UserRepository.delete(db_session, user_a.id)
    UserRepository.delete(db_session, user_b.id)


# ── Authentication Dependency Tests ───────────────────────────────────────────
def test_get_current_user_dependency(db_session: Session):
    test_email = "dep_test@example.com"
    # Pre-test cleanup ensures repeatability even if a previous run was interrupted
    existing = UserRepository.get_by_email(db_session, test_email)
    if existing:
        UserRepository.delete(db_session, existing.id)

    user = UserRepository.create(
        db_session,
        email=test_email,
        hashed_password=get_password_hash("TestPass123!"),
        full_name="Dependency User",
        is_active=True,
    )

    # Valid token resolves user
    token = create_access_token(subject=user.id)
    resolved = get_current_user(token=token, db=db_session)
    assert resolved.id == user.id
    assert resolved.email == user.email

    # Expired token raises 401
    expired_token = create_access_token(subject=user.id, expires_delta=timedelta(seconds=-10))
    with pytest.raises(HTTPException) as exc_expired:
        get_current_user(token=expired_token, db=db_session)
    assert exc_expired.value.status_code == 401
    assert "expired" in exc_expired.value.detail.lower()

    # Tampered token raises 401
    with pytest.raises(HTTPException) as exc_invalid:
        get_current_user(token="invalid.bearer.token", db=db_session)
    assert exc_invalid.value.status_code == 401

    # Inactive user raises 400
    user.is_active = False
    db_session.commit()
    with pytest.raises(HTTPException) as exc_inactive:
        get_current_user(token=token, db=db_session)
    assert exc_inactive.value.status_code == 400
    assert "inactive" in exc_inactive.value.detail.lower()

    # Cleanup
    UserRepository.delete(db_session, user.id)
