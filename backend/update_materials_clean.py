with open('frontend/src/pages/StudyMaterialsPage.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

old_str = "{sub.name.toLowerCase() === 'history' ? 'History' : sub.name}"
new_str = "{sub.name}"
assert old_str in code, "old_str not found"
code = code.replace(old_str, new_str, 1)

with open('frontend/src/pages/StudyMaterialsPage.tsx', 'w', encoding='utf-8') as f:
    f.write(code)
print("Updated StudyMaterialsPage.tsx")

