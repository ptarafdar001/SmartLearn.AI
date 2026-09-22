"""
Reusable OpenAI-compatible LLM Provider implementation.
Powers Groq, OpenRouter, Cerebras, and Mistral with unified message schemas,
strict multimodal vision enforcement, and sanitized error mapping.
"""

import base64
import logging
import re
from typing import Any, Dict, List, Optional
import httpx

from app.services.llm.base import (
    BaseLLMProvider,
    LLMGenerationResult,
    ProviderErrorCode,
    ProviderException,
)

logger = logging.getLogger("smartlearn.tutor.openai_compatible")


class OpenAICompatibleProvider(BaseLLMProvider):
    """
    Generic provider for inference endpoints adhering to the OpenAI Chat Completions API.
    """

    def __init__(
        self,
        provider_name: str,
        api_base_url: str,
        api_key: Optional[str],
        default_model: str,
        vision_model: Optional[str] = None,
        extra_headers: Optional[Dict[str, str]] = None,
        supports_vision_default: bool = False,
    ):
        self._provider_name = provider_name
        self._api_base_url = api_base_url
        self._api_key = api_key
        self._default_model = default_model
        self._vision_model = vision_model
        self._extra_headers = extra_headers or {}
        self._supports_vision_flag = supports_vision_default or bool(vision_model)

    @property
    def provider_name(self) -> str:
        return self._provider_name

    @property
    def default_model(self) -> str:
        return self._default_model

    @property
    def is_configured(self) -> bool:
        return bool(self._api_key and self._api_key.strip())

    @property
    def supports_vision(self) -> bool:
        return self._supports_vision_flag

    def _normalize_image_data_uri(self, raw_data: str) -> str:
        """Ensure image string is formatted as a valid data URI for OpenAI-compatible payload."""
        if raw_data.startswith("data:"):
            return raw_data

        # If raw base64, detect mime type or default to image/jpeg
        return f"data:image/jpeg;base64,{raw_data}"

    def _build_messages(
        self,
        messages: List[Dict[str, str]],
        system_instruction: str,
        image_base64: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Construct standard OpenAI messages array."""
        payload_messages: List[Dict[str, Any]] = [
            {"role": "system", "content": system_instruction}
        ]

        # Conversation history
        for turn in messages[:-1] if messages else []:
            role = turn.get("role", "user")
            if role in ["model", "tutor"]:
                role = "assistant"
            elif role == "student":
                role = "user"
            payload_messages.append({"role": role, "content": turn.get("content", "")})

        # Latest message turn
        current_turn = messages[-1] if messages else {"role": "user", "content": ""}
        current_content = current_turn.get("content", "")

        if image_base64:
            data_uri = self._normalize_image_data_uri(image_base64)
            payload_messages.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": current_content},
                    {"type": "image_url", "image_url": {"url": data_uri}},
                ],
            })
        else:
            payload_messages.append({
                "role": "user",
                "content": current_content,
            })

        return payload_messages

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
                message=f"{self.provider_name.capitalize()} API key is not configured in backend environment.",
                status_code=503,
                retryable=False,
            )

        # Vision routing & validation
        chosen_model = self._default_model
        if image_base64:
            if not self.supports_vision:
                raise ProviderException(
                    provider_name=self.provider_name,
                    code=ProviderErrorCode.UNSUPPORTED_MODALITY,
                    message=(
                        f"The configured model '{self._default_model}' on {self.provider_name} "
                        "does not support image attachments. Image questions cannot be silently downgraded."
                    ),
                    status_code=422,
                    retryable=False,
                )
            if self._vision_model:
                chosen_model = self._vision_model

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            **self._extra_headers,
        }

        payload = {
            "model": chosen_model,
            "messages": self._build_messages(messages, system_instruction, image_base64),
            "temperature": 0.7,
            "max_tokens": 2048,
            "top_p": 0.95,
        }

        try:
            if client:
                response = client.post(
                    self._api_base_url,
                    json=payload,
                    headers=headers,
                    timeout=timeout_seconds,
                )
            else:
                with httpx.Client(timeout=timeout_seconds) as http_client:
                    response = http_client.post(
                        self._api_base_url,
                        json=payload,
                        headers=headers,
                    )

            if response is None:
                raise ProviderException(
                    provider_name=self.provider_name,
                    code=ProviderErrorCode.TEMPORARY_OUTAGE,
                    message=f"Failed to receive response from {self.provider_name}.",
                    status_code=502,
                    retryable=True,
                )

            # Handle 429 Quota Exhaustion
            if response.status_code == 429:
                err_text = self.sanitize_error_string(response.text)
                logger.warning(f"{self.provider_name} rate limit or quota exceeded (429): {err_text[:180]}")
                retry_after_hdr = response.headers.get("retry-after")
                retry_after_sec = float(retry_after_hdr) if retry_after_hdr and retry_after_hdr.isdigit() else 30.0

                raise ProviderException(
                    provider_name=self.provider_name,
                    code=ProviderErrorCode.QUOTA_EXHAUSTED,
                    message=f"{self.provider_name} rate limit or daily quota exhausted.",
                    status_code=429,
                    retryable=True,
                    retry_after_seconds=retry_after_sec,
                )

            # Handle Auth Failures
            if response.status_code in [401, 403]:
                err_text = self.sanitize_error_string(response.text)
                logger.error(f"{self.provider_name} authentication failed ({response.status_code}): {err_text[:180]}")
                raise ProviderException(
                    provider_name=self.provider_name,
                    code=ProviderErrorCode.AUTH_ERROR,
                    message=f"{self.provider_name} authentication rejected. Please check API key.",
                    status_code=503,
                    retryable=False,
                )

            # Handle Unsupported Model / Modality
            if response.status_code == 400:
                err_body = response.text
                sanitized_err = self.sanitize_error_string(err_body)
                if "vision" in err_body.lower() or "image" in err_body.lower():
                    raise ProviderException(
                        provider_name=self.provider_name,
                        code=ProviderErrorCode.UNSUPPORTED_MODALITY,
                        message=f"{self.provider_name} model does not support image input: {sanitized_err[:180]}",
                        status_code=422,
                        retryable=False,
                    )
                raise ProviderException(
                    provider_name=self.provider_name,
                    code=ProviderErrorCode.INVALID_REQUEST,
                    message=f"{self.provider_name} invalid request: {sanitized_err[:180]}",
                    status_code=400,
                    retryable=False,
                )

            # Handle Temporary Service Outages
            if response.status_code in [500, 502, 503]:
                logger.warning(f"{self.provider_name} temporary outage ({response.status_code})")
                raise ProviderException(
                    provider_name=self.provider_name,
                    code=ProviderErrorCode.TEMPORARY_OUTAGE,
                    message=f"{self.provider_name} upstream service error ({response.status_code}).",
                    status_code=503,
                    retryable=True,
                    retry_after_seconds=5.0,
                )

            if response.status_code != 200:
                err_text = self.sanitize_error_string(response.text)
                logger.error(f"{self.provider_name} unexpected HTTP {response.status_code}: {err_text[:200]}")
                raise ProviderException(
                    provider_name=self.provider_name,
                    code=ProviderErrorCode.TEMPORARY_OUTAGE,
                    message=f"{self.provider_name} request failed with status {response.status_code}.",
                    status_code=response.status_code,
                    retryable=True,
                )

            data = response.json()
            choices = data.get("choices", [])
            if not choices:
                raise ProviderException(
                    provider_name=self.provider_name,
                    code=ProviderErrorCode.INVALID_REQUEST,
                    message=f"{self.provider_name} returned empty choices.",
                    status_code=502,
                    retryable=True,
                )

            first_choice = choices[0]
            message_obj = first_choice.get("message", {})
            reply_text = message_obj.get("content", "").strip()

            if not reply_text:
                raise ProviderException(
                    provider_name=self.provider_name,
                    code=ProviderErrorCode.INVALID_REQUEST,
                    message=f"{self.provider_name} returned empty reply content.",
                    status_code=502,
                    retryable=True,
                )

            usage = data.get("usage", {})

            return LLMGenerationResult(
                reply_text=reply_text,
                provider_name=self.provider_name,
                model_name=chosen_model,
                finish_reason=first_choice.get("finish_reason"),
                prompt_tokens=usage.get("prompt_tokens"),
                completion_tokens=usage.get("completion_tokens"),
                total_tokens=usage.get("total_tokens"),
            )

        except httpx.TimeoutException:
            logger.error(f"{self.provider_name} request timed out for model {chosen_model}")
            raise ProviderException(
                provider_name=self.provider_name,
                code=ProviderErrorCode.TIMEOUT,
                message=f"{self.provider_name} request timed out.",
                status_code=504,
                retryable=True,
            )
        except httpx.RequestError as exc:
            logger.error(f"Network error contacting {self.provider_name}: {type(exc).__name__}")
            raise ProviderException(
                provider_name=self.provider_name,
                code=ProviderErrorCode.TEMPORARY_OUTAGE,
                message=f"Network error connecting to {self.provider_name}: {type(exc).__name__}",
                status_code=502,
                retryable=True,
            )
