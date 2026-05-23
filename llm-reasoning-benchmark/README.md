# LLM Reasoning Benchmark

A multi-layer evaluation pipeline that tests LLM reasoning capabilities by having weak models answer challenging questions, then evaluating and meta-evaluating the results.

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    QUESTION GENERATION                       │
│                        GPT-5 (strong)                        │
│         "Generate a challenging reasoning question"          │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────────┐
        │         ANSWERING (weak models)      │
        ├──────────────────┬──────────────────┤
        │   GPT-5-nano     │   Claude Haiku   │
        └────────┬─────────┴────────┬─────────┘
                 │                  │
                 └────────┬─────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                       EVALUATION                             │
│                        GPT-5 (strong)                        │
│         "Evaluate accuracy and explanation quality"          │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    META-EVALUATION                           │
│                   Claude Opus 4.7 (strongest)                │
│         "Score the evaluator's response (0-100)"             │
└─────────────────────────────────────────────────────────────┘
```

## Default Configuration

| Role | Model | Purpose |
|------|-------|---------|
| Question Generator | GPT-5 | Creates challenging reasoning questions |
| Answerer 1 | GPT-5-nano | Weak model - tests basic reasoning |
| Answerer 2 | Claude Haiku 4.5 | Weak model - tests basic reasoning |
| Evaluator | GPT-5 | Assesses answer accuracy and explanations |
| Meta-Evaluator | Claude Opus 4.7 | Scores the evaluator (0-100) |

## Sample Output

```
==============================================================
LLM REASONING BENCHMARK
==============================================================

Pipeline:
  1. GPT-5 generates challenging question
  2. GPT-5-nano & Claude Haiku answer
  3. GPT-5 evaluates the answers
  4. Claude Opus 4.7 meta-evaluates
==============================================================

Generating question with gpt-5...

Question: A three-digit number is such that the sum of its digits is 18...

Getting answers from weak models...

--- gpt-5-nano ---
Let me work through this step by step...

--- claude-haiku-4-5 ---
I'll solve this systematically...

Evaluating with gpt-5...

--- Evaluator Response ---
Both models approached the problem correctly, however...

Meta-evaluating with claude-opus-4-7...

==================================================
META-EVALUATOR SCORE: 85
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
   # Edit .env with your OpenAI and Anthropic API keys
   ```

## Usage

### Run with defaults
```bash
python main.py
```

### Customize the pipeline
```python
from src.benchmark import run_benchmark

results = run_benchmark(
    question="Your custom question here",  # Or None to generate
    answerers=[
        ("openai", "gpt-5-nano"),
        ("anthropic", "claude-haiku-4-5"),
    ],
    question_generator="gpt-5",
    evaluator_model="gpt-5",
    meta_evaluator_model="claude-opus-4-7",
    verbose=True
)

print(f"Meta-evaluator score: {results['meta_evaluator_score']}")
```

## Project Structure

```
llm-reasoning-benchmark/
├── main.py              # Entry point
├── src/
│   ├── benchmark.py     # Pipeline orchestration
│   ├── models.py        # OpenAI/Anthropic query functions
│   └── judge.py         # Evaluator & meta-evaluator logic
├── requirements.txt
└── .env.example
```

---

## Credits

Built while taking the [Agentic AI course by Ed Donner](https://github.com/ed-donner/agents). This project demonstrates multi-model orchestration and evaluation patterns.
