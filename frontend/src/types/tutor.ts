export interface TutorChatMessage {
  id: string;
  role: 'student' | 'tutor';
  content: string;
  timestamp: string;
  imageUrl?: string | null;
  isError?: boolean;
}

export interface TutorChatPayload {
  topic_id: number;
  message: string;
  conversation_history: Array<{
    role: 'student' | 'tutor' | 'user' | 'model';
    content: string;
  }>;
  image_base64?: string | null;
}

export interface TutorChatResponse {
  reply: string;
  topic_id: number;
  topic_title: string;
  subject_name: string;
  board: string;
  grade: string;
  grounded_resource_titles: string[];
  is_out_of_scope: boolean;
}
