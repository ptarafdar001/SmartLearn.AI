with open('frontend/src/pages/onboarding/Step2Page.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update imports
old_import = "import React, { useState } from 'react';"
new_import = "import React, { useEffect, useState } from 'react';\nimport { useAuth } from '../../context/AuthContext';"
assert old_import in code, "old_import not found"
code = code.replace(old_import, new_import, 1)

# 2. Update step1Context resolution
old_context = """  // Retrieve Step 1 selections from navigation state or localStorage
  const step1Context = (() => {
    if (location.state && (location.state.board || location.state.grade)) {
      return location.state;
    }
    try {
      const stored = localStorage.getItem('smartlearn_onboarding_step1');
      if (stored) return JSON.parse(stored);
    } catch {
      // Ignore localStorage errors
    }
    return null;
  })();

  const studentBoard = step1Context?.board || 'CBSE';
  const studentGrade = step1Context?.grade || 'Class 11';
  const studentState = step1Context?.state || null;
  const initialStream = step1Context?.academic_stream || '';"""

new_context = """  const { onboardingSelections, refreshOnboardingSelections } = useAuth();

  const step1Context = location.state || {};
  const studentBoard = step1Context.board || onboardingSelections?.board || 'CBSE';
  const studentGrade = step1Context.grade || onboardingSelections?.grade || 'Class 10';
  const studentState = step1Context.state || null;
  const initialStream = step1Context.academic_stream || onboardingSelections?.academic_stream || '';"""

assert old_context in code, "old_context not found"
code = code.replace(old_context, new_context, 1)

with open('frontend/src/pages/onboarding/Step2Page.tsx', 'w', encoding='utf-8') as f:
    f.write(code)
print("Updated frontend/src/pages/onboarding/Step2Page.tsx successfully")

