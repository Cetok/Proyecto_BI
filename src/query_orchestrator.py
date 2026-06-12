from prompt_builder import build_prompt
from llm_client import generate_sql, generate_sql_correction
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


def generate_and_validate_sql_with_retry(question: str, semantic_dictionary: dict, max_retries: int = 3) -> dict:
    """
    Generates SQL from natural language, validates it, and executes it.
    If validation or execution fails, it calls the LLM for self-correction.
    Runs up to `max_retries` times.
    """
    prompt = build_prompt(question, semantic_dictionary)
    response = generate_sql(prompt)

    if response in ("UNSAFE_REQUEST", "OUT_OF_SCOPE"):
        return {
            "status": response,
            "sql": None,
            "dataframe": None,
            "retries": 0,
            "error": f"La IA retornó un estado: {response}",
            "history": []
        }

    sql = normalize_sql_response(response)
    try_count = 0
    history = []

    while try_count <= max_retries:
        # 1. Deterministic Validation
        is_valid, validation_message = validate_sql(sql, semantic_dictionary)
        
        if not is_valid:
            error_msg = f"Validación determinista fallida: {validation_message}"
            history.append({"sql": sql, "error": error_msg, "phase": "validation"})
            if try_count < max_retries:
                try_count += 1
                sql = normalize_sql_response(generate_sql_correction(question, sql, error_msg, semantic_dictionary))
                continue
            else:
                return {
                    "status": "SQL_VALIDATION_FAILED",
                    "sql": sql,
                    "dataframe": None,
                    "retries": try_count,
                    "error": error_msg,
                    "history": history
                }

        # 2. Database Execution Test
        try:
            df = run_query(sql)
            return {
                "status": "SUCCESS",
                "sql": sql,
                "dataframe": df,
                "retries": try_count,
                "error": None,
                "history": history
            }
        except Exception as e:
            error_msg = f"Error de ejecución en DB: {str(e)}"
            history.append({"sql": sql, "error": error_msg, "phase": "execution"})
            if try_count < max_retries:
                try_count += 1
                sql = normalize_sql_response(generate_sql_correction(question, sql, error_msg, semantic_dictionary))
                continue
            else:
                return {
                    "status": "EXECUTION_FAILED",
                    "sql": sql,
                    "dataframe": None,
                    "retries": try_count,
                    "error": error_msg,
                    "history": history
                }


def execute_dashboard_plan(plan: dict, semantic_dictionary: dict) -> list:
    """
    Executes all analytical items from a dashboard plan.

    The planner defines analytical intentions.
    This orchestrator turns each intention into SQL using the existing
    Text-to-SQL flow with self-healing, executes it and stores the result.

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
                "message": "Falta query_intent.",
                "sql": None,
                "dataframe": None,
                "retries": 0,
                "history": []
            })
            continue

        res = generate_and_validate_sql_with_retry(query_intent, semantic_dictionary)

        execution_results.append({
            **item,
            "status": res["status"],
            "message": res["error"] if res["error"] else "SQL aprobado y ejecutado con éxito.",
            "sql": res["sql"],
            "dataframe": res["dataframe"],
            "retries": res["retries"],
            "history": res["history"]
        })

    return execution_results

