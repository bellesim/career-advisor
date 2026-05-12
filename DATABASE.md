# Database Architecture

Career Advisor uses **Supabase** (managed PostgreSQL) for all persistent storage. This document covers the schema, relationships, access control, storage, and automated behaviour.

---

## Entity Relationship Overview

```
users (optional — authenticated only)
  └── sessions (guest or authenticated)
        ├── resumes
        ├── job_descriptions
        └── reports ──── resumes
                    └─── job_descriptions
```

Every piece of data is anchored to a **session**. Sessions may or may not belong to a user (guests get anonymous sessions). Deleting a session cascades and removes all its resumes, job descriptions, and reports automatically.

---

## Tables

### `users`
Stores registered accounts. Not used for guest users.

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | Primary key, auto-generated |
| `email` | TEXT | Unique, validated by regex constraint |
| `password_hash` | TEXT | Hashed by Supabase Auth (bcrypt) |
| `created_at` | TIMESTAMPTZ | Auto-set to now |
| `oauth_provider` | TEXT | e.g. `google`, `github` — null if email/password |
| `oauth_id` | TEXT | Provider's user ID — null if email/password |

---

### `sessions`
Tracks both guest sessions (anonymous, 24h) and authenticated sessions (7 days).

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | Primary key, auto-generated |
| `user_id` | UUID | FK → `users.id`, null for guest sessions |
| `is_guest` | BOOLEAN | `true` = guest (24h), `false` = authenticated (7d) |
| `expires_at` | TIMESTAMPTZ | **Set automatically by DB trigger** — do not set manually |
| `created_at` | TIMESTAMPTZ | Auto-set to now |

> **Important:** `expires_at` is controlled by the `trigger_set_session_expiry` trigger (migration 004). You do not need to set it in application code — the DB calculates it from `is_guest` and `created_at`.

---

### `resumes`
One record per uploaded resume file.

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | Primary key, auto-generated |
| `session_id` | UUID | FK → `sessions.id` (CASCADE delete) |
| `file_path` | TEXT | Path in Supabase Storage `resumes` bucket: `{session_id}/resume_{uuid}.{ext}` |
| `uploaded_at` | TIMESTAMPTZ | Auto-set to now |
| `parsed_data` | JSONB | `{"raw_text": "..."}` — extracted at upload time by `resume_parser.py` |

---

### `job_descriptions`
One record per job description, regardless of how it was provided.

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | Primary key, auto-generated |
| `session_id` | UUID | FK → `sessions.id` (CASCADE delete) |
| `source_type` | TEXT | Constrained to `text`, `file`, or `url` |
| `source_content` | TEXT | The original input: plain text, storage path, or URL |
| `parsed_data` | JSONB | `{"raw_text": "..."}` — extracted at upload time |
| `created_at` | TIMESTAMPTZ | Auto-set to now |

---

### `reports`
The full AI-generated analysis result.

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | Primary key, auto-generated |
| `session_id` | UUID | FK → `sessions.id` (CASCADE delete) |
| `user_id` | UUID | FK → `users.id` — null for guest reports |
| `resume_id` | UUID | FK → `resumes.id` (CASCADE delete) |
| `jd_id` | UUID | FK → `job_descriptions.id` (CASCADE delete) |
| `created_at` | TIMESTAMPTZ | Auto-set to now |
| `candidate_name` | TEXT | Extracted from resume by Claude |
| `target_role` | TEXT | Extracted from JD by Claude |
| `overall_score` | INTEGER | 0–100, weighted sum of category scores |
| `category_scores` | JSONB | See structure below — validated by DB trigger |
| `gaps` | JSONB | Array of gap objects |
| `strengths` | JSONB | Array of strength objects |
| `action_plan` | JSONB | 3-sprint 90-day plan |
| `is_shared` | BOOLEAN | Whether public sharing is enabled |
| `share_token` | UUID | Unique token for public link — managed by DB trigger |
| `view_count` | INTEGER | Number of public views |

#### `category_scores` structure
Every report **must** include all 5 categories or the DB trigger will reject the insert:

```json
{
  "software_technical":     { "score": 80, "weight": 0.35, "reasoning": "..." },
  "domain_knowledge":       { "score": 70, "weight": 0.25, "reasoning": "..." },
  "experience_seniority":   { "score": 75, "weight": 0.20, "reasoning": "..." },
  "credentials_education":  { "score": 65, "weight": 0.10, "reasoning": "..." },
  "soft_skills_leadership": { "score": 80, "weight": 0.10, "reasoning": "..." }
}
```

#### `gaps` structure
```json
[
  {
    "severity": "Critical | Moderate | Nice-to-have",
    "area": "Python",
    "description": "Candidate lacks production Python experience",
    "suggestions": ["Complete Python for Data Science course"]
  }
]
```

#### `strengths` structure
```json
[
  {
    "area": "Communication",
    "description": "Strong written communication demonstrated through blog posts",
    "examples": ["Published 3 technical articles on Medium"]
  }
]
```

