import json
from pathlib import Path

from llm_client import generate_text


def dataframe_to_records(df, max_rows: int = 10):
    if df is None or df.empty:
        return []
    return df.head(max_rows).to_dict(orient="records")


def build_dashboard_results_summary(execution_results: list) -> list:
    summary = []

    for item in execution_results:
        if item.get("status") != "SUCCESS":
            summary.append({
                "id": item.get("id"),
                "title": item.get("title"),
                "type": item.get("type"),
                "status": item.get("status"),
                "message": item.get("message"),
                "data": []
            })
            continue

        df = item.get("dataframe")
        summary.append({
            "id": item.get("id"),
            "title": item.get("title"),
            "type": item.get("type"),
            "chart_type": item.get("chart_type"),
            "query_intent": item.get("query_intent"),
            "status": item.get("status"),
            "data": dataframe_to_records(df)
        })

    return summary


def build_dashboard_insight_prompt(
    question: str,
    dashboard_plan: dict,
    execution_results: list,
    semantic_context: str
) -> str:
    project_root = Path(__file__).resolve().parent.parent
    prompt_path = project_root / "prompts" / "dashboard_insight_prompt.txt"

    with open(prompt_path, "r", encoding="utf-8") as file:
        template = file.read()

    dashboard_plan_text = json.dumps(dashboard_plan, indent=2, ensure_ascii=False)
    dashboard_results = build_dashboard_results_summary(execution_results)
    dashboard_results_text = json.dumps(dashboard_results, indent=2, ensure_ascii=False, default=str)

    prompt = template.replace("{{question}}", question)
    prompt = prompt.replace("{{dashboard_plan}}", dashboard_plan_text)
    prompt = prompt.replace("{{dashboard_results}}", dashboard_results_text)
    prompt = prompt.replace("{{semantic_context}}", semantic_context)

    return prompt


def generate_dashboard_insight(
    question: str,
    dashboard_plan: dict,
    execution_results: list,
    semantic_context: str
) -> str:
    prompt = build_dashboard_insight_prompt(
        question=question,
        dashboard_plan=dashboard_plan,
        execution_results=execution_results,
        semantic_context=semantic_context
    )

    return generate_text(prompt)
