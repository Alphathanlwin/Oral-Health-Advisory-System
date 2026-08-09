from fastapi import FastAPI

app = FastAPI(title="OHAS API", version="1.0.0")


@app.get("/api/v1/health")
async def health():
    return {"status": "ok"}
