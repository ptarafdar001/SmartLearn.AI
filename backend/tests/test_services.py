import pytest
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.repositories.user_repository import UserRepository
from app.schemas.auth import UserCreate, UserLogin
from app.schemas.onboarding import (
    Step1BoardClass,
    Step2StreamSubjects,
    Step3PreferencesGoals,
    Step4Schedule,
)
from app.services.auth_service import AuthService
from app.services.dashboard_service import DashboardService
from app.services.onboarding_service import OnboardingService


@pytest.fixture
def db_session():
    """Transactional test session."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


# ── AuthService Tests ─────────────────────────────────────────────────────────
def test_auth_service_registration_and_duplicate(db_session: Session):
    email = "service_test_student@example.com"
    existing = UserRepository.get_by_email(db_session, email)
    if existing:
        UserRepository.delete(db_session, existing.id)

    create_data = UserCreate(
        email=email,
        password="SecurePassword123!",
        full_name="Service Student",
        role="student",
        terms_accepted=True,
    )
    user_resp = AuthService.register_user(db_session, create_data)

    assert user_resp.id is not None
    assert user_resp.email == email
    assert user_resp.is_onboarded is False

    # Duplicate registration should raise ValueError
    with pytest.raises(ValueError, match="already registered"):
        AuthService.register_user(db_session, create_data)

    # Cleanup
    UserRepository.delete(db_session, user_resp.id)


def test_auth_service_authentication_and_tokens(db_session: Session):
    email = "auth_login_test@example.com"
    existing = UserRepository.get_by_email(db_session, email)
    if existing:
        UserRepository.delete(db_session, existing.id)

    create_data = UserCreate(
        email=email,
        password="CorrectPassword123!",
        full_name="Login Student",
        role="student",
        terms_accepted=True,
    )
    user_resp = AuthService.register_user(db_session, create_data)

    # Successful login
    login_data = UserLogin(email=email, password="CorrectPassword123!")
    user = AuthService.authenticate_user(db_session, login_data)
    assert user.id == user_resp.id

    # Token creation
    token = AuthService.create_token_for_user(user)
    assert token.access_token is not None
    assert token.token_type == "bearer"

    # Profile retrieval
    profile = AuthService.get_user_profile(db_session, user.id)
    assert profile.id == user.id
    assert profile.email == email

    # Invalid password raises ValueError
    bad_login = UserLogin(email=email, password="WrongPassword!")
    with pytest.raises(ValueError, match="Invalid email or password"):
        AuthService.authenticate_user(db_session, bad_login)

    # Unknown email raises ValueError
    unknown_login = UserLogin(email="nonexistent@example.com", password="Password123!")
    with pytest.raises(ValueError, match="Invalid email or password"):
        AuthService.authenticate_user(db_session, unknown_login)

    # Cleanup
    UserRepository.delete(db_session, user.id)


# ── OnboardingService Tests ───────────────────────────────────────────────────
def test_onboarding_four_steps_and_status_progression(db_session: Session):
    create_data = UserCreate(
        email="onboard_flow_test@example.com",
        password="Password123!",
        full_name="Flow Student",
        role="student",
        terms_accepted=True,
    )
    user = AuthService.register_user(db_session, create_data)

    # Initially at Step 1, is_onboarded=False
    status = OnboardingService.get_onboarding_status(db_session, user.id)
    assert status.is_onboarded is False
    assert status.step1_completed is False
    assert status.current_step == 1

    # Execute Step 1
    step1 = Step1BoardClass(board="CBSE", grade="Class 12", academic_stream="Science")
    p1 = OnboardingService.save_step1_board_class(db_session, user.id, step1)
    assert p1.board == "CBSE"

    status = OnboardingService.get_onboarding_status(db_session, user.id)
    assert status.step1_completed is True
    assert status.step2_completed is False
    assert status.is_onboarded is False
    assert status.current_step == 2

    # Execute Step 2
    step2 = Step2StreamSubjects(subjects=["Physics", "Mathematics", "Chemistry"])
    subs = OnboardingService.save_step2_stream_subjects(db_session, user.id, step2)
    assert len(subs) == 3

    status = OnboardingService.get_onboarding_status(db_session, user.id)
    assert status.step2_completed is True
    assert status.step3_completed is False
    assert status.is_onboarded is False
    assert status.current_step == 3

    # Execute Step 3
    step3 = Step3PreferencesGoals(
        preferred_style="Visual",
        goals=["Score 95% in Board Exams"],
        target_score="95%",
        target_exam="CBSE 12th",
    )
    p3 = OnboardingService.save_step3_preferences_goals(db_session, user.id, step3)
    assert p3["learning_preference"].preferred_style == "Visual"
    assert len(p3["study_goals"]) == 1

    status = OnboardingService.get_onboarding_status(db_session, user.id)
    assert status.step3_completed is True
    assert status.step4_completed is False
    assert status.is_onboarded is False
    assert status.current_step == 4

    # Execute Step 4
    step4 = Step4Schedule(
        daily_target_hours=3.5,
        preferred_slot="evening",
        available_days=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
    )
    p4 = OnboardingService.save_step4_schedule(db_session, user.id, step4)
    assert p4.daily_target_hours == 3.5

    # After Step 4, is_onboarded MUST become True
    status = OnboardingService.get_onboarding_status(db_session, user.id)
    assert status.step4_completed is True
    assert status.is_onboarded is True
    assert status.current_step == 5

    # Repeated submission (idempotency/update check)
    step1_update = Step1BoardClass(board="ICSE", grade="Class 12", academic_stream="Science")
    p1_updated = OnboardingService.save_step1_board_class(db_session, user.id, step1_update)
    assert p1_updated.board == "ICSE"

    # Cleanup
    UserRepository.delete(db_session, user.id)


# ── DashboardService & Data Isolation Tests ───────────────────────────────────
def test_dashboard_service_user_isolation_and_no_fake_metrics(db_session: Session):
    # Setup Student A (Science: Physics, Mathematics)
    user_a = AuthService.register_user(
        db_session,
        UserCreate(
            email="student_alpha_dash@example.com",
            password="Password123!",
            full_name="Alpha Student",
            terms_accepted=True,
        ),
    )
    OnboardingService.save_step1_board_class(
        db_session, user_a.id, Step1BoardClass(board="CBSE", grade="Class 12", academic_stream="Science")
    )
    OnboardingService.save_step2_stream_subjects(
        db_session, user_a.id, Step2StreamSubjects(subjects=["Physics", "Mathematics"])
    )
    OnboardingService.save_step3_preferences_goals(
        db_session, user_a.id, Step3PreferencesGoals(preferred_style="Visual", goals=["JEE Advanced Target"])
    )
    OnboardingService.save_step4_schedule(
        db_session, user_a.id, Step4Schedule(daily_target_hours=4.0, preferred_slot="morning", available_days=["Monday", "Tuesday"])
    )

    # Setup Student B (Commerce: Economics, Accountancy)
    user_b = AuthService.register_user(
        db_session,
        UserCreate(
            email="student_beta_dash@example.com",
            password="Password123!",
            full_name="Beta Student",
            terms_accepted=True,
        ),
    )
    OnboardingService.save_step1_board_class(
        db_session, user_b.id, Step1BoardClass(board="ICSE", grade="Class 11", academic_stream="Commerce")
    )
    OnboardingService.save_step2_stream_subjects(
        db_session, user_b.id, Step2StreamSubjects(subjects=["Economics", "Accountancy"])
    )
    OnboardingService.save_step3_preferences_goals(
        db_session, user_b.id, Step3PreferencesGoals(preferred_style="Reading", goals=["CA Foundation Target"])
    )
    OnboardingService.save_step4_schedule(
        db_session, user_b.id, Step4Schedule(daily_target_hours=2.5, preferred_slot="evening", available_days=["Saturday", "Sunday"])
    )

    # Check Dashboard Overview for Student A
    dash_a = DashboardService.get_dashboard_overview(db_session, user_a.id)
    assert dash_a.full_name == "Alpha Student"
    assert dash_a.board == "CBSE"
    assert dash_a.enrolled_subjects == ["Physics", "Mathematics"]
    assert dash_a.study_target.daily_target_hours == 4.0
    # Verify uncalculated metrics are None rather than fake numbers
    assert dash_a.study_streak_days is None
    assert dash_a.questions_solved is None
    assert dash_a.overall_progress_percentage is None

    # Check Dashboard Overview for Student B
    dash_b = DashboardService.get_dashboard_overview(db_session, user_b.id)
    assert dash_b.full_name == "Beta Student"
    assert dash_b.board == "ICSE"
    assert dash_b.enrolled_subjects == ["Economics", "Accountancy"]
    assert dash_b.study_target.daily_target_hours == 2.5
    assert dash_b.study_streak_days is None

    # Verify Enrolled Subjects separation
    subs_a = DashboardService.get_enrolled_subjects(db_session, user_a.id)
    subs_b = DashboardService.get_enrolled_subjects(db_session, user_b.id)
    assert [s.subject_name for s in subs_a] == ["Physics", "Mathematics"]
    assert [s.subject_name for s in subs_b] == ["Economics", "Accountancy"]
    assert not set([s.subject_name for s in subs_a]).intersection(set([s.subject_name for s in subs_b]))

    # Verify Data-Driven Recommendations
    recs_a = DashboardService.get_recommendations(db_session, user_a.id)
    rec_titles_a = [r.title for r in recs_a.recommendations]
    assert any("Physics" in t for t in rec_titles_a)
    assert any("Mathematics" in t for t in rec_titles_a)
    assert not any("Economics" in t for t in rec_titles_a)

    recs_b = DashboardService.get_recommendations(db_session, user_b.id)
    rec_titles_b = [r.title for r in recs_b.recommendations]
    assert any("Economics" in t for t in rec_titles_b)
    assert not any("Physics" in t for t in rec_titles_b)

    # Cleanup
    UserRepository.delete(db_session, user_a.id)
    UserRepository.delete(db_session, user_b.id)
