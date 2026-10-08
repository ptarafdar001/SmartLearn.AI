import { apiClient } from './api';
import type { TutorChatPayload, TutorChatResponse, VoiceSessionResponse } from '../types/tutor';

export async function askAITutor(payload: TutorChatPayload): Promise<TutorChatResponse> {
  return apiClient<TutorChatResponse>('/tutor/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
    requiresAuth: true,
  });
}

export async function createVoiceSession(topicId: number): Promise<VoiceSessionResponse> {
  return apiClient<VoiceSessionResponse>('/tutor/voice/session', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ topic_id: topicId }),
    requiresAuth: true,
  });
}

