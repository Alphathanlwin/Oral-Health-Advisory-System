# Oral Health Advisory System (OHAS)

## Backend

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn main:app --host 0.0.0.0 --port 8000
```

Runs at `http://localhost:8000` (and `http://<your-lan-ip>:8000` for other devices on the same Wi-Fi).

> **No `--reload`.** The diagnosis engine runs SWI-Prolog as a subprocess
> (`asyncio.create_subprocess_exec`), which requires Windows' Proactor event
> loop. `uvicorn --reload` spawns its worker via `multiprocessing`, which on
> Windows lands on a loop that doesn't support subprocesses at all — every
> assessment submission fails with a bare `NotImplementedError`. Restart the
> server manually after backend code changes instead.

## Frontend

```powershell
cd frontend
npm run dev
```

Runs at `https://localhost:5173` (and `https://<your-lan-ip>:5173` for other devices, e.g. testing the camera flow on a phone — accept the self-signed certificate warning).

## Phone Access

With both servers running, open on your phone (same Wi-Fi):

```text
https://10.224.87.70:5173
```

> This IP is this machine's current Wi-Fi address — it can change (e.g. after
> reconnecting to Wi-Fi or a DHCP lease renewal). If the page won't load,
> get the current one with:
>
> ```powershell
> Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias "Wi-Fi" | Select-Object IPAddress
> ```
