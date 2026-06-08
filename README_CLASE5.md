# Clase 5 — AI Dashboard Generator con GenBI

## Resumen del avance

En la Clase 5 se evolucionó el MVP de GenBI desde un sistema de pregunta individual hacia un **generador automático de dashboards ejecutivos** completo, gobernado y trazable.

El flujo anterior (Clases 1–4) era:

```
Pregunta → SQL → Validación → PostgreSQL → Resultado → Explicación → Visualización
```

El flujo implementado en la Clase 5:

```
Pregunta ejecutiva
→ Contexto semántico (RAG-lite)
→ Dashboard Planner (JSON)
→ Plan Validator
→ Query Orchestrator (múltiples SQL)
→ SQL Validator (por cada componente)
→ PostgreSQL
→ Dashboard Renderer (KPIs + Gráficos + Auditoría)
→ Dashboard Insight Generator (lectura ejecutiva IA)
```

---

## Dominio: Detección de Fraude en Comercios

El Data Mart utilizado está orientado a la detección de fraude en transacciones financieras de pequeños comercios.

### Modelo dimensional

| Tabla | Descripción |
|---|---|
| `fact_transaccion` | Tabla de hechos — una fila por transacción financiera |
| `dim_cliente` | Clientes (género, edad, rango etario) |
| `dim_comercio` | Comercios (nombre, categoría, país) |
| `dim_tarjeta` | Tarjetas de pago (marca, tipo, banco emisor) |
| `dim_tiempo` | Tiempo (año, mes, día, franja horaria, fin de semana) |
| `dim_ubicacion` | Ubicación (ciudad, región, zona de riesgo) |

### Métricas oficiales del diccionario semántico

| Métrica | Cálculo |
|---|---|
| `total_transacciones` | `COUNT(DISTINCT fact_transaccion.trans_num)` |
| `monto_total` | `SUM(fact_transaccion.monto_transaccion)` |
| `transacciones_fraude` | `SUM(CASE WHEN fraude_flag = true THEN 1 ELSE 0 END)` |
| `tasa_fraude` | `ROUND(fraudes * 100.0 / COUNT(*), 2)` |
| `monto_fraudulento_total` | `SUM(fact_transaccion.monto_fraudulento)` |
| `monto_promedio_transaccion` | `ROUND(AVG(fact_transaccion.monto_transaccion), 2)` |

---

## Archivos nuevos creados en Clase 5

### `knowledge_base/semantic_rules.md`

Base de conocimiento semántico curado en Markdown. Funciona como la capa RAG-lite del sistema.

Contiene:
- Cómo calcular cada métrica oficial.
- Qué columnas usar para análisis temporal, geográfico, por comercio, cliente y tarjeta.
- Qué tipo de gráfico recomendar según el análisis.
- Reglas de gobernanza del sistema.

Ejemplo de regla documentada:
```
total_transacciones must be calculated using COUNT(DISTINCT fact_transaccion.trans_num).
```

En una arquitectura enterprise, esta capa puede evolucionar hacia vector database, data catalog, semantic layer o knowledge graph.

---

### `src/semantic_context_retriever.py`

Módulo de recuperación de contexto semántico.

Carga los documentos curados desde `knowledge_base/` y los inyecta como contexto adicional al Dashboard Planner.

```python
def retrieve_semantic_context(question: str) -> str
```

Actualmente carga `semantic_rules.md`. En producción, este módulo podría usar embeddings + ChromaDB para recuperación semántica real.

---

### `src/dashboard_planner.py`

Módulo que convierte una pregunta ejecutiva en un **plan analítico JSON estructurado**.

El planner **no genera SQL**. Solo define la intención analítica.

Funciones:
- `build_dashboard_planner_prompt(question, semantic_dictionary, semantic_context)` — construye el prompt desde la plantilla.
- `generate_dashboard_plan(question, semantic_dictionary, semantic_context)` — llama al LLM y retorna el plan como `dict`.

Prompt utilizado: `prompts/dashboard_planner_prompt.txt`

