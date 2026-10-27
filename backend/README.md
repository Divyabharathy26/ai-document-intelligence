# DocuMind Backend

## Overview
The DocuMind backend provides REST APIs for PDF processing, document question answering, and AI-powered summarization.

## Technology Stack
- Python
- FastAPI
- Google Gemini API
- PDF text extraction and retrieval-augmented generation (RAG)

## Local Setup

Run these commands from the project root in PowerShell:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create a `.env` file in the `backend` directory and configure the environment variables required by the application. Keep API keys private and never commit `.env` to GitHub.

## Run the API

```powershell
python -m uvicorn app.main:app --reload
```

API base URL: `http://127.0.0.1:8000`

Interactive API documentation: `http://127.0.0.1:8000/docs`

## Deployment Notes
Configure the required environment variables in your hosting provider. Set production CORS origins appropriately and verify the API endpoints after deployment.

## Limitations
Supported PDF processing depends on the document's extractable text. AI requests are subject to the configured Gemini model's availability and usage quotas.
