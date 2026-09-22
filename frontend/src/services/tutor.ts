import { apiClient } from './api';
import type { TutorChatPayload, TutorChatResponse } from '../types/tutor';

export async function askAITutor(payload: TutorChatPayload): Promise<TutorChatResponse> {
  return apiClient<TutorChatResponse>('/tutor/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
    requiresAuth: true,
  });
}