Ejemplo de salida:
```json
{
  "status": "OK",
  "dashboard_title": "Dashboard Ejecutivo de Fraude",
  "business_goal": "Analizar tasa de fraude, monto fraudulento y evolución temporal.",
  "kpis": [
    {
      "id": "kpi_fraudes",
      "title": "Transacciones Fraudulentas",
      "metric": "transacciones_fraude",
      "query_intent": "Contar el total de transacciones fraudulentas registradas."
    }
  ],
  "visuals": [
    {
      "id": "fraude_por_mes",
      "title": "Evolución mensual del fraude",
      "chart_type": "line",
      "query_intent": "Mostrar la cantidad de transacciones fraudulentas agrupadas por mes."
    }
  ],
  "warnings": []
}
```

---

### `src/plan_validator.py`

Módulo de validación del plan analítico. Diferente al SQL Validator: valida la **intención**, no la consulta.

Controles implementados:
- El status debe ser `OK`, `OUT_OF_SCOPE` o `UNSAFE_REQUEST`.
- Si el status es `OUT_OF_SCOPE` o `UNSAFE_REQUEST`, el plan es rechazado.
- No se permiten más de 4 KPIs ni más de 4 visualizaciones.
- Los tipos de gráfico permitidos son: `bar`, `line`, `pie`, `scatter`.
- Las métricas de cada KPI deben existir en el diccionario semántico.
- Cada componente del plan debe incluir `query_intent`.

```python
def validate_dashboard_plan(plan: dict, semantic_dictionary: dict) -> tuple[bool, str]
```

Esto evita que la IA invente métricas o proponga análisis fuera del dominio.

---

### `src/query_orchestrator.py`

Módulo que ejecuta el plan analítico completo reutilizando el flujo Text-to-SQL existente.

Por cada KPI y visualización del plan:

1. Toma la `query_intent`.
2. Llama a `build_prompt()` para construir el prompt SQL.
3. Llama al LLM para generar SQL.
4. Normaliza la respuesta (`SQL_SELECT`, `UNSAFE_REQUEST`, `OUT_OF_SCOPE` o SQL puro).
5. Valida el SQL con `validate_sql()`.
6. Ejecuta el SQL en PostgreSQL con `run_query()`.
7. Almacena el resultado con su estado.

```python
def execute_dashboard_plan(plan: dict, semantic_dictionary: dict) -> list
```

Retorna una lista con el estado de ejecución de cada componente: `SUCCESS`, `FAILED`, `SQL_VALIDATION_FAILED`, `EXECUTION_FAILED`, `UNSAFE_REQUEST`, `OUT_OF_SCOPE`.

---

### `src/dashboard_renderer.py`

Módulo de renderizado del dashboard en Streamlit.

Funciones:
- `render_kpi_cards(successful_results)` — muestra KPIs como métricas de Streamlit con formato numérico automático.
- `render_visual_sections(successful_results)` — renderiza las visualizaciones usando `chart_generator.py` (Apache ECharts).
- `render_sql_audit(execution_results)` — muestra un expander por componente con su SQL, estado y resultado.
- `render_generated_dashboard(plan, execution_results)` — función principal que orquesta el renderizado completo.

La IA propone el tipo de gráfico. El sistema controla el renderizado. No se genera código visual libre.

---

### `src/dashboard_insight_generator.py`

Módulo que genera una **lectura ejecutiva** del dashboard completo.

Recibe:
- Pregunta original del usuario.
- Plan analítico JSON.
- Resultados de ejecución (hasta 10 filas por componente).
- Contexto semántico.

Genera una respuesta estructurada con:
1. Resumen ejecutivo.
2. Hallazgos clave.
3. Riesgos o advertencias.
4. Recomendaciones de negocio.

El prompt incluye reglas estrictas: no inventar datos, no mencionar causas externas no presentes en los resultados, reconocer datos limitados.

Prompt utilizado: `prompts/dashboard_insight_prompt.txt`

---

### `prompts/dashboard_planner_prompt.txt`

Prompt de sistema para el Dashboard Planner.

