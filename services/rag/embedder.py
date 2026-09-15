from __future__ import annotations

from functools import lru_cache

from sentence_transformers import SentenceTransformer

MODEL_NAME = "BAAI/bge-m3"


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    return SentenceTransformer(MODEL_NAME)


def embed_texts(texts: list[str]):
    model = get_embedding_model()

    return model.encode(
        texts,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=True,
    )


def embed_query(query: str):
    model = get_embedding_model()

    return model.encode(
        query,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )
