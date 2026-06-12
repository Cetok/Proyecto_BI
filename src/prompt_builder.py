import json
from pathlib import Path
from few_shot_retriever import retrieve_few_shot_examples


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

    # Recuperar ejemplos de consultas similares
    examples = retrieve_few_shot_examples(question, k=2)
    examples_text = ""
    for ex in examples:
        examples_text += f"Pregunta: {ex['question']}\nRespuesta correcta:\nSQL_SELECT\n{ex['sql']}\n\n"
    
    if not examples_text:
        examples_text = "No se encontraron ejemplos específicos. Utiliza las reglas generales del diccionario.\n"

    prompt = template.replace("{{semantic_dictionary}}", semantic_text)
    prompt = prompt.replace("{{few_shot_examples}}", examples_text.strip())
    prompt = prompt.replace("{{question}}", question)

    return prompt