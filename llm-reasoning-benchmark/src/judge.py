"""Evaluation and judging logic for LLM responses."""

import json
from openai import OpenAI


def build_judge_prompt(question: str, competitors: list[str], answers: list[str]) -> str:
    """Build the prompt for the judge to evaluate responses."""
    responses_text = ""
    for idx, answer in enumerate(answers):
        responses_text += f"# Response from competitor {idx + 1}\n\n{answer}\n\n"
    
    return f"""You are judging a competition between {len(competitors)} competitors.
Each model has been given this question:

{question}

Your job is to evaluate each response for clarity and strength of argument, and rank them in order of best to worst.
Respond with JSON, and only JSON, with the following format:
{{"results": ["best competitor number", "second best competitor number", "third best competitor number", ...]}}

Here are the responses from each competitor:

{responses_text}

Now respond with the JSON with the ranked order of the competitors, nothing else. Do not include markdown formatting or code blocks."""


def evaluate_responses(
    question: str,
    competitors: list[str],
    answers: list[str],
    judge_model: str = "gpt-4o-mini"
) -> dict:
    """
    Have a judge model evaluate and rank the responses.
    
    Returns a dict with:
        - rankings: list of model names in order from best to worst
        - raw_response: the raw JSON response from the judge
    """
    client = OpenAI()
    
    judge_prompt = build_judge_prompt(question, competitors, answers)
    messages = [{"role": "user", "content": judge_prompt}]
    
    response = client.chat.completions.create(
        model=judge_model,
        messages=messages
    )
    
    result_text = response.choices[0].message.content
    results_dict = json.loads(result_text)
    ranks = results_dict["results"]
    
    rankings = []
    for rank_idx in ranks:
        competitor_idx = int(rank_idx) - 1
        rankings.append(competitors[competitor_idx])
    
    return {
        "rankings": rankings,
        "raw_response": results_dict
    }
