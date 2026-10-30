with open('frontend/src/pages/DashboardPage.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace imports
old_import = "import { AlertCircle, BookOpen } from 'lucide-react';"
new_import = "import { AlertCircle, BookOpen, Play, Video } from 'lucide-react';"

assert old_import in content, "old_import not found"
content = content.replace(old_import, new_import, 1)

old_recs = """                {/* Recommendations */}
                {recommendations.length > 0 && (
                  <div style={{ marginTop: 24 }}>
                    <h3 style={{ fontSize: 16, fontWeight: 700, color: '#1e293b', marginBottom: 12 }}>
                      Recommended For You
                    </h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                      {recommendations.map((rec) => (
                        <div
                          key={rec.id}
                          style={{
                            background: '#ffffff',
                            border: '1px solid #e2e8f0',
                            borderRadius: 12,
                            padding: '12px 16px',
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                          }}
                        >
                          <div>
                            <div style={{ fontSize: 14, fontWeight: 600, color: '#1e293b' }}>
                              {rec.title}
                            </div>
                            <div style={{ fontSize: 12.5, color: '#64748b' }}>
                              {rec.description}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}"""

new_recs = """                {/* Recommendations with YouTube Video Lessons */}
                {recommendations.length > 0 && (
                  <div style={{ marginTop: 24 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                      <h3 style={{ fontSize: 16, fontWeight: 700, color: '#1e293b', margin: 0, display: 'flex', alignItems: 'center', gap: 8 }}>
                        <Video size={18} color="#ef4444" />
                        Recommended YouTube Video Lessons
                      </h3>
                      <Link to="/study-materials" style={{ fontSize: 13, color: '#6366f1', textDecoration: 'none', fontWeight: 600 }}>
                        View All Materials →
                      </Link>
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 14 }}>
                      {recommendations.map((rec) => (
                        <div
                          key={rec.id}
                          style={{
                            background: '#ffffff',
                            border: '1px solid #e2e8f0',
                            borderRadius: 14,
                            padding: '14px 16px',
                            display: 'flex',
                            flexDirection: 'column',
                            justifyContent: 'space-between',
                            boxShadow: '0 2px 4px rgba(0,0,0,0.02)',
                            transition: 'all 0.2s ease',
                          }}
                        >
                          <div>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                              <span style={{
                                fontSize: 11,
                                fontWeight: 700,
                                textTransform: 'uppercase',
                                letterSpacing: '0.05em',
                                background: '#fef2f2',
                                color: '#dc2626',
                                padding: '3px 8px',
                                borderRadius: 6,
                              }}>
                                {rec.subject}
                              </span>
                              {rec.duration_minutes && (
                                <span style={{ fontSize: 12, color: '#64748b', fontWeight: 500 }}>
                                  {rec.duration_minutes} min video
                                </span>
                              )}
                            </div>
                            <div style={{ fontSize: 14, fontWeight: 700, color: '#1e293b', marginBottom: 6, lineHeight: 1.4 }}>
                              {rec.title}
                            </div>
                            <div style={{ fontSize: 12.5, color: '#64748b', lineHeight: 1.5, marginBottom: 14 }}>
                              {rec.description}
                            </div>
                          </div>

                          <div style={{ display: 'flex', gap: 8, marginTop: 4 }}>
                            {rec.topic_id ? (
                              <Link
                                to={`/learning/topics/${rec.topic_id}`}
                                style={{
                                  display: 'inline-flex',
                                  alignItems: 'center',
                                  justifyContent: 'center',
                                  gap: 6,
                                  background: '#ef4444',
                                  color: '#ffffff',
                                  textDecoration: 'none',
                                  fontSize: 12.5,
                                  fontWeight: 600,
                                  padding: '7px 14px',
                                  borderRadius: 8,
                                  width: '100%',
                                }}
                              >
                                <Play size={13} fill="#ffffff" /> Watch & Study Topic
                              </Link>
                            ) : (
                              <Link
                                to="/study-materials"
                                style={{
                                  display: 'inline-flex',
                                  alignItems: 'center',
                                  justifyContent: 'center',
                                  gap: 6,
                                  background: '#4f46e5',
                                  color: '#ffffff',
                                  textDecoration: 'none',
                                  fontSize: 12.5,
                                  fontWeight: 600,
                                  padding: '7px 14px',
                                  borderRadius: 8,
                                  width: '100%',
                                }}
                              >
                                Open Syllabus Materials
                              </Link>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}"""

assert old_recs in content, "old_recs not found"
content = content.replace(old_recs, new_recs, 1)

with open('frontend/src/pages/DashboardPage.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated frontend/src/pages/DashboardPage.tsx successfully")

