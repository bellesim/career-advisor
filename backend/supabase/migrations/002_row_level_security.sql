-- Career Advisor Row-Level Security Policies
-- Migration: 002_row_level_security
-- Description: Set up RLS policies to ensure users can only access their own data

-- Enable Row Level Security on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE resumes ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_descriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;

-- Users table policies
-- Users can only read their own user record
CREATE POLICY "Users can view own profile"
    ON users FOR SELECT
    USING (auth.uid() = id);

-- Users can update their own profile
CREATE POLICY "Users can update own profile"
    ON users FOR UPDATE
    USING (auth.uid() = id);

-- Users can delete their own account
CREATE POLICY "Users can delete own account"
    ON users FOR DELETE
    USING (auth.uid() = id);

-- Sessions table policies
-- Users can view their own sessions
CREATE POLICY "Users can view own sessions"
    ON sessions FOR SELECT
    USING (
        user_id = auth.uid() OR
        (is_guest = TRUE AND expires_at > NOW())
    );

-- Users can create sessions
CREATE POLICY "Users can create sessions"
    ON sessions FOR INSERT
    WITH CHECK (user_id = auth.uid() OR is_guest = TRUE);

-- Users can delete their own sessions
CREATE POLICY "Users can delete own sessions"
    ON sessions FOR DELETE
    USING (user_id = auth.uid());

-- Resumes table policies
-- Users can view resumes from their sessions
CREATE POLICY "Users can view own resumes"
    ON resumes FOR SELECT
    USING (
        session_id IN (
            SELECT id FROM sessions WHERE user_id = auth.uid()
        ) OR
        session_id IN (
            SELECT id FROM sessions WHERE is_guest = TRUE AND expires_at > NOW()
        )
    );

-- Users can insert resumes to their sessions
CREATE POLICY "Users can upload resumes"
    ON resumes FOR INSERT
    WITH CHECK (
        session_id IN (
            SELECT id FROM sessions WHERE user_id = auth.uid() OR is_guest = TRUE
        )
    );

-- Users can delete their own resumes
CREATE POLICY "Users can delete own resumes"
    ON resumes FOR DELETE
    USING (
        session_id IN (
            SELECT id FROM sessions WHERE user_id = auth.uid()
        )
    );

-- Job descriptions table policies
-- Users can view job descriptions from their sessions
CREATE POLICY "Users can view own job descriptions"
    ON job_descriptions FOR SELECT
    USING (
        session_id IN (
            SELECT id FROM sessions WHERE user_id = auth.uid()
        ) OR
        session_id IN (
            SELECT id FROM sessions WHERE is_guest = TRUE AND expires_at > NOW()
        )
    );

-- Users can insert job descriptions to their sessions
CREATE POLICY "Users can create job descriptions"
    ON job_descriptions FOR INSERT
    WITH CHECK (
        session_id IN (
            SELECT id FROM sessions WHERE user_id = auth.uid() OR is_guest = TRUE
        )
    );

-- Users can delete their own job descriptions
CREATE POLICY "Users can delete own job descriptions"
    ON job_descriptions FOR DELETE
    USING (
        session_id IN (
            SELECT id FROM sessions WHERE user_id = auth.uid()
        )
    );

-- Reports table policies
-- Users can view their own reports OR publicly shared reports
CREATE POLICY "Users can view own reports or shared reports"
    ON reports FOR SELECT
    USING (
        user_id = auth.uid() OR
        session_id IN (
            SELECT id FROM sessions WHERE user_id = auth.uid()
        ) OR
        session_id IN (
            SELECT id FROM sessions WHERE is_guest = TRUE AND expires_at > NOW()
        ) OR
        (is_shared = TRUE AND share_token IS NOT NULL)
    );

-- Users can insert reports to their sessions
CREATE POLICY "Users can create reports"
    ON reports FOR INSERT
    WITH CHECK (
        session_id IN (
            SELECT id FROM sessions WHERE user_id = auth.uid() OR is_guest = TRUE
        )
    );

-- Users can update their own reports (for sharing settings)
CREATE POLICY "Users can update own reports"
    ON reports FOR UPDATE
    USING (
        user_id = auth.uid() OR
        session_id IN (
            SELECT id FROM sessions WHERE user_id = auth.uid()
        )
    );

-- Users can delete their own reports
CREATE POLICY "Users can delete own reports"
    ON reports FOR DELETE
    USING (
        user_id = auth.uid() OR
        session_id IN (
            SELECT id FROM sessions WHERE user_id = auth.uid()
        )
    );

-- Service role bypass (for backend operations)
-- The service role key can bypass RLS for administrative operations
-- This is handled automatically by Supabase when using the service role key

-- Add comments for documentation
COMMENT ON POLICY "Users can view own profile" ON users IS 'Users can only view their own user profile';
COMMENT ON POLICY "Users can view own sessions" ON sessions IS 'Users can view their own sessions and valid guest sessions';
COMMENT ON POLICY "Users can view own reports or shared reports" ON reports IS 'Users can view their own reports or any publicly shared reports';
