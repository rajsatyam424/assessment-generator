"""
FastAPI application -- assessment generation API.

Endpoints:
    POST /start      -- returns prompt for client-side LLM call (<1s)
    POST /validate   -- parses and validates raw LLM output (<1s)
    POST /generate   -- full pipeline (may timeout on Vercel Hobby)
    GET  /health     -- health check
"""

import os
import hashlib
import logging
import json
import time
from contextlib import asynccontextmanager
from typing import Optional

# Load .env before anything else
_env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
if os.path.exists(_env_path):
    with open(_env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from . import config
from .prompt import build_prompt
from .orchestrator import generate
from .parser import parse_response, ParseError
from .validator import validate

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


class StartRequest(BaseModel):
    course_name: str = Field(
        ..., min_length=1, max_length=200,
        description="Name of the course or topic for the assessment",
    )


class StartResponse(BaseModel):
    prompt_id: str
    prompt: str
    model: str
    base_url: str
    api_key: str


class ValidateRequest(BaseModel):
    prompt_id: str = Field(..., description="ID from /start response")
    raw_output: str = Field(..., description="Raw text returned by the LLM", min_length=10)


class ValidateResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    issues: list[str] = []


class HealthResponse(BaseModel):
    status: str
    provider: str
    model: str
    version: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not config.API_KEY:
        logger.warning("No API key set -- generation will fail. Set DEEPSEEK_API_KEY or OPENROUTER_API_KEY env var.")
    yield


app = FastAPI(
    title="Assessment Generator API",
    version="1.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Allow browser frontend to call our API from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", include_in_schema=False)
async def index():
    from fastapi.responses import HTMLResponse
    index_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static", "index.html")
    if os.path.isfile(index_path):
        with open(index_path) as f:
            return HTMLResponse(f.read())
    return HTMLResponse("<h1>Assessment Generator API</h1><p>Frontend not found.</p>")


@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="ok",
        provider=config.PROVIDER,
        model=config.MODEL,
        version="1.1.0",
    )


@app.post("/start", response_model=StartResponse)
async def start_assessment(req: StartRequest):
    """Return the prompt + config for client-side LLM call. No LLM call, <1s."""
    course = req.course_name.strip()
    prompt = build_prompt(course)
    prompt_id = hashlib.sha256((course + str(time.time())).encode()).hexdigest()[:12]

    return StartResponse(
        prompt_id=prompt_id,
        prompt=prompt,
        model=config.MODEL,
        base_url="https://api.deepseek.com/v1",
        api_key=config.API_KEY,
    )


@app.post("/validate", response_model=ValidateResponse)
async def validate_assessment(req: ValidateRequest):
    """Parse and validate raw LLM output. No LLM call, <1s."""
    try:
        data = parse_response(req.raw_output)
    except ParseError as e:
        return ValidateResponse(success=False, issues=[f"Parse error: {e}"])
    except Exception as e:
        return ValidateResponse(success=False, issues=[f"Unexpected error: {e}"])

    result = validate(data)

    return ValidateResponse(
        success=result.passed,
        data=data if result.passed else None,
        issues=result.issues,
    )


@app.post("/generate", response_model=GenerateResponse)
async def generate_assessment(req: GenerateRequest):
    """Full pipeline -- may timeout on Vercel Hobby (10s limit)."""
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
