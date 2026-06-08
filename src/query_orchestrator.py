from prompt_builder import build_prompt
from llm_client import generate_sql
from sql_validator import validate_sql
from db import run_query


def normalize_sql_response(response: str) -> str:
    """
    Normalizes the LLM SQL response.

    The Text-to-SQL prompt may return:
    - SQL_SELECT <query>
    - UNSAFE_REQUEST
    - OUT_OF_SCOPE
    - raw SELECT query
    """

    response = response.strip()

    if response.startswith("SQL_SELECT"):
        response = response.replace("SQL_SELECT", "", 1).strip()

    return response


def execute_dashboard_plan(plan: dict, semantic_dictionary: dict) -> list:
    """
    Executes all analytical items from a dashboard plan.

    The planner defines analytical intentions.
    This orchestrator turns each intention into SQL using the existing
    Text-to-SQL flow, validates it, executes it and stores the result.

    Returns a list of execution results.
    """

    execution_results = []

    analytical_items = []

    for kpi in plan.get("kpis", []):
        analytical_items.append({
            "type": "kpi",
            "id": kpi.get("id"),
            "title": kpi.get("title"),
            "metric": kpi.get("metric"),
            "query_intent": kpi.get("query_intent"),
            "chart_type": None
        })

    for visual in plan.get("visuals", []):
        analytical_items.append({
            "type": "visual",
            "id": visual.get("id"),
            "title": visual.get("title"),
            "metric": None,
            "query_intent": visual.get("query_intent"),
            "chart_type": visual.get("chart_type")
        })

    for item in analytical_items:
        query_intent = item.get("query_intent")

        if not query_intent:
            execution_results.append({
                **item,
                "status": "FAILED",
                "message": "Missing query_intent.",
                "sql": None,
                "dataframe": None
            })
            continue

        prompt = build_prompt(query_intent, semantic_dictionary)
        response = generate_sql(prompt)

        if response == "UNSAFE_REQUEST":
            execution_results.append({
                **item,
                "status": "UNSAFE_REQUEST",
                "message": "The generated query was blocked as unsafe.",
                "sql": None,
                "dataframe": None
            })
            continue

        if response == "OUT_OF_SCOPE":
            execution_results.append({
                **item,
                "status": "OUT_OF_SCOPE",
                "message": "The generated query is outside the semantic scope.",
                "sql": None,
                "dataframe": None
            })
            continue

        sql = normalize_sql_response(response)

        is_valid, validation_message = validate_sql(sql, semantic_dictionary)

        if not is_valid:
            execution_results.append({
                **item,
                "status": "SQL_VALIDATION_FAILED",
                "message": validation_message,
                "sql": sql,
                "dataframe": None
            })
            continue

        try:
            df = run_query(sql)

            execution_results.append({
                **item,
                "status": "SUCCESS",
                "message": validation_message,
                "sql": sql,
                "dataframe": df
            })

        except Exception as e:
            execution_results.append({
                **item,
                "status": "EXECUTION_FAILED",
                "message": str(e),
                "sql": sql,
                "dataframe": None
            })

    return execution_results
