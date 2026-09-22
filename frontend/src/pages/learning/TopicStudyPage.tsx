import React, { useEffect, useRef, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { BrandLogo } from '../../components/common/BrandLogo';
import { fetchTopicDetail, saveTopicProgress } from '../../services/learning';
import type { LearningResource, ProgressStatus, TopicDetail } from '../../types/learning';
import '../../styles/learning.css';

export const TopicStudyPage: React.FC = () => {
  const { topicId } = useParams<{ topicId: string }>();
  const { user, logout } = useAuth();

  const [topic, setTopic] = useState<TopicDetail | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [saveSuccess, setSaveSuccess] = useState<string | null>(null);
  const [saving, setSaving] = useState<boolean>(false);

  // Active resource tab ('text' | 'notes' | 'video')
  const [activeTab, setActiveTab] = useState<string>('video');

  // Study timer (seconds spent in this session)
  const [sessionSeconds, setSessionSeconds] = useState<number>(0);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Local progress state
  const [currentStatus, setCurrentStatus] = useState<ProgressStatus>('not_started');
  const [currentPct, setCurrentPct] = useState<number>(0);

  useEffect(() => {
    let isMounted = true;

    async function loadTopic() {
      if (!topicId) return;

      try {
        setLoading(true);
        setError(null);
        const data = await fetchTopicDetail(Number(topicId));
        if (isMounted) {
          setTopic(data);
          const prog = data.progress || data.user_progress;
          if (prog) {
            setCurrentStatus(prog.status);
            setCurrentPct(prog.progress_percentage);
            setSessionSeconds(prog.time_spent_seconds || 0);
          }

          // Select first available resource type if video is not available
          if (data.resources.length > 0) {
            const hasVideo = data.resources.some((r) => r.resource_type === 'video');
            if (hasVideo) {
              setActiveTab('video');
            } else {
              setActiveTab(data.resources[0].resource_type);
            }
          }
        }
      } catch (err: any) {
        if (isMounted) {
          setError(err.message || 'Failed to load topic learning resources.');
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    loadTopic();

    // Start session timer
    timerRef.current = setInterval(() => {
      setSessionSeconds((prev) => prev + 1);
    }, 1000);

    return () => {
      isMounted = false;
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, [topicId]);

  const handleUpdateProgress = async (newStatus: ProgressStatus, newPct: number) => {
    if (!topicId) return;

    try {
      setSaving(true);
      setSaveSuccess(null);
      setError(null);

      const resp = await saveTopicProgress(Number(topicId), {
        status: newStatus,
        progress_percentage: newPct,
        time_spent_seconds: sessionSeconds,
      });

      setCurrentStatus(resp.status);
      setCurrentPct(resp.progress_percentage);
      setSaveSuccess(
        newStatus === 'completed'
          ? 'Topic marked as completed! 100% saved.'
          : `Progress updated to ${newPct}%.`
      );

      // Auto-clear success message after 4 seconds
      setTimeout(() => {
        setSaveSuccess(null);
      }, 4000);
    } catch (err: any) {
      setError(err.message || 'Failed to save progress.');
    } finally {
      setSaving(false);
    }
  };

  const studentName = user?.full_name || 'Student';

  // Group resources by type
  const activeResources: LearningResource[] =
    topic?.resources.filter((r) => r.resource_type === activeTab) || [];

  return (
    <div className="learn-layout">
      {/* Top Navigation */}
      <header className="learn-nav">
        <div className="learn-nav-container">
          <Link to="/dashboard" className="learn-nav-brand" aria-label="SmartLearn Home">
            <BrandLogo size="sm" />
            <span style={{ fontWeight: 700, fontSize: '18px', color: '#0f172a' }}>
              SmartLearn.AI
            </span>
          </Link>
          <div className="learn-nav-actions">
            <div className="learn-user-pill">
              <div className="learn-user-avatar">{studentName.charAt(0).toUpperCase()}</div>
              <span>{studentName}</span>
            </div>
            <button type="button" className="learn-signout-btn" onClick={logout}>
              Sign Out
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="learn-container">
        {/* Breadcrumb Navigation */}
        <nav className="learn-breadcrumbs" aria-label="Breadcrumbs">
          <Link to="/dashboard" className="learn-breadcrumb-link">
            Dashboard
          </Link>
          <span className="learn-breadcrumb-sep">/</span>
          {topic && (
            <>
              <Link
                to={`/learning/subjects/${topic.subject_id}`}
                className="learn-breadcrumb-link"
              >
                {topic.subject_name}
              </Link>
              <span className="learn-breadcrumb-sep">/</span>
              <span className="learn-breadcrumb-link">{topic.chapter_title}</span>
              <span className="learn-breadcrumb-sep">/</span>
            </>
          )}
          <span className="learn-breadcrumb-current">{topic?.title || 'Topic'}</span>
        </nav>

        {error && (
          <div className="learn-error-box" role="alert">
            <span aria-hidden="true">⚠️</span>
            <div>
              <strong>Error:</strong> {error}
            </div>
          </div>
        )}

        {saveSuccess && (
          <div
            className="learn-error-box"
            role="status"
            style={{ background: '#ecfdf5', borderColor: '#a7f3d0', color: '#065f46' }}
          >
            <span aria-hidden="true">✅</span>
            <div>{saveSuccess}</div>
          </div>
        )}

        {loading ? (
          <div className="learn-loading-container" aria-live="polite">
            <div className="learn-spinner" aria-hidden="true" />
            <p>Loading lesson and educational resources...</p>
          </div>
        ) : topic ? (
          <>
            {/* Header Card */}
            <div className="study-header">
              <div style={{ display: 'flex', gap: '8px', marginBottom: '8px' }}>
                <span className="subject-badge">{topic.subject_name}</span>
                <span className="subject-badge">
                  Chapter {topic.chapter_number}: {topic.chapter_title}
                </span>
                <span className="subject-badge">Topic {topic.topic_number}</span>
              </div>

              <h1 className="study-title">{topic.title}</h1>
              {topic.description && <p className="study-desc">{topic.description}</p>}

              <div className="study-meta-row">
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px', fontSize: '13px', color: '#64748b' }}>
                  <span>⏱️ Est. Study Time: {topic.estimated_minutes} mins</span>
                  <span>•</span>
                  <span>⏳ Time in Session: {Math.floor(sessionSeconds / 60)}m {sessionSeconds % 60}s</span>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <span style={{ fontSize: '13px', fontWeight: 600, color: '#475569' }}>
                    Status:{' '}
                    <span
                      style={{
                        color:
                          currentStatus === 'completed'
                            ? '#10b981'
                            : currentStatus === 'in_progress'
                              ? '#4f46e5'
                              : '#64748b',
                      }}
                    >
                      {currentStatus === 'completed'
                        ? 'Completed (100%)'
                        : currentStatus === 'in_progress'
                          ? `In Progress (${currentPct}%)`
                          : 'Not Started'}
                    </span>
                  </span>
                </div>
              </div>
            </div>

            {/* Multi-Modal Modality Selection Bar */}
            <div className="modalities-bar" role="tablist" aria-label="Learning modalities">
              <button
                type="button"
                role="tab"
                aria-selected={activeTab === 'video'}
                className={`modality-tab ${activeTab === 'video' ? 'active' : ''}`}
                onClick={() => setActiveTab('video')}
              >
                <span>🎥</span> Video Lesson
              </button>

              <button
                type="button"
                role="tab"
                aria-selected={activeTab === 'notes'}
                className={`modality-tab ${activeTab === 'notes' ? 'active' : ''}`}
                onClick={() => setActiveTab('notes')}
              >
                <span>📝</span> Study Notes &amp; Summary
              </button>

              <button
                type="button"
                role="tab"
                aria-selected={activeTab === 'text'}
                className={`modality-tab ${activeTab === 'text' ? 'active' : ''}`}
                onClick={() => setActiveTab('text')}
              >
                <span>📖</span> Reading Material
              </button>
            </div>

            {/* Resource Display Area */}
            <div className="resource-viewer" role="tabpanel" aria-labelledby={`tab-${activeTab}`}>
              {activeResources.length === 0 ? (
                <div className="learn-empty-state">
                  <p>No {activeTab} resources available for this topic yet.</p>
                </div>
              ) : (
                activeResources.map((res) => (
                  <div key={res.id} style={{ marginBottom: '28px' }}>
                    <div className="resource-provenance">
                      <span className="provenance-tag">
                        Provider: {res.provider || 'SmartLearn'}
                      </span>
                      {res.source_name && (
                        <span>
                          Source: <strong>{res.source_name}</strong>
                        </span>
                      )}
                      {res.is_verified && (
                        <span className="verified-badge">
                          ✓ Official Verified Curriculum Resource
                        </span>
                      )}
                    </div>

                    <h2 style={{ fontSize: '18px', fontWeight: 700, margin: '0 0 16px' }}>
                      {res.title}
                    </h2>

                    {/* Video Player */}
                    {res.resource_type === 'video' && res.content_url && (
                      <div className="video-container">
                        <iframe
                          src={res.content_url}
                          title={res.title}
                          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                          allowFullScreen
                          sandbox="allow-scripts allow-same-origin allow-presentation"
                        />
                      </div>
                    )}

                    {/* Text / Notes Content */}
                    {res.text_content && (
                      <div className="text-content-box">
                        <div
                          style={{
                            whiteSpace: 'pre-line',
                            fontFamily: 'Inter, system-ui, sans-serif',
                          }}
                        >
                          {res.text_content}
                        </div>
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>

            {/* Interactive Progress Tracking Action Bar */}
            <section className="progress-action-bar" aria-label="Topic progress controls">
              <div className="progress-status-indicator">
                <span>Progress:</span>
                <span
                  style={{
                    color: currentStatus === 'completed' ? '#10b981' : '#4f46e5',
                    fontWeight: 700,
                  }}
                >
                  {currentPct}%
                </span>
                <span>({currentStatus.replace('_', ' ')})</span>
              </div>

              <div className="progress-buttons">
                {currentStatus !== 'completed' && (
                  <button
                    type="button"
                    className="btn-progress-toggle"
                    disabled={saving}
                    onClick={() => handleUpdateProgress('in_progress', 50.0)}
                    aria-label="Mark 50% in progress"
                  >
                    {saving ? 'Saving...' : 'Mark In Progress (50%)'}
                  </button>
                )}

                <button
                  type="button"
                  className={`btn-progress-toggle ${currentStatus === 'completed' ? 'completed' : ''}`}
                  disabled={saving}
                  onClick={() =>
                    handleUpdateProgress(
                      currentStatus === 'completed' ? 'in_progress' : 'completed',
                      currentStatus === 'completed' ? 50.0 : 100.0
                    )
                  }
                  aria-label={
                    currentStatus === 'completed'
                      ? 'Mark as incomplete'
                      : 'Mark topic as completed 100%'
                  }
                >
                  {saving
                    ? 'Saving...'
                    : currentStatus === 'completed'
                      ? '✓ Completed (Click to Reset)'
                      : '✓ Mark Complete (100%)'}
                </button>

                <Link
                  to="/dashboard"
                  className="continue-action-btn"
                  style={{ background: '#334155' }}
                  aria-label="Return to Dashboard to see updated metrics"
                >
                  Dashboard →
                </Link>
              </div>
            </section>
          </>
        ) : (
          <div className="learn-empty-state">
            <p>Topic not found.</p>
            <Link to="/dashboard" className="continue-action-btn" style={{ marginTop: '16px' }}>
              Return to Dashboard
            </Link>
          </div>
        )}
      </main>
    </div>
  );
};
