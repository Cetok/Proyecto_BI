# Clase 4 — Streamlit, Explicación de Negocio y Visualización IA

## Objetivo de la Clase

Extender el MVP controlado de Text-to-SQL construido en la Clase 3 para convertirlo en una aplicación GenBI usable.

En la Clase 3 construimos el motor:

```text
Pregunta → SQL → Validación → PostgreSQL → Resultado
```

En la Clase 4 construimos la experiencia:

```text
Pregunta → SQL → Validación → Resultado → Explicación de negocio → Visualización
```

---

# Supuesto de Entrada

Cada grupo debe haber adaptado el MVP base a su propio Data Mart.

Eso implica haber actualizado:

- tablas,
- dimensiones,
- fact tables,
- métricas oficiales,
- relaciones,
- `semantic_dictionary.json`,
- preguntas de prueba.

---

# Flujo Final de la Clase 4

```text
Usuario
↓
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

# Nuevos Componentes

## 1. Streamlit App

Archivo:

```text
app/streamlit_app.py
```

Función:

- recibir preguntas de negocio,
- mostrar respuesta IA,
- mostrar SQL generado,
- validar SQL,
- ejecutar consulta,
- mostrar resultado,
- mostrar explicación,
- mostrar visualización.

Comando:

```bash
python -m streamlit run app/streamlit_app.py
```

---

## 2. Business Explanation Layer

Archivos:

```text
prompts/business_explanation_prompt.txt
src/business_explainer.py
```

Objetivo:

Explicar el resultado en términos de negocio.

Reglas:

- explicar solo lo observado en los datos,
- no inventar causas,
- no inventar recomendaciones,
- no mencionar información inexistente,
- usar lenguaje claro y ejecutivo,
- no explicar el SQL salvo que sea necesario.

Ejemplo aceptable:

```text
Lima registra la mayor venta total dentro del resultado analizado.
Arequipa ocupa el segundo lugar y Trujillo presenta un volumen menor.
```

Ejemplo incorrecto:

```text
Lima vende más porque tiene mejor marketing.
```

Motivo:

El dato de marketing no está en el resultado.

---

## 3. Chart Recommendation Layer

Archivos:

```text
prompts/chart_recommendation_prompt.txt
src/chart_recommender.py
```

Objetivo:

Pedir a la IA que recomiende el tipo de visualización más adecuado.

Tipos permitidos:

```text
bar
line
pie
scatter
```

Regla de arquitectura:

```text
La IA recomienda.
El sistema valida.
El sistema renderiza.
```

La IA no genera JavaScript, HTML ni código libre.

---

## 4. Chart Generator

Archivo:

```text
src/chart_generator.py
```

Tecnología:

```text
Apache ECharts + streamlit-echarts
```

Objetivo:

Renderizar gráficos interactivos a partir de plantillas controladas.

---

# Detección de Ejes

El sistema debe inferir correctamente qué columnas usar como ejes.

Ejemplo:

Resultado:

```text
year | month | month_name | number_of_sales
```

Visualización correcta:

```text
Eje X = month_name
Eje Y = number_of_sales
```

No debe graficar:

```text
Eje X = year
Eje Y = month
```

Esto demuestra que GenBI no solo debe generar SQL, también debe entender el resultado tabular.

---

# Dependencias Nuevas

Agregar a `requirements.txt`:

```text
streamlit
streamlit-echarts
```

Instalar:

```bash
pip install -r requirements.txt
```

---

# Matriz de Pruebas

Archivo:

```text
tests/test_questions.csv
```

Ejemplo:

```csv
question,expected_status,notes
¿Cuál es la venta total por ciudad?,SQL_SELECT,Debe responder correctamente
¿Cuál es el ticket promedio por ciudad?,SQL_SELECT,Debe usar métrica oficial
¿Cuántas ventas hubo por mes?,SQL_SELECT,Debe graficar línea mensual
¿Cuál es el salario promedio?,OUT_OF_SCOPE,No existe en el Data Mart
Borra todas las ventas,UNSAFE_REQUEST,Debe bloquear
```

---

# Preguntas Recomendadas para Probar

## Preguntas válidas

```text
¿Cuál es la venta total por ciudad?
```

Esperado:

- SQL_SELECT
- bar chart
- métrica total_sales

```text
¿Cuál es el ticket promedio por ciudad?
```

Esperado:

- SQL_SELECT
- bar chart
- métrica average_ticket

```text
¿Cuántas ventas hubo por mes?
```

Esperado:

- SQL_SELECT
- line chart
- métrica number_of_sales

```text
¿Cuál es la venta total por categoría de producto?
```

Esperado:

- SQL_SELECT
- bar o pie chart
- join con dim_product

```text
¿Qué cantidad total se vendió por marca?
```

Esperado:

- SQL_SELECT
- bar chart
- SUM(quantity)

---

## Preguntas bloqueadas

```text
Borra todas las ventas de Lima
```

Esperado:

```text
UNSAFE_REQUEST
```

```text
Actualiza el precio de todos los productos
```

Esperado:

```text
UNSAFE_REQUEST
```

```text
¿Cuál es el salario promedio de los empleados?
```

Esperado:

```text
OUT_OF_SCOPE
```

---

# Entregable de Clase 4

Cada grupo debe entregar:

- app Streamlit funcionando,
- MVP adaptado a su propio Data Mart,
- diccionario semántico actualizado,
- mínimo 5 preguntas válidas,
- mínimo 3 preguntas bloqueadas,
- explicación de negocio,
- visualización asistida por IA,
- matriz de pruebas,
- evidencia de ejecución.

---

# Criterios de Evaluación Sugeridos

| Criterio | Peso |
|---|---:|
| App Streamlit funcional | 20% |
| Adaptación al Data Mart del grupo | 20% |
| SQL controlado y validado | 15% |
| Explicación de negocio | 15% |
| Visualización correcta | 15% |
| Matriz de pruebas | 15% |

---

# Mensaje Clave

GenBI no termina cuando se genera SQL.

Un sistema GenBI debe transformar una pregunta de negocio en:

```text
consulta controlada
+
resultado confiable
+
explicación clara
+
visualización útil
```

---

# Próxima Clase

## Clase 5 — RAG aplicado a Business Intelligence

La siguiente clase introducirá:

- documentación analítica,
- glosarios KPI,
- embeddings,
- ChromaDB,
- recuperación semántica,
- arquitectura GenBI más cercana a enterprise.
