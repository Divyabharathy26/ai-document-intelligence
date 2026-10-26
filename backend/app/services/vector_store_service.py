
import math
from typing import Any

from app.services.embedding_service import generate_embedding


def cosine_similarity(
    vector_a: list[float],
    vector_b: list[float],
) -> float:
    """Calculate cosine similarity between two vectors."""

    if len(vector_a) != len(vector_b):
        raise ValueError("Embedding dimensions must match.")

    dot_product = sum(
        a * b for a, b in zip(vector_a, vector_b)
    )

    norm_a = math.sqrt(sum(a * a for a in vector_a))
    norm_b = math.sqrt(sum(b * b for b in vector_b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot_product / (norm_a * norm_b)


def create_vector_index(
    chunks: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Generate and attach embeddings to document chunks."""

    indexed_chunks = []

    for chunk in chunks:
        text = chunk.get("text", "").strip()

        if not text:
            continue

        embedding = generate_embedding(text)

        indexed_chunks.append(
            {
                "chunk_id": chunk["chunk_id"],
                "page_number": chunk["page_number"],
                "text": text,
                "embedding": embedding,
            }
        )

    if not indexed_chunks:
        raise ValueError("No valid chunks were provided.")

    return indexed_chunks


def retrieve_relevant_chunks(
    question: str,
    indexed_chunks: list[dict[str, Any]],
    top_k: int = 4,
) -> list[dict[str, Any]]:
    """Return the most semantically relevant document chunks."""

    if not question or not question.strip():
        raise ValueError("Question must not be empty.")

    if top_k < 1:
        raise ValueError("top_k must be at least 1.")

    if not indexed_chunks:
        raise ValueError("The document index is empty.")

    question_embedding = generate_embedding(question.strip())

    scored_chunks = []

    for chunk in indexed_chunks:
        score = cosine_similarity(
            question_embedding,
            chunk["embedding"],
        )

        scored_chunks.append(
            {
                "chunk_id": chunk["chunk_id"],
                "page_number": chunk["page_number"],
                "text": chunk["text"],
                "similarity": score,
            }
        )

    scored_chunks.sort(
        key=lambda item: item["similarity"],
        reverse=True,
    )

    return scored_chunks[:top_k]
