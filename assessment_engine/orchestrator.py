"""
Orchestrator — ties prompt, LLM, parser, and validator together.
Returns JSON data directly (no docx).
"""

import logging
from typing import Optional, Any

from .prompt import build_prompt
from .llm import call_llm
from .parser import parse_response, ParseError
from .validator import validate

logger = logging.getLogger(__name__)


class AssessmentResult:
    def __init__(
        self,
        assessment_name: str,
        data: dict[str, Any],
        preview: dict,
        issues: list[str],
        success: bool,
    ):
        self.assessment_name = assessment_name
        self.data = data
        self.preview = preview
        self.issues = issues
        self.success = success


def generate(
    course_name: str,
    model: Optional[str] = None,
    provider: Optional[str] = None,
    api_key: Optional[str] = None,
) -> AssessmentResult:
    logger.info("Starting generation for: %s", course_name)

    prompt = build_prompt(course_name)

    try:
        raw = call_llm(prompt, model=model, provider=provider, api_key=api_key)
    except Exception as e:
        logger.exception("LLM call failed")
        return AssessmentResult(course_name, {}, {}, [f"LLM call failed: {e}"], False)

    try:
        data = parse_response(raw)
    except ParseError as e:
        logger.exception("Parsing failed")
        return AssessmentResult(course_name, {}, {}, [f"Parsing failed: {e}"], False)

    valid = validate(data)

    logger.info(
        "Generation complete: name=%s issues=%d",
        data.get("assessment_name"), len(valid.issues),
    )

    return AssessmentResult(
        assessment_name=data.get("assessment_name", course_name),
        data=data,
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
