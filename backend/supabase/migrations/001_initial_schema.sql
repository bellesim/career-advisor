-- Career Advisor Database Schema
-- Migration: 001_initial_schema
-- Description: Create initial database tables for users, sessions, resumes, job descriptions, and reports

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    oauth_provider TEXT,
    oauth_id TEXT,
    CONSTRAINT valid_email CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- Sessions table
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    is_guest BOOLEAN NOT NULL DEFAULT FALSE
);

-- Resumes table
CREATE TABLE resumes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    uploaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    parsed_data JSONB NOT NULL DEFAULT '{}'::JSONB
);

-- Job descriptions table
CREATE TABLE job_descriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    source_type TEXT NOT NULL CHECK (source_type IN ('text', 'file', 'url')),
    source_content TEXT NOT NULL,
    parsed_data JSONB NOT NULL DEFAULT '{}'::JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Reports table
CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    resume_id UUID NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
    jd_id UUID NOT NULL REFERENCES job_descriptions(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Metadata
    candidate_name TEXT NOT NULL,
    target_role TEXT NOT NULL,
    
    -- Scores
    overall_score INTEGER NOT NULL CHECK (overall_score >= 0 AND overall_score <= 100),
    category_scores JSONB NOT NULL DEFAULT '{}'::JSONB,
    
    -- Analysis
    gaps JSONB NOT NULL DEFAULT '[]'::JSONB,
    strengths JSONB NOT NULL DEFAULT '[]'::JSONB,
    action_plan JSONB NOT NULL DEFAULT '{}'::JSONB,
    
    -- Sharing
    is_shared BOOLEAN NOT NULL DEFAULT FALSE,
    share_token UUID UNIQUE,
    view_count INTEGER NOT NULL DEFAULT 0
);

-- Create indexes for performance
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_expires_at ON sessions(expires_at);
CREATE INDEX idx_resumes_session_id ON resumes(session_id);
CREATE INDEX idx_job_descriptions_session_id ON job_descriptions(session_id);
CREATE INDEX idx_reports_session_id ON reports(session_id);
CREATE INDEX idx_reports_user_id ON reports(user_id);
CREATE INDEX idx_reports_share_token ON reports(share_token) WHERE share_token IS NOT NULL;
CREATE INDEX idx_reports_created_at ON reports(created_at DESC);

-- Add comments for documentation
COMMENT ON TABLE users IS 'Authenticated user accounts';
COMMENT ON TABLE sessions IS 'User sessions (both guest and authenticated)';
COMMENT ON TABLE resumes IS 'Uploaded resume files and parsed data';
COMMENT ON TABLE job_descriptions IS 'Job descriptions from various sources';
COMMENT ON TABLE reports IS 'Generated career analysis reports';

COMMENT ON COLUMN sessions.is_guest IS 'True for guest sessions (24h expiry), false for authenticated sessions';
COMMENT ON COLUMN reports.share_token IS 'Unique token for public sharing, null if not shared';
COMMENT ON COLUMN reports.view_count IS 'Number of times the shared report has been viewed';
