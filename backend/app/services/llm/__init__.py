"""
LLM Provider and Failover package for SmartLearn.AI.
"""

from app.services.llm.base import (
    BaseLLMProvider,
    LLMGenerationResult,
    ProviderErrorCode,
    ProviderException,
)
from app.services.llm.gemini_provider import GeminiProvider
from app.services.llm.groq_provider import GroqProvider
from app.services.llm.openrouter_provider import OpenRouterProvider
from app.services.llm.failover_service import LLMFailoverService

__all__ = [
    "BaseLLMProvider",
    "LLMGenerationResult",
    "ProviderErrorCode",
    "ProviderException",
    "GeminiProvider",
    "GroqProvider",
    "OpenRouterProvider",
    "LLMFailoverService",
]