Define al LLM como un "AI Dashboard Planner especializado en GenBI". Incluye:
- Reglas de qué no puede hacer (inventar tablas, métricas, columnas, generar SQL).
- Límites: máximo 4 KPIs, máximo 4 visualizaciones.
- Tipos de gráfico permitidos.
- Respuesta esperada: únicamente JSON válido, sin Markdown.
- Variables inyectadas: `{{question}}`, `{{semantic_dictionary}}`, `{{semantic_context}}`.

---

### `prompts/dashboard_insight_prompt.txt`

Prompt de sistema para el Insight Generator.

Define al LLM como "Chief Data & AI Analyst especializado en Business Intelligence". Incluye:
- Reglas de análisis responsable (no inventar, no especular).
- Estructura obligatoria de respuesta.
- Respuesta en español.
- Variables inyectadas: `{{question}}`, `{{dashboard_plan}}`, `{{dashboard_results}}`, `{{semantic_context}}`.

---

## Archivos modificados en Clase 5

### `app/streamlit_app.py`

Se agregó la Tab 2 **"📊 Dashboard Generator"** a la aplicación existente.

Flujo implementado en la nueva pestaña:
1. El usuario ingresa una pregunta ejecutiva en un `st.text_area`.
2. El sistema recupera el contexto semántico con `retrieve_semantic_context()`.
3. Se muestra el contexto en un expander colapsado.
4. El Dashboard Planner genera el plan JSON con `generate_dashboard_plan()`.
5. El plan se muestra con `st.json()`.
6. El Plan Validator valida el plan con `validate_dashboard_plan()`.
7. Se muestra la lectura pedagógica del plan (KPIs y visualizaciones propuestas en dos columnas).
8. El Query Orchestrator ejecuta todas las consultas con `execute_dashboard_plan()`.
9. El Dashboard Renderer muestra el dashboard generado con `render_generated_dashboard()`.
10. El Insight Generator genera la lectura ejecutiva con `generate_dashboard_insight()`.

La Tab 1 (Pregunta Individual) no fue modificada.

Además se agregaron los imports de los nuevos módulos:
```python
from semantic_context_retriever import retrieve_semantic_context
from dashboard_planner import generate_dashboard_plan
from plan_validator import validate_dashboard_plan
from query_orchestrator import execute_dashboard_plan
from dashboard_renderer import render_generated_dashboard
from dashboard_insight_generator import generate_dashboard_insight
```

---

### `src/llm_client.py`

Se agregó la función `generate_text()` para el Dashboard Insight Generator.

```python
def generate_text(prompt: str) -> str
```

Utiliza el sistema: `"Eres un analista ejecutivo de Business Intelligence. Genera explicaciones claras, prudentes y basadas únicamente en los datos proporcionados."`

Con `max_tokens=2048`.

Las funciones `generate_sql()` y `generate_json()` ya existían y no fueron modificadas.

---

## Stack tecnológico completo

| Componente | Tecnología |
|---|---|
| Base de datos | PostgreSQL |
| Backend | Python |
| Conexión DB | SQLAlchemy + psycopg2 |
| LLM | Claude (Anthropic) — `claude-sonnet-4-6` |
| Interface | Streamlit |
| Visualización | Apache ECharts + streamlit-echarts |
| Contexto semántico | Markdown curado (RAG-lite) |
| Formato del plan | JSON |

---

## Arquitectura completa de la Clase 5

```
Usuario
  |
  v
[Streamlit — Tab: Dashboard Generator]
  |
  v
retrieve_semantic_context()
  ↳ Carga knowledge_base/semantic_rules.md
  |
  v
generate_dashboard_plan()
  ↳ build_dashboard_planner_prompt()
  ↳ LLM (generate_json)
  ↳ Retorna plan dict
  |
  v
validate_dashboard_plan()
  ↳ Valida status
  ↳ Valida límites (4 KPIs, 4 visuals)
  ↳ Valida métricas contra semantic_dictionary
  ↳ Valida chart_types permitidos
  |
  v
execute_dashboard_plan()
  ↳ Por cada KPI y visual del plan:
      ↳ build_prompt(query_intent)
      ↳ generate_sql()
      ↳ normalize_sql_response()
      ↳ validate_sql()
      ↳ run_query()
      ↳ Almacena resultado con status
  |
  v
render_generated_dashboard()
  ↳ render_kpi_cards()
  ↳ render_visual_sections() → render_chart()
  ↳ render_sql_audit()
  |
  v
generate_dashboard_insight()
  ↳ build_dashboard_insight_prompt()
  ↳ LLM (generate_text)
  ↳ Retorna lectura ejecutiva
```

