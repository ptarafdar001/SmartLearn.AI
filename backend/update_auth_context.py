with open('frontend/src/context/AuthContext.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update imports
old_import = "import type { OnboardingStatusResponse } from '../types/onboarding';"
new_import = "import type { OnboardingStatusResponse, OnboardingSelectionsResponse } from '../types/onboarding';"
assert old_import in code, "old_import not found"
code = code.replace(old_import, new_import, 1)

# 2. Update AuthContextType interface
old_interface = """  onboardingStatus: OnboardingStatusResponse | null;
  isLoading: boolean;"""

new_interface = """  onboardingStatus: OnboardingStatusResponse | null;
  onboardingSelections: OnboardingSelectionsResponse | null;
  isLoading: boolean;"""
assert old_interface in code, "old_interface not found"
code = code.replace(old_interface, new_interface, 1)

# Add fetchOnboardingSelections and setOnboardingSelections
old_interface2 = """  refreshUser: () => Promise<User | null>;
  checkOnboardingStatus: () => Promise<OnboardingStatusResponse | null>;"""

new_interface2 = """  refreshUser: () => Promise<User | null>;
  checkOnboardingStatus: () => Promise<OnboardingStatusResponse | null>;
  refreshOnboardingSelections: () => Promise<OnboardingSelectionsResponse | null>;"""
assert old_interface2 in code, "old_interface2 not found"
code = code.replace(old_interface2, new_interface2, 1)

# 3. Add state in AuthProvider
old_state = "  const [onboardingStatus, setOnboardingStatus] = useState<OnboardingStatusResponse | null>(null);"
new_state = """  const [onboardingStatus, setOnboardingStatus] = useState<OnboardingStatusResponse | null>(null);
  const [onboardingSelections, setOnboardingSelections] = useState<OnboardingSelectionsResponse | null>(null);"""
assert old_state in code, "old_state not found"
code = code.replace(old_state, new_state, 1)

# 4. Add refreshOnboardingSelections function
old_check = """  const checkOnboardingStatus = useCallback(async (): Promise<OnboardingStatusResponse | null> => {
    try {
      const statusData = await onboardingService.getOnboardingStatus();
      setOnboardingStatus(statusData);
      setIsOnboarded(statusData.is_onboarded);
      return statusData;
    } catch {
      return null;
    }
  }, []);"""

new_check = """  const refreshOnboardingSelections = useCallback(async (): Promise<OnboardingSelectionsResponse | null> => {
    try {
      const selectionsData = await onboardingService.getOnboardingSelections();
      setOnboardingSelections(selectionsData);
      return selectionsData;
    } catch {
      return null;
    }
  }, []);

  const checkOnboardingStatus = useCallback(async (): Promise<OnboardingStatusResponse | null> => {
    try {
      const statusData = await onboardingService.getOnboardingStatus();
      setOnboardingStatus(statusData);
      setIsOnboarded(statusData.is_onboarded);
      await refreshOnboardingSelections();
      return statusData;
    } catch {
      return null;
    }
  }, [refreshOnboardingSelections]);"""

assert old_check in code, "old_check not found"
code = code.replace(old_check, new_check, 1)

# 5. In refreshUser, call refreshOnboardingSelections
old_refresh_user = """      let onboarded = userData.is_onboarded;
      try {
        const statusData = await onboardingService.getOnboardingStatus();
        setOnboardingStatus(statusData);
        onboarded = statusData.is_onboarded;
      } catch {
        // Graceful fallback to user profile is_onboarded if status endpoint fails
      }
      setIsOnboarded(onboarded);

      return userData;"""

new_refresh_user = """      let onboarded = userData.is_onboarded;
      try {
        const [statusData, selectionsData] = await Promise.all([
          onboardingService.getOnboardingStatus().catch(() => null),
          onboardingService.getOnboardingSelections().catch(() => null),
        ]);
        if (statusData) {
          setOnboardingStatus(statusData);
          onboarded = statusData.is_onboarded;
        }
        if (selectionsData) {
          setOnboardingSelections(selectionsData);
        }
      } catch {
        // Graceful fallback
      }
      setIsOnboarded(onboarded);

      return userData;"""

assert old_refresh_user in code, "old_refresh_user not found"
code = code.replace(old_refresh_user, new_refresh_user, 1)

# In logout, clear onboardingSelections
old_logout = """    setUser(null);
    setToken(null);
    setOnboardingStatus(null);
    setIsOnboarded(false);"""

new_logout = """    setUser(null);
    setToken(null);
    setOnboardingStatus(null);
    setOnboardingSelections(null);
    setIsOnboarded(false);"""
assert old_logout in code, "old_logout not found"
code = code.replace(old_logout, new_logout, 1)

# 6. Provider value
old_value = """        refreshUser,
        checkOnboardingStatus,
      }}"""

new_value = """        onboardingSelections,
        refreshUser,
        checkOnboardingStatus,
        refreshOnboardingSelections,
      }}"""
assert old_value in code, "old_value not found"
code = code.replace(old_value, new_value, 1)

with open('frontend/src/context/AuthContext.tsx', 'w', encoding='utf-8') as f:
    f.write(code)
print("Updated frontend/src/context/AuthContext.tsx successfully")

