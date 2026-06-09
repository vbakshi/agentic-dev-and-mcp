"""Evaluate agent responses before returning them to the user."""

import os
from typing import TYPE_CHECKING

from openai import OpenAI
from pydantic import BaseModel

from .prompts import build_evaluator_system_prompt, build_evaluator_user_prompt
from .profile import ProfileContext

if TYPE_CHECKING:
    pass


class Evaluation(BaseModel):
    is_accurate: bool
    feedback: str


class ResponseEvaluator:
    """Structured evaluator using Gemini (OpenAI-compatible API) or OpenAI fallback."""

    def __init__(
        self,
        profile: ProfileContext,
        model: str | None = None,
    ):
        self.profile = profile
        self.model = model or os.getenv("AGENT_MODEL", "gpt-4o-mini")
        self._client = self._build_client()

    def _build_client(self) -> OpenAI:
        # google_key = os.getenv("GOOGLE_API_KEY")
        
        # if google_key:
        #     return OpenAI(
        #         api_key=google_key,
        #         base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        #     )
        return OpenAI()

    def evaluate(
        self,
        reply: str,
        message: str,
        history: list[dict],
    ) -> Evaluation:
        messages = [
            {"role": "system", "content": build_evaluator_system_prompt(self.profile)},
            {
                "role": "user",
                "content": build_evaluator_user_prompt(reply, message, history),
            },
        ]
        response = self._client.beta.chat.completions.parse(
            model=self.model,
            messages=messages,
            response_format=Evaluation,
        )
        parsed = response.choices[0].message.parsed
        if parsed is None:
            raise ValueError("Evaluator returned no structured response")
        return parsed
