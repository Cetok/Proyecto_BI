import json
from pathlib import Path


def load_semantic_dictionary():
    project_root = Path(__file__).resolve().parent.parent
    semantic_path = project_root / "semantic" / "semantic_dictionary.json"

    with open(semantic_path, "r", encoding="utf-8") as file:
        return json.load(file)