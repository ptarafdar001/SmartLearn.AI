import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { DashboardPage } from '../pages/DashboardPage';
import { SubjectDetailPage } from '../pages/learning/SubjectDetailPage';
import { TopicStudyPage } from '../pages/learning/TopicStudyPage';
import * as learningService from '../services/learning';
import type {
  ContinueLearningItem,
  DashboardOverview,
  SubjectDetail,
  SubjectSummary,
  TopicDetail,
} from '../types/learning';

vi.mock('../services/learning');

const mockUser = {
  id: 1,
  email: 'student@example.com',
  full_name: 'Ananya Sharma',
  role: 'student',
  is_active: true,
  is_onboarded: true,
  created_at: '2026-09-10T10:00:00Z',
};

const mockAuthContextValue = {
  user: mockUser,
  token: 'mock-jwt-token',
  isAuthenticated: true,
  isLoading: false,
  isOnboarded: true,
  onboardingStatus: null,
  login: vi.fn(),
  register: vi.fn(),
  logout: vi.fn(),
  refreshUser: vi.fn(),
  checkOnboardingStatus: vi.fn(),
};

vi.mock('../context/AuthContext', () => ({
  useAuth: () => mockAuthContextValue,
  AuthProvider: ({ children }: any) => children,
}));

const mockDashboardOverview: DashboardOverview = {
  user_id: 1,
  full_name: 'Ananya Sharma',
  board: 'ISC',
  grade: 'Class 11',
  academic_stream: 'Humanities',
  preferred_learning_style: 'Visual',
  study_target: {
    daily_target_hours: 2.5,
    preferred_slot: 'evening',
    available_days: ['Monday', 'Tuesday', 'Wednesday'],
  },
  goals: ['Score 95% in ISC History'],
  enrolled_subjects: ['History'],
  total_enrolled_subjects: 1,
  overall_progress_percentage: 45.0,
};

const mockSubjects: SubjectSummary[] = [
  {
    id: 43,
    code: 'isc-11-hist',
    name: 'History',
    subject_name: 'History',
    board: 'ISC',
    grade: 'Class 11',
    academic_stream: 'Humanities',
    category: 'elective',
    description: 'Official CISCE ISC Class XI History curriculum.',
    total_chapters: 3,
    total_topics: 5,
    completed_topics: 2,
    progress_percentage: 40.0,
  },
];

const mockContinueItem: ContinueLearningItem = {
  topic_id: 101,
  topic_title: 'Development of Transport & Communication: Railways, Roads, and Telegraphs',
  chapter_id: 1,
  chapter_title: 'Emergence of the Colonial Economy',
  subject_id: 43,
  subject_name: 'History',
  status: 'in_progress',
  progress_percentage: 50.0,
  estimated_minutes: 25,
};

const mockSubjectDetail: SubjectDetail = {
  id: 43,
  code: 'isc-11-hist',
  name: 'History',
  board: 'ISC',
  grade: 'Class 11',
  academic_stream: 'Humanities',
  category: 'elective',
  description: 'Official CISCE ISC Class XI History curriculum.',
  total_chapters: 1,
  total_topics: 2,
  completed_topics: 1,
  progress_percentage: 50.0,
  chapters: [
    {
      id: 1,
      subject_id: 43,
      chapter_number: 1,
      title: 'Emergence of the Colonial Economy',
      description: 'Development of transport, land revenue, and de-industrialisation.',
      total_topics: 2,
      completed_topics: 1,
      progress_percentage: 50.0,
      topics: [
        {
          id: 101,
          chapter_id: 1,
          topic_number: 1,
          title: 'Development of Transport & Communication: Railways, Roads, and Telegraphs',
          description: 'Strategic troop movements, commercial export of raw materials, guarantee system.',
          estimated_minutes: 25,
          progress: {
            status: 'completed',
            progress_percentage: 100.0,
            time_spent_seconds: 600,
          },
        },
        {
          id: 102,
          chapter_id: 1,
          topic_number: 2,
          title: 'Colonial Land Revenue Systems: Permanent, Ryotwari, and Mahalwari',
          description: 'Permanent Settlement, Ryotwari, and Mahalwari systems.',
          estimated_minutes: 25,
          progress: {
            status: 'not_started',
            progress_percentage: 0.0,
            time_spent_seconds: 0,
          },
        },
      ],
    },
  ],
};

