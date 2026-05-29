from db import run_query
from semantic_loader import load_semantic_dictionary
from prompt_builder import build_prompt
from llm_client import generate_sql
from sql_validator import validate_sql


def ask_datamart(question: str):
    semantic_dictionary = load_semantic_dictionary()
    prompt = build_prompt(question, semantic_dictionary)
    sql = generate_sql(prompt)

    print("\n=== PREGUNTA ===")
    print(question)

    print("\n=== RESPUESTA IA ===")
    print(sql)

    if sql == "UNSAFE_REQUEST":
        print("\n=== RESPUESTA DEL SISTEMA ===")
        print("Solicitud bloqueada: la pregunta intenta modificar o borrar datos.")
        return

    if sql == "OUT_OF_SCOPE":
        print("\n=== RESPUESTA DEL SISTEMA ===")
        print("No puedo responder esa pregunta con el Data Mart disponible.")
        return

    if sql.startswith("SQL_SELECT"):
        sql = sql.replace("SQL_SELECT", "", 1).strip()

    print("\n=== SQL GENERADO POR IA ===")
    print(sql)

    is_valid, message = validate_sql(sql, semantic_dictionary)

    print("\n=== VALIDACIÓN SQL ===")
    print(message)

    if not is_valid:
        print("\nConsulta bloqueada. No se ejecutará en PostgreSQL.")
        return

    df = run_query(sql)

    print("\n=== RESULTADO ===")
    print(df)

def test_fake_column_validation():
    semantic_dictionary = load_semantic_dictionary()

    fake_sql = """
    SELECT 
        fs.fake_column
    FROM fact_sales fs;
    """

    is_valid, message = validate_sql(fake_sql, semantic_dictionary)

    print("\n=== TEST COLUMNA FALSA ===")
    print(fake_sql)
    print("Valid:", is_valid)
    print("Message:", message)

if __name__ == "__main__":
    question = input("Pregunta de negocio: ")
    ask_datamart(question)