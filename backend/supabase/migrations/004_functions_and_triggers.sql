-- Career Advisor Database Functions and Triggers
-- Migration: 004_functions_and_triggers
-- Description: Create utility functions and triggers for automated tasks

-- Function: Clean up expired guest sessions
-- This function deletes guest sessions that have expired (older than 24 hours)
-- and cascades to delete associated resumes, job descriptions, and reports
CREATE OR REPLACE FUNCTION cleanup_expired_guest_sessions()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    -- Delete expired guest sessions (cascade will handle related records)
    DELETE FROM sessions
    WHERE is_guest = TRUE
    AND expires_at < NOW();
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION cleanup_expired_guest_sessions() IS 'Deletes expired guest sessions and their associated data';

-- Function: Generate unique share token for reports
-- This function generates a unique UUID for report sharing
CREATE OR REPLACE FUNCTION generate_share_token()
RETURNS UUID AS $$
BEGIN
    RETURN uuid_generate_v4();
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION generate_share_token() IS 'Generates a unique UUID for report sharing';

-- Function: Increment report view count
-- This function safely increments the view count for a shared report
CREATE OR REPLACE FUNCTION increment_report_view_count(report_id UUID)
RETURNS VOID AS $$
BEGIN
    UPDATE reports
    SET view_count = view_count + 1
    WHERE id = report_id
    AND is_shared = TRUE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION increment_report_view_count(UUID) IS 'Increments the view count for a shared report';

-- Function: Validate category scores structure
-- This function validates that category_scores JSONB has all required fields
CREATE OR REPLACE FUNCTION validate_category_scores(scores JSONB)
RETURNS BOOLEAN AS $$
DECLARE
    required_categories TEXT[] := ARRAY[
        'software_technical',
        'domain_knowledge',
        'experience_seniority',
        'credentials_education',
        'soft_skills_leadership'
    ];
    category TEXT;
BEGIN
    -- Check that all required categories exist
    FOREACH category IN ARRAY required_categories
    LOOP
        IF NOT (scores ? category) THEN
            RETURN FALSE;
        END IF;
        
        -- Check that each category has score, weight, and reasoning
        IF NOT (
            (scores -> category) ? 'score' AND
            (scores -> category) ? 'weight' AND
            (scores -> category) ? 'reasoning'
        ) THEN
            RETURN FALSE;
        END IF;
        
        -- Validate score is between 0 and 100
        IF (scores -> category ->> 'score')::INTEGER < 0 OR
           (scores -> category ->> 'score')::INTEGER > 100 THEN
            RETURN FALSE;
        END IF;
    END LOOP;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

COMMENT ON FUNCTION validate_category_scores(JSONB) IS 'Validates that category_scores JSONB has all required fields and valid values';

-- Trigger: Set session expiry on insert
-- Automatically sets expires_at based on session type (guest or authenticated)
CREATE OR REPLACE FUNCTION set_session_expiry()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.is_guest THEN
        -- Guest sessions expire in 24 hours
        NEW.expires_at := NEW.created_at + INTERVAL '24 hours';
    ELSE
        -- Authenticated sessions expire in 7 days
        NEW.expires_at := NEW.created_at + INTERVAL '7 days';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_set_session_expiry
    BEFORE INSERT ON sessions
    FOR EACH ROW
    EXECUTE FUNCTION set_session_expiry();

COMMENT ON TRIGGER trigger_set_session_expiry ON sessions IS 'Automatically sets session expiry based on session type';

-- Trigger: Validate category scores on report insert/update
CREATE OR REPLACE FUNCTION check_category_scores()
RETURNS TRIGGER AS $$
BEGIN
    IF NOT validate_category_scores(NEW.category_scores) THEN
        RAISE EXCEPTION 'Invalid category_scores structure. Must contain all 5 categories with score, weight, and reasoning.';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_check_category_scores
    BEFORE INSERT OR UPDATE ON reports
    FOR EACH ROW
    EXECUTE FUNCTION check_category_scores();

COMMENT ON TRIGGER trigger_check_category_scores ON reports IS 'Validates category_scores structure before insert/update';

-- Trigger: Clear share_token when sharing is disabled
CREATE OR REPLACE FUNCTION clear_share_token_on_disable()
RETURNS TRIGGER AS $$
BEGIN
    -- If is_shared is changed from true to false, clear the share_token
    IF OLD.is_shared = TRUE AND NEW.is_shared = FALSE THEN
        NEW.share_token := NULL;
    END IF;
    
    -- If is_shared is changed from false to true, generate a new share_token
    IF OLD.is_shared = FALSE AND NEW.is_shared = TRUE AND NEW.share_token IS NULL THEN
        NEW.share_token := generate_share_token();
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_manage_share_token
    BEFORE UPDATE ON reports
    FOR EACH ROW
    WHEN (OLD.is_shared IS DISTINCT FROM NEW.is_shared)
    EXECUTE FUNCTION clear_share_token_on_disable();

COMMENT ON TRIGGER trigger_manage_share_token ON reports IS 'Manages share_token when sharing is enabled/disabled';

-- Create a scheduled job to clean up expired guest sessions
-- Note: This requires pg_cron extension which may need to be enabled in Supabase
-- Alternatively, this can be run as a periodic backend job

-- Uncomment the following if pg_cron is available:
-- CREATE EXTENSION IF NOT EXISTS pg_cron;
-- 
-- SELECT cron.schedule(
--     'cleanup-expired-sessions',
--     '0 * * * *', -- Run every hour
--     $$SELECT cleanup_expired_guest_sessions();$$
-- );

-- For now, document that cleanup should be run periodically via backend job
COMMENT ON FUNCTION cleanup_expired_guest_sessions() IS 
'Should be run periodically (e.g., hourly) via backend scheduled job or pg_cron';
