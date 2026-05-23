"""Model client configurations for different LLM providers."""

import os
from openai import OpenAI
from anthropic import Anthropic


def get_openai_client() -> OpenAI:
    """Get OpenAI client."""
    return OpenAI()


def get_anthropic_client() -> Anthropic:
    """Get Anthropic client."""
    return Anthropic()


def query_openai(model: str, messages: list[dict]) -> str:
    """Query an OpenAI model."""
    client = get_openai_client()
    response = client.chat.completions.create(model=model, messages=messages)
    return response.choices[0].message.content


def query_anthropic(model: str, messages: list[dict], max_tokens: int = 1000) -> str:
    """Query an Anthropic model."""
    client = get_anthropic_client()
    response = client.messages.create(model=model, messages=messages, max_tokens=max_tokens)
    return response.content[0].text
