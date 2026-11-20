"""FastAPI application entry point and local static frontend hosting."""
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import PROJECT_ROOT, settings
from app.database.connection import DatabaseUnavailableError
from app.routes import assistants, chat, conversations, health
from app.services.llm_service import LLMServiceError

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

app = FastAPI(
    title="ROSE API",
    description="Backend for the ROSE modular multi-assistant platform.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.frontend_origins),
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type"],
)

app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(assistants.router, prefix="/api", tags=["assistants"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(conversations.router, prefix="/api", tags=["conversations"])


@app.exception_handler(DatabaseUnavailableError)
async def database_unavailable_handler(
    _request: Request, _exc: DatabaseUnavailableError
) -> JSONResponse:
    return JSONResponse(
        status_code=503,
        content={
            "detail": "MySQL is unavailable. Start MySQL and check the DATABASE_* settings in .env."
        },
    )


@app.exception_handler(LLMServiceError)
async def llm_error_handler(_request: Request, exc: LLMServiceError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": str(exc)})


frontend_path = PROJECT_ROOT / "frontend"
if frontend_path.is_dir():
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
