"""Pytest fixtures and helpers for unit tests."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, Any

import pytest

# Ensure the project root (one level up from tests/) is on sys.path so that
# `import src.*` works when the tests are executed from the project root.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class MockLLM:
    """A minimal stub that mimics the LLMClient interface for unit tests."""

    def __init__(self, response: Dict[str, Any]):
        self._response = response

    def call_and_parse_json(self, system_prompt: str, user_prompt: str):  # noqa: D401
        """Return a pre-baked response regardless of the prompt inputs."""
        return self._response


@pytest.fixture()
def sample_product_dict() -> Dict[str, Any]:
    """Return a representative product dictionary used in multiple tests."""

    return {
        "product_name": "BrightGlow Serum",
        "concentration": "10%",
        "skin_type": ["oily", "combination"],
        "key_ingredients": ["niacinamide", "vitamin C"],
        "benefits": ["brightening", "fade dark spots"],
        "how_to_use": "Apply nightly to cleansed skin.",
        "side_effects": "Mild tingling for sensitive skin.",
        "price": "$25",
    }
