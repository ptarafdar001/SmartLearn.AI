with open('frontend/src/services/learning.ts', 'r', encoding='utf-8') as f:
    text = f.read()

new_service_code = '''

export interface VideoRecommendationItem {
  video_id: string;
  title: string;
  description: string;
  channel_title: string;
  thumbnail_url: string;
  embed_url: string;
  duration_minutes: number;
  relevance_score: number;
}

export interface TopicVideoRecommendationsResponse {
  topic_id: number;
  topic_title: string;
  chapter_title?: string | null;
  subject_name?: string | null;
  board?: string | null;
  grade?: string | null;
  videos: VideoRecommendationItem[];
  total_count: number;
}

export async function fetchTopicVideoRecommendations(
  topicId: number
): Promise<TopicVideoRecommendationsResponse> {
  return apiClient<TopicVideoRecommendationsResponse>(
    `/learning/topics/${topicId}/video-recommendations`,
    {
      method: 'GET',
      requiresAuth: true,
    }
  );
}
'''

if 'fetchTopicVideoRecommendations' not in text:
    text += new_service_code
    with open('frontend/src/services/learning.ts', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Added fetchTopicVideoRecommendations to frontend/src/services/learning.ts")
else:
    print("fetchTopicVideoRecommendations already exists")

