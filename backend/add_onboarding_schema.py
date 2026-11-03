with open('backend/app/schemas/onboarding.py', 'r', encoding='utf-8') as f:
    code = f.read()

addition = """

class OnboardingSelectionsResponse(BaseModel):
    \"\"\"Unified single source of truth for the student's complete onboarding profile.\"\"\"
    user_id: int
    full_name: str
    email: str
    board: Optional[str] = None
    grade: Optional[str] = None
    academic_stream: Optional[str] = None
    enrolled_subjects: List[str] = []
    preferred_learning_style: Optional[str] = None
    study_goals: List[str] = []
    daily_target_hours: Optional[float] = None
    preferred_slot: Optional[str] = None
    slot_start_time: Optional[str] = None
    available_days: List[str] = []
    reminder_email: Optional[str] = None
    email_reminders_enabled: bool = True
    is_onboarded: bool = False
"""

if "class OnboardingSelectionsResponse" not in code:
    code = code + addition
    with open('backend/app/schemas/onboarding.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("Added OnboardingSelectionsResponse to backend/app/schemas/onboarding.py")
else:
    print("Already exists")

