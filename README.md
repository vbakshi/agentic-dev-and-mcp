# Agentic AI Development & MCP

A collection of projects exploring agentic AI patterns and Model Context Protocol (MCP) integrations.

## Projects

| Project | Description |
|---------|-------------|
| [llm-reasoning-benchmark](./llm-reasoning-benchmark/) | Compare reasoning capabilities across different LLMs (GPT, Claude, etc.) using a judge model to rank responses |
| [professional-profile-agent](./professional-profile-agent/) | Gradio career chat agent with resume context, Pushover tools, and per-response evaluation |
| [multi-agent-orchestration](./multi-agent-orchestration/) | Sales campaign workflow: writer agents as tools, Emailer handoff, SendGrid delivery |

## Getting Started

Each project has its own README with setup instructions. Generally:

1. Navigate to the project directory
2. Copy `.env.example` to `.env` and add your API keys
3. Install and run (see project README):
   - **professional-profile-agent:** `uv sync` then `uv run app.py`
   - **llm-reasoning-benchmark:** `python -m venv .venv`, `pip install -r requirements.txt`
   - **multi-agent-orchestration:** `uv sync` then `python main.py --dry-run`

## Tech Stack

- Python 3.12+
- OpenAI API
- Anthropic API
- Various LLM providers (Gemini, DeepSeek, Groq, Ollama)

---

Built while taking the [Agentic AI course by Ed Donner](https://github.com/ed-donner/agents).
