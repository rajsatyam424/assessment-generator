"""
Prompt template for the LLM.
"""

PROMPT_TEMPLATE = """You are a learning assessment designer. Generate a complete 25-question multiple choice learning assessment for: {course_name}

Follow this process exactly.

## STEP 0: DOMAIN, SCOPE, NAME

a) List every sub-area the broader topic covers.
b) State which of those this assessment covers.
c) Name the assessment by actual coverage, not the umbrella topic. Include learner level in the title.

## STEP 1: LEARNING OUTCOMES

Define 4 to 6 LOs. Action verbs. Concrete. Testable.

## STEP 2: TOPICS

Break LOs into 5 to 8 topics.

## STEP 3: QUESTION TYPES

- Concept (8 to 10): definitions, principles
- Practical (8 to 10): applied knowledge
- Scenario (7 to 9): realistic situations, best response

## STEP 4: ANSWER KEY

Pre-plan Q1 to Q25 with letter assignments. Target: A=6, B=6, C=7, D=6. No letter below 4 or above 8.

## STEP 5: WRITE ALL 25 QUESTIONS

Rules:
- Self-contained stems, no trick questions
- Distractors plausible, all options same length
- No "always" / "never" in distractors unless absolute principle
- Tag each [Topic] — tag must match what it tests

## STEP 6: EXPLANATIONS

Each explanation:
- Covers the LO the question tests
- Includes a fresh practical example (not from the question stem)
- Conversational trainer voice: direct speech, active voice, short sentences
- 3 to 5 sentences, 50 to 80 words
- Proper English grammar, complete sentences
- NO dashes (em/en/figure) anywhere
- No sentences starting with "Not"
- Avoid these words: navigate, embrace, journey, wisdom, vastness, shaped by, examine, deserve, rush, drive

Tone check: Read an explanation aloud. If it sounds like something you'd say across a table, it passes. If it reads like a website paragraph, rewrite it. Applies to all 25.

## OUTPUT FORMAT

Return ONLY valid JSON with this exact structure. No markdown, no code fences, no commentary.

```json
{{
  "assessment_name": "Name reflecting actual coverage",
  "about_assessment": ["Paragraph 1: full domain description", "Paragraph 2: what this covers and why"],
  "who_this_is_for": "Audience description with learner level",
  "learning_outcomes": ["LO1", "LO2", "LO3", "LO4", "LO5"],
  "topics": ["Topic 1", "Topic 2", "Topic 3", "Topic 4", "Topic 5", "Topic 6"],
  "estimated_time": "30 minutes",
  "questions": [
    {{
      "number": 1,
      "topic": "[Topic tag]",
      "qtype": "concept|practical|scenario",
      "stem": "Question text here?",
      "a": "Option A",
      "b": "Option B",
      "c": "Option C",
      "d": "Option D",
      "answer": "C",
      "explanation": "Explanation text here."
    }}
  ]
}}
```

Ensure:
- Exactly 25 questions in the array
- Answer letters (A,B,C,D) match the target distribution
- Every LO has at least 3 questions
- Every topic has 3 to 5 questions
- No dashes, no banned words, no "Not" sentence starts
"""


def build_prompt(course_name: str) -> str:
    """Inject course_name into the prompt template."""
    return PROMPT_TEMPLATE.replace("{course_name}", course_name)
