import json
import os
from typing import Any, Dict

from dotenv import load_dotenv
from groq import Groq

load_dotenv()


class LLMClient:
    """
    Thin wrapper around Groq's chat completions.
    We try to use JSON mode so responses are valid JSON.
    """

    def __init__(self, model_name: str = "llama-3.3-70b-versatile"):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY not set in environment or .env")
        self.client = Groq(api_key=api_key)
        self.model_name = model_name

    def call(self, system_prompt: str, user_prompt: str) -> str:
        resp = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.4,
            # If Groq complains about this, comment out response_format
            response_format={"type": "json_object"},
        )
        return resp.choices[0].message.content

    def call_and_parse_json(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        text = self.call(system_prompt, user_prompt)
        return json.loads(text)

