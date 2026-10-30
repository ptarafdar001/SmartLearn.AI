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


export async function fetchRewardsSummary() {
  return apiClient<{
    xp_points: number;
    streak_days: number;
    badges: string[];
    level: number;
    next_level_xp: number;
    level_progress: number;
  }>('/learning/rewards/summary', {
    method: 'GET',
    requiresAuth: true,
  });
}

export interface DetailedAnalytics {
  overall_progress_percentage: number;
  studied_this_week_text: string;
  total_studied_hours: number;
  quiz_average: number;
  study_streak_days: number;
  xp_points: number;
  daily_target_hours: number;
  preferred_slot: string;
  slot_start_time: string;
  routine_days: string[];
  today_day_name: string;
  is_today_scheduled_day: boolean;
  hours_studied_today: number;
  has_met_today_target: boolean;
  days_data: { day: string; hours: number; height: number }[];
  chapter_progress: { title: string; progress: number; color: string }[];
  needs_practice: { topic_id: number; title: string; accuracy: number }[];
  is_behind_schedule: boolean;
  alert_info: { id: number; status: string; sent_at: string; subject: string; message: string } | null;
  total_questions_attempted: number;
  total_questions_correct: number;
  child_email: string;
  reminders_enabled: boolean;
}

export async function fetchDetailedAnalytics(period: string = 'week'): Promise<DetailedAnalytics> {
  return apiClient<DetailedAnalytics>(`/analytics/detailed?period=${encodeURIComponent(period)}`, {
    method: 'GET',
    requiresAuth: true,
  });
}

export async function triggerMissedSlotAlert(): Promise<{ status: string; message: string; recipient: string }> {
  return apiClient<{ status: string; message: string; recipient: string }>('/analytics/alerts/trigger-missed-slot', {
    method: 'POST',
    requiresAuth: true,
  });
}
