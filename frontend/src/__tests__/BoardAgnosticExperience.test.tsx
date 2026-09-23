import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { DashboardPage } from '../pages/DashboardPage';
import { SubjectDetailPage } from '../pages/learning/SubjectDetailPage';
import { StudyMaterialsPage } from '../pages/StudyMaterialsPage';
import { PracticeQuizzesPage } from '../pages/PracticeQuizzesPage';
import { AITutorPage } from '../pages/AITutorPage';
import { SubjectsPage } from '../pages/SubjectsPage';
import * as learningService from '../services/learning';
import * as tutorService from '../services/tutor';
import type {
  DashboardOverview,
  SubjectDetail,
  SubjectSummary,
} from '../types/learning';

vi.mock('../services/learning');
vi.mock('../services/tutor');

const mockAuthUser = {
  id: 10,
  email: 'student@example.com',
  full_name: 'Priya Patel',
  role: 'student' as const,
  is_active: true,
  is_onboarded: true,
  created_at: '2026-09-10T10:00:00Z',
};

vi.mock('../context/AuthContext', () => ({
  useAuth: () => ({
    user: mockAuthUser,
    token: 'mock-token',
    isAuthenticated: true,
    isLoading: false,
    isOnboarded: true,
    logout: vi.fn(),
  }),
  AuthProvider: ({ children }: any) => children,
}));

