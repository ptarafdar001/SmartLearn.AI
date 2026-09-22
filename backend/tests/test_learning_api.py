"""
Integration tests for Learning API endpoints:
- GET /api/v1/learning/subjects
- GET /api/v1/learning/subjects/{subject_id}
- GET /api/v1/learning/chapters/{chapter_id}
- GET /api/v1/learning/topics/{topic_id}
- POST /api/v1/learning/topics/{topic_id}/progress
- GET /api/v1/learning/continue
- Authentication requirements, validation constraints, and cross-user isolation.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.seed_curriculum import seed_isc_history_curriculum
from app.db.session import SessionLocal
from app.main import app
from app.models.learning import Subject
from app.repositories.user_repository import UserRepository
from app.schemas.onboarding import (
    Step1BoardClass,
    Step2StreamSubjects,
    Step3PreferencesGoals,
    Step4Schedule,
)
from app.services.onboarding_service import OnboardingService


@pytest.fixture(scope="module")
def client():
    """FastAPI TestClient fixture."""
    return TestClient(app)


@pytest.fixture
def db_session():
    """Transactional test session."""
    session = SessionLocal()
    try:
        # Ensure ISC History curriculum seed is loaded
        seed_isc_history_curriculum(session)
        yield session
    finally:
        session.rollback()
        session.close()


def create_test_student(
    client: TestClient,
    db: Session,
    email: str,
    full_name: str,
    board: str = "ISC",
    grade: str = "Class 11",
    stream: str = "Humanities",
    subjects: list = None,
):
    """Helper to register and onboard a student."""
    if subjects is None:
        subjects = ["History"]

    existing = UserRepository.get_by_email(db, email)
    if existing:
        UserRepository.delete(db, existing.id)

    r_reg = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "SecurePassword123!",
            "full_name": full_name,
            "terms_accepted": True,
        },
    )
    assert r_reg.status_code == 201
    user_id = r_reg.json()["id"]

    r_login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "SecurePassword123!"},
    )
    assert r_login.status_code == 200
    token = r_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Complete Onboarding
    OnboardingService.save_step1_board_class(
        db, user_id, Step1BoardClass(board=board, grade=grade, academic_stream=stream)
    )
    OnboardingService.save_step2_stream_subjects(
        db, user_id, Step2StreamSubjects(subjects=subjects)
    )
    OnboardingService.save_step3_preferences_goals(
        db,
        user_id,
        Step3PreferencesGoals(
            preferred_style="Visual",
            goals=["Score 90% in ISC History"],
            target_score="90%",
            target_exam="ISC Class 11",
        ),
    )
    OnboardingService.save_step4_schedule(
        db,
        user_id,
        Step4Schedule(
            daily_target_hours=2.0,
            preferred_slot="evening",
            available_days=["Monday", "Tuesday", "Wednesday"],
        ),
    )

    return {"user_id": user_id, "token": token, "headers": headers}


# ── Authentication Protection Tests ───────────────────────────────────────────
def test_learning_endpoints_require_authentication(client: TestClient):
    """Verify that all learning endpoints reject unauthenticated requests with 401."""
    assert client.get("/api/v1/learning/subjects").status_code == 401
    assert client.get("/api/v1/learning/subjects/1").status_code == 401
    assert client.get("/api/v1/learning/chapters/1").status_code == 401
    assert client.get("/api/v1/learning/topics/1").status_code == 401
    assert client.post("/api/v1/learning/topics/1/progress", json={}).status_code == 401
    assert client.get("/api/v1/learning/continue").status_code == 401


# ── Subject Hierarchy & Retrieval Tests ────────────────────────────────────────
def test_enrolled_subjects_and_subject_detail_flow(client: TestClient, db_session: Session):
    """Verify enrolled subjects retrieval, subject detail, and chapter list."""
    student = create_test_student(
        client,
        db_session,
        email="isc_student_test@example.com",
        full_name="ISC History Student",
        board="ISC",
        grade="Class 11",
        stream="Humanities",
        subjects=["History"],
    )

    try:
        # 1. GET /api/v1/learning/subjects
        r_subs = client.get("/api/v1/learning/subjects", headers=student["headers"])
        assert r_subs.status_code == 200
        subs_data = r_subs.json()
        assert len(subs_data) >= 1
        history_sub = next((s for s in subs_data if s["name"] == "History"), None)
        assert history_sub is not None
        assert history_sub["board"] == "ISC"
        assert history_sub["grade"] == "Class 11"
        assert history_sub["chapter_count"] >= 3
        assert history_sub["topic_count"] >= 5
        subject_id = history_sub["id"]

        # 2. GET /api/v1/learning/subjects/{subject_id}
        r_sub_detail = client.get(
            f"/api/v1/learning/subjects/{subject_id}", headers=student["headers"]
        )
        assert r_sub_detail.status_code == 200
        sub_detail = r_sub_detail.json()
        assert sub_detail["id"] == subject_id
        assert sub_detail["name"] == "History"
        assert len(sub_detail["chapters"]) >= 3

        first_chapter = sub_detail["chapters"][0]
        assert first_chapter["chapter_number"] == 1
        assert "Emergence of the Colonial Economy" in first_chapter["title"]
        assert len(first_chapter["topics"]) >= 3
        first_topic = first_chapter["topics"][0]
        assert first_topic["topic_number"] == 1
        assert "Transport" in first_topic["title"]
        topic_id = first_topic["id"]
        chapter_id = first_chapter["id"]

        # 3. GET /api/v1/learning/chapters/{chapter_id}
        r_chap = client.get(
            f"/api/v1/learning/chapters/{chapter_id}", headers=student["headers"]
        )
        assert r_chap.status_code == 200
        chap_data = r_chap.json()
        assert chap_data["id"] == chapter_id
        assert len(chap_data["topics"]) >= 2

        # 4. GET /api/v1/learning/topics/{topic_id}
        r_topic = client.get(
            f"/api/v1/learning/topics/{topic_id}", headers=student["headers"]
        )
        assert r_topic.status_code == 200
        topic_data = r_topic.json()
        assert topic_data["id"] == topic_id
        assert len(topic_data["resources"]) >= 1

        # Check multi-modal resource fields
        res_types = [r["resource_type"] for r in topic_data["resources"]]
        assert "video" in res_types
        assert "notes" in res_types

        # Verify YouTube video embed metadata
        video_res = next(r for r in topic_data["resources"] if r["resource_type"] == "video")
        assert video_res["provider"].lower() == "youtube"
        assert video_res["external_id"] is not None
        assert "youtube-nocookie.com/embed" in video_res["content_url"]
        assert video_res["is_verified"] is True

    finally:
        UserRepository.delete(db_session, student["user_id"])


# ── Progress Lifecycle & Validation Tests ───────────────────────────────────────
def test_progress_lifecycle_and_validation(client: TestClient, db_session: Session):
    """Test progress creation, updates, completion timestamp, and Pydantic validation."""
    student = create_test_student(
        client,
        db_session,
        email="progress_student@example.com",
        full_name="Progress Student",
    )

    try:
        # Find a valid topic
        sub = db_session.query(Subject).filter(Subject.code == "isc-11-hist").first()
        topic = sub.chapters[0].topics[0]
        topic_id = topic.id

        # 1. Validation: negative time_spent_seconds rejected
        r_neg_time = client.post(
            f"/api/v1/learning/topics/{topic_id}/progress",
            headers=student["headers"],
            json={"status": "in_progress", "progress_percentage": 25.0, "time_spent_seconds": -50},
        )
        assert r_neg_time.status_code == 422

        # 2. Validation: progress_percentage > 100 rejected
        r_over_100 = client.post(
            f"/api/v1/learning/topics/{topic_id}/progress",
            headers=student["headers"],
            json={"status": "in_progress", "progress_percentage": 110.0, "time_spent_seconds": 60},
        )
        assert r_over_100.status_code == 422

        # 3. Validation: progress_percentage < 0 rejected
        r_neg_pct = client.post(
            f"/api/v1/learning/topics/{topic_id}/progress",
            headers=student["headers"],
            json={"status": "in_progress", "progress_percentage": -10.0, "time_spent_seconds": 60},
        )
        assert r_neg_pct.status_code == 422

        # 4. Validation: invalid status rejected
        r_bad_status = client.post(
            f"/api/v1/learning/topics/{topic_id}/progress",
            headers=student["headers"],
            json={"status": "mastered_already", "progress_percentage": 50.0, "time_spent_seconds": 60},
        )
        assert r_bad_status.status_code == 422

        # 5. Successful In-Progress creation
        r_progress_start = client.post(
            f"/api/v1/learning/topics/{topic_id}/progress",
            headers=student["headers"],
            json={"status": "in_progress", "progress_percentage": 45.0, "time_spent_seconds": 180},
        )
        assert r_progress_start.status_code == 200
        prog_data = r_progress_start.json()
        assert prog_data["topic_id"] == topic_id
        assert prog_data["status"] == "in_progress"
        assert prog_data["progress_percentage"] == 45.0
        assert prog_data["time_spent_seconds"] == 180
        assert prog_data["completed_at"] is None

        # 6. Verify topic detail now reflects the saved progress
        r_topic = client.get(f"/api/v1/learning/topics/{topic_id}", headers=student["headers"])
        assert r_topic.status_code == 200
        assert r_topic.json()["user_progress"] is not None
        assert r_topic.json()["user_progress"]["progress_percentage"] == 45.0

        # 7. Complete the topic
        r_complete = client.post(
            f"/api/v1/learning/topics/{topic_id}/progress",
            headers=student["headers"],
            json={"status": "completed", "progress_percentage": 100.0, "time_spent_seconds": 600},
        )
        assert r_complete.status_code == 200
        comp_data = r_complete.json()
        assert comp_data["status"] == "completed"
        assert comp_data["progress_percentage"] == 100.0
        assert comp_data["completed_at"] is not None

        # 8. Check Continue Learning endpoint
        r_continue = client.get("/api/v1/learning/continue", headers=student["headers"])
        assert r_continue.status_code == 200

    finally:
        UserRepository.delete(db_session, student["user_id"])


# ── Cross-User Progress Data Isolation Tests ──────────────────────────────────
def test_cross_user_progress_isolation(client: TestClient, db_session: Session):
    """Verify Student A cannot see or mutate Student B's progress, and progress is isolated."""
    student_a = create_test_student(
        client,
        db_session,
        email="isolation_student_a@example.com",
        full_name="Student Alpha",
    )
    student_b = create_test_student(
        client,
        db_session,
        email="isolation_student_b@example.com",
        full_name="Student Beta",
    )

    try:
        sub = db_session.query(Subject).filter(Subject.code == "isc-11-hist").first()
        topic = sub.chapters[0].topics[0]
        topic_id = topic.id

        # Student A marks topic as completed (100%)
        r_a = client.post(
            f"/api/v1/learning/topics/{topic_id}/progress",
            headers=student_a["headers"],
            json={"status": "completed", "progress_percentage": 100.0, "time_spent_seconds": 900},
        )
        assert r_a.status_code == 200

        # Student B checks topic detail: user_progress must be None for Student B
        r_b_topic = client.get(
            f"/api/v1/learning/topics/{topic_id}", headers=student_b["headers"]
        )
        assert r_b_topic.status_code == 200
        assert r_b_topic.json()["user_progress"] is None

        # Student B sets progress to 20%
        r_b_prog = client.post(
            f"/api/v1/learning/topics/{topic_id}/progress",
            headers=student_b["headers"],
            json={"status": "in_progress", "progress_percentage": 20.0, "time_spent_seconds": 120},
        )
        assert r_b_prog.status_code == 200
        assert r_b_prog.json()["progress_percentage"] == 20.0

        # Student A checks topic detail again: Student A's progress MUST still be 100%
        r_a_topic = client.get(
            f"/api/v1/learning/topics/{topic_id}", headers=student_a["headers"]
        )
        assert r_a_topic.status_code == 200
        assert r_a_topic.json()["user_progress"]["progress_percentage"] == 100.0
        assert r_a_topic.json()["user_progress"]["status"] == "completed"

    finally:
        UserRepository.delete(db_session, student_a["user_id"])
        UserRepository.delete(db_session, student_b["user_id"])
