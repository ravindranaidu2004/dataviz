"""
Configuration management module for the Data Analysis Agent.
Handles all environment variables and application settings.
"""

import os
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Config:
    """Central configuration class for the application."""

    # ============ Gemini API Configuration ============
    GEMINI_KEYS = [os.getenv(f"gemini_api_{i}") for i in range(1, 11)]
    GEMINI_KEYS = [k for k in GEMINI_KEYS if k]  # Filter out None values

    MODEL_HIERARCHY = [
        "gemini-2.5-pro",
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
    ]

    # ============ LLM Configuration ============
    GOOGLE_MODEL = os.getenv("GOOGLE_MODEL", "gemini-2.5-pro")
    LLM_TEMPERATURE = int(os.getenv("LLM_TEMPERATURE", "0"))
    LLM_TIMEOUT_SECONDS = int(os.getenv("LLM_TIMEOUT_SECONDS", "240"))

    # ============ Code Execution Configuration ============
    CODE_EXECUTION_TIMEOUT = int(os.getenv("CODE_EXECUTION_TIMEOUT", "60"))
    MAX_IMAGE_SIZE_BYTES = int(os.getenv("MAX_IMAGE_SIZE_BYTES", "100000"))
    MAX_RETRIES_PER_KEY = int(os.getenv("MAX_RETRIES_PER_KEY", "2"))

    # ============ Agent Configuration ============
    AGENT_MAX_ITERATIONS = int(os.getenv("AGENT_MAX_ITERATIONS", "3"))
    AGENT_EARLY_STOPPING_METHOD = os.getenv("AGENT_EARLY_STOPPING_METHOD", "generate")

    # ============ Logging Configuration ============
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"

    # ============ Streamlit Configuration ============
    STREAMLIT_LOGGER_LEVEL = os.getenv("STREAMLIT_LOGGER_LEVEL", "info")
    STREAMLIT_CLIENT_REMOUNT_ON_RERUN = (
        os.getenv("STREAMLIT_CLIENT_REMOUNT_ON_RERUN", "false").lower() == "true"
    )
    STREAMLIT_THEME_MODE = os.getenv("STREAMLIT_THEME_MODE", "dark")

    @classmethod
    def validate(cls):
        """Validate that all required configuration is present."""
        if not cls.GEMINI_KEYS:
            raise RuntimeError(
                "No Gemini API keys found. Please set gemini_api_1, gemini_api_2, etc. in your .env file"
            )
        logger.info(f"Loaded {len(cls.GEMINI_KEYS)} Gemini API keys")
        logger.info(f"LLM Timeout: {cls.LLM_TIMEOUT_SECONDS}s")
        logger.info(f"Code Execution Timeout: {cls.CODE_EXECUTION_TIMEOUT}s")


# Validate configuration on import
try:
    Config.validate()
except RuntimeError as e:
    logger.error(str(e))
    raise
