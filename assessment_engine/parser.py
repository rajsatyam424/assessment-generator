"""
Parser — extracts structured assessment data from LLM JSON responses.
Normalizes field naming (accepts stem/question, a/A, b/B, etc.)
"""

import json
import re
import logging
from typing import Any

logger = logging.getLogger(__name__)


class ParseError(ValueError):
    """Raised when LLM output cannot be parsed as valid assessment data."""
    pass


_FIELD_MAP = {
    "stem": "stem",
    "question": "stem",
    "a": "a", "A": "a",
    "b": "b", "B": "b",
    "c": "c", "C": "c",
    "d": "d", "D": "d",
}


def _normalize_question(q: dict, idx: int) -> dict:
    """Normalize a question dict to canonical field names (stem, a, b, c, d, answer, explanation, topic, qtype)."""
    out = {}
    out["number"] = q.get("number", idx + 1)

    # Map stem/question
    out["stem"] = q.get("stem") or q.get("question") or f"[missing stem for Q{idx+1}]"

    # Map option fields
    for canonical, variants in [("a", ["a", "A"]), ("b", ["b", "B"]), ("c", ["c", "C"]), ("d", ["d", "D"])]:
        val = None
        for v in variants:
            val = q.get(v)
            if val:
                break
        out[canonical] = val or f"[missing option {canonical.upper()}]"

    out["answer"] = q.get("answer", "A")
    out["explanation"] = q.get("explanation", "")
    out["topic"] = q.get("topic", q.get("[Topic]", ""))
    out["qtype"] = q.get("qtype", "concept")

    # Strip [Topic] prefix from stem if LLM put it there, and use it as topic
    stem = out["stem"]
    topic_match = re.match(r'^\[([^\]]+)\]\s*', stem)
    if topic_match:
        extracted_topic = topic_match.group(1)
        if not out["topic"] or out["topic"].startswith("[missing"):
            out["topic"] = extracted_topic
        # Remove the [Topic] prefix from stem for clean display
        out["stem"] = stem[topic_match.end():].strip()

    return out


def parse_response(text: str) -> dict[str, Any]:
    """
    Parse LLM response text into a structured assessment dict.

    Handles:
    - Raw JSON
    - JSON wrapped in markdown code fences (```json ... ```)
    - JSON with leading/trailing whitespace or stray characters
    - Both stem/question and a/A/b/B/c/C/d/D field naming

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

    # Normalize questions to canonical field names
    data["questions"] = [_normalize_question(q, i) for i, q in enumerate(data["questions"])]

    logger.info(
        "Parsed assessment '%s' with %d questions",
        data.get("assessment_name", "untitled"),
        len(data["questions"]),
    )
    return data
