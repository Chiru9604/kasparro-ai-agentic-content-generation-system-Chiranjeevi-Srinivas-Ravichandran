"""Centralized application settings using Pydantic BaseSettings."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import List, Any

from pydantic import Field, field_validator, ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Load variables early so BaseSettings picks them up
load_dotenv()


class Settings(BaseSettings):
    """Application settings.

    Environment variables are automatically parsed; defaults supplied
    here are only fallbacks.
    """
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    groq_api_key: str = Field(..., validation_alias="GROQ_API_KEY")
    faq_min_questions: int = Field(15, validation_alias="FAQ_MIN_QUESTIONS")
    faq_max_questions: int = Field(15, validation_alias="FAQ_MAX_QUESTIONS")
    log_level: str = Field("INFO", validation_alias="LOG_LEVEL")

    # LLM configuration
    model_name: str = Field("llama-3.3-70b-versatile", validation_alias="MODEL_NAME")
    model_temperature: float = Field(0.4, validation_alias="MODEL_TEMPERATURE")
    
    # Input/Output configuration
    input_path: str = Field("input/product_input.json", validation_alias="INPUT_PATH")

    @field_validator("faq_max_questions")
    @classmethod
    def _max_gte_min(cls, v: int, info: ValidationInfo):  # noqa: D401
        if "faq_min_questions" in info.data and v < info.data["faq_min_questions"]:
            raise ValueError("FAQ_MAX_QUESTIONS must be >= FAQ_MIN_QUESTIONS")
        return v


@lru_cache()
def get_settings() -> Settings:  # noqa: D401
    """Return a cached Settings instance."""

    return Settings()