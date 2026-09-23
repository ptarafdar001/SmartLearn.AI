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

export type CurriculumReadinessStatus =
  | 'content_available'
  | 'curriculum_verified'
  | 'in_preparation';

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
  curriculum_status?: CurriculumReadinessStatus | string | null;
  source_authority?: string | null;
  source_url?: string | null;
  syllabus_version?: string | null;
  status_message?: string | null;
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
  curriculum_status?: CurriculumReadinessStatus | string | null;
  source_authority?: string | null;
  source_url?: string | null;
  syllabus_version?: string | null;
  status_message?: string | null;
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

export interface LearningObjective {
  id: number;
  topic_id: number;
  code: string;
  description: string;
  taxonomy_level: string;
  is_core: boolean;
  is_verified: boolean;
}

export interface PreviousYearQuestion {
  id: number;
  subject_id: number;
  topic_id: number;
  board: string;
  grade: string;
  exam_year: number;
  paper_code: string;
  question_number: string;
  question_text: string;
  marks: number;
  marking_scheme?: string | null;
  source_name: string;
  source_url?: string | null;
  is_verified: boolean;
  verified_at?: string | null;
}

export interface PracticeOption {
  id: string;
  text: string;
}

export interface PracticeQuestion {
  id: number;
  topic_id: number;
  learning_objective_id?: number | null;
  question_text: string;
  question_type: string;
  options?: PracticeOption[] | null;
  correct_answer: string;
  explanation: string;
  difficulty: string;
  marks: number;
  is_ai_generated: boolean;
  generation_provenance?: any;
  created_at: string;
}

export interface PracticeAttemptResponse {
  id: number;
  question_id: number;
  question_type: string;
  user_answer: string;
  is_correct: boolean;
  marks_obtained: number;
  max_marks: number;
  feedback: string;
  explanation: string;
  attempted_at: string;
}

export interface TopicStudyNotes {
  id: number;
  topic_id: number;
  notes_type: string;
  title: string;
  overview: string;
  learning_objectives_json?: string[] | null;
  explanation_markdown: string;
  key_terms_json?: { term: string; definition: string }[] | null;
  formulas_and_dates_json?: { date?: string; event?: string; formula?: string }[] | null;
  diagrams_json?: { title: string; diagram_type: string; code: string; description: string }[] | null;
  common_misconceptions_json?: { misconception: string; correction: string }[] | null;
  exam_points_json?: string[] | null;
  practice_questions_json?: { question: string; answer: string }[] | null;
  source_references_json?: { title: string; url?: string; verified: boolean }[] | null;
  version: number;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
}

