"""Sales writer agent definitions and validated writer tools."""

from __future__ import annotations

from dataclasses import dataclass

from agents import Agent, Runner, function_tool
from agents.items import ItemHelpers
from agents.run_context import RunContextWrapper

from ..config import Settings
from ..prompts import SALES_WRITER_PROMPTS, SALES_WRITER_TOOL_DESCRIPTION
from ..validation import BriefValidationError, validate_writer_brief


@dataclass(frozen=True)
class SalesWriterSpec:
    key: str
    name: str
    tool_name: str


WRITER_SPECS: tuple[SalesWriterSpec, ...] = (
    SalesWriterSpec("professional", "Professional Sales Agent", "sales_agent_professional"),
    SalesWriterSpec("humorous", "Humorous Sales Agent", "sales_agent_humorous"),
    SalesWriterSpec("concise", "Concise Sales Agent", "sales_agent_concise"),
    SalesWriterSpec("friendly", "Friendly Sales Agent", "sales_agent_friendly"),
)


class SalesWriterPool:
    """
    Factory for the four style-specialized writer agents.

    Each writer is exposed as a tool with a `brief` parameter (not `input`) and
    server-side validation so the manager cannot pass draft emails by mistake.
    """

    def __init__(self, settings: Settings):
        self._settings = settings
        self.agents = self._build_agents()

    def _build_agents(self) -> dict[str, Agent]:
        return {
            spec.key: Agent(
                name=spec.name,
                instructions=SALES_WRITER_PROMPTS[spec.key],
                model=self._settings.agent_model,
            )
            for spec in WRITER_SPECS
        }

    def _writer_tool(self, spec: SalesWriterSpec):
        agent = self.agents[spec.key]

        @function_tool(
            name_override=spec.tool_name,
            description_override=(
                f"{SALES_WRITER_TOOL_DESCRIPTION} Style: {spec.key}."
            ),
        )
        async def run_writer(context: RunContextWrapper, brief: str) -> str:
            try:
                validated_brief = validate_writer_brief(brief)
            except BriefValidationError as exc:
                return f"TOOL ERROR: {exc}"

            result = await Runner.run(
                starting_agent=agent,
                input=validated_brief,
                context=context.context,
            )
            return ItemHelpers.text_message_outputs(result.new_items)

        return run_writer

    def tools(self):
        return [self._writer_tool(spec) for spec in WRITER_SPECS]
