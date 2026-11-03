with open('frontend/src/pages/onboarding/Step4Page.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update imports
old_import = "import React, { useState } from 'react';"
new_import = "import React, { useEffect, useState } from 'react';"
assert old_import in code, "old_import not found"
code = code.replace(old_import, new_import, 1)

# 2. Update prevContext resolution and state initialization
old_init = """  const { refreshUser } = useAuth();

  // Retrieve prior onboarding context from location.state or localStorage
  const prevContext = (() => {
    let context: any = {};
    try {
      const s1 = localStorage.getItem('smartlearn_onboarding_step1');
      if (s1) context = { ...context, ...JSON.parse(s1) };
    } catch {
      // Ignore
    }
    try {
      const s3 = localStorage.getItem('smartlearn_onboarding_step3');
      if (s3) context = { ...context, ...JSON.parse(s3) };
    } catch {
      // Ignore
    }
    try {
      const s4 = localStorage.getItem('smartlearn_onboarding_step4');
      if (s4) context = { ...context, ...JSON.parse(s4) };
    } catch {
      // Ignore
    }
    if (location.state) {
      context = { ...context, ...location.state };
    }
    return context;
  })();

  const [selectedTargetHours, setSelectedTargetHours] = useState<number | null>(
    typeof prevContext?.daily_target_hours === 'number'
      ? prevContext.daily_target_hours
      : null
  );

  const [selectedSlot, setSelectedSlot] = useState<string>(
    prevContext?.preferred_slot || ''
  );

  const [selectedDays, setSelectedDays] = useState<string[]>(() => {
    if (Array.isArray(prevContext?.available_days)) {
      return prevContext.available_days;
    }
    return [];
  });"""

new_init = """  const { refreshUser, onboardingSelections, refreshOnboardingSelections } = useAuth();

  const prevContext = location.state || {};

  const [selectedTargetHours, setSelectedTargetHours] = useState<number | null>(
    typeof prevContext?.daily_target_hours === 'number'
      ? prevContext.daily_target_hours
      : (onboardingSelections?.daily_target_hours ?? null)
  );

  const [selectedSlot, setSelectedSlot] = useState<string>(
    prevContext?.preferred_slot || onboardingSelections?.preferred_slot || ''
  );

  const [selectedDays, setSelectedDays] = useState<string[]>(() => {
    if (Array.isArray(prevContext?.available_days) && prevContext.available_days.length > 0) {
      return prevContext.available_days;
    }
    if (Array.isArray(onboardingSelections?.available_days) && onboardingSelections.available_days.length > 0) {
      return onboardingSelections.available_days;
    }
    return [];
  });

  useEffect(() => {
    refreshOnboardingSelections().then((sel) => {
      if (sel) {
        if (selectedTargetHours === null && sel.daily_target_hours) setSelectedTargetHours(sel.daily_target_hours);
        if (!selectedSlot && sel.preferred_slot) setSelectedSlot(sel.preferred_slot);
        if (selectedDays.length === 0 && sel.available_days?.length) setSelectedDays(sel.available_days);
      }
    });
  }, []);"""

assert old_init in code, "old_init not found"
code = code.replace(old_init, new_init, 1)

# 3. Replace lines around studentBoard
lines = code.splitlines()
target_start = -1
target_end = -1
for i, l in enumerate(lines):
    if "const studentBoard = prevContext?.board" in l:
        target_start = i
    if "const styleText = prevContext?.preferred_style" in l:
        target_end = i
        break

assert target_start != -1 and target_end != -1, "Target indices not found"
target_block = '\n'.join(lines[target_start:target_end+1])

replacement_block = """  const studentBoard = prevContext?.board || onboardingSelections?.board || 'CBSE';
  const studentGrade = prevContext?.grade || onboardingSelections?.grade || 'Class 10';
  const studentStream = prevContext?.academic_stream || onboardingSelections?.academic_stream || null;
  const isSenior = studentGrade === 'Class 11' || studentGrade === 'Class 12';

  const syllabusText = isSenior && studentStream
    ? `${studentBoard} · ${studentGrade} (${studentStream})`
    : `${studentBoard} · ${studentGrade}`;

  const subjectsText = (() => {
    if (Array.isArray(prevContext?.selectedSubjectNames) && prevContext.selectedSubjectNames.length > 0) {
      return prevContext.selectedSubjectNames.join(', ');
    }
    if (Array.isArray(onboardingSelections?.enrolled_subjects) && onboardingSelections.enrolled_subjects.length > 0) {
      return onboardingSelections.enrolled_subjects.join(', ');
    }
    return 'Not specified';
  })();

  const styleText = prevContext?.preferred_style || onboardingSelections?.preferred_learning_style || 'Not specified';"""

code = code.replace(target_block, replacement_block, 1)

with open('frontend/src/pages/onboarding/Step4Page.tsx', 'w', encoding='utf-8') as f:
    f.write(code)
print("Updated frontend/src/pages/onboarding/Step4Page.tsx successfully")
