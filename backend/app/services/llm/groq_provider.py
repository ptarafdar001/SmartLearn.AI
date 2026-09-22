"""
Groq LLM Provider implementation for SmartLearn.AI.
High-throughput inference with LPU acceleration, OpenAI API compatibility,
and explicit separation of text and vision models.
"""

from typing import Optional
from app.services.llm.openai_compatible_provider import OpenAICompatibleProvider

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


class GroqProvider(OpenAICompatibleProvider):
    """
    Groq Cloud inference provider.
    Uses Llama 3.3 70B Versatile for deep pedagogical text and Llama 3.2 11B Vision for diagrams.
    """

    def __init__(
        self,
        api_key: Optional[str],
        model: str = "llama-3.3-70b-versatile",
        vision_model: Optional[str] = "llama-3.2-11b-vision-preview",
    ):
        super().__init__(
            provider_name="groq",
            api_base_url=GROQ_API_URL,
            api_key=api_key,
            default_model=model,
            vision_model=vision_model,
            supports_vision_default=bool(vision_model),
        )
