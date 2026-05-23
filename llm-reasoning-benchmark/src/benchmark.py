"""Main benchmark logic for comparing LLM reasoning capabilities."""

import os
from dotenv import load_dotenv
from openai import OpenAI

from .models import query_model
from .judge import evaluate_responses


DEFAULT_MODELS = [
    ("openai", "gpt-4o-mini"),
    ("anthropic", "claude-haiku-4-5"),
]


def generate_question(model: str = "gpt-4o-mini") -> str:
    """Generate a challenging reasoning question using GPT."""
    client = OpenAI()
    
    request = (
        "Please come up with a challenging, nuanced question that I can ask "
        "a number of LLMs to evaluate their intelligence in general reasoning. "
        "Answer only with the question, no explanation."
    )
    
    messages = [{"role": "user", "content": request}]
    response = client.chat.completions.create(model=model, messages=messages)
    
    return response.choices[0].message.content


def run_benchmark(
    models: list[tuple[str, str]] | None = None,
    question: str | None = None,
    judge_model: str = "gpt-4o-mini",
    verbose: bool = True
) -> dict:
    """
    Run the full benchmark: generate question, query models, judge responses.
    
    Args:
        models: List of (provider, model_name) tuples. Defaults to GPT-4o-mini and Claude Haiku.
        question: Custom question to use. If None, generates one.
        judge_model: Model to use for judging. Defaults to gpt-4o-mini.
        verbose: Whether to print progress.
    
    Returns:
        dict with question, competitors, answers, and rankings.
    """
    load_dotenv(override=True)
    
    if models is None:
        models = DEFAULT_MODELS
    
    if question is None:
        if verbose:
            print("Generating challenge question...")
        question = generate_question()
    
    if verbose:
        print(f"\nQuestion: {question}\n")
    
    competitors = []
    answers = []
    messages = [{"role": "user", "content": question}]
    
    for provider, model_name in models:
        if verbose:
            print(f"Querying {model_name}...")
        try:
            answer = query_model(provider, model_name, messages)
            competitors.append(model_name)
            answers.append(answer)
            if verbose:
                print(f"  Got response ({len(answer)} chars)")
        except Exception as e:
            if verbose:
                print(f"  Error: {e}")
    
    if len(answers) < 2:
        raise ValueError("Need at least 2 successful responses to judge")
    
    if verbose:
        print(f"\nJudging with {judge_model}...")
    
    evaluation = evaluate_responses(question, competitors, answers, judge_model)
    
    if verbose:
        print("\n" + "=" * 50)
        print("RESULTS")
        print("=" * 50)
        for idx, model in enumerate(evaluation["rankings"]):
            print(f"  Rank {idx + 1}: {model}")
        print("=" * 50)
    
    return {
        "question": question,
        "competitors": competitors,
        "answers": answers,
        "rankings": evaluation["rankings"],
        "raw_judge_response": evaluation["raw_response"]
    }


if __name__ == "__main__":
    results = run_benchmark()
