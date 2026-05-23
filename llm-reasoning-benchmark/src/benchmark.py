"""
LLM Reasoning Benchmark

Pipeline:
1. GPT-5 (strong) generates a challenging reasoning question
2. GPT-5-nano and Claude Haiku (weak) answer the question
3. GPT-5 evaluates the answers
4. Claude Opus 4.7 meta-evaluates the evaluator's response
"""

from dotenv import load_dotenv

from .models import query_openai, query_anthropic
from .judge import evaluate_responses, meta_evaluate
from .output import save_benchmark_results


# Default configuration
QUESTION_GENERATOR = "gpt-5"
ANSWERERS = [
    ("openai", "gpt-5-nano"),
    ("anthropic", "claude-haiku-4-5"),
]
EVALUATOR = "gpt-5"
META_EVALUATOR = "claude-opus-4-7"


def generate_question(model: str = QUESTION_GENERATOR) -> str:
    """Generate a challenging reasoning question using a strong model."""
    request = (
        "Please come up with a challenging nuanced question that I can ask "
        "a number of LLMs to evaluate their intelligence in general reasoning. "
        "Answer only with the question, no explanation."
    )
    
    messages = [{"role": "user", "content": request}]
    return query_openai(model, messages)


def get_answers(question: str, answerers: list[tuple[str, str]] = None) -> tuple[list[str], list[str]]:
    """
    Get answers from the weak models.
    
    Returns (competitors, answers) lists.
    """
    if answerers is None:
        answerers = ANSWERERS
    
    competitors = []
    answers = []
    
    messages = [{"role": "user", "content": question}]
    
    for provider, model in answerers:
        if provider == "openai":
            answer = query_openai(model, messages)
        elif provider == "anthropic":
            answer = query_anthropic(model, messages)
        else:
            raise ValueError(f"Unknown provider: {provider}")
        
        competitors.append(model)
        answers.append(answer)
    
    return competitors, answers


def run_benchmark(
    question: str = None,
    answerers: list[tuple[str, str]] = None,
    question_generator: str = QUESTION_GENERATOR,
    evaluator_model: str = EVALUATOR,
    meta_evaluator_model: str = META_EVALUATOR,
    verbose: bool = True,
    save_output: bool = True,
    output_dir: str = "output",
    max_output_files: int = 3,
) -> dict:
    """
    Run the full benchmark pipeline.
    
    Pipeline:
    1. Generate challenging question (GPT-5)
    2. Get answers from weak models (nano, haiku)
    3. Evaluate answers (GPT-5)
    4. Meta-evaluate the evaluation (Opus 4.7)
    
    Returns dict with all results.
    """
    load_dotenv(override=True)
    
    # Step 1: Generate question
    if question is None:
        if verbose:
            print(f"Generating question with {question_generator}...")
        question = generate_question(question_generator)
    
    if verbose:
        print(f"\nQuestion: {question}\n")
    
    # Step 2: Get answers from weak models
    if verbose:
        print("Getting answers from weak models...")
    
    competitors, answers = get_answers(question, answerers)
    
    if verbose:
        for comp, ans in zip(competitors, answers):
            print(f"\n--- {comp} ---")
            print(ans[:300] + "..." if len(ans) > 300 else ans)
    
    # Step 3: Evaluate with strong model
    if verbose:
        print(f"\n\nEvaluating with {evaluator_model}...")
    
    evaluator_response = evaluate_responses(
        question, competitors, answers, evaluator_model
    )
    
    if verbose:
        print(f"\n--- Evaluator Response ---")
        print(evaluator_response[:500] + "..." if len(evaluator_response) > 500 else evaluator_response)
    
    # Step 4: Meta-evaluate with Opus
    if verbose:
        print(f"\n\nMeta-evaluating with {meta_evaluator_model}...")
    
    meta_score = meta_evaluate(
        question, competitors, answers, evaluator_response, meta_evaluator_model
    )
    
    if verbose:
        print(f"\n{'=' * 50}")
        print(f"META-EVALUATOR SCORE: {meta_score}")
        print(f"{'=' * 50}")

    results = {
        "question": question,
        "competitors": competitors,
        "answers": answers,
        "evaluator_response": evaluator_response,
        "meta_evaluator_score": meta_score,
        "config": {
            "question_generator": question_generator,
            "answerers": answerers or ANSWERERS,
            "evaluator": evaluator_model,
            "meta_evaluator": meta_evaluator_model,
        },
    }

    if save_output:
        output_path = save_benchmark_results(
            results, output_dir=output_dir, max_files=max_output_files
        )
        results["output_file"] = str(output_path)
        if verbose:
            print(f"\nResults saved to: {output_path}")

    return results


if __name__ == "__main__":
    results = run_benchmark()
