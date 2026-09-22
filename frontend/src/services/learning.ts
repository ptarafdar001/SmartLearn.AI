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
