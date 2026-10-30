with open('backend/app/services/onboarding_service.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Add get_current_selections to OnboardingService
if "get_current_selections" not in code:
    import_target = "from app.schemas.onboarding import ("
    import_replacement = "from app.schemas.onboarding import (\n    OnboardingSelectionsResponse,"
    assert import_target in code, "import_target not found"
    code = code.replace(import_target, import_replacement, 1)

    new_method = """
    @staticmethod
    def get_current_selections(db: Session, user_id: int) -> OnboardingSelectionsResponse:
        \"\"\"Retrieve the single unified source of truth for the student\'s onboarding data.\"\"\"
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            raise ValueError("User not found")

        profile = OnboardingRepository.get_student_profile(db, user_id)
        subjects = OnboardingRepository.get_subject_selections(db, user_id)
        preference = OnboardingRepository.get_learning_preference(db, user_id)
        goals = OnboardingRepository.get_study_goals(db, user_id)
        schedule = OnboardingRepository.get_study_schedule(db, user_id)

        subject_names = [s.subject_name for s in subjects]
        goal_texts = [g.goal_text for g in goals]

        return OnboardingSelectionsResponse(
            user_id=user.id,
            full_name=user.full_name or "",
            email=user.email,
            board=profile.board if profile else None,
            grade=profile.grade if profile else None,
            academic_stream=profile.academic_stream if profile else None,
            enrolled_subjects=subject_names,
            preferred_learning_style=preference.preferred_style if preference else None,
            study_goals=goal_texts,
            daily_target_hours=schedule.daily_target_hours if schedule else None,
            preferred_slot=schedule.preferred_slot if schedule else None,
            slot_start_time=getattr(schedule, 'slot_start_time', None) if schedule else None,
            available_days=schedule.available_days if schedule else [],
            reminder_email=getattr(schedule, 'reminder_email', None) if schedule else None,
            email_reminders_enabled=getattr(schedule, 'email_reminders_enabled', True) if schedule else True,
            is_onboarded=user.is_onboarded,
        )
"""
    code = code.rstrip() + new_method
    with open('backend/app/services/onboarding_service.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("Added get_current_selections to OnboardingService")
else:
    print("get_current_selections already in OnboardingService")

