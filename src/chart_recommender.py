from pathlib import Path
import anthropic
from config import ANTHROPIC_API_KEY, ANTHROPIC_MODEL

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

ALLOWED_CHART_TYPES = {
    "bar",
    "line",
    "scatter",
    "pie"
}

def recommend_chart_type(question, df):
    prompt_path = (
        Path(__file__).resolve().parent.parent
        / "prompts"
        / "chart_recommendation_prompt.txt"
    )

    with open(prompt_path, "r", encoding="utf-8") as file:
        template = file.read()

    prompt = template.format(
        question=question,
        columns=list(df.columns),
        sample=df.head(5).to_string(index=False)
    )

    message = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=64,
        system="Eres un experto en visualización BI. Devuelve solo el tipo de gráfico.",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    chart_type = message.content[0].text.strip().lower()
    if chart_type not in ALLOWED_CHART_TYPES:
        return "bar"
    return chart_type
