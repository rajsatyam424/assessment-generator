"""
FastAPI application — assessment generation API.

Endpoints:
    POST /generate — generate a new assessment, returns JSON
    GET  /health — health check
"""

import logging
import json
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from . import config
from .orchestrator import generate

logger = logging.getLogger(__name__)


class GenerateRequest(BaseModel):
    course_name: str = Field(
        ..., min_length=1, max_length=200,
        description="Name of the course or topic for the assessment",
        examples=["First Aid Basics"],
    )
    model: Optional[str] = Field(None)
    provider: Optional[str] = Field(None)


class GenerateResponse(BaseModel):
    assessment_name: str
    learning_outcomes: list[str]
    topics: list[str]
    questions: list[dict]
    issues: Optional[list[str]] = None
    success: bool


class HealthResponse(BaseModel):
    status: str
    provider: str
    model: str
    version: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not config.API_KEY:
        logger.warning("No API key set — generation will fail. Set OPENROUTER_API_KEY env var.")
    yield


app = FastAPI(
    title="Assessment Generator API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)


@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="ok",
        provider=config.PROVIDER,
        model=config.MODEL,
        version="1.0.0",
    )


@app.post("/generate", response_model=GenerateResponse)
async def generate_assessment(req: GenerateRequest):
    result = generate(
        course_name=req.course_name.strip(),
        model=req.model,
        provider=req.provider,
    )

    if not result.success:
        raise HTTPException(
            status_code=500,
            detail={"issues": result.issues, "success": False},
        )

    return GenerateResponse(
        assessment_name=result.assessment_name,
        learning_outcomes=result.preview.get("learning_outcomes", []),
        topics=result.preview.get("topics", []),
        questions=result.data.get("questions", []),
        issues=result.issues or None,
        success=True,
    )
