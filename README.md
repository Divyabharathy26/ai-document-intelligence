# DocuMind — AI Document Intelligence Platform

DocuMind is an AI-powered web application for analyzing PDF documents. Users can ask questions about document content, review supporting passages with page references, and generate document summaries.

## Features

- PDF text extraction
- Document question answering using retrieval-augmented generation (RAG)
- Answers grounded in retrieved document passages
- Page-based source citations
- AI-powered PDF summarization
- Responsive web interface

## Technology Stack

**Frontend:** React, TypeScript, Vite

**Backend:** Python, FastAPI

**AI:** Google Gemini API

**PDF Processing:** PyPDF

## Project Structure

- `backend/` — FastAPI application and AI services
- `frontend/` — React and TypeScript application
- `README.md` — Project documentation

## Local Setup

### Backend

From the project root, open PowerShell and run:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create a `backend/.env` file containing your Gemini API key and the model configuration required by your application. Never commit this file.

Start the API:

```powershell
python -m uvicorn app.main:app --reload
```

API documentation: `http://127.0.0.1:8000/docs`

### Frontend

Open a separate terminal:

```powershell
cd frontend
npm install
npm run dev
```

Use the local URL printed by Vite to open the application.

Configure `VITE_API_BASE_URL` to point to the backend. Do not put the Gemini API key in frontend environment variables.

## Security and Limitations

- Keep API keys and environment files out of version control.
- Configure production CORS and environment variables before deployment.
- Scanned PDFs without extractable text may not be supported.
- Gemini usage is subject to the selected model's availability and API quota.
- Review storage, persistence, request limits, and error handling before production use.

## Project Status

Portfolio project in development.
