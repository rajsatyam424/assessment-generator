"""
Tests for assessment_engine module.

Run: pytest tests/ -v
"""

import json
import pytest

from assessment_engine.prompt import build_prompt
from assessment_engine.parser import parse_response, ParseError
from assessment_engine.validator import validate
from assessment_engine.docx_builder import build_docx


# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------

class TestPrompt:
    def test_injects_course_name(self):
        result = build_prompt("First Aid Basics")
        assert "First Aid Basics" in result
        assert "25-question" in result

    def test_contains_key_sections(self):
        result = build_prompt("Test")
        assert "STEP 0: DOMAIN" in result
        assert "STEP 1: LEARNING OUTCOMES" in result
        assert "OUTPUT FORMAT" in result
        assert "explanation" in result.lower()


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

SAMPLE_VALID = {
    "assessment_name": "Foundations of First Aid for Beginners",
    "about_assessment": [
        "First aid covers emergency response, wound care, CPR, and more.",
        "This assessment covers emergency response basics and wound care at a beginner level.",
    ],
    "who_this_is_for": "Beginners with no prior first aid training.",
    "learning_outcomes": [
        "Recognise when emergency help is needed",
        "Apply basic wound care",
    ],
    "topics": [
        "Emergency Response", "Wound Care", "Burns",
        "Fractures", "Choking", "CPR Basics",
    ],
    "estimated_time": "30 minutes",
    "questions": [
        {
            "number": 1,
            "topic": "[Emergency Response]",
            "qtype": "concept",
            "stem": "What is the first step in an emergency?",
            "a": "Call for help",
            "b": "Check the scene",
            "c": "Start CPR",
            "d": "Apply bandages",
            "answer": "B",
            "explanation": "Checking the scene ensures you do not become a victim yourself.",
        }
        for _ in range(25)
    ],
}


class TestParser:
    def test_parses_valid_json(self):
        text = json.dumps(SAMPLE_VALID)
        result = parse_response(text)
        assert result["assessment_name"] == "Foundations of First Aid for Beginners"
        assert len(result["questions"]) == 25

    def test_parses_markdown_fenced_json(self):
        text = "```json\n" + json.dumps(SAMPLE_VALID) + "\n```"
        result = parse_response(text)
        assert len(result["questions"]) == 25

    def test_raises_on_invalid_json(self):
        with pytest.raises(ParseError):
            parse_response("not json at all")

    def test_raises_on_empty(self):
        with pytest.raises(ParseError):
            parse_response("")

    def test_raises_on_missing_keys(self):
        bad = {"assessment_name": "x", "questions": []}
        with pytest.raises(ParseError):
            parse_response(json.dumps(bad))

    def test_fills_missing_question_fields(self):
        data = dict(SAMPLE_VALID)
        data["questions"] = [{"stem": "Q", "a": "A", "b": "B", "c": "C", "d": "D", "answer": "A"}]
        result = parse_response(json.dumps(data))
        assert result["questions"][0].get("explanation") is not None


# ---------------------------------------------------------------------------
# Validator
# ---------------------------------------------------------------------------

class TestValidator:
    def test_passes_valid_assessment(self):
        result = validate(SAMPLE_VALID)
        assert result.passed is True

    def test_fails_wrong_question_count(self):
        data = dict(SAMPLE_VALID)
        data["questions"] = data["questions"][:10]
        result = validate(data)
        assert result.passed is False
        assert any("Question count" in i for i in result.issues)

    def test_fails_banned_words(self):
        data = dict(SAMPLE_VALID)
        data["questions"][0]["explanation"] = "You must navigate this situation carefully."
        result = validate(data)
        assert result.passed is False
        assert any("navigate" in i for i in result.issues)

    def test_fails_em_dash(self):
        data = dict(SAMPLE_VALID)
        data["questions"][0]["explanation"] = "It is important\u2014very important\u2014to check."
        result = validate(data)
        assert result.passed is False
        assert any("em dash" in i for i in result.issues)

    def test_fails_wrong_answer_distribution(self):
        data = dict(SAMPLE_VALID)
        for i, q in enumerate(data["questions"]):
            q["answer"] = "A"
        result = validate(data)
        assert result.passed is False
        assert any("Answer" in i for i in result.issues)

    def test_fails_stem_starts_with_not(self):
        data = dict(SAMPLE_VALID)
        data["questions"][0]["stem"] = "Not all emergencies require"
        result = validate(data)
        assert result.passed is False
        assert any("Not" in i for i in result.issues)

    def test_fails_topic_under_three(self):
        data = dict(SAMPLE_VALID)
        # Assign all questions to one topic
        for q in data["questions"]:
            q["topic"] = "[Emergency Response]"
        data["topics"] = ["Emergency Response", "Wound Care"]
        result = validate(data)
        assert result.passed is False
        assert any("Wound Care" in i for i in result.issues)


# ---------------------------------------------------------------------------
# DOCX Builder
# ---------------------------------------------------------------------------

class TestDocxBuilder:
    def test_creates_file(self):
        path = build_docx(SAMPLE_VALID)
        assert path.endswith(".docx")
        import os
        assert os.path.exists(path)
        assert os.path.getsize(path) > 0
        # Clean up
        os.unlink(path)

    def test_creates_file_with_different_name(self):
        data = dict(SAMPLE_VALID)
        data["assessment_name"] = "Custom Name Test"
        path = build_docx(data)
        import os
        assert os.path.exists(path)
        os.unlink(path)
