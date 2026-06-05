from streamlit_echarts import st_echarts

COLORS = [
    "#3b82f6", "#8b5cf6", "#06b6d4", "#10b981",
    "#f59e0b", "#ef4444", "#ec4899", "#84cc16"
]

GRADIENT_PAIRS = [
    ("#3b82f6", "#1d4ed8"),
    ("#8b5cf6", "#6d28d9"),
    ("#06b6d4", "#0891b2"),
    ("#10b981", "#059669"),
    ("#f59e0b", "#d97706"),
]


def _grad(top: str, bottom: str) -> dict:
    return {
        "type": "linear", "x": 0, "y": 0, "x2": 0, "y2": 1,
        "colorStops": [
            {"offset": 0, "color": top},
            {"offset": 1, "color": bottom}
        ]
    }


def infer_chart_axes(df, chart_type):
    columns = df.columns.tolist()
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    categorical_cols = df.select_dtypes(exclude="number").columns.tolist()

    if "month_name" in columns:
        candidates = [c for c in numeric_cols if c not in ("year", "month")]
        if candidates:
            return "month_name", candidates[0]

    if "month" in columns:
        candidates = [c for c in numeric_cols if c not in ("year", "month")]
        if candidates:
            return "month", candidates[0]

    if categorical_cols and numeric_cols:
        return categorical_cols[0], numeric_cols[0]

    if len(numeric_cols) >= 2:
        return numeric_cols[0], numeric_cols[1]

    if len(columns) >= 2:
        return columns[0], columns[1]

    return None, None


# Estilos base dark reutilizables
_ANIM = {
    "animation": True,
    "animationDuration": 900,
    "animationEasing": "cubicOut",
    "animationDurationUpdate": 500,
}

_TOOLTIP_AXIS = {
    "trigger": "axis",
    "backgroundColor": "rgba(13,17,23,0.95)",
    "borderColor": "rgba(59,130,246,0.35)",
    "borderWidth": 1,
    "textStyle": {"color": "#e2e8f0", "fontSize": 13, "fontFamily": "Inter"},
    "axisPointer": {"type": "shadow", "shadowStyle": {"color": "rgba(59,130,246,0.06)"}},
}

_TOOLTIP_ITEM = {
    "trigger": "item",
    "backgroundColor": "rgba(13,17,23,0.95)",
    "borderColor": "rgba(59,130,246,0.35)",
    "borderWidth": 1,
    "textStyle": {"color": "#e2e8f0", "fontSize": 13, "fontFamily": "Inter"},
}

_GRID = {"left": "4%", "right": "4%", "bottom": "12%", "top": "10%", "containLabel": True}

_LEGEND = {
    "bottom": 4,
    "textStyle": {"color": "#64748b", "fontSize": 12},
    "icon": "roundRect", "itemWidth": 14, "itemHeight": 8,
}

_X_AXIS_BASE = {
    "axisLine": {"lineStyle": {"color": "rgba(255,255,255,0.08)"}},
    "axisTick": {"show": False},
    "splitLine": {"show": False},
}

_Y_AXIS_BASE = {
    "axisLine": {"show": False},
    "axisTick": {"show": False},
    "splitLine": {"lineStyle": {"color": "rgba(255,255,255,0.05)", "type": "dashed"}},
}


