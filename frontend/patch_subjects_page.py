with open('frontend/src/pages/SubjectsPage.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace("Official CISCE syllabus, chapter by chapter.", "Official curriculum syllabus, chapter by chapter.")
text = text.replace("const grade = overview?.grade || 'Class 11';", "const grade = overview?.grade || 'Class 10';")

with open('frontend/src/pages/SubjectsPage.tsx', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated SubjectsPage.tsx successfully")

