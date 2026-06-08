# Semantic Rules for GenBI — Fraud Detection Data Mart

## Business context

This Data Mart is focused on fraud detection in financial transactions of small commerce.
The central table is fact_transaccion. All metrics must be derived from this table.

## Official metrics

- total_transacciones must be calculated using COUNT(DISTINCT fact_transaccion.trans_num).
- monto_total must be calculated using SUM(fact_transaccion.monto_transaccion).
- transacciones_fraude must be calculated using SUM(CASE WHEN fact_transaccion.fraude_flag = true THEN 1 ELSE 0 END).
- tasa_fraude must be calculated using ROUND(SUM(CASE WHEN fact_transaccion.fraude_flag = true THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2).
- monto_fraudulento_total must be calculated using SUM(fact_transaccion.monto_fraudulento).
- monto_promedio_transaccion must be calculated using ROUND(AVG(fact_transaccion.monto_transaccion), 2).

## Time analysis

- Monthly analysis should use dim_tiempo.mes.
- Yearly analysis should use dim_tiempo.anio.
- Day-of-week analysis should use dim_tiempo.dia_semana.
- Time-of-day analysis should use dim_tiempo.franja_horaria.
- Weekend analysis should use dim_tiempo.es_fin_semana.

## Commerce analysis

- Commerce category analysis should use dim_comercio.categoria_comercio.
- Commerce name analysis should use dim_comercio.nombre_comercio.

## Geographic analysis

- City analysis should use dim_ubicacion.ciudad.
- Region analysis should use dim_ubicacion.region.
- Risk zone analysis should use dim_ubicacion.zona_riesgo.

## Customer analysis

- Age range analysis should use dim_cliente.rango_edad.
- Gender analysis should use dim_cliente.genero.

## Card analysis

- Card brand analysis should use dim_tarjeta.marca_tarjeta.
- Card type analysis should use dim_tarjeta.tipo_tarjeta (debito, credito).
- Issuing bank analysis should use dim_tarjeta.banco_emisor.

## Dashboard guidelines

- Executive dashboards should start with KPI cards (total_transacciones, transacciones_fraude, tasa_fraude, monto_fraudulento_total).
- Use line charts for time evolution of fraud or transaction volume.
- Use bar charts for comparisons by commerce category, city, region, card brand or age range.
- Use pie charts only for share of total (e.g. fraud rate by card type).
- Use scatter charts only when comparing two numeric measures.

## Governance rules

- The AI can propose the dashboard structure.
- The system validates the plan.
- The system generates and validates SQL.
- The system executes only validated SQL.
- Do not invent tables, columns or metrics not present in the semantic dictionary.