def render_chart(df, chart_type):
    if df.empty or df.shape[1] < 2:
        return

    x_col, y_col = infer_chart_axes(df, chart_type)
    if not x_col or not y_col:
        return

    categories = df[x_col].astype(str).tolist()
    values = df[y_col].tolist()

    if chart_type == "bar":
        options = {
            **_ANIM,
            "backgroundColor": "transparent",
            "tooltip": _TOOLTIP_AXIS,
            "grid": _GRID,
            "xAxis": {
                "type": "category", "data": categories,
                "axisLabel": {
                    "rotate": 30 if len(categories) > 6 else 0,
                    "color": "#64748b", "fontSize": 12,
                },
                **_X_AXIS_BASE,
            },
            "yAxis": {
                "type": "value",
                "axisLabel": {"color": "#64748b", "fontSize": 11},
                **_Y_AXIS_BASE,
            },
            "series": [{
                "name": y_col, "type": "bar",
                "barMaxWidth": 54, "barMinHeight": 4,
                "itemStyle": {
                    "color": _grad(GRADIENT_PAIRS[0][0], GRADIENT_PAIRS[0][1]),
                    "borderRadius": [6, 6, 0, 0],
                },
                "emphasis": {
                    "itemStyle": {
                        "color": _grad(GRADIENT_PAIRS[1][0], GRADIENT_PAIRS[1][1]),
                        "shadowBlur": 14, "shadowColor": "rgba(59,130,246,0.4)",
                    }
                },
                "label": {
                    "show": True, "position": "top",
                    "color": "#64748b", "fontSize": 11, "fontWeight": "600",
                },
                "data": values,
            }],
        }

    elif chart_type == "line":
        options = {
            **_ANIM,
            "backgroundColor": "transparent",
            "tooltip": _TOOLTIP_AXIS,
            "grid": _GRID,
            "legend": _LEGEND,
            "xAxis": {
                "type": "category", "data": categories, "boundaryGap": False,
                "axisLabel": {
                    "rotate": 30 if len(categories) > 8 else 0,
                    "color": "#64748b", "fontSize": 12,
                },
                **_X_AXIS_BASE,
            },
            "yAxis": {
                "type": "value",
                "axisLabel": {"color": "#64748b", "fontSize": 11},
                **_Y_AXIS_BASE,
            },
            "series": [{
                "name": y_col, "type": "line",
                "smooth": True, "symbol": "circle", "symbolSize": 8,
                "lineStyle": {"width": 3, "color": "#3b82f6"},
                "itemStyle": {
                    "color": "#ffffff", "borderColor": "#3b82f6", "borderWidth": 3,
                    "shadowColor": "rgba(59,130,246,0.5)", "shadowBlur": 8,
                },
                "areaStyle": {
                    "color": _grad("rgba(59,130,246,0.22)", "rgba(59,130,246,0.01)")
                },
                "emphasis": {
                    "itemStyle": {
                        "color": "#3b82f6", "borderColor": "white", "borderWidth": 2,
                        "shadowBlur": 18, "shadowColor": "rgba(59,130,246,0.6)",
                    }
                },
                "data": values,
            }],
        }

    elif chart_type == "pie":
        pie_data = [
            {"name": str(row[x_col]), "value": row[y_col]}
            for _, row in df.iterrows()
        ]
        options = {
            **_ANIM,
            "backgroundColor": "transparent",
            "tooltip": {**_TOOLTIP_ITEM, "formatter": "{b}<br/><strong>{c}</strong>  ({d}%)"},
            "legend": {**_LEGEND, "orient": "horizontal", "bottom": 6},
            "color": COLORS,
            "series": [{
                "name": y_col, "type": "pie",
                "radius": ["38%", "68%"],
                "center": ["50%", "46%"],
                "padAngle": 3,
                "itemStyle": {"borderRadius": 6, "borderColor": "#0d1117", "borderWidth": 2},
                "label": {
                    "show": True,
                    "formatter": "{b}\n{d}%",
                    "color": "#94a3b8", "fontSize": 12, "fontWeight": "600",
                },
                "labelLine": {"length": 14, "length2": 8, "smooth": True, "lineStyle": {"color": "#475569"}},
                "emphasis": {
                    "itemStyle": {"shadowBlur": 20, "shadowColor": "rgba(0,0,0,0.5)"},
                    "scale": True, "scaleSize": 6,
                },
                "data": pie_data,
            }],
        }

    elif chart_type == "scatter":
        scatter_data = df[[x_col, y_col]].values.tolist()
        options = {
            **_ANIM,
            "backgroundColor": "transparent",
            "tooltip": _TOOLTIP_ITEM,
            "grid": _GRID,
            "xAxis": {
                "type": "value",
                "name": x_col, "nameLocation": "middle", "nameGap": 30,
                "nameTextStyle": {"color": "#64748b", "fontSize": 12},
                "axisLabel": {"color": "#64748b", "fontSize": 11},
                **{**_X_AXIS_BASE, "axisLine": {"lineStyle": {"color": "rgba(255,255,255,0.08)"}}},
                "splitLine": {"lineStyle": {"color": "rgba(255,255,255,0.05)", "type": "dashed"}},
            },
            "yAxis": {
                "type": "value",
                "name": y_col, "nameLocation": "middle", "nameGap": 44,
                "nameTextStyle": {"color": "#64748b", "fontSize": 12},
                "axisLabel": {"color": "#64748b", "fontSize": 11},
                **_Y_AXIS_BASE,
            },
            "series": [{
                "type": "scatter", "symbolSize": 11,
                "itemStyle": {
                    "color": _grad("#3b82f6", "#8b5cf6"),
                    "opacity": 0.82,
                    "shadowBlur": 8, "shadowColor": "rgba(59,130,246,0.35)",
                },
                "emphasis": {
                    "itemStyle": {"opacity": 1, "shadowBlur": 18, "shadowColor": "rgba(59,130,246,0.6)"}
                },
                "data": scatter_data,
            }],
        }

    else:
        options = {
            **_ANIM,
            "backgroundColor": "transparent",
            "tooltip": _TOOLTIP_AXIS,
            "grid": _GRID,
            "xAxis": {
                "type": "category", "data": categories,
                "axisLabel": {"color": "#64748b"},
                **_X_AXIS_BASE,
            },
            "yAxis": {
                "type": "value",
                "axisLabel": {"color": "#64748b"},
                **_Y_AXIS_BASE,
            },
            "series": [{
                "data": values, "type": "bar",
                "itemStyle": {
                    "color": _grad(GRADIENT_PAIRS[0][0], GRADIENT_PAIRS[0][1]),
                    "borderRadius": [5, 5, 0, 0],
                },
            }],
        }

    st_echarts(options=options, height="480px")
