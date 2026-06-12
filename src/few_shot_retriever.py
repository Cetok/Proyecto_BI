import json
import re
from pathlib import Path

STOPWORDS = {
    "de", "la", "el", "en", "por", "para", "con", "un", "una", "los", "las", "y", "o", "a", "al", "del",
    "que", "es", "son", "cual", "cuales", "como", "cuantos", "cuantas", "donde", "cuando", "por qué",
    "quien", "quienes", "esta", "este", "estos", "estas", "aquellos", "aquellas", "tiene", "tienen"
}

def clean_and_tokenize(text: str) -> set:
    """
    Cleans punctuation and tokenizes a string, removing standard Spanish stopwords.
    """
    words = re.findall(r'\b[a-z0-9áéíóúüñ]+\b', text.lower())
    return {w for w in words if w not in STOPWORDS}

def calculate_similarity(query_tokens: set, candidate_tokens: set) -> float:
    """
    Computes Jaccard Similarity between two token sets.
    """
    if not query_tokens or not candidate_tokens:
        return 0.0
    intersection = query_tokens.intersection(candidate_tokens)
    union = query_tokens.union(candidate_tokens)
    return len(intersection) / len(union)

def retrieve_few_shot_examples(question: str, k: int = 2) -> list:
    """
    Retrieves the top k golden queries based on similarity with the given question.
    """
    project_root = Path(__file__).resolve().parent.parent
    golden_path = project_root / "semantic" / "golden_queries.json"

    if not golden_path.exists():
        return []

    try:
        with open(golden_path, "r", encoding="utf-8") as f:
            candidates = json.load(f)
    except Exception:
        return []

    query_tokens = clean_and_tokenize(question)
    if not query_tokens:
        # If query has only stopwords, return the first k candidates as fallback
        return candidates[:k]

    scored_candidates = []
    for cand in candidates:
        cand_tokens = clean_and_tokenize(cand["question"])
        score = calculate_similarity(query_tokens, cand_tokens)
        scored_candidates.append((score, cand))

    # Sort by score descending
    scored_candidates.sort(key=lambda x: x[0], reverse=True)

    # Filter out examples with zero score, return top k
    results = [cand for score, cand in scored_candidates if score > 0.0]
    
    # If no matching examples found, fallback to first k golden queries
    if not results:
        return candidates[:k]

    return results[:k]
