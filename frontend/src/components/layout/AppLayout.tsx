import React, { useState } from 'react';
import { NavLink, Link } from 'react-router-dom';
import {
  LayoutDashboard,
  BookOpen,
  FileText,
  Bot,
  HelpCircle,
  BarChart3,
  Calendar,
  Settings,
  LogOut,
  Menu,
  X,
  ChevronRight,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { BrandLogo } from '../common/BrandLogo';

interface AppLayoutProps {
  children: React.ReactNode;
  breadcrumbs?: { label: string; href?: string }[];
}

const NAV_ITEMS = [
  { label: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
  { label: 'My Subjects', path: '/subjects', icon: BookOpen },
  { label: 'Study Materials & Notes', path: '/study-materials', icon: FileText },
  { label: 'AI Tutor', path: '/ai-tutor', icon: Bot },
  { label: 'Practice & Quizzes', path: '/practice', icon: HelpCircle },
  { label: 'Progress & Analytics', path: '/analytics', icon: BarChart3 },
  { label: 'Study Plan', path: '/study-plan', icon: Calendar },
  { label: 'Settings', path: '/settings', icon: Settings },
];

export const AppLayout: React.FC<AppLayoutProps> = ({ children, breadcrumbs }) => {
  const { user, logout } = useAuth();
  const [mobileOpen, setMobileOpen] = useState(false);

  const studentName = user?.full_name || 'Student';

  return (
    <div className="platform-layout">
      {/* Mobile Top Header */}
      <header className="mobile-header">
        <button
          type="button"
          className="mobile-menu-toggle"
          onClick={() => setMobileOpen(!mobileOpen)}
          aria-label={mobileOpen ? 'Close navigation sidebar' : 'Open navigation sidebar'}
        >
          {mobileOpen ? <X size={20} /> : <Menu size={20} />}
        </button>

        <Link to="/dashboard" className="mobile-brand">
          <BrandLogo size="sm" />
        </Link>

        <div className="mobile-user-avatar">
          {studentName.charAt(0).toUpperCase()}
        </div>
      </header>

      {/* Mobile Backdrop Overlay */}
      {mobileOpen && (
        <div
          className="mobile-sidebar-backdrop"
          onClick={() => setMobileOpen(false)}
          role="presentation"
        />
      )}

      {/* Persistent Left Sidebar */}
      <aside className={`platform-sidebar ${mobileOpen ? 'open' : ''}`}>
        {/* Sidebar Brand Header */}
        <div className="sidebar-brand-box">
          <Link to="/dashboard" className="sidebar-brand" onClick={() => setMobileOpen(false)}>
            <BrandLogo size="sm" />
            <span className="sidebar-badge">Student</span>
          </Link>
        </div>

        {/* Navigation Items List */}
        <nav className="sidebar-nav" aria-label="Main sidebar navigation">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `sidebar-nav-item ${isActive ? 'active' : ''}`
                }
                onClick={() => setMobileOpen(false)}
              >
                <Icon size={18} className="sidebar-nav-icon" />
                <span className="sidebar-nav-label">{item.label}</span>
              </NavLink>
            );
          })}
        </nav>

        {/* Sidebar Bottom Profile & Sign Out */}
        <div className="sidebar-footer">
          <div className="sidebar-user-card">
            <div className="sidebar-user-avatar">
              {studentName.charAt(0).toUpperCase()}
            </div>
            <div className="sidebar-user-info">
              <span className="sidebar-user-name">{studentName}</span>
              <span className="sidebar-user-role">ISC • Class 11</span>
            </div>
          </div>

          <button
            type="button"
            className="sidebar-signout-btn"
            onClick={logout}
            aria-label="Sign out of your account"
          >
            <LogOut size={15} />
            <span>Sign Out</span>
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="platform-main-wrap">
        {/* Top Header Bar for Desktop */}
        <header className="platform-topbar">
          <div className="platform-breadcrumbs">
            <Link to="/dashboard" className="topbar-crumb-link">
              SmartLearn
            </Link>
            {breadcrumbs && breadcrumbs.length > 0 ? (
              breadcrumbs.map((crumb, idx) => (
                <React.Fragment key={idx}>
                  <ChevronRight size={13} className="topbar-crumb-sep" />
                  {crumb.href ? (
                    <Link to={crumb.href} className="topbar-crumb-link">
                      {crumb.label}
                    </Link>
                  ) : (
                    <span className="topbar-crumb-current">{crumb.label}</span>
                  )}
                </React.Fragment>
              ))
            ) : (
              <>
                <ChevronRight size={13} className="topbar-crumb-sep" />
                <span className="topbar-crumb-current">Dashboard</span>
              </>
            )}
          </div>

          <div className="platform-topbar-actions">
            <div className="topbar-academic-pill">
              ISC • Class 11 • Humanities
            </div>
          </div>
        </header>

        {/* Page Content Body */}
        <main className="platform-content">
          {children}
        </main>
      </div>
    </div>
  );
};
