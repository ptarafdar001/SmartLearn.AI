import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import type { UserRole } from '../types/auth';
import { BrandLogo } from '../components/common/BrandLogo';
import { RoleSelector } from '../components/common/RoleSelector';
import { Input } from '../components/common/Input';
import { Checkbox } from '../components/common/Checkbox';
import { Button } from '../components/common/Button';
import { Alert } from '../components/common/Alert';
import '../styles/auth.css';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [role, setRole] = useState<UserRole>('student');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);

  const [errors, setErrors] = useState<{
    email?: string;
    password?: string;
    general?: string;
  }>({});
  const [infoNotice, setInfoNotice] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleRoleSelect = (selectedRole: UserRole) => {
    if (selectedRole !== 'student') {
      setInfoNotice(
        `${selectedRole.charAt(0).toUpperCase() + selectedRole.slice(1)} accounts are coming soon. Please sign in with your student account.`
      );
      setRole('student');
    } else {
      setInfoNotice(null);
      setRole('student');
    }
  };

  const handleForgotPassword = (e: React.MouseEvent) => {
    e.preventDefault();
    setInfoNotice(
      'Self-service password recovery is coming soon. Please reach out to your administrator to reset your password.'
    );
  };

  const handleGoogleSignIn = () => {
    setInfoNotice(
      'Sign in with Google will be enabled in a future release. Please sign in with your email and password.'
    );
  };

  const validate = (): boolean => {
    const newErrors: typeof errors = {};

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!email.trim()) {
      newErrors.email = 'Please enter your email address';
    } else if (!emailRegex.test(email.trim())) {
      newErrors.email = 'Please enter a valid email address';
    }

    if (!password) {
      newErrors.password = 'Please enter your password';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});

    if (!validate()) {
      return;
    }

    setIsLoading(true);
    try {
      const loggedInUser = await login({
        email: email.trim().toLowerCase(),
        password,
      });

      // On successful login, route based on onboarding status
      if (loggedInUser.is_onboarded) {
        navigate('/dashboard', { replace: true });
      } else {
        navigate('/onboarding/step1', { replace: true });
      }
    } catch (err: any) {
      setErrors({
        general: err.message || 'Invalid email or password. Please try again.',
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-page-container">
      <div className="auth-card" role="main">
        {/* Brand Logo */}
        <BrandLogo size="md" />

        {/* Title and Subtitle */}
        <h1 className="auth-title">Welcome back</h1>
        <p className="auth-subtitle">Please enter your details to sign in to your account</p>

        {/* Role Selector */}
        <RoleSelector selectedRole={role} onSelectRole={handleRoleSelect} />

        {infoNotice && (
          <Alert type="info" message={infoNotice} onClose={() => setInfoNotice(null)} />
        )}

        {errors.general && (
          <Alert type="error" message={errors.general} onClose={() => setErrors({ ...errors, general: undefined })} />
        )}

        {/* Login Form */}
        <form className="auth-form" onSubmit={handleSubmit} noValidate>
          <Input
            id="login-email"
            label="Email Address"
            type="email"
            placeholder="Enter your email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            error={errors.email}
            required
            autoComplete="email"
          />

          <Input
            id="login-password"
            label="Password"
            type="password"
            placeholder="Enter your password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            error={errors.password}
            showPasswordToggle
            required
            autoComplete="current-password"
          />

          {/* Remember Me and Forgot Password Row */}
          <div className="login-options-row">
            <Checkbox
              id="login-remember"
              checked={rememberMe}
              onChange={setRememberMe}
            >
              Remember me
            </Checkbox>

            <a
              href="#forgot-password"
              className="forgot-password-link"
              onClick={handleForgotPassword}
            >
              Forgot password?
            </a>
          </div>

          <Button type="submit" variant="primary" isLoading={isLoading}>
            Sign In
          </Button>

          <Button
            type="button"
            variant="google"
            onClick={handleGoogleSignIn}
          >
            Sign in with Google
          </Button>
        </form>

        <div className="auth-footer-text">
          Don't have an account?
          <Link to="/register" className="auth-link">
            Create account
          </Link>
        </div>
      </div>
    </div>
  );
};
