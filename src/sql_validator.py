import re


FORBIDDEN_KEYWORDS = [
    "DELETE",
    "UPDATE",
    "INSERT",
    "DROP",
    "ALTER",
    "TRUNCATE",
    "CREATE",
    "GRANT",
    "REVOKE"
]


SQL_RESERVED_WORDS = {
    "SELECT", "FROM", "JOIN", "ON", "WHERE", "GROUP", "BY",
    "ORDER", "ASC", "DESC", "AS", "AND", "OR", "SUM", "COUNT",
    "DISTINCT", "AVG", "MIN", "MAX"
}


def extract_tables(sql: str) -> list[str]:
    matches = re.findall(
        r"(?:FROM|JOIN)\s+([a-zA-Z_][a-zA-Z0-9_]*)",
        sql,
        re.IGNORECASE
    )
    return list(set(matches))


def extract_aliases(sql: str) -> dict[str, str]:
    matches = re.findall(
        r"(?:FROM|JOIN)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+([a-zA-Z_][a-zA-Z0-9_]*)",
        sql,
        re.IGNORECASE
    )

    return {alias: table for table, alias in matches}


def extract_qualified_columns(sql: str) -> list[tuple[str, str]]:
    matches = re.findall(
        r"([a-zA-Z_][a-zA-Z0-9_]*)\.([a-zA-Z_][a-zA-Z0-9_]*)",
        sql
    )
    return matches


def get_allowed_columns_by_table(semantic_dictionary: dict) -> dict[str, list[str]]:
    tables = semantic_dictionary["tables"]

    return {
        table_name: list(table_metadata["columns"].keys())
        for table_name, table_metadata in tables.items()
    }


def validate_columns(sql: str, semantic_dictionary: dict) -> tuple[bool, str]:
    aliases = extract_aliases(sql)
    qualified_columns = extract_qualified_columns(sql)
    allowed_columns_by_table = get_allowed_columns_by_table(semantic_dictionary)

    for qualifier, column in qualified_columns:
        table = aliases.get(qualifier, qualifier)

        if table not in allowed_columns_by_table:
            return False, f"Tabla o alias no reconocido: {qualifier}"

        allowed_columns = allowed_columns_by_table[table]

        if column not in allowed_columns:
            return False, f"Columna no permitida o inexistente: {qualifier}.{column}"

    return True, "Columnas aprobadas."


def validate_sql(sql: str, semantic_dictionary: dict) -> tuple[bool, str]:
    sql_clean = sql.strip()
    sql_upper = sql_clean.upper()

    if sql_upper == "NO_ANSWER":
        return False, "La pregunta no puede responderse con el diccionario actual."

    if not sql_upper.startswith("SELECT"):
        return False, "Solo se permiten consultas SELECT."

    for keyword in FORBIDDEN_KEYWORDS:
        if keyword in sql_upper:
            return False, f"Consulta bloqueada: contiene {keyword}."

    if ";" in sql_clean[:-1]:
        return False, "No se permiten múltiples sentencias SQL."

    allowed_tables = semantic_dictionary["allowed_tables"]
    used_tables = extract_tables(sql_clean)

    for table in used_tables:
        if table not in allowed_tables:
            return False, f"Tabla no permitida: {table}"

    columns_valid, columns_message = validate_columns(sql_clean, semantic_dictionary)

    if not columns_valid:
        return False, columns_message

    return True, "SQL aprobado."