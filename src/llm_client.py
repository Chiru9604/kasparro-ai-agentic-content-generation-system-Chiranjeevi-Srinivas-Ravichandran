import json
import time
import random
import logging
from typing import Any, Dict

from groq import Groq, APIError, RateLimitError
from .config import get_settings


class LLMClient:
    """
    Thin wrapper around Groq's chat completions with basic resiliency.
    """

    MAX_RETRIES: int = 3
    RETRY_BACKOFF: float = 2.0  # seconds multiplier

    def __init__(self):
        settings = get_settings()
        self.client = Groq(api_key=settings.groq_api_key)
        self.model_name = settings.model_name
        self.temperature = settings.model_temperature
        self.logger = logging.getLogger(self.__class__.__name__)

    # ------------------------------------------------------------------
    # Core helpers
    # ------------------------------------------------------------------
    def _chat_completion(self, system_prompt: str, user_prompt: str) -> str:
        """Invoke the Groq chat completion endpoint with retries."""
        attempt = 0
        while True:
            attempt += 1
            try:
                resp = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=self.temperature,
                    # If Groq complains about this, comment out response_format
                    response_format={"type": "json_object"},
                )
                return resp.choices[0].message.content
            except (RateLimitError, APIError) as exc:
                self.logger.warning("LLM call failed (attempt %d/%d): %s", attempt, self.MAX_RETRIES, exc)
                if attempt >= self.MAX_RETRIES:
                    raise
                # jittered exponential backoff
                wait = (self.RETRY_BACKOFF ** (attempt - 1)) * (1 + random.random())
                time.sleep(wait)
            except Exception as exc:
                # Don't retry on other errors (e.g. AuthenticationError, BadRequestError)
                self.logger.error("LLM call failed with fatal error: %s", exc)
                raise

    def call(self, system_prompt: str, user_prompt: str) -> str:  # noqa: D401
        return self._chat_completion(system_prompt, user_prompt)

    def call_and_parse_json(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        text = self.call(system_prompt, user_prompt)
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            self.logger.error("Failed to decode JSON from LLM: %s", exc)
            raise

