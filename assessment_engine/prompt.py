"""
Prompt template for the LLM.
Loads the master prompt from ~/Desktop/assessment-mcq-prompt-v2.md
and appends a strict JSON output instruction for API use.
"""

import os


_MASTER_PROMPT_PATH = os.path.expanduser("~/Desktop/assessment-mcq-prompt-v2.md")


def _load_master_prompt() -> str:
    """Load the full master prompt from Desktop."""
    path = os.environ.get("ASSESSMENT_PROMPT_PATH", _MASTER_PROMPT_PATH)
    if os.path.isfile(path):
        with open(path) as f:
            return f.read()
    # Fallback: use a hardcoded minimal version
    # This should never happen in production — the prompt file is committed.
    return _FALLBACK_PROMPT


_OUTPUT_INSTRUCTION = """

## FINAL INSTRUCTION — STRICT JSON OUTPUT

Return ONLY valid JSON. No markdown, no code fences, no commentary, no extra text.

JSON structure (exactly this):

{
  "assessment_name": "string — reflecting actual coverage, include learner level",
  "about_assessment": ["Paragraph 1 describing full domain", "Paragraph 2: what this covers and why"],
  "who_this_is_for": "string — audience and learner level",
  "learning_outcomes": ["string", "string", ...],
  "topics": ["string", "string", ...],
  "estimated_time": "string",
  "questions": [
    {
      "number": 1,
      "topic": "[Topic tag]",
      "question": "Question stem text",
      "A": "Option A",
      "B": "Option B",
      "C": "Option C",
      "D": "Option D",
      "answer": "A",
      "explanation": "Explanation text with fresh example"
    }
  ]
}

Rules:
- Exactly 25 questions in the questions array
- answer field is a single letter A/B/C/D matching the correct option
- Every question has all 4 options (A, B, C, D)
- distribution target: A=6, B=6, C=7, D=6
- No dashes (em/en/figure) anywhere in the entire output
- No banned words: navigate, embrace, journey, wisdom, vastness, shaped by, examine, deserve, rush, drive
- Proper English grammar throughout
- Valid JSON only — parseable by json.loads()
"""


def build_prompt(course_name: str) -> str:
    """Inject course_name into the master prompt and append JSON output instruction."""
    master = _load_master_prompt()
    prompt = master.replace("[COURSE NAME]", course_name).replace("[COURSE_NAME]", course_name)
    return prompt + _OUTPUT_INSTRUCTION


_FALLBACK_PROMPT = """You are a learning assessment designer. Generate a complete 25-question multiple choice learning assessment for the course named {course_name}.

This is a learning assessment, not just a test. Each question must test a real concept and each explanation must teach the learner.

Create 5 to 8 topics from the course name. Distribute 25 questions across topics (3 to 5 each). Mix concept, practical, and scenario questions. Pre-plan answer distribution: A=6, B=6, C=7, D=6.

Each explanation must be conversational, include a fresh practical example, and cover the learning outcome it tests. No dashes, no banned words, no sentences starting with "Not".
"""
