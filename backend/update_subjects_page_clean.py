with open('frontend/src/pages/SubjectsPage.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace getSubjectCardDetails to always preserve the exact subject name
old_card_details = """  // Helper for pastel card theme and explore button color
  const getSubjectCardDetails = (index: number, name: string) => {
    const lower = name.toLowerCase();
    if (lower.includes('history')) {
      return {
        themeCls: 'theme-yellow',
        barColor: '#eab308',
        btnCls: 'btn-orange',
        displayName: 'History & Civics',
        fallbackChapters: 12,
        fallbackTopics: 48,
        fallbackProgress: 40,
      };
    }
    if (lower.includes('geography')) {
      return {
        themeCls: 'theme-mint',
        barColor: '#10b981',
        btnCls: 'btn-mint',
        displayName: 'Geography',
        fallbackChapters: 10,
        fallbackTopics: 36,
        fallbackProgress: 15,
      };
    }
    if (lower.includes('english')) {
      return {
        themeCls: 'theme-peach',
        barColor: '#f97316',
        btnCls: 'btn-coral',
        displayName: 'English',
        fallbackChapters: 9,
        fallbackTopics: 30,
        fallbackProgress: 60,
      };
    }
    if (lower.includes('pol')) {
      return {
        themeCls: 'theme-purple',
        barColor: '#8b5cf6',
        btnCls: 'btn-purple',
        displayName: 'Political Science',
        fallbackChapters: 11,
        fallbackTopics: 40,
        fallbackProgress: 0,
      };
    }
    const defaults = [
      { themeCls: 'theme-yellow', barColor: '#eab308', btnCls: 'btn-orange', displayName: name, fallbackChapters: 10, fallbackTopics: 30, fallbackProgress: 20 },
      { themeCls: 'theme-mint', barColor: '#10b981', btnCls: 'btn-mint', displayName: name, fallbackChapters: 8, fallbackTopics: 24, fallbackProgress: 10 },
      { themeCls: 'theme-peach', barColor: '#f97316', btnCls: 'btn-coral', displayName: name, fallbackChapters: 6, fallbackTopics: 18, fallbackProgress: 50 },
      { themeCls: 'theme-purple', barColor: '#8b5cf6', btnCls: 'btn-purple', displayName: name, fallbackChapters: 12, fallbackTopics: 36, fallbackProgress: 0 },
    ];
    return defaults[index % defaults.length];
  };"""

new_card_details = """  // Helper for pastel card theme and explore button color
  const getSubjectCardDetails = (index: number, name: string) => {
    const themes = [
      { themeCls: 'theme-yellow', barColor: '#eab308', btnCls: 'btn-orange', displayName: name, fallbackChapters: 4, fallbackTopics: 8, fallbackProgress: 0 },
      { themeCls: 'theme-mint', barColor: '#10b981', btnCls: 'btn-mint', displayName: name, fallbackChapters: 4, fallbackTopics: 8, fallbackProgress: 0 },
      { themeCls: 'theme-peach', barColor: '#f97316', btnCls: 'btn-coral', displayName: name, fallbackChapters: 4, fallbackTopics: 8, fallbackProgress: 0 },
      { themeCls: 'theme-purple', barColor: '#8b5cf6', btnCls: 'btn-purple', displayName: name, fallbackChapters: 4, fallbackTopics: 8, fallbackProgress: 0 },
    ];
    return themes[index % themes.length];
  };"""

assert old_card_details in code, "old_card_details not found"
code = code.replace(old_card_details, new_card_details, 1)

with open('frontend/src/pages/SubjectsPage.tsx', 'w', encoding='utf-8') as f:
    f.write(code)
print("Updated frontend/src/pages/SubjectsPage.tsx successfully")

