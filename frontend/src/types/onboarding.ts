export interface Step1BoardClassRequest {
  board: string;
  grade: string;
  academic_stream?: string | null;
}

export interface StudentProfileResponse {
  id: number;
  user_id: number;
  board: string;
  grade: string;
  academic_stream?: string | null;
  created_at: string;
}

export interface Step2StreamSubjectsRequest {
  academic_stream?: string | null;
  subjects: string[];
}

export interface SubjectSelectionResponse {
  id: number;
  user_id: number;
  subject_name: string;
  created_at: string;
}

export interface Step3PreferencesGoalsRequest {
  preferred_style: string;
  goals: string[];
  target_score?: string | null;
  target_exam?: string | null;
}

export interface LearningPreferenceResponse {
  id: number;
  user_id: number;
  preferred_style: string;
  created_at: string;
}

export interface StudyGoalResponse {
  id: number;
  user_id: number;
  goal_text: string;
  target_score?: string | null;
  target_exam?: string | null;
  created_at: string;
}

export interface Step3Response {
  learning_preference: LearningPreferenceResponse;
  study_goals: StudyGoalResponse[];
}

export interface Step4ScheduleRequest {
  daily_target_hours: number;
  preferred_slot: string;
  available_days: string[];
}

export interface StudyScheduleResponse {
  id: number;
  user_id: number;
  daily_target_hours: number;
  preferred_slot: string;
  available_days: string[];
  created_at: string;
}

export interface OnboardingStatusResponse {
  is_onboarded: boolean;
  step1_completed: boolean;
  step2_completed: boolean;
  step3_completed: boolean;
  step4_completed: boolean;
  current_step: number;
}
