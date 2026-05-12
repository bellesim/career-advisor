# Supabase Setup Guide for Career Advisor

This guide walks you through setting up the Supabase project for the Career Advisor application, including database schema, storage buckets, and security policies.

## Prerequisites

- A Supabase account (sign up at https://supabase.com)
- Supabase CLI installed (optional, for local development)
- PostgreSQL client (optional, for running migrations manually)

## Step 1: Create a New Supabase Project

1. Log in to your Supabase dashboard at https://app.supabase.com
2. Click "New Project"
3. Fill in the project details:
   - **Name**: career-advisor (or your preferred name)
   - **Database Password**: Generate a strong password and save it securely
   - **Region**: Choose the region closest to your users
   - **Pricing Plan**: Select based on your needs (Free tier works for development)
4. Click "Create new project"
5. Wait for the project to be provisioned (usually takes 1-2 minutes)

## Step 2: Get Your Project Credentials

Once your project is ready:

1. Go to **Settings** → **API** in the Supabase dashboard
2. Copy the following values:
   - **Project URL**: `https://your-project-id.supabase.co`
   - **anon/public key**: This is your `SUPABASE_KEY`
   - **service_role key**: Keep this secure, used for backend operations
3. Go to **Settings** → **API** → **JWT Settings**
4. Copy the **JWT Secret**: This is your `SUPABASE_JWT_SECRET`

## Step 3: Update Environment Variables

Update your `backend/.env` file with the credentials:

```bash
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key-here
SUPABASE_JWT_SECRET=your-jwt-secret-here
```

## Step 4: Run Database Migrations

### Option A: Using Supabase Dashboard (Recommended for first-time setup)

1. Go to **SQL Editor** in your Supabase dashboard
2. Run each migration file in order:

#### Migration 1: Initial Schema
- Copy the contents of `migrations/001_initial_schema.sql`
- Paste into the SQL Editor
- Click "Run"
- Verify that tables are created: Go to **Table Editor** and check for `users`, `sessions`, `resumes`, `job_descriptions`, `reports`

#### Migration 2: Row-Level Security
- Copy the contents of `migrations/002_row_level_security.sql`
- Paste into the SQL Editor
- Click "Run"
- Verify RLS is enabled: Go to **Authentication** → **Policies** and check that policies are listed

#### Migration 3: Storage Buckets
- Copy the contents of `migrations/003_storage_buckets.sql`
- Paste into the SQL Editor
- Click "Run"
- Verify buckets are created: Go to **Storage** and check for `resumes` and `pdfs` buckets

#### Migration 4: Functions and Triggers
- Copy the contents of `migrations/004_functions_and_triggers.sql`
- Paste into the SQL Editor
- Click "Run"
- Verify functions are created: Go to **Database** → **Functions** and check for the created functions

### Option B: Using Supabase CLI (For automated deployments)

If you have the Supabase CLI installed:

```bash
# Initialize Supabase in your project (if not already done)
cd backend
supabase init

# Link to your remote project
supabase link --project-ref your-project-id

# Run migrations
supabase db push

# Or run migrations individually
psql $DATABASE_URL -f supabase/migrations/001_initial_schema.sql
psql $DATABASE_URL -f supabase/migrations/002_row_level_security.sql
psql $DATABASE_URL -f supabase/migrations/003_storage_buckets.sql
psql $DATABASE_URL -f supabase/migrations/004_functions_and_triggers.sql
```

## Step 5: Configure Storage Buckets

### Verify Bucket Configuration

1. Go to **Storage** in your Supabase dashboard
2. You should see two buckets: `resumes` and `pdfs`
3. Click on each bucket to verify settings:

#### Resumes Bucket
- **Public**: No (private)
- **File size limit**: 10 MB
- **Allowed MIME types**: 
  - `application/pdf`
  - `application/vnd.openxmlformats-officedocument.wordprocessingml.document`

#### PDFs Bucket
- **Public**: No (private)
- **File size limit**: 50 MB
- **Allowed MIME types**: 
  - `application/pdf`

### Verify Storage Policies

1. Go to **Storage** → **Policies**
2. Select each bucket and verify that the policies are in place:
   - Users can upload files to their own session folders
   - Users can view their own files
   - Users can delete their own files
   - Shared report PDFs are accessible via share tokens

## Step 6: Configure Authentication

### Enable Email/Password Authentication

1. Go to **Authentication** → **Providers**
2. Enable **Email** provider
3. Configure email settings:
   - **Enable email confirmations**: Optional (recommended for production)
   - **Enable email change confirmations**: Yes
   - **Secure email change**: Yes

### Enable OAuth Providers (Optional)

For Google OAuth:
1. Go to **Authentication** → **Providers**
2. Enable **Google** provider
3. Add your Google OAuth credentials:
   - **Client ID**: From Google Cloud Console
   - **Client Secret**: From Google Cloud Console
4. Add authorized redirect URL to your Google OAuth app:
   - `https://your-project-id.supabase.co/auth/v1/callback`

For GitHub OAuth:
1. Enable **GitHub** provider
2. Add your GitHub OAuth credentials
3. Add authorized callback URL to your GitHub OAuth app

### Configure Password Requirements

The password validation is handled in the backend, but you can also configure Supabase Auth settings:

1. Go to **Authentication** → **Policies**
2. Set minimum password length: 8 characters
3. The backend enforces additional requirements (uppercase, lowercase, number)

## Step 7: Set Up Row-Level Security Policies

RLS policies should already be created by migration 002. Verify them:

1. Go to **Authentication** → **Policies**
2. Check that policies exist for each table:
   - **users**: View own profile, update own profile, delete own account
   - **sessions**: View own sessions, create sessions, delete own sessions
   - **resumes**: View own resumes, upload resumes, delete own resumes
   - **job_descriptions**: View own JDs, create JDs, delete own JDs
   - **reports**: View own/shared reports, create reports, update own reports, delete own reports

### Test RLS Policies

You can test RLS policies using the SQL Editor:

```sql
-- Test as authenticated user
SELECT * FROM reports WHERE user_id = auth.uid();

-- Test as guest (should only see guest session data)
SELECT * FROM sessions WHERE is_guest = TRUE AND expires_at > NOW();

-- Test shared report access
SELECT * FROM reports WHERE is_shared = TRUE AND share_token IS NOT NULL;
```

## Step 8: Create Database Indexes

Indexes should already be created by migration 001. Verify them:

1. Go to **Database** → **Indexes**
2. Check that indexes exist for:
   - `sessions.user_id`
   - `sessions.expires_at`
   - `resumes.session_id`
   - `job_descriptions.session_id`
   - `reports.session_id`
   - `reports.user_id`
   - `reports.share_token`
   - `reports.created_at`

## Step 9: Set Up Scheduled Jobs (Optional)

For cleaning up expired guest sessions, you have two options:

### Option A: Backend Scheduled Job (Recommended)

Implement a scheduled job in your backend (e.g., using APScheduler in Python) to run:

```python
from supabase import create_client
import os

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# Run this hourly
def cleanup_expired_sessions():
    result = supabase.rpc('cleanup_expired_guest_sessions').execute()
    print(f"Cleaned up {result.data} expired sessions")
```

### Option B: pg_cron Extension (If available)

If your Supabase plan supports pg_cron:

1. Go to **SQL Editor**
2. Run:

```sql
CREATE EXTENSION IF NOT EXISTS pg_cron;

SELECT cron.schedule(
    'cleanup-expired-sessions',
    '0 * * * *', -- Run every hour
    $$SELECT cleanup_expired_guest_sessions();$$
);
```

## Step 10: Verify Setup

### Test Database Connection

Run this test from your backend:

```python
from supabase import create_client
import os

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# Test connection
result = supabase.table('users').select("*").limit(1).execute()
print("Database connection successful!")
```

### Test Storage Upload

```python
# Test file upload
with open('test.pdf', 'rb') as f:
    result = supabase.storage.from_('resumes').upload(
        'test-session-id/test.pdf',
        f
    )
print("Storage upload successful!")
```

### Test Authentication

```python
# Test user registration
result = supabase.auth.sign_up({
    "email": "test@example.com",
    "password": "TestPass123"
})
print("Authentication successful!")
```

## Step 11: Production Checklist

Before deploying to production:

- [ ] Enable email confirmations for new signups
- [ ] Configure custom SMTP settings for emails
- [ ] Set up database backups (automatic in Supabase)
- [ ] Enable database point-in-time recovery
- [ ] Set up monitoring and alerts
- [ ] Configure rate limiting in Supabase dashboard
- [ ] Review and test all RLS policies
- [ ] Test storage bucket policies
- [ ] Set up scheduled cleanup job for guest sessions
- [ ] Configure custom domain for Supabase (optional)
- [ ] Enable database connection pooling if needed
- [ ] Review and optimize database indexes
- [ ] Set up logging and error tracking

## Troubleshooting

### Common Issues

**Issue**: "relation does not exist" error
- **Solution**: Make sure all migrations have been run in order

**Issue**: "permission denied" error when accessing tables
- **Solution**: Check that RLS policies are correctly configured and you're using the right credentials

**Issue**: Storage upload fails with "policy violation"
- **Solution**: Verify storage policies are in place and the folder structure matches session IDs

**Issue**: Authentication fails
- **Solution**: Check that SUPABASE_JWT_SECRET is correctly set in your environment variables

**Issue**: Expired sessions not being cleaned up
- **Solution**: Set up the scheduled cleanup job (see Step 9)

### Getting Help

- Supabase Documentation: https://supabase.com/docs
- Supabase Discord: https://discord.supabase.com
- GitHub Issues: https://github.com/supabase/supabase/issues

## Database Schema Reference

### Tables

- **users**: Authenticated user accounts
- **sessions**: User sessions (guest and authenticated)
- **resumes**: Uploaded resume files and parsed data
- **job_descriptions**: Job descriptions from various sources
- **reports**: Generated career analysis reports

### Storage Buckets

- **resumes**: Uploaded resume files (PDF, DOCX)
- **pdfs**: Generated report PDFs

### Functions

- `cleanup_expired_guest_sessions()`: Deletes expired guest sessions
- `generate_share_token()`: Generates unique share tokens
- `increment_report_view_count(UUID)`: Increments view count for shared reports
- `validate_category_scores(JSONB)`: Validates category scores structure

### Triggers

- `trigger_set_session_expiry`: Automatically sets session expiry
- `trigger_check_category_scores`: Validates category scores on insert/update
- `trigger_manage_share_token`: Manages share tokens when sharing is enabled/disabled

## Next Steps

After completing the Supabase setup:

1. Test the database connection from your backend
2. Implement the Supabase client in your backend services
3. Create API endpoints that interact with Supabase
4. Implement authentication flows in your frontend
5. Test file upload and storage functionality
6. Implement report generation and storage

For implementation details, refer to the main project documentation and design documents.
