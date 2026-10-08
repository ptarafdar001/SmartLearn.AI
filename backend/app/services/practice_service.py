"""
Practice & Exam Question Service for SmartLearn.AI.

Strictly enforces:
1. Segregation of Authentic Previous-Year Questions (PYQs) from AI-generated practice.
2. Authentic PYQ metadata preservation (Board, Exam Year, Paper Code, Marks, Marking Scheme, Source URL).
3. Explicit labeling of generated questions: "AI-generated practice question".
4. Student attempt tracking, instant pedagogical grading, and feedback recording.
"""

from datetime import datetime, timezone
import json
import logging
from typing import Any, Dict, List, Optional
import httpx
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.learning import PracticeQuestion, PreviousYearQuestion
from app.repositories.learning_repository import LearningRepository
from app.schemas.learning import (
    PracticeQuestionAttemptRequest,
    PracticeQuestionAttemptResponse,
    PracticeQuestionResponse,
    PreviousYearQuestionResponse,
)
from app.services.rag_service import RAGRetrievalService
from app.services.tutor_service import TutorService

logger = logging.getLogger("smartlearn.practice")
settings = get_settings()


class PracticeService:
    """Orchestrates authentic PYQs retrieval, AI practice generation, and student attempt grading."""

    # ── Authentic PYQ Retrieval ───────────────────────────────────────────────
    @classmethod
    def get_authentic_pyqs(
        cls, db: Session, topic_id: int
    ) -> List[PreviousYearQuestionResponse]:
        """
        Fetch authentic official board examination questions for a topic.
        Never fabricates questions or official attribution.
        """
        pyqs = LearningRepository.get_pyqs_by_topic_id(db, topic_id=topic_id, only_verified=True)
        return [PreviousYearQuestionResponse.model_validate(q) for q in pyqs]

    @classmethod
    def get_subject_pyqs(
        cls, db: Session, subject_id: int
    ) -> List[PreviousYearQuestionResponse]:
        """Fetch all authentic PYQs for a subject catalog."""
        pyqs = LearningRepository.get_pyqs_by_subject_id(db, subject_id=subject_id, only_verified=True)
        return [PreviousYearQuestionResponse.model_validate(q) for q in pyqs]

    # ── AI-Generated Practice Questions ───────────────────────────────────────
    @classmethod
    def get_or_generate_practice_questions(
        cls,
        db: Session,
        user_id: int,
        topic_id: int,
        difficulty: Optional[str] = None,
        force_generate: bool = False,
        client: Optional[httpx.Client] = None,
    ) -> List[PracticeQuestionResponse]:
        """
        Fetch existing AI practice questions or synthesize new syllabus-aligned questions.
        All generated questions are strictly labeled with `is_ai_generated: True`.
        """
        if not force_generate:
            existing = LearningRepository.get_practice_questions(
                db, topic_id=topic_id, difficulty=difficulty
            )
            if existing:
                return [PracticeQuestionResponse.model_validate(q) for q in existing]

        # Retrieve verified syllabus evidence to guide generation
        bundle = RAGRetrievalService.validate_and_retrieve_context(
            db=db, user_id=user_id, topic_id=topic_id
        )

        api_key = settings.GEMINI_API_KEY
        if not api_key:
            # Return whatever practice questions exist in DB
            existing = LearningRepository.get_practice_questions(db, topic_id=topic_id)
            return [PracticeQuestionResponse.model_validate(q) for q in existing]

        evidence_text = RAGRetrievalService.format_evidence_for_prompt(bundle)

        prompt = (
            f"Generate 3 new educational multiple-choice practice questions (MCQs) for:\n"
            f"Subject: {bundle.subject.name} ({bundle.subject.board} {bundle.subject.grade})\n"
            f"Topic: {bundle.topic.title}\n\n"
            f"CURRICULUM GROUNDING EVIDENCE:\n{evidence_text}\n\n"
            f"Requirements:\n"
            f"1. Generate strictly 3 MCQs in valid JSON format.\n"
            f"2. Each MCQ must have:\n"
            f"   - 'question_text': Clear question scenario.\n"
            f"   - 'options': Array of 4 objects [{{'id': 'A', 'text': '...'}}, {{'id': 'B', 'text': '...'}}, ...]\n"
            f"   - 'correct_answer': The correct option letter ('A', 'B', 'C', or 'D').\n"
            f"   - 'explanation': Pedagogical rationale explaining why the answer is correct and others are incorrect.\n"
            f"   - 'difficulty': 'easy', 'medium', or 'hard'.\n"
            f"   - 'marks': 1\n"
            f"3. Return ONLY a JSON array of objects with no extraneous markdown or formatting."
        )

        system_instruction = (
            f"You are the examination assessment engine for SmartLearn.AI. "
            f"You construct syllabus-valid practice questions grounded in verified curriculum material. "
            f"Never claim that generated questions are official board PYQs."
        )

        gemini_payload = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "system_instruction": {"parts": [{"text": system_instruction}]},
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 2048,
                "responseMimeType": "application/json",
            },
        }

        reply_json_str = TutorService._call_gemini_api(
            api_key=api_key,
            model=settings.AI_TUTOR_MODEL,
            payload=gemini_payload,
            client=client,
        )

        created_questions: List[PracticeQuestion] = []
        try:
            questions_data = json.loads(reply_json_str)
            if isinstance(questions_data, dict) and "questions" in questions_data:
                questions_data = questions_data["questions"]

            if isinstance(questions_data, list):
                for item in questions_data:
                    pq = PracticeQuestion(
                        topic_id=bundle.topic.id,
                        question_text=item.get("question_text", ""),
                        question_type="mcq",
                        options=item.get("options", []),
                        correct_answer=item.get("correct_answer", "A"),
                        explanation=item.get("explanation", ""),
                        difficulty=item.get("difficulty", "medium"),
                        marks=item.get("marks", 1),
                        is_ai_generated=True,
                        generation_provenance={
                            "generator": "SmartLearn Practice Engine v2",
                            "model": settings.AI_TUTOR_MODEL,
                            "type": "AI-generated practice question",
                            "syllabus_aligned": True,
                        },
                    )
                    db.add(pq)
                    created_questions.append(pq)
                db.commit()
                for q in created_questions:
                    db.refresh(q)
        except Exception as e:
            logger.error(f"Failed to parse generated practice questions JSON: {e}")
            # Fall back to existing questions
            created_questions = LearningRepository.get_practice_questions(db, topic_id=topic_id)

        return [PracticeQuestionResponse.model_validate(q) for q in created_questions]

    # ── Student Attempt Evaluation ────────────────────────────────────────────
    @classmethod
    def evaluate_and_record_attempt(
        cls,
        db: Session,
        user_id: int,
        question_id: int,
        attempt_req: PracticeQuestionAttemptRequest,
    ) -> PracticeQuestionAttemptResponse:
        """
        Evaluate student's answer against official answer key, award score,
        and log attempt to student_question_attempts.
        """
        pq = LearningRepository.get_practice_question_by_id(db, question_id)
        if not pq:
            raise ValueError(f"Practice question with id {question_id} not found")

        student_answer = attempt_req.user_answer.strip().upper()
        correct_answer = pq.correct_answer.strip().upper()

        is_correct = (student_answer == correct_answer) or (
            len(student_answer) == 1 and student_answer == correct_answer[:1]
        )
        marks_obtained = float(pq.marks) if is_correct else 0.0

        feedback = (
            f"Correct! {pq.explanation}"
            if is_correct
            else f"Incorrect. The correct answer is ({correct_answer}). {pq.explanation}"
        )

        attempt_record = LearningRepository.record_question_attempt(
            db=db,
            user_id=user_id,
            question_type="practice",
            user_answer=attempt_req.user_answer,
            is_correct=is_correct,
            marks_obtained=marks_obtained,
            feedback=feedback,
            practice_question_id=pq.id,
        )

        return PracticeQuestionAttemptResponse(
            id=attempt_record.id,
            question_id=pq.id,
            question_type=pq.question_type,
            user_answer=attempt_req.user_answer,
            is_correct=is_correct,
            marks_obtained=marks_obtained,
            max_marks=pq.marks,
            feedback=feedback,
            explanation=pq.explanation,
            attempted_at=attempt_record.attempted_at,
        )
