with open('frontend/src/pages/StudyPlanPage.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace hardcoded days and subjects in weekSchedule
old_calc = """  const target = overview?.study_target;
  const board = overview?.board || 'ISC';
  const targetDailyHours = target?.daily_target_hours || 3;
  const slot = target?.preferred_slot?.toLowerCase() || 'evening';
  const slotTiming = slot === 'morning' ? '9 AM - 12 PM' : slot === 'afternoon' ? '2 - 5 PM' : '6 - 9 PM';

  const daysOfWeek = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  
  // Current day calculation
  const currentDayIndex = (new Date().getDay() + 6) % 7; // 0 = Mon, 4 = Fri

  const weekSchedule: DaySchedule[] = daysOfWeek.map((shortDay, idx) => {
    const isToday = idx === currentDayIndex || (idx === 4); // Highlight Friday/Today like in screenshot

    if (shortDay === 'Sat' || shortDay === 'Sun') {
      return {
        dayName: shortDay,
        isToday: false,
        isFreeDay: true,
        isTuitionDay: false,
        subjectBadge: shortDay === 'Sat' ? 'English: Ch 3' : undefined,
      };
    }

    if (shortDay === 'Tue' || shortDay === 'Thu') {
      return {
        dayName: shortDay,
        isToday: false,
        isFreeDay: false,
        isTuitionDay: true,
        studySlotText: 'Tuition',
        subjectBadge: shortDay === 'Tue' ? 'Short revision' : undefined,
      };
    }

    return {
      dayName: shortDay,
      isToday,
      isFreeDay: false,
      isTuitionDay: false,
      studySlotText: `${slotTiming} Study`,
      subjectBadge: shortDay === 'Mon' ? 'History: Ch 2' : shortDay === 'Wed' ? 'Geography: Ch 1' : undefined,
      actionBadge: isToday ? 'Quiz time' : undefined,
    };
  });"""

new_calc = """  const target = overview?.study_target;
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
  });"""

assert old_calc in code, "old_calc not found"
code = code.replace(old_calc, new_calc, 1)

# Also fix the bottom exam target card
old_exam_target = """          <h2 style={{ fontSize: 18, fontWeight: 800, color: '#1e1b4b', margin: 0 }}>
            Exam target
          </h2>
          <p style={{ fontSize: 14, color: '#64748b', margin: '6px 0 0 0' }}>
            {board} 2027 · 95% goal. We will tell you if you fall behind.
          </p>"""

new_exam_target = """          <h2 style={{ fontSize: 18, fontWeight: 800, color: '#1e1b4b', margin: 0 }}>
            Exam target: {board} {grade}
          </h2>
          <p style={{ fontSize: 14, color: '#64748b', margin: '6px 0 0 0' }}>
            {overview?.goals?.[0] || `${board} ${grade} Board Curriculum Target`}. We track your study routine daily.
          </p>"""

assert old_exam_target in code, "old_exam_target not found"
code = code.replace(old_exam_target, new_exam_target, 1)

with open('frontend/src/pages/StudyPlanPage.tsx', 'w', encoding='utf-8') as f:
    f.write(code)
print("Updated frontend/src/pages/StudyPlanPage.tsx successfully")

