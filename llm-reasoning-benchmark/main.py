#!/usr/bin/env python3
"""
LLM Reasoning Benchmark

Default pipeline:
- Question Generator: GPT-5 (strong)
- Answerers: GPT-5-nano, Claude Haiku (weak)
- Evaluator: GPT-5 (strong)
- Meta-Evaluator: Claude Opus 4.7 (strongest)
"""

from src.benchmark import run_benchmark


def main():
    """Run the benchmark with default settings."""
    print("=" * 60)
    print("LLM REASONING BENCHMARK")
    print("=" * 60)
    print("\nPipeline:")
    print("  1. GPT-5 generates challenging question")
    print("  2. GPT-5-nano & Claude Haiku answer")
    print("  3. GPT-5 evaluates the answers")
    print("  4. Claude Opus 4.7 meta-evaluates")
    print("=" * 60 + "\n")
    
    results = run_benchmark(verbose=True)
    
    print("\n\n" + "=" * 60)
    print("FULL RESULTS SUMMARY")
    print("=" * 60)
    print(f"\nQuestion: {results['question']}")
    print(f"\nMeta-Evaluator Score: {results['meta_evaluator_score']}/100")


if __name__ == "__main__":
    main()
