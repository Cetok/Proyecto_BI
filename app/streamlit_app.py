import sys
import re
from pathlib import Path

import streamlit as st

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

from semantic_context_retriever import retrieve_semantic_context
from dashboard_planner import generate_dashboard_plan
from plan_validator import validate_dashboard_plan
from query_orchestrator import execute_dashboard_plan
from dashboard_renderer import render_generated_dashboard
from dashboard_insight_generator import generate_dashboard_insight


# Convierte markdown a HTML limpio (sin signos raros)
def _inline(text: str) -> str:
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    text = re.sub(r'`(.+?)`', r'<code class="ic">\1</code>', text)
    return text


def md_html(text: str) -> str:
    lines = text.split('\n')
    out = []
    in_list = False
    for line in lines:
        s = line.strip()
        if s.startswith('### '):
            if in_list: out.append('</ul>'); in_list = False
            out.append(f'<h4 class="ei-sub">{_inline(s[4:])}</h4>')
        elif s.startswith('## '):
            if in_list: out.append('</ul>'); in_list = False
            out.append(f'<h3 class="ei-h">{_inline(s[3:])}</h3>')
        elif s.startswith('# '):
            if in_list: out.append('</ul>'); in_list = False
            out.append(f'<h2 class="ei-title">{_inline(s[2:])}</h2>')
        elif re.match(r'^[\*\-] ', s):
            if not in_list: out.append('<ul class="ei-ul">'); in_list = True
            out.append(f'<li>{_inline(s[2:])}</li>')
        elif s == '':
            if in_list: out.append('</ul>'); in_list = False
        else:
            if in_list: out.append('</ul>'); in_list = False
            out.append(f'<p class="ei-p">{_inline(s)}</p>')
    if in_list:
        out.append('</ul>')
    return '\n'.join(out)


