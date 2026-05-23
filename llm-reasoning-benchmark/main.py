#!/usr/bin/env python3
"""
LLM Reasoning Benchmark

Compare reasoning capabilities across different language models.
"""

from src.benchmark import run_benchmark


def main():
    """Run the benchmark with default settings."""
    
    models = [
        ("openai", "gpt-4o-mini"),
        ("anthropic", "claude-haiku-4-5"),
    ]
    
    results = run_benchmark(models=models, verbose=True)
    
    print("\n\nDetailed Responses:")
    print("-" * 50)
    for model, answer in zip(results["competitors"], results["answers"]):
        print(f"\n### {model}\n")
        print(answer[:500] + "..." if len(answer) > 500 else answer)
        print()


if __name__ == "__main__":
    main()
