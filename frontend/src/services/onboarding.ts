import { apiClient } from './api';
import type {
  Step1BoardClassRequest,
  Step2StreamSubjectsRequest,
  Step3PreferencesGoalsRequest,
  Step4ScheduleRequest,
  StudentProfileResponse,
  SubjectSelectionResponse,
  Step3Response,
  StudyScheduleResponse,
  OnboardingStatusResponse,
} from '../types/onboarding';

export const onboardingService = {
  async submitStep1(data: Step1BoardClassRequest): Promise<StudentProfileResponse> {
    return apiClient<StudentProfileResponse>('/users/onboarding/step1', {
      method: 'POST',
      body: JSON.stringify(data),
      requiresAuth: true,
    });
  },

  async submitStep2(data: Step2StreamSubjectsRequest): Promise<SubjectSelectionResponse[]> {
    return apiClient<SubjectSelectionResponse[]>('/users/onboarding/step2', {
      method: 'POST',
      body: JSON.stringify(data),
      requiresAuth: true,
    });
  },

  async submitStep3(data: Step3PreferencesGoalsRequest): Promise<Step3Response> {
    return apiClient<Step3Response>('/users/onboarding/step3', {
      method: 'POST',
      body: JSON.stringify(data),
      requiresAuth: true,
    });
  },

  async submitStep4(data: Step4ScheduleRequest): Promise<StudyScheduleResponse> {
    return apiClient<StudyScheduleResponse>('/users/onboarding/step4', {
      method: 'POST',
      body: JSON.stringify(data),
      requiresAuth: true,
    });
  },

  async getOnboardingStatus(): Promise<OnboardingStatusResponse> {
    return apiClient<OnboardingStatusResponse>('/users/onboarding/status', {
      method: 'GET',
      requiresAuth: true,
    });
  },
};
