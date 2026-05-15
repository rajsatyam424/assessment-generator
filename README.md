# Assessment Generator API

AI-powered 25-question MCQ assessment generator. Drop in a course name, get a formatted `.docx` with questions, answers, and teaching explanations.

Built with FastAPI + OpenAI-compatible LLMs.

## Quick Start

```bash
# 1. Clone and install
cd assessment-generator
pip install -r requirements.txt

# 2. Set your API key
cp .env.example .env
# Edit .env — set OPENAI_API_KEY

# 3. Run
python -m assessment_engine
```

Open **http://localhost:8000/docs** — Swagger UI is ready.

## API

### `POST /generate`

Generate a 25-question assessment.

```json
{
  "course_name": "First Aid Basics"
}
```

Response:

```json
{
  "assessment_name": "Foundations of First Aid for Beginners",
  "download_url": "/download/Foundations_of_First_Aid_a1b2.docx",
  "preview": {
    "learning_outcomes": ["..."],
    "topics": ["..."],
    "question_count": 25,
    "answer_distribution": {"A": 6, "B": 6, "C": 7, "D": 6}
  },
  "issues": null,
  "success": true
}
```

### `GET /download/{filename}`

Download the generated `.docx` file.

### `GET /health`

Health check.

## Deployment

### Docker

```bash
cp .env.example .env   # set OPENAI_API_KEY
docker compose up -d
```

### Production

- Set `ASSESSMENT_OUTPUT_DIR` to a persistent volume
- Set `ASSESSMENT_CLEANUP_HOURS` (default 24)
- Use `gunicorn -k uvicorn.workers.UvicornWorker` for multi-worker

### Environment Variables

| Variable | Default | Description |
|---|---|---|
| `OPENROUTER_API_KEY` | — | **Required.** OpenRouter API key (or `OPENAI_API_KEY` for direct OpenAI) |
| `ASSESSMENT_PROVIDER` | `openrouter` | `openai` or `openrouter` |
| `ASSESSMENT_MODEL` | `gpt-4o-mini` | LLM model name (e.g. `anthropic/claude-sonnet-4` on OpenRouter) |
| `ASSESSMENT_OUTPUT_DIR` | `/tmp/assessments` | Where `.docx` files are saved |
| `ASSESSMENT_CLEANUP_HOURS` | `24` | Auto-delete files after N hours |
| `HOST` | `0.0.0.0` | Bind address |
| `PORT` | `8000` | Port |

## How It Works

```
Course name
    → Prompt builder (embeds all rules from the assessment skill)
    → LLM (OpenAI / OpenRouter)
    → Parser (extracts structured JSON)
    → Validator (25 checks: answer distribution, banned words, topic coverage, etc.)
    → DOCX builder (formatted Word document with Calibri, 1-inch margins)
    → Download URL
```

The prompt embedded in the engine contains the full assessment design skill:

- Domain enumeration + scope narrowing + accurate naming (Step 0)
- Learning outcomes drive everything
- Pre-planned answer key (A=6, B=6, C=7, D=6)
- Concept / Practical / Scenario mix (8-10 / 8-10 / 7-9)
- Every explanation has a fresh practical example
- Conversational trainer tone, no textbook language
- No em dashes, no banned words, no "Not" sentence starts

## Project Structure

```
assessment-generator/
├── assessment_engine/
│   ├── __init__.py
│   ├── __main__.py          # CLI entry: python -m assessment_engine
│   ├── api.py               # FastAPI app
│   ├── config.py            # Settings from env vars
│   ├── docx_builder.py      # .docx file generator
│   ├── llm.py               # OpenAI / OpenRouter client
│   ├── orchestrator.py      # Full pipeline runner
│   ├── parser.py            # JSON response parser
│   ├── prompt.py            # Prompt template builder
│   └── validator.py         # Quality checks
├── tests/
│   ├── test_engine.py       # Unit tests
│   └── test_api.py          # API integration tests
├── docs/
├── Dockerfile
├── docker-compose.yml
├── config.yaml
├── .env.example
├── requirements.txt
├── pyproject.toml
├── pytest.ini
├── .gitignore
└── README.md
```

## Tests

```bash
pip install -e ".[dev]"
pytest tests/ -v
```
