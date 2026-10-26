
from typing import Any


DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 150


def chunk_document_pages(
    pages: list[dict[str, Any]],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[dict[str, Any]]:
    """Split page text into overlapping chunks with page metadata."""

    if chunk_size <= 0:
        raise ValueError("Chunk size must be greater than zero.")

    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError(
            "Chunk overlap must be non-negative and smaller "
            "than the chunk size."
        )

    chunks = []
    step = chunk_size - chunk_overlap

    for page in pages:
        page_number = page.get("page_number")
        text = page.get("text", "").strip()

        if not isinstance(page_number, int) or page_number < 1:
            raise ValueError("Each page must have a valid page number.")

        if not isinstance(text, str) or not text:
            continue

        start = 0

        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append(
                    {
                        "chunk_id": len(chunks),
                        "page_number": page_number,
                        "text": chunk_text,
                    }
                )

            if end == len(text):
                break

            start += step

    return chunks
