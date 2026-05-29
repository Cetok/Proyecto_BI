from streamlit_echarts import st_echarts


def infer_chart_axes(df, chart_type):
    columns = df.columns.tolist()
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    categorical_cols = df.select_dtypes(exclude="number").columns.tolist()

    # Caso temporal mensual
    if "month_name" in columns:
        x_col = "month_name"

        metric_candidates = [
            col for col in numeric_cols
            if col not in ["year", "month"]
        ]

        if metric_candidates:
            return x_col, metric_candidates[0]

    if "month" in columns:
        x_col = "month"

        metric_candidates = [
            col for col in numeric_cols
            if col not in ["year", "month"]
        ]

        if metric_candidates:
            return x_col, metric_candidates[0]

    # Caso categoría + métrica
    if categorical_cols and numeric_cols:
        return categorical_cols[0], numeric_cols[0]

    # Caso numérico + numérico
    if len(numeric_cols) >= 2:
        return numeric_cols[0], numeric_cols[1]

    # Fallback
    if len(columns) >= 2:
        return columns[0], columns[1]

    return None, None


def render_chart(df, chart_type):
    if df.empty or df.shape[1] < 2:
        return

    x_col, y_col = infer_chart_axes(df, chart_type)

    if not x_col or not y_col:
        return

    categories = df[x_col].astype(str).tolist()
    values = df[y_col].tolist()

    if chart_type == "line":
        options = {
            "tooltip": {"trigger": "axis"},
            "xAxis": {
                "type": "category",
                "data": categories
            },
            "yAxis": {"type": "value"},
            "series": [
                {
                    "data": values,
                    "type": "line",
                    "smooth": True
                }
            ]
        }

    elif chart_type == "pie":
        options = {
            "tooltip": {"trigger": "item"},
            "series": [
                {
                    "type": "pie",
                    "radius": "60%",
                    "data": [
                        {"name": str(row[x_col]), "value": row[y_col]}
                        for _, row in df.iterrows()
                    ]
                }
            ]
        }

    elif chart_type == "scatter":
        options = {
            "tooltip": {"trigger": "item"},
            "xAxis": {"type": "value"},
            "yAxis": {"type": "value"},
            "series": [
                {
                    "type": "scatter",
                    "data": df[[x_col, y_col]].values.tolist()
                }
            ]
        }

    else:
        options = {
            "tooltip": {"trigger": "axis"},
            "xAxis": {
                "type": "category",
                "data": categories
            },
            "yAxis": {"type": "value"},
            "series": [
                {
                    "data": values,
                    "type": "bar"
                }
            ]
        }

    st_echarts(
        options=options,
        height="450px"
    )