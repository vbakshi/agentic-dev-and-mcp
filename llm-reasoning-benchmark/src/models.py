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


def get_gemini_client() -> OpenAI:
    """Get Gemini client via OpenAI-compatible API."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not set")
    return OpenAI(
        api_key=api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )


def get_deepseek_client() -> OpenAI:
    """Get DeepSeek client via OpenAI-compatible API."""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY not set")
    return OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")


def get_groq_client() -> OpenAI:
    """Get Groq client via OpenAI-compatible API."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not set")
    return OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")


def get_ollama_client() -> OpenAI:
    """Get Ollama client (local) via OpenAI-compatible API."""
    return OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")


PROVIDER_CLIENTS = {
    "openai": get_openai_client,
    "anthropic": get_anthropic_client,
    "gemini": get_gemini_client,
    "deepseek": get_deepseek_client,
    "groq": get_groq_client,
    "ollama": get_ollama_client,
}


def get_model_client(provider: str):
    """Get a model client by provider name."""
    if provider not in PROVIDER_CLIENTS:
        raise ValueError(f"Unknown provider: {provider}. Available: {list(PROVIDER_CLIENTS.keys())}")
    return PROVIDER_CLIENTS[provider]()


def query_model(provider: str, model: str, messages: list[dict]) -> str:
    """Query a model and return the response text."""
    client = get_model_client(provider)
    
    if provider == "anthropic":
        response = client.messages.create(
            model=model,
            messages=messages,
            max_tokens=1000
        )
        return response.content[0].text
    else:
        response = client.chat.completions.create(
            model=model,
            messages=messages
        )
        return response.choices[0].message.content
