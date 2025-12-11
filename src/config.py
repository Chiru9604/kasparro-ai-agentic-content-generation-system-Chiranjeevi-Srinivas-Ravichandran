"""Centralized application settings using Pydantic BaseSettings."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import List, Any

from pydantic import Field, validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load variables early so BaseSettings picks them up
load_dotenv()


class Settings(BaseSettings):
    """Application settings.

    Environment variables are automatically parsed; defaults supplied
    here are only fallbacks.
    """

    groq_api_key: str = Field(..., env="GROQ_API_KEY")
    faq_min_questions: int = Field(15, env="FAQ_MIN_QUESTIONS")
    faq_max_questions: int = Field(15, env="FAQ_MAX_QUESTIONS")
    log_level: str = Field("INFO", env="LOG_LEVEL")

    # LLM configuration
    model_name: str = Field("llama-3.3-70b-versatile", env="MODEL_NAME")
    model_temperature: float = Field(0.4, env="MODEL_TEMPERATURE")
    
    # Input/Output configuration
    input_path: str = Field("input/product_input.json", env="INPUT_PATH")

    class Config:
        env_file = ".env"
        extra = "ignore"

    @validator("faq_max_questions")
    def _max_gte_min(cls, v: int, values: dict[str, Any]):  # noqa: D401
        if "faq_min_questions" in values and v < values["faq_min_questions"]:
            raise ValueError("FAQ_MAX_QUESTIONS must be >= FAQ_MIN_QUESTIONS")
        return v


@lru_cache()
def get_settings() -> Settings:  # noqa: D401
    """Return a cached Settings instance."""

    return Settings()