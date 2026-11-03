import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  CheckCircle,
  Flame,
  Loader2,
  AlertTriangle,
  Mail,
  ArrowRight,
} from 'lucide-react';
import { AppLayout } from '../components/layout/AppLayout';
import {
  fetchDetailedAnalytics,
  triggerMissedSlotAlert,
} from '../services/learning';
import type { DetailedAnalytics } from '../services/learning';

export const ProgressAnalyticsPage: React.FC = () => {
  const navigate = useNavigate();
  const [analytics, setAnalytics] = useState<DetailedAnalytics | null>(null);
  const [activeFilter, setActiveFilter] = useState<'week' | 'month' | 'all'>('week');
  const [isSendingAlert, setIsSendingAlert] = useState<boolean>(false);
  const [alertSuccessToast, setAlertSuccessToast] = useState<string | null>(null);

  useEffect(() => {
    loadAnalytics(activeFilter);
  }, [activeFilter]);

  const loadAnalytics = async (filter: string) => {
    try {
      const data = await fetchDetailedAnalytics(filter);
      setAnalytics(data);
    } catch (err) {
      console.error('Failed to load detailed analytics:', err);
    } finally {
    }
  };

  const handleSendAlert = async () => {
    try {
      setIsSendingAlert(true);
      const res = await triggerMissedSlotAlert();
      setAlertSuccessToast(`Email alert sent to ${res.recipient}!`);
      setTimeout(() => setAlertSuccessToast(null), 5000);
      loadAnalytics(activeFilter);
    } catch (err) {
      console.error('Failed to send study alert:', err);
    } finally {
      setIsSendingAlert(false);
    }
  };

  const overallProgress = analytics?.overall_progress_percentage ?? 0;
  const studiedText = analytics?.studied_this_week_text ?? '0m';
  const quizAvg = analytics?.quiz_average ?? 0;
  const streak = analytics?.study_streak_days ?? 1;
  const daysData = analytics?.days_data ?? [
    { day: 'Mon', hours: 0, height: 8 },
    { day: 'Tue', hours: 0, height: 8 },
    { day: 'Wed', hours: 0, height: 8 },
    { day: 'Thu', hours: 0, height: 8 },
    { day: 'Fri', hours: 0, height: 8 },
    { day: 'Sat', hours: 0, height: 8 },
    { day: 'Sun', hours: 0, height: 8 },
  ];
  const chapters = analytics?.chapter_progress ?? [];
  const weakTopics = analytics?.needs_practice ?? [];

  return (
    <AppLayout breadcrumbs={[{ label: 'Progress & Analytics' }]}>
      {/* ── Email Alert Notification Bar (Child Routine Alert System) ──────── */}
      {analytics && analytics.is_behind_schedule && (
        <div
          style={{
            background: '#fffbeb',
            border: '1px solid #fde68a',
            borderRadius: 16,
            padding: '16px 20px',
            marginBottom: 24,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: 12,
            boxShadow: '0 1px 3px rgba(0,0,0,0.03)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div
              style={{
                width: 38,
                height: 38,
                borderRadius: 10,
                background: '#fef3c7',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#d97706',
              }}
            >
              <AlertTriangle size={20} />
            </div>
            <div>
              <div style={{ fontSize: 13, fontWeight: 700, color: '#92400e' }}>
                Routine Alert: Scheduled for {analytics.daily_target_hours} hrs on {analytics.today_day_name} ({analytics.preferred_slot} at {analytics.slot_start_time || '6:00 PM'})
              </div>
              <div style={{ fontSize: 12, color: '#b45309', marginTop: 2 }}>
                Child has logged {analytics.hours_studied_today} hrs today. An automated reminder email is dispatched to {analytics.child_email} if target is missed.
              </div>
            </div>
          </div>

          <button
            type="button"
            onClick={handleSendAlert}
            disabled={isSendingAlert}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              background: '#d97706',
              color: '#ffffff',
              border: 'none',
              borderRadius: 10,
              padding: '8px 16px',
              fontSize: 12,
              fontWeight: 700,
              cursor: isSendingAlert ? 'not-allowed' : 'pointer',
              boxShadow: '0 2px 4px rgba(217,119,6,0.2)',
            }}
          >
            {isSendingAlert ? <Loader2 size={13} className="animate-spin" /> : <Mail size={13} />}
            <span>{isSendingAlert ? 'Dispatching...' : 'Send Reminder Email Now'}</span>
          </button>
        </div>
      )}

      {/* Floating Success Toast */}
      {alertSuccessToast && (
        <div
          style={{
            position: 'fixed',
            top: 24,
            right: 24,
            zIndex: 100,
            background: '#10b981',
            color: '#ffffff',
            padding: '12px 20px',
            borderRadius: 14,
            boxShadow: '0 10px 25px -5px rgba(16, 185, 129, 0.4)',
            display: 'flex',
            alignItems: 'center',
            gap: 10,
            fontWeight: 600,
            fontSize: 13,
          }}
        >
          <CheckCircle size={18} color="#d1fae5" />
          <span>{alertSuccessToast}</span>
        </div>
      )}

      {/* ── Header and Filter Pills (Matching Screenshot 1) ───────────────── */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 24, flexWrap: 'wrap', gap: 16 }}>
        <div>
          <h1 style={{ fontSize: 24, fontWeight: 800, color: '#1e1b4b', margin: 0 }}>Progress &amp; Analytics</h1>
          <p style={{ fontSize: 14, color: '#64748b', marginTop: 4, margin: '4px 0 0 0' }}>
            Real-world metrics calculated from student study sessions and quiz attempts.
          </p>
        </div>

        {/* Filter Pills */}
        <div style={{ display: 'flex', gap: 6, background: '#f1f5f9', padding: 4, borderRadius: 12 }}>
          <button
            type="button"
            onClick={() => setActiveFilter('week')}
            style={{
              background: activeFilter === 'week' ? '#4f46e5' : 'transparent',
              color: activeFilter === 'week' ? '#ffffff' : '#64748b',
              border: 'none',
              borderRadius: 8,
              padding: '6px 14px',
              fontWeight: 700,
              fontSize: 13,
              cursor: 'pointer',
              transition: 'all 0.15s ease',
            }}
          >
            This week
          </button>
          <button
            type="button"
            onClick={() => setActiveFilter('month')}
            style={{
              background: activeFilter === 'month' ? '#4f46e5' : 'transparent',
              color: activeFilter === 'month' ? '#ffffff' : '#64748b',
              border: 'none',
              borderRadius: 8,
              padding: '6px 14px',
              fontWeight: 700,
              fontSize: 13,
              cursor: 'pointer',
              transition: 'all 0.15s ease',
            }}
          >
            This month
          </button>
          <button
            type="button"
            onClick={() => setActiveFilter('all')}
            style={{
              background: activeFilter === 'all' ? '#4f46e5' : 'transparent',
              color: activeFilter === 'all' ? '#ffffff' : '#64748b',
              border: 'none',
              borderRadius: 8,
              padding: '6px 14px',
              fontWeight: 700,
              fontSize: 13,
              cursor: 'pointer',
              transition: 'all 0.15s ease',
            }}
          >
            All time
          </button>
        </div>
      </div>

      {/* ── Top 4 KPI Metric Cards (Matching Screenshot 1) ───────────────── */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: 16,
          marginBottom: 24,
        }}
      >
        {/* Card 1: Overall Progress */}
        <div style={{ background: '#ffffff', borderRadius: 16, padding: '20px 24px', border: '1px solid #f1f5f9', boxShadow: '0 1px 3px rgba(0,0,0,0.03)' }}>
          <div style={{ fontSize: 26, fontWeight: 800, color: '#4f46e5', lineHeight: 1 }}>{overallProgress}%</div>
          <div style={{ fontSize: 11, fontWeight: 700, color: '#64748b', marginTop: 8, letterSpacing: '0.05em' }}>
            OVERALL PROGRESS
          </div>
        </div>

        {/* Card 2: Studied this Week */}
        <div style={{ background: '#ffffff', borderRadius: 16, padding: '20px 24px', border: '1px solid #f1f5f9', boxShadow: '0 1px 3px rgba(0,0,0,0.03)' }}>
          <div style={{ fontSize: 26, fontWeight: 800, color: '#059669', lineHeight: 1 }}>{studiedText}</div>
          <div style={{ fontSize: 11, fontWeight: 700, color: '#64748b', marginTop: 8, letterSpacing: '0.05em' }}>
            STUDIED THIS WEEK
          </div>
        </div>

        {/* Card 3: Quiz Average */}
        <div style={{ background: '#ffffff', borderRadius: 16, padding: '20px 24px', border: '1px solid #f1f5f9', boxShadow: '0 1px 3px rgba(0,0,0,0.03)' }}>
          <div style={{ fontSize: 26, fontWeight: 800, color: '#d97706', lineHeight: 1 }}>{quizAvg}%</div>
          <div style={{ fontSize: 11, fontWeight: 700, color: '#64748b', marginTop: 8, letterSpacing: '0.05em' }}>
            QUIZ AVERAGE
          </div>
        </div>

        {/* Card 4: Study Streak */}
        <div style={{ background: '#ffffff', borderRadius: 16, padding: '20px 24px', border: '1px solid #f1f5f9', boxShadow: '0 1px 3px rgba(0,0,0,0.03)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 26, fontWeight: 800, color: '#ea580c', lineHeight: 1 }}>
            <Flame size={24} color="#ea580c" fill="#ea580c" />
            <span>{streak} {streak === 1 ? 'day' : 'days'}</span>
          </div>
          <div style={{ fontSize: 11, fontWeight: 700, color: '#64748b', marginTop: 8, letterSpacing: '0.05em' }}>
            STUDY STREAK
          </div>
        </div>
      </div>

      {/* ── Middle Grid: Hours Studied Bar Chart + Chapter Progress ─────── */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
          gap: 20,
          marginBottom: 24,
        }}
      >
        {/* Hours Studied Each Day (Dynamic from Real Routine Activity) */}
        <div style={{ background: '#ffffff', borderRadius: 20, padding: 24, border: '1px solid #f1f5f9', boxShadow: '0 1px 3px rgba(0,0,0,0.03)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
            <h2 style={{ fontSize: 17, fontWeight: 800, color: '#1e1b4b', margin: 0 }}>
              Hours studied each day
            </h2>
            {analytics && (
              <span style={{ fontSize: 11, fontWeight: 600, color: '#64748b', background: '#f1f5f9', padding: '3px 8px', borderRadius: 6 }}>
                Target: {analytics.daily_target_hours}h/day
              </span>
            )}
          </div>

          <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between', height: 160, paddingBottom: 10 }}>
            {daysData.map((d) => (
              <div key={d.day} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8, flex: 1 }}>
                <div
                  title={`${d.day}: ${d.hours} hours`}
                  style={{
                    width: '65%',
                    maxHeight: 120,
                    height: `${d.height}%`,
                    background: d.hours > 0 ? '#4f46e5' : '#e2e8f0',
                    borderRadius: 6,
                    transition: 'height 0.3s ease',
                  }}
                />
                <span style={{ fontSize: 12, fontWeight: 600, color: d.hours > 0 ? '#1e293b' : '#94a3b8' }}>
                  {d.day}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Real Chapter Progress (Dynamic from Enrolled Subjects) */}
        <div style={{ background: '#ffffff', borderRadius: 20, padding: 24, border: '1px solid #f1f5f9', boxShadow: '0 1px 3px rgba(0,0,0,0.03)' }}>
          <h2 style={{ fontSize: 17, fontWeight: 800, color: '#1e1b4b', margin: '0 0 20px 0' }}>
            Chapter progress
          </h2>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>
            {chapters.map((ch, idx) => (
              <div key={idx}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13, fontWeight: 700, color: '#1e293b', marginBottom: 6 }}>
                  <span>{ch.title}</span>
                  <span>{ch.progress}%</span>
                </div>
                <div style={{ height: 8, background: '#f1f5f9', borderRadius: 99, overflow: 'hidden' }}>
                  <div style={{ width: `${ch.progress}%`, height: '100%', background: ch.color, borderRadius: 99, transition: 'width 0.5s ease' }} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── Bottom Section: Real Weak Topics from Child Question Attempts ── */}
      <div style={{ background: '#ffffff', borderRadius: 20, padding: 24, border: '1px solid #f1f5f9', boxShadow: '0 1px 3px rgba(0,0,0,0.03)' }}>
        <h2 style={{ fontSize: 17, fontWeight: 800, color: '#1e1b4b', margin: '0 0 16px 0' }}>
          Needs more practice
        </h2>

        {weakTopics.length === 0 ? (
          <div style={{ fontSize: 13, color: '#64748b' }}>
            Great job! You have answered all recent curriculum questions accurately. Practice more questions in the Practice &amp; Assessment Hub to discover areas for revision.
          </div>
        ) : (
          <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: 12 }}>
            {weakTopics.map((item, idx) => (
              <div
                key={idx}
                style={{
                  background: idx % 2 === 0 ? '#fef2f2' : '#fefce8',
                  color: idx % 2 === 0 ? '#991b1b' : '#854d0e',
                  padding: '8px 16px',
                  borderRadius: 20,
                  fontSize: 13,
                  fontWeight: 600,
                }}
              >
                {item.title} · {item.accuracy}%
              </div>
            ))}

            <button
              type="button"
              onClick={() => {
                if (weakTopics.length > 0) {
                  navigate(`/practice?topicId=${weakTopics[0].topic_id}`);
                } else {
                  navigate('/practice');
                }
              }}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 6,
                background: '#4f46e5',
                color: '#ffffff',
                border: 'none',
                borderRadius: 20,
                padding: '8px 20px',
                fontSize: 13,
                fontWeight: 600,
                cursor: 'pointer',
              }}
            >
              <span>Practice these</span>
              <ArrowRight size={14} />
            </button>
          </div>
        )}
      </div>
    </AppLayout>
  );
};
