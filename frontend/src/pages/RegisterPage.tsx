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

export const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const { register } = useAuth();

  const [role, setRole] = useState<UserRole>('student');
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [termsAccepted, setTermsAccepted] = useState(false);

  const [errors, setErrors] = useState<{
    fullName?: string;
    email?: string;
    password?: string;
    terms?: string;
    general?: string;
  }>({});
  const [roleNotice, setRoleNotice] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleRoleSelect = (selectedRole: UserRole) => {
    if (selectedRole !== 'student') {
      setRoleNotice(
        `${selectedRole.charAt(0).toUpperCase() + selectedRole.slice(1)} accounts are coming soon. Currently, SmartLearn.AI supports student accounts.`
      );
      setRole('student');
    } else {
      setRoleNotice(null);
      setRole('student');
    }
  };

  const validate = (): boolean => {
    const newErrors: typeof errors = {};

    if (!fullName.trim()) {
      newErrors.fullName = 'Please enter your full name';
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!email.trim()) {
      newErrors.email = 'Please enter your email address';
    } else if (!emailRegex.test(email.trim())) {
      newErrors.email = 'Please enter a valid email address';
    }

    if (!password) {
      newErrors.password = 'Please enter a password';
    } else if (password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters long';
    }

    if (!termsAccepted) {
      newErrors.terms = 'You must agree to the Terms of Service and Privacy Policy';
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
      await register({
        full_name: fullName.trim(),
        email: email.trim().toLowerCase(),
        password,
        role: 'student',
        terms_accepted: termsAccepted,
      });

      // On successful registration, redirect newly registered student to onboarding wizard
      navigate('/onboarding/step1', { replace: true });
    } catch (err: any) {
      setErrors({
        general: err.message || 'Registration failed. Please check your details and try again.',
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
        <h1 className="auth-title">Create your account</h1>
        <p className="auth-subtitle">Get started with SmartLearn.AI's adaptive courses</p>

        {/* Role Selector */}
        <RoleSelector selectedRole={role} onSelectRole={handleRoleSelect} />

        {roleNotice && (
          <Alert type="info" message={roleNotice} onClose={() => setRoleNotice(null)} />
        )}

        {errors.general && (
          <Alert type="error" message={errors.general} onClose={() => setErrors({ ...errors, general: undefined })} />
        )}

        {/* Registration Form */}
        <form className="auth-form" onSubmit={handleSubmit} noValidate>
          <Input
            id="register-fullname"
            label="Full Name"
            type="text"
            placeholder="Enter your full name"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            error={errors.fullName}
            required
            autoComplete="name"
          />

          <Input
            id="register-email"
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
            id="register-password"
            label="Password"
            type="password"
            placeholder="Create secure password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            error={errors.password}
            showPasswordToggle
            required
            autoComplete="new-password"
          />

          <Checkbox
            id="register-terms"
            checked={termsAccepted}
            onChange={setTermsAccepted}
            error={errors.terms}
          >
            I agree to the Terms of Service and Privacy Policy.
          </Checkbox>

          <Button type="submit" variant="primary" isLoading={isLoading}>
            Create Account
          </Button>
        </form>

        <div className="auth-footer-text">
          Already have an account?
          <Link to="/login" className="auth-link">
            Sign In
          </Link>
        </div>
      </div>
    </div>
  );
};
