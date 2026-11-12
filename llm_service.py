"""
LLM Service module for managing Gemini LLM with fallback logic.
Handles API key rotation and model fallback when rate limits are hit.
"""

import time
import logging
from collections import defaultdict
from typing import Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from config import Config

logger = logging.getLogger(__name__)

# Keywords indicating quota exhaustion or rate limiting
QUOTA_KEYWORDS = ["quota", "exceeded", "rate limit", "403", "too many requests"]


class LLMWithFallback:
    """
    LLM wrapper with fallback logic for multiple API keys and models.
    Automatically tries different models and keys when rate limits are hit.
    """

    def __init__(self, keys=None, models=None, temperature=0):
        """Initialize the LLM with fallback wrapper.

        Args:
            keys: List of Gemini API keys to use. Defaults to Config.GEMINI_KEYS
            models: List of models to try. Defaults to Config.MODEL_HIERARCHY
            temperature: Temperature for LLM sampling (0-1)
        """
        self.keys = keys or Config.GEMINI_KEYS
        self.models = models or Config.MODEL_HIERARCHY
        self.temperature = temperature
        self.slow_keys_log = defaultdict(list)
        self.failing_keys_log = defaultdict(int)
        self.current_llm: Optional[ChatGoogleGenerativeAI] = None

        logger.info(
            f"Initialized LLM with {len(self.keys)} keys and {len(self.models)} models"
        )

    def _get_llm_instance(self) -> ChatGoogleGenerativeAI:
        """
        Get an LLM instance, trying different models and keys.
        Falls back to next option if quota/rate limit error is detected.

        Returns:
            ChatGoogleGenerativeAI instance

        Raises:
            RuntimeError: If all models/keys fail
        """
        last_error = None

        for model in self.models:
            for key in self.keys:
                try:
                    logger.debug(f"Trying model {model} with key {key[:10]}...")
                    llm_instance = ChatGoogleGenerativeAI(
                        model=model,
                        temperature=self.temperature,
                        google_api_key=key,
                    )
                    self.current_llm = llm_instance
                    logger.info(f"Successfully initialized LLM with model {model}")
                    return llm_instance

                except Exception as e:
                    last_error = e
                    msg = str(e).lower()

                    # Track slow/failing keys
                    if any(qk in msg for qk in QUOTA_KEYWORDS):
                        self.slow_keys_log[key].append(model)
                        logger.warning(
                            f"Quota issue with {key[:10]} and model {model}: {str(e)[:100]}"
                        )

                    self.failing_keys_log[key] += 1
                    time.sleep(0.5)  # Brief delay before retrying

        # If we get here, all options failed
        error_msg = f"All models/keys failed. Last error: {last_error}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    def bind_tools(self, tools):
        """Bind tools to the LLM for the LangChain agent.

        Args:
            tools: List of LangChain tools

        Returns:
            LLM instance with bound tools
        """
        llm_instance = self._get_llm_instance()
        return llm_instance.bind_tools(tools)

    def invoke(self, prompt):
        """Invoke the LLM with a prompt (compatible with LangChain agent interface).

        Args:
            prompt: The prompt or message to send to the LLM

        Returns:
            LLM response
        """
        llm_instance = self._get_llm_instance()
        return llm_instance.invoke(prompt)

    def get_stats(self) -> dict:
        """Get statistics about LLM usage and failures.

        Returns:
            Dictionary with stats about key performance
        """
        return {
            "slow_keys": dict(self.slow_keys_log),
            "failing_keys": dict(self.failing_keys_log),
            "current_model": self.current_llm.model if self.current_llm else None,
        }


# Global LLM instance (initialized once)
_llm_instance = None


def get_llm() -> LLMWithFallback:
    """Get or create the global LLM instance.

    Returns:
        LLMWithFallback instance
    """
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = LLMWithFallback(temperature=Config.LLM_TEMPERATURE)
    return _llm_instance
