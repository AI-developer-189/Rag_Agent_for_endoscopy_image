"""
backend/app/rag/embeddings.py
Loads knowledge base documents, chunks them, and generates sentence embeddings.
Uses sentence-transformers/all-MiniLM-L6-v2 — loaded once and kept in memory.
"""
import os
from typing import List, Dict, Any
import numpy as np

# ─── Config & Module State ───────────────────────────────────────────────────
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
KNOWLEDGE_DIR = os.path.join(os.path.dirname(__file__), "knowledge")

_embedder = None
_chunks: List[Dict[str, Any]] = []  # [{text, source, embedding}, ...]
_embeddings_loaded: bool = False


def _get_embedder():
    """Load the sentence-transformers model once."""
    global _embedder
    if _embedder is None:
        try:
            from sentence_transformers import SentenceTransformer
            print(f"[RAG] Loading embedding model: {MODEL_NAME}...")
            _embedder = SentenceTransformer(MODEL_NAME)
            print("[RAG] ✅ Embedding model loaded successfully.")
        except Exception as e:
            print(f"[RAG] ⚠️ Failed to load embedding model ({MODEL_NAME}): {e}")
            _embedder = None
    return _embedder


def _chunk_text(text: str, chunk_size: int = 400, overlap: int = 80) -> List[str]:
    """Split text into overlapping character-level chunks."""
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


def _load_knowledge_documents() -> List[Dict[str, str]]:
    """Read all .txt files from backend/app/rag/knowledge/."""
    docs = []
    if not os.path.exists(KNOWLEDGE_DIR):
        print(f"[RAG] ⚠️ Knowledge directory does not exist: {KNOWLEDGE_DIR}")
        return docs

    try:
        files = [f for f in os.listdir(KNOWLEDGE_DIR) if f.endswith(".txt")]
        if not files:
            print(f"[RAG] ⚠️ No .txt documents found in {KNOWLEDGE_DIR}")
            return docs

        for fname in files:
            fpath = os.path.join(KNOWLEDGE_DIR, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                if content:
                    docs.append({"source": fname, "text": content})
                    print(f"[RAG] Loaded document: {fname} ({len(content)} chars)")
            except Exception as fe:
                print(f"[RAG] ⚠️ Error reading file {fname}: {fe}")
    except Exception as e:
        print(f"[RAG] ⚠️ Error scanning knowledge directory: {e}")

    return docs


def build_index():
    """
    Build in-memory chunk and embedding index.
    Loads documents, chunks them, generates embeddings, stores in memory.
    """
    global _chunks, _embeddings_loaded

    embedder = _get_embedder()
    if embedder is None:
        print("[RAG] ⚠️ Skipping index build because embedding model could not be loaded.")
        _embeddings_loaded = False
        return

    docs = _load_knowledge_documents()
    if not docs:
        print("[RAG] ⚠️ No knowledge documents to index.")
        _chunks = []
        _embeddings_loaded = False
        return

    all_chunks = []
    for doc in docs:
        raw_chunks = _chunk_text(doc["text"])
        for chunk_str in raw_chunks:
            all_chunks.append({
                "source": doc["source"],
                "text": chunk_str
            })

    if not all_chunks:
        _chunks = []
        _embeddings_loaded = False
        return

    print(f"[RAG] Generating embeddings for {len(all_chunks)} chunks...")
    texts = [c["text"] for c in all_chunks]

    try:
        embeddings = embedder.encode(texts, show_progress_bar=False, convert_to_numpy=True)
        for i, chunk_dict in enumerate(all_chunks):
            chunk_dict["embedding"] = embeddings[i]

        _chunks = all_chunks
        _embeddings_loaded = True
        print(f"[RAG] ✅ Index built successfully with {len(_chunks)} chunks.")
    except Exception as e:
        print(f"[RAG] ⚠️ Error encoding embeddings: {e}")
        _chunks = []
        _embeddings_loaded = False


def get_chunks() -> List[Dict[str, Any]]:
    """Return the indexed chunks with embeddings."""
    return _chunks


def is_index_loaded() -> bool:
    """Return True if index is loaded and ready."""
    return _embeddings_loaded


def embed_query(query: str) -> np.ndarray:
    """Embed a search query using the singleton sentence-transformers model."""
    embedder = _get_embedder()
    if embedder is None:
        raise RuntimeError("Embedding model is not loaded.")
    embedding = embedder.encode([query], convert_to_numpy=True)[0]
    return embedding