# Clase 5 — AI Dashboard Generator con GenBI

## 1. Objetivo de la clase

En esta clase evolucionamos el MVP de GenBI desde un flujo de pregunta individual hacia un generador automático de dashboards ejecutivos.

Hasta la clase anterior, el sistema seguía este patrón:

```text
Pregunta de negocio
→ Prompt
→ LLM
→ SQL
→ Validación
→ PostgreSQL
→ Resultado
→ Explicación de negocio
→ Visualización
```

En esta clase damos un salto arquitectónico hacia un flujo más cercano a productos reales de Generative BI:

```text
Pregunta ejecutiva
→ Contexto semántico
→ Dashboard Planner
→ Plan JSON
→ Validación del plan
→ Múltiples SQL
→ Validación SQL
→ PostgreSQL
→ KPIs
→ Visualizaciones
→ Auditoría SQL
→ Insight ejecutivo
```

El objetivo no es construir únicamente un chatbot que genera SQL, sino un sistema capaz de transformar una intención de negocio en un producto analítico gobernado.

---

## 2. Principio rector

Durante todo el bloque GenBI se mantiene la misma filosofía:

```text
La IA propone.
El sistema valida.
El sistema ejecuta.
```

En esta clase ampliamos esa filosofía:

```text
La IA planifica.
El sistema valida el plan.
La IA propone SQL.
El sistema valida cada SQL.
El sistema ejecuta.
El sistema renderiza.
La IA explica con base en los resultados.
```

Esto permite mantener control, trazabilidad y gobernanza sobre el uso de IA en analítica.

---

## 3. De Text-to-SQL a Text-to-Analytical Dashboard

El MVP inicial permitía responder preguntas concretas como:

```text
¿Cuál es la venta total por ciudad?
```

Ese flujo genera una única SQL y un único resultado.

En la Clase 5 trabajamos con preguntas ejecutivas más amplias, por ejemplo:

```text
Genera un dashboard ejecutivo para analizar la venta total, ticket promedio y número de ventas por mes, categoría y ciudad.
```

Esta pregunta ya no puede resolverse correctamente con una sola consulta SQL. Requiere planificar varios componentes analíticos:

- KPIs principales.
- Evolución temporal.
- Comparaciones por dimensión.
- Visualizaciones adecuadas.
- Explicación ejecutiva.
- Auditoría de SQL generada.

Por eso introducimos una nueva capa llamada **Dashboard Planner**.

---

## 4. Nueva arquitectura incorporada

La arquitectura final queda de la siguiente forma:

```text
Usuario
  |
  v
Pregunta ejecutiva
  |
  v
Semantic Context Retriever
  |
  v
Dashboard Planner
  |
  v
Plan Validator
  |
  v
Query Orchestrator
  |
  v
SQL Generator
  |
  v
SQL Validator
  |
  v
PostgreSQL
  |
  v
Dashboard Renderer
  |
  v
Dashboard Insight Generator
```

Cada componente tiene una responsabilidad clara.

---

## 5. Componentes nuevos agregados

### 5.1. `semantic_context_retriever.py`

Este módulo implementa una primera versión de RAG-lite.

Su responsabilidad es recuperar contexto semántico desde la carpeta `knowledge_base/`.

En esta clase no usamos todavía una base vectorial. En su lugar, cargamos documentos curados en Markdown para mantener el MVP simple y pedagógico.

Ejemplo de archivos usados:

```text
knowledge_base/
└── semantic_rules.md
```

Este archivo contiene reglas como:

- Cómo calcular ventas.
- Cómo calcular ticket promedio.
- Qué dimensiones usar para análisis temporal.
- Qué gráficos son recomendables según el tipo de análisis.
- Qué límites debe respetar la IA.

Conceptualmente, este componente representa la capa de conocimiento semántico del sistema.

En una arquitectura enterprise, esta capa podría evolucionar hacia:

- Vector database.
- Data catalog.
- Semantic layer.
- Knowledge graph.
- Documentación de dashboards.
- Catálogo de KPIs oficiales.

---

### 5.2. `dashboard_planner.py`

Este módulo convierte una pregunta ejecutiva en un plan analítico estructurado.

El planner no genera SQL.

Su salida es un JSON que describe:

- Título del dashboard.
- Objetivo de negocio.
- KPIs propuestos.
- Visualizaciones propuestas.
- Tipo de gráfico recomendado.
- Intención analítica de cada componente.

Ejemplo conceptual:

```json
{
  "status": "OK",
  "dashboard_title": "Análisis Ejecutivo de Ventas",
  "business_goal": "Analizar la venta total, ticket promedio y número de ventas.",
  "kpis": [
    {
      "id": "total_sales",
      "title": "Venta Total",
      "metric": "total_sales",
      "query_intent": "Calcular la suma del importe total de ventas."
    }
  ],
  "visuals": [
    {
      "id": "sales_by_month",
      "title": "Evolución Mensual de Venta Total",
      "chart_type": "line",
      "query_intent": "Mostrar la venta total agrupada por mes."
    }
  ],
  "warnings": []
}
```

La importancia de este módulo es que separa la planificación analítica de la generación SQL.

Esto permite controlar la intención antes de ejecutar consultas.

---

### 5.3. `plan_validator.py`

Este módulo valida el plan generado por la IA antes de pasar a SQL.

La validación del plan es diferente a la validación SQL.

La validación SQL responde:

```text
¿Esta consulta es segura y válida?
```

La validación del plan responde:

```text
¿Esta intención analítica es permitida y coherente con el contrato semántico?
```

El validador revisa:

- Que el estado sea válido.
- Que no sea `OUT_OF_SCOPE`.
- Que no sea `UNSAFE_REQUEST`.
- Que no existan más de 4 KPIs.
- Que no existan más de 4 visualizaciones.
- Que los tipos de gráficos estén permitidos.
- Que los KPIs existan en el diccionario semántico.
- Que cada componente tenga una intención analítica.

Esto evita que la IA invente métricas o proponga análisis fuera del dominio disponible.

---

### 5.4. `query_orchestrator.py`

Este módulo ejecuta el plan analítico.

A partir del JSON generado por el planner, toma cada KPI y cada visualización y ejecuta el flujo existente de Text-to-SQL:

```text
Intención analítica
→ Prompt Builder
→ LLM
→ SQL
→ SQL Validator
→ PostgreSQL
→ Resultado
```

La diferencia es que ahora este flujo se ejecuta múltiples veces.

Ejemplo:

```text
Plan:
- Venta total
- Ticket promedio
- Número de ventas
- Venta por mes
- Venta por categoría
- Venta por ciudad
- Ticket promedio por mes

Resultado:
7 componentes analíticos
7 SQL generadas
7 SQL validadas
7 resultados ejecutados
```

El orquestador no reemplaza el MVP anterior. Lo reutiliza.

Esto demuestra un principio importante de arquitectura:

```text
No destruimos el MVP.
Lo convertimos en una pieza reutilizable dentro de una arquitectura mayor.
```

---

### 5.5. `dashboard_renderer.py`

Este módulo transforma los resultados ejecutados en un dashboard visual dentro de Streamlit.

Renderiza:

- Título del dashboard.
- Objetivo de negocio.
- KPI cards.
- Visualizaciones automáticas.
- Resumen de ejecución.
- Auditoría SQL.

El renderizado sigue siendo controlado por el sistema.

La IA puede proponer:

```text
line
bar
pie
scatter
```

Pero no genera código visual libre.

El sistema decide cómo renderizar cada gráfico usando componentes permitidos.

Esto mantiene la filosofía:

```text
La IA recomienda.
El sistema renderiza.
```

---

### 5.6. `dashboard_insight_generator.py`

Este módulo genera una lectura ejecutiva del dashboard.

