"""SendGrid-backed email delivery tools."""

from __future__ import annotations

import logging

import sendgrid
from agents import function_tool
from sendgrid.helpers.mail import Content, Email, Mail, To

from ..config import Settings

logger = logging.getLogger(__name__)


class EmailDeliveryService:
    """
    Wraps SendGrid operations as agent tools.

    Separates transport from agent logic so delivery can be dry-run tested
    without changing agent prompts.
    """

    def __init__(self, settings: Settings):
        self._settings = settings

    def _send(
        self,
        subject: str,
        body: str,
        *,
        content_type: str,
    ) -> int:
        self._settings.require_sendgrid()

        if self._settings.dry_run:
            logger.info(
                "DRY RUN email | subject=%r | to=%s | bytes=%d",
                subject,
                self._settings.to_email,
                len(body),
            )
            return 202

        client = sendgrid.SendGridAPIClient(api_key=self._settings.sendgrid_api_key)
        mail = Mail(
            Email(self._settings.from_email),
            To(self._settings.to_email),
            subject,
            Content(content_type, body),
        ).get()
        response = client.client.mail.send.post(request_body=mail)
        status = response.status_code

        if status >= 400:
            raise RuntimeError(f"SendGrid returned HTTP {status}")

        return status

    def plain_text_tool(self):
        @function_tool
        def send_email(email: str) -> str:
            """Send a plain-text sales email body to the configured recipient."""
            status = self._send("Cold sales email", email, content_type="text/plain")
            return f"Email sent successfully (HTTP {status})."

        return send_email

    def html_tool(self):
        @function_tool
        def send_html_email(subject_line: str, html_body: str) -> str:
            """Send an HTML email with the given subject line and body."""
            if not subject_line.strip():
                raise ValueError("subject_line must not be empty")
            if not html_body.strip():
                raise ValueError("html_body must not be empty")

            status = self._send(
                subject_line.strip(),
                html_body,
                content_type="text/html",
            )
            return f"HTML email sent successfully (HTTP {status})."

        return send_html_email
