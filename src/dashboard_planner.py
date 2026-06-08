import json
from pathlib import Path

from llm_client import generate_json


def build_dashboard_planner_prompt(
    question: str,
    semantic_dictionary: dict,
    semantic_context: str
) -> str:
    project_root = Path(__file__).resolve().parent.parent
    prompt_path = project_root / "prompts" / "dashboard_planner_prompt.txt"

    with open(prompt_path, "r", encoding="utf-8") as file:
        template = file.read()

    semantic_dictionary_text = json.dumps(
        semantic_dictionary,
        indent=2,
        ensure_ascii=False
    )

    prompt = template.replace("{{question}}", question)
    prompt = prompt.replace("{{semantic_dictionary}}", semantic_dictionary_text)
    prompt = prompt.replace("{{semantic_context}}", semantic_context)

    return prompt


def generate_dashboard_plan(
    question: str,
    semantic_dictionary: dict,
    semantic_context: str
) -> dict:
    prompt = build_dashboard_planner_prompt(
        question=question,
        semantic_dictionary=semantic_dictionary,
        semantic_context=semantic_context
    )

    response = generate_json(prompt)

    try:
        return json.loads(response)
    except json.JSONDecodeError:
        return {
            "status": "INVALID_JSON",
            "dashboard_title": "",
            "business_goal": "",
            "kpis": [],
            "visuals": [],
            "warnings": [
                "The LLM response could not be parsed as valid JSON.",
                response
            ]
        }
