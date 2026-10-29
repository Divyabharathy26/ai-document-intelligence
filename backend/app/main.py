
import logging

import httpx
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.services.gemini_service import generate_ai_response
from app.services.pdf_service import extract_pdf_text
from app.services.summarization_service import summarize_document
from app.services.document_processing_service import process_pdf_document
from app.services.vector_store_service import create_vector_index
from app.services.rag_service import answer_document_question


# --------------------------------------------------
# Logging
# --------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --------------------------------------------------
# Application configuration
# --------------------------------------------------

app = FastAPI(
    title="AI Document Intelligence Platform",
    description="AI-powered document analysis and question answering.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://ai-document-intelligence-xi.vercel.app",
        "https://ai-document-intelligence-git-main-divyabharathy26.vercel.app",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_PDF_SIZE = 10 * 1024 * 1024  # 10 MB


# --------------------------------------------------
# Request and response schemas
# --------------------------------------------------

class AITestRequest(BaseModel):
    prompt: str = Field(min_length=3, max_length=1000)


class AITestResponse(BaseModel):
    response: str


# --------------------------------------------------
# Shared PDF validation
# --------------------------------------------------

async def read_pdf_upload(file: UploadFile) -> bytes:
    """Validate and read a PDF upload with a 10 MB limit."""

    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=415,
            detail="Please upload a PDF file.",
        )

    try:
        content = await file.read(MAX_PDF_SIZE + 1)
    finally:
        await file.close()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty.",
        )

    if len(content) > MAX_PDF_SIZE:
        raise HTTPException(
            status_code=413,
            detail="The PDF must not exceed 10 MB.",
        )

    return content


# --------------------------------------------------
# Root and health endpoints
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "AI Document Intelligence Platform API",
        "status": "running",
    }


@app.get("/health")
def health_check():
    """Lightweight health check for Render."""

    return {"status": "healthy"}


# --------------------------------------------------
# AI connectivity test
# --------------------------------------------------

@app.post("/api/ai-test", response_model=AITestResponse)
def ai_test(request: AITestRequest):
    try:
        result = generate_ai_response(request.prompt)
        return AITestResponse(response=result)

    except RuntimeError as exc:
        logger.exception("AI test failed")

        raise HTTPException(
            status_code=502,
            detail="The AI service is temporarily unavailable.",
        ) from exc

    except httpx.RequestError as exc:
        logger.exception("Network error during AI test")

        raise HTTPException(
            status_code=503,
            detail="Could not connect to the AI service.",
        ) from exc

    except Exception as exc:
        logger.exception("Unexpected AI test error")

        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred during the AI test.",
        ) from exc


# --------------------------------------------------
# Extract PDF text
# --------------------------------------------------

@app.post("/api/documents/extract")
async def extract_document(file: UploadFile = File(...)):
    content = await read_pdf_upload(file)

    try:
        result = extract_pdf_text(content)

        return {
            "filename": file.filename,
            "page_count": result["page_count"],
            "character_count": len(result["text"]),
            "text": result["text"],
        }

    except HTTPException:
        raise

    except ValueError as exc:
        logger.warning("PDF extraction validation failed: %s", exc)

        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        logger.exception("PDF extraction failed")

        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while extracting the PDF.",
        ) from exc


# --------------------------------------------------
# Summarize PDF
# --------------------------------------------------

@app.post("/api/documents/summarize")
async def summarize_uploaded_document(file: UploadFile = File(...)):
    content = await read_pdf_upload(file)

    try:
        extracted = extract_pdf_text(content)
        result = summarize_document(extracted["text"])

        return {
            "filename": file.filename,
            "page_count": extracted["page_count"],
            "summary": result["summary"],
            "character_count": result["character_count"],
        }

    except HTTPException:
        raise

    except ValueError as exc:
        logger.warning("Document summarization validation failed: %s", exc)

        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except RuntimeError as exc:
        logger.exception("Document summarization AI failure")

        raise HTTPException(
            status_code=502,
            detail="The AI service is temporarily unavailable.",
        ) from exc

    except httpx.RequestError as exc:
        logger.exception("Document summarization network failure")

        raise HTTPException(
            status_code=503,
            detail="Could not connect to the AI service.",
        ) from exc

    except Exception as exc:
        logger.exception("Unexpected document summarization error")

        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing the PDF.",
        ) from exc


# --------------------------------------------------
# Chat with PDF using retrieval-augmented generation
# --------------------------------------------------

@app.post("/api/documents/chat")
async def chat_with_document(
    question: str = Query(min_length=3, max_length=1000),
    file: UploadFile = File(...),
):
    content = await read_pdf_upload(file)
    filename = file.filename or "uploaded.pdf"

    try:
        logger.info(
            "Document chat started: filename=%s, question_length=%d",
            filename,
            len(question),
        )

        # Stage 1: Extract and split the PDF.
        document = process_pdf_document(content)
        chunks = document.get("chunks", [])

        if not chunks:
            raise HTTPException(
                status_code=422,
                detail="No readable text was found in the PDF.",
            )

        logger.info(
            "PDF processing completed: filename=%s, pages=%d, chunks=%d",
            filename,
            document["page_count"],
            len(chunks),
        )

        # Stage 2: Create the vector index using embeddings.
        indexed_chunks = create_vector_index(chunks)

        if not indexed_chunks:
            raise RuntimeError(
                "The vector index did not contain any indexed chunks."
            )

        logger.info(
            "Vector index created successfully: chunks=%d",
            len(indexed_chunks),
        )

        # Stage 3: Retrieve relevant passages and generate the answer.
        result = answer_document_question(
            question=question.strip(),
            indexed_chunks=indexed_chunks,
        )

        logger.info(
            "Document chat completed successfully: filename=%s",
            filename,
        )

        return {
            "filename": filename,
            "page_count": document["page_count"],
            "answer": result["answer"],
            "citations": result["citations"],
        }

    except HTTPException:
        raise

    except ValueError as exc:
        logger.warning("Invalid document chat input: %s", exc)

        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except RuntimeError as exc:
        # The traceback includes the underlying exception chain.
        logger.exception("Document chat service failure")

        raise HTTPException(
            status_code=502,
            detail=(
                "The AI service is temporarily unavailable. "
                "Please try again later."
            ),
        ) from exc

    except httpx.RequestError as exc:
        logger.exception("Document chat network failure")

        raise HTTPException(
            status_code=503,
            detail="A network error occurred while contacting the AI service.",
        ) from exc

    except Exception as exc:
        logger.exception(
            "Unexpected document chat error: filename=%s",
            filename,
        )

        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while answering the question.",
        ) from exc
