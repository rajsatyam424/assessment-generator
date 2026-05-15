"""
Tests for assessment_engine module.

Run: pytest tests/ -v
"""

import json
import pytest

from assessment_engine.prompt import build_prompt
from assessment_engine.parser import parse_response, ParseError
from assessment_engine.validator import validate


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

    def test_fails_answer_distribution(self):
        data = dict(SAMPLE_VALID)
        for q in data["questions"]:
            q["answer"] = "A"
        result = validate(data)
        assert result.passed is False
        assert any("Answer" in i for i in result.issues)
