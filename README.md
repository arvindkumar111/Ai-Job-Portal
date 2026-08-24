## Presentaion video= https://drive.google.com/file/d/1X4xCJTZBOEY5X7OXYi5XCFgWGwgtuzH-/view?usp=sharing

## Deployment link = [ai-job-portal-gold.vercel.app](https://ai-job-portal-eq2eqax75-arvindkumar111s-projects.vercel.app/)

# AI Job Portal

An AI-assisted job discovery application with:

- Job browsing, filtering, pagination, and detail pages
- Resume upload and skill extraction
- Semantic job recommendations using PostgreSQL and pgvector
- Gemini-powered career chat with a fallback model
- A database-backed fallback when AI services are unavailable

## Project structure

```text
backend/
   app/                 FastAPI application, routers, services, and scripts
   data/                Local job-ingestion data (not included in GitHub)
   requirements.txt
frontend/
   src/                 React application
   public/              Static frontend assets
   package.json
README.md
```

## Requirements

- Python 3.11 recommended
- Node.js and npm
- PostgreSQL with the `vector` extension
- A Gemini API key for AI chat and optional job enrichment

The application expects job records and 384-dimensional embeddings in PostgreSQL.
Keyword recommendations are enabled by default so the web service does not need to
load PyTorch. The original RAG recommendation path remains available by setting
`RECOMMENDATION_MODE=rag` and installing the optional ML dependency.

To enable the original RAG recommendation mode in a larger-memory environment:

```powershell
pip install -r requirements-rag.txt
```

Then set:

```env
RECOMMENDATION_MODE=rag
```

## Environment setup

The real environment files are intentionally ignored by Git. Copy the examples:

```powershell
Copy-Item backend\.env.example backend\.env
Copy-Item frontend\.env.example frontend\.env
```

Set `backend/.env`:

```env
DATABASE_URL=postgresql+psycopg://username:password@host:5432/database
GEMINI_API_KEY=
LLM_MODEL=gemini-3.7-flash
FALLBACK_LLM_MODEL=gemini-3.5-flash-lite
ALLOWED_ORIGINS=["http://localhost:5173"]
```

Set `frontend/.env`:

```env
VITE_API_URL=http://127.0.0.1:8000/api
```

Never commit either real `.env` file or any API key and database password.

## Database setup

Create a PostgreSQL database with pgvector enabled. Then, from the backend directory,
create the tables:

```powershell
cd backend
..\.venv\Scripts\Activate.ps1
python -m app.scripts.create_tables
```

The large `backend/data/jobs_raw.json` source dataset is intentionally not stored in
GitHub because it exceeds GitHub's 100 MB file limit. Place that file at:

```text
backend/data/jobs_raw.json
```

If you have the dataset locally, run the full ingestion process from `backend`:

```powershell
python -m app.scripts.ingest
```

The ingestion script creates embeddings locally, removes duplicates, and enriches a
limited number of jobs through Gemini. `ingest_small.py` is available for a small test
run, but it currently only checks the first three records and does not insert them.

## Run locally

Open two terminals.

Backend terminal:

```powershell
cd C:\path\to\Ai-Job-Portal\backend
..\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Backend URLs:

- Health check: `http://127.0.0.1:8000/`
- API documentation: `http://127.0.0.1:8000/docs`

Frontend terminal:

```powershell
cd C:\path\to\Ai-Job-Portal\frontend
npm install
npm run dev
```

Open `http://localhost:5173` in a browser.

## Frontend production build

```powershell
cd frontend
npm run build
npm run preview
```

Set `VITE_API_URL` to the deployed backend URL before running the production build.

## Deployment outline

The frontend and backend are separate services:

```text
React/Vite frontend -> static site hosting
FastAPI backend      -> Python web service
PostgreSQL/pgvector  -> managed database
```

For a platform such as Render:

Backend:

```text
Root directory: backend
Build command: pip install -r requirements.txt
Start command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Frontend:

```text
Root directory: frontend
Build command: npm install && npm run build
Publish directory: dist
```

Production variables should include:

```env
DATABASE_URL=your-managed-postgresql-url
ALLOWED_ORIGINS=["https://your-frontend-domain.com"]
VITE_API_URL=https://your-backend-domain.com/api
```

Create the production tables and ingest the job data separately. Do not use a local
virtual environment or local `.env` file as a production secret store.

## Security notes

- `.gitignore` excludes secrets, virtual environments, dependencies, build output, and caches.
- Resume uploads are limited to PDF/DOCX files and 5 MB.
- Chat and resume endpoints have request limits and basic rate limiting.
- Use HTTPS, rotate exposed credentials, and restrict production CORS to the frontend domain.
