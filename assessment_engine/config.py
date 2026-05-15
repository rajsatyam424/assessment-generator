"""
Configuration for the assessment generator.
All settings are env-var driven with sensible defaults.
"""

import os
from pathlib import Path


def _env_str(key: str, default: str) -> str:
    return os.environ.get(key, default)


def _env_int(key: str, default: int) -> int:
    try:
        return int(os.environ.get(key, str(default)))
    except (TypeError, ValueError):
        return default


# LLM
PROVIDER = _env_str("ASSESSMENT_PROVIDER", "openai")
MODEL = _env_str("ASSESSMENT_MODEL", "gpt-4o-mini")
API_KEY = os.environ.get("OPENAI_API_KEY", "")

# Output
OUTPUT_DIR = Path(_env_str("ASSESSMENT_OUTPUT_DIR", "/tmp/assessments"))
CLEANUP_HOURS = _env_int("ASSESSMENT_CLEANUP_HOURS", 24)

# Document
FONT_NAME = _env_str("ASSESSMENT_FONT", "Calibri")
FONT_SIZE = _env_int("ASSESSMENT_FONT_SIZE", 11)
MARGIN_INCHES = _env_int("ASSESSMENT_MARGIN", 1)

# Assessment rules
NUM_QUESTIONS = 25
ANSWER_TARGETS = {"A": 6, "B": 6, "C": 7, "D": 6}
ANSWER_MIN = 4
ANSWER_MAX = 8
QTYPE_CONCEPT_MIN = 8
QTYPE_CONCEPT_MAX = 10
QTYPE_PRACTICAL_MIN = 8
QTYPE_PRACTICAL_MAX = 10
QTYPE_SCENARIO_MIN = 7
QTYPE_SCENARIO_MAX = 9
EXPLANATION_WORD_MIN = 20
EXPLANATION_WORD_MAX = 120
TOPIC_MIN_QUESTIONS = 3
TOPIC_MAX_QUESTIONS = 5
LO_MIN_QUESTIONS = 3

# Style
BANNED_WORDS = [
    "navigate", "embrace", "journey", "wisdom", "vastness",
    "shaped by", "examine", "deserve", "rush", "drive",
]
