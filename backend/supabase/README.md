# Supabase Configuration

This directory contains all Supabase-related configuration files for the Career Advisor application.

## Directory Structure

```
supabase/
├── README.md                           # This file
├── SETUP.md                            # Detailed setup guide
├── setup_verify.py                     # Setup verification script
└── migrations/
    ├── 001_initial_schema.sql          # Database tables and indexes
    ├── 002_row_level_security.sql      # RLS policies for data access control
    ├── 003_storage_buckets.sql         # Storage buckets and policies
    └── 004_functions_and_triggers.sql  # Database functions and triggers
```

## Quick Start

### 1. Create Supabase Project

1. Sign up at https://supabase.com
2. Create a new project
3. Note your project URL and API keys

### 2. Configure Environment Variables

Copy the example environment file and update with your Supabase credentials:

```bash
cp ../.env.example ../.env
```

Edit `../.env` and set:
```bash
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_JWT_SECRET=your-jwt-secret
```

### 3. Run Migrations

Go to your Supabase dashboard → SQL Editor and run each migration file in order:

1. `001_initial_schema.sql` - Creates tables and indexes
2. `002_row_level_security.sql` - Sets up RLS policies
3. `003_storage_buckets.sql` - Creates storage buckets
4. `004_functions_and_triggers.sql` - Adds functions and triggers

### 4. Verify Setup

Run the verification script to ensure everything is configured correctly:

```bash
cd backend
python supabase/setup_verify.py
```

## Detailed Documentation

For detailed setup instructions, see [SETUP.md](./SETUP.md).

## Database Schema

### Tables

- **users**: Authenticated user accounts
  - `id` (UUID, PK)
  - `email` (TEXT, UNIQUE)
  - `password_hash` (TEXT)
  - `created_at` (TIMESTAMPTZ)
  - `oauth_provider` (TEXT, nullable)
  - `oauth_id` (TEXT, nullable)

- **sessions**: User sessions (guest and authenticated)
  - `id` (UUID, PK)
  - `user_id` (UUID, FK to users, nullable)
  - `created_at` (TIMESTAMPTZ)
  - `expires_at` (TIMESTAMPTZ)
  - `is_guest` (BOOLEAN)

- **resumes**: Uploaded resume files and parsed data
  - `id` (UUID, PK)
  - `session_id` (UUID, FK to sessions)
  - `file_path` (TEXT)
  - `uploaded_at` (TIMESTAMPTZ)
  - `parsed_data` (JSONB)

- **job_descriptions**: Job descriptions from various sources
  - `id` (UUID, PK)
  - `session_id` (UUID, FK to sessions)
  - `source_type` (TEXT: 'text', 'file', 'url')
  - `source_content` (TEXT)
  - `parsed_data` (JSONB)
  - `created_at` (TIMESTAMPTZ)

- **reports**: Generated career analysis reports
  - `id` (UUID, PK)
  - `session_id` (UUID, FK to sessions)
  - `user_id` (UUID, FK to users, nullable)
  - `resume_id` (UUID, FK to resumes)
  - `jd_id` (UUID, FK to job_descriptions)
  - `created_at` (TIMESTAMPTZ)
  - `candidate_name` (TEXT)
  - `target_role` (TEXT)
  - `overall_score` (INTEGER, 0-100)
  - `category_scores` (JSONB)
  - `gaps` (JSONB)
  - `strengths` (JSONB)
  - `action_plan` (JSONB)
  - `is_shared` (BOOLEAN)
  - `share_token` (UUID, UNIQUE, nullable)
  - `view_count` (INTEGER)

### Storage Buckets

- **resumes**: Uploaded resume files (PDF, DOCX)
  - Max size: 10 MB
  - Private bucket
  - Folder structure: `{session_id}/{filename}`

- **pdfs**: Generated report PDFs
  - Max size: 50 MB
  - Private bucket
  - Folder structure: `{session_id}/{report_id}.pdf`

### Functions

- `cleanup_expired_guest_sessions()`: Deletes expired guest sessions and associated data
- `generate_share_token()`: Generates unique UUID for report sharing
- `increment_report_view_count(report_id UUID)`: Increments view count for shared reports
- `validate_category_scores(scores JSONB)`: Validates category scores structure

### Triggers

- `trigger_set_session_expiry`: Automatically sets session expiry (24h for guests, 7d for authenticated)
- `trigger_check_category_scores`: Validates category scores before insert/update
- `trigger_manage_share_token`: Manages share tokens when sharing is enabled/disabled

## Security

### Row-Level Security (RLS)

All tables have RLS enabled with policies that ensure:
- Users can only access their own data
- Guest users can only access data from their valid sessions
- Shared reports are accessible via share tokens
- Service role can bypass RLS for administrative operations

### Storage Security

Storage buckets have policies that:
- Users can only upload to their own session folders
- Users can only view their own files
- Shared report PDFs are accessible via share tokens
- File size and MIME type restrictions are enforced

### Authentication

- Email/password authentication with complexity requirements
- OAuth support (Google, GitHub)
- JWT-based session management
- Automatic session expiry (24h for guests, 7d for authenticated)

## Maintenance

### Cleanup Expired Sessions

Guest sessions expire after 24 hours and should be cleaned up regularly. You can:

1. **Run manually** via SQL Editor:
   ```sql
   SELECT cleanup_expired_guest_sessions();
   ```

2. **Schedule via backend** (recommended):
   ```python
   # Run hourly via APScheduler or similar
   supabase.rpc('cleanup_expired_guest_sessions').execute()
   ```

3. **Schedule via pg_cron** (if available):
   ```sql
   SELECT cron.schedule(
       'cleanup-expired-sessions',
       '0 * * * *',
       $$SELECT cleanup_expired_guest_sessions();$$
   );
   ```

### Monitoring

Monitor the following in your Supabase dashboard:

- Database size and growth
- Storage usage
- API request volume
- Authentication activity
- Error logs

### Backups

Supabase automatically backs up your database. For production:
- Enable point-in-time recovery
- Set up additional backup schedules if needed
- Test restore procedures regularly

## Troubleshooting

### Common Issues

**Tables not found**
- Ensure all migrations have been run in order
- Check that you're using the correct Supabase project

**Permission denied errors**
- Verify RLS policies are correctly configured
- Check that you're using the correct API key (anon vs service role)

**Storage upload fails**
- Verify storage buckets exist
- Check storage policies
- Ensure folder structure matches session IDs

**Authentication fails**
- Verify SUPABASE_JWT_SECRET is correct
- Check that email provider is enabled in Supabase dashboard

### Getting Help

- [Supabase Documentation](https://supabase.com/docs)
- [Supabase Discord](https://discord.supabase.com)
- [GitHub Issues](https://github.com/supabase/supabase/issues)

## Development vs Production

### Development

- Use separate Supabase project for development
- Disable email confirmations for faster testing
- Use test data and sample files
- Enable verbose logging

### Production

- Use dedicated Supabase project
- Enable email confirmations
- Configure custom SMTP settings
- Set up monitoring and alerts
- Enable database backups and point-in-time recovery
- Review and test all security policies
- Set up rate limiting
- Configure custom domain (optional)

## Next Steps

After completing the Supabase setup:

1. ✅ Verify setup using `setup_verify.py`
2. ✅ Test database connection from backend
3. ✅ Implement Supabase client in backend services
4. ✅ Create API endpoints that interact with Supabase
5. ✅ Implement authentication flows
6. ✅ Test file upload and storage
7. ✅ Implement report generation and storage

For implementation details, refer to the main project documentation.
