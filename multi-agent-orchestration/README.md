# Multi-Agent Orchestration

Production-oriented multi-agent workflows using the [OpenAI Agents SDK](https://github.com/openai/openai-agents-python) (`agents` package).

The primary workflow is a **ComplAI cold-sales campaign**: a Sales Manager coordinates four writer agents (as tools), selects the best draft, and **hands off** to an Emailer Agent for subject line, HTML conversion, and SendGrid delivery.

## Architecture

```
User request
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│                     Sales Manager                            │
│  tools: 4× sales writers (agents-as-tools)                   │
│  handoff: Emailer Agent                                      │
└───────────────┬──────────────────────────────┬──────────────┘
                │                              │
    brief ──────┼──► Professional Writer       │
    brief ──────┼──► Humorous Writer           │
    brief ──────┼──► Concise Writer            │
    brief ──────┼──► Friendly Writer           │
                │                              │
                │  winning email_body          │
                └──────────────────────────────► Emailer Agent
                                                   ├─ generate_subject_line (tool)
                                                   ├─ convert_to_html (tool)
                                                   └─ send_html_email (tool)
```

### Design layers

| Layer | Module | Responsibility |
|-------|--------|----------------|
| Config | `src/config.py` | Env-backed `Settings`; fail fast on missing keys |
| Prompts | `src/prompts.py` | Single source of truth for agent instructions |
| Validation | `src/validation.py` | Reject draft emails passed as writer briefs |
| Tools | `src/tools/email.py` | SendGrid delivery; supports dry-run |
| Agents | `src/agents/` | Factories for writers, emailer, sales manager |
| Workflow | `src/workflow/sales_campaign.py` | Wires dependencies and runs `Runner` |
| Output | `src/output.py` | JSON artifacts (max 3 files, rolling) |

### Agents-as-tools vs handoffs

- **Writer tools** (`SalesWriterPool`): Each writer is a nested agent invoked with a `brief` string. The manager stays in control; writers do not see full conversation history. Server-side validation blocks draft emails masquerading as briefs.
- **Emailer handoff** (`SalesManagerFactory`): Delegates delivery to a specialist agent with structured input (`email_body`). The emailer receives a filtered slice of context and runs its own tool chain.

## Setup

```bash
cd multi-agent-orchestration
cp .env.example .env
# Set OPENAI_API_KEY, SENDGRID_API_KEY, SALES_FROM_EMAIL, SALES_TO_EMAIL

uv sync
# or: pip install -r requirements.txt
```

## Run

**Dry run** (no SendGrid call — good for testing orchestration):

```bash
python main.py --dry-run
```

**Live send:**

```bash
python main.py --request "Send a cold sales email from Alice. Open with Dear CEO."
```

**Options:**

```bash
python main.py --help
python main.py --no-save          # skip output/ JSON
python main.py --verbose          # debug logs
```

## Notebooks

Interactive prototyping (source for this production code):

```bash
jupyter notebook notebooks/workflow_prototype.ipynb
```

## Project structure

```
multi-agent-orchestration/
├── main.py
├── notebooks/
│   └── workflow_prototype.ipynb
├── src/
│   ├── config.py
│   ├── prompts.py
│   ├── validation.py
│   ├── output.py
│   ├── tools/
│   │   └── email.py
│   ├── agents/
│   │   ├── sales_writers.py
│   │   ├── emailer.py
│   │   └── sales_manager.py
│   └── workflow/
│       └── sales_campaign.py
├── output/                 # gitignored run artifacts
├── pyproject.toml
├── requirements.txt
└── .env.example
```

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | Agent models |
| `SENDGRID_API_KEY` | Yes* | HTML email delivery |
| `SALES_FROM_EMAIL` | No | Verified SendGrid sender |
| `SALES_TO_EMAIL` | No | Recipient for campaign emails |
| `SALES_AGENT_MODEL` | No | Default `gpt-4o-mini` |
| `SALES_WORKFLOW_DRY_RUN` | No | Set `true` to skip SendGrid |

\*Not required when using `--dry-run` or `SALES_WORKFLOW_DRY_RUN=true`.

---

Built while taking the [Agentic AI course by Ed Donner](https://github.com/ed-donner/agents).
