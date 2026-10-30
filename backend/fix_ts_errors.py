with open('frontend/src/pages/onboarding/Step1Page.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

old_ref = "const prevData = (location.state as any) || existingStep1 || {};"
new_ref = "const prevData = (location.state as any) || onboardingSelections || {};"
assert old_ref in code, "old_ref not found"
code = code.replace(old_ref, new_ref, 1)

with open('frontend/src/pages/onboarding/Step1Page.tsx', 'w', encoding='utf-8') as f:
    f.write(code)
print("Fixed Step1Page.tsx")

with open('frontend/src/pages/onboarding/Step2Page.tsx', 'r', encoding='utf-8') as f:
    code2 = f.read()

old_import2 = "import React, { useEffect, useState } from 'react';"
new_import2 = "import React, { useState } from 'react';"
code2 = code2.replace(old_import2, new_import2, 1)

old_auth2 = "const { onboardingSelections, refreshOnboardingSelections } = useAuth();"
new_auth2 = "const { onboardingSelections } = useAuth();"
code2 = code2.replace(old_auth2, new_auth2, 1)

with open('frontend/src/pages/onboarding/Step2Page.tsx', 'w', encoding='utf-8') as f:
    f.write(code2)
print("Fixed Step2Page.tsx")

