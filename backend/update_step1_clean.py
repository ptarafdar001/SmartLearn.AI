with open('frontend/src/pages/onboarding/Step1Page.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update imports
old_import = "import React, { useState } from 'react';"
new_import = "import React, { useEffect, useState } from 'react';\nimport { useAuth } from '../../context/AuthContext';"
assert old_import in code, "old_import not found"
code = code.replace(old_import, new_import, 1)

# 2. In component, pull onboardingSelections from useAuth()
old_init = """  const navigate = useNavigate();
  const location = useLocation();

  // Retrieve existing Step 1 selections if returning via Back navigation or from storage
  const existingStep1 = (() => {
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

  const [selectedBoard, setSelectedBoard] = useState<string>(existingStep1?.board || '');
  const [selectedState, setSelectedState] = useState<string>(existingStep1?.state || '');
  const [selectedGrade, setSelectedGrade] = useState<string>(existingStep1?.grade || '');"""

new_init = """  const navigate = useNavigate();
  const location = useLocation();
  const { onboardingSelections, refreshOnboardingSelections } = useAuth();

  const [selectedBoard, setSelectedBoard] = useState<string>(
    location.state?.board || onboardingSelections?.board || ''
  );
  const [selectedState, setSelectedState] = useState<string>(
    location.state?.state || ''
  );
  const [selectedGrade, setSelectedGrade] = useState<string>(
    location.state?.grade || onboardingSelections?.grade || ''
  );

  useEffect(() => {
    refreshOnboardingSelections().then((sel) => {
      if (sel) {
        if (!selectedBoard && sel.board) setSelectedBoard(sel.board);
        if (!selectedGrade && sel.grade) setSelectedGrade(sel.grade);
      }
    });
  }, []);"""

assert old_init in code, "old_init not found"
code = code.replace(old_init, new_init, 1)

with open('frontend/src/pages/onboarding/Step1Page.tsx', 'w', encoding='utf-8') as f:
    f.write(code)
print("Updated frontend/src/pages/onboarding/Step1Page.tsx successfully")

