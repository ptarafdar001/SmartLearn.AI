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

export interface VoiceSessionResponse {
  session_id: string;
  session_token: string;
  ws_endpoint: string;
  topic_id: number;
  topic_title: string;
  subject_name: string;
  board: string;
  grade: string;
  expires_in_seconds: number;
}

export type VoiceState =
  | 'idle'
  | 'connecting'
  | 'connected'
  | 'listening'
  | 'thinking'
  | 'speaking'
  | 'error';

