"""
Google Gemini LLM Provider implementation for SmartLearn.AI.
Handles native multimodal vision, thinking model accommodation, and syllabus grounding.
"""

import base64
import logging
import re
import time
from typing import Any, Dict, List, Optional
import httpx

from app.services.llm.base import (
    BaseLLMProvider,
    LLMGenerationResult,
    ProviderErrorCode,
    ProviderException,
)

logger = logging.getLogger("smartlearn.tutor.gemini")

GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"


class GeminiProvider(BaseLLMProvider):
    """Encapsulates inference against Google Gemini APIs."""

    def __init__(self, api_key: Optional[str], model: str = "gemini-3.6-flash"):
        self._api_key = api_key
        self._model = model.removeprefix("models/")

    @property
    def provider_name(self) -> str:
        return "gemini"

    @property
    def default_model(self) -> str:
        return self._model

    @property
    def is_configured(self) -> bool:
        return bool(self._api_key and self._api_key.strip())

    @property
    def supports_vision(self) -> bool:
        # All modern Gemini Flash/Pro models support multimodal vision
        return True

    def _parse_image_payload(self, image_data: str) -> Dict[str, Any]:
        """Validate and parse base64 image data URI or raw base64 into Gemini inline_data."""
        mime_type = "image/jpeg"
        raw_b64 = image_data

        if image_data.startswith("data:"):
            match = re.match(r"^data:(image/[a-zA-Z0-9.+_-]+);base64,(.*)$", image_data)
            if match:
                mime_type = match.group(1)
                raw_b64 = match.group(2)
            else:
                raise ProviderException(
                    provider_name=self.provider_name,
                    code=ProviderErrorCode.INVALID_REQUEST,
                    message="Invalid data URI format for image attachment",
                    status_code=400,
                )

        try:
            decoded = base64.b64decode(raw_b64, validate=True)
        except Exception:
            raise ProviderException(
                provider_name=self.provider_name,
                code=ProviderErrorCode.INVALID_REQUEST,
                message="Invalid base64 encoding in image attachment",
                status_code=400,
            )

        if len(decoded) > 7 * 1024 * 1024:
            raise ProviderException(
                provider_name=self.provider_name,
                code=ProviderErrorCode.INVALID_REQUEST,
                message="Image attachment exceeds maximum allowed size of 7MB",
                status_code=400,
            )

        return {
            "inline_data": {
                "mime_type": mime_type,
                "data": raw_b64,
            }
        }

    def _build_payload(
        self,
        messages: List[Dict[str, str]],
        system_instruction: str,
        image_base64: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Construct Gemini contents array with system instruction and optional image."""
        contents: List[Dict[str, Any]] = []

        # Previous conversation turns
        for turn in messages[:-1] if messages else []:
            role = "model" if turn.get("role") in ["assistant", "model", "tutor"] else "user"
            contents.append({
                "role": role,
                "parts": [{"text": turn.get("content", "")}],
            })

        # Latest message turn (attaching image if present)
        current_turn = messages[-1] if messages else {"role": "user", "content": ""}
        current_parts: List[Dict[str, Any]] = []
        if image_base64:
            current_parts.append(self._parse_image_payload(image_base64))
        current_parts.append({"text": current_turn.get("content", "")})

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

    def generate(
        self,
        messages: List[Dict[str, str]],
        system_instruction: str,
        image_base64: Optional[str] = None,
        timeout_seconds: float = 30.0,
        client: Optional[httpx.Client] = None,
    ) -> LLMGenerationResult:
        if not self.is_configured:
            raise ProviderException(
                provider_name=self.provider_name,
                code=ProviderErrorCode.CONFIG_ERROR,
                message="Gemini API key is not configured in backend environment.",
                status_code=503,
                retryable=False,
            )

        url = f"{GEMINI_API_BASE}/{self._model}:generateContent?key={self._api_key}"
        headers = {"Content-Type": "application/json"}
        payload = self._build_payload(messages, system_instruction, image_base64)

        try:
            max_attempts = 2
            response = None
            for attempt in range(1, max_attempts + 1):
                if client:
                    response = client.post(url, json=payload, headers=headers, timeout=timeout_seconds)
                else:
                    with httpx.Client(timeout=timeout_seconds) as http_client:
                        response = http_client.post(url, json=payload, headers=headers)

                # Retry once if provider indicates temporary demand spike (503)
                if response.status_code == 503 and attempt < max_attempts:
                    logger.warning(
                        f"Gemini API returned 503 (high demand); retrying in 1.5s (attempt {attempt}/{max_attempts})..."
                    )
                    time.sleep(1.5)
                    continue
                break

            if response is None:
                raise ProviderException(
                    provider_name=self.provider_name,
                    code=ProviderErrorCode.TEMPORARY_OUTAGE,
                    message="Failed to obtain response from Gemini API.",
                    status_code=502,
                    retryable=True,
                )

            # Check status codes
            if response.status_code == 429:
                err_text = self.sanitize_error_string(response.text)
                logger.warning(f"Gemini quota exhausted (429): {err_text[:180]}")
                raise ProviderException(
                    provider_name=self.provider_name,
                    code=ProviderErrorCode.QUOTA_EXHAUSTED,
                    message="Gemini rate limit or quota exceeded.",
                    status_code=429,
                    retryable=True,
                    retry_after_seconds=60.0,
                )

            if response.status_code != 200:
                err_body = response.text
                sanitized_err = self.sanitize_error_string(err_body)
                logger.error(f"Gemini API returned error {response.status_code}: {sanitized_err[:250]}")

                if "API_KEY_INVALID" in err_body or "PERMISSION_DENIED" in err_body:
                    raise ProviderException(
                        provider_name=self.provider_name,
                        code=ProviderErrorCode.AUTH_ERROR,
                        message="Gemini authentication failed. Please verify API key.",
                        status_code=503,
                        retryable=False,
                    )
                if response.status_code == 404:
                    raise ProviderException(
                        provider_name=self.provider_name,
                        code=ProviderErrorCode.CONFIG_ERROR,
                        message=f"Gemini model '{self._model}' is unavailable or not supported.",
                        status_code=502,
                        retryable=False,
                    )
                if response.status_code == 503:
                    raise ProviderException(
                        provider_name=self.provider_name,
                        code=ProviderErrorCode.TEMPORARY_OUTAGE,
                        message="Gemini provider is temporarily experiencing high demand.",
                        status_code=503,
                        retryable=True,
                        retry_after_seconds=5.0,
                    )

                raise ProviderException(
                    provider_name=self.provider_name,
                    code=ProviderErrorCode.TEMPORARY_OUTAGE,
                    message=f"Gemini upstream error ({response.status_code}).",
                    status_code=502,
                    retryable=True,
                )

            data = response.json()
            candidates = data.get("candidates", [])
            if not candidates:
                raise ProviderException(
                    provider_name=self.provider_name,
                    code=ProviderErrorCode.INVALID_REQUEST,
                    message="Gemini did not generate candidate content.",
                    status_code=502,
                    retryable=True,
                )

            parts = candidates[0].get("content", {}).get("parts", [])
            text_parts = [p.get("text", "") for p in parts if isinstance(p, dict) and "text" in p]
            reply_text = "\n\n".join(text_parts).strip()
            if not reply_text:
                raise ProviderException(
                    provider_name=self.provider_name,
                    code=ProviderErrorCode.INVALID_REQUEST,
                    message="Empty response content returned from Gemini.",
                    status_code=502,
                    retryable=True,
                )

            finish_reason = candidates[0].get("finishReason")
            usage = data.get("usageMetadata", {})

            return LLMGenerationResult(
                reply_text=reply_text,
                provider_name=self.provider_name,
                model_name=self._model,
                finish_reason=finish_reason,
                prompt_tokens=usage.get("promptTokenCount"),
                completion_tokens=usage.get("candidatesTokenCount"),
                total_tokens=usage.get("totalTokenCount"),
            )

        except httpx.TimeoutException:
            logger.error(f"Gemini API request timed out for model {self._model}")
            raise ProviderException(
                provider_name=self.provider_name,
                code=ProviderErrorCode.TIMEOUT,
                message="Gemini request timed out.",
                status_code=504,
                retryable=True,
            )
        except httpx.RequestError as exc:
            logger.error(f"Network error contacting Gemini API: {type(exc).__name__}")
            raise ProviderException(
                provider_name=self.provider_name,
                code=ProviderErrorCode.TEMPORARY_OUTAGE,
                message=f"Network error connecting to Gemini: {type(exc).__name__}",
                status_code=502,
                retryable=True,
            )
