with open('frontend/src/types/onboarding.ts', 'r', encoding='utf-8') as f:
    content = f.read()

addition = """
export interface OnboardingSelectionsResponse {
  user_id: number;
  full_name: string;
  email: string;
  board?: string | null;
  grade?: string | null;
  academic_stream?: string | null;
  enrolled_subjects: string[];
  preferred_learning_style?: string | null;
  study_goals: string[];
  daily_target_hours?: number | null;
  preferred_slot?: string | null;
  slot_start_time?: string | null;
  available_days: string[];
  reminder_email?: string | null;
  email_reminders_enabled: boolean;
  is_onboarded: boolean;
}
"""

if 'interface OnboardingSelectionsResponse' not in content:
    content = content + addition
    with open('frontend/src/types/onboarding.ts', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Added OnboardingSelectionsResponse to frontend/src/types/onboarding.ts")
else:
    print("Already exists in frontend/src/types/onboarding.ts")

