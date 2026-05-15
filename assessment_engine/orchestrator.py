"""
Orchestrator — ties prompt, LLM, parser, validator, and docx builder together.
"""

import logging
from typing import Optional

from . import config
from .prompt import build_prompt
from .llm import call_llm
from .parser import parse_response, ParseError
from .validator import validate
from .docx_builder import build_docx

logger = logging.getLogger(__name__)


class AssessmentResult:
    """Result of a full assessment generation run."""

    def __init__(
        self,
        assessment_name: str,
        download_path: str,
        preview: dict,
        issues: list[str],
        success: bool,
    ):
        self.assessment_name = assessment_name
        self.download_path = download_path
        self.preview = preview
        self.issues = issues
        self.success = success

    def to_dict(self) -> dict:
        return {
            "assessment_name": self.assessment_name,
            "download_path": self.download_path,
            "preview": self.preview,
            "issues": self.issues or None,
            "success": self.success,
        }


def generate(
    course_name: str,
    model: Optional[str] = None,
    provider: Optional[str] = None,
    api_key: Optional[str] = None,
) -> AssessmentResult:
    """
    Full generation pipeline.

    1. Build prompt from course name
    2. Call LLM
    3. Parse response
    4. Validate
    5. Build .docx
    6. Return result

    Args:
        course_name: The course/topic name.
        model: LLM model override.
        provider: LLM provider override.
        api_key: API key override.

    Returns:
        AssessmentResult with download path, preview, and any issues.
    """
    logger.info("Starting generation for: %s", course_name)

    # 1. Prompt
    prompt = build_prompt(course_name)

    # 2. LLM
    try:
        raw = call_llm(prompt, model=model, provider=provider, api_key=api_key)
    except Exception as e:
        logger.exception("LLM call failed")
        return AssessmentResult(
            assessment_name=course_name,
            download_path="",
            preview={},
            issues=[f"LLM call failed: {e}"],
            success=False,
        )

    # 3. Parse
    try:
        data = parse_response(raw)
    except ParseError as e:
        logger.exception("Parsing failed")
        return AssessmentResult(
            assessment_name=course_name,
            download_path="",
            preview={},
            issues=[f"Parsing failed: {e}"],
            success=False,
        )

    # 4. Validate
    valid = validate(data)

    # 5. Build docx
    try:
        output_path = build_docx(data)
    except Exception as e:
        logger.exception("DOCX build failed")
        return AssessmentResult(
            assessment_name=data.get("assessment_name", course_name),
            download_path="",
            preview={},
            issues=[f"DOCX build failed: {e}"],
            success=False,
        )

    logger.info(
        "Generation complete: name=%s path=%s issues=%d",
        data.get("assessment_name"), output_path, len(valid.issues),
    )

    return AssessmentResult(
        assessment_name=data.get("assessment_name", course_name),
        download_path=output_path,
        preview={
            "assessment_name": data.get("assessment_name"),
            "learning_outcomes": data.get("learning_outcomes", []),
            "topics": data.get("topics", []),
            "question_count": len(data.get("questions", [])),
            "answer_distribution": valid.stats.get("answer_dist"),
            "question_types": valid.stats.get("qtypes"),
        },
        issues=valid.issues,
        success=True,
    )
