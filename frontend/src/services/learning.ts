import { apiClient } from './api';
import type {
  ChapterSummary,
  ContinueLearningItem,
  DashboardOverview,
  ProgressUpdateRequest,
  RecommendationsResponse,
  SubjectDetail,
  SubjectSummary,
  TopicDetail,
  TopicProgressResponse,
} from '../types/learning';

export async function fetchEnrolledSubjects(): Promise<SubjectSummary[]> {
  return apiClient<SubjectSummary[]>('/learning/subjects', {
    method: 'GET',
    requiresAuth: true,
  });
}

export async function fetchSubjectDetail(subjectId: number): Promise<SubjectDetail> {
  return apiClient<SubjectDetail>(`/learning/subjects/${subjectId}`, {
    method: 'GET',
    requiresAuth: true,
  });
}

export async function fetchChapterDetail(chapterId: number): Promise<ChapterSummary> {
  return apiClient<ChapterSummary>(`/learning/chapters/${chapterId}`, {
    method: 'GET',
    requiresAuth: true,
  });
}

export async function fetchTopicDetail(topicId: number): Promise<TopicDetail> {
  return apiClient<TopicDetail>(`/learning/topics/${topicId}`, {
    method: 'GET',
    requiresAuth: true,
  });
}

export async function saveTopicProgress(
  topicId: number,
  data: ProgressUpdateRequest
): Promise<TopicProgressResponse> {
  return apiClient<TopicProgressResponse>(`/learning/topics/${topicId}/progress`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
    requiresAuth: true,
  });
}

export async function fetchContinueLearning(): Promise<ContinueLearningItem | null> {
  return apiClient<ContinueLearningItem | null>('/learning/continue', {
    method: 'GET',
    requiresAuth: true,
  });
}

export async function fetchRecommendations(): Promise<RecommendationsResponse> {
  return apiClient<RecommendationsResponse>('/learning/recommendations', {
    method: 'GET',
    requiresAuth: true,
  });
}

export async function fetchDashboardOverview(): Promise<DashboardOverview> {
  return apiClient<DashboardOverview>('/analytics/overview', {
    method: 'GET',
    requiresAuth: true,
  });
}

export async function fetchTopicObjectives(topicId: number) {
  return apiClient<any[]>(`/learning/topics/${topicId}/objectives`, {
    method: 'GET',
    requiresAuth: true,
  });
}

export async function fetchTopicPYQs(topicId: number) {
  return apiClient<any[]>(`/learning/topics/${topicId}/pyqs`, {
    method: 'GET',
    requiresAuth: true,
  });
}

export async function fetchSubjectPYQs(subjectId: number) {
  return apiClient<any[]>(`/learning/subjects/${subjectId}/pyqs`, {
    method: 'GET',
    requiresAuth: true,
  });
}

export async function fetchPracticeQuestions(topicId: number, difficulty?: string) {
  const query = difficulty ? `?difficulty=${encodeURIComponent(difficulty)}` : '';
  return apiClient<any[]>(`/learning/topics/${topicId}/practice-questions${query}`, {
    method: 'GET',
    requiresAuth: true,
  });
}

export async function generatePracticeQuestions(topicId: number, difficulty?: string) {
  const query = difficulty ? `?difficulty=${encodeURIComponent(difficulty)}` : '';
  return apiClient<any[]>(`/learning/topics/${topicId}/practice-questions/generate${query}`, {
    method: 'POST',
    requiresAuth: true,
  });
}

export async function submitPracticeAttempt(questionId: number, userAnswer: string) {
  return apiClient<any>(`/learning/practice-questions/${questionId}/attempt`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_answer: userAnswer }),
    requiresAuth: true,
  });
}

export async function fetchMyPracticeAttempts(topicId?: number, limit: number = 100) {
  const query = topicId ? `?topic_id=${topicId}&limit=${limit}` : `?limit=${limit}`;
  return apiClient<any[]>(`/learning/practice-questions/my-attempts${query}`, {
    method: 'GET',
    requiresAuth: true,
  });
}

export async function fetchTopicStudyNotes(topicId: number, notesType: string = 'comprehensive') {
  return apiClient<any>(`/learning/topics/${topicId}/notes?type=${encodeURIComponent(notesType)}`, {
    method: 'GET',
    requiresAuth: true,
  });
}

export async function regenerateTopicStudyNotes(topicId: number, notesType: string = 'comprehensive') {
  return apiClient<any>(`/learning/topics/${topicId}/notes/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ notes_type: notesType }),
    requiresAuth: true,
  });
}

