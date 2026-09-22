import React, { useState } from 'react';
import { ArrowRight, RotateCcw, Award } from 'lucide-react';
import { AppLayout } from '../components/layout/AppLayout';

interface PracticeItem {
  id: number;
  question: string;
  options: string[];
  correctIndex: number;
  explanation: string;
}

const PRACTICE_QUESTIONS: PracticeItem[] = [
  {
    id: 1,
    question: 'The first railway line in India was opened in 1853 between which two stations?',
    options: ['Calcutta to Raniganj', 'Bombay to Thane', 'Madras to Arkonam', 'Delhi to Agra'],
    correctIndex: 1,
    explanation: 'The initial 21-mile railway line opened on 16 April 1853 connecting Bombay (Bori Bunder) to Thane under the Great Indian Peninsula Railway.',
  },
  {
    id: 2,
    question: 'Under the "Old Guarantee System", private British companies were assured a return of what percentage from Indian tax revenues?',
    options: ['3%', '4%', '5%', '7.5%'],
    correctIndex: 2,
    explanation: 'The British East India Company guaranteed a 5% minimum return on capital to British investors, leading to wasteful expenditure known as "private enterprise at public risk".',
  },
  {
    id: 3,
    question: 'Which Governor-General penned the famous 1853 Railway Minute that outlined the trunk lines policy?',
    options: ['Lord Bentinck', 'Lord Dalhousie', 'Lord Canning', 'Lord Curzon'],
    correctIndex: 1,
    explanation: 'Lord Dalhousie formulated the strategic railway scheme in his comprehensive Railway Minute of 1853.',
  },
  {
    id: 4,
    question: 'How did the colonial freight tariff structure impact indigenous Indian manufacturing?',
    options: [
      'It granted heavy subsidies for domestic handicrafts',
      'It imposed higher charges on domestic goods transit while giving preferential rates to raw material exports and British imports',
      'It abolished all transit duties equally across India',
      'It prohibited British goods from utilizing railways',
    ],
    correctIndex: 1,
    explanation: 'Discriminatory railway freight rates made inland transport of Indian goods more costly than transporting British industrial goods from ports to the interior.',
  },
  {
    id: 5,
    question: 'The Permanent Settlement of Bengal was introduced by Lord Cornwallis in which year?',
    options: ['1773', '1784', '1793', '1802'],
    correctIndex: 2,
    explanation: 'The Permanent Settlement was enacted in 1793, fixing the land revenue demand of the British government in perpetuity.',
  },
];

export const PracticeQuizzesPage: React.FC = () => {
  const [selectedAnswers, setSelectedAnswers] = useState<Record<number, number>>({});
  const [submitted, setSubmitted] = useState<boolean>(false);

  const handleSelect = (qId: number, optIdx: number) => {
    if (submitted) return;
    setSelectedAnswers((prev) => ({ ...prev, [qId]: optIdx }));
  };

  const calculateScore = () => {
    let score = 0;
    PRACTICE_QUESTIONS.forEach((q) => {
      if (selectedAnswers[q.id] === q.correctIndex) {
        score += 1;
      }
    });
    return score;
  };

  const handleReset = () => {
    setSelectedAnswers({});
    setSubmitted(false);
  };

  const score = calculateScore();

  return (
    <AppLayout breadcrumbs={[{ label: 'Practice & Quizzes' }]}>
      <div className="page-header-compact">
        <div>
          <h1 className="page-title-compact">Practice &amp; Assessment Hub</h1>
          <p className="page-subtitle-compact">
            CISCE-aligned practice modules, mock chapter tests, and self-assessment quizzes to test curriculum mastery.
          </p>
        </div>

        {submitted ? (
          <button type="button" className="continue-action-btn" onClick={handleReset} style={{ padding: '6px 14px', fontSize: '13px' }}>
            <RotateCcw size={14} />
            <span>Retake Quiz</span>
          </button>
        ) : (
          <span className="page-count-badge">5 Practice Questions</span>
        )}
      </div>

      {submitted && (
        <div className="quiz-results-banner">
          <div className="results-score-badge">
            <Award size={24} className="text-indigo-600" />
            <div>
              <span className="results-score-val">{score} / {PRACTICE_QUESTIONS.length}</span>
              <span className="results-score-label">Score ({Math.round((score / PRACTICE_QUESTIONS.length) * 100)}%)</span>
            </div>
          </div>
          <p className="results-summary-text">
            {score === 5
              ? 'Outstanding! You have mastered all key CISCE Section A concepts for this chapter.'
              : score >= 3
                ? 'Good effort! Review the highlighted explanations below to solidify your understanding.'
                : 'Review Chapter 1 notes and re-attempt the quiz to improve your score.'}
          </p>
        </div>
      )}

      <div className="quiz-questions-stack">
        {PRACTICE_QUESTIONS.map((q, idx) => {
          const selected = selectedAnswers[q.id];
          const isCorrect = selected === q.correctIndex;

          return (
            <div key={q.id} className="quiz-card-full">
              <div className="quiz-card-meta">
                <span className="q-badge">Question {idx + 1}</span>
                {submitted && (
                  <span className={`q-status-badge ${isCorrect ? 'status-correct' : 'status-wrong'}`}>
                    {isCorrect ? 'Correct' : 'Incorrect'}
                  </span>
                )}
              </div>

              <h3 className="quiz-q-title">{q.question}</h3>

              <div className="quiz-options-list">
                {q.options.map((opt, optIdx) => {
                  let optClass = 'quiz-opt-row';
                  if (selected === optIdx) optClass += ' selected';
                  if (submitted) {
                    if (optIdx === q.correctIndex) optClass += ' correct';
                    else if (selected === optIdx) optClass += ' wrong';
                  }

                  return (
                    <button
                      key={optIdx}
                      type="button"
                      className={optClass}
                      onClick={() => handleSelect(q.id, optIdx)}
                      disabled={submitted}
                    >
                      <span className="opt-letter-chip">
                        {String.fromCharCode(65 + optIdx)}
                      </span>
                      <span className="opt-label-text">{opt}</span>
                    </button>
                  );
                })}
              </div>

              {submitted && (
                <div className="quiz-explanation-callout">
                  <strong>Explanation:</strong> {q.explanation}
                </div>
              )}
            </div>
          );
        })}

        {!submitted && (
          <div className="quiz-submit-bar">
            <button
              type="button"
              className="continue-action-btn"
              onClick={() => setSubmitted(true)}
              disabled={Object.keys(selectedAnswers).length === 0}
              style={{ padding: '10px 24px' }}
            >
              <span>Submit &amp; View Evaluation</span>
              <ArrowRight size={15} />
            </button>
          </div>
        )}
      </div>
    </AppLayout>
  );
};
