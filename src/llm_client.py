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
