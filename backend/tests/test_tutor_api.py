"""
Tests for Curriculum-Aware AI Tutor API:
- POST /api/v1/tutor/chat
- Authentication, validation, curriculum grounding, multimodal image doubt-solving,
  quota/error handling, and cross-user context isolation.
"""

import base64
from unittest.mock import MagicMock, patch
import httpx
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.seed_curriculum import seed_isc_history_curriculum
from app.db.session import SessionLocal
from app.main import app
from app.models.learning import Topic
from app.repositories.user_repository import UserRepository
from app.schemas.onboarding import (
    Step1BoardClass,
    Step2StreamSubjects,
    Step3PreferencesGoals,
    Step4Schedule,
)
from app.services.onboarding_service import OnboardingService

settings = get_settings()


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.fixture
def db_session():
    session = SessionLocal()
    try:
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
):
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
    user_id = r_reg.json()["id"]

    r_login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "SecurePassword123!"},
    )
    token = r_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    OnboardingService.save_step1_board_class(
        db, user_id, Step1BoardClass(board=board, grade=grade, academic_stream=stream)
    )
    OnboardingService.save_step2_stream_subjects(
        db, user_id, Step2StreamSubjects(subjects=["History"])
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
            available_days=["Monday", "Tuesday"],
        ),
    )

    return {"user_id": user_id, "token": token, "headers": headers}


# ── 1. Authentication Protection ──────────────────────────────────────────────
def test_tutor_chat_requires_authentication(client: TestClient):
    """Verify unauthenticated request is rejected with 401."""
    resp = client.post("/api/v1/tutor/chat", json={"topic_id": 1, "message": "Help me"})
    assert resp.status_code == 401


# ── 2. Missing API Key Returns 503 Service Unavailable ────────────────────────
def test_tutor_chat_missing_api_key(client: TestClient, db_session: Session):
    """Verify friendly 503 error when GEMINI_API_KEY is not configured."""
    student = create_test_student(
        client, db_session, "tutor_key_test@example.com", "Key Test Student"
    )
    topic = db_session.query(Topic).first()
    assert topic is not None

    with patch.object(settings, "GEMINI_API_KEY", None):
        resp = client.post(
            "/api/v1/tutor/chat",
            json={"topic_id": topic.id, "message": "Explain the railway guarantee system"},
            headers=student["headers"],
        )
        assert resp.status_code == 503
        assert "GEMINI_API_KEY is required" in resp.json()["detail"]


# ── 3. Grounded Text Tutoring with Mocked Gemini API ──────────────────────────
def test_tutor_chat_successful_grounded_text(client: TestClient, db_session: Session):
    """Verify tutor generates grounded response with student and syllabus context."""
    student = create_test_student(
        client, db_session, "tutor_success@example.com", "Rohan Mehta", board="ISC", grade="Class 11"
    )
    topic = db_session.query(Topic).first()

    mock_gemini_resp = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": (
                                "Hello Rohan! The Railway Guarantee System guaranteed British investors "
                                "a 4.5% to 5% return directly from Indian taxes, which encouraged wasteful expenditure."
                            )
                        }
                    ]
                }
            }
        ]
    }

    mock_client_instance = MagicMock()
    mock_client_instance.__enter__.return_value = mock_client_instance
    mock_client_instance.post.return_value = MagicMock(
        status_code=200,
        json=lambda: mock_gemini_resp,
    )

    with patch.object(settings, "GEMINI_API_KEY", "mock-test-key"):
        with patch("app.services.tutor_service.httpx.Client", return_value=mock_client_instance):
            resp = client.post(
                "/api/v1/tutor/chat",
                json={
                    "topic_id": topic.id,
                    "message": "Can you explain the railway guarantee system simply?",
                    "conversation_history": [],
                },
                headers=student["headers"],
            )

            assert resp.status_code == 200
            data = resp.json()
            assert "Railway Guarantee System" in data["reply"]
            assert data["topic_id"] == topic.id
            assert data["topic_title"] == topic.title
            assert data["board"] == "ISC"
            assert data["grade"] == "Class 11"
            assert len(data["grounded_resource_titles"]) >= 1
            assert data["is_out_of_scope"] is False

            # Verify Gemini payload received system instruction with curriculum context
            called_payload = mock_client_instance.post.call_args[1]["json"]
            sys_text = called_payload["system_instruction"]["parts"][0]["text"]
            assert "ISC" in sys_text
            assert "Class 11" in sys_text
            assert "Rohan Mehta" in sys_text
            assert topic.title in sys_text