const mockTopicDetail: TopicDetail = {
  id: 101,
  chapter_id: 1,
  chapter_title: 'Emergence of the Colonial Economy',
  chapter_number: 1,
  subject_id: 43,
  subject_name: 'History',
  topic_number: 1,
  title: 'Development of Transport & Communication: Railways, Roads, and Telegraphs',
  description: 'Colonial transport infrastructure and the railway guarantee system.',
  estimated_minutes: 25,
  progress: {
    status: 'in_progress',
    progress_percentage: 50.0,
    time_spent_seconds: 300,
  },
  resources: [
    {
      id: 1,
      topic_id: 101,
      title: 'Colonial Transport Infrastructure & The Railway Guarantee System',
      resource_type: 'video',
      provider: 'YouTube',
      source_name: 'National Educational Video Archive',
      content_url: 'https://www.youtube-nocookie.com/embed/kYJq1000m9A',
      external_id: 'kYJq1000m9A',
      language: 'en',
      order_index: 1,
      is_active: true,
      is_verified: true,
    },
    {
      id: 2,
      topic_id: 101,
      title: 'Chapter 1 Topic 1 Revision Notes',
      resource_type: 'notes',
      provider: 'SmartLearn',
      text_content: 'Key Exam Pointers: 1853 first train between Bombay and Thane.',
      language: 'en',
      order_index: 2,
      is_active: true,
      is_verified: true,
    },
    {
      id: 3,
      topic_id: 101,
      title: 'Detailed Reading Text',
      resource_type: 'text',
      provider: 'SmartLearn',
      text_content: 'Comprehensive reading material on 19th-century colonial transport.',
      language: 'en',
      order_index: 3,
      is_active: true,
      is_verified: true,
    },
  ],
};

