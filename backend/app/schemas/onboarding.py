from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


# ── Step 1: Board & Grade ─────────────────────────────────────────────────────
class Step1BoardClass(BaseModel):
    """Step 1 request schema: Academic board and grade."""
    board: str = Field(..., min_length=2, max_length=100)
    grade: str = Field(..., min_length=1, max_length=50)
    academic_stream: Optional[str] = Field(None, max_length=100)


class StudentProfileResponse(BaseModel):
    """Step 1 profile response schema."""
    id: int
    user_id: int
    board: str
    grade: str
    academic_stream: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ── Step 2: Stream & Subjects ─────────────────────────────────────────────────
class Step2StreamSubjects(BaseModel):
    """Step 2 request schema: Academic stream and enrolled subjects."""
    academic_stream: Optional[str] = Field(None, max_length=100)
    subjects: List[str] = Field(..., min_length=1)

    @field_validator("subjects")
    @classmethod
    def clean_subjects(cls, v: List[str]) -> List[str]:
        cleaned = [s.strip() for s in v if s.strip()]
        if not cleaned:
            raise ValueError("At least one non-empty subject must be selected")
        # Preserve order while removing duplicates
        seen = set()
        unique = []
        for s in cleaned:
            if s.lower() not in seen:
                seen.add(s.lower())
                unique.append(s)
        return unique


class SubjectSelectionResponse(BaseModel):
    """Subject selection response schema."""
    id: int
    user_id: int
    subject_name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ── Step 3: Preferences & Goals ───────────────────────────────────────────────
class Step3PreferencesGoals(BaseModel):
    """Step 3 request schema: Learning style preference and study goals."""
    preferred_style: str = Field(..., min_length=2, max_length=100)
    goals: List[str] = Field(..., min_length=1)
    target_score: Optional[str] = Field(None, max_length=50)
    target_exam: Optional[str] = Field(None, max_length=100)

    @field_validator("goals")
    @classmethod
    def clean_goals(cls, v: List[str]) -> List[str]:
        cleaned = [g.strip() for g in v if g.strip()]
        if not cleaned:
            raise ValueError("At least one study goal must be provided")
        return cleaned


class LearningPreferenceResponse(BaseModel):
    """Learning preference response schema."""
    id: int
    user_id: int
    preferred_style: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StudyGoalResponse(BaseModel):
    """Study goal response schema."""
    id: int
    user_id: int
    goal_text: str
    target_score: Optional[str] = None
    target_exam: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ── Step 4: Study Schedule ────────────────────────────────────────────────────
class Step4Schedule(BaseModel):
    """Step 4 request schema: Daily target hours, study slot, available days."""
    daily_target_hours: float = Field(..., gt=0.0, le=24.0)
    preferred_slot: str = Field(..., min_length=2, max_length=100)
    available_days: List[str] = Field(..., min_length=1)

    @field_validator("available_days")
    @classmethod
    def validate_days(cls, v: List[str]) -> List[str]:
        valid_days = {
            "monday", "tuesday", "wednesday", "thursday",
            "friday", "saturday", "sunday"
        }
        cleaned = []
        for day in v:
            day_clean = day.strip()
            if day_clean.lower() not in valid_days:
                raise ValueError(f"Invalid weekday name: {day}")
            cleaned.append(day_clean.capitalize())
        return list(dict.fromkeys(cleaned))  # unique days


class StudyScheduleResponse(BaseModel):
    """Study schedule response schema."""
    id: int
    user_id: int
    daily_target_hours: float
    preferred_slot: str
    available_days: List[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ── Onboarding Completion Status ──────────────────────────────────────────────
class OnboardingStatusResponse(BaseModel):
    """Comprehensive status for 4-step onboarding progress."""
    is_onboarded: bool
    step1_completed: bool
    step2_completed: bool
    step3_completed: bool
    step4_completed: bool
    current_step: int
