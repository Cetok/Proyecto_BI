import sys
from pathlib import Path

import streamlit as st

# Permite importar módulos desde /src
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = PROJECT_ROOT / "src"
sys.path.append(str(SRC_PATH))

from db import run_query
from semantic_loader import load_semantic_dictionary
from prompt_builder import build_prompt
from llm_client import generate_sql
from sql_validator import validate_sql
from business_explainer import explain_result
from chart_recommender import recommend_chart_type
from chart_generator import render_chart


st.set_page_config(
    page_title="GenBI Text-to-SQL MVP",
    layout="wide"
)

st.title("GenBI Text-to-SQL MVP")
st.caption("Pregunta → IA → SQL → Validación → PostgreSQL → Resultado → Interpretación")

question = st.text_input(
    "Pregunta de negocio",
    placeholder="Ejemplo: ¿Cuál es la venta total por ciudad?"
)

if st.button("Generar consulta"):
    if not question.strip():
        st.warning("Escribe una pregunta de negocio.")
        st.stop()

    semantic_dictionary = load_semantic_dictionary()
    prompt = build_prompt(question, semantic_dictionary)
    response = generate_sql(prompt)

    st.subheader("Respuesta IA")
    st.code(response)

    if response == "UNSAFE_REQUEST":
        st.error("Solicitud bloqueada: la pregunta intenta modificar o borrar datos.")
        st.stop()

    if response == "OUT_OF_SCOPE":
        st.warning("No puedo responder esa pregunta con el Data Mart disponible.")
        st.stop()

    sql = response

    if sql.startswith("SQL_SELECT"):
        sql = sql.replace("SQL_SELECT", "", 1).strip()

    st.subheader("SQL generado")
    st.code(sql, language="sql")

    is_valid, message = validate_sql(sql, semantic_dictionary)

    st.subheader("Validación SQL")

    if not is_valid:
        st.error(message)
        st.stop()

    st.success(message)

    df = run_query(sql)

    st.subheader("Resultado")
    st.dataframe(df, use_container_width=True)

    business_explanation = explain_result(
        question=question,
        sql=sql,
        df=df
    )

    st.subheader("Interpretación de negocio")
    st.info(business_explanation)
    st.subheader("Visualización")

    chart_type = recommend_chart_type(question, df)
    st.subheader(f"Visualización sugerida: {chart_type}")
    render_chart(df, chart_type)
        