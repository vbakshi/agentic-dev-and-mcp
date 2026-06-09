---
title: professional-profile-agent
app_file: app.py
sdk: gradio
sdk_version: 6.14.0
---
# Professional Profile Agent

A deployable Gradio chat agent that represents your professional profile using your resume and summary. Every response is evaluated for accuracy and professionalism before being shown to the user, with automatic retry on failure. The agent can call tools to send **Pushover** notifications when visitors share contact details or ask unknown questions.

## Architecture

```
User message
     │
     ▼
┌─────────────────┐     tools: record_user_details
│  Profile Agent  │            record_unknown_question
│  (GPT-4o-mini)  │──────────────────► Pushover API
└────────┬────────┘
         │ reply
         ▼
┌─────────────────┐
│   Evaluator     │  structured: is_accurate, feedback
│ (Gemini Flash)  │
└────────┬────────┘
         │ if rejected
         ▼
┌─────────────────┐
│  Agent retry    │  revised reply with evaluator feedback
└─────────────────┘
```

## Setup

Install [uv](https://docs.astral.sh/uv/) if needed, then from this directory:

```bash
cd professional-profile-agent
cp .env.example .env
# Add OPENAI_API_KEY, GOOGLE_API_KEY, PUSHOVER_USER, PUSHOVER_TOKEN

uv sync
```

**How `uv sync` works:** uv reads `pyproject.toml` (and `uv.lock` if present), creates a project `.venv` if it does not exist, and installs all dependencies into that virtual environment. You do not need to run `python -m venv` or `pip install` manually.

Replace `data/me/summary.txt` and `data/me/Vinayak-Bakshi-Resume.pdf` with your own profile files, or set `PROFILE_NAME` in `.env`.

## Run locally

Run the app inside the project venv with `uv run` (no need to `source .venv/bin/activate`):

```bash
uv run app.py
```

Open the URL printed in the terminal (default `http://127.0.0.1:7860`).

For a public Gradio link:

```bash
GRADIO_SHARE=true uv run app.py
```

Alternative (activate the venv yourself):

```bash
source .venv/bin/activate
python app.py
```

## Deploy to Gradio Spaces

1. Push this folder to a Hugging Face Space (SDK: **Gradio**)
2. Set Space secrets: `OPENAI_API_KEY`, `GOOGLE_API_KEY`, `PUSHOVER_USER`, `PUSHOVER_TOKEN`
3. Use `app.py` as the entry file

Example `README.md` front matter for Spaces:

```yaml
---
title: Professional Profile Agent
sdk: gradio
app_file: app.py
---
```

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | Agent model (tool calling) |
| `GOOGLE_API_KEY` | Yes* | Evaluator via Gemini API |
| `PUSHOVER_USER` | For tools | Pushover user key |
| `PUSHOVER_TOKEN` | For tools | Pushover app token |
| `PROFILE_NAME` | No | Display name (default: Vinayak Bakshi) |
| `AGENT_MODEL` | No | Default `gpt-4o-mini` |
| `EVALUATOR_MODEL` | No | Default `gemini-2.5-flash` |
| `GRADIO_SHARE` | No | Set `true` for public link |

\*If `GOOGLE_API_KEY` is omitted, the evaluator falls back to `OPENAI_API_KEY`.

## Project structure

```
professional-profile-agent/
├── app.py              # Gradio entry point
├── data/me/            # summary.txt + resume PDF
├── src/
│   ├── agent.py        # Agent + tool loop + evaluation retry
│   ├── evaluator.py    # Structured response evaluation
│   ├── profile.py      # Load resume & summary
│   ├── prompts.py      # System prompts
│   └── tools.py        # Pushover + tool schemas
├── pyproject.toml      # dependencies (used by uv sync)
├── uv.lock             # locked versions (optional but recommended)
├── requirements.txt    # for Hugging Face Spaces (pip)
└── .env.example
```

## Credits

Based on patterns from the [Agentic AI course by Ed Donner](https://github.com/ed-donner/agents) career conversation notebook.
