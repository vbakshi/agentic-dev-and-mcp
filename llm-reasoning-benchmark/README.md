# LLM Reasoning Benchmark

Compare reasoning capabilities across different large language models by generating challenging questions, collecting responses, and having a judge model rank the results.

## How It Works

```
┌─────────────────┐
│  Generate       │
│  Challenge      │──────────────────────────────────────┐
│  Question       │                                      │
└────────┬────────┘                                      │
         │                                               │
         ▼                                               ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   GPT-4o-mini   │    │  Claude Haiku   │    │   Other Models  │
│                 │    │                 │    │   (optional)    │
└────────┬────────┘    └────────┬────────┘    └────────┬────────┘
         │                      │                      │
         └──────────────────────┼──────────────────────┘
                                │
                                ▼
                    ┌─────────────────────┐
                    │   Judge (GPT-4o)    │
                    │   Evaluates &       │
                    │   Ranks Responses   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Final Rankings    │
                    └─────────────────────┘
```

## Sample Output

```
Generating challenge question...

Question: A farmer has 17 sheep. All but 9 die. How many sheep does the farmer have left?

Querying gpt-4o-mini...
  Got response (234 chars)
Querying claude-haiku-4-5...
  Got response (189 chars)

Judging with gpt-4o-mini...

==================================================
RESULTS
==================================================
  Rank 1: claude-haiku-4-5
  Rank 2: gpt-4o-mini
==================================================
```

## Setup

1. **Navigate to this directory**
   ```bash
   cd llm-reasoning-benchmark
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API keys**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

## Usage

### Run the default benchmark
```bash
python main.py
```

### Use as a library
```python
from src.benchmark import run_benchmark

# Run with default models (GPT-4o-mini vs Claude Haiku)
results = run_benchmark()

# Or specify your own models
results = run_benchmark(
    models=[
        ("openai", "gpt-4o-mini"),
        ("anthropic", "claude-sonnet-4-5"),
        ("gemini", "gemini-2.5-flash"),
    ],
    question="What is the meaning of life?",  # Optional custom question
    verbose=True
)

print(results["rankings"])
```

### Supported Providers

| Provider | Example Models | API Key Required |
|----------|---------------|------------------|
| `openai` | gpt-4o-mini, gpt-4o | OPENAI_API_KEY |
| `anthropic` | claude-haiku-4-5, claude-sonnet-4-5 | ANTHROPIC_API_KEY |
| `gemini` | gemini-2.5-flash | GOOGLE_API_KEY |
| `deepseek` | deepseek-chat | DEEPSEEK_API_KEY |
| `groq` | llama-3.1-70b-versatile | GROQ_API_KEY |
| `ollama` | llama3.2, mistral | None (local) |

## Project Structure

```
llm-reasoning-benchmark/
├── main.py              # Entry point
├── src/
│   ├── benchmark.py     # Main benchmark orchestration
│   ├── models.py        # Model client configurations
│   └── judge.py         # Evaluation logic
├── requirements.txt
└── .env.example
```

---

## Credits

This project was built while taking the [Agentic AI course by Ed Donner](https://github.com/ed-donner/agents). The course covers foundations of building AI agents, including multi-model orchestration patterns demonstrated here.
