with open('frontend/src/pages/learning/SubjectDetailPage.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace hardcoded fallbacks
old_fallbacks = """  const board = overview?.board || subject?.board || 'ISC';
  const grade = overview?.grade || subject?.grade || 'Class 11';
  const stream = overview?.academic_stream ? overview.academic_stream.replace(' / Arts', '') : 'Humanities';
  const subjectName = subject?.name || 'History';
  const overallPct = subject?.progress_percentage ?? 40;"""

new_fallbacks = """  const board = subject?.board || overview?.board || 'Curriculum';
  const grade = subject?.grade || overview?.grade || 'Class 10';
  const stream = subject?.academic_stream || (overview?.academic_stream ? overview.academic_stream.replace(' / Arts', '') : null);
  const subjectName = subject?.name || 'Subject Syllabus';
  const overallPct = subject?.progress_percentage ?? 0;"""

assert old_fallbacks in code, "old_fallbacks not found"
code = code.replace(old_fallbacks, new_fallbacks, 1)

with open('frontend/src/pages/learning/SubjectDetailPage.tsx', 'w', encoding='utf-8') as f:
    f.write(code)
print("Updated frontend/src/pages/learning/SubjectDetailPage.tsx successfully")

