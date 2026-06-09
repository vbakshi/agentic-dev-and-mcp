"""End-to-end sales campaign orchestration workflow."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from agents import Agent, Runner, trace

from ..agents import EmailerPipeline, SalesManagerFactory, SalesWriterPool
from ..config import Settings, load_project_env
from ..output import save_workflow_result
from ..tools import EmailDeliveryService

logger = logging.getLogger(__name__)

DEFAULT_CAMPAIGN_BRIEF = (
    "Send a cold sales email from Alice at ComplAI. "
    "Address the recipient as 'Dear CEO' and focus on SOC2 audit preparation."
)


@dataclass
class WorkflowRunResult:
    """Structured result from a sales campaign run."""

    user_request: str
    final_output: str
    trace_name: str
    dry_run: bool
    output_file: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)


class SalesCampaignWorkflow:
    """
    Orchestrates the full Sales Manager -> writers (tools) -> Emailer (handoff) flow.

    Build order (dependency injection):
    1. Settings — env-backed configuration
    2. EmailDeliveryService — SendGrid tools
    3. SalesWriterPool — four validated writer tools
    4. EmailerPipeline — subject/HTML/send sub-agents
    5. SalesManagerFactory — top-level agent with tools + handoff
    """

    def __init__(self, settings: Settings | None = None):
        load_project_env()
        self.settings = settings or Settings.from_env(load_env=False)
        self.settings.require_sendgrid()

        delivery = EmailDeliveryService(self.settings)
        writers = SalesWriterPool(self.settings)
        emailer = EmailerPipeline(self.settings, delivery)
        self.manager: Agent = SalesManagerFactory(
            self.settings, writers, emailer
        ).build()

    async def run(
        self,
        user_request: str = DEFAULT_CAMPAIGN_BRIEF,
        *,
        trace_name: str = "Sales Campaign Workflow",
        save_output: bool = True,
    ) -> WorkflowRunResult:
        logger.info("Starting workflow | dry_run=%s", self.settings.dry_run)

        with trace(trace_name):
            run_result = await Runner.run(self.manager, user_request)

        payload = {
            "user_request": user_request,
            "final_output": run_result.final_output,
            "trace_name": trace_name,
            "dry_run": self.settings.dry_run,
            "agent_model": self.settings.agent_model,
        }

        output_file = None
        if save_output:
            path = save_workflow_result(
                payload,
                output_dir=self.settings.output_dir,
                max_files=self.settings.max_output_files,
            )
            output_file = str(path)
            logger.info("Saved workflow result to %s", path)

        return WorkflowRunResult(
            user_request=user_request,
            final_output=str(run_result.final_output),
            trace_name=trace_name,
            dry_run=self.settings.dry_run,
            output_file=output_file,
            raw=payload,
        )
