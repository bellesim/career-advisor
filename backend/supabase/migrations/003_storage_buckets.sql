-- Career Advisor Storage Buckets Configuration
-- Migration: 003_storage_buckets
-- Description: Create storage buckets for resumes and PDFs with appropriate policies

-- Note: Storage buckets are typically created via Supabase Dashboard or CLI
-- This file documents the required configuration

-- Bucket: resumes
-- Purpose: Store uploaded resume files (PDF, DOCX)
-- Configuration:
--   - Public: false (private bucket)
--   - File size limit: 10MB
--   - Allowed MIME types: application/pdf, application/vnd.openxmlformats-officedocument.wordprocessingml.document

INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'resumes',
    'resumes',
    false,
    10485760, -- 10MB in bytes
    ARRAY['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
)
ON CONFLICT (id) DO NOTHING;

-- Bucket: pdfs
-- Purpose: Store generated report PDFs
-- Configuration:
--   - Public: false (private bucket, access controlled via signed URLs)
--   - File size limit: 50MB
--   - Allowed MIME types: application/pdf

INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'pdfs',
    'pdfs',
    false,
    52428800, -- 50MB in bytes
    ARRAY['application/pdf']
)
ON CONFLICT (id) DO NOTHING;

-- Storage policies for resumes bucket
-- Users can upload resumes to their own session folders
CREATE POLICY "Users can upload resumes to own sessions"
    ON storage.objects FOR INSERT
    WITH CHECK (
        bucket_id = 'resumes' AND
        (
            -- Authenticated users can upload to their session folders
            (auth.uid() IS NOT NULL AND (storage.foldername(name))[1] IN (
                SELECT id::text FROM sessions WHERE user_id = auth.uid()
            )) OR
            -- Guest users can upload to their session folders
            (auth.uid() IS NULL AND (storage.foldername(name))[1] IN (
                SELECT id::text FROM sessions WHERE is_guest = TRUE AND expires_at > NOW()
            ))
        )
    );

-- Users can view resumes from their own sessions
CREATE POLICY "Users can view own resumes"
    ON storage.objects FOR SELECT
    USING (
        bucket_id = 'resumes' AND
        (
            -- Authenticated users can view their session files
            (auth.uid() IS NOT NULL AND (storage.foldername(name))[1] IN (
                SELECT id::text FROM sessions WHERE user_id = auth.uid()
            )) OR
            -- Guest users can view their session files
            (auth.uid() IS NULL AND (storage.foldername(name))[1] IN (
                SELECT id::text FROM sessions WHERE is_guest = TRUE AND expires_at > NOW()
            ))
        )
    );

-- Users can delete resumes from their own sessions
CREATE POLICY "Users can delete own resumes"
    ON storage.objects FOR DELETE
    USING (
        bucket_id = 'resumes' AND
        auth.uid() IS NOT NULL AND
        (storage.foldername(name))[1] IN (
            SELECT id::text FROM sessions WHERE user_id = auth.uid()
        )
    );

-- Storage policies for pdfs bucket
-- Users can upload PDFs to their own session folders
CREATE POLICY "Users can upload PDFs to own sessions"
    ON storage.objects FOR INSERT
    WITH CHECK (
        bucket_id = 'pdfs' AND
        (
            -- Authenticated users can upload to their session folders
            (auth.uid() IS NOT NULL AND (storage.foldername(name))[1] IN (
                SELECT id::text FROM sessions WHERE user_id = auth.uid()
            )) OR
            -- Guest users can upload to their session folders
            (auth.uid() IS NULL AND (storage.foldername(name))[1] IN (
                SELECT id::text FROM sessions WHERE is_guest = TRUE AND expires_at > NOW()
            ))
        )
    );

-- Users can view PDFs from their own sessions OR shared reports
CREATE POLICY "Users can view own PDFs or shared PDFs"
    ON storage.objects FOR SELECT
    USING (
        bucket_id = 'pdfs' AND
        (
            -- Authenticated users can view their session files
            (auth.uid() IS NOT NULL AND (storage.foldername(name))[1] IN (
                SELECT id::text FROM sessions WHERE user_id = auth.uid()
            )) OR
            -- Guest users can view their session files
            (auth.uid() IS NULL AND (storage.foldername(name))[1] IN (
                SELECT id::text FROM sessions WHERE is_guest = TRUE AND expires_at > NOW()
            )) OR
            -- Anyone can view PDFs for shared reports
            ((storage.foldername(name))[2] IN (
                SELECT id::text FROM reports WHERE is_shared = TRUE AND share_token IS NOT NULL
            ))
        )
    );

-- Users can delete PDFs from their own sessions
CREATE POLICY "Users can delete own PDFs"
    ON storage.objects FOR DELETE
    USING (
        bucket_id = 'pdfs' AND
        auth.uid() IS NOT NULL AND
        (storage.foldername(name))[1] IN (
            SELECT id::text FROM sessions WHERE user_id = auth.uid()
        )
    );

-- Add comments for documentation
COMMENT ON POLICY "Users can upload resumes to own sessions" ON storage.objects IS 'Users can upload resume files to folders matching their session IDs';
COMMENT ON POLICY "Users can view own PDFs or shared PDFs" ON storage.objects IS 'Users can view their own PDFs or PDFs from shared reports';
