# AI-Powered Job Board

This repository contains a starter backend scaffold for an AI-powered job board project with:
- job ingestion from a structured JSON dataset
- deduplication
- LLM-based job enrichment
- resume parsing and personalization
- recommendation logic
- Gemini-backed chat assistant

The backend is structured around a FastAPI app and SQLAlchemy models.

## Folder structure

- backend/app/
- backend/data/
- backend/requirements.txt
- backend/.env
- frontend/

## Local startup

1. Create and activate a virtual environment.
2. Install backend requirements:
   pip install -r backend/requirements.txt
3. Add your environment variables in backend/.env
4. Run the FastAPI server:
   uvicorn backend.app.main:app --reload

This is a starter scaffold, not a full production deployment.
