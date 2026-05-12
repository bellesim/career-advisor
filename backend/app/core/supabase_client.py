"""
Supabase Client Module

Provides a singleton Supabase client instance for use throughout the application.
"""

from typing import Optional
from supabase import create_client, Client
from app.core.config import settings


class SupabaseClient:
    """
    Singleton Supabase client wrapper.
    
    Provides a single instance of the Supabase client that can be reused
    throughout the application.
    """
    
    _instance: Optional[Client] = None

    @classmethod
    def get_client(cls) -> Client:
        """Server-side client using the service role key — bypasses RLS."""
        if cls._instance is None:
            if not settings.SUPABASE_URL:
                raise ValueError("SUPABASE_URL is not configured")
            key = settings.SUPABASE_SERVICE_KEY or settings.SUPABASE_KEY
            if not key:
                raise ValueError("SUPABASE_SERVICE_KEY (or SUPABASE_KEY) is not configured")

            cls._instance = create_client(settings.SUPABASE_URL, key)

        return cls._instance
    
    @classmethod
    def reset_client(cls):
        """
        Reset the client instance.
        
        Useful for testing or when configuration changes.
        """
        cls._instance = None


# Convenience function for getting the client
def get_supabase_client() -> Client:
    """
    Get the Supabase client instance.
    
    Returns:
        Client: Supabase client instance
    """
    return SupabaseClient.get_client()


# Example usage functions for common operations

async def create_session(user_id: Optional[str] = None, is_guest: bool = False) -> dict:
    """
    Create a new session in the database.
    
    Args:
        user_id: User ID for authenticated sessions (None for guest sessions)
        is_guest: Whether this is a guest session
        
    Returns:
        dict: Created session data
    """
    client = get_supabase_client()
    
    session_data = {
        "user_id": user_id,
        "is_guest": is_guest,
    }
    
    result = client.table("sessions").insert(session_data).execute()
    return result.data[0] if result.data else None


async def get_session(session_id: str) -> Optional[dict]:
    """
    Get a session by ID.
    
    Args:
        session_id: Session ID
        
    Returns:
        dict: Session data or None if not found
    """
    client = get_supabase_client()
    
    result = client.table("sessions").select("*").eq("id", session_id).execute()
    return result.data[0] if result.data else None


async def cleanup_expired_sessions() -> int:
    """
    Clean up expired guest sessions.
    
    Returns:
        int: Number of sessions cleaned up
    """
    client = get_supabase_client()
    
    result = client.rpc("cleanup_expired_guest_sessions").execute()
    return result.data if result.data is not None else 0


async def upload_file(bucket: str, path: str, file_data: bytes) -> dict:
    """
    Upload a file to Supabase storage.
    
    Args:
        bucket: Bucket name ('resumes' or 'pdfs')
        path: File path within the bucket
        file_data: File content as bytes
        
    Returns:
        dict: Upload result
    """
    client = get_supabase_client()
    
    result = client.storage.from_(bucket).upload(path, file_data)
    return result


async def get_file_url(bucket: str, path: str, expires_in: int = 3600) -> str:
    """
    Get a signed URL for a file in storage.
    
    Args:
        bucket: Bucket name ('resumes' or 'pdfs')
        path: File path within the bucket
        expires_in: URL expiration time in seconds (default: 1 hour)
        
    Returns:
        str: Signed URL
    """
    client = get_supabase_client()
    
    result = client.storage.from_(bucket).create_signed_url(path, expires_in)
    return result.get("signedURL", "")


async def delete_file(bucket: str, path: str) -> dict:
    """
    Delete a file from storage.
    
    Args:
        bucket: Bucket name ('resumes' or 'pdfs')
        path: File path within the bucket
        
    Returns:
        dict: Deletion result
    """
    client = get_supabase_client()
    
    result = client.storage.from_(bucket).remove([path])
    return result


async def create_report(report_data: dict) -> dict:
    """
    Create a new report in the database.
    
    Args:
        report_data: Report data dictionary
        
    Returns:
        dict: Created report data
    """
    client = get_supabase_client()
    
    result = client.table("reports").insert(report_data).execute()
    return result.data[0] if result.data else None


async def get_report(report_id: str) -> Optional[dict]:
    """
    Get a report by ID.
    
    Args:
        report_id: Report ID
        
    Returns:
        dict: Report data or None if not found
    """
    client = get_supabase_client()
    
    result = client.table("reports").select("*").eq("id", report_id).execute()
    return result.data[0] if result.data else None


async def get_report_by_share_token(share_token: str) -> Optional[dict]:
    """
    Get a shared report by its share token.
    
    Args:
        share_token: Share token
        
    Returns:
        dict: Report data or None if not found or not shared
    """
    client = get_supabase_client()
    
    result = (
        client.table("reports")
        .select("*")
        .eq("share_token", share_token)
        .eq("is_shared", True)
        .execute()
    )
    return result.data[0] if result.data else None


async def update_report_sharing(report_id: str, is_shared: bool) -> dict:
    """
    Update report sharing status.
    
    Args:
        report_id: Report ID
        is_shared: Whether the report should be shared
        
    Returns:
        dict: Updated report data
    """
    client = get_supabase_client()
    
    result = (
        client.table("reports")
        .update({"is_shared": is_shared})
        .eq("id", report_id)
        .execute()
    )
    return result.data[0] if result.data else None


async def increment_report_views(report_id: str):
    """
    Increment the view count for a shared report.
    
    Args:
        report_id: Report ID
    """
    client = get_supabase_client()
    
    client.rpc("increment_report_view_count", {"report_id": report_id}).execute()


async def get_user_reports(user_id: str, limit: int = 50, offset: int = 0) -> list:
    """
    Get all reports for a user, sorted by creation date.
    
    Args:
        user_id: User ID
        limit: Maximum number of reports to return
        offset: Number of reports to skip
        
    Returns:
        list: List of report data
    """
    client = get_supabase_client()
    
    result = (
        client.table("reports")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(limit)
        .offset(offset)
        .execute()
    )
    return result.data if result.data else []


async def delete_report(report_id: str) -> bool:
    """
    Delete a report and its associated files.
    
    Args:
        report_id: Report ID
        
    Returns:
        bool: True if deleted successfully
    """
    client = get_supabase_client()
    
    # Get report to find associated files
    report = await get_report(report_id)
    if not report:
        return False
    
    # Delete report from database (cascade will handle related records)
    client.table("reports").delete().eq("id", report_id).execute()
    
    # Delete associated PDF if it exists
    try:
        session_id = report.get("session_id")
        pdf_path = f"{session_id}/{report_id}.pdf"
        await delete_file("pdfs", pdf_path)
    except Exception:
        # PDF might not exist yet, that's okay
        pass
    
    return True
