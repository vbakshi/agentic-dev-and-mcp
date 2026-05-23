# Agentic AI Development & MCP

A collection of projects exploring agentic AI patterns and Model Context Protocol (MCP) integrations.

## Projects

| Project | Description |
|---------|-------------|
| [llm-reasoning-benchmark](./llm-reasoning-benchmark/) | Compare reasoning capabilities across different LLMs (GPT, Claude, etc.) using a judge model to rank responses |

## Getting Started

Each project has its own README with setup instructions. Generally:

1. Navigate to the project directory
2. Create a virtual environment: `python -m venv .venv && source .venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and add your API keys
5. Run the project

## Tech Stack

- Python 3.12+
- OpenAI API
- Anthropic API
- Various LLM providers (Gemini, DeepSeek, Groq, Ollama)

---

Built while taking the [Agentic AI course by Ed Donner](https://github.com/ed-donner/agents).
