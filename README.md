# Oral Health Advisory System (OHAS)

An AI-powered oral health advisory web app: a guided symptom questionnaire (plus optional mouth photo) run through a SWI-Prolog knowledge base to infer possible dental conditions with explainable risk levels and recommendations.

**Stack**: Vite + React · FastAPI · SWI-Prolog · PostgreSQL · JWT

> Disclaimer: OHAS is an educational project. It does not replace a licensed dentist.

## Project Structure

```
backend/       FastAPI app (auth, assessments, Prolog engine, CV)
context-kit/   Design docs, build plan, progress tracker, standards
frontend/      Vite + React SPA (not yet initialized)
```

## Backend Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 15+ (a Supabase free-tier instance works)
- SWI-Prolog (only needed for Phase 3 diagnosis engine)

### 1. Create and activate a virtual environment

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure environment

Copy the template and fill in real values:

```powershell
Copy-Item .env.example .env
```

Edit `.env`:

```
DATABASE_URL=postgresql+asyncpg://USER:PASSWORD@HOST:PORT/postgres?ssl=require
SECRET_KEY=your-jwt-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
HUGGINGFACE_API_TOKEN=hf_xxxxxxxxxxxxxxxxxxxx
HUGGINGFACE_MODEL_URL=https://api-inference.huggingface.co/models/xxxxxxxx/xxxxxxxx
```

> **Supabase note**: use the **Transaction pooler** connection string
> (`aws-0-<region>.pooler.supabase.com:6543`) rather than the direct
> `db.<ref>.supabase.co:5432` host, which is IPv6-only. The pooler requires
> `?ssl=require`. If you see `DuplicatePreparedStatementError`, statement
> caching has already been disabled for you in `database.py`.

### 4. Run database migrations

```powershell
alembic upgrade head
```

### 5. Start the server

```powershell
uvicorn main:app --reload --port 8000
```

The API is served at `http://localhost:8000`. Interactive docs (Swagger UI) are at `http://localhost:8000/docs`.

## Backend API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/health` | GET | Health check |
| `/api/v1/auth/register` | POST | Create an account |
| `/api/v1/auth/login` | POST | Login, returns a JWT |
| `/api/v1/assessments/` | POST | Submit a symptom assessment (Phase 2+) |
| `/api/v1/assessments/` | GET | List your assessments (Phase 5+) |
| `/api/v1/assessments/{id}` | GET | Assessment detail (Phase 5+) |

All assessment endpoints require `Authorization: Bearer <token>`.

## Quick Smoke Test

Register a user and log in with PowerShell:

```powershell
$body = '{"email":"test@example.com","password":"SecurePassword123","full_name":"Test User"}'
Invoke-RestMethod -Uri http://localhost:8000/api/v1/auth/register -Method Post -ContentType "application/json" -Body $body

$login = '{"email":"test@example.com","password":"SecurePassword123"}'
Invoke-RestMethod -Uri http://localhost:8000/api/v1/auth/login -Method Post -ContentType "application/json" -Body $login
```

## Frontend (Phase 1+)

Not yet implemented. Planned commands:

```powershell
cd frontend
npm install
npm run dev     # serves on http://localhost:5173
```

## Docs

Design and implementation details live in `context-kit/` — start with `project-overview.md` and `architecture.md`.
