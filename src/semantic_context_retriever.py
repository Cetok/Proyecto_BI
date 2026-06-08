from pathlib import Path


def retrieve_semantic_context(question: str) -> str:
    """
    RAG-lite version.

    For the academic MVP, we load curated semantic documents from the
    knowledge_base folder and provide them as additional business context.

    In an enterprise architecture, this could evolve into:
    - Vector database
    - Data catalog
    - Semantic layer
    - Knowledge graph
    """

    project_root = Path(__file__).resolve().parent.parent
    knowledge_base_path = project_root / "knowledge_base"

    files = [
        "semantic_rules.md"
    ]

    context_parts = []

    for file_name in files:
        file_path = knowledge_base_path / file_name

        if file_path.exists():
            context_parts.append(file_path.read_text(encoding="utf-8"))

    return "\n\n".join(context_parts)