---

## Componentes reutilizados del MVP anterior

La Clase 5 no reemplazó el MVP. Lo extendió. Los siguientes módulos se reutilizaron sin modificación:

| Módulo | Función |
|---|---|
| `src/db.py` | Conexión a PostgreSQL y ejecución de consultas |
| `src/semantic_loader.py` | Carga del `semantic_dictionary.json` |
| `src/prompt_builder.py` | Construcción del prompt Text-to-SQL |
| `src/sql_validator.py` | Validación determinista del SQL generado |
| `src/business_explainer.py` | Explicación de negocio para pregunta individual |
| `src/chart_recommender.py` | Recomendación de tipo de gráfico |
| `src/chart_generator.py` | Renderizado de gráficos con Apache ECharts |
| `semantic/semantic_dictionary.json` | Contrato semántico del Data Mart |

---

## Gobernanza y guardrails implementados

El sistema mantiene múltiples capas de control:

| Capa | Responsabilidad |
|---|---|
| Prompt del Planner | No generar SQL, no inventar tablas ni métricas |
| Plan Validator | Validar intención antes de generar cualquier SQL |
| SQL Validator | Validar cada SQL generada por el orquestador |
| Controlled Renderer | La IA propone gráficos, el sistema renderiza |
| Insight Guardrails | No inventar datos, no especular, solo los resultados reales |
| SQL Audit | Trazabilidad completa de cada consulta generada y ejecutada |

Principio rector de todo el bloque GenBI:

```
La IA propone.
El sistema valida.
El sistema ejecuta.
El sistema renderiza.
La IA explica — solo con base en los resultados reales.
```

---

## Cómo ejecutar el proyecto

### 1. Activar entorno virtual

Windows:
```bash
.venv\Scripts\activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

Crear `.env` basado en `.env.example`:
```env
ANTHROPIC_API_KEY=tu_api_key
ANTHROPIC_MODEL=claude-sonnet-4-6

DB_HOST=localhost
DB_PORT=5432
DB_NAME=genbi_dm
DB_USER=postgres
DB_PASSWORD=postgres
```

### 4. Levantar la aplicación

```bash
python -m streamlit run app/streamlit_app.py
```

---

## Ejemplo de pregunta ejecutiva para el Dashboard Generator

```
Genera un dashboard ejecutivo para analizar el desempeño comercial general,
considerando venta total, ticket promedio, número de ventas, evolución mensual,
categorías principales y ciudades con mayor contribución.
```

El sistema generará automáticamente:
- KPIs: total de transacciones, monto total, transacciones de fraude, tasa de fraude.
- Visualización de evolución mensual de fraude (línea).
- Visualización de fraude por categoría de comercio (barras).
- Visualización de monto fraudulento por ciudad (barras).
- Visualización de distribución por tipo de tarjeta (pie).
- Auditoría SQL de cada componente.
- Insight ejecutivo generado por IA.

---

## Limitaciones conocidas del MVP académico

- El RAG es simple: carga documentos Markdown, no usa embeddings ni vector database.
- No hay autenticación de usuarios ni control de permisos.
- No hay row-level security.
- No hay caché de resultados ni control de costes del LLM.
- No hay monitoreo de calidad analítica.
- No hay despliegue cloud.

Estas limitaciones son intencionales para mantener el proyecto pedagógicamente comprensible.

---

## Evolución del bloque GenBI

| Clase | Logro |
|---|---|
| Clase 1 | Fundamentos de GenBI, semántica y gobernanza |
| Clase 2 | SQL válido ≠ SQL correcto |
| Clase 3 | MVP técnico de Text-to-SQL controlado |
| Clase 4 | App Streamlit con explicación de negocio y visualización IA |
| **Clase 5** | **Generador de dashboards ejecutivos con planner, RAG-lite, orquestador, renderer e insight** |
