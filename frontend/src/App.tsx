import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { DashboardPlaceholder } from './pages/DashboardPlaceholder';
import { ProtectedRoute } from './routes/ProtectedRoute';
import { PublicOnlyRoute } from './routes/PublicOnlyRoute';
import { OnboardingRoute } from './routes/OnboardingRoute';
import { Step1Page } from './pages/onboarding/Step1Page';
import { Step2Page } from './pages/onboarding/Step2Page';
import { Step3Page } from './pages/onboarding/Step3Page';
import { Step4Page } from './pages/onboarding/Step4Page';

export const RootRedirect: React.FC = () => {
  const { isAuthenticated, isLoading, isOnboarded } = useAuth();

  if (isLoading) {
    return (
      <div className="auth-page-container">
        <div
          className="btn-spinner"
          style={{
            borderColor: 'rgba(79, 70, 229, 0.3)',
            borderTopColor: '#4f46e5',
            width: 36,
            height: 36,
          }}
        />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (isOnboarded) {
    return <Navigate to="/dashboard" replace />;
  }

  return <Navigate to="/onboarding/step1" replace />;
};

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* Public-only routes */}
          <Route element={<PublicOnlyRoute />}>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
          </Route>

          {/* Protected onboarding wizard routes */}
          <Route element={<OnboardingRoute />}>
            <Route path="/onboarding" element={<Navigate to="/onboarding/step1" replace />} />
            <Route path="/onboarding/step1" element={<Step1Page />} />
            <Route path="/onboarding/step2" element={<Step2Page />} />
            <Route path="/onboarding/step3" element={<Step3Page />} />
            <Route path="/onboarding/step4" element={<Step4Page />} />
          </Route>

          {/* Protected authenticated routes */}
          <Route element={<ProtectedRoute />}>
            <Route path="/dashboard" element={<DashboardPlaceholder />} />
          </Route>

          {/* Root and fallback */}
          <Route path="/" element={<RootRedirect />} />
          <Route path="*" element={<RootRedirect />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;