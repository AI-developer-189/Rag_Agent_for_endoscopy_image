"""
backend/app/rag/retriever.py
Semantic similarity search over in-memory chunk embeddings.
Exports retrieve_relevant_guidelines(query, top_k=3).
"""
from typing import List, Dict, Any
import numpy as np

from app.rag.embeddings import get_chunks, is_index_loaded, embed_query


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Compute cosine similarity between two 1D numpy vectors."""
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


def retrieve_relevant_guidelines(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """
    Retrieve top-k relevant clinical guidelines for a given query string.

    Returns:
        List[Dict[str, Any]]: List of dicts with keys 'text', 'source', 'score'.
    """
    if not is_index_loaded():
        return [
            {
                "text": "Clinical guideline retrieval is not available (RAG index not loaded).",
                "source": "system",
                "score": 0.0,
            }
        ]

    chunks = get_chunks()
    if not chunks:
        return [
            {
                "text": "No clinical knowledge guidelines are available in the index.",
                "source": "system",
                "score": 0.0,
            }
        ]

    try:
        query_vector = embed_query(query)
    except Exception as e:
        return [
            {
                "text": f"Error generating query embedding: {str(e)}",
                "source": "system",
                "score": 0.0,
            }
        ]

    scored_results = []
    for chunk in chunks:
        chunk_vector = chunk.get("embedding")
        if chunk_vector is None:
            continue

        score = _cosine_similarity(query_vector, chunk_vector)
        # Format source name nicely (e.g. polyps.txt -> Polyps)
        source_name = chunk.get("source", "guidelines").replace(".txt", "").replace("_", " ").title()

        scored_results.append({
            "text": chunk.get("text", ""),
            "source": source_name,
            "score": round(float(score), 4),
        })

    # Sort descending by similarity score
    scored_results.sort(key=lambda item: item["score"], reverse=True)
    top_results = scored_results[:top_k]

    # Filter out extremely low correlation scores if desired, or return top_k
    filtered = [r for r in top_results if r["score"] > 0.10]
    if not filtered and top_results:
        # If all scores are below threshold, still return non-empty structure indicating no strong match
        return [
            {
                "text": "No highly relevant clinical guidelines were found matching the specific query.",
                "source": "system",
                "score": 0.0,
            }
        ]

    return filtered if filtered else top_results
