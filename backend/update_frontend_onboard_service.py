with open('frontend/src/services/onboarding.ts', 'r', encoding='utf-8') as f:
    content = f.read()

import_target = "  OnboardingStatusResponse,\n}"
import_replacement = "  OnboardingStatusResponse,\n  OnboardingSelectionsResponse,\n}"

if 'OnboardingSelectionsResponse' not in content:
    assert import_target in content, "import_target not found"
    content = content.replace(import_target, import_replacement, 1)

    method_addition = """
  async getOnboardingSelections(): Promise<OnboardingSelectionsResponse> {
    return apiClient<OnboardingSelectionsResponse>('/users/onboarding/selections', {
      method: 'GET',
      requiresAuth: true,
    });
  },
};"""

    method_target = "  async getOnboardingStatus(): Promise<OnboardingStatusResponse> {\n    return apiClient<OnboardingStatusResponse>('/users/onboarding/status', {\n      method: 'GET',\n      requiresAuth: true,\n    });\n  },\n};"

    assert method_target in content, "method_target not found"
    content = content.replace(method_target, "  async getOnboardingStatus(): Promise<OnboardingStatusResponse> {\n    return apiClient<OnboardingStatusResponse>('/users/onboarding/status', {\n      method: 'GET',\n      requiresAuth: true,\n    });\n  }," + method_addition, 1)

    with open('frontend/src/services/onboarding.ts', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated frontend/src/services/onboarding.ts")
else:
    print("Already updated frontend/src/services/onboarding.ts")

