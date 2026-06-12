from pathlib import Path
import anthropic
from config import ANTHROPIC_API_KEY, ANTHROPIC_MODEL

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def explain_result(question, sql, df):

    result_text = df.to_string(index=False)

    prompt_path = (
        Path(__file__).resolve().parent.parent
        / "prompts"
        / "business_explanation_prompt.txt"
    )

    with open(prompt_path, "r", encoding="utf-8") as file:
        template = file.read()

    prompt = template.format(
        question=question,
        sql=sql,
        result=result_text
    )

    message = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=1024,
        system="Eres un Agente Experto en Gestión de Riesgo de Fraude y Ciberseguridad.",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return message.content[0].text.strip()
