# Academia–Industry Collaboration Portal

A web app that helps students map their skills to internship opportunities. It includes resume skill extraction, internship recommendations, skill-gap analysis, learning plans, and an AI career assistant.

## Features

- Manage a student profile and confirmed skills.
- Parse a PDF or text resume and review extracted skills.
- Rank internships using skills, semantic relevance, and preferences.
- Analyze skill gaps and generate learning plans from curated resources.
- Ask the career agent questions about internships and preparation.
- Explore the REST API through FastAPI's interactive documentation.

## Tech stack

- **Frontend:** React, TypeScript, Vite
- **Backend:** Python, FastAPI, SQLAlchemy, SQLite
- **Recommendations:** Sentence Transformers and FAISS, with a fallback when the semantic embedder is unavailable
- **Optional AI provider:** Google Gemini

## Requirements

- Python and pip
- Node.js and npm

## Run locally

Open two terminals from the project root.

### 1. Start the backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

The backend runs at <http://localhost:8000>. On startup it creates the SQLite database (`backend/academia.db`) and seeds sample internship and learning-resource data if those tables are empty.

### 2. Start the frontend

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open <http://localhost:5173>. Vite proxies `/api` requests to the backend at `http://localhost:8000`.

## Configuration

The app works without external API credentials, using a deterministic career-agent provider by default. To use Google Gemini, set `GEMINI_API_KEY` before starting the backend. `GEMINI_MODEL` is optional and defaults to `gemini-2.5-flash`.

Other optional backend environment variables:

| Variable | Default | Description |
| --- | --- | --- |
| `DATABASE_URL` | SQLite database at `backend/academia.db` | SQLAlchemy database URL |
| `EMBEDDING_MODEL_NAME` | `all-MiniLM-L6-v2` | Sentence Transformers model used for semantic matching |

Keep credentials in a local `.env` or environment variables; do not commit secrets.

## API endpoints

With the backend running:

- Interactive API docs: <http://localhost:8000/docs>
- Health check: <http://localhost:8000/health>
- Profile and resume parsing: `/profile`
- Internship recommendations and details: `/internships/recommendations`, `/internships/{internship_id}`
- Skill-gap analysis: `/skill-gap`
- Learning plans: `/learning-plan`
- Career agent: `/agent/chat`

## Tests

Run the backend tests from the `backend` directory:

```powershell
python -m pytest
```

Build the frontend from the `frontend` directory:

```powershell
npm run build
```
