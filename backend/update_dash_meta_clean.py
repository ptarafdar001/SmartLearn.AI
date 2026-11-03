with open('frontend/src/pages/DashboardPage.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace hardcoded fallbacks in student metadata
old_meta = """  const studentName = overview?.full_name || user?.full_name || 'pg';
  const firstName = studentName.split(' ')[0] || studentName;
  const board = overview?.board || 'ISC';
  const grade = overview?.grade || 'Class 11';
  const stream = overview?.academic_stream ? overview.academic_stream.replace(' / Arts', '') : 'Humanities';"""

new_meta = """  const studentName = overview?.full_name || user?.full_name || 'Student';
  const firstName = studentName.split(' ')[0] || studentName;
  const board = overview?.board || 'Curriculum';
  const grade = overview?.grade || 'Class 10';
  const stream = overview?.academic_stream ? overview.academic_stream.replace(' / Arts', '') : null;"""

assert old_meta in code, "old_meta not found"
code = code.replace(old_meta, new_meta, 1)

with open('frontend/src/pages/DashboardPage.tsx', 'w', encoding='utf-8') as f:
    f.write(code)
print("Updated frontend/src/pages/DashboardPage.tsx successfully")

