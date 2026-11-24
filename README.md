# receipt-2-sql

A multimodal AI expense tracker. Send it a line of text, a photo of a receipt,
or a voice note, and it returns a structured, validated expense record and
stores it in Postgres. Built for Pakistani users: it understands English, Urdu,
and Roman Urdu, and defaults to PKR.

## What it does

Three ways in, one clean record out:

- **Text**: "kal petrol dala 3 hazaar ka" becomes a Fuel expense of 3000 PKR dated yesterday.
- **Image**: upload a receipt photo and Gemini reads the amount, vendor, date, and category.
- **Voice**: upload an audio note, Whisper transcribes it, and the same extraction runs on the text.

Every extracted record is validated against a strict schema before it reaches
the database, and anything the model is unsure about is flagged for human review.

## What makes it interesting

- **Multilingual, locale-aware prompting.** The extraction prompt handles
  code-mixed English, Urdu, and Roman Urdu (`kal`, `hazaar`, `lakh`, `rupay`)
  and resolves relative dates like `kal` and `parson` against the current date.
- **Confidence-gated human review.** The model returns a confidence score. A
  record is flagged with `needs_review = true` when confidence is below 0.70,
  the category comes back as `Other`, or no vendor could be identified.
- **Schema as a guardrail.** A Pydantic model rejects impossible data before it
  is stored, including a check that an expense date can never be in the future,
  which catches a common class of model hallucination.
- **Async end to end.** FastAPI, SQLAlchemy async, and asyncpg, so the LLM call,
  the transcription, and the database write never block the event loop.

## How it works

```
text  ----------------------------+
                                   |
image ----------------------------+---> Gemini (structured JSON output)
                                   |            |
voice --> Whisper (transcribe) ---+            v
                                        Pydantic validation
                                        (schema + future-date guard
                                         + needs_review logic)
                                               |
                                               v
                                        Postgres (async, SQLAlchemy)
```

## Tech stack

| Layer | Technology | Role |
|---|---|---|
| API | FastAPI | Async endpoints for text, image, and audio |
| LLM | Google Gemini (`gemini-3.5-flash`) via `google-genai` | Structured expense extraction (JSON mode) |
| Speech to text | OpenAI Whisper (`base`, local) | Transcribes voice notes before extraction |
| Validation | Pydantic v2 | Schema, enums, future-date guard, review flagging |
| Database | PostgreSQL + SQLAlchemy async + asyncpg | Stores validated expenses |
| Migrations | Alembic | Schema versioning |
| Alternate LLM | OpenRouter client (`httpx`) | Drop-in alternative to the Gemini client |

## Getting started

### Prerequisites

- Python 3.11+
- PostgreSQL running locally or reachable via a URL
- A Gemini API key, free at [aistudio.google.com](https://aistudio.google.com)
- `ffmpeg` installed on your system (required by Whisper for the audio endpoint)

### Install

Using `uv` (recommended, this repo ships a `uv.lock`):

```bash
git clone https://github.com/mxms-IP/receipt-2-sql.git
cd receipt-2-sql
uv sync
```

Or with pip:

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e .
```

### Configure

```bash
cp .env.example .env
```

Set `GEMINI_API_KEY` and `DATABASE_URL` in `.env`. The database URL must use the
async driver, for example:

```
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/expenses
```

### Create the database schema

```bash
alembic upgrade head
```

### Run

```bash
uvicorn main:app --reload
```

Interactive API docs at `http://localhost:8000/docs`.

## API

All extraction routes are under `/expenses`.

### `POST /expenses/extract_from_text`

```bash
curl -X POST http://localhost:8000/expenses/extract_from_text \
  -H "Content-Type: application/json" \
  -d '{"raw_text": "spent 450 on lunch at Student Biryani"}'
```

Response:
```json
{
  "id": "4f1e...",
  "amount": 450.00,
  "currency": "PKR",
  "category": "Food & Dining",
  "vendor": "Student Biryani",
  "date": "2026-11-19",
  "needs_review": false,
  "created_at": "2026-11-19T10:12:00Z"
}
```

### `POST /expenses/extract_from_image`

```bash
curl -X POST http://localhost:8000/expenses/extract_from_image \
  -F "file=@receipt.jpg"
```

### `POST /expenses/extract_from_audio`

```bash
curl -X POST http://localhost:8000/expenses/extract_from_audio \
  -F "file=@expense_note.mp3"
```

Images and audio are capped at 5 MB.

## Project structure

```
app/
├── api/routes/expense_api.py   # the three extraction endpoints
├── core/
│   ├── config.py               # settings loaded from .env
│   └── database.py             # async engine, session, ExpenseDB table
├── models/
│   ├── expense.py              # domain model: categories, currency, validation
│   ├── requests.py             # request schemas
│   └── response.py             # API response schema
├── repositories/ExpenseRepo.py # persistence layer
├── services/
│   ├── llm/gemini.py           # Gemini extraction client (default)
│   ├── llm/openrouter.py       # alternate OpenRouter client
│   ├── llm/prompts.py          # the multilingual extraction prompt
│   └── audio/whisper.py        # voice-note transcription
alembic/                        # database migrations
main.py                         # FastAPI app entry point
```

## Notes and roadmap

- The default LLM client is Gemini. `services/llm/openrouter.py` is a complete
  alternate client with the same interface; swap it in where the router
  instantiates the client.
- `SECONDARY_MODEL` and `FALLBACK_MODEL` are reserved for a planned automatic
  fallback chain and are not wired in yet.
- The Whisper `base` model runs locally on CPU, so the first audio request is
  slow while the model loads.

Retry with error hints: On a schema or format failure, feed the exact validation error back into a retry prompt (with low temperature, such as 0) to repair the output.

## Author

**Rabia L.** ([mxms-IP](https://github.com/mxms-IP))