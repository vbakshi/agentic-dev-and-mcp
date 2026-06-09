"""Email formatting and delivery agent pipeline."""

from __future__ import annotations

from agents import Agent, Runner, function_tool
from agents.items import ItemHelpers
from agents.run_context import RunContextWrapper

from ..config import Settings
from ..prompts import (
    EMAILER_INSTRUCTIONS,
    HTML_CONVERTER_INSTRUCTIONS,
    SUBJECT_LINE_INSTRUCTIONS,
)
from ..tools.email import EmailDeliveryService
from ..validation import strip_embedded_subject_line


class EmailerPipeline:
    """
    Builds the Emailer Agent and its sub-tools.

    Architecture:
    - Subject Line Agent (tool): body-only text -> subject
    - HTML Converter Agent (tool): body-only text -> HTML
    - send_html_email (tool): subject + HTML -> SendGrid
    - Emailer Agent orchestrates the three tools in sequence

    Both sub-agent tools strip any leading ``Subject:`` line before invocation
    so writer-included subjects cannot anchor the subject specialist.
    """

    def __init__(self, settings: Settings, delivery: EmailDeliveryService):
        self._settings = settings
        self._delivery = delivery
        self._subject_agent = Agent(
            name="Subject Line Agent",
            instructions=SUBJECT_LINE_INSTRUCTIONS,
            model=self._settings.agent_model,
        )
        self._html_agent = Agent(
            name="HTML Converter Agent",
            instructions=HTML_CONVERTER_INSTRUCTIONS,
            model=self._settings.agent_model,
        )

    def _subject_line_tool(self):
        agent = self._subject_agent

        @function_tool(
            name_override="generate_subject_line",
            description_override=(
                "Generate an attention-grabbing subject line from a plain-text email body. "
                "Pass body-only text (no subject line)."
            ),
        )
        async def generate_subject_line(
            context: RunContextWrapper, email_body: str
        ) -> str:
            body = strip_embedded_subject_line(email_body)
            result = await Runner.run(
                starting_agent=agent,
                input=body,
                context=context.context,
            )
            return ItemHelpers.text_message_outputs(result.new_items)

        return generate_subject_line

    def _html_converter_tool(self):
        agent = self._html_agent

        @function_tool(
            name_override="convert_to_html",
            description_override=(
                "Convert a plain-text email body into simple HTML. "
                "Pass body-only text (no subject line)."
            ),
        )
        async def convert_to_html(context: RunContextWrapper, email_body: str) -> str:
            body = strip_embedded_subject_line(email_body)
            result = await Runner.run(
                starting_agent=agent,
                input=body,
                context=context.context,
            )
            return ItemHelpers.text_message_outputs(result.new_items)

        return convert_to_html

    def build_agent(self) -> Agent:
        return Agent(
            name="Emailer Agent",
            instructions=EMAILER_INSTRUCTIONS,
            model=self._settings.agent_model,
            tools=[
                self._subject_line_tool(),
                self._html_converter_tool(),
                self._delivery.html_tool(),
            ],
            handoff_description=(
                "Format the winning sales email body (subject line, HTML) and send it."
            ),
        )
