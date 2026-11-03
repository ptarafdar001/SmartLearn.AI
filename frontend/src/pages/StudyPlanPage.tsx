import React, { useEffect, useState } from 'react';
import { AppLayout } from '../components/layout/AppLayout';
import { fetchDashboardOverview } from '../services/learning';
import type { DashboardOverview } from '../types/learning';

interface DaySchedule {
  dayName: string;
  isToday: boolean;
  isFreeDay: boolean;
  isTuitionDay: boolean;
  studySlotText?: string;
  subjectBadge?: string;
  actionBadge?: string;
}

export const StudyPlanPage: React.FC = () => {
  const [overview, setOverview] = useState<DashboardOverview | null>(null);

  useEffect(() => {
    fetchDashboardOverview().then(setOverview).catch(() => {});
  }, []);

  const target = overview?.study_target;
  const board = overview?.board || 'Curriculum';
  const grade = overview?.grade || 'Class 10';
  const targetDailyHours = target?.daily_target_hours || 2;
  const slot = target?.preferred_slot?.toLowerCase() || 'evening';
  const slotTiming = slot === 'morning' ? '9 AM - 12 PM' : slot === 'afternoon' ? '2 - 5 PM' : '6 - 9 PM';
  const enrolledSubjects = overview?.enrolled_subjects || [];

  const daysOfWeek = [
    { short: 'Mon', full: 'Monday' },
    { short: 'Tue', full: 'Tuesday' },
    { short: 'Wed', full: 'Wednesday' },
    { short: 'Thu', full: 'Thursday' },
    { short: 'Fri', full: 'Friday' },
    { short: 'Sat', full: 'Saturday' },
    { short: 'Sun', full: 'Sunday' },
  ];
  
  // Current day calculation
  const currentDayIndex = (new Date().getDay() + 6) % 7; // 0 = Mon, 4 = Fri

  const availableDays = (target?.available_days || []).map((d) => d.toLowerCase());

  const weekSchedule: DaySchedule[] = daysOfWeek.map((dayObj, idx) => {
    const isToday = idx === currentDayIndex;
    const isScheduled = availableDays.length > 0
      ? availableDays.some((ad) => ad.startsWith(dayObj.short.toLowerCase()) || ad === dayObj.full.toLowerCase())
      : idx < 6; // fallback Mon-Sat

    if (!isScheduled) {
      return {
        dayName: dayObj.short,
        isToday,
        isFreeDay: true,
        isTuitionDay: false,
        subjectBadge: undefined,
      };
    }

    // Assign the student's actual enrolled subjects across scheduled study days
    const subjectIndex = idx % (enrolledSubjects.length || 1);
    const assignedSubject = enrolledSubjects.length > 0 ? enrolledSubjects[subjectIndex] : 'Syllabus Topic';

    return {
      dayName: dayObj.short,
      isToday,
      isFreeDay: false,
      isTuitionDay: false,
      studySlotText: `${slotTiming} Study`,
      subjectBadge: `${assignedSubject}: Unit ${((idx % 2) + 1)}`,
      actionBadge: isToday ? 'Active Target' : undefined,
    };
  });

  return (
    <AppLayout breadcrumbs={[{ label: 'Study Plan' }]}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 24 }}>
        <div>
          <h1 style={{ fontSize: 24, fontWeight: 800, color: '#1e1b4b', margin: 0 }}>Study Plan</h1>
          <p style={{ fontSize: 14, color: '#64748b', marginTop: 4 }}>
            Built from your study time, free days and tuition days.
          </p>
        </div>
        <button
          type="button"
          style={{
            background: '#4f46e5',
            color: '#fff',
            border: 'none',
            borderRadius: 10,
            padding: '10px 20px',
            fontWeight: 600,
            fontSize: 14,
            cursor: 'pointer',
          }}
        >
          Edit schedule
        </button>
      </div>

      {/* Week Calendar Row matching Screenshot 2 */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))',
          gap: 16,
          marginBottom: 24,
        }}
      >
        {weekSchedule.map((item) => {
          const isHighlight = item.isToday;
          return (
            <div
              key={item.dayName}
              style={{
                background: '#ffffff',
                borderRadius: 16,
                padding: '16px 14px',
                border: isHighlight ? '2px solid #4f46e5' : '1px solid #f1f5f9',
                boxShadow: isHighlight ? '0 4px 12px rgba(79, 70, 229, 0.1)' : '0 2px 6px rgba(0,0,0,0.02)',
                display: 'flex',
                flexDirection: 'column',
                minHeight: 180,
              }}
            >
              <div
                style={{
                  fontSize: 14,
                  fontWeight: 700,
                  color: isHighlight ? '#4f46e5' : '#1e293b',
                  marginBottom: 12,
                }}
              >
                {item.isToday ? `${item.dayName} · Today` : item.dayName}
              </div>

              {/* Badges Stack */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8, flex: 1 }}>
                {item.studySlotText && (
                  <div
                    style={{
                      background: item.isTuitionDay ? '#f3e8ff' : '#ecfdf5',
                      color: item.isTuitionDay ? '#6b21a8' : '#065f46',
                      borderRadius: 8,
                      padding: '8px 10px',
                      fontSize: 12,
                      fontWeight: 600,
                    }}
                  >
                    {item.studySlotText}
                  </div>
                )}

                {item.isFreeDay && (
                  <div
                    style={{
                      background: '#f8fafc',
                      color: '#64748b',
                      borderRadius: 8,
                      padding: '8px 10px',
                      fontSize: 12,
                      fontWeight: 500,
                    }}
                  >
                    Free day
                  </div>
                )}

                {item.subjectBadge && (
                  <div
                    style={{
                      background: item.dayName === 'Sat' ? '#fee2e2' : item.dayName === 'Tue' ? '#f5f3ff' : '#fef3c7',
                      color: item.dayName === 'Sat' ? '#991b1b' : item.dayName === 'Tue' ? '#5b21b6' : '#92400e',
                      borderRadius: 8,
                      padding: '8px 10px',
                      fontSize: 12,
                      fontWeight: 600,
                    }}
                  >
                    {item.subjectBadge}
                  </div>
                )}

                {item.actionBadge && (
                  <div
                    style={{
                      background: '#ede9fe',
                      color: '#5b21b6',
                      borderRadius: 8,
                      padding: '8px 10px',
                      fontSize: 12,
                      fontWeight: 600,
                    }}
                  >
                    {item.actionBadge}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Bottom 2 Cards Grid matching Screenshot 2 */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
          gap: 20,
        }}
      >
        {/* Today's Goal Card with Progress Ring */}
        <div
          style={{
            background: '#ffffff',
            borderRadius: 20,
            padding: '24px 28px',
            border: '1px solid #f1f5f9',
            display: 'flex',
            alignItems: 'center',
            gap: 24,
            boxShadow: '0 2px 6px rgba(0,0,0,0.02)',
          }}
        >
          {/* Circular Meter */}
          <div
            style={{
              position: 'relative',
              width: 84,
              height: 84,
              borderRadius: '50%',
              background: 'conic-gradient(#4f46e5 0% 45%, #e0e7ff 45% 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0,
            }}
          >
            <div
              style={{
                width: 66,
                height: 66,
                borderRadius: '50%',
                background: '#ffffff',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontWeight: 700,
                fontSize: 13,
                color: '#1e1b4b',
              }}
            >
              1h 20m
            </div>
          </div>

          <div>
            <h2 style={{ fontSize: 18, fontWeight: 800, color: '#1e1b4b', margin: 0 }}>
              Today's goal: {targetDailyHours} hours
            </h2>
            <p style={{ fontSize: 14, color: '#64748b', margin: '4px 0 0 0' }}>
              {target?.preferred_slot ? `${target.preferred_slot} is your study slot.` : 'Evening is your study slot.'}
            </p>
          </div>
        </div>

        {/* Exam Target Card */}
        <div
          style={{
            background: '#ffffff',
            borderRadius: 20,
            padding: '24px 28px',
            border: '1px solid #f1f5f9',
            boxShadow: '0 2px 6px rgba(0,0,0,0.02)',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
          }}
        >
          <h2 style={{ fontSize: 18, fontWeight: 800, color: '#1e1b4b', margin: 0 }}>
            Exam target: {board} {grade}
          </h2>
          <p style={{ fontSize: 14, color: '#64748b', margin: '6px 0 0 0' }}>
            {overview?.goals?.[0] || `${board} ${grade} Board Curriculum Target`}. We track your study routine daily.
          </p>
        </div>
      </div>
    </AppLayout>
  );
};