#### `action_plan` structure
```json
{
  "sprints": [
    {
      "sprint": 1,
      "duration_days": 30,
      "focus": "Technical foundations",
      "tracks": {
        "skills":      [{ "action": "...", "resources": ["Course name"] }],
        "experience":  [{ "action": "...", "resources": ["..."] }],
        "credentials": [{ "action": "...", "resources": ["Certification name"] }]
      }
    },
    { "sprint": 2, "duration_days": 30, ... },
    { "sprint": 3, "duration_days": 30, ... }
  ]
}
```

---

## Indexes

| Index | Table | Column(s) | Purpose |
|---|---|---|---|
| `idx_sessions_user_id` | sessions | user_id | Lookup sessions by user |
| `idx_sessions_expires_at` | sessions | expires_at | Efficient cleanup of expired sessions |
| `idx_resumes_session_id` | resumes | session_id | Lookup resumes by session |
| `idx_job_descriptions_session_id` | job_descriptions | session_id | Lookup JDs by session |
| `idx_reports_session_id` | reports | session_id | Lookup reports by session |
| `idx_reports_user_id` | reports | user_id | Dashboard: all reports for a user |
| `idx_reports_share_token` | reports | share_token | Partial index (WHERE NOT NULL) — public share lookups |
| `idx_reports_created_at` | reports | created_at DESC | Dashboard: sorted by newest first |

---

## Row-Level Security (RLS)

RLS is enabled on all tables. The backend uses the **service role key** which bypasses RLS entirely — these policies apply when using the **anon key** (e.g. direct client-side queries).

| Table | Who can SELECT | Who can INSERT | Who can DELETE |
|---|---|---|---|
| `users` | Own record only | — (Supabase Auth handles this) | Own record only |
| `sessions` | Own sessions + valid guest sessions | Authenticated user or guest | Own sessions only |
| `resumes` | Own session's resumes + valid guest sessions | Own or guest sessions | Own sessions only |
| `job_descriptions` | Same as resumes | Same as resumes | Own sessions only |
| `reports` | Own + guest session reports + publicly shared | Own or guest sessions | Own reports only |

---

## Database Triggers & Functions

### Triggers

| Trigger | Table | Event | What it does |
|---|---|---|---|
| `trigger_set_session_expiry` | sessions | BEFORE INSERT | Sets `expires_at` to +24h (guest) or +7d (authenticated) |
| `trigger_check_category_scores` | reports | BEFORE INSERT/UPDATE | Validates `category_scores` has all 5 required keys with valid scores |
| `trigger_manage_share_token` | reports | BEFORE UPDATE | Auto-generates `share_token` when sharing enabled; clears it when disabled |

### Functions

| Function | Returns | Purpose |
|---|---|---|
| `cleanup_expired_guest_sessions()` | INTEGER | Deletes expired guest sessions (cascade removes all related data). Run hourly via pg_cron or a backend job. |
| `generate_share_token()` | UUID | Generates a UUID for report sharing (called by trigger) |
| `increment_report_view_count(report_id)` | VOID | Safely increments `view_count` on a shared report |
| `validate_category_scores(scores JSONB)` | BOOLEAN | Checks all 5 category keys exist with `score` (0–100), `weight`, `reasoning` |

---

## Storage Buckets

Managed separately from the database (Supabase Storage = S3-compatible object store).

| Bucket | Public | Size limit | Allowed types | Path format |
|---|---|---|---|---|
| `resumes` | No | 10 MB | PDF, DOCX | `{session_id}/resume_{uuid}.{ext}` and `{session_id}/jd_{uuid}.{ext}` |
| `pdfs` | No | 50 MB | PDF only | `{session_id}/{report_id}.pdf` (future: generated report PDFs) |

Access to both buckets is via **signed URLs** (time-limited) generated by the backend.

---

## Migrations

Migration files live in `backend/supabase/migrations/` and must be run in order.

| File | What it does | How to run |
|---|---|---|
| `001_initial_schema.sql` | Creates all tables and indexes | Supabase SQL Editor or `supabase db push` |
| `002_row_level_security.sql` | Enables RLS and creates access policies | Supabase SQL Editor or `supabase db push` |
| `003_storage_buckets.sql` | Creates storage buckets | Run only the `INSERT INTO storage.buckets` statements via SQL Editor; create policies manually via Dashboard UI |
| `004_functions_and_triggers.sql` | Creates all triggers and utility functions | Supabase SQL Editor or `supabase db push` |

> **Storage policy limitation:** `CREATE POLICY` on `storage.objects` requires ownership that the SQL Editor doesn't grant. Use the Supabase Dashboard → Storage → select bucket → Policies tab to create storage policies manually.

### Using Supabase CLI (recommended for teams)
```bash
supabase login
supabase link --project-ref <your-project-ref>
supabase db push   # runs all migrations in order with correct permissions
```

---

## Cascade Behaviour

Deleting a **session** cascades to delete:
- All `resumes` linked to it
- All `job_descriptions` linked to it
- All `reports` linked to it

Deleting a **user** cascades to delete:
- All their `sessions` (which then cascade as above)

This means deleting a user removes all their data completely — no orphan records.