# ── 4. Multimodal Image Doubt Solving ─────────────────────────────────────────
def test_tutor_chat_multimodal_image_doubt(client: TestClient, db_session: Session):
    """Verify image base64 is accepted and formatted as inline_data for Gemini."""
    student = create_test_student(
        client, db_session, "tutor_image@example.com", "Priya Das"
    )
    topic = db_session.query(Topic).first()

    # Create dummy 1x1 png image base64
    fake_png_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    fake_b64 = f"data:image/png;base64,{base64.b64encode(fake_png_bytes).decode('utf-8')}"

    mock_gemini_resp = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": "Looking at the diagram of the 1853 railway route, notice how it linked Bombay with Thane."
                        }
                    ]
                }
            }
        ]
    }

    mock_client_instance = MagicMock()
    mock_client_instance.__enter__.return_value = mock_client_instance
    mock_client_instance.post.return_value = MagicMock(
        status_code=200,
        json=lambda: mock_gemini_resp,
    )

    with patch.object(settings, "GEMINI_API_KEY", "mock-test-key"):
        with patch("app.services.tutor_service.httpx.Client", return_value=mock_client_instance):
            resp = client.post(
                "/api/v1/tutor/chat",
                json={
                    "topic_id": topic.id,
                    "message": "What is shown in this map from my textbook?",
                    "image_base64": fake_b64,
                },
                headers=student["headers"],
            )

            assert resp.status_code == 200
            assert "1853 railway route" in resp.json()["reply"]

            # Inspect that inline_data part was constructed
            called_payload = mock_client_instance.post.call_args[1]["json"]
            user_parts = called_payload["contents"][0]["parts"]
            image_part = next((p for p in user_parts if "inline_data" in p), None)
            assert image_part is not None
            assert image_part["inline_data"]["mime_type"] == "image/png"


# ── 5. Quota Exceeded (429) Handling ──────────────────────────────────────────
def test_tutor_chat_quota_handling(client: TestClient, db_session: Session):
    """Verify 429 quota error from upstream Gemini is transformed into clean HTTP 429."""
    student = create_test_student(
        client, db_session, "tutor_quota@example.com", "Quota Student"
    )
    topic = db_session.query(Topic).first()

    mock_client_instance = MagicMock()
    mock_client_instance.__enter__.return_value = mock_client_instance
    mock_client_instance.post.return_value = MagicMock(
        status_code=429,
        text="Quota exceeded",
    )

    with patch.object(settings, "GEMINI_API_KEY", "mock-test-key"):
        with patch("app.services.tutor_service.httpx.Client", return_value=mock_client_instance):
            resp = client.post(
                "/api/v1/tutor/chat",
                json={"topic_id": topic.id, "message": "Give me practice questions"},
                headers=student["headers"],
            )

            assert resp.status_code == 429
            assert "quota or rate limit exceeded" in resp.json()["detail"].lower()


# ── 6. Out-of-Scope Redirection Handling ──────────────────────────────────────
def test_tutor_chat_out_of_scope_handling(client: TestClient, db_session: Session):
    """Verify out-of-scope response flags is_out_of_scope=True."""
    student = create_test_student(
        client, db_session, "tutor_scope@example.com", "Scope Student"
    )
    topic = db_session.query(Topic).first()

    mock_gemini_resp = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": (
                                "This concept is outside the syllabus for ISC Class 11 History, "
                                "as quantum mechanics is not covered in this topic. Let's return to the Colonial Economy."
                            )
                        }
                    ]
                }
            }
        ]
    }

    mock_client_instance = MagicMock()
    mock_client_instance.__enter__.return_value = mock_client_instance
    mock_client_instance.post.return_value = MagicMock(
        status_code=200,
        json=lambda: mock_gemini_resp,
    )

    with patch.object(settings, "GEMINI_API_KEY", "mock-test-key"):
        with patch("app.services.tutor_service.httpx.Client", return_value=mock_client_instance):
            resp = client.post(
                "/api/v1/tutor/chat",
                json={"topic_id": topic.id, "message": "Can you explain quantum physics?"},
                headers=student["headers"],
            )

            assert resp.status_code == 200
            assert resp.json()["is_out_of_scope"] is True


