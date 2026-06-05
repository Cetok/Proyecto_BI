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
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado con paleta blanco y azul
st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    /* Fondo general */
    .stApp {
        background: linear-gradient(135deg, #f0f4f8 0%, #ffffff 100%);
    }
    
    /* Header principal */
    .header-container {
        background: linear-gradient(135deg, #003f87 0%, #0066cc 100%);
        color: white;
        padding: 40px 20px;
        border-radius: 12px;
        margin-bottom: 30px;
        box-shadow: 0 4px 15px rgba(0, 63, 135, 0.1);
    }
    
    .header-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }
    
    .header-subtitle {
        font-size: 1rem;
        font-weight: 300;
        margin-top: 8px;
        opacity: 0.95;
    }
    
    /* Input y botones */
    .stTextInput > div > div > input {
        border: 2px solid #e0e7ff !important;
        border-radius: 8px !important;
        padding: 12px !important;
        font-size: 1rem !important;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #0066cc !important;
        box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.1) !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #0066cc 0%, #003f87 100%);
        color: white;
        border: none;
        padding: 12px 32px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(0, 102, 204, 0.2);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 102, 204, 0.3);
        background: linear-gradient(135deg, #003f87 0%, #0066cc 100%);
    }
    
    /* Secciones */
    .section-card {
        background: white;
        border-left: 4px solid #0066cc;
        padding: 20px;
        border-radius: 8px;
        margin: 20px 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    .stSubheader {
        color: #003f87 !important;
        font-weight: 700 !important;
        margin-top: 24px !important;
        margin-bottom: 12px !important;
    }
    
    /* Códigos */
    .stCode {
        background: #f5f7fa !important;
        border: 1px solid #e0e7ff !important;
        border-radius: 8px !important;
    }
    
    .stCodeBlock {
        background: #f5f7fa !important;
    }
    
    /* Dataframe */
    .stDataFrame {
        border: 1px solid #e0e7ff !important;
        border-radius: 8px !important;
        overflow: hidden;
    }
    
    /* Mensajes */
    .stSuccess {
        background-color: #ecfdf5 !important;
        color: #065f46 !important;
        border: 1px solid #a7f3d0 !important;
        border-left: 4px solid #10b981 !important;
        border-radius: 8px !important;
    }
    
    .stError {
        background-color: #fef2f2 !important;
        color: #991b1b !important;
        border: 1px solid #fecaca !important;
        border-left: 4px solid #ef4444 !important;
        border-radius: 8px !important;
    }
    
    .stWarning {
        background-color: #fffbeb !important;
        color: #92400e !important;
        border: 1px solid #fde68a !important;
        border-left: 4px solid #f59e0b !important;
        border-radius: 8px !important;
    }
    
    .stInfo {
        background: linear-gradient(135deg, #eff6ff 0%, #f0f9ff 100%);
        color: #003f87 !important;
        border: 1px solid #bfdbfe !important;
        border-left: 4px solid #0066cc !important;
        border-radius: 8px !important;
    }
    
    /* Tabla de resultados */
    [data-testid="stDataFrameResizable"] {
        border: 1px solid #e0e7ff !important;
        border-radius: 8px !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header-container">
    <h1 class="header-title">🔍 GenBI Text-to-SQL MVP</h1>
    <p class="header-subtitle">Pregunta → IA → SQL → Validación → PostgreSQL → Resultado → Interpretación</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([4, 1])

with col1:
    question = st.text_input(
        "Pregunta de negocio",
        placeholder="Ejemplo: ¿Cuál es la venta total por ciudad?",
        key="question_input"
    )

with col2:
    st.markdown("")
    st.markdown("")
    btn = st.button("🚀 Generar", use_container_width=True)

if btn:
    if not question.strip():
        st.warning("✏️ Escribe una pregunta de negocio.")
        st.stop()

    semantic_dictionary = load_semantic_dictionary()
    prompt = build_prompt(question, semantic_dictionary)
    response = generate_sql(prompt)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("💡 Respuesta IA")
    st.code(response, language="sql")
    st.markdown('</div>', unsafe_allow_html=True)

    if response == "UNSAFE_REQUEST":
        st.error("🚫 Solicitud bloqueada: la pregunta intenta modificar o borrar datos.")
        st.stop()

    if response == "OUT_OF_SCOPE":
        st.warning("⚠️ No puedo responder esa pregunta con el Data Mart disponible.")
        st.stop()

    sql = response

    if sql.startswith("SQL_SELECT"):
        sql = sql.replace("SQL_SELECT", "", 1).strip()

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("⚙️ SQL Generado")
    st.code(sql, language="sql")
    st.markdown('</div>', unsafe_allow_html=True)

    is_valid, message = validate_sql(sql, semantic_dictionary)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("✓ Validación SQL")

    if not is_valid:
        st.error(f"❌ {message}")
        st.markdown('</div>', unsafe_allow_html=True)
        st.stop()

    st.success(f"✅ {message}")
    st.markdown('</div>', unsafe_allow_html=True)

    df = run_query(sql)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("📊 Resultado")
    st.dataframe(df, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    business_explanation = explain_result(
        question=question,
        sql=sql,
        df=df
    )

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("🔎 Interpretación de Negocio")
    st.info(business_explanation)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("📈 Visualización")

    chart_type = recommend_chart_type(question, df)
    st.markdown(f"**Tipo sugerido:** `{chart_type}`", unsafe_allow_html=True)
    st.divider()
    render_chart(df, chart_type)
    st.markdown('</div>', unsafe_allow_html=True)