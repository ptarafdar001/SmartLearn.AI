"""
Comprehensive tests for SmartLearn.AI multi-provider AI failover system:
- Primary provider (Gemini) success
- Quota exhaustion (429) on primary with graceful fallback to Groq / OpenRouter
- Temporary outage (503 / 502) on primary with fallback success
- All providers exhausted returning friendly error without exposing secrets
- Invalid credentials handling (disables bad provider without spamming)
- Unsupported image input (never silently downgrading image to text)
- Timeout handling and bounded retries
- Preservation of curriculum context, verified source citations, and syllabus objectives across providers.
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
from app.models.learning import Chapter, Subject, Topic
from app.repositories.user_repository import UserRepository
from app.services.llm.base import ProviderErrorCode, ProviderException
from app.services.llm.failover_service import LLMFailoverService

settings = get_settings()


def get_isc_topic(db: Session) -> Topic:
    topic = (
        db.query(Topic)
        .join(Chapter, Topic.chapter_id == Chapter.id)
        .join(Subject, Chapter.subject_id == Subject.id)
        .filter(Subject.code == "isc-11-hist")
        .first()
    )
    if not topic:
        topic = db.query(Topic).filter(Topic.id == 44).first()
    assert topic is not None
    return topic


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.fixture
def db_session():
    session = SessionLocal()
    try:
        seed_isc_history_curriculum(session)
        LLMFailoverService.reset_provider_health()
        yield session
    finally:
        session.rollback()
        session.close()


from app.services.onboarding_service import OnboardingService
from app.schemas.onboarding import (
    Step1BoardClass,
    Step2StreamSubjects,
    Step3PreferencesGoals,
    Step4Schedule,
)


def create_test_student(client: TestClient, db: Session, email: str, full_name: str):
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
        db, user_id, Step1BoardClass(board="ISC", grade="Class 11", academic_stream="Humanities")
    )
    OnboardingService.save_step2_stream_subjects(
        db, user_id, Step2StreamSubjects(subjects=["History"])
    )
    OnboardingService.save_step3_preferences_goals(
        db,
        user_id,
        Step3PreferencesGoals(
            preferred_style="Interactive",
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
    return {"id": user_id, "token": token, "headers": headers}


# ── 1. Primary Provider Success (Gemini) ──────────────────────────────────────
def test_primary_provider_success(client: TestClient, db_session: Session):
    """Verify Gemini as primary provider returns grounded response."""
    student = create_test_student(client, db_session, "primary_ok@example.com", "Primary Student")
    topic = get_isc_topic(db_session)

    mock_client = MagicMock()
    mock_client.__enter__.return_value = mock_client
    mock_client.post.return_value = MagicMock(
        status_code=200,
        json=lambda: {
            "candidates": [{"content": {"parts": [{"text": "Primary response on Colonial Railways."}]}}]
        },
    )

    with patch.object(settings, "GEMINI_API_KEY", "mock-gemini-key"):
        with patch.object(settings, "GROQ_API_KEY", "mock-groq-key"):
            with patch("app.services.llm.gemini_provider.httpx.Client", return_value=mock_client):
                resp = client.post(
                    "/api/v1/tutor/chat",
                    json={"topic_id": topic.id, "message": "Explain Lord Dalhousie's railways"},
                    headers=student["headers"],
                )
                assert resp.status_code == 200
                data = resp.json()
                assert "Primary response on Colonial Railways" in data["reply"]
                assert data["topic_id"] == topic.id
                assert len(data["grounded_sources"]) > 0


# ── 2. Quota Exhaustion (429) Fallback to Groq ────────────────────────────────
def test_quota_exhaustion_fallback_to_groq(client: TestClient, db_session: Session):
    """When Gemini returns 429 RESOURCE_EXHAUSTED, failover seamlessly calls Groq."""
    student = create_test_student(client, db_session, "quota_fb@example.com", "Quota Student")
    topic = get_isc_topic(db_session)

    def mock_post(url, *args, **kwargs):
        if "generativelanguage.googleapis.com" in str(url):
            return MagicMock(status_code=429, text='{"error": {"code": 429, "message": "RESOURCE_EXHAUSTED"}}')
        elif "api.groq.com" in str(url):
            return MagicMock(
                status_code=200,
                json=lambda: {
                    "choices": [
                        {
                            "message": {
                                "content": "Groq fallback response: The Railway Guarantee System assured 5% interest to British private companies."
                            },
                            "finish_reason": "stop",
                        }
                    ]
                },
            )
        return MagicMock(status_code=500, text="Unexpected URL")

    mock_client = MagicMock()
    mock_client.__enter__.return_value = mock_client
    mock_client.post.side_effect = mock_post

    with patch.object(settings, "GEMINI_API_KEY", "mock-gemini-key"):
        with patch.object(settings, "GROQ_API_KEY", "mock-groq-key"):
            with patch("app.services.llm.gemini_provider.httpx.Client", return_value=mock_client):
                with patch("app.services.llm.openai_compatible_provider.httpx.Client", return_value=mock_client):
                    resp = client.post(
                        "/api/v1/tutor/chat",
                        json={"topic_id": topic.id, "message": "Explain the Railway Guarantee System"},
                        headers=student["headers"],
                    )
                    assert resp.status_code == 200
                    data = resp.json()
                    assert "Groq fallback response" in data["reply"]
                    # Context & provenance preserved
                    assert data["topic_id"] == topic.id
                    assert data["subject_name"] == "History"
                    assert len(data["grounded_sources"]) > 0


# ── 3. Temporary Outage (503) Fallback to OpenRouter ──────────────────────────
def test_temporary_outage_fallback(client: TestClient, db_session: Session):
    """When Gemini and Groq fail with 503, failover routes to OpenRouter."""
    student = create_test_student(client, db_session, "outage_fb@example.com", "Outage Student")
    topic = get_isc_topic(db_session)

    def mock_post(url, *args, **kwargs):
        if "generativelanguage.googleapis.com" in str(url):
            return MagicMock(status_code=503, text='{"error": "Service Unavailable"}')
        elif "api.groq.com" in str(url):
            return MagicMock(status_code=502, text='{"error": "Bad Gateway"}')
        elif "openrouter.ai" in str(url):
            return MagicMock(
                status_code=200,
                json=lambda: {
                    "choices": [
                        {
                            "message": {
                                "content": "OpenRouter fallback response: The telegraph system facilitated military intelligence."
                            },
                            "finish_reason": "stop",
                        }
                    ]
                },
            )
        return MagicMock(status_code=500, text="Unexpected URL")

    mock_client = MagicMock()
    mock_client.__enter__.return_value = mock_client
    mock_client.post.side_effect = mock_post

    with patch.object(settings, "GEMINI_API_KEY", "mock-gemini-key"):
        with patch.object(settings, "GROQ_API_KEY", "mock-groq-key"):
            with patch.object(settings, "OPENROUTER_API_KEY", "mock-openrouter-key"):
                with patch("app.services.llm.gemini_provider.httpx.Client", return_value=mock_client):
                    with patch("app.services.llm.openai_compatible_provider.httpx.Client", return_value=mock_client):
                        resp = client.post(
                            "/api/v1/tutor/chat",
                            json={"topic_id": topic.id, "message": "Explain telegraph communications"},
                            headers=student["headers"],
                        )
                        assert resp.status_code == 200
                        data = resp.json()
                        assert "OpenRouter fallback response" in data["reply"]


# ── 4. All Providers Exhausted Returns User-Friendly Error ────────────────────
def test_all_providers_exhausted(client: TestClient, db_session: Session):
    """When all configured providers fail with quota/outages, clean 429/503 is returned."""
    student = create_test_student(client, db_session, "all_exhausted@example.com", "Exhausted Student")
    topic = get_isc_topic(db_session)

    mock_client = MagicMock()
    mock_client.__enter__.return_value = mock_client
    mock_client.post.return_value = MagicMock(
        status_code=429,
        text='{"error": "Daily quota limit reached"}',
    )

    with patch.object(settings, "GEMINI_API_KEY", "mock-gemini-key"):
        with patch.object(settings, "GROQ_API_KEY", "mock-groq-key"):
            with patch("app.services.llm.gemini_provider.httpx.Client", return_value=mock_client):
                with patch("app.services.llm.openai_compatible_provider.httpx.Client", return_value=mock_client):
                    resp = client.post(
                        "/api/v1/tutor/chat",
                        json={"topic_id": topic.id, "message": "Hello"},
                        headers=student["headers"],
                    )
                    assert resp.status_code == 429
                    assert "quota or rate limit exceeded" in resp.json()["detail"].lower()


# ── 5. Invalid Credentials Disables Provider Without Infinite Retries ────────
def test_invalid_credentials_disables_bad_provider(client: TestClient, db_session: Session):
    """When a provider fails with AUTH_ERROR, failover skips it on subsequent calls."""
    student = create_test_student(client, db_session, "auth_disable@example.com", "Auth Student")
    topic = get_isc_topic(db_session)

    call_count = {"gemini": 0, "groq": 0}

    def mock_post(url, *args, **kwargs):
        if "generativelanguage.googleapis.com" in str(url):
            call_count["gemini"] += 1
            return MagicMock(status_code=400, text='{"error": {"message": "API_KEY_INVALID"}}')
        elif "api.groq.com" in str(url):
            call_count["groq"] += 1
            return MagicMock(
                status_code=200,
                json=lambda: {
                    "choices": [{"message": {"content": "Groq answers after Gemini auth failure."}}]
                },
            )
        return MagicMock(status_code=500, text="Unexpected")

    mock_client = MagicMock()
    mock_client.__enter__.return_value = mock_client
    mock_client.post.side_effect = mock_post

    with patch.object(settings, "GEMINI_API_KEY", "bad-gemini-key"):
        with patch.object(settings, "GROQ_API_KEY", "good-groq-key"):
            with patch("app.services.llm.gemini_provider.httpx.Client", return_value=mock_client):
                with patch("app.services.llm.openai_compatible_provider.httpx.Client", return_value=mock_client):
                    # Call 1: Gemini fails with AUTH_ERROR, Groq succeeds
                    resp1 = client.post(
                        "/api/v1/tutor/chat",
                        json={"topic_id": topic.id, "message": "First question"},
                        headers=student["headers"],
                    )
                    assert resp1.status_code == 200
                    assert "Groq answers" in resp1.json()["reply"]
                    assert call_count["gemini"] == 1
                    assert call_count["groq"] == 1

                    # Call 2: Gemini was marked auth_disabled=True, so it should NOT be called again!
                    resp2 = client.post(
                        "/api/v1/tutor/chat",
                        json={"topic_id": topic.id, "message": "Second question"},
                        headers=student["headers"],
                    )
                    assert resp2.status_code == 200
                    assert call_count["gemini"] == 1  # Not called again!
                    assert call_count["groq"] == 2


# ── 6. Unsupported Image Input Never Silently Downgraded ──────────────────────
def test_unsupported_image_modality_fails_fast(client: TestClient, db_session: Session):
    """When student attaches an image but no configured provider supports vision, 422 is returned."""
    student = create_test_student(client, db_session, "img_modality@example.com", "Image Modality Student")
    topic = get_isc_topic(db_session)

    fake_png = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    fake_b64 = f"data:image/png;base64,{base64.b64encode(fake_png).decode('utf-8')}"

    # Only Groq configured with NO vision model
    with patch.object(settings, "GEMINI_API_KEY", None):
        with patch.object(settings, "GROQ_API_KEY", "mock-groq-key"):
            with patch.object(settings, "GROQ_VISION_MODEL", None):
                resp = client.post(
                    "/api/v1/tutor/chat",
                    json={
                        "topic_id": topic.id,
                        "message": "What is in this diagram?",
                        "image_base64": fake_b64,
                    },
                    headers=student["headers"],
                )
                assert resp.status_code == 422
                assert "visual doubt solving with images is currently unavailable" in resp.json()["detail"].lower()


# ── 7. Timeout and Retry Limits ───────────────────────────────────────────────
def test_timeout_failover(client: TestClient, db_session: Session):
    """When Gemini times out, failover proceeds to Groq."""
    student = create_test_student(client, db_session, "timeout_fb@example.com", "Timeout Student")
    topic = get_isc_topic(db_session)

    def mock_post(url, *args, **kwargs):
        if "generativelanguage.googleapis.com" in str(url):
            raise httpx.TimeoutException("Gemini connection timed out")
        elif "api.groq.com" in str(url):
            return MagicMock(
                status_code=200,
                json=lambda: {
                    "choices": [{"message": {"content": "Groq answers after Gemini timeout."}}]
                },
            )
        return MagicMock(status_code=500, text="Unexpected")

    mock_client = MagicMock()
    mock_client.__enter__.return_value = mock_client
    mock_client.post.side_effect = mock_post

    with patch.object(settings, "GEMINI_API_KEY", "mock-gemini-key"):
        with patch.object(settings, "GROQ_API_KEY", "mock-groq-key"):
            with patch("app.services.llm.gemini_provider.httpx.Client", return_value=mock_client):
                with patch("app.services.llm.openai_compatible_provider.httpx.Client", return_value=mock_client):
                    resp = client.post(
                        "/api/v1/tutor/chat",
                        json={"topic_id": topic.id, "message": "Explain colonial taxation"},
                        headers=student["headers"],
                    )
                    assert resp.status_code == 200
                    assert "Groq answers after Gemini timeout" in resp.json()["reply"]


# ── 8. Voice Flow Preservation ────────────────────────────────────────────────
def test_voice_turn_failover_preservation(client: TestClient, db_session: Session):
    """Verify voice turn processing uses failover and preserves speech instructions."""
    student = create_test_student(client, db_session, "voice_fb@example.com", "Voice Student")
    topic = get_isc_topic(db_session)

    # Create voice session
    session_resp = client.post(
        "/api/v1/tutor/voice/session",
        json={"topic_id": topic.id},
        headers=student["headers"],
    )
    assert session_resp.status_code == 200

    def mock_post(url, *args, **kwargs):
        if "generativelanguage.googleapis.com" in str(url):
            return MagicMock(status_code=429, text='{"error": "Quota"}')
        elif "api.groq.com" in str(url):
            return MagicMock(
                status_code=200,
                json=lambda: {
                    "choices": [
                        {
                            "message": {
                                "content": "The railways connected inland cotton fields to major ports for export. Does that make sense?"
                            }
                        }
                    ]
                },
            )
        return MagicMock(status_code=500, text="Unexpected")

    mock_client = MagicMock()
    mock_client.__enter__.return_value = mock_client
    mock_client.post.side_effect = mock_post

    with patch.object(settings, "GEMINI_API_KEY", "mock-gemini-key"):
        with patch.object(settings, "GROQ_API_KEY", "mock-groq-key"):
            with patch("app.services.llm.gemini_provider.httpx.Client", return_value=mock_client):
                with patch("app.services.llm.openai_compatible_provider.httpx.Client", return_value=mock_client):
                    from app.services.tutor_service import TutorService

                    turn_result = TutorService.process_voice_turn(
                        db=db_session,
                        user_id=student["id"],
                        topic_id=topic.id,
                        speech_text="Why did the British connect the railways to ports?",
                        conversation_history=[],
                        client=mock_client,
                    )
                    assert "railways connected inland cotton fields" in turn_result["reply"]
                    assert turn_result["topic_id"] == topic.id
                    assert turn_result["subject_name"] == "History"
