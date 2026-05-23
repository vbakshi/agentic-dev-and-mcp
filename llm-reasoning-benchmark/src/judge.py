"""Evaluation and meta-evaluation logic for LLM responses."""

from .models import query_openai, query_anthropic


def build_evaluator_prompt(
    question: str,
    competitors: list[str],
    answers: list[str]
) -> str:
    """Build the prompt for the evaluator to assess responses."""
    content = f"Please evaluate the answers to the question: {question} "
    content += "from the following list of competitor LLMs and evaluate the accuracy and explanation of the answers\n\n"
    
    for competitor, answer in zip(competitors, answers):
        content += f"Competitor: {competitor}\n\nAnswer: {answer}\n\n"
    
    return content


def build_meta_evaluator_prompt(
    question: str,
    competitors: list[str],
    answers: list[str],
    evaluator_response: str
) -> str:
    """Build the prompt for the meta-evaluator to assess the evaluator."""
    content = f"You are evaluating an evaluator's response to the evaluation of {len(competitors)} answers "
    content += f"from LLMs to the question: {question}\n\n"
    content += "Answers from LLMs:\n\n"
    
    for competitor, answer in zip(competitors, answers):
        content += f"Competitor: {competitor}\n\nAnswer: {answer}\n\n"
    
    content += f"And the evaluator's response is: {evaluator_response}\n\n"
    content += "Please evaluate the evaluator's response, and provide a score between 0 and 100, "
    content += "where 0 is the worst and 100 is the best.\n\n"
    content += "Respond only with the score, no explanation."
    
    return content


def evaluate_responses(
    question: str,
    competitors: list[str],
    answers: list[str],
    evaluator_model: str = "gpt-5"
) -> str:
    """
    Have the evaluator model assess the responses.
    
    Returns the evaluator's detailed assessment.
    """
    prompt = build_evaluator_prompt(question, competitors, answers)
    messages = [{"role": "user", "content": prompt}]
    
    return query_openai(evaluator_model, messages)


def meta_evaluate(
    question: str,
    competitors: list[str],
    answers: list[str],
    evaluator_response: str,
    meta_evaluator_model: str = "claude-opus-4-7"
) -> str:
    """
    Have the meta-evaluator assess the evaluator's response.
    
    Returns a score from 0-100.
    """
    prompt = build_meta_evaluator_prompt(question, competitors, answers, evaluator_response)
    messages = [{"role": "user", "content": prompt}]
    
    return query_anthropic(meta_evaluator_model, messages, max_tokens=1000)
