"""
Application entry point.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.app.api.v1.router import api_router
from src.app.exceptions.handlers import register_exception_handlers
import src.app.models


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown events.
    """

    # Startup
    yield

    # Shutdown


app = FastAPI(
    title="Job Radar API",
    description="Backend API for the Job Radar application.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

register_exception_handlers(app)

app.include_router(api_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}
