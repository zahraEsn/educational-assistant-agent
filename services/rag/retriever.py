from __future__ import annotations

from pathlib import Path

import numpy as np

from services.rag.embedder import embed_query
from services.rag.vector_store import VectorStore


INDEX_PATH = Path("data/vector_store/index.faiss")
METADATA_PATH = Path("data/vector_store/metadata.json")


_store: VectorStore | None = None


def get_vector_store() -> VectorStore:
    global _store

    if _store is None:
        _store = VectorStore(
            index_path=INDEX_PATH,
            metadata_path=METADATA_PATH,
        )
        _store.load()

    return _store


def retrieve(
    query: str,
    grade: str,
    subject: str,
    top_k: int = 4,
    candidate_k: int = 50,
) -> list[dict]:
    """
    Retrieve relevant textbook chunks for a specific grade and subject.
    """

    query = query.strip()

    if not query:
        return []

    store = get_vector_store()

    query_embedding = embed_query(query)

    query_embedding = np.asarray(
        query_embedding,
        dtype="float32",
    )

    candidates = store.search(
        query_embedding,
        top_k=candidate_k,
    )

    filtered = [
        item
        for item in candidates
        if item.get("grade") == grade
        and item.get("subject") == subject
    ]

    return filtered[:top_k]


def build_context(results: list[dict]) -> str:
    if not results:
        return ""

    parts = []

    for i, result in enumerate(results, start=1):
        parts.append(
            f"""
منبع {i}:
پایه: {result["grade"]}
درس: {result["subject"]}
صفحه: {result["page"]}
فایل: {result["source"]}

متن:
{result["text"]}
""".strip()
        )

    return "\n\n---\n\n".join(parts)