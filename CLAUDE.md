# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Career Advisor is an AI-powered web app that analyses the gap between a candidate's resume and a target job description. It returns a fit score, gap analysis, and a 90-day action plan.

**Stack:** Next.js 14 (TypeScript + Tailwind) · FastAPI (Python 3.11+) · Supabase (Postgres + Storage) · OpenRouter (Claude Sonnet via OpenAI-compatible API)

---

## Running the App

**Backend** (port 8000):
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

**Frontend** (port 3000):
```bash
cd frontend
npm run dev
```

**API docs:** http://localhost:8000/api/v1/docs

---

## Development Commands

```bash
# Backend tests
cd backend && source venv/bin/activate
pytest -v --cov=app

# Single test file
pytest tests/test_main.py -v

# Code quality
black .
flake8 .
mypy .

# Frontend type check
cd frontend && npx tsc --noEmit

# Frontend lint
cd frontend && npm run lint
```

---

## Required Environment Variables

Copy `backend/.env.example` → `backend/.env` and fill in:

| Variable | Purpose |
|---|---|
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_KEY` | Anon/public key (browser-side) |
| `SUPABASE_SERVICE_KEY` | Service role key — used by the backend to bypass RLS |
| `SUPABASE_JWT_SECRET` | JWT secret for token verification |
| `OPENROUTER_API_KEY` | OpenRouter API key |
| `OPENROUTER_MODEL` | Model ID (default: `anthropic/claude-sonnet-4-5`) |
| `CORS_ORIGINS` | JSON array e.g. `["http://localhost:3000"]` — must be valid JSON, not comma-separated |

The backend uses the **service role key** (not the anon key) for all Supabase operations because it runs server-side and needs to bypass row-level security.

---

## Architecture & Data Flow

### User Flow
```
/upload → POST /api/v1/upload/ → session_id, resume_id, jd_id (stored in sessionStorage)
       → POST /api/v1/questions/ → 0–3 clarifying questions
       → POST /api/v1/analyze/ → report_id
       → GET /api/v1/report/{report_id} → full report
```

### Backend Layer Structure
```
main.py                        FastAPI app, CORS, global exception handler
app/core/config.py             All settings via Pydantic BaseSettings
app/core/supabase_client.py    Singleton Supabase client (uses service key)
app/api/v1/endpoints/          One file per route group (upload, questions, analyze, report)
app/services/upload_service.py File validation, Supabase Storage upload, DB insert
app/services/session_service.py Guest/auth session creation and validation
app/services/parsing/          resume_parser.py and jd_parser.py — extract raw_text from PDF/DOCX/URL
app/services/ai/analyzer.py    OpenRouter calls — generate_questions() and analyze()
app/schemas/                   Pydantic request/response models
```

### Frontend Pages
```
app/page.tsx              Landing page
app/upload/page.tsx       Drag-and-drop resume + JD input (text/file/URL tabs)
app/questions/page.tsx    Displays clarifying questions, submits answers, triggers analysis
app/report/[id]/page.tsx  Renders full report (score, category breakdown, gaps, strengths, action plan)
```

### Database Tables (Supabase)
- **sessions** — guest (24h) or authenticated (7d), `expires_at` set by DB trigger
- **resumes** — `file_path` in Storage + `parsed_data.raw_text` extracted at upload time
- **job_descriptions** — `source_type` (text|file|url), `source_content`, `parsed_data.raw_text`
- **reports** — `overall_score`, `category_scores` (JSON), `gaps`, `strengths`, `action_plan`

The `category_scores` column is validated by a DB trigger requiring exactly 5 keys: `software_technical`, `domain_knowledge`, `experience_seniority`, `credentials_education`, `soft_skills_leadership` — each with `score`, `weight`, `reasoning`.

---

## AI Analysis Design

`app/services/ai/analyzer.py` makes two types of OpenRouter calls:

**`generate_questions(resume_text, jd_text)`** — returns 0–3 clarifying questions as a JSON array. Returns `[]` on any failure (non-fatal).

**`analyze(resume_text, jd_text, answers?)`** — returns a full analysis JSON. The prompt enforces a rigid schema with hardcoded category weights:
- Technical skills: 35%
- Domain knowledge: 25%
- Experience/seniority: 20%
- Credentials/education: 10%
- Soft skills/leadership: 10%

Text is truncated before sending: resume to 6000 chars, JD to 3000 chars.

The response is extracted with a regex `{.*}` (DOTALL) to handle any markdown wrapping before JSON parsing.

---

## Key Implementation Notes

- **Parsing happens at upload time** — `upload_service.py` parses files immediately after upload and stores `parsed_data.raw_text` in the DB. The analyze endpoint reads from DB, not from storage.
- **CORS_ORIGINS must be a JSON array** in `.env` — pydantic-settings v2 parses list fields as JSON. Use `["http://localhost:3000"]` not `http://localhost:3000`.
- **Supabase migrations** live in `backend/supabase/migrations/`. Run them in order (001→004) via the Supabase SQL Editor or `supabase db push`. Migration 003 (storage policies) must be applied via the Supabase Dashboard UI — the SQL Editor lacks permission to create policies on `storage.objects`.
- **Session expiry** is set by a DB trigger in migration 004 (`set_session_expiry`), not in application code — the service layer sets it redundantly as a fallback.
- **Global exception handler** in `main.py` catches unhandled exceptions and returns JSON so CORS headers are preserved on errors. All endpoint-level errors use `HTTPException` to ensure CORS middleware processes them.

---

## What's Not Yet Built

- User authentication (Supabase Auth — Task 16)
- Report dashboard per user (Task 17)
- Report sharing via public link (Task 18)
- PDF export (Task 13)
- Rate limiting, caching, background cleanup job
