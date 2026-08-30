"""
agent/rag_tool.py
Wraps the RAG retriever for use by the agentic orchestrator.
"""
from typing import List, Dict, Any

from app.rag.retriever import retrieve_relevant_guidelines


def retrieve_guidelines_tool(
    disease: str,
    severity: str = "",
    patient_context: str = "",
    top_k: int = 3,
) -> List[Dict[str, Any]]:
    """
    Tool 3: Retrieve relevant clinical guidelines for the predicted disease.

    Args:
        disease: Predicted disease name (e.g., "polyps", "esophagitis")
        severity: Severity level (e.g., "Mild", "Moderate", "Severe")
        patient_context: Additional patient context for query enrichment
        top_k: Number of guideline chunks to return

    Returns:
        List of [{text, source, score}, ...]
    """
    # Build a rich query combining disease, severity, and patient context
    query_parts = [f"endoscopy {disease}"]
    if severity:
        query_parts.append(f"{severity} severity")
    query_parts.append("clinical guidelines treatment management")
    if patient_context:
        query_parts.append(patient_context)

    query = " ".join(query_parts)
    return retrieve_relevant_guidelines(query, top_k=top_k)
