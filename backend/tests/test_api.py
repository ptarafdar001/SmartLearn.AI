from datetime import timedelta
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.db.session import SessionLocal
from app.main import app
from app.repositories.user_repository import UserRepository


@pytest.fixture
def client():
    """FastAPI TestClient fixture."""
    return TestClient(app)


@pytest.fixture
def db_session():
    """Transactional test session."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


# ── OpenAPI & Diagnostics Tests ───────────────────────────────────────────────
def test_openapi_and_docs_endpoints(client: TestClient):
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    schema = resp.json()
    assert "paths" in schema
    paths = schema["paths"]

    # Verify all expected route paths exist in OpenAPI schema
    expected = [
        "/api/v1/auth/register",
        "/api/v1/auth/login",
        "/api/v1/auth/me",
        "/api/v1/users/onboarding/step1",
        "/api/v1/users/onboarding/step2",
        "/api/v1/users/onboarding/step3",
        "/api/v1/users/onboarding/step4",
        "/api/v1/users/onboarding/status",
        "/api/v1/learning/subjects",
        "/api/v1/learning/recommendations",
        "/api/v1/analytics/overview",
    ]
    for p in expected:
        assert p in paths, f"Path {p} missing from OpenAPI schema"

    # Verify docs page
    docs_resp = client.get("/docs")
    assert docs_resp.status_code == 200


# ── Authentication API Tests ──────────────────────────────────────────────────
def test_auth_api_registration_login_and_me_flow(client: TestClient, db_session: Session):
    test_email = "api_test_student@example.com"
    existing = UserRepository.get_by_email(db_session, test_email)
    if existing:
        UserRepository.delete(db_session, existing.id)

    # 1. Successful registration
    reg_payload = {
        "email": test_email,
        "password": "StrongPassword123!",
        "full_name": "API Tester",
        "role": "student",
        "terms_accepted": True,
    }
    r_reg = client.post("/api/v1/auth/register", json=reg_payload)
    assert r_reg.status_code == 201
    user_data = r_reg.json()
    assert user_data["email"] == test_email
    assert "hashed_password" not in user_data
    assert "password" not in user_data
    user_id = user_data["id"]

    # 2. Duplicate registration returns 409 Conflict
    r_dup = client.post("/api/v1/auth/register", json=reg_payload)
    assert r_dup.status_code == 409
    assert "already registered" in r_dup.json()["detail"].lower()

    # 3. Invalid payload returns 422 Unprocessable Entity
    r_invalid = client.post("/api/v1/auth/register", json={"email": "bad-email", "password": "short"})
    assert r_invalid.status_code == 422

    # 4. Successful login returns Token
    login_payload = {"email": test_email, "password": "StrongPassword123!"}
    r_login = client.post("/api/v1/auth/login", json=login_payload)
    assert r_login.status_code == 200
    token_data = r_login.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    token = token_data["access_token"]

    # 5. Invalid password returns 401
    r_bad_pw = client.post("/api/v1/auth/login", json={"email": test_email, "password": "WrongPassword!"})
    assert r_bad_pw.status_code == 401
    assert r_bad_pw.json()["detail"] == "Invalid email or password"

    # 6. Nonexistent email returns 401
    r_no_user = client.post("/api/v1/auth/login", json={"email": "unknown@example.com", "password": "Pass!"})
    assert r_no_user.status_code == 401
    assert r_no_user.json()["detail"] == "Invalid email or password"

    # 7. /me with valid token
    headers = {"Authorization": f"Bearer {token}"}
    r_me = client.get("/api/v1/auth/me", headers=headers)
    assert r_me.status_code == 200
    me_data = r_me.json()
    assert me_data["id"] == user_id
    assert me_data["email"] == test_email
    assert "hashed_password" not in me_data

    # 8. /me without token returns 401
    r_no_token = client.get("/api/v1/auth/me")
    assert r_no_token.status_code == 401

    # 9. /me with invalid token returns 401
    r_bad_token = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer bad.token.here"})
    assert r_bad_token.status_code == 401

    # 10. /me with expired token returns 401
    expired_token = create_access_token(subject=user_id, expires_delta=timedelta(seconds=-10))
    r_expired = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
    assert r_expired.status_code == 401

    # Cleanup
    UserRepository.delete(db_session, user_id)


# ── Onboarding API Tests ──────────────────────────────────────────────────────
def test_onboarding_api_full_workflow_and_status(client: TestClient, db_session: Session):
    # Setup test user
    email = "onboard_api_student@example.com"
    existing = UserRepository.get_by_email(db_session, email)
    if existing:
        UserRepository.delete(db_session, existing.id)

    r_reg = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "Password123!",
            "full_name": "Onboard Student",
            "terms_accepted": True,
        },
    )
    user_id = r_reg.json()["id"]

    r_login = client.post("/api/v1/auth/login", json={"email": email, "password": "Password123!"})
    token = r_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Unauthenticated access rejected
    assert client.post("/api/v1/users/onboarding/step1", json={}).status_code == 401
    assert client.get("/api/v1/users/onboarding/status").status_code == 401

    # Initial status: current_step = 1, is_onboarded = False
    r_stat = client.get("/api/v1/users/onboarding/status", headers=headers)
    assert r_stat.status_code == 200
    assert r_stat.json()["current_step"] == 1
    assert r_stat.json()["is_onboarded"] is False

    # Step 1
    s1_resp = client.post(
        "/api/v1/users/onboarding/step1",
        headers=headers,
        json={"board": "CBSE", "grade": "Class 12", "academic_stream": "Science"},
    )
    assert s1_resp.status_code == 200
    assert s1_resp.json()["board"] == "CBSE"

    stat1 = client.get("/api/v1/users/onboarding/status", headers=headers).json()
    assert stat1["step1_completed"] is True
    assert stat1["is_onboarded"] is False
    assert stat1["current_step"] == 2

    # Step 2
    s2_resp = client.post(
        "/api/v1/users/onboarding/step2",
        headers=headers,
        json={"subjects": ["Physics", "Mathematics", "Computer Science"]},
    )
    assert s2_resp.status_code == 200
    assert len(s2_resp.json()) == 3

    stat2 = client.get("/api/v1/users/onboarding/status", headers=headers).json()
    assert stat2["step2_completed"] is True
    assert stat2["is_onboarded"] is False
    assert stat2["current_step"] == 3

    # Step 3
    s3_resp = client.post(
        "/api/v1/users/onboarding/step3",
        headers=headers,
        json={
            "preferred_style": "Visual",
            "goals": ["Ace Class 12 Boards", "Qualify JEE"],
            "target_score": "95%",
            "target_exam": "CBSE Board",
        },
    )
    assert s3_resp.status_code == 200
    assert s3_resp.json()["learning_preference"]["preferred_style"] == "Visual"

    stat3 = client.get("/api/v1/users/onboarding/status", headers=headers).json()
    assert stat3["step3_completed"] is True
    assert stat3["is_onboarded"] is False
    assert stat3["current_step"] == 4

    # Step 4
    s4_resp = client.post(
        "/api/v1/users/onboarding/step4",
        headers=headers,
        json={
            "daily_target_hours": 3.0,
            "preferred_slot": "evening",
            "available_days": ["Monday", "Tuesday", "Wednesday"],
        },
    )
    assert s4_resp.status_code == 200
    assert s4_resp.json()["daily_target_hours"] == 3.0

    # After Step 4, is_onboarded MUST be True and current_step = 5
    stat4 = client.get("/api/v1/users/onboarding/status", headers=headers).json()
    assert stat4["step4_completed"] is True
    assert stat4["is_onboarded"] is True
    assert stat4["current_step"] == 5

    # Check /me now reports is_onboarded = True
    me_after = client.get("/api/v1/auth/me", headers=headers).json()
    assert me_after["is_onboarded"] is True

    # Repeated submission (idempotent update check)
    s1_update = client.post(
        "/api/v1/users/onboarding/step1",
        headers=headers,
        json={"board": "CBSE", "grade": "Class 12", "academic_stream": "Science"},
    )
    assert s1_update.status_code == 200

    # Cleanup
    UserRepository.delete(db_session, user_id)


# ── Learning & Analytics API Tests with User Isolation ────────────────────────
def test_learning_and_analytics_apis_user_isolation(client: TestClient, db_session: Session):
    # Setup Student 1 (Physics, Mathematics)
    client.post(
        "/api/v1/auth/register",
        json={"email": "student1_api@example.com", "password": "Password123!", "full_name": "Student One", "terms_accepted": True},
    )
    tok1 = client.post("/api/v1/auth/login", json={"email": "student1_api@example.com", "password": "Password123!"}).json()["access_token"]
    h1 = {"Authorization": f"Bearer {tok1}"}

    client.post("/api/v1/users/onboarding/step1", headers=h1, json={"board": "CBSE", "grade": "12", "academic_stream": "Science"})
    client.post("/api/v1/users/onboarding/step2", headers=h1, json={"subjects": ["Physics", "Mathematics"]})
    client.post("/api/v1/users/onboarding/step3", headers=h1, json={"preferred_style": "Visual", "goals": ["Top Rank"]})
    client.post("/api/v1/users/onboarding/step4", headers=h1, json={"daily_target_hours": 4.0, "preferred_slot": "night", "available_days": ["Monday"]})

    # Setup Student 2 (Chemistry, Biology)
    client.post(
        "/api/v1/auth/register",
        json={"email": "student2_api@example.com", "password": "Password123!", "full_name": "Student Two", "terms_accepted": True},
    )
    tok2 = client.post("/api/v1/auth/login", json={"email": "student2_api@example.com", "password": "Password123!"}).json()["access_token"]
    h2 = {"Authorization": f"Bearer {tok2}"}

    client.post("/api/v1/users/onboarding/step1", headers=h2, json={"board": "ICSE", "grade": "11", "academic_stream": "Medical"})
    client.post("/api/v1/users/onboarding/step2", headers=h2, json={"subjects": ["Chemistry", "Biology"]})
    client.post("/api/v1/users/onboarding/step3", headers=h2, json={"preferred_style": "Auditory", "goals": ["NEET Rank"]})
    client.post("/api/v1/users/onboarding/step4", headers=h2, json={"daily_target_hours": 3.0, "preferred_slot": "morning", "available_days": ["Sunday"]})

    # 1. Unauthenticated learning & analytics access rejected
    assert client.get("/api/v1/learning/subjects").status_code == 401
    assert client.get("/api/v1/learning/recommendations").status_code == 401
    assert client.get("/api/v1/analytics/overview").status_code == 401

    # 2. Verify Enrolled Subjects separation
    subs1 = client.get("/api/v1/learning/subjects", headers=h1).json()
    subs2 = client.get("/api/v1/learning/subjects", headers=h2).json()
    assert [s["subject_name"] for s in subs1] == ["Physics", "Mathematics"]
    assert [s["subject_name"] for s in subs2] == ["Chemistry", "Biology"]
    # Progress percentage must be None (not fake 50% or 100%)
    assert subs1[0]["progress_percentage"] is None

    # 3. Verify Recommendations are data-driven and isolated
    recs1 = client.get("/api/v1/learning/recommendations", headers=h1).json()
    recs2 = client.get("/api/v1/learning/recommendations", headers=h2).json()
    recs1_titles = [r["title"] for r in recs1["recommendations"]]
    recs2_titles = [r["title"] for r in recs2["recommendations"]]
    assert any("Physics" in t for t in recs1_titles)
    assert not any("Chemistry" in t for t in recs1_titles)
    assert any("Chemistry" in t for t in recs2_titles)
    assert not any("Physics" in t for t in recs2_titles)

    # 4. Verify Analytics Overview
    over1 = client.get("/api/v1/analytics/overview", headers=h1).json()
    over2 = client.get("/api/v1/analytics/overview", headers=h2).json()
    assert over1["full_name"] == "Student One"
    assert over1["board"] == "CBSE"
    assert over1["enrolled_subjects"] == ["Physics", "Mathematics"]
    assert over1["study_target"]["daily_target_hours"] == 4.0
    # Unavailable metrics must be None
    assert over1["study_streak_days"] is None
    assert over1["questions_solved"] is None
    assert over1["overall_progress_percentage"] is None

    assert over2["full_name"] == "Student Two"
    assert over2["board"] == "ICSE"
    assert over2["enrolled_subjects"] == ["Chemistry", "Biology"]
    assert over2["study_target"]["daily_target_hours"] == 3.0

    # Cleanup
    u1 = UserRepository.get_by_email(db_session, "student1_api@example.com")
    u2 = UserRepository.get_by_email(db_session, "student2_api@example.com")
    if u1:
        UserRepository.delete(db_session, u1.id)
    if u2:
        UserRepository.delete(db_session, u2.id)
