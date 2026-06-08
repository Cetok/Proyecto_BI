import streamlit as st
from chart_generator import render_chart


def extract_single_value(df):
    if df is None or df.empty:
        return None
    return df.iloc[0, 0]


def format_kpi_value(value):
    if value is None:
        return "N/A"
    try:
        numeric_value = float(value)
        if numeric_value >= 1000:
            return f"{numeric_value:,.0f}"
        if numeric_value % 1 == 0:
            return f"{numeric_value:,.0f}"
        return f"{numeric_value:,.2f}"
    except Exception:
        return str(value)


def render_kpi_cards(successful_results):
    kpi_items = [item for item in successful_results if item.get("type") == "kpi"]

    if not kpi_items:
        return

    st.subheader("KPIs ejecutivos")
    columns = st.columns(len(kpi_items))

    for col, item in zip(columns, kpi_items):
        df = item.get("dataframe")
        value = extract_single_value(df)
        with col:
            st.metric(label=item.get("title", "KPI"), value=format_kpi_value(value))


def render_visual_sections(successful_results):
    visual_items = [item for item in successful_results if item.get("type") == "visual"]

    if not visual_items:
        return

    st.subheader("Visualizaciones generadas")

    for item in visual_items:
        st.markdown(f"### {item.get('title')}")
        chart_type = item.get("chart_type", "bar")
        df = item.get("dataframe")

        if df is None or df.empty:
            st.warning("No hay datos disponibles para esta visualización.")
            continue

        render_chart(df, chart_type)


def render_sql_audit(execution_results):
    st.subheader("Auditoría SQL")

    for item in execution_results:
        status = item.get("status")
        title = item.get("title")
        item_type = item.get("type", "").upper()

        with st.expander(f"{title} — {item_type} — {status}", expanded=False):
            st.markdown(f"**Intención analítica:** {item.get('query_intent')}")
            st.markdown(f"**Estado:** `{status}`")
            st.markdown(f"**Mensaje:** {item.get('message')}")

            if item.get("sql"):
                st.markdown("**SQL generado y validado:**")
                st.code(item.get("sql"), language="sql")

            df = item.get("dataframe")
            if df is not None:
                st.markdown("**Resultado:**")
                st.dataframe(df, use_container_width=True)


def render_generated_dashboard(plan, execution_results):
    successful_results = [item for item in execution_results if item.get("status") == "SUCCESS"]
    failed_results = [item for item in execution_results if item.get("status") != "SUCCESS"]

    st.divider()
    st.header(plan.get("dashboard_title", "Dashboard generado"))
    st.caption(plan.get("business_goal", ""))

    render_kpi_cards(successful_results)

    st.divider()

    render_visual_sections(successful_results)

    st.divider()

    st.subheader("Resumen de ejecución")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Componentes ejecutados", len(successful_results))
    with col2:
        st.metric("Componentes fallidos", len(failed_results))

    if failed_results:
        st.warning("Algunos componentes no pudieron ejecutarse.")

    render_sql_audit(execution_results)
