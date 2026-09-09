from datetime import timedelta
import pytest
import jwt
from pydantic import ValidationError

from app.core.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)
from app.schemas.auth import UserCreate, UserLogin
from app.schemas.onboarding import (
    Step1BoardClass,
    Step2StreamSubjects,
    Step3PreferencesGoals,
    Step4Schedule,
)


# ── Password Security Tests ───────────────────────────────────────────────────
def test_password_hashing_and_verification():
    plain = "SuperSecurePassword123!"
    hashed = get_password_hash(plain)

    # Password must never equal the plaintext
    assert hashed != plain
    assert hashed.startswith("$2b$") or hashed.startswith("$2a$")

    # Correct verification
    assert verify_password(plain, hashed) is True

    # Incorrect password fails
    assert verify_password("WrongPassword123!", hashed) is False
    assert verify_password("", hashed) is False
    assert verify_password(plain, "") is False


def test_password_never_stored_plaintext():
    plain = "PlaintextPasswordTest"
    hashed = get_password_hash(plain)
    assert plain not in hashed


# ── JWT Token Tests ───────────────────────────────────────────────────────────
def test_jwt_creation_and_decoding():
    token = create_access_token(subject=42, extra_claims={"role": "student"})
    assert isinstance(token, str)

    payload = decode_access_token(token)
    assert payload["sub"] == "42"
    assert payload["role"] == "student"
    assert "exp" in payload
    assert "iat" in payload


def test_jwt_expired_token_rejection():
    expired_delta = timedelta(minutes=-10)
    token = create_access_token(subject=99, expires_delta=expired_delta)

    with pytest.raises(jwt.ExpiredSignatureError):
        decode_access_token(token)


def test_jwt_tampered_token_rejection():
    token = create_access_token(subject=100)
    tampered = token[:-4] + "fake"

    with pytest.raises(jwt.PyJWTError):
        decode_access_token(tampered)


# ── Pydantic Schema Validation Tests ──────────────────────────────────────────
def test_user_create_validation_success():
    payload = {
        "email": "Valid.Student@Example.COM",
        "password": "strongpassword123",
        "full_name": "Jane Doe",
        "role": "STUDENT",
        "terms_accepted": True,
    }
    user = UserCreate(**payload)
    assert user.email == "valid.student@example.com"
    assert user.role == "student"


def test_user_create_validation_failure_short_password():
    with pytest.raises(ValidationError):
        UserCreate(
            email="test@example.com",
            password="short",
            full_name="Test",
            terms_accepted=True,
        )


def test_user_create_validation_failure_invalid_email():
    with pytest.raises(ValidationError):
        UserCreate(
            email="not-an-email",
            password="validpassword123",
            full_name="Test",
            terms_accepted=True,
        )


def test_user_create_validation_failure_terms_not_accepted():
    with pytest.raises(ValidationError):
        UserCreate(
            email="test@example.com",
            password="validpassword123",
            full_name="Test",
            terms_accepted=False,
        )


def test_onboarding_schemas_validation():
    # Step 1
    step1 = Step1BoardClass(board="CBSE", grade="Class 10", academic_stream="Science")
    assert step1.board == "CBSE"

    # Step 2: Cleans whitespace and deduplicates
    step2 = Step2StreamSubjects(subjects=[" Physics ", "Mathematics", "Physics", "Chemistry"])
    assert step2.subjects == ["Physics", "Mathematics", "Chemistry"]

    # Step 3
    step3 = Step3PreferencesGoals(preferred_style="Visual", goals=["Target 90%+"])
    assert step3.preferred_style == "Visual"

    # Step 4: Validates weekday and normalizes capitalization
    step4 = Step4Schedule(
        daily_target_hours=2.5,
        preferred_slot="evening",
        available_days=["monday", "Wednesday"],
    )
    assert step4.available_days == ["Monday", "Wednesday"]

    # Step 4: Fails on invalid weekday
    with pytest.raises(ValidationError):
        Step4Schedule(
            daily_target_hours=2.5,
            preferred_slot="evening",
            available_days=["Funday"],
        )