Utiliza:

- Pregunta original.
- Plan analítico.
- Resultados agregados.
- Contexto semántico.

Genera una respuesta estructurada en cuatro partes:

1. Resumen ejecutivo.
2. Hallazgos clave.
3. Riesgos o advertencias.
4. Recomendaciones de negocio.

El prompt incluye reglas estrictas:

- No inventar datos.
- No inventar causas externas.
- No mencionar mercado, competencia o campañas si no están en los datos.
- Reconocer si los datos son limitados.
- Basar el análisis únicamente en los resultados disponibles.

Este componente permite que el dashboard no solo muestre datos, sino que también genere una primera interpretación ejecutiva.

---

## 6. Archivos nuevos creados

Durante esta clase se agregaron los siguientes archivos:

```text
knowledge_base/
└── semantic_rules.md

prompts/
├── dashboard_planner_prompt.txt
└── dashboard_insight_prompt.txt

src/
├── semantic_context_retriever.py
├── dashboard_planner.py
├── plan_validator.py
├── query_orchestrator.py
├── dashboard_renderer.py
└── dashboard_insight_generator.py
```

Además, se modificaron:

```text
app/
└── streamlit_app.py

src/
└── llm_client.py
```

---

## 7. Componentes reutilizados del MVP anterior

La Clase 5 reutiliza los siguientes componentes ya existentes:

```text
src/semantic_loader.py
src/prompt_builder.py
src/llm_client.py
src/sql_validator.py
src/db.py
src/business_explainer.py
src/chart_recommender.py
src/chart_generator.py
semantic/semantic_dictionary.json
```

Esto es importante porque muestra una evolución natural del proyecto.

El sistema anterior no se descarta. Se convierte en la base para construir un producto analítico más completo.

---

## 8. Flujo completo implementado

El flujo final implementado es:

```text
1. El usuario escribe una pregunta ejecutiva.
2. El sistema recupera contexto semántico desde knowledge_base.
3. El Dashboard Planner genera un plan JSON.
4. El Plan Validator valida que el plan sea permitido.
5. El Query Orchestrator toma cada KPI y visualización del plan.
6. Para cada componente:
   - Construye un prompt SQL.
   - Llama al LLM.
   - Normaliza la respuesta.
   - Valida la SQL.
   - Ejecuta la SQL en PostgreSQL.
   - Guarda el resultado.
7. El Dashboard Renderer muestra:
   - KPI cards.
   - Visualizaciones.
   - Resumen de ejecución.
   - Auditoría SQL.
8. El Dashboard Insight Generator genera una lectura ejecutiva.
```

---

## 9. Ejemplo de pregunta usada en la demo

```text
Genera un dashboard ejecutivo para analizar el desempeño comercial general, considerando venta total, ticket promedio, número de ventas, evolución mensual, categorías principales y ciudades con mayor contribución.
```

El sistema genera automáticamente:

- KPI de venta total.
- KPI de ticket promedio.
- KPI de número de ventas.
- Evolución mensual de ventas.
- Venta por categoría.
- Venta por ciudad.
- Evolución mensual del ticket promedio.
- Insight ejecutivo.
- Auditoría SQL.

---

## 10. Diferencia entre SQL válido y producto analítico correcto

En clases anteriores se explicó que SQL válido no necesariamente significa SQL correcto.

En esta clase ampliamos esa idea:

```text
Un dashboard generado tampoco es correcto solo porque se vea bien.
```

Debe cumplir:

- Métricas oficiales.
- Grano correcto.
- Dimensiones permitidas.
- SQL validada.
- Visualización coherente.
- Insight basado en datos.
- Auditoría trazable.

Por eso introducimos validaciones en diferentes niveles:

```text
Plan Validator
SQL Validator
Controlled Chart Renderer
Executive Insight Guardrails
SQL Audit
```

---

## 11. Conceptos clave aprendidos

### Dashboard Planner

