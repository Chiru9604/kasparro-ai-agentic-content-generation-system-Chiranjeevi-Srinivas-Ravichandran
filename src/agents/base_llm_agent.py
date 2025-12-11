from __future__ import annotations

"""Common functionality for agents that invoke the LLM."""

from typing import Any, Dict, Optional
import json
import logging
import time

from pydantic import BaseModel, ValidationError

from ..llm_client import LLMClient

logger = logging.getLogger(__name__)


class BaseLLMAgent:
    """Base class that provides ``call_json`` convenience wrapper."""

    #: Maximum number of times we will retry a JSON parse failure.
    MAX_RETRIES: int = 2
    #: Seconds to wait between retries (exponential backoff multiplier applied).
    RETRY_BACKOFF: float = 1.5

    def __init__(self, llm: Optional[LLMClient] = None):
        # Allow sharing a single LLMClient across agents, but create a fresh
        # one if none is supplied.
        self.llm: LLMClient = llm or LLMClient()

    # ---------------------------------------------------------------------
    # Helper for derived agents
    # ---------------------------------------------------------------------

    def call_json(
        self,
        system_prompt: str,
        user_prompt: str,
        schema: type[BaseModel] | None = None,
    ) -> Dict[str, Any]:
        """Call the LLM, parse as JSON and (optionally) validate against ``schema``.

        If JSON parsing *or* schema validation fails, we retry up to ``MAX_RETRIES``
        with exponential backoff. After that we raise the original error so the
        caller can decide what to do.
        """
        attempt = 0
        while True:
            attempt += 1
            try:
                data = self.llm.call_and_parse_json(system_prompt, user_prompt)
                if schema is not None:
                    # Validate and return the *dict* form so downstream code doesn’t
                    # need to know about Pydantic models yet.
                    return schema.model_validate(data).model_dump()
                return data
            except (json.JSONDecodeError, ValidationError) as exc:
                if attempt > self.MAX_RETRIES:
                    logger.error("LLM returned invalid JSON or failed validation after %d attempts", attempt)
                    raise

                wait = self.RETRY_BACKOFF ** (attempt - 1)
                logger.warning(
                    "LLM response error on attempt %d/%d – retrying in %.1fs: %s",
                    attempt,
                    self.MAX_RETRIES,
                    wait,
                    exc.__class__.__name__,
                )
                time.sleep(wait)

    # Convenience alias so subclasses can do ``self._j``
    _j = call_json
