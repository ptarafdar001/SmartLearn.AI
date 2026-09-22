"""
Production-conscious, quota-aware multi-provider AI failover orchestrator for SmartLearn.AI.
Manages provider order, health tracking, cooldowns on 429/503, circuit-breaking,
and strict multimodal vision routing.
"""

from datetime import datetime, timezone
import logging
import time
from typing import Any, Dict, List, Optional
from fastapi import HTTPException, status
import httpx

from app.core.config import get_settings
from app.services.llm.base import (
    BaseLLMProvider,
    LLMGenerationResult,
    ProviderErrorCode,
    ProviderException,
)
from app.services.llm.gemini_provider import GeminiProvider
from app.services.llm.groq_provider import GroqProvider
from app.services.llm.openrouter_provider import OpenRouterProvider

logger = logging.getLogger("smartlearn.tutor.failover")
settings = get_settings()


class ProviderHealthRecord:
    """Tracks runtime operational state and cooldowns for an individual provider."""

    def __init__(self, name: str):
        self.name = name
        self.consecutive_failures = 0
        self.last_failure_code: Optional[ProviderErrorCode] = None
        self.last_failure_time: Optional[float] = None
        self.cooldown_until: float = 0.0
        self.auth_disabled: bool = False

    def is_available(self) -> bool:
        """Returns True if the provider is not disabled by bad auth and not in cooldown."""
        if self.auth_disabled:
            return False
        return time.time() >= self.cooldown_until

    def mark_success(self) -> None:
        """Reset consecutive failures upon successful inference."""
        self.consecutive_failures = 0
        self.last_failure_code = None

    def mark_failure(
        self,
        code: ProviderErrorCode,
        cooldown_seconds: float = 30.0,
    ) -> None:
        """Record failure and set temporary backoff cooldown."""
        self.consecutive_failures += 1
        self.last_failure_code = code
        self.last_failure_time = time.time()
        self.cooldown_until = time.time() + cooldown_seconds
        if code == ProviderErrorCode.AUTH_ERROR:
            self.auth_disabled = True


