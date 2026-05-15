# Assessment Generator API

AI-powered 25-question MCQ assessment generator. Drop in a course name, get JSON with questions, answers, and explanations. No docx, no storage.

Built with FastAPI + OpenRouter.

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env   # put your OPENROUTER_API_KEY
python -m assessment_engine
```

## API

### `POST /generate`

```json
{
  "course_name": "First Aid Basics"
}
```

Response:

```json
{
  "assessment_name": "Foundations of First Aid for Beginners",
  "learning_outcomes": ["..."],
  "topics": ["..."],
  "questions": [
    {
      "number": 1,
      "topic": "[Emergency Response]",
      "qtype": "concept",
      "stem": "What is the first step in an emergency?",
      "a": "...", "b": "...", "c": "...", "d": "...",
      "answer": "B",
      "explanation": "..."
    }
  ],
  "issues": null,
  "success": true
}
```

### `GET /health`

Health check.

## Deployment

```bash
vercel --prod
```

Set `OPENROUTER_API_KEY` in Vercel env vars.

## Environment

| Variable | Default | Description |
|---|---|---|
| `OPENROUTER_API_KEY` | — | **Required.** OpenRouter API key |
| `ASSESSMENT_PROVIDER` | `openrouter` | `openai` or `openrouter` |
| `ASSESSMENT_MODEL` | `gpt-4o-mini` | Model name |
