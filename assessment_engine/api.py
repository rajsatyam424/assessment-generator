"""
FastAPI application — assessment generation API.

Endpoints:
    POST /generate — generate a new assessment
    GET  /download/{filename} — download a .docx
    GET  /health — health check
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from . import config
from .orchestrator import generate
from . import docx_builder as docx_module

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------


class GenerateRequest(BaseModel):
    course_name: str = Field(
        ..., min_length=1, max_length=200,
        description="Name of the course or topic for the assessment",
        examples=["First Aid Basics"],
    )
    model: Optional[str] = Field(
        None, description="LLM model override (e.g. gpt-4o-mini, anthropic/claude-sonnet-4)"
    )
    provider: Optional[str] = Field(
        None, description="LLM provider (openai, openrouter)"
    )


class GenerateResponse(BaseModel):
    assessment_name: str
    download_url: str
    preview: dict
    issues: Optional[list[str]] = None
    success: bool


class HealthResponse(BaseModel):
    status: str
    provider: str
    model: str
    version: str


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown."""
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if not config.API_KEY:
        logger.warning("OPENAI_API_KEY not set — generation will fail")
    yield


app = FastAPI(
    title="Assessment Generator API",
    description=(
        "Generate 25-question multiple choice assessments for any course. "
        "Uses AI to create questions, explanations, and a formatted .docx file."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# Background cleanup
# ---------------------------------------------------------------------------


def _cleanup_old_files():
    """Remove assessment files older than CLEANUP_HOURS."""
    cutoff = datetime.now() - timedelta(hours=config.CLEANUP_HOURS)
    removed = 0
    for f in config.OUTPUT_DIR.iterdir():
        if f.is_file() and f.suffix == ".docx":
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            if mtime < cutoff:
                f.unlink()
                removed += 1
    if removed:
        logger.info("Cleaned up %d old assessment files", removed)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="ok",
        provider=config.PROVIDER,
        model=config.MODEL,
        version="1.0.0",
    )


@app.post("/generate", response_model=GenerateResponse)
async def generate_assessment(
    req: GenerateRequest,
    bg_tasks: BackgroundTasks,
):
    """
    Generate a 25-question MCQ assessment.

    Sends the course name to an LLM, validates the response,
    builds a .docx file, and returns a download URL.
    """
    result = generate(
        course_name=req.course_name.strip(),
        model=req.model,
        provider=req.provider,
    )

    # Schedule cleanup in background
    bg_tasks.add_task(_cleanup_old_files)

    if not result.success:
        raise HTTPException(
            status_code=500,
            detail={
                "assessment_name": result.assessment_name,
                "issues": result.issues,
                "success": False,
            },
        )

    # Build download URL
    filename = Path(result.download_path).name
    download_url = f"/download/{filename}"

    return GenerateResponse(
        assessment_name=result.assessment_name,
        download_url=download_url,
        preview=result.preview,
        issues=result.issues if result.issues else None,
        success=True,
    )


@app.get("/download/{filename:path}")
async def download_assessment(filename: str):
    """
    Download a generated .docx assessment file.
    Files are auto-deleted after {CLEANUP_HOURS} hours.
    """
    # Prevent directory traversal
    safe_name = Path(filename).name
    filepath = config.OUTPUT_DIR / safe_name

    if not filepath.exists():
        raise HTTPException(
            status_code=404,
            detail="File not found. It may have been cleaned up (files expire).",
        )

    return FileResponse(
        path=str(filepath),
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        ),
        filename=safe_name,
    )
