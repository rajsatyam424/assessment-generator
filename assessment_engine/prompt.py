"""
Prompt template for the LLM.
Loads the master JSON prompt from ~/Desktop/assessment-mcq-prompt-v2.md,
injects the course name, and appends a JSON output instruction.
"""

import json
import os

_MASTER_PROMPT_PATH = os.path.expanduser("~/Desktop/assessment-mcq-prompt-v2.md")


def build_prompt(course_name: str) -> str:
    """Load master JSON prompt, inject course name, append output format instruction."""
    path = os.environ.get("ASSESSMENT_PROMPT_PATH", _MASTER_PROMPT_PATH)
    if os.path.isfile(path):
        with open(path) as f:
            raw = f.read()
        try:
            master = json.loads(raw)
        except json.JSONDecodeError:
            master = json.loads(raw.replace("[COURSE_NAME]", course_name))
    else:
        master = _default_json_prompt(course_name)

    # Inject course name into the task field
    master["course_name"] = course_name

    prompt_str = json.dumps(master, indent=2)
    return prompt_str + _OUTPUT_INSTRUCTION


_OUTPUT_INSTRUCTION = """

## OUTPUT — STRICT JSON ONLY

Return exactly 25 questions as valid JSON. No markdown, no code fences, no extra text.

{
  "assessment_name": "string with learner level reflecting actual coverage",
  "about_assessment": ["Full domain paragraph", "What this covers paragraph"],
  "who_this_is_for": "Audience and learner level",
  "learning_outcomes": ["LO1", "LO2", "LO3", "LO4"],
  "topics": ["Topic 1", "Topic 2", "Topic 3", "Topic 4", "Topic 5"],
  "estimated_time": "30 minutes",
  "questions": [
    {
      "number": 1,
      "topic": "Topic Name",
      "qtype": "concept",
      "question": "What is the correct definition of X?",
      "A": "Option A",
      "B": "Option B",
      "C": "Option C",
      "D": "Option D",
      "answer": "B",
      "explanation": "Explanation with a fresh example."
    }
  ]
}

VERIFY BEFORE OUTPUT:
- Count A answers: exactly 6 | Count B: exactly 6 | Count C: exactly 7 | Count D: exactly 6
- concept qtype: 8-10 | practical: 8-10 | scenario: 7-9
- No dashes | No banned words | Every explanation has a fresh example
"""


def _default_json_prompt(course_name: str) -> dict:
    return {
        "task": f"Generate a 25-question multiple choice learning assessment",
        "course_name": course_name,
        "assessment_type": "learning_assessment",
        "philosophy": [
            "This is a learning assessment, not just a test.",
            "Explanations are the primary teaching component."
        ],
        "planning_sequence": [
            {"step": 1, "action": "Define 4 to 6 Learning Outcomes. Action verbs. Concrete."},
            {"step": 2, "action": "Break into 5 to 8 topics."},
            {"step": 3, "action": "Plan qtype distribution: concept 8-10, practical 8-10, scenario 7-9."},
            {"step": 4, "action": "Pre-plan answer key. Target: A=6, B=6, C=7, D=6."},
            {"step": 5, "action": "Write 25 questions with plausible distractors, same-length options, no trick questions."},
            {"step": 6, "action": "Write explanations: cover the LO, include one fresh practical example, conversational tone."}
        ],
        "style_rules": [
            "NO dashes (em, en, figure) anywhere. Use periods or commas.",
            "No sentences starting with 'Not'.",
            "Never use: navigate, embrace, journey, wisdom, vastness, shaped by, examine, deserve, rush, drive.",
            "Conversational trainer voice. Short sentences. Active voice."
        ],
        "learner_level": "beginner",
        "standards": "globally recognised",
        "audience": "general adult"
    }
