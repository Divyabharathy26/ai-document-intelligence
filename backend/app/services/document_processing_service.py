
from typing import Any

from app.services.chunking_service import chunk_document_pages
from app.services.pdf_service import extract_pdf_text


def process_pdf_document(file_bytes: bytes) -> dict[str, Any]:
    """Extract a PDF and prepare page-aware chunks for retrieval."""

    extracted = extract_pdf_text(file_bytes)

    chunks = chunk_document_pages(
        pages=extracted["pages"],
    )

    if not chunks:
        raise ValueError(
            "No usable text chunks could be generated from the PDF."
        )

    return {
        "page_count": extracted["page_count"],
        "character_count": len(extracted["text"]),
        "chunks": chunks,
        "chunk_count": len(chunks),
    }
