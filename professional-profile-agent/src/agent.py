"""Profile chat agent with tool calling and per-response evaluation."""

import logging
import os
from dataclasses import dataclass, field

from openai import OpenAI

from .evaluator import Evaluation, ResponseEvaluator
from .profile import ProfileContext, load_profile
from .prompts import build_agent_system_prompt, build_rerun_system_prompt
from .tools import TOOL_DEFINITIONS, handle_tool_calls

logger = logging.getLogger(__name__)


@dataclass
class ChatResult:
    reply: str
    evaluation: Evaluation | None = None
    retried: bool = False


@dataclass
class ProfileAgent:
    """Career profile agent with Pushover tools and response evaluation."""

    profile: ProfileContext
    agent_model: str = field(default_factory=lambda: os.getenv("AGENT_MODEL", "gpt-4o-mini"))
    max_tokens: int = 1000
    evaluate_responses: bool = True

    def __post_init__(self) -> None:
        self._openai = OpenAI()
        self._system_prompt = build_agent_system_prompt(self.profile)
        self._evaluator = ResponseEvaluator(self.profile) if self.evaluate_responses else None

    @classmethod
    def from_env(cls, data_dir=None, **kwargs) -> "ProfileAgent":
        name = os.getenv("PROFILE_NAME")
        profile = load_profile(data_dir=data_dir, name=name)
        return cls(profile=profile, **kwargs)

    def _run_agent_loop(
        self,
        messages: list[dict],
    ) -> str:
        """Run the agent with tool-call loop until a text response is ready."""
        working = list(messages)

        while True:
            response = self._openai.chat.completions.create(
                model=self.agent_model,
                messages=working,
                max_tokens=self.max_tokens,
                tools=TOOL_DEFINITIONS,
            )
            choice = response.choices[0]

            if choice.finish_reason == "tool_calls":
                assistant_message = choice.message
                tool_results = handle_tool_calls(assistant_message.tool_calls)
                working.append(assistant_message)
                working.extend(tool_results)
                continue

            return choice.message.content or ""

    def _generate_reply(
        self,
        message: str,
        history: list[dict],
        system_prompt: str | None = None,
    ) -> str:
        system = system_prompt or self._system_prompt
        messages = [{"role": "system", "content": system}] + history + [
            {"role": "user", "content": message}
        ]
        return self._run_agent_loop(messages)

    def chat(self, message: str, history: list[dict]) -> str:
        """Gradio-compatible chat handler. Returns evaluated (and possibly retried) reply."""
        result = self.respond(message, history)
        return result.reply

    def respond(self, message: str, history: list[dict]) -> ChatResult:
        """Generate a reply with optional evaluation and one retry on failure."""
        reply = self._generate_reply(message, history)
        evaluation = None
        retried = False

        if not self._evaluator:
            return ChatResult(reply=reply)

        evaluation = self._evaluator.evaluate(reply, message, history)

        if evaluation.is_accurate:
            logger.info("Response passed evaluation")
            return ChatResult(reply=reply, evaluation=evaluation)

        logger.info("Response failed evaluation: %s", evaluation.feedback)
        rerun_prompt = build_rerun_system_prompt(
            self._system_prompt, reply, evaluation.feedback
        )
        reply = self._generate_reply(message, history, system_prompt=rerun_prompt)
        retried = True

        return ChatResult(reply=reply, evaluation=evaluation, retried=retried)
