import json
from pathlib import Path


def build_prompt(question: str, semantic_dictionary: dict) -> str:
    project_root = Path(__file__).resolve().parent.parent
    prompt_path = project_root / "prompts" / "text_to_sql_prompt.txt"

    with open(prompt_path, "r", encoding="utf-8") as file:
        template = file.read()

    semantic_text = json.dumps(
        semantic_dictionary,
        indent=2,
        ensure_ascii=False
    )

    prompt = template.replace("{{semantic_dictionary}}", semantic_text)
    prompt = prompt.replace("{{question}}", question)

    return prompt