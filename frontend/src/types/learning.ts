export type ResourceType =
  | 'text'
  | 'notes'
  | 'video'
  | 'quiz'
  | 'practice'
  | 'audio'
  | 'interactive'
  | 'revision';

export type ProgressStatus = 'not_started' | 'in_progress' | 'completed';

export interface LearningResource {
  id: number;
  topic_id: number;
  title: string;
  resource_type: ResourceType;
  provider: string;
  source_name?: string | null;
  source_url?: string | null;
  external_id?: string | null;
  content_url?: string | null;
  text_content?: string | null;
  duration_seconds?: number | null;
  language: string;
  order_index: number;
  is_active: boolean;
  is_verified: boolean;
  verified_at?: string | null;
}

export interface TopicProgressSummary {
  status: ProgressStatus;
  progress_percentage: number;
  time_spent_seconds: number;
  last_accessed_at?: string | null;
  completed_at?: string | null;
}

export interface TopicSummary {
  id: number;
  chapter_id: number;
  topic_number: number;
  title: string;
  description?: string | null;
  estimated_minutes: number;
  progress?: TopicProgressSummary | null;
}

export interface ChapterSummary {
  id: number;
  subject_id: number;
  chapter_number: number;
  title: string;
  description?: string | null;
  total_topics: number;
  completed_topics: number;
  progress_percentage: number;
  topics: TopicSummary[];
}

export interface SubjectSummary {
  id: number;
  code: string;
  name: string;
  subject_name: string;
  board: string;
  grade: string;
  academic_stream?: string | null;
  category: string;
  description?: string | null;
  total_chapters: number;
  total_topics: number;
  chapter_count?: number | null;
  topic_count?: number | null;
  completed_topics: number;
  progress_percentage?: number | null;
}

export interface SubjectDetail {
  id: number;
  code: string;
  name: string;
  board: string;
  grade: string;
  academic_stream?: string | null;
  category: string;
  description?: string | null;
  total_chapters: number;
  total_topics: number;
  completed_topics: number;
  progress_percentage: number;
  chapters: ChapterSummary[];
}

export interface TopicDetail {
  id: number;
  chapter_id: number;
  chapter_title: string;
  chapter_number: number;
  subject_id: number;
  subject_name: string;
  topic_number: number;
  title: string;
  description?: string | null;
  estimated_minutes: number;
  progress?: TopicProgressSummary | null;
  user_progress?: TopicProgressSummary | null;
  resources: LearningResource[];
}

export interface ProgressUpdateRequest {
  status: ProgressStatus;
  progress_percentage: number;
  time_spent_seconds: number;
}

export interface TopicProgressResponse {
  id: number;
  user_id: number;
  topic_id: number;
  status: ProgressStatus;
  progress_percentage: number;
  time_spent_seconds: number;
  last_accessed_at?: string | null;
  completed_at?: string | null;
}

export interface ContinueLearningItem {
  topic_id: number;
  topic_title: string;
  chapter_id: number;
  chapter_title: string;
  subject_id: number;
  subject_name: string;
  status: ProgressStatus;
  progress_percentage: number;
  estimated_minutes: number;
  last_accessed_at?: string | null;
}

export interface StudyTargetSummary {
  daily_target_hours: number;
  preferred_slot: string;
  available_days: string[];
}

export interface DashboardOverview {
  user_id: number;
  full_name: string;
  board?: string | null;
  grade?: string | null;
  academic_stream?: string | null;
  preferred_learning_style?: string | null;
  study_target?: StudyTargetSummary | null;
  goals: string[];
  enrolled_subjects: string[];
  total_enrolled_subjects: number;
  study_streak_days?: number | null;
  questions_solved?: number | null;
  overall_progress_percentage?: number | null;
}

export interface RecommendationItem {
  id: string;
  title: string;
  description: string;
  subject: string;
  learning_style?: string | null;
  recommendation_type: string;
}

export interface RecommendationsResponse {
  user_id: number;
  recommendations: RecommendationItem[];
  total_count: number;
}
