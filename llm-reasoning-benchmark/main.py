#!/usr/bin/env python3
"""
LLM Reasoning Benchmark

Default pipeline:
- Question Generator: GPT-5 (strong)
- Answerers: GPT-5-nano, Claude Haiku (weak)
- Evaluator: GPT-5 (strong)
- Meta-Evaluator: Claude Opus 4.7 (strongest)
"""

import argparse

from src.benchmark import run_benchmark

DEFAULT_COIN_QUESTION = (
    "You are handed one coin chosen uniformly at random from three: Coin A is "
    "double‑headed (always lands heads), Coin B lands heads with probability 3/4, "
    "and Coin C is fair. You may flip the coin up to three times, observing outcomes "
    "as you go; at any point you may stop and name which coin it is. There is no cost "
    "to flipping, and you win if and only if you name the coin correctly. What "
    "stopping rule and final decision rule maximize your probability of being correct, "
    "and what is that maximum probability (give the exact value)?"
)


def main():
    """Run the benchmark with default or custom settings."""
    parser = argparse.ArgumentParser(description="Run the LLM reasoning benchmark")
    parser.add_argument(
        "--question",
        type=str,
        default=None,
        help="Custom question (skips question generation)",
    )
    parser.add_argument(
        "--use-coin-question",
        action="store_true",
        help="Run with the three-coin optimal stopping problem",
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Do not write results to the output folder",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="output",
        help="Directory for saved benchmark results (default: output)",
    )
    args = parser.parse_args()

    question = args.question
    if args.use_coin_question:
        question = DEFAULT_COIN_QUESTION

    print("=" * 60)
    print("LLM REASONING BENCHMARK")
    print("=" * 60)
    print("\nPipeline:")
    if question:
        print("  1. Using provided question (no generation)")
    else:
        print("  1. GPT-5 generates challenging question")
    print("  2. GPT-5-nano & Claude Haiku answer")
    print("  3. GPT-5 evaluates the answers")
    print("  4. Claude Opus 4.7 meta-evaluates")
    print("=" * 60 + "\n")

    results = run_benchmark(
        question=question,
        verbose=True,
        save_output=not args.no_save,
        output_dir=args.output_dir,
    )

    print("\n\n" + "=" * 60)
    print("FULL RESULTS SUMMARY")
    print("=" * 60)
    print(f"\nQuestion: {results['question']}")
    print(f"\nMeta-Evaluator Score: {results['meta_evaluator_score']}/100")
    if results.get("output_file"):
        print(f"\nSaved to: {results['output_file']}")


if __name__ == "__main__":
    main()
