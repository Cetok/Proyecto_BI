import anthropic
from config import ANTHROPIC_API_KEY, ANTHROPIC_MODEL

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def clean_sql_response(response: str) -> str:
    response = response.strip()
    response = response.replace("```sql", "")
    response = response.replace("```", "")
    return response.strip()


def clean_json_response(response: str) -> str:
    response = response.strip()
    response = response.replace("```json", "")
    response = response.replace("```", "")
    return response.strip()


def generate_sql(prompt: str) -> str:
    message = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=1024,
        system="Eres un generador SQL seguro para PostgreSQL. Devuelve únicamente SQL plano, sin Markdown.",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    raw_sql = message.content[0].text.strip()
    return clean_sql_response(raw_sql)


def generate_sql_correction(question: str, failing_sql: str, error_message: str, semantic_dictionary: dict) -> str:
    from pathlib import Path
    import json

    project_root = Path(__file__).resolve().parent.parent
    prompt_path = project_root / "prompts" / "sql_correction_prompt.txt"

    with open(prompt_path, "r", encoding="utf-8") as file:
        template = file.read()

    semantic_text = json.dumps(
        semantic_dictionary,
        indent=2,
        ensure_ascii=False
    )

    prompt = template.replace("{{question}}", question)
    prompt = prompt.replace("{{failing_sql}}", failing_sql)
    prompt = prompt.replace("{{error_message}}", error_message)
    prompt = prompt.replace("{{semantic_dictionary}}", semantic_text)

    message = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=1024,
        system="Eres un asistente experto en depuración de consultas SQL. Devuelve únicamente el SQL plano corregido.",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    raw_sql = message.content[0].text.strip()
    return clean_sql_response(raw_sql)



def generate_json(prompt: str) -> str:
    message = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=2048,
        system="Eres un generador de JSON para sistemas de Business Intelligence. Devuelve únicamente JSON válido, sin Markdown.",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    raw_json = message.content[0].text.strip()
    return clean_json_response(raw_json)


def generate_text(prompt: str) -> str:
    message = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=2048,
        system=(
            "Eres un analista ejecutivo de Business Intelligence. "
            "Genera explicaciones claras, prudentes y basadas únicamente en los datos proporcionados."
        ),
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return message.content[0].text.strip()
