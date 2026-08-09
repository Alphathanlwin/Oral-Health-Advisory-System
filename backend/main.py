from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from routers import auth
from utils.response import error_response

app = FastAPI(title="OHAS API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if isinstance(exc.detail, dict) and "code" in exc.detail:
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response(exc.detail["code"], exc.detail["message"]),
        )
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response("REQUEST_ERROR", str(exc.detail)),
    )


@app.get("/api/v1/health")
async def health():
    return {"status": "ok"}
