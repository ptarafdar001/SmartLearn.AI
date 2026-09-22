"""
OpenRouter LLM Provider implementation for SmartLearn.AI.
Multi-model aggregator with support for free-tier auto-routing models.
"""

from typing import Optional
from app.services.llm.openai_compatible_provider import OpenAICompatibleProvider

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"


class OpenRouterProvider(OpenAICompatibleProvider):
    """
    OpenRouter inference provider.
    Includes SmartLearn.AI attribution headers as recommended by OpenRouter documentation.
    """

    def __init__(
        self,
        api_key: Optional[str],
        model: str = "openrouter/free",
        vision_model: Optional[str] = None,
    ):
        super().__init__(
            provider_name="openrouter",
            api_base_url=OPENROUTER_API_URL,
            api_key=api_key,
            default_model=model,
            vision_model=vision_model,
            extra_headers={
                "HTTP-Referer": "https://smartlearn.ai",
                "X-Title": "SmartLearn.AI Curriculum Tutor",
            },
            supports_vision_default=bool(vision_model),
        )