describe('Batch 2: Board-Agnostic Curriculum UI Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // ── 1. ISC Class 11 History Student ─────────────────────────────────────────
  it('renders ISC Class 11 History student context dynamically without invented exam targets', async () => {
    const iscOverview: DashboardOverview = {
      user_id: 10,
      full_name: 'Priya Patel',
      board: 'ISC',
      grade: 'Class 11',
      academic_stream: 'Humanities',
      goals: ['Aiming for 95% in Board Exams'],
      enrolled_subjects: ['History'],
      total_enrolled_subjects: 1,
      overall_progress_percentage: 28,
      study_target: {
        daily_target_hours: 2.0,
        preferred_slot: 'evening',
        available_days: ['Monday', 'Tuesday', 'Wednesday'],
      },
    };

    const iscSubjects: SubjectSummary[] = [
      {
        id: 43,
        code: 'isc-11-hist',
        name: 'History',
        subject_name: 'History',
        board: 'ISC',
        grade: 'Class 11',
        academic_stream: 'Humanities',
        category: 'core',
        total_chapters: 5,
        total_topics: 12,
        completed_topics: 3,
        progress_percentage: 25.0,
        curriculum_status: 'content_available',
        source_authority: 'CISCE',
      },
    ];

    vi.mocked(learningService.fetchDashboardOverview).mockResolvedValue(iscOverview);
    vi.mocked(learningService.fetchEnrolledSubjects).mockResolvedValue(iscSubjects);
    vi.mocked(learningService.fetchContinueLearning).mockResolvedValue(null);
    vi.mocked(learningService.fetchRecommendations).mockResolvedValue({ user_id: 10, recommendations: [], total_count: 0 });

    render(
      <MemoryRouter>
        <DashboardPage />
      </MemoryRouter>
    );

    expect(await screen.findByText(/Welcome back, Priya Patel!/i)).toBeInTheDocument();
    expect(screen.getAllByText('ISC').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Class 11').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Humanities').length).toBeGreaterThan(0);
    expect(screen.getByText('Aiming for 95% in Board Exams')).toBeInTheDocument();

    // Verify invented target ISC 2027 (95%) is NOT present
    expect(screen.queryByText(/ISC 2027 \(95%\)/i)).toBeNull();
  });

  // ── 2. CBSE Class 10 Science Student ────────────────────────────────────────
  it('renders CBSE Class 10 Science student context cleanly without ISC or CISCE assumptions', async () => {
    const cbseOverview: DashboardOverview = {
      user_id: 20,
      full_name: 'Aarav Sharma',
      board: 'CBSE',
      grade: 'Class 10',
      academic_stream: null,
      goals: ['Master Science Concepts'],
      enrolled_subjects: ['Science', 'Mathematics'],
      total_enrolled_subjects: 2,
      overall_progress_percentage: 15,
      study_target: {
        daily_target_hours: 1.5,
        preferred_slot: 'morning',
        available_days: ['Monday', 'Thursday', 'Saturday'],
      },
    };

    const cbseSubjects: SubjectSummary[] = [
      {
        id: 70,
        code: 'cbse-10-sci',
        name: 'Science',
        subject_name: 'Science',
        board: 'CBSE',
        grade: 'Class 10',
        academic_stream: null,
        category: 'core',
        total_chapters: 16,
        total_topics: 48,
        completed_topics: 7,
        progress_percentage: 14.5,
        curriculum_status: 'content_available',
        source_authority: 'CBSE',
      },
      {
        id: 71,
        code: 'cbse-10-math',
        name: 'Mathematics',
        subject_name: 'Mathematics',
        board: 'CBSE',
        grade: 'Class 10',
        academic_stream: null,
        category: 'core',
        total_chapters: 14,
        total_topics: 42,
        completed_topics: 0,
        progress_percentage: 0,
        curriculum_status: 'curriculum_verified',
        source_authority: 'CBSE',
      },
    ];

    vi.mocked(learningService.fetchDashboardOverview).mockResolvedValue(cbseOverview);
    vi.mocked(learningService.fetchEnrolledSubjects).mockResolvedValue(cbseSubjects);
    vi.mocked(learningService.fetchContinueLearning).mockResolvedValue(null);
    vi.mocked(learningService.fetchRecommendations).mockResolvedValue({ user_id: 20, recommendations: [], total_count: 0 });

    render(
      <MemoryRouter>
        <DashboardPage />
      </MemoryRouter>
    );

    expect(await screen.findByText(/Welcome back, Aarav Sharma!/i)).toBeInTheDocument();
    expect(screen.getAllByText('CBSE').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Class 10').length).toBeGreaterThan(0);
    expect(screen.queryByText('Humanities')).toBeNull();
    expect(screen.queryByText(/CISCE/i)).toBeNull();
    expect(screen.queryByText(/ISC 2027/i)).toBeNull();

    // Check subjects
    expect(screen.getByText('Science')).toBeInTheDocument();
    expect(screen.getByText('Mathematics')).toBeInTheDocument();
  });

  // ── 3. Subject Detail: Curriculum Verified but Unpopulated Subject ──────────
  it('renders curriculum-verified empty state with official provenance and no 43 redirect', async () => {
    const verifiedSubject: SubjectDetail = {
      id: 85,
      code: 'cbse-10-soc',
      name: 'Social Science',
      board: 'CBSE',
      grade: 'Class 10',
      category: 'core',
      total_chapters: 0,
      total_topics: 0,
      completed_topics: 0,
      progress_percentage: 0,
      curriculum_status: 'curriculum_verified',
      source_authority: 'CBSE Academic Central',
      syllabusVersion: '2024-25 Annual',
      source_url: 'https://cbseacademic.nic.in/curriculum_2025.html',
      status_message: 'Curriculum structure verified from official CBSE guidelines. Interactive chapters are being compiled.',
      chapters: [],
    };

    vi.mocked(learningService.fetchSubjectDetail).mockResolvedValue(verifiedSubject);
    vi.mocked(learningService.fetchDashboardOverview).mockResolvedValue(null as any);

    render(
      <MemoryRouter initialEntries={['/learning/subjects/85']}>
        <Routes>
          <Route path="/learning/subjects/:subjectId" element={<SubjectDetailPage />} />
        </Routes>
      </MemoryRouter>
    );

    expect(await screen.findByRole('heading', { name: 'Social Science' })).toBeInTheDocument();
    expect(screen.getByTestId('curriculum-status-card')).toBeInTheDocument();
    expect(screen.getAllByText(/Curriculum Verified/i).length).toBeGreaterThan(0);
    expect(screen.getByText(/CBSE Academic Central/i)).toBeInTheDocument();
    expect(screen.getByText(/Curriculum structure verified from official CBSE guidelines/i)).toBeInTheDocument();

    // Ensure no hardcoded History 43 link exists
    const links = screen.getAllByRole('link');
    const hasHistory43 = links.some((l) => l.getAttribute('href')?.includes('/subjects/43'));
    expect(hasHistory43).toBe(false);

    // Ensure Back to My Subjects button is available
    expect(screen.getByText('Back to My Subjects')).toBeInTheDocument();
  });

  // ── 4. Subject Detail: In-Preparation Subject ────────────────────────────────
  it('renders helpful in-preparation state for subjects awaiting curation', async () => {
    const inPrepSubject: SubjectDetail = {
      id: 99,
      code: 'wb-12-phys',
      name: 'Physics',
      board: 'WBCHSE',
      grade: 'Class 12',
      category: 'science',
      total_chapters: 0,
      total_topics: 0,
      completed_topics: 0,
      progress_percentage: 0,
      curriculum_status: 'in_preparation',
      source_authority: 'West Bengal Council of Higher Secondary Education',
      status_message: 'Syllabus framework registered. Official chapter mapping in preparation.',
      chapters: [],
    };

    vi.mocked(learningService.fetchSubjectDetail).mockResolvedValue(inPrepSubject);
    vi.mocked(learningService.fetchDashboardOverview).mockResolvedValue(null as any);

    render(
      <MemoryRouter initialEntries={['/learning/subjects/99']}>
        <Routes>
          <Route path="/learning/subjects/:subjectId" element={<SubjectDetailPage />} />
        </Routes>
      </MemoryRouter>
    );

    expect(await screen.findByRole('heading', { name: 'Physics' })).toBeInTheDocument();
    expect(screen.getAllByText(/In Preparation/i).length).toBeGreaterThan(0);
    expect(screen.getByText(/Syllabus framework registered/i)).toBeInTheDocument();

    // Back to subjects link
    expect(screen.getByText('Back to My Subjects')).toBeInTheDocument();
  });

  // ── 5. Missing / Incomplete Profile Data ─────────────────────────────────────
  it('gracefully handles missing profile without falling back to hardcoded ISC assumptions', async () => {
    const emptyOverview: DashboardOverview = {
      user_id: 30,
      full_name: 'New Student',
      board: null,
      grade: null,
      academic_stream: null,
      goals: [],
      enrolled_subjects: [],
      total_enrolled_subjects: 0,
      overall_progress_percentage: 0,
    };

    vi.mocked(learningService.fetchDashboardOverview).mockResolvedValue(emptyOverview);
    vi.mocked(learningService.fetchEnrolledSubjects).mockResolvedValue([]);
    vi.mocked(learningService.fetchContinueLearning).mockResolvedValue(null);
    vi.mocked(learningService.fetchRecommendations).mockResolvedValue({ user_id: 30, recommendations: [], total_count: 0 });

    render(
      <MemoryRouter>
        <DashboardPage />
      </MemoryRouter>
    );

    expect(await screen.findByText(/Welcome back, New Student!/i)).toBeInTheDocument();
    expect(screen.getByText(/No enrolled subjects found/i)).toBeInTheDocument();

    // Must NOT show fake ISC or Class 11 badges
    expect(screen.queryByText(/ISC 2027/i)).toBeNull();
  });

  // ── 6. AI Tutor & Practice Quizzes: No Topic Fallback ────────────────────────
  it('AITutorPage renders general assistant greeting when no topic is selected and does NOT fallback to 44', async () => {
    vi.mocked(learningService.fetchEnrolledSubjects).mockResolvedValue([]);
    vi.mocked(learningService.fetchDashboardOverview).mockResolvedValue(null as any);

    render(
      <MemoryRouter initialEntries={['/ai-tutor']}>
        <Routes>
          <Route path="/ai-tutor" element={<AITutorPage />} />
        </Routes>
      </MemoryRouter>
    );

    expect(await screen.findByText(/SmartLearn AI Academic Assistant/i)).toBeInTheDocument();
    expect(screen.getByText(/General Assistance/i)).toBeInTheDocument();
    expect(screen.getByText(/No curriculum topic selected/i)).toBeInTheDocument();

    // Verify starter prompts are general and do NOT mention Dalhousie or 1853 railways
    expect(screen.queryByText(/1853 Railway Guarantee/i)).toBeNull();
    expect(screen.queryByText(/Lord Dalhousie/i)).toBeNull();
  });

  it('PracticeQuizzesPage handles subjects in preparation without defaulting to topic 44', async () => {
    vi.mocked(learningService.fetchEnrolledSubjects).mockResolvedValue([
      {
        id: 110,
        code: 'cbse-9-eng',
        name: 'English Language',
        subject_name: 'English Language',
        board: 'CBSE',
        grade: 'Class 9',
        category: 'language',
        total_chapters: 0,
        total_topics: 0,
        completed_topics: 0,
        curriculum_status: 'in_preparation',
      },
    ]);
    vi.mocked(learningService.fetchSubjectDetail).mockResolvedValue({
      id: 110,
      code: 'cbse-9-eng',
      name: 'English Language',
      board: 'CBSE',
      grade: 'Class 9',
      category: 'language',
      total_chapters: 0,
      total_topics: 0,
      completed_topics: 0,
      progress_percentage: 0,
      chapters: [],
    });
    vi.mocked(learningService.fetchDashboardOverview).mockResolvedValue(null as any);

    render(
      <MemoryRouter initialEntries={['/practice']}>
        <Routes>
          <Route path="/practice" element={<PracticeQuizzesPage />} />
        </Routes>
      </MemoryRouter>
    );

    // Verify in-preparation state is shown rather than loading topic 44
    expect(await screen.findByText(/No interactive topics or quizzes are available yet/i)).toBeInTheDocument();
    expect(screen.getByText(/Browse All Subjects/i)).toBeInTheDocument();
    expect(learningService.fetchTopicPYQs).not.toHaveBeenCalledWith(44);
  });

  // ── 7. Study Materials: Dynamic Selection and In-Preparation Handling ────────
  it('StudyMaterialsPage handles in-preparation subjects without defaulting to 43', async () => {
    vi.mocked(learningService.fetchEnrolledSubjects).mockResolvedValue([
      {
        id: 120,
        code: 'icse-10-chem',
        name: 'Chemistry',
        subject_name: 'Chemistry',
        board: 'ICSE',
        grade: 'Class 10',
        category: 'science',
        total_chapters: 0,
        total_topics: 0,
        completed_topics: 0,
        curriculum_status: 'in_preparation',
        source_authority: 'CISCE ICSE Board',
        status_message: 'Curriculum syllabus verified. Study notes and video lectures in preparation.',
      },
    ]);
    vi.mocked(learningService.fetchSubjectDetail).mockResolvedValue({
      id: 120,
      code: 'icse-10-chem',
      name: 'Chemistry',
      board: 'ICSE',
      grade: 'Class 10',
      category: 'science',
      total_chapters: 0,
      total_topics: 0,
      completed_topics: 0,
      progress_percentage: 0,
      curriculum_status: 'in_preparation',
      source_authority: 'CISCE ICSE Board',
      status_message: 'Curriculum syllabus verified. Study notes and video lectures in preparation.',
      chapters: [],
    });
    vi.mocked(learningService.fetchDashboardOverview).mockResolvedValue(null as any);

    render(
      <MemoryRouter initialEntries={['/study-materials']}>
        <Routes>
          <Route path="/study-materials" element={<StudyMaterialsPage />} />
        </Routes>
      </MemoryRouter>
    );

    expect(await screen.findByText('Chemistry In Preparation')).toBeInTheDocument();
    expect(screen.getByText(/Study notes and video lectures in preparation/i)).toBeInTheDocument();
    expect(screen.getByText(/CISCE ICSE Board/i)).toBeInTheDocument();

    // Verify there is NO button linking or switching to 43
    expect(screen.queryByText(/View Seeded ISC History Notes/i)).toBeNull();
  });
});
