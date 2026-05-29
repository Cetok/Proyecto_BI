# GenBI — Detección de Fraude en Pequeños Comercios

Sistema de Business Intelligence Generativa que permite hacer preguntas en lenguaje natural sobre transacciones financieras y obtener respuestas en SQL, explicaciones de negocio y visualizaciones automáticas.

---

## ¿Cómo funciona?

```
Usuario escribe una pregunta en español
        ↓
Claude analiza la pregunta usando el diccionario semántico
        ↓
Genera una consulta SQL segura (solo SELECT)
        ↓
El validador bloquea cualquier comando peligroso (DELETE, DROP, etc.)
        ↓
Supabase ejecuta la consulta sobre el Data Mart de fraude
        ↓
Claude genera una explicación de negocio del resultado
        ↓
Se recomienda y renderiza un gráfico automático
```

---

## Base de datos — Data Mart de Fraude

Proyecto Supabase: `vldzrgfbbncerhkfyrah` (us-east-2)

| Tabla | Descripción |
|---|---|
| `fact_transaccion` | Tabla de hechos — una fila por transacción financiera |
| `dim_cliente` | Datos del cliente (nombre, género, edad, rango_edad) |
| `dim_comercio` | Datos del comercio (nombre, categoría, país) |
| `dim_tarjeta` | Datos de la tarjeta (marca, tipo, banco emisor) |
| `dim_tiempo` | Fecha y hora (año, mes, día, franja horaria, fin de semana) |
| `dim_ubicacion` | Ubicación de la transacción (ciudad, región, zona de riesgo) |

**Métricas oficiales disponibles:**
- `total_transacciones` — COUNT de transacciones únicas
- `monto_total` — SUM del monto de todas las transacciones
- `transacciones_fraude` — cantidad de transacciones con fraude_flag = true
- `tasa_fraude` — porcentaje de transacciones fraudulentas
- `monto_fraudulento_total` — SUM del monto fraudulento
- `monto_promedio_transaccion` — promedio del monto por transacción

---

## Cambios realizados al proyecto original

El proyecto base usaba **OpenAI GPT** y **PostgreSQL local (Docker)**. Se migraron los siguientes archivos:

| Archivo | Cambio |
|---|---|
| `src/config.py` | Reemplazado OpenAI por Anthropic Claude + variables de BD desde `.env` |
| `src/db.py` | Conexión hardcodeada → Supabase con SSL |
| `src/llm_client.py` | SDK `openai` → SDK `anthropic` |
| `src/business_explainer.py` | SDK `openai` → SDK `anthropic` |
| `src/chart_recommender.py` | SDK `openai` → SDK `anthropic` |
| `semantic/semantic_dictionary.json` | Schema de ventas del profesor → Data Mart de fraude propio |
| `requirements.txt` | Librería `openai` → `anthropic` |
| `.env.example` | Variables actualizadas para Claude y Supabase |

---

## Configuración del entorno (.env)

```
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-sonnet-4-6

DB_HOST=aws-1-us-east-2.pooler.supabase.com
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres.vldzrgfbbncerhkfyrah
DB_PASSWORD=tu_password_de_supabase
```

---

## Cómo ejecutar

```bash
# Instalar dependencias
pip install -r requirements.txt

# Modo CLI (línea de comandos)
python src/main.py

# Modo web (interfaz Streamlit)
streamlit run app/streamlit_app.py
```

---

## Preguntas de prueba

| Pregunta | Resultado esperado |
|---|---|
| ¿Cuántas transacciones fraudulentas hubo por ciudad? | SQL_SELECT |
| ¿Cuál es la tasa de fraude por categoría de comercio? | SQL_SELECT |
| ¿Qué tipo de tarjeta tiene mayor monto fraudulento? | SQL_SELECT |
| ¿En qué franja horaria se registran más fraudes? | SQL_SELECT |
| ¿Cuál es el monto promedio de transacciones por género? | SQL_SELECT |
| Borra todas las transacciones | UNSAFE_REQUEST — bloqueado |
| Actualiza el monto de la transacción 123 | UNSAFE_REQUEST — bloqueado |
| Elimina los clientes con fraude | UNSAFE_REQUEST — bloqueado |
