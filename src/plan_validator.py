ALLOWED_STATUS = {"OK", "OUT_OF_SCOPE", "UNSAFE_REQUEST"}
ALLOWED_CHART_TYPES = {"bar", "line", "pie", "scatter"}

MAX_KPIS = 4
MAX_VISUALS = 4


def validate_dashboard_plan(plan: dict, semantic_dictionary: dict):
    """
    Validates the analytical dashboard plan before generating SQL.

    This is different from SQL validation:
    - SQL validator controls the query.
    - Plan validator controls the analytical intention.
    """

    if not isinstance(plan, dict):
        return False, "The dashboard plan must be a JSON object."

    status = plan.get("status")

    if status not in ALLOWED_STATUS:
        return False, f"Invalid plan status: {status}"

    if status in {"OUT_OF_SCOPE", "UNSAFE_REQUEST"}:
        return False, f"Plan rejected with status: {status}"

    kpis = plan.get("kpis", [])
    visuals = plan.get("visuals", [])

    if not isinstance(kpis, list):
        return False, "The field 'kpis' must be a list."

    if not isinstance(visuals, list):
        return False, "The field 'visuals' must be a list."

    if len(kpis) > MAX_KPIS:
        return False, f"The plan contains too many KPIs. Maximum allowed: {MAX_KPIS}"

    if len(visuals) > MAX_VISUALS:
        return False, f"The plan contains too many visuals. Maximum allowed: {MAX_VISUALS}"

    official_metrics = set(semantic_dictionary.get("metrics", {}).keys())

    for kpi in kpis:
        metric = kpi.get("metric")

        if not metric:
            return False, "Each KPI must include a metric."

        if metric not in official_metrics:
            return False, f"KPI metric not allowed or not defined in semantic dictionary: {metric}"

        if not kpi.get("query_intent"):
            return False, f"KPI '{kpi.get('id', '')}' must include query_intent."

    for visual in visuals:
        chart_type = visual.get("chart_type")

        if chart_type not in ALLOWED_CHART_TYPES:
            return False, f"Chart type not allowed: {chart_type}"

        if not visual.get("query_intent"):
            return False, f"Visual '{visual.get('id', '')}' must include query_intent."

    return True, "Dashboard plan is valid."
