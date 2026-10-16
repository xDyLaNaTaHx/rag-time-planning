# RAG Time Planning

Takes the user's goals and time constraints, then recommends how to budget the week using retrieval-augmented generation.

## Setup

```powershell
# Backend
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# Ensure .env has AI_KEY and AI_MODEL

# Frontend
cd frontend
npm install
```

## Run

Terminal 1 — API:

```powershell
uvicorn src.ui:app --reload
```

Terminal 2 — UI:

```powershell
cd frontend
npm run dev
```

Open [http://localhost:5173](http://localhost:5173).

API docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## API

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/goals` | List goals |
| `PUT` | `/api/goals` | Replace goals |
| `GET` | `/api/constraints` | List constraints |
| `PUT` | `/api/constraints` | Replace constraints |
| `POST` | `/api/schedule/generate` | Propose a weekly schedule |

AI failures return a structured error body `{ "code": "...", "message": "..." }` (for example `ai_provider_error` with HTTP 503) without leaking provider internals. The UI shows an **AI recommendation failed** banner in those cases.

## Tests

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest
```
