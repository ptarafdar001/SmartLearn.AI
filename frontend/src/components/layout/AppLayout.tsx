import React, { useState, useEffect } from 'react';
import { NavLink, Link } from 'react-router-dom';
import {
  LogOut,
  Menu,
  X,
  ChevronRight,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { fetchDashboardOverview } from '../../services/learning';
import type { DashboardOverview } from '../../types/learning';

interface AppLayoutProps {
  children: React.ReactNode;
  breadcrumbs?: { label: string; href?: string }[];
}

const NAV_ITEMS = [
  { label: 'Dashboard', path: '/dashboard' },
  { label: 'My Subjects', path: '/subjects' },
  { label: 'Materials & Notes', path: '/study-materials' },
  { label: 'AI Tutor', path: '/ai-tutor' },
  { label: 'Practice & Quizzes', path: '/practice' },
  { label: 'Progress & Analytics', path: '/analytics' },
  { label: 'Study Plan', path: '/study-plan' },
  { label: 'Settings', path: '/settings' },
];

export const AppLayout: React.FC<AppLayoutProps> = ({ children, breadcrumbs }) => {
  const { user, logout } = useAuth();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [overview, setOverview] = useState<DashboardOverview | null>(null);

  useEffect(() => {
    let isMounted = true;
    async function loadAcademicDetails() {
      try {
        const data = await fetchDashboardOverview();
        if (isMounted && data) {
          setOverview(data);
        }
      } catch {
        // Fallback gracefully
      }
    }
    loadAcademicDetails();
    return () => {
      isMounted = false;
    };
  }, []);

  const studentName = user?.full_name || overview?.full_name || 'pg';
  const board = overview?.board || 'ISC';
  const grade = overview?.grade || 'Class 11';
  // Stream is strictly only applicable for senior secondary (Class 11 & 12)
  const isSeniorSecondary = grade === 'Class 11' || grade === 'Class 12';
  const stream = isSeniorSecondary && overview?.academic_stream
    ? overview.academic_stream.replace(' / Arts', '')
    : null;
  const initialLetter = (studentName.charAt(0) || 'P').toUpperCase();

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

        <Link to="/dashboard" className="sidebar-brand-clean">
          SmartLearn.AI
        </Link>

        <div className="sidebar-user-avatar-orange" style={{ width: 28, height: 28, fontSize: 13 }}>
          {initialLetter}
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
          <Link to="/dashboard" className="sidebar-brand-clean" onClick={() => setMobileOpen(false)}>
            SmartLearn.AI
          </Link>
        </div>

        {/* Navigation Items List with Dot Indicator matching Design */}
        <nav className="sidebar-nav" aria-label="Main sidebar navigation">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `sidebar-nav-item-modern ${isActive ? 'active' : ''}`
              }
              onClick={() => setMobileOpen(false)}
            >
              <span className="sidebar-nav-dot" aria-hidden="true" />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        {/* Sidebar Bottom Profile & Sign Out */}
        <div className="sidebar-footer">
          <div className="sidebar-user-card">
            <div className="sidebar-user-avatar-orange">
              {initialLetter}
            </div>
            <div className="sidebar-user-info">
              <span className="sidebar-user-name" style={{ fontWeight: 700, color: '#1e293b' }}>
                {studentName}
              </span>
              <span className="sidebar-user-role" style={{ color: '#64748b', fontSize: 12 }}>
                {board} · {grade}
              </span>
            </div>
          </div>

          <button
            type="button"
            className="sidebar-signout-btn"
            onClick={logout}
            aria-label="Sign out of your account"
          >
            <LogOut size={14} />
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
              {board} · {grade}{stream ? ` · ${stream}` : ''}
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
