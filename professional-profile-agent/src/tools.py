"""Agent tools: Pushover notifications and lead capture."""

import json
import logging
import os
from pathlib import Path
from typing import Any

import requests

logger = logging.getLogger(__name__)

PUSHOVER_URL = "https://api.pushover.net/1/messages.json"
RL_PROJECTS_FILE = Path(__file__).resolve().parent.parent / "data" / "rl_projects_26h1.md"


def push_notification(message: str) -> None:
    """Send a Pushover notification. Logs and skips if credentials are missing."""
    user = os.getenv("PUSHOVER_USER")
    token = os.getenv("PUSHOVER_TOKEN")

    if not user or not token:
        logger.warning("Pushover credentials missing; skipping notification: %s", message)
        return

    payload = {"token": token, "user": user, "message": message}
    response = requests.post(PUSHOVER_URL, data=payload, timeout=10)
    response.raise_for_status()
    logger.info("Pushover notification sent")


def record_user_details(
    email: str,
    name: str = "Not Provided",
    notes: str = "No additional notes",
) -> dict[str, str]:
    push_notification(
        f"New user details received:\nEmail: {email}\nName: {name}\nNotes: {notes}"
    )
    return {"recorded": "ok"}


def record_unknown_question(question: str) -> dict[str, str]:
    push_notification(f"Unknown question received: {question}")
    return {"recorded": "ok"}


def get_reality_labs_context() -> dict[str, str]:
    if not RL_PROJECTS_FILE.exists():
        return {"error": f"Missing context file: {RL_PROJECTS_FILE.name}"}
    return {"context": RL_PROJECTS_FILE.read_text(encoding="utf-8")}


TOOL_DEFINITIONS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "record_user_details",
            "description": "Record the user's contact details when they share email or want to get in touch.",
            "parameters": {
                "type": "object",
                "properties": {
                    "email": {
                        "type": "string",
                        "description": "The user's email address",
                    },
                    "name": {
                        "type": "string",
                        "description": "The user's name",
                    },
                    "notes": {
                        "type": "string",
                        "description": "Any additional notes about the user",
                    },
                },
                "required": ["email"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "record_unknown_question",
            "description": "Record a question the agent could not answer from the profile context.",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The user's question",
                    },
                },
                "required": ["question"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_reality_labs_context",
            "description": (
                "Load detailed H1 2026 Reality Labs (Meta) project context. "
                "Call ONLY when the user asks about Reality Labs, Horizon OS, or Meta VR/MR work experience."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
        },
    },
]


def handle_tool_calls(tool_calls: list) -> list[dict[str, str]]:
    """Execute tool calls and return OpenAI tool result messages."""
    results = []
    for tool_call in tool_calls:
        tool_name = tool_call.function.name
        tool_args = json.loads(tool_call.function.arguments)

        if tool_name == "record_user_details":
            result = record_user_details(**tool_args)
        elif tool_name == "record_unknown_question":
            result = record_unknown_question(**tool_args)
        elif tool_name == "get_reality_labs_context":
            result = get_reality_labs_context()
        else:
            result = {"error": f"Unknown tool: {tool_name}"}

        results.append(
            {
                "role": "tool",
                "content": json.dumps(result),
                "tool_call_id": tool_call.id,
            }
        )
    return results
