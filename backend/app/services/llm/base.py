"""
Abstract base class and contract definitions for SmartLearn.AI LLM providers.
Provides standardized interfaces for text generation, multimodal vision,
error classification, and health/quota state tracking.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
import re
from typing import Any, Dict, List, Optional
import httpx


class ProviderErrorCode(str, Enum):
    """Standardized error classifications across diverse LLM providers."""
    QUOTA_EXHAUSTED = "QUOTA_EXHAUSTED"          # 429 rate limit or daily quota cap
    TEMPORARY_OUTAGE = "TEMPORARY_OUTAGE"        # 503 high demand, 502 bad gateway, 500
    TIMEOUT = "TIMEOUT"                          # 504 gateway timeout, socket timeout
    AUTH_ERROR = "AUTH_ERROR"                    # 401 invalid key, 403 permission denied
    UNSUPPORTED_MODALITY = "UNSUPPORTED_MODALITY"# Image sent to text-only model
    INVALID_REQUEST = "INVALID_REQUEST"          # 400 bad request, context length exceeded
    CONFIG_ERROR = "CONFIG_ERROR"                # Missing credentials or unsupported model ID


class ProviderException(Exception):
    """Exception raised by provider implementations when an upstream call fails."""

    def __init__(
        self,
        provider_name: str,
        code: ProviderErrorCode,
        message: str,
        status_code: int = 502,
        retryable: bool = False,
        retry_after_seconds: Optional[float] = None,
    ):
        super().__init__(f"[{provider_name}] {code.value}: {message}")
        self.provider_name = provider_name
        self.code = code
        self.message = message
        self.status_code = status_code
        self.retryable = retryable
        self.retry_after_seconds = retry_after_seconds


@dataclass
class LLMGenerationResult:
    """Standardized result returned by all LLM providers."""
    reply_text: str
    provider_name: str
    model_name: str
    finish_reason: Optional[str] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None


class BaseLLMProvider(ABC):
    """Abstract interface for all curriculum AI tutor inference providers."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Unique canonical identifier for the provider (e.g. 'gemini', 'groq')."""
        pass

    @property
    @abstractmethod
    def default_model(self) -> str:
        """Configured default model ID for standard text tutoring."""
        pass

    @property
    @abstractmethod
    def is_configured(self) -> bool:
        """Returns True if the provider has necessary API credentials configured."""
        pass

    @property
    @abstractmethod
    def supports_vision(self) -> bool:
        """Returns True if this provider can process visual image doubts."""
        pass

    @abstractmethod
    def generate(
        self,
        messages: List[Dict[str, str]],
        system_instruction: str,
        image_base64: Optional[str] = None,
        timeout_seconds: float = 30.0,
        client: Optional[httpx.Client] = None,
    ) -> LLMGenerationResult:
        """
        Execute inference for a student question or conversation turn.

        Args:
            messages: List of conversation turns with 'role' ('user'|'assistant') and 'content'.
            system_instruction: Curriculum-grounded pedagogical instructions.
            image_base64: Optional base64-encoded image string (data URI or raw base64).
            timeout_seconds: Request timeout in seconds.
            client: Optional httpx.Client (e.g. for mocked unit testing).

        Returns:
            LLMGenerationResult containing the response text and metadata.

        Raises:
            ProviderException: Categorized upstream failure.
        """
        pass

    @staticmethod
    def sanitize_error_string(raw: str) -> str:
        """Strip raw API keys, bearer tokens, or query param credentials from error strings."""
        sanitized = re.sub(r"key=[a-zA-Z0-9_\-]+", "key=[REDACTED]", raw)
        sanitized = re.sub(r"Bearer\s+[a-zA-Z0-9_\-\.]+", "Bearer [REDACTED]", sanitized)
        sanitized = re.sub(r"gsk_[a-zA-Z0-9_\-]+", "gsk_[REDACTED]", sanitized)
        sanitized = re.sub(r"AIza[a-zA-Z0-9_\-]+", "AIza[REDACTED]", sanitized)
        return sanitized
