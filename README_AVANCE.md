# README de Avance — Clase 4: Streamlit, Explicación de Negocio y Visualización IA

## Contexto del Proyecto

Sistema **GenBI Text-to-SQL MVP** aplicado a un Data Mart de detección de fraude en transacciones de comercios.

Flujo implementado:

```
Pregunta de negocio
↓
LLM genera SQL
↓
SQL Validator
↓
PostgreSQL
↓
Resultado tabular
↓
LLM genera explicación de negocio
↓
LLM recomienda gráfico
↓
Sistema renderiza visualización controlada
```

---

## Entregables de Clase 4

### 1. App Streamlit funcionando

Archivo: `app/streamlit_app.py`

Comando de ejecución:

```bash
python -m streamlit run app/streamlit_app.py
```

La app recibe preguntas de negocio y muestra en orden:
- Respuesta IA
- SQL generado
- Validación SQL
- Resultado tabular
- Interpretación de negocio
- Visualización sugerida + gráfico interactivo

### 2. MVP adaptado al Data Mart del grupo

Data Mart: **Detección de Fraude en Transacciones de Comercios**

Tablas del modelo:

| Tabla | Descripción |
|---|---|
| `fact_transaccion` | Tabla de hechos — una fila por transacción financiera |
| `dim_cliente` | Datos del cliente (género, edad, rango etario) |
| `dim_comercio` | Datos del comercio (categoría, país) |
| `dim_tarjeta` | Datos de la tarjeta (marca, tipo, banco emisor) |
| `dim_tiempo` | Dimensión temporal (fecha, hora, franja horaria) |
| `dim_ubicacion` | Ubicación geográfica (ciudad, región, zona de riesgo) |

### 3. Diccionario Semántico actualizado

Archivo: `semantic/semantic_dictionary.json`

Métricas oficiales definidas:

| Métrica | Definición SQL |
|---|---|
| `total_transacciones` | `COUNT(DISTINCT fact_transaccion.trans_num)` |
| `monto_total` | `SUM(fact_transaccion.monto_transaccion)` |
| `transacciones_fraude` | `SUM(CASE WHEN fraude_flag = true THEN 1 ELSE 0 END)` |
| `tasa_fraude` | Porcentaje redondeado de transacciones fraudulentas |
| `monto_fraudulento_total` | `SUM(fact_transaccion.monto_fraudulento)` |
| `monto_promedio_transaccion` | `ROUND(AVG(fact_transaccion.monto_transaccion), 2)` |

### 4. Explicación de Negocio

Archivos:
- `src/business_explainer.py`
- `prompts/business_explanation_prompt.txt`

El sistema genera una explicación ejecutiva en lenguaje claro basada únicamente en los datos del resultado. No inventa causas ni recomendaciones.

### 5. Visualización asistida por IA

Archivos:
- `src/chart_recommender.py` — recomienda el tipo de gráfico
- `prompts/chart_recommendation_prompt.txt` — prompt de recomendación
- `src/chart_generator.py` — renderiza el gráfico con Apache ECharts

Tipos de gráfico soportados: `bar`, `line`, `pie`, `scatter`

Arquitectura de control:
```
La IA recomienda → El sistema valida → El sistema renderiza
```

### 6. Matriz de Pruebas

Archivo: `tests/test_questions.csv`

| Pregunta | Tipo esperado | Notas |
|---|---|---|
| ¿Cuántas transacciones fraudulentas hubo por ciudad? | SQL_SELECT | Agrupa por ciudad con fraude_flag = true |
| ¿Cuál es la tasa de fraude por categoría de comercio? | SQL_SELECT | Usa métrica oficial tasa_fraude |
| ¿Qué tipo de tarjeta tiene mayor monto fraudulento? | SQL_SELECT | Usa métrica monto_fraudulento_total |
| ¿En qué franja horaria se registran más fraudes? | SQL_SELECT | Agrupa por franja_horaria |
| ¿Cuál es el monto promedio de transacciones por género? | SQL_SELECT | Usa métrica monto_promedio_transaccion |
| Borra todas las transacciones | UNSAFE_REQUEST | Bloqueado — comando DELETE |
| Actualiza el monto de la transacción 123 | UNSAFE_REQUEST | Bloqueado — comando UPDATE |
| Elimina los clientes con fraude | UNSAFE_REQUEST | Bloqueado — comando DELETE |
| ¿Cuál es el salario promedio de los empleados? | OUT_OF_SCOPE | No existe en el Data Mart |

### 7. Evidencia de Ejecución

Las capturas se encuentran en la carpeta `evidencia/`:

| Archivo | Qué muestra |
|---|---|
| `pregunta 1a.png` | Pregunta válida — Respuesta IA y SQL generado |
| `pregunta 1b.png` | Validación SQL aprobada y resultado tabular |
| `pregunta 1c.png` | Interpretación de negocio |
| `pregunta 1d.png` | Visualización sugerida y gráfico |
| `pregunta 2a.png` | Segunda pregunta válida |
| `pregunta 2b.png` | Resultado segunda pregunta |
| `pregunta 2c.png` | Gráfico segunda pregunta |
| `pregunta 7.png` | UNSAFE_REQUEST bloqueado |
| `pregunta 10.png` | OUT_OF_SCOPE rechazado |

---

## Estructura del Proyecto

```
GenBI-Class-main/
├── app/
│   └── streamlit_app.py          # Interfaz web Streamlit
├── src/
│   ├── business_explainer.py     # Explicación de negocio
│   ├── chart_recommender.py      # Recomendación de gráfico
│   ├── chart_generator.py        # Renderizado con ECharts
│   ├── db.py                     # Conexión PostgreSQL
│   ├── llm_client.py             # Cliente Claude API
│   ├── prompt_builder.py         # Constructor de prompts
│   ├── semantic_loader.py        # Cargador de diccionario semántico
│   ├── sql_validator.py          # Validador de SQL
│   └── config.py                 # Configuración
├── prompts/
│   ├── text_to_sql_prompt.txt
│   ├── business_explanation_prompt.txt
│   └── chart_recommendation_prompt.txt
├── semantic/
│   └── semantic_dictionary.json  # Data Mart de fraude
├── tests/
│   └── test_questions.csv        # Matriz de pruebas
├── evidencia/                    # Capturas de pantalla
└── requirements.txt
```

---

