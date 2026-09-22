"""
Curriculum-Aware AI Tutor Service for SmartLearn.AI.
Grounds responses in student academic profile, verified syllabus resources, and pedagogy.
"""

import base64
from datetime import timedelta
import logging
import re
import time
from typing import Any, Dict, List, Optional, Tuple
import uuid
import httpx
from fastapi import HTTPException, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import create_access_token, decode_access_token
from app.models.learning import LearningResource, Subject, Topic
from app.models.users import User
from app.repositories.learning_repository import LearningRepository
from app.repositories.onboarding_repository import OnboardingRepository
from app.repositories.user_repository import UserRepository
from app.schemas.tutor import (
    GroundedSourceItem,
    TutorChatMessage,
    TutorChatRequest,
    TutorChatResponse,
    VoiceSessionResponse,
)
from app.services.rag_service import RAGRetrievalService
from app.services.llm.failover_service import LLMFailoverService

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
        # 1. Retrieve authenticated student and learning context
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            raise ValueError("Student user not found")

        learning_pref = OnboardingRepository.get_learning_preference(db, user_id)

        # 2. Retrieve verified curriculum evidence bundle and evaluate academic scope
        bundle = RAGRetrievalService.validate_and_retrieve_context(
            db=db,
            user_id=user_id,
            topic_id=request.topic_id,
            student_query=request.message,
        )

        board_name = bundle.subject.board
        grade_name = bundle.subject.grade
        stream_name = bundle.subject.academic_stream or (
            bundle.profile.academic_stream if bundle.profile else None
        )
        subject_name = bundle.subject.name
        chapter_title = bundle.chapter.title
        chapter_num = bundle.chapter.chapter_number
        topic = bundle.topic

        grounded_sources = [
            GroundedSourceItem(
                title=r.title,
                source_name=r.source_name,
                source_url=r.source_url,
                is_verified=r.is_verified,
                resource_type=r.resource_type,
            )
            for r in bundle.verified_resources
        ]
        grounded_titles = [r.title for r in bundle.verified_resources]
        objectives_list = [obj.description for obj in bundle.learning_objectives]

        # 3. Server-side curriculum scope enforcement
        if bundle.is_out_of_scope and bundle.redirection_guidance:
            return TutorChatResponse(
                reply=bundle.redirection_guidance,
                topic_id=topic.id,
                topic_title=topic.title,
                subject_name=subject_name,
                board=board_name,
                grade=grade_name,
                grounded_resource_titles=grounded_titles,
                grounded_sources=grounded_sources,
                learning_objectives=objectives_list,
                is_out_of_scope=True,
                scope_redirection_guidance=bundle.redirection_guidance,
            )

        # 4. Construct System Instruction with verified curriculum grounding
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
            resources=bundle.verified_resources,
            evidence_bundle=bundle,
        )

        # 5. Convert conversation turns to standard message dicts for failover service
        messages: List[Dict[str, str]] = [
            {
                "role": "assistant" if turn.role in ["tutor", "model"] else "user",
                "content": turn.content,
            }
            for turn in request.conversation_history
        ]
        messages.append({"role": "user", "content": request.message})

        # 6. Execute inference through quota-aware multi-provider failover
        llm_result = LLMFailoverService.execute_with_failover(
            messages=messages,
            system_instruction=system_instruction,
            image_base64=request.image_base64,
            timeout_seconds=float(settings.AI_TUTOR_TIMEOUT_SECONDS),
            client=client,
        )
        reply_text = llm_result.reply_text

        # Detect potential out-of-scope flag based on standardized redirection phrasing
        is_out_of_scope = (
            "outside the syllabus" in reply_text.lower()
            or "not covered in this topic" in reply_text.lower()
            or "outside of our topic" in reply_text.lower()
        )

        # Extract Mermaid diagram if present
        diagram_code = None
        if "```mermaid" in reply_text:
            try:
                diagram_code = reply_text.split("```mermaid")[1].split("```")[0].strip()
            except Exception:
                pass

        return TutorChatResponse(
            reply=reply_text,
            topic_id=topic.id,
            topic_title=topic.title,
            subject_name=subject_name,
            board=board_name,
            grade=grade_name,
            grounded_resource_titles=grounded_titles,
            grounded_sources=grounded_sources,
            learning_objectives=objectives_list,
            is_out_of_scope=is_out_of_scope,
            diagram_code=diagram_code,
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
        evidence_bundle: Optional[Any] = None,
    ) -> str:
        """Construct a syllabus-grounded system prompt."""
        # Compile verified resources context
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

        objectives_text = ""
        if evidence_bundle and evidence_bundle.learning_objectives:
            obj_lines = [
                f"- [{obj.code}] {obj.description}"
                for obj in evidence_bundle.learning_objectives
            ]
            objectives_text = "\n\nOFFICIAL SYLLABUS LEARNING OBJECTIVES:\n" + "\n".join(obj_lines)

        pyq_text = ""
        if evidence_bundle and evidence_bundle.authentic_pyqs:
            pyq_lines = [
                f"- [{q.board} {q.exam_year} {q.paper_code} {q.question_number} ({q.marks} Marks)]: {q.question_text}"
                for q in evidence_bundle.authentic_pyqs[:3]
            ]
            pyq_text = "\n\nAUTHENTIC PREVIOUS-YEAR EXAMINATION PATTERNS:\n" + "\n".join(pyq_lines)

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
            f"- Topic Description: {topic_description}\n"
            f"{objectives_text}\n"
            f"{pyq_text}\n\n"
            f"VERIFIED CURRICULUM GROUNDING MATERIAL:\n"
            f"{resources_text}\n\n"
            f"CORE TUTORING PRINCIPLES:\n"
            f"1. Curriculum Grounding: Keep explanations strictly aligned with {board} {grade} level expectations.\n"
            f"2. Student-Centric Pedagogical Style: Explain clearly with relatable analogies, break multi-part concepts into bullet points, and adapt to the student's {preferred_style} style.\n"
            f"3. Visual Doubt Solving & Diagrams: If the student provides an image, identify key elements and guide them. When explaining processes, cause-and-effect, or timelines, you may include a safe ```mermaid flowchart TD``` code block to visualize the concept.\n"
            f"4. Socratic Guidance & Practice: When helping with exercises or questions, give helpful hints and conceptual steps rather than solving it passively.\n"
            f"5. Scope & Boundary Management: If the student asks about something clearly irrelevant or beyond the {board} {grade} syllabus, politely clarify: 'This concept is outside the syllabus for {board} {grade} {subject_name}, but let's connect it back to {topic_title}...' and guide them back.\n"
            f"6. Accuracy: Never hallucinate curriculum requirements or claim fake syllabus regulations.\n"
            f"7. Tone: Friendly, patient, academic, and encouraging.\n"
            f"8. Presentation Quality: Present answers with professional, ChatGPT-quality Markdown. Use clear headings (###), bullet points, markdown tables for comparisons or data, LaTeX math formatting ($inline$ or $$block$$) for any formulas or equations, and callouts (> **Key Takeaway:**) for high-yield exam points. Do not use emojis in explanations."
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
                "maxOutputTokens": 2048,
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
        clean_model = model.removeprefix("models/")
        url = f"{GEMINI_API_BASE}/{clean_model}:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}

        timeout = float(settings.AI_TUTOR_TIMEOUT_SECONDS)

        try:
            max_attempts = 2
            response = None
            for attempt in range(1, max_attempts + 1):
                if client:
                    response = client.post(url, json=payload, headers=headers, timeout=timeout)
                else:
                    with httpx.Client(timeout=timeout) as http_client:
                        response = http_client.post(url, json=payload, headers=headers)

                # Retry once if provider indicates temporary demand spike (503)
                if response.status_code == 503 and attempt < max_attempts:
                    logger.warning(f"Gemini API returned 503 (high demand); retrying in 1.5s (attempt {attempt}/{max_attempts})...")
                    time.sleep(1.5)
                    continue
                break

            if response is None:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Failed to obtain response from AI Tutor service.",
                )

            if response.status_code == 429:
                logger.warning("Gemini API rate limit exceeded (429)")
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="AI Tutor quota or rate limit exceeded. Please wait a moment before sending another message.",
                )

            if response.status_code != 200:
                err_body = response.text
                sanitized_err = re.sub(r"key=[a-zA-Z0-9_\-]+", "key=[REDACTED]", err_body)
                logger.error(f"Gemini API returned error {response.status_code}: {sanitized_err}")
                if "API_KEY_INVALID" in err_body or "PERMISSION_DENIED" in err_body:
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="AI Tutor authentication failed. Please verify GEMINI_API_KEY.",
                    )
                if response.status_code == 404:
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail=f"The configured AI Tutor model '{clean_model}' is unavailable or not supported. Please verify AI_TUTOR_MODEL configuration.",
                    )
                if response.status_code == 503:
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="AI Tutor provider is temporarily experiencing high demand. Please try again in a few moments.",
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
            text_parts = [p.get("text", "") for p in parts if isinstance(p, dict) and "text" in p]
            if not text_parts or not "".join(text_parts).strip():
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Empty response returned from AI Tutor.",
                )

            return "\n\n".join(text_parts).strip()

        except httpx.TimeoutException:
            logger.error(f"Gemini API request timed out for model {clean_model}")
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="AI Tutor request timed out. Please try again.",
            )
        except httpx.RequestError as exc:
            logger.error(f"Network error contacting Gemini API: {type(exc).__name__}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Unable to reach AI Tutor provider. Please check network connectivity.",
            )

    # ── Voice Conversational Tutoring Engine ──────────────────────────────────
    @classmethod
    def create_voice_session(
        cls, db: Session, user_id: int, topic_id: int
    ) -> VoiceSessionResponse:
        """Initialize an authenticated conversational voice session with ephemeral credential."""
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            raise ValueError("Student user not found")

        topic = LearningRepository.get_topic_by_id(db, topic_id)
        if not topic:
            raise ValueError(f"Topic with id {topic_id} not found")

        chapter = LearningRepository.get_chapter_by_id(db, topic.chapter_id)
        subject = (
            LearningRepository.get_subject_by_id(db, chapter.subject_id)
            if chapter
            else None
        )
        profile = OnboardingRepository.get_student_profile(db, user_id)

        board_name = subject.board if subject else (profile.board if profile else "CBSE")
        grade_name = subject.grade if subject else (profile.grade if profile else "Class 11")
        subject_name = subject.name if subject else "General Studies"

        session_id = str(uuid.uuid4())
        expires_seconds = 900  # 15 minutes ephemeral token
        session_token = create_access_token(
            subject=user.id,
            expires_delta=timedelta(seconds=expires_seconds),
            extra_claims={
                "topic_id": topic_id,
                "session_id": session_id,
                "type": "voice_session",
            },
        )

        return VoiceSessionResponse(
            session_id=session_id,
            session_token=session_token,
            ws_endpoint=f"/api/v1/tutor/voice/ws?token={session_token}",
            topic_id=topic.id,
            topic_title=topic.title,
            subject_name=subject_name,
            board=board_name,
            grade=grade_name,
            expires_in_seconds=expires_seconds,
        )

    @classmethod
    def _build_voice_system_instruction(
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
        """Construct spoken voice conversation system instruction."""
        resource_excerpts = []
        for r in resources:
            if r.text_content:
                resource_excerpts.append(
                    f"[{r.resource_type.upper()}] {r.title}:\n{r.text_content.strip()}"
                )

        resources_text = (
            "\n\n---\n\n".join(resource_excerpts)
            if resource_excerpts
            else "Standard verified syllabus topic guidelines."
        )

        stream_info = f", Stream: {stream}" if stream else ""

        return (
            f"You are the official SmartLearn.AI Conversational Voice Tutor.\n"
            f"You are in a live, real-time voice call with the student.\n\n"
            f"STUDENT CONTEXT:\n"
            f"- Name: {student_name}\n"
            f"- Board: {board}\n"
            f"- Grade/Class: {grade}{stream_info}\n"
            f"- Preferred Learning Style: {preferred_style}\n\n"
            f"CURRICULUM CONTEXT:\n"
            f"- Subject: {subject_name}\n"
            f"- Chapter {chapter_number}: {chapter_title}\n"
            f"- Topic {topic_number}: {topic_title}\n"
            f"- Topic Summary: {topic_description}\n\n"
            f"VERIFIED SYLLABUS GROUNDING MATERIAL:\n"
            f"{resources_text}\n\n"
            f"SPOKEN VOICE RULES:\n"
            f"1. Spoken Audio Output: Your response will be spoken aloud to the student. Keep answers conversational, natural, warm, and brief (typically 2 to 4 sentences max per turn).\n"
            f"2. No Markdown Formatting: Do NOT use markdown symbols (no asterisks, bold tags, bullet points, headers, or hashtags) because they sound awkward when spoken aloud.\n"
            f"3. Socratic Turn-Taking: Address the student directly by name occasionally, explain one concept at a time, and end with an engaging guiding check for understanding (e.g., 'Does that make sense, or would you like a quick example?').\n"
            f"4. Curriculum Grounding: Stay strictly grounded in {board} {grade} {subject_name} syllabus expectations.\n"
            f"5. Scope Management: If the student asks something outside {board} {grade} {subject_name}, politely mention in one sentence that it is outside this topic and gently redirect them."
        )

    @classmethod
    def process_voice_turn(
        cls,
        db: Session,
        user_id: int,
        topic_id: int,
        speech_text: str,
        conversation_history: List[TutorChatMessage],
        client: Optional[httpx.Client] = None,
    ) -> Dict[str, Any]:
        """Process an incremental or finalized conversational voice turn."""
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            raise ValueError("Student user not found")

        topic = LearningRepository.get_topic_by_id(db, topic_id)
        if not topic:
            raise ValueError(f"Topic with id {topic_id} not found")

        chapter = LearningRepository.get_chapter_by_id(db, topic.chapter_id)
        subject = (
            LearningRepository.get_subject_by_id(db, chapter.subject_id)
            if chapter
            else None
        )
        profile = OnboardingRepository.get_student_profile(db, user_id)
        learning_pref = OnboardingRepository.get_learning_preference(db, user_id)

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

        resources = LearningRepository.get_resources_by_topic_id(
            db, topic.id, only_active=True
        )
        grounded_titles = [r.title for r in resources if r.is_verified]

        system_instruction = cls._build_voice_system_instruction(
            student_name=user.full_name,
            board=board_name,
            grade=grade_name,
            stream=stream_name,
            preferred_style=learning_pref.preferred_style if learning_pref else "Auditory",
            subject_name=subject_name,
            chapter_number=chapter_num,
            chapter_title=chapter_title,
            topic_number=topic.topic_number,
            topic_title=topic.title,
            topic_description=topic.description or "",
            resources=resources,
        )

        messages: List[Dict[str, str]] = [
            {
                "role": "assistant" if turn.role in ["tutor", "model"] else "user",
                "content": turn.content,
            }
            for turn in conversation_history
        ]
        messages.append({"role": "user", "content": speech_text})

        llm_result = LLMFailoverService.execute_with_failover(
            messages=messages,
            system_instruction=system_instruction,
            image_base64=None,
            timeout_seconds=float(settings.AI_TUTOR_TIMEOUT_SECONDS),
            client=client,
        )
        reply_text = llm_result.reply_text

        is_out_of_scope = (
            "outside the syllabus" in reply_text.lower()
            or "not covered in this topic" in reply_text.lower()
            or "outside of our topic" in reply_text.lower()
        )

        return {
            "reply": reply_text,
            "topic_id": topic.id,
            "topic_title": topic.title,
            "subject_name": subject_name,
            "board": board_name,
            "grade": grade_name,
            "grounded_resource_titles": grounded_titles,
            "is_out_of_scope": is_out_of_scope,
        }

    @classmethod
    async def handle_voice_websocket(
        cls,
        websocket: WebSocket,
        token: str,
        db: Session,
        client: Optional[httpx.Client] = None,
    ) -> None:
        """Handle full-duplex WebSocket conversational turn-taking with interruption."""
        # 1. Authenticate token
        try:
            payload = decode_access_token(token)
            user_id = int(payload.get("sub"))
            topic_id = int(payload.get("topic_id", 0))
            session_id = payload.get("session_id", "default")
        except Exception as e:
            logger.warning(f"Voice WebSocket auth rejection: {e}")
            await websocket.close(code=4401, reason="Invalid or expired session token")
            return

        user = UserRepository.get_by_id(db, user_id)
        if not user or not user.is_active:
            await websocket.close(code=4401, reason="Inactive or non-existent user")
            return

        topic = LearningRepository.get_topic_by_id(db, topic_id)
        if not topic:
            await websocket.close(code=4404, reason="Curriculum topic not found")
            return

        chapter = LearningRepository.get_chapter_by_id(db, topic.chapter_id)
        subject = (
            LearningRepository.get_subject_by_id(db, chapter.subject_id)
            if chapter
            else None
        )
        profile = OnboardingRepository.get_student_profile(db, user_id)

        board_name = subject.board if subject else (profile.board if profile else "CBSE")
        grade_name = subject.grade if subject else (profile.grade if profile else "Class 11")
        subject_name = subject.name if subject else "General Studies"

        await websocket.accept()

        # 2. Emit initial session_ready handshake
        await websocket.send_json({
            "type": "session_ready",
            "session_id": session_id,
            "state": "listening",
            "topic_id": topic.id,
            "topic_title": topic.title,
            "subject_name": subject_name,
            "board": board_name,
            "grade": grade_name,
            "message": f"Connected to Voice Tutor for {topic.title}. You may start speaking.",
        })

        conversation_history: List[TutorChatMessage] = []

        try:
            while True:
                msg = await websocket.receive_json()
                event_type = msg.get("type", "")

                if event_type == "ping":
                    await websocket.send_json({"type": "pong"})
                    continue

                if event_type == "interrupt":
                    logger.info(f"Student barged in / interrupted voice session {session_id}")
                    await websocket.send_json({
                        "type": "tutor_interrupted",
                        "state": "listening",
                        "message": "Playback halted. Listening to student.",
                    })
                    continue

                if event_type == "speech_interim":
                    interim_text = msg.get("text", "")
                    await websocket.send_json({
                        "type": "transcript_echo",
                        "state": "listening",
                        "text": interim_text,
                    })
                    continue

                if event_type == "speech_final":
                    speech_text = msg.get("text", "").strip()
                    if not speech_text:
                        await websocket.send_json({"type": "listening", "state": "listening"})
                        continue

                    # Transition to thinking state
                    await websocket.send_json({
                        "type": "thinking",
                        "state": "thinking",
                        "transcript": speech_text,
                    })

                    try:
                        turn_result = cls.process_voice_turn(
                            db=db,
                            user_id=user.id,
                            topic_id=topic.id,
                            speech_text=speech_text,
                            conversation_history=conversation_history,
                            client=client,
                        )

                        reply_text = turn_result["reply"]

                        # Append to history
                        conversation_history.append(
                            TutorChatMessage(role="student", content=speech_text)
                        )
                        conversation_history.append(
                            TutorChatMessage(role="tutor", content=reply_text)
                        )

                        # Trim history to last 10 turns
                        if len(conversation_history) > 10:
                            conversation_history = conversation_history[-10:]

                        # Emit speaking event
                        await websocket.send_json({
                            "type": "speaking",
                            "state": "speaking",
                            "text": reply_text,
                            "user_transcript": speech_text,
                            "grounded_resource_titles": turn_result["grounded_resource_titles"],
                            "is_out_of_scope": turn_result["is_out_of_scope"],
                        })

                    except HTTPException as http_exc:
                        await websocket.send_json({
                            "type": "error",
                            "state": "error",
                            "status_code": http_exc.status_code,
                            "detail": http_exc.detail,
                        })
                    except Exception as err:
                        logger.error(f"Voice generation error: {err}")
                        await websocket.send_json({
                            "type": "error",
                            "state": "error",
                            "detail": "Voice tutor processing error. Please try speaking again.",
                        })

        except WebSocketDisconnect:
            logger.info(f"Voice WebSocket disconnected gracefully for session {session_id}")
        except Exception as e:
            logger.error(f"Voice WebSocket unhandled exception: {e}")
            try:
                await websocket.close(code=1011, reason="Server voice processing error")
            except Exception:
                pass