describe('Learning Slice Frontend Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // ── DashboardPage Tests ───────────────────────────────────────────────────
  describe('DashboardPage', () => {
    it('renders greeting, enrolled subjects, continue learning, and recommendations', async () => {
      vi.mocked(learningService.fetchDashboardOverview).mockResolvedValue(mockDashboardOverview);
      vi.mocked(learningService.fetchEnrolledSubjects).mockResolvedValue(mockSubjects);
      vi.mocked(learningService.fetchContinueLearning).mockResolvedValue(mockContinueItem);
      vi.mocked(learningService.fetchRecommendations).mockResolvedValue({
        user_id: 1,
        recommendations: [
          {
            id: 'rec-1',
            title: 'History: Concept Mapping',
            description: 'Begin study with visual notes',
            subject: 'History',
            recommendation_type: 'starter_guide',
          },
        ],
        total_count: 1,
      });

      render(
        <MemoryRouter>
          <DashboardPage />
        </MemoryRouter>
      );

      // Verify greeting
      expect(await screen.findByText(/Welcome back, Ananya Sharma!/i)).toBeInTheDocument();

      // Verify study target
      expect(screen.getByText(/2.5 hrs\/day/i)).toBeInTheDocument();

      // Verify continue learning widget
      expect(
        screen.getByText(
          'Development of Transport & Communication: Railways, Roads, and Telegraphs'
        )
      ).toBeInTheDocument();
      expect(screen.getByText('Resume Topic →')).toBeInTheDocument();

      // Verify enrolled subjects card
      expect(screen.getByRole('heading', { name: 'History' })).toBeInTheDocument();
      expect(screen.getByText(/3 Chapters • 5 Topics/i)).toBeInTheDocument();

      // Verify recommendation
      expect(screen.getByText('History: Concept Mapping')).toBeInTheDocument();
    });

    it('handles empty states gracefully when no subjects enrolled', async () => {
      vi.mocked(learningService.fetchDashboardOverview).mockResolvedValue({
        ...mockDashboardOverview,
        enrolled_subjects: [],
        total_enrolled_subjects: 0,
      });
      vi.mocked(learningService.fetchEnrolledSubjects).mockResolvedValue([]);
      vi.mocked(learningService.fetchContinueLearning).mockResolvedValue(null);
      vi.mocked(learningService.fetchRecommendations).mockResolvedValue({
        user_id: 1,
        recommendations: [],
        total_count: 0,
      });

      render(
        <MemoryRouter>
          <DashboardPage />
        </MemoryRouter>
      );

      expect(
        await screen.findByText(/No enrolled subjects found/i)
      ).toBeInTheDocument();
    });
  });

  // ── SubjectDetailPage Tests ───────────────────────────────────────────────
  describe('SubjectDetailPage', () => {
    it('renders subject syllabus hierarchy with chapters and topics', async () => {
      vi.mocked(learningService.fetchSubjectDetail).mockResolvedValue(mockSubjectDetail);

      render(
        <MemoryRouter initialEntries={['/learning/subjects/43']}>
          <Routes>
            <Route path="/learning/subjects/:subjectId" element={<SubjectDetailPage />} />
          </Routes>
        </MemoryRouter>
      );

      // Subject title
      expect(await screen.findByRole('heading', { name: 'History' })).toBeInTheDocument();

      // Chapter title
      expect(screen.getByText('Emergence of the Colonial Economy')).toBeInTheDocument();

      // Topics under default open chapter
      expect(screen.getByRole('heading', { name: /Development of Transport/i })).toBeInTheDocument();
      expect(screen.getByText(/Colonial Land Revenue Systems/i)).toBeInTheDocument();

      // Completed checkmark
      expect(screen.getByText('✓')).toBeInTheDocument();
    });

    it('toggles chapter expansion on clicking chapter header', async () => {
      vi.mocked(learningService.fetchSubjectDetail).mockResolvedValue(mockSubjectDetail);

      render(
        <MemoryRouter initialEntries={['/learning/subjects/43']}>
          <Routes>
            <Route path="/learning/subjects/:subjectId" element={<SubjectDetailPage />} />
          </Routes>
        </MemoryRouter>
      );

      const chapterHeader = await screen.findByRole('button', {
        name: /Ch 1 Emergence of the Colonial Economy/i,
      });
      expect(chapterHeader).toBeInTheDocument();

      // Initial state: first chapter is expanded
      expect(screen.getByText(/Colonial Land Revenue Systems/i)).toBeInTheDocument();

      // Click to collapse
      fireEvent.click(chapterHeader);
      expect(screen.queryByText(/Colonial Land Revenue Systems/i)).not.toBeInTheDocument();

      // Click to re-expand
      fireEvent.click(chapterHeader);
      expect(screen.getByText(/Colonial Land Revenue Systems/i)).toBeInTheDocument();
    });
  });

  // ── TopicStudyPage Tests ──────────────────────────────────────────────────
  describe('TopicStudyPage', () => {
    it('renders topic details, video embed, notes, and supports modality switching', async () => {
      vi.mocked(learningService.fetchTopicDetail).mockResolvedValue(mockTopicDetail);

      render(
        <MemoryRouter initialEntries={['/learning/topics/101']}>
          <Routes>
            <Route path="/learning/topics/:topicId" element={<TopicStudyPage />} />
          </Routes>
        </MemoryRouter>
      );

      // Topic header
      expect(
        await screen.findByRole('heading', {
          name: 'Development of Transport & Communication: Railways, Roads, and Telegraphs',
        })
      ).toBeInTheDocument();

      // Modality tabs
      const videoTab = screen.getByRole('tab', { name: /Video Lesson/i });
      const notesTab = screen.getByRole('tab', { name: /Study Notes/i });
      const textTab = screen.getByRole('tab', { name: /Reading Material/i });

      expect(videoTab).toBeInTheDocument();
      expect(notesTab).toBeInTheDocument();
      expect(textTab).toBeInTheDocument();

      // Video iframe rendered initially
      const iframe = screen.getByTitle('Colonial Transport Infrastructure & The Railway Guarantee System');
      expect(iframe).toBeInTheDocument();
      expect(iframe).toHaveAttribute(
        'src',
        'https://www.youtube-nocookie.com/embed/kYJq1000m9A'
      );

      // Switch to notes tab
      fireEvent.click(notesTab);
      expect(
        screen.getByText(/1853 first train between Bombay and Thane/i)
      ).toBeInTheDocument();

      // Switch to reading text tab
      fireEvent.click(textTab);
      expect(
        screen.getByText(/Comprehensive reading material on 19th-century colonial transport/i)
      ).toBeInTheDocument();
    });

    it('updates progress when mark complete is clicked', async () => {
      vi.mocked(learningService.fetchTopicDetail).mockResolvedValue(mockTopicDetail);
      vi.mocked(learningService.saveTopicProgress).mockResolvedValue({
        id: 1,
        user_id: 1,
        topic_id: 101,
        status: 'completed',
        progress_percentage: 100.0,
        time_spent_seconds: 350,
      });

      render(
        <MemoryRouter initialEntries={['/learning/topics/101']}>
          <Routes>
            <Route path="/learning/topics/:topicId" element={<TopicStudyPage />} />
          </Routes>
        </MemoryRouter>
      );

      await screen.findByRole('heading', {
        name: 'Development of Transport & Communication: Railways, Roads, and Telegraphs',
      });

      const completeBtn = screen.getByRole('button', { name: /Mark topic as completed 100%/i });
      fireEvent.click(completeBtn);

      await waitFor(() => {
        expect(learningService.saveTopicProgress).toHaveBeenCalledWith(
          101,
          expect.objectContaining({
            status: 'completed',
            progress_percentage: 100.0,
          })
        );
      });

      // Feedback message shown
      expect(
        await screen.findByText(/Topic marked as completed! 100% saved./i)
      ).toBeInTheDocument();
    });
  });
});
