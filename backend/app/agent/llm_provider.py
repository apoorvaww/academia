import os
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from app.config import GEMINI_API_KEY, GEMINI_MODEL

logger = logging.getLogger(__name__)

class BaseLLMProvider(ABC):
    @abstractmethod
    def generate_step(self, system_prompt: str, user_prompt: str) -> str:
        """Generates raw text response for a ReAct reasoning step."""
        pass

class GeminiProvider(BaseLLMProvider):
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or GEMINI_API_KEY
        self.model_name = model or GEMINI_MODEL
        self._client = None
        if self.api_key:
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize google-genai Client: {e}")

    def generate_step(self, system_prompt: str, user_prompt: str) -> str:
        if not self._client:
            raise RuntimeError("Gemini Client is not configured. Set GEMINI_API_KEY.")
        
        full_content = f"{system_prompt}\n\nUser Question:\n{user_prompt}"
        response = self._client.models.generate_content(
            model=self.model_name,
            contents=full_content
        )
        return response.text or ""

class DeterministicReActProvider(BaseLLMProvider):
    """
    Deterministic rule-based ReAct engine that ensures the agent completes multi-step
    career advisory workflows reliably even without an external API key or network connection.
    """
    def generate_step(self, system_prompt: str, user_prompt: str) -> str:
        # This fallback operates within the ReAct agent runner directly
        return ""

def get_llm_provider() -> BaseLLMProvider:
    """Returns GeminiProvider if API key is present, otherwise DeterministicReActProvider."""
    if GEMINI_API_KEY and len(GEMINI_API_KEY.strip()) > 5:
        try:
            provider = GeminiProvider()
            if provider._client:
                return provider
        except Exception as e:
            logger.warning(f"Error initializing GeminiProvider: {e}. Falling back to deterministic provider.")
    return DeterministicReActProvider()