Componente que transforma una intención ejecutiva en un plan analítico estructurado.

### Plan Validator

Componente que valida la intención analítica antes de generar SQL.

### Query Orchestrator

Componente que ejecuta múltiples flujos Text-to-SQL a partir del plan.

### RAG-lite semántico

Uso de documentos curados para enriquecer el contexto de la IA.

### Controlled Rendering

La IA propone gráficos, pero el sistema controla el renderizado.

### SQL Audit

Trazabilidad de cada consulta generada, validada y ejecutada.

### Executive Insight

Capa que convierte resultados en lectura ejecutiva de negocio.

---

## 12. Relación con productos reales de mercado

Esta clase acerca el MVP a la lógica de productos modernos de Generative BI, como:

- Power BI Copilot.
- Microsoft Fabric Copilot.
- Tableau Pulse.
- Amazon QuickSight Q.
- Otros asistentes analíticos basados en modelos semánticos.

Estos productos no se limitan a generar SQL.

Buscan ayudar al usuario a:

- Entender métricas.
- Explorar datos.
- Crear visualizaciones.
- Generar narrativas.
- Descubrir insights.
- Construir productos analíticos de forma asistida.

Nuestro MVP académico implementa una versión simplificada de esa idea.

---

## 13. Limitaciones actuales del MVP

El sistema actual funciona como demostración académica, pero tiene limitaciones:

- El RAG es simple y no usa embeddings.
- No hay control de usuarios ni permisos.
- No hay row-level security.
- No hay versionado formal del contrato semántico.
- El Data Mart es pequeño.
- El planner puede requerir más validaciones en escenarios complejos.
- No hay caché de resultados.
- No hay monitoreo de costes del LLM.
- No hay evaluación automática de calidad analítica.
- No hay despliegue cloud.

Estas limitaciones son intencionales para mantener el proyecto entendible y ejecutable en clase.

---

## 14. Evolución enterprise propuesta

En una arquitectura empresarial, este MVP podría evolucionar hacia:

```text
Data Warehouse / Lakehouse
→ Semantic Layer
→ KPI Registry
→ Data Catalog
→ Vector Store
→ GenBI Planner
→ SQL / DAX / SPARQL / API Generator
→ Policy Engine
→ Query Validator
→ Execution Engine
→ Dashboard Renderer
→ Insight Generator
→ Audit & Observability
```

Componentes enterprise posibles:

- Lakehouse con Iceberg, Delta o Hudi.
- Catálogo de datos.
- Motor de políticas.
- Semantic layer corporativo.
- Métricas certificadas.
- Vector database.
- Observabilidad de prompts.
- Evaluación de respuestas.
- Control de costes.
- Seguridad por roles.
- Auditoría de decisiones analíticas.

---

## 15. Cierre conceptual del bloque GenBI

La evolución del bloque queda así:

```text
Clase 1:
Entendimos qué es GenBI y por qué necesita semántica, métricas y gobernanza.

Clase 2:
Aprendimos que SQL válido no es lo mismo que SQL correcto.

Clase 3:
Construimos un MVP técnico de Text-to-SQL controlado.

Clase 4:
Convertimos el MVP en una aplicación GenBI con explicación y visualización.

Clase 5:
Transformamos la aplicación en un generador de dashboards ejecutivos con planner, contexto semántico, múltiples SQL, visualizaciones, auditoría e insight ejecutivo.
```

La conclusión principal es:

```text
GenBI no consiste en conectar un LLM libremente a una base de datos.

GenBI consiste en diseñar una arquitectura donde la IA puede asistir,
pero el sistema mantiene el control sobre la semántica, la seguridad,
la ejecución, la visualización y la trazabilidad.
```

---

## 16. Frase final de la clase

```text
La madurez de GenBI no se mide por cuántas respuestas genera la IA,
sino por cuántas decisiones puede soportar de forma confiable,
trazable y gobernada.
```
