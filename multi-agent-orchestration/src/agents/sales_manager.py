"""Sales Manager agent with writer tools and emailer handoff."""

from __future__ import annotations

from agents import Agent, handoff
from agents.handoffs import HandoffInputData
from agents.items import HandoffCallItem, HandoffOutputItem
from pydantic import BaseModel, Field

from ..config import Settings
from ..prompts import SALES_MANAGER_INSTRUCTIONS
from ..validation import strip_embedded_subject_line
from .emailer import EmailerPipeline
from .sales_writers import SalesWriterPool


class EmailHandoffPayload(BaseModel):
    """Structured payload for handing a winning draft to the Emailer Agent."""

    email_body: str = Field(
        description="The single winning plain-text sales email draft to format and send."
    )


def _on_email_handoff(_ctx, payload: EmailHandoffPayload) -> None:
    """Validate and normalize handoff input before the Emailer Agent runs."""
    if not payload.email_body.strip():
        raise ValueError("email_body must not be empty")
    payload.email_body = strip_embedded_subject_line(payload.email_body)


def _email_handoff_input_filter(data: HandoffInputData) -> HandoffInputData:
    """
    Give the Emailer Agent a clean context without writer tool-call history.

    Truncating ``new_items`` by count breaks OpenAI's requirement that every
    function_call has a matching function_call_output. We keep only the
    handoff call + handoff output pair (which includes the winning email_body).
    """
    handoff_items = [
        item
        for item in data.new_items
        if isinstance(item, (HandoffCallItem, HandoffOutputItem))
    ]

    if len(handoff_items) < 2:
        # Fall back to unfiltered data if the pair is incomplete
        return data

    return data.clone(
        pre_handoff_items=(),
        new_items=tuple(handoff_items),
    )


class SalesManagerFactory:
    """
    Composes the top-level Sales Manager agent.

    Tools (agents-as-tools): four validated sales writers
    Handoff: Emailer Agent for subject/HTML/send pipeline
    """

    def __init__(
        self,
        settings: Settings,
        writers: SalesWriterPool,
        emailer_pipeline: EmailerPipeline,
    ):
        self._settings = settings
        self._writers = writers
        self._emailer_pipeline = emailer_pipeline

    def build(self) -> Agent:
        emailer = self._emailer_pipeline.build_agent()

        emailer_handoff = handoff(
            agent=emailer,
            tool_name_override="transfer_to_Emailer_Agent",
            tool_description_override=(
                "Hand off exactly one winning plain-text email body (no subject line) "
                "for formatting and delivery. Provide the body in email_body."
            ),
            on_handoff=_on_email_handoff,
            input_type=EmailHandoffPayload,
            input_filter=_email_handoff_input_filter,
        )

        return Agent(
            name="Sales Manager",
            instructions=SALES_MANAGER_INSTRUCTIONS,
            model=self._settings.agent_model,
            tools=self._writers.tools(),
            handoffs=[emailer_handoff],
        )
