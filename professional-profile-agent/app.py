#!/usr/bin/env python3
"""Gradio app entry point for the professional profile agent."""

import logging
import os

import gradio as gr
from dotenv import load_dotenv

from src.agent import ProfileAgent

logging.basicConfig(level=logging.INFO)
load_dotenv(override=True)


def create_app() -> gr.ChatInterface:
    agent = ProfileAgent.from_env()
    title = f"Chat with {agent.profile.name}"
    description = (
        "Ask about career background, skills, and experience. "
        "Responses are evaluated for accuracy and professionalism before delivery. "
        "Unknown questions and contact details are recorded via Pushover notifications."
    )
    return gr.ChatInterface(
        fn=agent.chat,
        title=title,
        description=description,
        examples=[
            "What is your current role at Meta?",
            "Tell me about your experience at Goldman Sachs.",
            "What machine learning skills do you have?",
        ],
    )


def main() -> None:
    share = os.getenv("GRADIO_SHARE", "false").lower() in ("1", "true", "yes")
    demo = create_app()
    demo.launch(share=share)


if __name__ == "__main__":
    main()
