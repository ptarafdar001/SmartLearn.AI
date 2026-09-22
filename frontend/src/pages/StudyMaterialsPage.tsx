import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { FileText, Video, ArrowRight, Check } from 'lucide-react';
import { AppLayout } from '../components/layout/AppLayout';
import { fetchSubjectDetail } from '../services/learning';
import type { SubjectDetail } from '../types/learning';

export const StudyMaterialsPage: React.FC = () => {
  const [subject, setSubject] = useState<SubjectDetail | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [filterType, setFilterType] = useState<string>('all');

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        // Load default enrolled subject (History id=43)
        const data = await fetchSubjectDetail(43);
        setSubject(data);
      } catch {
        // fallback
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const chapters = subject?.chapters || [];

  return (
    <AppLayout breadcrumbs={[{ label: 'Study Materials & Notes' }]}>
      <div className="page-header-compact">
        <div>
          <h1 className="page-title-compact">Study Materials &amp; Verified Notes</h1>
          <p className="page-subtitle-compact">
            Curated revision sheets, textbook extracts, and video lectures aligned with CISCE ISC Class 11 regulations.
          </p>
        </div>

        <div className="filter-pills-row">
          <button
            type="button"
            className={`filter-pill ${filterType === 'all' ? 'active' : ''}`}
            onClick={() => setFilterType('all')}
          >
            All Resources
          </button>
          <button
            type="button"
            className={`filter-pill ${filterType === 'notes' ? 'active' : ''}`}
            onClick={() => setFilterType('notes')}
          >
            <FileText size={13} />
            <span>Revision Notes</span>
          </button>
          <button
            type="button"
            className={`filter-pill ${filterType === 'video' ? 'active' : ''}`}
            onClick={() => setFilterType('video')}
          >
            <Video size={13} />
            <span>Video Lectures</span>
          </button>
        </div>
      </div>

      {loading ? (
        <div className="learn-loading-container">
          <div className="learn-spinner" />
          <p>Loading study materials catalog...</p>
        </div>
      ) : (
        <div className="materials-grid">
          {chapters.map((ch) => (
            <div key={ch.id} className="materials-chapter-card">
              <div className="materials-ch-header">
                <span className="chapter-num-badge">Chapter {ch.chapter_number}</span>
                <h3 className="materials-ch-title">{ch.title}</h3>
              </div>

              <div className="materials-topics-list">
                {ch.topics.map((t) => (
                  <div key={t.id} className="materials-topic-row">
                    <div className="materials-topic-info">
                      <div className="materials-badge-verified">
                        <Check size={11} />
                        <span>Official CISCE Syllabus</span>
                      </div>
                      <h4 className="materials-topic-name">{t.topic_number}. {t.title}</h4>
                      <p className="materials-topic-desc">{t.description}</p>
                    </div>

                    <div className="materials-actions">
                      <Link to={`/learning/topics/${t.id}`} className="materials-view-btn">
                        <span>Study Notes &amp; Video</span>
                        <ArrowRight size={13} />
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </AppLayout>
  );
};
