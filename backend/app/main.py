import logging
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.services.gemini_service import generate_ai_response
from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from app.services.pdf_service import extract_pdf_text
from app.services.summarization_service import summarize_document

from app.services.document_processing_service import process_pdf_document
from app.services.vector_store_service import create_vector_index
from app.services.rag_service import answer_document_question

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Document Intelligence Platform",
    description="AI-powered document analysis and question answering.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)


class AITestRequest(BaseModel):
    prompt: str = Field(min_length=3, max_length=1000)


class AITestResponse(BaseModel):
    response: str


class DocumentChatRequest(BaseModel):
    question: str = Query(min_length=3, max_length=1000),


@app.get("/")
def root():
    return {
        "message": "AI Document Intelligence Platform API",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/api/ai-test", response_model=AITestResponse)
def ai_test(request: AITestRequest):
    try:
        result = generate_ai_response(request.prompt)
        return AITestResponse(response=result)

    except RuntimeError as exc:
        logger.warning("AI request failed: %s", exc)
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc

    except Exception:
        logger.exception("Unexpected AI service error")
        raise HTTPException(
            status_code=502,
            detail="The AI service is temporarily unavailable.",
        )
MAX_PDF_SIZE = 10 * 1024 * 1024  # 10 MB

@app.post("/api/documents/extract")
async def extract_document(file: UploadFile = File(...)):
    """Upload a PDF and extract its text."""

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

    try:
        result = extract_pdf_text(content)

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    return {
        "filename": file.filename,
        "page_count": result["page_count"],
        "character_count": len(result["text"]),
        "text": result["text"],
    }


@app.post("/api/documents/summarize")
async def summarize_uploaded_document(file: UploadFile = File(...)):
    """Upload a PDF and return its AI-generated summary."""

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

    try:
        extracted = extract_pdf_text(content)
        result = summarize_document(extracted["text"])

        return {
            "filename": file.filename,
            "page_count": extracted["page_count"],
            "summary": result["summary"],
            "character_count": result["character_count"],
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except RuntimeError as exc:
        logger.warning("Document summarization failed: %s", exc)
        raise HTTPException(
            status_code=502,
            detail=(
                "The AI service is temporarily unavailable. "
                "Please try again later."
            ),
        ) from exc
    except httpx.RequestError:
        logger.warning(
            "Network error while contacting the AI service",
            exc_info=True,
        )
        raise HTTPException(
            status_code=503,
            detail=(
                "The AI service could not be reached. "
                "Please check your internet connection and retry."
            ),
        )
    except Exception:
        logger.exception("Unexpected document summarization error")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing the PDF.",
        )


@app.post("/api/documents/chat")
async def chat_with_document(
    question: str = __import__("fastapi").Query(
        min_length=3,
        max_length=1000,
    ),
    file: UploadFile = File(...),
):
    """Answer a question using evidence retrieved from an uploaded PDF."""

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

    try:
        document = process_pdf_document(content)
        indexed_chunks = create_vector_index(document["chunks"])

        result = answer_document_question(
            question=question,
            indexed_chunks=indexed_chunks,
        )

        return {
            "filename": file.filename,
            "page_count": document["page_count"],
            "answer": result["answer"],
            "citations": result["citations"],
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except RuntimeError as exc:
        logger.warning("Document chat failed: %s", exc)
        raise HTTPException(
            status_code=502,
            detail="The AI service is temporarily unavailable.",
        ) from exc

    except Exception:
        logger.exception("Unexpected document chat error")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while answering the question.",
        )

