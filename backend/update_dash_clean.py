with open('frontend/src/pages/DashboardPage.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace Continue learning fallback text
old_streak_calc = """  // Streak & Studied time
  const streakDays = overview?.study_streak_days ?? (continueItem ? 4 : 0);
  const studiedFormatted = continueItem?.time_spent_seconds
    ? `${Math.floor(continueItem.time_spent_seconds / 3600)}h ${Math.floor((continueItem.time_spent_seconds % 3600) / 60)}m`
    : '1h 20m';

  // Continue learning item
  const activeContinue = continueItem;
  const subjectInitial = activeContinue ? (activeContinue.subject_name.charAt(0) || 'H').toUpperCase() : 'H';"""

new_streak_calc = """  // Streak & Studied time
  const streakDays = overview?.study_streak_days ?? (continueItem ? 1 : 0);
  const studiedFormatted = continueItem?.time_spent_seconds
    ? `${Math.floor(continueItem.time_spent_seconds / 3600)}h ${Math.floor((continueItem.time_spent_seconds % 3600) / 60)}m`
    : '0m';

  // Continue learning item
  const activeContinue = continueItem;
  const subjectInitial = activeContinue
    ? (activeContinue.subject_name.charAt(0) || 'S').toUpperCase()
    : subjects[0]?.name?.charAt(0).toUpperCase() || 'S';"""

assert old_streak_calc in code, "old_streak_calc not found"
code = code.replace(old_streak_calc, new_streak_calc, 1)

# Replace Today's plan static names
old_today_plan = """                  <div className="plan-items-list">
                    <div className="plan-item-pill plan-mint">
                      {slot === 'morning' ? '9:00 AM' : slot === 'afternoon' ? '2:00 PM' : '6:00 PM'} ·{' '}
                      {subjects[0]?.name || 'History'} notes
                    </div>
                    <div className="plan-item-pill plan-purple">
                      {slot === 'morning' ? '10:00 AM' : slot === 'afternoon' ? '3:00 PM' : '7:00 PM'} ·{' '}
                      {subjects[1]?.name || 'Geography'} quiz
                    </div>
                    <div className="plan-item-pill plan-yellow">
                      {slot === 'morning' ? '11:00 AM' : slot === 'afternoon' ? '4:00 PM' : '8:00 PM'} · Revise with
                      AI Tutor
                    </div>
                  </div>"""

new_today_plan = """                  <div className="plan-items-list">
                    <div className="plan-item-pill plan-mint">
                      {slot === 'morning' ? '9:00 AM' : slot === 'afternoon' ? '2:00 PM' : '6:00 PM'} ·{' '}
                      {subjects[0]?.name || 'Core Subject'} Study Notes
                    </div>
                    <div className="plan-item-pill plan-purple">
                      {slot === 'morning' ? '10:00 AM' : slot === 'afternoon' ? '3:00 PM' : '7:00 PM'} ·{' '}
                      {subjects[1]?.name || subjects[0]?.name || 'Syllabus'} Practice Quiz
                    </div>
                    <div className="plan-item-pill plan-yellow">
                      {slot === 'morning' ? '11:00 AM' : slot === 'afternoon' ? '4:00 PM' : '8:00 PM'} · Revise with
                      AI Tutor
                    </div>
                  </div>"""

assert old_today_plan in code, "old_today_plan not found"
code = code.replace(old_today_plan, new_today_plan, 1)

with open('frontend/src/pages/DashboardPage.tsx', 'w', encoding='utf-8') as f:
    f.write(code)
print("Updated frontend/src/pages/DashboardPage.tsx successfully")

