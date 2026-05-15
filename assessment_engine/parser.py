"""
Parser — extracts structured assessment data from LLM JSON responses.
"""

import json
import re
import logging
from typing import Any

logger = logging.getLogger(__name__)


class ParseError(ValueError):
    """Raised when LLM output cannot be parsed as valid assessment data."""
    pass


def parse_response(text: str) -> dict[str, Any]:
    """
    Parse LLM response text into a structured assessment dict.

    Handles:
    - Raw JSON
    - JSON wrapped in markdown code fences (```json ... ```)
    - JSON with leading/trailing whitespace or stray characters

    Returns:
        dict with keys: assessment_name, about_assessment, who_this_is_for,
        learning_outcomes, topics, estimated_time, questions

    Raises:
        ParseError: If the response cannot be parsed as valid JSON.
    """
    text = text.strip()

    # Strip markdown code fences
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    text = text.strip()

    if not text:
        raise ParseError("Empty response from LLM")

    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        logger.error("Failed to parse LLM response: %s", e)
        logger.debug("Raw response (first 500 chars): %s", text[:500])
        raise ParseError(f"Invalid JSON from LLM: {e}") from e

    # Validate top-level structure
    required_keys = [
        "assessment_name", "about_assessment", "who_this_is_for",
        "learning_outcomes", "topics", "questions",
    ]
    missing = [k for k in required_keys if k not in data]
    if missing:
        raise ParseError(f"Missing required keys: {missing}")

    # Ensure questions is a list
    if not isinstance(data.get("questions"), list):
        raise ParseError("'questions' must be a list")

    # Normalize: ensure all questions have required fields
    for i, q in enumerate(data["questions"]):
        q.setdefault("number", i + 1)
        for field in ["stem", "a", "b", "c", "d", "answer", "explanation", "topic", "qtype"]:
            if field not in q:
                logger.warning("Question %d missing field '%s' — filling with placeholder", i + 1, field)
                q[field] = f"[missing {field}]"

    logger.info(
        "Parsed assessment '%s' with %d questions",
        data.get("assessment_name", "untitled"),
        len(data["questions"]),
    )
    return data
