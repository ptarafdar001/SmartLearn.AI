"""
Curriculum-Aware AI Tutor Service for SmartLearn.AI.
Grounds responses in student academic profile, verified syllabus resources, and pedagogy.
"""

import base64
import logging
import re
from typing import Any, Dict, List, Optional, Tuple
import httpx
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.learning import LearningResource, Subject, Topic
from app.models.users import User
from app.repositories.learning_repository import LearningRepository
from app.repositories.onboarding_repository import OnboardingRepository
from app.repositories.user_repository import UserRepository
from app.schemas.tutor import TutorChatMessage, TutorChatRequest, TutorChatResponse

logger = logging.getLogger("smartlearn.tutor")
settings = get_settings()

GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"


class TutorService:
    """Orchestrates curriculum retrieval, system prompt synthesis, and multimodal LLM inference."""

    @classmethod
    def generate_tutor_reply(
        cls,
        db: Session,
        user_id: int,
        request: TutorChatRequest,
        client: Optional[httpx.Client] = None,
    ) -> TutorChatResponse:
        """
        Generate a pedagogical, curriculum-grounded response for the authenticated student.
        """
        # 1. Verify and retrieve student context
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            raise ValueError("Student user not found")

        profile = OnboardingRepository.get_student_profile(db, user_id)
        learning_pref = OnboardingRepository.get_learning_preference(db, user_id)

        # 2. Verify and retrieve topic & syllabus context
        topic = LearningRepository.get_topic_by_id(db, request.topic_id)
        if not topic:
            raise ValueError(f"Topic with id {request.topic_id} not found")

        chapter = LearningRepository.get_chapter_by_id(db, topic.chapter_id)
        subject = (
            LearningRepository.get_subject_by_id(db, chapter.subject_id)
            if chapter
            else None
        )

        board_name = subject.board if subject else (profile.board if profile else "CBSE")
        grade_name = subject.grade if subject else (profile.grade if profile else "Class 11")
        stream_name = (
            subject.academic_stream
            if subject and subject.academic_stream
            else (profile.academic_stream if profile else None)
        )
        subject_name = subject.name if subject else "General Studies"
        chapter_title = chapter.title if chapter else "Current Chapter"
        chapter_num = chapter.chapter_number if chapter else 1

        # 3. Retrieve verified learning resources for grounding
        resources = LearningRepository.get_resources_by_topic_id(
            db, topic.id, only_active=True
        )
        grounded_titles = [r.title for r in resources if r.is_verified]

        # 4. Construct System Instruction with curriculum grounding
        system_instruction = cls._build_system_instruction(
            student_name=user.full_name,
            board=board_name,
            grade=grade_name,
            stream=stream_name,
            preferred_style=learning_pref.preferred_style if learning_pref else "Interactive",
            subject_name=subject_name,
            chapter_number=chapter_num,
            chapter_title=chapter_title,
            topic_number=topic.topic_number,
            topic_title=topic.title,
            topic_description=topic.description or "",
            resources=resources,
        )

        # 5. Check API key configuration
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI Tutor service is not configured. GEMINI_API_KEY is required in the backend environment.",
            )

        # 6. Parse and validate optional image
        image_part: Optional[Dict[str, Any]] = None
        if request.image_base64:
            image_part = cls._parse_image_payload(request.image_base64)

        # 7. Construct Gemini multimodal request payload
        gemini_payload = cls._build_gemini_payload(
            system_instruction=system_instruction,
            conversation_history=request.conversation_history,
            current_message=request.message,
            image_part=image_part,
        )

        # 8. Call Gemini REST API
        reply_text = cls._call_gemini_api(
            api_key=api_key,
            model=settings.AI_TUTOR_MODEL,
            payload=gemini_payload,
            client=client,
        )

        # Detect potential out-of-scope flag based on standardized redirection phrasing
        is_out_of_scope = (
            "outside the syllabus" in reply_text.lower()
            or "not covered in this topic" in reply_text.lower()
            or "outside of our topic" in reply_text.lower()
        )

        return TutorChatResponse(
            reply=reply_text,
            topic_id=topic.id,
            topic_title=topic.title,
            subject_name=subject_name,
            board=board_name,
            grade=grade_name,
            grounded_resource_titles=grounded_titles,
            is_out_of_scope=is_out_of_scope,
        )

    @classmethod
    def _build_system_instruction(
        cls,
        student_name: str,
        board: str,
        grade: str,
        stream: Optional[str],
        preferred_style: str,
        subject_name: str,
        chapter_number: int,
        chapter_title: str,
        topic_number: int,
        topic_title: str,
        topic_description: str,
        resources: List[LearningResource],
    ) -> str:
        """Construct a syllabus-grounded system prompt."""
        # Compile verified resources context (notes and reading texts)
        resource_excerpts = []
        for r in resources:
            if r.text_content:
                resource_excerpts.append(
                    f"[{r.resource_type.upper()}] {r.title} (Source: {r.source_name or r.provider}):\n{r.text_content.strip()}"
                )

        resources_text = (
            "\n\n---\n\n".join(resource_excerpts)
            if resource_excerpts
            else "No explicit text resources pre-loaded for this topic. Base guidance on standard verified syllabus concepts."
        )

        stream_info = f", Stream: {stream}" if stream else ""

        return (
            f"You are the official SmartLearn.AI Curriculum-Aware AI Tutor.\n\n"
            f"STUDENT PROFILE:\n"
            f"- Name: {student_name}\n"
            f"- Board: {board}\n"
            f"- Grade/Class: {grade}{stream_info}\n"
            f"- Preferred Learning Style: {preferred_style}\n\n"
            f"CURRENT TOPIC CONTEXT:\n"
            f"- Subject: {subject_name}\n"
            f"- Chapter {chapter_number}: {chapter_title}\n"
            f"- Topic {topic_number}: {topic_title}\n"
            f"- Topic Description: {topic_description}\n\n"
            f"VERIFIED CURRICULUM GROUNDING MATERIAL:\n"
            f"{resources_text}\n\n"
            f"CORE TUTORING PRINCIPLES:\n"
            f"1. Curriculum Grounding: Keep explanations strictly aligned with {board} {grade} level expectations.\n"
            f"2. Student-Centric Pedagogical Style: Explain clearly with relatable analogies, break multi-part concepts into bullet points, and adapt to the student's {preferred_style} style.\n"
            f"3. Visual Doubt Solving: If the student provides an image (e.g. textbook page, exercise diagram, or handwritten doubt), carefully identify what is shown, pinpoint their error or confusion, and provide step-by-step guidance.\n"
            f"4. Socratic Guidance & Practice: When helping with exercises or questions, give helpful hints and conceptual steps rather than solving it passively.\n"
            f"5. Scope & Boundary Management: If the student asks about something clearly irrelevant or beyond the {board} {grade} syllabus, politely clarify: 'This concept is outside the syllabus for {board} {grade} {subject_name}, but let's connect it back to {topic_title}...' and guide them back.\n"
            f"6. Accuracy: Never hallucinate curriculum requirements or claim fake syllabus regulations.\n"
            f"7. Tone: Friendly, patient, academic, and encouraging."
        )

    @classmethod
    def _parse_image_payload(cls, image_data: str) -> Dict[str, Any]:
        """Validate and parse base64 image data URI or raw base64."""
        mime_type = "image/jpeg"
        raw_b64 = image_data

        if image_data.startswith("data:"):
            match = re.match(r"^data:(image/[a-zA-Z0-9.+_-]+);base64,(.*)$", image_data)
            if match:
                mime_type = match.group(1)
                raw_b64 = match.group(2)
            else:
                raise ValueError("Invalid data URI format for image")

        # Validate base64 decoding and approximate size (< 7MB)
        try:
            decoded = base64.b64decode(raw_b64, validate=True)
        except Exception:
            raise ValueError("Invalid base64 encoding in image attachment")

        if len(decoded) > 7 * 1024 * 1024:
            raise ValueError("Image attachment exceeds maximum allowed size of 7MB")

        return {
            "inline_data": {
                "mime_type": mime_type,
                "data": raw_b64,
            }
        }

    @classmethod
    def _build_gemini_payload(
        cls,
        system_instruction: str,
        conversation_history: List[TutorChatMessage],
        current_message: str,
        image_part: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Construct the Gemini API contents array and generation configuration."""
        contents: List[Dict[str, Any]] = []

        # Map previous turns
        for turn in conversation_history:
            role = "model" if turn.role in ["tutor", "model"] else "user"
            contents.append({
                "role": role,
                "parts": [{"text": turn.content}],
            })

        # Add current message turn
        current_parts: List[Dict[str, Any]] = []
        if image_part:
            current_parts.append(image_part)
        current_parts.append({"text": current_message})

        contents.append({
            "role": "user",
            "parts": current_parts,
        })

        return {
            "contents": contents,
            "system_instruction": {
                "parts": [{"text": system_instruction}]
            },
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 1200,
                "topP": 0.95,
            },
        }

    @classmethod
    def _call_gemini_api(
        cls,
        api_key: str,
        model: str,
        payload: Dict[str, Any],
        client: Optional[httpx.Client] = None,
    ) -> str:
        """Send synchronous HTTP request to Google Gemini API."""
        url = f"{GEMINI_API_BASE}/{model}:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}

        timeout = float(settings.AI_TUTOR_TIMEOUT_SECONDS)

        try:
            if client:
                response = client.post(url, json=payload, headers=headers, timeout=timeout)
            else:
                with httpx.Client(timeout=timeout) as http_client:
                    response = http_client.post(url, json=payload, headers=headers)

            if response.status_code == 429:
                logger.warning("Gemini API rate limit exceeded (429)")
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="AI Tutor quota or rate limit exceeded. Please wait a moment before sending another message.",
                )

            if response.status_code != 200:
                err_body = response.text
                logger.error(f"Gemini API returned error {response.status_code}: {err_body}")
                if "API_KEY_INVALID" in err_body or "PERMISSION_DENIED" in err_body:
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="AI Tutor authentication failed. Please verify GEMINI_API_KEY.",
                    )
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"AI Tutor upstream service error ({response.status_code}).",
                )

            data = response.json()
            candidates = data.get("candidates", [])
            if not candidates:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="AI Tutor did not generate a response. Please try rephrasing.",
                )

            parts = candidates[0].get("content", {}).get("parts", [])
            if not parts:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Empty response returned from AI Tutor.",
                )

            return parts[0].get("text", "").strip()

        except httpx.TimeoutException:
            logger.error("Gemini API request timed out")
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="AI Tutor request timed out. Please try again.",
            )
        except httpx.RequestError as exc:
            logger.error(f"Network error contacting Gemini API: {exc}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Unable to reach AI Tutor provider. Please check network connectivity.",
            )