st.set_page_config(
    page_title="Streamlit",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── ESTILOS DARK MODE ───────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

  *, *::before, *::after { box-sizing: border-box; }

  /* ── Ocultar chrome de Streamlit y sidebar ── */
  #MainMenu, footer, header { visibility: hidden !important; }
  [data-testid="stDecoration"],
  [data-testid="stSidebar"],
  [data-testid="collapsedControl"] { display: none !important; }

  /* ── Fondo dark ── */
  .stApp,
  [data-testid="stAppViewContainer"],
  [data-testid="stAppViewContainer"] > .main,
  section.main {
    background: #0d1117 !important;
    font-family: 'Inter', -apple-system, sans-serif !important;
  }

  .block-container {
    padding: 2.5rem 3.5rem !important;
    max-width: 1180px !important;
  }

  /* Texto base */
  .stMarkdown p, .stMarkdown li, label { color: #cbd5e1 !important; }

  /* ── HERO ── */
  .hero {
    background: linear-gradient(135deg, #1e3a8a 0%, #1d4ed8 55%, #3b82f6 100%);
    border-radius: 18px;
    padding: 44px 44px 40px;
    margin-bottom: 32px;
    position: relative; overflow: hidden;
    box-shadow: 0 24px 64px rgba(37,99,235,0.45), 0 4px 16px rgba(0,0,0,0.4);
    animation: heroIn 0.65s cubic-bezier(.22,1,.36,1) both;
  }
  .hero::before {
    content:''; position:absolute; top:-50%; right:-5%;
    width:480px; height:480px;
    background: radial-gradient(circle, rgba(255,255,255,0.07) 0%, transparent 65%);
    border-radius:50%;
  }
  .hero::after {
    content:''; position:absolute; bottom:-50%; left:20%;
    width:320px; height:320px;
    background: radial-gradient(circle, rgba(147,197,253,0.1) 0%, transparent 65%);
    border-radius:50%;
  }
  .hero-badge {
    display: inline-block;
    background: rgba(255,255,255,0.14); color: rgba(255,255,255,0.9);
    padding: 4px 14px; border-radius: 20px;
    font-size: 0.73rem; font-weight: 600; letter-spacing: 0.9px; text-transform: uppercase;
    margin-bottom: 14px; border: 1px solid rgba(255,255,255,0.22);
  }
  .hero h1 {
    color: white; font-size: 2.8rem; font-weight: 800;
    line-height: 1.1; letter-spacing: -1px; position: relative; z-index: 1; margin: 0 0 10px;
  }
  .hero h1 span {
    background: linear-gradient(90deg, #93c5fd 0%, #bfdbfe 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  }
  .hero-sub {
    color: rgba(255,255,255,0.72); font-size: 1rem; line-height: 1.65;
    position: relative; z-index: 1; max-width: 620px;
  }
  .hero-pills { display: flex; gap: 10px; margin-top: 22px; flex-wrap: wrap; position: relative; z-index: 1; }
  .hero-pill {
    background: rgba(255,255,255,0.11); color: rgba(255,255,255,0.8);
    padding: 5px 14px; border-radius: 20px;
    font-size: 0.79rem; font-weight: 500; border: 1px solid rgba(255,255,255,0.18);
  }

  /* ── QUERY BOX ── */
  .query-container {
    background: #161b27;
    border-radius: 14px;
    padding: 24px 28px 20px;
    box-shadow: 0 4px 24px rgba(0,0,0,0.35);
    border: 1px solid rgba(255,255,255,0.07);
    margin-bottom: 28px;
    animation: fadeUp 0.5s cubic-bezier(.22,1,.36,1) 0.12s both;
  }
  .query-label {
    font-size: 0.74rem; font-weight: 700;
    color: #475569; text-transform: uppercase; letter-spacing: 0.9px; margin-bottom: 12px;
  }

  /* ── INPUT ── */
  .stTextInput > div > div > input {
    background: #1e293b !important;
    border: 1.5px solid rgba(255,255,255,0.09) !important;
    border-radius: 10px !important;
    padding: 13px 16px !important;
    font-size: 1rem !important;
    font-family: 'Inter', sans-serif !important;
    color: #e2e8f0 !important;
    transition: all 0.2s ease !important;
  }
  .stTextInput > div > div > input:focus {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.15) !important;
    outline: none !important;
  }
  .stTextInput > div > div > input::placeholder { color: #475569 !important; }

  /* ── BOTÓN ── */
  .stButton > button {
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
    color: white !important; border: none !important;
    padding: 13px 22px !important; border-radius: 10px !important;
    font-size: 0.93rem !important; font-weight: 700 !important;
    font-family: 'Inter', sans-serif !important;
    transition: all 0.25s ease !important;
    box-shadow: 0 4px 18px rgba(37,99,235,0.45) !important;
    width: 100% !important;
  }
  .stButton > button:hover {
    background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(37,99,235,0.55) !important;
  }
  .stButton > button:active {
    transform: translateY(0) !important;
    box-shadow: 0 2px 8px rgba(37,99,235,0.3) !important;
  }

  /* ── CARDS ── */
  .card {
    background: #161b27;
    border-radius: 14px;
    padding: 20px 24px;
    margin: 16px 0 6px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    border: 1px solid rgba(255,255,255,0.06);
    animation: fadeUp 0.45s cubic-bezier(.22,1,.36,1) both;
    transition: box-shadow 0.25s ease, border-color 0.25s ease;
  }
  .card:hover {
    border-color: rgba(59,130,246,0.22);
    box-shadow: 0 8px 32px rgba(0,0,0,0.4), 0 0 0 1px rgba(59,130,246,0.12);
  }
  .card-header {
    display: flex; align-items: center; gap: 12px;
  }
  .card-icon {
    width: 36px; height: 36px; border-radius: 9px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem; flex-shrink: 0;
  }
  .card-icon.blue   { background: rgba(59,130,246,0.15); }
  .card-icon.green  { background: rgba(34,197,94,0.12); }
  .card-icon.purple { background: rgba(139,92,246,0.15); }
  .card-icon.orange { background: rgba(251,146,60,0.15); }
  .card-title { font-size: 0.95rem; font-weight: 700; color: #e2e8f0; flex: 1; }
  .card-badge {
    padding: 3px 11px; border-radius: 20px;
    font-size: 0.68rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.7px;
  }
  .badge-success { background: rgba(34,197,94,0.12);  color: #4ade80; }
  .badge-info    { background: rgba(59,130,246,0.12);  color: #60a5fa; }
  .badge-warning { background: rgba(251,191,36,0.12);  color: #fbbf24; }
  .badge-error   { background: rgba(239,68,68,0.12);   color: #f87171; }

  /* ── MÉTRICAS ── */
  .metrics-row { display: flex; gap: 14px; margin: 6px 0 20px; animation: fadeUp 0.4s cubic-bezier(.22,1,.36,1) both; }
  .metric-card {
    flex: 1;
    background: linear-gradient(135deg, #161b27 0%, #1a2240 100%);
    border: 1px solid rgba(59,130,246,0.18);
    border-radius: 12px; padding: 16px; text-align: center;
    transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s;
  }
  .metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(59,130,246,0.18);
    border-color: rgba(59,130,246,0.38);
  }
  .metric-value { font-size: 2rem; font-weight: 800; color: #60a5fa; line-height: 1; margin-bottom: 5px; }
  .metric-label { font-size: 0.69rem; font-weight: 600; color: #475569; text-transform: uppercase; letter-spacing: 0.6px; }

  /* ── INTERPRETACIÓN DE NEGOCIO ── */
  .explanation-wrap {
    background: linear-gradient(135deg, #0c1929 0%, #111827 100%);
    border: 1px solid rgba(59,130,246,0.18);
    border-left: 3px solid #3b82f6;
    border-radius: 10px;
    padding: 22px 26px;
    margin-top: 16px;
  }
  .ei-title { font-size: 1.1rem; font-weight: 800; color: #e2e8f0; margin: 0 0 12px; line-height: 1.3; }
  .ei-h     { font-size: 1rem;   font-weight: 700; color: #cbd5e1; margin: 16px 0 6px; padding-top: 4px; border-top: 1px solid rgba(255,255,255,0.05); }
  .ei-sub   { font-size: 0.9rem; font-weight: 600; color: #94a3b8; margin: 10px 0 4px; }
  .ei-p     { font-size: 0.92rem; color: #94a3b8; line-height: 1.8; margin: 6px 0; }
  .ei-ul    { margin: 6px 0 10px 18px; padding: 0; }
  .ei-ul li { font-size: 0.92rem; color: #94a3b8; line-height: 1.78; margin: 5px 0; }
  .ei-ul li::marker { color: #3b82f6; }
  .ei-ul li strong, .ei-p strong { color: #93c5fd; font-weight: 700; }
  .ei-ul li em,     .ei-p em     { color: #c4b5fd; font-style: italic; }
  .ic {
    background: rgba(59,130,246,0.15);
    padding: 2px 7px; border-radius: 4px;
    font-size: 0.85em; color: #93c5fd;
    font-family: 'Fira Code', 'Cascadia Code', monospace;
  }

  /* ── CHIP GRÁFICO ── */
  .chart-chip {
    display: inline-flex; align-items: center; gap: 7px;
    background: rgba(59,130,246,0.1);
    color: #60a5fa; padding: 7px 18px; border-radius: 22px;
    font-size: 0.8rem; font-weight: 700;
    border: 1px solid rgba(59,130,246,0.22); margin: 14px 0 16px;
    text-transform: uppercase; letter-spacing: 0.6px;
  }

  /* ── MENSAJES ── */
  [data-testid="stSuccess"] {
    background: rgba(34,197,94,0.07)  !important;
    border: 1px solid rgba(34,197,94,0.18) !important;
    border-left: 3px solid #16a34a !important;
    border-radius: 10px !important;
  }
  [data-testid="stSuccess"] * { color: #4ade80 !important; }
  [data-testid="stError"] {
    background: rgba(239,68,68,0.07) !important;
    border: 1px solid rgba(239,68,68,0.18) !important;
    border-left: 3px solid #dc2626 !important;
    border-radius: 10px !important;
  }
  [data-testid="stError"] * { color: #f87171 !important; }
  [data-testid="stWarning"] {
    background: rgba(234,179,8,0.07) !important;
    border: 1px solid rgba(234,179,8,0.18) !important;
    border-left: 3px solid #ca8a04 !important;
    border-radius: 10px !important;
  }
  [data-testid="stWarning"] * { color: #fbbf24 !important; }

  /* ── CODE / DATAFRAME ── */
  .stCode, [data-testid="stCodeBlock"] {
    border-radius: 10px !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    overflow: hidden !important;
    margin-top: 6px !important;
  }
  [data-testid="stDataFrameResizable"],
  [data-testid="stDataFrame"] {
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 10px !important; overflow: hidden !important;
    margin-top: 6px !important;
  }

  /* ── SPINNER ── */
  [data-testid="stSpinner"] > div { color: #60a5fa !important; }

  /* ── ANIMACIONES ── */
  @keyframes heroIn {
    from { opacity: 0; transform: translateY(-20px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(14px); }
    to   { opacity: 1; transform: translateY(0); }
  }
</style>
""", unsafe_allow_html=True)

# ─── HERO ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-badge">IA · SQL · Business Intelligence</div>
  <h1>GenBI <span>Text-to-SQL</span></h1>
  <p class="hero-sub">
    Convierte preguntas en lenguaje natural a consultas SQL ejecutadas sobre PostgreSQL —
    con validación automática, interpretación de negocio y visualización inteligente.
  </p>
  <div class="hero-pills">
    <span class="hero-pill">🤖 Claude AI</span>
    <span class="hero-pill">🐘 PostgreSQL</span>
    <span class="hero-pill">📊 Apache ECharts</span>
    <span class="hero-pill">🔒 Validación SQL</span>
    <span class="hero-pill">🔎 Explicación IA</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── TABS ─────────────────────────────────────────────────────────────────────
tab_single, tab_dashboard = st.tabs(["💬 Pregunta Individual", "📊 Dashboard Generator"])

# ─── TAB 1: PREGUNTA INDIVIDUAL ───────────────────────────────────────────────
with tab_single:
    st.markdown('<div class="query-container">', unsafe_allow_html=True)
    st.markdown('<div class="query-label">💬 Escribe tu pregunta de negocio</div>', unsafe_allow_html=True)

    col_q, col_btn = st.columns([5, 1])
    with col_q:
        question = st.text_input(
            label="question",
            label_visibility="collapsed",
            placeholder="Ej: ¿Cuáles son los comercios con más transacciones fraudulentas este año?",
            key="question_input"
        )
    with col_btn:
        btn = st.button("🔍 Consultar", use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

    if btn:
        if not question.strip():
            st.warning("✏️ Escribe una pregunta antes de continuar.")
            st.stop()

        # 1 — Generar SQL
        with st.spinner("🤖 Generando SQL con IA…"):
            semantic_dictionary = load_semantic_dictionary()
            prompt = build_prompt(question, semantic_dictionary)
            response = generate_sql(prompt)

        st.markdown("""
        <div class="card">
          <div class="card-header">
            <div class="card-icon blue">💡</div>
            <div class="card-title">Respuesta de la IA</div>
            <span class="card-badge badge-info">GENERADO</span>
          </div>
        </div>""", unsafe_allow_html=True)
        st.code(response, language="sql")

        if response == "UNSAFE_REQUEST":
            st.error("🚫 **Solicitud bloqueada** — La pregunta intenta modificar o eliminar datos del sistema.")
            st.stop()
        if response == "OUT_OF_SCOPE":
            st.warning("⚠️ **Fuera de alcance** — Esta pregunta no puede responderse con el Data Mart disponible.")
            st.stop()

        sql = response.replace("SQL_SELECT", "", 1).strip() if response.startswith("SQL_SELECT") else response

        # 2 — SQL limpio
        st.markdown("""
        <div class="card">
          <div class="card-header">
            <div class="card-icon blue">⚙️</div>
            <div class="card-title">SQL Generado</div>
            <span class="card-badge badge-info">SQL</span>
          </div>
        </div>""", unsafe_allow_html=True)
        st.code(sql, language="sql")

        # 3 — Validación
        is_valid, message = validate_sql(sql, semantic_dictionary)

        icon_c = "green" if is_valid else "orange"
        badge_c = "badge-success" if is_valid else "badge-error"
        badge_t = "VÁLIDO" if is_valid else "INVÁLIDO"

        st.markdown(f"""
        <div class="card">
          <div class="card-header">
            <div class="card-icon {icon_c}">✓</div>
            <div class="card-title">Validación SQL</div>
            <span class="card-badge {badge_c}">{badge_t}</span>
          </div>
        </div>""", unsafe_allow_html=True)

        if not is_valid:
            st.error(f"❌ {message}")
            st.stop()
        st.success(f"✅ {message}")

        # 4 — Ejecutar
        with st.spinner("🐘 Ejecutando en PostgreSQL…"):
            df = run_query(sql)

        st.markdown(f"""
        <div class="metrics-row">
          <div class="metric-card">
            <div class="metric-value">{len(df):,}</div>
            <div class="metric-label">Filas devueltas</div>
          </div>
          <div class="metric-card">
            <div class="metric-value">{df.shape[1]}</div>
            <div class="metric-label">Columnas</div>
          </div>
          <div class="metric-card">
            <div class="metric-value">{len(df) * df.shape[1]:,}</div>
            <div class="metric-label">Celdas totales</div>
          </div>
        </div>""", unsafe_allow_html=True)

        st.markdown("""
        <div class="card">
          <div class="card-header">
            <div class="card-icon blue">📊</div>
            <div class="card-title">Resultado de la Consulta</div>
            <span class="card-badge badge-success">EJECUTADO</span>
          </div>
        </div>""", unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True, hide_index=True)

        # 5 — Interpretación de negocio
        with st.spinner("🔎 Generando interpretación de negocio…"):
            business_explanation = explain_result(question=question, sql=sql, df=df)

        expl_html = md_html(business_explanation)
        st.markdown(f"""
        <div class="card">
          <div class="card-header">
            <div class="card-icon purple">🔎</div>
            <div class="card-title">Interpretación de Negocio</div>
            <span class="card-badge badge-info">IA</span>
          </div>
          <div class="explanation-wrap">
            {expl_html}
          </div>
        </div>""", unsafe_allow_html=True)

        # 6 — Visualización
        with st.spinner("📈 Generando visualización…"):
            chart_type = recommend_chart_type(question, df)

        ICONS  = {"bar": "📊", "line": "📈", "pie": "🥧", "scatter": "🔵"}
        LABELS = {"bar": "Barras", "line": "Línea", "pie": "Pastel", "scatter": "Dispersión"}

        st.markdown(f"""
        <div class="card">
          <div class="card-header">
            <div class="card-icon orange">📈</div>
            <div class="card-title">Visualización Inteligente</div>
            <span class="card-badge badge-info">ECHARTS</span>
          </div>
          <div class="chart-chip">
            {ICONS.get(chart_type,"📊")}&nbsp;
            Gráfico de {LABELS.get(chart_type, chart_type).upper()}
            &nbsp;— recomendado por IA
          </div>
        </div>""", unsafe_allow_html=True)
        render_chart(df, chart_type)

# ─── TAB 2: DASHBOARD GENERATOR ───────────────────────────────────────────────
with tab_dashboard:
    st.markdown('<div class="query-container">', unsafe_allow_html=True)
    st.markdown('<div class="query-label">📊 Pregunta ejecutiva de negocio</div>', unsafe_allow_html=True)

    dashboard_question = st.text_area(
        label="dashboard_question",
        label_visibility="collapsed",
        placeholder=(
            "Ej: Genera un dashboard ejecutivo para analizar el desempeño comercial general, "
            "considerando venta total, ticket promedio, número de ventas, evolución mensual, "
            "categorías principales y ciudades con mayor contribución."
        ),
        height=100,
        key="dashboard_question_input"
    )

    btn_dash = st.button("📊 Generar Dashboard", use_container_width=False, key="btn_dashboard")
    st.markdown('</div>', unsafe_allow_html=True)

    if btn_dash:
        if not dashboard_question.strip():
            st.warning("✏️ Escribe una pregunta ejecutiva antes de continuar.")
            st.stop()

        semantic_dictionary = load_semantic_dictionary()

        # 1 — Contexto semántico
        with st.spinner("🔎 Recuperando contexto semántico…"):
            semantic_context = retrieve_semantic_context(dashboard_question)

        with st.expander("Contexto semántico recuperado", expanded=False):
            st.markdown(semantic_context)

        # 2 — Plan analítico
        with st.spinner("🤖 Generando plan analítico…"):
            dashboard_plan = generate_dashboard_plan(
                question=dashboard_question,
                semantic_dictionary=semantic_dictionary,
                semantic_context=semantic_context
            )

        st.markdown("""
        <div class="card">
          <div class="card-header">
            <div class="card-icon blue">🗺️</div>
            <div class="card-title">Plan generado por la IA</div>
            <span class="card-badge badge-info">JSON</span>
          </div>
        </div>""", unsafe_allow_html=True)
        st.json(dashboard_plan)

        # 3 — Validación del plan
        is_valid_plan, plan_message = validate_dashboard_plan(dashboard_plan, semantic_dictionary)

        badge_p = "badge-success" if is_valid_plan else "badge-error"
        badge_t_p = "VÁLIDO" if is_valid_plan else "INVÁLIDO"
        icon_p = "green" if is_valid_plan else "orange"

        st.markdown(f"""
        <div class="card">
          <div class="card-header">
            <div class="card-icon {icon_p}">✓</div>
            <div class="card-title">Validación del Plan</div>
            <span class="card-badge {badge_p}">{badge_t_p}</span>
          </div>
        </div>""", unsafe_allow_html=True)

        if not is_valid_plan:
            st.error(f"❌ {plan_message}")
            st.stop()
        st.success(f"✅ {plan_message}")

        # 4 — Lectura pedagógica del plan
        st.markdown("""
        <div class="card">
          <div class="card-header">
            <div class="card-icon purple">📋</div>
            <div class="card-title">Lectura del Plan</div>
            <span class="card-badge badge-info">ESTRUCTURA</span>
          </div>
        </div>""", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**KPIs propuestos**")
            for kpi in dashboard_plan.get("kpis", []):
                st.markdown(f"- **{kpi.get('title')}** `{kpi.get('metric')}`")
                st.caption(kpi.get("query_intent", ""))
        with col2:
            st.markdown("**Visualizaciones propuestas**")
            for visual in dashboard_plan.get("visuals", []):
                st.markdown(f"- **{visual.get('title')}** — `{visual.get('chart_type')}`")
                st.caption(visual.get("query_intent", ""))

        # 5 — Ejecución del plan
        with st.spinner("🐘 Generando y ejecutando múltiples consultas SQL…"):
            execution_results = execute_dashboard_plan(dashboard_plan, semantic_dictionary)

        render_generated_dashboard(plan=dashboard_plan, execution_results=execution_results)

        # 6 — Insight ejecutivo
        st.divider()
        st.markdown("""
        <div class="card">
          <div class="card-header">
            <div class="card-icon purple">🔎</div>
            <div class="card-title">Insight Ejecutivo</div>
            <span class="card-badge badge-info">IA</span>
          </div>
        </div>""", unsafe_allow_html=True)

        with st.spinner("🔎 Generando insight ejecutivo…"):
            dashboard_insight = generate_dashboard_insight(
                question=dashboard_question,
                dashboard_plan=dashboard_plan,
                execution_results=execution_results,
                semantic_context=semantic_context
            )

        insight_html = md_html(dashboard_insight)
        st.markdown(f'<div class="explanation-wrap">{insight_html}</div>', unsafe_allow_html=True)
