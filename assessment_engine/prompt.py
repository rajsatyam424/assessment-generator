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

IMPORTANT RULES — FOLLOW THESE EXACTLY:
- Exactly 25 questions in the questions array
- answer field is a single letter A/B/C/D matching the correct option
- Every question has all 4 options (A, B, C, D)
- Answer distribution MUST be: A=6, B=6, C=7, D=6 (you plan this before writing questions)
- Question type distribution: concept 8-10, practical 8-10, scenario 7-9
- Every question MUST have a "qtype" field set to exactly "concept", "practical", or "scenario"
- No dashes (em/en/figure) anywhere in the entire output
- No banned words: navigate, embrace, journey, wisdom, vastness, shaped by, examine, deserve, rush, drive
- Proper English grammar throughout
- Valid JSON only — parseable by json.loads()

JSON structure (exactly this format):

{
  "assessment_name": "string with learner level",
  "about_assessment": ["Paragraph 1", "Paragraph 2"],
  "who_this_is_for": "string",
  "learning_outcomes": ["LO1", "LO2", "LO3", "LO4"],
  "topics": ["Topic 1", "Topic 2", "Topic 3", "Topic 4", "Topic 5"],
  "estimated_time": "30 minutes",
  "questions": [
    {
      "number": 1,
      "topic": "Topic Name",
      "qtype": "concept",
      "question": "What is...?",
      "A": "Option A",
      "B": "Option B",
      "C": "Option C",
      "D": "Option D",
      "answer": "B",
      "explanation": "Explanation with a fresh example."
    },
    {
      "number": 2,
      "topic": "Topic Name",
      "qtype": "practical",
      "question": "Which is the best way to...?",
      "A": "Option A",
      "B": "Option B",
      "C": "Option C",
      "D": "Option D",
      "answer": "C",
      "explanation": "Explanation with a fresh example."
    },
    {
      "number": 3,
      "topic": "Topic Name",
      "qtype": "scenario",
      "question": "You are in a situation where... What should you do?",
      "A": "Option A",
      "B": "Option B",
      "C": "Option C",
      "D": "Option D",
      "answer": "A",
      "explanation": "Explanation with a fresh example."
    }
  ]
}

Pre-plan your answer key across all 25 before writing: count A, B, C, D and make sure they hit the target distribution exactly. Mix qtype values across the 25 questions — do not set all to the same type.
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