class LLMFailoverService:
    """
    Orchestrates resilient, ordered AI provider inference with health awareness.
    """

    _providers: Dict[str, BaseLLMProvider] = {}
    _health_tracker: Dict[str, ProviderHealthRecord] = {}

    @classmethod
    def initialize_providers(cls) -> None:
        """Instantiate configured providers based on active application settings."""
        current_settings = get_settings()
        cls._providers = {
            "gemini": GeminiProvider(
                api_key=current_settings.GEMINI_API_KEY,
                model=current_settings.AI_TUTOR_MODEL,
            ),
            "groq": GroqProvider(
                api_key=getattr(current_settings, "GROQ_API_KEY", None),
                model=getattr(current_settings, "GROQ_MODEL", "llama-3.3-70b-versatile"),
                vision_model=getattr(current_settings, "GROQ_VISION_MODEL", "llama-3.2-11b-vision-preview"),
            ),
            "openrouter": OpenRouterProvider(
                api_key=getattr(current_settings, "OPENROUTER_API_KEY", None),
                model=getattr(current_settings, "OPENROUTER_MODEL", "openrouter/free"),
                vision_model=None,
            ),
        }

        for name in cls._providers:
            if name not in cls._health_tracker:
                cls._health_tracker[name] = ProviderHealthRecord(name)

    @classmethod
    def get_configured_providers(cls) -> List[str]:
        """Return list of provider names that currently have active API credentials."""
        cls.initialize_providers()
        return [name for name, p in cls._providers.items() if p.is_configured]

    @classmethod
    def get_health_status(cls) -> Dict[str, Dict[str, Any]]:
        """Return sanitized operational health snapshot for monitoring."""
        cls.initialize_providers()
        now = time.time()
        status_map = {}
        for name, provider in cls._providers.items():
            record = cls._health_tracker[name]
            in_cooldown = now < record.cooldown_until
            remaining_cooldown = max(0.0, record.cooldown_until - now) if in_cooldown else 0.0

            status_map[name] = {
                "configured": provider.is_configured,
                "supports_vision": provider.supports_vision,
                "default_model": provider.default_model,
                "healthy": record.is_available(),
                "in_cooldown": in_cooldown,
                "cooldown_remaining_seconds": round(remaining_cooldown, 1),
                "consecutive_failures": record.consecutive_failures,
                "last_failure_code": record.last_failure_code.value if record.last_failure_code else None,
                "auth_disabled": record.auth_disabled,
            }
        return status_map

    @classmethod
    def reset_provider_health(cls, provider_name: Optional[str] = None) -> None:
        """Reset cooldowns and health records (useful in tests or admin maintenance)."""
        if provider_name and provider_name in cls._health_tracker:
            cls._health_tracker[provider_name] = ProviderHealthRecord(provider_name)
        else:
            cls._health_tracker = {name: ProviderHealthRecord(name) for name in cls._providers}

    @classmethod
    def execute_with_failover(
        cls,
        messages: List[Dict[str, str]],
        system_instruction: str,
        image_base64: Optional[str] = None,
        timeout_seconds: float = 30.0,
        client: Optional[httpx.Client] = None,
        override_provider: Optional[str] = None,
    ) -> LLMGenerationResult:
        """
        Execute LLM inference through configured providers in order, failing over
        only upon legitimate quota exhaustion (429), outages (503/502), or timeouts (504).
        """
        cls.initialize_providers()
        current_settings = get_settings()

        # Determine target provider list
        order_str = getattr(current_settings, "AI_TUTOR_PROVIDER_ORDER", "gemini,groq,openrouter")
        configured_order = [p.strip().lower() for p in order_str.split(",") if p.strip()]

        if override_provider:
            configured_order = [override_provider.lower()]

        # Filter down to known, configured providers
        available_providers: List[BaseLLMProvider] = []
        for name in configured_order:
            provider = cls._providers.get(name)
            if provider and provider.is_configured:
                available_providers.append(provider)

        if not available_providers:
            logger.error("No AI Tutor providers are configured with valid API credentials.")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI Tutor service is not configured. GEMINI_API_KEY is required in the backend environment.",
            )

        # Modality check: If image is present, only consider vision-capable providers
        has_image = bool(image_base64 and image_base64.strip())
        if has_image:
            vision_providers = [p for p in available_providers if p.supports_vision]
            if not vision_providers:
                logger.warning("Image doubt requested, but no configured provider supports visual reasoning.")
                raise HTTPException(
                    status_code=422,
                    detail=(
                        "Visual doubt solving with images is currently unavailable on configured AI providers. "
                        "Please submit your question as text or configure a vision-capable provider."
                    ),
                )
            target_candidates = vision_providers
        else:
            target_candidates = available_providers

        # Attempt inference through candidate providers in priority order
        last_exception: Optional[ProviderException] = None
        attempted_count = 0

        for provider in target_candidates:
            health = cls._health_tracker[provider.provider_name]

            # If provider is currently on backoff cooldown, skip to next unless it's the only one
            if not health.is_available() and len(target_candidates) > 1:
                logger.info(
                    f"Skipping provider '{provider.provider_name}' due to active cooldown "
                    f"({health.cooldown_until - time.time():.1f}s remaining, last error: {health.last_failure_code})"
                )
                continue

            attempted_count += 1
            try:
                logger.info(
                    f"Dispatching AI Tutor inference to provider '{provider.provider_name}' "
                    f"(model: {provider.default_model}, has_image: {has_image})..."
                )

                result = provider.generate(
                    messages=messages,
                    system_instruction=system_instruction,
                    image_base64=image_base64,
                    timeout_seconds=timeout_seconds,
                    client=client,
                )

                # Successful inference: update health and return result
                health.mark_success()
                logger.info(
                    f"Successfully generated response via provider '{provider.provider_name}' "
                    f"({len(result.reply_text)} chars)."
                )
                return result

            except ProviderException as exc:
                last_exception = exc
                cooldown = exc.retry_after_seconds if exc.retry_after_seconds else (60.0 if exc.code == ProviderErrorCode.QUOTA_EXHAUSTED else 15.0)
                health.mark_failure(exc.code, cooldown_seconds=cooldown)

                logger.warning(
                    f"Provider '{provider.provider_name}' failed with {exc.code.value}: {exc.message}. "
                    f"Cooldown set to {cooldown}s."
                )

                # If non-retryable failure (e.g. invalid request, auth error), do NOT retry this provider
                if not exc.retryable and exc.code == ProviderErrorCode.AUTH_ERROR:
                    logger.error(f"Provider '{provider.provider_name}' authentication failed. Disabling provider.")

                # If more candidates exist, continue loop to next provider (failover)
                continue

            except Exception as unhandled:
                logger.error(f"Unexpected error in provider '{provider.provider_name}': {type(unhandled).__name__}")
                health.mark_failure(ProviderErrorCode.TEMPORARY_OUTAGE, cooldown_seconds=15.0)
                last_exception = ProviderException(
                    provider_name=provider.provider_name,
                    code=ProviderErrorCode.TEMPORARY_OUTAGE,
                    message="Unexpected internal error during provider inference.",
                    status_code=500,
                    retryable=True,
                )
                continue

        # If all candidate providers failed, provide student-friendly error
        if last_exception:
            if last_exception.code == ProviderErrorCode.QUOTA_EXHAUSTED:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="AI Tutor quota or rate limit exceeded. Please wait a moment before sending another message.",
                )
            if last_exception.code == ProviderErrorCode.TIMEOUT:
                raise HTTPException(
                    status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                    detail="AI Tutor request timed out across available providers. Please try again.",
                )
            if last_exception.code == ProviderErrorCode.AUTH_ERROR:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"AI Tutor authentication failed. Please verify {last_exception.provider_name.upper()}_API_KEY.",
                )
            if last_exception.code == ProviderErrorCode.CONFIG_ERROR:
                raise HTTPException(
                    status_code=last_exception.status_code,
                    detail=f"The configured AI Tutor model is unavailable or not supported ({last_exception.message}).",
                )
            if last_exception.code == ProviderErrorCode.UNSUPPORTED_MODALITY:
                raise HTTPException(
                    status_code=422,
                    detail=last_exception.message,
                )

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The AI Tutor service is temporarily experiencing high demand across all available providers. Please try again in a few moments.",
        )
