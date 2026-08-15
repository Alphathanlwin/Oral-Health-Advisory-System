# Oral Health Advisory System (OHAS)

## Backend

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Runs at `http://localhost:8000` (and `http://<your-lan-ip>:8000` for other devices on the same Wi-Fi).

## Frontend

```powershell
cd frontend
npm run dev
```

Runs at `https://localhost:5173` (and `https://<your-lan-ip>:5173` for other devices, e.g. testing the camera flow on a phone — accept the self-signed certificate warning).
