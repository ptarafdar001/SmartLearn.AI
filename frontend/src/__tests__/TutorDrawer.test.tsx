import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { TutorDrawer } from '../components/learning/TutorDrawer';
import * as tutorService from '../services/tutor';

vi.mock('../services/tutor');

describe('TutorDrawer Component', () => {
  const defaultProps = {
    isOpen: true,
    onClose: vi.fn(),
    topicId: 101,
    topicTitle: 'Development of Transport & Communication',
    subjectName: 'History',
    chapterTitle: 'Emergence of the Colonial Economy',
    chapterNumber: 1,
  };

  beforeEach(() => {
    vi.clearAllMocks();
    // Polyfill scrollIntoView
    window.HTMLElement.prototype.scrollIntoView = vi.fn();
  });

  it('renders drawer with curriculum context and welcome message', () => {
    render(<TutorDrawer {...defaultProps} />);

    expect(screen.getByRole('dialog', { name: /Curriculum AI Tutor/i })).toBeInTheDocument();
    expect(screen.getByText('SmartLearn AI Tutor')).toBeInTheDocument();
    expect(screen.getByText(/History • Development of Transport & Communication/i)).toBeInTheDocument();
    expect(screen.getByText(/We're currently exploring/i)).toBeInTheDocument();
  });

  it('submits student question and displays tutor reply', async () => {
    vi.mocked(tutorService.askAITutor).mockResolvedValue({
      reply: 'The Railway Guarantee System promised British investors a 5% return guaranteed from Indian taxes.',
      topic_id: 101,
      topic_title: 'Development of Transport & Communication',
      subjectName: 'History',
      board: 'ISC',
      grade: 'Class 11',
      grounded_resource_titles: ['Colonial Transport Infrastructure'],
      is_out_of_scope: false,
    });

    render(<TutorDrawer {...defaultProps} />);

    const textarea = screen.getByPlaceholderText(/Ask a question or explain your doubt/i);
    fireEvent.change(textarea, { target: { value: 'Why was the guarantee system controversial?' } });

    const sendBtn = screen.getByRole('button', { name: /Send message to AI Tutor/i });
    fireEvent.click(sendBtn);

    // Verify student bubble
    expect(screen.getByText('Why was the guarantee system controversial?')).toBeInTheDocument();

    // Verify tutor reply
    await waitFor(() => {
      expect(
        screen.getByText(
          'The Railway Guarantee System promised British investors a 5% return guaranteed from Indian taxes.'
        )
      ).toBeInTheDocument();
    });

    expect(tutorService.askAITutor).toHaveBeenCalledWith(
      expect.objectContaining({
        topic_id: 101,
        message: 'Why was the guarantee system controversial?',
      })
    );
  });

  it('handles clicking starter prompt chips', async () => {
    vi.mocked(tutorService.askAITutor).mockResolvedValue({
      reply: 'Here is a simple explanation of the concept...',
      topic_id: 101,
      topic_title: 'Development of Transport & Communication',
      subjectName: 'History',
      board: 'ISC',
      grade: 'Class 11',
      grounded_resource_titles: [],
      is_out_of_scope: false,
    });

    render(<TutorDrawer {...defaultProps} />);

    const chip = screen.getByRole('button', { name: /Explain this concept in simple terms/i });
    fireEvent.click(chip);

    await waitFor(() => {
      expect(tutorService.askAITutor).toHaveBeenCalledWith(
        expect.objectContaining({
          topic_id: 101,
          message: 'Explain this concept in simple terms 💡',
        })
      );
    });
  });

  it('displays error banner when AI Tutor service throws an error', async () => {
    vi.mocked(tutorService.askAITutor).mockRejectedValue(
      new Error('AI Tutor service is not configured. GEMINI_API_KEY is required in backend.')
    );

    render(<TutorDrawer {...defaultProps} />);

    const textarea = screen.getByPlaceholderText(/Ask a question or explain your doubt/i);
    fireEvent.change(textarea, { target: { value: 'Explain railways' } });

    const sendBtn = screen.getByRole('button', { name: /Send message to AI Tutor/i });
    fireEvent.click(sendBtn);

    await waitFor(() => {
      expect(
        screen.getByText(/AI Tutor service is not configured. GEMINI_API_KEY is required/i)
      ).toBeInTheDocument();
    });
  });

  it('closes when close button is clicked', () => {
    render(<TutorDrawer {...defaultProps} />);

    const closeBtn = screen.getByRole('button', { name: /Close AI Tutor/i });
    fireEvent.click(closeBtn);

    expect(defaultProps.onClose).toHaveBeenCalled();
  });
});
