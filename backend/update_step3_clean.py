with open('frontend/src/pages/onboarding/Step3Page.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update imports
old_import = "import React, { useState } from 'react';"
new_import = "import React, { useEffect, useState } from 'react';\nimport { useAuth } from '../../context/AuthContext';"
assert old_import in code, "old_import not found"
code = code.replace(old_import, new_import, 1)

# 2. Update existingStep3 resolution
old_step3 = """  // Retrieve existing state from navigation or localStorage
  const existingStep3 = (() => {
    if (location.state && (location.state.preferred_style || location.state.goals)) {
      return location.state;
    }
    try {
      const stored = localStorage.getItem('smartlearn_onboarding_step3');
      if (stored) return JSON.parse(stored);
    } catch {
      // Ignore localStorage error
    }
    return null;
  })();

  const [selectedStyle, setSelectedStyle] = useState<string>(
    existingStep3?.preferred_style || ''
  );
  const [selectedGoals, setSelectedGoals] = useState<string[]>(() => {
    if (Array.isArray(existingStep3?.goals)) {
      return existingStep3.goals;
    }
    return [];
  });"""

new_step3 = """  const { onboardingSelections, refreshOnboardingSelections } = useAuth();

  const [selectedStyle, setSelectedStyle] = useState<string>(
    location.state?.preferred_style || onboardingSelections?.preferred_learning_style || ''
  );
  const [selectedGoals, setSelectedGoals] = useState<string[]>(() => {
    if (Array.isArray(location.state?.goals)) {
      return location.state.goals;
    }
    if (Array.isArray(onboardingSelections?.study_goals) && onboardingSelections.study_goals.length > 0) {
      return onboardingSelections.study_goals;
    }
    return [];
  });

  useEffect(() => {
    refreshOnboardingSelections().then((sel) => {
      if (sel) {
        if (!selectedStyle && sel.preferred_learning_style) setSelectedStyle(sel.preferred_learning_style);
        if (selectedGoals.length === 0 && sel.study_goals?.length) setSelectedGoals(sel.study_goals);
      }
    });
  }, []);"""

assert old_step3 in code, "old_step3 not found"
code = code.replace(old_step3, new_step3, 1)

with open('frontend/src/pages/onboarding/Step3Page.tsx', 'w', encoding='utf-8') as f:
    f.write(code)
print("Updated frontend/src/pages/onboarding/Step3Page.tsx successfully")

