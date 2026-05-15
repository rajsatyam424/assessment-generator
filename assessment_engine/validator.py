"""
Validation — checks generated assessments against all quality rules.

Returns structured issues that can be surfaced to the user
without stopping generation.
"""

import re
import logging
from collections import Counter
from typing import Any

from . import config

logger = logging.getLogger(__name__)


class ValidationResult:
    """Result of validating an assessment."""

    def __init__(self, issues: list[str], stats: dict[str, Any]):
        self.issues = issues
        self.stats = stats
        self.passed = len(issues) == 0

    def __bool__(self):
        return self.passed

    def __repr__(self):
        if self.passed:
            return "<ValidationResult: passed>"
        return f"<ValidationResult: {len(self.issues)} issues>"


def validate(data: dict) -> ValidationResult:
    """
    Run all validation checks against an assessment.

    Checks:
    - Question count exactly 25
    - Answer distribution (A/B/C/D min/max)
    - Banned words
    - Em/en dashes
    - Stems starting with "Not"
    - Topic coverage (3-5 per topic)
    - Explanation word count
    - Question type mix

    Returns:
        ValidationResult with issues list and stats dict.
    """
    issues = []
    questions = data.get("questions", [])
    stats = {}

    # --- Question count ---
    if len(questions) != config.NUM_QUESTIONS:
        issues.append(
            f"Question count: {len(questions)} (need {config.NUM_QUESTIONS})"
        )

    # --- Answer distribution ---
    dist = Counter(q["answer"] for q in questions if "answer" in q)
    for letter in ["A", "B", "C", "D"]:
        count = dist.get(letter, 0)
        if count < config.ANSWER_MIN or count > config.ANSWER_MAX:
            issues.append(
                f"Answer {letter}: {count} "
                f"(need {config.ANSWER_MIN}-{config.ANSWER_MAX})"
            )
    stats["answer_dist"] = dict(dist)

    # --- Full text scan ---
    full_text = " ".join(
        str(q.get(field, ""))
        for q in questions
        for field in ["explanation", "stem", "a", "b", "c", "d"]
    ).lower()

    # Banned words
    found = [
        w for w in config.BANNED_WORDS
        if re.search(r"\b" + re.escape(w) + r"\b", full_text)
    ]
    if found:
        issues.append(f"Banned words found: {found}")

    # Dashes
    for char, name in [("\u2014", "em dash"), ("\u2013", "en dash")]:
        if char in full_text:
            issues.append(f"{name}(es) found in content")

    # Stems starting with "Not"
    for i, q in enumerate(questions):
        stem = q.get("stem", "")
        if stem.startswith("Not") and not stem.startswith("Note"):
            issues.append(f"Q{i+1} stem starts with 'Not'")

    # --- Topic coverage ---
    topics = data.get("topics", [])
    coverage = Counter(q.get("topic", "") for q in questions)
    for t in topics:
        count = coverage.get(t, 0)
        if count < config.TOPIC_MIN_QUESTIONS:
            issues.append(
                f"Topic '{t}': {count} questions (need {config.TOPIC_MIN_QUESTINGS}+)"
            )
        if count > config.TOPIC_MAX_QUESTIONS:
            issues.append(
                f"Topic '{t}': {count} questions (max {config.TOPIC_MAX_QUESTIONS})"
            )
    stats["topic_coverage"] = dict(coverage)

    # --- Explanation length ---
    short = 0
    long_ = 0
    for i, q in enumerate(questions):
        wc = len(q.get("explanation", "").split())
        if wc < config.EXPLANATION_WORD_MIN:
            short += 1
        if wc > config.EXPLANATION_WORD_MAX:
            long_ += 1
    if short:
        issues.append(f"{short} explanation(s) too short (min {config.EXPLANATION_WORD_MIN} words)")
    if long_:
        issues.append(f"{long_} explanation(s) too long (max {config.EXPLANATION_WORD_MAX} words)")

    # --- Question type mix ---
    qtypes = Counter(q.get("qtype", "concept") for q in questions)
    stats["qtypes"] = dict(qtypes)
    concept = qtypes.get("concept", 0)
    practical = qtypes.get("practical", 0)
    scenario = qtypes.get("scenario", 0)
    if concept < config.QTYPE_CONCEPT_MIN or concept > config.QTYPE_CONCEPT_MAX:
        issues.append(f"Concept questions: {concept} (need {config.QTYPE_CONCEPT_MIN}-{config.QTYPE_CONCEPT_MAX})")
    if practical < config.QTYPE_PRACTICAL_MIN or practical > config.QTYPE_PRACTICAL_MAX:
        issues.append(f"Practical questions: {practical} (need {config.QTYPE_PRACTICAL_MIN}-{config.QTYPE_PRACTICAL_MAX})")
    if scenario < config.QTYPE_SCENARIO_MIN or scenario > config.QTYPE_SCENARIO_MAX:
        issues.append(f"Scenario questions: {scenario} (need {config.QTYPE_SCENARIO_MIN}-{config.QTYPE_SCENARIO_MAX})")

    result = ValidationResult(issues, stats)
    if result.passed:
        logger.info("Validation passed — all checks ok")
    else:
        logger.warning("Validation found %d issues", len(issues))

    return result
