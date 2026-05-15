"""
Prompt template for the LLM.
Generates a focused, clean prompt for 25-question JSON assessments.
"""

import os

_MASTER_PROMPT_PATH = os.path.expanduser("~/Desktop/assessment-mcq-prompt-v2.md")


def build_prompt(course_name: str) -> str:
    """Build a self-contained prompt for the LLM."""
    prompt = _BASE_PROMPT.replace("{course_name}", course_name)
    return prompt + _OUTPUT_INSTRUCTION


_BASE_PROMPT = """You are a learning assessment designer. Generate a complete 25-question multiple choice learning assessment for: {course_name}

## CONTEXT

This is a learning assessment, not just a test. Each question must test real understanding. Explanations are the primary teaching component — they must do the job of a trainer.

Learner level: Beginner. Use globally recognised standards. No jargon without explanation.

## PLANNING (do in order)

Step 1: Define 4 to 6 Learning Outcomes. Action verbs. Concrete. Testable.

Step 2: Break LOs into 5 to 8 topics.

Step 3: Plan question types. Mix across all 25:
- Concept (8 to 10): definitions, principles, recognition
- Practical (8 to 10): applied knowledge, best practices
- Scenario (7 to 9): realistic 1-2 sentence situation, ask best response

Step 4: Pre-plan answer key for Q1 to Q25. Target every letter count: A=6, B=6, C=7, D=6. No letter below 4 or above 8.

Step 5: Write each question to fit its pre-assigned answer letter and type. Use plausible distractors. All four options roughly same length. No trick questions. Self-contained stems.

## EXPLANATIONS

Every explanation must:
- Cover the LO the question tests
- Include one fresh practical example (different from the scenario in the question)
- Be conversational: direct speech, active voice, short sentences
- Be 3 to 5 sentences (50 to 80 words)
- Use proper English, complete sentences
- Sound like a trainer talking across a table, not a textbook paragraph

Style rules:
- NO dashes (em, en, figure dashes) anywhere. Use periods or commas instead.
- No sentences starting with "Not" (unless it's "Note")
- Never use these words: navigate, embrace, journey, wisdom, vastness, shaped by, examine, deserve, rush, drive
"""

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
    },
    {
      "number": 2,
      "topic": "Topic Name",
      "qtype": "practical",
      "question": "Which approach works best when doing Y?",
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
      "question": "You are in a situation where Z happens. What should you do first?",
      "A": "Option A",
      "B": "Option B",
      "C": "Option C",
      "D": "Option D",
      "answer": "A",
      "explanation": "Explanation with a fresh example."
    }
  ]
}

VERIFY BEFORE OUTPUT:
- Count A answers: must be exactly 6 across 25 questions
- Count B answers: must be exactly 6
- Count C answers: must be exactly 7
- Count D answers: must be exactly 6
- Count concept qtype: between 8 and 10
- Count practical qtype: between 8 and 10
- Count scenario qtype: between 7 and 9
- No dashes anywhere
- No banned words
- Every explanation has a fresh example
"""