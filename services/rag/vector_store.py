from __future__ import annotations

import json
from pathlib import Path

import faiss
import numpy as np


class VectorStore:
    def __init__(
        self,
        index_path: str | Path,
        metadata_path: str | Path,
    ):
        self.index_path = Path(index_path)
        self.metadata_path = Path(metadata_path)

        self.index = None
        self.metadata = []

    def build(
        self,
        embeddings: np.ndarray,
        metadata: list[dict],
    ) -> None:
        embeddings = np.asarray(
            embeddings,
            dtype="float32",
        )

        dimension = embeddings.shape[1]

        self.index = faiss.IndexFlatIP(dimension)

        self.index.add(embeddings)

        self.metadata = metadata

    def save(self) -> None:
        if self.index is None:
            raise RuntimeError("Index has not been built.")

        self.index_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        faiss.write_index(
            self.index,
            str(self.index_path),
        )

        self.metadata_path.write_text(
            json.dumps(
                self.metadata,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    def load(self) -> None:
        self.index = faiss.read_index(
            str(self.index_path)
        )

        self.metadata = json.loads(
            self.metadata_path.read_text(
                encoding="utf-8"
            )
        )

    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5,
    ) -> list[dict]:
        if self.index is None:
            raise RuntimeError("Index is not loaded.")

        query_embedding = np.asarray(
            [query_embedding],
            dtype="float32",
        )

        scores, indices = self.index.search(
            query_embedding,
            top_k,
        )

        results = []

        for score, index in zip(
            scores[0],
            indices[0],
        ):
            if index == -1:
                continue

            item = {
                **self.metadata[index],
                "score": float(score),
            }

            results.append(item)

        return results