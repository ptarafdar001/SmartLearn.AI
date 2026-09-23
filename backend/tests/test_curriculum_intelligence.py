"""
Automated unit and integration tests for SmartLearn.AI Curriculum Intelligence Engine.

Covers:
- Syllabus learning objectives
- Server-side curriculum scope enforcement & redirection
- Authentic PYQ retrieval and metadata preservation (strictly non-AI)
- AI-generated practice questions labeling and provenance
- Student question attempt grading and submission persistence
- Dynamic 10-part study notes caching and retrieval
"""

import json
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
import pytest
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.seed_curriculum import seed_isc_history_curriculum
from app.db.session import SessionLocal
from app.main import app
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
from app.models.onboarding import LearningPreference, StudentProfile
from app.models.users import User
from app.repositories.user_repository import UserRepository
from app.schemas.learning import PracticeQuestionAttemptRequest
from app.schemas.onboarding import (
    Step1BoardClass,
    Step2StreamSubjects,
    Step3PreferencesGoals,
    Step4Schedule,
)
from app.services.onboarding_service import OnboardingService
from scripts.seed_curriculum_intelligence import seed_curriculum_intelligence

settings = get_settings()


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.fixture
def db_session():
    session = SessionLocal()
    try:
        seed_isc_history_curriculum(session)
        seed_curriculum_intelligence()
        yield session
    finally:
        session.rollback()
        session.close()


def get_auth_student(client: TestClient, db_session: Session, email: str = "curriculum_test@example.com"):
    """Helper to create and authenticate a test student enrolled in ISC Class 11 History."""
    existing = UserRepository.get_by_email(db_session, email)
    if existing:
        UserRepository.delete(db_session, existing.id)

    r_reg = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "SecurePassword123!",
            "full_name": "Curriculum Tester",
            "terms_accepted": True,
        },
    )
    user_id = r_reg.json()["id"]

    r_login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "SecurePassword123!"},
    )
    token = r_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    OnboardingService.save_step1_board_class(
        db_session, user_id, Step1BoardClass(board="ISC", grade="Class 11", academic_stream="Humanities")
    )
    OnboardingService.save_step2_stream_subjects(
        db_session, user_id, Step2StreamSubjects(subjects=["History"])
    )
    OnboardingService.save_step3_preferences_goals(
        db_session,
        user_id,
        Step3PreferencesGoals(
            preferred_style="Interactive",
            goals=["Master ISC History"],
            target_score="90%",
            target_exam="ISC Class 11",
        ),
    )
    OnboardingService.save_step4_schedule(
        db_session,
        user_id,
        Step4Schedule(
            daily_target_hours=2.0,
            preferred_slot="evening",
            available_days=["Monday", "Tuesday"],
        ),
    )

    return {"user_id": user_id, "token": token, "headers": headers}


# ── 1. Learning Objectives Test ───────────────────────────────────────────────
def test_get_topic_objectives(client: TestClient, db_session: Session):
    """Verify topic syllabus objectives can be retrieved with Bloom taxonomy."""
    auth = get_auth_student(client, db_session, "obj_test@example.com")
    topic = db_session.query(Topic).filter(Topic.id == 44).first() or db_session.query(Topic).join(LearningObjective).first()
    assert topic is not None

    resp = client.get(
        f"/api/v1/learning/topics/{topic.id}/objectives",
        headers=auth["headers"],
    )
    assert resp.status_code == 200
    objs = resp.json()
    assert len(objs) >= 1
    assert "code" in objs[0]
    assert "taxonomy_level" in objs[0]


# ── 2. Authentic PYQs Retrieval & Segregation ─────────────────────────────────
def test_get_authentic_pyqs_metadata(client: TestClient, db_session: Session):
    """Verify authentic PYQs have official examination year, paper code, and marks."""
    auth = get_auth_student(client, db_session, "pyq_test@example.com")
    topic = db_session.query(Topic).filter(Topic.id == 44).first() or db_session.query(Topic).join(PreviousYearQuestion).first()
    assert topic is not None

    resp = client.get(
        f"/api/v1/learning/topics/{topic.id}/pyqs",
        headers=auth["headers"],
    )
    assert resp.status_code == 200
    pyqs = resp.json()
    assert len(pyqs) >= 1
    pyq = pyqs[0]
    assert pyq["board"] == "ISC"
    assert pyq["exam_year"] in [2020, 2022, 2023]
    assert "paper_code" in pyq
    assert pyq["is_verified"] is True
    assert pyq["source_name"] != ""


# ── 3. AI-Generated Practice Questions Labeled Correctly ──────────────────────
def test_ai_practice_questions_explicitly_labeled(client: TestClient, db_session: Session):
    """Verify generated practice questions are strictly tagged as AI-generated."""
    auth = get_auth_student(client, db_session, "practice_test@example.com")
    topic = db_session.query(Topic).filter(Topic.id == 44).first() or db_session.query(Topic).join(PracticeQuestion).first()
    assert topic is not None

    resp = client.get(
        f"/api/v1/learning/topics/{topic.id}/practice-questions",
        headers=auth["headers"],
    )
    assert resp.status_code == 200
    questions = resp.json()
    assert len(questions) >= 1
    q = questions[0]
    assert q["is_ai_generated"] is True
    assert q["options"] is not None
    assert len(q["options"]) == 4


# ── 4. Student Attempt Evaluation & Persistence ───────────────────────────────
def test_submit_practice_attempt(client: TestClient, db_session: Session):
    """Verify submitting an answer evaluates correctness, awards marks, and returns explanation."""
    auth = get_auth_student(client, db_session, "attempt_test@example.com")
    pq = db_session.query(PracticeQuestion).first()
    assert pq is not None

    # Submit correct answer
    resp = client.post(
        f"/api/v1/learning/practice-questions/{pq.id}/attempt",
        json={"user_answer": pq.correct_answer},
        headers=auth["headers"],
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_correct"] is True
    assert data["marks_obtained"] == pq.marks
    assert data["explanation"] == pq.explanation

    # Verify attempt history endpoint
    hist_resp = client.get(
        "/api/v1/learning/practice-questions/my-attempts",
        headers=auth["headers"],
    )
    assert hist_resp.status_code == 200
    attempts = hist_resp.json()
    assert any(a["practice_question_id"] == pq.id for a in attempts)


# ── 5. Dynamic 10-Part Study Notes ────────────────────────────────────────────
def test_get_topic_study_notes(client: TestClient, db_session: Session):
    """Verify 10-part study notes are served with structured sections."""
    auth = get_auth_student(client, db_session, "notes_test@example.com")
    topic = db_session.query(Topic).filter(Topic.id == 44).first() or db_session.query(Topic).join(TopicStudyNotes).first()
    assert topic is not None

    resp = client.get(
        f"/api/v1/learning/topics/{topic.id}/notes?type=comprehensive",
        headers=auth["headers"],
    )
    assert resp.status_code == 200
    notes = resp.json()
    assert "Topic Overview" in notes["explanation_markdown"]
    assert "Learning Objectives" in notes["explanation_markdown"]
    assert notes["notes_type"] == "comprehensive"
    assert notes["is_verified"] is True


# ── 6. Out-of-Scope Server-Side Redirection ───────────────────────────────────
def test_out_of_scope_redirection_guard(client: TestClient, db_session: Session):
    """Verify questions outside topic syllabus are gracefully redirected by backend."""
    auth = get_auth_student(client, db_session, "scope_test@example.com")
    topic = db_session.query(Topic).filter(Topic.id == 44).first() or db_session.query(Topic).first()
    assert topic is not None

    with patch.object(settings, "GEMINI_API_KEY", "mock-test-key"):
        resp = client.post(
            "/api/v1/tutor/chat",
            json={
                "topic_id": topic.id,
                "message": "Can you explain quantum thermodynamics and entropy in black holes?",
            },
            headers=auth["headers"],
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_out_of_scope"] is True
        assert "outside the isc" in data["reply"].lower() or "outside" in data["reply"].lower()


# ── 7. Practice Attempt Persistence, Topic Filter & User Isolation ────────────
def test_practice_attempt_persistence_topic_filter_and_isolation(client: TestClient, db_session: Session):
    """Verify student question attempts persist, can be filtered by topic_id, and enforce strict user isolation."""
    student_a = get_auth_student(client, db_session, "attempt_user_a@example.com")
    student_b = get_auth_student(client, db_session, "attempt_user_b@example.com")

    pq = db_session.query(PracticeQuestion).first()
    assert pq is not None, "At least one practice question required for test"

    # 1. Student A submits attempt
    resp_a = client.post(
        f"/api/v1/learning/practice-questions/{pq.id}/attempt",
        json={"user_answer": pq.correct_answer},
        headers=student_a["headers"],
    )
    assert resp_a.status_code == 200
    assert resp_a.json()["is_correct"] is True

    # 2. Student A retrieves attempts filtered by matching topic_id
    filtered_resp = client.get(
        f"/api/v1/learning/practice-questions/my-attempts?topic_id={pq.topic_id}",
        headers=student_a["headers"],
    )
    assert filtered_resp.status_code == 200
    filtered_attempts = filtered_resp.json()
    assert len(filtered_attempts) >= 1
    assert any(a["practice_question_id"] == pq.id for a in filtered_attempts)

    # 3. Student A retrieves attempts filtered by non-matching topic_id (e.g. 999999)
    mismatch_resp = client.get(
        "/api/v1/learning/practice-questions/my-attempts?topic_id=999999",
        headers=student_a["headers"],
    )
    assert mismatch_resp.status_code == 200
    assert len(mismatch_resp.json()) == 0

    # 4. Student B retrieves attempts; must NOT see Student A's attempt
    b_attempts_resp = client.get(
        "/api/v1/learning/practice-questions/my-attempts",
        headers=student_b["headers"],
    )
    assert b_attempts_resp.status_code == 200
    b_attempts = b_attempts_resp.json()
    assert not any(a["practice_question_id"] == pq.id for a in b_attempts)

