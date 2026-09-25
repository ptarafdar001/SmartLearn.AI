from datetime import datetime
import re
from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


class UserBase(BaseModel):
    """Base schema with common user fields."""
    email: str
    full_name: str
    role: str = "student"

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        clean = v.strip().lower()
        if not EMAIL_REGEX.match(clean):
            raise ValueError("Invalid email format")
        return clean

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        clean = v.strip().lower()
        if clean not in {"student", "teacher", "parent"}:
            raise ValueError("Role must be 'student', 'teacher', or 'parent'")
        return clean


class UserCreate(UserBase):
    """Registration request schema."""
    password: str
    terms_accepted: bool = True

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v

    @field_validator("terms_accepted")
    @classmethod
    def validate_terms(cls, v: bool) -> bool:
        if not v:
            raise ValueError("Terms and conditions must be accepted")
        return v


class UserLogin(BaseModel):
    """Login credentials request schema."""
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        clean = v.strip().lower()
        if not EMAIL_REGEX.match(clean):
            raise ValueError("Invalid email format")
        return clean


class Token(BaseModel):
    """JWT response schema."""
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Decoded JWT payload data."""
    sub: Optional[str] = None
    exp: Optional[int] = None
    role: Optional[str] = None


class UserResponse(BaseModel):
    """Public user response schema; never exposes hashed_password."""
    id: int
    email: str
    full_name: str
    role: str
    is_active: bool
    is_onboarded: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
