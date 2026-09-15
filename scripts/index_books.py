from __future__ import annotations

from pathlib import Path

import numpy as np

from services.rag.chunker import chunk_pages
from services.rag.embedder import embed_texts
from services.rag.pdf_loader import load_pdf_pages
from services.rag.vector_store import VectorStore

BOOKS_DIR = Path("data/books")
VECTOR_STORE_DIR = Path("data/vector_store")

INDEX_PATH = VECTOR_STORE_DIR / "index.faiss"
METADATA_PATH = VECTOR_STORE_DIR / "metadata.json"


def collect_pdf_files() -> list[Path]:
    return sorted(BOOKS_DIR.rglob("*.pdf"))


def build_metadata(
    pdf_path: Path,
    chunks: list[dict],
) -> list[dict]:
    relative_path = pdf_path.relative_to(BOOKS_DIR)

    parts = relative_path.parts

    grade = parts[0] if len(parts) > 1 else None
    subject = pdf_path.stem

    metadata = []

    for chunk in chunks:
        metadata.append(
            {
                "id": chunk["id"],
                "source": str(relative_path),
                "grade": grade,
                "subject": subject,
                "page": chunk["page"],
                "text": chunk["text"],
            }
        )

    return metadata


def main() -> None:
    pdf_files = collect_pdf_files()

    if not pdf_files:
        raise RuntimeError(f"No PDF files found in {BOOKS_DIR}")

    all_chunks = []
    all_metadata = []

    global_chunk_id = 0

    for pdf_path in pdf_files:
        print(f"\nProcessing: {pdf_path}")

        pages = load_pdf_pages(pdf_path)

        print(f"  pages: {len(pages)}")

        chunks = chunk_pages(pages)

        print(f"  chunks: {len(chunks)}")

        metadata = build_metadata(
            pdf_path,
            chunks,
        )

        for item in metadata:
            item["id"] = global_chunk_id
            global_chunk_id += 1

        all_chunks.extend(item["text"] for item in metadata)

        all_metadata.extend(metadata)

    print("\nEmbedding...")
    print(f"Total chunks: {len(all_chunks)}")

    embeddings = embed_texts(all_chunks)

    print("Embedding shape:", embeddings.shape)

    embeddings = np.asarray(
        embeddings,
        dtype="float32",
    )

    store = VectorStore(
        index_path=INDEX_PATH,
        metadata_path=METADATA_PATH,
    )

    store.build(
        embeddings=embeddings,
        metadata=all_metadata,
    )

    store.save()

    print("\nIndex saved successfully.")
    print(f"Index: {INDEX_PATH}")
    print(f"Metadata: {METADATA_PATH}")


if __name__ == "__main__":
    main()
