# Oral Health Advisory System (OHAS)

OHAS is a FastAPI + React oral-health triage application that supports both a static symptom questionnaire and a guided live screening flow, backed by a SWI-Prolog risk engine and structured result pages.

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL database
- SWI-Prolog installed and available on PATH
- A working `.env` file for both frontend/backend, depending on your deployment setup

## Backend setup

1. Open a terminal in the backend folder.
2. Create and activate a virtual environment:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies:

```powershell
pip install -r requirements.txt
```

4. Configure your database and secrets in `backend/.env` (or the project environment) as required by `config.py`.
5. Run the database migrations:

```powershell
alembic upgrade head
```

6. Start the API server:

```powershell
uvicorn main:app --host 0.0.0.0 --port 8000
```

The API is available at `http://localhost:8000` and `http://<your-lan-ip>:8000`.

> Important: do not use `--reload` on Windows while the backend is invoking SWI-Prolog in a subprocess. The diagnosis engine relies on the Proactor event loop for subprocess execution; `uvicorn --reload` can break that flow.

## Frontend setup

1. Open a terminal in the frontend folder.
2. Install dependencies:

```powershell
cd frontend
npm install
```

3. Start the app:

```powershell
npm run dev -- --host 0.0.0.0
```

The frontend runs at `https://localhost:5173` and can be reached from a phone on the same network using the machine's LAN IP.

## Phone Access (yours or a friend's)

Anyone on the **same Wi-Fi network** as this machine — you or a friend — can open the app on their phone once both servers above are running:

```text
https://172.20.11.222:5173
```

> This is this machine's current Wi-Fi IP — it can change (different network,
> reconnecting, DHCP lease renewal). Get the current one with:
>
> ```powershell
> Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias "Wi-Fi" | Select-Object IPAddress
> ```
>
> No code change needed when it does — the dev cert (`vite.config.js`) is
> generated fresh on every server start and automatically covers whatever
> LAN IP(s) the machine currently has.

**First time on each phone:** the browser will warn that the connection isn't
private (it's a self-signed dev certificate, not a public browser-trusted
one). This is expected — tap **Advanced → proceed anyway** (Android
Chrome) or the equivalent option on your browser. Each phone needs to do
this once; after that it won't ask again for that address.

## Demo and test flow

- Register or log in using the auth UI.
- Use either the static questionnaire under `/assessment/new` or the live screening flow at `/assessment/live`.
- Review the generated result on the result page, including disclaimer copy, recommendations, and risk badge.
- Open the history dashboard to review prior assessments and pagination state.

## Common issues

- If the backend reports 500 errors, confirm the database and Prolog engine are both reachable.
- If the live camera path fails on a phone, use HTTPS/localhost as required by browser secure-context rules.
- If `uvicorn` crashes after a code change, restart it manually rather than using `--reload` on Windows.

## Project structure

- `backend/` — FastAPI app, services, models, Prolog engine, and auth routes
- `frontend/` — Vite + React patient experience
- `context-kit/` — product, architecture, API, and design documentation
- `OHAS.pen` — design source for the app UI system
