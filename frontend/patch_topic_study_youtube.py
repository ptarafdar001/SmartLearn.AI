with open('frontend/src/pages/learning/TopicStudyPage.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update imports
old_import = "import { fetchTopicDetail, fetchTopicStudyNotes, saveTopicProgress, fetchPracticeQuestions } from '../../services/learning';"
new_import = "import { fetchTopicDetail, fetchTopicStudyNotes, saveTopicProgress, fetchPracticeQuestions, fetchTopicVideoRecommendations, type VideoRecommendationItem } from '../../services/learning';"
text = text.replace(old_import, new_import, 1)

# Add Play, Film icons if needed
old_icons = "import {\n  Check,\n  AlertCircle,\n  HelpCircle,\n} from 'lucide-react';"
new_icons = "import {\n  Check,\n  AlertCircle,\n  HelpCircle,\n  Play,\n  Video,\n  Film,\n} from 'lucide-react';"
text = text.replace(old_icons, new_icons, 1)

# 2. Add video recommendation state
old_state = "  const [dynamicNotes, setDynamicNotes] = useState<TopicStudyNotes | null>(null);\n  const [topicQuiz, setTopicQuiz] = useState<PracticeQuestion[]>([]);"
new_state = """  const [dynamicNotes, setDynamicNotes] = useState<TopicStudyNotes | null>(null);
  const [topicQuiz, setTopicQuiz] = useState<PracticeQuestion[]>([]);
  const [recommendedVideos, setRecommendedVideos] = useState<VideoRecommendationItem[]>([]);
  const [activeVideoId, setActiveVideoId] = useState<string | null>(null);
  const [activeVideoTitle, setActiveVideoTitle] = useState<string | null>(null);"""
text = text.replace(old_state, new_state, 1)

# 3. Add fetch call inside loadTopic()
old_fetch_all = """        // Load 10-part syllabus study notes & real curriculum practice quiz
        try {
          const [notesData, quizData] = await Promise.all([
            fetchTopicStudyNotes(Number(topicId)).catch(() => null),
            fetchPracticeQuestions(Number(topicId)).catch(() => []),
          ]);
          if (isMounted) {
            if (notesData) setDynamicNotes(notesData);
            if (quizData && quizData.length > 0) setTopicQuiz(quizData);
          }
        } catch {
          // Fallback gracefully
        }"""

new_fetch_all = """        // Load 10-part syllabus study notes, real curriculum practice quiz, and dynamic YouTube recommendations
        try {
          const [notesData, quizData, videoRecData] = await Promise.all([
            fetchTopicStudyNotes(Number(topicId)).catch(() => null),
            fetchPracticeQuestions(Number(topicId)).catch(() => []),
            fetchTopicVideoRecommendations(Number(topicId)).catch(() => null),
          ]);
          if (isMounted) {
            if (notesData) setDynamicNotes(notesData);
            if (quizData && quizData.length > 0) setTopicQuiz(quizData);
            if (videoRecData && videoRecData.videos && videoRecData.videos.length > 0) {
              setRecommendedVideos(videoRecData.videos);
              // Set the top-ranked educational video as current active if not manually overridden
              setActiveVideoId(videoRecData.videos[0].video_id);
              setActiveVideoTitle(videoRecData.videos[0].title);
            }
          }
        } catch {
          // Fallback gracefully
        }"""
text = text.replace(old_fetch_all, new_fetch_all, 1)

# 4. Update videoEmbedUrl computation
old_embed_calc = """  const videoEmbedUrl =
    videoResource?.content_url ||
    `https://www.youtube-nocookie.com/embed/${videoResource?.external_id || fallbackVideoId}`;

  const videoTitle =
    videoResource?.title || `${subjectName}: ${topicTitle} Video Lesson`;"""

new_embed_calc = """  // Active video prioritized from dynamic YouTube recommendation or verified resource
  const currentVidId = activeVideoId || videoResource?.external_id || fallbackVideoId;
  const videoEmbedUrl = `https://www.youtube-nocookie.com/embed/${currentVidId}`;
  const videoTitle = activeVideoTitle || videoResource?.title || `${subjectName}: ${topicTitle} Video Lesson`;"""
text = text.replace(old_embed_calc, new_embed_calc, 1)

# 5. Insert Recommended Educational Videos selector right below Key points card
old_key_points_card = """                  {/* Key Points Card matching Design */}
                  <div className="key-points-card-clean">
                    <h3 className="key-points-title">Key points</h3>
                    <p className="key-points-desc">
                      {notesResource?.text_content ||
                        dynamicNotes?.overview ||
                        `Key study notes for ${topicTitle} (${subjectName}) aligned with your curriculum syllabus.`}
                    </p>
                  </div>"""

new_key_points_card = """                  {/* Key Points Card matching Design */}
                  <div className="key-points-card-clean">
                    <h3 className="key-points-title">Key points</h3>
                    <p className="key-points-desc">
                      {notesResource?.text_content ||
                        dynamicNotes?.overview ||
                        `Key study notes for ${topicTitle} (${subjectName}) aligned with your curriculum syllabus.`}
                    </p>
                  </div>

                  {/* Chapter-Specific Dynamic YouTube Recommendations */}
                  <div style={{ marginTop: 20, background: '#ffffff', borderRadius: 14, border: '1px solid #e2e8f0', padding: '16px 20px', boxShadow: '0 1px 3px rgba(0,0,0,0.03)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                      <h4 style={{ margin: 0, fontSize: 14, fontWeight: 700, color: '#1e293b', display: 'flex', alignItems: 'center', gap: 7 }}>
                        <Film size={16} color="#ef4444" />
                        Curriculum Video Recommendations ({recommendedVideos.length > 0 ? recommendedVideos.length : 'Searching...'})
                      </h4>
                      <span style={{ fontSize: 11.5, color: '#64748b', fontWeight: 500 }}>
                        Ranked by curriculum alignment & educational quality
                      </span>
                    </div>

                    {recommendedVideos.length > 0 ? (
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: 12 }}>
                        {recommendedVideos.map((vid) => {
                          const isCurrent = vid.video_id === currentVidId;
                          return (
                            <div
                              key={vid.video_id}
                              onClick={() => {
                                setActiveVideoId(vid.video_id);
                                setActiveVideoTitle(vid.title);
                              }}
                              style={{
                                cursor: 'pointer',
                                border: '1px solid',
                                borderColor: isCurrent ? '#6366f1' : '#e2e8f0',
                                background: isCurrent ? '#f5f3ff' : '#f8fafc',
                                borderRadius: 10,
                                padding: '10px 12px',
                                display: 'flex',
                                gap: 10,
                                alignItems: 'center',
                                transition: 'all 0.15s ease',
                              }}
                            >
                              <div style={{ position: 'relative', width: 72, height: 48, borderRadius: 6, overflow: 'hidden', flexShrink: 0, background: '#0f172a' }}>
                                <img
                                  src={vid.thumbnail_url}
                                  alt={vid.title}
                                  style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                                />
                                <div style={{ position: 'absolute', inset: 0, background: 'rgba(0,0,0,0.25)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                  <Play size={14} fill="#ffffff" color="#ffffff" />
                                </div>
                              </div>
                              <div style={{ flex: 1, minWidth: 0 }}>
                                <div style={{ fontSize: 12, fontWeight: 700, color: '#1e293b', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                                  {vid.title}
                                </div>
                                <div style={{ fontSize: 11, color: '#64748b', marginTop: 2, display: 'flex', justifyContent: 'space-between' }}>
                                  <span>{vid.channel_title || 'Educational Stream'}</span>
                                  <span>{vid.duration_minutes} min</span>
                                </div>
                                {isCurrent && (
                                  <span style={{ display: 'inline-block', fontSize: 10, fontWeight: 700, color: '#4f46e5', marginTop: 3 }}>
                                    ● Now Playing
                                  </span>
                                )}
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    ) : (
                      <div style={{ fontSize: 12.5, color: '#64748b', padding: '10px 0', textAlign: 'center' }}>
                        Searching verified educational channels for {topicTitle} lessons...
                      </div>
                    )}
                  </div>"""
text = text.replace(old_key_points_card, new_key_points_card, 1)

with open('frontend/src/pages/learning/TopicStudyPage.tsx', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated TopicStudyPage.tsx with dynamic YouTube recommendations!")