# ── 7. Non-existent Topic 404 ─────────────────────────────────────────────────
def test_tutor_chat_topic_not_found(client: TestClient, db_session: Session):

    """Verify 404 when topic_id does not exist."""
    student = create_test_student(
        client, db_session, "tutor_404@example.com", "Missing Topic Student"
    )

    with patch.object(settings, "GEMINI_API_KEY", "mock-test-key"):
        resp = client.post(
            "/api/v1/tutor/chat",
            json={"topic_id": 999999, "message": "Hello"},
            headers=student["headers"],
        )
        assert resp.status_code == 404
        assert "not found" in resp.json()["detail"].lower()


# ── 8. Voice Session Creation ─────────────────────────────────────────────────
def test_create_voice_session_success_and_auth(client: TestClient, db_session: Session):
    """Verify voice session creation requires auth and returns ephemeral token."""
    # 401 unauthenticated
    resp_unauth = client.post("/api/v1/tutor/voice/session", json={"topic_id": 1})
    assert resp_unauth.status_code == 401

    student = create_test_student(
        client, db_session, "voice_session_test@example.com", "Voice Student"
    )
    topic = db_session.query(Topic).first()

    # Success with auth
    resp = client.post(
        "/api/v1/tutor/voice/session",
        json={"topic_id": topic.id},
        headers=student["headers"],
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "session_id" in data
    assert "session_token" in data
    assert "/api/v1/tutor/voice/ws" in data["ws_endpoint"]
    assert data["topic_id"] == topic.id
    assert data["board"] == "ISC"
    assert data["grade"] == "Class 11"
    assert data["expires_in_seconds"] == 900


# ── 9. Voice WebSocket Full-Duplex Turn-Taking & Interruption ─────────────────
def test_voice_websocket_lifecycle_and_interruption(client: TestClient, db_session: Session):
    """Verify WebSocket handshake, interim transcript, barge-in, and spoken response generation."""
    student = create_test_student(
        client, db_session, "voice_ws_test@example.com", "Voice WS Student"
    )
    topic = db_session.query(Topic).first()

    # 1. Create session to get ephemeral token
    resp_session = client.post(
        "/api/v1/tutor/voice/session",
        json={"topic_id": topic.id},
        headers=student["headers"],
    )
    assert resp_session.status_code == 200
    token = resp_session.json()["session_token"]

    mock_gemini_resp = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": "The 1853 railway between Bombay and Thane changed colonial trade dramatically. Does that answer your question?"
                        }
                    ]
                }
            }
        ]
    }

    mock_client_instance = MagicMock()
    mock_client_instance.__enter__.return_value = mock_client_instance
    mock_client_instance.post.return_value = MagicMock(
        status_code=200,
        json=lambda: mock_gemini_resp,
    )

    with patch.object(settings, "GEMINI_API_KEY", "mock-voice-key"):
        with patch("app.services.tutor_service.httpx.Client", return_value=mock_client_instance):
            with client.websocket_connect(f"/api/v1/tutor/voice/ws?token={token}") as ws:
                # Expect session_ready event
                ready_event = ws.receive_json()
                assert ready_event["type"] == "session_ready"
                assert ready_event["state"] == "listening"
                assert ready_event["topic_id"] == topic.id

                # Test ping / pong
                ws.send_json({"type": "ping"})
                pong = ws.receive_json()
                assert pong["type"] == "pong"

                # Test interim speech echo
                ws.send_json({"type": "speech_interim", "text": "What about Dalhousie"})
                echo = ws.receive_json()
                assert echo["type"] == "transcript_echo"
                assert echo["text"] == "What about Dalhousie"

                # Test barge-in / interrupt
                ws.send_json({"type": "interrupt"})
                interrupt_ack = ws.receive_json()
                assert interrupt_ack["type"] == "tutor_interrupted"
                assert interrupt_ack["state"] == "listening"

                # Test final speech turn
                ws.send_json({"type": "speech_final", "text": "Tell me about the 1853 railway."})
                thinking_event = ws.receive_json()
                assert thinking_event["type"] == "thinking"

                speaking_event = ws.receive_json()
                assert speaking_event["type"] == "speaking"
                assert "1853 railway between Bombay and Thane" in speaking_event["text"]
                assert speaking_event["is_out_of_scope"] is False


# ── 10. Model Prefix Normalization & Clean URL ────────────────────────────────
def test_tutor_chat_model_prefix_normalization(client: TestClient, db_session: Session):
    """Verify models/ prefix in AI_TUTOR_MODEL is stripped to avoid double path prefix."""
    student = create_test_student(
        client, db_session, "model_norm@example.com", "Norm Student"
    )
    topic = db_session.query(Topic).first()

    mock_gemini_resp = {
        "candidates": [{"content": {"parts": [{"text": "Model normalization works."}]}}]
    }
    mock_client_instance = MagicMock()
    mock_client_instance.__enter__.return_value = mock_client_instance
    mock_client_instance.post.return_value = MagicMock(
        status_code=200,
        json=lambda: mock_gemini_resp,
    )

    with patch.object(settings, "GEMINI_API_KEY", "mock-test-key"):
        with patch.object(settings, "AI_TUTOR_MODEL", "models/gemini-3.5-flash"):
            with patch("app.services.tutor_service.httpx.Client", return_value=mock_client_instance):
                resp = client.post(
                    "/api/v1/tutor/chat",
                    json={"topic_id": topic.id, "message": "Test normalization"},
                    headers=student["headers"],
                )

                assert resp.status_code == 200
                assert resp.json()["reply"] == "Model normalization works."
                called_url = mock_client_instance.post.call_args[0][0]
                assert "models/models/" not in called_url
                assert "models/gemini-3.5-flash:generateContent" in called_url


# ── 11. Upstream Model Unavailable (404) ──────────────────────────────────────
def test_tutor_chat_upstream_model_not_found_404(client: TestClient, db_session: Session):
    """Verify 404 from upstream Gemini translates into 502 with clear diagnostic message."""
    student = create_test_student(
        client, db_session, "model_404@example.com", "Model 404 Student"
    )
    topic = db_session.query(Topic).first()

    mock_client_instance = MagicMock()
    mock_client_instance.__enter__.return_value = mock_client_instance
    mock_client_instance.post.return_value = MagicMock(
        status_code=404,
        text='{"error": {"code": 404, "message": "models/gemini-deprecated is not found"}}',
    )

    with patch.object(settings, "GEMINI_API_KEY", "mock-test-key"):
        with patch("app.services.tutor_service.httpx.Client", return_value=mock_client_instance):
            resp = client.post(
                "/api/v1/tutor/chat",
                json={"topic_id": topic.id, "message": "Test 404 model"},
                headers=student["headers"],
            )

            assert resp.status_code == 502
            assert "unavailable or not supported" in resp.json()["detail"].lower()


# ── 12. Upstream High Demand (503) ───────────────────────────────────────────
def test_tutor_chat_upstream_high_demand_503(client: TestClient, db_session: Session):
    """Verify 503 from upstream Gemini translates into friendly retry message."""
    student = create_test_student(
        client, db_session, "model_503@example.com", "Model 503 Student"
    )
    topic = db_session.query(Topic).first()

    mock_client_instance = MagicMock()
    mock_client_instance.__enter__.return_value = mock_client_instance
    mock_client_instance.post.return_value = MagicMock(
        status_code=503,
        text='{"error": {"code": 503, "message": "This model is currently experiencing high demand"}}',
    )

    with patch.object(settings, "GEMINI_API_KEY", "mock-test-key"):
        with patch("app.services.tutor_service.httpx.Client", return_value=mock_client_instance):
            resp = client.post(
                "/api/v1/tutor/chat",
                json={"topic_id": topic.id, "message": "Test 503 model"},
                headers=student["headers"],
            )

            assert resp.status_code == 503
            assert "high demand" in resp.json()["detail"].lower()


# ── 13. Upstream Invalid Key (API_KEY_INVALID) ───────────────────────────────
def test_tutor_chat_invalid_api_key_503(client: TestClient, db_session: Session):
    """Verify invalid API key error returns clean 503 instruction."""
    student = create_test_student(
        client, db_session, "model_invalid_key@example.com", "Invalid Key Student"
    )
    topic = db_session.query(Topic).first()

    mock_client_instance = MagicMock()
    mock_client_instance.__enter__.return_value = mock_client_instance
    mock_client_instance.post.return_value = MagicMock(
        status_code=400,
        text='{"error": {"code": 400, "message": "API_KEY_INVALID", "status": "INVALID_ARGUMENT"}}',
    )

    with patch.object(settings, "GEMINI_API_KEY", "invalid-key-here"):
        with patch("app.services.tutor_service.httpx.Client", return_value=mock_client_instance):
            resp = client.post(
                "/api/v1/tutor/chat",
                json={"topic_id": topic.id, "message": "Test invalid key"},
                headers=student["headers"],
            )

            assert resp.status_code == 503
            assert "authentication failed" in resp.json()["detail"].lower()


